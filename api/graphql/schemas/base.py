"""
Base GraphQL schema types.

This module provides the root Query and Mutation types that other
module-specific types will extend.
"""

import logging
from typing import Any, Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    import strawberry
    from strawberry.types import Info

    STRAWBERRY_AVAILABLE = True
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL schema")
    STRAWBERRY_AVAILABLE = False

if STRAWBERRY_AVAILABLE:

    @strawberry.type
    class HealthCheckResult:
        """Health check response for the GraphQL API"""

        status: str
        version: str
        timestamp: str
        uptime_seconds: float

    @strawberry.type
    class Query:
        """Base root Query type that all other query types will extend"""

        @strawberry.field
        def health(self, info: Info) -> HealthCheckResult:
            """
            Health check endpoint for the GraphQL API.

            Returns:
                Basic health information about the API
            """
            import time
            from datetime import datetime

            # Get API server from context if available
            server = getattr(info.context.get("request").app.state, "api_server", None)
            uptime = server.get_uptime() if server else 0

            return HealthCheckResult(
                status="ok",
                version=info.context.get("request").app.version,
                timestamp=datetime.now().isoformat(),
                uptime_seconds=uptime,
            )

        @strawberry.field
        def api_info(self) -> str:
            """
            Get basic information about the GraphQL API.

            Returns:
                API information string
            """
            return "pAIssive Income GraphQL API"

    @strawberry.type
    class Mutation:
        """Base root Mutation type that all other mutation types will extend"""

        @strawberry.field
        def ping(self) -> str:
            """
            Simple ping test for the GraphQL API.

            Returns:
                Pong response
            """
            return "pong"

else:
    # Fallbacks if Strawberry isn't available
    class Query:
        pass

    class Mutation:
        pass

    class HealthCheckResult:
        pass
