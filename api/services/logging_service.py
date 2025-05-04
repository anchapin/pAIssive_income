"""
"""
Logging service for the API server.
Logging service for the API server.


This module provides enhanced logging capabilities with structured logs,
This module provides enhanced logging capabilities with structured logs,
log rotation, and security event logging.
log rotation, and security event logging.
"""
"""


import json
import json
import logging
import logging
import os
import os
import sys
import sys
import time
import time
import traceback
import traceback
from datetime import datetime, timezone
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


# Configure default logger
# Configure default logger
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class SecurityLogFilter(logging.Filter):
    class SecurityLogFilter(logging.Filter):
    """Filter for security-related log events."""

    def __init__(self, security_levels: List[str] = None):
    """
    """
    Initialize the security log filter.
    Initialize the security log filter.


    Args:
    Args:
    security_levels: List of security levels to include
    security_levels: List of security levels to include
    """
    """
    super().__init__()
    super().__init__()
    self.security_levels = security_levels or ["SECURITY", "AUTH", "AUDIT"]
    self.security_levels = security_levels or ["SECURITY", "AUTH", "AUDIT"]


    def filter(self, record):
    def filter(self, record):
    """
    """
    Filter log records.
    Filter log records.


    Args:
    Args:
    record: Log record
    record: Log record


    Returns:
    Returns:
    True if the record should be logged, False otherwise
    True if the record should be logged, False otherwise
    """
    """
    # Check if the record has a security level
    # Check if the record has a security level
    if (
    if (
    hasattr(record, "security_level")
    hasattr(record, "security_level")
    and record.security_level in self.security_levels
    and record.security_level in self.security_levels
    ):
    ):
    return True
    return True


    # Check if the record has security in the message
    # Check if the record has security in the message
    if any(
    if any(
    level.lower() in record.getMessage().lower()
    level.lower() in record.getMessage().lower()
    for level in self.security_levels
    for level in self.security_levels
    ):
    ):
    return True
    return True


    return False
    return False




    class JsonFormatter(logging.Formatter):
    class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, include_timestamp: bool = True):
    """
    """
    Initialize the JSON formatter.
    Initialize the JSON formatter.


    Args:
    Args:
    include_timestamp: Whether to include a timestamp in the log
    include_timestamp: Whether to include a timestamp in the log
    """
    """
    super().__init__()
    super().__init__()
    self.include_timestamp = include_timestamp
    self.include_timestamp = include_timestamp


    def format(self, record):
    def format(self, record):
    """
    """
    Format a log record as JSON.
    Format a log record as JSON.


    Args:
    Args:
    record: Log record
    record: Log record


    Returns:
    Returns:
    JSON-formatted log message
    JSON-formatted log message
    """
    """
    log_data = {
    log_data = {
    "level": record.levelname,
    "level": record.levelname,
    "message": record.getMessage(),
    "message": record.getMessage(),
    "logger": record.name,
    "logger": record.name,
    "path": record.pathname,
    "path": record.pathname,
    "line": record.lineno,
    "line": record.lineno,
    "function": record.funcName,
    "function": record.funcName,
    }
    }


    # Add timestamp
    # Add timestamp
    if self.include_timestamp:
    if self.include_timestamp:
    log_data["timestamp"] = datetime.fromtimestamp(
    log_data["timestamp"] = datetime.fromtimestamp(
    record.created, tz=timezone.utc
    record.created, tz=timezone.utc
    ).isoformat()
    ).isoformat()


    # Add exception info if available
    # Add exception info if available
    if record.exc_info:
    if record.exc_info:
    log_data["exception"] = {
    log_data["exception"] = {
    "type": record.exc_info[0].__name__,
    "type": record.exc_info[0].__name__,
    "message": str(record.exc_info[1]),
    "message": str(record.exc_info[1]),
    "traceback": traceback.format_exception(*record.exc_info),
    "traceback": traceback.format_exception(*record.exc_info),
    }
    }


    # Add extra fields
    # Add extra fields
    for key, value in record.__dict__.items():
    for key, value in record.__dict__.items():
    if key not in [
    if key not in [
    "args",
    "args",
    "asctime",
    "asctime",
    "created",
    "created",
    "exc_info",
    "exc_info",
    "exc_text",
    "exc_text",
    "filename",
    "filename",
    "funcName",
    "funcName",
    "id",
    "id",
    "levelname",
    "levelname",
    "levelno",
    "levelno",
    "lineno",
    "lineno",
    "module",
    "module",
    "msecs",
    "msecs",
    "message",
    "message",
    "msg",
    "msg",
    "name",
    "name",
    "pathname",
    "pathname",
    "process",
    "process",
    "processName",
    "processName",
    "relativeCreated",
    "relativeCreated",
    "stack_info",
    "stack_info",
    "thread",
    "thread",
    "threadName",
    "threadName",
    ]:
    ]:
    log_data[key] = value
    log_data[key] = value


    return json.dumps(log_data)
    return json.dumps(log_data)




    class LoggingService:
    class LoggingService:
    """Service for enhanced logging capabilities."""

    def __init__(
    self,
    log_dir: str = None,
    log_level: int = logging.INFO,
    max_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 10,
    console_output: bool = True,
    json_format: bool = True,
    security_log_enabled: bool = True,
    ):
    """
    """
    Initialize the logging service.
    Initialize the logging service.


    Args:
    Args:
    log_dir: Directory for log files
    log_dir: Directory for log files
    log_level: Logging level
    log_level: Logging level
    max_size: Maximum size of log files before rotation
    max_size: Maximum size of log files before rotation
    backup_count: Number of backup files to keep
    backup_count: Number of backup files to keep
    console_output: Whether to output logs to console
    console_output: Whether to output logs to console
    json_format: Whether to use JSON format for logs
    json_format: Whether to use JSON format for logs
    security_log_enabled: Whether to enable security logging
    security_log_enabled: Whether to enable security logging
    """
    """
    self.log_dir = log_dir or os.path.join(os.path.dirname(__file__), "../logs")
    self.log_dir = log_dir or os.path.join(os.path.dirname(__file__), "../logs")
    self.log_level = log_level
    self.log_level = log_level
    self.max_size = max_size
    self.max_size = max_size
    self.backup_count = backup_count
    self.backup_count = backup_count
    self.console_output = console_output
    self.console_output = console_output
    self.json_format = json_format
    self.json_format = json_format
    self.security_log_enabled = security_log_enabled
    self.security_log_enabled = security_log_enabled


    # Create log directory if it doesn't exist
    # Create log directory if it doesn't exist
    os.makedirs(self.log_dir, exist_ok=True)
    os.makedirs(self.log_dir, exist_ok=True)


    # Set up logging
    # Set up logging
    self._setup_logging()
    self._setup_logging()


    def _setup_logging(self):
    def _setup_logging(self):
    """Set up logging configuration."""
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(self.log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

    # Create formatters
    if self.json_format:
    formatter = JsonFormatter()
    else:
    formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add console handler if enabled
    if self.console_output:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler for general logs
    general_log_path = os.path.join(self.log_dir, "api.log")
    file_handler = RotatingFileHandler(
    general_log_path, maxBytes=self.max_size, backupCount=self.backup_count
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Add file handler for security logs if enabled
    if self.security_log_enabled:
    security_log_path = os.path.join(self.log_dir, "security.log")
    security_handler = RotatingFileHandler(
    security_log_path, maxBytes=self.max_size, backupCount=self.backup_count
    )
    security_handler.setFormatter(formatter)
    security_handler.addFilter(SecurityLogFilter())
    root_logger.addHandler(security_handler)

    logger.info("Logging service initialized")

    def get_logger(self, name: str) -> logging.Logger:
    """
    """
    Get a logger with the specified name.
    Get a logger with the specified name.


    Args:
    Args:
    name: Logger name
    name: Logger name


    Returns:
    Returns:
    Logger instance
    Logger instance
    """
    """
    return logging.getLogger(name)
    return logging.getLogger(name)


    def log_security_event(
    def log_security_event(
    self,
    self,
    message: str,
    message: str,
    level: str = "INFO",
    level: str = "INFO",
    security_level: str = "SECURITY",
    security_level: str = "SECURITY",
    event_type: str = None,
    event_type: str = None,
    user_id: str = None,
    user_id: str = None,
    ip_address: str = None,
    ip_address: str = None,
    resource_type: str = None,
    resource_type: str = None,
    resource_id: str = None,
    resource_id: str = None,
    action: str = None,
    action: str = None,
    status: str = None,
    status: str = None,
    details: Dict[str, Any] = None,
    details: Dict[str, Any] = None,
    ):
    ):
    """
    """
    Log a security event.
    Log a security event.


    Args:
    Args:
    message: Log message
    message: Log message
    level: Log level
    level: Log level
    security_level: Security level
    security_level: Security level
    event_type: Type of event
    event_type: Type of event
    user_id: ID of the user
    user_id: ID of the user
    ip_address: IP address
    ip_address: IP address
    resource_type: Type of resource
    resource_type: Type of resource
    resource_id: ID of the resource
    resource_id: ID of the resource
    action: Action performed
    action: Action performed
    status: Status of the event
    status: Status of the event
    details: Additional details
    details: Additional details
    """
    """
    # Get logger
    # Get logger
    security_logger = logging.getLogger("security")
    security_logger = logging.getLogger("security")


    # Determine log level
    # Determine log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    log_level = getattr(logging, level.upper(), logging.INFO)


    # Create extra fields
    # Create extra fields
    extra = {
    extra = {
    "security_level": security_level,
    "security_level": security_level,
    "event_type": event_type,
    "event_type": event_type,
    "user_id": user_id,
    "user_id": user_id,
    "ip_address": ip_address,
    "ip_address": ip_address,
    "resource_type": resource_type,
    "resource_type": resource_type,
    "resource_id": resource_id,
    "resource_id": resource_id,
    "action": action,
    "action": action,
    "status": status,
    "status": status,
    "details": details or {},
    "details": details or {},
    }
    }


    # Log the event
    # Log the event
    security_logger.log(log_level, message, extra=extra)
    security_logger.log(log_level, message, extra=extra)


    def log_api_request(
    def log_api_request(
    self,
    self,
    request_id: str,
    request_id: str,
    method: str,
    method: str,
    path: str,
    path: str,
    status_code: int,
    status_code: int,
    duration_ms: float,
    duration_ms: float,
    user_id: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_size: Optional[int] = None,
    request_size: Optional[int] = None,
    response_size: Optional[int] = None,
    response_size: Optional[int] = None,
    error: Optional[str] = None,
    error: Optional[str] = None,
    ):
    ):
    """
    """
    Log an API request.
    Log an API request.


    Args:
    Args:
    request_id: Request ID
    request_id: Request ID
    method: HTTP method
    method: HTTP method
    path: Request path
    path: Request path
    status_code: Response status code
    status_code: Response status code
    duration_ms: Request duration in milliseconds
    duration_ms: Request duration in milliseconds
    user_id: ID of the user
    user_id: ID of the user
    ip_address: IP address
    ip_address: IP address
    user_agent: User agent
    user_agent: User agent
    request_size: Size of the request in bytes
    request_size: Size of the request in bytes
    response_size: Size of the response in bytes
    response_size: Size of the response in bytes
    error: Error message if any
    error: Error message if any
    """
    """
    # Get logger
    # Get logger
    api_logger = logging.getLogger("api")
    api_logger = logging.getLogger("api")


    # Determine log level based on status code
    # Determine log level based on status code
    if status_code >= 500:
    if status_code >= 500:
    log_level = logging.ERROR
    log_level = logging.ERROR
    elif status_code >= 400:
    elif status_code >= 400:
    log_level = logging.WARNING
    log_level = logging.WARNING
    else:
    else:
    log_level = logging.INFO
    log_level = logging.INFO


    # Create message
    # Create message
    message = f"{method} {path} {status_code} {duration_ms}ms"
    message = f"{method} {path} {status_code} {duration_ms}ms"


    # Create extra fields
    # Create extra fields
    extra = {
    extra = {
    "request_id": request_id,
    "request_id": request_id,
    "method": method,
    "method": method,
    "path": path,
    "path": path,
    "status_code": status_code,
    "status_code": status_code,
    "duration_ms": duration_ms,
    "duration_ms": duration_ms,
    "user_id": user_id,
    "user_id": user_id,
    "ip_address": ip_address,
    "ip_address": ip_address,
    "user_agent": user_agent,
    "user_agent": user_agent,
    "request_size": request_size,
    "request_size": request_size,
    "response_size": response_size,
    "response_size": response_size,
    }
    }


    # Add error if any
    # Add error if any
    if error:
    if error:
    extra["error"] = error
    extra["error"] = error


    # Log the request
    # Log the request
    api_logger.log(log_level, message, extra=extra)
    api_logger.log(log_level, message, extra=extra)


    def log_webhook_delivery(
    def log_webhook_delivery(
    self,
    self,
    webhook_id: str,
    webhook_id: str,
    delivery_id: str,
    delivery_id: str,
    event_type: str,
    event_type: str,
    url: str,
    url: str,
    status_code: Optional[int],
    status_code: Optional[int],
    success: bool,
    success: bool,
    duration_ms: float,
    duration_ms: float,
    attempt: int,
    attempt: int,
    max_attempts: int,
    max_attempts: int,
    error: Optional[str] = None,
    error: Optional[str] = None,
    ):
    ):
    """
    """
    Log a webhook delivery.
    Log a webhook delivery.


    Args:
    Args:
    webhook_id: Webhook ID
    webhook_id: Webhook ID
    delivery_id: Delivery ID
    delivery_id: Delivery ID
    event_type: Event type
    event_type: Event type
    url: Webhook URL
    url: Webhook URL
    status_code: Response status code
    status_code: Response status code
    success: Whether the delivery was successful
    success: Whether the delivery was successful
    duration_ms: Delivery duration in milliseconds
    duration_ms: Delivery duration in milliseconds
    attempt: Attempt number
    attempt: Attempt number
    max_attempts: Maximum number of attempts
    max_attempts: Maximum number of attempts
    error: Error message if any
    error: Error message if any
    """
    """
    # Get logger
    # Get logger
    webhook_logger = logging.getLogger("webhook")
    webhook_logger = logging.getLogger("webhook")


    # Determine log level based on success
    # Determine log level based on success
    log_level = logging.INFO if success else logging.WARNING
    log_level = logging.INFO if success else logging.WARNING


    # Create message
    # Create message
    message = f"Webhook delivery {'succeeded' if success else 'failed'}: {delivery_id} to {url}"
    message = f"Webhook delivery {'succeeded' if success else 'failed'}: {delivery_id} to {url}"


    # Create extra fields
    # Create extra fields
    extra = {
    extra = {
    "webhook_id": webhook_id,
    "webhook_id": webhook_id,
    "delivery_id": delivery_id,
    "delivery_id": delivery_id,
    "event_type": event_type,
    "event_type": event_type,
    "url": url,
    "url": url,
    "status_code": status_code,
    "status_code": status_code,
    "success": success,
    "success": success,
    "duration_ms": duration_ms,
    "duration_ms": duration_ms,
    "attempt": attempt,
    "attempt": attempt,
    "max_attempts": max_attempts,
    "max_attempts": max_attempts,
    }
    }


    # Add error if any
    # Add error if any
    if error:
    if error:
    extra["error"] = error
    extra["error"] = error


    # Log the delivery
    # Log the delivery
    webhook_logger.log(log_level, message, extra=extra)
    webhook_logger.log(log_level, message, extra=extra)


    def log_auth_event(
    def log_auth_event(
    self,
    self,
    event_type: str,
    event_type: str,
    user_id: Optional[str],
    user_id: Optional[str],
    success: bool,
    success: bool,
    ip_address: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Dict[str, Any] = None,
    details: Dict[str, Any] = None,
    ):
    ):
    """
    """
    Log an authentication event.
    Log an authentication event.


    Args:
    Args:
    event_type: Type of event
    event_type: Type of event
    user_id: ID of the user
    user_id: ID of the user
    success: Whether the authentication was successful
    success: Whether the authentication was successful
    ip_address: IP address
    ip_address: IP address
    user_agent: User agent
    user_agent: User agent
    details: Additional details
    details: Additional details
    """
    """
    # Get logger
    # Get logger
    auth_logger = logging.getLogger("auth")
    auth_logger = logging.getLogger("auth")


    # Determine log level based on success
    # Determine log level based on success
    log_level = logging.INFO if success else logging.WARNING
    log_level = logging.INFO if success else logging.WARNING


    # Create message
    # Create message
    message = f"Auth {event_type} {'succeeded' if success else 'failed'}"
    message = f"Auth {event_type} {'succeeded' if success else 'failed'}"
    if user_id:
    if user_id:
    message += f" for user {user_id}"
    message += f" for user {user_id}"


    # Create extra fields
    # Create extra fields
    extra = {
    extra = {
    "security_level": "AUTH",
    "security_level": "AUTH",
    "event_type": event_type,
    "event_type": event_type,
    "user_id": user_id,
    "user_id": user_id,
    "success": success,
    "success": success,
    "ip_address": ip_address,
    "ip_address": ip_address,
    "user_agent": user_agent,
    "user_agent": user_agent,
    "details": details or {},
    "details": details or {},
    }
    }


    # Log the event
    # Log the event
    auth_logger.log(log_level, message, extra=extra)
    auth_logger.log(log_level, message, extra=extra)


    def get_logs(
    def get_logs(
    self,
    self,
    log_type: str = "api",
    log_type: str = "api",
    level: Optional[str] = None,
    level: Optional[str] = None,
    start_time: Optional[datetime] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    limit: int = 100,
    offset: int = 0,
    offset: int = 0,
    filters: Dict[str, Any] = None,
    filters: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get logs from the log files.
    Get logs from the log files.


    Args:
    Args:
    log_type: Type of logs to get
    log_type: Type of logs to get
    level: Filter by log level
    level: Filter by log level
    start_time: Filter by start time
    start_time: Filter by start time
    end_time: Filter by end time
    end_time: Filter by end time
    limit: Maximum number of logs to return
    limit: Maximum number of logs to return
    offset: Number of logs to skip
    offset: Number of logs to skip
    filters: Additional filters
    filters: Additional filters


    Returns:
    Returns:
    List of log entries
    List of log entries
    """
    """
    # Determine log file path
    # Determine log file path
    if log_type == "security":
    if log_type == "security":
    log_path = os.path.join(self.log_dir, "security.log")
    log_path = os.path.join(self.log_dir, "security.log")
    elif log_type == "webhook":
    elif log_type == "webhook":
    log_path = os.path.join(self.log_dir, "webhook.log")
    log_path = os.path.join(self.log_dir, "webhook.log")
    else:
    else:
    log_path = os.path.join(self.log_dir, "api.log")
    log_path = os.path.join(self.log_dir, "api.log")


    # Check if log file exists
    # Check if log file exists
    if not os.path.exists(log_path):
    if not os.path.exists(log_path):
    return []
    return []


    # Parse log file
    # Parse log file
    logs = []
    logs = []
    with open(log_path, "r") as f:
    with open(log_path, "r") as f:
    for line in f:
    for line in f:
    try:
    try:
    # Parse JSON log entry
    # Parse JSON log entry
    log_entry = json.loads(line)
    log_entry = json.loads(line)


    # Apply filters
    # Apply filters
    if level and log_entry.get("level") != level:
    if level and log_entry.get("level") != level:
    continue
    continue


    if start_time and "timestamp" in log_entry:
    if start_time and "timestamp" in log_entry:
    log_time = datetime.fromisoformat(
    log_time = datetime.fromisoformat(
    log_entry["timestamp"].replace("Z", "+00:00")
    log_entry["timestamp"].replace("Z", "+00:00")
    )
    )
    if log_time < start_time:
    if log_time < start_time:
    continue
    continue


    if end_time and "timestamp" in log_entry:
    if end_time and "timestamp" in log_entry:
    log_time = datetime.fromisoformat(
    log_time = datetime.fromisoformat(
    log_entry["timestamp"].replace("Z", "+00:00")
    log_entry["timestamp"].replace("Z", "+00:00")
    )
    )
    if log_time > end_time:
    if log_time > end_time:
    continue
    continue


    if filters:
    if filters:
    skip = False
    skip = False
    for key, value in filters.items():
    for key, value in filters.items():
    if key not in log_entry or log_entry[key] != value:
    if key not in log_entry or log_entry[key] != value:
    skip = True
    skip = True
    break
    break
    if skip:
    if skip:
    continue
    continue


    logs.append(log_entry)
    logs.append(log_entry)
except json.JSONDecodeError:
except json.JSONDecodeError:
    # Skip non-JSON lines
    # Skip non-JSON lines
    continue
    continue


    # Sort logs by timestamp (newest first)
    # Sort logs by timestamp (newest first)
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)


    # Apply limit and offset
    # Apply limit and offset
    return logs[offset : offset + limit]
    return logs[offset : offset + limit]