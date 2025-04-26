"""
Niche Analysis Service for the pAIssive Income UI.

This service provides methods for interacting with the Niche Analysis module.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from .base_service import BaseService

# Set up logging
logger = logging.getLogger(__name__)

class NicheAnalysisService(BaseService):
    """
    Service for interacting with the Niche Analysis module.
    """
    
    def __init__(self):
        """Initialize the Niche Analysis service."""
        super().__init__()
        self.niches_file = 'niches.json'
        self.market_segments_file = 'market_segments.json'
        
        # Import the Niche Analysis classes
        try:
            from niche_analysis import MarketAnalyzer, ProblemIdentifier, OpportunityScorer
            self.niche_analysis_available = True
            self.market_analyzer = MarketAnalyzer()
            self.problem_identifier = ProblemIdentifier()
            self.opportunity_scorer = OpportunityScorer()
        except ImportError:
            logger.warning("Niche Analysis module not available. Using mock data.")
            self.niche_analysis_available = False
    
    def get_market_segments(self) -> List[str]:
        """
        Get all market segments.
        
        Returns:
            List of market segments
        """
        segments = self._load_data(self.market_segments_file)
        if segments is None:
            # Default market segments
            segments = [
                "e-commerce",
                "content creation",
                "freelancing",
                "education",
                "real estate",
                "healthcare",
                "finance",
                "legal",
                "marketing",
                "software development"
            ]
            self._save_data(segments, self.market_segments_file)
        return segments
    
    def add_market_segment(self, segment: str) -> List[str]:
        """
        Add a new market segment.
        
        Args:
            segment: Market segment to add
            
        Returns:
            Updated list of market segments
        """
        segments = self.get_market_segments()
        if segment not in segments:
            segments.append(segment)
            self._save_data(segments, self.market_segments_file)
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
                    opportunity = self.opportunity_scorer.score_opportunity(segment, market_data, problems)
                    
                    # Create niche data
                    niche = {
                        'id': str(uuid.uuid4()),
                        'name': segment.title(),
                        'market_segment': segment,
                        'description': f"AI tools for {segment}",
                        'opportunity_score': opportunity.get('score', 0.5),
                        'market_data': market_data,
                        'problems': problems,
                        'opportunity_analysis': opportunity,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    niches.append(niche)
            except Exception as e:
                logger.error(f"Error analyzing niches: {e}")
                niches = self._create_mock_niches(market_segments)
        else:
            niches = self._create_mock_niches(market_segments)
        
        # Sort niches by opportunity score (descending)
        niches.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        # Save the niches
        all_niches = self.get_niches()
        for niche in niches:
            all_niches.append(niche)
        self._save_data(all_niches, self.niches_file)
        
        return niches
    
    def get_niches(self) -> List[Dict[str, Any]]:
        """
        Get all niches.
        
        Returns:
            List of niches
        """
        niches = self._load_data(self.niches_file)
        if niches is None:
            niches = []
            self._save_data(niches, self.niches_file)
        return niches
    
    def get_niche(self, niche_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a niche by ID.
        
        Args:
            niche_id: ID of the niche
            
        Returns:
            Niche data, or None if not found
        """
        niches = self.get_niches()
        for niche in niches:
            if niche['id'] == niche_id:
                return niche
        return None
    
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
            "software development": 0.76
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
            "software development": "AI tools for code generation and documentation"
        }
        
        for segment in market_segments:
            # Create mock niche data
            niche = {
                'id': str(uuid.uuid4()),
                'name': segment.title(),
                'market_segment': segment,
                'description': descriptions.get(segment, f"AI tools for {segment}"),
                'opportunity_score': opportunity_scores.get(segment, 0.7),
                'market_data': {
                    'market_size': 'medium',
                    'growth_rate': 'high',
                    'competition': 'medium',
                    'entry_barriers': 'low'
                },
                'problems': [
                    {
                        'name': f"Problem 1 in {segment}",
                        'description': f"Description of problem 1 in {segment}",
                        'impact': ['impact 1', 'impact 2'],
                        'severity': 'high'
                    },
                    {
                        'name': f"Problem 2 in {segment}",
                        'description': f"Description of problem 2 in {segment}",
                        'impact': ['impact 1', 'impact 2'],
                        'severity': 'medium'
                    }
                ],
                'opportunity_analysis': {
                    'score': opportunity_scores.get(segment, 0.7),
                    'factors': {
                        'market_size': 0.8,
                        'growth_rate': 0.9,
                        'competition': 0.6,
                        'problem_severity': 0.7,
                        'solution_feasibility': 0.8,
                        'monetization_potential': 0.7
                    }
                },
                'created_at': datetime.now().isoformat(),
                'is_mock': True
            }
            
            mock_niches.append(niche)
        
        # Sort mock niches by opportunity score (descending)
        mock_niches.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return mock_niches
