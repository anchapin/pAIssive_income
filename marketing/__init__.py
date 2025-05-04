"""
"""
Marketing module for the pAIssive Income project.
Marketing module for the pAIssive Income project.


This module provides functionality for generating and managing marketing
This module provides functionality for generating and managing marketing
strategies, tactics, and content for niche AI tools.
strategies, tactics, and content for niche AI tools.
"""
"""




from .ab_testing import ABTest, ABTesting
from .ab_testing import ABTest, ABTesting
from .channel_strategies import ChannelStrategy
from .channel_strategies import ChannelStrategy
from .content_generator_impl import ConcreteContentGenerator
from .content_generator_impl import ConcreteContentGenerator
from .content_generators import ContentGenerator
from .content_generators import ContentGenerator
from .content_optimization import (KeywordAnalyzer, ReadabilityAnalyzer,
from .content_optimization import (KeywordAnalyzer, ReadabilityAnalyzer,
SEOAnalyzer)
SEOAnalyzer)
from .content_performance import ContentPerformanceAnalyzer
from .content_performance import ContentPerformanceAnalyzer
from .content_templates import ContentTemplate
from .content_templates import ContentTemplate
from .marketing_plan import MarketingPlan
from .marketing_plan import MarketingPlan
from .social_media_integration import SocialMediaIntegration
from .social_media_integration import SocialMediaIntegration
from .strategy_generator import StrategyGenerator
from .strategy_generator import StrategyGenerator
from .style_adjuster import StyleAdjuster
from .style_adjuster import StyleAdjuster
from .tone_analyzer import ToneAnalyzer
from .tone_analyzer import ToneAnalyzer
from .user_personas import PersonaCreator
from .user_personas import PersonaCreator


__all__
__all__


(
(
ContentMarketingStrategyGenerator,
ContentMarketingStrategyGenerator,
DefaultStrategyGenerator,
DefaultStrategyGenerator,
EmailMarketingStrategyGenerator,
EmailMarketingStrategyGenerator,
SocialMediaStrategyGenerator,
SocialMediaStrategyGenerator,
)
)
(  # Social Media schemas
(  # Social Media schemas
AudienceAnalysisSchema,
AudienceAnalysisSchema,
AudienceInsightSchema,
AudienceInsightSchema,
BillingPeriod,
BillingPeriod,
BudgetSchema,
BudgetSchema,
BusinessAnalysisSchema,
BusinessAnalysisSchema,
BusinessSize,
BusinessSize,
BusinessType,
BusinessType,
ChannelAnalysisSchema,
ChannelAnalysisSchema,
ChannelType,
ChannelType,
ConfigSchema,
ConfigSchema,
ContentCalendarSchema,
ContentCalendarSchema,
ContentItemSchema,
ContentItemSchema,
ContentVisibility,
ContentVisibility,
DemographicsSchema,
DemographicsSchema,
DifficultyLevel,
DifficultyLevel,
MarketingPlanSchema,
MarketingPlanSchema,
MarketingStrategyInputSchema,
MarketingStrategyInputSchema,
MarketingStrategyResultsSchema,
MarketingStrategyResultsSchema,
MarketingTacticSchema,
MarketingTacticSchema,
MetricSchema,
MetricSchema,
PersonaSchema,
PersonaSchema,
PostScheduleType,
PostScheduleType,
PriorityLevel,
PriorityLevel,
SocialMediaAnalyticsSchema,
SocialMediaAnalyticsSchema,
SocialMediaAuthSchema,
SocialMediaAuthSchema,
SocialMediaCampaignSchema,
SocialMediaCampaignSchema,
SocialMediaConnectionSchema,
SocialMediaConnectionSchema,
SocialMediaPlatform,
SocialMediaPlatform,
SocialMediaPostSchema,
SocialMediaPostSchema,
TargetAudienceSchema,
TargetAudienceSchema,
TimeframeSchema,
TimeframeSchema,
TimeframeUnit,
TimeframeUnit,
)
)
(
(
InsufficientDataError,
InsufficientDataError,
InvalidParameterError,
InvalidParameterError,
StatisticalAnalysis,
StatisticalAnalysis,
StatisticalAnalysisError,
StatisticalAnalysisError,
)
)
= [
= [
# Strategy generators
# Strategy generators
"ChannelStrategy",
"ChannelStrategy",
"ContentMarketingStrategyGenerator",
"ContentMarketingStrategyGenerator",
"ConcreteContentGenerator",
"ConcreteContentGenerator",
"ContentGenerator",
"ContentGenerator",
"DefaultStrategyGenerator",
"DefaultStrategyGenerator",
"EmailMarketingStrategyGenerator",
"EmailMarketingStrategyGenerator",
"SocialMediaStrategyGenerator",
"SocialMediaStrategyGenerator",
"StrategyGenerator",
"StrategyGenerator",
# Content and marketing tools
# Content and marketing tools
"ABTest",
"ABTest",
"ABTesting",
"ABTesting",
"ContentPerformanceAnalyzer",
"ContentPerformanceAnalyzer",
"ContentTemplate",
"ContentTemplate",
"InsufficientDataError",
"InsufficientDataError",
"InvalidParameterError",
"InvalidParameterError",
"KeywordAnalyzer",
"KeywordAnalyzer",
"MarketingPlan",
"MarketingPlan",
"PersonaCreator",
"PersonaCreator",
"ReadabilityAnalyzer",
"ReadabilityAnalyzer",
"SEOAnalyzer",
"SEOAnalyzer",
"SocialMediaIntegration",
"SocialMediaIntegration",
"StatisticalAnalysis",
"StatisticalAnalysis",
"StatisticalAnalysisError",
"StatisticalAnalysisError",
"StyleAdjuster",
"StyleAdjuster",
"ToneAnalyzer",
"ToneAnalyzer",
# Schema exports
# Schema exports
"AudienceAnalysisSchema",
"AudienceAnalysisSchema",
"BillingPeriod",
"BillingPeriod",
"BudgetSchema",
"BudgetSchema",
"BusinessAnalysisSchema",
"BusinessAnalysisSchema",
"BusinessSize",
"BusinessSize",
"BusinessType",
"BusinessType",
"ChannelAnalysisSchema",
"ChannelAnalysisSchema",
"ChannelType",
"ChannelType",
"ConfigSchema",
"ConfigSchema",
"ContentCalendarSchema",
"ContentCalendarSchema",
"ContentItemSchema",
"ContentItemSchema",
"DemographicsSchema",
"DemographicsSchema",
"DifficultyLevel",
"DifficultyLevel",
"MarketingPlanSchema",
"MarketingPlanSchema",
"MarketingStrategyInputSchema",
"MarketingStrategyInputSchema",
"MarketingStrategyResultsSchema",
"MarketingStrategyResultsSchema",
"MarketingTacticSchema",
"MarketingTacticSchema",
"MetricSchema",
"MetricSchema",
"PersonaSchema",
"PersonaSchema",
"PriorityLevel",
"PriorityLevel",
"TargetAudienceSchema",
"TargetAudienceSchema",
"TimeframeSchema",
"TimeframeSchema",
"TimeframeUnit",
"TimeframeUnit",
# Social Media exports
# Social Media exports
"AudienceInsightSchema",
"AudienceInsightSchema",
"ContentVisibility",
"ContentVisibility",
"PostScheduleType",
"PostScheduleType",
"SocialMediaAnalyticsSchema",
"SocialMediaAnalyticsSchema",
"SocialMediaAuthSchema",
"SocialMediaAuthSchema",
"SocialMediaCampaignSchema",
"SocialMediaCampaignSchema",
"SocialMediaConnectionSchema",
"SocialMediaConnectionSchema",
"SocialMediaPlatform",
"SocialMediaPlatform",
"SocialMediaPostSchema",
"SocialMediaPostSchema",
]
]