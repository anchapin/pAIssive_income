"""Logging middleware for Flask application."""

from __future__ import annotations

import time
import traceback
import uuid
from logging import ERROR, INFO, Logger, getLogger
from typing import TYPE_CHECKING, Any, Union, cast

if TYPE_CHECKING:
    from werkzeug.wrappers import Response as WerkzeugResponse

    from flask.app import Flask
    from flask.wrappers import Response

from app_flask.utils.logging_utils import sanitize_log_data, structured_log
from flask.globals import current_app, g, request

# Type hint for Flask app logger
FlaskLogger = Logger


def logging_getattr(module: object, name: str, default: object = None) -> object:
    """Safe getattr for logging module."""
    return getattr(module, name, default)


class FlaskConfig(dict[str, Any]):
    """Type definition for Flask config used in logging middleware."""

    LOG_REQUEST_ID_HEADER: str
    LOG_CORRELATION_ID_HEADER: str


def get_config() -> dict[str, Any]:
    """Get typed config from current app."""
    return cast("dict[str, Any]", current_app.config)


def get_request_context() -> dict[str, Any]:
    """
    Get common request context for logging.

    Returns:
        Dict with common request context fields

    """
    context: dict[str, Any] = {}
    try:
        context.update(
            {
                "request_id": getattr(g, "request_id", "unknown"),
                "correlation_id": getattr(g, "correlation_id", None),
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
            }
        )
        if request.user_agent:
            context["user_agent"] = request.user_agent.string
    except (AttributeError, RuntimeError):
        # Handle case where request context is not available
        logger = getLogger(__name__)
        logger.debug("Failed to get request context", exc_info=True)
    return context


def _setup_before_request(app: Flask) -> None:
    """
    Set up before request handler.

    Args:
        app: Flask application instance

    """

    @app.before_request
    def before_request() -> None:
        """Set up logging context before each request."""
        # Generate or get request and correlation IDs
        config = get_config()
        request_id_header = config["LOG_REQUEST_ID_HEADER"]
        correlation_id_header = config["LOG_CORRELATION_ID_HEADER"]

        g.request_id = str(request.headers.get(request_id_header) or uuid.uuid4())
        g.correlation_id = str(
            request.headers.get(correlation_id_header) or g.request_id
        )
        g.start_time = time.perf_counter()

        # Log request start
        structured_log(
            "request.started",
            f"Started {request.method} {request.path}",
            extra={
                **get_request_context(),
                "query_params": sanitize_log_data(dict(request.args)),
                "headers": sanitize_log_data(dict(request.headers)),
            },
        )


def _get_log_level_for_duration(duration_ms: int, config: dict) -> tuple[str, dict]:
    """
    Determine log level based on request duration.

    Args:
        duration_ms: Request duration in milliseconds
        config: Application configuration

    Returns:
        Tuple of (log_level, additional_log_data)

    """
    slow_threshold = config["LOG_SLOW_REQUEST_THRESHOLD"]
    very_slow_threshold = config["LOG_VERY_SLOW_REQUEST_THRESHOLD"]

    additional_data = {}

    if duration_ms > very_slow_threshold:
        log_level = "warning"
        additional_data["performance_warning"] = "very_slow_request"
    elif duration_ms > slow_threshold:
        log_level = "info"
        additional_data["performance_warning"] = "slow_request"
    else:
        log_level = "info"

    return log_level, additional_data


def _setup_after_request(app: Flask) -> None:
    """
    Set up after request handler.

    Args:
        app: Flask application instance

    """

    @app.after_request
    def after_request(response: Response) -> Response:
        """
        Log request details after each request.

        Args:
            response: Flask response object

        Returns:
            Flask response object

        """
        # Skip detailed logging for health check endpoints
        if request.path == "/health":
            return response

        duration_ms = int((time.perf_counter() - g.start_time) * 1000)
        config = get_config()

        # Get log level and additional data based on duration
        log_level, performance_data = _get_log_level_for_duration(duration_ms, config)

        log_data = {
            **get_request_context(),
            **performance_data,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "response_size": len(response.get_data()),
            "response_headers": sanitize_log_data(dict(response.headers)),
        }

        # Get log level value from log level name
        log_level_value = cast(
            "int",
            getattr(getLogger(), log_level.upper(), INFO),
        )
        structured_log(
            "request.completed",
            f"Completed {request.method} {request.path} in {duration_ms}ms",
            level=log_level_value,
            extra=log_data,
        )

        # Add tracking headers to response
        response.headers[config["LOG_REQUEST_ID_HEADER"]] = g.request_id
        if getattr(g, "correlation_id", None):
            response.headers[config["LOG_CORRELATION_ID_HEADER"]] = g.correlation_id

        return response


def _setup_error_handler(app: Flask) -> None:
    """
    Set up exception handler.

    Args:
        app: Flask application instance

    """

    @app.errorhandler(Exception)
    def log_exception(
        error: Exception,
    ) -> Union[tuple[Response, int], tuple[WerkzeugResponse, int]]:
        """
        Log unhandled exceptions.

        Args:
            error: The unhandled exception

        Returns:
            Tuple of (response, status_code)

        """
        error_data = {
            **get_request_context(),
            "error_type": error.__class__.__name__,
            "error_message": str(error),
        }

        config = get_config()
        if config["LOG_INCLUDE_TRACE"]:
            tb_limit = config["LOG_MAX_TRACEBACK_DEPTH"]
            error_data["traceback"] = traceback.format_tb(
                error.__traceback__, limit=tb_limit
            )

        if config["LOG_SANITIZE_ERRORS"]:
            sanitized_data = sanitize_log_data(error_data)
            if isinstance(sanitized_data, dict):
                error_data = sanitized_data

        structured_log(
            "request.error",
            f"Unhandled exception in {request.method} {request.path}",
            level=ERROR,
            extra=error_data,
        )

        return {"error": "Internal server error", "request_id": g.request_id}, 500


def setup_request_logging(app: Flask) -> None:
    """
    Set up request logging middleware.

    Args:
        app: Flask application instance

    """
    _setup_before_request(app)
    _setup_after_request(app)
    _setup_error_handler(app)
