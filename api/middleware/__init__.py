"""
Middleware for the API server.

This module provides middleware components for the API server.
"""

from .auth import AuthMiddleware
from .rate_limit import RateLimitMiddleware
from .cors import CORSMiddleware
from .version import VersionMiddleware
from .analytics import AnalyticsMiddleware
from .query_params import QueryParamsMiddleware, setup_query_params_middleware
from .setup import setup_middleware

__all__ = [
    "AuthMiddleware",
    "RateLimitMiddleware",
    "CORSMiddleware",
    "VersionMiddleware",
    "AnalyticsMiddleware",
    "QueryParamsMiddleware",
    "setup_query_params_middleware",
    "setup_middleware",
]
