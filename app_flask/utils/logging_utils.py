"""Utilities for enhanced application logging."""

import functools
import logging
import re
import time
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from flask import current_app, g

# Type variables for generic function decorators
F = TypeVar("F", bound=Callable[..., Any])

# Patterns for sensitive data
SENSITIVE_PATTERNS = [
    (r'password[\'"]\s*:\s*[\'"][^\'"]+[\'"]', "***"),
    (r'token[\'"]\s*:\s*[\'"][^\'"]+[\'"]', "***"),
    (r'secret[\'"]\s*:\s*[\'"][^\'"]+[\'"]', "***"),
    (r'key[\'"]\s*:\s*[\'"][^\'"]+[\'"]', "***"),
    (r'auth[\'"]\s*:\s*[\'"][^\'"]+[\'"]', "***"),
    # Add patterns for email, phone, etc. if needed
]


def sanitize_log_data(data: Any) -> Any:
    """Remove sensitive information from log data.

    Args:
        data: Data to sanitize

    Returns:
        Sanitized data
    """
    if isinstance(data, str):
        # Apply all patterns
        result = data
        for pattern, replacement in SENSITIVE_PATTERNS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result
    elif isinstance(data, dict):
        # Recursively sanitize dictionary values
        return {k: sanitize_log_data(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        # Recursively sanitize sequence items
        return type(data)(sanitize_log_data(x) for x in data)
    return data


def log_execution_time(logger: Optional[logging.Logger] = None) -> Callable[[F], F]:
    """Decorator to log function execution time.

    Args:
        logger: Logger to use, defaults to app logger

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            duration = (time.perf_counter() - start_time) * 1000  # ms

            log = logger or current_app.logger
            log.info(
                f"{func.__name__} executed",
                extra={
                    "duration_ms": duration,
                    "function": func.__name__,
                    "module": func.__module__,
                    "correlation_id": getattr(g, "correlation_id", None),
                },
            )
            return result

        return cast(F, wrapper)

    return decorator


def structured_log(
    event: str,
    message: str,
    level: Any = logging.INFO,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Log a structured log message with sanitized inputs.

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
        log_data.update(sanitize_log_data(extra))

    # Set log level with explicit typing
    numeric_level: int = logging.INFO
    if isinstance(level, str):
        numeric_level = getattr(logging, level.upper(), logging.INFO)
    elif isinstance(level, int):
        numeric_level = level

    log.log(numeric_level, safe_message, extra=log_data)


def audit_log(
    action: str,
    status: str,
    user_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Log an audit event.

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

    current_app.logger.info(f"Audit: {action}", extra=log_data)
