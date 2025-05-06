"""cli - Module for common_utils/secrets.cli.

This module provides a command-line interface for managing secrets.
"""

# Standard library imports
import argparse
import getpass
import sys

# Third-party imports
# Local imports
from common_utils.logging import get_logger

from .audit import SecretsAuditor
from .rotation import SecretRotation
from .secrets_manager import (
    SecretsBackend,
    delete_secret,
    get_secret,
    list_secrets,
    set_secret,
)

# Initialize logger
logger = get_logger(__name__)


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


def get_secret_value(key: str) -> str:
    """Get a secret value from the user.

    Args:
    ----
        key: Key of the secret

    Returns:
    -------
        str: Value of the secret

    """
    return getpass.getpass(f"Enter value for {key}: ")


def handle_get(args: argparse.Namespace) -> None:
    """Handle the get command.

    Args:
    ----
        args: Command-line arguments

    """
    value = get_secret(args.key, args.backend)
    if value is None:
        print(f"Secret {args.key} not found")
        sys.exit(1)
    print(value)


def handle_set(args: argparse.Namespace) -> None:
    """Handle the set command.

    Args:
    ----
        args: Command-line arguments

    """
    value = args.value
    if value is None:
        value = get_secret_value(args.key)

    if set_secret(args.key, value, args.backend):
        print(f"Secret {args.key} set successfully")
    else:
        print(f"Failed to set secret {args.key}")
        sys.exit(1)


def handle_delete(args: argparse.Namespace) -> None:
    """Handle the delete command.

    Args:
    ----
        args: Command-line arguments

    """
    if delete_secret(args.key, args.backend):
        print(f"Secret {args.key} deleted successfully")
    else:
        print(f"Failed to delete secret {args.key}")
        sys.exit(1)


def handle_list(args: argparse.Namespace) -> None:
    """Handle the list command.

    Args:
    ----
        args: Command-line arguments

    """
    secrets = list_secrets(args.backend)
    if not secrets:
        print("No secrets found")
        return

    print(f"Found {len(secrets)} secrets:")
    for key in sorted(secrets.keys()):
        print(f"  {key}")


def handle_audit(args: argparse.Namespace) -> None:
    """Handle the audit command.

    Args:
    ----
        args: Command-line arguments

    """
    exclude_dirs = set(args.exclude) if args.exclude else None
    auditor = SecretsAuditor(exclude_dirs=exclude_dirs)
    auditor.audit(args.directory, args.output, args.json)


def handle_rotation(args: argparse.Namespace) -> None:
    """Handle the rotation command.

    Args:
    ----
        args: Command-line arguments

    """
    rotation = SecretRotation(secrets_backend=SecretsBackend(args.backend))

    if args.rotation_command == "schedule":
        rotation.schedule_rotation(args.key, args.interval)
        print(f"Scheduled rotation for {args.key} every {args.interval} days")
    elif args.rotation_command == "rotate":
        value = args.value
        if value is None:
            value = get_secret_value(args.key)

        if rotation.rotate_secret(args.key, value):
            print(f"Rotated secret {args.key}")
        else:
            print(f"Failed to rotate secret {args.key}")
            sys.exit(1)
    elif args.rotation_command == "rotate-all":
        count, rotated = rotation.rotate_all_due()
        if count > 0:
            print(f"Rotated {count} secrets:")
            for key in rotated:
                print(f"  {key}")
        else:
            print("No secrets due for rotation")
    elif args.rotation_command == "list-due":
        due = rotation.get_secrets_due_for_rotation()
        if due:
            print(f"Found {len(due)} secrets due for rotation:")
            for key in due:
                print(f"  {key}")
        else:
            print("No secrets due for rotation")
    else:
        print("Unknown rotation command")
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
