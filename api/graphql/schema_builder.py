"""
GraphQL schema builder.

This module constructs the complete GraphQL schema by merging
all the type definitions and resolvers from different modules.
"""

import logging
from typing import Any, Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    import strawberry
    from strawberry.fastapi import GraphQLRouter
    from strawberry.schema.config import StrawberryConfig

    STRAWBERRY_AVAILABLE = True
except ImportError:
    logger.warning("Strawberry GraphQL is required for GraphQL API")
    STRAWBERRY_AVAILABLE = False

# Import resolvers
if STRAWBERRY_AVAILABLE:
    from .resolvers import (
        AgentTeamMutation,
        AgentTeamQuery,
        AIModelsMutation,
        AIModelsQuery,
        MarketingMutation,
        MarketingQuery,
        MonetizationMutation,
        MonetizationQuery,
        Mutation,
        NicheAnalysisMutation,
        NicheAnalysisQuery,
        Query,
        UserMutation,
        UserQuery,
    )


def build_schema():
    """
    Build the complete GraphQL schema.

    This function combines all query and mutation types from the different
    modules into a single unified GraphQL schema.

    Returns:
        Strawberry schema object
    """
    if not STRAWBERRY_AVAILABLE:
        logger.error("Cannot build schema: Strawberry GraphQL is not installed")
        return None

    # Create root query type by combining all module queries
    @strawberry.type
    class RootQuery(
        Query,
        NicheAnalysisQuery,
        MonetizationQuery,
        MarketingQuery,
        AIModelsQuery,
        AgentTeamQuery,
        UserQuery,
    ):
        pass

    # Create root mutation type by combining all module mutations
    @strawberry.type
    class RootMutation(
        Mutation,
        NicheAnalysisMutation,
        MonetizationMutation,
        MarketingMutation,
        AIModelsMutation,
        AgentTeamMutation,
        UserMutation,
    ):
        pass

    # Create schema
    schema = strawberry.Schema(
        query=RootQuery,
        mutation=RootMutation,
        config=StrawberryConfig(auto_camel_case=True),  
            # Convert snake_case to camelCase
    )

    return schema


def create_graphql_router(path: str = " / graphql", graphiql: bool = True):
    """
    Create a GraphQL router for FastAPI.

    Args:
        path: GraphQL endpoint path
        graphiql: Whether to enable GraphiQL interface

    Returns:
        GraphQL router
    """
    if not STRAWBERRY_AVAILABLE:
        logger.error(
            "Cannot create GraphQL router: Strawberry GraphQL is not installed")
        return None

    # Build schema
    schema = build_schema()
    if not schema:
        return None

    # Create context getter
    from .context import get_context

    # Create router
    router = GraphQLRouter(schema=schema, graphiql=graphiql, path=path, 
        context_getter=get_context)

    return router
