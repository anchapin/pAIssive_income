"""
Performance monitoring for the AI Models module.

This module provides functionality for monitoring and analyzing the performance
of AI models, including inference speed, memory usage, and other metrics.
"""

import os
import time
import logging
import threading
import json
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import statistics

from .model_config import ModelConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available. GPU memory monitoring will be limited.")
    TORCH_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    logger.warning("psutil not available. System memory monitoring will be limited.")
    PSUTIL_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    logger.warning("NumPy not available. Statistical analysis will be limited.")
    NUMPY_AVAILABLE = False


@dataclass
class InferenceMetrics:
    """
    Metrics for a single inference run.
    """
    model_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Time metrics
    start_time: float = 0.0
    end_time: float = 0.0
    total_time: float = 0.0
    time_to_first_token: float = 0.0
    latency_ms: float = 0.0

    # Token metrics
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    tokens_per_second: float = 0.0

    # Memory metrics
    memory_usage_mb: float = 0.0
    peak_cpu_memory_mb: float = 0.0
    peak_gpu_memory_mb: float = 0.0
    gpu_device: str = ""

    # System metrics
    cpu_percent: float = 0.0
    gpu_percent: float = 0.0

    # Additional data
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        Initialize derived values.
        """
        # Convert total_time to latency_ms if not provided
        if self.latency_ms == 0.0 and self.total_time > 0.0:
            self.latency_ms = self.total_time * 1000.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the metrics to a dictionary.

        Returns:
            Dictionary representation of the metrics
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InferenceMetrics':
        """
        Create an InferenceMetrics instance from a dictionary.

        Args:
            data: Dictionary containing metrics data

        Returns:
            InferenceMetrics instance
        """
        return cls(**data)


@dataclass
class ModelPerformanceReport:
    """
    Performance report for a model.
    """
    model_id: str
    model_name: str = ""
    report_id: str = field(default_factory=lambda: f"report_{int(time.time())}")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Aggregated metrics
    num_inferences: int = 0
    avg_inference_time: float = 0.0
    avg_latency_ms: float = 0.0
    avg_tokens_per_second: float = 0.0
    avg_time_to_first_token: float = 0.0

    # Memory metrics
    avg_memory_usage_mb: float = 0.0
    avg_peak_cpu_memory_mb: float = 0.0
    avg_peak_gpu_memory_mb: float = 0.0

    # Token metrics
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    # System metrics
    avg_cpu_percent: float = 0.0
    avg_gpu_percent: float = 0.0

    # Detailed metrics
    metrics: List[InferenceMetrics] = field(default_factory=list)

    # Additional data
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the report to a dictionary.

        Returns:
            Dictionary representation of the report
        """
        result = asdict(self)
        result["metrics"] = [m.to_dict() for m in self.metrics]
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelPerformanceReport':
        """
        Create a ModelPerformanceReport instance from a dictionary.

        Args:
            data: Dictionary containing report data

        Returns:
            ModelPerformanceReport instance
        """
        metrics_data = data.pop("metrics", [])
        report = cls(**data)
        report.metrics = [InferenceMetrics.from_dict(m) for m in metrics_data]
        return report

    def update_aggregated_metrics(self) -> None:
        """
        Update the aggregated metrics based on the detailed metrics.
        """
        if not self.metrics:
            return

        self.num_inferences = len(self.metrics)

        # Helper function to safely calculate mean
        def safe_mean(values):
            filtered_values = [v for v in values if v > 0]
            return statistics.mean(filtered_values) if filtered_values else 0.0

        # Calculate averages
        self.avg_inference_time = safe_mean([m.total_time for m in self.metrics])
        self.avg_latency_ms = safe_mean([m.latency_ms for m in self.metrics])
        self.avg_tokens_per_second = safe_mean([m.tokens_per_second for m in self.metrics])
        self.avg_time_to_first_token = safe_mean([m.time_to_first_token for m in self.metrics])

        # Memory metrics
        self.avg_memory_usage_mb = safe_mean([m.memory_usage_mb for m in self.metrics])
        self.avg_peak_cpu_memory_mb = safe_mean([m.peak_cpu_memory_mb for m in self.metrics])
        self.avg_peak_gpu_memory_mb = safe_mean([m.peak_gpu_memory_mb for m in self.metrics])

        # Token metrics
        self.total_input_tokens = sum([m.input_tokens for m in self.metrics])
        self.total_output_tokens = sum([m.output_tokens for m in self.metrics])

        # System metrics
        self.avg_cpu_percent = safe_mean([m.cpu_percent for m in self.metrics])
        self.avg_gpu_percent = safe_mean([m.gpu_percent for m in self.metrics])


class PerformanceMonitor:
    """
    Monitor for tracking and analyzing model performance.
    """

    def __init__(self, config: Optional[ModelConfig] = None):
        """
        Initialize the performance monitor.

        Args:
            config: Optional model configuration
        """
        self.config = config or ModelConfig.get_default()
        self.metrics_history: Dict[str, List[InferenceMetrics]] = {}
        self.report_cache: Dict[str, ModelPerformanceReport] = {}
        self.metrics_lock = threading.Lock()

        # Create performance data directory
        self.performance_dir = os.path.join(self.config.models_dir, "performance")
        os.makedirs(self.performance_dir, exist_ok=True)

    def track_inference(
        self,
        model: Any,
        input_text: str,
        output_text: str,
        parameters: Dict[str, Any] = None
    ) -> InferenceMetrics:
        """
        Track an inference run.

        Args:
            model: Model used for inference
            input_text: Input text
            output_text: Output text
            parameters: Additional parameters for the inference

        Returns:
            InferenceMetrics instance
        """
        # Create a tracker
        tracker = InferenceTracker(monitor=self, model_id=model.id)

        # Start tracking
        tracker.start(input_text=input_text)

        # Add a small delay to ensure latency is measurable
        import time
        time.sleep(0.001)

        # Stop tracking
        metrics = tracker.stop(output_text=output_text)

        # Add parameters
        if parameters:
            metrics.parameters.update(parameters)

        # Ensure latency_ms is set
        if metrics.latency_ms <= 0 and metrics.total_time > 0:
            metrics.latency_ms = metrics.total_time * 1000.0

        return metrics

    def start_inference_tracking(self, model_id: str, input_tokens: int = 0, parameters: Dict[str, Any] = None) -> InferenceMetrics:
        """
        Start tracking an inference run.

        Args:
            model_id: ID of the model
            input_tokens: Number of input tokens
            parameters: Additional parameters for the inference

        Returns:
            InferenceMetrics instance
        """
        # Create metrics
        metrics = InferenceMetrics(
            model_id=model_id,
            start_time=time.time(),
            input_tokens=input_tokens,
            parameters=parameters or {}
        )

        # Capture initial memory usage
        if PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            metrics.peak_cpu_memory_mb = process.memory_info().rss / (1024 * 1024)
            metrics.cpu_percent = process.cpu_percent()

        if TORCH_AVAILABLE and torch.cuda.is_available():
            metrics.gpu_device = torch.cuda.get_device_name(0)
            metrics.peak_gpu_memory_mb = torch.cuda.memory_allocated(0) / (1024 * 1024)
            if hasattr(torch.cuda, 'utilization'):
                metrics.gpu_percent = torch.cuda.utilization(0)

        return metrics

    def end_inference_tracking(
        self,
        metrics: InferenceMetrics,
        output_tokens: int = 0,
        time_to_first_token: float = 0.0,
        metadata: Dict[str, Any] = None
    ) -> InferenceMetrics:
        """
        End tracking an inference run.

        Args:
            metrics: InferenceMetrics instance from start_inference_tracking
            output_tokens: Number of output tokens
            time_to_first_token: Time to first token in seconds
            metadata: Additional metadata for the inference

        Returns:
            Updated InferenceMetrics instance
        """
        # Update metrics
        metrics.end_time = time.time()
        metrics.total_time = metrics.end_time - metrics.start_time
        metrics.output_tokens = output_tokens
        metrics.total_tokens = metrics.input_tokens + metrics.output_tokens
        metrics.time_to_first_token = time_to_first_token

        # Calculate tokens per second
        if metrics.output_tokens > 0 and metrics.total_time > 0:
            metrics.tokens_per_second = metrics.output_tokens / metrics.total_time

        # Capture final memory usage
        if PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            current_memory = process.memory_info().rss / (1024 * 1024)
            metrics.peak_cpu_memory_mb = max(metrics.peak_cpu_memory_mb, current_memory)
            metrics.cpu_percent = process.cpu_percent()

        if TORCH_AVAILABLE and torch.cuda.is_available():
            current_gpu_memory = torch.cuda.memory_allocated(0) / (1024 * 1024)
            metrics.peak_gpu_memory_mb = max(metrics.peak_gpu_memory_mb, current_gpu_memory)
            if hasattr(torch.cuda, 'utilization'):
                metrics.gpu_percent = torch.cuda.utilization(0)

        # Add metadata
        if metadata:
            metrics.metadata.update(metadata)

        # Store the metrics
        with self.metrics_lock:
            if metrics.model_id not in self.metrics_history:
                self.metrics_history[metrics.model_id] = []

            self.metrics_history[metrics.model_id].append(metrics)

        return metrics

    def get_model_metrics(self, model_id: str) -> List[InferenceMetrics]:
        """
        Get all metrics for a model.

        Args:
            model_id: ID of the model

        Returns:
            List of InferenceMetrics instances
        """
        with self.metrics_lock:
            return self.metrics_history.get(model_id, [])

    def generate_report(self, model_id: str, model_name: str = "") -> ModelPerformanceReport:
        """
        Generate a performance report for a model.

        Args:
            model_id: ID of the model
            model_name: Name of the model

        Returns:
            ModelPerformanceReport instance
        """
        # Get metrics for the model
        metrics = self.get_model_metrics(model_id)

        # Create report
        report = ModelPerformanceReport(
            model_id=model_id,
            model_name=model_name,
            metrics=metrics
        )

        # Update aggregated metrics
        report.update_aggregated_metrics()

        # Store the report
        self.report_cache[report.report_id] = report

        # Save the report to disk
        self._save_report(report)

        return report

    def generate_performance_report(self, model_id: str, model_name: str) -> ModelPerformanceReport:
        """
        Generate a performance report for a model (alias for generate_report).

        Args:
            model_id: ID of the model
            model_name: Name of the model

        Returns:
            ModelPerformanceReport instance
        """
        return self.generate_report(model_id, model_name)

    def _save_report(self, report: ModelPerformanceReport) -> None:
        """
        Save a performance report to disk.

        Args:
            report: ModelPerformanceReport instance
        """
        # Create model directory
        model_dir = os.path.join(self.performance_dir, report.model_id)
        os.makedirs(model_dir, exist_ok=True)

        # Save report
        report_path = os.path.join(model_dir, f"{report.report_id}.json")

        try:
            with open(report_path, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)

            logger.info(f"Saved performance report to {report_path}")

        except Exception as e:
            logger.error(f"Error saving performance report: {e}")

    def load_report(self, report_path: str) -> Optional[ModelPerformanceReport]:
        """
        Load a performance report from disk.

        Args:
            report_path: Path to the report file

        Returns:
            ModelPerformanceReport instance or None if loading failed
        """
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)

            report = ModelPerformanceReport.from_dict(data)
            self.reports[report.report_id] = report

            return report

        except Exception as e:
            logger.error(f"Error loading performance report: {e}")
            return None

    def get_all_reports(self) -> List[ModelPerformanceReport]:
        """
        Get all performance reports.

        Returns:
            List of ModelPerformanceReport instances
        """
        return list(self.report_cache.values())

    def get_report(self, report_id: str) -> Optional[ModelPerformanceReport]:
        """
        Get a performance report by ID.

        Args:
            report_id: ID of the report

        Returns:
            ModelPerformanceReport instance or None if not found
        """
        return self.report_cache.get(report_id)

    def clear_metrics(self, model_id: Optional[str] = None) -> int:
        """
        Clear metrics for a model or all models.

        Args:
            model_id: Optional ID of the model to clear metrics for

        Returns:
            Number of metrics cleared
        """
        with self.metrics_lock:
            if model_id:
                # Clear metrics for a specific model
                metrics_count = len(self.metrics_history.get(model_id, []))
                self.metrics_history[model_id] = []
                return metrics_count
            else:
                # Clear metrics for all models
                metrics_count = sum(len(metrics) for metrics in self.metrics_history.values())
                self.metrics_history = {}
                return metrics_count

    def get_system_performance(self) -> Dict[str, Any]:
        """
        Get current system performance metrics.

        Returns:
            Dictionary with system performance metrics
        """
        performance = {
            "timestamp": time.time(),
            "cpu": {},
            "memory": {},
            "gpu": {}
        }

        # Get CPU metrics
        if PSUTIL_AVAILABLE:
            performance["cpu"]["percent"] = psutil.cpu_percent(interval=0.1)
            performance["cpu"]["count"] = psutil.cpu_count()
            performance["cpu"]["frequency"] = psutil.cpu_freq().current if psutil.cpu_freq() else None

            # Get memory metrics
            memory = psutil.virtual_memory()
            performance["memory"]["total_gb"] = memory.total / (1024 ** 3)
            performance["memory"]["available_gb"] = memory.available / (1024 ** 3)
            performance["memory"]["used_gb"] = memory.used / (1024 ** 3)
            performance["memory"]["percent"] = memory.percent

        # Get GPU metrics
        if TORCH_AVAILABLE and torch.cuda.is_available():
            performance["gpu"]["count"] = torch.cuda.device_count()
            performance["gpu"]["devices"] = []

            for i in range(torch.cuda.device_count()):
                device_info = {
                    "name": torch.cuda.get_device_name(i),
                    "memory_allocated_mb": torch.cuda.memory_allocated(i) / (1024 * 1024),
                    "memory_reserved_mb": torch.cuda.memory_reserved(i) / (1024 * 1024)
                }

                if hasattr(torch.cuda, 'memory_stats'):
                    memory_stats = torch.cuda.memory_stats(i)
                    device_info["memory_active_mb"] = memory_stats.get("active.all.current", 0) / (1024 * 1024)

                if hasattr(torch.cuda, 'utilization'):
                    device_info["utilization"] = torch.cuda.utilization(i)

                performance["gpu"]["devices"].append(device_info)

        return performance


class InferenceTracker:
    """
    Context manager for tracking inference performance.
    """

    def __init__(
        self,
        monitor: PerformanceMonitor,
        model_id: str,
        input_tokens: int = 0,
        parameters: Dict[str, Any] = None
    ):
        """
        Initialize the inference tracker.

        Args:
            monitor: PerformanceMonitor instance
            model_id: ID of the model
            input_tokens: Number of input tokens
            parameters: Additional parameters for the inference
        """
        self.monitor = monitor
        self.model_id = model_id
        self.input_tokens = input_tokens
        self.parameters = parameters or {}
        self.metrics = None
        self.first_token_time = None
        self.output_tokens = 0
        self.metadata = {}
        self.start_time = 0
        self.end_time = 0
        self.memory_usage_start = 0
        self.memory_usage_end = 0

    def start(self, input_text: str = "") -> None:
        """
        Start tracking inference.

        Args:
            input_text: Input text for the inference
        """
        self.start_time = time.time()

        # Count input tokens if not provided
        if self.input_tokens == 0 and input_text:
            self.input_tokens = len(input_text.split())

        # Capture initial memory usage
        if PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            self.memory_usage_start = process.memory_info().rss / (1024 * 1024)

    def stop(self, output_text: str = "") -> InferenceMetrics:
        """
        Stop tracking inference and return metrics.

        Args:
            output_text: Output text from the inference

        Returns:
            InferenceMetrics instance
        """
        self.end_time = time.time()

        # Count output tokens if not provided
        if self.output_tokens == 0 and output_text:
            self.output_tokens = len(output_text.split())

        # Capture final memory usage
        if PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            self.memory_usage_end = process.memory_info().rss / (1024 * 1024)

        # Calculate metrics
        total_time = self.end_time - self.start_time
        latency_ms = total_time * 1000.0
        tokens_per_second = self.output_tokens / total_time if total_time > 0 and self.output_tokens > 0 else 0
        memory_usage_mb = max(self.memory_usage_start, self.memory_usage_end)

        # Create metrics object
        metrics = InferenceMetrics(
            model_id=self.model_id,
            start_time=self.start_time,
            end_time=self.end_time,
            total_time=total_time,
            latency_ms=latency_ms,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            tokens_per_second=tokens_per_second,
            memory_usage_mb=memory_usage_mb,
            parameters=self.parameters,
            metadata=self.metadata
        )

        # Store metrics in monitor
        with self.monitor.metrics_lock:
            if self.model_id not in self.monitor.metrics_history:
                self.monitor.metrics_history[self.model_id] = []

            self.monitor.metrics_history[self.model_id].append(metrics)

        return metrics

    def __enter__(self) -> 'InferenceTracker':
        """
        Start tracking inference when used as a context manager.

        Returns:
            Self
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        End tracking inference when used as a context manager.
        """
        self.stop()

    def record_first_token(self) -> None:
        """
        Record the time when the first token is generated.
        """
        self.first_token_time = time.time()

    def update_output_tokens(self, tokens: int) -> None:
        """
        Update the number of output tokens.

        Args:
            tokens: Number of output tokens
        """
        self.output_tokens = tokens

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the inference metrics.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value


# Example usage
if __name__ == "__main__":
    # Create a performance monitor
    monitor = PerformanceMonitor()

    # Track inference performance
    with InferenceTracker(monitor, "example-model", input_tokens=10) as tracker:
        # Simulate inference
        time.sleep(0.5)  # Simulate time to first token
        tracker.record_first_token()

        time.sleep(1.0)  # Simulate generation time
        tracker.update_output_tokens(20)

        # Add metadata
        tracker.add_metadata("prompt", "Example prompt")
        tracker.add_metadata("temperature", 0.7)

    # Generate a performance report
    report = monitor.generate_performance_report("example-model", "Example Model")

    # Print the report
    print(f"Performance Report for {report.model_name}")
    print(f"Average inference time: {report.avg_inference_time:.4f} seconds")
    print(f"Average tokens per second: {report.avg_tokens_per_second:.2f}")
    print(f"Average time to first token: {report.avg_time_to_first_token:.4f} seconds")

    if report.avg_peak_cpu_memory_mb > 0:
        print(f"Average peak CPU memory: {report.avg_peak_cpu_memory_mb:.2f} MB")

    if report.avg_peak_gpu_memory_mb > 0:
        print(f"Average peak GPU memory: {report.avg_peak_gpu_memory_mb:.2f} MB")

    # Get system performance
    system_perf = monitor.get_system_performance()

    print("\nSystem Performance:")
    if "cpu" in system_perf and "percent" in system_perf["cpu"]:
        print(f"CPU Usage: {system_perf['cpu']['percent']}%")

    if "memory" in system_perf and "percent" in system_perf["memory"]:
        print(f"Memory Usage: {system_perf['memory']['percent']}%")

    if "gpu" in system_perf and "devices" in system_perf["gpu"] and system_perf["gpu"]["devices"]:
        gpu = system_perf["gpu"]["devices"][0]
        print(f"GPU: {gpu.get('name', 'Unknown')}")
        print(f"GPU Memory Allocated: {gpu.get('memory_allocated_mb', 0):.2f} MB")
