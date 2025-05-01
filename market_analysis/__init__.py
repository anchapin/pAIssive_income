"""
Market Analysis module for pAIssive Income project.

This module provides tools for analyzing market trends and competitive intelligence.
"""

from .competitive_intelligence import (
    CompetitiveIntelligence,
    CompetitorMonitor,
    PricingAnalyzer,
    FeatureComparator
)

from .market_trends import (
    MarketTrendAnalyzer,
    SeasonalPatternDetector,
    TrendDataProcessor,
    MultiYearTrendComparator
)

from .errors import (
    MarketAnalysisError,
    CompetitiveIntelligenceError,
    MarketTrendError,
    InvalidDataError,
    InsufficientDataError
)

__all__ = [
    'CompetitiveIntelligence',
    'CompetitorMonitor',
    'PricingAnalyzer',
    'FeatureComparator',
    'MarketTrendAnalyzer',
    'SeasonalPatternDetector',
    'TrendDataProcessor',
    'MultiYearTrendComparator',
    'MarketAnalysisError',
    'CompetitiveIntelligenceError',
    'MarketTrendError',
    'InvalidDataError',
    'InsufficientDataError'
]
