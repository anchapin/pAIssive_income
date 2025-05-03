"""
Tiered pricing for the pAIssive Income project.

This module provides classes for implementing tiered pricing models,
including volume discounts and graduated pricing.
"""


from typing import Any, Dict, List, Optional

from .billing_calculator import 
from .usage_tracking import UsageCategory, UsageMetric


class VolumeDiscount

(
    BillingCalculator,
    PricingModel,
    PricingRule,
    PricingTier,
)
:
    """
    Class representing a volume discount.

    This class provides a structured way to represent a volume discount,
    including the minimum quantity and discount percentage.
    """

    def __init__(self, min_quantity: float, discount_percentage: float):
        """
        Initialize a volume discount.

        Args:
            min_quantity: Minimum quantity for this discount
            discount_percentage: Discount percentage (0-100)
        """
        self.min_quantity = min_quantity
        self.discount_percentage = discount_percentage

    def applies_to(self, quantity: float) -> bool:
        """
        Check if this discount applies to a quantity.

        Args:
            quantity: Quantity to check

        Returns:
            True if this discount applies, False otherwise
        """
        return quantity >= self.min_quantity

    def apply_discount(self, cost: float) -> float:
        """
        Apply the discount to a cost.

        Args:
            cost: Cost to apply discount to

        Returns:
            Discounted cost
        """
        discount = cost * (self.discount_percentage / 100.0)
        return cost - discount

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the volume discount to a dictionary.

        Returns:
            Dictionary representation of the volume discount
        """
        return {
            "min_quantity": self.min_quantity,
            "discount_percentage": self.discount_percentage,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VolumeDiscount":
        """
        Create a volume discount from a dictionary.

        Args:
            data: Dictionary with volume discount data

        Returns:
            VolumeDiscount instance
        """
        return cls(
            min_quantity=data["min_quantity"],
            discount_percentage=data["discount_percentage"],
        )

    def __str__(self) -> str:
        """String representation of the volume discount."""
        return f"VolumeDiscount({self.min_quantity}+ units, {self.discount_percentage}% off)"


class TieredPricingRule(PricingRule):
    """
    Class representing a tiered pricing rule with volume discounts.

    This class extends the PricingRule class to add support for volume discounts.
    """

    def __init__(
        self,
        metric: str,
        model: str,
        tiers: List[PricingTier],
        volume_discounts: Optional[List[VolumeDiscount]] = None,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
    ):
        """
        Initialize a tiered pricing rule with volume discounts.

        Args:
            metric: Type of usage metric
            model: Pricing model (e.g., TIERED, GRADUATED)
            tiers: List of pricing tiers
            volume_discounts: List of volume discounts
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost
        """
        super().__init__(
            metric=metric,
            model=model,
            tiers=tiers,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
        )

        self.volume_discounts = volume_discounts or []

    def calculate_cost(self, quantity: float) -> float:
        """
        Calculate the cost for a quantity using this rule.

        Args:
            quantity: Quantity to calculate cost for

        Returns:
            Cost for the quantity
        """
        # Calculate base cost using parent method
        cost = super().calculate_cost(quantity)

        # Apply volume discounts
        for discount in sorted(
            self.volume_discounts, key=lambda d: d.min_quantity, reverse=True
        ):
            if discount.applies_to(quantity):
                cost = discount.apply_discount(cost)
                break

        return cost

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tiered pricing rule to a dictionary.

        Returns:
            Dictionary representation of the tiered pricing rule
        """
        result = super().to_dict()

        if self.volume_discounts:
            result["volume_discounts"] = [
                discount.to_dict() for discount in self.volume_discounts
            ]

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TieredPricingRule":
        """
        Create a tiered pricing rule from a dictionary.

        Args:
            data: Dictionary with tiered pricing rule data

        Returns:
            TieredPricingRule instance
        """
        tiers = [PricingTier.from_dict(tier_data) for tier_data in data["tiers"]]

        volume_discounts = None
        if "volume_discounts" in data:
            volume_discounts = [
                VolumeDiscount.from_dict(discount_data)
                for discount_data in data["volume_discounts"]
            ]

        return cls(
            metric=data["metric"],
            model=data["model"],
            tiers=tiers,
            volume_discounts=volume_discounts,
            category=data.get("category"),
            resource_type=data.get("resource_type"),
            minimum_cost=data.get("minimum_cost", 0.0),
            maximum_cost=data.get("maximum_cost"),
        )


class TieredPricingCalculator(BillingCalculator):
    """
    Class for calculating billing based on tiered pricing.

    This class extends the BillingCalculator class to add support for
    tiered pricing with volume discounts.
    """

    def create_tiered_pricing_rule_with_discounts(
        self,
        metric: str,
        tiers: List[Dict[str, Any]],
        volume_discounts: List[Dict[str, Any]],
        graduated: bool = False,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
    ) -> TieredPricingRule:
        """
        Create a tiered pricing rule with volume discounts.

        Args:
            metric: Type of usage metric
            tiers: List of tier dictionaries with min_quantity, max_quantity, and price_per_unit
            volume_discounts: List of discount dictionaries with min_quantity and discount_percentage
            graduated: Whether to use graduated pricing
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost

        Returns:
            Tiered pricing rule with volume discounts
        """
        pricing_tiers = []

        for tier_data in tiers:
            tier = PricingTier(
                min_quantity=tier_data["min_quantity"],
                max_quantity=tier_data.get("max_quantity"),
                price_per_unit=tier_data["price_per_unit"],
                flat_fee=tier_data.get("flat_fee", 0.0),
            )

            pricing_tiers.append(tier)

        # Sort tiers by min_quantity
        pricing_tiers.sort(key=lambda t: t.min_quantity)

        pricing_discounts = []

        for discount_data in volume_discounts:
            discount = VolumeDiscount(
                min_quantity=discount_data["min_quantity"],
                discount_percentage=discount_data["discount_percentage"],
            )

            pricing_discounts.append(discount)

        # Sort discounts by min_quantity
        pricing_discounts.sort(key=lambda d: d.min_quantity)

        rule = TieredPricingRule(
            metric=metric,
            model=PricingModel.GRADUATED if graduated else PricingModel.TIERED,
            tiers=pricing_tiers,
            volume_discounts=pricing_discounts,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
        )

        self.add_pricing_rule(rule)

        return rule

    def calculate_tiered_cost_breakdown(
        self,
        metric: str,
        quantity: float,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate a detailed breakdown of tiered costs.

        Args:
            metric: Type of usage metric
            quantity: Quantity to calculate cost for
            category: Category of usage
            resource_type: Type of resource

        Returns:
            Dictionary with cost breakdown details
        """
        rule = self.get_pricing_rule(metric, category, resource_type)

        if rule is None or not hasattr(rule, "tiers") or not rule.tiers:
            return {
                "metric": metric,
                "quantity": quantity,
                "cost": self.calculate_cost(metric, quantity, category, resource_type),
                "tiers": [],
                "volume_discount": None,
            }

        # Initialize result
        result = {
            "metric": metric,
            "quantity": quantity,
            "model": rule.model,
            "tiers": [],
            "volume_discount": None,
            "subtotal": 0.0,
            "total": 0.0,
        }

        # Calculate cost for each tier
        graduated = rule.model == PricingModel.GRADUATED

        for tier in rule.tiers:
            tier_quantity = (
                tier.get_quantity_in_tier(quantity)
                if graduated
                else (quantity if tier.contains(quantity) else 0.0)
            )

            tier_cost = tier.calculate_cost(quantity, graduated=graduated)

            if tier_quantity > 0 or tier_cost > 0:
                tier_info = {
                    "min_quantity": tier.min_quantity,
                    "max_quantity": tier.max_quantity,
                    "price_per_unit": tier.price_per_unit,
                    "flat_fee": tier.flat_fee,
                    "quantity": tier_quantity,
                    "cost": tier_cost,
                }

                result["tiers"].append(tier_info)
                result["subtotal"] += tier_cost

        # Apply volume discounts
        result["total"] = result["subtotal"]

        if hasattr(rule, "volume_discounts") and rule.volume_discounts:
            for discount in sorted(
                rule.volume_discounts, key=lambda d: d.min_quantity, reverse=True
            ):
                if discount.applies_to(quantity):
                    discounted_cost = discount.apply_discount(result["subtotal"])
                    discount_amount = result["subtotal"] - discounted_cost

                    result["volume_discount"] = {
                        "min_quantity": discount.min_quantity,
                        "discount_percentage": discount.discount_percentage,
                        "discount_amount": discount_amount,
                    }

                    result["total"] = discounted_cost
                    break

        # Apply minimum and maximum costs
        if result["total"] < rule.minimum_cost:
            result["total"] = rule.minimum_cost
            result["minimum_cost_applied"] = True
        else:
            result["minimum_cost_applied"] = False

        if rule.maximum_cost is not None and result["total"] > rule.maximum_cost:
            result["total"] = rule.maximum_cost
            result["maximum_cost_applied"] = True
        else:
            result["maximum_cost_applied"] = False

        return result


# Example usage
if __name__ == "__main__":
    # Create a tiered pricing calculator
    calculator = TieredPricingCalculator()

    # Add a tiered pricing rule with volume discounts
    calculator.create_tiered_pricing_rule_with_discounts(
        metric=UsageMetric.TOKEN,
        tiers=[
            {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.001},
            {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0008},
            {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.0005},
        ],
        volume_discounts=[
            {"min_quantity": 100000, "discount_percentage": 10},
            {"min_quantity": 1000000, "discount_percentage": 20},
        ],
        graduated=True,
        category=UsageCategory.INFERENCE,
    )

    # Calculate cost
    cost = calculator.calculate_cost(
        metric=UsageMetric.TOKEN, quantity=150000, category=UsageCategory.INFERENCE
    )

    print(f"Cost for 150,000 tokens: ${cost:.2f}")

    # Get detailed cost breakdown
    breakdown = calculator.calculate_tiered_cost_breakdown(
        metric=UsageMetric.TOKEN, quantity=150000, category=UsageCategory.INFERENCE
    )

    print("\nCost breakdown:")
    print(f"Model: {breakdown['model']}")
    print(f"Quantity: {breakdown['quantity']}")

    print("\nTiers:")
    for tier in breakdown["tiers"]:
        max_str = str(tier["max_quantity"]) if tier["max_quantity"] is not None else "∞"
        print(
            f"- {tier['min_quantity']}-{max_str}: {tier['quantity']} units at ${tier['price_per_unit']}/unit = ${tier['cost']:.2f}"
        )

    print(f"\nSubtotal: ${breakdown['subtotal']:.2f}")

    if breakdown["volume_discount"]:
        discount = breakdown["volume_discount"]
        print(
            f"Volume discount: {discount['discount_percentage']}% off for {discount['min_quantity']}+ units = -${discount['discount_amount']:.2f}"
        )

    print(f"Total: ${breakdown['total']:.2f}")