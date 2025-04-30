"""
Middleware setup for the API server.

This module provides functions for setting up middleware for the API server.
"""

import logging
from typing import Any

from ..config import APIConfig
from ..version_manager import VersionManager

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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


def setup_middleware(
    app: Any, config: APIConfig, version_manager: VersionManager = None
) -> None:
    """
    Set up middleware for the API server.

    Args:
        app: FastAPI application
        config: API configuration
        version_manager: Optional version manager for version middleware
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

    # Add version middleware if version manager is provided
    if version_manager is not None:
        from .version import setup_version_middleware

        setup_version_middleware(app, config, version_manager)

    # Add analytics middleware
    if config.enable_analytics:
        from .analytics import AnalyticsMiddleware

        AnalyticsMiddleware(app)

    # Add query parameters middleware
    from .query_params import setup_query_params_middleware

    # Define allowed sort and filter fields for each endpoint
    allowed_sort_fields = {
        "/api/v1/niche-analysis/niches": [
            "name",
            "market_segment",
            "opportunity_score",
            "created_at",
        ],
        "/api/v1/monetization/subscription-models": ["name", "type", "created_at"],
        "/api/v1/marketing/campaigns": ["name", "status", "start_date", "end_date"],
        "/api/v1/ai-models/models": ["name", "type", "size", "created_at"],
        "/api/v1/agent-team/agents": ["name", "role", "status", "created_at"],
        "/api/v1/users": ["username", "email", "created_at", "last_login"],
    }

    allowed_filter_fields = {
        "/api/v1/niche-analysis/niches": [
            "name",
            "market_segment",
            "opportunity_score",
        ],
        "/api/v1/monetization/subscription-models": ["name", "type", "solution_id"],
        "/api/v1/marketing/campaigns": ["name", "status", "channel"],
        "/api/v1/ai-models/models": ["name", "type", "provider"],
        "/api/v1/agent-team/agents": ["name", "role", "status"],
        "/api/v1/users": ["username", "email", "status"],
    }

    setup_query_params_middleware(
        app,
        allowed_sort_fields=allowed_sort_fields,
        allowed_filter_fields=allowed_filter_fields,
        max_page_size=config.max_page_size,
    )
