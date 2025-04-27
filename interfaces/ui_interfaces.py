"""
Interfaces for the UI module.

This module provides interfaces for the UI services to enable dependency injection
and improve testability and maintainability.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


class IBaseService(ABC):
    """Interface for the base service."""

    @abstractmethod
    def load_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load data from a JSON file.

        Args:
            filename: Name of the file to load

        Returns:
            Data from the file, or None if the file doesn't exist

        Raises:
            DataError: If there's an issue loading the data
        """
        pass

    @abstractmethod
    def save_data(self, filename: str, data: Dict[str, Any]) -> bool:
        """
        Save data to a JSON file.

        Args:
            filename: Name of the file to save
            data: Data to save

        Returns:
            True if successful, False otherwise

        Raises:
            DataError: If there's an issue saving the data
        """
        pass


class IAgentTeamService(IBaseService):
    """Interface for the Agent Team service."""

    @abstractmethod
    def create_project(self, project_name: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new project with an agent team.
        
        Args:
            project_name: Name of the project
            config: Optional configuration for the agent team
            
        Returns:
            Project dictionary
        """
        pass

    @abstractmethod
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects.
        
        Returns:
            List of project dictionaries
        """
        pass

    @abstractmethod
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a project by ID.
        
        Args:
            project_id: ID of the project
            
        Returns:
            Project dictionary, or None if not found
        """
        pass

    @abstractmethod
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a project.
        
        Args:
            project_id: ID of the project
            updates: Dictionary of updates
            
        Returns:
            Updated project dictionary, or None if not found
        """
        pass

    @abstractmethod
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: ID of the project
            
        Returns:
            True if successful, False otherwise
        """
        pass


class INicheAnalysisService(IBaseService):
    """Interface for the Niche Analysis service."""

    @abstractmethod
    def get_market_segments(self) -> List[Dict[str, Any]]:
        """
        Get all market segments.
        
        Returns:
            List of market segment dictionaries
        """
        pass

    @abstractmethod
    def get_niches(self) -> List[Dict[str, Any]]:
        """
        Get all niches.
        
        Returns:
            List of niche dictionaries
        """
        pass

    @abstractmethod
    def get_niche(self, niche_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a niche by ID.
        
        Args:
            niche_id: ID of the niche
            
        Returns:
            Niche dictionary, or None if not found
        """
        pass

    @abstractmethod
    def analyze_niches(self, market_segments: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze niches in market segments.
        
        Args:
            market_segments: List of market segments to analyze
            
        Returns:
            List of niche dictionaries
        """
        pass

    @abstractmethod
    def save_niche(self, niche: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a niche.
        
        Args:
            niche: Niche dictionary
            
        Returns:
            Saved niche dictionary
        """
        pass


class IDeveloperService(IBaseService):
    """Interface for the Developer service."""

    @abstractmethod
    def get_solutions(self) -> List[Dict[str, Any]]:
        """
        Get all solutions.
        
        Returns:
            List of solution dictionaries
        """
        pass

    @abstractmethod
    def get_solution(self, solution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a solution by ID.
        
        Args:
            solution_id: ID of the solution
            
        Returns:
            Solution dictionary, or None if not found
        """
        pass

    @abstractmethod
    def create_solution(self, niche_id: str) -> Dict[str, Any]:
        """
        Create a solution for a niche.
        
        Args:
            niche_id: ID of the niche
            
        Returns:
            Solution dictionary
        """
        pass

    @abstractmethod
    def save_solution(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a solution.
        
        Args:
            solution: Solution dictionary
            
        Returns:
            Saved solution dictionary
        """
        pass


class IMonetizationService(IBaseService):
    """Interface for the Monetization service."""

    @abstractmethod
    def get_strategies(self) -> List[Dict[str, Any]]:
        """
        Get all monetization strategies.
        
        Returns:
            List of strategy dictionaries
        """
        pass

    @abstractmethod
    def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a monetization strategy by ID.
        
        Args:
            strategy_id: ID of the strategy
            
        Returns:
            Strategy dictionary, or None if not found
        """
        pass

    @abstractmethod
    def create_strategy(self, solution_id: str) -> Dict[str, Any]:
        """
        Create a monetization strategy for a solution.
        
        Args:
            solution_id: ID of the solution
            
        Returns:
            Strategy dictionary
        """
        pass

    @abstractmethod
    def save_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a monetization strategy.
        
        Args:
            strategy: Strategy dictionary
            
        Returns:
            Saved strategy dictionary
        """
        pass


class IMarketingService(IBaseService):
    """Interface for the Marketing service."""

    @abstractmethod
    def get_campaigns(self) -> List[Dict[str, Any]]:
        """
        Get all marketing campaigns.
        
        Returns:
            List of campaign dictionaries
        """
        pass

    @abstractmethod
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a marketing campaign by ID.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Campaign dictionary, or None if not found
        """
        pass

    @abstractmethod
    def create_campaign(self, solution_id: str, strategy_id: str) -> Dict[str, Any]:
        """
        Create a marketing campaign for a solution and strategy.
        
        Args:
            solution_id: ID of the solution
            strategy_id: ID of the monetization strategy
            
        Returns:
            Campaign dictionary
        """
        pass

    @abstractmethod
    def save_campaign(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a marketing campaign.
        
        Args:
            campaign: Campaign dictionary
            
        Returns:
            Saved campaign dictionary
        """
        pass
