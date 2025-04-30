"""
Marketing module for the pAIssive Income project.

This module provides functionality for generating and managing marketing
strategies, tactics, and content for niche AI tools.
"""

from .strategy_generator import StrategyGenerator
from .concrete_strategy_generator import (
    DefaultStrategyGenerator,
    ContentMarketingStrategyGenerator,
    SocialMediaStrategyGenerator,
    EmailMarketingStrategyGenerator,
)
from .channel_strategies import ChannelStrategy
from .content_generators import ContentGenerator
from .content_generator_impl import ConcreteContentGenerator
from .content_optimization import KeywordAnalyzer, ReadabilityAnalyzer, SEOAnalyzer
from .content_templates import ContentTemplate
from .style_adjuster import StyleAdjuster
from .tone_analyzer import ToneAnalyzer
from .user_personas import PersonaCreator
from .marketing_plan import MarketingPlan
from .ab_testing import ABTesting, ABTest
from .content_performance import ContentPerformanceAnalyzer
from .social_media_integration import SocialMediaIntegration
from .statistical_analysis import (
    StatisticalAnalysis,
    StatisticalAnalysisError,
    InsufficientDataError,
    InvalidParameterError,
)
from .schemas import (
    BusinessType,
    BusinessSize,
    BillingPeriod,
    TimeframeUnit,
    ChannelType,
    PriorityLevel,
    DifficultyLevel,
    BudgetSchema,
    TimeframeSchema,
    DemographicsSchema,
    TargetAudienceSchema,
    ConfigSchema,
    MarketingTacticSchema,
    MetricSchema,
    ContentItemSchema,
    ContentCalendarSchema,
    PersonaSchema,
    ChannelAnalysisSchema,
    MarketingPlanSchema,
    MarketingStrategyInputSchema,
    MarketingStrategyResultsSchema,
    AudienceAnalysisSchema,
    BusinessAnalysisSchema,
    # Social Media schemas
    SocialMediaPlatform,
    SocialMediaConnectionSchema,
    SocialMediaAuthSchema,
    SocialMediaPostSchema,
    SocialMediaAnalyticsSchema,
    SocialMediaCampaignSchema,
    AudienceInsightSchema,
    ContentVisibility,
    PostScheduleType,
)

__all__ = [
    # Strategy generators
    "ChannelStrategy",
    "ContentMarketingStrategyGenerator",
    "ConcreteContentGenerator",
    "ContentGenerator",
    "DefaultStrategyGenerator",
    "EmailMarketingStrategyGenerator",
    "SocialMediaStrategyGenerator",
    "StrategyGenerator",
    # Content and marketing tools
    "ABTest",
    "ABTesting",
    "ContentPerformanceAnalyzer",
    "ContentTemplate",
    "InsufficientDataError",
    "InvalidParameterError",
    "KeywordAnalyzer",
    "MarketingPlan",
    "PersonaCreator",
    "ReadabilityAnalyzer",
    "SEOAnalyzer",
    "SocialMediaIntegration",
    "StatisticalAnalysis",
    "StatisticalAnalysisError",
    "StyleAdjuster",
    "ToneAnalyzer",
    # Schema exports
    "AudienceAnalysisSchema",
    "BillingPeriod",
    "BudgetSchema",
    "BusinessAnalysisSchema",
    "BusinessSize",
    "BusinessType",
    "ChannelAnalysisSchema",
    "ChannelType",
    "ConfigSchema",
    "ContentCalendarSchema",
    "ContentItemSchema",
    "DemographicsSchema",
    "DifficultyLevel",
    "MarketingPlanSchema",
    "MarketingStrategyInputSchema",
    "MarketingStrategyResultsSchema",
    "MarketingTacticSchema",
    "MetricSchema",
    "PersonaSchema",
    "PriorityLevel",
    "TargetAudienceSchema",
    "TimeframeSchema",
    "TimeframeUnit",
    # Social Media exports
    "AudienceInsightSchema",
    "ContentVisibility",
    "PostScheduleType",
    "SocialMediaAnalyticsSchema",
    "SocialMediaAuthSchema",
    "SocialMediaCampaignSchema",
    "SocialMediaConnectionSchema",
    "SocialMediaPlatform",
    "SocialMediaPostSchema",
]
