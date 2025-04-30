"""
Routes for the API server.

This module provides route handlers for the API server.
"""

from .niche_analysis import router as niche_analysis_router
from .monetization import router as monetization_router
from .marketing import router as marketing_router
from .ai_models import router as ai_models_router
from .agent_team import router as agent_team_router
from .user import router as user_router
from .dashboard import router as dashboard_router
from .api_key import router as api_key_router
from .analytics import router as analytics_router

__all__ = [
    "niche_analysis_router",
    "monetization_router",
    "marketing_router",
    "ai_models_router",
    "agent_team_router",
    "user_router",
    "dashboard_router",
    "api_key_router",
    "analytics_router",
]
