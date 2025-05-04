"""
Base GraphQL resolvers.

This module provides the base Query and Mutation classes that other
module-specific resolvers will extend.
"""

import datetime
import logging
from datetime import datetime

import strawberry
from strawberry.types import Info

STRAWBERRY_AVAILABLE
from ..schemas.base import HealthCheckResult



# Set up logging
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:

    = True
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL resolvers")
    STRAWBERRY_AVAILABLE = False

    if STRAWBERRY_AVAILABLE:
    @strawberry.type
    class Query:
    """Base query type that all other query types will extend."""

    @strawberry.field
    def health(self, info: Info) -> HealthCheckResult:
    """
    Get API health status.

    Args:
    info: GraphQL resolver info

    Returns:
    Health check result
    """
    # Get request context
    request = info.context["request"]

    # Get server instance from app state
    server = getattr(request.app.state, "api_server", None)

    # Get uptime
    uptime = 0
    if server:
    uptime = server.get_uptime()

    # Return health check result
    return HealthCheckResult(
    status="ok",
    version=getattr(request.app, "version", "unknown"),
    timestamp=datetime.datetime.now().isoformat(),
    uptime_seconds=uptime,
    )

    @strawberry.type
    class Mutation:
    """Base mutation type that all other mutation types will extend."""

    @strawberry.field
    def ping(self) -> str:
    """
    Simple ping mutation for testing.

    Returns:
    Pong response
    """
    return "pong"