"""
Usage-based pricing for the pAIssive Income project.

This module provides classes for implementing usage-based pricing models,
where customers are charged based on their actual usage of a service.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid

from .billing_calculator import (
    PricingRule,
    BillingCalculator,
)
from .usage_tracking import UsageMetric, UsageCategory
from .usage_tracker import UsageTracker


class UsageBasedPricing:
    """
    Class for implementing usage-based pricing models.

    This class provides methods for creating and managing usage-based pricing models,
    where customers are charged based on their actual usage of a service.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        billing_calculator: Optional[BillingCalculator] = None,
        usage_tracker: Optional[UsageTracker] = None,
    ):
        """
        Initialize a usage-based pricing model.

        Args:
            name: Name of the pricing model
            description: Description of the pricing model
            billing_calculator: Billing calculator to use
            usage_tracker: Usage tracker to use
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.billing_calculator = billing_calculator or BillingCalculator()
        self.usage_tracker = usage_tracker or UsageTracker()
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def add_per_unit_pricing(
        self,
        metric: str,
        price_per_unit: float,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
    ) -> PricingRule:
        """
        Add a per-unit pricing rule to the model.

        Args:
            metric: Type of usage metric
            price_per_unit: Price per unit
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost

        Returns:
            The created pricing rule
        """
        return self.billing_calculator.create_per_unit_pricing_rule(
            metric=metric,
            price_per_unit=price_per_unit,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
        )

    def add_tiered_pricing(
        self,
        metric: str,
        tiers: List[Dict[str, Any]],
        graduated: bool = False,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
    ) -> PricingRule:
        """
        Add a tiered pricing rule to the model.

        Args:
            metric: Type of usage metric
            tiers: List of tier dictionaries
            graduated: Whether to use graduated pricing
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost

        Returns:
            The created pricing rule
        """
        return self.billing_calculator.create_tiered_pricing_rule(
            metric=metric,
            tiers=tiers,
            graduated=graduated,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
        )

    def add_package_pricing(
        self,
        metric: str,
        quantity: float,
        price: float,
        overage_price: Optional[float] = None,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
    ) -> PricingRule:
        """
        Add a package pricing rule to the model.

        Args:
            metric: Type of usage metric
            quantity: Quantity included in the package
            price: Price for the package
            overage_price: Price per unit for usage beyond the package quantity
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost

        Returns:
            The created pricing rule
        """
        return self.billing_calculator.create_package_pricing_rule(
            metric=metric,
            quantity=quantity,
            price=price,
            overage_price=overage_price,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
        )

    def calculate_cost(
        self, customer_id: str, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """
        Calculate the cost for a customer based on their usage.

        Args:
            customer_id: ID of the customer
            start_time: Start time for the billing period
            end_time: End time for the billing period

        Returns:
            Dictionary with cost information
        """
        return self.billing_calculator.calculate_usage_cost(
            customer_id=customer_id, start_time=start_time, end_time=end_time
        )

    def get_usage_summary(
        self, customer_id: str, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """
        Get a summary of usage for a customer.

        Args:
            customer_id: ID of the customer
            start_time: Start time for the period
            end_time: End time for the period

        Returns:
            Dictionary with usage summary
        """
        return self.usage_tracker.get_usage_summary(
            customer_id=customer_id, start_time=start_time, end_time=end_time
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the usage-based pricing model to a dictionary.

        Returns:
            Dictionary representation of the model
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        billing_calculator: Optional[BillingCalculator] = None,
        usage_tracker: Optional[UsageTracker] = None,
    ) -> "UsageBasedPricing":
        """
        Create a usage-based pricing model from a dictionary.

        Args:
            data: Dictionary with model data
            billing_calculator: Billing calculator to use
            usage_tracker: Usage tracker to use

        Returns:
            UsageBasedPricing instance
        """
        model = cls(
            name=data["name"],
            description=data.get("description", ""),
            billing_calculator=billing_calculator,
            usage_tracker=usage_tracker,
        )

        model.id = data.get("id", model.id)
        model.created_at = data.get("created_at", model.created_at)
        model.updated_at = data.get("updated_at", model.updated_at)

        return model


# Example usage
if __name__ == "__main__":
    # Create a usage-based pricing model
    model = UsageBasedPricing(
        name="API Usage Pricing", description="Pricing model for API usage"
    )

    # Add pricing rules
    model.add_per_unit_pricing(
        metric=UsageMetric.API_CALL,
        price_per_unit=0.01,
        category=UsageCategory.INFERENCE,
    )

    model.add_tiered_pricing(
        metric=UsageMetric.TOKEN,
        tiers=[
            {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.001},
            {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0008},
            {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.0005},
        ],
        graduated=True,
        category=UsageCategory.INFERENCE,
    )

    model.add_package_pricing(
        metric=UsageMetric.STORAGE,
        quantity=10.0,  # GB
        price=5.0,
        overage_price=0.5,  # per GB
        category=UsageCategory.STORAGE,
    )

    # Calculate cost for a customer
    cost = model.calculate_cost(
        customer_id="customer123",
        start_time=datetime.now() - timedelta(days=30),
        end_time=datetime.now(),
    )

    print(f"Total cost: ${cost['total']:.2f}")
    print(f"Cost breakdown: {cost['breakdown']}")
