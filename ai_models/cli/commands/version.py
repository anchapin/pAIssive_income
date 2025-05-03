"""
Version command for the command - line interface.

This module provides the version command for the command - line interface.
"""

import argparse
import logging
from typing import Any, Dict, List, Optional

from ...model_base_types import ModelInfo
from ...model_manager import ModelManager
from ..base import BaseCommand

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class VersionCommand(BaseCommand):
    """
    Command to manage model versions.
    """

    description = "Manage model versions"

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """
        Add command - specific arguments.

        Args:
            parser: Argument parser
        """
        # Add subcommands
        subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand to execute")

        # List versions subcommand
        list_parser = subparsers.add_parser("list", help="List versions of a model")
        list_parser.add_argument("model_id", help="ID of the model")

        # Create version subcommand
        create_parser = subparsers.add_parser("create", help="Create a new version of a model")
        create_parser.add_argument("model_id", help="ID of the model")
        create_parser.add_argument("version", help="Version string (e.g., '1.0.0')")
        create_parser.add_argument(
            "--features", nargs=" + ", help="Features supported by this version"
        )

        # Get version subcommand
        get_parser = subparsers.add_parser("get", help="Get information about a specific version")
        get_parser.add_argument("model_id", help="ID of the model")
        get_parser.add_argument("version", help="Version string (e.g., '1.0.0')")

        # Check compatibility subcommand
        check_parser = subparsers.add_parser("check", help="Check compatibility between versions")
        check_parser.add_argument("model_id1", help="ID of the first model")
        check_parser.add_argument("version1", help="Version of the first model")
        check_parser.add_argument("model_id2", help="ID of the second model")
        check_parser.add_argument("version2", help="Version of the second model")

    def run(self) -> int:
        """
        Run the command.

        Returns:
            Exit code
        """
        # Check if a subcommand was specified
        if not hasattr(self.args, "subcommand") or not self.args.subcommand:
            logger.error("No subcommand specified")
            return 1

        # Create model manager
        model_manager = ModelManager()

        # Execute subcommand
        if self.args.subcommand == "list":
            return self._list_versions(model_manager)
        elif self.args.subcommand == "create":
            return self._create_version(model_manager)
        elif self.args.subcommand == "get":
            return self._get_version(model_manager)
        elif self.args.subcommand == "check":
            return self._check_compatibility(model_manager)
        else:
            logger.error(f"Unknown subcommand: {self.args.subcommand}")
            return 1

    def _list_versions(self, model_manager: ModelManager) -> int:
        """
        List versions of a model.

        Args:
            model_manager: Model manager

        Returns:
            Exit code
        """
        # Get model info
        model_info = model_manager.get_model_info(self.args.model_id)
        if not model_info:
            logger.error(f"Model with ID {self.args.model_id} not found")
            return 1

        # Get versions
        versions = model_manager.get_model_versions(self.args.model_id)

        # Print versions
        print(f"Versions of model {model_info.name} ({self.args.model_id}):")
        if not versions:
            print("  No versions found")
        else:
            for version in versions:
                print(f"  {version.version} - {version.timestamp}")

        return 0

    def _create_version(self, model_manager: ModelManager) -> int:
        """
        Create a new version of a model.

        Args:
            model_manager: Model manager

        Returns:
            Exit code
        """
        # Get model info
        model_info = model_manager.get_model_info(self.args.model_id)
        if not model_info:
            logger.error(f"Model with ID {self.args.model_id} not found")
            return 1

        # Create version
        try:
            version = model_manager.create_model_version(
                model_id=self.args.model_id, version=self.args.version, features=self.args.features
            )

            print(f"Created version {version.version} for model {model_info.name}")
            return 0

        except ValueError as e:
            logger.error(f"Error creating version: {e}")
            return 1

    def _get_version(self, model_manager: ModelManager) -> int:
        """
        Get information about a specific version.

        Args:
            model_manager: Model manager

        Returns:
            Exit code
        """
        # Get model info
        model_info = model_manager.get_model_info(self.args.model_id)
        if not model_info:
            logger.error(f"Model with ID {self.args.model_id} not found")
            return 1

        # Get version
        version = model_manager.versioned_manager.get_model_version(
            self.args.model_id, self.args.version
        )

        if not version:
            logger.error(f"Version {self.args.version} of model {self.args.model_id} not found")
            return 1

        # Print version info
        print(f"Version {version.version} of model {model_info.name} ({self.args.model_id}):")
        print(f"  Timestamp: {version.timestamp}")
        print(f"  Hash: {version.hash_value}")
        print(f"  Features: {', '.join(version.features) if version.features else 'None'}")
        print(f"  Dependencies: {version.dependencies}")
        print(
            f"  Compatible with: {', '.join(version.is_compatible_with) if version.is_compatible_with else 'None'}"
        )

        return 0

    def _check_compatibility(self, model_manager: ModelManager) -> int:
        """
        Check compatibility between versions.

        Args:
            model_manager: Model manager

        Returns:
            Exit code
        """
        # Check compatibility
        compatible = model_manager.check_version_compatibility(
            self.args.model_id1, self.args.version1, self.args.model_id2, self.args.version2
        )

        if compatible:
            print(
                f"Version {self.args.version1} of model {self.args.model_id1} is compatible with "
                f"version {self.args.version2} of model {self.args.model_id2}"
            )
        else:
            print(
                f"Version {self.args.version1} of model {self.args.model_id1} is NOT compatible with "
                f"version {self.args.version2} of model {self.args.model_id2}"
            )

        return 0
