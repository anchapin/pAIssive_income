"""
API module for the pAIssive Income project.

This module provides RESTful API endpoints for all core services in the project.
"""

from .server import APIServer, APIConfig
from .middleware import AuthMiddleware, RateLimitMiddleware, CORSMiddleware
from .routes import (
    niche_analysis_router,
    monetization_router,
    # marketing_router,  # Commented out as file doesn't exist yet
    # ai_models_router,  # Commented out as file doesn't exist yet
    # agent_team_router,  # Commented out as file doesn't exist yet
    # user_router,  # Commented out as file doesn't exist yet
    # dashboard_router,  # Commented out as file doesn't exist yet
    api_key_router,
    analytics_router
)

__all__ = [
    'APIServer',
    'APIConfig',
    'AuthMiddleware',
    'RateLimitMiddleware',
    'CORSMiddleware',
    'niche_analysis_router',
    'monetization_router',
    # 'marketing_router',
    # 'ai_models_router',
    # 'agent_team_router',
    # 'user_router',
    # 'dashboard_router',
    'api_key_router',
    'analytics_router',
]
