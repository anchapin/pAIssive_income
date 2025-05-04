"""
"""
GraphQL API for the pAIssive Income project.
GraphQL API for the pAIssive Income project.


This module provides a GraphQL API alongside the REST API to allow for
This module provides a GraphQL API alongside the REST API to allow for
more flexible and efficient data querying.
more flexible and efficient data querying.
"""
"""




from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .context import get_context
from .context import get_context
from .schema_builder import build_schema, create_graphql_router
from .schema_builder import build_schema, create_graphql_router


__all__
__all__


# Import schema builder and router creation
# Import schema builder and router creation
= ["build_schema", "create_graphql_router", "get_context"]
= ["build_schema", "create_graphql_router", "get_context"]