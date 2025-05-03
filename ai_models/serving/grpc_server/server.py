"""
gRPC server for AI models.

This module provides a gRPC server for serving AI models.
"""

try:
    import torch
except ImportError:
    pass


import logging
import os
import threading
import time
from concurrent import futures
from typing import Any, Dict, List

from ..server import ModelServer
from .config import GRPCConfig
from .servicer import ModelServicer


    import grpc
    from grpc_health.v1 import health, health_pb2, health_pb2_grpc
    from grpc_reflection.v1alpha import reflection

    GRPC_AVAILABLE 
            import torch
            from transformers import AutoTokenizer
        except ImportError
            from transformers import AutoModelForCausalLM

            self.model 
            from transformers import AutoModelForSequenceClassification

            self.model 
            from transformers import AutoModel

            self.model 
            import statistics
            from .proto import model_pb2, model_pb2_grpc
        except ImportError

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import gRPC
try:

= True
except ImportError:
    logger.warning("gRPC is required for gRPC server")
    GRPC_AVAILABLE = False


class GRPCServer(ModelServer):
    """
    gRPC server for AI models.
    """

    def __init__(self, config: GRPCConfig):
        """
        Initialize the gRPC server.

        Args:
            config: Server configuration
        """
        if not GRPC_AVAILABLE:
            raise ImportError("gRPC is required for gRPC server")

        super().__init__(config)

        # Initialize server
        self.server = None
        self.server_thread = None
        self.start_time = None

        # Initialize metrics
        self.request_count = 0
        self.error_count = 0
        self.token_count = 0
        self.latencies = []

    def load_model(self) -> None:
        """
        Load the model for serving.
        """
        logger.info(f"Loading model from {self.config.model_path}")

        # Import required modules
        try:

:
            raise ImportError("PyTorch and Transformers are required for model loading")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)

        # Load model based on type
        if self.config.model_type == "text-generation":
= AutoModelForCausalLM.from_pretrained(
                self.config.model_path, device_map="auto"
            )
        elif self.config.model_type == "text-classification":
= AutoModelForSequenceClassification.from_pretrained(
                self.config.model_path, device_map="auto"
            )
        elif self.config.model_type == "embedding":
= AutoModel.from_pretrained(
                self.config.model_path, device_map="auto"
            )
        else:
            raise ValueError(f"Unsupported model type: {self.config.model_type}")

        logger.info("Model loaded successfully")

    def start(self) -> None:
        """
        Start the gRPC server.
        """
        if self.is_running():
            logger.warning("Server is already running")
                    return # Create gRPC server
        self.server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=self.config.workers),
            options=[
                ("grpc.max_send_message_length", self.config.max_message_length),
                ("grpc.max_receive_message_length", self.config.max_message_length),
                ("grpc.max_concurrent_streams", self.config.max_concurrent_rpcs),
            ],
        )

        # Add servicers
        self._add_servicers()

        # Add TLS credentials if enabled
        if self.config.enable_tls:
            if not self.config.tls_key_file or not self.config.tls_cert_file:
                raise ValueError("TLS key and certificate files are required for TLS")

            with open(self.config.tls_key_file, "rb") as f:
                private_key = f.read()

            with open(self.config.tls_cert_file, "rb") as f:
                certificate_chain = f.read()

            server_credentials = grpc.ssl_server_credentials(
                [(private_key, certificate_chain)]
            )

            # Add secure port
            server_address = f"{self.config.host}:{self.config.port}"
            self.server.add_secure_port(server_address, server_credentials)
        else:
            # Add insecure port
            server_address = f"{self.config.host}:{self.config.port}"
            self.server.add_insecure_port(server_address)

        # Start server
        self.start_time = time.time()
        self.server.start()

        # Start server thread
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

        logger.info(f"Server started at {server_address}")

    def stop(self) -> None:
        """
        Stop the gRPC server.
        """
        if not self.is_running():
            logger.warning("Server is not running")
                    return # Stop server
        if self.server:
            self.server.stop(grace=5)
            self.server = None

        # Wait for server thread to stop
        if self.server_thread:
            self.server_thread.join(timeout=5)
            self.server_thread = None

        logger.info("Server stopped")

    def is_running(self) -> bool:
        """
        Check if the server is running.

        Returns:
            True if the server is running, False otherwise
        """
                return self.server_thread is not None and self.server_thread.is_alive()

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the server.

        Returns:
            Dictionary with server information
        """
                return {
            "version": "1.0.0",
            "model_id": self.config.model_id
            or os.path.basename(self.config.model_path),
            "model_type": self.config.model_type,
            "uptime": time.time() - self.start_time if self.start_time else 0,
            "host": self.config.host,
            "port": self.config.port,
            "protocol": self.config.protocol.value,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "token_count": self.token_count,
        }

    def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get server metrics.

        Returns:
            List of metrics
        """
        metrics = []

        # Add request count
        metrics.append(
            {
                "name": "request_count",
                "value": self.request_count,
                "labels": {
                    "model_id": self.config.model_id
                    or os.path.basename(self.config.model_path),
                    "model_type": self.config.model_type,
                },
            }
        )

        # Add error count
        metrics.append(
            {
                "name": "error_count",
                "value": self.error_count,
                "labels": {
                    "model_id": self.config.model_id
                    or os.path.basename(self.config.model_path),
                    "model_type": self.config.model_type,
                },
            }
        )

        # Add token count
        metrics.append(
            {
                "name": "token_count",
                "value": self.token_count,
                "labels": {
                    "model_id": self.config.model_id
                    or os.path.basename(self.config.model_path),
                    "model_type": self.config.model_type,
                },
            }
        )

        # Add latency metrics
        if self.latencies:


            # Calculate latency statistics
            latency_mean = statistics.mean(self.latencies)
            latency_median = statistics.median(self.latencies)
            latency_p90 = self._percentile(self.latencies, 90)
            latency_p95 = self._percentile(self.latencies, 95)
            latency_p99 = self._percentile(self.latencies, 99)

            # Add latency metrics
            metrics.append(
                {
                    "name": "latency_mean",
                    "value": latency_mean,
                    "labels": {
                        "model_id": self.config.model_id
                        or os.path.basename(self.config.model_path),
                        "model_type": self.config.model_type,
                    },
                }
            )

            metrics.append(
                {
                    "name": "latency_median",
                    "value": latency_median,
                    "labels": {
                        "model_id": self.config.model_id
                        or os.path.basename(self.config.model_path),
                        "model_type": self.config.model_type,
                    },
                }
            )

            metrics.append(
                {
                    "name": "latency_p90",
                    "value": latency_p90,
                    "labels": {
                        "model_id": self.config.model_id
                        or os.path.basename(self.config.model_path),
                        "model_type": self.config.model_type,
                    },
                }
            )

            metrics.append(
                {
                    "name": "latency_p95",
                    "value": latency_p95,
                    "labels": {
                        "model_id": self.config.model_id
                        or os.path.basename(self.config.model_path),
                        "model_type": self.config.model_type,
                    },
                }
            )

            metrics.append(
                {
                    "name": "latency_p99",
                    "value": latency_p99,
                    "labels": {
                        "model_id": self.config.model_id
                        or os.path.basename(self.config.model_path),
                        "model_type": self.config.model_type,
                    },
                }
            )

                return metrics

    def _run_server(self) -> None:
        """
        Run the gRPC server.
        """
        try:
            # Keep server running
            self.server.wait_for_termination()
        except KeyboardInterrupt:
            self.stop()

    def _add_servicers(self) -> None:
        """
        Add servicers to the server.
        """
        # Import proto modules
        try:
:
            logger.warning(
                "Proto modules not found. Make sure to generate them from .proto files."
            )
                    return # Create servicer
        servicer = ModelServicer(self)

        # Add servicer to server
        model_pb2_grpc.add_ModelServiceServicer_to_server(servicer, self.server)

        # Add reflection service
        if self.config.enable_reflection:
            service_names = (
                model_pb2.DESCRIPTOR.services_by_name["ModelService"].full_name,
                reflection.SERVICE_NAME,
            )
            reflection.enable_server_reflection(service_names, self.server)

        # Add health service
        if self.config.enable_health_checking:
            health_servicer = health.HealthServicer(
                experimental_non_blocking=True,
                experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=1),
            )
            health_pb2_grpc.add_HealthServicer_to_server(health_servicer, self.server)

            # Set serving status
            health_servicer.set_serving_status(
                model_pb2.DESCRIPTOR.services_by_name["ModelService"].full_name,
                health_pb2.HealthCheckResponse.SERVING,
            )

    def _percentile(self, data: List[float], percentile: float) -> float:
        """
        Calculate a percentile of a list of values.

        Args:
            data: List of values
            percentile: Percentile to calculate (0-100)

        Returns:
            Percentile value
        """
        size = len(data)
        sorted_data = sorted(data)

        if not size:
                    return 0

        if size == 1:
                    return sorted_data[0]

        # Calculate the index
        k = (size - 1) * percentile / 100
        f = int(k)
        c = int(k) + 1 if k > f else f

        if f >= size:
                    return sorted_data[-1]

        if c >= size:
                    return sorted_data[-1]

        # Interpolate
        d0 = sorted_data[f] * (c - k)
        d1 = sorted_data[c] * (k - f)
                return d0 + d1