"""
Marketing module for the pAIssive Income project.

This module provides functionality for generating and managing marketing
strategies, tactics, and content for niche AI tools.
"""


from .ab_testing import ABTest, ABTesting
from .channel_strategies import ChannelStrategy
from .content_generator_impl import ConcreteContentGenerator
from .content_generators import ContentGenerator
from .content_optimization import (KeywordAnalyzer, ReadabilityAnalyzer,
SEOAnalyzer)
from .content_performance import ContentPerformanceAnalyzer
from .content_templates import ContentTemplate
from .marketing_plan import MarketingPlan
from .social_media_integration import SocialMediaIntegration
from .strategy_generator import StrategyGenerator
from .style_adjuster import StyleAdjuster
from .tone_analyzer import ToneAnalyzer
from .user_personas import PersonaCreator

__all__

(
ContentMarketingStrategyGenerator,
DefaultStrategyGenerator,
EmailMarketingStrategyGenerator,
SocialMediaStrategyGenerator,
)
(  # Social Media schemas
AudienceAnalysisSchema,
AudienceInsightSchema,
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
ContentVisibility,
DemographicsSchema,
DifficultyLevel,
MarketingPlanSchema,
MarketingStrategyInputSchema,
MarketingStrategyResultsSchema,
MarketingTacticSchema,
MetricSchema,
PersonaSchema,
PostScheduleType,
PriorityLevel,
SocialMediaAnalyticsSchema,
SocialMediaAuthSchema,
SocialMediaCampaignSchema,
SocialMediaConnectionSchema,
SocialMediaPlatform,
SocialMediaPostSchema,
TargetAudienceSchema,
TimeframeSchema,
TimeframeUnit,
)
(
InsufficientDataError,
InvalidParameterError,
StatisticalAnalysis,
StatisticalAnalysisError,
)
= [
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