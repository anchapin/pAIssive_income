"""
"""
Middleware for the API Gateway service.
Middleware for the API Gateway service.


This module provides middleware for the API Gateway service,
This module provides middleware for the API Gateway service,
including authentication, rate limiting, and other cross-cutting concerns.
including authentication, rate limiting, and other cross-cutting concerns.
"""
"""




import logging
import logging
import time
import time
from typing import Callable, Dict, List, Optional
from typing import Callable, Dict, List, Optional


from fastapi import Request, Response, status
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


from services.shared.auth import ServiceTokenError, validate_service_token
from services.shared.auth import ServiceTokenError, validate_service_token


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class ServiceAuthMiddleware(BaseHTTPMiddleware):
    class ServiceAuthMiddleware(BaseHTTPMiddleware):
    """
    """
    Middleware for service-to-service authentication.
    Middleware for service-to-service authentication.


    This middleware validates JWT tokens for service-to-service communication.
    This middleware validates JWT tokens for service-to-service communication.
    """
    """


    def __init__(
    def __init__(
    self, app, exclude_paths: Optional[List[str]] = None, require_auth: bool = True
    self, app, exclude_paths: Optional[List[str]] = None, require_auth: bool = True
    ):
    ):
    """
    """
    Initialize the service authentication middleware.
    Initialize the service authentication middleware.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    exclude_paths: List of paths to exclude from authentication
    exclude_paths: List of paths to exclude from authentication
    require_auth: Whether to require authentication for all requests
    require_auth: Whether to require authentication for all requests
    """
    """
    super().__init__(app)
    super().__init__(app)
    self.exclude_paths = exclude_paths or []
    self.exclude_paths = exclude_paths or []
    self.require_auth = require_auth
    self.require_auth = require_auth


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
    # Skip authentication for excluded paths
    # Skip authentication for excluded paths
    path = request.url.path
    path = request.url.path
    if any(path.startswith(excluded) for excluded in self.exclude_paths):
    if any(path.startswith(excluded) for excluded in self.exclude_paths):
    return await call_next(request)
    return await call_next(request)


    # Get service token from header
    # Get service token from header
    service_token = request.headers.get("X-Service-Token")
    service_token = request.headers.get("X-Service-Token")


    # If token is not provided
    # If token is not provided
    if not service_token:
    if not service_token:
    if self.require_auth:
    if self.require_auth:
    return JSONResponse(
    return JSONResponse(
    content={"detail": "Service token is required"},
    content={"detail": "Service token is required"},
    status_code=status.HTTP_401_UNAUTHORIZED,
    status_code=status.HTTP_401_UNAUTHORIZED,
    )
    )
    else:
    else:
    # If authentication is not required, continue
    # If authentication is not required, continue
    return await call_next(request)
    return await call_next(request)


    try:
    try:
    # Validate the service token
    # Validate the service token
    # The audience is "api-gateway" since we're validating tokens sent to the API Gateway
    # The audience is "api-gateway" since we're validating tokens sent to the API Gateway
    token_payload = validate_service_token(
    token_payload = validate_service_token(
    token=service_token, audience="api-gateway"
    token=service_token, audience="api-gateway"
    )
    )


    # Add the token payload to the request state
    # Add the token payload to the request state
    request.state.service_token = token_payload
    request.state.service_token = token_payload


    # Log the authenticated service
    # Log the authenticated service
    logger.info(f"Authenticated service: {token_payload.iss}")
    logger.info(f"Authenticated service: {token_payload.iss}")


    # Continue processing the request
    # Continue processing the request
    return await call_next(request)
    return await call_next(request)


except ServiceTokenError as e:
except ServiceTokenError as e:
    # Return authentication error
    # Return authentication error
    return JSONResponse(
    return JSONResponse(
    content={"detail": str(e)}, status_code=status.HTTP_401_UNAUTHORIZED
    content={"detail": str(e)}, status_code=status.HTTP_401_UNAUTHORIZED
    )
    )
except Exception as e:
except Exception as e:
    # Log and return server error
    # Log and return server error
    logger.error(f"Error in service authentication: {str(e)}")
    logger.error(f"Error in service authentication: {str(e)}")
    return JSONResponse(
    return JSONResponse(
    content={"detail": "Internal server error during authentication"},
    content={"detail": "Internal server error during authentication"},
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    )




    class RateLimitMiddleware(BaseHTTPMiddleware):
    class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    """
    Middleware for rate limiting.
    Middleware for rate limiting.


    This middleware limits the number of requests a client can make in a given time window.
    This middleware limits the number of requests a client can make in a given time window.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    app,
    app,
    rate_limit: int = 100,
    rate_limit: int = 100,
    window_size: int = 60,
    window_size: int = 60,
    exclude_paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    ):
    ):
    """
    """
    Initialize the rate limiting middleware.
    Initialize the rate limiting middleware.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    rate_limit: Maximum number of requests per window
    rate_limit: Maximum number of requests per window
    window_size: Time window in seconds
    window_size: Time window in seconds
    exclude_paths: List of paths to exclude from rate limiting
    exclude_paths: List of paths to exclude from rate limiting
    """
    """
    super().__init__(app)
    super().__init__(app)
    self.rate_limit = rate_limit
    self.rate_limit = rate_limit
    self.window_size = window_size
    self.window_size = window_size
    self.exclude_paths = exclude_paths or []
    self.exclude_paths = exclude_paths or []
    self.requests: Dict[str, List[float]] = {}
    self.requests: Dict[str, List[float]] = {}


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
    # Skip rate limiting for excluded paths
    # Skip rate limiting for excluded paths
    path = request.url.path
    path = request.url.path
    if any(path.startswith(excluded) for excluded in self.exclude_paths):
    if any(path.startswith(excluded) for excluded in self.exclude_paths):
    return await call_next(request)
    return await call_next(request)


    # Get client ID (IP address or API key or service name)
    # Get client ID (IP address or API key or service name)
    client_id = None
    client_id = None


    # If the request has a service token, use the service name as the client ID
    # If the request has a service token, use the service name as the client ID
    if hasattr(request.state, "service_token"):
    if hasattr(request.state, "service_token"):
    client_id = request.state.service_token.iss
    client_id = request.state.service_token.iss
    else:
    else:
    # Otherwise, use the API key or IP address
    # Otherwise, use the API key or IP address
    client_id = request.headers.get("X-API-Key", request.client.host)
    client_id = request.headers.get("X-API-Key", request.client.host)


    # Get current time
    # Get current time
    current_time = time.time()
    current_time = time.time()


    # Initialize client's request history if not exists
    # Initialize client's request history if not exists
    if client_id not in self.requests:
    if client_id not in self.requests:
    self.requests[client_id] = []
    self.requests[client_id] = []


    # Remove requests older than the window size
    # Remove requests older than the window size
    self.requests[client_id] = [
    self.requests[client_id] = [
    timestamp
    timestamp
    for timestamp in self.requests[client_id]
    for timestamp in self.requests[client_id]
    if current_time - timestamp < self.window_size
    if current_time - timestamp < self.window_size
    ]
    ]


    # Check if rate limit is exceeded
    # Check if rate limit is exceeded
    if len(self.requests[client_id]) >= self.rate_limit:
    if len(self.requests[client_id]) >= self.rate_limit:
    return JSONResponse(
    return JSONResponse(
    content={"detail": "Rate limit exceeded"},
    content={"detail": "Rate limit exceeded"},
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )
    )


    # Add current request to history
    # Add current request to history
    self.requests[client_id].append(current_time)
    self.requests[client_id].append(current_time)


    # Continue processing the request
    # Continue processing the request
    return await call_next(request)
    return await call_next(request)