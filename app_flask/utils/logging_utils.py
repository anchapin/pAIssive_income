"""Utilities for enhanced application logging."""

import functools
import logging
from logging import getLogger
import re
import time
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from flask import current_app, g, request

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
    event_type: str,
    message: str,
    level: int = logging.INFO,
    extra: Optional[Dict[str, Any]] = None,
    logger: Optional[logging.Logger] = None,
) -> None:
    """Log a structured event with consistent formatting.

    Args:
        event_type: Type of event being logged
        message: Log message
        level: Log level (default: INFO)
        extra: Additional fields to log
        logger: Logger to use (default: app logger)
    """
    # Get or create logger
    log = logger or getLogger("app")

    # Build structured log data
    log_data = {
        "event_type": event_type,
        "message": message,
        "correlation_id": getattr(g, "correlation_id", None),
        "request_id": getattr(g, "request_id", None),
    }

    # Add request context if available
    try:
        if request:
            log_data.update({
                "path": request.path,
                "method": request.method,
                "remote_addr": request.remote_addr,
            })
    except RuntimeError:
        # Not in request context
        pass

    # Add extra fields
    if extra:
        log_data.update(sanitize_log_data(extra))

    # Set log level
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    log.log(level, message, extra=log_data)


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
