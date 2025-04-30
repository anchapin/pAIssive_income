"""
Routes for the API server.

This module provides route handlers for the API server.
"""

# Import routers from their respective modules
from .niche_analysis_router import router as niche_analysis_router
from .monetization_router import router as monetization_router
from .marketing_router import router as marketing_router
from .ai_models_router import router as ai_models_router
from .agent_team_router import router as agent_team_router
from .user_router import router as user_router
from .dashboard_router import router as dashboard_router
from .api_key_router import router as api_key_router
from .analytics_router import router as analytics_router

__all__ = [
    'niche_analysis_router',
    'monetization_router',
    'marketing_router',
    'ai_models_router',
    'agent_team_router',
    'user_router',
    'dashboard_router',
    'api_key_router',
    'analytics_router',
]
