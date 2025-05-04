"""
"""
Command implementations for the command-line interface.
Command implementations for the command-line interface.


This module provides the implementation of all commands for the CLI.
This module provides the implementation of all commands for the CLI.
"""
"""




import argparse
import argparse
import csv
import csv
import json
import json
import logging
import logging
import os
import os
import signal
import signal
import sys
import sys
import time
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Optional
from typing import Optional


import matplotlib
import matplotlib


from ai_models.model_config import ModelConfig
from ai_models.model_config import ModelConfig
from ai_models.model_downloader import ModelDownloader
from ai_models.model_downloader import ModelDownloader
from ai_models.model_manager import ModelManager
from ai_models.model_manager import ModelManager


from .base import BaseCommand
from .base import BaseCommand


# Add the project root to the Python path to import other modules
# Add the project root to the Python path to import other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
(
(
InferenceTracker,
InferenceTracker,
PerformanceMonitor,
PerformanceMonitor,
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




class DownloadCommand(BaseCommand):
    class DownloadCommand(BaseCommand):
    """
    """
    Command for downloading models.
    Command for downloading models.
    """
    """


    description = "Download a model from a repository"
    description = "Download a model from a repository"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.
    """
    """
    parser.add_argument(
    parser.add_argument(
    "--model-id", required=True, help="ID or name of the model to download"
    "--model-id", required=True, help="ID or name of the model to download"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--source",
    "--source",
    choices=["huggingface", "local", "url"],
    choices=["huggingface", "local", "url"],
    default="huggingface",
    default="huggingface",
    help="Source of the model",
    help="Source of the model",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--output-dir",
    "--output-dir",
    help="Directory to save the model to (default: models directory from config)",
    help="Directory to save the model to (default: models directory from config)",
    )
    )
    parser.add_argument("--config", help="Path to a configuration file")
    parser.add_argument("--config", help="Path to a configuration file")


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id", "source"]):
    if not self._validate_args(["model_id", "source"]):
    return 1
    return 1


    # Load configuration
    # Load configuration
    config = self._load_config()
    config = self._load_config()
    if not config:
    if not config:
    return 1
    return 1


    # Create model manager and downloader
    # Create model manager and downloader
    model_manager = ModelManager(config)
    model_manager = ModelManager(config)
    downloader = ModelDownloader(model_manager)
    downloader = ModelDownloader(model_manager)


    # Determine output directory
    # Determine output directory
    output_dir = self._get_arg("output_dir") or config.models_dir
    output_dir = self._get_arg("output_dir") or config.models_dir
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    # Determine destination path
    # Determine destination path
    destination = os.path.join(output_dir, self._get_arg("model_id"))
    destination = os.path.join(output_dir, self._get_arg("model_id"))


    # Start download
    # Start download
    download_task = downloader.download_model(
    download_task = downloader.download_model(
    model_id=self._get_arg("model_id"),
    model_id=self._get_arg("model_id"),
    source=self._get_arg("source"),
    source=self._get_arg("source"),
    destination=destination,
    destination=destination,
    )
    )


    # Wait for download to complete
    # Wait for download to complete
    result = downloader.wait_for_download(download_task.id)
    result = downloader.wait_for_download(download_task.id)


    # Check download status
    # Check download status
    if result.status == "completed":
    if result.status == "completed":
    logger.info(f"Successfully downloaded model to {result.destination}")
    logger.info(f"Successfully downloaded model to {result.destination}")


    # Register the downloaded model
    # Register the downloaded model
    model_type = (
    model_type = (
    "huggingface" if self._get_arg("source") == "huggingface" else "unknown"
    "huggingface" if self._get_arg("source") == "huggingface" else "unknown"
    )
    )
    description = (
    description = (
    f"Downloaded {self._get_arg('model_id')} from {self._get_arg('source')}"
    f"Downloaded {self._get_arg('model_id')} from {self._get_arg('source')}"
    )
    )


    model_info = model_manager.register_downloaded_model(
    model_info = model_manager.register_downloaded_model(
    download_task=download_task,
    download_task=download_task,
    model_type=model_type,
    model_type=model_type,
    description=description,
    description=description,
    )
    )


    if model_info:
    if model_info:
    logger.info(f"Registered model as {model_info.id}")
    logger.info(f"Registered model as {model_info.id}")


    return 0
    return 0
    else:
    else:
    logger.error(f"Download failed: {result.error}")
    logger.error(f"Download failed: {result.error}")
    return 1
    return 1


    def _load_config(self) -> Optional[ModelConfig]:
    def _load_config(self) -> Optional[ModelConfig]:
    """
    """
    Load the configuration.
    Load the configuration.
    """
    """
    config_path = self._get_arg("config")
    config_path = self._get_arg("config")


    if config_path:
    if config_path:
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    logger.error(f"Configuration file {config_path} not found")
    logger.error(f"Configuration file {config_path} not found")
    return None
    return None


    try:
    try:
    return ModelConfig.load(config_path)
    return ModelConfig.load(config_path)
except Exception as e:
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.error(f"Error loading configuration: {e}")
    return None
    return None


    return ModelConfig.get_default()
    return ModelConfig.get_default()




    class ListCommand(BaseCommand):
    class ListCommand(BaseCommand):
    """
    """
    Command for listing models.
    Command for listing models.
    """
    """


    description = "List all available models"
    description = "List all available models"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.
    """
    """
    parser.add_argument("--type", help="Filter models by type")
    parser.add_argument("--type", help="Filter models by type")
    parser.add_argument(
    parser.add_argument(
    "--format", choices=["text", "json"], default="text", help="Output format"
    "--format", choices=["text", "json"], default="text", help="Output format"
    )
    )
    parser.add_argument("--config", help="Path to a configuration file")
    parser.add_argument("--config", help="Path to a configuration file")


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.
    """
    """
    # Load configuration
    # Load configuration
    config = self._load_config()
    config = self._load_config()
    if not config:
    if not config:
    return 1
    return 1


    # Create model manager
    # Create model manager
    model_manager = ModelManager(config)
    model_manager = ModelManager(config)


    # Get all models
    # Get all models
    models = model_manager.get_all_models()
    models = model_manager.get_all_models()


    # Filter by type
    # Filter by type
    model_type = self._get_arg("type")
    model_type = self._get_arg("type")
    if model_type:
    if model_type:
    models = [model for model in models if model.type == model_type]
    models = [model for model in models if model.type == model_type]


    # Format output
    # Format output
    if self._get_arg("format") == "json":
    if self._get_arg("format") == "json":
    # JSON output
    # JSON output
    model_data = [model.to_dict() for model in models]
    model_data = [model.to_dict() for model in models]
    print(json.dumps(model_data, indent=2))
    print(json.dumps(model_data, indent=2))
    else:
    else:
    # Text output
    # Text output
    print(f"Found {len(models)} models:")
    print(f"Found {len(models)} models:")
    for model in models:
    for model in models:
    print(
    print(
    f"- {model.name} (ID: {model.id}, Type: {model.type}, Format: {model.format})"
    f"- {model.name} (ID: {model.id}, Type: {model.type}, Format: {model.format})"
    )
    )
    if model.version != "0.0.0":
    if model.version != "0.0.0":
    print(f"  Version: {model.version}")
    print(f"  Version: {model.version}")
    if model.description:
    if model.description:
    print(f"  Description: {model.description}")
    print(f"  Description: {model.description}")
    print(f"  Path: {model.path}")
    print(f"  Path: {model.path}")
    print("")
    print("")


    return 0
    return 0


    def _load_config(self) -> Optional[ModelConfig]:
    def _load_config(self) -> Optional[ModelConfig]:
    """
    """
    Load the configuration.
    Load the configuration.
    """
    """
    config_path = self._get_arg("config")
    config_path = self._get_arg("config")


    if config_path:
    if config_path:
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    logger.error(f"Configuration file {config_path} not found")
    logger.error(f"Configuration file {config_path} not found")
    return None
    return None


    try:
    try:
    return ModelConfig.load(config_path)
    return ModelConfig.load(config_path)
except Exception as e:
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.error(f"Error loading configuration: {e}")
    return None
    return None


    return ModelConfig.get_default()
    return ModelConfig.get_default()




    class InfoCommand(BaseCommand):
    class InfoCommand(BaseCommand):
    """
    """
    Command for getting model information.
    Command for getting model information.
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
    """
    """
    parser.add_argument("--model-id", required=True, help="ID of the model")
    parser.add_argument("--model-id", required=True, help="ID of the model")
    parser.add_argument(
    parser.add_argument(
    "--format", choices=["text", "json"], default="text", help="Output format"
    "--format", choices=["text", "json"], default="text", help="Output format"
    )
    )
    parser.add_argument("--config", help="Path to a configuration file")
    parser.add_argument("--config", help="Path to a configuration file")


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id"]):
    if not self._validate_args(["model_id"]):
    return 1
    return 1


    # Load configuration
    # Load configuration
    config = self._load_config()
    config = self._load_config()
    if not config:
    if not config:
    return 1
    return 1


    # Create model manager
    # Create model manager
    model_manager = ModelManager(config)
    model_manager = ModelManager(config)


    # Get model information
    # Get model information
    model_info = model_manager.get_model_info(self._get_arg("model_id"))
    model_info = model_manager.get_model_info(self._get_arg("model_id"))


    if not model_info:
    if not model_info:
    logger.error(f"Model with ID {self._get_arg('model_id')} not found")
    logger.error(f"Model with ID {self._get_arg('model_id')} not found")
    return 1
    return 1


    # Format output
    # Format output
    if self._get_arg("format") == "json":
    if self._get_arg("format") == "json":
    # JSON output
    # JSON output
    print(json.dumps(model_info.to_dict(), indent=2))
    print(json.dumps(model_info.to_dict(), indent=2))
    else:
    else:
    # Text output
    # Text output
    print("Model Information:")
    print("Model Information:")
    print(f"- ID: {model_info.id}")
    print(f"- ID: {model_info.id}")
    print(f"- Name: {model_info.name}")
    print(f"- Name: {model_info.name}")
    print(f"- Type: {model_info.type}")
    print(f"- Type: {model_info.type}")
    print(f"- Format: {model_info.format}")
    print(f"- Format: {model_info.format}")
    if model_info.version != "0.0.0":
    if model_info.version != "0.0.0":
    print(f"- Version: {model_info.version}")
    print(f"- Version: {model_info.version}")
    print(f"- Description: {model_info.description}")
    print(f"- Description: {model_info.description}")
    print(f"- Path: {model_info.path}")
    print(f"- Path: {model_info.path}")
    print(f"- Size: {model_info.size_mb:.2f} MB")
    print(f"- Size: {model_info.size_mb:.2f} MB")
    print(
    print(
    f"- Capabilities: {', '.join(model_info.capabilities) if model_info.capabilities else 'None'}"
    f"- Capabilities: {', '.join(model_info.capabilities) if model_info.capabilities else 'None'}"
    )
    )
    print(f"- Created At: {model_info.created_at}")
    print(f"- Created At: {model_info.created_at}")
    print(f"- Last Updated: {model_info.updated_at}")
    print(f"- Last Updated: {model_info.updated_at}")


    # Performance metrics if available
    # Performance metrics if available
    if model_info.performance:
    if model_info.performance:
    print("\nPerformance Metrics:")
    print("\nPerformance Metrics:")
    for key, value in model_info.performance.items():
    for key, value in model_info.performance.items():
    print(f"- {key}: {value}")
    print(f"- {key}: {value}")


    return 0
    return 0


    def _load_config(self) -> Optional[ModelConfig]:
    def _load_config(self) -> Optional[ModelConfig]:
    """
    """
    Load the configuration.
    Load the configuration.
    """
    """
    config_path = self._get_arg("config")
    config_path = self._get_arg("config")


    if config_path:
    if config_path:
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    logger.error(f"Configuration file {config_path} not found")
    logger.error(f"Configuration file {config_path} not found")
    return None
    return None


    try:
    try:
    return ModelConfig.load(config_path)
    return ModelConfig.load(config_path)
except Exception as e:
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.error(f"Error loading configuration: {e}")
    return None
    return None


    return ModelConfig.get_default()
    return ModelConfig.get_default()




    class ServeRESTCommand(BaseCommand):
    class ServeRESTCommand(BaseCommand):
    """
    """
    Command for serving models via REST API.
    Command for serving models via REST API.
    """
    """


    description = "Serve models via a REST API"
    description = "Serve models via a REST API"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.
    """
    """
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument(
    parser.add_argument(
    "--model-id",
    "--model-id",
    help="ID of the model to serve (if not specified, all models will be available)",
    help="ID of the model to serve (if not specified, all models will be available)",
    )
    )
    parser.add_argument("--config", help="Path to a configuration file")
    parser.add_argument("--config", help="Path to a configuration file")


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.
    """
    """
    logger.info("REST server is not implemented yet")
    logger.info("REST server is not implemented yet")
    return 1
    return 1


    def _load_config(self) -> Optional[ModelConfig]:
    def _load_config(self) -> Optional[ModelConfig]:
    """
    """
    Load the configuration.
    Load the configuration.
    """
    """
    config_path = self._get_arg("config")
    config_path = self._get_arg("config")


    if config_path:
    if config_path:
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    logger.error(f"Configuration file {config_path} not found")
    logger.error(f"Configuration file {config_path} not found")
    return None
    return None


    try:
    try:
    return ModelConfig.load(config_path)
    return ModelConfig.load(config_path)
except Exception as e:
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.error(f"Error loading configuration: {e}")
    return None
    return None


    return ModelConfig.get_default()
    return ModelConfig.get_default()




    class ServeGRPCCommand(BaseCommand):
    class ServeGRPCCommand(BaseCommand):
    """
    """
    Command for serving models via gRPC.
    Command for serving models via gRPC.
    """
    """


    description = "Serve models via a gRPC API"
    description = "Serve models via a gRPC API"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.
    """
    """
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=50051, help="Port to bind to")
    parser.add_argument("--port", type=int, default=50051, help="Port to bind to")
    parser.add_argument(
    parser.add_argument(
    "--model-id",
    "--model-id",
    help="ID of the model to serve (if not specified, all models will be available)",
    help="ID of the model to serve (if not specified, all models will be available)",
    )
    )
    parser.add_argument("--config", help="Path to a configuration file")
    parser.add_argument("--config", help="Path to a configuration file")


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.
    """
    """
    logger.info("gRPC server is not implemented yet")
    logger.info("gRPC server is not implemented yet")
    return 1
    return 1


    def _load_config(self) -> Optional[ModelConfig]:
    def _load_config(self) -> Optional[ModelConfig]:
    """
    """
    Load the configuration.
    Load the configuration.
    """
    """
    config_path = self._get_arg("config")
    config_path = self._get_arg("config")


    if config_path:
    if config_path:
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    logger.error(f"Configuration file {config_path} not found")
    logger.error(f"Configuration file {config_path} not found")
    return None
    return None


    try:
    try:
    return ModelConfig.load(config_path)
    return ModelConfig.load(config_path)
except Exception as e:
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.error(f"Error loading configuration: {e}")
    return None
    return None


    return ModelConfig.get_default()
    return ModelConfig.get_default()




    class OptimizeCommand(BaseCommand):
    class OptimizeCommand(BaseCommand):
    """
    """
    Command for optimizing models.
    Command for optimizing models.
    """
    """


    description = "Optimize a model"
    description = "Optimize a model"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.
    """
    """
    parser.add_argument(
    parser.add_argument(
    "--model-id", required=True, help="ID of the model to optimize"
    "--model-id", required=True, help="ID of the model to optimize"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--method",
    "--method",
    choices=["quantize", "prune", "distill"],
    choices=["quantize", "prune", "distill"],
    default="quantize",
    default="quantize",
    help="Optimization method",
    help="Optimization method",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--output-dir", help="Directory to save the optimized model"
    "--output-dir", help="Directory to save the optimized model"
    )
    )
    parser.add_argument("--config", help="Path to a configuration file")
    parser.add_argument("--config", help="Path to a configuration file")


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.
    """
    """
    logger.info("Model optimization is not implemented yet")
    logger.info("Model optimization is not implemented yet")
    return 1
    return 1


    def _load_config(self) -> Optional[ModelConfig]:
    def _load_config(self) -> Optional[ModelConfig]:
    """
    """
    Load the configuration.
    Load the configuration.
    """
    """
    config_path = self._get_arg("config")
    config_path = self._get_arg("config")


    if config_path:
    if config_path:
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    logger.error(f"Configuration file {config_path} not found")
    logger.error(f"Configuration file {config_path} not found")
    return None
    return None


    try:
    try:
    return ModelConfig.load(config_path)
    return ModelConfig.load(config_path)
except Exception as e:
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.error(f"Error loading configuration: {e}")
    return None
    return None


    return ModelConfig.get_default()
    return ModelConfig.get_default()




    class BenchmarkCommand(BaseCommand):
    class BenchmarkCommand(BaseCommand):
    """
    """
    Command for benchmarking models.
    Command for benchmarking models.
    """
    """


    description = "Benchmark a model"
    description = "Benchmark a model"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.
    """
    """
    parser.add_argument(
    parser.add_argument(
    "--model-id", required=True, help="ID of the model to benchmark"
    "--model-id", required=True, help="ID of the model to benchmark"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--iterations", type=int, default=10, help="Number of iterations"
    "--iterations", type=int, default=10, help="Number of iterations"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--input-text", default="Hello, world!", help="Input text for benchmarking"
    "--input-text", default="Hello, world!", help="Input text for benchmarking"
    )
    )
    parser.add_argument("--config", help="Path to a configuration file")
    parser.add_argument("--config", help="Path to a configuration file")


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.
    """
    """
    logger.info("Model benchmarking is not implemented yet")
    logger.info("Model benchmarking is not implemented yet")
    return 1
    return 1


    def _load_config(self) -> Optional[ModelConfig]:
    def _load_config(self) -> Optional[ModelConfig]:
    """
    """
    Load the configuration.
    Load the configuration.
    """
    """
    config_path = self._get_arg("config")
    config_path = self._get_arg("config")


    if config_path:
    if config_path:
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    logger.error(f"Configuration file {config_path} not found")
    logger.error(f"Configuration file {config_path} not found")
    return None
    return None


    try:
    try:
    return ModelConfig.load(config_path)
    return ModelConfig.load(config_path)
except Exception as e:
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.error(f"Error loading configuration: {e}")
    return None
    return None


    return ModelConfig.get_default()
    return ModelConfig.get_default()




    class DeployCommand(BaseCommand):
    class DeployCommand(BaseCommand):
    """
    """
    Command for deploying models.
    Command for deploying models.
    """
    """


    description = "Deploy a model"
    description = "Deploy a model"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.
    """
    """
    parser.add_argument(
    parser.add_argument(
    "--model-id", required=True, help="ID of the model to deploy"
    "--model-id", required=True, help="ID of the model to deploy"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--target",
    "--target",
    choices=["docker", "kubernetes", "aws", "azure", "gcp"],
    choices=["docker", "kubernetes", "aws", "azure", "gcp"],
    default="docker",
    default="docker",
    help="Deployment target",
    help="Deployment target",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--output-dir", help="Directory to save deployment artifacts"
    "--output-dir", help="Directory to save deployment artifacts"
    )
    )
    parser.add_argument("--config", help="Path to a configuration file")
    parser.add_argument("--config", help="Path to a configuration file")


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.
    """
    """
    logger.info("Model deployment is not implemented yet")
    logger.info("Model deployment is not implemented yet")
    return 1
    return 1


    def _load_config(self) -> Optional[ModelConfig]:
    def _load_config(self) -> Optional[ModelConfig]:
    """
    """
    Load the configuration.
    Load the configuration.
    """
    """
    config_path = self._get_arg("config")
    config_path = self._get_arg("config")


    if config_path:
    if config_path:
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    logger.error(f"Configuration file {config_path} not found")
    logger.error(f"Configuration file {config_path} not found")
    return None
    return None


    try:
    try:
    return ModelConfig.load(config_path)
    return ModelConfig.load(config_path)
except Exception as e:
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.error(f"Error loading configuration: {e}")
    return None
    return None


    return ModelConfig.get_default()
    return ModelConfig.get_default()




    class ValidateCommand(BaseCommand):
    class ValidateCommand(BaseCommand):
    """
    """
    Command for validating models.
    Command for validating models.
    """
    """


    description = "Validate a model"
    description = "Validate a model"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.
    """
    """
    parser.add_argument(
    parser.add_argument(
    "--model-id", required=True, help="ID of the model to validate"
    "--model-id", required=True, help="ID of the model to validate"
    )
    )
    parser.add_argument("--test-data", help="Path to test data")
    parser.add_argument("--test-data", help="Path to test data")
    parser.add_argument("--config", help="Path to a configuration file")
    parser.add_argument("--config", help="Path to a configuration file")


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.
    """
    """
    logger.info("Model validation is not implemented yet")
    logger.info("Model validation is not implemented yet")
    return 1
    return 1


    def _load_config(self) -> Optional[ModelConfig]:
    def _load_config(self) -> Optional[ModelConfig]:
    """
    """
    Load the configuration.
    Load the configuration.
    """
    """
    config_path = self._get_arg("config")
    config_path = self._get_arg("config")


    if config_path:
    if config_path:
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    logger.error(f"Configuration file {config_path} not found")
    logger.error(f"Configuration file {config_path} not found")
    return None
    return None


    try:
    try:
    return ModelConfig.load(config_path)
    return ModelConfig.load(config_path)
except Exception as e:
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.error(f"Error loading configuration: {e}")
    return None
    return None


    return ModelConfig.get_default()
    return ModelConfig.get_default()




    class VersionCommand(BaseCommand):
    class VersionCommand(BaseCommand):
    """
    """
    Command for managing model versions.
    Command for managing model versions.
    """
    """


    description = "Manage model versions"
    description = "Manage model versions"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.
    """
    """
    subparsers = parser.add_subparsers(
    subparsers = parser.add_subparsers(
    dest="version_command", help="Version management command"
    dest="version_command", help="Version management command"
    )
    )


    # Create a new version
    # Create a new version
    create_parser = subparsers.add_parser(
    create_parser = subparsers.add_parser(
    "create", help="Create a new version for a model"
    "create", help="Create a new version for a model"
    )
    )
    create_parser.add_argument("--model-id", required=True, help="ID of the model")
    create_parser.add_argument("--model-id", required=True, help="ID of the model")
    create_parser.add_argument(
    create_parser.add_argument(
    "--version",
    "--version",
    required=True,
    required=True,
    help="Version string in semver format (e.g., '1.0.0')",
    help="Version string in semver format (e.g., '1.0.0')",
    )
    )
    create_parser.add_argument(
    create_parser.add_argument(
    "--features", nargs="*", help="Features supported by this version"
    "--features", nargs="*", help="Features supported by this version"
    )
    )
    create_parser.add_argument(
    create_parser.add_argument(
    "--dependencies",
    "--dependencies",
    nargs="*",
    nargs="*",
    help="Dependencies in the format 'name:version'",
    help="Dependencies in the format 'name:version'",
    )
    )
    create_parser.add_argument(
    create_parser.add_argument(
    "--compatibility",
    "--compatibility",
    nargs="*",
    nargs="*",
    help="Compatible versions in the format 'model_id:version'",
    help="Compatible versions in the format 'model_id:version'",
    )
    )
    create_parser.add_argument(
    create_parser.add_argument(
    "--metadata-file", help="Path to a JSON file with additional metadata"
    "--metadata-file", help="Path to a JSON file with additional metadata"
    )
    )
    create_parser.add_argument("--config", help="Path to a configuration file")
    create_parser.add_argument("--config", help="Path to a configuration file")


    # List versions
    # List versions
    list_parser = subparsers.add_parser("list", help="List versions of a model")
    list_parser = subparsers.add_parser("list", help="List versions of a model")
    list_parser.add_argument("--model-id", required=True, help="ID of the model")
    list_parser.add_argument("--model-id", required=True, help="ID of the model")
    list_parser.add_argument(
    list_parser.add_argument(
    "--format", choices=["text", "json"], default="text", help="Output format"
    "--format", choices=["text", "json"], default="text", help="Output format"
    )
    )
    list_parser.add_argument("--config", help="Path to a configuration file")
    list_parser.add_argument("--config", help="Path to a configuration file")


    # Get version info
    # Get version info
    info_parser = subparsers.add_parser(
    info_parser = subparsers.add_parser(
    "info", help="Get information about a specific version"
    "info", help="Get information about a specific version"
    )
    )
    info_parser.add_argument("--model-id", required=True, help="ID of the model")
    info_parser.add_argument("--model-id", required=True, help="ID of the model")
    info_parser.add_argument("--version", required=True, help="Version string")
    info_parser.add_argument("--version", required=True, help="Version string")
    info_parser.add_argument(
    info_parser.add_argument(
    "--format", choices=["text", "json"], default="text", help="Output format"
    "--format", choices=["text", "json"], default="text", help="Output format"
    )
    )
    info_parser.add_argument("--config", help="Path to a configuration file")
    info_parser.add_argument("--config", help="Path to a configuration file")


    # Check compatibility
    # Check compatibility
    check_parser = subparsers.add_parser(
    check_parser = subparsers.add_parser(
    "check-compatibility", help="Check if two model versions are compatible"
    "check-compatibility", help="Check if two model versions are compatible"
    )
    )
    check_parser.add_argument(
    check_parser.add_argument(
    "--model-id1", required=True, help="ID of the first model"
    "--model-id1", required=True, help="ID of the first model"
    )
    )
    check_parser.add_argument(
    check_parser.add_argument(
    "--version1", required=True, help="Version of the first model"
    "--version1", required=True, help="Version of the first model"
    )
    )
    check_parser.add_argument(
    check_parser.add_argument(
    "--model-id2", required=True, help="ID of the second model"
    "--model-id2", required=True, help="ID of the second model"
    )
    )
    check_parser.add_argument(
    check_parser.add_argument(
    "--version2", required=True, help="Version of the second model"
    "--version2", required=True, help="Version of the second model"
    )
    )
    check_parser.add_argument("--config", help="Path to a configuration file")
    check_parser.add_argument("--config", help="Path to a configuration file")


    # Load a specific version
    # Load a specific version
    load_parser = subparsers.add_parser(
    load_parser = subparsers.add_parser(
    "load", help="Load a specific version of a model"
    "load", help="Load a specific version of a model"
    )
    )
    load_parser.add_argument("--model-id", required=True, help="ID of the model")
    load_parser.add_argument("--model-id", required=True, help="ID of the model")
    load_parser.add_argument("--version", required=True, help="Version string")
    load_parser.add_argument("--version", required=True, help="Version string")
    load_parser.add_argument("--config", help="Path to a configuration file")
    load_parser.add_argument("--config", help="Path to a configuration file")


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.
    """
    """
    # Check if a subcommand was specified
    # Check if a subcommand was specified
    version_command = self._get_arg("version_command")
    version_command = self._get_arg("version_command")
    if not version_command:
    if not version_command:
    logger.error("No version command specified")
    logger.error("No version command specified")
    return 1
    return 1


    # Load configuration
    # Load configuration
    config = self._load_config()
    config = self._load_config()
    if not config:
    if not config:
    return 1
    return 1


    # Create model manager
    # Create model manager
    model_manager = ModelManager(config)
    model_manager = ModelManager(config)


    # Execute the subcommand
    # Execute the subcommand
    if version_command == "create":
    if version_command == "create":
    return self._create_version(model_manager)
    return self._create_version(model_manager)
    elif version_command == "list":
    elif version_command == "list":
    return self._list_versions(model_manager)
    return self._list_versions(model_manager)
    elif version_command == "info":
    elif version_command == "info":
    return self._get_version_info(model_manager)
    return self._get_version_info(model_manager)
    elif version_command == "check-compatibility":
    elif version_command == "check-compatibility":
    return self._check_compatibility(model_manager)
    return self._check_compatibility(model_manager)
    elif version_command == "load":
    elif version_command == "load":
    return self._load_version(model_manager)
    return self._load_version(model_manager)
    else:
    else:
    logger.error(f"Unknown version command: {version_command}")
    logger.error(f"Unknown version command: {version_command}")
    return 1
    return 1


    def _create_version(self, model_manager: ModelManager) -> int:
    def _create_version(self, model_manager: ModelManager) -> int:
    """
    """
    Create a new version for a model.
    Create a new version for a model.
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id", "version"]):
    if not self._validate_args(["model_id", "version"]):
    return 1
    return 1


    # Get model info
    # Get model info
    model_id = self._get_arg("model_id")
    model_id = self._get_arg("model_id")
    model_info = model_manager.get_model_info(model_id)
    model_info = model_manager.get_model_info(model_id)


    if not model_info:
    if not model_info:
    logger.error(f"Model with ID {model_id} not found")
    logger.error(f"Model with ID {model_id} not found")
    return 1
    return 1


    # Parse dependencies
    # Parse dependencies
    dependencies = {}
    dependencies = {}
    if self._get_arg("dependencies"):
    if self._get_arg("dependencies"):
    for dep in self._get_arg("dependencies"):
    for dep in self._get_arg("dependencies"):
    try:
    try:
    name, version = dep.split(":", 1)
    name, version = dep.split(":", 1)
    dependencies[name] = version
    dependencies[name] = version
except ValueError:
except ValueError:
    logger.error(f"Invalid dependency format: {dep}")
    logger.error(f"Invalid dependency format: {dep}")
    return 1
    return 1


    # Load metadata from file if specified
    # Load metadata from file if specified
    metadata = {}
    metadata = {}
    if self._get_arg("metadata_file"):
    if self._get_arg("metadata_file"):
    try:
    try:
    with open(self._get_arg("metadata_file"), "r") as f:
    with open(self._get_arg("metadata_file"), "r") as f:
    metadata = json.load(f)
    metadata = json.load(f)
except Exception as e:
except Exception as e:
    logger.error(f"Error loading metadata file: {e}")
    logger.error(f"Error loading metadata file: {e}")
    return 1
    return 1


    try:
    try:
    # Create version
    # Create version
    version_obj = model_manager.create_model_version(
    version_obj = model_manager.create_model_version(
    model_id=model_id,
    model_id=model_id,
    version=self._get_arg("version"),
    version=self._get_arg("version"),
    features=self._get_arg("features"),
    features=self._get_arg("features"),
    dependencies=dependencies,
    dependencies=dependencies,
    compatibility=self._get_arg("compatibility"),
    compatibility=self._get_arg("compatibility"),
    metadata=metadata,
    metadata=metadata,
    )
    )


    logger.info(f"Created version {version_obj.version} for model {model_id}")
    logger.info(f"Created version {version_obj.version} for model {model_id}")
    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error creating version: {e}")
    logger.error(f"Error creating version: {e}")
    return 1
    return 1


    def _list_versions(self, model_manager: ModelManager) -> int:
    def _list_versions(self, model_manager: ModelManager) -> int:
    """
    """
    List versions of a model.
    List versions of a model.
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id"]):
    if not self._validate_args(["model_id"]):
    return 1
    return 1


    # Get model info
    # Get model info
    model_id = self._get_arg("model_id")
    model_id = self._get_arg("model_id")
    model_info = model_manager.get_model_info(model_id)
    model_info = model_manager.get_model_info(model_id)


    if not model_info:
    if not model_info:
    logger.error(f"Model with ID {model_id} not found")
    logger.error(f"Model with ID {model_id} not found")
    return 1
    return 1


    # Get versions
    # Get versions
    try:
    try:
    versions = model_manager.get_model_versions(model_id)
    versions = model_manager.get_model_versions(model_id)


    # Format output
    # Format output
    if self._get_arg("format") == "json":
    if self._get_arg("format") == "json":
    # JSON output
    # JSON output
    version_data = [v.to_dict() for v in versions]
    version_data = [v.to_dict() for v in versions]
    print(json.dumps(version_data, indent=2))
    print(json.dumps(version_data, indent=2))
    else:
    else:
    # Text output
    # Text output
    print(f"Versions for model {model_info.name} ({model_id}):")
    print(f"Versions for model {model_info.name} ({model_id}):")


    if not versions:
    if not versions:
    print("  No versions found")
    print("  No versions found")
    else:
    else:
    # Get latest version
    # Get latest version
    latest_version = model_manager.get_latest_version(model_id)
    latest_version = model_manager.get_latest_version(model_id)
    latest_version_str = (
    latest_version_str = (
    latest_version.version if latest_version else None
    latest_version.version if latest_version else None
    )
    )


    for version in versions:
    for version in versions:
    # Mark latest version
    # Mark latest version
    latest_marker = (
    latest_marker = (
    " (latest)" if version.version == latest_version_str else ""
    " (latest)" if version.version == latest_version_str else ""
    )
    )
    print(f"- {version.version}{latest_marker}")
    print(f"- {version.version}{latest_marker}")
    print(f"  Timestamp: {version.timestamp}")
    print(f"  Timestamp: {version.timestamp}")


    # Print features
    # Print features
    if version.features:
    if version.features:
    print(f"  Features: {', '.join(version.features)}")
    print(f"  Features: {', '.join(version.features)}")


    # Print hash
    # Print hash
    if version.hash_value:
    if version.hash_value:
    print(
    print(
    f"  Hash: {version.hash_value[:8]}..."
    f"  Hash: {version.hash_value[:8]}..."
    )  # Show first 8 chars
    )  # Show first 8 chars


    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error listing versions: {e}")
    logger.error(f"Error listing versions: {e}")
    return 1
    return 1


    def _get_version_info(self, model_manager: ModelManager) -> int:
    def _get_version_info(self, model_manager: ModelManager) -> int:
    """
    """
    Get information about a specific version.
    Get information about a specific version.
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id", "version"]):
    if not self._validate_args(["model_id", "version"]):
    return 1
    return 1


    # Get model info
    # Get model info
    model_id = self._get_arg("model_id")
    model_id = self._get_arg("model_id")
    model_info = model_manager.get_model_info(model_id)
    model_info = model_manager.get_model_info(model_id)


    if not model_info:
    if not model_info:
    logger.error(f"Model with ID {model_id} not found")
    logger.error(f"Model with ID {model_id} not found")
    return 1
    return 1


    # Get version
    # Get version
    try:
    try:
    version = model_manager.versioned_manager.get_version(
    version = model_manager.versioned_manager.get_version(
    model_id, self._get_arg("version")
    model_id, self._get_arg("version")
    )
    )


    if not version:
    if not version:
    logger.error(
    logger.error(
    f"Version {self._get_arg('version')} not found for model {model_id}"
    f"Version {self._get_arg('version')} not found for model {model_id}"
    )
    )
    return 1
    return 1


    # Format output
    # Format output
    if self._get_arg("format") == "json":
    if self._get_arg("format") == "json":
    # JSON output
    # JSON output
    print(json.dumps(version.to_dict(), indent=2))
    print(json.dumps(version.to_dict(), indent=2))
    else:
    else:
    # Text output
    # Text output
    print(f"Version: {version.version}")
    print(f"Version: {version.version}")
    print(f"Model: {model_info.name} ({model_id})")
    print(f"Model: {model_info.name} ({model_id})")
    print(f"Timestamp: {version.timestamp}")
    print(f"Timestamp: {version.timestamp}")


    # Features
    # Features
    if version.features:
    if version.features:
    print(f"Features: {', '.join(version.features)}")
    print(f"Features: {', '.join(version.features)}")


    # Dependencies
    # Dependencies
    if version.dependencies:
    if version.dependencies:
    print("\nDependencies:")
    print("\nDependencies:")
    for name, ver in version.dependencies.items():
    for name, ver in version.dependencies.items():
    print(f"- {name}: {ver}")
    print(f"- {name}: {ver}")


    # Compatibility
    # Compatibility
    if version.is_compatible_with:
    if version.is_compatible_with:
    print("\nExplicitly compatible with:")
    print("\nExplicitly compatible with:")
    for comp_version in version.is_compatible_with:
    for comp_version in version.is_compatible_with:
    print(f"- {comp_version}")
    print(f"- {comp_version}")


    # Hash value
    # Hash value
    if version.hash_value:
    if version.hash_value:
    print(f"\nHash: {version.hash_value}")
    print(f"\nHash: {version.hash_value}")


    # Metadata
    # Metadata
    if version.metadata:
    if version.metadata:
    print("\nMetadata:")
    print("\nMetadata:")
    for key, value in version.metadata.items():
    for key, value in version.metadata.items():
    print(f"- {key}: {value}")
    print(f"- {key}: {value}")


    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error getting version info: {e}")
    logger.error(f"Error getting version info: {e}")
    return 1
    return 1


    def _check_compatibility(self, model_manager: ModelManager) -> int:
    def _check_compatibility(self, model_manager: ModelManager) -> int:
    """
    """
    Check if two model versions are compatible.
    Check if two model versions are compatible.
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id1", "version1", "model_id2", "version2"]):
    if not self._validate_args(["model_id1", "version1", "model_id2", "version2"]):
    return 1
    return 1


    try:
    try:
    # Check compatibility
    # Check compatibility
    compatible = model_manager.check_version_compatibility(
    compatible = model_manager.check_version_compatibility(
    self._get_arg("model_id1"),
    self._get_arg("model_id1"),
    self._get_arg("version1"),
    self._get_arg("version1"),
    self._get_arg("model_id2"),
    self._get_arg("model_id2"),
    self._get_arg("version2"),
    self._get_arg("version2"),
    )
    )


    if compatible:
    if compatible:
    print("Models are compatible")
    print("Models are compatible")
    else:
    else:
    print("Models are NOT compatible")
    print("Models are NOT compatible")


    return 0 if compatible else 2  # Use 2 as exit code for incompatible models
    return 0 if compatible else 2  # Use 2 as exit code for incompatible models


except Exception as e:
except Exception as e:
    logger.error(f"Error checking compatibility: {e}")
    logger.error(f"Error checking compatibility: {e}")
    return 1
    return 1


    def _load_version(self, model_manager: ModelManager) -> int:
    def _load_version(self, model_manager: ModelManager) -> int:
    """
    """
    Load a specific version of a model.
    Load a specific version of a model.
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id", "version"]):
    if not self._validate_args(["model_id", "version"]):
    return 1
    return 1


    try:
    try:
    # Load model
    # Load model
    model = model_manager.load_model(
    model = model_manager.load_model(
    self._get_arg("model_id"), version=self._get_arg("version")
    self._get_arg("model_id"), version=self._get_arg("version")
    )
    )


    logger.info(f"Successfully loaded model version {self._get_arg('version')}")
    logger.info(f"Successfully loaded model version {self._get_arg('version')}")


    # Basic info about the loaded model (type-specific)
    # Basic info about the loaded model (type-specific)
    print("Loaded model information:")
    print("Loaded model information:")
    print(f"- Type: {type(model).__name__}")
    print(f"- Type: {type(model).__name__}")


    # Basic inference test
    # Basic inference test
    if hasattr(model, "generate"):
    if hasattr(model, "generate"):
    print("Model supports generation. Example output:")
    print("Model supports generation. Example output:")
    try:
    try:
    # Use a very short timeout to avoid long waits
    # Use a very short timeout to avoid long waits




    def timeout_handler(signum, frame):
    def timeout_handler(signum, frame):
    raise TimeoutError("Generation timed out")
    raise TimeoutError("Generation timed out")


    # Set timeout to 5 seconds
    # Set timeout to 5 seconds
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)
    signal.alarm(5)


    output = model.generate("Hello, world!")[
    output = model.generate("Hello, world!")[
    :100
    :100
    ]  # Limit output length
    ]  # Limit output length
    print("  Input: 'Hello, world!'")
    print("  Input: 'Hello, world!'")
    print(f"  Output: '{output}'")
    print(f"  Output: '{output}'")


    # Cancel the timeout
    # Cancel the timeout
    signal.alarm(0)
    signal.alarm(0)
except Exception as e:
except Exception as e:
    print(f"  Generation test failed: {e}")
    print(f"  Generation test failed: {e}")


    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error loading model version: {e}")
    logger.error(f"Error loading model version: {e}")
    return 1
    return 1


    def _load_config(self) -> Optional[ModelConfig]:
    def _load_config(self) -> Optional[ModelConfig]:
    """
    """
    Load the configuration.
    Load the configuration.
    """
    """
    config_path = self._get_arg("config")
    config_path = self._get_arg("config")


    if config_path:
    if config_path:
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    logger.error(f"Configuration file {config_path} not found")
    logger.error(f"Configuration file {config_path} not found")
    return None
    return None


    try:
    try:
    return ModelConfig.load(config_path)
    return ModelConfig.load(config_path)
except Exception as e:
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.error(f"Error loading configuration: {e}")
    return None
    return None


    return ModelConfig.get_default()
    return ModelConfig.get_default()




    class PerformanceCommand(BaseCommand):
    class PerformanceCommand(BaseCommand):
    """
    """
    Command for managing model performance metrics.
    Command for managing model performance metrics.
    """
    """


    description = "Monitor and analyze model performance"
    description = "Monitor and analyze model performance"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.
    """
    """
    subparsers = parser.add_subparsers(
    subparsers = parser.add_subparsers(
    dest="perf_command", help="Performance monitoring command"
    dest="perf_command", help="Performance monitoring command"
    )
    )


    # Generate performance report
    # Generate performance report
    report_parser = subparsers.add_parser(
    report_parser = subparsers.add_parser(
    "report", help="Generate a performance report for a model"
    "report", help="Generate a performance report for a model"
    )
    )
    report_parser.add_argument("--model-id", required=True, help="ID of the model")
    report_parser.add_argument("--model-id", required=True, help="ID of the model")
    report_parser.add_argument(
    report_parser.add_argument(
    "--model-name",
    "--model-name",
    help="Name of the model (defaults to model ID if not provided)",
    help="Name of the model (defaults to model ID if not provided)",
    )
    )
    report_parser.add_argument(
    report_parser.add_argument(
    "--days",
    "--days",
    type=int,
    type=int,
    default=30,
    default=30,
    help="Number of days to include in the report",
    help="Number of days to include in the report",
    )
    )
    report_parser.add_argument(
    report_parser.add_argument(
    "--format",
    "--format",
    choices=["text", "json", "csv"],
    choices=["text", "json", "csv"],
    default="text",
    default="text",
    help="Output format",
    help="Output format",
    )
    )
    report_parser.add_argument("--output", help="Path to save the report to")
    report_parser.add_argument("--output", help="Path to save the report to")
    report_parser.add_argument("--config", help="Path to a configuration file")
    report_parser.add_argument("--config", help="Path to a configuration file")


    # Compare model performance
    # Compare model performance
    compare_parser = subparsers.add_parser(
    compare_parser = subparsers.add_parser(
    "compare", help="Compare the performance of multiple models"
    "compare", help="Compare the performance of multiple models"
    )
    )
    compare_parser.add_argument(
    compare_parser.add_argument(
    "--model-ids", required=True, nargs="+", help="IDs of the models to compare"
    "--model-ids", required=True, nargs="+", help="IDs of the models to compare"
    )
    )
    compare_parser.add_argument(
    compare_parser.add_argument(
    "--model-names",
    "--model-names",
    nargs="+",
    nargs="+",
    help="Names of the models (defaults to model IDs if not provided)",
    help="Names of the models (defaults to model IDs if not provided)",
    )
    )
    compare_parser.add_argument(
    compare_parser.add_argument(
    "--format",
    "--format",
    choices=["text", "json", "csv"],
    choices=["text", "json", "csv"],
    default="text",
    default="text",
    help="Output format",
    help="Output format",
    )
    )
    compare_parser.add_argument("--output", help="Path to save the comparison to")
    compare_parser.add_argument("--output", help="Path to save the comparison to")
    compare_parser.add_argument("--config", help="Path to a configuration file")
    compare_parser.add_argument("--config", help="Path to a configuration file")


    # Visualize performance metrics
    # Visualize performance metrics
    visualize_parser = subparsers.add_parser(
    visualize_parser = subparsers.add_parser(
    "visualize", help="Generate visualizations of model performance metrics"
    "visualize", help="Generate visualizations of model performance metrics"
    )
    )
    visualize_parser.add_argument(
    visualize_parser.add_argument(
    "--model-id", required=True, help="ID of the model"
    "--model-id", required=True, help="ID of the model"
    )
    )
    visualize_parser.add_argument(
    visualize_parser.add_argument(
    "--metrics",
    "--metrics",
    nargs="+",
    nargs="+",
    default=[
    default=[
    "total_time",
    "total_time",
    "latency_ms",
    "latency_ms",
    "tokens_per_second",
    "tokens_per_second",
    "memory_usage_mb",
    "memory_usage_mb",
    ],
    ],
    help="Metrics to visualize",
    help="Metrics to visualize",
    )
    )
    visualize_parser.add_argument(
    visualize_parser.add_argument(
    "--days",
    "--days",
    type=int,
    type=int,
    default=30,
    default=30,
    help="Number of days to include in the visualization",
    help="Number of days to include in the visualization",
    )
    )
    visualize_parser.add_argument(
    visualize_parser.add_argument(
    "--output-dir", help="Directory to save the visualizations to"
    "--output-dir", help="Directory to save the visualizations to"
    )
    )
    visualize_parser.add_argument("--config", help="Path to a configuration file")
    visualize_parser.add_argument("--config", help="Path to a configuration file")


    # Export metrics to CSV
    # Export metrics to CSV
    export_parser = subparsers.add_parser(
    export_parser = subparsers.add_parser(
    "export", help="Export performance metrics to CSV"
    "export", help="Export performance metrics to CSV"
    )
    )
    export_parser.add_argument("--model-id", required=True, help="ID of the model")
    export_parser.add_argument("--model-id", required=True, help="ID of the model")
    export_parser.add_argument("--output", help="Path to save the CSV file to")
    export_parser.add_argument("--output", help="Path to save the CSV file to")
    export_parser.add_argument("--config", help="Path to a configuration file")
    export_parser.add_argument("--config", help="Path to a configuration file")


    # Set performance alert threshold
    # Set performance alert threshold
    alert_parser = subparsers.add_parser(
    alert_parser = subparsers.add_parser(
    "set-alert", help="Set an alert threshold for a model metric"
    "set-alert", help="Set an alert threshold for a model metric"
    )
    )
    alert_parser.add_argument("--model-id", required=True, help="ID of the model")
    alert_parser.add_argument("--model-id", required=True, help="ID of the model")
    alert_parser.add_argument(
    alert_parser.add_argument(
    "--metric",
    "--metric",
    required=True,
    required=True,
    choices=[
    choices=[
    "latency_ms",
    "latency_ms",
    "memory_usage_mb",
    "memory_usage_mb",
    "tokens_per_second",
    "tokens_per_second",
    "time_to_first_token",
    "time_to_first_token",
    "cpu_percent",
    "cpu_percent",
    "gpu_percent",
    "gpu_percent",
    ],
    ],
    help="Metric to set alert for",
    help="Metric to set alert for",
    )
    )
    alert_parser.add_argument(
    alert_parser.add_argument(
    "--threshold", required=True, type=float, help="Threshold value"
    "--threshold", required=True, type=float, help="Threshold value"
    )
    )
    alert_parser.add_argument(
    alert_parser.add_argument(
    "--upper-bound",
    "--upper-bound",
    action="store_true",
    action="store_true",
    help="If set, alert when value exceeds threshold; otherwise alert when below",
    help="If set, alert when value exceeds threshold; otherwise alert when below",
    )
    )
    alert_parser.add_argument("--config", help="Path to a configuration file")
    alert_parser.add_argument("--config", help="Path to a configuration file")


    # Track a simple inference for performance monitoring
    # Track a simple inference for performance monitoring
    track_parser = subparsers.add_parser(
    track_parser = subparsers.add_parser(
    "track-inference",
    "track-inference",
    help="Track a simple inference run for performance monitoring",
    help="Track a simple inference run for performance monitoring",
    )
    )
    track_parser.add_argument("--model-id", required=True, help="ID of the model")
    track_parser.add_argument("--model-id", required=True, help="ID of the model")
    track_parser.add_argument(
    track_parser.add_argument(
    "--input", required=True, help="Input text for inference"
    "--input", required=True, help="Input text for inference"
    )
    )
    track_parser.add_argument(
    track_parser.add_argument(
    "--show-metrics", action="store_true", help="Show the resulting metrics"
    "--show-metrics", action="store_true", help="Show the resulting metrics"
    )
    )
    track_parser.add_argument("--config", help="Path to a configuration file")
    track_parser.add_argument("--config", help="Path to a configuration file")


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.
    """
    """
    # Check if a subcommand was specified
    # Check if a subcommand was specified
    perf_command = self._get_arg("perf_command")
    perf_command = self._get_arg("perf_command")
    if not perf_command:
    if not perf_command:
    logger.error("No performance command specified")
    logger.error("No performance command specified")
    return 1
    return 1


    # Load configuration
    # Load configuration
    config = self._load_config()
    config = self._load_config()
    if not config:
    if not config:
    return 1
    return 1


    # Create model manager and performance monitor
    # Create model manager and performance monitor
    model_manager = ModelManager(config)
    model_manager = ModelManager(config)
    performance_monitor = PerformanceMonitor(config)
    performance_monitor = PerformanceMonitor(config)


    # Execute the subcommand
    # Execute the subcommand
    if perf_command == "report":
    if perf_command == "report":
    return self._generate_report(model_manager, performance_monitor)
    return self._generate_report(model_manager, performance_monitor)
    elif perf_command == "compare":
    elif perf_command == "compare":
    return self._compare_models(model_manager, performance_monitor)
    return self._compare_models(model_manager, performance_monitor)
    elif perf_command == "visualize":
    elif perf_command == "visualize":
    return self._visualize_metrics(model_manager, performance_monitor)
    return self._visualize_metrics(model_manager, performance_monitor)
    elif perf_command == "export":
    elif perf_command == "export":
    return self._export_metrics(model_manager, performance_monitor)
    return self._export_metrics(model_manager, performance_monitor)
    elif perf_command == "set-alert":
    elif perf_command == "set-alert":
    return self._set_alert(model_manager, performance_monitor)
    return self._set_alert(model_manager, performance_monitor)
    elif perf_command == "track-inference":
    elif perf_command == "track-inference":
    return self._track_inference(model_manager, performance_monitor)
    return self._track_inference(model_manager, performance_monitor)
    else:
    else:
    logger.error(f"Unknown performance command: {perf_command}")
    logger.error(f"Unknown performance command: {perf_command}")
    return 1
    return 1


    def _generate_report(
    def _generate_report(
    self, model_manager: ModelManager, performance_monitor: PerformanceMonitor
    self, model_manager: ModelManager, performance_monitor: PerformanceMonitor
    ) -> int:
    ) -> int:
    """
    """
    Generate a performance report for a model.
    Generate a performance report for a model.
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id"]):
    if not self._validate_args(["model_id"]):
    return 1
    return 1


    # Get model info
    # Get model info
    model_id = self._get_arg("model_id")
    model_id = self._get_arg("model_id")
    model_info = model_manager.get_model_info(model_id)
    model_info = model_manager.get_model_info(model_id)


    if not model_info:
    if not model_info:
    logger.error(f"Model with ID {model_id} not found")
    logger.error(f"Model with ID {model_id} not found")
    return 1
    return 1


    # Use model_name from args if provided, otherwise use model name from model_info
    # Use model_name from args if provided, otherwise use model name from model_info
    model_name = self._get_arg("model_name") or model_info.name or model_id
    model_name = self._get_arg("model_name") or model_info.name or model_id


    # Filter metrics by time range
    # Filter metrics by time range
    days = self._get_arg("days")
    days = self._get_arg("days")
    time_range = None
    time_range = None
    if days:
    if days:
    end_time = datetime.now()
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    start_time = end_time - timedelta(days=days)
    time_range = (start_time, end_time)
    time_range = (start_time, end_time)


    try:
    try:
    # Generate report
    # Generate report
    report = performance_monitor.generate_report(
    report = performance_monitor.generate_report(
    model_id=model_id,
    model_id=model_id,
    model_name=model_name,
    model_name=model_name,
    time_range=time_range,
    time_range=time_range,
    include_metrics=True,
    include_metrics=True,
    )
    )


    # Format output
    # Format output
    output_format = self._get_arg("format")
    output_format = self._get_arg("format")
    output_path = self._get_arg("output")
    output_path = self._get_arg("output")


    if output_format == "json":
    if output_format == "json":
    report_data = report.to_dict()
    report_data = report.to_dict()


    if output_path:
    if output_path:
    with open(output_path, "w") as f:
    with open(output_path, "w") as f:
    json.dump(report_data, f, indent=2)
    json.dump(report_data, f, indent=2)
    logger.info(f"Saved report to {output_path}")
    logger.info(f"Saved report to {output_path}")
    else:
    else:
    print(json.dumps(report_data, indent=2))
    print(json.dumps(report_data, indent=2))


    elif output_format == "csv":
    elif output_format == "csv":
    if not output_path:
    if not output_path:
    output_path = (
    output_path = (
    f"performance_report_{model_id}_{int(time.time())}.csv"
    f"performance_report_{model_id}_{int(time.time())}.csv"
    )
    )


    with open(output_path, "w", newline="") as f:
    with open(output_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer = csv.writer(f)


    # Write header
    # Write header
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Metric", "Value"])


    # Write model info
    # Write model info
    writer.writerow(["Model ID", report.model_id])
    writer.writerow(["Model ID", report.model_id])
    writer.writerow(["Model Name", report.model_name])
    writer.writerow(["Model Name", report.model_name])
    writer.writerow(["Report Generated", report.timestamp])
    writer.writerow(["Report Generated", report.timestamp])
    writer.writerow(["Number of Inferences", report.num_inferences])
    writer.writerow(["Number of Inferences", report.num_inferences])


    # Write time metrics
    # Write time metrics
    writer.writerow([])
    writer.writerow([])
    writer.writerow(["Time Metrics", ""])
    writer.writerow(["Time Metrics", ""])
    writer.writerow(
    writer.writerow(
    ["Average Inference Time (s)", report.avg_inference_time]
    ["Average Inference Time (s)", report.avg_inference_time]
    )
    )
    writer.writerow(
    writer.writerow(
    ["Min Inference Time (s)", report.min_inference_time]
    ["Min Inference Time (s)", report.min_inference_time]
    )
    )
    writer.writerow(
    writer.writerow(
    ["Max Inference Time (s)", report.max_inference_time]
    ["Max Inference Time (s)", report.max_inference_time]
    )
    )
    writer.writerow(
    writer.writerow(
    ["Median Inference Time (s)", report.median_inference_time]
    ["Median Inference Time (s)", report.median_inference_time]
    )
    )
    writer.writerow(
    writer.writerow(
    ["Standard Deviation (s)", report.stddev_inference_time]
    ["Standard Deviation (s)", report.stddev_inference_time]
    )
    )
    writer.writerow(["90th Percentile (s)", report.p90_inference_time])
    writer.writerow(["90th Percentile (s)", report.p90_inference_time])
    writer.writerow(["95th Percentile (s)", report.p95_inference_time])
    writer.writerow(["95th Percentile (s)", report.p95_inference_time])
    writer.writerow(["99th Percentile (s)", report.p99_inference_time])
    writer.writerow(["99th Percentile (s)", report.p99_inference_time])
    writer.writerow(["Average Latency (ms)", report.avg_latency_ms])
    writer.writerow(["Average Latency (ms)", report.avg_latency_ms])
    writer.writerow(
    writer.writerow(
    [
    [
    "Average Time to First Token (s)",
    "Average Time to First Token (s)",
    report.avg_time_to_first_token,
    report.avg_time_to_first_token,
    ]
    ]
    )
    )


    # Write token metrics
    # Write token metrics
    writer.writerow([])
    writer.writerow([])
    writer.writerow(["Token Metrics", ""])
    writer.writerow(["Token Metrics", ""])
    writer.writerow(["Total Input Tokens", report.total_input_tokens])
    writer.writerow(["Total Input Tokens", report.total_input_tokens])
    writer.writerow(["Total Output Tokens", report.total_output_tokens])
    writer.writerow(["Total Output Tokens", report.total_output_tokens])
    writer.writerow(["Average Input Tokens", report.avg_input_tokens])
    writer.writerow(["Average Input Tokens", report.avg_input_tokens])
    writer.writerow(["Average Output Tokens", report.avg_output_tokens])
    writer.writerow(["Average Output Tokens", report.avg_output_tokens])
    writer.writerow(
    writer.writerow(
    ["Average Tokens per Second", report.avg_tokens_per_second]
    ["Average Tokens per Second", report.avg_tokens_per_second]
    )
    )


    # Write memory metrics
    # Write memory metrics
    writer.writerow([])
    writer.writerow([])
    writer.writerow(["Memory Metrics", ""])
    writer.writerow(["Memory Metrics", ""])
    writer.writerow(
    writer.writerow(
    ["Average Memory Usage (MB)", report.avg_memory_usage_mb]
    ["Average Memory Usage (MB)", report.avg_memory_usage_mb]
    )
    )
    writer.writerow(
    writer.writerow(
    ["Max Memory Usage (MB)", report.max_memory_usage_mb]
    ["Max Memory Usage (MB)", report.max_memory_usage_mb]
    )
    )
    writer.writerow(
    writer.writerow(
    ["Average Peak CPU Memory (MB)", report.avg_peak_cpu_memory_mb]
    ["Average Peak CPU Memory (MB)", report.avg_peak_cpu_memory_mb]
    )
    )
    writer.writerow(
    writer.writerow(
    ["Average Peak GPU Memory (MB)", report.avg_peak_gpu_memory_mb]
    ["Average Peak GPU Memory (MB)", report.avg_peak_gpu_memory_mb]
    )
    )


    # Write system metrics
    # Write system metrics
    writer.writerow([])
    writer.writerow([])
    writer.writerow(["System Metrics", ""])
    writer.writerow(["System Metrics", ""])
    writer.writerow(["Average CPU Usage (%)", report.avg_cpu_percent])
    writer.writerow(["Average CPU Usage (%)", report.avg_cpu_percent])
    writer.writerow(["Average GPU Usage (%)", report.avg_gpu_percent])
    writer.writerow(["Average GPU Usage (%)", report.avg_gpu_percent])


    # Write quality metrics
    # Write quality metrics
    if (
    if (
    report.avg_perplexity > 0
    report.avg_perplexity > 0
    or report.avg_bleu_score > 0
    or report.avg_bleu_score > 0
    or report.avg_rouge_score > 0
    or report.avg_rouge_score > 0
    ):
    ):
    writer.writerow([])
    writer.writerow([])
    writer.writerow(["Quality Metrics", ""])
    writer.writerow(["Quality Metrics", ""])
    if report.avg_perplexity > 0:
    if report.avg_perplexity > 0:
    writer.writerow(
    writer.writerow(
    ["Average Perplexity", report.avg_perplexity]
    ["Average Perplexity", report.avg_perplexity]
    )
    )
    if report.avg_bleu_score > 0:
    if report.avg_bleu_score > 0:
    writer.writerow(
    writer.writerow(
    ["Average BLEU Score", report.avg_bleu_score]
    ["Average BLEU Score", report.avg_bleu_score]
    )
    )
    if report.avg_rouge_score > 0:
    if report.avg_rouge_score > 0:
    writer.writerow(
    writer.writerow(
    ["Average ROUGE Score", report.avg_rouge_score]
    ["Average ROUGE Score", report.avg_rouge_score]
    )
    )


    # Write cost metrics
    # Write cost metrics
    if report.total_estimated_cost > 0:
    if report.total_estimated_cost > 0:
    writer.writerow([])
    writer.writerow([])
    writer.writerow(["Cost Metrics", ""])
    writer.writerow(["Cost Metrics", ""])
    writer.writerow(
    writer.writerow(
    [
    [
    "Total Estimated Cost",
    "Total Estimated Cost",
    f"{report.total_estimated_cost:.6f} {report.currency}",
    f"{report.total_estimated_cost:.6f} {report.currency}",
    ]
    ]
    )
    )
    writer.writerow(
    writer.writerow(
    [
    [
    "Average Cost per Inference",
    "Average Cost per Inference",
    f"{report.avg_cost_per_inference:.6f} {report.currency}",
    f"{report.avg_cost_per_inference:.6f} {report.currency}",
    ]
    ]
    )
    )


    logger.info(f"Saved report to {output_path}")
    logger.info(f"Saved report to {output_path}")


    else:  # text format
    else:  # text format
    print(
    print(
    f"Performance Report for {report.model_name} (ID: {report.model_id})"
    f"Performance Report for {report.model_name} (ID: {report.model_id})"
    )
    )
    print(f"Report Generated: {report.timestamp}")
    print(f"Report Generated: {report.timestamp}")
    print(f"Number of Inferences: {report.num_inferences}")
    print(f"Number of Inferences: {report.num_inferences}")
    print("")
    print("")


    print("Time Metrics:")
    print("Time Metrics:")
    print(
    print(
    f"- Average Inference Time: {report.avg_inference_time:.4f} seconds"
    f"- Average Inference Time: {report.avg_inference_time:.4f} seconds"
    )
    )
    print(f"- Min Inference Time: {report.min_inference_time:.4f} seconds")
    print(f"- Min Inference Time: {report.min_inference_time:.4f} seconds")
    print(f"- Max Inference Time: {report.max_inference_time:.4f} seconds")
    print(f"- Max Inference Time: {report.max_inference_time:.4f} seconds")
    print(
    print(
    f"- Median Inference Time: {report.median_inference_time:.4f} seconds"
    f"- Median Inference Time: {report.median_inference_time:.4f} seconds"
    )
    )
    print(
    print(
    f"- Standard Deviation: {report.stddev_inference_time:.4f} seconds"
    f"- Standard Deviation: {report.stddev_inference_time:.4f} seconds"
    )
    )
    print(f"- 90th Percentile: {report.p90_inference_time:.4f} seconds")
    print(f"- 90th Percentile: {report.p90_inference_time:.4f} seconds")
    print(f"- 95th Percentile: {report.p95_inference_time:.4f} seconds")
    print(f"- 95th Percentile: {report.p95_inference_time:.4f} seconds")
    print(f"- 99th Percentile: {report.p99_inference_time:.4f} seconds")
    print(f"- 99th Percentile: {report.p99_inference_time:.4f} seconds")
    print(f"- Average Latency: {report.avg_latency_ms:.2f} ms")
    print(f"- Average Latency: {report.avg_latency_ms:.2f} ms")
    print(
    print(
    f"- Average Time to First Token: {report.avg_time_to_first_token:.4f} seconds"
    f"- Average Time to First Token: {report.avg_time_to_first_token:.4f} seconds"
    )
    )
    print("")
    print("")


    print("Token Metrics:")
    print("Token Metrics:")
    print(f"- Total Input Tokens: {report.total_input_tokens}")
    print(f"- Total Input Tokens: {report.total_input_tokens}")
    print(f"- Total Output Tokens: {report.total_output_tokens}")
    print(f"- Total Output Tokens: {report.total_output_tokens}")
    print(f"- Average Input Tokens: {report.avg_input_tokens:.2f}")
    print(f"- Average Input Tokens: {report.avg_input_tokens:.2f}")
    print(f"- Average Output Tokens: {report.avg_output_tokens:.2f}")
    print(f"- Average Output Tokens: {report.avg_output_tokens:.2f}")
    print(
    print(
    f"- Average Tokens per Second: {report.avg_tokens_per_second:.2f}"
    f"- Average Tokens per Second: {report.avg_tokens_per_second:.2f}"
    )
    )
    print("")
    print("")


    print("Memory Metrics:")
    print("Memory Metrics:")
    print(f"- Average Memory Usage: {report.avg_memory_usage_mb:.2f} MB")
    print(f"- Average Memory Usage: {report.avg_memory_usage_mb:.2f} MB")
    print(f"- Max Memory Usage: {report.max_memory_usage_mb:.2f} MB")
    print(f"- Max Memory Usage: {report.max_memory_usage_mb:.2f} MB")
    print(
    print(
    f"- Average Peak CPU Memory: {report.avg_peak_cpu_memory_mb:.2f} MB"
    f"- Average Peak CPU Memory: {report.avg_peak_cpu_memory_mb:.2f} MB"
    )
    )
    print(
    print(
    f"- Average Peak GPU Memory: {report.avg_peak_gpu_memory_mb:.2f} MB"
    f"- Average Peak GPU Memory: {report.avg_peak_gpu_memory_mb:.2f} MB"
    )
    )
    print("")
    print("")


    print("System Metrics:")
    print("System Metrics:")
    print(f"- Average CPU Usage: {report.avg_cpu_percent:.2f}%")
    print(f"- Average CPU Usage: {report.avg_cpu_percent:.2f}%")
    print(f"- Average GPU Usage: {report.avg_gpu_percent:.2f}%")
    print(f"- Average GPU Usage: {report.avg_gpu_percent:.2f}%")


    # Print quality metrics if available
    # Print quality metrics if available
    if (
    if (
    report.avg_perplexity > 0
    report.avg_perplexity > 0
    or report.avg_bleu_score > 0
    or report.avg_bleu_score > 0
    or report.avg_rouge_score > 0
    or report.avg_rouge_score > 0
    ):
    ):
    print("")
    print("")
    print("Quality Metrics:")
    print("Quality Metrics:")
    if report.avg_perplexity > 0:
    if report.avg_perplexity > 0:
    print(f"- Average Perplexity: {report.avg_perplexity:.4f}")
    print(f"- Average Perplexity: {report.avg_perplexity:.4f}")
    if report.avg_bleu_score > 0:
    if report.avg_bleu_score > 0:
    print(f"- Average BLEU Score: {report.avg_bleu_score:.4f}")
    print(f"- Average BLEU Score: {report.avg_bleu_score:.4f}")
    if report.avg_rouge_score > 0:
    if report.avg_rouge_score > 0:
    print(f"- Average ROUGE Score: {report.avg_rouge_score:.4f}")
    print(f"- Average ROUGE Score: {report.avg_rouge_score:.4f}")


    # Print cost metrics if available
    # Print cost metrics if available
    if report.total_estimated_cost > 0:
    if report.total_estimated_cost > 0:
    print("")
    print("")
    print("Cost Metrics:")
    print("Cost Metrics:")
    print(
    print(
    f"- Total Estimated Cost: {report.total_estimated_cost:.6f} {report.currency}"
    f"- Total Estimated Cost: {report.total_estimated_cost:.6f} {report.currency}"
    )
    )
    print(
    print(
    f"- Average Cost per Inference: {report.avg_cost_per_inference:.6f} {report.currency}"
    f"- Average Cost per Inference: {report.avg_cost_per_inference:.6f} {report.currency}"
    )
    )


    # Print time range if specified
    # Print time range if specified
    if report.start_time and report.end_time:
    if report.start_time and report.end_time:
    print("")
    print("")
    print(f"Time Range: {report.start_time} to {report.end_time}")
    print(f"Time Range: {report.start_time} to {report.end_time}")


    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error generating report: {e}")
    logger.error(f"Error generating report: {e}")
    return 1
    return 1


    def _compare_models(
    def _compare_models(
    self, model_manager: ModelManager, performance_monitor: PerformanceMonitor
    self, model_manager: ModelManager, performance_monitor: PerformanceMonitor
    ) -> int:
    ) -> int:
    """
    """
    Compare the performance of multiple models.
    Compare the performance of multiple models.
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_ids"]):
    if not self._validate_args(["model_ids"]):
    return 1
    return 1


    model_ids = self._get_arg("model_ids")
    model_ids = self._get_arg("model_ids")
    model_names = self._get_arg("model_names")
    model_names = self._get_arg("model_names")


    # Validate and get model info for all models
    # Validate and get model info for all models
    for model_id in model_ids:
    for model_id in model_ids:
    model_info = model_manager.get_model_info(model_id)
    model_info = model_manager.get_model_info(model_id)
    if not model_info:
    if not model_info:
    logger.error(f"Model with ID {model_id} not found")
    logger.error(f"Model with ID {model_id} not found")
    return 1
    return 1


    try:
    try:
    # Generate comparison report
    # Generate comparison report
    comparison = performance_monitor.compare_models(
    comparison = performance_monitor.compare_models(
    model_ids=model_ids,
    model_ids=model_ids,
    model_names=model_names,
    model_names=model_names,
    title="Model Performance Comparison",
    title="Model Performance Comparison",
    )
    )


    # Format output
    # Format output
    output_format = self._get_arg("format")
    output_format = self._get_arg("format")
    output_path = self._get_arg("output")
    output_path = self._get_arg("output")


    if output_format == "json":
    if output_format == "json":
    comparison_data = comparison.to_dict()
    comparison_data = comparison.to_dict()


    if output_path:
    if output_path:
    with open(output_path, "w") as f:
    with open(output_path, "w") as f:
    json.dump(comparison_data, f, indent=2)
    json.dump(comparison_data, f, indent=2)
    logger.info(f"Saved comparison to {output_path}")
    logger.info(f"Saved comparison to {output_path}")
    else:
    else:
    print(json.dumps(comparison_data, indent=2))
    print(json.dumps(comparison_data, indent=2))


    elif output_format == "csv":
    elif output_format == "csv":
    if not output_path:
    if not output_path:
    output_path = f"model_comparison_{int(time.time())}.csv"
    output_path = f"model_comparison_{int(time.time())}.csv"


    with open(output_path, "w", newline="") as f:
    with open(output_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer = csv.writer(f)


    # Get model keys and metrics
    # Get model keys and metrics
    metrics = [
    metrics = [
    "avg_inference_time",
    "avg_inference_time",
    "avg_latency_ms",
    "avg_latency_ms",
    "avg_tokens_per_second",
    "avg_tokens_per_second",
    "avg_time_to_first_token",
    "avg_time_to_first_token",
    "avg_memory_usage_mb",
    "avg_memory_usage_mb",
    ]
    ]


    # Write header
    # Write header
    header = ["Metric"]
    header = ["Metric"]
    for model_key in comparison.comparison_metrics:
    for model_key in comparison.comparison_metrics:
    model_name = comparison.comparison_metrics[model_key].get(
    model_name = comparison.comparison_metrics[model_key].get(
    "model_name", model_key
    "model_name", model_key
    )
    )
    header.append(model_name)
    header.append(model_name)
    writer.writerow(header)
    writer.writerow(header)


    # Write metrics
    # Write metrics
    for metric in metrics:
    for metric in metrics:
    row = [metric]
    row = [metric]
    for model_key in comparison.comparison_metrics:
    for model_key in comparison.comparison_metrics:
    value = comparison.comparison_metrics[model_key].get(
    value = comparison.comparison_metrics[model_key].get(
    metric, 0
    metric, 0
    )
    )
    row.append(value)
    row.append(value)
    writer.writerow(row)
    writer.writerow(row)


    # Write percent differences
    # Write percent differences
    writer.writerow([])
    writer.writerow([])
    writer.writerow(["Percent Differences (compared to best model)"])
    writer.writerow(["Percent Differences (compared to best model)"])


    for metric in metrics:
    for metric in metrics:
    diff_metric = f"{metric}_percent_dif"
    diff_metric = f"{metric}_percent_dif"
    row = [f"{metric} % dif"]
    row = [f"{metric} % dif"]
    for model_key in comparison.comparison_metrics:
    for model_key in comparison.comparison_metrics:
    value = comparison.comparison_metrics[model_key].get(
    value = comparison.comparison_metrics[model_key].get(
    diff_metric, 0
    diff_metric, 0
    )
    )
    row.append(f"{value:.2f}%")
    row.append(f"{value:.2f}%")
    writer.writerow(row)
    writer.writerow(row)


    logger.info(f"Saved comparison to {output_path}")
    logger.info(f"Saved comparison to {output_path}")


    else:  # text format
    else:  # text format
    print("Model Performance Comparison")
    print("Model Performance Comparison")
    print(f"Generated: {comparison.timestamp}")
    print(f"Generated: {comparison.timestamp}")
    print("")
    print("")


    # Print comparison table
    # Print comparison table
    # Get metrics to display
    # Get metrics to display
    display_metrics = {
    display_metrics = {
    "avg_inference_time": "Avg Inference Time (s)",
    "avg_inference_time": "Avg Inference Time (s)",
    "avg_latency_ms": "Avg Latency (ms)",
    "avg_latency_ms": "Avg Latency (ms)",
    "avg_tokens_per_second": "Avg Tokens/sec",
    "avg_tokens_per_second": "Avg Tokens/sec",
    "avg_time_to_first_token": "Avg Time to 1st Token (s)",
    "avg_time_to_first_token": "Avg Time to 1st Token (s)",
    "avg_memory_usage_mb": "Avg Memory (MB)",
    "avg_memory_usage_mb": "Avg Memory (MB)",
    }
    }


    # Header
    # Header
    print(f"{'Metric':<25}", end="")
    print(f"{'Metric':<25}", end="")
    for model_key in comparison.comparison_metrics:
    for model_key in comparison.comparison_metrics:
    model_name = comparison.comparison_metrics[model_key].get(
    model_name = comparison.comparison_metrics[model_key].get(
    "model_name", model_key
    "model_name", model_key
    )
    )
    print(f"{model_name:<20}", end="")
    print(f"{model_name:<20}", end="")
    print("")
    print("")
    print("-" * (25 + 20 * len(comparison.comparison_metrics)))
    print("-" * (25 + 20 * len(comparison.comparison_metrics)))


    # Metrics
    # Metrics
    for metric, display_name in display_metrics.items():
    for metric, display_name in display_metrics.items():
    print(f"{display_name:<25}", end="")
    print(f"{display_name:<25}", end="")
    for model_key in comparison.comparison_metrics:
    for model_key in comparison.comparison_metrics:
    value = comparison.comparison_metrics[model_key].get(metric, 0)
    value = comparison.comparison_metrics[model_key].get(metric, 0)
    if "time" in metric:
    if "time" in metric:
    print(f"{value:.4f}".ljust(20), end="")
    print(f"{value:.4f}".ljust(20), end="")
    else:
    else:
    print(f"{value:.2f}".ljust(20), end="")
    print(f"{value:.2f}".ljust(20), end="")
    print("")
    print("")


    print("")
    print("")
    print("Percent Differences (compared to best model)")
    print("Percent Differences (compared to best model)")
    print("-" * (25 + 20 * len(comparison.comparison_metrics)))
    print("-" * (25 + 20 * len(comparison.comparison_metrics)))


    for metric, display_name in display_metrics.items():
    for metric, display_name in display_metrics.items():
    diff_metric = f"{metric}_percent_dif"
    diff_metric = f"{metric}_percent_dif"
    print(f"{display_name + ' % diff':<25}", end="")
    print(f"{display_name + ' % diff':<25}", end="")
    for model_key in comparison.comparison_metrics:
    for model_key in comparison.comparison_metrics:
    value = comparison.comparison_metrics[model_key].get(
    value = comparison.comparison_metrics[model_key].get(
    diff_metric, 0
    diff_metric, 0
    )
    )
    print(f"{value:+.2f}%".ljust(20), end="")
    print(f"{value:+.2f}%".ljust(20), end="")
    print("")
    print("")


    print("")
    print("")
    print(
    print(
    "Note: For time metrics, lower values are better (negative % diff means faster)."
    "Note: For time metrics, lower values are better (negative % diff means faster)."
    )
    )
    print(
    print(
    "      For tokens/sec, higher values are better (negative % diff means slower)."
    "      For tokens/sec, higher values are better (negative % diff means slower)."
    )
    )


    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error comparing models: {e}")
    logger.error(f"Error comparing models: {e}")
    return 1
    return 1


    def _visualize_metrics(
    def _visualize_metrics(
    self, model_manager: ModelManager, performance_monitor: PerformanceMonitor
    self, model_manager: ModelManager, performance_monitor: PerformanceMonitor
    ) -> int:
    ) -> int:
    """
    """
    Generate visualizations of model performance metrics.
    Generate visualizations of model performance metrics.
    """
    """
    try:
    try:




except ImportError:
except ImportError:
    logger.error(
    logger.error(
    "Visualization requires matplotlib and pandas. Install with: pip install matplotlib pandas"
    "Visualization requires matplotlib and pandas. Install with: pip install matplotlib pandas"
    )
    )
    return 1
    return 1


    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id"]):
    if not self._validate_args(["model_id"]):
    return 1
    return 1


    # Get model info
    # Get model info
    model_id = self._get_arg("model_id")
    model_id = self._get_arg("model_id")
    model_info = model_manager.get_model_info(model_id)
    model_info = model_manager.get_model_info(model_id)


    if not model_info:
    if not model_info:
    logger.error(f"Model with ID {model_id} not found")
    logger.error(f"Model with ID {model_id} not found")
    return 1
    return 1


    # Get arguments
    # Get arguments
    metrics = self._get_arg("metrics")
    metrics = self._get_arg("metrics")
    days = self._get_arg("days")
    days = self._get_arg("days")
    output_dir = self._get_arg("output_dir")
    output_dir = self._get_arg("output_dir")


    try:
    try:
    # Generate visualizations
    # Generate visualizations
    viz_files = performance_monitor.visualize_metrics(
    viz_files = performance_monitor.visualize_metrics(
    model_id=model_id, metric_names=metrics, days=days, save_path=output_dir
    model_id=model_id, metric_names=metrics, days=days, save_path=output_dir
    )
    )


    if not viz_files:
    if not viz_files:
    logger.warning("No visualizations were generated - no data available")
    logger.warning("No visualizations were generated - no data available")
    return 0
    return 0


    logger.info(f"Generated {len(viz_files)} visualizations")
    logger.info(f"Generated {len(viz_files)} visualizations")
    for file_path in viz_files:
    for file_path in viz_files:
    print(f"- {file_path}")
    print(f"- {file_path}")


    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error generating visualizations: {e}")
    logger.error(f"Error generating visualizations: {e}")
    return 1
    return 1


    def _export_metrics(
    def _export_metrics(
    self, model_manager: ModelManager, performance_monitor: PerformanceMonitor
    self, model_manager: ModelManager, performance_monitor: PerformanceMonitor
    ) -> int:
    ) -> int:
    """
    """
    Export performance metrics to CSV.
    Export performance metrics to CSV.
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id"]):
    if not self._validate_args(["model_id"]):
    return 1
    return 1


    # Get model info
    # Get model info
    model_id = self._get_arg("model_id")
    model_id = self._get_arg("model_id")
    model_info = model_manager.get_model_info(model_id)
    model_info = model_manager.get_model_info(model_id)


    if not model_info:
    if not model_info:
    logger.error(f"Model with ID {model_id} not found")
    logger.error(f"Model with ID {model_id} not found")
    return 1
    return 1


    # Get output path
    # Get output path
    output_path = self._get_arg("output")
    output_path = self._get_arg("output")


    try:
    try:
    # Export metrics
    # Export metrics
    csv_path = performance_monitor.export_metrics_csv(
    csv_path = performance_monitor.export_metrics_csv(
    model_id=model_id, filename=output_path
    model_id=model_id, filename=output_path
    )
    )


    if not csv_path:
    if not csv_path:
    logger.error("Failed to export metrics")
    logger.error("Failed to export metrics")
    return 1
    return 1


    logger.info(f"Exported metrics to {csv_path}")
    logger.info(f"Exported metrics to {csv_path}")
    print(f"Metrics exported to: {csv_path}")
    print(f"Metrics exported to: {csv_path}")


    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error exporting metrics: {e}")
    logger.error(f"Error exporting metrics: {e}")
    return 1
    return 1


    def _set_alert(
    def _set_alert(
    self, model_manager: ModelManager, performance_monitor: PerformanceMonitor
    self, model_manager: ModelManager, performance_monitor: PerformanceMonitor
    ) -> int:
    ) -> int:
    """
    """
    Set an alert threshold for a model metric.
    Set an alert threshold for a model metric.
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id", "metric", "threshold"]):
    if not self._validate_args(["model_id", "metric", "threshold"]):
    return 1
    return 1


    # Get model info
    # Get model info
    model_id = self._get_arg("model_id")
    model_id = self._get_arg("model_id")
    model_info = model_manager.get_model_info(model_id)
    model_info = model_manager.get_model_info(model_id)


    if not model_info:
    if not model_info:
    logger.error(f"Model with ID {model_id} not found")
    logger.error(f"Model with ID {model_id} not found")
    return 1
    return 1


    # Get arguments
    # Get arguments
    metric = self._get_arg("metric")
    metric = self._get_arg("metric")
    threshold = self._get_arg("threshold")
    threshold = self._get_arg("threshold")
    is_upper_bound = self._get_arg("upper_bound")
    is_upper_bound = self._get_arg("upper_bound")


    try:
    try:
    # Set alert threshold
    # Set alert threshold
    performance_monitor.set_alert_threshold(
    performance_monitor.set_alert_threshold(
    model_id=model_id,
    model_id=model_id,
    metric_name=metric,
    metric_name=metric,
    threshold_value=threshold,
    threshold_value=threshold,
    is_upper_bound=is_upper_bound,
    is_upper_bound=is_upper_bound,
    )
    )


    bound_type = "above" if is_upper_bound else "below"
    bound_type = "above" if is_upper_bound else "below"
    logger.info(
    logger.info(
    f"Set alert for {metric} {bound_type} {threshold} for model {model_id}"
    f"Set alert for {metric} {bound_type} {threshold} for model {model_id}"
    )
    )
    print(f"Alert set: {model_id} - {metric} {bound_type} {threshold}")
    print(f"Alert set: {model_id} - {metric} {bound_type} {threshold}")


    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error setting alert: {e}")
    logger.error(f"Error setting alert: {e}")
    return 1
    return 1


    def _track_inference(
    def _track_inference(
    self, model_manager: ModelManager, performance_monitor: PerformanceMonitor
    self, model_manager: ModelManager, performance_monitor: PerformanceMonitor
    ) -> int:
    ) -> int:
    """
    """
    Track a simple inference run for performance monitoring.
    Track a simple inference run for performance monitoring.
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id", "input"]):
    if not self._validate_args(["model_id", "input"]):
    return 1
    return 1


    # Get model info
    # Get model info
    model_id = self._get_arg("model_id")
    model_id = self._get_arg("model_id")
    model_info = model_manager.get_model_info(model_id)
    model_info = model_manager.get_model_info(model_id)


    if not model_info:
    if not model_info:
    logger.error(f"Model with ID {model_id} not found")
    logger.error(f"Model with ID {model_id} not found")
    return 1
    return 1


    # Get input text
    # Get input text
    input_text = self._get_arg("input")
    input_text = self._get_arg("input")


    try:
    try:
    # Load the model
    # Load the model
    model = model_manager.load_model(model_id)
    model = model_manager.load_model(model_id)


    if not model:
    if not model:
    logger.error(f"Failed to load model {model_id}")
    logger.error(f"Failed to load model {model_id}")
    return 1
    return 1


    # Create inference tracker
    # Create inference tracker
    tracker = InferenceTracker(performance_monitor, model_id)
    tracker = InferenceTracker(performance_monitor, model_id)


    # Start tracking
    # Start tracking
    tracker.start(input_text=input_text)
    tracker.start(input_text=input_text)


    # Perform inference (if the model supports generate or __call__)
    # Perform inference (if the model supports generate or __call__)
    output_text = ""
    output_text = ""
    try:
    try:
    if hasattr(model, "generate"):
    if hasattr(model, "generate"):
    output_text = model.generate(input_text)
    output_text = model.generate(input_text)
    elif hasattr(model, "__call__"):
    elif hasattr(model, "__call__"):
    output_text = model(input_text)
    output_text = model(input_text)
    else:
    else:
    # Just simulate an inference
    # Just simulate an inference




    time.sleep(0.5)
    time.sleep(0.5)
    output_text = "Simulated output for " + input_text
    output_text = "Simulated output for " + input_text
except Exception as e:
except Exception as e:
    logger.error(f"Error during inference: {e}")
    logger.error(f"Error during inference: {e}")
    output_text = f"Error: {e}"
    output_text = f"Error: {e}"


    # Stop tracking and get metrics
    # Stop tracking and get metrics
    metrics = tracker.stop(output_text=output_text)
    metrics = tracker.stop(output_text=output_text)


    # Show the result
    # Show the result
    print(f"Input:  {input_text}")
    print(f"Input:  {input_text}")
    print(
    print(
    f"Output: {output_text[:100]}..."
    f"Output: {output_text[:100]}..."
    if len(output_text) > 100
    if len(output_text) > 100
    else output_text
    else output_text
    )
    )
    print("")
    print("")


    # Show metrics if requested
    # Show metrics if requested
    if self._get_arg("show_metrics"):
    if self._get_arg("show_metrics"):
    print("Performance Metrics:")
    print("Performance Metrics:")
    print(f"- Inference Time: {metrics.total_time:.4f} seconds")
    print(f"- Inference Time: {metrics.total_time:.4f} seconds")
    print(f"- Latency: {metrics.latency_ms:.2f} ms")
    print(f"- Latency: {metrics.latency_ms:.2f} ms")
    print(f"- Input Tokens: {metrics.input_tokens}")
    print(f"- Input Tokens: {metrics.input_tokens}")
    print(f"- Output Tokens: {metrics.output_tokens}")
    print(f"- Output Tokens: {metrics.output_tokens}")
    print(f"- Tokens per Second: {metrics.tokens_per_second:.2f}")
    print(f"- Tokens per Second: {metrics.tokens_per_second:.2f}")
    print(f"- Memory Usage: {metrics.memory_usage_mb:.2f} MB")
    print(f"- Memory Usage: {metrics.memory_usage_mb:.2f} MB")
    if metrics.peak_cpu_memory_mb > 0:
    if metrics.peak_cpu_memory_mb > 0:
    print(f"- Peak CPU Memory: {metrics.peak_cpu_memory_mb:.2f} MB")
    print(f"- Peak CPU Memory: {metrics.peak_cpu_memory_mb:.2f} MB")
    if metrics.peak_gpu_memory_mb > 0:
    if metrics.peak_gpu_memory_mb > 0:
    print(f"- Peak GPU Memory: {metrics.peak_gpu_memory_mb:.2f} MB")
    print(f"- Peak GPU Memory: {metrics.peak_gpu_memory_mb:.2f} MB")
    else:
    else:
    print(f"Inference tracked in {metrics.total_time:.4f} seconds")
    print(f"Inference tracked in {metrics.total_time:.4f} seconds")


    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error tracking inference: {e}")
    logger.error(f"Error tracking inference: {e}")
    return 1
    return 1


    def _load_config(self) -> Optional[ModelConfig]:
    def _load_config(self) -> Optional[ModelConfig]:
    """
    """
    Load the configuration.
    Load the configuration.
    """
    """
    config_path = self._get_arg("config")
    config_path = self._get_arg("config")


    if config_path:
    if config_path:
    if not os.path.exists(config_path):
    if not os.path.exists(config_path):
    logger.error(f"Configuration file {config_path} not found")
    logger.error(f"Configuration file {config_path} not found")
    return None
    return None


    try:
    try:
    return ModelConfig.load(config_path)
    return ModelConfig.load(config_path)
except Exception as e:
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    logger.error(f"Error loading configuration: {e}")
    return None
    return None


    return ModelConfig.get_default()
    return ModelConfig.get_default()