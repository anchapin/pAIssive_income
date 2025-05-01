"""
Logging middleware for Flask.

This module provides middleware for logging HTTP requests and responses.
"""

import logging
import time

from flask import g, request
from werkzeug.wrappers import Response

# Configure logger
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware for logging HTTP requests and responses.
    """

    def __init__(self, app):
        """
        Initialize the middleware.

        Args:
            app: Flask application
        """
        self.app = app

    def __call__(self, environ, start_response):
        """
        Process the request.

        Args:
            environ: WSGI environment
            start_response: WSGI start_response function

        Returns:
            WSGI response
        """
        # Start timer
        start_time = time.time()

        # Process the request
        response = self.app(environ, start_response)

        # Calculate request duration
        duration = time.time() - start_time

        # Log the request
        self._log_request(environ, response, duration)

        return response

    def _log_request(self, environ, response, duration):
        """
        Log the request.

        Args:
            environ: WSGI environment
            response: WSGI response
            duration: Request duration in seconds
        """
        # Extract request information
        method = environ.get("REQUEST_METHOD", "UNKNOWN")
        path = environ.get("PATH_INFO", "UNKNOWN")
        query_string = environ.get("QUERY_STRING", "")
        remote_addr = environ.get("REMOTE_ADDR", "UNKNOWN")
        user_agent = environ.get("HTTP_USER_AGENT", "UNKNOWN")

        # Extract response information
        status_code = self._get_status_code(response)

        # Build the log message
        log_data = {
            "method": method,
            "path": path,
            "query_string": query_string,
            "remote_addr": remote_addr,
            "user_agent": user_agent,
            "status_code": status_code,
            "duration": duration,
        }

        # Add user ID if available
        if hasattr(g, "user_id"):
            log_data["user_id"] = g.user_id

        # Log the request
        logger.info(
            f"HTTP {method} {path} {status_code} {duration:.3f}s", extra=log_data
        )

    def _get_status_code(self, response):
        """
        Get the status code from the response.

        Args:
            response: WSGI response

        Returns:
            HTTP status code
        """
        # If response is a list, it's a WSGI response
        if isinstance(response, list):
            return 200  # Default status code

        # If response is a Response object, get the status code
        if hasattr(response, "status_code"):
            return response.status_code

        # If response has a status attribute, parse it
        if hasattr(response, "status"):
            return int(response.status.split(" ")[0])

        # Default status code
        return 200


def init_app(app):
    """
    Initialize the logging middleware.

    Args:
        app: Flask application
    """
    app.wsgi_app = RequestLoggingMiddleware(app.wsgi_app)
