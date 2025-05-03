"""
REST API server for AI models.

This module provides a REST API server for serving AI models.
"""

import logging
import os
import threading
import time
from typing import Any, Dict, List

from ..server import ModelServer
from .config import RESTConfig
from .middleware import setup_middleware
from .routes import (
    audio_router,
    embedding_router,
    health_router,
    image_router,
    metrics_router,
    text_classification_router,
    text_generation_router,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    import uvicorn
    from fastapi import FastAPI

    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI and uvicorn are required for REST API server")
    FASTAPI_AVAILABLE = False


class RESTServer(ModelServer):
    """
    REST API server for AI models.
    """

    def __init__(self, config: RESTConfig):
        """
        Initialize the REST API server.

        Args:
            config: Server configuration
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI and uvicorn are required for REST API server")

        super().__init__(config)

        # Initialize server
        self.app = None
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
            from transformers import AutoTokenizer
        except ImportError:
            raise ImportError("PyTorch and Transformers are required for model loading")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)

        # Load model based on type
        if self.config.model_type == "text - generation":
            from transformers import AutoModelForCausalLM

            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path, device_map="auto"
            )
        elif self.config.model_type == "text - classification":
            from transformers import AutoModelForSequenceClassification

            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.config.model_path, device_map="auto"
            )
        elif self.config.model_type == "embedding":
            from transformers import AutoModel

            self.model = AutoModel.from_pretrained(self.config.model_path, device_map="auto")
        else:
            raise ValueError(f"Unsupported model type: {self.config.model_type}")

        logger.info("Model loaded successfully")

    def start(self) -> None:
        """
        Start the REST API server.
        """
        if self.is_running():
            logger.warning("Server is already running")
            return

        # Create FastAPI app
        self.app = FastAPI(
            title="AI Models API",
            description="REST API for AI models",
            version="1.0.0",
            docs_url=self.config.docs_url,
            openapi_url=self.config.openapi_url,
            redoc_url=self.config.redoc_url,
        )

        # Set up middleware
        setup_middleware(self.app, self.config)

        # Set up routes
        self._setup_routes()

        # Set up dependencies
        self._setup_dependencies()

        # Start server
        self.start_time = time.time()
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

        logger.info(f"Server started at http://{self.config.host}:{self.config.port}")

    def stop(self) -> None:
        """
        Stop the REST API server.
        """
        if not self.is_running():
            logger.warning("Server is not running")
            return

        # Stop server
        if self.server:
            self.server.should_exit = True
            self.server.force_exit = True
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
            "model_id": self.config.model_id or os.path.basename(self.config.model_path),
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
                    "model_id": self.config.model_id or os.path.basename(self.config.model_path),
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
                    "model_id": self.config.model_id or os.path.basename(self.config.model_path),
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
                    "model_id": self.config.model_id or os.path.basename(self.config.model_path),
                    "model_type": self.config.model_type,
                },
            }
        )

        # Add latency metrics
        if self.latencies:
            import statistics

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
        Run the uvicorn server.
        """
        # Set up uvicorn config
        uvicorn_config = uvicorn.Config(
            app=self.app,
            host=self.config.host,
            port=self.config.port,
            workers=self.config.workers,
            timeout_keep_alive=self.config.timeout,
            log_level=self.config.log_level.lower(),
            ssl_keyfile=self.config.ssl_keyfile if self.config.enable_https else None,
            ssl_certfile=self.config.ssl_certfile if self.config.enable_https else None,
        )

        # Create and run server
        self.server = uvicorn.Server(uvicorn_config)
        self.server.run()

    def _setup_routes(self) -> None:
        """
        Set up routes for the server.
        """
        # Add health check route
        if self.config.enable_health_check:
            self.app.include_router(health_router, prefix="", tags=["Health"])

        # Add metrics route
        if self.config.enable_metrics:
            self.app.include_router(metrics_router, prefix="", tags=["Metrics"])

        # Add model - specific routes
        if self.config.enable_text_generation:
            self.app.include_router(text_generation_router, prefix="", tags=["Text Generation"])

        if self.config.enable_text_classification:
            self.app.include_router(
                text_classification_router, prefix="", tags=["Text Classification"]
            )

        if self.config.enable_embedding:
            self.app.include_router(embedding_router, prefix="", tags=["Embeddings"])

        if self.config.enable_image:
            self.app.include_router(image_router, prefix="", tags=["Images"])

        if self.config.enable_audio:
            self.app.include_router(audio_router, prefix="", tags=["Audio"])

    def _setup_dependencies(self) -> None:
        """
        Set up dependencies for the routes.
        """

        # Add model dependency
        @self.app.dependency
        def get_model():
            return self.model

        # Add server dependency
        @self.app.dependency
        def get_server():
            return self

    def _percentile(self, data: List[float], percentile: float) -> float:
        """
        Calculate a percentile of a list of values.

        Args:
            data: List of values
            percentile: Percentile to calculate (0 - 100)

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
