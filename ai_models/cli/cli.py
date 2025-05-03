"""
Command-line interface for AI models.

This module provides the main entry point for the command-line interface.
"""


import argparse
import logging
import sys
from typing import Dict, List, Optional, Type

from .base import BaseCommand
from .commands import 

(
    BenchmarkCommand,
    DeployCommand,
    DownloadCommand,
    InfoCommand,
    ListCommand,
    OptimizeCommand,
    ServeGRPCCommand,
    ServeRESTCommand,
    ValidateCommand,
    VersionCommand,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_commands() -> Dict[str, Type[BaseCommand]]:
    """
    Get all available commands.

    Returns:
        Dictionary mapping command names to command classes
    """
    return {
        # Model management commands
        "download": DownloadCommand,
        "list": ListCommand,
        "info": InfoCommand,
        # Serving commands
        "serve-rest": ServeRESTCommand,
        "serve-grpc": ServeGRPCCommand,
        # Optimization commands
        "optimize": OptimizeCommand,
        "benchmark": BenchmarkCommand,
        # Deployment commands
        "deploy": DeployCommand,
        # Utility commands
        "validate": ValidateCommand,
        # Version management commands
        "version": VersionCommand,
    }


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser.

    Returns:
        Argument parser
    """
    # Create main parser
    parser = argparse.ArgumentParser(
        description="Command-line interface for AI models",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Add global arguments
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level",
    )

    # Add subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add command subparsers
    commands = get_commands()
    for name, command_class in commands.items():
        command_parser = subparsers.add_parser(
            name,
            help=command_class.description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        command_class.add_arguments(command_parser)

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the command-line interface.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code
    """
    # Parse arguments
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Set up logging
    log_level = getattr(logging, parsed_args.log_level)
    logging.getLogger().setLevel(log_level)

    # Check if a command was specified
    if not parsed_args.command:
        parser.print_help()
        return 1

    # Get command class
    commands = get_commands()
    command_class = commands[parsed_args.command]

    try:
        # Create and run command
        command = command_class(parsed_args)
        return command.run()

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"Error executing command: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())