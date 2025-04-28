"""
Metrics collection and reporting system for pAIssive_income.

This module provides tools for creating, updating, and exporting application metrics
to various backends (Prometheus, CloudWatch, etc.) for monitoring and visualization.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
import threading
import json
import os
from pathlib import Path

# Import our logging module
from common_utils.logging import get_logger

logger = get_logger(__name__)

class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"         # Values that only increase (e.g., request count)
    GAUGE = "gauge"             # Values that can go up and down (e.g., memory usage)
    HISTOGRAM = "histogram"     # Distribution of values (e.g., response times)
    SUMMARY = "summary"         # Similar to histogram but with calculated quantiles


@dataclass
class Metric:
    """Represents a single metric being tracked in the application."""
    name: str
    type: MetricType
    description: str
    value: Union[int, float, Dict[str, Union[int, float]]] = 0
    labels: Dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)


class MetricsRegistry:
    """
    Central registry for all application metrics.
    
    This class manages the creation, updating, and exporting of all metrics
    in the application. It is a singleton to ensure metrics are consistent
    across the application.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetricsRegistry, cls).__new__(cls)
                cls._instance._metrics: Dict[str, Metric] = {}
                cls._instance._export_handlers: List[Callable[[Dict[str, Metric]], None]] = []
        return cls._instance
    
    def create_metric(
        self,
        name: str,
        type: MetricType,
        description: str,
        labels: Optional[Dict[str, str]] = None
    ) -> Metric:
        """
        Create and register a new metric.
        
        Args:
            name: Unique name for the metric
            type: Type of metric (counter, gauge, etc.)
            description: Human-readable description
            labels: Optional key-value pairs for additional context
            
        Returns:
            The newly created metric
        """
        if name in self._metrics:
            logger.warning(f"Metric '{name}' already exists, returning existing metric")
            return self._metrics[name]
        
        metric = Metric(
            name=name,
            type=type,
            description=description,
            labels=labels or {},
        )
        self._metrics[name] = metric
        logger.debug(f"Created new metric: {name} ({type.value})")
        return metric
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a metric by name."""
        return self._metrics.get(name)
    
    def increment(self, name: str, value: Union[int, float] = 1, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a counter metric.
        
        Args:
            name: Name of the metric to increment
            value: Amount to increment by (default: 1)
            labels: Optional additional labels for this increment
        """
        metric = self.get_metric(name)
        if not metric:
            logger.error(f"Cannot increment non-existent metric: {name}")
            return
        
        if metric.type != MetricType.COUNTER:
            logger.error(f"Cannot increment non-counter metric: {name}")
            return
        
        metric.value += value
        metric.last_updated = time.time()
        
        if labels:
            metric.labels.update(labels)
    
    def record(self, name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None) -> None:
        """
        Record a value for a gauge, histogram, or summary metric.
        
        Args:
            name: Name of the metric
            value: Value to record
            labels: Optional additional labels for this record
        """
        metric = self.get_metric(name)
        if not metric:
            logger.error(f"Cannot record value for non-existent metric: {name}")
            return
        
        if metric.type == MetricType.COUNTER:
            logger.error(f"Use increment() instead of record() for counter metrics: {name}")
            return
        
        if metric.type == MetricType.GAUGE:
            metric.value = value
        elif metric.type in (MetricType.HISTOGRAM, MetricType.SUMMARY):
            if isinstance(metric.value, dict):
                # For histograms and summaries, we store all values to compute percentiles later
                timestamp = time.time()
                if "values" not in metric.value:
                    metric.value["values"] = []
                metric.value["values"].append((timestamp, value))
                # Optionally compute running stats
                if "count" not in metric.value:
                    metric.value["count"] = 0
                    metric.value["sum"] = 0
                    metric.value["min"] = float('inf')
                    metric.value["max"] = float('-inf')
                
                metric.value["count"] += 1
                metric.value["sum"] += value
                metric.value["min"] = min(metric.value["min"], value)
                metric.value["max"] = max(metric.value["max"], value)
            else:
                # Initialize the histogram/summary structure
                metric.value = {
                    "values": [(time.time(), value)],
                    "count": 1,
                    "sum": value,
                    "min": value,
                    "max": value
                }
        
        metric.last_updated = time.time()
        
        if labels:
            metric.labels.update(labels)
    
    def get_all_metrics(self) -> Dict[str, Metric]:
        """Get all registered metrics."""
        return self._metrics.copy()
    
    def register_export_handler(self, handler: Callable[[Dict[str, Metric]], None]) -> None:
        """
        Register a function to handle exporting metrics to an external system.
        
        Args:
            handler: Function that takes a dictionary of metrics and exports them
        """
        if handler not in self._export_handlers:
            self._export_handlers.append(handler)
    
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
    labels: Optional[Dict[str, str]] = None
) -> Metric:
    """
    Create and register a new metric.
    
    Args:
        name: Unique name for the metric
        type: Type of metric (counter, gauge, histogram, summary)
        description: Human-readable description
        labels: Optional key-value pairs for additional context
        
    Returns:
        The newly created metric
    """
    if isinstance(type, str):
        type = MetricType(type)
    return _registry.create_metric(name, type, description, labels)


def increment_counter(name: str, value: Union[int, float] = 1, labels: Optional[Dict[str, str]] = None) -> None:
    """
    Increment a counter metric.
    
    Args:
        name: Name of the metric to increment
        value: Amount to increment by (default: 1)
        labels: Optional additional labels for this increment
    """
    _registry.increment(name, value, labels)


def record_value(name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None) -> None:
    """
    Record a value for a gauge, histogram, or summary metric.
    
    Args:
        name: Name of the metric
        value: Value to record
        labels: Optional additional labels for this record
    """
    _registry.record(name, value, labels)


def record_latency(name: str, labels: Optional[Dict[str, str]] = None):
    """
    Context manager for recording the time taken by an operation.
    
    Args:
        name: Name of the latency metric
        labels: Optional labels to attach to the metric
        
    Usage:
        with record_latency("api_request_time", {"endpoint": "/users"}):
            # Code to time goes here
            ...
    """
    class LatencyRecorder:
        def __init__(self, metric_name, labels):
            self.metric_name = metric_name
            self.labels = labels
            self.start_time = None
            
        def __enter__(self):
            self.start_time = time.time()
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            end_time = time.time()
            duration_ms = (end_time - self.start_time) * 1000  # Convert to milliseconds
            record_value(self.metric_name, duration_ms, self.labels)
    
    return LatencyRecorder(name, labels)


def get_metrics() -> Dict[str, Any]:
    """
    Get all metrics in a serializable format.
    
    Returns:
        Dict containing all metrics with their values
    """
    metrics = _registry.get_all_metrics()
    result = {}
    
    for name, metric in metrics.items():
        metric_data = {
            "type": metric.type.value,
            "description": metric.description,
            "labels": metric.labels,
            "created_at": metric.created_at,
            "last_updated": metric.last_updated,
        }
        
        # Handle different value formats based on metric type
        if metric.type in (MetricType.HISTOGRAM, MetricType.SUMMARY) and isinstance(metric.value, dict):
            # For histogram/summary, include computed stats
            stats = {
                "count": metric.value.get("count", 0),
                "sum": metric.value.get("sum", 0),
                "min": metric.value.get("min", 0),
                "max": metric.value.get("max", 0),
            }
            
            # Compute percentiles if we have values
            values = metric.value.get("values", [])
            if values:
                # Extract just the values (not timestamps)
                sorted_values = sorted([v for _, v in values])
                count = len(sorted_values)
                
                if count > 0:
                    # Calculate common percentiles
                    p50_idx = int(count * 0.5)
                    p90_idx = int(count * 0.9)
                    p95_idx = int(count * 0.95)
                    p99_idx = int(count * 0.99)
                    
                    stats["p50"] = sorted_values[p50_idx]
                    stats["p90"] = sorted_values[p90_idx]
                    stats["p95"] = sorted_values[p95_idx]
                    stats["p99"] = sorted_values[p99_idx]
            
            metric_data["value"] = stats
        else:
            # For simple metrics, just include the value directly
            metric_data["value"] = metric.value
        
        result[name] = metric_data
    
    return result


def export_metrics() -> None:
    """Export all metrics using the registered handlers."""
    _registry.export_metrics()


# Example metric export handlers

def prometheus_exporter(metrics: Dict[str, Metric]) -> None:
    """
    Export metrics in Prometheus format.
    
    Args:
        metrics: Dictionary of metrics to export
    """
    logger.debug("Exporting metrics to Prometheus format")
    # Implementation would convert metrics to Prometheus format
    # and expose them via an HTTP endpoint


def json_file_exporter(metrics: Dict[str, Metric], file_path: str) -> None:
    """
    Export metrics to a JSON file.
    
    Args:
        metrics: Dictionary of metrics to export
        file_path: Path to the output JSON file
    """
    logger.debug(f"Exporting metrics to JSON file: {file_path}")
    
    # Convert metrics to a serializable format
    serializable_metrics = {}
    for name, metric in metrics.items():
        metric_data = {
            "type": metric.type.value,
            "description": metric.description,
            "labels": metric.labels,
            "created_at": metric.created_at,
            "last_updated": metric.last_updated,
        }
        
        # Handle different metric types
        if metric.type == MetricType.COUNTER or metric.type == MetricType.GAUGE:
            metric_data["value"] = metric.value
        elif metric.type in (MetricType.HISTOGRAM, MetricType.SUMMARY) and isinstance(metric.value, dict):
            # For histogram/summary, include computed stats
            metric_data["value"] = {
                "count": metric.value.get("count", 0),
                "sum": metric.value.get("sum", 0),
                "min": metric.value.get("min", float('inf')),
                "max": metric.value.get("max", float('-inf')),
            }
            
            # Don't include raw values in the export
        
        serializable_metrics[name] = metric_data
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write to file
    with open(file_path, 'w') as f:
        json.dump(serializable_metrics, f, indent=2)


# Register the JSON file exporter as a default handler
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