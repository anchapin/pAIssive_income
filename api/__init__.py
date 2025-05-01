"""
API module for the pAIssive Income project.

This module provides RESTful API endpoints for all core services in the project.
"""

from .server import APIServer, APIConfig
from .middleware import AuthMiddleware, RateLimitMiddleware, CORSMiddleware
from .routes import (
    niche_analysis_router,
)

__all__ = [
    "APIServer",
    "APIConfig",
    "AuthMiddleware",
    "RateLimitMiddleware",
    "CORSMiddleware",
    "niche_analysis_router",
]
