"""
Niche Analysis service for the pAIssive Income API.

This module provides a service for interacting with the niche analysis endpoints.
"""

from typing import Dict, List, Any, Optional

from .base import BaseService


class NicheAnalysisService(BaseService):
    """
    Niche Analysis service.
    """
    
    def get_market_segments(self) -> Dict[str, Any]:
        """
        Get all market segments.
        
        Returns:
            List of market segments
        """
        return self._get("niche-analysis/segments")
    
    def analyze_niches(self, segments: List[str]) -> Dict[str, Any]:
        """
        Analyze niches for the given market segments.
        
        Args:
            segments: List of market segment IDs
            
        Returns:
            Analysis results
        """
        return self._post("niche-analysis/analyze", {"segments": segments})
    
    def get_analysis_results(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get results for a specific analysis.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Analysis results
        """
        return self._get(f"niche-analysis/results/{analysis_id}")
    
    def get_all_results(self) -> Dict[str, Any]:
        """
        Get all analysis results.
        
        Returns:
            List of analysis results
        """
        return self._get("niche-analysis/results")
    
    def get_problems(self, niche_id: str) -> Dict[str, Any]:
        """
        Get problems for a specific niche.
        
        Args:
            niche_id: Niche ID
            
        Returns:
            List of problems
        """
        return self._get(f"niche-analysis/niches/{niche_id}/problems")
    
    def get_opportunities(self, niche_id: str) -> Dict[str, Any]:
        """
        Get opportunities for a specific niche.
        
        Args:
            niche_id: Niche ID
            
        Returns:
            List of opportunities
        """
        return self._get(f"niche-analysis/niches/{niche_id}/opportunities")
    
    def compare_opportunities(self, opportunity_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple opportunities.
        
        Args:
            opportunity_ids: List of opportunity IDs
            
        Returns:
            Comparison results
        """
        return self._post("niche-analysis/opportunities/compare", {"opportunity_ids": opportunity_ids})