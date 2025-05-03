"""
Query parameter middleware for the API server.

This module provides middleware for processing query parameters in API requests.
"""


import logging
from typing import Callable, Dict, List

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.query_params import QueryParams


    from fastapi import FastAPI

    FASTAPI_AVAILABLE 

# Set up logging
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
= True
except ImportError:
    logger.warning("FastAPI is not available. QueryParamsMiddleware will not work.")
    FASTAPI_AVAILABLE = False


class QueryParamsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for processing query parameters.

    This middleware processes query parameters and adds a QueryParams object
    to the request state for use in route handlers.
    """

    def __init__(
        self,
        app,
        allowed_sort_fields: Dict[str, List[str]] = None,
        allowed_filter_fields: Dict[str, List[str]] = None,
        max_page_size: int = 100,
    ):
        """
        Initialize the middleware.

        Args:
            app: FastAPI application
            allowed_sort_fields: Dictionary mapping endpoint paths to allowed sort fields
            allowed_filter_fields: Dictionary mapping endpoint paths to allowed filter fields
            max_page_size: Maximum allowed page size
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI is required for QueryParamsMiddleware")

        super().__init__(app)
        self.allowed_sort_fields = allowed_sort_fields or {}
        self.allowed_filter_fields = allowed_filter_fields or {}
        self.max_page_size = max_page_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request.

        Args:
            request: FastAPI request
            call_next: Next middleware or route handler

        Returns:
            Response
        """
        # Skip processing for non-GET requests
        if request.method != "GET":
                    return await call_next(request)

        # Get request path
        path = request.url.path

        # Get allowed fields for this path
        allowed_sort = None
        allowed_filter = None

        # Check for exact path match
        if path in self.allowed_sort_fields:
            allowed_sort = self.allowed_sort_fields[path]

        if path in self.allowed_filter_fields:
            allowed_filter = self.allowed_filter_fields[path]

        # Check for path prefix match if no exact match
        if allowed_sort is None or allowed_filter is None:
            for prefix, fields in self.allowed_sort_fields.items():
                if path.startswith(prefix) and (allowed_sort is None):
                    allowed_sort = fields
                    break

            for prefix, fields in self.allowed_filter_fields.items():
                if path.startswith(prefix) and (allowed_filter is None):
                    allowed_filter = fields
                    break

        # Get query parameters
        params = dict(request.query_params)

        # Create QueryParams object
        query_params = QueryParams.from_request(
            params,
            allowed_sort_fields=allowed_sort,
            allowed_filter_fields=allowed_filter,
            max_page_size=self.max_page_size,
        )

        # Add QueryParams to request state
        request.state.query_params = query_params

        # Continue processing the request
                return await call_next(request)


def setup_query_params_middleware(
    app,
    allowed_sort_fields: Dict[str, List[str]] = None,
    allowed_filter_fields: Dict[str, List[str]] = None,
    max_page_size: int = 100,
) -> None:
    """
    Set up query parameter middleware.

    Args:
        app: FastAPI application
        allowed_sort_fields: Dictionary mapping endpoint paths to allowed sort fields
        allowed_filter_fields: Dictionary mapping endpoint paths to allowed filter fields
        max_page_size: Maximum allowed page size
    """
    if not FASTAPI_AVAILABLE:
        logger.warning(
            "FastAPI is not available. QueryParamsMiddleware will not be added."
        )
                return app.add_middleware(
        QueryParamsMiddleware,
        allowed_sort_fields=allowed_sort_fields,
        allowed_filter_fields=allowed_filter_fields,
        max_page_size=max_page_size,
    )