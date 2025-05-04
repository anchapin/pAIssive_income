"""
"""
Version middleware for the API server.
Version middleware for the API server.


This module provides middleware for handling API versioning.
This module provides middleware for handling API versioning.
"""
"""




import logging
import logging
from typing import Any, Callable
from typing import Any, Callable


from fastapi import FastAPI, Request, Response
from fastapi import FastAPI, Request, Response


from ..config import APIConfig, APIVersion
from ..config import APIConfig, APIVersion
from ..version_manager import VersionManager
from ..version_manager import VersionManager


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
    logger.warning("FastAPI is required for version middleware")
    logger.warning("FastAPI is required for version middleware")
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False




    class VersionMiddleware:
    class VersionMiddleware:
    """
    """
    Middleware for handling API versioning.
    Middleware for handling API versioning.
    """
    """


    def __init__(self, config: APIConfig, version_manager: VersionManager):
    def __init__(self, config: APIConfig, version_manager: VersionManager):
    """
    """
    Initialize the version middleware.
    Initialize the version middleware.


    Args:
    Args:
    config: API configuration
    config: API configuration
    version_manager: Version manager
    version_manager: Version manager
    """
    """
    self.config = config
    self.config = config
    self.version_manager = version_manager
    self.version_manager = version_manager


    def add_version_headers(self, response: Response, version: APIVersion) -> None:
    def add_version_headers(self, response: Response, version: APIVersion) -> None:
    """
    """
    Add version headers to the response.
    Add version headers to the response.


    Args:
    Args:
    response: HTTP response
    response: HTTP response
    version: API version
    version: API version
    """
    """
    if self.config.enable_version_header:
    if self.config.enable_version_header:
    response.headers[self.config.version_header_name] = version.value
    response.headers[self.config.version_header_name] = version.value


    # Check if this version has any deprecated endpoints
    # Check if this version has any deprecated endpoints
    if self.config.enable_version_deprecation_header:
    if self.config.enable_version_deprecation_header:
    deprecated_endpoints = self.version_manager.get_deprecated_endpoints()
    deprecated_endpoints = self.version_manager.get_deprecated_endpoints()


    # Check if this version has any deprecated endpoints
    # Check if this version has any deprecated endpoints
    is_deprecated = any(
    is_deprecated = any(
    change.get("from_version") == version.value
    change.get("from_version") == version.value
    for change in deprecated_endpoints
    for change in deprecated_endpoints
    )
    )


    if is_deprecated:
    if is_deprecated:
    response.headers[self.config.deprecation_header_name] = "true"
    response.headers[self.config.deprecation_header_name] = "true"


    # Get the earliest sunset date for this version's deprecated endpoints
    # Get the earliest sunset date for this version's deprecated endpoints
    sunset_dates = [
    sunset_dates = [
    change.get("sunset_date")
    change.get("sunset_date")
    for change in deprecated_endpoints
    for change in deprecated_endpoints
    if change.get("from_version") == version.value
    if change.get("from_version") == version.value
    and change.get("sunset_date")
    and change.get("sunset_date")
    ]
    ]


    if sunset_dates:
    if sunset_dates:
    response.headers[self.config.sunset_header_name] = min(sunset_dates)
    response.headers[self.config.sunset_header_name] = min(sunset_dates)




    def setup_version_middleware(
    def setup_version_middleware(
    app: Any, config: APIConfig, version_manager: VersionManager
    app: Any, config: APIConfig, version_manager: VersionManager
    ) -> None:
    ) -> None:
    """
    """
    Set up version middleware for the API server.
    Set up version middleware for the API server.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    config: API configuration
    config: API configuration
    version_manager: Version manager
    version_manager: Version manager
    """
    """
    if not FASTAPI_AVAILABLE:
    if not FASTAPI_AVAILABLE:
    logger.warning("FastAPI is required for version middleware")
    logger.warning("FastAPI is required for version middleware")
    return # Create middleware
    return # Create middleware
    version_middleware = VersionMiddleware(config, version_manager)
    version_middleware = VersionMiddleware(config, version_manager)


    @app.middleware("http")
    @app.middleware("http")
    async def version_middleware_func(
    async def version_middleware_func(
    request: Request, call_next: Callable
    request: Request, call_next: Callable
    ) -> Response:
    ) -> Response:
    """
    """
    Version middleware function.
    Version middleware function.


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
    # Process the request
    # Process the request
    response = await call_next(request)
    response = await call_next(request)


    # Extract version from the URL path
    # Extract version from the URL path
    path = request.url.path
    path = request.url.path
    parts = path.split("/")
    parts = path.split("/")


    # Find the version part in the URL
    # Find the version part in the URL
    version_str = None
    version_str = None
    for i, part in enumerate(parts):
    for i, part in enumerate(parts):
    if part == "api" and i + 1 < len(parts):
    if part == "api" and i + 1 < len(parts):
    version_str = parts[i + 1]
    version_str = parts[i + 1]
    break
    break


    # If version is found in the URL, add version headers
    # If version is found in the URL, add version headers
    if version_str and APIVersion.is_valid_version(version_str):
    if version_str and APIVersion.is_valid_version(version_str):
    for version in APIVersion:
    for version in APIVersion:
    if version.value == version_str:
    if version.value == version_str:
    version_middleware.add_version_headers(response, version)
    version_middleware.add_version_headers(response, version)
    break
    break


    return response
    return response