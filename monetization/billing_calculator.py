"""
"""
Billing calculator for the pAIssive Income project.
Billing calculator for the pAIssive Income project.


This module provides classes for calculating billing based on usage,
This module provides classes for calculating billing based on usage,
including different pricing models and cost estimation.
including different pricing models and cost estimation.
"""
"""


import hashlib
import hashlib
import json
import json
import time
import time
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from common_utils.caching import default_cache
from common_utils.caching import default_cache


from .usage_tracker import UsageTracker
from .usage_tracker import UsageTracker
from .usage_tracking import UsageCategory, UsageMetric
from .usage_tracking import UsageCategory, UsageMetric




class PricingModel:
    class PricingModel:
    from .usage_tracker import UsageTracker
    from .usage_tracker import UsageTracker






    # Import the centralized caching service
    # Import the centralized caching service
    :
    :
    """Enumeration of pricing models."""

    FLAT_RATE = "flat_rate"
    PER_UNIT = "per_unit"
    TIERED = "tiered"
    GRADUATED = "graduated"
    PACKAGE = "package"
    CUSTOM = "custom"


    class PricingTier:
    """
    """
    Class representing a pricing tier.
    Class representing a pricing tier.


    This class provides a structured way to represent a pricing tier,
    This class provides a structured way to represent a pricing tier,
    including the minimum and maximum quantities and the price per unit.
    including the minimum and maximum quantities and the price per unit.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    min_quantity: float,
    min_quantity: float,
    max_quantity: Optional[float],
    max_quantity: Optional[float],
    price_per_unit: float,
    price_per_unit: float,
    flat_fee: float = 0.0,
    flat_fee: float = 0.0,
    ):
    ):
    """
    """
    Initialize a pricing tier.
    Initialize a pricing tier.


    Args:
    Args:
    min_quantity: Minimum quantity for this tier
    min_quantity: Minimum quantity for this tier
    max_quantity: Maximum quantity for this tier (None for unlimited)
    max_quantity: Maximum quantity for this tier (None for unlimited)
    price_per_unit: Price per unit for this tier
    price_per_unit: Price per unit for this tier
    flat_fee: Flat fee for this tier
    flat_fee: Flat fee for this tier
    """
    """
    self.min_quantity = min_quantity
    self.min_quantity = min_quantity
    self.max_quantity = max_quantity
    self.max_quantity = max_quantity
    self.price_per_unit = price_per_unit
    self.price_per_unit = price_per_unit
    self.flat_fee = flat_fee
    self.flat_fee = flat_fee


    def contains(self, quantity: float) -> bool:
    def contains(self, quantity: float) -> bool:
    """
    """
    Check if a quantity is within this tier.
    Check if a quantity is within this tier.


    Args:
    Args:
    quantity: Quantity to check
    quantity: Quantity to check


    Returns:
    Returns:
    True if the quantity is within this tier, False otherwise
    True if the quantity is within this tier, False otherwise
    """
    """
    if quantity < self.min_quantity:
    if quantity < self.min_quantity:
    return False
    return False


    if self.max_quantity is not None and quantity > self.max_quantity:
    if self.max_quantity is not None and quantity > self.max_quantity:
    return False
    return False


    return True
    return True


    def get_quantity_in_tier(self, quantity: float) -> float:
    def get_quantity_in_tier(self, quantity: float) -> float:
    """
    """
    Get the quantity that falls within this tier.
    Get the quantity that falls within this tier.


    Args:
    Args:
    quantity: Total quantity
    quantity: Total quantity


    Returns:
    Returns:
    Quantity within this tier
    Quantity within this tier
    """
    """
    if quantity <= self.min_quantity:
    if quantity <= self.min_quantity:
    return 0.0
    return 0.0


    if self.max_quantity is not None:
    if self.max_quantity is not None:
    return min(quantity, self.max_quantity) - self.min_quantity
    return min(quantity, self.max_quantity) - self.min_quantity


    return quantity - self.min_quantity
    return quantity - self.min_quantity


    def calculate_cost(self, quantity: float, graduated: bool = False) -> float:
    def calculate_cost(self, quantity: float, graduated: bool = False) -> float:
    """
    """
    Calculate the cost for a quantity using this tier.
    Calculate the cost for a quantity using this tier.


    Args:
    Args:
    quantity: Quantity to calculate cost for
    quantity: Quantity to calculate cost for
    graduated: Whether to use graduated pricing
    graduated: Whether to use graduated pricing


    Returns:
    Returns:
    Cost for the quantity
    Cost for the quantity
    """
    """
    if graduated:
    if graduated:
    # Only calculate cost for the portion of the quantity that falls within this tier
    # Only calculate cost for the portion of the quantity that falls within this tier
    quantity_in_tier = self.get_quantity_in_tier(quantity)
    quantity_in_tier = self.get_quantity_in_tier(quantity)


    if quantity_in_tier <= 0:
    if quantity_in_tier <= 0:
    return 0.0
    return 0.0


    return self.flat_fee + (quantity_in_tier * self.price_per_unit)
    return self.flat_fee + (quantity_in_tier * self.price_per_unit)
    else:
    else:
    # Calculate cost for the entire quantity using this tier's pricing
    # Calculate cost for the entire quantity using this tier's pricing
    if not self.contains(quantity):
    if not self.contains(quantity):
    return 0.0
    return 0.0


    return self.flat_fee + (quantity * self.price_per_unit)
    return self.flat_fee + (quantity * self.price_per_unit)


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the pricing tier to a dictionary.
    Convert the pricing tier to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the pricing tier
    Dictionary representation of the pricing tier
    """
    """
    return {
    return {
    "min_quantity": self.min_quantity,
    "min_quantity": self.min_quantity,
    "max_quantity": self.max_quantity,
    "max_quantity": self.max_quantity,
    "price_per_unit": self.price_per_unit,
    "price_per_unit": self.price_per_unit,
    "flat_fee": self.flat_fee,
    "flat_fee": self.flat_fee,
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PricingTier":
    def from_dict(cls, data: Dict[str, Any]) -> "PricingTier":
    """
    """
    Create a pricing tier from a dictionary.
    Create a pricing tier from a dictionary.


    Args:
    Args:
    data: Dictionary with pricing tier data
    data: Dictionary with pricing tier data


    Returns:
    Returns:
    PricingTier instance
    PricingTier instance
    """
    """
    return cls(
    return cls(
    min_quantity=data["min_quantity"],
    min_quantity=data["min_quantity"],
    max_quantity=data["max_quantity"],
    max_quantity=data["max_quantity"],
    price_per_unit=data["price_per_unit"],
    price_per_unit=data["price_per_unit"],
    flat_fee=data.get("flat_fee", 0.0),
    flat_fee=data.get("flat_fee", 0.0),
    )
    )


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the pricing tier."""
    max_str = str(self.max_quantity) if self.max_quantity is not None else "∞"
    return f"PricingTier({self.min_quantity}-{max_str}, ${self.price_per_unit}/unit, ${self.flat_fee} flat)"


    class PricingPackage:
    """
    """
    Class representing a pricing package.
    Class representing a pricing package.


    This class provides a structured way to represent a pricing package,
    This class provides a structured way to represent a pricing package,
    including the quantity, price, and overage pricing.
    including the quantity, price, and overage pricing.
    """
    """


    def __init__(
    def __init__(
    self, quantity: float, price: float, overage_price: Optional[float] = None
    self, quantity: float, price: float, overage_price: Optional[float] = None
    ):
    ):
    """
    """
    Initialize a pricing package.
    Initialize a pricing package.


    Args:
    Args:
    quantity: Quantity included in the package
    quantity: Quantity included in the package
    price: Price for the package
    price: Price for the package
    overage_price: Price per unit for usage beyond the package quantity
    overage_price: Price per unit for usage beyond the package quantity
    """
    """
    self.quantity = quantity
    self.quantity = quantity
    self.price = price
    self.price = price
    self.overage_price = overage_price
    self.overage_price = overage_price


    def calculate_cost(self, quantity: float) -> float:
    def calculate_cost(self, quantity: float) -> float:
    """
    """
    Calculate the cost for a quantity using this package.
    Calculate the cost for a quantity using this package.


    Args:
    Args:
    quantity: Quantity to calculate cost for
    quantity: Quantity to calculate cost for


    Returns:
    Returns:
    Cost for the quantity
    Cost for the quantity
    """
    """
    if quantity <= self.quantity:
    if quantity <= self.quantity:
    return self.price
    return self.price


    if self.overage_price is None:
    if self.overage_price is None:
    return self.price
    return self.price


    overage = quantity - self.quantity
    overage = quantity - self.quantity
    return self.price + (overage * self.overage_price)
    return self.price + (overage * self.overage_price)


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the pricing package to a dictionary.
    Convert the pricing package to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the pricing package
    Dictionary representation of the pricing package
    """
    """
    return {
    return {
    "quantity": self.quantity,
    "quantity": self.quantity,
    "price": self.price,
    "price": self.price,
    "overage_price": self.overage_price,
    "overage_price": self.overage_price,
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PricingPackage":
    def from_dict(cls, data: Dict[str, Any]) -> "PricingPackage":
    """
    """
    Create a pricing package from a dictionary.
    Create a pricing package from a dictionary.


    Args:
    Args:
    data: Dictionary with pricing package data
    data: Dictionary with pricing package data


    Returns:
    Returns:
    PricingPackage instance
    PricingPackage instance
    """
    """
    return cls(
    return cls(
    quantity=data["quantity"],
    quantity=data["quantity"],
    price=data["price"],
    price=data["price"],
    overage_price=data.get("overage_price"),
    overage_price=data.get("overage_price"),
    )
    )


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the pricing package."""
    overage_str = (
    f", ${self.overage_price}/unit overage"
    if self.overage_price is not None
    else ""
    )
    return f"PricingPackage({self.quantity} units, ${self.price}{overage_str})"


    class PricingRule:
    """
    """
    Class representing a pricing rule.
    Class representing a pricing rule.


    This class provides a structured way to represent a pricing rule,
    This class provides a structured way to represent a pricing rule,
    including the metric, pricing model, and pricing details.
    including the metric, pricing model, and pricing details.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    metric: str,
    metric: str,
    model: str,
    model: str,
    price_per_unit: Optional[float] = None,
    price_per_unit: Optional[float] = None,
    flat_fee: float = 0.0,
    flat_fee: float = 0.0,
    tiers: Optional[List[PricingTier]] = None,
    tiers: Optional[List[PricingTier]] = None,
    package: Optional[PricingPackage] = None,
    package: Optional[PricingPackage] = None,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    custom_calculator: Optional[callable] = None,
    custom_calculator: Optional[callable] = None,
    ):
    ):
    """
    """
    Initialize a pricing rule.
    Initialize a pricing rule.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    model: Pricing model (e.g., FLAT_RATE, PER_UNIT, TIERED)
    model: Pricing model (e.g., FLAT_RATE, PER_UNIT, TIERED)
    price_per_unit: Price per unit (for PER_UNIT model)
    price_per_unit: Price per unit (for PER_UNIT model)
    flat_fee: Flat fee (for FLAT_RATE model)
    flat_fee: Flat fee (for FLAT_RATE model)
    tiers: List of pricing tiers (for TIERED and GRADUATED models)
    tiers: List of pricing tiers (for TIERED and GRADUATED models)
    package: Pricing package (for PACKAGE model)
    package: Pricing package (for PACKAGE model)
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource
    minimum_cost: Minimum cost
    minimum_cost: Minimum cost
    maximum_cost: Maximum cost
    maximum_cost: Maximum cost
    custom_calculator: Custom calculator function (for CUSTOM model)
    custom_calculator: Custom calculator function (for CUSTOM model)
    """
    """
    self.metric = metric
    self.metric = metric
    self.model = model
    self.model = model
    self.price_per_unit = price_per_unit
    self.price_per_unit = price_per_unit
    self.flat_fee = flat_fee
    self.flat_fee = flat_fee
    self.tiers = tiers or []
    self.tiers = tiers or []
    self.package = package
    self.package = package
    self.category = category
    self.category = category
    self.resource_type = resource_type
    self.resource_type = resource_type
    self.minimum_cost = minimum_cost
    self.minimum_cost = minimum_cost
    self.maximum_cost = maximum_cost
    self.maximum_cost = maximum_cost
    self.custom_calculator = custom_calculator
    self.custom_calculator = custom_calculator


    def matches(
    def matches(
    self,
    self,
    metric: str,
    metric: str,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    ) -> bool:
    ) -> bool:
    """
    """
    Check if this rule matches a metric, category, and resource type.
    Check if this rule matches a metric, category, and resource type.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource


    Returns:
    Returns:
    True if this rule matches, False otherwise
    True if this rule matches, False otherwise
    """
    """
    if self.metric != metric:
    if self.metric != metric:
    return False
    return False


    if (
    if (
    self.category is not None
    self.category is not None
    and category is not None
    and category is not None
    and self.category != category
    and self.category != category
    ):
    ):
    return False
    return False


    if (
    if (
    self.resource_type is not None
    self.resource_type is not None
    and resource_type is not None
    and resource_type is not None
    and self.resource_type != resource_type
    and self.resource_type != resource_type
    ):
    ):
    return False
    return False


    return True
    return True


    def calculate_cost(self, quantity: float) -> float:
    def calculate_cost(self, quantity: float) -> float:
    """
    """
    Calculate the cost for a quantity using this pricing rule's model.
    Calculate the cost for a quantity using this pricing rule's model.


    This algorithm implements a comprehensive billing calculation system that supports
    This algorithm implements a comprehensive billing calculation system that supports
    multiple pricing models commonly used in SaaS and cloud services. The implementation
    multiple pricing models commonly used in SaaS and cloud services. The implementation
    follows these key stages:
    follows these key stages:


    1. MODEL-SPECIFIC CALCULATION STRATEGIES:
    1. MODEL-SPECIFIC CALCULATION STRATEGIES:
    - Implements six distinct pricing models in a single unified method:
    - Implements six distinct pricing models in a single unified method:
    a) FLAT_RATE: Fixed cost regardless of usage (e.g., base subscription fee)
    a) FLAT_RATE: Fixed cost regardless of usage (e.g., base subscription fee)
    b) PER_UNIT: Simple linear pricing (e.g., $0.01 per API call)
    b) PER_UNIT: Simple linear pricing (e.g., $0.01 per API call)
    c) TIERED: Threshold-based pricing where the entire quantity is priced at the
    c) TIERED: Threshold-based pricing where the entire quantity is priced at the
    tier rate that contains it (e.g., 0-1000 units at $10, 1001-10000 at $8)
    tier rate that contains it (e.g., 0-1000 units at $10, 1001-10000 at $8)
    d) GRADUATED: Volume-based pricing where each usage segment is priced at its
    d) GRADUATED: Volume-based pricing where each usage segment is priced at its
    corresponding tier rate (e.g., first 1000 units at $10, next 9000 at $8)
    corresponding tier rate (e.g., first 1000 units at $10, next 9000 at $8)
    e) PACKAGE: Bundle pricing with optional overage charges (e.g., $5 for 1000 units,
    e) PACKAGE: Bundle pricing with optional overage charges (e.g., $5 for 1000 units,
    then $0.005 per unit after that)
    then $0.005 per unit after that)
    f) CUSTOM: Extensible pricing using custom calculator functions
    f) CUSTOM: Extensible pricing using custom calculator functions


    2. TIERED PRICING LOGIC:
    2. TIERED PRICING LOGIC:
    - For standard tiered pricing, finds the containing tier for the entire quantity
    - For standard tiered pricing, finds the containing tier for the entire quantity
    - Uses binary definition of tier membership (a quantity either belongs to a tier or not)
    - Uses binary definition of tier membership (a quantity either belongs to a tier or not)
    - Applies the tier's pricing to the entire quantity
    - Applies the tier's pricing to the entire quantity
    - Maintains consistent business logic for threshold-based pricing models
    - Maintains consistent business logic for threshold-based pricing models


    3. GRADUATED PRICING LOGIC:
    3. GRADUATED PRICING LOGIC:
    - For graduated pricing, calculates costs across multiple tiers
    - For graduated pricing, calculates costs across multiple tiers
    - Applies different rates to different portions of the total quantity
    - Applies different rates to different portions of the total quantity
    - Aggregates costs from each tier segment
    - Aggregates costs from each tier segment
    - Properly handles partial tier utilization at boundaries
    - Properly handles partial tier utilization at boundaries


    4. PACKAGE PRICING WITH OVERAGE:
    4. PACKAGE PRICING WITH OVERAGE:
    - Implements the common "included quantity + overage" pricing pattern
    - Implements the common "included quantity + overage" pricing pattern
    - Handles cases both with and without overage pricing
    - Handles cases both with and without overage pricing
    - Accurately calculates overage only for usage beyond the package limit
    - Accurately calculates overage only for usage beyond the package limit


    5. BOUNDARY CONDITION HANDLING:
    5. BOUNDARY CONDITION HANDLING:
    - Enforces minimum and maximum cost constraints if specified
    - Enforces minimum and maximum cost constraints if specified
    - Handles edge cases like zero quantity correctly
    - Handles edge cases like zero quantity correctly
    - Provides safeguards against incorrect pricing configurations
    - Provides safeguards against incorrect pricing configurations


    The calculate_cost method is the computational core of the billing system and
    The calculate_cost method is the computational core of the billing system and
    enables flexible monetization strategies for various business models:
    enables flexible monetization strategies for various business models:


    - Usage-based services with predictable per-unit costs
    - Usage-based services with predictable per-unit costs
    - Volume discount systems where unit price decreases with usage
    - Volume discount systems where unit price decreases with usage
    - Hybrid models combining base fees with usage components
    - Hybrid models combining base fees with usage components
    - Packages with bundled units and overage charges
    - Packages with bundled units and overage charges
    - Custom pricing for specialized business arrangements
    - Custom pricing for specialized business arrangements


    This implementation addresses common real-world billing requirements, including:
    This implementation addresses common real-world billing requirements, including:
    - Simple flat monthly fees (FLAT_RATE)
    - Simple flat monthly fees (FLAT_RATE)
    - Basic metered pricing (PER_UNIT)
    - Basic metered pricing (PER_UNIT)
    - Volume discount thresholds (TIERED)
    - Volume discount thresholds (TIERED)
    - Incremental discount bands (GRADUATED)
    - Incremental discount bands (GRADUATED)
    - Bundled offerings with included quantities (PACKAGE)
    - Bundled offerings with included quantities (PACKAGE)
    - Complex custom pricing logic (CUSTOM)
    - Complex custom pricing logic (CUSTOM)
    - Minimum spend requirements and spend caps
    - Minimum spend requirements and spend caps


    Args:
    Args:
    quantity: The total unit quantity to calculate cost for. Can represent any
    quantity: The total unit quantity to calculate cost for. Can represent any
    measurable usage dimension such as API calls, minutes, GB, etc.
    measurable usage dimension such as API calls, minutes, GB, etc.


    Returns:
    Returns:
    The calculated cost based on the quantity and this rule's pricing model.
    The calculated cost based on the quantity and this rule's pricing model.
    Returns 0.0 if no applicable pricing model is found or if the quantity
    Returns 0.0 if no applicable pricing model is found or if the quantity
    doesn't match the rule's criteria.
    doesn't match the rule's criteria.
    """
    """
    # Initialize the cost accumulator
    # Initialize the cost accumulator
    cost = 0.0
    cost = 0.0


    # FLAT_RATE: Fixed cost regardless of usage
    # FLAT_RATE: Fixed cost regardless of usage
    # This model applies a set fee regardless of the quantity used
    # This model applies a set fee regardless of the quantity used
    # Example: Base subscription fee of $10/month regardless of usage
    # Example: Base subscription fee of $10/month regardless of usage
    if self.model == PricingModel.FLAT_RATE:
    if self.model == PricingModel.FLAT_RATE:
    cost = self.flat_fee
    cost = self.flat_fee


    # PER_UNIT: Simple linear pricing
    # PER_UNIT: Simple linear pricing
    # This model multiplies the quantity by a fixed per-unit price
    # This model multiplies the quantity by a fixed per-unit price
    # Example: $0.01 per API call, so 100 calls = $1.00
    # Example: $0.01 per API call, so 100 calls = $1.00
    elif self.model == PricingModel.PER_UNIT:
    elif self.model == PricingModel.PER_UNIT:
    if self.price_per_unit is not None:
    if self.price_per_unit is not None:
    cost = quantity * self.price_per_unit
    cost = quantity * self.price_per_unit


    # TIERED: Threshold-based pricing
    # TIERED: Threshold-based pricing
    # In this model, the entire quantity is priced at the rate of the tier that contains it
    # In this model, the entire quantity is priced at the rate of the tier that contains it
    # Example: 0-1000 units at $0.10/unit, 1001-10000 at $0.08/unit
    # Example: 0-1000 units at $0.10/unit, 1001-10000 at $0.08/unit
    #          900 units = $90 (all priced at $0.10)
    #          900 units = $90 (all priced at $0.10)
    #          1500 units = $120 (all priced at $0.08)
    #          1500 units = $120 (all priced at $0.08)
    elif self.model == PricingModel.TIERED:
    elif self.model == PricingModel.TIERED:
    # Find the tier that contains the quantity
    # Find the tier that contains the quantity
    for tier in self.tiers:
    for tier in self.tiers:
    if tier.contains(quantity):
    if tier.contains(quantity):
    # Calculate cost using that tier's pricing for the entire quantity
    # Calculate cost using that tier's pricing for the entire quantity
    cost = tier.calculate_cost(quantity)
    cost = tier.calculate_cost(quantity)
    break
    break


    # GRADUATED: Volume-based pricing
    # GRADUATED: Volume-based pricing
    # In this model, different portions of the quantity are priced at different tier rates
    # In this model, different portions of the quantity are priced at different tier rates
    # Example: 0-1000 units at $0.10/unit, 1001-10000 at $0.08/unit
    # Example: 0-1000 units at $0.10/unit, 1001-10000 at $0.08/unit
    #          1500 units = $100 + $40 = $140 (first 1000 at $0.10, next 500 at $0.08)
    #          1500 units = $100 + $40 = $140 (first 1000 at $0.10, next 500 at $0.08)
    elif self.model == PricingModel.GRADUATED:
    elif self.model == PricingModel.GRADUATED:
    # Iterate through each tier and accumulate costs for portions of the quantity
    # Iterate through each tier and accumulate costs for portions of the quantity
    for tier in self.tiers:
    for tier in self.tiers:
    # The tier's calculate_cost method handles partial tier calculation when graduated=True
    # The tier's calculate_cost method handles partial tier calculation when graduated=True
    tier_cost = tier.calculate_cost(quantity, graduated=True)
    tier_cost = tier.calculate_cost(quantity, graduated=True)
    cost += tier_cost
    cost += tier_cost


    # PACKAGE: Bundle pricing with optional overage
    # PACKAGE: Bundle pricing with optional overage
    # This model provides a set quantity for a fixed price, with optional overage charges
    # This model provides a set quantity for a fixed price, with optional overage charges
    # Example: $5 for 1000 units, then $0.005 per additional unit
    # Example: $5 for 1000 units, then $0.005 per additional unit
    elif self.model == PricingModel.PACKAGE:
    elif self.model == PricingModel.PACKAGE:
    if self.package is not None:
    if self.package is not None:
    cost = self.package.calculate_cost(quantity)
    cost = self.package.calculate_cost(quantity)


    # CUSTOM: Custom pricing logic
    # CUSTOM: Custom pricing logic
    # This model allows for completely custom pricing calculations via a callback function
    # This model allows for completely custom pricing calculations via a callback function
    # Example: Special volume discounts, step functions, or other complex logic
    # Example: Special volume discounts, step functions, or other complex logic
    elif self.model == PricingModel.CUSTOM:
    elif self.model == PricingModel.CUSTOM:
    if self.custom_calculator is not None:
    if self.custom_calculator is not None:
    cost = self.custom_calculator(quantity)
    cost = self.custom_calculator(quantity)


    # Apply minimum cost constraint if specified
    # Apply minimum cost constraint if specified
    # This ensures the customer pays at least a minimum amount
    # This ensures the customer pays at least a minimum amount
    if cost < self.minimum_cost:
    if cost < self.minimum_cost:
    cost = self.minimum_cost
    cost = self.minimum_cost


    # Apply maximum cost constraint if specified
    # Apply maximum cost constraint if specified
    # This implements a price ceiling or spend cap
    # This implements a price ceiling or spend cap
    if self.maximum_cost is not None and cost > self.maximum_cost:
    if self.maximum_cost is not None and cost > self.maximum_cost:
    cost = self.maximum_cost
    cost = self.maximum_cost


    return cost
    return cost


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the pricing rule to a dictionary.
    Convert the pricing rule to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the pricing rule
    Dictionary representation of the pricing rule
    """
    """
    result = {
    result = {
    "metric": self.metric,
    "metric": self.metric,
    "model": self.model,
    "model": self.model,
    "price_per_unit": self.price_per_unit,
    "price_per_unit": self.price_per_unit,
    "flat_fee": self.flat_fee,
    "flat_fee": self.flat_fee,
    "category": self.category,
    "category": self.category,
    "resource_type": self.resource_type,
    "resource_type": self.resource_type,
    "minimum_cost": self.minimum_cost,
    "minimum_cost": self.minimum_cost,
    "maximum_cost": self.maximum_cost,
    "maximum_cost": self.maximum_cost,
    }
    }


    if self.tiers:
    if self.tiers:
    result["tiers"] = [tier.to_dict() for tier in self.tiers]
    result["tiers"] = [tier.to_dict() for tier in self.tiers]


    if self.package:
    if self.package:
    result["package"] = self.package.to_dict()
    result["package"] = self.package.to_dict()


    return result
    return result


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PricingRule":
    def from_dict(cls, data: Dict[str, Any]) -> "PricingRule":
    """
    """
    Create a pricing rule from a dictionary.
    Create a pricing rule from a dictionary.


    Args:
    Args:
    data: Dictionary with pricing rule data
    data: Dictionary with pricing rule data


    Returns:
    Returns:
    PricingRule instance
    PricingRule instance
    """
    """
    tiers = None
    tiers = None
    if "tiers" in data:
    if "tiers" in data:
    tiers = [PricingTier.from_dict(tier_data) for tier_data in data["tiers"]]
    tiers = [PricingTier.from_dict(tier_data) for tier_data in data["tiers"]]


    package = None
    package = None
    if "package" in data:
    if "package" in data:
    package = PricingPackage.from_dict(data["package"])
    package = PricingPackage.from_dict(data["package"])


    return cls(
    return cls(
    metric=data["metric"],
    metric=data["metric"],
    model=data["model"],
    model=data["model"],
    price_per_unit=data.get("price_per_unit"),
    price_per_unit=data.get("price_per_unit"),
    flat_fee=data.get("flat_fee", 0.0),
    flat_fee=data.get("flat_fee", 0.0),
    tiers=tiers,
    tiers=tiers,
    package=package,
    package=package,
    category=data.get("category"),
    category=data.get("category"),
    resource_type=data.get("resource_type"),
    resource_type=data.get("resource_type"),
    minimum_cost=data.get("minimum_cost", 0.0),
    minimum_cost=data.get("minimum_cost", 0.0),
    maximum_cost=data.get("maximum_cost"),
    maximum_cost=data.get("maximum_cost"),
    )
    )


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the pricing rule."""
    return f"PricingRule({self.metric}, {self.model})"


    class BillingCalculator:
    """
    """
    Class for calculating billing based on usage.
    Class for calculating billing based on usage.


    This class provides methods for calculating billing based on usage records,
    This class provides methods for calculating billing based on usage records,
    using different pricing models and rules.
    using different pricing models and rules.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    usage_tracker: Optional[UsageTracker] = None,
    usage_tracker: Optional[UsageTracker] = None,
    pricing_rules: Optional[List[PricingRule]] = None,
    pricing_rules: Optional[List[PricingRule]] = None,
    ):
    ):
    """
    """
    Initialize a billing calculator.
    Initialize a billing calculator.


    Args:
    Args:
    usage_tracker: Usage tracker to use
    usage_tracker: Usage tracker to use
    pricing_rules: List of pricing rules
    pricing_rules: List of pricing rules
    """
    """
    self.usage_tracker = usage_tracker
    self.usage_tracker = usage_tracker
    self.pricing_rules = pricing_rules or []
    self.pricing_rules = pricing_rules or []


    # Cache TTL in seconds (24 hours by default)
    # Cache TTL in seconds (24 hours by default)
    self.cache_ttl = 86400
    self.cache_ttl = 86400


    def add_pricing_rule(self, rule: PricingRule) -> None:
    def add_pricing_rule(self, rule: PricingRule) -> None:
    """
    """
    Add a pricing rule.
    Add a pricing rule.


    Args:
    Args:
    rule: Pricing rule to add
    rule: Pricing rule to add
    """
    """
    self.pricing_rules.append(rule)
    self.pricing_rules.append(rule)


    # Invalidate the rule cache when rules change
    # Invalidate the rule cache when rules change
    self._invalidate_rule_cache()
    self._invalidate_rule_cache()


    def get_pricing_rule(
    def get_pricing_rule(
    self,
    self,
    metric: str,
    metric: str,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    ) -> Optional[PricingRule]:
    ) -> Optional[PricingRule]:
    """
    """
    Get a pricing rule that matches a metric, category, and resource type.
    Get a pricing rule that matches a metric, category, and resource type.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource


    Returns:
    Returns:
    Matching pricing rule or None if not found
    Matching pricing rule or None if not found
    """
    """
    # Generate a cache key
    # Generate a cache key
    cache_key = self._generate_rule_cache_key(metric, category, resource_type)
    cache_key = self._generate_rule_cache_key(metric, category, resource_type)


    # Try to get from cache first
    # Try to get from cache first
    cached_result = default_cache.get(cache_key, namespace="pricing_rules")
    cached_result = default_cache.get(cache_key, namespace="pricing_rules")
    if cached_result is not None:
    if cached_result is not None:
    # Recreate the rule from cached dictionary
    # Recreate the rule from cached dictionary
    if cached_result:
    if cached_result:
    return PricingRule.from_dict(cached_result)
    return PricingRule.from_dict(cached_result)
    else:
    else:
    # Cache indicates no matching rule
    # Cache indicates no matching rule
    return None
    return None


    # Find the most specific matching rule
    # Find the most specific matching rule
    best_match = None
    best_match = None
    best_match_score = -1
    best_match_score = -1


    for rule in self.pricing_rules:
    for rule in self.pricing_rules:
    if rule.matches(metric, category, resource_type):
    if rule.matches(metric, category, resource_type):
    # Calculate match score (higher is more specific)
    # Calculate match score (higher is more specific)
    score = 1
    score = 1


    if rule.category is not None and rule.category == category:
    if rule.category is not None and rule.category == category:
    score += 1
    score += 1


    if (
    if (
    rule.resource_type is not None
    rule.resource_type is not None
    and rule.resource_type == resource_type
    and rule.resource_type == resource_type
    ):
    ):
    score += 1
    score += 1


    if score > best_match_score:
    if score > best_match_score:
    best_match = rule
    best_match = rule
    best_match_score = score
    best_match_score = score


    # Cache the result
    # Cache the result
    rule_dict = best_match.to_dict() if best_match else None
    rule_dict = best_match.to_dict() if best_match else None
    default_cache.set(
    default_cache.set(
    cache_key, rule_dict, ttl=self.cache_ttl, namespace="pricing_rules"
    cache_key, rule_dict, ttl=self.cache_ttl, namespace="pricing_rules"
    )
    )


    return best_match
    return best_match


    def _generate_rule_cache_key(
    def _generate_rule_cache_key(
    self, metric: str, category: Optional[str], resource_type: Optional[str]
    self, metric: str, category: Optional[str], resource_type: Optional[str]
    ) -> str:
    ) -> str:
    """
    """
    Generate a cache key for pricing rules.
    Generate a cache key for pricing rules.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource


    Returns:
    Returns:
    Cache key string
    Cache key string
    """
    """
    key_parts = [
    key_parts = [
    f"metric:{metric}",
    f"metric:{metric}",
    f"category:{category or 'None'}",
    f"category:{category or 'None'}",
    f"resource_type:{resource_type or 'None'}",
    f"resource_type:{resource_type or 'None'}",
    ]
    ]


    return hashlib.md5("|".join(key_parts).encode()).hexdigest()
    return hashlib.md5("|".join(key_parts).encode()).hexdigest()


    def _invalidate_rule_cache(self) -> None:
    def _invalidate_rule_cache(self) -> None:
    """Invalidate the pricing rule cache."""
    default_cache.clear(namespace="pricing_rules")

    def calculate_cost(
    self,
    metric: str,
    quantity: float,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    ) -> float:
    """
    """
    Calculate the cost for a quantity using the appropriate pricing rule.
    Calculate the cost for a quantity using the appropriate pricing rule.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    quantity: Quantity to calculate cost for
    quantity: Quantity to calculate cost for
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource


    Returns:
    Returns:
    Cost for the quantity
    Cost for the quantity
    """
    """
    # Generate a cache key
    # Generate a cache key
    cache_key = self._generate_cost_cache_key(
    cache_key = self._generate_cost_cache_key(
    metric, quantity, category, resource_type
    metric, quantity, category, resource_type
    )
    )


    # Try to get from cache first
    # Try to get from cache first
    cached_cost = default_cache.get(cache_key, namespace="cost_calculations")
    cached_cost = default_cache.get(cache_key, namespace="cost_calculations")
    if cached_cost is not None:
    if cached_cost is not None:
    return cached_cost
    return cached_cost


    # Get the pricing rule
    # Get the pricing rule
    rule = self.get_pricing_rule(metric, category, resource_type)
    rule = self.get_pricing_rule(metric, category, resource_type)


    if rule is None:
    if rule is None:
    cost = 0.0
    cost = 0.0
    else:
    else:
    cost = rule.calculate_cost(quantity)
    cost = rule.calculate_cost(quantity)


    # Cache the result
    # Cache the result
    default_cache.set(
    default_cache.set(
    cache_key, cost, ttl=self.cache_ttl, namespace="cost_calculations"
    cache_key, cost, ttl=self.cache_ttl, namespace="cost_calculations"
    )
    )


    return cost
    return cost


    def _generate_cost_cache_key(
    def _generate_cost_cache_key(
    self,
    self,
    metric: str,
    metric: str,
    quantity: float,
    quantity: float,
    category: Optional[str],
    category: Optional[str],
    resource_type: Optional[str],
    resource_type: Optional[str],
    ) -> str:
    ) -> str:
    """
    """
    Generate a cache key for cost calculations.
    Generate a cache key for cost calculations.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    quantity: Quantity to calculate cost for
    quantity: Quantity to calculate cost for
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource


    Returns:
    Returns:
    Cache key string
    Cache key string
    """
    """
    key_parts = [
    key_parts = [
    f"metric:{metric}",
    f"metric:{metric}",
    f"quantity:{quantity}",
    f"quantity:{quantity}",
    f"category:{category or 'None'}",
    f"category:{category or 'None'}",
    f"resource_type:{resource_type or 'None'}",
    f"resource_type:{resource_type or 'None'}",
    ]
    ]


    return hashlib.md5("|".join(key_parts).encode()).hexdigest()
    return hashlib.md5("|".join(key_parts).encode()).hexdigest()


    def calculate_usage_cost(
    def calculate_usage_cost(
    self,
    self,
    customer_id: str,
    customer_id: str,
    start_time: Optional[datetime] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate the cost for a customer's usage within a specified time period.
    Calculate the cost for a customer's usage within a specified time period.


    This algorithm implements a comprehensive usage-based billing system that transforms
    This algorithm implements a comprehensive usage-based billing system that transforms
    raw usage data into structured cost information organized by service dimensions.
    raw usage data into structured cost information organized by service dimensions.
    The implementation follows these key phases:
    The implementation follows these key phases:


    1. USAGE DATA COLLECTION AND AGGREGATION:
    1. USAGE DATA COLLECTION AND AGGREGATION:
    - Retrieves raw usage records from the usage tracking system
    - Retrieves raw usage records from the usage tracking system
    - Properly handles the specified time window boundaries
    - Properly handles the specified time window boundaries
    - Ensures all relevant usage records are included in the calculation
    - Ensures all relevant usage records are included in the calculation
    - Groups usage data by appropriate dimensions (metric, category, resource)
    - Groups usage data by appropriate dimensions (metric, category, resource)
    - Consolidates usage quantities across multiple records
    - Consolidates usage quantities across multiple records


    2. HIERARCHICAL COST CALCULATION:
    2. HIERARCHICAL COST CALCULATION:
    - Processes usage at multiple granularity levels (metric → category → resource)
    - Processes usage at multiple granularity levels (metric → category → resource)
    - Applies the most specific matching pricing rule for each usage group
    - Applies the most specific matching pricing rule for each usage group
    - Ensures consistent handling of usage across different pricing models
    - Ensures consistent handling of usage across different pricing models
    - Maintains proper cost attribution for financial reporting
    - Maintains proper cost attribution for financial reporting
    - Prevents double-counting or missing usage records
    - Prevents double-counting or missing usage records


    3. STRUCTURED RESULT COMPOSITION:
    3. STRUCTURED RESULT COMPOSITION:
    - Creates a comprehensive billing breakdown for transparency
    - Creates a comprehensive billing breakdown for transparency
    - Organizes costs in a hierarchical structure for easy analysis
    - Organizes costs in a hierarchical structure for easy analysis
    - Includes all relevant metadata for audit and reporting purposes
    - Includes all relevant metadata for audit and reporting purposes
    - Maintains traceability from costs back to individual usage records
    - Maintains traceability from costs back to individual usage records
    - Provides both summary totals and detailed line items
    - Provides both summary totals and detailed line items


    The implementation specifically addresses several critical enterprise billing requirements:
    The implementation specifically addresses several critical enterprise billing requirements:
    - Accurate temporal boundary handling (billing periods, usage timestamps)
    - Accurate temporal boundary handling (billing periods, usage timestamps)
    - Multi-dimensional usage tracking (services, features, resources)
    - Multi-dimensional usage tracking (services, features, resources)
    - Complex pricing model application (tiered, graduated, package pricing)
    - Complex pricing model application (tiered, graduated, package pricing)
    - Detailed cost breakdowns for customer transparency
    - Detailed cost breakdowns for customer transparency
    - Full audit trail from charges to usage events
    - Full audit trail from charges to usage events


    This algorithm forms the computational foundation for invoice generation, cost
    This algorithm forms the computational foundation for invoice generation, cost
    reporting, and financial analytics in the monetization system.
    reporting, and financial analytics in the monetization system.


    Args:
    Args:
    customer_id: Unique identifier for the customer whose usage is being calculated
    customer_id: Unique identifier for the customer whose usage is being calculated
    start_time: Beginning timestamp of the billing period (inclusive)
    start_time: Beginning timestamp of the billing period (inclusive)
    end_time: Ending timestamp of the billing period (exclusive)
    end_time: Ending timestamp of the billing period (exclusive)


    Returns:
    Returns:
    A structured dictionary containing:
    A structured dictionary containing:
    - customer_id: ID of the customer
    - customer_id: ID of the customer
    - start_time: ISO formatted start time of the billing period
    - start_time: ISO formatted start time of the billing period
    - end_time: ISO formatted end time of the billing period
    - end_time: ISO formatted end time of the billing period
    - total_cost: Aggregate cost across all usage items
    - total_cost: Aggregate cost across all usage items
    - items: List of cost items, each containing:
    - items: List of cost items, each containing:
    - metric: The usage metric (e.g., API_CALL, TOKEN)
    - metric: The usage metric (e.g., API_CALL, TOKEN)
    - category: The usage category (e.g., INFERENCE, TRAINING)
    - category: The usage category (e.g., INFERENCE, TRAINING)
    - resource_type: The specific resource used (e.g., MODEL_GPT4)
    - resource_type: The specific resource used (e.g., MODEL_GPT4)
    - quantity: The total usage quantity
    - quantity: The total usage quantity
    - cost: The calculated cost for this item
    - cost: The calculated cost for this item
    - records: List of usage record IDs contributing to this item
    - records: List of usage record IDs contributing to this item


    Raises:
    Raises:
    ValueError: If usage_tracker is not set or other required dependencies are missing
    ValueError: If usage_tracker is not set or other required dependencies are missing
    """
    """
    # Generate a cache key
    # Generate a cache key
    cache_key = self._generate_usage_cost_cache_key(
    cache_key = self._generate_usage_cost_cache_key(
    customer_id, start_time, end_time
    customer_id, start_time, end_time
    )
    )


    # Try to get from cache first
    # Try to get from cache first
    cached_result = default_cache.get(
    cached_result = default_cache.get(
    cache_key, namespace="usage_cost_calculations"
    cache_key, namespace="usage_cost_calculations"
    )
    )
    if cached_result is not None:
    if cached_result is not None:
    return cached_result
    return cached_result


    if self.usage_tracker is None:
    if self.usage_tracker is None:
    raise ValueError("Usage tracker is required to calculate usage cost")
    raise ValueError("Usage tracker is required to calculate usage cost")


    # Get usage summary
    # Get usage summary
    summary = self.usage_tracker.get_usage_summary(
    summary = self.usage_tracker.get_usage_summary(
    customer_id=customer_id,
    customer_id=customer_id,
    start_time=start_time,
    start_time=start_time,
    end_time=end_time,
    end_time=end_time,
    group_by="metric",
    group_by="metric",
    )
    )


    # Initialize result
    # Initialize result
    result = {
    result = {
    "customer_id": customer_id,
    "customer_id": customer_id,
    "start_time": start_time.isoformat() if start_time else None,
    "start_time": start_time.isoformat() if start_time else None,
    "end_time": end_time.isoformat() if end_time else None,
    "end_time": end_time.isoformat() if end_time else None,
    "total_cost": 0.0,
    "total_cost": 0.0,
    "items": [],
    "items": [],
    }
    }


    # Calculate cost for each metric
    # Calculate cost for each metric
    if "grouped" in summary:
    if "grouped" in summary:
    for metric, data in summary["grouped"].items():
    for metric, data in summary["grouped"].items():
    data["quantity"]
    data["quantity"]


    # Get all records for this metric
    # Get all records for this metric
    records = []
    records = []
    for record_id in data["records"]:
    for record_id in data["records"]:
    record = self.usage_tracker.get_record(record_id)
    record = self.usage_tracker.get_record(record_id)
    if record:
    if record:
    records.append(record)
    records.append(record)


    # Group records by category and resource type
    # Group records by category and resource type
    grouped_records = {}
    grouped_records = {}
    for record in records:
    for record in records:
    key = (record.category, record.resource_type)
    key = (record.category, record.resource_type)


    if key not in grouped_records:
    if key not in grouped_records:
    grouped_records[key] = {
    grouped_records[key] = {
    "category": record.category,
    "category": record.category,
    "resource_type": record.resource_type,
    "resource_type": record.resource_type,
    "quantity": 0.0,
    "quantity": 0.0,
    "records": [],
    "records": [],
    }
    }


    grouped_records[key]["quantity"] += record.quantity
    grouped_records[key]["quantity"] += record.quantity
    grouped_records[key]["records"].append(record.id)
    grouped_records[key]["records"].append(record.id)


    # Calculate cost for each group
    # Calculate cost for each group
    for key, group_data in grouped_records.items():
    for key, group_data in grouped_records.items():
    category, resource_type = key
    category, resource_type = key
    group_quantity = group_data["quantity"]
    group_quantity = group_data["quantity"]


    cost = self.calculate_cost(
    cost = self.calculate_cost(
    metric=metric,
    metric=metric,
    quantity=group_quantity,
    quantity=group_quantity,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    )
    )


    # Add to result
    # Add to result
    item = {
    item = {
    "metric": metric,
    "metric": metric,
    "category": category,
    "category": category,
    "resource_type": resource_type,
    "resource_type": resource_type,
    "quantity": group_quantity,
    "quantity": group_quantity,
    "cost": cost,
    "cost": cost,
    "records": group_data["records"],
    "records": group_data["records"],
    }
    }


    result["items"].append(item)
    result["items"].append(item)
    result["total_cost"] += cost
    result["total_cost"] += cost


    # Cache the result
    # Cache the result
    default_cache.set(
    default_cache.set(
    cache_key, result, ttl=self.cache_ttl, namespace="usage_cost_calculations"
    cache_key, result, ttl=self.cache_ttl, namespace="usage_cost_calculations"
    )
    )


    return result
    return result


    def _generate_usage_cost_cache_key(
    def _generate_usage_cost_cache_key(
    self,
    self,
    customer_id: str,
    customer_id: str,
    start_time: Optional[datetime],
    start_time: Optional[datetime],
    end_time: Optional[datetime],
    end_time: Optional[datetime],
    ) -> str:
    ) -> str:
    """
    """
    Generate a cache key for usage cost calculations.
    Generate a cache key for usage cost calculations.


    Args:
    Args:
    customer_id: Customer ID
    customer_id: Customer ID
    start_time: Start time
    start_time: Start time
    end_time: End time
    end_time: End time


    Returns:
    Returns:
    Cache key string
    Cache key string
    """
    """
    # Format times as ISO strings or "None"
    # Format times as ISO strings or "None"
    start_str = start_time.isoformat() if start_time else "None"
    start_str = start_time.isoformat() if start_time else "None"
    end_str = end_time.isoformat() if end_time else "None"
    end_str = end_time.isoformat() if end_time else "None"


    key_parts = [f"customer:{customer_id}", f"start:{start_str}", f"end:{end_str}"]
    key_parts = [f"customer:{customer_id}", f"start:{start_str}", f"end:{end_str}"]


    return hashlib.md5("|".join(key_parts).encode()).hexdigest()
    return hashlib.md5("|".join(key_parts).encode()).hexdigest()


    def estimate_cost(
    def estimate_cost(
    self, usage_estimates: Dict[str, Dict[str, float]]
    self, usage_estimates: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Estimate the cost for estimated usage.
    Estimate the cost for estimated usage.


    This algorithm implements a sophisticated cost estimation system that enables predictive
    This algorithm implements a sophisticated cost estimation system that enables predictive
    billing analysis based on anticipated usage patterns. The implementation follows these
    billing analysis based on anticipated usage patterns. The implementation follows these
    key phases:
    key phases:


    1. USAGE PROJECTION PROCESSING:
    1. USAGE PROJECTION PROCESSING:
    - Takes structured usage estimates across multiple service dimensions
    - Takes structured usage estimates across multiple service dimensions
    - Handles multi-metric and multi-category projections in a single calculation
    - Handles multi-metric and multi-category projections in a single calculation
    - Processes arbitrarily complex usage matrices with nested dictionaries
    - Processes arbitrarily complex usage matrices with nested dictionaries
    - Preserves the hierarchical relationship between metrics and categories
    - Preserves the hierarchical relationship between metrics and categories
    - Provides a consistent interface for both simple and complex estimations
    - Provides a consistent interface for both simple and complex estimations


    2. COST PROJECTION CALCULATION:
    2. COST PROJECTION CALCULATION:
    - Applies the appropriate pricing rules to each usage estimate
    - Applies the appropriate pricing rules to each usage estimate
    - Properly matches pricing rules with specific metric/category combinations
    - Properly matches pricing rules with specific metric/category combinations
    - Ensures consistent pricing application across different estimation scenarios
    - Ensures consistent pricing application across different estimation scenarios
    - Retains the multi-dimensional nature of the cost structure
    - Retains the multi-dimensional nature of the cost structure
    - Produces itemized cost projections for detailed analysis
    - Produces itemized cost projections for detailed analysis


    3. CONSOLIDATED RESULT CREATION:
    3. CONSOLIDATED RESULT CREATION:
    - Assembles a comprehensive cost projection summary
    - Assembles a comprehensive cost projection summary
    - Preserves the full breakdown of individual cost components
    - Preserves the full breakdown of individual cost components
    - Calculates accurate total cost across all dimensions
    - Calculates accurate total cost across all dimensions
    - Returns a structured response suitable for presentation or further analysis
    - Returns a structured response suitable for presentation or further analysis
    - Facilitates cost optimization through transparent itemization
    - Facilitates cost optimization through transparent itemization


    This algorithm serves several critical business functions:
    This algorithm serves several critical business functions:
    - Budget planning and cost forecasting for customers
    - Budget planning and cost forecasting for customers
    - "What-if" scenario analysis for usage pattern changes
    - "What-if" scenario analysis for usage pattern changes
    - Cost optimization consulting for enterprise customers
    - Cost optimization consulting for enterprise customers
    - New feature financial impact assessment
    - New feature financial impact assessment
    - Tier upgrade recommendations for customers approaching usage thresholds
    - Tier upgrade recommendations for customers approaching usage thresholds


    The estimate_cost method is particularly valuable for enterprise customers with
    The estimate_cost method is particularly valuable for enterprise customers with
    complex usage patterns across multiple service dimensions, enabling them to:
    complex usage patterns across multiple service dimensions, enabling them to:
    - Plan resource allocation across departments
    - Plan resource allocation across departments
    - Forecast costs based on expected growth trends
    - Forecast costs based on expected growth trends
    - Compare different usage strategies for cost efficiency
    - Compare different usage strategies for cost efficiency
    - Understand cost implications of changing usage patterns
    - Understand cost implications of changing usage patterns
    - Evaluate price elasticity for different service components
    - Evaluate price elasticity for different service components


    Args:
    Args:
    usage_estimates: A nested dictionary structure with the following format:
    usage_estimates: A nested dictionary structure with the following format:
    {
    {
    "metric1": {
    "metric1": {
    "category1": quantity1,
    "category1": quantity1,
    "category2": quantity2,
    "category2": quantity2,
    ...
    ...
    },
    },
    "metric2": {
    "metric2": {
    "category1": quantity3,
    "category1": quantity3,
    ...
    ...
    },
    },
    ...
    ...
    }
    }
    Where metrics are strings identifying the type of usage (e.g., "API_CALL"),
    Where metrics are strings identifying the type of usage (e.g., "API_CALL"),
    categories are strings identifying usage categories (e.g., "INFERENCE"),
    categories are strings identifying usage categories (e.g., "INFERENCE"),
    and quantities are float values representing the estimated usage amount.
    and quantities are float values representing the estimated usage amount.


    Returns:
    Returns:
    A dictionary containing:
    A dictionary containing:
    - total_cost: The aggregate projected cost across all metrics and categories
    - total_cost: The aggregate projected cost across all metrics and categories
    - items: A list of itemized cost projections, each containing:
    - items: A list of itemized cost projections, each containing:
    - metric: The specific service metric
    - metric: The specific service metric
    - category: The usage category for this estimate
    - category: The usage category for this estimate
    - quantity: The projected usage quantity
    - quantity: The projected usage quantity
    - cost: The calculated cost for this specific item
    - cost: The calculated cost for this specific item


    Example:
    Example:
    usage_estimates = {
    usage_estimates = {
    "API_CALL": {"INFERENCE": 10000, "TRAINING": 5000},
    "API_CALL": {"INFERENCE": 10000, "TRAINING": 5000},
    "TOKEN": {"INFERENCE": 50000}
    "TOKEN": {"INFERENCE": 50000}
    }
    }
    result = calculator.estimate_cost(usage_estimates)
    result = calculator.estimate_cost(usage_estimates)
    # result = {
    # result = {
    #     "total_cost": 135.0,
    #     "total_cost": 135.0,
    #     "items": [
    #     "items": [
    #         {"metric": "API_CALL", "category": "INFERENCE", "quantity": 10000, "cost": 100.0},
    #         {"metric": "API_CALL", "category": "INFERENCE", "quantity": 10000, "cost": 100.0},
    #         {"metric": "API_CALL", "category": "TRAINING", "quantity": 5000, "cost": 25.0},
    #         {"metric": "API_CALL", "category": "TRAINING", "quantity": 5000, "cost": 25.0},
    #         {"metric": "TOKEN", "category": "INFERENCE", "quantity": 50000, "cost": 10.0}
    #         {"metric": "TOKEN", "category": "INFERENCE", "quantity": 50000, "cost": 10.0}
    #     ]
    #     ]
    # }
    # }
    """
    """
    # Generate a cache key for these usage estimates
    # Generate a cache key for these usage estimates
    cache_key = self._generate_estimate_cache_key(usage_estimates)
    cache_key = self._generate_estimate_cache_key(usage_estimates)


    # Try to get from cache first
    # Try to get from cache first
    cached_result = default_cache.get(cache_key, namespace="cost_estimates")
    cached_result = default_cache.get(cache_key, namespace="cost_estimates")
    if cached_result is not None:
    if cached_result is not None:
    return cached_result
    return cached_result


    # Initialize result
    # Initialize result
    result = {"total_cost": 0.0, "items": []}
    result = {"total_cost": 0.0, "items": []}


    # Calculate cost for each metric and category
    # Calculate cost for each metric and category
    for metric, categories in usage_estimates.items():
    for metric, categories in usage_estimates.items():
    for category, quantity in categories.items():
    for category, quantity in categories.items():
    cost = self.calculate_cost(
    cost = self.calculate_cost(
    metric=metric, quantity=quantity, category=category
    metric=metric, quantity=quantity, category=category
    )
    )


    # Add to result
    # Add to result
    item = {
    item = {
    "metric": metric,
    "metric": metric,
    "category": category,
    "category": category,
    "quantity": quantity,
    "quantity": quantity,
    "cost": cost,
    "cost": cost,
    }
    }


    result["items"].append(item)
    result["items"].append(item)
    result["total_cost"] += cost
    result["total_cost"] += cost


    # Cache the result
    # Cache the result
    default_cache.set(
    default_cache.set(
    cache_key, result, ttl=self.cache_ttl, namespace="cost_estimates"
    cache_key, result, ttl=self.cache_ttl, namespace="cost_estimates"
    )
    )


    return result
    return result


    def _generate_estimate_cache_key(
    def _generate_estimate_cache_key(
    self, usage_estimates: Dict[str, Dict[str, float]]
    self, usage_estimates: Dict[str, Dict[str, float]]
    ) -> str:
    ) -> str:
    """
    """
    Generate a cache key for cost estimations.
    Generate a cache key for cost estimations.


    Args:
    Args:
    usage_estimates: Usage estimates dictionary
    usage_estimates: Usage estimates dictionary


    Returns:
    Returns:
    Cache key string
    Cache key string
    """
    """
    # Convert the nested dict to a stable string representation
    # Convert the nested dict to a stable string representation
    usage_str = json.dumps(usage_estimates, sort_keys=True)
    usage_str = json.dumps(usage_estimates, sort_keys=True)


    # Create a hash of the string
    # Create a hash of the string
    return hashlib.md5(usage_str.encode()).hexdigest()
    return hashlib.md5(usage_str.encode()).hexdigest()


    def invalidate_cost_cache(self) -> None:
    def invalidate_cost_cache(self) -> None:
    """Invalidate all cost calculation caches."""
    default_cache.clear(namespace="cost_calculations")
    default_cache.clear(namespace="usage_cost_calculations")
    default_cache.clear(namespace="cost_estimates")

    def set_cache_ttl(self, ttl_seconds: int) -> None:
    """
    """
    Set the cache TTL (time to live) for cost calculations.
    Set the cache TTL (time to live) for cost calculations.


    Args:
    Args:
    ttl_seconds: Cache TTL in seconds
    ttl_seconds: Cache TTL in seconds
    """
    """
    self.cache_ttl = ttl_seconds
    self.cache_ttl = ttl_seconds




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a usage tracker
    # Create a usage tracker
    tracker = UsageTracker()
    tracker = UsageTracker()


    # Create a billing calculator
    # Create a billing calculator
    calculator = BillingCalculator(usage_tracker=tracker)
    calculator = BillingCalculator(usage_tracker=tracker)


    # Add pricing rules
    # Add pricing rules
    calculator.create_per_unit_pricing_rule(
    calculator.create_per_unit_pricing_rule(
    metric=UsageMetric.API_CALL,
    metric=UsageMetric.API_CALL,
    price_per_unit=0.01,
    price_per_unit=0.01,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    )
    )


    calculator.create_tiered_pricing_rule(
    calculator.create_tiered_pricing_rule(
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


    calculator.create_package_pricing_rule(
    calculator.create_package_pricing_rule(
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


    # Calculate costs
    # Calculate costs
    api_cost = calculator.calculate_cost(
    api_cost = calculator.calculate_cost(
    metric=UsageMetric.API_CALL, quantity=100, category=UsageCategory.INFERENCE
    metric=UsageMetric.API_CALL, quantity=100, category=UsageCategory.INFERENCE
    )
    )


    token_cost = calculator.calculate_cost(
    token_cost = calculator.calculate_cost(
    metric=UsageMetric.TOKEN, quantity=5000, category=UsageCategory.INFERENCE
    metric=UsageMetric.TOKEN, quantity=5000, category=UsageCategory.INFERENCE
    )
    )


    storage_cost = calculator.calculate_cost(
    storage_cost = calculator.calculate_cost(
    metric=UsageMetric.STORAGE, quantity=15.0, category=UsageCategory.STORAGE
    metric=UsageMetric.STORAGE, quantity=15.0, category=UsageCategory.STORAGE
    )
    )


    print(f"API call cost: ${api_cost:.2f}")
    print(f"API call cost: ${api_cost:.2f}")
    print(f"Token cost: ${token_cost:.2f}"
    print(f"Token cost: ${token_cost:.2f}"
    print(f"Storage cost: ${storage_cost:.2f}"
    print(f"Storage cost: ${storage_cost:.2f}"


    # Estimate total cost
    # Estimate total cost
    estimated_cost = calculator.estimate_cost(
    estimated_cost = calculator.estimate_cost(
    {
    {
    UsageMetric.API_CALL: {UsageCategory.INFERENCE: 100},
    UsageMetric.API_CALL: {UsageCategory.INFERENCE: 100},
    UsageMetric.TOKEN: {UsageCategory.INFERENCE: 5000},
    UsageMetric.TOKEN: {UsageCategory.INFERENCE: 5000},
    UsageMetric.STORAGE: {UsageCategory.STORAGE: 15.0},
    UsageMetric.STORAGE: {UsageCategory.STORAGE: 15.0},
    }
    }




    print(f"\nEstimated total cost: ${estimated_cost['total_cost']:.2f}"
    print(f"\nEstimated total cost: ${estimated_cost['total_cost']:.2f}"


    for item in estimated_cost["items"]:
    for item in estimated_cost["items"]:
    print(
    print(
    f"- {item['metric']} ({item['category']}: {item['quantity']} units, ${item['cost']:.2f}"
    f"- {item['metric']} ({item['category']}: {item['quantity']} units, ${item['cost']:.2f}"

