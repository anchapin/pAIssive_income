"""Utilities for enhanced application logging."""

from __future__ import annotations

import functools
import logging
import re
import sys  # Added sys import
import time
from collections.abc import Callable
from typing import Any, TypeVar, cast

logger = logging.getLogger(__name__)  # Initialize logger

try:
    from flask.globals import current_app, g
    from werkzeug.local import LocalProxy

# Configure logging


# Configure logging


# Configure logging


# Configure logging



# Configure logging
except ImportError:

    logger.exception(
        "Error: Flask or Werkzeug module not found. Please install them (e.g., pip install Flask Werkzeug)."
    )
    sys.exit(1)


# Type variables for generic function decorators
F = TypeVar("F", bound=Callable[..., Any])

# Type hint for Flask app logger
app_logger = LocalProxy(lambda: current_app.logger)

# Type hint for Flask app logger
FlaskLogger = logging.Logger

# Constants
FIRST_PRINTABLE_ASCII = 32  # ASCII value for space character (first printable)

# Patterns for sensitive data
SENSITIVE_PATTERNS = [
    (r'password[\'"]\s*:\s*[\'"][^\'"]+[\'"]', "***"),
    (r'token[\'"]\s*:\s*[\'"][^\'"]+[\'"]', "***"),
    (r'secret[\'"]\s*:\s*[\'"][^\'"]+[\'"]', "***"),
    (r'key[\'"]\s*:\s*[\'"][^\'"]+[\'"]', "***"),
    (r'auth[\'"]\s*:\s*[\'"][^\'"]+[\'"]', "***"),
    # Add patterns for email, phone, etc. if needed
]


def sanitize_log_data(data: object) -> object:
    """
    Remove sensitive information and prevent log injection from log data.

    Args:
        data: Data to sanitize

    Returns:
        Sanitized data

    """
    if isinstance(data, str):
        # First remove any potential log injection characters
        result = data.replace("\n", " ").replace("\r", " ").replace("\t", " ")

        # Remove any ANSI escape sequences
        result = re.sub(r"\x1b\[[0-9;]*[mGKH]", "", result)

        # Remove any control characters
        result = "".join(
            char
            for char in result
            if ord(char) >= FIRST_PRINTABLE_ASCII or char in " \t"
        )

        # Apply sensitive data patterns
        for pattern, replacement in SENSITIVE_PATTERNS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result
    if isinstance(data, dict):
        # Recursively sanitize dictionary values
        return {k: sanitize_log_data(v) for k, v in data.items()}
    if isinstance(data, list | tuple):
        # Recursively sanitize sequence items
        return type(data)(sanitize_log_data(x) for x in data)
    return data


def log_execution_time(logger: logging.Logger | None = None) -> Callable[[F], F]:
    """
    Log function execution time.

    Args:
        logger: Logger to use, defaults to app logger

    Returns:
        Decorated function

    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            duration = (time.perf_counter() - start_time) * 1000  # ms

            log = logger or current_app.logger
            log.info(
                "%s executed",
                func.__name__,
                extra={
                    "duration_ms": duration,
                    "function": func.__name__,
                    "func_module": func.__module__,  # Renamed to avoid clash with LogRecord field
                    "correlation_id": getattr(g, "correlation_id", None),
                },
            )
            return result

        return cast("F", wrapper)

    return decorator


def structured_log(
    event: str,
    message: str,
    level: int | str = logging.INFO,
    extra: dict[str, object] | None = None,
) -> None:
    """
    Log a structured log message with sanitized inputs.

    Args:
        event: The event type/name (will be sanitized)
        message: The log message (will be sanitized)
        level: The log level (can be string name or int constant)
        extra: Additional fields to include in the log (will be sanitized)

    Note:
        The level parameter can be either a string (e.g. 'INFO') or an int constant from the logging module.
        If a string is provided, it will be converted to the corresponding logging level constant.
        All user-provided inputs are sanitized to prevent log injection attacks.

    """
    log = current_app.logger

    # Sanitize all inputs including event name and message
    safe_event = sanitize_log_data(event)
    safe_message = sanitize_log_data(message)
    log_data = {"event": safe_event}

    # Add sanitized extra fields
    if extra:
        # Cast to dict to satisfy mypy
        sanitized_extra = sanitize_log_data(extra)
        if isinstance(sanitized_extra, dict):
            log_data.update(sanitized_extra)

    # Set log level with explicit typing
    numeric_level: int
    if isinstance(level, str):
        _level_name_upper = level.upper()
        if _level_name_upper in logging._nameToLevel:
            numeric_level = logging._nameToLevel[_level_name_upper]
        else:
            # If the string level name is not recognized, default to INFO
            # and log a warning about the unrecognized level.
            logger.warning(
                f"Unrecognized log level string: '{level}'. Defaulting to INFO."
            )
            numeric_level = logging.INFO
    elif isinstance(level, int):
        numeric_level = level
    else:
        # This case should ideally not be reached due to type hints,
        # but as a fallback, default to INFO and log a warning.
        logger.warning(
            f"Invalid type for log level: {type(level)}. Defaulting to INFO."
        )
        numeric_level = logging.INFO

    log.log(numeric_level, safe_message, extra=log_data)


def audit_log(
    action: str,
    status: str,
    user_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """
    Log an audit event.

    Args:
        action: The action being audited
        status: Status of the action (success/failure)
        user_id: ID of user performing action
        details: Additional audit details

    """
    log_data = {
        "event_type": "audit",
        "action": action,
        "status": status,
        "user_id": user_id,
        "correlation_id": getattr(g, "correlation_id", None),
    }

    if details:
        log_data["details"] = sanitize_log_data(details)

    current_app.logger.info("Audit: %s", action, extra=log_data)
