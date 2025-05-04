"""
"""
Cache statistics dashboard for the pAIssive Income project.
Cache statistics dashboard for the pAIssive Income project.


This module provides tools for monitoring cache performance, analyzing hit rates,
This module provides tools for monitoring cache performance, analyzing hit rates,
and optimizing cache configurations based on usage patterns.
and optimizing cache configurations based on usage patterns.
"""
"""




import json
import json
import logging
import logging
import threading
import threading
import time
import time
from dataclasses import asdict, dataclass, field
from dataclasses import asdict, dataclass, field
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




@dataclass
@dataclass
class CacheEvent:
    class CacheEvent:
    """Represents a single cache event for analytics."""

    operation: str  # 'get', 'set', 'delete', 'clear'
    namespace: str
    key: str
    success: bool
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    hit: Optional[bool] = None  # Only relevant for 'get' operations
    size_bytes: Optional[int] = None  # Size of cached value if available

    def to_dict(self) -> Dict[str, Any]:
    """Convert event to dictionary for serialization."""
    data = asdict(self)
    data["timestamp"] = data["timestamp"].isoformat()
    return data


    @dataclass
    class CacheNamespaceStats:

    namespace: str
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    clears: int = 0
    total_duration_ms: float = 0
    cache_size_bytes: int = 0

    @property
    def hit_rate(self) -> float:
    """Calculate the hit rate for this namespace."""
    total_gets = self.hits + self.misses
    return self.hits / total_gets if total_gets > 0 else 0

    @property
    def average_duration_ms(self) -> float:
    """Calculate the average operation duration."""
    total_ops = self.hits + self.misses + self.sets + self.deletes + self.clears
    return self.total_duration_ms / total_ops if total_ops > 0 else 0

    def to_dict(self) -> Dict[str, Any]:
    """Convert stats to dictionary with calculated properties."""
    return {
    "namespace": self.namespace,
    "hits": self.hits,
    "misses": self.misses,
    "sets": self.sets,
    "deletes": self.deletes,
    "clears": self.clears,
    "hit_rate": self.hit_rate,
    "total_gets": self.hits + self.misses,
    "average_duration_ms": self.average_duration_ms,
    "cache_size_bytes": self.cache_size_bytes,
    }


    class CacheStatsDashboard:
    """
    """
    Dashboard for monitoring cache performance and statistics.
    Dashboard for monitoring cache performance and statistics.


    This class collects, analyzes, and reports cache statistics to help optimize
    This class collects, analyzes, and reports cache statistics to help optimize
    cache configurations and identify performance bottlenecks.
    cache configurations and identify performance bottlenecks.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    max_events: int = 1000,
    max_events: int = 1000,
    periodic_reporting: bool = False,
    periodic_reporting: bool = False,
    report_interval_seconds: int = 300,
    report_interval_seconds: int = 300,
    ):
    ):
    """
    """
    Initialize a new cache statistics dashboard.
    Initialize a new cache statistics dashboard.


    Args:
    Args:
    max_events: Maximum number of events to store in history
    max_events: Maximum number of events to store in history
    periodic_reporting: Whether to periodically log statistics
    periodic_reporting: Whether to periodically log statistics
    report_interval_seconds: Interval between reports when periodic_reporting is True
    report_interval_seconds: Interval between reports when periodic_reporting is True
    """
    """
    self._events: List[CacheEvent] = []
    self._events: List[CacheEvent] = []
    self._max_events = max_events
    self._max_events = max_events
    self._periodic_reporting = periodic_reporting
    self._periodic_reporting = periodic_reporting
    self._report_interval_seconds = report_interval_seconds
    self._report_interval_seconds = report_interval_seconds
    self._namespace_stats: Dict[str, CacheNamespaceStats] = {}
    self._namespace_stats: Dict[str, CacheNamespaceStats] = {}
    self._lock = threading.RLock()
    self._lock = threading.RLock()


    # Start periodic reporting if enabled
    # Start periodic reporting if enabled
    if periodic_reporting:
    if periodic_reporting:
    self._start_periodic_reporting()
    self._start_periodic_reporting()


    def record_event(self, event: CacheEvent) -> None:
    def record_event(self, event: CacheEvent) -> None:
    """
    """
    Record a cache event for analysis.
    Record a cache event for analysis.


    Args:
    Args:
    event: The cache event to record
    event: The cache event to record
    """
    """
    with self._lock:
    with self._lock:
    # Update namespace statistics
    # Update namespace statistics
    if event.namespace not in self._namespace_stats:
    if event.namespace not in self._namespace_stats:
    self._namespace_stats[event.namespace] = CacheNamespaceStats(
    self._namespace_stats[event.namespace] = CacheNamespaceStats(
    namespace=event.namespace
    namespace=event.namespace
    )
    )


    stats = self._namespace_stats[event.namespace]
    stats = self._namespace_stats[event.namespace]


    # Update relevant metrics based on operation
    # Update relevant metrics based on operation
    if event.operation == "get":
    if event.operation == "get":
    if event.hit:
    if event.hit:
    stats.hits += 1
    stats.hits += 1
    else:
    else:
    stats.misses += 1
    stats.misses += 1
    elif event.operation == "set":
    elif event.operation == "set":
    stats.sets += 1
    stats.sets += 1
    if event.size_bytes is not None:
    if event.size_bytes is not None:
    stats.cache_size_bytes += event.size_bytes
    stats.cache_size_bytes += event.size_bytes
    elif event.operation == "delete":
    elif event.operation == "delete":
    stats.deletes += 1
    stats.deletes += 1
    # We don't know size of deleted item to subtract from cache_size_bytes
    # We don't know size of deleted item to subtract from cache_size_bytes
    elif event.operation == "clear":
    elif event.operation == "clear":
    stats.clears += 1
    stats.clears += 1
    stats.cache_size_bytes = 0
    stats.cache_size_bytes = 0


    stats.total_duration_ms += event.duration_ms
    stats.total_duration_ms += event.duration_ms


    # Add event to history, limiting size
    # Add event to history, limiting size
    self._events.append(event)
    self._events.append(event)
    if len(self._events) > self._max_events:
    if len(self._events) > self._max_events:
    self._events.pop(0)
    self._events.pop(0)


    def get_namespace_stats(self, namespace: Optional[str] = None) -> Dict[str, Any]:
    def get_namespace_stats(self, namespace: Optional[str] = None) -> Dict[str, Any]:
    """
    """
    Get statistics for a specific namespace or all namespaces.
    Get statistics for a specific namespace or all namespaces.


    Args:
    Args:
    namespace: Specific namespace to get stats for, or None for all
    namespace: Specific namespace to get stats for, or None for all


    Returns:
    Returns:
    Dictionary of cache statistics
    Dictionary of cache statistics
    """
    """
    with self._lock:
    with self._lock:
    if namespace:
    if namespace:
    if namespace in self._namespace_stats:
    if namespace in self._namespace_stats:
    return self._namespace_stats[namespace].to_dict()
    return self._namespace_stats[namespace].to_dict()
    return {}
    return {}


    return {ns: stats.to_dict() for ns, stats in self._namespace_stats.items()}
    return {ns: stats.to_dict() for ns, stats in self._namespace_stats.items()}


    def get_stats_summary(self) -> Dict[str, Any]:
    def get_stats_summary(self) -> Dict[str, Any]:
    """
    """
    Get a summary of overall cache statistics.
    Get a summary of overall cache statistics.


    Returns:
    Returns:
    Dictionary with overall cache statistics
    Dictionary with overall cache statistics
    """
    """
    with self._lock:
    with self._lock:
    total_hits = sum(stats.hits for stats in self._namespace_stats.values())
    total_hits = sum(stats.hits for stats in self._namespace_stats.values())
    total_misses = sum(stats.misses for stats in self._namespace_stats.values())
    total_misses = sum(stats.misses for stats in self._namespace_stats.values())
    total_sets = sum(stats.sets for stats in self._namespace_stats.values())
    total_sets = sum(stats.sets for stats in self._namespace_stats.values())
    total_deletes = sum(
    total_deletes = sum(
    stats.deletes for stats in self._namespace_stats.values()
    stats.deletes for stats in self._namespace_stats.values()
    )
    )
    total_clears = sum(stats.clears for stats in self._namespace_stats.values())
    total_clears = sum(stats.clears for stats in self._namespace_stats.values())
    total_size_bytes = sum(
    total_size_bytes = sum(
    stats.cache_size_bytes for stats in self._namespace_stats.values()
    stats.cache_size_bytes for stats in self._namespace_stats.values()
    )
    )


    total_gets = total_hits + total_misses
    total_gets = total_hits + total_misses
    hit_rate = total_hits / total_gets if total_gets > 0 else 0
    hit_rate = total_hits / total_gets if total_gets > 0 else 0


    return {
    return {
    "total_namespaces": len(self._namespace_stats),
    "total_namespaces": len(self._namespace_stats),
    "total_hits": total_hits,
    "total_hits": total_hits,
    "total_misses": total_misses,
    "total_misses": total_misses,
    "total_sets": total_sets,
    "total_sets": total_sets,
    "total_deletes": total_deletes,
    "total_deletes": total_deletes,
    "total_clears": total_clears,
    "total_clears": total_clears,
    "total_gets": total_gets,
    "total_gets": total_gets,
    "total_operations": total_gets
    "total_operations": total_gets
    + total_sets
    + total_sets
    + total_deletes
    + total_deletes
    + total_clears,
    + total_clears,
    "overall_hit_rate": hit_rate,
    "overall_hit_rate": hit_rate,
    "total_size_bytes": total_size_bytes,
    "total_size_bytes": total_size_bytes,
    "total_size_mb": total_size_bytes / (1024 * 1024),
    "total_size_mb": total_size_bytes / (1024 * 1024),
    "event_history_size": len(self._events),
    "event_history_size": len(self._events),
    "namespaces": list(self._namespace_stats.keys()),
    "namespaces": list(self._namespace_stats.keys()),
    }
    }


    def get_recommendations(self) -> Dict[str, Any]:
    def get_recommendations(self) -> Dict[str, Any]:
    """
    """
    Get recommendations for optimizing cache performance.
    Get recommendations for optimizing cache performance.


    Returns:
    Returns:
    Dictionary with cache optimization recommendations
    Dictionary with cache optimization recommendations
    """
    """
    with self._lock:
    with self._lock:
    recommendations = []
    recommendations = []


    # Check namespaces with low hit rates
    # Check namespaces with low hit rates
    for namespace, stats in self._namespace_stats.items():
    for namespace, stats in self._namespace_stats.items():
    if (
    if (
    stats.hits + stats.misses > 10
    stats.hits + stats.misses > 10
    ):  # Only consider namespaces with enough data
    ):  # Only consider namespaces with enough data
    if stats.hit_rate < 0.3:
    if stats.hit_rate < 0.3:
    recommendations.append(
    recommendations.append(
    {
    {
    "namespace": namespace,
    "namespace": namespace,
    "issue": "low_hit_rate",
    "issue": "low_hit_rate",
    "message": (
    "message": (
    f"Low hit rate ({stats.hit_rate:.2%}) for namespace '{namespace}'. "
    f"Low hit rate ({stats.hit_rate:.2%}) for namespace '{namespace}'. "
    "Consider adjusting TTL or caching strategy."
    "Consider adjusting TTL or caching strategy."
    ),
    ),
    "hit_rate": stats.hit_rate,
    "hit_rate": stats.hit_rate,
    }
    }
    )
    )
    elif stats.hit_rate > 0.95 and stats.hits > 100:
    elif stats.hit_rate > 0.95 and stats.hits > 100:
    recommendations.append(
    recommendations.append(
    {
    {
    "namespace": namespace,
    "namespace": namespace,
    "issue": "high_hit_rate",
    "issue": "high_hit_rate",
    "message": (
    "message": (
    f"Very high hit rate ({stats.hit_rate:.2%}) for namespace '{namespace}'. "
    f"Very high hit rate ({stats.hit_rate:.2%}) for namespace '{namespace}'. "
    "Consider increasing TTL to improve performance."
    "Consider increasing TTL to improve performance."
    ),
    ),
    "hit_rate": stats.hit_rate,
    "hit_rate": stats.hit_rate,
    }
    }
    )
    )


    return {
    return {
    "timestamp": datetime.now().isoformat(),
    "timestamp": datetime.now().isoformat(),
    "recommendations": recommendations,
    "recommendations": recommendations,
    }
    }


    def generate_report(self) -> Dict[str, Any]:
    def generate_report(self) -> Dict[str, Any]:
    """
    """
    Generate a comprehensive cache performance report.
    Generate a comprehensive cache performance report.


    Returns:
    Returns:
    Dictionary with full cache performance report
    Dictionary with full cache performance report
    """
    """
    return {
    return {
    "timestamp": datetime.now().isoformat(),
    "timestamp": datetime.now().isoformat(),
    "summary": self.get_stats_summary(),
    "summary": self.get_stats_summary(),
    "namespaces": self.get_namespace_stats(),
    "namespaces": self.get_namespace_stats(),
    "recommendations": self.get_recommendations(),
    "recommendations": self.get_recommendations(),
    }
    }


    def reset_stats(self) -> None:
    def reset_stats(self) -> None:
    """Reset all statistics."""
    with self._lock:
    self._events = []
    self._namespace_stats = {}

    def _start_periodic_reporting(self) -> None:

    def report_stats():
    while self._periodic_reporting:
    time.sleep(self._report_interval_seconds)
    try:
    report = self.generate_report()
    summary = report["summary"]
    logger.info(
    f"Cache stats: {summary['total_gets']} gets (hit rate: {summary['overall_hit_rate']:.2%}), "
    f"{summary['total_sets']} sets, {summary['total_size_mb']:.2f} MB"
    )

    # Log recommendations
    for rec in report["recommendations"]["recommendations"]:
    logger.info(f"Cache recommendation: {rec['message']}")
except Exception as e:
    logger.error(f"Error generating cache stats report: {e}")

    thread = threading.Thread(target=report_stats, daemon=True)
    thread.start()

    def export_report_to_json(self, filepath: str) -> bool:
    """
    """
    Export the current report to a JSON file.
    Export the current report to a JSON file.


    Args:
    Args:
    filepath: Path to save the JSON report
    filepath: Path to save the JSON report


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    try:
    try:
    report = self.generate_report()
    report = self.generate_report()
    with open(filepath, "w") as f:
    with open(filepath, "w") as f:
    json.dump(report, f, indent=2)
    json.dump(report, f, indent=2)
    return True
    return True
except Exception as e:
except Exception as e:
    logger.error(f"Error exporting cache stats report: {e}")
    logger.error(f"Error exporting cache stats report: {e}")
    return False
    return False




    # Create a default instance for use throughout the application
    # Create a default instance for use throughout the application
    stats_dashboard = CacheStatsDashboard(periodic_reporting=True)
    stats_dashboard = CacheStatsDashboard(periodic_reporting=True)