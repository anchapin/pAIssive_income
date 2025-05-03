"""
UI service interfaces for the pAIssive Income project.

This module defines the interfaces for UI services, allowing the UI
to interact with the core functionality of the framework.
"""


from abc import abstractmethod
from typing import Any, Dict, List, Optional

from .health_interfaces import IHealthCheckable


class IBaseService:

    pass  # Added missing block
    """Base interface for all services."""

@abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about the service.

Returns:
            Dict[str, Any]: Information about the service.
        """
        pass


class IAgentTeamService(IBaseService):
    """Interface for agent team services."""

@abstractmethod
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects.

Returns:
            List[Dict[str, Any]]: List of projects.
        """
        pass

@abstractmethod
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a project by ID.

Args:
            project_id (str): The ID of the project.

Returns:
            Optional[Dict[str, Any]]: The project data or None if not found.
        """
        pass

@abstractmethod
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new project.

Args:
            project_data (Dict[str, Any]): The data of the project to create.

Returns:
            Dict[str, Any]: The created project data.
        """
        pass

@abstractmethod
    def update_project(
        self, project_id: str, project_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing project.

Args:
            project_id (str): The ID of the project to update.
            project_data (Dict[str, Any]): The new data for the project.

Returns:
            Optional[Dict[str, Any]]: The updated project data or None if not found.
        """
        pass

@abstractmethod
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.

Args:
            project_id (str): The ID of the project to delete.

Returns:
            bool: True if the project was deleted, False otherwise.
        """
        pass


class INicheAnalysisService(IBaseService):
    """Interface for niche analysis services."""

@abstractmethod
    def get_market_segments(self) -> List[Dict[str, Any]]:
        """
        Get all market segments.

Returns:
            List[Dict[str, Any]]: List of market segments.
        """
        pass

@abstractmethod
    def get_niches(self) -> List[Dict[str, Any]]:
        """
        Get all niches.

Returns:
            List[Dict[str, Any]]: List of niches.
        """
        pass

@abstractmethod
    def get_niche(self, niche_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a niche by ID.

Args:
            niche_id (str): The ID of the niche.

Returns:
            Optional[Dict[str, Any]]: The niche data or None if not found.
        """
        pass

@abstractmethod
    def analyze_niches(self, market_segments: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze niches in the given market segments.

Args:
            market_segments (List[str]): The market segments to analyze.

Returns:
            List[Dict[str, Any]]: List of analyzed niches.
        """
        pass

@abstractmethod
    def save_niche(self, niche: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a niche.

Args:
            niche (Dict[str, Any]): The niche data to save.

Returns:
            Dict[str, Any]: The saved niche data.
        """
        pass


class IDeveloperService(IBaseService):
    """Interface for developer services."""

@abstractmethod
    def get_solutions(self) -> List[Dict[str, Any]]:
        """
        Get all solutions.

Returns:
            List[Dict[str, Any]]: List of solutions.
        """
        pass

@abstractmethod
    def get_solution(self, solution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a solution by ID.

Args:
            solution_id (str): The ID of the solution.

Returns:
            Optional[Dict[str, Any]]: The solution data or None if not found.
        """
        pass

@abstractmethod
    def create_solution(self, niche_id: str) -> Dict[str, Any]:
        """
        Create a solution for a niche.

Args:
            niche_id (str): The ID of the niche.

Returns:
            Dict[str, Any]: The created solution data.
        """
        pass

@abstractmethod
    def save_solution(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a solution.

Args:
            solution (Dict[str, Any]): The solution data to save.

Returns:
            Dict[str, Any]: The saved solution data.
        """
        pass


class IMonetizationService(IBaseService):
    """Interface for monetization services."""

@abstractmethod
    def get_strategies(self) -> List[Dict[str, Any]]:
        """
        Get all monetization strategies.

Returns:
            List[Dict[str, Any]]: List of strategies.
        """
        pass

@abstractmethod
    def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a monetization strategy by ID.

Args:
            strategy_id (str): The ID of the strategy.

Returns:
            Optional[Dict[str, Any]]: The strategy data or None if not found.
        """
        pass

@abstractmethod
    def create_strategy(self, solution_id: str) -> Dict[str, Any]:
        """
        Create a monetization strategy for a solution.

Args:
            solution_id (str): The ID of the solution.

Returns:
            Dict[str, Any]: The created strategy data.
        """
        pass

@abstractmethod
    def save_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a monetization strategy.

Args:
            strategy (Dict[str, Any]): The strategy data to save.

Returns:
            Dict[str, Any]: The saved strategy data.
        """
        pass


class IMarketingService(IBaseService):
    """Interface for marketing services."""

@abstractmethod
    def get_campaigns(self) -> List[Dict[str, Any]]:
        """
        Get all marketing campaigns.

Returns:
            List[Dict[str, Any]]: List of marketing campaigns.
        """
        pass

@abstractmethod
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a marketing campaign by ID.

Args:
            campaign_id (str): The ID of the campaign.

Returns:
            Optional[Dict[str, Any]]: The campaign data or None if not found.
        """
        pass

@abstractmethod
    def create_campaign(self, solution_id: str, strategy_id: str) -> Dict[str, Any]:
        """
        Create a marketing campaign for a solution and strategy.

Args:
            solution_id (str): The ID of the solution.
            strategy_id (str): The ID of the monetization strategy.

Returns:
            Dict[str, Any]: The created campaign data.
        """
        pass

@abstractmethod
    def save_campaign(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a marketing campaign.

Args:
            campaign (Dict[str, Any]): The campaign data to save.

Returns:
            Dict[str, Any]: The saved campaign data.
        """
        pass