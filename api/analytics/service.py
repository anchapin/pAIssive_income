"""
"""
API Analytics Service.
API Analytics Service.


This module provides a service for collecting, analyzing, and reporting on API usage.
This module provides a service for collecting, analyzing, and reporting on API usage.
"""
"""


import csv
import csv
import io
import io
import logging
import logging
import statistics
import statistics
import threading
import threading
import time
import time
import uuid
import uuid
from collections import deque
from collections import deque
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List
from typing import Any, Callable, Dict, List


from .database import AnalyticsDatabase
from .database import AnalyticsDatabase


# Set up logging
# Set up logging
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class AnalyticsService:
    class AnalyticsService:
    """
    """
    Service for collecting and analyzing API usage data.
    Service for collecting and analyzing API usage data.
    """
    """


    _instance = None
    _instance = None


    @classmethod
    @classmethod
    def get_instance(cls, db_path: str = None):
    def get_instance(cls, db_path: str = None):
    """
    """
    Get or create a singleton instance of the analytics service.
    Get or create a singleton instance of the analytics service.


    Args:
    Args:
    db_path: Optional database path to use when creating the instance
    db_path: Optional database path to use when creating the instance


    Returns:
    Returns:
    AnalyticsService instance
    AnalyticsService instance
    """
    """
    if cls._instance is None:
    if cls._instance is None:
    cls._instance = cls(db_path)
    cls._instance = cls(db_path)
    return cls._instance
    return cls._instance


    def __init__(self, db_path: str = None):
    def __init__(self, db_path: str = None):
    """
    """
    Initialize the analytics service.
    Initialize the analytics service.


    Args:
    Args:
    db_path: Path to the analytics database
    db_path: Path to the analytics database
    """
    """
    self.db = AnalyticsDatabase(db_path)
    self.db = AnalyticsDatabase(db_path)
    self._lock = threading.Lock()
    self._lock = threading.Lock()


    # Real-time monitoring
    # Real-time monitoring
    self._recent_requests = deque(
    self._recent_requests = deque(
    maxlen=1000
    maxlen=1000
    )  # Store recent requests for real-time analysis
    )  # Store recent requests for real-time analysis
    self._alert_thresholds = {
    self._alert_thresholds = {
    "error_rate": 0.05,  # 5% error rate
    "error_rate": 0.05,  # 5% error rate
    "response_time": 1000,  # 1000ms response time
    "response_time": 1000,  # 1000ms response time
    "requests_per_minute": 1000,  # 1000 requests per minute
    "requests_per_minute": 1000,  # 1000 requests per minute
    }
    }
    self._alert_cooldowns = {
    self._alert_cooldowns = {
    "error_rate": datetime.min,
    "error_rate": datetime.min,
    "response_time": datetime.min,
    "response_time": datetime.min,
    "requests_per_minute": datetime.min,
    "requests_per_minute": datetime.min,
    }
    }
    self._alert_cooldown_minutes = 15  # Cooldown period between alerts
    self._alert_cooldown_minutes = 15  # Cooldown period between alerts
    self._alert_handlers = []  # List of alert handler functions
    self._alert_handlers = []  # List of alert handler functions


    # Start background threads
    # Start background threads
    self._stop_event = threading.Event()
    self._stop_event = threading.Event()


    # Daily metrics aggregation thread
    # Daily metrics aggregation thread
    self._aggregation_thread = threading.Thread(
    self._aggregation_thread = threading.Thread(
    target=self._daily_aggregation_task, daemon=True
    target=self._daily_aggregation_task, daemon=True
    )
    )
    self._aggregation_thread.start()
    self._aggregation_thread.start()


    # Real-time monitoring thread
    # Real-time monitoring thread
    self._monitoring_thread = threading.Thread(
    self._monitoring_thread = threading.Thread(
    target=self._real_time_monitoring_task, daemon=True
    target=self._real_time_monitoring_task, daemon=True
    )
    )
    self._monitoring_thread.start()
    self._monitoring_thread.start()


    def track_request(
    def track_request(
    self,
    self,
    method: str,
    method: str,
    path: str,
    path: str,
    endpoint: str,
    endpoint: str,
    version: str = None,
    version: str = None,
    status_code: int = None,
    status_code: int = None,
    response_time: float = None,
    response_time: float = None,
    user_id: str = None,
    user_id: str = None,
    api_key_id: str = None,
    api_key_id: str = None,
    client_ip: str = None,
    client_ip: str = None,
    user_agent: str = None,
    user_agent: str = None,
    request_size: int = None,
    request_size: int = None,
    response_size: int = None,
    response_size: int = None,
    query_params: Dict[str, Any] = None,
    query_params: Dict[str, Any] = None,
    error_type: str = None,
    error_type: str = None,
    error_message: str = None,
    error_message: str = None,
    metadata: Dict[str, Any] = None,
    metadata: Dict[str, Any] = None,
    ) -> str:
    ) -> str:
    """
    """
    Track an API request.
    Track an API request.


    Args:
    Args:
    method: HTTP method (GET, POST, etc.)
    method: HTTP method (GET, POST, etc.)
    path: Request path
    path: Request path
    endpoint: Endpoint name (e.g., "/api/v1/users")
    endpoint: Endpoint name (e.g., "/api/v1/users")
    version: API version
    version: API version
    status_code: HTTP status code
    status_code: HTTP status code
    response_time: Response time in seconds
    response_time: Response time in seconds
    user_id: User ID
    user_id: User ID
    api_key_id: API key ID
    api_key_id: API key ID
    client_ip: Client IP address
    client_ip: Client IP address
    user_agent: User agent string
    user_agent: User agent string
    request_size: Request size in bytes
    request_size: Request size in bytes
    response_size: Response size in bytes
    response_size: Response size in bytes
    query_params: Query parameters
    query_params: Query parameters
    error_type: Error type if an error occurred
    error_type: Error type if an error occurred
    error_message: Error message if an error occurred
    error_message: Error message if an error occurred
    metadata: Additional metadata
    metadata: Additional metadata


    Returns:
    Returns:
    Request ID
    Request ID
    """
    """
    # Generate request ID
    # Generate request ID
    request_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())


    # Create request data
    # Create request data
    request_data = {
    request_data = {
    "id": request_id,
    "id": request_id,
    "timestamp": datetime.now().isoformat(),
    "timestamp": datetime.now().isoformat(),
    "method": method,
    "method": method,
    "path": path,
    "path": path,
    "endpoint": endpoint,
    "endpoint": endpoint,
    "version": version,
    "version": version,
    "status_code": status_code,
    "status_code": status_code,
    "response_time": response_time,
    "response_time": response_time,
    "user_id": user_id,
    "user_id": user_id,
    "api_key_id": api_key_id,
    "api_key_id": api_key_id,
    "client_ip": client_ip,
    "client_ip": client_ip,
    "user_agent": user_agent,
    "user_agent": user_agent,
    "request_size": request_size,
    "request_size": request_size,
    "response_size": response_size,
    "response_size": response_size,
    "query_params": query_params,
    "query_params": query_params,
    "error_type": error_type,
    "error_type": error_type,
    "error_message": error_message,
    "error_message": error_message,
    "metadata": metadata,
    "metadata": metadata,
    }
    }


    # Save request data
    # Save request data
    try:
    try:
    self.db.save_request(request_data)
    self.db.save_request(request_data)


    # Add to recent requests for real-time monitoring
    # Add to recent requests for real-time monitoring
    with self._lock:
    with self._lock:
    self._recent_requests.append(request_data)
    self._recent_requests.append(request_data)


except Exception as e:
except Exception as e:
    logger.error(f"Error saving request data: {e}")
    logger.error(f"Error saving request data: {e}")


    return request_id
    return request_id


    def get_requests(
    def get_requests(
    self,
    self,
    endpoint: str = None,
    endpoint: str = None,
    version: str = None,
    version: str = None,
    user_id: str = None,
    user_id: str = None,
    api_key_id: str = None,
    api_key_id: str = None,
    status_code: int = None,
    status_code: int = None,
    days: int = 7,
    days: int = 7,
    limit: int = 1000,
    limit: int = 1000,
    offset: int = 0,
    offset: int = 0,
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get API requests.
    Get API requests.


    Args:
    Args:
    endpoint: Filter by endpoint
    endpoint: Filter by endpoint
    version: Filter by API version
    version: Filter by API version
    user_id: Filter by user ID
    user_id: Filter by user ID
    api_key_id: Filter by API key ID
    api_key_id: Filter by API key ID
    status_code: Filter by status code
    status_code: Filter by status code
    days: Number of days to include
    days: Number of days to include
    limit: Maximum number of records to return
    limit: Maximum number of records to return
    offset: Number of records to skip
    offset: Number of records to skip


    Returns:
    Returns:
    List of request dictionaries
    List of request dictionaries
    """
    """
    # Calculate time range
    # Calculate time range
    end_time = datetime.now()
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    start_time = end_time - timedelta(days=days)
    time_range = (start_time, end_time)
    time_range = (start_time, end_time)


    return self.db.get_requests(
    return self.db.get_requests(
    endpoint=endpoint,
    endpoint=endpoint,
    version=version,
    version=version,
    user_id=user_id,
    user_id=user_id,
    api_key_id=api_key_id,
    api_key_id=api_key_id,
    status_code=status_code,
    status_code=status_code,
    time_range=time_range,
    time_range=time_range,
    limit=limit,
    limit=limit,
    offset=offset,
    offset=offset,
    )
    )


    def get_daily_metrics(
    def get_daily_metrics(
    self, days: int = 30, endpoint: str = None, version: str = None
    self, days: int = 30, endpoint: str = None, version: str = None
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get daily aggregated metrics.
    Get daily aggregated metrics.


    Args:
    Args:
    days: Number of days to include
    days: Number of days to include
    endpoint: Filter by endpoint
    endpoint: Filter by endpoint
    version: Filter by API version
    version: Filter by API version


    Returns:
    Returns:
    List of daily metrics dictionaries
    List of daily metrics dictionaries
    """
    """
    # Calculate date range
    # Calculate date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")


    return self.db.get_daily_metrics(
    return self.db.get_daily_metrics(
    start_date=start_date, end_date=end_date, endpoint=endpoint, version=version
    start_date=start_date, end_date=end_date, endpoint=endpoint, version=version
    )
    )


    def get_user_metrics(
    def get_user_metrics(
    self, days: int = 30, user_id: str = None
    self, days: int = 30, user_id: str = None
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get user metrics.
    Get user metrics.


    Args:
    Args:
    days: Number of days to include
    days: Number of days to include
    user_id: Filter by user ID
    user_id: Filter by user ID


    Returns:
    Returns:
    List of user metrics dictionaries
    List of user metrics dictionaries
    """
    """
    # Calculate date range
    # Calculate date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")


    return self.db.get_user_metrics(
    return self.db.get_user_metrics(
    start_date=start_date, end_date=end_date, user_id=user_id
    start_date=start_date, end_date=end_date, user_id=user_id
    )
    )


    def get_api_key_metrics(
    def get_api_key_metrics(
    self, days: int = 30, api_key_id: str = None
    self, days: int = 30, api_key_id: str = None
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get API key metrics.
    Get API key metrics.


    Args:
    Args:
    days: Number of days to include
    days: Number of days to include
    api_key_id: Filter by API key ID
    api_key_id: Filter by API key ID


    Returns:
    Returns:
    List of API key metrics dictionaries
    List of API key metrics dictionaries
    """
    """
    # Calculate date range
    # Calculate date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")


    return self.db.get_api_key_metrics(
    return self.db.get_api_key_metrics(
    start_date=start_date, end_date=end_date, api_key_id=api_key_id
    start_date=start_date, end_date=end_date, api_key_id=api_key_id
    )
    )


    def get_endpoint_stats(self, days: int = 30) -> List[Dict[str, Any]]:
    def get_endpoint_stats(self, days: int = 30) -> List[Dict[str, Any]]:
    """
    """
    Get aggregated statistics for each endpoint.
    Get aggregated statistics for each endpoint.


    Args:
    Args:
    days: Number of days to include
    days: Number of days to include


    Returns:
    Returns:
    List of endpoint statistics dictionaries
    List of endpoint statistics dictionaries
    """
    """
    # Calculate date range
    # Calculate date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")


    return self.db.get_endpoint_stats(start_date=start_date, end_date=end_date)
    return self.db.get_endpoint_stats(start_date=start_date, end_date=end_date)


    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
    """
    """
    Get a summary of API usage.
    Get a summary of API usage.


    Args:
    Args:
    days: Number of days to include
    days: Number of days to include


    Returns:
    Returns:
    Dictionary with usage summary
    Dictionary with usage summary
    """
    """
    # Get endpoint stats
    # Get endpoint stats
    endpoint_stats = self.get_endpoint_stats(days)
    endpoint_stats = self.get_endpoint_stats(days)


    # Calculate totals
    # Calculate totals
    total_requests = sum(stat.get("total_requests", 0) for stat in endpoint_stats)
    total_requests = sum(stat.get("total_requests", 0) for stat in endpoint_stats)
    total_errors = sum(stat.get("total_errors", 0) for stat in endpoint_stats)
    total_errors = sum(stat.get("total_errors", 0) for stat in endpoint_stats)
    error_rate = total_errors / total_requests if total_requests > 0 else 0
    error_rate = total_errors / total_requests if total_requests > 0 else 0


    # Calculate average response time
    # Calculate average response time
    total_response_time = sum(
    total_response_time = sum(
    stat.get("avg_response_time", 0) * stat.get("total_requests", 0)
    stat.get("avg_response_time", 0) * stat.get("total_requests", 0)
    for stat in endpoint_stats
    for stat in endpoint_stats
    )
    )
    avg_response_time = (
    avg_response_time = (
    total_response_time / total_requests if total_requests > 0 else 0
    total_response_time / total_requests if total_requests > 0 else 0
    )
    )


    # Get top endpoints
    # Get top endpoints
    top_endpoints = sorted(
    top_endpoints = sorted(
    endpoint_stats, key=lambda x: x.get("total_requests", 0), reverse=True
    endpoint_stats, key=lambda x: x.get("total_requests", 0), reverse=True
    )[:5]
    )[:5]


    # Get user metrics
    # Get user metrics
    user_metrics = self.get_user_metrics(days)
    user_metrics = self.get_user_metrics(days)


    # Calculate unique users
    # Calculate unique users
    unique_users = len(set(metric.get("user_id") for metric in user_metrics))
    unique_users = len(set(metric.get("user_id") for metric in user_metrics))


    # Get API key metrics
    # Get API key metrics
    api_key_metrics = self.get_api_key_metrics(days)
    api_key_metrics = self.get_api_key_metrics(days)


    # Calculate unique API keys
    # Calculate unique API keys
    unique_api_keys = len(
    unique_api_keys = len(
    set(metric.get("api_key_id") for metric in api_key_metrics)
    set(metric.get("api_key_id") for metric in api_key_metrics)
    )
    )


    return {
    return {
    "total_requests": total_requests,
    "total_requests": total_requests,
    "total_errors": total_errors,
    "total_errors": total_errors,
    "error_rate": error_rate,
    "error_rate": error_rate,
    "avg_response_time": avg_response_time,
    "avg_response_time": avg_response_time,
    "unique_users": unique_users,
    "unique_users": unique_users,
    "unique_api_keys": unique_api_keys,
    "unique_api_keys": unique_api_keys,
    "top_endpoints": top_endpoints,
    "top_endpoints": top_endpoints,
    }
    }


    def export_requests_csv(
    def export_requests_csv(
    self,
    self,
    days: int = 30,
    days: int = 30,
    endpoint: str = None,
    endpoint: str = None,
    version: str = None,
    version: str = None,
    user_id: str = None,
    user_id: str = None,
    api_key_id: str = None,
    api_key_id: str = None,
    ) -> str:
    ) -> str:
    """
    """
    Export API requests to CSV.
    Export API requests to CSV.


    Args:
    Args:
    days: Number of days to include
    days: Number of days to include
    endpoint: Filter by endpoint
    endpoint: Filter by endpoint
    version: Filter by API version
    version: Filter by API version
    user_id: Filter by user ID
    user_id: Filter by user ID
    api_key_id: Filter by API key ID
    api_key_id: Filter by API key ID


    Returns:
    Returns:
    CSV string
    CSV string
    """
    """
    # Get requests
    # Get requests
    requests = self.get_requests(
    requests = self.get_requests(
    endpoint=endpoint,
    endpoint=endpoint,
    version=version,
    version=version,
    user_id=user_id,
    user_id=user_id,
    api_key_id=api_key_id,
    api_key_id=api_key_id,
    days=days,
    days=days,
    limit=10000,  # Higher limit for exports
    limit=10000,  # Higher limit for exports
    )
    )


    if not requests:
    if not requests:
    return "No data to export"
    return "No data to export"


    # Create CSV
    # Create CSV
    output = io.StringIO()
    output = io.StringIO()
    writer = csv.DictWriter(
    writer = csv.DictWriter(
    output,
    output,
    fieldnames=[
    fieldnames=[
    "id",
    "id",
    "timestamp",
    "timestamp",
    "method",
    "method",
    "path",
    "path",
    "endpoint",
    "endpoint",
    "version",
    "version",
    "status_code",
    "status_code",
    "response_time",
    "response_time",
    "user_id",
    "user_id",
    "api_key_id",
    "api_key_id",
    "client_ip",
    "client_ip",
    "request_size",
    "request_size",
    "response_size",
    "response_size",
    "error_type",
    "error_type",
    ],
    ],
    )
    )


    writer.writeheader()
    writer.writeheader()


    for request in requests:
    for request in requests:
    # Create a simplified row with only the fields we want
    # Create a simplified row with only the fields we want
    row = {
    row = {
    "id": request.get("id"),
    "id": request.get("id"),
    "timestamp": request.get("timestamp"),
    "timestamp": request.get("timestamp"),
    "method": request.get("method"),
    "method": request.get("method"),
    "path": request.get("path"),
    "path": request.get("path"),
    "endpoint": request.get("endpoint"),
    "endpoint": request.get("endpoint"),
    "version": request.get("version"),
    "version": request.get("version"),
    "status_code": request.get("status_code"),
    "status_code": request.get("status_code"),
    "response_time": request.get("response_time"),
    "response_time": request.get("response_time"),
    "user_id": request.get("user_id"),
    "user_id": request.get("user_id"),
    "api_key_id": request.get("api_key_id"),
    "api_key_id": request.get("api_key_id"),
    "client_ip": request.get("client_ip"),
    "client_ip": request.get("client_ip"),
    "request_size": request.get("request_size"),
    "request_size": request.get("request_size"),
    "response_size": request.get("response_size"),
    "response_size": request.get("response_size"),
    "error_type": request.get("error_type"),
    "error_type": request.get("error_type"),
    }
    }


    writer.writerow(row)
    writer.writerow(row)


    return output.getvalue()
    return output.getvalue()


    def export_metrics_csv(self, days: int = 30) -> str:
    def export_metrics_csv(self, days: int = 30) -> str:
    """
    """
    Export daily metrics to CSV.
    Export daily metrics to CSV.


    Args:
    Args:
    days: Number of days to include
    days: Number of days to include


    Returns:
    Returns:
    CSV string
    CSV string
    """
    """
    # Get daily metrics
    # Get daily metrics
    metrics = self.get_daily_metrics(days)
    metrics = self.get_daily_metrics(days)


    if not metrics:
    if not metrics:
    return "No data to export"
    return "No data to export"


    # Create CSV
    # Create CSV
    output = io.StringIO()
    output = io.StringIO()
    writer = csv.DictWriter(
    writer = csv.DictWriter(
    output,
    output,
    fieldnames=[
    fieldnames=[
    "date",
    "date",
    "endpoint",
    "endpoint",
    "version",
    "version",
    "request_count",
    "request_count",
    "error_count",
    "error_count",
    "avg_response_time",
    "avg_response_time",
    "min_response_time",
    "min_response_time",
    "max_response_time",
    "max_response_time",
    "p95_response_time",
    "p95_response_time",
    "total_request_size",
    "total_request_size",
    "total_response_size",
    "total_response_size",
    "unique_users",
    "unique_users",
    "unique_api_keys",
    "unique_api_keys",
    ],
    ],
    )
    )


    writer.writeheader()
    writer.writeheader()


    for metric in metrics:
    for metric in metrics:
    writer.writerow(metric)
    writer.writerow(metric)


    return output.getvalue()
    return output.getvalue()


    def cleanup_old_data(self, days: int = 365) -> int:
    def cleanup_old_data(self, days: int = 365) -> int:
    """
    """
    Remove data older than the specified number of days.
    Remove data older than the specified number of days.


    Args:
    Args:
    days: Number of days to keep
    days: Number of days to keep


    Returns:
    Returns:
    Number of records deleted
    Number of records deleted
    """
    """
    return self.db.cleanup_old_data(days)
    return self.db.cleanup_old_data(days)


    def _daily_aggregation_task(self) -> None:
    def _daily_aggregation_task(self) -> None:
    """
    """
    Background task for daily metrics aggregation.
    Background task for daily metrics aggregation.
    """
    """
    while not self._stop_event.is_set():
    while not self._stop_event.is_set():
    try:
    try:
    # Get current date
    # Get current date
    today = datetime.now().strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


    # Update metrics for yesterday and today
    # Update metrics for yesterday and today
    self.db.update_daily_metrics(yesterday)
    self.db.update_daily_metrics(yesterday)
    self.db.update_daily_metrics(today)
    self.db.update_daily_metrics(today)


    # Cleanup old data once a day
    # Cleanup old data once a day
    self.db.cleanup_old_data()
    self.db.cleanup_old_data()


    # Sleep for 1 hour
    # Sleep for 1 hour
    self._stop_event.wait(3600)
    self._stop_event.wait(3600)


except Exception as e:
except Exception as e:
    logger.error(f"Error in daily aggregation task: {e}")
    logger.error(f"Error in daily aggregation task: {e}")
    # Sleep for 5 minutes before retrying
    # Sleep for 5 minutes before retrying
    self._stop_event.wait(300)
    self._stop_event.wait(300)


    def register_alert_handler(
    def register_alert_handler(
    self, handler: Callable[[str, Dict[str, Any]], None]
    self, handler: Callable[[str, Dict[str, Any]], None]
    ) -> None:
    ) -> None:
    """
    """
    Register a function to be called when an alert is triggered.
    Register a function to be called when an alert is triggered.


    Args:
    Args:
    handler: Function that takes (alert_message, alert_data) as arguments
    handler: Function that takes (alert_message, alert_data) as arguments
    """
    """
    self._alert_handlers.append(handler)
    self._alert_handlers.append(handler)


    def set_alert_threshold(self, metric: str, threshold: float) -> None:
    def set_alert_threshold(self, metric: str, threshold: float) -> None:
    """
    """
    Set an alert threshold for a specific metric.
    Set an alert threshold for a specific metric.


    Args:
    Args:
    metric: Metric name ('error_rate', 'response_time', 'requests_per_minute')
    metric: Metric name ('error_rate', 'response_time', 'requests_per_minute')
    threshold: Threshold value
    threshold: Threshold value
    """
    """
    if metric in self._alert_thresholds:
    if metric in self._alert_thresholds:
    self._alert_thresholds[metric] = threshold
    self._alert_thresholds[metric] = threshold
    logger.info(f"Set alert threshold for {metric} to {threshold}")
    logger.info(f"Set alert threshold for {metric} to {threshold}")
    else:
    else:
    logger.warning(f"Unknown metric for alert threshold: {metric}")
    logger.warning(f"Unknown metric for alert threshold: {metric}")


    def get_real_time_metrics(self, minutes: int = 5) -> Dict[str, Any]:
    def get_real_time_metrics(self, minutes: int = 5) -> Dict[str, Any]:
    """
    """
    Get real-time metrics for the last N minutes.
    Get real-time metrics for the last N minutes.


    Args:
    Args:
    minutes: Number of minutes to include
    minutes: Number of minutes to include


    Returns:
    Returns:
    Dictionary with real-time metrics
    Dictionary with real-time metrics
    """
    """
    with self._lock:
    with self._lock:
    # Filter requests from the last N minutes
    # Filter requests from the last N minutes
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    recent_requests = [
    recent_requests = [
    r
    r
    for r in self._recent_requests
    for r in self._recent_requests
    if datetime.fromisoformat(r["timestamp"]) > cutoff_time
    if datetime.fromisoformat(r["timestamp"]) > cutoff_time
    ]
    ]


    if not recent_requests:
    if not recent_requests:
    return {
    return {
    "request_count": 0,
    "request_count": 0,
    "error_count": 0,
    "error_count": 0,
    "error_rate": 0,
    "error_rate": 0,
    "avg_response_time": 0,
    "avg_response_time": 0,
    "p95_response_time": 0,
    "p95_response_time": 0,
    "requests_per_minute": 0,
    "requests_per_minute": 0,
    "endpoints": {},
    "endpoints": {},
    }
    }


    # Calculate metrics
    # Calculate metrics
    request_count = len(recent_requests)
    request_count = len(recent_requests)
    error_count = sum(
    error_count = sum(
    1 for r in recent_requests if r.get("status_code", 0) >= 400
    1 for r in recent_requests if r.get("status_code", 0) >= 400
    )
    )
    error_rate = error_count / request_count if request_count > 0 else 0
    error_rate = error_count / request_count if request_count > 0 else 0


    response_times = [
    response_times = [
    r.get("response_time", 0)
    r.get("response_time", 0)
    for r in recent_requests
    for r in recent_requests
    if r.get("response_time") is not None
    if r.get("response_time") is not None
    ]
    ]
    avg_response_time = statistics.mean(response_times) if response_times else 0
    avg_response_time = statistics.mean(response_times) if response_times else 0
    p95_response_time = (
    p95_response_time = (
    statistics.quantiles(response_times, n=20)[-1]
    statistics.quantiles(response_times, n=20)[-1]
    if len(response_times) >= 20
    if len(response_times) >= 20
    else max(response_times, default=0)
    else max(response_times, default=0)
    )
    )


    # Calculate requests per minute
    # Calculate requests per minute
    requests_per_minute = request_count / minutes
    requests_per_minute = request_count / minutes


    # Calculate per-endpoint metrics
    # Calculate per-endpoint metrics
    endpoints = {}
    endpoints = {}
    for r in recent_requests:
    for r in recent_requests:
    endpoint = r.get("endpoint", "unknown")
    endpoint = r.get("endpoint", "unknown")
    if endpoint not in endpoints:
    if endpoint not in endpoints:
    endpoints[endpoint] = {
    endpoints[endpoint] = {
    "request_count": 0,
    "request_count": 0,
    "error_count": 0,
    "error_count": 0,
    "response_times": [],
    "response_times": [],
    }
    }


    endpoints[endpoint]["request_count"] += 1
    endpoints[endpoint]["request_count"] += 1
    if r.get("status_code", 0) >= 400:
    if r.get("status_code", 0) >= 400:
    endpoints[endpoint]["error_count"] += 1
    endpoints[endpoint]["error_count"] += 1


    if r.get("response_time") is not None:
    if r.get("response_time") is not None:
    endpoints[endpoint]["response_times"].append(r.get("response_time"))
    endpoints[endpoint]["response_times"].append(r.get("response_time"))


    # Calculate averages for endpoints
    # Calculate averages for endpoints
    for endpoint, data in endpoints.items():
    for endpoint, data in endpoints.items():
    data["error_rate"] = (
    data["error_rate"] = (
    data["error_count"] / data["request_count"]
    data["error_count"] / data["request_count"]
    if data["request_count"] > 0
    if data["request_count"] > 0
    else 0
    else 0
    )
    )
    data["avg_response_time"] = (
    data["avg_response_time"] = (
    statistics.mean(data["response_times"])
    statistics.mean(data["response_times"])
    if data["response_times"]
    if data["response_times"]
    else 0
    else 0
    )
    )
    data["requests_per_minute"] = data["request_count"] / minutes
    data["requests_per_minute"] = data["request_count"] / minutes
    # Remove raw response times from result
    # Remove raw response times from result
    del data["response_times"]
    del data["response_times"]


    return {
    return {
    "request_count": request_count,
    "request_count": request_count,
    "error_count": error_count,
    "error_count": error_count,
    "error_rate": error_rate,
    "error_rate": error_rate,
    "avg_response_time": avg_response_time,
    "avg_response_time": avg_response_time,
    "p95_response_time": p95_response_time,
    "p95_response_time": p95_response_time,
    "requests_per_minute": requests_per_minute,
    "requests_per_minute": requests_per_minute,
    "endpoints": endpoints,
    "endpoints": endpoints,
    }
    }


    def _real_time_monitoring_task(self) -> None:
    def _real_time_monitoring_task(self) -> None:
    """
    """
    Background task for real-time monitoring.
    Background task for real-time monitoring.
    """
    """
    while not self._stop_event.is_set():
    while not self._stop_event.is_set():
    try:
    try:
    # Get real-time metrics
    # Get real-time metrics
    metrics = self.get_real_time_metrics(minutes=5)
    metrics = self.get_real_time_metrics(minutes=5)


    # Check for alerts
    # Check for alerts
    self._check_alerts(metrics)
    self._check_alerts(metrics)


    # Sleep for 30 seconds
    # Sleep for 30 seconds
    self._stop_event.wait(30)
    self._stop_event.wait(30)


except Exception as e:
except Exception as e:
    logger.error(f"Error in real-time monitoring task: {e}")
    logger.error(f"Error in real-time monitoring task: {e}")
    # Sleep for 1 minute before retrying
    # Sleep for 1 minute before retrying
    self._stop_event.wait(60)
    self._stop_event.wait(60)


    def _check_alerts(self, metrics: Dict[str, Any]) -> None:
    def _check_alerts(self, metrics: Dict[str, Any]) -> None:
    """
    """
    Check metrics against alert thresholds and trigger alerts if needed.
    Check metrics against alert thresholds and trigger alerts if needed.


    Args:
    Args:
    metrics: Real-time metrics
    metrics: Real-time metrics
    """
    """
    now = datetime.now()
    now = datetime.now()


    # Check error rate
    # Check error rate
    if metrics["error_rate"] > self._alert_thresholds["error_rate"]:
    if metrics["error_rate"] > self._alert_thresholds["error_rate"]:
    if now > self._alert_cooldowns["error_rate"]:
    if now > self._alert_cooldowns["error_rate"]:
    self._trigger_alert(
    self._trigger_alert(
    "High API Error Rate",
    "High API Error Rate",
    f"Error rate of {metrics['error_rate']:.2%} exceeds threshold of {self._alert_thresholds['error_rate']:.2%}",
    f"Error rate of {metrics['error_rate']:.2%} exceeds threshold of {self._alert_thresholds['error_rate']:.2%}",
    {
    {
    "metric": "error_rate",
    "metric": "error_rate",
    "value": metrics["error_rate"],
    "value": metrics["error_rate"],
    "threshold": self._alert_thresholds["error_rate"],
    "threshold": self._alert_thresholds["error_rate"],
    "request_count": metrics["request_count"],
    "request_count": metrics["request_count"],
    "error_count": metrics["error_count"],
    "error_count": metrics["error_count"],
    },
    },
    )
    )
    self._alert_cooldowns["error_rate"] = now + timedelta(
    self._alert_cooldowns["error_rate"] = now + timedelta(
    minutes=self._alert_cooldown_minutes
    minutes=self._alert_cooldown_minutes
    )
    )


    # Check response time
    # Check response time
    if metrics["avg_response_time"] > self._alert_thresholds["response_time"]:
    if metrics["avg_response_time"] > self._alert_thresholds["response_time"]:
    if now > self._alert_cooldowns["response_time"]:
    if now > self._alert_cooldowns["response_time"]:
    self._trigger_alert(
    self._trigger_alert(
    "High API Response Time",
    "High API Response Time",
    f"Average response time of {metrics['avg_response_time']:.2f}ms exceeds threshold of {self._alert_thresholds['response_time']}ms",
    f"Average response time of {metrics['avg_response_time']:.2f}ms exceeds threshold of {self._alert_thresholds['response_time']}ms",
    {
    {
    "metric": "response_time",
    "metric": "response_time",
    "value": metrics["avg_response_time"],
    "value": metrics["avg_response_time"],
    "threshold": self._alert_thresholds["response_time"],
    "threshold": self._alert_thresholds["response_time"],
    "p95_response_time": metrics["p95_response_time"],
    "p95_response_time": metrics["p95_response_time"],
    },
    },
    )
    )
    self._alert_cooldowns["response_time"] = now + timedelta(
    self._alert_cooldowns["response_time"] = now + timedelta(
    minutes=self._alert_cooldown_minutes
    minutes=self._alert_cooldown_minutes
    )
    )


    # Check requests per minute
    # Check requests per minute
    if (
    if (
    metrics["requests_per_minute"]
    metrics["requests_per_minute"]
    > self._alert_thresholds["requests_per_minute"]
    > self._alert_thresholds["requests_per_minute"]
    ):
    ):
    if now > self._alert_cooldowns["requests_per_minute"]:
    if now > self._alert_cooldowns["requests_per_minute"]:
    self._trigger_alert(
    self._trigger_alert(
    "High API Request Volume",
    "High API Request Volume",
    f"Request rate of {metrics['requests_per_minute']:.2f} requests/minute exceeds threshold of {self._alert_thresholds['requests_per_minute']} requests/minute",
    f"Request rate of {metrics['requests_per_minute']:.2f} requests/minute exceeds threshold of {self._alert_thresholds['requests_per_minute']} requests/minute",
    {
    {
    "metric": "requests_per_minute",
    "metric": "requests_per_minute",
    "value": metrics["requests_per_minute"],
    "value": metrics["requests_per_minute"],
    "threshold": self._alert_thresholds["requests_per_minute"],
    "threshold": self._alert_thresholds["requests_per_minute"],
    "request_count": metrics["request_count"],
    "request_count": metrics["request_count"],
    },
    },
    )
    )
    self._alert_cooldowns["requests_per_minute"] = now + timedelta(
    self._alert_cooldowns["requests_per_minute"] = now + timedelta(
    minutes=self._alert_cooldown_minutes
    minutes=self._alert_cooldown_minutes
    )
    )


    # Check per-endpoint metrics
    # Check per-endpoint metrics
    for endpoint, data in metrics["endpoints"].items():
    for endpoint, data in metrics["endpoints"].items():
    # Check endpoint error rate
    # Check endpoint error rate
    if (
    if (
    data["error_rate"] > self._alert_thresholds["error_rate"] * 2
    data["error_rate"] > self._alert_thresholds["error_rate"] * 2
    ):  # Higher threshold for individual endpoints
    ):  # Higher threshold for individual endpoints
    alert_key = f"error_rate_{endpoint}"
    alert_key = f"error_rate_{endpoint}"
    if (
    if (
    alert_key not in self._alert_cooldowns
    alert_key not in self._alert_cooldowns
    or now > self._alert_cooldowns[alert_key]
    or now > self._alert_cooldowns[alert_key]
    ):
    ):
    self._trigger_alert(
    self._trigger_alert(
    f"High Error Rate for Endpoint {endpoint}",
    f"High Error Rate for Endpoint {endpoint}",
    f"Error rate of {data['error_rate']:.2%} for endpoint {endpoint} exceeds threshold of {self._alert_thresholds['error_rate'] * 2:.2%}",
    f"Error rate of {data['error_rate']:.2%} for endpoint {endpoint} exceeds threshold of {self._alert_thresholds['error_rate'] * 2:.2%}",
    {
    {
    "metric": "error_rate",
    "metric": "error_rate",
    "endpoint": endpoint,
    "endpoint": endpoint,
    "value": data["error_rate"],
    "value": data["error_rate"],
    "threshold": self._alert_thresholds["error_rate"] * 2,
    "threshold": self._alert_thresholds["error_rate"] * 2,
    "request_count": data["request_count"],
    "request_count": data["request_count"],
    "error_count": data["error_count"],
    "error_count": data["error_count"],
    },
    },
    )
    )
    self._alert_cooldowns[alert_key] = now + timedelta(
    self._alert_cooldowns[alert_key] = now + timedelta(
    minutes=self._alert_cooldown_minutes
    minutes=self._alert_cooldown_minutes
    )
    )


    # Check endpoint response time
    # Check endpoint response time
    if (
    if (
    data["avg_response_time"]
    data["avg_response_time"]
    > self._alert_thresholds["response_time"] * 1.5
    > self._alert_thresholds["response_time"] * 1.5
    ):  # Higher threshold for individual endpoints
    ):  # Higher threshold for individual endpoints
    alert_key = f"response_time_{endpoint}"
    alert_key = f"response_time_{endpoint}"
    if (
    if (
    alert_key not in self._alert_cooldowns
    alert_key not in self._alert_cooldowns
    or now > self._alert_cooldowns[alert_key]
    or now > self._alert_cooldowns[alert_key]
    ):
    ):
    self._trigger_alert(
    self._trigger_alert(
    f"High Response Time for Endpoint {endpoint}",
    f"High Response Time for Endpoint {endpoint}",
    f"Average response time of {data['avg_response_time']:.2f}ms for endpoint {endpoint} exceeds threshold of {self._alert_thresholds['response_time'] * 1.5}ms",
    f"Average response time of {data['avg_response_time']:.2f}ms for endpoint {endpoint} exceeds threshold of {self._alert_thresholds['response_time'] * 1.5}ms",
    {
    {
    "metric": "response_time",
    "metric": "response_time",
    "endpoint": endpoint,
    "endpoint": endpoint,
    "value": data["avg_response_time"],
    "value": data["avg_response_time"],
    "threshold": self._alert_thresholds["response_time"] * 1.5,
    "threshold": self._alert_thresholds["response_time"] * 1.5,
    },
    },
    )
    )
    self._alert_cooldowns[alert_key] = now + timedelta(
    self._alert_cooldowns[alert_key] = now + timedelta(
    minutes=self._alert_cooldown_minutes
    minutes=self._alert_cooldown_minutes
    )
    )


    def _trigger_alert(self, title: str, message: str, data: Dict[str, Any]) -> None:
    def _trigger_alert(self, title: str, message: str, data: Dict[str, Any]) -> None:
    """
    """
    Trigger an alert by calling all registered alert handlers.
    Trigger an alert by calling all registered alert handlers.


    Args:
    Args:
    title: Alert title
    title: Alert title
    message: Alert message
    message: Alert message
    data: Alert data
    data: Alert data
    """
    """
    logger.warning(f"API ALERT: {title} - {message}")
    logger.warning(f"API ALERT: {title} - {message}")


    alert_data = {
    alert_data = {
    "title": title,
    "title": title,
    "message": message,
    "message": message,
    "timestamp": datetime.now().isoformat(),
    "timestamp": datetime.now().isoformat(),
    "data": data,
    "data": data,
    }
    }


    # Call all registered alert handlers
    # Call all registered alert handlers
    for handler in self._alert_handlers:
    for handler in self._alert_handlers:
    try:
    try:
    handler(message, alert_data)
    handler(message, alert_data)
except Exception as e:
except Exception as e:
    logger.error(f"Error in alert handler: {e}")
    logger.error(f"Error in alert handler: {e}")


    def stop(self) -> None:
    def stop(self) -> None:
    """
    """
    Stop the analytics service.
    Stop the analytics service.
    """
    """
    self._stop_event.set()
    self._stop_event.set()
    if self._aggregation_thread.is_alive():
    if self._aggregation_thread.is_alive():
    self._aggregation_thread.join(timeout=5)
    self._aggregation_thread.join(timeout=5)
    if self._monitoring_thread.is_alive():
    if self._monitoring_thread.is_alive():
    self._monitoring_thread.join(timeout=5)
    self._monitoring_thread.join(timeout=5)


    self.db.close()
    self.db.close()




    # Create a global instance of the analytics service
    # Create a global instance of the analytics service
    analytics_service = AnalyticsService.get_instance()
    analytics_service = AnalyticsService.get_instance()