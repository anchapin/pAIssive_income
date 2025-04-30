"""
API documentation module.

This module provides documentation for the API server.
"""

from .openapi import setup_openapi, get_openapi_schema
from .custom_docs import setup_custom_docs

__all__ = [
    "setup_openapi",
    "get_openapi_schema",
    "setup_custom_docs",
]
