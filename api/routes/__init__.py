"""
Routes for the API server.

This module provides route handlers for the API server.
"""

from .niche_analysis import router as niche_analysis_router
from .monetization import router as monetization_router
# from .marketing import router as marketing_router  # Commented out as file doesn't exist yet
# from .ai_models import router as ai_models_router  # Commented out as file doesn't exist yet
# from .agent_team import router as agent_team_router  # Commented out as file doesn't exist yet
# from .user import router as user_router  # Commented out as file doesn't exist yet
# from .dashboard import router as dashboard_router  # Commented out as file doesn't exist yet
from .api_key import router as api_key_router
from .analytics import router as analytics_router

__all__ = [
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
