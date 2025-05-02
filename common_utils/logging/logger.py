"""
Structured logger implementation for the pAIssive_income application.

This module provides a structured logging system that:
1. Formats logs as JSON for easy parsing by log aggregation tools
2. Adds contextual information to all logs (user ID, request ID, etc.)
3. Supports different log levels and environments
4. Provides a consistent interface across the application
"""

import json
import logging
import os
import sys
import traceback
from enum import Enum
from logging.handlers import RotatingFileHandler
from typing import Optional, Union

import contextvars

# Context variables for storing request-specific information
request_id_var = contextvars.ContextVar("request_id", default=None)
user_id_var = contextvars.ContextVar("user_id", default=None)
session_id_var = contextvars.ContextVar("session_id", default=None)
component_var = contextvars.ContextVar("component", default=None)
additional_context_var = contextvars.ContextVar("additional_context", default={})


class LogLevel(str, Enum):
    """Log levels supported by the application logger."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def add_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    component: Optional[str] = None,
    **kwargs
) -> None:
    """
    Add contextual information to be included in all subsequent log entries.

    Args:
        request_id: A unique identifier for the current request
        user_id: The ID of the user making the request
        session_id: The current session identifier
        component: The component or module generating the log
        **kwargs: Additional key-value pairs to include in the context
    """
    if request_id:
        request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if session_id:
        session_id_var.set(session_id)
    if component:
        component_var.set(component)

    # Add any additional context
    if kwargs:
        current = additional_context_var.get()
        current.update(kwargs)
        additional_context_var.set(current)


def clear_context() -> None:
    """Clear all contextual information."""
    request_id_var.set(None)
    user_id_var.set(None)
    session_id_var.set(None)
    component_var.set(None)
    additional_context_var.set({})


class StructuredJsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after formatting the log record.
    """

    def __init__(self, *args, **kwargs):
        self.fmt_keys = {
            "timestamp": "timestamp",
            "level": "levelname",
            "message": "message",
            "module": "module",
            "function": "funcName",
            "line": "lineno",
            "logger": "name",
        }
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a JSON string.

        Args:
            record: The log record to format

        Returns:
            str: The formatted log record as a JSON string
        """
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "process_id": record.process,
            "thread_id": record.thread,
        }

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add contextual information
        request_id = request_id_var.get()
        if request_id:
            log_record["request_id"] = request_id

        user_id = user_id_var.get()
        if user_id:
            log_record["user_id"] = user_id

        session_id = session_id_var.get()
        if session_id:
            log_record["session_id"] = session_id

        component = component_var.get()
        if component:
            log_record["component"] = component

        # Add any additional context
        additional_context = additional_context_var.get()
        if additional_context:
            log_record.update(additional_context)

        # Add any extra attributes from the record
        if hasattr(record, "extra"):
            log_record.update(record.extra)

        return json.dumps(log_record)


def setup_logging(
    level: Union[str, LogLevel] = LogLevel.INFO,
    log_file: Optional[str] = None,
    max_file_size_mb: int = 10,
    backup_count: int = 5,
    log_to_console: bool = True,
    log_to_file: bool = False,
) -> None:
    """
    Configure the logging system for the application.

    Args:
        level: The minimum log level to capture
        log_file: Path to the log file, if file logging is enabled
        max_file_size_mb: Maximum size of each log file in MB
        backup_count: Number of backup log files to keep
        log_to_console: Whether to output logs to the console
        log_to_file: Whether to output logs to a file
    """
    root_logger = logging.getLogger()
    # Remove all existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set the log level
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    else:
        level = getattr(logging, level.value)

    root_logger.setLevel(level)
    formatter = StructuredJsonFormatter()

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_to_file and log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_file_size_mb * 1024 * 1024, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for the specified name.

    Args:
        name: The name of the logger, typically __name__

    Returns:
        logging.Logger: A configured logger
    """
    return logging.getLogger(name)
