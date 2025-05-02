"""
Marketing module for the pAIssive Income project.

This module provides functionality for generating and managing marketing
strategies, tactics, and content for niche AI tools.
"""

from .channel_strategies import ChannelStrategy
from .content_generators import ContentGenerator
from .content_optimization import ContentOptimizer
from .content_templates import ContentTemplate
from .schemas import (
    AudienceAnalysisSchema,
    BillingPeriod,
    BudgetSchema,
    BusinessAnalysisSchema,
    BusinessSize,
    BusinessType,
    ChannelAnalysisSchema,
    ChannelType,
    ConfigSchema,
    ContentCalendarSchema,
    ContentItemSchema,
    DemographicsSchema,
    DifficultyLevel,
    MarketingPlanSchema,
    MarketingStrategyInputSchema,
    MarketingStrategyResultsSchema,
    MarketingTacticSchema,
    MetricSchema,
    PersonaSchema,
    PriorityLevel,
    TargetAudienceSchema,
    TimeframeSchema,
    TimeframeUnit,
)
from .strategy_generator import StrategyGenerator
from .style_adjuster import StyleAdjuster
from .tone_analyzer import ToneAnalyzer
from .user_personas import PersonaCreator

__all__ = [
    "StrategyGenerator",
    "ChannelStrategy",
    "ContentGenerator",
    "ContentOptimizer",
    "ContentTemplate",
    "StyleAdjuster",
    "ToneAnalyzer",
    "PersonaCreator",
    # Schema exports
    "BusinessType",
    "BusinessSize",
    "BillingPeriod",
    "TimeframeUnit",
    "ChannelType",
    "PriorityLevel",
    "DifficultyLevel",
    "BudgetSchema",
    "TimeframeSchema",
    "DemographicsSchema",
    "TargetAudienceSchema",
    "ConfigSchema",
    "MarketingTacticSchema",
    "MarketingMetricSchema",
    "MetricSchema",
    "ContentItemSchema",
    "ContentCalendarSchema",
    "PersonaSchema",
    "ChannelAnalysisSchema",
    "MarketingChannelSchema",
    "MarketingPlanSchema",
    "MarketingStrategyInputSchema",
    "MarketingStrategyResultsSchema",
    "AudienceAnalysisSchema",
    "BusinessAnalysisSchema",
]
