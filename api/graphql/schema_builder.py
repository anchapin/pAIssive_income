"""
GraphQL schema builder.

This module constructs the complete GraphQL schema by merging 
all the type definitions and resolvers from different modules.
"""

import logging
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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

# Import schema types
from .schemas.base import Query, Mutation
from .schemas.niche_analysis import NicheAnalysisQuery, NicheAnalysisMutation
from .schemas.monetization import MonetizationQuery, MonetizationMutation
from .schemas.marketing import MarketingQuery, MarketingMutation
from .schemas.ai_models import AIModelsQuery, AIModelsMutation
from .schemas.agent_team import AgentTeamQuery, AgentTeamMutation
from .schemas.user import UserQuery, UserMutation


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
        UserQuery
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
        UserMutation
    ):
        pass
    
    # Build and return the schema
    return strawberry.Schema(
        query=RootQuery, 
        mutation=RootMutation,
        config=StrawberryConfig(
            auto_camel_case=True  # Convert snake_case to camelCase
        )
    )