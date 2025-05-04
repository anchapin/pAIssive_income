"""
"""
Info command for the command-line interface.
Info command for the command-line interface.


This module provides a command for getting information about a model.
This module provides a command for getting information about a model.
"""
"""




import argparse
import argparse
import json
import json
import logging
import logging
import os
import os


from ...core import ModelManager
from ...core import ModelManager
from ..base import BaseCommand
from ..base import BaseCommand


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




class InfoCommand(BaseCommand):
    class InfoCommand(BaseCommand):
    """
    """
    Command for getting information about a model.
    Command for getting information about a model.
    """
    """


    description = "Get information about a model"
    description = "Get information about a model"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.


    Args:
    Args:
    parser: Argument parser
    parser: Argument parser
    """
    """
    parser.add_argument(
    parser.add_argument(
    "--model-path", type=str, required=True, help="Path to the model"
    "--model-path", type=str, required=True, help="Path to the model"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--format", choices=["text", "json"], default="text", help="Output format"
    "--format", choices=["text", "json"], default="text", help="Output format"
    )
    )
    parser.add_argument("--output", type=str, help="Output file (default: stdout)")
    parser.add_argument("--output", type=str, help="Output file (default: stdout)")
    parser.add_argument(
    parser.add_argument(
    "--include-files",
    "--include-files",
    action="store_true",
    action="store_true",
    help="Include list of files in the model",
    help="Include list of files in the model",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--include-weights",
    "--include-weights",
    action="store_true",
    action="store_true",
    help="Include information about model weights",
    help="Include information about model weights",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--include-performance",
    "--include-performance",
    action="store_true",
    action="store_true",
    help="Include performance information",
    help="Include performance information",
    )
    )


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.


    Returns:
    Returns:
    Exit code
    Exit code
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_path"]):
    if not self._validate_args(["model_path"]):
    return 1
    return 1


    try:
    try:
    # Import required modules
    # Import required modules
    # Check if model exists
    # Check if model exists
    if not os.path.exists(self.args.model_path):
    if not os.path.exists(self.args.model_path):
    logger.error(f"Model not found: {self.args.model_path}")
    logger.error(f"Model not found: {self.args.model_path}")
    return 1
    return 1


    # Get model information
    # Get model information
    manager = ModelManager(os.path.dirname(self.args.model_path))
    manager = ModelManager(os.path.dirname(self.args.model_path))
    model_info = manager.get_model_info(self.args.model_path)
    model_info = manager.get_model_info(self.args.model_path)


    if not model_info:
    if not model_info:
    logger.error(
    logger.error(
    f"Failed to get information for model: {self.args.model_path}"
    f"Failed to get information for model: {self.args.model_path}"
    )
    )
    return 1
    return 1


    # Format output
    # Format output
    if self.args.format == "json":
    if self.args.format == "json":
    # Convert model info to dictionary
    # Convert model info to dictionary
    info_dict = {
    info_dict = {
    "name": model_info.name,
    "name": model_info.name,
    "path": model_info.path,
    "path": model_info.path,
    "type": model_info.type,
    "type": model_info.type,
    "size": model_info.size,
    "size": model_info.size,
    }
    }


    # Add configuration
    # Add configuration
    if model_info.config:
    if model_info.config:
    info_dict["config"] = model_info.config.to_dict()
    info_dict["config"] = model_info.config.to_dict()


    # Add files if requested
    # Add files if requested
    if self.args.include_files:
    if self.args.include_files:
    info_dict["files"] = model_info.get_files()
    info_dict["files"] = model_info.get_files()


    # Add weights information if requested
    # Add weights information if requested
    if self.args.include_weights:
    if self.args.include_weights:
    info_dict["weights"] = model_info.get_weights_info()
    info_dict["weights"] = model_info.get_weights_info()


    # Add performance information if requested
    # Add performance information if requested
    if self.args.include_performance:
    if self.args.include_performance:
    info_dict["performance"] = model_info.get_performance_info()
    info_dict["performance"] = model_info.get_performance_info()


    # Convert to JSON
    # Convert to JSON
    output = json.dumps(info_dict, indent=2)
    output = json.dumps(info_dict, indent=2)
    else:
    else:
    # Format as text
    # Format as text
    lines = [
    lines = [
    f"Model: {model_info.name}",
    f"Model: {model_info.name}",
    f"Path: {model_info.path}",
    f"Path: {model_info.path}",
    f"Type: {model_info.type}",
    f"Type: {model_info.type}",
    ]
    ]


    # Add size
    # Add size
    if model_info.size:
    if model_info.size:
    size_mb = model_info.size / (1024 * 1024)
    size_mb = model_info.size / (1024 * 1024)
    lines.append(f"Size: {size_mb:.2f} MB")
    lines.append(f"Size: {size_mb:.2f} MB")


    # Add configuration
    # Add configuration
    if model_info.config:
    if model_info.config:
    lines.append("\nConfiguration:")
    lines.append("\nConfiguration:")
    for key, value in model_info.config.to_dict().items():
    for key, value in model_info.config.to_dict().items():
    if isinstance(value, dict):
    if isinstance(value, dict):
    continue
    continue
    lines.append(f"  {key}: {value}")
    lines.append(f"  {key}: {value}")


    # Add files if requested
    # Add files if requested
    if self.args.include_files:
    if self.args.include_files:
    files = model_info.get_files()
    files = model_info.get_files()
    if files:
    if files:
    lines.append("\nFiles:")
    lines.append("\nFiles:")
    for file in files:
    for file in files:
    lines.append(f"  {file}")
    lines.append(f"  {file}")


    # Add weights information if requested
    # Add weights information if requested
    if self.args.include_weights:
    if self.args.include_weights:
    weights_info = model_info.get_weights_info()
    weights_info = model_info.get_weights_info()
    if weights_info:
    if weights_info:
    lines.append("\nWeights:")
    lines.append("\nWeights:")
    for key, value in weights_info.items():
    for key, value in weights_info.items():
    lines.append(f"  {key}: {value}")
    lines.append(f"  {key}: {value}")


    # Add performance information if requested
    # Add performance information if requested
    if self.args.include_performance:
    if self.args.include_performance:
    perf_info = model_info.get_performance_info()
    perf_info = model_info.get_performance_info()
    if perf_info:
    if perf_info:
    lines.append("\nPerformance:")
    lines.append("\nPerformance:")
    for key, value in perf_info.items():
    for key, value in perf_info.items():
    lines.append(f"  {key}: {value}")
    lines.append(f"  {key}: {value}")


    # Join lines
    # Join lines
    output = "\n".join(lines)
    output = "\n".join(lines)


    # Write output
    # Write output
    if self.args.output:
    if self.args.output:
    with open(self.args.output, "w", encoding="utf-8") as f:
    with open(self.args.output, "w", encoding="utf-8") as f:
    f.write(output)
    f.write(output)
    logger.info(f"Model information written to {self.args.output}")
    logger.info(f"Model information written to {self.args.output}")
    else:
    else:
    print(output)
    print(output)


    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error getting model information: {e}", exc_info=True)
    logger.error(f"Error getting model information: {e}", exc_info=True)
    return 1
    return 1