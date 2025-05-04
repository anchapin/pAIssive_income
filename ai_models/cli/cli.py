"""
"""
Command-line interface for AI models.
Command-line interface for AI models.


This module provides the main entry point for the command-line interface.
This module provides the main entry point for the command-line interface.
"""
"""




import argparse
import argparse
import logging
import logging
import sys
import sys
from typing import Dict, List, Optional, Type
from typing import Dict, List, Optional, Type


from .base import BaseCommand
from .base import BaseCommand


(
(
BenchmarkCommand,
BenchmarkCommand,
DeployCommand,
DeployCommand,
DownloadCommand,
DownloadCommand,
InfoCommand,
InfoCommand,
ListCommand,
ListCommand,
OptimizeCommand,
OptimizeCommand,
ServeGRPCCommand,
ServeGRPCCommand,
ServeRESTCommand,
ServeRESTCommand,
ValidateCommand,
ValidateCommand,
VersionCommand,
VersionCommand,
)
)


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




def get_commands() -> Dict[str, Type[BaseCommand]]:
    def get_commands() -> Dict[str, Type[BaseCommand]]:
    """
    """
    Get all available commands.
    Get all available commands.


    Returns:
    Returns:
    Dictionary mapping command names to command classes
    Dictionary mapping command names to command classes
    """
    """
    return {
    return {
    # Model management commands
    # Model management commands
    "download": DownloadCommand,
    "download": DownloadCommand,
    "list": ListCommand,
    "list": ListCommand,
    "info": InfoCommand,
    "info": InfoCommand,
    # Serving commands
    # Serving commands
    "serve-rest": ServeRESTCommand,
    "serve-rest": ServeRESTCommand,
    "serve-grpc": ServeGRPCCommand,
    "serve-grpc": ServeGRPCCommand,
    # Optimization commands
    # Optimization commands
    "optimize": OptimizeCommand,
    "optimize": OptimizeCommand,
    "benchmark": BenchmarkCommand,
    "benchmark": BenchmarkCommand,
    # Deployment commands
    # Deployment commands
    "deploy": DeployCommand,
    "deploy": DeployCommand,
    # Utility commands
    # Utility commands
    "validate": ValidateCommand,
    "validate": ValidateCommand,
    # Version management commands
    # Version management commands
    "version": VersionCommand,
    "version": VersionCommand,
    }
    }




    def create_parser() -> argparse.ArgumentParser:
    def create_parser() -> argparse.ArgumentParser:
    """
    """
    Create the argument parser.
    Create the argument parser.


    Returns:
    Returns:
    Argument parser
    Argument parser
    """
    """
    # Create main parser
    # Create main parser
    parser = argparse.ArgumentParser(
    parser = argparse.ArgumentParser(
    description="Command-line interface for AI models",
    description="Command-line interface for AI models",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    )


    # Add global arguments
    # Add global arguments
    parser.add_argument(
    parser.add_argument(
    "--log-level",
    "--log-level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    default="INFO",
    default="INFO",
    help="Logging level",
    help="Logging level",
    )
    )


    # Add subparsers for commands
    # Add subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")


    # Add command subparsers
    # Add command subparsers
    commands = get_commands()
    commands = get_commands()
    for name, command_class in commands.items():
    for name, command_class in commands.items():
    command_parser = subparsers.add_parser(
    command_parser = subparsers.add_parser(
    name,
    name,
    help=command_class.description,
    help=command_class.description,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    )
    command_class.add_arguments(command_parser)
    command_class.add_arguments(command_parser)


    return parser
    return parser




    def main(args: Optional[List[str]] = None) -> int:
    def main(args: Optional[List[str]] = None) -> int:
    """
    """
    Main entry point for the command-line interface.
    Main entry point for the command-line interface.


    Args:
    Args:
    args: Command-line arguments (defaults to sys.argv[1:])
    args: Command-line arguments (defaults to sys.argv[1:])


    Returns:
    Returns:
    Exit code
    Exit code
    """
    """
    # Parse arguments
    # Parse arguments
    parser = create_parser()
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    parsed_args = parser.parse_args(args)


    # Set up logging
    # Set up logging
    log_level = getattr(logging, parsed_args.log_level)
    log_level = getattr(logging, parsed_args.log_level)
    logging.getLogger().setLevel(log_level)
    logging.getLogger().setLevel(log_level)


    # Check if a command was specified
    # Check if a command was specified
    if not parsed_args.command:
    if not parsed_args.command:
    parser.print_help()
    parser.print_help()
    return 1
    return 1


    # Get command class
    # Get command class
    commands = get_commands()
    commands = get_commands()
    command_class = commands[parsed_args.command]
    command_class = commands[parsed_args.command]


    try:
    try:
    # Create and run command
    # Create and run command
    command = command_class(parsed_args)
    command = command_class(parsed_args)
    return command.run()
    return command.run()


except KeyboardInterrupt:
except KeyboardInterrupt:
    logger.info("Interrupted by user")
    logger.info("Interrupted by user")
    return 130
    return 130


except Exception as e:
except Exception as e:
    logger.error(f"Error executing command: {e}", exc_info=True)
    logger.error(f"Error executing command: {e}", exc_info=True)
    return 1
    return 1




    if __name__ == "__main__":
    if __name__ == "__main__":
    sys.exit(main())
    sys.exit(main())