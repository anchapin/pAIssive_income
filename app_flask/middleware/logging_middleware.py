"""Logging middleware for Flask application."""

import logging
import time
import traceback
import uuid
from typing import Any, Dict, Tuple, Union, cast

from flask.app import Flask
from flask.globals import current_app, g, request
from flask.wrappers import Response
from werkzeug.wrappers import Response as WerkzeugResponse

from ..utils.logging_utils import sanitize_log_data, structured_log

# Type hint for Flask app logger
FlaskLogger = logging.Logger


def logging_getattr(module: Any, name: str, default: Any = None) -> Any:
    """Safe getattr for logging module."""
    return getattr(module, name, default)


class FlaskConfig(Dict[str, Any]):
    """Type definition for Flask config used in logging middleware."""

    LOG_REQUEST_ID_HEADER: str
    LOG_CORRELATION_ID_HEADER: str


def get_config() -> Dict[str, Any]:
    """Get typed config from current app."""
    return cast(Dict[str, Any], current_app.config)


def get_request_context() -> Dict[str, Any]:
    """Get common request context for logging.

    Returns:
        Dict with common request context fields
    """
    context: Dict[str, Any] = {}
    try:
        context.update({
            "request_id": getattr(g, "request_id", "unknown"),
            "correlation_id": getattr(g, "correlation_id", None),
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
        })
        if request.user_agent:
            context["user_agent"] = request.user_agent.string
    except Exception:
        # Handle case where request context is not available
        pass
    return context


def setup_request_logging(app: Flask) -> None:
    """Set up request logging middleware.

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

    @app.after_request
    def after_request(response: Response) -> Response:
        """Log request details after each request.

        Args:
            response: Flask response object

        Returns:
            Flask response object
        """  # Skip detailed logging for health check endpoints
        if request.path == "/health":
            return response

        duration_ms = int((time.perf_counter() - g.start_time) * 1000)

        # Determine if request was slow
        config = get_config()
        slow_threshold = config["LOG_SLOW_REQUEST_THRESHOLD"]
        very_slow_threshold = config["LOG_VERY_SLOW_REQUEST_THRESHOLD"]

        log_data = {
            **get_request_context(),
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "response_size": len(response.get_data()),
            "response_headers": sanitize_log_data(dict(response.headers)),
        }

        # Add performance warning for slow requests
        if duration_ms > very_slow_threshold:
            log_level = "warning"
            log_data["performance_warning"] = "very_slow_request"
        elif duration_ms > slow_threshold:
            log_level = "info"
            log_data["performance_warning"] = "slow_request"
        else:
            log_level = "info"

        structured_log(
            "request.completed",
            f"Completed {request.method} {request.path} in {duration_ms}ms",
            level=logging_getattr(logging, log_level.upper(), logging.INFO),
            extra=log_data,
        )

        # Add tracking headers to response
        config = get_config()
        response.headers[config["LOG_REQUEST_ID_HEADER"]] = g.request_id
        if getattr(g, "correlation_id", None):
            response.headers[config["LOG_CORRELATION_ID_HEADER"]] = g.correlation_id

        return response

    @app.errorhandler(Exception)
    def log_exception(
        error: Exception,
    ) -> Union[Tuple[Response, int], Tuple[WerkzeugResponse, int]]:
        """Log unhandled exceptions.

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
            error_data = sanitize_log_data(error_data)

        structured_log(
            "request.error",
            f"Unhandled exception in {request.method} {request.path}",
            level=logging.ERROR,
            extra=error_data,
        )

        return {"error": "Internal server error", "request_id": g.request_id}, 500
