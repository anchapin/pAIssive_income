"""
"""
API endpoints for monitoring and logging system.
API endpoints for monitoring and logging system.


This module provides API endpoints for accessing monitoring data, health status,
This module provides API endpoints for accessing monitoring data, health status,
system metrics, and log data. It's designed to be integrated with a web framework
system metrics, and log data. It's designed to be integrated with a web framework
like Flask or FastAPI.
like Flask or FastAPI.
"""
"""


import json
import json
import time
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from pathlib import Path
from pathlib import Path
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional


from common_utils.logging import get_logger
from common_utils.logging import get_logger
from common_utils.monitoring.health import get_health_status
from common_utils.monitoring.health import get_health_status
from common_utils.monitoring.metrics import export_metrics, get_metrics
from common_utils.monitoring.metrics import export_metrics, get_metrics
from common_utils.monitoring.system import get_system_metrics
from common_utils.monitoring.system import get_system_metrics


logger
logger


= get_logger(__name__)
= get_logger(__name__)




class MonitoringAPI:
    class MonitoringAPI:
    """
    """
    API endpoints for monitoring and logging.
    API endpoints for monitoring and logging.


    This class provides methods that can be integrated with a web framework
    This class provides methods that can be integrated with a web framework
    to expose monitoring and logging data through a REST API.
    to expose monitoring and logging data through a REST API.
    """
    """


    @staticmethod
    @staticmethod
    def get_metrics(format: str = "json") -> Dict[str, Any]:
    def get_metrics(format: str = "json") -> Dict[str, Any]:
    """
    """
    Get all application metrics.
    Get all application metrics.


    Args:
    Args:
    format: Output format (json or prometheus)
    format: Output format (json or prometheus)


    Returns:
    Returns:
    Dictionary of metrics data
    Dictionary of metrics data
    """
    """
    metrics_data = get_metrics()
    metrics_data = get_metrics()


    if format.lower() == "prometheus":
    if format.lower() == "prometheus":
    # Convert to Prometheus format (simplified version)
    # Convert to Prometheus format (simplified version)
    prometheus_output = []
    prometheus_output = []
    for name, metric_data in metrics_data.items():
    for name, metric_data in metrics_data.items():
    metric_type = metric_data["type"]
    metric_type = metric_data["type"]
    description = metric_data["description"]
    description = metric_data["description"]
    value = metric_data["value"]
    value = metric_data["value"]
    labels = metric_data["labels"]
    labels = metric_data["labels"]


    # Add HELP and TYPE lines
    # Add HELP and TYPE lines
    prometheus_output.append(f"# HELP {name} {description}")
    prometheus_output.append(f"# HELP {name} {description}")
    prometheus_output.append(f"# TYPE {name} {metric_type}")
    prometheus_output.append(f"# TYPE {name} {metric_type}")


    # Format labels if present
    # Format labels if present
    if labels:
    if labels:
    label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
    label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
    prometheus_output.append(f"{name}{{{label_str}}} {value}")
    prometheus_output.append(f"{name}{{{label_str}}} {value}")
    else:
    else:
    prometheus_output.append(f"{name} {value}")
    prometheus_output.append(f"{name} {value}")


    return {"prometheus_format": "\n".join(prometheus_output)}
    return {"prometheus_format": "\n".join(prometheus_output)}


    return {"metrics": metrics_data}
    return {"metrics": metrics_data}


    @staticmethod
    @staticmethod
    def get_health() -> Dict[str, Any]:
    def get_health() -> Dict[str, Any]:
    """
    """
    Get system health status.
    Get system health status.


    Returns:
    Returns:
    Dictionary with health status information
    Dictionary with health status information
    """
    """
    return get_health_status()
    return get_health_status()


    @staticmethod
    @staticmethod
    def get_system() -> Dict[str, Any]:
    def get_system() -> Dict[str, Any]:
    """
    """
    Get system metrics.
    Get system metrics.


    Returns:
    Returns:
    Dictionary with system resource metrics
    Dictionary with system resource metrics
    """
    """
    return {"system": get_system_metrics()}
    return {"system": get_system_metrics()}


    @staticmethod
    @staticmethod
    def get_logs(
    def get_logs(
    start_time: Optional[datetime] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    level: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100,
    limit: int = 100,
    offset: int = 0,
    offset: int = 0,
    search_term: Optional[str] = None,
    search_term: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get application logs.
    Get application logs.


    Args:
    Args:
    start_time: Start time for log filtering
    start_time: Start time for log filtering
    end_time: End time for log filtering
    end_time: End time for log filtering
    level: Filter by log level
    level: Filter by log level
    limit: Maximum number of logs to return
    limit: Maximum number of logs to return
    offset: Offset for pagination
    offset: Offset for pagination
    search_term: Search term to filter logs
    search_term: Search term to filter logs


    Returns:
    Returns:
    Dictionary with log entries and metadata
    Dictionary with log entries and metadata
    """
    """
    # Find log files
    # Find log files
    log_dir = Path("logs")
    log_dir = Path("logs")
    if not log_dir.exists():
    if not log_dir.exists():
    return {
    return {
    "logs": [],
    "logs": [],
    "total": 0,
    "total": 0,
    "metadata": {
    "metadata": {
    "start_time": start_time,
    "start_time": start_time,
    "end_time": end_time,
    "end_time": end_time,
    "level": level,
    "level": level,
    "limit": limit,
    "limit": limit,
    "offset": offset,
    "offset": offset,
    "search_term": search_term,
    "search_term": search_term,
    "error": "Log directory not found",
    "error": "Log directory not found",
    },
    },
    }
    }


    # Default to last 24 hours if no time range specified
    # Default to last 24 hours if no time range specified
    if not end_time:
    if not end_time:
    end_time = datetime.now()
    end_time = datetime.now()
    if not start_time:
    if not start_time:
    start_time = end_time - timedelta(days=1)
    start_time = end_time - timedelta(days=1)


    # Find all log files in the logs directory
    # Find all log files in the logs directory
    log_files = sorted(log_dir.glob("*.log"), reverse=True)
    log_files = sorted(log_dir.glob("*.log"), reverse=True)


    logs = []
    logs = []
    total_matching = 0
    total_matching = 0


    # Process each log file
    # Process each log file
    for log_file in log_files:
    for log_file in log_files:
    try:
    try:
    with open(log_file, "r", encoding="utf-8") as f:
    with open(log_file, "r", encoding="utf-8") as f:
    for line in f:
    for line in f:
    try:
    try:
    # Parse JSON log entry
    # Parse JSON log entry
    log_entry = json.loads(line.strip())
    log_entry = json.loads(line.strip())


    # Extract timestamp
    # Extract timestamp
    log_time = datetime.fromtimestamp(
    log_time = datetime.fromtimestamp(
    log_entry.get("timestamp", 0)
    log_entry.get("timestamp", 0)
    )
    )


    # Apply time filter
    # Apply time filter
    if log_time < start_time or log_time > end_time:
    if log_time < start_time or log_time > end_time:
    continue
    continue


    # Apply level filter
    # Apply level filter
    if (
    if (
    level
    level
    and log_entry.get("level", "").lower() != level.lower()
    and log_entry.get("level", "").lower() != level.lower()
    ):
    ):
    continue
    continue


    # Apply search term filter
    # Apply search term filter
    if search_term:
    if search_term:
    message = log_entry.get("message", "")
    message = log_entry.get("message", "")
    if search_term.lower() not in message.lower():
    if search_term.lower() not in message.lower():
    continue
    continue


    # Count total matching entries for pagination
    # Count total matching entries for pagination
    total_matching += 1
    total_matching += 1


    # Apply pagination
    # Apply pagination
    if total_matching <= offset:
    if total_matching <= offset:
    continue
    continue


    if len(logs) >= limit:
    if len(logs) >= limit:
    continue
    continue


    # Add to results
    # Add to results
    logs.append(log_entry)
    logs.append(log_entry)


except json.JSONDecodeError:
except json.JSONDecodeError:
    # Skip non-JSON lines
    # Skip non-JSON lines
    continue
    continue
except Exception as e:
except Exception as e:
    logger.error(f"Error reading log file {log_file}: {e}")
    logger.error(f"Error reading log file {log_file}: {e}")


    return {
    return {
    "logs": logs,
    "logs": logs,
    "total": total_matching,
    "total": total_matching,
    "metadata": {
    "metadata": {
    "start_time": start_time.isoformat() if start_time else None,
    "start_time": start_time.isoformat() if start_time else None,
    "end_time": end_time.isoformat() if end_time else None,
    "end_time": end_time.isoformat() if end_time else None,
    "level": level,
    "level": level,
    "limit": limit,
    "limit": limit,
    "offset": offset,
    "offset": offset,
    "search_term": search_term,
    "search_term": search_term,
    },
    },
    }
    }


    @staticmethod
    @staticmethod
    def export_dashboard_data() -> Dict[str, Any]:
    def export_dashboard_data() -> Dict[str, Any]:
    """
    """
    Export all monitoring data for dashboards.
    Export all monitoring data for dashboards.


    This method combines metrics, health status, and system metrics
    This method combines metrics, health status, and system metrics
    into a single response for easy consumption by dashboards.
    into a single response for easy consumption by dashboards.


    Returns:
    Returns:
    Dictionary with combined monitoring data
    Dictionary with combined monitoring data
    """
    """
    # Export metrics to update any cached values
    # Export metrics to update any cached values
    export_metrics()
    export_metrics()


    # Combine all monitoring data
    # Combine all monitoring data
    return {
    return {
    "metrics": get_metrics(),
    "metrics": get_metrics(),
    "health": get_health_status(),
    "health": get_health_status(),
    "system": get_system_metrics(),
    "system": get_system_metrics(),
    "timestamp": datetime.now().isoformat(),
    "timestamp": datetime.now().isoformat(),
    }
    }




    # Register API routes with Flask
    # Register API routes with Flask
    def register_monitoring_api(app):
    def register_monitoring_api(app):
    """
    """
    Register monitoring API endpoints with a Flask application.
    Register monitoring API endpoints with a Flask application.


    Args:
    Args:
    app: Flask application instance
    app: Flask application instance
    """
    """
    monitoring_api = MonitoringAPI()
    monitoring_api = MonitoringAPI()


    @app.route("/api/metrics", methods=["GET"])
    @app.route("/api/metrics", methods=["GET"])
    def api_metrics():
    def api_metrics():
    format = app.request.args.get("format", "json")
    format = app.request.args.get("format", "json")
    return monitoring_api.get_metrics(format)
    return monitoring_api.get_metrics(format)


    @app.route("/api/health", methods=["GET"])
    @app.route("/api/health", methods=["GET"])
    def api_health():
    def api_health():
    return monitoring_api.get_health()
    return monitoring_api.get_health()


    @app.route("/api/system", methods=["GET"])
    @app.route("/api/system", methods=["GET"])
    def api_system():
    def api_system():
    return monitoring_api.get_system()
    return monitoring_api.get_system()


    @app.route("/api/logs", methods=["GET"])
    @app.route("/api/logs", methods=["GET"])
    def api_logs():
    def api_logs():
    # Parse request parameters
    # Parse request parameters
    request = app.request
    request = app.request
    start_time = request.args.get("start_time")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    end_time = request.args.get("end_time")
    level = request.args.get("level")
    level = request.args.get("level")
    limit = int(request.args.get("limit", 100))
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    offset = int(request.args.get("offset", 0))
    search_term = request.args.get("search")
    search_term = request.args.get("search")


    # Convert string timestamps to datetime objects
    # Convert string timestamps to datetime objects
    if start_time:
    if start_time:
    start_time = datetime.fromisoformat(start_time)
    start_time = datetime.fromisoformat(start_time)
    if end_time:
    if end_time:
    end_time = datetime.fromisoformat(end_time)
    end_time = datetime.fromisoformat(end_time)


    return monitoring_api.get_logs(
    return monitoring_api.get_logs(
    start_time, end_time, level, limit, offset, search_term
    start_time, end_time, level, limit, offset, search_term
    )
    )


    @app.route("/api/dashboard", methods=["GET"])
    @app.route("/api/dashboard", methods=["GET"])
    def api_dashboard():
    def api_dashboard():
    return monitoring_api.export_dashboard_data()
    return monitoring_api.export_dashboard_data()




    # Register API routes with FastAPI
    # Register API routes with FastAPI
    def register_fastapi_monitoring_api(app):
    def register_fastapi_monitoring_api(app):
    """
    """
    Register monitoring API endpoints with a FastAPI application.
    Register monitoring API endpoints with a FastAPI application.


    Args:
    Args:
    app: FastAPI application instance
    app: FastAPI application instance
    """
    """
    monitoring_api = MonitoringAPI()
    monitoring_api = MonitoringAPI()


    @app.get("/api/metrics")
    @app.get("/api/metrics")
    def api_metrics(format: str = "json"):
    def api_metrics(format: str = "json"):
    return monitoring_api.get_metrics(format)
    return monitoring_api.get_metrics(format)


    @app.get("/api/health")
    @app.get("/api/health")
    def api_health():
    def api_health():
    return monitoring_api.get_health()
    return monitoring_api.get_health()


    @app.get("/api/system")
    @app.get("/api/system")
    def api_system():
    def api_system():
    return monitoring_api.get_system()
    return monitoring_api.get_system()


    @app.get("/api/logs")
    @app.get("/api/logs")
    def api_logs(
    def api_logs(
    start_time: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    end_time: Optional[str] = None,
    level: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100,
    limit: int = 100,
    offset: int = 0,
    offset: int = 0,
    search: Optional[str] = None,
    search: Optional[str] = None,
    ):
    ):
    # Convert string timestamps to datetime objects
    # Convert string timestamps to datetime objects
    start_dt = None
    start_dt = None
    end_dt = None
    end_dt = None


    if start_time:
    if start_time:
    start_dt = datetime.fromisoformat(start_time)
    start_dt = datetime.fromisoformat(start_time)
    if end_time:
    if end_time:
    end_dt = datetime.fromisoformat(end_time)
    end_dt = datetime.fromisoformat(end_time)


    return monitoring_api.get_logs(start_dt, end_dt, level, limit, offset, search)
    return monitoring_api.get_logs(start_dt, end_dt, level, limit, offset, search)


    @app.get("/api/dashboard")
    @app.get("/api/dashboard")
    def api_dashboard():
    def api_dashboard():
    return monitoring_api.export_dashboard_data()
    return monitoring_api.export_dashboard_data()