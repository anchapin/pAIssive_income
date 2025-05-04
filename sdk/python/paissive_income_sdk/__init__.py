"""
"""
pAIssive Income SDK for Python.
pAIssive Income SDK for Python.


This package provides a Python client for the pAIssive Income API.
This package provides a Python client for the pAIssive Income API.
"""
"""




from .auth import APIKeyAuth, JWTAuth
from .auth import APIKeyAuth, JWTAuth
from .client import Client
from .client import Client


__version__ = "0.1.0"
__version__ = "0.1.0"
(
(
AgentTeamService,
AgentTeamService,
AIModelsService,
AIModelsService,
APIKeyService,
APIKeyService,
DashboardService,
DashboardService,
MarketingService,
MarketingService,
MonetizationService,
MonetizationService,
NicheAnalysisService,
NicheAnalysisService,
UserService,
UserService,
)
)


__all__ = [
__all__ = [
"Client",
"Client",
"APIKeyAuth",
"APIKeyAuth",
"JWTAuth",
"JWTAuth",
"NicheAnalysisService",
"NicheAnalysisService",
"MonetizationService",
"MonetizationService",
"MarketingService",
"MarketingService",
"AIModelsService",
"AIModelsService",
"AgentTeamService",
"AgentTeamService",
"UserService",
"UserService",
"DashboardService",
"DashboardService",
"APIKeyService",
"APIKeyService",
]
]