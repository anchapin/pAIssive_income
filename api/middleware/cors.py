"""
"""
CORS middleware for the API server.
CORS middleware for the API server.


This module provides CORS middleware for the API server.
This module provides CORS middleware for the API server.
"""
"""




import logging
import logging
from typing import Any, List
from typing import Any, List


from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware


from ..config import APIConfig
from ..config import APIConfig


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
    logger.warning("FastAPI is required for CORS middleware")
    logger.warning("FastAPI is required for CORS middleware")
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False




    class CORSMiddleware:
    class CORSMiddleware:
    """
    """
    CORS middleware for the API server.
    CORS middleware for the API server.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    allow_origins: List[str] = ["*"],
    allow_origins: List[str] = ["*"],
    allow_methods: List[str] = ["*"],
    allow_methods: List[str] = ["*"],
    allow_headers: List[str] = ["*"],
    allow_headers: List[str] = ["*"],
    allow_credentials: bool = True,
    allow_credentials: bool = True,
    expose_headers: List[str] = [],
    expose_headers: List[str] = [],
    max_age: int = 600,
    max_age: int = 600,
    ):
    ):
    """
    """
    Initialize the CORS middleware.
    Initialize the CORS middleware.


    Args:
    Args:
    allow_origins: List of allowed origins
    allow_origins: List of allowed origins
    allow_methods: List of allowed methods
    allow_methods: List of allowed methods
    allow_headers: List of allowed headers
    allow_headers: List of allowed headers
    allow_credentials: Whether to allow credentials
    allow_credentials: Whether to allow credentials
    expose_headers: List of headers to expose
    expose_headers: List of headers to expose
    max_age: Maximum age of preflight requests
    max_age: Maximum age of preflight requests
    """
    """
    self.allow_origins = allow_origins
    self.allow_origins = allow_origins
    self.allow_methods = allow_methods
    self.allow_methods = allow_methods
    self.allow_headers = allow_headers
    self.allow_headers = allow_headers
    self.allow_credentials = allow_credentials
    self.allow_credentials = allow_credentials
    self.expose_headers = expose_headers
    self.expose_headers = expose_headers
    self.max_age = max_age
    self.max_age = max_age




    def setup_cors_middleware(app: Any, config: APIConfig) -> None:
    def setup_cors_middleware(app: Any, config: APIConfig) -> None:
    """
    """
    Set up CORS middleware for the API server.
    Set up CORS middleware for the API server.


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
    logger.warning("FastAPI is required for CORS middleware")
    logger.warning("FastAPI is required for CORS middleware")
    return # Add CORS middleware
    return # Add CORS middleware
    app.add_middleware(
    app.add_middleware(
    FastAPICORSMiddleware,
    FastAPICORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_credentials=True,
    allow_methods=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_headers=["*"],
    )
    )