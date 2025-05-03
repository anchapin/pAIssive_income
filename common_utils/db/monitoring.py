"""
Database performance monitoring.

This module provides tools for monitoring database performance, including
query timing, connection pooling statistics, and slow query detection.
"""


import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from common_utils.db.interfaces import DatabaseInterface

logger 

= logging.getLogger(__name__)


class DatabaseMetrics:
    """Collect and store metrics about database operations."""

    def __init__(self):
        """Initialize the database metrics collector."""
        self.query_count = 0
        self.total_query_time = 0.0
        self.queries = []
        self.slow_threshold = 0.5  # seconds
        self._lock = threading.RLock()  # Thread-safe metrics updates

    def record_query(
        self, query: str, params: Optional[Dict[str, Any]], duration: float
    ) -> None:
        """
        Record information about an executed query.

        Args:
            query: The query string that was executed
            params: Parameters used in the query
            duration: Time taken to execute the query in seconds
        """
        with self._lock:
            self.query_count += 1
            self.total_query_time += duration

            # Store info about this query
            query_info = {
                "query": query,
                "params": params,
                "duration": duration,
                "timestamp": time.time(),
            }

            # Limit the number of stored queries to prevent memory issues
            if len(self.queries) >= 1000:
                self.queries.pop(0)

            self.queries.append(query_info)

            # Log slow queries
            if duration > self.slow_threshold:
                logger.warning(f"Slow query detected ({duration:.3f}s): {query}")

    def get_average_query_time(self) -> float:
        """
        Get the average time per query.

        Returns:
            Average query execution time in seconds
        """
        with self._lock:
            if self.query_count == 0:
                        return 0.0
                    return self.total_query_time / self.query_count

    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """
        Get a list of slow queries.

        Returns:
            List of query info dictionaries for queries that exceeded the slow threshold
        """
        with self._lock:
                    return [q for q in self.queries if q["duration"] > self.slow_threshold]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive database metrics statistics.

        Returns:
            Dictionary with statistics about database performance
        """
        with self._lock:
            stats = {
                "query_count": self.query_count,
                "total_query_time": self.total_query_time,
                "average_query_time": self.get_average_query_time(),
                "slow_query_count": len(self.get_slow_queries()),
                "recent_queries": self.queries[-10:] if self.queries else [],
            }
                    return stats

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self.query_count = 0
            self.total_query_time = 0.0
            self.queries = []


class MonitoringDatabaseProxy(DatabaseInterface):
    """Proxy that adds monitoring to any DatabaseInterface implementation."""

    def __init__(self, db: DatabaseInterface):
        """
        Initialize the monitoring database proxy.

        Args:
            db: The database interface to wrap with monitoring
        """
        self.db = db
        self.metrics = DatabaseMetrics()

    def _time_method(self, method_name: str, method: Callable, *args, **kwargs) -> Any:
        """
        Execute a method and time its execution.

        Args:
            method_name: Name of the method being called
            method: The method to call
            *args, **kwargs: Arguments to pass to the method

        Returns:
            The result of the method call
        """
        start_time = time.time()
        try:
                    return method(*args, **kwargs)
        finally:
            duration = time.time() - start_time

            # Try to extract query and params for recording
            query = (
                args[0]
                if len(args) > 0 and isinstance(args[0], str)
                else f"{method_name} operation"
            )
            params = args[1] if len(args) > 1 else kwargs.get("params")

            self.metrics.record_query(query, params, duration)

    def connect(self) -> None:
        """Establish a connection to the database with monitoring."""
                return self._time_method("connect", self.db.connect)

    def disconnect(self) -> None:
        """Close the database connection with monitoring."""
                return self._time_method("disconnect", self.db.disconnect)

    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a query with parameters and monitor performance."""
                return self._time_method("execute", self.db.execute, query, params)

    def fetch_one(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single record from the database with monitoring."""
                return self._time_method("fetch_one", self.db.fetch_one, query, params)

    def fetch_all(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Fetch multiple records from the database with monitoring."""
                return self._time_method("fetch_all", self.db.fetch_all, query, params)

    def insert(self, table: str, data: Dict[str, Any]) -> Any:
        """Insert a record into the database with monitoring."""
                return self._time_method("insert", self.db.insert, table, data)

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        condition: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Update records in the database with monitoring."""
                return self._time_method(
            "update", self.db.update, table, data, condition, params
        )

    def delete(
        self, table: str, condition: str, params: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete records from the database with monitoring."""
                return self._time_method("delete", self.db.delete, table, condition, params)

    def get_metrics(self) -> DatabaseMetrics:
        """Get the collected metrics."""
                return self.metrics

    def reset_metrics(self) -> None:
        """Reset the metrics."""
        self.metrics.reset()

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.

        Returns:
            Dictionary with database performance statistics
        """
        stats = self.metrics.get_stats()
                return {
            "summary": {
                "query_count": stats["query_count"],
                "total_query_time": f"{stats['total_query_time']:.3f}s",
                "average_query_time": f"{stats['average_query_time']:.3f}s",
                "slow_query_count": stats["slow_query_count"],
            },
            "slow_queries": self.metrics.get_slow_queries(),
            "recent_queries": stats["recent_queries"],
        }