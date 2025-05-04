"""
"""
Interfaces for the pAIssive Income project.
Interfaces for the pAIssive Income project.


This module provides interfaces for key components to enable dependency injection
This module provides interfaces for key components to enable dependency injection
and improve testability and maintainability.
and improve testability and maintainability.
"""
"""


# Import agent interfaces
# Import agent interfaces
from .agent_interfaces import (IAgentTeam, IDeveloperAgent, IFeedbackAgent,
from .agent_interfaces import (IAgentTeam, IDeveloperAgent, IFeedbackAgent,
IMarketingAgent, IMonetizationAgent,
IMarketingAgent, IMonetizationAgent,
IResearchAgent)
IResearchAgent)
from .marketing_interfaces import (IContentTemplate, IMarketingStrategy,
from .marketing_interfaces import (IContentTemplate, IMarketingStrategy,
IPersonaCreator)
IPersonaCreator)
# Import marketing interfaces
# Import marketing interfaces
# Import model interfaces
# Import model interfaces
from .model_interfaces import (ICacheManager, IModelAdapter, IModelConfig,
from .model_interfaces import (ICacheManager, IModelAdapter, IModelConfig,
IModelInfo, IModelManager, IPerformanceMonitor)
IModelInfo, IModelManager, IPerformanceMonitor)
# Import monetization interfaces
# Import monetization interfaces
from .monetization_interfaces import (IPricingCalculator, IRevenueProjector,
from .monetization_interfaces import (IPricingCalculator, IRevenueProjector,
ISubscriptionManager, ISubscriptionModel,
ISubscriptionManager, ISubscriptionModel,
SubscriptionStatus, TransactionStatus,
SubscriptionStatus, TransactionStatus,
TransactionType)
TransactionType)
from .niche_interfaces import (IMarketAnalyzer, IOpportunityScorer,
from .niche_interfaces import (IMarketAnalyzer, IOpportunityScorer,
IProblemIdentifier)
IProblemIdentifier)
# Import niche analysis interfaces
# Import niche analysis interfaces
# Import UI interfaces
# Import UI interfaces
from .ui_interfaces import (IAgentTeamService, IBaseService, IDeveloperService,
from .ui_interfaces import (IAgentTeamService, IBaseService, IDeveloperService,
IMarketingService, IMonetizationService,
IMarketingService, IMonetizationService,
INicheAnalysisService)
INicheAnalysisService)


__all__ = [
__all__ = [
# Agent interfaces
# Agent interfaces
"IAgentTeam",
"IAgentTeam",
"IResearchAgent",
"IResearchAgent",
"IDeveloperAgent",
"IDeveloperAgent",
"IMonetizationAgent",
"IMonetizationAgent",
"IMarketingAgent",
"IMarketingAgent",
"IFeedbackAgent",
"IFeedbackAgent",
# Model interfaces
# Model interfaces
"IModelConfig",
"IModelConfig",
"IModelInfo",
"IModelInfo",
"IModelManager",
"IModelManager",
"IModelAdapter",
"IModelAdapter",
"ICacheManager",
"ICacheManager",
"IPerformanceMonitor",
"IPerformanceMonitor",
# Niche analysis interfaces
# Niche analysis interfaces
"IMarketAnalyzer",
"IMarketAnalyzer",
"IProblemIdentifier",
"IProblemIdentifier",
"IOpportunityScorer",
"IOpportunityScorer",
# Monetization interfaces
# Monetization interfaces
"ISubscriptionModel",
"ISubscriptionModel",
"IPricingCalculator",
"IPricingCalculator",
"IRevenueProjector",
"IRevenueProjector",
"ISubscriptionManager",
"ISubscriptionManager",
"SubscriptionStatus",
"SubscriptionStatus",
"TransactionStatus",
"TransactionStatus",
"TransactionType",
"TransactionType",
# Marketing interfaces
# Marketing interfaces
"IPersonaCreator",
"IPersonaCreator",
"IMarketingStrategy",
"IMarketingStrategy",
"IContentTemplate",
"IContentTemplate",
# UI interfaces
# UI interfaces
"IBaseService",
"IBaseService",
"IAgentTeamService",
"IAgentTeamService",
"INicheAnalysisService",
"INicheAnalysisService",
"IDeveloperService",
"IDeveloperService",
"IMonetizationService",
"IMonetizationService",
"IMarketingService",
"IMarketingService",
]
]

