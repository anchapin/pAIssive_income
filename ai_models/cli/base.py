"""
Base command for the command-line interface.

This module provides the base class for all commands.
"""

import abc
import argparse
import logging
from typing import Any, List

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BaseCommand(abc.ABC):
    """
    Base class for all commands.
    """

    # Command description
    description = "Base command"

    def __init__(self, args: argparse.Namespace):
        """
        Initialize the command.

        Args:
            args: Command-line arguments
        """
        self.args = args

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """
        Add command-specific arguments to the parser.

        Args:
            parser: Argument parser
        """

    @abc.abstractmethod
    def run(self) -> int:
        """
        Run the command.

        Returns:
            Exit code
        """

    def _get_arg(self, name: str, default: Any = None) -> Any:
        """
        Get an argument value.

        Args:
            name: Argument name
            default: Default value

        Returns:
            Argument value
        """
        return getattr(self.args, name, default)

    def _validate_args(self, required_args: List[str]) -> bool:
        """
        Validate required arguments.

        Args:
            required_args: List of required argument names

        Returns:
            True if all required arguments are present, False otherwise
        """
        for arg in required_args:
            if not hasattr(self.args, arg) or getattr(self.args, arg) is None:
                logger.error(f"Missing required argument: {arg}")
                return False

        return True
