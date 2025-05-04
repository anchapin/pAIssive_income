"""
GraphQL API for the pAIssive Income project.

This module provides a GraphQL API alongside the REST API to allow for
more flexible and efficient data querying.
"""

from .context import get_context

# Import schema builder and router creation
from .schema_builder import build_schema, create_graphql_router

__all__ = ["build_schema", "create_graphql_router", "get_context"]
