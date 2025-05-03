"""
Interfaces for the Niche Analysis module.

This module provides interfaces for the niche analysis components to enable dependency injection
and improve testability and maintainability.
"""


from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IMarketAnalyzer

(ABC):
    """Interface for market analyzer."""

@abstractmethod
    def analyze_market(self, market_segment: str) -> Dict[str, Any]:
        """
        Analyze a market segment.

Args:
            market_segment: Market segment to analyze

Returns:
            Market analysis dictionary
        """
        pass

@abstractmethod
    def get_market_segments(self) -> List[str]:
        """
        Get a list of market segments.

Returns:
            List of market segments
        """
        pass

@abstractmethod
    def get_market_size(self, market_segment: str) -> Dict[str, Any]:
        """
        Get the size of a market segment.

Args:
            market_segment: Market segment to analyze

Returns:
            Market size dictionary
        """
        pass

@abstractmethod
    def get_market_trends(self, market_segment: str) -> List[Dict[str, Any]]:
        """
        Get trends for a market segment.

Args:
            market_segment: Market segment to analyze

Returns:
            List of market trend dictionaries
        """
        pass


class IProblemIdentifier(ABC):
    """Interface for problem identifier."""

@abstractmethod
    def identify_problems(self, market_segment: str) -> List[Dict[str, Any]]:
        """
        Identify problems in a market segment.

Args:
            market_segment: Market segment to analyze

Returns:
            List of problem dictionaries
        """
        pass

@abstractmethod
    def analyze_problem(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a problem.

Args:
            problem: Problem dictionary

Returns:
            Problem analysis dictionary
        """
        pass

@abstractmethod
    def get_problem_categories(self) -> List[str]:
        """
        Get a list of problem categories.

Returns:
            List of problem categories
        """
        pass


class IOpportunityScorer(ABC):
    """Interface for opportunity scorer."""

@abstractmethod
    def score_opportunity(
        self,
        market_segment: str,
        market_data: Dict[str, Any],
        problems: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Score an opportunity.

Args:
            market_segment: Market segment
            market_data: Market data dictionary
            problems: List of problem dictionaries

Returns:
            Opportunity score dictionary
        """
        pass

@abstractmethod
    def rank_opportunities(
        self, opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rank opportunities.

Args:
            opportunities: List of opportunity dictionaries

Returns:
            Ranked list of opportunity dictionaries
        """
        pass

@abstractmethod
    def get_scoring_factors(self) -> List[str]:
        """
        Get a list of scoring factors.

Returns:
            List of scoring factors
        """
        pass


class INicheAnalyzer(ABC):
    """Interface for niche analyzer."""

@abstractmethod
    def analyze_niche(self, niche_name: str) -> Dict[str, Any]:
        """
        Analyze a niche.

Args:
            niche_name: Name of the niche to analyze

Returns:
            Niche analysis dictionary
        """
        pass

@abstractmethod
    def identify_niches(self, market_segments: List[str]) -> List[Dict[str, Any]]:
        """
        Identify niches within market segments.

Args:
            market_segments: List of market segments to analyze

Returns:
            List of niche dictionaries
        """
        pass

@abstractmethod
    def analyze_competition(self, niche_name: str) -> Dict[str, Any]:
        """
        Analyze competition in a niche.

Args:
            niche_name: Name of the niche to analyze

Returns:
            Competition analysis dictionary
        """
        pass

@abstractmethod
    def get_niche_opportunities(self, niche_name: str) -> List[Dict[str, Any]]:
        """
        Get opportunities in a niche.

Args:
            niche_name: Name of the niche to analyze

Returns:
            List of opportunity dictionaries
        """
        pass