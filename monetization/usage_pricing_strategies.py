"""
Usage-based pricing strategies for the pAIssive Income project.

This module provides specialized classes for implementing different
usage-based pricing strategies, such as pay-as-you-go, tiered usage,
and consumption-based pricing.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from .billing_calculator import (
    PricingRule,
    BillingCalculator,
)
from .usage_tracking import UsageMetric, UsageCategory
from .usage_tracker import UsageTracker
from .usage_based_pricing import UsageBasedPricing


class PayAsYouGoPricing(UsageBasedPricing):
    """
    Pay-as-you-go pricing model.

    This model charges customers based on their actual usage with a simple
    per-unit pricing structure. There are no upfront commitments or minimum fees.
    """

    def __init__(
        self,
        name: str = "Pay-As-You-Go Pricing",
        description: str = "Simple usage-based pricing with no commitments",
        billing_calculator: Optional[BillingCalculator] = None,
        usage_tracker: Optional[UsageTracker] = None,
    ):
        """
        Initialize a pay-as-you-go pricing model.

        Args:
            name: Name of the pricing model
            description: Description of the pricing model
            billing_calculator: Billing calculator to use
            usage_tracker: Usage tracker to use
        """
        super().__init__(
            name=name,
            description=description,
            billing_calculator=billing_calculator,
            usage_tracker=usage_tracker,
        )

    def add_metric_pricing(
        self,
        metric: str,
        price_per_unit: float,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> PricingRule:
        """
        Add pricing for a specific metric.

        Args:
            metric: Type of usage metric
            price_per_unit: Price per unit
            category: Category of usage
            resource_type: Type of resource

        Returns:
            The created pricing rule
        """
        return self.add_per_unit_pricing(
            metric=metric,
            price_per_unit=price_per_unit,
            category=category,
            resource_type=resource_type,
        )


class TieredUsagePricing(UsageBasedPricing):
    """
    Tiered usage pricing model.

    This model uses tiered pricing based on usage volume, where the price per unit
    decreases as usage increases. It can use either standard tiered pricing or
    graduated pricing.
    """

    def __init__(
        self,
        name: str = "Tiered Usage Pricing",
        description: str = "Volume-based pricing with tiered discounts",
        graduated: bool = True,
        billing_calculator: Optional[BillingCalculator] = None,
        usage_tracker: Optional[UsageTracker] = None,
    ):
        """
        Initialize a tiered usage pricing model.

        Args:
            name: Name of the pricing model
            description: Description of the pricing model
            graduated: Whether to use graduated pricing
            billing_calculator: Billing calculator to use
            usage_tracker: Usage tracker to use
        """
        super().__init__(
            name=name,
            description=description,
            billing_calculator=billing_calculator,
            usage_tracker=usage_tracker,
        )
        self.graduated = graduated

    def add_metric_pricing(
        self,
        metric: str,
        tiers: List[Dict[str, Any]],
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> PricingRule:
        """
        Add tiered pricing for a specific metric.

        Args:
            metric: Type of usage metric
            tiers: List of tier dictionaries
            category: Category of usage
            resource_type: Type of resource

        Returns:
            The created pricing rule
        """
        return self.add_tiered_pricing(
            metric=metric,
            tiers=tiers,
            graduated=self.graduated,
            category=category,
            resource_type=resource_type,
        )


class ConsumptionBasedPricing(UsageBasedPricing):
    """
    Consumption-based pricing model.

    This model charges customers based on their resource consumption,
    such as compute time, storage, or bandwidth. It's commonly used for
    cloud services and infrastructure.
    """

    def __init__(
        self,
        name: str = "Consumption-Based Pricing",
        description: str = "Pricing based on resource consumption",
        billing_calculator: Optional[BillingCalculator] = None,
        usage_tracker: Optional[UsageTracker] = None,
    ):
        """
        Initialize a consumption-based pricing model.

        Args:
            name: Name of the pricing model
            description: Description of the pricing model
            billing_calculator: Billing calculator to use
            usage_tracker: Usage tracker to use
        """
        super().__init__(
            name=name,
            description=description,
            billing_calculator=billing_calculator,
            usage_tracker=usage_tracker,
        )

    def add_compute_pricing(
        self, price_per_hour: float, resource_type: Optional[str] = None
    ) -> PricingRule:
        """
        Add pricing for compute resources.

        Args:
            price_per_hour: Price per hour of compute time
            resource_type: Type of compute resource

        Returns:
            The created pricing rule
        """
        return self.add_per_unit_pricing(
            metric=UsageMetric.COMPUTE_TIME,
            price_per_unit=price_per_hour,
            category=UsageCategory.COMPUTE,
            resource_type=resource_type,
        )

    def add_storage_pricing(
        self, price_per_gb: float, resource_type: Optional[str] = None
    ) -> PricingRule:
        """
        Add pricing for storage resources.

        Args:
            price_per_gb: Price per GB of storage
            resource_type: Type of storage resource

        Returns:
            The created pricing rule
        """
        return self.add_per_unit_pricing(
            metric=UsageMetric.STORAGE,
            price_per_unit=price_per_gb,
            category=UsageCategory.STORAGE,
            resource_type=resource_type,
        )

    def add_bandwidth_pricing(
        self, price_per_gb: float, resource_type: Optional[str] = None
    ) -> PricingRule:
        """
        Add pricing for bandwidth usage.

        Args:
            price_per_gb: Price per GB of bandwidth
            resource_type: Type of bandwidth resource

        Returns:
            The created pricing rule
        """
        return self.add_per_unit_pricing(
            metric=UsageMetric.BANDWIDTH,
            price_per_unit=price_per_gb,
            category=UsageCategory.NETWORK,
            resource_type=resource_type,
        )


class HybridUsagePricing(UsageBasedPricing):
    """
    Hybrid usage pricing model.

    This model combines a base subscription fee with usage-based pricing
    for consumption beyond what's included in the base subscription.
    """

    def __init__(
        self,
        name: str = "Hybrid Usage Pricing",
        description: str = "Base subscription plus usage-based pricing",
        base_fee: float = 0.0,
        billing_calculator: Optional[BillingCalculator] = None,
        usage_tracker: Optional[UsageTracker] = None,
    ):
        """
        Initialize a hybrid usage pricing model.

        Args:
            name: Name of the pricing model
            description: Description of the pricing model
            base_fee: Base subscription fee
            billing_calculator: Billing calculator to use
            usage_tracker: Usage tracker to use
        """
        super().__init__(
            name=name,
            description=description,
            billing_calculator=billing_calculator,
            usage_tracker=usage_tracker,
        )
        self.base_fee = base_fee

        # Add the base fee as a flat rate pricing rule
        self.billing_calculator.create_flat_rate_pricing_rule(
            metric="subscription", flat_fee=base_fee
        )

    def add_included_usage(
        self,
        metric: str,
        quantity: float,
        overage_price: float,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> PricingRule:
        """
        Add included usage with overage pricing.

        Args:
            metric: Type of usage metric
            quantity: Quantity included in the base subscription
            overage_price: Price per unit for usage beyond the included quantity
            category: Category of usage
            resource_type: Type of resource

        Returns:
            The created pricing rule
        """
        return self.add_package_pricing(
            metric=metric,
            quantity=quantity,
            price=0.0,  # Already included in the base fee
            overage_price=overage_price,
            category=category,
            resource_type=resource_type,
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
        # Calculate usage cost
        cost = super().calculate_cost(
            customer_id=customer_id, start_time=start_time, end_time=end_time
        )

        # Ensure the base fee is included
        if "subscription" not in cost["breakdown"]:
            cost["breakdown"]["subscription"] = self.base_fee
            cost["total"] += self.base_fee

        return cost


# Example usage
if __name__ == "__main__":
    # Create a pay-as-you-go pricing model
    payg_model = PayAsYouGoPricing()

    # Add pricing for API calls
    payg_model.add_metric_pricing(
        metric=UsageMetric.API_CALL,
        price_per_unit=0.01,
        category=UsageCategory.INFERENCE,
    )

    # Create a tiered usage pricing model
    tiered_model = TieredUsagePricing(graduated=True)

    # Add tiered pricing for tokens
    tiered_model.add_metric_pricing(
        metric=UsageMetric.TOKEN,
        tiers=[
            {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.001},
            {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0008},
            {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.0005},
        ],
        category=UsageCategory.INFERENCE,
    )

    # Create a consumption-based pricing model
    consumption_model = ConsumptionBasedPricing()

    # Add pricing for compute, storage, and bandwidth
    consumption_model.add_compute_pricing(price_per_hour=0.10, resource_type="cpu")
    consumption_model.add_storage_pricing(price_per_gb=0.05, resource_type="standard")
    consumption_model.add_bandwidth_pricing(price_per_gb=0.08, resource_type="outbound")

    # Create a hybrid usage pricing model
    hybrid_model = HybridUsagePricing(base_fee=9.99)

    # Add included usage with overage pricing
    hybrid_model.add_included_usage(
        metric=UsageMetric.API_CALL,
        quantity=1000,
        overage_price=0.005,
        category=UsageCategory.INFERENCE,
    )

    hybrid_model.add_included_usage(
        metric=UsageMetric.STORAGE,
        quantity=5.0,  # GB
        overage_price=0.10,  # per GB
        category=UsageCategory.STORAGE,
    )
