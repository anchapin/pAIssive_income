"""
Logging service for the API server.

This module provides enhanced logging capabilities with structured logs,
log rotation, and security event logging.
"""

import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Any, Dict, List, Optional, Union

# Configure default logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityLogFilter(logging.Filter):
    """Filter for security - related log events."""

    def __init__(self, security_levels: List[str] = None):
        """
        Initialize the security log filter.

        Args:
            security_levels: List of security levels to include
        """
        super().__init__()
        self.security_levels = security_levels or ["SECURITY", "AUTH", "AUDIT"]

    def filter(self, record):
        """
        Filter log records.

        Args:
            record: Log record

        Returns:
            True if the record should be logged, False otherwise
        """
        # Check if the record has a security level
        if hasattr(record, 
            "security_level") and record.security_level in self.security_levels:
            return True

        # Check if the record has security in the message
        if any(
            level.lower() in record.getMessage().lower() for level in self.security_levels):
            return True

        return False


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, include_timestamp: bool = True):
        """
        Initialize the JSON formatter.

        Args:
            include_timestamp: Whether to include a timestamp in the log
        """
        super().__init__()
        self.include_timestamp = include_timestamp

    def format(self, record):
        """
        Format a log record as JSON.

        Args:
            record: Log record

        Returns:
            JSON - formatted log message
        """
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "path": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add timestamp
        if self.include_timestamp:
            log_data["timestamp"] = datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat()

        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


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
        Initialize the logging service.

        Args:
            log_dir: Directory for log files
            log_level: Logging level
            max_size: Maximum size of log files before rotation
            backup_count: Number of backup files to keep
            console_output: Whether to output logs to console
            json_format: Whether to use JSON format for logs
            security_log_enabled: Whether to enable security logging
        """
        self.log_dir = log_dir or os.path.join(os.path.dirname(__file__), "../logs")
        self.log_level = log_level
        self.max_size = max_size
        self.backup_count = backup_count
        self.console_output = console_output
        self.json_format = json_format
        self.security_log_enabled = security_log_enabled

        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)

        # Set up logging
        self._setup_logging()

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
            formatter = logging.Formatter(" % (asctime)s - \
                %(name)s - %(levelname)s - %(message)s")

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
        Get a logger with the specified name.

        Args:
            name: Logger name

        Returns:
            Logger instance
        """
        return logging.getLogger(name)

    def log_security_event(
        self,
        message: str,
        level: str = "INFO",
        security_level: str = "SECURITY",
        event_type: str = None,
        user_id: str = None,
        ip_address: str = None,
        resource_type: str = None,
        resource_id: str = None,
        action: str = None,
        status: str = None,
        details: Dict[str, Any] = None,
    ):
        """
        Log a security event.

        Args:
            message: Log message
            level: Log level
            security_level: Security level
            event_type: Type of event
            user_id: ID of the user
            ip_address: IP address
            resource_type: Type of resource
            resource_id: ID of the resource
            action: Action performed
            status: Status of the event
            details: Additional details
        """
        # Get logger
        security_logger = logging.getLogger("security")

        # Determine log level
        log_level = getattr(logging, level.upper(), logging.INFO)

        # Create extra fields
        extra = {
            "security_level": security_level,
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "status": status,
            "details": details or {},
        }

        # Log the event
        security_logger.log(log_level, message, extra=extra)

    def log_api_request(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None,
        error: Optional[str] = None,
    ):
        """
        Log an API request.

        Args:
            request_id: Request ID
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            user_id: ID of the user
            ip_address: IP address
            user_agent: User agent
            request_size: Size of the request in bytes
            response_size: Size of the response in bytes
            error: Error message if any
        """
        # Get logger
        api_logger = logging.getLogger("api")

        # Determine log level based on status code
        if status_code >= 500:
            log_level = logging.ERROR
        elif status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

        # Create message
        message = f"{method} {path} {status_code} {duration_ms}ms"

        # Create extra fields
        extra = {
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "request_size": request_size,
            "response_size": response_size,
        }

        # Add error if any
        if error:
            extra["error"] = error

        # Log the request
        api_logger.log(log_level, message, extra=extra)

    def log_webhook_delivery(
        self,
        webhook_id: str,
        delivery_id: str,
        event_type: str,
        url: str,
        status_code: Optional[int],
        success: bool,
        duration_ms: float,
        attempt: int,
        max_attempts: int,
        error: Optional[str] = None,
    ):
        """
        Log a webhook delivery.

        Args:
            webhook_id: Webhook ID
            delivery_id: Delivery ID
            event_type: Event type
            url: Webhook URL
            status_code: Response status code
            success: Whether the delivery was successful
            duration_ms: Delivery duration in milliseconds
            attempt: Attempt number
            max_attempts: Maximum number of attempts
            error: Error message if any
        """
        # Get logger
        webhook_logger = logging.getLogger("webhook")

        # Determine log level based on success
        log_level = logging.INFO if success else logging.WARNING

        # Create message
        message = \
            f"Webhook delivery {'succeeded' if success else 'failed'}: {delivery_id} to {url}"

        # Create extra fields
        extra = {
            "webhook_id": webhook_id,
            "delivery_id": delivery_id,
            "event_type": event_type,
            "url": url,
            "status_code": status_code,
            "success": success,
            "duration_ms": duration_ms,
            "attempt": attempt,
            "max_attempts": max_attempts,
        }

        # Add error if any
        if error:
            extra["error"] = error

        # Log the delivery
        webhook_logger.log(log_level, message, extra=extra)

    def log_auth_event(
        self,
        event_type: str,
        user_id: Optional[str],
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Dict[str, Any] = None,
    ):
        """
        Log an authentication event.

        Args:
            event_type: Type of event
            user_id: ID of the user
            success: Whether the authentication was successful
            ip_address: IP address
            user_agent: User agent
            details: Additional details
        """
        # Get logger
        auth_logger = logging.getLogger("auth")

        # Determine log level based on success
        log_level = logging.INFO if success else logging.WARNING

        # Create message
        message = f"Auth {event_type} {'succeeded' if success else 'failed'}"
        if user_id:
            message += f" for user {user_id}"

        # Create extra fields
        extra = {
            "security_level": "AUTH",
            "event_type": event_type,
            "user_id": user_id,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {},
        }

        # Log the event
        auth_logger.log(log_level, message, extra=extra)

    def get_logs(
        self,
        log_type: str = "api",
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        filters: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get logs from the log files.

        Args:
            log_type: Type of logs to get
            level: Filter by log level
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            filters: Additional filters

        Returns:
            List of log entries
        """
        # Determine log file path
        if log_type == "security":
            log_path = os.path.join(self.log_dir, "security.log")
        elif log_type == "webhook":
            log_path = os.path.join(self.log_dir, "webhook.log")
        else:
            log_path = os.path.join(self.log_dir, "api.log")

        # Check if log file exists
        if not os.path.exists(log_path):
            return []

        # Parse log file
        logs = []
        with open(log_path, "r") as f:
            for line in f:
                try:
                    # Parse JSON log entry
                    log_entry = json.loads(line)

                    # Apply filters
                    if level and log_entry.get("level") != level:
                        continue

                    if start_time and "timestamp" in log_entry:
                        log_time = datetime.fromisoformat(
                            log_entry["timestamp"].replace("Z", " + 00:00")
                        )
                        if log_time < start_time:
                            continue

                    if end_time and "timestamp" in log_entry:
                        log_time = datetime.fromisoformat(
                            log_entry["timestamp"].replace("Z", " + 00:00")
                        )
                        if log_time > end_time:
                            continue

                    if filters:
                        skip = False
                        for key, value in filters.items():
                            if key not in log_entry or log_entry[key] != value:
                                skip = True
                                break
                        if skip:
                            continue

                    logs.append(log_entry)
                except json.JSONDecodeError:
                    # Skip non - JSON lines
                    continue

        # Sort logs by timestamp (newest first)
        logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # Apply limit and offset
        return logs[offset : offset + limit]
