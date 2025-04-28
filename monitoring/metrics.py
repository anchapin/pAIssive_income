"""
Metrics collection for the pAIssive_income project.

This module provides functions for collecting and exposing metrics.
"""

import time
import threading
from typing import Dict, Any, Optional, Callable
from collections import defaultdict

# In-memory storage for metrics
_metrics = {
    "counters": defaultdict(int),
    "gauges": {},
    "histograms": defaultdict(list),
    "timers": {}
}

# Lock for thread-safe access to metrics
_metrics_lock = threading.RLock()


def initialize_metrics():
    """
    Initialize the metrics collection.
    """
    with _metrics_lock:
        _metrics["counters"] = defaultdict(int)
        _metrics["gauges"] = {}
        _metrics["histograms"] = defaultdict(list)
        _metrics["timers"] = {}


def increment_counter(name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
    """
    Increment a counter metric.
    
    Args:
        name: Name of the counter
        value: Value to increment by (default: 1)
        labels: Optional labels for the counter
    """
    with _metrics_lock:
        key = _get_metric_key(name, labels)
        _metrics["counters"][key] += value


def observe_value(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """
    Observe a value for a gauge or histogram metric.
    
    Args:
        name: Name of the metric
        value: Value to observe
        labels: Optional labels for the metric
    """
    with _metrics_lock:
        key = _get_metric_key(name, labels)
        
        # Update gauge
        _metrics["gauges"][key] = value
        
        # Add to histogram
        _metrics["histograms"][key].append(value)
        
        # Limit histogram size
        if len(_metrics["histograms"][key]) > 1000:
            _metrics["histograms"][key] = _metrics["histograms"][key][-1000:]


def start_timer(name: str, labels: Optional[Dict[str, str]] = None) -> Callable[[], float]:
    """
    Start a timer for measuring execution time.
    
    Args:
        name: Name of the timer
        labels: Optional labels for the timer
        
    Returns:
        Function that stops the timer and returns the elapsed time
    """
    start_time = time.time()
    
    def stop_timer() -> float:
        elapsed = time.time() - start_time
        with _metrics_lock:
            key = _get_metric_key(name, labels)
            _metrics["timers"][key] = elapsed
            # Also add to histogram for aggregation
            _metrics["histograms"][f"{key}_histogram"].append(elapsed)
            if len(_metrics["histograms"][f"{key}_histogram"]) > 1000:
                _metrics["histograms"][f"{key}_histogram"] = _metrics["histograms"][f"{key}_histogram"][-1000:]
        return elapsed
    
    return stop_timer


def get_metrics() -> Dict[str, Any]:
    """
    Get all collected metrics.
    
    Returns:
        Dictionary of metrics
    """
    with _metrics_lock:
        # Calculate histogram statistics
        histograms_stats = {}
        for key, values in _metrics["histograms"].items():
            if not values:
                continue
                
            values.sort()
            count = len(values)
            histograms_stats[key] = {
                "count": count,
                "min": values[0],
                "max": values[-1],
                "avg": sum(values) / count,
                "p50": values[count // 2],
                "p90": values[int(count * 0.9)],
                "p95": values[int(count * 0.95)],
                "p99": values[int(count * 0.99)] if count >= 100 else values[-1]
            }
        
        # Return a copy of the metrics
        return {
            "counters": dict(_metrics["counters"]),
            "gauges": dict(_metrics["gauges"]),
            "timers": dict(_metrics["timers"]),
            "histograms": histograms_stats
        }


def _get_metric_key(name: str, labels: Optional[Dict[str, str]] = None) -> str:
    """
    Get a unique key for a metric based on its name and labels.
    
    Args:
        name: Name of the metric
        labels: Optional labels for the metric
        
    Returns:
        Unique key for the metric
    """
    if not labels:
        return name
        
    # Sort labels by key to ensure consistent ordering
    sorted_labels = sorted(labels.items())
    labels_str = ",".join(f"{k}={v}" for k, v in sorted_labels)
    
    return f"{name}{{{labels_str}}}"
