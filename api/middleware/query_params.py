"""
"""
Query parameter middleware for the API server.
Query parameter middleware for the API server.


This module provides middleware for processing query parameters in API requests.
This module provides middleware for processing query parameters in API requests.
"""
"""




import logging
import logging
from typing import Callable, Dict, List
from typing import Callable, Dict, List


from fastapi import FastAPI, Request, Response
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


from ..utils.query_params import QueryParams
from ..utils.query_params import QueryParams


FASTAPI_AVAILABLE
FASTAPI_AVAILABLE


# Set up logging
# Set up logging
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
    logger.warning("FastAPI is not available. QueryParamsMiddleware will not work.")
    logger.warning("FastAPI is not available. QueryParamsMiddleware will not work.")
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False




    class QueryParamsMiddleware(BaseHTTPMiddleware):
    class QueryParamsMiddleware(BaseHTTPMiddleware):
    """
    """
    Middleware for processing query parameters.
    Middleware for processing query parameters.


    This middleware processes query parameters and adds a QueryParams object
    This middleware processes query parameters and adds a QueryParams object
    to the request state for use in route handlers.
    to the request state for use in route handlers.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    app,
    app,
    allowed_sort_fields: Dict[str, List[str]] = None,
    allowed_sort_fields: Dict[str, List[str]] = None,
    allowed_filter_fields: Dict[str, List[str]] = None,
    allowed_filter_fields: Dict[str, List[str]] = None,
    max_page_size: int = 100,
    max_page_size: int = 100,
    ):
    ):
    """
    """
    Initialize the middleware.
    Initialize the middleware.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    allowed_sort_fields: Dictionary mapping endpoint paths to allowed sort fields
    allowed_sort_fields: Dictionary mapping endpoint paths to allowed sort fields
    allowed_filter_fields: Dictionary mapping endpoint paths to allowed filter fields
    allowed_filter_fields: Dictionary mapping endpoint paths to allowed filter fields
    max_page_size: Maximum allowed page size
    max_page_size: Maximum allowed page size
    """
    """
    if not FASTAPI_AVAILABLE:
    if not FASTAPI_AVAILABLE:
    raise ImportError("FastAPI is required for QueryParamsMiddleware")
    raise ImportError("FastAPI is required for QueryParamsMiddleware")


    super().__init__(app)
    super().__init__(app)
    self.allowed_sort_fields = allowed_sort_fields or {}
    self.allowed_sort_fields = allowed_sort_fields or {}
    self.allowed_filter_fields = allowed_filter_fields or {}
    self.allowed_filter_fields = allowed_filter_fields or {}
    self.max_page_size = max_page_size
    self.max_page_size = max_page_size


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
    # Skip processing for non-GET requests
    # Skip processing for non-GET requests
    if request.method != "GET":
    if request.method != "GET":
    return await call_next(request)
    return await call_next(request)


    # Get request path
    # Get request path
    path = request.url.path
    path = request.url.path


    # Get allowed fields for this path
    # Get allowed fields for this path
    allowed_sort = None
    allowed_sort = None
    allowed_filter = None
    allowed_filter = None


    # Check for exact path match
    # Check for exact path match
    if path in self.allowed_sort_fields:
    if path in self.allowed_sort_fields:
    allowed_sort = self.allowed_sort_fields[path]
    allowed_sort = self.allowed_sort_fields[path]


    if path in self.allowed_filter_fields:
    if path in self.allowed_filter_fields:
    allowed_filter = self.allowed_filter_fields[path]
    allowed_filter = self.allowed_filter_fields[path]


    # Check for path prefix match if no exact match
    # Check for path prefix match if no exact match
    if allowed_sort is None or allowed_filter is None:
    if allowed_sort is None or allowed_filter is None:
    for prefix, fields in self.allowed_sort_fields.items():
    for prefix, fields in self.allowed_sort_fields.items():
    if path.startswith(prefix) and (allowed_sort is None):
    if path.startswith(prefix) and (allowed_sort is None):
    allowed_sort = fields
    allowed_sort = fields
    break
    break


    for prefix, fields in self.allowed_filter_fields.items():
    for prefix, fields in self.allowed_filter_fields.items():
    if path.startswith(prefix) and (allowed_filter is None):
    if path.startswith(prefix) and (allowed_filter is None):
    allowed_filter = fields
    allowed_filter = fields
    break
    break


    # Get query parameters
    # Get query parameters
    params = dict(request.query_params)
    params = dict(request.query_params)


    # Create QueryParams object
    # Create QueryParams object
    query_params = QueryParams.from_request(
    query_params = QueryParams.from_request(
    params,
    params,
    allowed_sort_fields=allowed_sort,
    allowed_sort_fields=allowed_sort,
    allowed_filter_fields=allowed_filter,
    allowed_filter_fields=allowed_filter,
    max_page_size=self.max_page_size,
    max_page_size=self.max_page_size,
    )
    )


    # Add QueryParams to request state
    # Add QueryParams to request state
    request.state.query_params = query_params
    request.state.query_params = query_params


    # Continue processing the request
    # Continue processing the request
    return await call_next(request)
    return await call_next(request)




    def setup_query_params_middleware(
    def setup_query_params_middleware(
    app,
    app,
    allowed_sort_fields: Dict[str, List[str]] = None,
    allowed_sort_fields: Dict[str, List[str]] = None,
    allowed_filter_fields: Dict[str, List[str]] = None,
    allowed_filter_fields: Dict[str, List[str]] = None,
    max_page_size: int = 100,
    max_page_size: int = 100,
    ) -> None:
    ) -> None:
    """
    """
    Set up query parameter middleware.
    Set up query parameter middleware.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    allowed_sort_fields: Dictionary mapping endpoint paths to allowed sort fields
    allowed_sort_fields: Dictionary mapping endpoint paths to allowed sort fields
    allowed_filter_fields: Dictionary mapping endpoint paths to allowed filter fields
    allowed_filter_fields: Dictionary mapping endpoint paths to allowed filter fields
    max_page_size: Maximum allowed page size
    max_page_size: Maximum allowed page size
    """
    """
    if not FASTAPI_AVAILABLE:
    if not FASTAPI_AVAILABLE:
    logger.warning(
    logger.warning(
    "FastAPI is not available. QueryParamsMiddleware will not be added."
    "FastAPI is not available. QueryParamsMiddleware will not be added."
    )
    )
    return app.add_middleware(
    return app.add_middleware(
    QueryParamsMiddleware,
    QueryParamsMiddleware,
    allowed_sort_fields=allowed_sort_fields,
    allowed_sort_fields=allowed_sort_fields,
    allowed_filter_fields=allowed_filter_fields,
    allowed_filter_fields=allowed_filter_fields,
    max_page_size=max_page_size,
    max_page_size=max_page_size,
    )
    )