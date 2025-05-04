"""
"""
Base GraphQL resolvers.
Base GraphQL resolvers.


This module provides the base Query and Mutation classes that other
This module provides the base Query and Mutation classes that other
module-specific resolvers will extend.
module-specific resolvers will extend.
"""
"""


import datetime
import datetime
import logging
import logging
from datetime import datetime
from datetime import datetime


import strawberry
import strawberry
from strawberry.types import Info
from strawberry.types import Info


STRAWBERRY_AVAILABLE
STRAWBERRY_AVAILABLE
from ..schemas.base import HealthCheckResult
from ..schemas.base import HealthCheckResult






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


try:
    try:


    = True
    = True
except ImportError:
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL resolvers")
    logger.warning("Strawberry GraphQL is required for GraphQL resolvers")
    STRAWBERRY_AVAILABLE = False
    STRAWBERRY_AVAILABLE = False


    if STRAWBERRY_AVAILABLE:
    if STRAWBERRY_AVAILABLE:
    @strawberry.type
    @strawberry.type
    class Query:
    class Query:
    """Base query type that all other query types will extend."""

    @strawberry.field
    def health(self, info: Info) -> HealthCheckResult:
    """
    """
    Get API health status.
    Get API health status.


    Args:
    Args:
    info: GraphQL resolver info
    info: GraphQL resolver info


    Returns:
    Returns:
    Health check result
    Health check result
    """
    """
    # Get request context
    # Get request context
    request = info.context["request"]
    request = info.context["request"]


    # Get server instance from app state
    # Get server instance from app state
    server = getattr(request.app.state, "api_server", None)
    server = getattr(request.app.state, "api_server", None)


    # Get uptime
    # Get uptime
    uptime = 0
    uptime = 0
    if server:
    if server:
    uptime = server.get_uptime()
    uptime = server.get_uptime()


    # Return health check result
    # Return health check result
    return HealthCheckResult(
    return HealthCheckResult(
    status="ok",
    status="ok",
    version=getattr(request.app, "version", "unknown"),
    version=getattr(request.app, "version", "unknown"),
    timestamp=datetime.datetime.now().isoformat(),
    timestamp=datetime.datetime.now().isoformat(),
    uptime_seconds=uptime,
    uptime_seconds=uptime,
    )
    )


    @strawberry.type
    @strawberry.type
    class Mutation:
    class Mutation:
    """Base mutation type that all other mutation types will extend."""

    @strawberry.field
    def ping(self) -> str:
    """
    """
    Simple ping mutation for testing.
    Simple ping mutation for testing.


    Returns:
    Returns:
    Pong response
    Pong response
    """
    """
    return "pong"
    return "pong"