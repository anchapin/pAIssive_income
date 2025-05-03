"""
pAIssive Income SDK for Python.

This package provides a Python client for the pAIssive Income API.
"""

__version__ = "0.1.0"

from .auth import APIKeyAuth, JWTAuth
from .client import Client
from .services import (
    AgentTeamService,
    AIModelsService,
    APIKeyService,
    DashboardService,
    MarketingService,
    MonetizationService,
    NicheAnalysisService,
    UserService,
)

__all__ = [
    'Client',
    'APIKeyAuth',
    'JWTAuth',
    'NicheAnalysisService',
    'MonetizationService',
    'MarketingService',
    'AIModelsService',
    'AgentTeamService',
    'UserService',
    'DashboardService',
    'APIKeyService'
]
