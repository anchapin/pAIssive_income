"""
"""
Logging middleware for the API server.
Logging middleware for the API server.


This module provides middleware for request logging and performance monitoring.
This module provides middleware for request logging and performance monitoring.
"""
"""




import logging
import logging
import time
import time
import uuid
import uuid
from typing import Callable, Optional
from typing import Callable, Optional


from fastapi import Request, Response
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


from ..services.logging_service import LoggingService
from ..services.logging_service import LoggingService


# Configure logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class RequestLoggingMiddleware(BaseHTTPMiddleware):
    class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging."""

    def __init__(
    self,
    app,
    logging_service: Optional[LoggingService] = None,
    exclude_paths: list = None,
    ):
    """
    """
    Initialize the middleware.
    Initialize the middleware.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    logging_service: Logging service
    logging_service: Logging service
    exclude_paths: Paths to exclude from logging
    exclude_paths: Paths to exclude from logging
    """
    """
    super().__init__(app)
    super().__init__(app)
    self.logging_service = logging_service or LoggingService()
    self.logging_service = logging_service or LoggingService()
    self.exclude_paths = exclude_paths or ["/health", "/metrics"]
    self.exclude_paths = exclude_paths or ["/health", "/metrics"]


    async def dispatch(self, request: Request, call_next: Callable) -> Response:
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
    """
    """
    Process the request.
    Process the request.


    Args:
    Args:
    request: FastAPI request
    request: FastAPI request
    call_next: Next middleware or route handler
    call_next: Next middleware or route handler


    Returns:
    Returns:
    Response
    Response
    """
    """
    # Skip excluded paths
    # Skip excluded paths
    if any(request.url.path.startswith(path) for path in self.exclude_paths):
    if any(request.url.path.startswith(path) for path in self.exclude_paths):
    return await call_next(request)
    return await call_next(request)


    # Generate request ID if not present
    # Generate request ID if not present
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())


    # Add request ID to request state
    # Add request ID to request state
    request.state.request_id = request_id
    request.state.request_id = request_id


    # Get start time
    # Get start time
    start_time = time.time()
    start_time = time.time()


    # Get client info
    # Get client info
    client_host = request.client.host if request.client else None
    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    user_agent = request.headers.get("user-agent")


    # Get user ID if available
    # Get user ID if available
    user_id = None
    user_id = None
    if hasattr(request.state, "user") and request.state.user:
    if hasattr(request.state, "user") and request.state.user:
    user_id = request.state.user.id
    user_id = request.state.user.id
    elif hasattr(request.state, "api_key") and request.state.api_key:
    elif hasattr(request.state, "api_key") and request.state.api_key:
    user_id = request.state.api_key.user_id
    user_id = request.state.api_key.user_id


    # Process request
    # Process request
    try:
    try:
    # Add request ID header to response
    # Add request ID header to response
    response = await call_next(request)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Request-ID"] = request_id


    # Calculate duration
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    duration_ms = (time.time() - start_time) * 1000


    # Log request
    # Log request
    self.logging_service.log_api_request(
    self.logging_service.log_api_request(
    request_id=request_id,
    request_id=request_id,
    method=request.method,
    method=request.method,
    path=request.url.path,
    path=request.url.path,
    status_code=response.status_code,
    status_code=response.status_code,
    duration_ms=duration_ms,
    duration_ms=duration_ms,
    user_id=user_id,
    user_id=user_id,
    ip_address=client_host,
    ip_address=client_host,
    user_agent=user_agent,
    user_agent=user_agent,
    request_size=int(request.headers.get("content-length", 0)),
    request_size=int(request.headers.get("content-length", 0)),
    response_size=int(response.headers.get("content-length", 0)),
    response_size=int(response.headers.get("content-length", 0)),
    )
    )


    return response
    return response


except Exception as e:
except Exception as e:
    # Calculate duration
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    duration_ms = (time.time() - start_time) * 1000


    # Log error
    # Log error
    self.logging_service.log_api_request(
    self.logging_service.log_api_request(
    request_id=request_id,
    request_id=request_id,
    method=request.method,
    method=request.method,
    path=request.url.path,
    path=request.url.path,
    status_code=500,
    status_code=500,
    duration_ms=duration_ms,
    duration_ms=duration_ms,
    user_id=user_id,
    user_id=user_id,
    ip_address=client_host,
    ip_address=client_host,
    user_agent=user_agent,
    user_agent=user_agent,
    request_size=int(request.headers.get("content-length", 0)),
    request_size=int(request.headers.get("content-length", 0)),
    error=str(e),
    error=str(e),
    )
    )


    # Re-raise exception
    # Re-raise exception
    raise
    raise




    class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for security event logging."""

    def __init__(self, app, logging_service: Optional[LoggingService] = None):
    """
    """
    Initialize the middleware.
    Initialize the middleware.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    logging_service: Logging service
    logging_service: Logging service
    """
    """
    super().__init__(app)
    super().__init__(app)
    self.logging_service = logging_service or LoggingService()
    self.logging_service = logging_service or LoggingService()


    async def dispatch(self, request: Request, call_next: Callable) -> Response:
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
    """
    """
    Process the request.
    Process the request.


    Args:
    Args:
    request: FastAPI request
    request: FastAPI request
    call_next: Next middleware or route handler
    call_next: Next middleware or route handler


    Returns:
    Returns:
    Response
    Response
    """
    """
    # Process request
    # Process request
    response = await call_next(request)
    response = await call_next(request)


    # Check for security-related responses
    # Check for security-related responses
    if response.status_code == 401:
    if response.status_code == 401:
    # Log authentication failure
    # Log authentication failure
    self.logging_service.log_security_event(
    self.logging_service.log_security_event(
    message="Authentication failed",
    message="Authentication failed",
    level="WARNING",
    level="WARNING",
    security_level="AUTH",
    security_level="AUTH",
    event_type="auth.failed",
    event_type="auth.failed",
    ip_address=request.client.host if request.client else None,
    ip_address=request.client.host if request.client else None,
    resource_type="api",
    resource_type="api",
    action="access",
    action="access",
    status="failure",
    status="failure",
    details={
    details={
    "path": request.url.path,
    "path": request.url.path,
    "method": request.method,
    "method": request.method,
    "user_agent": request.headers.get("user-agent"),
    "user_agent": request.headers.get("user-agent"),
    },
    },
    )
    )


    elif response.status_code == 403:
    elif response.status_code == 403:
    # Log authorization failure
    # Log authorization failure
    self.logging_service.log_security_event(
    self.logging_service.log_security_event(
    message="Authorization failed",
    message="Authorization failed",
    level="WARNING",
    level="WARNING",
    security_level="AUTH",
    security_level="AUTH",
    event_type="permission.denied",
    event_type="permission.denied",
    user_id=(
    user_id=(
    request.state.user.id
    request.state.user.id
    if hasattr(request.state, "user") and request.state.user
    if hasattr(request.state, "user") and request.state.user
    else None
    else None
    ),
    ),
    ip_address=request.client.host if request.client else None,
    ip_address=request.client.host if request.client else None,
    resource_type="api",
    resource_type="api",
    action="access",
    action="access",
    status="failure",
    status="failure",
    details={
    details={
    "path": request.url.path,
    "path": request.url.path,
    "method": request.method,
    "method": request.method,
    "user_agent": request.headers.get("user-agent"),
    "user_agent": request.headers.get("user-agent"),
    },
    },
    )
    )


    elif response.status_code == 429:
    elif response.status_code == 429:
    # Log rate limit exceeded
    # Log rate limit exceeded
    self.logging_service.log_security_event(
    self.logging_service.log_security_event(
    message="Rate limit exceeded",
    message="Rate limit exceeded",
    level="WARNING",
    level="WARNING",
    security_level="SECURITY",
    security_level="SECURITY",
    event_type="rate_limit.exceeded",
    event_type="rate_limit.exceeded",
    user_id=(
    user_id=(
    request.state.user.id
    request.state.user.id
    if hasattr(request.state, "user") and request.state.user
    if hasattr(request.state, "user") and request.state.user
    else None
    else None
    ),
    ),
    ip_address=request.client.host if request.client else None,
    ip_address=request.client.host if request.client else None,
    resource_type="api",
    resource_type="api",
    action="limit",
    action="limit",
    status="warning",
    status="warning",
    details={
    details={
    "path": request.url.path,
    "path": request.url.path,
    "method": request.method,
    "method": request.method,
    "user_agent": request.headers.get("user-agent"),
    "user_agent": request.headers.get("user-agent"),
    },
    },
    )
    )


    return response
    return response