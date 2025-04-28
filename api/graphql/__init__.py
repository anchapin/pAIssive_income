"""
GraphQL API for the pAIssive Income project.

This module provides a GraphQL API alongside the REST API to allow for
more flexible and efficient data querying.
"""

from typing import Dict, Any, List, Optional

# Import your schema and resolver modules
from .schema_builder import build_schema
from .context import get_context