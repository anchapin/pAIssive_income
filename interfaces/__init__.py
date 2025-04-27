"""
Interfaces for the pAIssive Income project.

This module provides interfaces for key components to enable dependency injection
and improve testability and maintainability.
"""

# Import agent interfaces
from .agent_interfaces import (
    IAgentTeam, IResearchAgent, IDeveloperAgent,
    IMonetizationAgent, IMarketingAgent, IFeedbackAgent
)

# Import model interfaces
from .model_interfaces import (
    IModelConfig, IModelInfo, IModelManager,
    IModelAdapter, ICacheManager, IPerformanceMonitor
)

# Import niche analysis interfaces
from .niche_interfaces import (
    IMarketAnalyzer, IProblemIdentifier, IOpportunityScorer
)

# Import monetization interfaces
from .monetization_interfaces import (
    ISubscriptionModel, IPricingCalculator, IRevenueProjector,
    ISubscriptionManager, SubscriptionStatus, TransactionStatus, TransactionType
)

# Import marketing interfaces
from .marketing_interfaces import (
    IPersonaCreator, IMarketingStrategy, IContentTemplate
)

__all__ = [
    # Agent interfaces
    'IAgentTeam',
    'IResearchAgent',
    'IDeveloperAgent',
    'IMonetizationAgent',
    'IMarketingAgent',
    'IFeedbackAgent',

    # Model interfaces
    'IModelConfig',
    'IModelInfo',
    'IModelManager',
    'IModelAdapter',
    'ICacheManager',
    'IPerformanceMonitor',

    # Niche analysis interfaces
    'IMarketAnalyzer',
    'IProblemIdentifier',
    'IOpportunityScorer',

    # Monetization interfaces
    'ISubscriptionModel',
    'IPricingCalculator',
    'IRevenueProjector',
    'ISubscriptionManager',
    'SubscriptionStatus',
    'TransactionStatus',
    'TransactionType',

    # Marketing interfaces
    'IPersonaCreator',
    'IMarketingStrategy',
    'IContentTemplate',
]
