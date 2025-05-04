
import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from api.analytics import analytics_service

FASTAPI_AVAILABLE
from api.analytics import analytics_service


class AnalyticsMiddleware

"""
"""
Analytics middleware for the API server.
Analytics middleware for the API server.


This middleware collects analytics data for API requests.
This middleware collects analytics data for API requests.
"""
"""




# Set up logging
# Set up logging
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Try to import FastAPI
# Try to import FastAPI
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning("FastAPI is required for analytics middleware")
    logger.warning("FastAPI is required for analytics middleware")
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False


    # Import analytics service
    # Import analytics service
    :
    :
    """
    """
    Middleware for collecting API analytics.
    Middleware for collecting API analytics.
    """
    """


    def __init__(self, app):
    def __init__(self, app):
    """
    """
    Initialize the analytics middleware.
    Initialize the analytics middleware.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    """
    """
    if not FASTAPI_AVAILABLE:
    if not FASTAPI_AVAILABLE:
    raise ImportError("FastAPI is required for analytics middleware")
    raise ImportError("FastAPI is required for analytics middleware")


    self.app = app
    self.app = app


    # Register middleware
    # Register middleware
    @app.middleware("http")
    @app.middleware("http")
    async def analytics_middleware(
    async def analytics_middleware(
    request: Request, call_next: Callable
    request: Request, call_next: Callable
    ) -> Response:
    ) -> Response:
    return await self.dispatch(request, call_next)
    return await self.dispatch(request, call_next)


    async def dispatch(self, request: Request, call_next: Callable) -> Response:
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
    """
    """
    Process the request and collect analytics data.
    Process the request and collect analytics data.


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
    # Skip analytics for docs and OpenAPI
    # Skip analytics for docs and OpenAPI
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
    return await call_next(request)
    return await call_next(request)


    # Record start time
    # Record start time
    start_time = time.time()
    start_time = time.time()


    # Get request information
    # Get request information
    method = request.method
    method = request.method
    path = request.url.path
    path = request.url.path


    # Extract API version from path
    # Extract API version from path
    version = None
    version = None
    if "/api/" in path:
    if "/api/" in path:
    parts = path.split("/")
    parts = path.split("/")
    for i, part in enumerate(parts):
    for i, part in enumerate(parts):
    if part == "api" and i + 1 < len(parts):
    if part == "api" and i + 1 < len(parts):
    version = parts[i + 1]
    version = parts[i + 1]
    break
    break


    # Get client information
    # Get client information
    client_ip = request.client.host if request.client else None
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    user_agent = request.headers.get("User-Agent")


    # Get authentication information
    # Get authentication information
    user_id = None
    user_id = None
    api_key_id = None
    api_key_id = None


    # Try to get user ID from request state
    # Try to get user ID from request state
    if hasattr(request, "state") and hasattr(request.state, "user"):
    if hasattr(request, "state") and hasattr(request.state, "user"):
    user = request.state.user
    user = request.state.user
    if hasattr(user, "id"):
    if hasattr(user, "id"):
    user_id = str(user.id)
    user_id = str(user.id)


    # Try to get API key ID from header
    # Try to get API key ID from header
    api_key = request.headers.get("X-API-Key")
    api_key = request.headers.get("X-API-Key")
    if api_key:
    if api_key:
    # Use the API key as the ID for now
    # Use the API key as the ID for now
    # In a real implementation, you would look up the API key ID
    # In a real implementation, you would look up the API key ID
    api_key_id = api_key
    api_key_id = api_key


    # Get query parameters
    # Get query parameters
    query_params = {}
    query_params = {}
    for key, value in request.query_params.items():
    for key, value in request.query_params.items():
    query_params[key] = value
    query_params[key] = value


    # Process the request
    # Process the request
    response = None
    response = None
    error_type = None
    error_type = None
    error_message = None
    error_message = None


    try:
    try:
    # Call the next middleware or route handler
    # Call the next middleware or route handler
    response = await call_next(request)
    response = await call_next(request)


    # Get response information
    # Get response information
    status_code = response.status_code
    status_code = response.status_code


    # Check if response is an error
    # Check if response is an error
    if status_code >= 400:
    if status_code >= 400:
    error_type = f"HTTP{status_code}"
    error_type = f"HTTP{status_code}"
    error_message = "HTTP error"
    error_message = "HTTP error"


except Exception as e:
except Exception as e:
    # Handle exceptions
    # Handle exceptions
    error_type = type(e).__name__
    error_type = type(e).__name__
    error_message = str(e)
    error_message = str(e)


    # Re-raise the exception
    # Re-raise the exception
    raise
    raise


finally:
finally:
    # Calculate response time
    # Calculate response time
    response_time = time.time() - start_time
    response_time = time.time() - start_time


    # Get response size (if available)
    # Get response size (if available)
    response_size = None
    response_size = None
    if response and hasattr(response, "headers"):
    if response and hasattr(response, "headers"):
    content_length = response.headers.get("Content-Length")
    content_length = response.headers.get("Content-Length")
    if content_length and content_length.isdigit():
    if content_length and content_length.isdigit():
    response_size = int(content_length)
    response_size = int(content_length)


    # Get request size (if available)
    # Get request size (if available)
    request_size = None
    request_size = None
    content_length = request.headers.get("Content-Length")
    content_length = request.headers.get("Content-Length")
    if content_length and content_length.isdigit():
    if content_length and content_length.isdigit():
    request_size = int(content_length)
    request_size = int(content_length)


    # Determine endpoint
    # Determine endpoint
    endpoint = path
    endpoint = path


    # Try to get a more descriptive endpoint name from the route
    # Try to get a more descriptive endpoint name from the route
    if hasattr(request, "scope") and "route" in request.scope:
    if hasattr(request, "scope") and "route" in request.scope:
    route = request.scope["route"]
    route = request.scope["route"]
    if hasattr(route, "path"):
    if hasattr(route, "path"):
    endpoint = route.path
    endpoint = route.path


    # Track the request
    # Track the request
    try:
    try:
    analytics_service.track_request(
    analytics_service.track_request(
    method=method,
    method=method,
    path=path,
    path=path,
    endpoint=endpoint,
    endpoint=endpoint,
    version=version,
    version=version,
    status_code=response.status_code if response else None,
    status_code=response.status_code if response else None,
    response_time=response_time,
    response_time=response_time,
    user_id=user_id,
    user_id=user_id,
    api_key_id=api_key_id,
    api_key_id=api_key_id,
    client_ip=client_ip,
    client_ip=client_ip,
    user_agent=user_agent,
    user_agent=user_agent,
    request_size=request_size,
    request_size=request_size,
    response_size=response_size,
    response_size=response_size,
    query_params=query_params,
    query_params=query_params,
    error_type=error_type,
    error_type=error_type,
    error_message=error_message,
    error_message=error_message,
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error tracking request: {e}")
    logger.error(f"Error tracking request: {e}")


    return response
    return response