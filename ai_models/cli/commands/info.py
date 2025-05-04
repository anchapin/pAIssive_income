"""
Info command for the command-line interface.

This module provides a command for getting information about a model.
"""


import argparse
import json
import logging
import os

from ...core import ModelManager
from ..base import BaseCommand

# Set up logging
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InfoCommand(BaseCommand):
    """
    Command for getting information about a model.
    """

    description = "Get information about a model"

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    Add command-specific arguments to the parser.

    Args:
    parser: Argument parser
    """
    parser.add_argument(
    "--model-path", type=str, required=True, help="Path to the model"
    )
    parser.add_argument(
    "--format", choices=["text", "json"], default="text", help="Output format"
    )
    parser.add_argument("--output", type=str, help="Output file (default: stdout)")
    parser.add_argument(
    "--include-files",
    action="store_true",
    help="Include list of files in the model",
    )
    parser.add_argument(
    "--include-weights",
    action="store_true",
    help="Include information about model weights",
    )
    parser.add_argument(
    "--include-performance",
    action="store_true",
    help="Include performance information",
    )

    def run(self) -> int:
    """
    Run the command.

    Returns:
    Exit code
    """
    # Validate arguments
    if not self._validate_args(["model_path"]):
    return 1

    try:
    # Import required modules
    # Check if model exists
    if not os.path.exists(self.args.model_path):
    logger.error(f"Model not found: {self.args.model_path}")
    return 1

    # Get model information
    manager = ModelManager(os.path.dirname(self.args.model_path))
    model_info = manager.get_model_info(self.args.model_path)

    if not model_info:
    logger.error(
    f"Failed to get information for model: {self.args.model_path}"
    )
    return 1

    # Format output
    if self.args.format == "json":
    # Convert model info to dictionary
    info_dict = {
    "name": model_info.name,
    "path": model_info.path,
    "type": model_info.type,
    "size": model_info.size,
    }

    # Add configuration
    if model_info.config:
    info_dict["config"] = model_info.config.to_dict()

    # Add files if requested
    if self.args.include_files:
    info_dict["files"] = model_info.get_files()

    # Add weights information if requested
    if self.args.include_weights:
    info_dict["weights"] = model_info.get_weights_info()

    # Add performance information if requested
    if self.args.include_performance:
    info_dict["performance"] = model_info.get_performance_info()

    # Convert to JSON
    output = json.dumps(info_dict, indent=2)
    else:
    # Format as text
    lines = [
    f"Model: {model_info.name}",
    f"Path: {model_info.path}",
    f"Type: {model_info.type}",
    ]

    # Add size
    if model_info.size:
    size_mb = model_info.size / (1024 * 1024)
    lines.append(f"Size: {size_mb:.2f} MB")

    # Add configuration
    if model_info.config:
    lines.append("\nConfiguration:")
    for key, value in model_info.config.to_dict().items():
    if isinstance(value, dict):
    continue
    lines.append(f"  {key}: {value}")

    # Add files if requested
    if self.args.include_files:
    files = model_info.get_files()
    if files:
    lines.append("\nFiles:")
    for file in files:
    lines.append(f"  {file}")

    # Add weights information if requested
    if self.args.include_weights:
    weights_info = model_info.get_weights_info()
    if weights_info:
    lines.append("\nWeights:")
    for key, value in weights_info.items():
    lines.append(f"  {key}: {value}")

    # Add performance information if requested
    if self.args.include_performance:
    perf_info = model_info.get_performance_info()
    if perf_info:
    lines.append("\nPerformance:")
    for key, value in perf_info.items():
    lines.append(f"  {key}: {value}")

    # Join lines
    output = "\n".join(lines)

    # Write output
    if self.args.output:
    with open(self.args.output, "w", encoding="utf-8") as f:
    f.write(output)
    logger.info(f"Model information written to {self.args.output}")
    else:
    print(output)

    return 0

except Exception as e:
    logger.error(f"Error getting model information: {e}", exc_info=True)
    return 1