"""
Version command for the command-line interface.

This module provides a command to display version information.
"""

import argparse
import logging

from ..base import BaseCommand

# Set up logging
logger = logging.getLogger(__name__)


class VersionCommand(BaseCommand):
    """Command to display version information."""

    description = "Display version information"

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """
        Add command-specific arguments to the parser.

        Args:
            parser: Argument parser
        """
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format",
        )

    def run(self) -> int:
        """
        Run the command.

        Returns:
            Exit code
        """
        try:
            from ai_models.version import __version__

            if self.args.json:
                import json

                print(json.dumps({"version": __version__}))
            else:
                print(f"AI Models version: {__version__}")

            return 0

        except ImportError:
            logger.error("Could not determine version information")
            return 1
