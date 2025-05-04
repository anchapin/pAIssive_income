"""
"""
Rate limiting middleware for the API server.
Rate limiting middleware for the API server.


This module provides rate limiting middleware for the API server.
This module provides rate limiting middleware for the API server.
"""
"""




import logging
import logging
from typing import Any, Callable, Dict, Optional, Tuple
from typing import Any, Callable, Dict, Optional, Tuple


from fastapi import FastAPI, Request, Response
from fastapi import FastAPI, Request, Response


from ..config import APIConfig, RateLimitScope
from ..config import APIConfig, RateLimitScope
from ..rate_limit import RateLimitManager
from ..rate_limit import RateLimitManager


FASTAPI_AVAILABLE
FASTAPI_AVAILABLE


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


# Try to import FastAPI
# Try to import FastAPI
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning("FastAPI is required for rate limiting middleware")
    logger.warning("FastAPI is required for rate limiting middleware")
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False




    class RateLimitMiddleware:
    class RateLimitMiddleware:
    """
    """
    Rate limiting middleware for the API server.
    Rate limiting middleware for the API server.
    """
    """


    def __init__(self, config: APIConfig):
    def __init__(self, config: APIConfig):
    """
    """
    Initialize the rate limiting middleware.
    Initialize the rate limiting middleware.


    Args:
    Args:
    config: API configuration
    config: API configuration
    """
    """
    self.config = config
    self.config = config


    # Create rate limit manager
    # Create rate limit manager
    storage_type = (
    storage_type = (
    "redis" if hasattr(config, "redis_url") and config.redis_url else "memory"
    "redis" if hasattr(config, "redis_url") and config.redis_url else "memory"
    )
    )
    storage_kwargs = {}
    storage_kwargs = {}
    if storage_type == "redis":
    if storage_type == "redis":
    storage_kwargs["redis_url"] = config.redis_url
    storage_kwargs["redis_url"] = config.redis_url


    self.rate_limit_manager = RateLimitManager(
    self.rate_limit_manager = RateLimitManager(
    config, storage_type, **storage_kwargs
    config, storage_type, **storage_kwargs
    )
    )


    def check_rate_limit(
    def check_rate_limit(
    self,
    self,
    client_id: str,
    client_id: str,
    endpoint: Optional[str] = None,
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    api_key: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
    ) -> Tuple[bool, Dict[str, Any]]:
    """
    """
    Check if a request should be rate limited.
    Check if a request should be rate limited.


    Args:
    Args:
    client_id: Client identifier (e.g., IP address)
    client_id: Client identifier (e.g., IP address)
    endpoint: Optional endpoint path
    endpoint: Optional endpoint path
    api_key: Optional API key
    api_key: Optional API key


    Returns:
    Returns:
    Tuple of (allowed, limit_info)
    Tuple of (allowed, limit_info)
    - allowed: True if the request is allowed, False if it should be rate limited
    - allowed: True if the request is allowed, False if it should be rate limited
    - limit_info: Dictionary with rate limit information
    - limit_info: Dictionary with rate limit information
    """
    """
    return self.rate_limit_manager.check_rate_limit(client_id, endpoint, api_key)
    return self.rate_limit_manager.check_rate_limit(client_id, endpoint, api_key)


    def get_rate_limit_headers(self, limit_info: Dict[str, Any]) -> Dict[str, str]:
    def get_rate_limit_headers(self, limit_info: Dict[str, Any]) -> Dict[str, str]:
    """
    """
    Get rate limit headers for a response.
    Get rate limit headers for a response.


    Args:
    Args:
    limit_info: Rate limit information
    limit_info: Rate limit information


    Returns:
    Returns:
    Dictionary of rate limit headers
    Dictionary of rate limit headers
    """
    """
    return self.rate_limit_manager.get_rate_limit_headers(limit_info)
    return self.rate_limit_manager.get_rate_limit_headers(limit_info)




    def setup_rate_limit_middleware(app: Any, config: APIConfig) -> None:
    def setup_rate_limit_middleware(app: Any, config: APIConfig) -> None:
    """
    """
    Set up rate limiting middleware for the API server.
    Set up rate limiting middleware for the API server.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    config: API configuration
    config: API configuration
    """
    """
    if not FASTAPI_AVAILABLE:
    if not FASTAPI_AVAILABLE:
    logger.warning("FastAPI is required for rate limiting middleware")
    logger.warning("FastAPI is required for rate limiting middleware")
    return # Skip if rate limiting is disabled
    return # Skip if rate limiting is disabled
    if not config.enable_rate_limit:
    if not config.enable_rate_limit:
    logger.info("Rate limiting is disabled")
    logger.info("Rate limiting is disabled")
    return # Create middleware
    return # Create middleware
    rate_limit_middleware = RateLimitMiddleware(config)
    rate_limit_middleware = RateLimitMiddleware(config)


    @app.middleware("http")
    @app.middleware("http")
    async def rate_limit_middleware_func(
    async def rate_limit_middleware_func(
    request: Request, call_next: Callable
    request: Request, call_next: Callable
    ) -> Response:
    ) -> Response:
    """
    """
    Rate limiting middleware function.
    Rate limiting middleware function.


    Args:
    Args:
    request: HTTP request
    request: HTTP request
    call_next: Next middleware function
    call_next: Next middleware function


    Returns:
    Returns:
    HTTP response
    HTTP response
    """
    """
    # Skip rate limiting for certain paths
    # Skip rate limiting for certain paths
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
    return await call_next(request)
    return await call_next(request)


    # Get client ID based on rate limit scope
    # Get client ID based on rate limit scope
    client_id = "unknown"
    client_id = "unknown"
    if config.rate_limit_scope == RateLimitScope.IP:
    if config.rate_limit_scope == RateLimitScope.IP:
    client_id = request.client.host if request.client else "unknown"
    client_id = request.client.host if request.client else "unknown"
    elif config.rate_limit_scope == RateLimitScope.API_KEY:
    elif config.rate_limit_scope == RateLimitScope.API_KEY:
    client_id = request.headers.get("X-API-Key", "unknown")
    client_id = request.headers.get("X-API-Key", "unknown")
    elif config.rate_limit_scope == RateLimitScope.USER:
    elif config.rate_limit_scope == RateLimitScope.USER:
    # Get user ID from authentication
    # Get user ID from authentication
    client_id = getattr(request.state, "user_id", "unknown")
    client_id = getattr(request.state, "user_id", "unknown")


    # Get API key if available
    # Get API key if available
    api_key = request.headers.get("X-API-Key")
    api_key = request.headers.get("X-API-Key")


    # Get endpoint path
    # Get endpoint path
    endpoint = request.url.path
    endpoint = request.url.path


    # Check rate limit
    # Check rate limit
    allowed, limit_info = rate_limit_middleware.check_rate_limit(
    allowed, limit_info = rate_limit_middleware.check_rate_limit(
    client_id, endpoint, api_key
    client_id, endpoint, api_key
    )
    )


    if not allowed:
    if not allowed:
    # Return rate limit exceeded response
    # Return rate limit exceeded response
    headers = rate_limit_middleware.get_rate_limit_headers(limit_info)
    headers = rate_limit_middleware.get_rate_limit_headers(limit_info)


    return Response(
    return Response(
    status_code=429,
    status_code=429,
    content='{"detail":"Rate limit exceeded"}',
    content='{"detail":"Rate limit exceeded"}',
    media_type="application/json",
    media_type="application/json",
    headers=headers,
    headers=headers,
    )
    )


    # Process the request
    # Process the request
    response = await call_next(request)
    response = await call_next(request)


    # Add rate limit headers
    # Add rate limit headers
    headers = rate_limit_middleware.get_rate_limit_headers(limit_info)
    headers = rate_limit_middleware.get_rate_limit_headers(limit_info)
    for header, value in headers.items():
    for header, value in headers.items():
    response.headers[header] = value
    response.headers[header] = value


    return response
    return response