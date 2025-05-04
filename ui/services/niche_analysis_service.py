"""
Niche Analysis Service for the pAIssive Income UI.

This service provides methods for interacting with the Niche Analysis module.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from interfaces.ui_interfaces import INicheAnalysisService

from .base_service import BaseService

# Set up logging
logger = logging.getLogger(__name__)


class NicheAnalysisService(BaseService, INicheAnalysisService):
    """
    Service for interacting with the Niche Analysis module.
    """

    def __init__(self):
        """Initialize the Niche Analysis service."""
        super().__init__()
        self.niches_file = "niches.json"
        self.market_segments_file = "market_segments.json"

        # Import the Niche Analysis classes
        try:
            from niche_analysis import (MarketAnalyzer, OpportunityScorer,
                                       ProblemIdentifier)

            self.niche_analysis_available = True
            self.market_analyzer = MarketAnalyzer()
            self.problem_identifier = ProblemIdentifier()
            self.opportunity_scorer = OpportunityScorer()
        except ImportError:
            logger.warning("Niche Analysis module not available. Using mock data.")
            self.niche_analysis_available = False

    def get_market_segments(self) -> List[Dict[str, Any]]:
        """
        Get all market segments.

        Returns:
            List of market segment dictionaries
        """
        segments_data = self.load_data(self.market_segments_file)
        if segments_data is None:
            # Default market segments
            segment_names = [
                "e-commerce",
                "content creation",
                "freelancing",
                "education",
                "real estate",
                "healthcare",
                "finance",
                "legal",
                "marketing",
                "software development",
            ]
            segments_data = [
                {"id": str(uuid.uuid4()), "name": segment} for segment in segment_names
            ]
            self.save_data(self.market_segments_file, segments_data)
        return segments_data

    def add_market_segment(self, segment: str) -> List[Dict[str, Any]]:
        """
        Add a new market segment.

        Args:
            segment: Market segment to add

        Returns:
            Updated list of market segments
        """
        segments = self.get_market_segments()
        segment_names = [s["name"] for s in segments]
        if segment not in segment_names:
            segments.append({"id": str(uuid.uuid4()), "name": segment})
            self.save_data(self.market_segments_file, segments)
        return segments

    def analyze_niches(self, market_segments: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze niches in the given market segments.

        Args:
            market_segments: List of market segments to analyze

        Returns:
            List of niche opportunities
        """
        niches = []

        if self.niche_analysis_available:
            try:
                for segment in market_segments:
                    # Analyze market data
                    market_data = self.market_analyzer.analyze_market(segment)

                    # Identify problems
                    problems = self.problem_identifier.identify_problems(segment)

                    # Score opportunity
                    opportunity = self.opportunity_scorer.score_opportunity(
                        segment, market_data, problems
                    )

                    # Create niche data
                    niche = {
                        "id": str(uuid.uuid4()),
                        "name": segment.title(),
                        "market_segment": segment,
                        "description": f"AI tools for {segment}",
                        "opportunity_score": opportunity.get("score", 0.5),
                        "market_data": market_data,
                        "problems": problems,
                        "opportunity_analysis": opportunity,
                        "created_at": datetime.now().isoformat(),
                    }

                    niches.append(niche)
            except Exception as e:
                logger.error(f"Error analyzing niches: {e}")
                niches = self._create_mock_niches(market_segments)
        else:
            niches = self._create_mock_niches(market_segments)

        # Sort niches by opportunity score (descending)
        niches.sort(key=lambda x: x["opportunity_score"], reverse=True)

        # Save the niches
        all_niches = self.get_niches()
        for niche in niches:
            all_niches.append(niche)
        self.save_data(self.niches_file, all_niches)

        return niches

    def get_niches(self) -> List[Dict[str, Any]]:
        """
        Get all niches.

        Returns:
            List of niches
        """
        niches = self.load_data(self.niches_file)
        if niches is None:
            niches = []
            self.save_data(self.niches_file, niches)
        return niches

    def get_niche(self, niche_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a niche by ID.

        Args:
            niche_id: ID of the niche

        Returns:
            Niche dictionary, or None if not found
        """
        niches = self.get_niches()
        for niche in niches:
            if niche["id"] == niche_id:
                return niche
        return None

    def save_niche(self, niche: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a niche.

        Args:
            niche: Niche dictionary

        Returns:
            Saved niche dictionary
        """
        niches = self.get_niches()

        # Check if the niche already exists
        for i, existing_niche in enumerate(niches):
            if existing_niche["id"] == niche["id"]:
                # Update existing niche
                niches[i] = niche
                self.save_data(self.niches_file, niches)
                return niche

        # Add new niche
        niches.append(niche)
        self.save_data(self.niches_file, niches)
        return niche

    def _create_mock_niches(self, market_segments: List[str]) -> List[Dict[str, Any]]:
        """
        Create mock niches for testing.

        Args:
            market_segments: List of market segments

        Returns:
            List of mock niches
        """
        mock_niches = []

        # Mock opportunity scores for different niches
        opportunity_scores = {
            "e-commerce": 0.85,
            "content creation": 0.82,
            "freelancing": 0.78,
            "education": 0.75,
            "real estate": 0.80,
            "healthcare": 0.72,
            "finance": 0.68,
            "legal": 0.65,
            "marketing": 0.79,
            "software development": 0.76,
        }

        # Mock descriptions for different niches
        descriptions = {
            "e-commerce": "AI tools for inventory management and product descriptions",
            "content creation": "AI tools for generating and optimizing content",
            "freelancing": "AI tools for proposal writing and client management",
            "education": "AI tools for study note generation and personalized learning",
            "real estate": "AI tools for property descriptions and market analysis",
            "healthcare": "AI tools for patient management and medical transcription",
            "finance": "AI tools for financial analysis and reporting",
            "legal": "AI tools for contract analysis and legal research",
            "marketing": "AI tools for campaign planning and content creation",
            "software development": "AI tools for code generation and documentation",
        }

        for segment in market_segments:
            # Create mock niche data
            niche = {
                "id": str(uuid.uuid4()),
                "name": segment.title(),
                "market_segment": segment,
                "description": descriptions.get(segment, f"AI tools for {segment}"),
                "opportunity_score": opportunity_scores.get(segment, 0.7),
                "market_data": {
                    "market_size": "medium",
                    "growth_rate": "high",
                    "competition": "medium",
                    "entry_barriers": "low",
                },
                "problems": [
                    {
                        "name": f"Problem 1 in {segment}",
                        "description": f"Description of problem 1 in {segment}",
                        "impact": ["impact 1", "impact 2"],
                        "severity": "high",
                    },
                    {
                        "name": f"Problem 2 in {segment}",
                        "description": f"Description of problem 2 in {segment}",
                        "impact": ["impact 1", "impact 2"],
                        "severity": "medium",
                    },
                ],
                "opportunity_analysis": {
                    "score": opportunity_scores.get(segment, 0.7),
                    "factors": {
                        "market_size": 0.8,
                        "growth_rate": 0.9,
                        "competition": 0.6,
                        "problem_severity": 0.7,
                        "solution_feasibility": 0.8,
                        "monetization_potential": 0.7,
                    },
                },
                "created_at": datetime.now().isoformat(),
                "is_mock": True,
            }

            mock_niches.append(niche)

        # Sort mock niches by opportunity score (descending)
        mock_niches.sort(key=lambda x: x["opportunity_score"], reverse=True)

        return mock_niches
