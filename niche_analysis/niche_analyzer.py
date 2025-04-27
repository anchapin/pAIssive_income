"""
Niche analyzer for the Niche Analysis module.

This module provides the NicheAnalyzer class that analyzes niches and identifies opportunities.
"""

import os
import logging
from typing import Dict, List, Any, Optional

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from interfaces.niche_interfaces import INicheAnalyzer
from interfaces.agent_interfaces import IAgentTeam
from niche_analysis.errors import NicheAnalysisError
from .schemas import (
    ProblemSchema, CompetitionAnalysisSchema, OpportunityScoreSchema
)

# Set up logging
logger = logging.getLogger(__name__)


class NicheAnalyzer(INicheAnalyzer):
    """
    Niche analyzer class.
    
    This class analyzes niches and identifies opportunities.
    """
    
    def __init__(self, agent_team: Optional[IAgentTeam] = None):
        """
        Initialize the niche analyzer.
        
        Args:
            agent_team: Optional agent team instance
        """
        self.agent_team = agent_team
        logger.debug("Created niche analyzer")
    
    def analyze_niche(self, niche_name: str) -> Dict[str, Any]:
        """
        Analyze a niche.
        
        Args:
            niche_name: Name of the niche to analyze
            
        Returns:
            Niche analysis dictionary
        """
        logger.info(f"Analyzing niche: {niche_name}")
        
        try:
            # Get the research agent from the agent team
            if not self.agent_team:
                raise NicheAnalysisError("Agent team not available")
                
            research_agent = self.agent_team.get_agent("researcher")
            if not research_agent:
                raise NicheAnalysisError("Research agent not available")
            
            # Analyze problems in the niche
            problems = research_agent.analyze_problems(niche_name)
            
            # Analyze competition
            competition = self.analyze_competition(niche_name)
            
            # Get opportunities
            opportunities = self.get_niche_opportunities(niche_name)
            
            # Create the niche analysis
            analysis = {
                "niche_name": niche_name,
                "problems": problems,
                "competition": competition,
                "opportunities": opportunities,
                "summary": f"Analysis of {niche_name} niche"
            }
            
            logger.info(f"Completed analysis of niche: {niche_name}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing niche {niche_name}: {e}")
            raise NicheAnalysisError(f"Error analyzing niche {niche_name}", original_exception=e)
    
    def identify_niches(self, market_segments: List[str]) -> List[Dict[str, Any]]:
        """
        Identify niches within market segments.
        
        Args:
            market_segments: List of market segments to analyze
            
        Returns:
            List of niche dictionaries
        """
        logger.info(f"Identifying niches in {len(market_segments)} market segments")
        
        try:
            # Get the research agent from the agent team
            if not self.agent_team:
                raise NicheAnalysisError("Agent team not available")
                
            research_agent = self.agent_team.get_agent("researcher")
            if not research_agent:
                raise NicheAnalysisError("Research agent not available")
            
            # Identify niches
            niches = research_agent.identify_niches(market_segments)
            
            logger.info(f"Identified {len(niches)} niches")
            return niches
            
        except Exception as e:
            logger.error(f"Error identifying niches: {e}")
            raise NicheAnalysisError("Error identifying niches", original_exception=e)
    
    def analyze_competition(self, niche_name: str) -> Dict[str, Any]:
        """
        Analyze competition in a niche.
        
        Args:
            niche_name: Name of the niche to analyze
            
        Returns:
            Competition analysis dictionary
        """
        logger.info(f"Analyzing competition in niche: {niche_name}")
        
        # This is a placeholder implementation
        # In a real implementation, this would analyze competitors in the niche
        competition = {
            "niche_name": niche_name,
            "competitors": [],
            "market_leaders": [],
            "market_gaps": [],
            "summary": f"Competition analysis for {niche_name} niche"
        }
        
        logger.info(f"Completed competition analysis for niche: {niche_name}")
        return competition
    
    def get_niche_opportunities(self, niche_name: str) -> List[Dict[str, Any]]:
        """
        Get opportunities in a niche.
        
        Args:
            niche_name: Name of the niche to analyze
            
        Returns:
            List of opportunity dictionaries
        """
        logger.info(f"Getting opportunities in niche: {niche_name}")
        
        # This is a placeholder implementation
        # In a real implementation, this would identify opportunities in the niche
        opportunities = [
            {
                "name": f"Opportunity 1 in {niche_name}",
                "description": "Description of opportunity 1",
                "score": 0.8,
                "difficulty": "medium"
            },
            {
                "name": f"Opportunity 2 in {niche_name}",
                "description": "Description of opportunity 2",
                "score": 0.7,
                "difficulty": "low"
            }
        ]
        
        logger.info(f"Found {len(opportunities)} opportunities in niche: {niche_name}")
        return opportunities
