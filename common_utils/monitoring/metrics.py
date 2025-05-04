"""
"""
Metrics collection and reporting system for pAIssive_income.
Metrics collection and reporting system for pAIssive_income.


This module provides tools for creating, updating, and exporting application metrics
This module provides tools for creating, updating, and exporting application metrics
to various backends (Prometheus, CloudWatch, etc.) for monitoring and visualization.
to various backends (Prometheus, CloudWatch, etc.) for monitoring and visualization.
"""
"""




import json
import json
import os
import os
import threading
import threading
import time
import time
from dataclasses import dataclass, field
from dataclasses import dataclass, field
from enum import Enum
from enum import Enum
from pathlib import Path
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from typing import Any, Callable, Dict, List, Optional, Union


from common_utils.logging import get_logger
from common_utils.logging import get_logger


logger
logger


# Import our logging module
# Import our logging module
= get_logger(__name__)
= get_logger(__name__)




class MetricType(Enum):
    class MetricType(Enum):
    """Types of metrics that can be collected."""

    COUNTER = "counter"  # Values that only increase (e.g., request count)
    GAUGE = "gauge"  # Values that can go up and down (e.g., memory usage)
    HISTOGRAM = "histogram"  # Distribution of values (e.g., response times)
    SUMMARY = "summary"  # Similar to histogram but with calculated quantiles


    @dataclass
    class Metric:

    name: str
    type: MetricType
    description: str
    value: Union[int, float, Dict[str, Union[int, float]]] = 0
    labels: Dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)


    class MetricsRegistry:
    """
    """
    Central registry for all application metrics.
    Central registry for all application metrics.


    This class manages the creation, updating, and exporting of all metrics
    This class manages the creation, updating, and exporting of all metrics
    in the application. It is a singleton to ensure metrics are consistent
    in the application. It is a singleton to ensure metrics are consistent
    across the application.
    across the application.
    """
    """


    _instance = None
    _instance = None
    _lock = threading.Lock()
    _lock = threading.Lock()


    def __new__(cls):
    def __new__(cls):
    with cls._lock:
    with cls._lock:
    if cls._instance is None:
    if cls._instance is None:
    cls._instance = super(MetricsRegistry, cls).__new__(cls)
    cls._instance = super(MetricsRegistry, cls).__new__(cls)
    cls._instance._metrics: Dict[str, Metric] = {}
    cls._instance._metrics: Dict[str, Metric] = {}
    cls._instance._export_handlers: List[
    cls._instance._export_handlers: List[
    Callable[[Dict[str, Metric]], None]
    Callable[[Dict[str, Metric]], None]
    ] = []
    ] = []
    return cls._instance
    return cls._instance


    def create_metric(
    def create_metric(
    self,
    self,
    name: str,
    name: str,
    type: MetricType,
    type: MetricType,
    description: str,
    description: str,
    labels: Optional[Dict[str, str]] = None,
    labels: Optional[Dict[str, str]] = None,
    ) -> Metric:
    ) -> Metric:
    """
    """
    Create and register a new metric.
    Create and register a new metric.


    Args:
    Args:
    name: Unique name for the metric
    name: Unique name for the metric
    type: Type of metric (counter, gauge, etc.)
    type: Type of metric (counter, gauge, etc.)
    description: Human-readable description
    description: Human-readable description
    labels: Optional key-value pairs for additional context
    labels: Optional key-value pairs for additional context


    Returns:
    Returns:
    The newly created metric
    The newly created metric
    """
    """
    if name in self._metrics:
    if name in self._metrics:
    logger.warning(f"Metric '{name}' already exists, returning existing metric")
    logger.warning(f"Metric '{name}' already exists, returning existing metric")
    return self._metrics[name]
    return self._metrics[name]


    metric = Metric(
    metric = Metric(
    name=name,
    name=name,
    type=type,
    type=type,
    description=description,
    description=description,
    labels=labels or {},
    labels=labels or {},
    )
    )
    self._metrics[name] = metric
    self._metrics[name] = metric
    logger.debug(f"Created new metric: {name} ({type.value})")
    logger.debug(f"Created new metric: {name} ({type.value})")
    return metric
    return metric


    def get_metric(self, name: str) -> Optional[Metric]:
    def get_metric(self, name: str) -> Optional[Metric]:
    """Get a metric by name."""
    return self._metrics.get(name)

    def increment(
    self,
    name: str,
    value: Union[int, float] = 1,
    labels: Optional[Dict[str, str]] = None,
    ) -> None:
    """
    """
    Increment a counter metric.
    Increment a counter metric.


    Args:
    Args:
    name: Name of the metric to increment
    name: Name of the metric to increment
    value: Amount to increment by (default: 1)
    value: Amount to increment by (default: 1)
    labels: Optional additional labels for this increment
    labels: Optional additional labels for this increment
    """
    """
    metric = self.get_metric(name)
    metric = self.get_metric(name)
    if not metric:
    if not metric:
    logger.error(f"Cannot increment non-existent metric: {name}")
    logger.error(f"Cannot increment non-existent metric: {name}")
    return if metric.type != MetricType.COUNTER:
    return if metric.type != MetricType.COUNTER:
    logger.error(f"Cannot increment non-counter metric: {name}")
    logger.error(f"Cannot increment non-counter metric: {name}")
    return metric.value += value
    return metric.value += value
    metric.last_updated = time.time()
    metric.last_updated = time.time()


    if labels:
    if labels:
    metric.labels.update(labels)
    metric.labels.update(labels)


    def record(
    def record(
    self,
    self,
    name: str,
    name: str,
    value: Union[int, float],
    value: Union[int, float],
    labels: Optional[Dict[str, str]] = None,
    labels: Optional[Dict[str, str]] = None,
    ) -> None:
    ) -> None:
    """
    """
    Record a value for a gauge, histogram, or summary metric.
    Record a value for a gauge, histogram, or summary metric.


    Args:
    Args:
    name: Name of the metric
    name: Name of the metric
    value: Value to record
    value: Value to record
    labels: Optional additional labels for this record
    labels: Optional additional labels for this record
    """
    """
    metric = self.get_metric(name)
    metric = self.get_metric(name)
    if not metric:
    if not metric:
    logger.error(f"Cannot record value for non-existent metric: {name}")
    logger.error(f"Cannot record value for non-existent metric: {name}")
    return if metric.type == MetricType.COUNTER:
    return if metric.type == MetricType.COUNTER:
    logger.error(
    logger.error(
    f"Use increment() instead of record() for counter metrics: {name}"
    f"Use increment() instead of record() for counter metrics: {name}"
    )
    )
    return if metric.type == MetricType.GAUGE:
    return if metric.type == MetricType.GAUGE:
    metric.value = value
    metric.value = value
    elif metric.type in (MetricType.HISTOGRAM, MetricType.SUMMARY):
    elif metric.type in (MetricType.HISTOGRAM, MetricType.SUMMARY):
    if isinstance(metric.value, dict):
    if isinstance(metric.value, dict):
    # For histograms and summaries, we store all values to compute percentiles later
    # For histograms and summaries, we store all values to compute percentiles later
    timestamp = time.time()
    timestamp = time.time()
    if "values" not in metric.value:
    if "values" not in metric.value:
    metric.value["values"] = []
    metric.value["values"] = []
    metric.value["values"].append((timestamp, value))
    metric.value["values"].append((timestamp, value))
    # Optionally compute running stats
    # Optionally compute running stats
    if "count" not in metric.value:
    if "count" not in metric.value:
    metric.value["count"] = 0
    metric.value["count"] = 0
    metric.value["sum"] = 0
    metric.value["sum"] = 0
    metric.value["min"] = float("in")
    metric.value["min"] = float("in")
    metric.value["max"] = float("-in")
    metric.value["max"] = float("-in")


    metric.value["count"] += 1
    metric.value["count"] += 1
    metric.value["sum"] += value
    metric.value["sum"] += value
    metric.value["min"] = min(metric.value["min"], value)
    metric.value["min"] = min(metric.value["min"], value)
    metric.value["max"] = max(metric.value["max"], value)
    metric.value["max"] = max(metric.value["max"], value)
    else:
    else:
    # Initialize the histogram/summary structure
    # Initialize the histogram/summary structure
    metric.value = {
    metric.value = {
    "values": [(time.time(), value)],
    "values": [(time.time(), value)],
    "count": 1,
    "count": 1,
    "sum": value,
    "sum": value,
    "min": value,
    "min": value,
    "max": value,
    "max": value,
    }
    }


    metric.last_updated = time.time()
    metric.last_updated = time.time()


    if labels:
    if labels:
    metric.labels.update(labels)
    metric.labels.update(labels)


    def get_all_metrics(self) -> Dict[str, Metric]:
    def get_all_metrics(self) -> Dict[str, Metric]:
    """Get all registered metrics."""
    return self._metrics.copy()

    def register_export_handler(
    self, handler: Callable[[Dict[str, Metric]], None]
    ) -> None:
    """
    """
    Register a function to handle exporting metrics to an external system.
    Register a function to handle exporting metrics to an external system.


    Args:
    Args:
    handler: Function that takes a dictionary of metrics and exports them
    handler: Function that takes a dictionary of metrics and exports them
    """
    """
    if handler not in self._export_handlers:
    if handler not in self._export_handlers:
    self._export_handlers.append(handler)
    self._export_handlers.append(handler)


    def export_metrics(self) -> None:
    def export_metrics(self) -> None:
    """Export all metrics using the registered handlers."""
    metrics = self.get_all_metrics()
    for handler in self._export_handlers:
    try:
    handler(metrics)
except Exception as e:
    logger.error(f"Error in metric export handler: {e}")


    # Create a global metrics registry
    _registry = MetricsRegistry()


    # Public API functions


    def create_metric(
    name: str,
    type: Union[str, MetricType],
    description: str,
    labels: Optional[Dict[str, str]] = None,
    ) -> Metric:
    """
    """
    Create and register a new metric.
    Create and register a new metric.


    Args:
    Args:
    name: Unique name for the metric
    name: Unique name for the metric
    type: Type of metric (counter, gauge, histogram, summary)
    type: Type of metric (counter, gauge, histogram, summary)
    description: Human-readable description
    description: Human-readable description
    labels: Optional key-value pairs for additional context
    labels: Optional key-value pairs for additional context


    Returns:
    Returns:
    The newly created metric
    The newly created metric
    """
    """
    if isinstance(type, str):
    if isinstance(type, str):
    type = MetricType(type)
    type = MetricType(type)
    return _registry.create_metric(name, type, description, labels)
    return _registry.create_metric(name, type, description, labels)




    def increment_counter(
    def increment_counter(
    name: str, value: Union[int, float] = 1, labels: Optional[Dict[str, str]] = None
    name: str, value: Union[int, float] = 1, labels: Optional[Dict[str, str]] = None
    ) -> None:
    ) -> None:
    """
    """
    Increment a counter metric.
    Increment a counter metric.


    Args:
    Args:
    name: Name of the metric to increment
    name: Name of the metric to increment
    value: Amount to increment by (default: 1)
    value: Amount to increment by (default: 1)
    labels: Optional additional labels for this increment
    labels: Optional additional labels for this increment
    """
    """
    _registry.increment(name, value, labels)
    _registry.increment(name, value, labels)




    def record_value(
    def record_value(
    name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None
    name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None
    ) -> None:
    ) -> None:
    """
    """
    Record a value for a gauge, histogram, or summary metric.
    Record a value for a gauge, histogram, or summary metric.


    Args:
    Args:
    name: Name of the metric
    name: Name of the metric
    value: Value to record
    value: Value to record
    labels: Optional additional labels for this record
    labels: Optional additional labels for this record
    """
    """
    _registry.record(name, value, labels)
    _registry.record(name, value, labels)




    def record_latency(name: str, labels: Optional[Dict[str, str]] = None):
    def record_latency(name: str, labels: Optional[Dict[str, str]] = None):
    """
    """
    Context manager for recording the time taken by an operation.
    Context manager for recording the time taken by an operation.


    Args:
    Args:
    name: Name of the latency metric
    name: Name of the latency metric
    labels: Optional labels to attach to the metric
    labels: Optional labels to attach to the metric


    Usage:
    Usage:
    with record_latency("api_request_time", {"endpoint": "/users"}):
    with record_latency("api_request_time", {"endpoint": "/users"}):
    # Code to time goes here
    # Code to time goes here
    ...
    ...
    """
    """


    class LatencyRecorder:
    class LatencyRecorder:
    def __init__(self, metric_name, labels):
    def __init__(self, metric_name, labels):
    self.metric_name = metric_name
    self.metric_name = metric_name
    self.labels = labels
    self.labels = labels
    self.start_time = None
    self.start_time = None


    def __enter__(self):
    def __enter__(self):
    self.start_time = time.time()
    self.start_time = time.time()
    return self
    return self


    def __exit__(self, exc_type, exc_val, exc_tb):
    def __exit__(self, exc_type, exc_val, exc_tb):
    end_time = time.time()
    end_time = time.time()
    duration_ms = (end_time - self.start_time) * 1000  # Convert to milliseconds
    duration_ms = (end_time - self.start_time) * 1000  # Convert to milliseconds
    record_value(self.metric_name, duration_ms, self.labels)
    record_value(self.metric_name, duration_ms, self.labels)


    return LatencyRecorder(name, labels)
    return LatencyRecorder(name, labels)




    def get_metrics() -> Dict[str, Any]:
    def get_metrics() -> Dict[str, Any]:
    """
    """
    Get all metrics in a serializable format.
    Get all metrics in a serializable format.


    Returns:
    Returns:
    Dict containing all metrics with their values
    Dict containing all metrics with their values
    """
    """
    metrics = _registry.get_all_metrics()
    metrics = _registry.get_all_metrics()
    result = {}
    result = {}


    for name, metric in metrics.items():
    for name, metric in metrics.items():
    metric_data = {
    metric_data = {
    "type": metric.type.value,
    "type": metric.type.value,
    "description": metric.description,
    "description": metric.description,
    "labels": metric.labels,
    "labels": metric.labels,
    "created_at": metric.created_at,
    "created_at": metric.created_at,
    "last_updated": metric.last_updated,
    "last_updated": metric.last_updated,
    }
    }


    # Handle different value formats based on metric type
    # Handle different value formats based on metric type
    if metric.type in (MetricType.HISTOGRAM, MetricType.SUMMARY) and isinstance(
    if metric.type in (MetricType.HISTOGRAM, MetricType.SUMMARY) and isinstance(
    metric.value, dict
    metric.value, dict
    ):
    ):
    # For histogram/summary, include computed stats
    # For histogram/summary, include computed stats
    stats = {
    stats = {
    "count": metric.value.get("count", 0),
    "count": metric.value.get("count", 0),
    "sum": metric.value.get("sum", 0),
    "sum": metric.value.get("sum", 0),
    "min": metric.value.get("min", 0),
    "min": metric.value.get("min", 0),
    "max": metric.value.get("max", 0),
    "max": metric.value.get("max", 0),
    }
    }


    # Compute percentiles if we have values
    # Compute percentiles if we have values
    values = metric.value.get("values", [])
    values = metric.value.get("values", [])
    if values:
    if values:
    # Extract just the values (not timestamps)
    # Extract just the values (not timestamps)
    sorted_values = sorted([v for _, v in values])
    sorted_values = sorted([v for _, v in values])
    count = len(sorted_values)
    count = len(sorted_values)


    if count > 0:
    if count > 0:
    # Calculate common percentiles
    # Calculate common percentiles
    p50_idx = int(count * 0.5)
    p50_idx = int(count * 0.5)
    p90_idx = int(count * 0.9)
    p90_idx = int(count * 0.9)
    p95_idx = int(count * 0.95)
    p95_idx = int(count * 0.95)
    p99_idx = int(count * 0.99)
    p99_idx = int(count * 0.99)


    stats["p50"] = sorted_values[p50_idx]
    stats["p50"] = sorted_values[p50_idx]
    stats["p90"] = sorted_values[p90_idx]
    stats["p90"] = sorted_values[p90_idx]
    stats["p95"] = sorted_values[p95_idx]
    stats["p95"] = sorted_values[p95_idx]
    stats["p99"] = sorted_values[p99_idx]
    stats["p99"] = sorted_values[p99_idx]


    metric_data["value"] = stats
    metric_data["value"] = stats
    else:
    else:
    # For simple metrics, just include the value directly
    # For simple metrics, just include the value directly
    metric_data["value"] = metric.value
    metric_data["value"] = metric.value


    result[name] = metric_data
    result[name] = metric_data


    return result
    return result




    def export_metrics() -> None:
    def export_metrics() -> None:
    """Export all metrics using the registered handlers."""
    _registry.export_metrics()


    # Example metric export handlers


    def prometheus_exporter(metrics: Dict[str, Metric]) -> None:
    """
    """
    Export metrics in Prometheus format.
    Export metrics in Prometheus format.


    Args:
    Args:
    metrics: Dictionary of metrics to export
    metrics: Dictionary of metrics to export
    """
    """
    logger.debug("Exporting metrics to Prometheus format")
    logger.debug("Exporting metrics to Prometheus format")
    # Implementation would convert metrics to Prometheus format
    # Implementation would convert metrics to Prometheus format
    # and expose them via an HTTP endpoint
    # and expose them via an HTTP endpoint




    def json_file_exporter(metrics: Dict[str, Metric], file_path: str) -> None:
    def json_file_exporter(metrics: Dict[str, Metric], file_path: str) -> None:
    """
    """
    Export metrics to a JSON file.
    Export metrics to a JSON file.


    Args:
    Args:
    metrics: Dictionary of metrics to export
    metrics: Dictionary of metrics to export
    file_path: Path to the output JSON file
    file_path: Path to the output JSON file
    """
    """
    logger.debug(f"Exporting metrics to JSON file: {file_path}")
    logger.debug(f"Exporting metrics to JSON file: {file_path}")


    # Convert metrics to a serializable format
    # Convert metrics to a serializable format
    serializable_metrics = {}
    serializable_metrics = {}
    for name, metric in metrics.items():
    for name, metric in metrics.items():
    metric_data = {
    metric_data = {
    "type": metric.type.value,
    "type": metric.type.value,
    "description": metric.description,
    "description": metric.description,
    "labels": metric.labels,
    "labels": metric.labels,
    "created_at": metric.created_at,
    "created_at": metric.created_at,
    "last_updated": metric.last_updated,
    "last_updated": metric.last_updated,
    }
    }


    # Handle different metric types
    # Handle different metric types
    if metric.type == MetricType.COUNTER or metric.type == MetricType.GAUGE:
    if metric.type == MetricType.COUNTER or metric.type == MetricType.GAUGE:
    metric_data["value"] = metric.value
    metric_data["value"] = metric.value
    elif metric.type in (MetricType.HISTOGRAM, MetricType.SUMMARY) and isinstance(
    elif metric.type in (MetricType.HISTOGRAM, MetricType.SUMMARY) and isinstance(
    metric.value, dict
    metric.value, dict
    ):
    ):
    # For histogram/summary, include computed stats
    # For histogram/summary, include computed stats
    metric_data["value"] = {
    metric_data["value"] = {
    "count": metric.value.get("count", 0),
    "count": metric.value.get("count", 0),
    "sum": metric.value.get("sum", 0),
    "sum": metric.value.get("sum", 0),
    "min": metric.value.get("min", float("in")),
    "min": metric.value.get("min", float("in")),
    "max": metric.value.get("max", float("-in")),
    "max": metric.value.get("max", float("-in")),
    }
    }


    # Don't include raw values in the export
    # Don't include raw values in the export


    serializable_metrics[name] = metric_data
    serializable_metrics[name] = metric_data


    # Create directory if it doesn't exist
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)


    # Write to file
    # Write to file
    with open(file_path, "w") as f:
    with open(file_path, "w") as f:
    json.dump(serializable_metrics, f, indent=2)
    json.dump(serializable_metrics, f, indent=2)




    # Register the JSON file exporter as a default handler
    # Register the JSON file exporter as a default handler
    def setup_default_exporters():
    def setup_default_exporters():
    """Set up default metric exporters."""
    # Create a metrics directory in the application's data directory
    metrics_dir = Path("data/metrics")
    metrics_dir.mkdir(parents=True, exist_ok=True)

    # Register the JSON file exporter with a default path
    metrics_file = metrics_dir / "application_metrics.json"
    _registry.register_export_handler(
    lambda metrics: json_file_exporter(metrics, str(metrics_file))
    )


    # Initialize default exporters
    setup_default_exporters()