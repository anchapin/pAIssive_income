"""
API documentation module.

This module provides documentation for the API server.
"""


from .custom_docs import setup_custom_docs
from .openapi import get_openapi_schema, setup_openapi

__all__ 

= [
    "setup_openapi",
    "get_openapi_schema",
    "setup_custom_docs",
]