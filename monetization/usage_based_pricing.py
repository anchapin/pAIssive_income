"""
"""
Usage-based pricing for the pAIssive Income project.
Usage-based pricing for the pAIssive Income project.


This module provides classes for implementing usage-based pricing models,
This module provides classes for implementing usage-based pricing models,
where customers are charged based on their actual usage of a service.
where customers are charged based on their actual usage of a service.
"""
"""


import time
import time
import uuid
import uuid
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .usage_tracker import UsageTracker
from .usage_tracker import UsageTracker
from .usage_tracking import UsageCategory, UsageMetric
from .usage_tracking import UsageCategory, UsageMetric




class UsageBasedPricing
class UsageBasedPricing


(
(
BillingCalculator,
BillingCalculator,
PricingRule,
PricingRule,
)
)
:
    :
    """
    """
    Class for implementing usage-based pricing models.
    Class for implementing usage-based pricing models.


    This class provides methods for creating and managing usage-based pricing models,
    This class provides methods for creating and managing usage-based pricing models,
    where customers are charged based on their actual usage of a service.
    where customers are charged based on their actual usage of a service.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    name: str,
    name: str,
    description: str = "",
    description: str = "",
    billing_calculator: Optional[BillingCalculator] = None,
    billing_calculator: Optional[BillingCalculator] = None,
    usage_tracker: Optional[UsageTracker] = None,
    usage_tracker: Optional[UsageTracker] = None,
    ):
    ):
    """
    """
    Initialize a usage-based pricing model.
    Initialize a usage-based pricing model.


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
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.name = name
    self.name = name
    self.description = description
    self.description = description
    self.billing_calculator = billing_calculator or BillingCalculator()
    self.billing_calculator = billing_calculator or BillingCalculator()
    self.usage_tracker = usage_tracker or UsageTracker()
    self.usage_tracker = usage_tracker or UsageTracker()
    self.created_at = datetime.now().isoformat()
    self.created_at = datetime.now().isoformat()
    self.updated_at = self.created_at
    self.updated_at = self.created_at


    def add_per_unit_pricing(
    def add_per_unit_pricing(
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
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    ) -> PricingRule:
    ) -> PricingRule:
    """
    """
    Add a per-unit pricing rule to the model.
    Add a per-unit pricing rule to the model.


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
    minimum_cost: Minimum cost
    minimum_cost: Minimum cost
    maximum_cost: Maximum cost
    maximum_cost: Maximum cost


    Returns:
    Returns:
    The created pricing rule
    The created pricing rule
    """
    """
    return self.billing_calculator.create_per_unit_pricing_rule(
    return self.billing_calculator.create_per_unit_pricing_rule(
    metric=metric,
    metric=metric,
    price_per_unit=price_per_unit,
    price_per_unit=price_per_unit,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    minimum_cost=minimum_cost,
    minimum_cost=minimum_cost,
    maximum_cost=maximum_cost,
    maximum_cost=maximum_cost,
    )
    )


    def add_tiered_pricing(
    def add_tiered_pricing(
    self,
    self,
    metric: str,
    metric: str,
    tiers: List[Dict[str, Any]],
    tiers: List[Dict[str, Any]],
    graduated: bool = False,
    graduated: bool = False,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    ) -> PricingRule:
    ) -> PricingRule:
    """
    """
    Add a tiered pricing rule to the model.
    Add a tiered pricing rule to the model.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    tiers: List of tier dictionaries
    tiers: List of tier dictionaries
    graduated: Whether to use graduated pricing
    graduated: Whether to use graduated pricing
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource
    minimum_cost: Minimum cost
    minimum_cost: Minimum cost
    maximum_cost: Maximum cost
    maximum_cost: Maximum cost


    Returns:
    Returns:
    The created pricing rule
    The created pricing rule
    """
    """
    return self.billing_calculator.create_tiered_pricing_rule(
    return self.billing_calculator.create_tiered_pricing_rule(
    metric=metric,
    metric=metric,
    tiers=tiers,
    tiers=tiers,
    graduated=graduated,
    graduated=graduated,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    minimum_cost=minimum_cost,
    minimum_cost=minimum_cost,
    maximum_cost=maximum_cost,
    maximum_cost=maximum_cost,
    )
    )


    def add_package_pricing(
    def add_package_pricing(
    self,
    self,
    metric: str,
    metric: str,
    quantity: float,
    quantity: float,
    price: float,
    price: float,
    overage_price: Optional[float] = None,
    overage_price: Optional[float] = None,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    ) -> PricingRule:
    ) -> PricingRule:
    """
    """
    Add a package pricing rule to the model.
    Add a package pricing rule to the model.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    quantity: Quantity included in the package
    quantity: Quantity included in the package
    price: Price for the package
    price: Price for the package
    overage_price: Price per unit for usage beyond the package quantity
    overage_price: Price per unit for usage beyond the package quantity
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource
    minimum_cost: Minimum cost
    minimum_cost: Minimum cost
    maximum_cost: Maximum cost
    maximum_cost: Maximum cost


    Returns:
    Returns:
    The created pricing rule
    The created pricing rule
    """
    """
    return self.billing_calculator.create_package_pricing_rule(
    return self.billing_calculator.create_package_pricing_rule(
    metric=metric,
    metric=metric,
    quantity=quantity,
    quantity=quantity,
    price=price,
    price=price,
    overage_price=overage_price,
    overage_price=overage_price,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    minimum_cost=minimum_cost,
    minimum_cost=minimum_cost,
    maximum_cost=maximum_cost,
    maximum_cost=maximum_cost,
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
    return self.billing_calculator.calculate_usage_cost(
    return self.billing_calculator.calculate_usage_cost(
    customer_id=customer_id, start_time=start_time, end_time=end_time
    customer_id=customer_id, start_time=start_time, end_time=end_time
    )
    )


    def get_usage_summary(
    def get_usage_summary(
    self, customer_id: str, start_time: datetime, end_time: datetime
    self, customer_id: str, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get a summary of usage for a customer.
    Get a summary of usage for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    start_time: Start time for the period
    start_time: Start time for the period
    end_time: End time for the period
    end_time: End time for the period


    Returns:
    Returns:
    Dictionary with usage summary
    Dictionary with usage summary
    """
    """
    return self.usage_tracker.get_usage_summary(
    return self.usage_tracker.get_usage_summary(
    customer_id=customer_id, start_time=start_time, end_time=end_time
    customer_id=customer_id, start_time=start_time, end_time=end_time
    )
    )


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the usage-based pricing model to a dictionary.
    Convert the usage-based pricing model to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the model
    Dictionary representation of the model
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "name": self.name,
    "name": self.name,
    "description": self.description,
    "description": self.description,
    "created_at": self.created_at,
    "created_at": self.created_at,
    "updated_at": self.updated_at,
    "updated_at": self.updated_at,
    }
    }


    @classmethod
    @classmethod
    def from_dict(
    def from_dict(
    cls,
    cls,
    data: Dict[str, Any],
    data: Dict[str, Any],
    billing_calculator: Optional[BillingCalculator] = None,
    billing_calculator: Optional[BillingCalculator] = None,
    usage_tracker: Optional[UsageTracker] = None,
    usage_tracker: Optional[UsageTracker] = None,
    ) -> "UsageBasedPricing":
    ) -> "UsageBasedPricing":
    """
    """
    Create a usage-based pricing model from a dictionary.
    Create a usage-based pricing model from a dictionary.


    Args:
    Args:
    data: Dictionary with model data
    data: Dictionary with model data
    billing_calculator: Billing calculator to use
    billing_calculator: Billing calculator to use
    usage_tracker: Usage tracker to use
    usage_tracker: Usage tracker to use


    Returns:
    Returns:
    UsageBasedPricing instance
    UsageBasedPricing instance
    """
    """
    model = cls(
    model = cls(
    name=data["name"],
    name=data["name"],
    description=data.get("description", ""),
    description=data.get("description", ""),
    billing_calculator=billing_calculator,
    billing_calculator=billing_calculator,
    usage_tracker=usage_tracker,
    usage_tracker=usage_tracker,
    )
    )


    model.id = data.get("id", model.id)
    model.id = data.get("id", model.id)
    model.created_at = data.get("created_at", model.created_at)
    model.created_at = data.get("created_at", model.created_at)
    model.updated_at = data.get("updated_at", model.updated_at)
    model.updated_at = data.get("updated_at", model.updated_at)


    return model
    return model




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a usage-based pricing model
    # Create a usage-based pricing model
    model = UsageBasedPricing(
    model = UsageBasedPricing(
    name="API Usage Pricing", description="Pricing model for API usage"
    name="API Usage Pricing", description="Pricing model for API usage"
    )
    )


    # Add pricing rules
    # Add pricing rules
    model.add_per_unit_pricing(
    model.add_per_unit_pricing(
    metric=UsageMetric.API_CALL,
    metric=UsageMetric.API_CALL,
    price_per_unit=0.01,
    price_per_unit=0.01,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    )
    )


    model.add_tiered_pricing(
    model.add_tiered_pricing(
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
    graduated=True,
    graduated=True,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    )
    )


    model.add_package_pricing(
    model.add_package_pricing(
    metric=UsageMetric.STORAGE,
    metric=UsageMetric.STORAGE,
    quantity=10.0,  # GB
    quantity=10.0,  # GB
    price=5.0,
    price=5.0,
    overage_price=0.5,  # per GB
    overage_price=0.5,  # per GB
    category=UsageCategory.STORAGE,
    category=UsageCategory.STORAGE,
    )
    )


    # Calculate cost for a customer
    # Calculate cost for a customer
    cost = model.calculate_cost(
    cost = model.calculate_cost(
    customer_id="customer123",
    customer_id="customer123",
    start_time=datetime.now() - timedelta(days=30),
    start_time=datetime.now() - timedelta(days=30),
    end_time=datetime.now(),
    end_time=datetime.now(),
    )
    )


    print(f"Total cost: ${cost['total']:.2f}")
    print(f"Total cost: ${cost['total']:.2f}")
    print(f"Cost breakdown: {cost['breakdown']}")
    print(f"Cost breakdown: {cost['breakdown']}")