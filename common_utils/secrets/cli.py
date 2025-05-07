"""cli - Module for common_utils/secrets.cli.

This module provides a command-line interface for managing secrets.
"""

# Standard library imports
import argparse
import getpass
import hashlib
import os
import sys
import time
from secrets import compare_digest
from typing import Dict as _Dict
from typing import Optional

# Local imports
from common_utils.logging.secure_logging import get_secure_logger, mask_sensitive_data

from .audit import SecretsAuditor
from .rotation import SecretRotation
from .secrets_manager import (
    SecretsBackend,
    delete_secret,
    get_secret,
    list_secrets,
    set_secret,
)

# Initialize secure logger
logger = get_secure_logger(__name__)

# Security settings
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_DURATION = 300  # 5 minutes
ADMIN_TOKEN_FILE = os.path.expanduser("~/.secrets/admin_token")
failed_attempts: _Dict[str, int] = {}
lockout_times: _Dict[str, float] = {}


def require_auth(func):
    """Require authentication for sensitive operations."""

    def wrapper(*args, **kwargs):
        if not _check_auth():
            raise PermissionError("Authentication required for this operation")
        return func(*args, **kwargs)

    return wrapper


def _check_auth() -> bool:
    """Check if the user is authenticated."""
    if not os.path.exists(ADMIN_TOKEN_FILE):
        return False

    try:
        with open(ADMIN_TOKEN_FILE) as f:
            stored_token = f.read().strip()
        token = os.environ.get("SECRETS_ADMIN_TOKEN")
        if not token:
            return False
        return compare_digest(hashlib.sha256(token.encode()).hexdigest(), stored_token)
    except Exception as e:
        logger.error("Auth check failed", extra={"error": str(e)})
        return False


def _check_rate_limit(operation: str) -> None:
    """Check rate limiting for operations."""
    current_time = time.time()

    # Check lockout
    if operation in lockout_times:
        if current_time - lockout_times[operation] < LOCKOUT_DURATION:
            remaining_time = LOCKOUT_DURATION - (
                current_time - lockout_times[operation]
            )
            raise PermissionError(f"Operation locked for {remaining_time:.0f} seconds")
        del lockout_times[operation]
        failed_attempts[operation] = 0

    # Track failed attempts
    if failed_attempts.get(operation, 0) >= MAX_FAILED_ATTEMPTS:
        lockout_times[operation] = current_time
        raise PermissionError(
            f"Too many failed attempts. Locked for {LOCKOUT_DURATION} seconds"
        )


def _validate_secret_value(value: str) -> bool:
    """Validate a secret value."""
    if not value or len(value) < 8:
        return False
    has_upper = any(c.isupper() for c in value)
    has_lower = any(c.islower() for c in value)
    has_digit = any(c.isdigit() for c in value)
    has_special = any(not c.isalnum() for c in value)
    return has_upper and has_lower and has_digit and has_special


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns
    -------
        argparse.Namespace: Parsed arguments

    """
    parser = argparse.ArgumentParser(description="Manage secrets")
    parser.add_argument(
        "--backend",
        choices=[b.value for b in SecretsBackend],
        default=SecretsBackend.ENV.value,
        help="Backend to use for secrets",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get a secret")
    get_parser.add_argument("key", help="Key of the secret")

    # Set command
    set_parser = subparsers.add_parser("set", help="Set a secret")
    set_parser.add_argument("key", help="Key of the secret")
    set_parser.add_argument(
        "--value", help="Value of the secret (if not provided, will prompt)"
    )

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a secret")
    delete_parser.add_argument("key", help="Key of the secret")

    # Audit command
    audit_parser = subparsers.add_parser(
        "audit", help="Audit code for hardcoded secrets"
    )
    audit_parser.add_argument(
        "directory", nargs="?", default=".", help="Directory to scan"
    )
    audit_parser.add_argument("--output", help="Output file for the report")
    audit_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    audit_parser.add_argument(
        "--exclude",
        nargs="+",
        help="Directories to exclude from scanning",
    )

    # Rotation command
    rotation_parser = subparsers.add_parser("rotation", help="Manage secret rotation")
    rotation_subparsers = rotation_parser.add_subparsers(
        dest="rotation_command", help="Rotation command to run"
    )

    # Schedule rotation command
    schedule_parser = rotation_subparsers.add_parser(
        "schedule", help="Schedule a secret for rotation"
    )
    schedule_parser.add_argument("key", help="Key of the secret")
    schedule_parser.add_argument(
        "--interval", type=int, default=30, help="Interval in days between rotations"
    )

    # Rotate command
    rotate_parser = rotation_subparsers.add_parser("rotate", help="Rotate a secret")
    rotate_parser.add_argument("key", help="Key of the secret")
    rotate_parser.add_argument(
        "--value", help="New value for the secret (if not provided, will generate)"
    )

    return parser.parse_args()


def get_secret_value(key: str) -> Optional[str]:
    """Get a secret value from the user with validation.

    Args:
    ----
        key: Key of the secret

    Returns:
    -------
        Optional[str]: Value of the secret or None if validation fails

    """
    try:
        value = getpass.getpass(f"Enter value for {key}: ")
        if not _validate_secret_value(value):
            logger.warning(
                "Invalid secret format",
                extra={
                    "key": key,
                    "requirements": "8+ chars, upper, lower, number, special",
                },
            )
            return None
        return value
    except Exception as e:
        logger.error("Error getting secret value", extra={"error": str(e)})
        return None


@require_auth
def handle_get(args: argparse.Namespace) -> None:
    """Handle the get command.

    Args:
    ----
        args: Command-line arguments

    Raises:
    ------
        PermissionError: If authentication fails
        ValueError: If operation is rate limited

    """
    try:
        _check_rate_limit("get")
        value = get_secret(args.key, args.backend)

        if value is None:
            logger.warning("Secret not found", extra={"key": args.key})
            print(f"Secret {args.key} not found")
            sys.exit(1)

        # SECURITY FIX: Only provide visual confirmation that the secret exists,
        # don't show even a masked version of the value unless explicitly requested
        logger.info("Secret retrieved successfully", extra={"key": args.key})
        print(f"Secret {args.key} retrieved successfully")

        # If user explicitly needs to see the value, only show a heavily masked version
        if os.environ.get("SHOW_MASKED_SECRETS") == "true":
            masked_value = mask_sensitive_data(value)
            # Apply double masking for critical values
            masked_value = mask_sensitive_data(masked_value)
            print(f"Value: {masked_value}")

    except Exception as e:
        if isinstance(e, PermissionError):
            raise
        failed_attempts["get"] = failed_attempts.get("get", 0) + 1
        # Don't log the actual error as it might contain sensitive data
        logger.error(
            "Error retrieving secret",
            extra={"key": args.key, "error_type": type(e).__name__},
        )
        print("Error retrieving secret: Access error")
        sys.exit(1)


@require_auth
def handle_set(args: argparse.Namespace) -> None:
    """Handle the set command.

    Args:
    ----
        args: Command-line arguments

    Raises:
    ------
        PermissionError: If authentication fails
        ValueError: If operation is rate limited or validation fails

    """
    try:
        _check_rate_limit("set")
        value = args.value

        if value is None:
            value = get_secret_value(args.key)
            if value is None:
                logger.error(
                    "Invalid secret format",
                    extra={
                        "key": args.key,
                        "requirements": "8+ chars, upper, lower, number, special",
                    },
                )
                print("Invalid secret format. Requirements:")
                print("- At least 8 characters")
                print("- At least one uppercase letter")
                print("- At least one lowercase letter")
                print("- At least one number")
                print("- At least one special character")
                sys.exit(1)

        if set_secret(args.key, value, args.backend):
            logger.info("Secret set successfully", extra={"key": args.key})
            print(f"Secret {args.key} set successfully")
        else:
            failed_attempts["set"] = failed_attempts.get("set", 0) + 1
            logger.error("Failed to set secret", extra={"key": args.key})
            print(f"Failed to set secret {args.key}")
            sys.exit(1)

    except Exception as e:
        if isinstance(e, PermissionError):
            raise
        failed_attempts["set"] = failed_attempts.get("set", 0) + 1
        logger.error("Error setting secret", extra={"error": str(e), "key": args.key})
        print(f"Error setting secret: {str(e)}")
        sys.exit(1)


@require_auth
def handle_delete(args: argparse.Namespace) -> None:
    """Handle the delete command.

    Args:
    ----
        args: Command-line arguments

    Raises:
    ------
        PermissionError: If authentication fails
        ValueError: If operation is rate limited

    """
    try:
        _check_rate_limit("delete")

        # Require confirmation for delete
        confirm = input(
            f"Are you sure you want to delete secret {args.key}? (yes/no): "
        )
        if confirm.lower() != "yes":
            print("Delete operation cancelled")
            return

        if delete_secret(args.key, args.backend):
            logger.info("Secret deleted successfully", extra={"key": args.key})
            print(f"Secret {args.key} deleted successfully")
        else:
            failed_attempts["delete"] = failed_attempts.get("delete", 0) + 1
            logger.error("Failed to delete secret", extra={"key": args.key})
            print(f"Failed to delete secret {args.key}")
            sys.exit(1)

    except Exception as e:
        if isinstance(e, PermissionError):
            raise
        failed_attempts["delete"] = failed_attempts.get("delete", 0) + 1
        logger.error("Error deleting secret", extra={"error": str(e), "key": args.key})
        print(f"Error deleting secret: {str(e)}")
        sys.exit(1)


@require_auth
def handle_list(args: argparse.Namespace) -> None:
    """Handle the list command.

    Args:
    ----
        args: Command-line arguments

    Raises:
    ------
        PermissionError: If authentication fails
        ValueError: If operation is rate limited

    """
    try:
        _check_rate_limit("list")
        secrets_list = list_secrets(args.backend)

        if not secrets_list:
            print("No secrets found")
            logger.info("No secrets found in listing")
            return

        # Only print non-sensitive information
        print(f"Found {len(secrets_list)} secrets:")
        for idx, secret_key in enumerate(secrets_list):
            # Mask any sensitive information in the key names
            masked_key = mask_sensitive_data(secret_key)
            print(f"  {idx + 1}. {masked_key}")

        logger.info("Secrets listed successfully", extra={"count": len(secrets_list)})

    except Exception as e:
        if isinstance(e, PermissionError):
            raise
        failed_attempts["list"] = failed_attempts.get("list", 0) + 1
        logger.error("Error listing secrets", extra={"error": str(e)})
        print(f"Error listing secrets: {str(e)}")
        sys.exit(1)


@require_auth
def handle_audit(args: argparse.Namespace) -> None:
    """Handle the audit command.

    Args:
    ----
        args: Command-line arguments

    Raises:
    ------
        PermissionError: If authentication fails
        ValueError: If operation is rate limited

    """
    try:
        _check_rate_limit("audit")

        # Validate directory
        if not os.path.exists(args.directory):
            logger.error("Directory not found", extra={"directory": args.directory})
            print(f"Directory not found: {args.directory}")
            sys.exit(1)

        # Ensure output file location is secure
        if args.output:
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                logger.error(
                    "Output directory not found", extra={"directory": output_dir}
                )
                print(f"Output directory not found: {output_dir}")
                sys.exit(1)

        exclude_dirs = set(args.exclude) if args.exclude else None
        auditor = SecretsAuditor(exclude_dirs=exclude_dirs)

        logger.info(
            "Starting secrets audit",
            extra={
                "directory": args.directory,
                "output": args.output if args.output else "stdout",
                "format": "JSON" if args.json else "text",
            },
        )

        try:
            auditor.audit(args.directory, args.output, args.json)
            logger.info("Audit completed successfully")
        except Exception as e:
            logger.error("Audit failed", extra={"error": str(e)})
            print(f"Audit failed: {str(e)}")
            sys.exit(1)

    except Exception as e:
        if isinstance(e, PermissionError):
            raise
        failed_attempts["audit"] = failed_attempts.get("audit", 0) + 1
        logger.error("Error in audit command", extra={"error": str(e)})
        print(f"Error in audit command: {str(e)}")
        sys.exit(1)


@require_auth
def handle_rotation(args: argparse.Namespace) -> None:
    """Handle the rotation command.

    Args:
    ----
        args: Command-line arguments

    Raises:
    ------
        PermissionError: If authentication fails
        ValueError: If operation is rate limited or validation fails

    """
    try:
        _check_rate_limit("rotation")

        rotation = SecretRotation(secrets_backend=SecretsBackend(args.backend))

        try:
            if args.rotation_command == "schedule":
                if args.interval < 1:
                    raise ValueError("Rotation interval must be at least 1 day")

                rotation.schedule_rotation(args.key, args.interval)
                logger.info(
                    "Scheduled rotation",
                    extra={"key": args.key, "interval": args.interval},
                )
                print(f"Scheduled rotation for {args.key} every {args.interval} days")

            elif args.rotation_command == "rotate":
                value = args.value
                if value is None:
                    value = get_secret_value(args.key)
                    if value is None:
                        sys.exit(1)

                if rotation.rotate_secret(args.key, value):
                    logger.info("Secret rotated", extra={"key": args.key})
                    print(f"Rotated secret {args.key}")
                else:
                    failed_attempts["rotation"] = failed_attempts.get("rotation", 0) + 1
                    logger.error("Failed to rotate secret", extra={"key": args.key})
                    print(f"Failed to rotate secret {args.key}")
                    sys.exit(1)

            elif args.rotation_command == "rotate-all":
                count, rotated = rotation.rotate_all_due()
                if count > 0:
                    logger.info(f"Rotated {count} secrets")
                    print(f"Rotated {count} secrets:")
                    for key in rotated:
                        # Mask key names in output
                        masked_key = mask_sensitive_data(key)
                        print(f"  {masked_key}")
                else:
                    logger.info("No secrets due for rotation")
                    print("No secrets due for rotation")

            elif args.rotation_command == "list-due":
                due = rotation.get_secrets_due_for_rotation()
                if due:
                    logger.info(f"Found {len(due)} secrets due for rotation")
                    print(f"Found {len(due)} secrets due for rotation:")
                    for key in due:
                        # Mask key names in output
                        masked_key = mask_sensitive_data(key)
                        print(f"  {masked_key}")
                else:
                    logger.info("No secrets due for rotation")
                    print("No secrets due for rotation")
            else:
                logger.error(
                    "Unknown rotation command", extra={"command": args.rotation_command}
                )
                print("Unknown rotation command")
                sys.exit(1)

        except Exception as e:
            logger.error(
                "Error in rotation operation",
                extra={"command": args.rotation_command, "error": str(e)},
            )
            print(f"Error in rotation operation: {str(e)}")
            sys.exit(1)

    except Exception as e:
        if isinstance(e, PermissionError):
            raise
        failed_attempts["rotation"] = failed_attempts.get("rotation", 0) + 1
        logger.error("Error in rotation command", extra={"error": str(e)})
        print(f"Error in rotation command: {str(e)}")
        sys.exit(1)


def main() -> None:
    """Implement the main entry point for the CLI."""
    args = parse_args()

    if args.command == "get":
        handle_get(args)
    elif args.command == "set":
        handle_set(args)
    elif args.command == "delete":
        handle_delete(args)
    elif args.command == "list":
        handle_list(args)
    elif args.command == "audit":
        handle_audit(args)
    elif args.command == "rotation":
        handle_rotation(args)
    else:
        print("Unknown command")
        sys.exit(1)


if __name__ == "__main__":
    main()
