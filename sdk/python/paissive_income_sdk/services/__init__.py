"""
Services for the pAIssive Income API.

This module provides service classes for interacting with the API endpoints.
"""

from .base import BaseService
from .niche_analysis import NicheAnalysisService
from .monetization import MonetizationService
from .marketing import MarketingService
from .ai_models import AIModelsService
from .agent_team import AgentTeamService
from .user import UserService
from .dashboard import DashboardService
from .api_key import APIKeyService

__all__ = [
    "BaseService",
    "NicheAnalysisService",
    "MonetizationService",
    "MarketingService",
    "AIModelsService",
    "AgentTeamService",
    "UserService",
    "DashboardService",
    "APIKeyService",
]
