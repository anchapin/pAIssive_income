"""
Middleware setup for the API server.

This module provides functions for setting up middleware for the API server.
"""

import logging
from typing import Any

from ..config import APIConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI is required for middleware setup")
    FASTAPI_AVAILABLE = False


def setup_middleware(app: Any, config: APIConfig) -> None:
    """
    Set up middleware for the API server.
    
    Args:
        app: FastAPI application
        config: API configuration
    """
    if not FASTAPI_AVAILABLE:
        logger.warning("FastAPI is required for middleware setup")
        return
    
    # Add CORS middleware
    if config.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify allowed origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Add GZip middleware
    if config.enable_gzip:
        app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add authentication middleware
    if config.enable_auth:
        from .auth import setup_auth_middleware
        setup_auth_middleware(app, config)
    
    # Add rate limiting middleware
    if config.enable_rate_limit:
        from .rate_limit import setup_rate_limit_middleware
        setup_rate_limit_middleware(app, config)
