"""
"""
Usage-based pricing strategies for the pAIssive Income project.
Usage-based pricing strategies for the pAIssive Income project.


This module provides specialized classes for implementing different
This module provides specialized classes for implementing different
usage-based pricing strategies, such as pay-as-you-go, tiered usage,
usage-based pricing strategies, such as pay-as-you-go, tiered usage,
and consumption-based pricing.
and consumption-based pricing.
"""
"""


import time
import time
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .usage_based_pricing import UsageBasedPricing
from .usage_based_pricing import UsageBasedPricing
from .usage_tracker import UsageTracker
from .usage_tracker import UsageTracker
from .usage_tracking import UsageCategory, UsageMetric
from .usage_tracking import UsageCategory, UsageMetric




class PayAsYouGoPricing
class PayAsYouGoPricing


(
(
BillingCalculator,
BillingCalculator,
PricingRule,
PricingRule,
)
)
(UsageBasedPricing):
    (UsageBasedPricing):
    """
    """
    Pay-as-you-go pricing model.
    Pay-as-you-go pricing model.


    This model charges customers based on their actual usage with a simple
    This model charges customers based on their actual usage with a simple
    per-unit pricing structure. There are no upfront commitments or minimum fees.
    per-unit pricing structure. There are no upfront commitments or minimum fees.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    name: str = "Pay-As-You-Go Pricing",
    name: str = "Pay-As-You-Go Pricing",
    description: str = "Simple usage-based pricing with no commitments",
    description: str = "Simple usage-based pricing with no commitments",
    billing_calculator: Optional[BillingCalculator] = None,
    billing_calculator: Optional[BillingCalculator] = None,
    usage_tracker: Optional[UsageTracker] = None,
    usage_tracker: Optional[UsageTracker] = None,
    ):
    ):
    """
    """
    Initialize a pay-as-you-go pricing model.
    Initialize a pay-as-you-go pricing model.


    Args:
    Args:
    name: Name of the pricing model
    name: Name of the pricing model
    description: Description of the pricing model
    description: Description of the pricing model
    billing_calculator: Billing calculator to use
    billing_calculator: Billing calculator to use
    usage_tracker: Usage tracker to use
    usage_tracker: Usage tracker to use
    """
    """
    super().__init__(
    super().__init__(
    name=name,
    name=name,
    description=description,
    description=description,
    billing_calculator=billing_calculator,
    billing_calculator=billing_calculator,
    usage_tracker=usage_tracker,
    usage_tracker=usage_tracker,
    )
    )


    def add_metric_pricing(
    def add_metric_pricing(
    self,
    self,
    metric: str,
    metric: str,
    price_per_unit: float,
    price_per_unit: float,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    ) -> PricingRule:
    ) -> PricingRule:
    """
    """
    Add pricing for a specific metric.
    Add pricing for a specific metric.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    price_per_unit: Price per unit
    price_per_unit: Price per unit
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource


    Returns:
    Returns:
    The created pricing rule
    The created pricing rule
    """
    """
    return self.add_per_unit_pricing(
    return self.add_per_unit_pricing(
    metric=metric,
    metric=metric,
    price_per_unit=price_per_unit,
    price_per_unit=price_per_unit,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    )
    )




    class TieredUsagePricing(UsageBasedPricing):
    class TieredUsagePricing(UsageBasedPricing):
    """
    """
    Tiered usage pricing model.
    Tiered usage pricing model.


    This model uses tiered pricing based on usage volume, where the price per unit
    This model uses tiered pricing based on usage volume, where the price per unit
    decreases as usage increases. It can use either standard tiered pricing or
    decreases as usage increases. It can use either standard tiered pricing or
    graduated pricing.
    graduated pricing.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    name: str = "Tiered Usage Pricing",
    name: str = "Tiered Usage Pricing",
    description: str = "Volume-based pricing with tiered discounts",
    description: str = "Volume-based pricing with tiered discounts",
    graduated: bool = True,
    graduated: bool = True,
    billing_calculator: Optional[BillingCalculator] = None,
    billing_calculator: Optional[BillingCalculator] = None,
    usage_tracker: Optional[UsageTracker] = None,
    usage_tracker: Optional[UsageTracker] = None,
    ):
    ):
    """
    """
    Initialize a tiered usage pricing model.
    Initialize a tiered usage pricing model.


    Args:
    Args:
    name: Name of the pricing model
    name: Name of the pricing model
    description: Description of the pricing model
    description: Description of the pricing model
    graduated: Whether to use graduated pricing
    graduated: Whether to use graduated pricing
    billing_calculator: Billing calculator to use
    billing_calculator: Billing calculator to use
    usage_tracker: Usage tracker to use
    usage_tracker: Usage tracker to use
    """
    """
    super().__init__(
    super().__init__(
    name=name,
    name=name,
    description=description,
    description=description,
    billing_calculator=billing_calculator,
    billing_calculator=billing_calculator,
    usage_tracker=usage_tracker,
    usage_tracker=usage_tracker,
    )
    )
    self.graduated = graduated
    self.graduated = graduated


    def add_metric_pricing(
    def add_metric_pricing(
    self,
    self,
    metric: str,
    metric: str,
    tiers: List[Dict[str, Any]],
    tiers: List[Dict[str, Any]],
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    ) -> PricingRule:
    ) -> PricingRule:
    """
    """
    Add tiered pricing for a specific metric.
    Add tiered pricing for a specific metric.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    tiers: List of tier dictionaries
    tiers: List of tier dictionaries
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource


    Returns:
    Returns:
    The created pricing rule
    The created pricing rule
    """
    """
    return self.add_tiered_pricing(
    return self.add_tiered_pricing(
    metric=metric,
    metric=metric,
    tiers=tiers,
    tiers=tiers,
    graduated=self.graduated,
    graduated=self.graduated,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    )
    )




    class ConsumptionBasedPricing(UsageBasedPricing):
    class ConsumptionBasedPricing(UsageBasedPricing):
    """
    """
    Consumption-based pricing model.
    Consumption-based pricing model.


    This model charges customers based on their resource consumption,
    This model charges customers based on their resource consumption,
    such as compute time, storage, or bandwidth. It's commonly used for
    such as compute time, storage, or bandwidth. It's commonly used for
    cloud services and infrastructure.
    cloud services and infrastructure.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    name: str = "Consumption-Based Pricing",
    name: str = "Consumption-Based Pricing",
    description: str = "Pricing based on resource consumption",
    description: str = "Pricing based on resource consumption",
    billing_calculator: Optional[BillingCalculator] = None,
    billing_calculator: Optional[BillingCalculator] = None,
    usage_tracker: Optional[UsageTracker] = None,
    usage_tracker: Optional[UsageTracker] = None,
    ):
    ):
    """
    """
    Initialize a consumption-based pricing model.
    Initialize a consumption-based pricing model.


    Args:
    Args:
    name: Name of the pricing model
    name: Name of the pricing model
    description: Description of the pricing model
    description: Description of the pricing model
    billing_calculator: Billing calculator to use
    billing_calculator: Billing calculator to use
    usage_tracker: Usage tracker to use
    usage_tracker: Usage tracker to use
    """
    """
    super().__init__(
    super().__init__(
    name=name,
    name=name,
    description=description,
    description=description,
    billing_calculator=billing_calculator,
    billing_calculator=billing_calculator,
    usage_tracker=usage_tracker,
    usage_tracker=usage_tracker,
    )
    )


    def add_compute_pricing(
    def add_compute_pricing(
    self, price_per_hour: float, resource_type: Optional[str] = None
    self, price_per_hour: float, resource_type: Optional[str] = None
    ) -> PricingRule:
    ) -> PricingRule:
    """
    """
    Add pricing for compute resources.
    Add pricing for compute resources.


    Args:
    Args:
    price_per_hour: Price per hour of compute time
    price_per_hour: Price per hour of compute time
    resource_type: Type of compute resource
    resource_type: Type of compute resource


    Returns:
    Returns:
    The created pricing rule
    The created pricing rule
    """
    """
    return self.add_per_unit_pricing(
    return self.add_per_unit_pricing(
    metric=UsageMetric.COMPUTE_TIME,
    metric=UsageMetric.COMPUTE_TIME,
    price_per_unit=price_per_hour,
    price_per_unit=price_per_hour,
    category=UsageCategory.COMPUTE,
    category=UsageCategory.COMPUTE,
    resource_type=resource_type,
    resource_type=resource_type,
    )
    )


    def add_storage_pricing(
    def add_storage_pricing(
    self, price_per_gb: float, resource_type: Optional[str] = None
    self, price_per_gb: float, resource_type: Optional[str] = None
    ) -> PricingRule:
    ) -> PricingRule:
    """
    """
    Add pricing for storage resources.
    Add pricing for storage resources.


    Args:
    Args:
    price_per_gb: Price per GB of storage
    price_per_gb: Price per GB of storage
    resource_type: Type of storage resource
    resource_type: Type of storage resource


    Returns:
    Returns:
    The created pricing rule
    The created pricing rule
    """
    """
    return self.add_per_unit_pricing(
    return self.add_per_unit_pricing(
    metric=UsageMetric.STORAGE,
    metric=UsageMetric.STORAGE,
    price_per_unit=price_per_gb,
    price_per_unit=price_per_gb,
    category=UsageCategory.STORAGE,
    category=UsageCategory.STORAGE,
    resource_type=resource_type,
    resource_type=resource_type,
    )
    )


    def add_bandwidth_pricing(
    def add_bandwidth_pricing(
    self, price_per_gb: float, resource_type: Optional[str] = None
    self, price_per_gb: float, resource_type: Optional[str] = None
    ) -> PricingRule:
    ) -> PricingRule:
    """
    """
    Add pricing for bandwidth usage.
    Add pricing for bandwidth usage.


    Args:
    Args:
    price_per_gb: Price per GB of bandwidth
    price_per_gb: Price per GB of bandwidth
    resource_type: Type of bandwidth resource
    resource_type: Type of bandwidth resource


    Returns:
    Returns:
    The created pricing rule
    The created pricing rule
    """
    """
    return self.add_per_unit_pricing(
    return self.add_per_unit_pricing(
    metric=UsageMetric.BANDWIDTH,
    metric=UsageMetric.BANDWIDTH,
    price_per_unit=price_per_gb,
    price_per_unit=price_per_gb,
    category=UsageCategory.NETWORK,
    category=UsageCategory.NETWORK,
    resource_type=resource_type,
    resource_type=resource_type,
    )
    )




    class HybridUsagePricing(UsageBasedPricing):
    class HybridUsagePricing(UsageBasedPricing):
    """
    """
    Hybrid usage pricing model.
    Hybrid usage pricing model.


    This model combines a base subscription fee with usage-based pricing
    This model combines a base subscription fee with usage-based pricing
    for consumption beyond what's included in the base subscription.
    for consumption beyond what's included in the base subscription.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    name: str = "Hybrid Usage Pricing",
    name: str = "Hybrid Usage Pricing",
    description: str = "Base subscription plus usage-based pricing",
    description: str = "Base subscription plus usage-based pricing",
    base_fee: float = 0.0,
    base_fee: float = 0.0,
    billing_calculator: Optional[BillingCalculator] = None,
    billing_calculator: Optional[BillingCalculator] = None,
    usage_tracker: Optional[UsageTracker] = None,
    usage_tracker: Optional[UsageTracker] = None,
    ):
    ):
    """
    """
    Initialize a hybrid usage pricing model.
    Initialize a hybrid usage pricing model.


    Args:
    Args:
    name: Name of the pricing model
    name: Name of the pricing model
    description: Description of the pricing model
    description: Description of the pricing model
    base_fee: Base subscription fee
    base_fee: Base subscription fee
    billing_calculator: Billing calculator to use
    billing_calculator: Billing calculator to use
    usage_tracker: Usage tracker to use
    usage_tracker: Usage tracker to use
    """
    """
    super().__init__(
    super().__init__(
    name=name,
    name=name,
    description=description,
    description=description,
    billing_calculator=billing_calculator,
    billing_calculator=billing_calculator,
    usage_tracker=usage_tracker,
    usage_tracker=usage_tracker,
    )
    )
    self.base_fee = base_fee
    self.base_fee = base_fee


    # Add the base fee as a flat rate pricing rule
    # Add the base fee as a flat rate pricing rule
    self.billing_calculator.create_flat_rate_pricing_rule(
    self.billing_calculator.create_flat_rate_pricing_rule(
    metric="subscription", flat_fee=base_fee
    metric="subscription", flat_fee=base_fee
    )
    )


    def add_included_usage(
    def add_included_usage(
    self,
    self,
    metric: str,
    metric: str,
    quantity: float,
    quantity: float,
    overage_price: float,
    overage_price: float,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    ) -> PricingRule:
    ) -> PricingRule:
    """
    """
    Add included usage with overage pricing.
    Add included usage with overage pricing.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    quantity: Quantity included in the base subscription
    quantity: Quantity included in the base subscription
    overage_price: Price per unit for usage beyond the included quantity
    overage_price: Price per unit for usage beyond the included quantity
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource


    Returns:
    Returns:
    The created pricing rule
    The created pricing rule
    """
    """
    return self.add_package_pricing(
    return self.add_package_pricing(
    metric=metric,
    metric=metric,
    quantity=quantity,
    quantity=quantity,
    price=0.0,  # Already included in the base fee
    price=0.0,  # Already included in the base fee
    overage_price=overage_price,
    overage_price=overage_price,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    )
    )


    def calculate_cost(
    def calculate_cost(
    self, customer_id: str, start_time: datetime, end_time: datetime
    self, customer_id: str, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate the cost for a customer based on their usage.
    Calculate the cost for a customer based on their usage.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    start_time: Start time for the billing period
    start_time: Start time for the billing period
    end_time: End time for the billing period
    end_time: End time for the billing period


    Returns:
    Returns:
    Dictionary with cost information
    Dictionary with cost information
    """
    """
    # Calculate usage cost
    # Calculate usage cost
    cost = super().calculate_cost(
    cost = super().calculate_cost(
    customer_id=customer_id, start_time=start_time, end_time=end_time
    customer_id=customer_id, start_time=start_time, end_time=end_time
    )
    )


    # Ensure the base fee is included
    # Ensure the base fee is included
    if "subscription" not in cost["breakdown"]:
    if "subscription" not in cost["breakdown"]:
    cost["breakdown"]["subscription"] = self.base_fee
    cost["breakdown"]["subscription"] = self.base_fee
    cost["total"] += self.base_fee
    cost["total"] += self.base_fee


    return cost
    return cost




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a pay-as-you-go pricing model
    # Create a pay-as-you-go pricing model
    payg_model = PayAsYouGoPricing()
    payg_model = PayAsYouGoPricing()


    # Add pricing for API calls
    # Add pricing for API calls
    payg_model.add_metric_pricing(
    payg_model.add_metric_pricing(
    metric=UsageMetric.API_CALL,
    metric=UsageMetric.API_CALL,
    price_per_unit=0.01,
    price_per_unit=0.01,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    )
    )


    # Create a tiered usage pricing model
    # Create a tiered usage pricing model
    tiered_model = TieredUsagePricing(graduated=True)
    tiered_model = TieredUsagePricing(graduated=True)


    # Add tiered pricing for tokens
    # Add tiered pricing for tokens
    tiered_model.add_metric_pricing(
    tiered_model.add_metric_pricing(
    metric=UsageMetric.TOKEN,
    metric=UsageMetric.TOKEN,
    tiers=[
    tiers=[
    {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.001},
    {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.001},
    {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0008},
    {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0008},
    {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.0005},
    {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.0005},
    ],
    ],
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    )
    )


    # Create a consumption-based pricing model
    # Create a consumption-based pricing model
    consumption_model = ConsumptionBasedPricing()
    consumption_model = ConsumptionBasedPricing()


    # Add pricing for compute, storage, and bandwidth
    # Add pricing for compute, storage, and bandwidth
    consumption_model.add_compute_pricing(price_per_hour=0.10, resource_type="cpu")
    consumption_model.add_compute_pricing(price_per_hour=0.10, resource_type="cpu")
    consumption_model.add_storage_pricing(price_per_gb=0.05, resource_type="standard")
    consumption_model.add_storage_pricing(price_per_gb=0.05, resource_type="standard")
    consumption_model.add_bandwidth_pricing(price_per_gb=0.08, resource_type="outbound")
    consumption_model.add_bandwidth_pricing(price_per_gb=0.08, resource_type="outbound")


    # Create a hybrid usage pricing model
    # Create a hybrid usage pricing model
    hybrid_model = HybridUsagePricing(base_fee=9.99)
    hybrid_model = HybridUsagePricing(base_fee=9.99)


    # Add included usage with overage pricing
    # Add included usage with overage pricing
    hybrid_model.add_included_usage(
    hybrid_model.add_included_usage(
    metric=UsageMetric.API_CALL,
    metric=UsageMetric.API_CALL,
    quantity=1000,
    quantity=1000,
    overage_price=0.005,
    overage_price=0.005,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    )
    )


    hybrid_model.add_included_usage(
    hybrid_model.add_included_usage(
    metric=UsageMetric.STORAGE,
    metric=UsageMetric.STORAGE,
    quantity=5.0,  # GB
    quantity=5.0,  # GB
    overage_price=0.10,  # per GB
    overage_price=0.10,  # per GB
    category=UsageCategory.STORAGE,
    category=UsageCategory.STORAGE,
    )
    )