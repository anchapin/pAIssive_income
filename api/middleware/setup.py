"""
"""
Middleware setup for the API server.
Middleware setup for the API server.


This module provides functions for setting up middleware for the API server.
This module provides functions for setting up middleware for the API server.
"""
"""




import logging
import logging
from typing import Any
from typing import Any


from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.gzip import GZipMiddleware


from ..config import APIConfig
from ..config import APIConfig
from ..version_manager import VersionManager
from ..version_manager import VersionManager


FASTAPI_AVAILABLE
FASTAPI_AVAILABLE
from .auth import setup_auth_middleware
from .auth import setup_auth_middleware


setup_auth_middleware
setup_auth_middleware
from .rate_limit import setup_rate_limit_middleware
from .rate_limit import setup_rate_limit_middleware


setup_rate_limit_middleware
setup_rate_limit_middleware
from .version import setup_version_middleware
from .version import setup_version_middleware


setup_version_middleware
setup_version_middleware
from .analytics import AnalyticsMiddleware
from .analytics import AnalyticsMiddleware


AnalyticsMiddleware
AnalyticsMiddleware
from .query_params import setup_query_params_middleware
from .query_params import setup_query_params_middleware






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
    logger.warning("FastAPI is required for middleware setup")
    logger.warning("FastAPI is required for middleware setup")
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False




    def setup_middleware(
    def setup_middleware(
    app: Any, config: APIConfig, version_manager: VersionManager = None
    app: Any, config: APIConfig, version_manager: VersionManager = None
    ) -> None:
    ) -> None:
    """
    """
    Set up middleware for the API server.
    Set up middleware for the API server.


    Args:
    Args:
    app: FastAPI application
    app: FastAPI application
    config: API configuration
    config: API configuration
    version_manager: Optional version manager for version middleware
    version_manager: Optional version manager for version middleware
    """
    """
    if not FASTAPI_AVAILABLE:
    if not FASTAPI_AVAILABLE:
    logger.warning("FastAPI is required for middleware setup")
    logger.warning("FastAPI is required for middleware setup")
    return # Add CORS middleware
    return # Add CORS middleware
    if config.enable_cors:
    if config.enable_cors:
    app.add_middleware(
    app.add_middleware(
    CORSMiddleware,
    CORSMiddleware,
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


    # Add GZip middleware
    # Add GZip middleware
    if config.enable_gzip:
    if config.enable_gzip:
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(GZipMiddleware, minimum_size=1000)


    # Add authentication middleware
    # Add authentication middleware
    if config.enable_auth:
    if config.enable_auth:
    (app, config)
    (app, config)


    # Add rate limiting middleware
    # Add rate limiting middleware
    if config.enable_rate_limit:
    if config.enable_rate_limit:
    (app, config)
    (app, config)


    # Add version middleware if version manager is provided
    # Add version middleware if version manager is provided
    if version_manager is not None:
    if version_manager is not None:
    (app, config, version_manager)
    (app, config, version_manager)


    # Add analytics middleware
    # Add analytics middleware
    if config.enable_analytics:
    if config.enable_analytics:
    (app)
    (app)


    # Add query parameters middleware
    # Add query parameters middleware
    # Define allowed sort and filter fields for each endpoint
    # Define allowed sort and filter fields for each endpoint
    allowed_sort_fields = {
    allowed_sort_fields = {
    "/api/v1/niche-analysis/niches": [
    "/api/v1/niche-analysis/niches": [
    "name",
    "name",
    "market_segment",
    "market_segment",
    "opportunity_score",
    "opportunity_score",
    "created_at",
    "created_at",
    ],
    ],
    "/api/v1/monetization/subscription-models": ["name", "type", "created_at"],
    "/api/v1/monetization/subscription-models": ["name", "type", "created_at"],
    "/api/v1/marketing/campaigns": ["name", "status", "start_date", "end_date"],
    "/api/v1/marketing/campaigns": ["name", "status", "start_date", "end_date"],
    "/api/v1/ai-models/models": ["name", "type", "size", "created_at"],
    "/api/v1/ai-models/models": ["name", "type", "size", "created_at"],
    "/api/v1/agent-team/agents": ["name", "role", "status", "created_at"],
    "/api/v1/agent-team/agents": ["name", "role", "status", "created_at"],
    "/api/v1/users": ["username", "email", "created_at", "last_login"],
    "/api/v1/users": ["username", "email", "created_at", "last_login"],
    }
    }


    allowed_filter_fields = {
    allowed_filter_fields = {
    "/api/v1/niche-analysis/niches": [
    "/api/v1/niche-analysis/niches": [
    "name",
    "name",
    "market_segment",
    "market_segment",
    "opportunity_score",
    "opportunity_score",
    ],
    ],
    "/api/v1/monetization/subscription-models": ["name", "type", "solution_id"],
    "/api/v1/monetization/subscription-models": ["name", "type", "solution_id"],
    "/api/v1/marketing/campaigns": ["name", "status", "channel"],
    "/api/v1/marketing/campaigns": ["name", "status", "channel"],
    "/api/v1/ai-models/models": ["name", "type", "provider"],
    "/api/v1/ai-models/models": ["name", "type", "provider"],
    "/api/v1/agent-team/agents": ["name", "role", "status"],
    "/api/v1/agent-team/agents": ["name", "role", "status"],
    "/api/v1/users": ["username", "email", "status"],
    "/api/v1/users": ["username", "email", "status"],
    }
    }


    setup_query_params_middleware(
    setup_query_params_middleware(
    app,
    app,
    allowed_sort_fields=allowed_sort_fields,
    allowed_sort_fields=allowed_sort_fields,
    allowed_filter_fields=allowed_filter_fields,
    allowed_filter_fields=allowed_filter_fields,
    max_page_size=config.max_page_size,
    max_page_size=config.max_page_size,
    )
    )