"""
Marketing service for the pAIssive Income API.

This module provides a service for interacting with the marketing endpoints.
"""

from typing import Any, Dict, List, Optional

from .base import BaseService


class MarketingService(BaseService):
    """
    Marketing service.
    """

    def get_solutions(self) -> Dict[str, Any]:
        """
        Get all solutions available for marketing.

        Returns:
            List of solutions
        """
        return self._get("marketing / solutions")

    def create_marketing_strategy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a marketing strategy.

        Args:
            data: Marketing strategy data
                - solution_id: Solution ID
                - audience_ids: List of target audience IDs
                - channel_ids: List of marketing channel IDs
                - budget: Budget information
                - timeframe: Timeframe information

        Returns:
            Created marketing strategy
        """
        return self._post("marketing / strategies", data)

    def get_marketing_strategies(self) -> Dict[str, Any]:
        """
        Get all marketing strategies.

        Returns:
            List of marketing strategies
        """
        return self._get("marketing / strategies")

    def get_marketing_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """
        Get a specific marketing strategy.

        Args:
            strategy_id: Marketing strategy ID

        Returns:
            Marketing strategy details
        """
        return self._get(f"marketing / strategies/{strategy_id}")

    def update_marketing_strategy(self, strategy_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a marketing strategy.

        Args:
            strategy_id: Marketing strategy ID
            data: Updated marketing strategy data

        Returns:
            Updated marketing strategy
        """
        return self._put(f"marketing / strategies/{strategy_id}", data)

    def delete_marketing_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """
        Delete a marketing strategy.

        Args:
            strategy_id: Marketing strategy ID

        Returns:
            Result of the deletion
        """
        return self._delete(f"marketing / strategies/{strategy_id}")

    def get_user_personas(self) -> Dict[str, Any]:
        """
        Get all user personas.

        Returns:
            List of user personas
        """
        return self._get("marketing / personas")

    def create_user_persona(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a user persona.

        Args:
            data: User persona data

        Returns:
            Created user persona
        """
        return self._post("marketing / personas", data)

    def get_marketing_channels(self) -> Dict[str, Any]:
        """
        Get all marketing channels.

        Returns:
            List of marketing channels
        """
        return self._get("marketing / channels")

    def generate_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate marketing content.

        Args:
            data: Content generation data
                - strategy_id: Marketing strategy ID
                - content_type: Type of content to generate

        Returns:
            Generated content
        """
        return self._post("marketing / content", data)

    def create_content_calendar(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a content calendar.

        Args:
            data: Content calendar data
                - strategy_id: Marketing strategy ID
                - start_date: Start date
                - end_date: End date

        Returns:
            Content calendar
        """
        return self._post("marketing / content - calendars", data)
