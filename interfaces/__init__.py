""""""

"""Interfaces for the pAIssive Income project."""

"""This module provides interfaces for key components to enable dependency injection"""
"""and improve testability and maintainability."""
"""

# Import agent interfaces
from .agent_interfaces import (IAgentTeam, IDeveloperAgent, IFeedbackAgent,
IMarketingAgent, IMonetizationAgent,
IResearchAgent)
from .marketing_interfaces import (IContentTemplate, IMarketingStrategy,
IPersonaCreator
# Import marketing interfaces
# Import model interfaces
from .model_interfaces import (ICacheManager, IModelAdapter, IModelConfig,
IModelInfo, IModelManager, IPerformanceMonitor
# Import monetization interfaces
from .monetization_interfaces import (IPricingCalculator, IRevenueProjector,
ISubscriptionManager, ISubscriptionModel,
SubscriptionStatus, TransactionStatus,
TransactionType)
from .niche_interfaces import (IMarketAnalyzer, IOpportunityScorer,
IProblemIdentifier
# Import niche analysis interfaces
# Import UI interfaces
from .ui_interfaces import (IAgentTeamService, IBaseService, IDeveloperService,
IMarketingService, IMonetizationService,
INicheAnalysisService)

__all__ = []
# Agent interfaces
"IAgentTeam",
"IResearchAgent",
"IDeveloperAgent",
"IMonetizationAgent",
"IMarketingAgent",
"IFeedbackAgent",
# Model interfaces
"IModelConfig",
"IModelInfo",
"IModelManager",
"IModelAdapter",
"ICacheManager",
"IPerformanceMonitor",
# Niche analysis interfaces
"IMarketAnalyzer",
"IProblemIdentifier",
"IOpportunityScorer",
# Monetization interfaces
"ISubscriptionModel",
"IPricingCalculator",
"IRevenueProjector",
"ISubscriptionManager",
"SubscriptionStatus",
"TransactionStatus",
"TransactionType",
# Marketing interfaces
"IPersonaCreator",
"IMarketingStrategy",
"IContentTemplate",
# UI interfaces
"IBaseService",
"IAgentTeamService",
"INicheAnalysisService",
"IDeveloperService",
"IMonetizationService",
"IMarketingService",
"""
