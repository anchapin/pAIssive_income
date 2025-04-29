"""
Rate limiting middleware for the API server.

This module provides rate limiting middleware for the API server.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime, timedelta

from ..config import APIConfig, RateLimitScope
from ..rate_limit import RateLimitManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    from fastapi import FastAPI, Request, Response
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI is required for rate limiting middleware")
    FASTAPI_AVAILABLE = False


class RateLimitMiddleware:
    """
    Rate limiting middleware for the API server.
    """

    def __init__(self, config: APIConfig):
        """
        Initialize the rate limiting middleware.

        Args:
            config: API configuration
        """
        self.config = config

        # Create rate limit manager
        storage_type = "redis" if hasattr(config, "redis_url") and config.redis_url else "memory"
        storage_kwargs = {}
        if storage_type == "redis":
            storage_kwargs["redis_url"] = config.redis_url

        self.rate_limit_manager = RateLimitManager(config, storage_type, **storage_kwargs)

    def check_rate_limit(
        self,
        client_id: str,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request should be rate limited.

        Args:
            client_id: Client identifier (e.g., IP address)
            endpoint: Optional endpoint path
            api_key: Optional API key

        Returns:
            Tuple of (allowed, limit_info)
            - allowed: True if the request is allowed, False if it should be rate limited
            - limit_info: Dictionary with rate limit information
        """
        return self.rate_limit_manager.check_rate_limit(client_id, endpoint, api_key)

    def get_rate_limit_headers(self, limit_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Get rate limit headers for a response.

        Args:
            limit_info: Rate limit information

        Returns:
            Dictionary of rate limit headers
        """
        return self.rate_limit_manager.get_rate_limit_headers(limit_info)


def setup_rate_limit_middleware(app: Any, config: APIConfig) -> None:
    """
    Set up rate limiting middleware for the API server.

    Args:
        app: FastAPI application
        config: API configuration
    """
    if not FASTAPI_AVAILABLE:
        logger.warning("FastAPI is required for rate limiting middleware")
        return

    # Skip if rate limiting is disabled
    if not config.enable_rate_limit:
        logger.info("Rate limiting is disabled")
        return

    # Create middleware
    rate_limit_middleware = RateLimitMiddleware(config)

    @app.middleware("http")
    async def rate_limit_middleware_func(request: Request, call_next: Callable) -> Response:
        """
        Rate limiting middleware function.

        Args:
            request: HTTP request
            call_next: Next middleware function

        Returns:
            HTTP response
        """
        # Skip rate limiting for certain paths
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get client ID based on rate limit scope
        client_id = "unknown"
        if config.rate_limit_scope == RateLimitScope.IP:
            client_id = request.client.host if request.client else "unknown"
        elif config.rate_limit_scope == RateLimitScope.API_KEY:
            client_id = request.headers.get("X-API-Key", "unknown")
        elif config.rate_limit_scope == RateLimitScope.USER:
            # Get user ID from authentication
            client_id = getattr(request.state, "user_id", "unknown")

        # Get API key if available
        api_key = request.headers.get("X-API-Key")

        # Get endpoint path
        endpoint = request.url.path

        # Check rate limit
        allowed, limit_info = rate_limit_middleware.check_rate_limit(client_id, endpoint, api_key)

        if not allowed:
            # Return rate limit exceeded response
            headers = rate_limit_middleware.get_rate_limit_headers(limit_info)

            return Response(
                status_code=429,
                content='{"detail":"Rate limit exceeded"}',
                media_type="application/json",
                headers=headers
            )

        # Process the request
        response = await call_next(request)

        # Add rate limit headers
        headers = rate_limit_middleware.get_rate_limit_headers(limit_info)
        for header, value in headers.items():
            response.headers[header] = value

        return response
