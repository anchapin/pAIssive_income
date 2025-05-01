"""
Command Line Interface for Secrets Management

This module provides a command line interface for managing secrets.
"""

import argparse
import getpass
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from .secrets_manager import (
    SecretsBackend,
    delete_secret,
    get_secret,
    list_secret_names,
    set_secret,
)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def setup_parser() -> argparse.ArgumentParser:
    """
    Set up the argument parser for the CLI.

    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Secrets management for pAIssive Income",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set a secret in the default backend (environment variable)
  python -m common_utils.secrets.cli set API_KEY 

  # Get a secret from the file backend
  python -m common_utils.secrets.cli get --backend file API_KEY
  
  # List all secrets in Vault
  python -m common_utils.secrets.cli list --backend vault
  
  # Delete a secret
  python -m common_utils.secrets.cli delete API_KEY
        """,
    )

    # Backend option for all commands
    parser.add_argument(
        "--backend",
        choices=["env", "file", "memory", "vault"],
        default="env",
        help="Secret storage backend to use (default: env)",
    )

    # Subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Set command
    set_parser = subparsers.add_parser("set", help="Set a secret")
    set_parser.add_argument("name", help="Name of the secret")
    set_parser.add_argument(
        "--value", help="Secret value (if not provided, will prompt securely)"
    )

    # Get command
    get_parser = subparsers.add_parser("get", help="Get a secret")
    get_parser.add_argument("name", help="Name of the secret")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a secret")
    delete_parser.add_argument("name", help="Name of the secret")

    # List command
    list_parser = subparsers.add_parser("list", help="List secrets")

    return parser


def handle_set_command(args: argparse.Namespace) -> int:
    """
    Handle the 'set' command.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    name = args.name
    value = args.value

    if value is None:
        # Prompt for the secret value
        value = getpass.getpass(f"Enter value for secret '{name}': ")

    if set_secret(name, value, backend=args.backend):
        logger.info(f"Secret '{name}' set successfully in '{args.backend}' backend")
        return 0
    else:
        logger.error(f"Failed to set secret '{name}'")
        return 1


def handle_get_command(args: argparse.Namespace) -> int:
    """
    Handle the 'get' command.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    name = args.name
    value = get_secret(name, backend=args.backend)

    if value is None:
        logger.error(f"Secret '{name}' not found in '{args.backend}' backend")
        return 1
    else:
        # Print directly to stdout without logger
        print(value)
        return 0


def handle_delete_command(args: argparse.Namespace) -> int:
    """
    Handle the 'delete' command.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    name = args.name

    if delete_secret(name, backend=args.backend):
        logger.info(
            f"Secret '{name}' deleted successfully from '{args.backend}' backend"
        )
        return 0
    else:
        logger.error(f"Failed to delete secret '{name}' or secret not found")
        return 1


def handle_list_command(args: argparse.Namespace) -> int:
    """
    Handle the 'list' command.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    secrets = list_secret_names(backend=args.backend)

    if not secrets:
        logger.info(f"No secrets found in '{args.backend}' backend")
    else:
        logger.info(f"Secrets in '{args.backend}' backend:")
        for secret in sorted(secrets):
            print(f"  {secret}")

    return 0


def main() -> int:
    """
    Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = setup_parser()
    args = parser.parse_args()

    # Handle commands
    if args.command == "set":
        return handle_set_command(args)
    elif args.command == "get":
        return handle_get_command(args)
    elif args.command == "delete":
        return handle_delete_command(args)
    elif args.command == "list":
        return handle_list_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
