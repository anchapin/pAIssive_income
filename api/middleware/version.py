"""
Version middleware for the API server.

This module provides middleware for handling API versioning.
"""


import logging
from typing import Any, Callable

from fastapi import FastAPI, Request, Response

from ..config import APIConfig, APIVersion
from ..version_manager import VersionManager

FASTAPI_AVAILABLE

# Set up logging
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    = True
except ImportError:
    logger.warning("FastAPI is required for version middleware")
    FASTAPI_AVAILABLE = False


    class VersionMiddleware:
    """
    Middleware for handling API versioning.
    """

    def __init__(self, config: APIConfig, version_manager: VersionManager):
    """
    Initialize the version middleware.

    Args:
    config: API configuration
    version_manager: Version manager
    """
    self.config = config
    self.version_manager = version_manager

    def add_version_headers(self, response: Response, version: APIVersion) -> None:
    """
    Add version headers to the response.

    Args:
    response: HTTP response
    version: API version
    """
    if self.config.enable_version_header:
    response.headers[self.config.version_header_name] = version.value

    # Check if this version has any deprecated endpoints
    if self.config.enable_version_deprecation_header:
    deprecated_endpoints = self.version_manager.get_deprecated_endpoints()

    # Check if this version has any deprecated endpoints
    is_deprecated = any(
    change.get("from_version") == version.value
    for change in deprecated_endpoints
    )

    if is_deprecated:
    response.headers[self.config.deprecation_header_name] = "true"

    # Get the earliest sunset date for this version's deprecated endpoints
    sunset_dates = [
    change.get("sunset_date")
    for change in deprecated_endpoints
    if change.get("from_version") == version.value
    and change.get("sunset_date")
    ]

    if sunset_dates:
    response.headers[self.config.sunset_header_name] = min(sunset_dates)


    def setup_version_middleware(
    app: Any, config: APIConfig, version_manager: VersionManager
    ) -> None:
    """
    Set up version middleware for the API server.

    Args:
    app: FastAPI application
    config: API configuration
    version_manager: Version manager
    """
    if not FASTAPI_AVAILABLE:
    logger.warning("FastAPI is required for version middleware")
    return # Create middleware
    version_middleware = VersionMiddleware(config, version_manager)

    @app.middleware("http")
    async def version_middleware_func(
    request: Request, call_next: Callable
    ) -> Response:
    """
    Version middleware function.

    Args:
    request: HTTP request
    call_next: Next middleware function

    Returns:
    HTTP response
    """
    # Process the request
    response = await call_next(request)

    # Extract version from the URL path
    path = request.url.path
    parts = path.split("/")

    # Find the version part in the URL
    version_str = None
    for i, part in enumerate(parts):
    if part == "api" and i + 1 < len(parts):
    version_str = parts[i + 1]
    break

    # If version is found in the URL, add version headers
    if version_str and APIVersion.is_valid_version(version_str):
    for version in APIVersion:
    if version.value == version_str:
    version_middleware.add_version_headers(response, version)
    break

    return response