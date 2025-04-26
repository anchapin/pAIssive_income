"""
Niche Analysis module for the pAIssive Income project.
This module contains tools for analyzing market segments and identifying profitable niches.
"""

from .market_analyzer import MarketAnalyzer
from .problem_identifier import ProblemIdentifier
from .opportunity_scorer import OpportunityScorer

__all__ = [
    'MarketAnalyzer',
    'ProblemIdentifier',
    'OpportunityScorer',
]
