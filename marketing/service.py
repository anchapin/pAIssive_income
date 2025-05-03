"""Marketing service module."""

import logging
from typing import Any, Dict, List, Optional

from interfaces.marketing_interfaces import IMarketingStrategy

logger = logging.getLogger(__name__)


class MarketingService:
    """Service for managing marketing strategies."""

    def __init__(self, strategy: Optional[IMarketingStrategy] = None) -> None:
        """Initialize the service."""
        self.strategy = strategy

    def create_strategy(self, target_persona: Dict[str, Any], 
        goals: List[str]) -> Dict[str, Any]:
        """
        Create a marketing strategy.

        Args:
            target_persona: Target user persona
            goals: List of marketing goals

        Returns:
            Marketing strategy dictionary

        Raises:
            ValueError: If no strategy is set
        """
        if self.strategy is None:
            raise ValueError("No marketing strategy set")
        return self.strategy.create_strategy(target_persona, goals)

    def get_tactics(self) -> List[Dict[str, Any]]:
        """
        Get marketing tactics.

        Returns:
            List of marketing tactic dictionaries

        Raises:
            ValueError: If no strategy is set
        """
        if self.strategy is None:
            raise ValueError("No marketing strategy set")
        return self.strategy.get_tactics()

    def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get marketing metrics.

        Returns:
            List of marketing metric dictionaries

        Raises:
            ValueError: If no strategy is set
        """
        if self.strategy is None:
            raise ValueError("No marketing strategy set")
        return self.strategy.get_metrics()

    def get_full_strategy(self) -> Dict[str, Any]:
        """
        Get the full marketing strategy.

        Returns:
            Dictionary with complete strategy details

        Raises:
            ValueError: If no strategy is set
        """
        if self.strategy is None:
            raise ValueError("No marketing strategy set")
        return self.strategy.get_full_strategy()
