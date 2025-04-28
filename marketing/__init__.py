"""
Marketing module for the pAIssive Income project.

This module provides functionality for generating and managing marketing
strategies, tactics, and content for niche AI tools.
"""

from .strategy_generator import StrategyGenerator
from .channel_strategies import ChannelStrategy
from .content_generators import ContentGenerator
from .content_optimization import ContentOptimizer
from .content_templates import ContentTemplate
from .style_adjuster import StyleAdjuster
from .tone_analyzer import ToneAnalyzer
from .user_personas import PersonaCreator
from .marketing_plan import MarketingPlan
from .schemas import (
    BusinessType, BusinessSize, BillingPeriod, TimeframeUnit,
    ChannelType, PriorityLevel, DifficultyLevel,
    BudgetSchema, TimeframeSchema, DemographicsSchema, TargetAudienceSchema,
    ConfigSchema, MarketingTacticSchema, MetricSchema, ContentItemSchema,
    ContentCalendarSchema, PersonaSchema, ChannelAnalysisSchema,
    MarketingPlanSchema, MarketingStrategyInputSchema, MarketingStrategyResultsSchema,
    AudienceAnalysisSchema, BusinessAnalysisSchema
)

__all__ = [
    'StrategyGenerator',
    'ChannelStrategy',
    'ContentGenerator',
    'ContentOptimizer',
    'ContentTemplate',
    'StyleAdjuster',
    'ToneAnalyzer',
    'PersonaCreator',
    'MarketingPlan',
    # Schema exports
    'BusinessType',
    'BusinessSize',
    'BillingPeriod',
    'TimeframeUnit',
    'ChannelType',
    'PriorityLevel',
    'DifficultyLevel',
    'BudgetSchema',
    'TimeframeSchema',
    'DemographicsSchema',
    'TargetAudienceSchema',
    'ConfigSchema',
    'MarketingTacticSchema',
    'MetricSchema',
    'ContentItemSchema',
    'ContentCalendarSchema',
    'PersonaSchema',
    'ChannelAnalysisSchema',
    'MarketingPlanSchema',
    'MarketingStrategyInputSchema',
    'MarketingStrategyResultsSchema',
    'AudienceAnalysisSchema',
    'BusinessAnalysisSchema'
]
