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
from typing import Optional

# Local imports
from common_utils.logging.secure_logging import get_secure_logger
from common_utils.logging.secure_logging import mask_sensitive_data

from .audit import SecretsAuditor
from .rotation import SecretRotation
from .secrets_manager import SecretsBackend
from .secrets_manager import delete_secret
from .secrets_manager import get_secret
from .secrets_manager import list_secrets
from .secrets_manager import set_secret

# Initialize secure logger
logger = get_secure_logger(__name__)

# Security settings
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_DURATION = 300  # 5 minutes
# Store token in a secure location with proper permissions
ADMIN_TOKEN_DIR = os.path.expanduser("~/.secrets")
ADMIN_TOKEN_FILE = os.path.join(ADMIN_TOKEN_DIR, "admin_token")
failed_attempts: dict[str, int] = {}
lockout_times: dict[str, float] = {}


def require_auth(func):
    """Require authentication for sensitive operations."""

    def wrapper(*args, **kwargs):
        if not _check_auth():
            # Don't provide specific info on why auth failed for security
            raise PermissionError("Authentication required")
        return func(*args, **kwargs)

    return wrapper


def _check_auth() -> bool:
    """Check if the user is authenticated."""
    # Ensure admin token directory exists with proper permissions
    if not os.path.exists(ADMIN_TOKEN_DIR):
        try:
            os.makedirs(ADMIN_TOKEN_DIR, mode=0o700, exist_ok=True)
        except Exception:
            logger.error("Could not create secure token directory")
            return False

    if not os.path.exists(ADMIN_TOKEN_FILE):
        return False

    try:
        # Check file permissions
        if os.name != "nt":  # Skip on Windows
            file_stat = os.stat(ADMIN_TOKEN_FILE)
            if file_stat.st_mode & 0o077:  # Check if group or others have permissions
                logger.error("Insecure token file permissions")
                return False

        with open(ADMIN_TOKEN_FILE) as f:
            stored_token_hash = f.read().strip()

        # Get token from environment variable, not from command line or config file
        token = os.environ.get("SECRETS_ADMIN_TOKEN")
        if not token:
            # Don't provide specific info on why auth failed
            logger.warning("Authentication failed: missing token")
            return False

        # Use constant-time comparison to prevent timing attacks
        # Hash the provided token before comparison
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return compare_digest(token_hash, stored_token_hash)
    except Exception:
        # Don't log specific error details which might leak sensitive info
        logger.error("Authentication check failed")
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
    """Validate a secret value.

    Args:
    ----
        value: The secret value to validate

    Returns:
    -------
        bool: Whether the value passes validation

    """
    # Check for minimum criteria
    if not value:
        return False

    # Check minimum length - higher entropy requirements
    if len(value) < 12:
        return False

    # Check complexity requirements
    has_upper = any(c.isupper() for c in value)
    has_lower = any(c.islower() for c in value)
    has_digit = any(c.isdigit() for c in value)
    has_special = any(not c.isalnum() for c in value)

    # Calculate entropy score (simple implementation)
    char_set_size = 0
    if has_upper:
        char_set_size += 26
    if has_lower:
        char_set_size += 26
    if has_digit:
        char_set_size += 10
    if has_special:
        char_set_size += 32  # Approximation for special characters

    # Avoid logging any details about validation to prevent leaking information
    return (
        has_upper
        and has_lower
        and has_digit
        and has_special
        and char_set_size > 30
        and len(value) >= 12
    )


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
    # SECURITY FIX: Remove --value option to prevent secrets in command line
    set_parser = subparsers.add_parser("set", help="Set a secret")
    set_parser.add_argument("key", help="Key of the secret")
    # Removed --value argument for security

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a secret")
    delete_parser.add_argument("key", help="Key of the secret")

    # List command
    # Using add_parser but not capturing the returned parser since it's not needed
    subparsers.add_parser("list", help="List available secrets")

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

    # Rotate command - SECURITY FIX: Remove --value option
    rotate_parser = rotation_subparsers.add_parser("rotate", help="Rotate a secret")
    rotate_parser.add_argument("key", help="Key of the secret")
    # Removed --value argument for security

    # Add list-due and rotate-all commands
    rotation_subparsers.add_parser("list-due", help="List secrets due for rotation")
    rotation_subparsers.add_parser("rotate-all", help="Rotate all due secrets")

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

        # Mask the key name in case it contains sensitive information
        masked_key = mask_sensitive_data(args.key)

        value = get_secret(args.key, args.backend)

        if value is None:
            # Use masked key in logs to avoid potential sensitive information
            logger.warning("Secret not found", extra={"key": masked_key})
            print(f"Secret {masked_key} not found")
            sys.exit(1)

        # SECURITY FIX: Only provide visual confirmation that the secret exists,
        # don't show even a masked version of the value unless explicitly requested
        logger.info("Secret retrieved successfully", extra={"key": masked_key})
        print(f"Secret {masked_key} retrieved successfully")

        # SECURITY ENHANCEMENT: Replace double masking with secure clipboard copy option
        if os.environ.get("SECRETS_CLI_MODE") == "interactive":
            print("For security reasons, secrets are not displayed in the terminal.")
            print("Available options:")
            print(
                "  1. Copy to clipboard (temporary, will be cleared after 30 seconds)"
            )
            print("  2. Cancel")
            try:
                choice = input("Enter your choice (1-2): ")
                if choice == "1":
                    try:
                        # Import here to avoid dependency for non-interactive use
                        from threading import Timer

                        import pyperclip

                        # Copy to clipboard
                        pyperclip.copy(value)
                        print("Secret copied to clipboard for 30 seconds.")

                        # Set up timer to clear clipboard
                        def clear_clipboard():
                            pyperclip.copy("")
                            print("Clipboard cleared for security.")

                        Timer(30.0, clear_clipboard).start()
                    except ImportError:
                        print(
                            "pyperclip package not installed. "
                            "Install with: pip install pyperclip"
                        )
                else:
                    print("Operation cancelled.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                # Clear any partial data that might have been copied
                try:
                    import pyperclip

                    pyperclip.copy("")
                except ImportError:
                    # If pyperclip isn't installed, we can't clear the clipboard but
                    # that's acceptable since it wasn't used to begin with
                    logger.debug(
                        "pyperclip not installed, couldn't clear clipboard on interrupt"
                    )

    except Exception as e:
        if isinstance(e, PermissionError):
            raise
        # Increment failure counter before handling the error
        failed_attempts["get"] = failed_attempts.get("get", 0) + 1

        # Don't log the actual error as it might contain sensitive data
        # Only log the error type, not the message
        logger.error(
            "Error retrieving secret",
            extra={
                "key": mask_sensitive_data(args.key),
                "error_type": type(e).__name__,
            },
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

        # SECURITY FIX: Always prompt for secret value, never read from command line
        masked_key = mask_sensitive_data(args.key)
        logger.info("Getting secret value", extra={"key": masked_key})

        value = get_secret_value(args.key)
        if value is None:
            logger.error(
                "Invalid secret format",
                extra={
                    "key": masked_key,
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
            logger.info("Secret set successfully", extra={"key": masked_key})
            print(f"Secret {masked_key} set successfully")
        else:
            failed_attempts["set"] = failed_attempts.get("set", 0) + 1
            logger.error("Failed to set secret", extra={"key": masked_key})
            print(f"Failed to set secret {masked_key}")
            sys.exit(1)

    except Exception as e:
        if isinstance(e, PermissionError):
            raise
        failed_attempts["set"] = failed_attempts.get("set", 0) + 1
        # SECURITY FIX: Don't log specific error information
        logger.error(
            "Error setting secret",
            extra={
                "key": mask_sensitive_data(args.key),
                "error_type": type(e).__name__,
            },
        )
        print("Error setting secret: Access error")
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
        masked_key = mask_sensitive_data(args.key)

        # Require confirmation for delete
        confirm = input(
            f"Are you sure you want to delete secret {masked_key}? (yes/no): "
        )
        if confirm.lower() != "yes":
            print("Delete operation cancelled")
            return

        if delete_secret(args.key, args.backend):
            logger.info("Secret deleted successfully", extra={"key": masked_key})
            print(f"Secret {masked_key} deleted successfully")
        else:
            failed_attempts["delete"] = failed_attempts.get("delete", 0) + 1
            logger.error("Failed to delete secret", extra={"key": masked_key})
            print(f"Failed to delete secret {masked_key}")
            sys.exit(1)

    except Exception as e:
        if isinstance(e, PermissionError):
            raise
        failed_attempts["delete"] = failed_attempts.get("delete", 0) + 1
        # SECURITY FIX: Don't log specific error details
        logger.error(
            "Error deleting secret",
            extra={
                "key": mask_sensitive_data(args.key),
                "error_type": type(e).__name__,
            },
        )
        print("Error deleting secret: Access error")
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
        print(f"Error listing secrets: {e!s}")
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
            print(f"Audit failed: {e!s}")
            sys.exit(1)

    except Exception as e:
        if isinstance(e, PermissionError):
            raise
        failed_attempts["audit"] = failed_attempts.get("audit", 0) + 1
        logger.error("Error in audit command", extra={"error": str(e)})
        print(f"Error in audit command: {e!s}")
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

        # SECURITY FIX: Validate inputs
        if not hasattr(args, "rotation_command") or not args.rotation_command:
            logger.error("Missing rotation command")
            print("Missing rotation command")
            sys.exit(1)

        rotation = SecretRotation(secrets_backend=SecretsBackend(args.backend))
        masked_key = mask_sensitive_data(getattr(args, "key", "unknown"))

        try:
            if args.rotation_command == "schedule":
                if args.interval < 1:
                    raise ValueError("Rotation interval must be at least 1 day")

                rotation.schedule_rotation(args.key, args.interval)
                logger.info(
                    "Scheduled rotation",
                    extra={"key": masked_key, "interval": args.interval},
                )
                print(f"Scheduled rotation for {masked_key} every {args.interval} days")

            elif args.rotation_command == "rotate":
                # SECURITY FIX: Always prompt for secret value
                logger.info("Getting new secret value", extra={"key": masked_key})
                value = get_secret_value(args.key)
                if value is None:
                    sys.exit(1)

                if rotation.rotate_secret(args.key, value):
                    logger.info("Secret rotated", extra={"key": masked_key})
                    print(f"Rotated secret {masked_key}")
                else:
                    failed_attempts["rotation"] = failed_attempts.get("rotation", 0) + 1
                    logger.error("Failed to rotate secret", extra={"key": masked_key})
                    print(f"Failed to rotate secret {masked_key}")
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
            # SECURITY FIX: Don't log specific error details
            logger.error(
                "Error in rotation operation",
                extra={
                    "command": args.rotation_command,
                    "error_type": type(e).__name__,
                },
            )
            print("Error in rotation operation: Access error")
            sys.exit(1)

    except Exception as e:
        if isinstance(e, PermissionError):
            raise
        failed_attempts["rotation"] = failed_attempts.get("rotation", 0) + 1
        # SECURITY FIX: Don't log specific error details
        logger.error(
            "Error in rotation command", extra={"error_type": type(e).__name__}
        )
        print("Error in rotation command: Access error")
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
