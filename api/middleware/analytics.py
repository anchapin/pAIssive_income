"""
Analytics middleware for the API server.

This middleware collects analytics data for API requests.
"""

import logging
import time
from typing import Callable

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    from fastapi import Request, Response

    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI is required for analytics middleware")
    FASTAPI_AVAILABLE = False

# Import analytics service
from api.analytics import analytics_service

class AnalyticsMiddleware:
    """
    Middleware for collecting API analytics.
    """

    def __init__(self, app):
        """
        Initialize the analytics middleware.

        Args:
            app: FastAPI application
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI is required for analytics middleware")

        self.app = app

        # Register middleware
        @app.middleware("http")
        async def analytics_middleware(request: Request, 
            call_next: Callable) -> Response:
            return await self.dispatch(request, call_next)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and collect analytics data.

        Args:
            request: FastAPI request
            call_next: Next middleware or route handler

        Returns:
            Response
        """
        # Skip analytics for docs and OpenAPI
        if request.url.path in [" / docs", " / redoc", " / openapi.json"]:
            return await call_next(request)

        # Record start time
        start_time = time.time()

        # Get request information
        method = request.method
        path = request.url.path

        # Extract API version from path
        version = None
        if " / api / " in path:
            parts = path.split(" / ")
            for i, part in enumerate(parts):
                if part == "api" and i + 1 < len(parts):
                    version = parts[i + 1]
                    break

        # Get client information
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("User - Agent")

        # Get authentication information
        user_id = None
        api_key_id = None

        # Try to get user ID from request state
        if hasattr(request, "state") and hasattr(request.state, "user"):
            user = request.state.user
            if hasattr(user, "id"):
                user_id = str(user.id)

        # Try to get API key ID from header
        api_key = request.headers.get("X - API - Key")
        if api_key:
            # Use the API key as the ID for now
            # In a real implementation, you would look up the API key ID
            api_key_id = api_key

        # Get query parameters
        query_params = {}
        for key, value in request.query_params.items():
            query_params[key] = value

        # Process the request
        response = None
        error_type = None
        error_message = None

        try:
            # Call the next middleware or route handler
            response = await call_next(request)

            # Get response information
            status_code = response.status_code

            # Check if response is an error
            if status_code >= 400:
                error_type = f"HTTP{status_code}"
                error_message = "HTTP error"

        except Exception as e:
            # Handle exceptions
            error_type = type(e).__name__
            error_message = str(e)

            # Re - raise the exception
            raise

        finally:
            # Calculate response time
            response_time = time.time() - start_time

            # Get response size (if available)
            response_size = None
            if response and hasattr(response, "headers"):
                content_length = response.headers.get("Content - Length")
                if content_length and content_length.isdigit():
                    response_size = int(content_length)

            # Get request size (if available)
            request_size = None
            content_length = request.headers.get("Content - Length")
            if content_length and content_length.isdigit():
                request_size = int(content_length)

            # Determine endpoint
            endpoint = path

            # Try to get a more descriptive endpoint name from the route
            if hasattr(request, "scope") and "route" in request.scope:
                route = request.scope["route"]
                if hasattr(route, "path"):
                    endpoint = route.path

            # Track the request
            try:
                analytics_service.track_request(
                    method=method,
                    path=path,
                    endpoint=endpoint,
                    version=version,
                    status_code=response.status_code if response else None,
                    response_time=response_time,
                    user_id=user_id,
                    api_key_id=api_key_id,
                    client_ip=client_ip,
                    user_agent=user_agent,
                    request_size=request_size,
                    response_size=response_size,
                    query_params=query_params,
                    error_type=error_type,
                    error_message=error_message,
                )
            except Exception as e:
                logger.error(f"Error tracking request: {e}")

        return response
