"""Monetization service module."""

import logging
from typing import Any, Dict, List, Optional

from interfaces.monetization_interfaces import IMonetizationCalculator

logger = logging.getLogger(__name__)


class MonetizationService:
    """Service for managing monetization strategies."""

    def __init__(self, calculator: Optional[IMonetizationCalculator] = None) -> None:
        """Initialize the service."""
        self.calculator = calculator

    def create_strategy(
        self, solution_data: Dict[str, Any], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a monetization strategy.

        Args:
            solution_data: Solution data
            options: Strategy options

        Returns:
            Monetization strategy dictionary

        Raises:
            ValueError: If no calculator is set
        """
        if self.calculator is None:
            raise ValueError("No monetization calculator set")
        return self.calculator.calculate_strategy(solution_data, options)

    def get_pricing_tiers(self, strategy_id: str) -> List[Dict[str, Any]]:
        """
        Get pricing tiers for a strategy.

        Args:
            strategy_id: Strategy ID

        Returns:
            List of pricing tier dictionaries

        Raises:
            ValueError: If no calculator is set
        """
        if self.calculator is None:
            raise ValueError("No monetization calculator set")
        return self.calculator.get_pricing_tiers(strategy_id)

    def get_revenue_projections(self, strategy_id: str) -> Dict[str, Any]:
        """
        Get revenue projections for a strategy.

        Args:
            strategy_id: Strategy ID

        Returns:
            Revenue projections dictionary

        Raises:
            ValueError: If no calculator is set
        """
        if self.calculator is None:
            raise ValueError("No monetization calculator set")
        return self.calculator.get_revenue_projections(strategy_id)
