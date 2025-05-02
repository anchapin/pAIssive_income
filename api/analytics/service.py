"""
API Analytics Service.

This module provides a service for collecting, analyzing, and reporting on API usage.
"""

import csv
import io
import logging
import statistics
import threading
import uuid
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List

from .database import AnalyticsDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for collecting and analyzing API usage data.
    """

    _instance = None

    @classmethod
    def get_instance(cls, db_path: str = None):
        """
        Get or create a singleton instance of the analytics service.

        Args:
            db_path: Optional database path to use when creating the instance

        Returns:
            AnalyticsService instance
        """
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance

    def __init__(self, db_path: str = None):
        """
        Initialize the analytics service.

        Args:
            db_path: Path to the analytics database
        """
        self.db = AnalyticsDatabase(db_path)
        self._lock = threading.Lock()

        # Real-time monitoring
        self._recent_requests = deque(
            maxlen=1000
        )  # Store recent requests for real-time analysis
        self._alert_thresholds = {
            "error_rate": 0.05,  # 5% error rate
            "response_time": 1000,  # 1000ms response time
            "requests_per_minute": 1000,  # 1000 requests per minute
        }
        self._alert_cooldowns = {
            "error_rate": datetime.min,
            "response_time": datetime.min,
            "requests_per_minute": datetime.min,
        }
        self._alert_cooldown_minutes = 15  # Cooldown period between alerts
        self._alert_handlers = []  # List of alert handler functions

        # Start background threads
        self._stop_event = threading.Event()

        # Daily metrics aggregation thread
        self._aggregation_thread = threading.Thread(
            target=self._daily_aggregation_task, daemon=True
        )
        self._aggregation_thread.start()

        # Real-time monitoring thread
        self._monitoring_thread = threading.Thread(
            target=self._real_time_monitoring_task, daemon=True
        )
        self._monitoring_thread.start()

    def track_request(
        self,
        method: str,
        path: str,
        endpoint: str,
        version: str = None,
        status_code: int = None,
        response_time: float = None,
        user_id: str = None,
        api_key_id: str = None,
        client_ip: str = None,
        user_agent: str = None,
        request_size: int = None,
        response_size: int = None,
        query_params: Dict[str, Any] = None,
        error_type: str = None,
        error_message: str = None,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """
        Track an API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            endpoint: Endpoint name (e.g., "/api/v1/users")
            version: API version
            status_code: HTTP status code
            response_time: Response time in seconds
            user_id: User ID
            api_key_id: API key ID
            client_ip: Client IP address
            user_agent: User agent string
            request_size: Request size in bytes
            response_size: Response size in bytes
            query_params: Query parameters
            error_type: Error type if an error occurred
            error_message: Error message if an error occurred
            metadata: Additional metadata

        Returns:
            Request ID
        """
        # Generate request ID
        request_id = str(uuid.uuid4())

        # Create request data
        request_data = {
            "id": request_id,
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "path": path,
            "endpoint": endpoint,
            "version": version,
            "status_code": status_code,
            "response_time": response_time,
            "user_id": user_id,
            "api_key_id": api_key_id,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "request_size": request_size,
            "response_size": response_size,
            "query_params": query_params,
            "error_type": error_type,
            "error_message": error_message,
            "metadata": metadata,
        }

        # Save request data
        try:
            self.db.save_request(request_data)

            # Add to recent requests for real-time monitoring
            with self._lock:
                self._recent_requests.append(request_data)

        except Exception as e:
            logger.error(f"Error saving request data: {e}")

        return request_id

    def get_requests(
        self,
        endpoint: str = None,
        version: str = None,
        user_id: str = None,
        api_key_id: str = None,
        status_code: int = None,
        days: int = 7,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get API requests.

        Args:
            endpoint: Filter by endpoint
            version: Filter by API version
            user_id: Filter by user ID
            api_key_id: Filter by API key ID
            status_code: Filter by status code
            days: Number of days to include
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of request dictionaries
        """
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        time_range = (start_time, end_time)

        return self.db.get_requests(
            endpoint=endpoint,
            version=version,
            user_id=user_id,
            api_key_id=api_key_id,
            status_code=status_code,
            time_range=time_range,
            limit=limit,
            offset=offset,
        )

    def get_daily_metrics(
        self, days: int = 30, endpoint: str = None, version: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get daily aggregated metrics.

        Args:
            days: Number of days to include
            endpoint: Filter by endpoint
            version: Filter by API version

        Returns:
            List of daily metrics dictionaries
        """
        # Calculate date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        return self.db.get_daily_metrics(
            start_date=start_date, end_date=end_date, endpoint=endpoint, version=version
        )

    def get_user_metrics(
        self, days: int = 30, user_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get user metrics.

        Args:
            days: Number of days to include
            user_id: Filter by user ID

        Returns:
            List of user metrics dictionaries
        """
        # Calculate date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        return self.db.get_user_metrics(
            start_date=start_date, end_date=end_date, user_id=user_id
        )

    def get_api_key_metrics(
        self, days: int = 30, api_key_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get API key metrics.

        Args:
            days: Number of days to include
            api_key_id: Filter by API key ID

        Returns:
            List of API key metrics dictionaries
        """
        # Calculate date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        return self.db.get_api_key_metrics(
            start_date=start_date, end_date=end_date, api_key_id=api_key_id
        )

    def get_endpoint_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get aggregated statistics for each endpoint.

        Args:
            days: Number of days to include

        Returns:
            List of endpoint statistics dictionaries
        """
        # Calculate date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        return self.db.get_endpoint_stats(start_date=start_date, end_date=end_date)

    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get a summary of API usage.

        Args:
            days: Number of days to include

        Returns:
            Dictionary with usage summary
        """
        # Get endpoint stats
        endpoint_stats = self.get_endpoint_stats(days)

        # Calculate totals
        total_requests = sum(stat.get("total_requests", 0) for stat in endpoint_stats)
        total_errors = sum(stat.get("total_errors", 0) for stat in endpoint_stats)
        error_rate = total_errors / total_requests if total_requests > 0 else 0

        # Calculate average response time
        total_response_time = sum(
            stat.get("avg_response_time", 0) * stat.get("total_requests", 0)
            for stat in endpoint_stats
        )
        avg_response_time = (
            total_response_time / total_requests if total_requests > 0 else 0
        )

        # Get top endpoints
        top_endpoints = sorted(
            endpoint_stats, key=lambda x: x.get("total_requests", 0), reverse=True
        )[:5]

        # Get user metrics
        user_metrics = self.get_user_metrics(days)

        # Calculate unique users
        unique_users = len(set(metric.get("user_id") for metric in user_metrics))

        # Get API key metrics
        api_key_metrics = self.get_api_key_metrics(days)

        # Calculate unique API keys
        unique_api_keys = len(
            set(metric.get("api_key_id") for metric in api_key_metrics)
        )

        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "unique_users": unique_users,
            "unique_api_keys": unique_api_keys,
            "top_endpoints": top_endpoints,
        }

    def export_requests_csv(
        self,
        days: int = 30,
        endpoint: str = None,
        version: str = None,
        user_id: str = None,
        api_key_id: str = None,
    ) -> str:
        """
        Export API requests to CSV.

        Args:
            days: Number of days to include
            endpoint: Filter by endpoint
            version: Filter by API version
            user_id: Filter by user ID
            api_key_id: Filter by API key ID

        Returns:
            CSV string
        """
        # Get requests
        requests = self.get_requests(
            endpoint=endpoint,
            version=version,
            user_id=user_id,
            api_key_id=api_key_id,
            days=days,
            limit=10000,  # Higher limit for exports
        )

        if not requests:
            return "No data to export"

        # Create CSV
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "id",
                "timestamp",
                "method",
                "path",
                "endpoint",
                "version",
                "status_code",
                "response_time",
                "user_id",
                "api_key_id",
                "client_ip",
                "request_size",
                "response_size",
                "error_type",
            ],
        )

        writer.writeheader()

        for request in requests:
            # Create a simplified row with only the fields we want
            row = {
                "id": request.get("id"),
                "timestamp": request.get("timestamp"),
                "method": request.get("method"),
                "path": request.get("path"),
                "endpoint": request.get("endpoint"),
                "version": request.get("version"),
                "status_code": request.get("status_code"),
                "response_time": request.get("response_time"),
                "user_id": request.get("user_id"),
                "api_key_id": request.get("api_key_id"),
                "client_ip": request.get("client_ip"),
                "request_size": request.get("request_size"),
                "response_size": request.get("response_size"),
                "error_type": request.get("error_type"),
            }

            writer.writerow(row)

        return output.getvalue()

    def export_metrics_csv(self, days: int = 30) -> str:
        """
        Export daily metrics to CSV.

        Args:
            days: Number of days to include

        Returns:
            CSV string
        """
        # Get daily metrics
        metrics = self.get_daily_metrics(days)

        if not metrics:
            return "No data to export"

        # Create CSV
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "date",
                "endpoint",
                "version",
                "request_count",
                "error_count",
                "avg_response_time",
                "min_response_time",
                "max_response_time",
                "p95_response_time",
                "total_request_size",
                "total_response_size",
                "unique_users",
                "unique_api_keys",
            ],
        )

        writer.writeheader()

        for metric in metrics:
            writer.writerow(metric)

        return output.getvalue()

    def cleanup_old_data(self, days: int = 365) -> int:
        """
        Remove data older than the specified number of days.

        Args:
            days: Number of days to keep

        Returns:
            Number of records deleted
        """
        return self.db.cleanup_old_data(days)

    def _daily_aggregation_task(self) -> None:
        """
        Background task for daily metrics aggregation.
        """
        while not self._stop_event.is_set():
            try:
                # Get current date
                today = datetime.now().strftime("%Y-%m-%d")
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

                # Update metrics for yesterday and today
                self.db.update_daily_metrics(yesterday)
                self.db.update_daily_metrics(today)

                # Cleanup old data once a day
                self.db.cleanup_old_data()

                # Sleep for 1 hour
                self._stop_event.wait(3600)

            except Exception as e:
                logger.error(f"Error in daily aggregation task: {e}")
                # Sleep for 5 minutes before retrying
                self._stop_event.wait(300)

    def register_alert_handler(
        self, handler: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """
        Register a function to be called when an alert is triggered.

        Args:
            handler: Function that takes (alert_message, alert_data) as arguments
        """
        self._alert_handlers.append(handler)

    def set_alert_threshold(self, metric: str, threshold: float) -> None:
        """
        Set an alert threshold for a specific metric.

        Args:
            metric: Metric name ('error_rate', 'response_time', 'requests_per_minute')
            threshold: Threshold value
        """
        if metric in self._alert_thresholds:
            self._alert_thresholds[metric] = threshold
            logger.info(f"Set alert threshold for {metric} to {threshold}")
        else:
            logger.warning(f"Unknown metric for alert threshold: {metric}")

    def get_real_time_metrics(self, minutes: int = 5) -> Dict[str, Any]:
        """
        Get real-time metrics for the last N minutes.

        Args:
            minutes: Number of minutes to include

        Returns:
            Dictionary with real-time metrics
        """
        with self._lock:
            # Filter requests from the last N minutes
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            recent_requests = [
                r
                for r in self._recent_requests
                if datetime.fromisoformat(r["timestamp"]) > cutoff_time
            ]

            if not recent_requests:
                return {
                    "request_count": 0,
                    "error_count": 0,
                    "error_rate": 0,
                    "avg_response_time": 0,
                    "p95_response_time": 0,
                    "requests_per_minute": 0,
                    "endpoints": {},
                }

            # Calculate metrics
            request_count = len(recent_requests)
            error_count = sum(
                1 for r in recent_requests if r.get("status_code", 0) >= 400
            )
            error_rate = error_count / request_count if request_count > 0 else 0

            response_times = [
                r.get("response_time", 0)
                for r in recent_requests
                if r.get("response_time") is not None
            ]
            avg_response_time = statistics.mean(response_times) if response_times else 0
            p95_response_time = (
                statistics.quantiles(response_times, n=20)[-1]
                if len(response_times) >= 20
                else max(response_times, default=0)
            )

            # Calculate requests per minute
            requests_per_minute = request_count / minutes

            # Calculate per-endpoint metrics
            endpoints = {}
            for r in recent_requests:
                endpoint = r.get("endpoint", "unknown")
                if endpoint not in endpoints:
                    endpoints[endpoint] = {
                        "request_count": 0,
                        "error_count": 0,
                        "response_times": [],
                    }

                endpoints[endpoint]["request_count"] += 1
                if r.get("status_code", 0) >= 400:
                    endpoints[endpoint]["error_count"] += 1

                if r.get("response_time") is not None:
                    endpoints[endpoint]["response_times"].append(r.get("response_time"))

            # Calculate averages for endpoints
            for endpoint, data in endpoints.items():
                data["error_rate"] = (
                    data["error_count"] / data["request_count"]
                    if data["request_count"] > 0
                    else 0
                )
                data["avg_response_time"] = (
                    statistics.mean(data["response_times"])
                    if data["response_times"]
                    else 0
                )
                data["requests_per_minute"] = data["request_count"] / minutes
                # Remove raw response times from result
                del data["response_times"]

            return {
                "request_count": request_count,
                "error_count": error_count,
                "error_rate": error_rate,
                "avg_response_time": avg_response_time,
                "p95_response_time": p95_response_time,
                "requests_per_minute": requests_per_minute,
                "endpoints": endpoints,
            }

    def _real_time_monitoring_task(self) -> None:
        """
        Background task for real-time monitoring.
        """
        while not self._stop_event.is_set():
            try:
                # Get real-time metrics
                metrics = self.get_real_time_metrics(minutes=5)

                # Check for alerts
                self._check_alerts(metrics)

                # Sleep for 30 seconds
                self._stop_event.wait(30)

            except Exception as e:
                logger.error(f"Error in real-time monitoring task: {e}")
                # Sleep for 1 minute before retrying
                self._stop_event.wait(60)

    def _check_alerts(self, metrics: Dict[str, Any]) -> None:
        """
        Check metrics against alert thresholds and trigger alerts if needed.

        Args:
            metrics: Real-time metrics
        """
        now = datetime.now()

        # Check error rate
        if metrics["error_rate"] > self._alert_thresholds["error_rate"]:
            if now > self._alert_cooldowns["error_rate"]:
                self._trigger_alert(
                    "High API Error Rate",
                    f"Error rate of {metrics['error_rate']:.2%} exceeds threshold of {self._alert_thresholds['error_rate']:.2%}",
                    {
                        "metric": "error_rate",
                        "value": metrics["error_rate"],
                        "threshold": self._alert_thresholds["error_rate"],
                        "request_count": metrics["request_count"],
                        "error_count": metrics["error_count"],
                    },
                )
                self._alert_cooldowns["error_rate"] = now + timedelta(
                    minutes=self._alert_cooldown_minutes
                )

        # Check response time
        if metrics["avg_response_time"] > self._alert_thresholds["response_time"]:
            if now > self._alert_cooldowns["response_time"]:
                self._trigger_alert(
                    "High API Response Time",
                    f"Average response time of {metrics['avg_response_time']:.2f}ms exceeds threshold of {self._alert_thresholds['response_time']}ms",
                    {
                        "metric": "response_time",
                        "value": metrics["avg_response_time"],
                        "threshold": self._alert_thresholds["response_time"],
                        "p95_response_time": metrics["p95_response_time"],
                    },
                )
                self._alert_cooldowns["response_time"] = now + timedelta(
                    minutes=self._alert_cooldown_minutes
                )

        # Check requests per minute
        if (
            metrics["requests_per_minute"]
            > self._alert_thresholds["requests_per_minute"]
        ):
            if now > self._alert_cooldowns["requests_per_minute"]:
                self._trigger_alert(
                    "High API Request Volume",
                    f"Request rate of {metrics['requests_per_minute']:.2f} requests/minute exceeds threshold of {self._alert_thresholds['requests_per_minute']} requests/minute",
                    {
                        "metric": "requests_per_minute",
                        "value": metrics["requests_per_minute"],
                        "threshold": self._alert_thresholds["requests_per_minute"],
                        "request_count": metrics["request_count"],
                    },
                )
                self._alert_cooldowns["requests_per_minute"] = now + timedelta(
                    minutes=self._alert_cooldown_minutes
                )

        # Check per-endpoint metrics
        for endpoint, data in metrics["endpoints"].items():
            # Check endpoint error rate
            if (
                data["error_rate"] > self._alert_thresholds["error_rate"] * 2
            ):  # Higher threshold for individual endpoints
                alert_key = f"error_rate_{endpoint}"
                if (
                    alert_key not in self._alert_cooldowns
                    or now > self._alert_cooldowns[alert_key]
                ):
                    self._trigger_alert(
                        f"High Error Rate for Endpoint {endpoint}",
                        f"Error rate of {data['error_rate']:.2%} for endpoint {endpoint} exceeds threshold of {self._alert_thresholds['error_rate'] * 2:.2%}",
                        {
                            "metric": "error_rate",
                            "endpoint": endpoint,
                            "value": data["error_rate"],
                            "threshold": self._alert_thresholds["error_rate"] * 2,
                            "request_count": data["request_count"],
                            "error_count": data["error_count"],
                        },
                    )
                    self._alert_cooldowns[alert_key] = now + timedelta(
                        minutes=self._alert_cooldown_minutes
                    )

            # Check endpoint response time
            if (
                data["avg_response_time"]
                > self._alert_thresholds["response_time"] * 1.5
            ):  # Higher threshold for individual endpoints
                alert_key = f"response_time_{endpoint}"
                if (
                    alert_key not in self._alert_cooldowns
                    or now > self._alert_cooldowns[alert_key]
                ):
                    self._trigger_alert(
                        f"High Response Time for Endpoint {endpoint}",
                        f"Average response time of {data['avg_response_time']:.2f}ms for endpoint {endpoint} exceeds threshold of {self._alert_thresholds['response_time'] * 1.5}ms",
                        {
                            "metric": "response_time",
                            "endpoint": endpoint,
                            "value": data["avg_response_time"],
                            "threshold": self._alert_thresholds["response_time"] * 1.5,
                        },
                    )
                    self._alert_cooldowns[alert_key] = now + timedelta(
                        minutes=self._alert_cooldown_minutes
                    )

    def _trigger_alert(self, title: str, message: str, data: Dict[str, Any]) -> None:
        """
        Trigger an alert by calling all registered alert handlers.

        Args:
            title: Alert title
            message: Alert message
            data: Alert data
        """
        logger.warning(f"API ALERT: {title} - {message}")

        alert_data = {
            "title": title,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }

        # Call all registered alert handlers
        for handler in self._alert_handlers:
            try:
                handler(message, alert_data)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")

    def stop(self) -> None:
        """
        Stop the analytics service.
        """
        self._stop_event.set()
        if self._aggregation_thread.is_alive():
            self._aggregation_thread.join(timeout=5)
        if self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)

        self.db.close()


# Create a global instance of the analytics service
analytics_service = AnalyticsService.get_instance()
