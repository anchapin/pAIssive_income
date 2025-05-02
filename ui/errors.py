"""
Error handling for the UI module.

This module provides custom exceptions and error handling utilities
specific to the UI module.
"""

import logging
import os
import sys
from typing import Any, Dict, Optional, Union

from flask import jsonify

# Add the project root to the Python path to import the errors module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Import after path modification
from errors import APIError, UIError, ValidationError, handle_exception

# Set up logging
logger = logging.getLogger(__name__)

# Re-export the error classes for convenience
__all__ = [
    "UIError",
    "APIError",
    "ValidationError",
    "handle_exception",
    "ServiceError",
    "TemplateError",
    "RouteError",
    "ConfigurationError",
    "DataError",
    "api_error_handler",
    "error_to_json_response",
]


class ServiceError(UIError):
    """Error raised when a service operation fails."""

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the service error.

        Args:
            message: Human-readable error message
            service_name: Name of the service that raised the error
            operation: Operation that failed
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if service_name:
            details["service_name"] = service_name
        if operation:
            details["operation"] = operation

        super().__init__(message=message, code="service_error", details=details, **kwargs)


class TemplateError(UIError):
    """Error raised when there's an issue with a template."""

    def __init__(self, message: str, template_name: Optional[str] = None, **kwargs):
        """
        Initialize the template error.

        Args:
            message: Human-readable error message
            template_name: Name of the template that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if template_name:
            details["template_name"] = template_name

        super().__init__(message=message, code="template_error", details=details, **kwargs)


class RouteError(UIError):
    """Error raised when there's an issue with a route."""

    def __init__(
        self, message: str, route: Optional[str] = None, method: Optional[str] = None, **kwargs
    ):
        """
        Initialize the route error.

        Args:
            message: Human-readable error message
            route: Route that caused the error
            method: HTTP method used
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if route:
            details["route"] = route
        if method:
            details["method"] = method

        super().__init__(message=message, code="route_error", details=details, **kwargs)


class ConfigurationError(UIError):
    """Error raised when there's an issue with configuration."""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        """
        Initialize the configuration error.

        Args:
            message: Human-readable error message
            config_key: Configuration key that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if config_key:
            details["config_key"] = config_key

        super().__init__(message=message, code="configuration_error", details=details, **kwargs)


class DataError(UIError):
    """Error raised when there's an issue with data handling."""

    def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the data error.

        Args:
            message: Human-readable error message
            data_type: Type of data that caused the error
            operation: Operation that failed
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if data_type:
            details["data_type"] = data_type
        if operation:
            details["operation"] = operation

        super().__init__(message=message, code="data_error", details=details, **kwargs)


def api_error_handler(error: Exception) -> tuple:
    """
    Handle API errors and return appropriate JSON responses.

    Args:
        error: The error to handle

    Returns:
        Tuple of (JSON response, HTTP status code)
    """
    if isinstance(error, UIError):
        response = error.to_dict()
        status_code = error.http_status
    else:
        # Convert standard exception to UIError
        ui_error = UIError(
            message=str(error), code=error.__class__.__name__, original_exception=error
        )
        response = ui_error.to_dict()
        status_code = ui_error.http_status

    return jsonify(response), status_code


def error_to_json_response(error: Union[UIError, Exception]) -> Dict[str, Any]:
    """
    Convert an error to a JSON response.

    Args:
        error: The error to convert

    Returns:
        JSON response dictionary
    """
    if isinstance(error, UIError):
        return error.to_dict()

    # Convert standard exception to UIError
    ui_error = UIError(message=str(error), code=error.__class__.__name__, original_exception=error)

    return ui_error.to_dict()
