"""
Services for the pAIssive Income API.

This module provides service classes for interacting with the API endpoints.
"""

from .agent_team import AgentTeamService
from .ai_models import AIModelsService
from .api_key import APIKeyService
from .base import BaseService
from .dashboard import DashboardService
from .marketing import MarketingService
from .monetization import MonetizationService
from .niche_analysis import NicheAnalysisService
from .user import UserService

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
