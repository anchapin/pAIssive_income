"""
"""
Base GraphQL schema types.
Base GraphQL schema types.


This module provides the root Query and Mutation types that other
This module provides the root Query and Mutation types that other
module-specific types will extend.
module-specific types will extend.
"""
"""




import logging
import logging


import strawberry
import strawberry
from strawberry.types import Info
from strawberry.types import Info


STRAWBERRY_AVAILABLE
STRAWBERRY_AVAILABLE
from datetime import datetime
from datetime import datetime






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
    logger.warning("Strawberry GraphQL is required for GraphQL schema")
    logger.warning("Strawberry GraphQL is required for GraphQL schema")
    STRAWBERRY_AVAILABLE = False
    STRAWBERRY_AVAILABLE = False


    if STRAWBERRY_AVAILABLE:
    if STRAWBERRY_AVAILABLE:


    @strawberry.type
    @strawberry.type
    class HealthCheckResult:
    class HealthCheckResult:
    """Health check response for the GraphQL API"""

    status: str
    version: str
    timestamp: str
    uptime_seconds: float

    @strawberry.type
    class Query:

    @strawberry.field
    def health(self, info: Info) -> HealthCheckResult:
    """
    """
    Health check endpoint for the GraphQL API.
    Health check endpoint for the GraphQL API.


    Returns:
    Returns:
    Basic health information about the API
    Basic health information about the API
    """
    """
    # Get API server from context if available
    # Get API server from context if available
    server = getattr(info.context.get("request").app.state, "api_server", None)
    server = getattr(info.context.get("request").app.state, "api_server", None)
    uptime = server.get_uptime() if server else 0
    uptime = server.get_uptime() if server else 0


    return HealthCheckResult(
    return HealthCheckResult(
    status="ok",
    status="ok",
    version=info.context.get("request").app.version,
    version=info.context.get("request").app.version,
    timestamp=datetime.now().isoformat(),
    timestamp=datetime.now().isoformat(),
    uptime_seconds=uptime,
    uptime_seconds=uptime,
    )
    )


    @strawberry.field
    @strawberry.field
    def api_info(self) -> str:
    def api_info(self) -> str:
    """
    """
    Get basic information about the GraphQL API.
    Get basic information about the GraphQL API.


    Returns:
    Returns:
    API information string
    API information string
    """
    """
    return "pAIssive Income GraphQL API"
    return "pAIssive Income GraphQL API"


    @strawberry.type
    @strawberry.type
    class Mutation:
    class Mutation:
    """Base root Mutation type that all other mutation types will extend"""

    @strawberry.field
    def ping(self) -> str:
    """
    """
    Simple ping test for the GraphQL API.
    Simple ping test for the GraphQL API.


    Returns:
    Returns:
    Pong response
    Pong response
    """
    """
    return "pong"
    return "pong"


    else:
    else:
    # Fallbacks if Strawberry isn't available
    # Fallbacks if Strawberry isn't available
    class Query:
    class Query:
    pass
    pass


    class Mutation:
    class Mutation:
    pass
    pass


    class HealthCheckResult:
    class HealthCheckResult:
    pass
    pass