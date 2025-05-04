"""
"""
gRPC server for AI models.
gRPC server for AI models.


This module provides a gRPC server for serving AI models.
This module provides a gRPC server for serving AI models.
"""
"""


try:
    try:
    import torch
    import torch
except ImportError:
except ImportError:
    pass
    pass




    import logging
    import logging
    import os
    import os
    import threading
    import threading
    import time
    import time
    from concurrent import futures
    from concurrent import futures
    from typing import Any, Dict, List
    from typing import Any, Dict, List


    import grpc
    import grpc
    from grpc_health.v1 import health, health_pb2, health_pb2_grpc
    from grpc_health.v1 import health, health_pb2, health_pb2_grpc
    from grpc_reflection.v1alpha import reflection
    from grpc_reflection.v1alpha import reflection


    from ..server import ModelServer
    from ..server import ModelServer
    from .config import GRPCConfig
    from .config import GRPCConfig
    from .servicer import ModelServicer
    from .servicer import ModelServicer


    GRPC_AVAILABLE
    GRPC_AVAILABLE
    import torch
    import torch
    from transformers import AutoTokenizer
    from transformers import AutoTokenizer
except ImportError
except ImportError
    from transformers import AutoModelForCausalLM
    from transformers import AutoModelForCausalLM


    self.model
    self.model
    from transformers import AutoModelForSequenceClassification
    from transformers import AutoModelForSequenceClassification


    self.model
    self.model
    from transformers import AutoModel
    from transformers import AutoModel


    self.model
    self.model
    import statistics
    import statistics


    from .proto import model_pb2, model_pb2_grpc
    from .proto import model_pb2, model_pb2_grpc
except ImportError
except ImportError


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


    # Try to import gRPC
    # Try to import gRPC
    try:
    try:


    = True
    = True
except ImportError:
except ImportError:
    logger.warning("gRPC is required for gRPC server")
    logger.warning("gRPC is required for gRPC server")
    GRPC_AVAILABLE = False
    GRPC_AVAILABLE = False




    class GRPCServer(ModelServer):
    class GRPCServer(ModelServer):
    """
    """
    gRPC server for AI models.
    gRPC server for AI models.
    """
    """


    def __init__(self, config: GRPCConfig):
    def __init__(self, config: GRPCConfig):
    """
    """
    Initialize the gRPC server.
    Initialize the gRPC server.


    Args:
    Args:
    config: Server configuration
    config: Server configuration
    """
    """
    if not GRPC_AVAILABLE:
    if not GRPC_AVAILABLE:
    raise ImportError("gRPC is required for gRPC server")
    raise ImportError("gRPC is required for gRPC server")


    super().__init__(config)
    super().__init__(config)


    # Initialize server
    # Initialize server
    self.server = None
    self.server = None
    self.server_thread = None
    self.server_thread = None
    self.start_time = None
    self.start_time = None


    # Initialize metrics
    # Initialize metrics
    self.request_count = 0
    self.request_count = 0
    self.error_count = 0
    self.error_count = 0
    self.token_count = 0
    self.token_count = 0
    self.latencies = []
    self.latencies = []


    def load_model(self) -> None:
    def load_model(self) -> None:
    """
    """
    Load the model for serving.
    Load the model for serving.
    """
    """
    logger.info(f"Loading model from {self.config.model_path}")
    logger.info(f"Loading model from {self.config.model_path}")


    # Import required modules
    # Import required modules
    try:
    try:


    :
    :
    raise ImportError("PyTorch and Transformers are required for model loading")
    raise ImportError("PyTorch and Transformers are required for model loading")


    # Load tokenizer
    # Load tokenizer
    self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)
    self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)


    # Load model based on type
    # Load model based on type
    if self.config.model_type == "text-generation":
    if self.config.model_type == "text-generation":
    = AutoModelForCausalLM.from_pretrained(
    = AutoModelForCausalLM.from_pretrained(
    self.config.model_path, device_map="auto"
    self.config.model_path, device_map="auto"
    )
    )
    elif self.config.model_type == "text-classification":
    elif self.config.model_type == "text-classification":
    = AutoModelForSequenceClassification.from_pretrained(
    = AutoModelForSequenceClassification.from_pretrained(
    self.config.model_path, device_map="auto"
    self.config.model_path, device_map="auto"
    )
    )
    elif self.config.model_type == "embedding":
    elif self.config.model_type == "embedding":
    = AutoModel.from_pretrained(
    = AutoModel.from_pretrained(
    self.config.model_path, device_map="auto"
    self.config.model_path, device_map="auto"
    )
    )
    else:
    else:
    raise ValueError(f"Unsupported model type: {self.config.model_type}")
    raise ValueError(f"Unsupported model type: {self.config.model_type}")


    logger.info("Model loaded successfully")
    logger.info("Model loaded successfully")


    def start(self) -> None:
    def start(self) -> None:
    """
    """
    Start the gRPC server.
    Start the gRPC server.
    """
    """
    if self.is_running():
    if self.is_running():
    logger.warning("Server is already running")
    logger.warning("Server is already running")
    return # Create gRPC server
    return # Create gRPC server
    self.server = grpc.server(
    self.server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=self.config.workers),
    futures.ThreadPoolExecutor(max_workers=self.config.workers),
    options=[
    options=[
    ("grpc.max_send_message_length", self.config.max_message_length),
    ("grpc.max_send_message_length", self.config.max_message_length),
    ("grpc.max_receive_message_length", self.config.max_message_length),
    ("grpc.max_receive_message_length", self.config.max_message_length),
    ("grpc.max_concurrent_streams", self.config.max_concurrent_rpcs),
    ("grpc.max_concurrent_streams", self.config.max_concurrent_rpcs),
    ],
    ],
    )
    )


    # Add servicers
    # Add servicers
    self._add_servicers()
    self._add_servicers()


    # Add TLS credentials if enabled
    # Add TLS credentials if enabled
    if self.config.enable_tls:
    if self.config.enable_tls:
    if not self.config.tls_key_file or not self.config.tls_cert_file:
    if not self.config.tls_key_file or not self.config.tls_cert_file:
    raise ValueError("TLS key and certificate files are required for TLS")
    raise ValueError("TLS key and certificate files are required for TLS")


    with open(self.config.tls_key_file, "rb") as f:
    with open(self.config.tls_key_file, "rb") as f:
    private_key = f.read()
    private_key = f.read()


    with open(self.config.tls_cert_file, "rb") as f:
    with open(self.config.tls_cert_file, "rb") as f:
    certificate_chain = f.read()
    certificate_chain = f.read()


    server_credentials = grpc.ssl_server_credentials(
    server_credentials = grpc.ssl_server_credentials(
    [(private_key, certificate_chain)]
    [(private_key, certificate_chain)]
    )
    )


    # Add secure port
    # Add secure port
    server_address = f"{self.config.host}:{self.config.port}"
    server_address = f"{self.config.host}:{self.config.port}"
    self.server.add_secure_port(server_address, server_credentials)
    self.server.add_secure_port(server_address, server_credentials)
    else:
    else:
    # Add insecure port
    # Add insecure port
    server_address = f"{self.config.host}:{self.config.port}"
    server_address = f"{self.config.host}:{self.config.port}"
    self.server.add_insecure_port(server_address)
    self.server.add_insecure_port(server_address)


    # Start server
    # Start server
    self.start_time = time.time()
    self.start_time = time.time()
    self.server.start()
    self.server.start()


    # Start server thread
    # Start server thread
    self.server_thread = threading.Thread(target=self._run_server, daemon=True)
    self.server_thread = threading.Thread(target=self._run_server, daemon=True)
    self.server_thread.start()
    self.server_thread.start()


    logger.info(f"Server started at {server_address}")
    logger.info(f"Server started at {server_address}")


    def stop(self) -> None:
    def stop(self) -> None:
    """
    """
    Stop the gRPC server.
    Stop the gRPC server.
    """
    """
    if not self.is_running():
    if not self.is_running():
    logger.warning("Server is not running")
    logger.warning("Server is not running")
    return # Stop server
    return # Stop server
    if self.server:
    if self.server:
    self.server.stop(grace=5)
    self.server.stop(grace=5)
    self.server = None
    self.server = None


    # Wait for server thread to stop
    # Wait for server thread to stop
    if self.server_thread:
    if self.server_thread:
    self.server_thread.join(timeout=5)
    self.server_thread.join(timeout=5)
    self.server_thread = None
    self.server_thread = None


    logger.info("Server stopped")
    logger.info("Server stopped")


    def is_running(self) -> bool:
    def is_running(self) -> bool:
    """
    """
    Check if the server is running.
    Check if the server is running.


    Returns:
    Returns:
    True if the server is running, False otherwise
    True if the server is running, False otherwise
    """
    """
    return self.server_thread is not None and self.server_thread.is_alive()
    return self.server_thread is not None and self.server_thread.is_alive()


    def get_info(self) -> Dict[str, Any]:
    def get_info(self) -> Dict[str, Any]:
    """
    """
    Get information about the server.
    Get information about the server.


    Returns:
    Returns:
    Dictionary with server information
    Dictionary with server information
    """
    """
    return {
    return {
    "version": "1.0.0",
    "version": "1.0.0",
    "model_id": self.config.model_id
    "model_id": self.config.model_id
    or os.path.basename(self.config.model_path),
    or os.path.basename(self.config.model_path),
    "model_type": self.config.model_type,
    "model_type": self.config.model_type,
    "uptime": time.time() - self.start_time if self.start_time else 0,
    "uptime": time.time() - self.start_time if self.start_time else 0,
    "host": self.config.host,
    "host": self.config.host,
    "port": self.config.port,
    "port": self.config.port,
    "protocol": self.config.protocol.value,
    "protocol": self.config.protocol.value,
    "request_count": self.request_count,
    "request_count": self.request_count,
    "error_count": self.error_count,
    "error_count": self.error_count,
    "token_count": self.token_count,
    "token_count": self.token_count,
    }
    }


    def get_metrics(self) -> List[Dict[str, Any]]:
    def get_metrics(self) -> List[Dict[str, Any]]:
    """
    """
    Get server metrics.
    Get server metrics.


    Returns:
    Returns:
    List of metrics
    List of metrics
    """
    """
    metrics = []
    metrics = []


    # Add request count
    # Add request count
    metrics.append(
    metrics.append(
    {
    {
    "name": "request_count",
    "name": "request_count",
    "value": self.request_count,
    "value": self.request_count,
    "labels": {
    "labels": {
    "model_id": self.config.model_id
    "model_id": self.config.model_id
    or os.path.basename(self.config.model_path),
    or os.path.basename(self.config.model_path),
    "model_type": self.config.model_type,
    "model_type": self.config.model_type,
    },
    },
    }
    }
    )
    )


    # Add error count
    # Add error count
    metrics.append(
    metrics.append(
    {
    {
    "name": "error_count",
    "name": "error_count",
    "value": self.error_count,
    "value": self.error_count,
    "labels": {
    "labels": {
    "model_id": self.config.model_id
    "model_id": self.config.model_id
    or os.path.basename(self.config.model_path),
    or os.path.basename(self.config.model_path),
    "model_type": self.config.model_type,
    "model_type": self.config.model_type,
    },
    },
    }
    }
    )
    )


    # Add token count
    # Add token count
    metrics.append(
    metrics.append(
    {
    {
    "name": "token_count",
    "name": "token_count",
    "value": self.token_count,
    "value": self.token_count,
    "labels": {
    "labels": {
    "model_id": self.config.model_id
    "model_id": self.config.model_id
    or os.path.basename(self.config.model_path),
    or os.path.basename(self.config.model_path),
    "model_type": self.config.model_type,
    "model_type": self.config.model_type,
    },
    },
    }
    }
    )
    )


    # Add latency metrics
    # Add latency metrics
    if self.latencies:
    if self.latencies:




    # Calculate latency statistics
    # Calculate latency statistics
    latency_mean = statistics.mean(self.latencies)
    latency_mean = statistics.mean(self.latencies)
    latency_median = statistics.median(self.latencies)
    latency_median = statistics.median(self.latencies)
    latency_p90 = self._percentile(self.latencies, 90)
    latency_p90 = self._percentile(self.latencies, 90)
    latency_p95 = self._percentile(self.latencies, 95)
    latency_p95 = self._percentile(self.latencies, 95)
    latency_p99 = self._percentile(self.latencies, 99)
    latency_p99 = self._percentile(self.latencies, 99)


    # Add latency metrics
    # Add latency metrics
    metrics.append(
    metrics.append(
    {
    {
    "name": "latency_mean",
    "name": "latency_mean",
    "value": latency_mean,
    "value": latency_mean,
    "labels": {
    "labels": {
    "model_id": self.config.model_id
    "model_id": self.config.model_id
    or os.path.basename(self.config.model_path),
    or os.path.basename(self.config.model_path),
    "model_type": self.config.model_type,
    "model_type": self.config.model_type,
    },
    },
    }
    }
    )
    )


    metrics.append(
    metrics.append(
    {
    {
    "name": "latency_median",
    "name": "latency_median",
    "value": latency_median,
    "value": latency_median,
    "labels": {
    "labels": {
    "model_id": self.config.model_id
    "model_id": self.config.model_id
    or os.path.basename(self.config.model_path),
    or os.path.basename(self.config.model_path),
    "model_type": self.config.model_type,
    "model_type": self.config.model_type,
    },
    },
    }
    }
    )
    )


    metrics.append(
    metrics.append(
    {
    {
    "name": "latency_p90",
    "name": "latency_p90",
    "value": latency_p90,
    "value": latency_p90,
    "labels": {
    "labels": {
    "model_id": self.config.model_id
    "model_id": self.config.model_id
    or os.path.basename(self.config.model_path),
    or os.path.basename(self.config.model_path),
    "model_type": self.config.model_type,
    "model_type": self.config.model_type,
    },
    },
    }
    }
    )
    )


    metrics.append(
    metrics.append(
    {
    {
    "name": "latency_p95",
    "name": "latency_p95",
    "value": latency_p95,
    "value": latency_p95,
    "labels": {
    "labels": {
    "model_id": self.config.model_id
    "model_id": self.config.model_id
    or os.path.basename(self.config.model_path),
    or os.path.basename(self.config.model_path),
    "model_type": self.config.model_type,
    "model_type": self.config.model_type,
    },
    },
    }
    }
    )
    )


    metrics.append(
    metrics.append(
    {
    {
    "name": "latency_p99",
    "name": "latency_p99",
    "value": latency_p99,
    "value": latency_p99,
    "labels": {
    "labels": {
    "model_id": self.config.model_id
    "model_id": self.config.model_id
    or os.path.basename(self.config.model_path),
    or os.path.basename(self.config.model_path),
    "model_type": self.config.model_type,
    "model_type": self.config.model_type,
    },
    },
    }
    }
    )
    )


    return metrics
    return metrics


    def _run_server(self) -> None:
    def _run_server(self) -> None:
    """
    """
    Run the gRPC server.
    Run the gRPC server.
    """
    """
    try:
    try:
    # Keep server running
    # Keep server running
    self.server.wait_for_termination()
    self.server.wait_for_termination()
except KeyboardInterrupt:
except KeyboardInterrupt:
    self.stop()
    self.stop()


    def _add_servicers(self) -> None:
    def _add_servicers(self) -> None:
    """
    """
    Add servicers to the server.
    Add servicers to the server.
    """
    """
    # Import proto modules
    # Import proto modules
    try:
    try:
    :
    :
    logger.warning(
    logger.warning(
    "Proto modules not found. Make sure to generate them from .proto files."
    "Proto modules not found. Make sure to generate them from .proto files."
    )
    )
    return # Create servicer
    return # Create servicer
    servicer = ModelServicer(self)
    servicer = ModelServicer(self)


    # Add servicer to server
    # Add servicer to server
    model_pb2_grpc.add_ModelServiceServicer_to_server(servicer, self.server)
    model_pb2_grpc.add_ModelServiceServicer_to_server(servicer, self.server)


    # Add reflection service
    # Add reflection service
    if self.config.enable_reflection:
    if self.config.enable_reflection:
    service_names = (
    service_names = (
    model_pb2.DESCRIPTOR.services_by_name["ModelService"].full_name,
    model_pb2.DESCRIPTOR.services_by_name["ModelService"].full_name,
    reflection.SERVICE_NAME,
    reflection.SERVICE_NAME,
    )
    )
    reflection.enable_server_reflection(service_names, self.server)
    reflection.enable_server_reflection(service_names, self.server)


    # Add health service
    # Add health service
    if self.config.enable_health_checking:
    if self.config.enable_health_checking:
    health_servicer = health.HealthServicer(
    health_servicer = health.HealthServicer(
    experimental_non_blocking=True,
    experimental_non_blocking=True,
    experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=1),
    experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=1),
    )
    )
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, self.server)
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, self.server)


    # Set serving status
    # Set serving status
    health_servicer.set_serving_status(
    health_servicer.set_serving_status(
    model_pb2.DESCRIPTOR.services_by_name["ModelService"].full_name,
    model_pb2.DESCRIPTOR.services_by_name["ModelService"].full_name,
    health_pb2.HealthCheckResponse.SERVING,
    health_pb2.HealthCheckResponse.SERVING,
    )
    )


    def _percentile(self, data: List[float], percentile: float) -> float:
    def _percentile(self, data: List[float], percentile: float) -> float:
    """
    """
    Calculate a percentile of a list of values.
    Calculate a percentile of a list of values.


    Args:
    Args:
    data: List of values
    data: List of values
    percentile: Percentile to calculate (0-100)
    percentile: Percentile to calculate (0-100)


    Returns:
    Returns:
    Percentile value
    Percentile value
    """
    """
    size = len(data)
    size = len(data)
    sorted_data = sorted(data)
    sorted_data = sorted(data)


    if not size:
    if not size:
    return 0
    return 0


    if size == 1:
    if size == 1:
    return sorted_data[0]
    return sorted_data[0]


    # Calculate the index
    # Calculate the index
    k = (size - 1) * percentile / 100
    k = (size - 1) * percentile / 100
    f = int(k)
    f = int(k)
    c = int(k) + 1 if k > f else f
    c = int(k) + 1 if k > f else f


    if f >= size:
    if f >= size:
    return sorted_data[-1]
    return sorted_data[-1]


    if c >= size:
    if c >= size:
    return sorted_data[-1]
    return sorted_data[-1]


    # Interpolate
    # Interpolate
    d0 = sorted_data[f] * (c - k)
    d0 = sorted_data[f] * (c - k)
    d1 = sorted_data[c] * (k - f)
    d1 = sorted_data[c] * (k - f)
    return d0 + d1
    return d0 + d1