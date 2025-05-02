"""
Middleware for REST API server.

This module provides middleware for the REST API server.
"""

import time
from typing import Callable, List

# Try to import FastAPI
try:
    from fastapi import Request, Response
    from fastapi.security import APIKeyHeader
    from starlette.middleware.base import BaseHTTPMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for type hints
    class BaseHTTPMiddleware:
        pass

    class Request:
        pass

    class Response:
        pass


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API key authentication.
    """

    def __init__(self, app, api_keys: List[str]):
        """
        Initialize the authentication middleware.

        Args:
            app: FastAPI application
            api_keys: List of valid API keys
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI is required for REST API server")

        super().__init__(app)
        self.api_keys = api_keys
        self.api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request.

        Args:
            request: FastAPI request
            call_next: Next middleware or route handler

        Returns:
            Response
        """
        # Skip authentication for docs and OpenAPI
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get("X-API-Key")

        # Check if API key is valid
        if not api_key or api_key not in self.api_keys:
            return Response(
                content='{"detail":"Invalid or missing API key"}',
                status_code=401,
                media_type="application/json",
            )

        # Continue processing the request
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting.
    """

    def __init__(self, app, rate_limit: int = 60):
        """
        Initialize the rate limiting middleware.

        Args:
            app: FastAPI application
            rate_limit: Maximum number of requests per minute
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI is required for REST API server")

        super().__init__(app)
        self.rate_limit = rate_limit
        self.window_size = 60  # 1 minute window
        self.requests = {}  # client_id -> list of request timestamps

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request.

        Args:
            request: FastAPI request
            call_next: Next middleware or route handler

        Returns:
            Response
        """
        # Skip rate limiting for docs and OpenAPI
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get client ID (IP address or API key)
        client_id = request.headers.get("X-API-Key", request.client.host)

        # Get current time
        current_time = time.time()

        # Initialize client's request history if not exists
        if client_id not in self.requests:
            self.requests[client_id] = []

        # Remove requests older than the window size
        self.requests[client_id] = [
            timestamp
            for timestamp in self.requests[client_id]
            if current_time - timestamp < self.window_size
        ]

        # Check if rate limit is exceeded
        if len(self.requests[client_id]) >= self.rate_limit:
            return Response(
                content='{"detail":"Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
            )

        # Add current request to history
        self.requests[client_id].append(current_time)

        # Continue processing the request
        return await call_next(request)


def setup_middleware(app, config):
    """
    Set up middleware for the REST API server.

    Args:
        app: FastAPI application
        config: Server configuration
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI is required for REST API server")

    # Add authentication middleware if enabled
    if config.enable_auth and config.api_keys:
        app.add_middleware(AuthMiddleware, api_keys=config.api_keys)

    # Add rate limiting middleware if enabled
    if config.enable_rate_limit:
        app.add_middleware(RateLimitMiddleware, rate_limit=config.rate_limit)

    # Add CORS middleware if enabled
    if config.enable_cors:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add GZip middleware if enabled
    if config.enable_gzip:
        from fastapi.middleware.gzip import GZipMiddleware

        app.add_middleware(GZipMiddleware, minimum_size=1000)
