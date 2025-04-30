"""
API route handlers.

This module provides route handlers for different API endpoints.
"""

from .niche_analysis_router import router as niche_analysis_router
from .monetization_router import router as monetization_router
from .marketing_router import router as marketing_router
from .ai_models_router import router as ai_models_router
from .agent_team_router import router as agent_team_router
from .user_router import router as user_router
from .dashboard_router import router as dashboard_router
from .webhook_router import router as webhook_router
from .analytics_router import router as analytics_router
from .developer_router import router as developer_router
from .api_key_router import router as api_key_router

__all__ = [
    'niche_analysis_router',
    'monetization_router',
    'marketing_router',
    'ai_models_router',
    'agent_team_router',
    'user_router',
    'dashboard_router',
    'webhook_router',
    'analytics_router',
    'developer_router',
    'api_key_router',
]
