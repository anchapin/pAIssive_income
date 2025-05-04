"""
"""
List command for the command-line interface.
List command for the command-line interface.


This module provides a command for listing available models.
This module provides a command for listing available models.
"""
"""




import argparse
import argparse
import json
import json
import logging
import logging


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




class ListCommand(BaseCommand):
    class ListCommand(BaseCommand):
    """
    """
    Command for listing available models.
    Command for listing available models.
    """
    """


    description = "List available models"
    description = "List available models"


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
    "--model-dir",
    "--model-dir",
    type=str,
    type=str,
    default="models",
    default="models",
    help="Directory containing models",
    help="Directory containing models",
    )
    )
    parser.add_argument("--filter", type=str, help="Filter models by name")
    parser.add_argument("--filter", type=str, help="Filter models by name")
    parser.add_argument("--type", type=str, help="Filter models by type")
    parser.add_argument("--type", type=str, help="Filter models by type")
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
    "--include-details",
    "--include-details",
    action="store_true",
    action="store_true",
    help="Include detailed information about each model",
    help="Include detailed information about each model",
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
    if not self._validate_args(["model_dir"]):
    if not self._validate_args(["model_dir"]):
    return 1
    return 1


    try:
    try:
    # Import required modules
    # Import required modules
    # Create model manager
    # Create model manager
    manager = ModelManager(self.args.model_dir)
    manager = ModelManager(self.args.model_dir)


    # Get models
    # Get models
    models = manager.list_models()
    models = manager.list_models()


    # Apply filters
    # Apply filters
    if self.args.filter:
    if self.args.filter:
    models = [
    models = [
    m for m in models if self.args.filter.lower() in m.name.lower()
    m for m in models if self.args.filter.lower() in m.name.lower()
    ]
    ]


    if self.args.type:
    if self.args.type:
    models = [m for m in models if m.type == self.args.type]
    models = [m for m in models if m.type == self.args.type]


    # Format output
    # Format output
    if self.args.format == "json":
    if self.args.format == "json":
    # Convert models to dictionaries
    # Convert models to dictionaries
    model_dicts = []
    model_dicts = []
    for model in models:
    for model in models:
    model_dict = {
    model_dict = {
    "name": model.name,
    "name": model.name,
    "path": model.path,
    "path": model.path,
    "type": model.type,
    "type": model.type,
    "size": model.size,
    "size": model.size,
    }
    }


    # Add details if requested
    # Add details if requested
    if self.args.include_details and model.config:
    if self.args.include_details and model.config:
    model_dict["config"] = model.config.to_dict()
    model_dict["config"] = model.config.to_dict()


    model_dicts.append(model_dict)
    model_dicts.append(model_dict)


    # Convert to JSON
    # Convert to JSON
    output = json.dumps(model_dicts, indent=2)
    output = json.dumps(model_dicts, indent=2)
    else:
    else:
    # Format as text
    # Format as text
    lines = []
    lines = []
    for model in models:
    for model in models:
    line = f"{model.name} ({model.type})"
    line = f"{model.name} ({model.type})"


    # Add size
    # Add size
    if model.size:
    if model.size:
    size_mb = model.size / (1024 * 1024)
    size_mb = model.size / (1024 * 1024)
    line += f" - {size_mb:.2f} MB"
    line += f" - {size_mb:.2f} MB"


    # Add path
    # Add path
    line += f"\n  Path: {model.path}"
    line += f"\n  Path: {model.path}"


    # Add details if requested
    # Add details if requested
    if self.args.include_details and model.config:
    if self.args.include_details and model.config:
    for key, value in model.config.to_dict().items():
    for key, value in model.config.to_dict().items():
    if isinstance(value, dict):
    if isinstance(value, dict):
    continue
    continue
    line += f"\n  {key}: {value}"
    line += f"\n  {key}: {value}"


    lines.append(line)
    lines.append(line)


    # Join lines
    # Join lines
    output = "\n\n".join(lines)
    output = "\n\n".join(lines)


    # Write output
    # Write output
    if self.args.output:
    if self.args.output:
    with open(self.args.output, "w", encoding="utf-8") as f:
    with open(self.args.output, "w", encoding="utf-8") as f:
    f.write(output)
    f.write(output)
    logger.info(f"Model list written to {self.args.output}")
    logger.info(f"Model list written to {self.args.output}")
    else:
    else:
    print(output)
    print(output)


    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error listing models: {e}", exc_info=True)
    logger.error(f"Error listing models: {e}", exc_info=True)
    return 1
    return 1