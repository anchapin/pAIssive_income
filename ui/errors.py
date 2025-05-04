"""
"""
Error handling for the UI module.
Error handling for the UI module.


This module provides custom exceptions and error handling utilities
This module provides custom exceptions and error handling utilities
specific to the UI module.
specific to the UI module.
"""
"""




import logging
import logging
import os
import os
import sys
import sys
from typing import Any, Dict, Optional, Union
from typing import Any, Dict, Optional, Union


from errors import APIError, UIError, ValidationError, handle_exception
from errors import APIError, UIError, ValidationError, handle_exception
from flask import jsonify
from flask import jsonify


# Add the project root to the Python path to import the errors module
# Add the project root to the Python path to import the errors module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Re-export the error classes for convenience
# Re-export the error classes for convenience
__all__ = [
__all__ = [
"UIError",
"UIError",
"APIError",
"APIError",
"ValidationError",
"ValidationError",
"handle_exception",
"handle_exception",
"ServiceError",
"ServiceError",
"TemplateError",
"TemplateError",
"RouteError",
"RouteError",
"ConfigurationError",
"ConfigurationError",
"DataError",
"DataError",
"api_error_handler",
"api_error_handler",
"error_to_json_response",
"error_to_json_response",
]
]




class ServiceError(UIError):
    class ServiceError(UIError):
    """Error raised when a service operation fails."""

    def __init__(
    self,
    message: str,
    service_name: Optional[str] = None,
    operation: Optional[str] = None,
    **kwargs
    ):
    """
    """
    Initialize the service error.
    Initialize the service error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    service_name: Name of the service that raised the error
    service_name: Name of the service that raised the error
    operation: Operation that failed
    operation: Operation that failed
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if service_name:
    if service_name:
    details["service_name"] = service_name
    details["service_name"] = service_name
    if operation:
    if operation:
    details["operation"] = operation
    details["operation"] = operation


    super().__init__(
    super().__init__(
    message=message, code="service_error", details=details, **kwargs
    message=message, code="service_error", details=details, **kwargs
    )
    )




    class TemplateError(UIError):
    class TemplateError(UIError):
    """Error raised when there's an issue with a template."""

    def __init__(self, message: str, template_name: Optional[str] = None, **kwargs):
    """
    """
    Initialize the template error.
    Initialize the template error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    template_name: Name of the template that caused the error
    template_name: Name of the template that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if template_name:
    if template_name:
    details["template_name"] = template_name
    details["template_name"] = template_name


    super().__init__(
    super().__init__(
    message=message, code="template_error", details=details, **kwargs
    message=message, code="template_error", details=details, **kwargs
    )
    )




    class RouteError(UIError):
    class RouteError(UIError):
    """Error raised when there's an issue with a route."""

    def __init__(
    self,
    message: str,
    route: Optional[str] = None,
    method: Optional[str] = None,
    **kwargs
    ):
    """
    """
    Initialize the route error.
    Initialize the route error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    route: Route that caused the error
    route: Route that caused the error
    method: HTTP method used
    method: HTTP method used
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if route:
    if route:
    details["route"] = route
    details["route"] = route
    if method:
    if method:
    details["method"] = method
    details["method"] = method


    super().__init__(message=message, code="route_error", details=details, **kwargs)
    super().__init__(message=message, code="route_error", details=details, **kwargs)




    class ConfigurationError(UIError):
    class ConfigurationError(UIError):
    """Error raised when there's an issue with configuration."""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
    """
    """
    Initialize the configuration error.
    Initialize the configuration error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    config_key: Configuration key that caused the error
    config_key: Configuration key that caused the error
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if config_key:
    if config_key:
    details["config_key"] = config_key
    details["config_key"] = config_key


    super().__init__(
    super().__init__(
    message=message, code="configuration_error", details=details, **kwargs
    message=message, code="configuration_error", details=details, **kwargs
    )
    )




    class DataError(UIError):
    class DataError(UIError):
    """Error raised when there's an issue with data handling."""

    def __init__(
    self,
    message: str,
    data_type: Optional[str] = None,
    operation: Optional[str] = None,
    **kwargs
    ):
    """
    """
    Initialize the data error.
    Initialize the data error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    data_type: Type of data that caused the error
    data_type: Type of data that caused the error
    operation: Operation that failed
    operation: Operation that failed
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if data_type:
    if data_type:
    details["data_type"] = data_type
    details["data_type"] = data_type
    if operation:
    if operation:
    details["operation"] = operation
    details["operation"] = operation


    super().__init__(message=message, code="data_error", details=details, **kwargs)
    super().__init__(message=message, code="data_error", details=details, **kwargs)




    def api_error_handler(error: Exception) -> tuple:
    def api_error_handler(error: Exception) -> tuple:
    """
    """
    Handle API errors and return appropriate JSON responses.
    Handle API errors and return appropriate JSON responses.


    Args:
    Args:
    error: The error to handle
    error: The error to handle


    Returns:
    Returns:
    Tuple of (JSON response, HTTP status code)
    Tuple of (JSON response, HTTP status code)
    """
    """
    if isinstance(error, UIError):
    if isinstance(error, UIError):
    response = error.to_dict()
    response = error.to_dict()
    status_code = error.http_status
    status_code = error.http_status
    else:
    else:
    # Convert standard exception to UIError
    # Convert standard exception to UIError
    ui_error = UIError(
    ui_error = UIError(
    message=str(error), code=error.__class__.__name__, original_exception=error
    message=str(error), code=error.__class__.__name__, original_exception=error
    )
    )
    response = ui_error.to_dict()
    response = ui_error.to_dict()
    status_code = ui_error.http_status
    status_code = ui_error.http_status


    return jsonify(response), status_code
    return jsonify(response), status_code




    def error_to_json_response(error: Union[UIError, Exception]) -> Dict[str, Any]:
    def error_to_json_response(error: Union[UIError, Exception]) -> Dict[str, Any]:
    """
    """
    Convert an error to a JSON response.
    Convert an error to a JSON response.


    Args:
    Args:
    error: The error to convert
    error: The error to convert


    Returns:
    Returns:
    JSON response dictionary
    JSON response dictionary
    """
    """
    if isinstance(error, UIError):
    if isinstance(error, UIError):
    return error.to_dict()
    return error.to_dict()


    # Convert standard exception to UIError
    # Convert standard exception to UIError
    ui_error = UIError(
    ui_error = UIError(
    message=str(error), code=error.__class__.__name__, original_exception=error
    message=str(error), code=error.__class__.__name__, original_exception=error
    )
    )


    return ui_error.to_dict()
    return ui_error.to_dict()