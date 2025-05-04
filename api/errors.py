"""
"""
Error handling utilities for the API server.
Error handling utilities for the API server.


This module provides standardized error handling for the API server,
This module provides standardized error handling for the API server,
including HTTP status codes, error response formatting, and exception mapping.
including HTTP status codes, error response formatting, and exception mapping.
"""
"""




import logging
import logging
import traceback
import traceback
from datetime import datetime
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type
from typing import Any, Callable, Dict, List, Optional, Type


from fastapi import FastAPI, Request, Response, status
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.responses import JSONResponse
from pydantic import ConfigDict
from pydantic import ConfigDict
from pydantic import ValidationError as PydanticValidationError
from pydantic import ValidationError as PydanticValidationError


FASTAPI_AVAILABLE
FASTAPI_AVAILABLE
from errors import BaseError, ValidationError
from errors import BaseError, ValidationError


# Try to import FastAPI
# Try to import FastAPI
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False


    # Create dummy classes for type hints
    # Create dummy classes for type hints
    class RequestValidationError(Exception):
    class RequestValidationError(Exception):
    pass
    pass


    class PydanticValidationError(Exception):
    class PydanticValidationError(Exception):
    pass
    pass




    # Import base error classes
    # Import base error classes
    # Set up logging
    # Set up logging
    logger = logging.getLogger(__name__)
    logger = logging.getLogger(__name__)




    # HTTP Status Codes
    # HTTP Status Codes
    class HTTPStatus:
    class HTTPStatus:
    """HTTP status code constants."""

    # 2xx Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # 3xx Redirection
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    TEMPORARY_REDIRECT = 307
    PERMANENT_REDIRECT = 308

    # 4xx Client Errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    CONFLICT = 409
    GONE = 410
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # 5xx Server Errors
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


    # Error response format
    class ErrorDetail:

    def __init__(
    self,
    message: str,
    code: Optional[str] = None,
    field: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    ):
    """
    """
    Initialize error detail.
    Initialize error detail.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    code: Error code for programmatic handling
    code: Error code for programmatic handling
    field: Field that caused the error (for validation errors)
    field: Field that caused the error (for validation errors)
    params: Additional parameters for the error
    params: Additional parameters for the error
    """
    """
    self.message = message
    self.message = message
    self.code = code
    self.code = code
    self.field = field
    self.field = field
    self.params = params or {}
    self.params = params or {}


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert to dictionary.
    Convert to dictionary.


    Returns:
    Returns:
    Dictionary representation
    Dictionary representation
    """
    """
    result = {"message": self.message}
    result = {"message": self.message}


    if self.code:
    if self.code:
    result["code"] = self.code
    result["code"] = self.code


    if self.field:
    if self.field:
    result["field"] = self.field
    result["field"] = self.field


    if self.params:
    if self.params:
    result["params"] = self.params
    result["params"] = self.params


    return result
    return result




    class ErrorResponse:
    class ErrorResponse:
    """Standard error response format."""

    def __init__(
    self,
    message: str,
    code: Optional[str] = None,
    details: Optional[List[ErrorDetail]] = None,
    path: Optional[str] = None,
    timestamp: Optional[str] = None,
    trace_id: Optional[str] = None,
    ):
    """
    """
    Initialize error response.
    Initialize error response.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    code: Error code for programmatic handling
    code: Error code for programmatic handling
    details: List of error details
    details: List of error details
    path: Path where the error occurred
    path: Path where the error occurred
    timestamp: Timestamp of the error
    timestamp: Timestamp of the error
    trace_id: Trace ID for debugging
    trace_id: Trace ID for debugging
    """
    """
    self.message = message
    self.message = message
    self.code = code
    self.code = code
    self.details = details or []
    self.details = details or []
    self.path = path
    self.path = path
    self.timestamp = timestamp or datetime.now().isoformat()
    self.timestamp = timestamp or datetime.now().isoformat()
    self.trace_id = trace_id
    self.trace_id = trace_id


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert to dictionary.
    Convert to dictionary.


    Returns:
    Returns:
    Dictionary representation
    Dictionary representation
    """
    """
    result = {"error": {"message": self.message, "timestamp": self.timestamp}}
    result = {"error": {"message": self.message, "timestamp": self.timestamp}}


    if self.code:
    if self.code:
    result["error"]["code"] = self.code
    result["error"]["code"] = self.code


    if self.details:
    if self.details:
    result["error"]["details"] = [detail.to_dict() for detail in self.details]
    result["error"]["details"] = [detail.to_dict() for detail in self.details]


    if self.path:
    if self.path:
    result["error"]["path"] = self.path
    result["error"]["path"] = self.path


    if self.trace_id:
    if self.trace_id:
    result["error"]["trace_id"] = self.trace_id
    result["error"]["trace_id"] = self.trace_id


    return result
    return result




    # Exception to HTTP status code mapping
    # Exception to HTTP status code mapping
    EXCEPTION_STATUS_CODE_MAP = {
    EXCEPTION_STATUS_CODE_MAP = {
    # Standard exceptions
    # Standard exceptions
    ValueError: HTTPStatus.BAD_REQUEST,
    ValueError: HTTPStatus.BAD_REQUEST,
    TypeError: HTTPStatus.BAD_REQUEST,
    TypeError: HTTPStatus.BAD_REQUEST,
    KeyError: HTTPStatus.BAD_REQUEST,
    KeyError: HTTPStatus.BAD_REQUEST,
    IndexError: HTTPStatus.BAD_REQUEST,
    IndexError: HTTPStatus.BAD_REQUEST,
    AttributeError: HTTPStatus.BAD_REQUEST,
    AttributeError: HTTPStatus.BAD_REQUEST,
    FileNotFoundError: HTTPStatus.NOT_FOUND,
    FileNotFoundError: HTTPStatus.NOT_FOUND,
    PermissionError: HTTPStatus.FORBIDDEN,
    PermissionError: HTTPStatus.FORBIDDEN,
    NotImplementedError: HTTPStatus.NOT_IMPLEMENTED,
    NotImplementedError: HTTPStatus.NOT_IMPLEMENTED,
    TimeoutError: HTTPStatus.GATEWAY_TIMEOUT,
    TimeoutError: HTTPStatus.GATEWAY_TIMEOUT,
    ConnectionError: HTTPStatus.SERVICE_UNAVAILABLE,
    ConnectionError: HTTPStatus.SERVICE_UNAVAILABLE,
    # Validation errors
    # Validation errors
    ValidationError: HTTPStatus.BAD_REQUEST,
    ValidationError: HTTPStatus.BAD_REQUEST,
    RequestValidationError: HTTPStatus.BAD_REQUEST,
    RequestValidationError: HTTPStatus.BAD_REQUEST,
    PydanticValidationError: HTTPStatus.BAD_REQUEST,
    PydanticValidationError: HTTPStatus.BAD_REQUEST,
    }
    }




    def get_status_code_for_exception(exception: Exception) -> int:
    def get_status_code_for_exception(exception: Exception) -> int:
    """
    """
    Get the appropriate HTTP status code for an exception.
    Get the appropriate HTTP status code for an exception.


    Args:
    Args:
    exception: The exception
    exception: The exception


    Returns:
    Returns:
    HTTP status code
    HTTP status code
    """
    """
    # If it's a BaseError with a defined http_status, use that
    # If it's a BaseError with a defined http_status, use that
    if isinstance(exception, BaseError) and hasattr(exception, "http_status"):
    if isinstance(exception, BaseError) and hasattr(exception, "http_status"):
    return exception.http_status
    return exception.http_status


    # Check the exception type in the mapping
    # Check the exception type in the mapping
    for exc_type, status_code in EXCEPTION_STATUS_CODE_MAP.items():
    for exc_type, status_code in EXCEPTION_STATUS_CODE_MAP.items():
    if isinstance(exception, exc_type):
    if isinstance(exception, exc_type):
    return status_code
    return status_code


    # Default to internal server error
    # Default to internal server error
    return HTTPStatus.INTERNAL_SERVER_ERROR
    return HTTPStatus.INTERNAL_SERVER_ERROR




    def create_error_response(
    def create_error_response(
    exception: Exception, request: Optional[Any] = None, include_traceback: bool = False
    exception: Exception, request: Optional[Any] = None, include_traceback: bool = False
    ) -> ErrorResponse:
    ) -> ErrorResponse:
    """
    """
    Create a standardized error response from an exception.
    Create a standardized error response from an exception.


    Args:
    Args:
    exception: The exception
    exception: The exception
    request: The request that caused the exception
    request: The request that caused the exception
    include_traceback: Whether to include traceback in the response
    include_traceback: Whether to include traceback in the response


    Returns:
    Returns:
    Standardized error response
    Standardized error response
    """
    """
    # Get message and code
    # Get message and code
    if isinstance(exception, BaseError):
    if isinstance(exception, BaseError):
    message = exception.message
    message = exception.message
    code = exception.code
    code = exception.code
    details = []
    details = []


    # Add details from the exception
    # Add details from the exception
    if hasattr(exception, "details") and exception.details:
    if hasattr(exception, "details") and exception.details:
    for key, value in exception.details.items():
    for key, value in exception.details.items():
    details.append(
    details.append(
    ErrorDetail(message=str(value), code=key, params={key: value})
    ErrorDetail(message=str(value), code=key, params={key: value})
    )
    )
    else:
    else:
    message = str(exception)
    message = str(exception)
    code = exception.__class__.__name__
    code = exception.__class__.__name__
    details = []
    details = []


    # Get path from request
    # Get path from request
    path = None
    path = None
    if request and hasattr(request, "url"):
    if request and hasattr(request, "url"):
    path = str(request.url)
    path = str(request.url)


    # Create error response
    # Create error response
    response = ErrorResponse(message=message, code=code, details=details, path=path)
    response = ErrorResponse(message=message, code=code, details=details, path=path)


    # Add traceback if requested
    # Add traceback if requested
    if include_traceback:
    if include_traceback:
    tb = traceback.format_exception(
    tb = traceback.format_exception(
    type(exception), exception, exception.__traceback__
    type(exception), exception, exception.__traceback__
    )
    )
    response.details.append(
    response.details.append(
    ErrorDetail(
    ErrorDetail(
    message="Traceback", code="traceback", params={"traceback": "".join(tb)}
    message="Traceback", code="traceback", params={"traceback": "".join(tb)}
    )
    )
    )
    )


    return response
    return response




    # FastAPI exception handlers
    # FastAPI exception handlers
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:


    def create_exception_handlers() -> Dict[Type[Exception], Callable]:
    def create_exception_handlers() -> Dict[Type[Exception], Callable]:
    """
    """
    Create exception handlers for FastAPI.
    Create exception handlers for FastAPI.


    Returns:
    Returns:
    Dictionary of exception handlers
    Dictionary of exception handlers
    """
    """


    def handle_validation_error(
    def handle_validation_error(
    request: Request, exc: RequestValidationError
    request: Request, exc: RequestValidationError
    ) -> JSONResponse:
    ) -> JSONResponse:
    """
    """
    Handle validation errors.
    Handle validation errors.


    Args:
    Args:
    request: FastAPI request
    request: FastAPI request
    exc: Validation exception
    exc: Validation exception


    Returns:
    Returns:
    JSON response
    JSON response
    """
    """
    # Log the error
    # Log the error
    logger.warning(f"Validation error: {exc}")
    logger.warning(f"Validation error: {exc}")


    # Create error details
    # Create error details
    details = []
    details = []
    for error in exc.errors():
    for error in exc.errors():
    field = ".".join(str(loc) for loc in error.get("loc", []))
    field = ".".join(str(loc) for loc in error.get("loc", []))
    details.append(
    details.append(
    ErrorDetail(
    ErrorDetail(
    message=error.get("msg", "Validation error"),
    message=error.get("msg", "Validation error"),
    code=error.get("type", "validation_error"),
    code=error.get("type", "validation_error"),
    field=field,
    field=field,
    params=error,
    params=error,
    )
    )
    )
    )


    # Create error response
    # Create error response
    response = ErrorResponse(
    response = ErrorResponse(
    message="Validation error",
    message="Validation error",
    code="validation_error",
    code="validation_error",
    details=details,
    details=details,
    path=str(request.url),
    path=str(request.url),
    )
    )


    # Return JSON response
    # Return JSON response
    return JSONResponse(
    return JSONResponse(
    status_code=HTTPStatus.BAD_REQUEST, content=response.to_dict()
    status_code=HTTPStatus.BAD_REQUEST, content=response.to_dict()
    )
    )


    def handle_base_error(request: Request, exc: BaseError) -> JSONResponse:
    def handle_base_error(request: Request, exc: BaseError) -> JSONResponse:
    """
    """
    Handle base errors.
    Handle base errors.


    Args:
    Args:
    request: FastAPI request
    request: FastAPI request
    exc: Base error
    exc: Base error


    Returns:
    Returns:
    JSON response
    JSON response
    """
    """
    # Log the error
    # Log the error
    exc.log()
    exc.log()


    # Create error response
    # Create error response
    response = create_error_response(exc, request)
    response = create_error_response(exc, request)


    # Get status code
    # Get status code
    status_code = get_status_code_for_exception(exc)
    status_code = get_status_code_for_exception(exc)


    # Return JSON response
    # Return JSON response
    return JSONResponse(status_code=status_code, content=response.to_dict())
    return JSONResponse(status_code=status_code, content=response.to_dict())


    def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
    def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
    """
    """
    Handle generic exceptions.
    Handle generic exceptions.


    Args:
    Args:
    request: FastAPI request
    request: FastAPI request
    exc: Exception
    exc: Exception


    Returns:
    Returns:
    JSON response
    JSON response
    """
    """
    # Log the error
    # Log the error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)


    # Create error response
    # Create error response
    response = create_error_response(exc, request)
    response = create_error_response(exc, request)


    # Get status code
    # Get status code
    status_code = get_status_code_for_exception(exc)
    status_code = get_status_code_for_exception(exc)


    # Return JSON response
    # Return JSON response
    return JSONResponse(status_code=status_code, content=response.to_dict())
    return JSONResponse(status_code=status_code, content=response.to_dict())


    # Return exception handlers
    # Return exception handlers
    return {
    return {
    RequestValidationError: handle_validation_error,
    RequestValidationError: handle_validation_error,
    PydanticValidationError: handle_validation_error,
    PydanticValidationError: handle_validation_error,
    BaseError: handle_base_error,
    BaseError: handle_base_error,
    Exception: handle_generic_exception,
    Exception: handle_generic_exception,
    }
    }




    def setup_error_handlers(app: Any) -> None:
    def setup_error_handlers(app: Any) -> None:
    """
    """
    Set up error handlers for the API server.
    Set up error handlers for the API server.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    """
    """
    if not FASTAPI_AVAILABLE:
    if not FASTAPI_AVAILABLE:
    logger.warning("FastAPI is required for error handlers")
    logger.warning("FastAPI is required for error handlers")
    return # Add exception handlers
    return # Add exception handlers
    exception_handlers = create_exception_handlers()
    exception_handlers = create_exception_handlers()
    for exc_type, handler in exception_handlers.items():
    for exc_type, handler in exception_handlers.items():
    app.add_exception_handler(exc_type, handler)
    app.add_exception_handler(exc_type, handler)


    logger.info("Error handlers set up")
    logger.info("Error handlers set up")