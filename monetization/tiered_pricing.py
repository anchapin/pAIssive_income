"""
"""
Tiered pricing for the pAIssive Income project.
Tiered pricing for the pAIssive Income project.


This module provides classes for implementing tiered pricing models,
This module provides classes for implementing tiered pricing models,
including volume discounts and graduated pricing.
including volume discounts and graduated pricing.
"""
"""




from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .usage_tracking import UsageCategory, UsageMetric
from .usage_tracking import UsageCategory, UsageMetric




class VolumeDiscount
class VolumeDiscount


(
(
BillingCalculator,
BillingCalculator,
PricingModel,
PricingModel,
PricingRule,
PricingRule,
PricingTier,
PricingTier,
)
)
:
    :
    """
    """
    Class representing a volume discount.
    Class representing a volume discount.


    This class provides a structured way to represent a volume discount,
    This class provides a structured way to represent a volume discount,
    including the minimum quantity and discount percentage.
    including the minimum quantity and discount percentage.
    """
    """


    def __init__(self, min_quantity: float, discount_percentage: float):
    def __init__(self, min_quantity: float, discount_percentage: float):
    """
    """
    Initialize a volume discount.
    Initialize a volume discount.


    Args:
    Args:
    min_quantity: Minimum quantity for this discount
    min_quantity: Minimum quantity for this discount
    discount_percentage: Discount percentage (0-100)
    discount_percentage: Discount percentage (0-100)
    """
    """
    self.min_quantity = min_quantity
    self.min_quantity = min_quantity
    self.discount_percentage = discount_percentage
    self.discount_percentage = discount_percentage


    def applies_to(self, quantity: float) -> bool:
    def applies_to(self, quantity: float) -> bool:
    """
    """
    Check if this discount applies to a quantity.
    Check if this discount applies to a quantity.


    Args:
    Args:
    quantity: Quantity to check
    quantity: Quantity to check


    Returns:
    Returns:
    True if this discount applies, False otherwise
    True if this discount applies, False otherwise
    """
    """
    return quantity >= self.min_quantity
    return quantity >= self.min_quantity


    def apply_discount(self, cost: float) -> float:
    def apply_discount(self, cost: float) -> float:
    """
    """
    Apply the discount to a cost.
    Apply the discount to a cost.


    Args:
    Args:
    cost: Cost to apply discount to
    cost: Cost to apply discount to


    Returns:
    Returns:
    Discounted cost
    Discounted cost
    """
    """
    discount = cost * (self.discount_percentage / 100.0)
    discount = cost * (self.discount_percentage / 100.0)
    return cost - discount
    return cost - discount


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the volume discount to a dictionary.
    Convert the volume discount to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the volume discount
    Dictionary representation of the volume discount
    """
    """
    return {
    return {
    "min_quantity": self.min_quantity,
    "min_quantity": self.min_quantity,
    "discount_percentage": self.discount_percentage,
    "discount_percentage": self.discount_percentage,
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VolumeDiscount":
    def from_dict(cls, data: Dict[str, Any]) -> "VolumeDiscount":
    """
    """
    Create a volume discount from a dictionary.
    Create a volume discount from a dictionary.


    Args:
    Args:
    data: Dictionary with volume discount data
    data: Dictionary with volume discount data


    Returns:
    Returns:
    VolumeDiscount instance
    VolumeDiscount instance
    """
    """
    return cls(
    return cls(
    min_quantity=data["min_quantity"],
    min_quantity=data["min_quantity"],
    discount_percentage=data["discount_percentage"],
    discount_percentage=data["discount_percentage"],
    )
    )


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the volume discount."""
    return f"VolumeDiscount({self.min_quantity}+ units, {self.discount_percentage}% off)"


    class TieredPricingRule(PricingRule):
    """
    """
    Class representing a tiered pricing rule with volume discounts.
    Class representing a tiered pricing rule with volume discounts.


    This class extends the PricingRule class to add support for volume discounts.
    This class extends the PricingRule class to add support for volume discounts.
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
    tiers: List[PricingTier],
    tiers: List[PricingTier],
    volume_discounts: Optional[List[VolumeDiscount]] = None,
    volume_discounts: Optional[List[VolumeDiscount]] = None,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    ):
    ):
    """
    """
    Initialize a tiered pricing rule with volume discounts.
    Initialize a tiered pricing rule with volume discounts.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    model: Pricing model (e.g., TIERED, GRADUATED)
    model: Pricing model (e.g., TIERED, GRADUATED)
    tiers: List of pricing tiers
    tiers: List of pricing tiers
    volume_discounts: List of volume discounts
    volume_discounts: List of volume discounts
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource
    minimum_cost: Minimum cost
    minimum_cost: Minimum cost
    maximum_cost: Maximum cost
    maximum_cost: Maximum cost
    """
    """
    super().__init__(
    super().__init__(
    metric=metric,
    metric=metric,
    model=model,
    model=model,
    tiers=tiers,
    tiers=tiers,
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


    self.volume_discounts = volume_discounts or []
    self.volume_discounts = volume_discounts or []


    def calculate_cost(self, quantity: float) -> float:
    def calculate_cost(self, quantity: float) -> float:
    """
    """
    Calculate the cost for a quantity using this rule.
    Calculate the cost for a quantity using this rule.


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
    # Calculate base cost using parent method
    # Calculate base cost using parent method
    cost = super().calculate_cost(quantity)
    cost = super().calculate_cost(quantity)


    # Apply volume discounts
    # Apply volume discounts
    for discount in sorted(
    for discount in sorted(
    self.volume_discounts, key=lambda d: d.min_quantity, reverse=True
    self.volume_discounts, key=lambda d: d.min_quantity, reverse=True
    ):
    ):
    if discount.applies_to(quantity):
    if discount.applies_to(quantity):
    cost = discount.apply_discount(cost)
    cost = discount.apply_discount(cost)
    break
    break


    return cost
    return cost


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the tiered pricing rule to a dictionary.
    Convert the tiered pricing rule to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the tiered pricing rule
    Dictionary representation of the tiered pricing rule
    """
    """
    result = super().to_dict()
    result = super().to_dict()


    if self.volume_discounts:
    if self.volume_discounts:
    result["volume_discounts"] = [
    result["volume_discounts"] = [
    discount.to_dict() for discount in self.volume_discounts
    discount.to_dict() for discount in self.volume_discounts
    ]
    ]


    return result
    return result


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TieredPricingRule":
    def from_dict(cls, data: Dict[str, Any]) -> "TieredPricingRule":
    """
    """
    Create a tiered pricing rule from a dictionary.
    Create a tiered pricing rule from a dictionary.


    Args:
    Args:
    data: Dictionary with tiered pricing rule data
    data: Dictionary with tiered pricing rule data


    Returns:
    Returns:
    TieredPricingRule instance
    TieredPricingRule instance
    """
    """
    tiers = [PricingTier.from_dict(tier_data) for tier_data in data["tiers"]]
    tiers = [PricingTier.from_dict(tier_data) for tier_data in data["tiers"]]


    volume_discounts = None
    volume_discounts = None
    if "volume_discounts" in data:
    if "volume_discounts" in data:
    volume_discounts = [
    volume_discounts = [
    VolumeDiscount.from_dict(discount_data)
    VolumeDiscount.from_dict(discount_data)
    for discount_data in data["volume_discounts"]
    for discount_data in data["volume_discounts"]
    ]
    ]


    return cls(
    return cls(
    metric=data["metric"],
    metric=data["metric"],
    model=data["model"],
    model=data["model"],
    tiers=tiers,
    tiers=tiers,
    volume_discounts=volume_discounts,
    volume_discounts=volume_discounts,
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




    class TieredPricingCalculator(BillingCalculator):
    class TieredPricingCalculator(BillingCalculator):
    """
    """
    Class for calculating billing based on tiered pricing.
    Class for calculating billing based on tiered pricing.


    This class extends the BillingCalculator class to add support for
    This class extends the BillingCalculator class to add support for
    tiered pricing with volume discounts.
    tiered pricing with volume discounts.
    """
    """


    def create_tiered_pricing_rule_with_discounts(
    def create_tiered_pricing_rule_with_discounts(
    self,
    self,
    metric: str,
    metric: str,
    tiers: List[Dict[str, Any]],
    tiers: List[Dict[str, Any]],
    volume_discounts: List[Dict[str, Any]],
    volume_discounts: List[Dict[str, Any]],
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
    ) -> TieredPricingRule:
    ) -> TieredPricingRule:
    """
    """
    Create a tiered pricing rule with volume discounts.
    Create a tiered pricing rule with volume discounts.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    tiers: List of tier dictionaries with min_quantity, max_quantity, and price_per_unit
    tiers: List of tier dictionaries with min_quantity, max_quantity, and price_per_unit
    volume_discounts: List of discount dictionaries with min_quantity and discount_percentage
    volume_discounts: List of discount dictionaries with min_quantity and discount_percentage
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
    Tiered pricing rule with volume discounts
    Tiered pricing rule with volume discounts
    """
    """
    pricing_tiers = []
    pricing_tiers = []


    for tier_data in tiers:
    for tier_data in tiers:
    tier = PricingTier(
    tier = PricingTier(
    min_quantity=tier_data["min_quantity"],
    min_quantity=tier_data["min_quantity"],
    max_quantity=tier_data.get("max_quantity"),
    max_quantity=tier_data.get("max_quantity"),
    price_per_unit=tier_data["price_per_unit"],
    price_per_unit=tier_data["price_per_unit"],
    flat_fee=tier_data.get("flat_fee", 0.0),
    flat_fee=tier_data.get("flat_fee", 0.0),
    )
    )


    pricing_tiers.append(tier)
    pricing_tiers.append(tier)


    # Sort tiers by min_quantity
    # Sort tiers by min_quantity
    pricing_tiers.sort(key=lambda t: t.min_quantity)
    pricing_tiers.sort(key=lambda t: t.min_quantity)


    pricing_discounts = []
    pricing_discounts = []


    for discount_data in volume_discounts:
    for discount_data in volume_discounts:
    discount = VolumeDiscount(
    discount = VolumeDiscount(
    min_quantity=discount_data["min_quantity"],
    min_quantity=discount_data["min_quantity"],
    discount_percentage=discount_data["discount_percentage"],
    discount_percentage=discount_data["discount_percentage"],
    )
    )


    pricing_discounts.append(discount)
    pricing_discounts.append(discount)


    # Sort discounts by min_quantity
    # Sort discounts by min_quantity
    pricing_discounts.sort(key=lambda d: d.min_quantity)
    pricing_discounts.sort(key=lambda d: d.min_quantity)


    rule = TieredPricingRule(
    rule = TieredPricingRule(
    metric=metric,
    metric=metric,
    model=PricingModel.GRADUATED if graduated else PricingModel.TIERED,
    model=PricingModel.GRADUATED if graduated else PricingModel.TIERED,
    tiers=pricing_tiers,
    tiers=pricing_tiers,
    volume_discounts=pricing_discounts,
    volume_discounts=pricing_discounts,
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


    self.add_pricing_rule(rule)
    self.add_pricing_rule(rule)


    return rule
    return rule


    def calculate_tiered_cost_breakdown(
    def calculate_tiered_cost_breakdown(
    self,
    self,
    metric: str,
    metric: str,
    quantity: float,
    quantity: float,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate a detailed breakdown of tiered costs.
    Calculate a detailed breakdown of tiered costs.


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
    Dictionary with cost breakdown details
    Dictionary with cost breakdown details
    """
    """
    rule = self.get_pricing_rule(metric, category, resource_type)
    rule = self.get_pricing_rule(metric, category, resource_type)


    if rule is None or not hasattr(rule, "tiers") or not rule.tiers:
    if rule is None or not hasattr(rule, "tiers") or not rule.tiers:
    return {
    return {
    "metric": metric,
    "metric": metric,
    "quantity": quantity,
    "quantity": quantity,
    "cost": self.calculate_cost(metric, quantity, category, resource_type),
    "cost": self.calculate_cost(metric, quantity, category, resource_type),
    "tiers": [],
    "tiers": [],
    "volume_discount": None,
    "volume_discount": None,
    }
    }


    # Initialize result
    # Initialize result
    result = {
    result = {
    "metric": metric,
    "metric": metric,
    "quantity": quantity,
    "quantity": quantity,
    "model": rule.model,
    "model": rule.model,
    "tiers": [],
    "tiers": [],
    "volume_discount": None,
    "volume_discount": None,
    "subtotal": 0.0,
    "subtotal": 0.0,
    "total": 0.0,
    "total": 0.0,
    }
    }


    # Calculate cost for each tier
    # Calculate cost for each tier
    graduated = rule.model == PricingModel.GRADUATED
    graduated = rule.model == PricingModel.GRADUATED


    for tier in rule.tiers:
    for tier in rule.tiers:
    tier_quantity = (
    tier_quantity = (
    tier.get_quantity_in_tier(quantity)
    tier.get_quantity_in_tier(quantity)
    if graduated
    if graduated
    else (quantity if tier.contains(quantity) else 0.0)
    else (quantity if tier.contains(quantity) else 0.0)
    )
    )


    tier_cost = tier.calculate_cost(quantity, graduated=graduated)
    tier_cost = tier.calculate_cost(quantity, graduated=graduated)


    if tier_quantity > 0 or tier_cost > 0:
    if tier_quantity > 0 or tier_cost > 0:
    tier_info = {
    tier_info = {
    "min_quantity": tier.min_quantity,
    "min_quantity": tier.min_quantity,
    "max_quantity": tier.max_quantity,
    "max_quantity": tier.max_quantity,
    "price_per_unit": tier.price_per_unit,
    "price_per_unit": tier.price_per_unit,
    "flat_fee": tier.flat_fee,
    "flat_fee": tier.flat_fee,
    "quantity": tier_quantity,
    "quantity": tier_quantity,
    "cost": tier_cost,
    "cost": tier_cost,
    }
    }


    result["tiers"].append(tier_info)
    result["tiers"].append(tier_info)
    result["subtotal"] += tier_cost
    result["subtotal"] += tier_cost


    # Apply volume discounts
    # Apply volume discounts
    result["total"] = result["subtotal"]
    result["total"] = result["subtotal"]


    if hasattr(rule, "volume_discounts") and rule.volume_discounts:
    if hasattr(rule, "volume_discounts") and rule.volume_discounts:
    for discount in sorted(
    for discount in sorted(
    rule.volume_discounts, key=lambda d: d.min_quantity, reverse=True
    rule.volume_discounts, key=lambda d: d.min_quantity, reverse=True
    ):
    ):
    if discount.applies_to(quantity):
    if discount.applies_to(quantity):
    discounted_cost = discount.apply_discount(result["subtotal"])
    discounted_cost = discount.apply_discount(result["subtotal"])
    discount_amount = result["subtotal"] - discounted_cost
    discount_amount = result["subtotal"] - discounted_cost


    result["volume_discount"] = {
    result["volume_discount"] = {
    "min_quantity": discount.min_quantity,
    "min_quantity": discount.min_quantity,
    "discount_percentage": discount.discount_percentage,
    "discount_percentage": discount.discount_percentage,
    "discount_amount": discount_amount,
    "discount_amount": discount_amount,
    }
    }


    result["total"] = discounted_cost
    result["total"] = discounted_cost
    break
    break


    # Apply minimum and maximum costs
    # Apply minimum and maximum costs
    if result["total"] < rule.minimum_cost:
    if result["total"] < rule.minimum_cost:
    result["total"] = rule.minimum_cost
    result["total"] = rule.minimum_cost
    result["minimum_cost_applied"] = True
    result["minimum_cost_applied"] = True
    else:
    else:
    result["minimum_cost_applied"] = False
    result["minimum_cost_applied"] = False


    if rule.maximum_cost is not None and result["total"] > rule.maximum_cost:
    if rule.maximum_cost is not None and result["total"] > rule.maximum_cost:
    result["total"] = rule.maximum_cost
    result["total"] = rule.maximum_cost
    result["maximum_cost_applied"] = True
    result["maximum_cost_applied"] = True
    else:
    else:
    result["maximum_cost_applied"] = False
    result["maximum_cost_applied"] = False


    return result
    return result




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a tiered pricing calculator
    # Create a tiered pricing calculator
    calculator = TieredPricingCalculator()
    calculator = TieredPricingCalculator()


    # Add a tiered pricing rule with volume discounts
    # Add a tiered pricing rule with volume discounts
    calculator.create_tiered_pricing_rule_with_discounts(
    calculator.create_tiered_pricing_rule_with_discounts(
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
    volume_discounts=[
    volume_discounts=[
    {"min_quantity": 100000, "discount_percentage": 10},
    {"min_quantity": 100000, "discount_percentage": 10},
    {"min_quantity": 1000000, "discount_percentage": 20},
    {"min_quantity": 1000000, "discount_percentage": 20},
    ],
    ],
    graduated=True,
    graduated=True,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    )
    )


    # Calculate cost
    # Calculate cost
    cost = calculator.calculate_cost(
    cost = calculator.calculate_cost(
    metric=UsageMetric.TOKEN, quantity=150000, category=UsageCategory.INFERENCE
    metric=UsageMetric.TOKEN, quantity=150000, category=UsageCategory.INFERENCE
    )
    )


    print(f"Cost for 150,000 tokens: ${cost:.2f}")
    print(f"Cost for 150,000 tokens: ${cost:.2f}")


    # Get detailed cost breakdown
    # Get detailed cost breakdown
    breakdown = calculator.calculate_tiered_cost_breakdown(
    breakdown = calculator.calculate_tiered_cost_breakdown(
    metric=UsageMetric.TOKEN, quantity=150000, category=UsageCategory.INFERENCE
    metric=UsageMetric.TOKEN, quantity=150000, category=UsageCategory.INFERENCE
    )
    )


    print("\nCost breakdown:")
    print("\nCost breakdown:")
    print(f"Model: {breakdown['model']}")
    print(f"Model: {breakdown['model']}")
    print(f"Quantity: {breakdown['quantity']}")
    print(f"Quantity: {breakdown['quantity']}")


    print("\nTiers:")
    print("\nTiers:")
    for tier in breakdown["tiers"]:
    for tier in breakdown["tiers"]:
    max_str = str(tier["max_quantity"]) if tier["max_quantity"] is not None else "∞"
    max_str = str(tier["max_quantity"]) if tier["max_quantity"] is not None else "∞"
    print(
    print(
    f"- {tier['min_quantity']}-{max_str}: {tier['quantity']} units at ${tier['price_per_unit']}/unit = ${tier['cost']:.2f}"
    f"- {tier['min_quantity']}-{max_str}: {tier['quantity']} units at ${tier['price_per_unit']}/unit = ${tier['cost']:.2f}"
    )
    )


    print(f"\nSubtotal: ${breakdown['subtotal']:.2f}")
    print(f"\nSubtotal: ${breakdown['subtotal']:.2f}")


    if breakdown["volume_discount"]:
    if breakdown["volume_discount"]:
    discount = breakdown["volume_discount"]
    discount = breakdown["volume_discount"]
    print(
    print(
    f"Volume discount: {discount['discount_percentage']}% off for {discount['min_quantity']}+ units = -${discount['discount_amount']:.2f}"
    f"Volume discount: {discount['discount_percentage']}% off for {discount['min_quantity']}+ units = -${discount['discount_amount']:.2f}"
    )
    )


    print(f"Total: ${breakdown['total']:.2f}")
    print(f"Total: ${breakdown['total']:.2f}")