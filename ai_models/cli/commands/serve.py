"""
Serve commands for the command-line interface.

This module provides commands for serving models.
"""


import argparse
import json
import logging
import os

from ..base import BaseCommand


            from ...serving import RESTConfig, RESTServer

            
                import time
            from ...serving import GRPCConfig, GRPCServer

            
                import time

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ServeRESTCommand(BaseCommand):
    """
    Command for serving a model with a REST API.
    """

    description = "Serve a model with a REST API"

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
            "--model-type",
            type=str,
            default="text-generation",
            choices=[
                "text-generation",
                "text-classification",
                "embedding",
                "image",
                "audio",
            ],
            help="Type of the model",
        )
        parser.add_argument(
            "--host", type=str, default="0.0.0.0", help="Host to bind the server to"
        )
        parser.add_argument(
            "--port", type=int, default=8000, help="Port to bind the server to"
        )
        parser.add_argument(
            "--workers", type=int, default=1, help="Number of worker processes"
        )
        parser.add_argument(
            "--timeout", type=int, default=60, help="Timeout in seconds"
        )
        parser.add_argument(
            "--max-batch-size",
            type=int,
            default=4,
            help="Maximum batch size for inference",
        )
        parser.add_argument(
            "--enable-auth", action="store_true", help="Enable authentication"
        )
        parser.add_argument(
            "--api-keys", type=str, help="Comma-separated list of API keys"
        )
        parser.add_argument("--enable-cors", action="store_true", help="Enable CORS")
        parser.add_argument(
            "--cors-origins",
            type=str,
            default="*",
            help="Comma-separated list of allowed origins for CORS",
        )
        parser.add_argument(
            "--enable-rate-limit", action="store_true", help="Enable rate limiting"
        )
        parser.add_argument(
            "--rate-limit",
            type=int,
            default=60,
            help="Maximum number of requests per minute",
        )
        parser.add_argument("--enable-https", action="store_true", help="Enable HTTPS")
        parser.add_argument("--ssl-keyfile", type=str, help="Path to SSL key file")
        parser.add_argument(
            "--ssl-certfile", type=str, help="Path to SSL certificate file"
        )
        parser.add_argument(
            "--enable-docs", action="store_true", help="Enable API documentation"
        )
        parser.add_argument(
            "--docs-url",
            type=str,
            default="/docs",
            help="URL path for API documentation",
        )
        parser.add_argument(
            "--enable-metrics", action="store_true", help="Enable metrics endpoint"
        )
        parser.add_argument(
            "--metrics-path",
            type=str,
            default="/metrics",
            help="URL path for metrics endpoint",
        )
        parser.add_argument("--log-file", type=str, help="Path to log file")
        parser.add_argument(
            "--config-file", type=str, help="Path to configuration file"
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
# Load configuration from file if provided
            config_dict = {}
            if self.args.config_file and os.path.exists(self.args.config_file):
                with open(self.args.config_file, "r", encoding="utf-8") as f:
                    config_dict = json.load(f)

            # Update configuration with command-line arguments
            config_dict.update(
                {
                    "model_path": self.args.model_path,
                    "model_type": self.args.model_type,
                    "host": self.args.host,
                    "port": self.args.port,
                    "workers": self.args.workers,
                    "timeout": self.args.timeout,
                    "max_batch_size": self.args.max_batch_size,
                    "enable_auth": self.args.enable_auth,
                    "enable_cors": self.args.enable_cors,
                    "enable_rate_limit": self.args.enable_rate_limit,
                    "rate_limit": self.args.rate_limit,
                    "enable_https": self.args.enable_https,
                    "ssl_keyfile": self.args.ssl_keyfile,
                    "ssl_certfile": self.args.ssl_certfile,
                    "docs_url": self.args.docs_url if self.args.enable_docs else None,
                    "openapi_url": "/openapi.json" if self.args.enable_docs else None,
                    "redoc_url": "/redoc" if self.args.enable_docs else None,
                    "enable_metrics": self.args.enable_metrics,
                    "metrics_path": self.args.metrics_path,
                    "log_level": self.args.log_level,
                    "log_file": self.args.log_file,
                }
            )

            # Parse API keys
            if self.args.api_keys:
                config_dict["api_keys"] = [
                    key.strip() for key in self.args.api_keys.split(",")
                ]

            # Parse CORS origins
            if self.args.cors_origins:
                config_dict["cors_origins"] = [
                    origin.strip() for origin in self.args.cors_origins.split(",")
                ]

            # Create server configuration
            config = RESTConfig.from_dict(config_dict)

            # Create server
            server = RESTServer(config)

            # Load model
            logger.info(f"Loading model from {self.args.model_path}")
            server.load_model()

            # Start server
            logger.info(f"Starting server at http://{self.args.host}:{self.args.port}")
            server.start()

            # Wait for server to stop
            try:


                while server.is_running():
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping server...")
                server.stop()

            return 0

        except Exception as e:
            logger.error(f"Error serving model: {e}", exc_info=True)
            return 1


class ServeGRPCCommand(BaseCommand):
    """
    Command for serving a model with a gRPC API.
    """

    description = "Serve a model with a gRPC API"

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
            "--model-type",
            type=str,
            default="text-generation",
            choices=[
                "text-generation",
                "text-classification",
                "embedding",
                "image",
                "audio",
            ],
            help="Type of the model",
        )
        parser.add_argument(
            "--host", type=str, default="0.0.0.0", help="Host to bind the server to"
        )
        parser.add_argument(
            "--port", type=int, default=50051, help="Port to bind the server to"
        )
        parser.add_argument(
            "--workers", type=int, default=1, help="Number of worker processes"
        )
        parser.add_argument(
            "--max-message-length",
            type=int,
            default=100 * 1024 * 1024,  # 100 MB
            help="Maximum message length in bytes",
        )
        parser.add_argument(
            "--max-concurrent-rpcs",
            type=int,
            default=100,
            help="Maximum number of concurrent RPCs",
        )
        parser.add_argument(
            "--enable-reflection", action="store_true", help="Enable gRPC reflection"
        )
        parser.add_argument(
            "--enable-health-checking",
            action="store_true",
            help="Enable health checking",
        )
        parser.add_argument("--enable-tls", action="store_true", help="Enable TLS")
        parser.add_argument("--tls-key-file", type=str, help="Path to TLS key file")
        parser.add_argument(
            "--tls-cert-file", type=str, help="Path to TLS certificate file"
        )
        parser.add_argument("--log-file", type=str, help="Path to log file")
        parser.add_argument(
            "--config-file", type=str, help="Path to configuration file"
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
# Load configuration from file if provided
            config_dict = {}
            if self.args.config_file and os.path.exists(self.args.config_file):
                with open(self.args.config_file, "r", encoding="utf-8") as f:
                    config_dict = json.load(f)

            # Update configuration with command-line arguments
            config_dict.update(
                {
                    "model_path": self.args.model_path,
                    "model_type": self.args.model_type,
                    "host": self.args.host,
                    "port": self.args.port,
                    "workers": self.args.workers,
                    "max_message_length": self.args.max_message_length,
                    "max_concurrent_rpcs": self.args.max_concurrent_rpcs,
                    "enable_reflection": self.args.enable_reflection,
                    "enable_health_checking": self.args.enable_health_checking,
                    "enable_tls": self.args.enable_tls,
                    "tls_key_file": self.args.tls_key_file,
                    "tls_cert_file": self.args.tls_cert_file,
                    "log_level": self.args.log_level,
                    "log_file": self.args.log_file,
                }
            )

            # Create server configuration
            config = GRPCConfig.from_dict(config_dict)

            # Create server
            server = GRPCServer(config)

            # Load model
            logger.info(f"Loading model from {self.args.model_path}")
            server.load_model()

            # Start server
            logger.info(f"Starting server at {self.args.host}:{self.args.port}")
            server.start()

            # Wait for server to stop
            try:


                while server.is_running():
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping server...")
                server.stop()

            return 0

        except Exception as e:
            logger.error(f"Error serving model: {e}", exc_info=True)
            return 1