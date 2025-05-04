"""
"""
GraphQL schema builder.
GraphQL schema builder.


This module constructs the complete GraphQL schema by merging
This module constructs the complete GraphQL schema by merging
all the type definitions and resolvers from different modules.
all the type definitions and resolvers from different modules.
"""
"""




import logging
import logging


import strawberry
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig
from strawberry.schema.config import StrawberryConfig


STRAWBERRY_AVAILABLE
STRAWBERRY_AVAILABLE
from .context import get_context
from .context import get_context






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
    logger.warning("Strawberry GraphQL is required for GraphQL API")
    logger.warning("Strawberry GraphQL is required for GraphQL API")
    STRAWBERRY_AVAILABLE = False
    STRAWBERRY_AVAILABLE = False


    # Import resolvers
    # Import resolvers
    if STRAWBERRY_AVAILABLE:
    if STRAWBERRY_AVAILABLE:
    from .resolvers import (AgentTeamMutation, AgentTeamQuery,
    from .resolvers import (AgentTeamMutation, AgentTeamQuery,
    AIModelsMutation, AIModelsQuery, MarketingMutation,
    AIModelsMutation, AIModelsQuery, MarketingMutation,
    MarketingQuery, MonetizationMutation,
    MarketingQuery, MonetizationMutation,
    MonetizationQuery, Mutation, NicheAnalysisMutation,
    MonetizationQuery, Mutation, NicheAnalysisMutation,
    NicheAnalysisQuery, Query, UserMutation, UserQuery)
    NicheAnalysisQuery, Query, UserMutation, UserQuery)




    def build_schema():
    def build_schema():
    """
    """
    Build the complete GraphQL schema.
    Build the complete GraphQL schema.


    This function combines all query and mutation types from the different
    This function combines all query and mutation types from the different
    modules into a single unified GraphQL schema.
    modules into a single unified GraphQL schema.


    Returns:
    Returns:
    Strawberry schema object
    Strawberry schema object
    """
    """
    if not STRAWBERRY_AVAILABLE:
    if not STRAWBERRY_AVAILABLE:
    logger.error("Cannot build schema: Strawberry GraphQL is not installed")
    logger.error("Cannot build schema: Strawberry GraphQL is not installed")
    return None
    return None


    # Create root query type by combining all module queries
    # Create root query type by combining all module queries
    @strawberry.type
    @strawberry.type
    class RootQuery(
    class RootQuery(
    Query,
    Query,
    NicheAnalysisQuery,
    NicheAnalysisQuery,
    MonetizationQuery,
    MonetizationQuery,
    MarketingQuery,
    MarketingQuery,
    AIModelsQuery,
    AIModelsQuery,
    AgentTeamQuery,
    AgentTeamQuery,
    UserQuery,
    UserQuery,
    ):
    ):
    pass
    pass


    # Create root mutation type by combining all module mutations
    # Create root mutation type by combining all module mutations
    @strawberry.type
    @strawberry.type
    class RootMutation(
    class RootMutation(
    Mutation,
    Mutation,
    NicheAnalysisMutation,
    NicheAnalysisMutation,
    MonetizationMutation,
    MonetizationMutation,
    MarketingMutation,
    MarketingMutation,
    AIModelsMutation,
    AIModelsMutation,
    AgentTeamMutation,
    AgentTeamMutation,
    UserMutation,
    UserMutation,
    ):
    ):
    pass
    pass


    # Create schema
    # Create schema
    schema = strawberry.Schema(
    schema = strawberry.Schema(
    query=RootQuery,
    query=RootQuery,
    mutation=RootMutation,
    mutation=RootMutation,
    config=StrawberryConfig(
    config=StrawberryConfig(
    auto_camel_case=True  # Convert snake_case to camelCase
    auto_camel_case=True  # Convert snake_case to camelCase
    ),
    ),
    )
    )


    return schema
    return schema




    def create_graphql_router(path: str = "/graphql", graphiql: bool = True):
    def create_graphql_router(path: str = "/graphql", graphiql: bool = True):
    """
    """
    Create a GraphQL router for FastAPI.
    Create a GraphQL router for FastAPI.


    Args:
    Args:
    path: GraphQL endpoint path
    path: GraphQL endpoint path
    graphiql: Whether to enable GraphiQL interface
    graphiql: Whether to enable GraphiQL interface


    Returns:
    Returns:
    GraphQL router
    GraphQL router
    """
    """
    if not STRAWBERRY_AVAILABLE:
    if not STRAWBERRY_AVAILABLE:
    logger.error(
    logger.error(
    "Cannot create GraphQL router: Strawberry GraphQL is not installed"
    "Cannot create GraphQL router: Strawberry GraphQL is not installed"
    )
    )
    return None
    return None


    # Build schema
    # Build schema
    schema = build_schema()
    schema = build_schema()
    if not schema:
    if not schema:
    return None
    return None


    # Create context getter
    # Create context getter
    # Create router
    # Create router
    router = GraphQLRouter(
    router = GraphQLRouter(
    schema=schema, graphiql=graphiql, path=path, context_getter=get_context
    schema=schema, graphiql=graphiql, path=path, context_getter=get_context
    )
    )


    return router
    return router