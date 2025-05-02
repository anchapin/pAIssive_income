"""Monetization service for handling pricing and billing."""

from typing import Dict, List, Optional

from monetization import BillingCalculator
from monetization import MonetizationService as CoreMonetizationService
from monetization import PricingModel, SubscriptionModel

from .base_service import BaseService


class MonetizationService(BaseService):
    """Service for managing monetization features."""

    def __init__(self, core_service: CoreMonetizationService):
        """Initialize monetization service."""
        super().__init__()
        self._core = core_service
        self._billing_calculator = BillingCalculator()
        self._subscription_model = SubscriptionModel()

    def create_pricing_model(self, model_data: Dict) -> PricingModel:
        """
        Create a new pricing model.

        Args:
            model_data: Pricing model configuration data

        Returns:
            Created pricing model
        """
        try:
            return self._core.create_pricing_model(model_data)
        except Exception as e:
            self._handle_error(e, "Failed to create pricing model")
            raise

    def get_pricing_model(self, model_id: str) -> Optional[PricingModel]:
        """
        Get a pricing model by ID.

        Args:
            model_id: ID of pricing model to get

        Returns:
            Pricing model if found, None otherwise
        """
        try:
            return self._core.get_pricing_model(model_id)
        except Exception as e:
            self._handle_error(e, "Failed to get pricing model")
            return None

    def list_pricing_models(self) -> List[PricingModel]:
        """
        List all pricing models.

        Returns:
            List of pricing models
        """
        try:
            return self._core.list_pricing_models()
        except Exception as e:
            self._handle_error(e, "Failed to list pricing models")
            return []

    def update_pricing_model(self, model_id: str, model_data: Dict) -> Optional[PricingModel]:
        """
        Update a pricing model.

        Args:
            model_id: ID of model to update
            model_data: Updated model data

        Returns:
            Updated model if successful, None otherwise
        """
        try:
            return self._core.update_pricing_model(model_id, model_data)
        except Exception as e:
            self._handle_error(e, "Failed to update pricing model")
            return None

    def delete_pricing_model(self, model_id: str) -> bool:
        """
        Delete a pricing model.

        Args:
            model_id: ID of model to delete

        Returns:
            True if deleted, False otherwise
        """
        try:
            return self._core.delete_pricing_model(model_id)
        except Exception as e:
            self._handle_error(e, "Failed to delete pricing model")
            return False

    def calculate_price(self, model_id: str, usage_data: Dict) -> Optional[float]:
        """
        Calculate price based on usage.

        Args:
            model_id: ID of pricing model to use
            usage_data: Usage data for calculation

        Returns:
            Calculated price if successful, None otherwise
        """
        try:
            return self._billing_calculator.calculate_price(
                self._core.get_pricing_model(model_id), usage_data
            )
        except Exception as e:
            self._handle_error(e, "Failed to calculate price")
            return None
