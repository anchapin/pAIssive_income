"""
pAIssive Income SDK for Python.

This package provides a Python client for the pAIssive Income API.
"""

__version__ = "0.1.0"

from .client import Client
from .auth import APIKeyAuth, JWTAuth
from .services import (
    NicheAnalysisService,
    MonetizationService,
    MarketingService,
    AIModelsService,
    AgentTeamService,
    UserService,
    DashboardService,
    APIKeyService
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
