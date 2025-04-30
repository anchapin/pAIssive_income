"""
List command for the command-line interface.

This module provides a command for listing available models.
"""

import os
import json
import argparse
import logging
from typing import Dict, Any, Optional, List

from ..base import BaseCommand

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ListCommand(BaseCommand):
    """
    Command for listing available models.
    """

    description = "List available models"

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """
        Add command-specific arguments to the parser.

        Args:
            parser: Argument parser
        """
        parser.add_argument(
            "--model-dir",
            type=str,
            default="models",
            help="Directory containing models",
        )
        parser.add_argument("--filter", type=str, help="Filter models by name")
        parser.add_argument("--type", type=str, help="Filter models by type")
        parser.add_argument(
            "--format", choices=["text", "json"], default="text", help="Output format"
        )
        parser.add_argument("--output", type=str, help="Output file (default: stdout)")
        parser.add_argument(
            "--include-details",
            action="store_true",
            help="Include detailed information about each model",
        )

    def run(self) -> int:
        """
        Run the command.

        Returns:
            Exit code
        """
        # Validate arguments
        if not self._validate_args(["model_dir"]):
            return 1

        try:
            # Import required modules
            from ...core import ModelManager

            # Create model manager
            manager = ModelManager(self.args.model_dir)

            # Get models
            models = manager.list_models()

            # Apply filters
            if self.args.filter:
                models = [
                    m for m in models if self.args.filter.lower() in m.name.lower()
                ]

            if self.args.type:
                models = [m for m in models if m.type == self.args.type]

            # Format output
            if self.args.format == "json":
                # Convert models to dictionaries
                model_dicts = []
                for model in models:
                    model_dict = {
                        "name": model.name,
                        "path": model.path,
                        "type": model.type,
                        "size": model.size,
                    }

                    # Add details if requested
                    if self.args.include_details and model.config:
                        model_dict["config"] = model.config.to_dict()

                    model_dicts.append(model_dict)

                # Convert to JSON
                output = json.dumps(model_dicts, indent=2)
            else:
                # Format as text
                lines = []
                for model in models:
                    line = f"{model.name} ({model.type})"

                    # Add size
                    if model.size:
                        size_mb = model.size / (1024 * 1024)
                        line += f" - {size_mb:.2f} MB"

                    # Add path
                    line += f"\n  Path: {model.path}"

                    # Add details if requested
                    if self.args.include_details and model.config:
                        for key, value in model.config.to_dict().items():
                            if isinstance(value, dict):
                                continue
                            line += f"\n  {key}: {value}"

                    lines.append(line)

                # Join lines
                output = "\n\n".join(lines)

            # Write output
            if self.args.output:
                with open(self.args.output, "w", encoding="utf-8") as f:
                    f.write(output)
                logger.info(f"Model list written to {self.args.output}")
            else:
                print(output)

            return 0

        except Exception as e:
            logger.error(f"Error listing models: {e}", exc_info=True)
            return 1
