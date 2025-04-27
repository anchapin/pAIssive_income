"""
Billing calculator for the pAIssive Income project.

This module provides classes for calculating billing based on usage,
including different pricing models and cost estimation.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import math
import copy

from .usage_tracking import UsageRecord, UsageMetric, UsageCategory
from .usage_tracker import UsageTracker


class PricingModel:
    """Enumeration of pricing models."""
    FLAT_RATE = "flat_rate"
    PER_UNIT = "per_unit"
    TIERED = "tiered"
    GRADUATED = "graduated"
    PACKAGE = "package"
    CUSTOM = "custom"


class PricingTier:
    """
    Class representing a pricing tier.
    
    This class provides a structured way to represent a pricing tier,
    including the minimum and maximum quantities and the price per unit.
    """
    
    def __init__(
        self,
        min_quantity: float,
        max_quantity: Optional[float],
        price_per_unit: float,
        flat_fee: float = 0.0
    ):
        """
        Initialize a pricing tier.
        
        Args:
            min_quantity: Minimum quantity for this tier
            max_quantity: Maximum quantity for this tier (None for unlimited)
            price_per_unit: Price per unit for this tier
            flat_fee: Flat fee for this tier
        """
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
        self.price_per_unit = price_per_unit
        self.flat_fee = flat_fee
    
    def contains(self, quantity: float) -> bool:
        """
        Check if a quantity is within this tier.
        
        Args:
            quantity: Quantity to check
            
        Returns:
            True if the quantity is within this tier, False otherwise
        """
        if quantity < self.min_quantity:
            return False
        
        if self.max_quantity is not None and quantity > self.max_quantity:
            return False
        
        return True
    
    def get_quantity_in_tier(self, quantity: float) -> float:
        """
        Get the quantity that falls within this tier.
        
        Args:
            quantity: Total quantity
            
        Returns:
            Quantity within this tier
        """
        if quantity <= self.min_quantity:
            return 0.0
        
        if self.max_quantity is not None:
            return min(quantity, self.max_quantity) - self.min_quantity
        
        return quantity - self.min_quantity
    
    def calculate_cost(self, quantity: float, graduated: bool = False) -> float:
        """
        Calculate the cost for a quantity using this tier.
        
        Args:
            quantity: Quantity to calculate cost for
            graduated: Whether to use graduated pricing
            
        Returns:
            Cost for the quantity
        """
        if graduated:
            # Only calculate cost for the portion of the quantity that falls within this tier
            quantity_in_tier = self.get_quantity_in_tier(quantity)
            
            if quantity_in_tier <= 0:
                return 0.0
            
            return self.flat_fee + (quantity_in_tier * self.price_per_unit)
        else:
            # Calculate cost for the entire quantity using this tier's pricing
            if not self.contains(quantity):
                return 0.0
            
            return self.flat_fee + (quantity * self.price_per_unit)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the pricing tier to a dictionary.
        
        Returns:
            Dictionary representation of the pricing tier
        """
        return {
            "min_quantity": self.min_quantity,
            "max_quantity": self.max_quantity,
            "price_per_unit": self.price_per_unit,
            "flat_fee": self.flat_fee
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PricingTier':
        """
        Create a pricing tier from a dictionary.
        
        Args:
            data: Dictionary with pricing tier data
            
        Returns:
            PricingTier instance
        """
        return cls(
            min_quantity=data["min_quantity"],
            max_quantity=data["max_quantity"],
            price_per_unit=data["price_per_unit"],
            flat_fee=data.get("flat_fee", 0.0)
        )
    
    def __str__(self) -> str:
        """String representation of the pricing tier."""
        max_str = str(self.max_quantity) if self.max_quantity is not None else "∞"
        return f"PricingTier({self.min_quantity}-{max_str}, ${self.price_per_unit}/unit, ${self.flat_fee} flat)"


class PricingPackage:
    """
    Class representing a pricing package.
    
    This class provides a structured way to represent a pricing package,
    including the quantity, price, and overage pricing.
    """
    
    def __init__(
        self,
        quantity: float,
        price: float,
        overage_price: Optional[float] = None
    ):
        """
        Initialize a pricing package.
        
        Args:
            quantity: Quantity included in the package
            price: Price for the package
            overage_price: Price per unit for usage beyond the package quantity
        """
        self.quantity = quantity
        self.price = price
        self.overage_price = overage_price
    
    def calculate_cost(self, quantity: float) -> float:
        """
        Calculate the cost for a quantity using this package.
        
        Args:
            quantity: Quantity to calculate cost for
            
        Returns:
            Cost for the quantity
        """
        if quantity <= self.quantity:
            return self.price
        
        if self.overage_price is None:
            return self.price
        
        overage = quantity - self.quantity
        return self.price + (overage * self.overage_price)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the pricing package to a dictionary.
        
        Returns:
            Dictionary representation of the pricing package
        """
        return {
            "quantity": self.quantity,
            "price": self.price,
            "overage_price": self.overage_price
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PricingPackage':
        """
        Create a pricing package from a dictionary.
        
        Args:
            data: Dictionary with pricing package data
            
        Returns:
            PricingPackage instance
        """
        return cls(
            quantity=data["quantity"],
            price=data["price"],
            overage_price=data.get("overage_price")
        )
    
    def __str__(self) -> str:
        """String representation of the pricing package."""
        overage_str = f", ${self.overage_price}/unit overage" if self.overage_price is not None else ""
        return f"PricingPackage({self.quantity} units, ${self.price}{overage_str})"


class PricingRule:
    """
    Class representing a pricing rule.
    
    This class provides a structured way to represent a pricing rule,
    including the metric, pricing model, and pricing details.
    """
    
    def __init__(
        self,
        metric: str,
        model: str,
        price_per_unit: Optional[float] = None,
        flat_fee: float = 0.0,
        tiers: Optional[List[PricingTier]] = None,
        package: Optional[PricingPackage] = None,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
        custom_calculator: Optional[callable] = None
    ):
        """
        Initialize a pricing rule.
        
        Args:
            metric: Type of usage metric
            model: Pricing model (e.g., FLAT_RATE, PER_UNIT, TIERED)
            price_per_unit: Price per unit (for PER_UNIT model)
            flat_fee: Flat fee (for FLAT_RATE model)
            tiers: List of pricing tiers (for TIERED and GRADUATED models)
            package: Pricing package (for PACKAGE model)
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost
            custom_calculator: Custom calculator function (for CUSTOM model)
        """
        self.metric = metric
        self.model = model
        self.price_per_unit = price_per_unit
        self.flat_fee = flat_fee
        self.tiers = tiers or []
        self.package = package
        self.category = category
        self.resource_type = resource_type
        self.minimum_cost = minimum_cost
        self.maximum_cost = maximum_cost
        self.custom_calculator = custom_calculator
    
    def matches(
        self,
        metric: str,
        category: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> bool:
        """
        Check if this rule matches a metric, category, and resource type.
        
        Args:
            metric: Type of usage metric
            category: Category of usage
            resource_type: Type of resource
            
        Returns:
            True if this rule matches, False otherwise
        """
        if self.metric != metric:
            return False
        
        if self.category is not None and category is not None and self.category != category:
            return False
        
        if self.resource_type is not None and resource_type is not None and self.resource_type != resource_type:
            return False
        
        return True
    
    def calculate_cost(self, quantity: float) -> float:
        """
        Calculate the cost for a quantity using this rule.
        
        Args:
            quantity: Quantity to calculate cost for
            
        Returns:
            Cost for the quantity
        """
        cost = 0.0
        
        if self.model == PricingModel.FLAT_RATE:
            cost = self.flat_fee
        
        elif self.model == PricingModel.PER_UNIT:
            if self.price_per_unit is not None:
                cost = quantity * self.price_per_unit
        
        elif self.model == PricingModel.TIERED:
            # Find the tier that contains the quantity
            for tier in self.tiers:
                if tier.contains(quantity):
                    cost = tier.calculate_cost(quantity)
                    break
        
        elif self.model == PricingModel.GRADUATED:
            # Calculate cost for each tier up to the quantity
            for tier in self.tiers:
                cost += tier.calculate_cost(quantity, graduated=True)
        
        elif self.model == PricingModel.PACKAGE:
            if self.package is not None:
                cost = self.package.calculate_cost(quantity)
        
        elif self.model == PricingModel.CUSTOM:
            if self.custom_calculator is not None:
                cost = self.custom_calculator(quantity)
        
        # Apply minimum and maximum costs
        if cost < self.minimum_cost:
            cost = self.minimum_cost
        
        if self.maximum_cost is not None and cost > self.maximum_cost:
            cost = self.maximum_cost
        
        return cost
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the pricing rule to a dictionary.
        
        Returns:
            Dictionary representation of the pricing rule
        """
        result = {
            "metric": self.metric,
            "model": self.model,
            "price_per_unit": self.price_per_unit,
            "flat_fee": self.flat_fee,
            "category": self.category,
            "resource_type": self.resource_type,
            "minimum_cost": self.minimum_cost,
            "maximum_cost": self.maximum_cost
        }
        
        if self.tiers:
            result["tiers"] = [tier.to_dict() for tier in self.tiers]
        
        if self.package:
            result["package"] = self.package.to_dict()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PricingRule':
        """
        Create a pricing rule from a dictionary.
        
        Args:
            data: Dictionary with pricing rule data
            
        Returns:
            PricingRule instance
        """
        tiers = None
        if "tiers" in data:
            tiers = [PricingTier.from_dict(tier_data) for tier_data in data["tiers"]]
        
        package = None
        if "package" in data:
            package = PricingPackage.from_dict(data["package"])
        
        return cls(
            metric=data["metric"],
            model=data["model"],
            price_per_unit=data.get("price_per_unit"),
            flat_fee=data.get("flat_fee", 0.0),
            tiers=tiers,
            package=package,
            category=data.get("category"),
            resource_type=data.get("resource_type"),
            minimum_cost=data.get("minimum_cost", 0.0),
            maximum_cost=data.get("maximum_cost")
        )
    
    def __str__(self) -> str:
        """String representation of the pricing rule."""
        return f"PricingRule({self.metric}, {self.model})"


class BillingCalculator:
    """
    Class for calculating billing based on usage.
    
    This class provides methods for calculating billing based on usage records,
    using different pricing models and rules.
    """
    
    def __init__(
        self,
        usage_tracker: Optional[UsageTracker] = None,
        pricing_rules: Optional[List[PricingRule]] = None
    ):
        """
        Initialize a billing calculator.
        
        Args:
            usage_tracker: Usage tracker to use
            pricing_rules: List of pricing rules
        """
        self.usage_tracker = usage_tracker
        self.pricing_rules = pricing_rules or []
    
    def add_pricing_rule(self, rule: PricingRule) -> None:
        """
        Add a pricing rule.
        
        Args:
            rule: Pricing rule to add
        """
        self.pricing_rules.append(rule)
    
    def get_pricing_rule(
        self,
        metric: str,
        category: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> Optional[PricingRule]:
        """
        Get a pricing rule that matches a metric, category, and resource type.
        
        Args:
            metric: Type of usage metric
            category: Category of usage
            resource_type: Type of resource
            
        Returns:
            Matching pricing rule or None if not found
        """
        # Find the most specific matching rule
        best_match = None
        best_match_score = -1
        
        for rule in self.pricing_rules:
            if rule.matches(metric, category, resource_type):
                # Calculate match score (higher is more specific)
                score = 1
                
                if rule.category is not None and rule.category == category:
                    score += 1
                
                if rule.resource_type is not None and rule.resource_type == resource_type:
                    score += 1
                
                if score > best_match_score:
                    best_match = rule
                    best_match_score = score
        
        return best_match
    
    def calculate_cost(
        self,
        metric: str,
        quantity: float,
        category: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> float:
        """
        Calculate the cost for a quantity using the appropriate pricing rule.
        
        Args:
            metric: Type of usage metric
            quantity: Quantity to calculate cost for
            category: Category of usage
            resource_type: Type of resource
            
        Returns:
            Cost for the quantity
        """
        rule = self.get_pricing_rule(metric, category, resource_type)
        
        if rule is None:
            return 0.0
        
        return rule.calculate_cost(quantity)
    
    def calculate_usage_cost(
        self,
        customer_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate the cost for a customer's usage.
        
        Args:
            customer_id: ID of the customer
            start_time: Start time for usage records
            end_time: End time for usage records
            
        Returns:
            Dictionary with usage cost details
        """
        if self.usage_tracker is None:
            raise ValueError("Usage tracker is required to calculate usage cost")
        
        # Get usage summary
        summary = self.usage_tracker.get_usage_summary(
            customer_id=customer_id,
            start_time=start_time,
            end_time=end_time,
            group_by="metric"
        )
        
        # Initialize result
        result = {
            "customer_id": customer_id,
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "total_cost": 0.0,
            "items": []
        }
        
        # Calculate cost for each metric
        if "grouped" in summary:
            for metric, data in summary["grouped"].items():
                quantity = data["quantity"]
                
                # Get all records for this metric
                records = []
                for record_id in data["records"]:
                    record = self.usage_tracker.get_record(record_id)
                    if record:
                        records.append(record)
                
                # Group records by category and resource type
                grouped_records = {}
                for record in records:
                    key = (record.category, record.resource_type)
                    
                    if key not in grouped_records:
                        grouped_records[key] = {
                            "category": record.category,
                            "resource_type": record.resource_type,
                            "quantity": 0.0,
                            "records": []
                        }
                    
                    grouped_records[key]["quantity"] += record.quantity
                    grouped_records[key]["records"].append(record.id)
                
                # Calculate cost for each group
                for key, group_data in grouped_records.items():
                    category, resource_type = key
                    group_quantity = group_data["quantity"]
                    
                    cost = self.calculate_cost(
                        metric=metric,
                        quantity=group_quantity,
                        category=category,
                        resource_type=resource_type
                    )
                    
                    # Add to result
                    item = {
                        "metric": metric,
                        "category": category,
                        "resource_type": resource_type,
                        "quantity": group_quantity,
                        "cost": cost,
                        "records": group_data["records"]
                    }
                    
                    result["items"].append(item)
                    result["total_cost"] += cost
        
        return result
    
    def estimate_cost(
        self,
        usage_estimates: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Estimate the cost for estimated usage.
        
        Args:
            usage_estimates: Dictionary mapping metrics to dictionaries mapping
                categories to quantities
            
        Returns:
            Dictionary with estimated cost details
        """
        # Initialize result
        result = {
            "total_cost": 0.0,
            "items": []
        }
        
        # Calculate cost for each metric and category
        for metric, categories in usage_estimates.items():
            for category, quantity in categories.items():
                cost = self.calculate_cost(
                    metric=metric,
                    quantity=quantity,
                    category=category
                )
                
                # Add to result
                item = {
                    "metric": metric,
                    "category": category,
                    "quantity": quantity,
                    "cost": cost
                }
                
                result["items"].append(item)
                result["total_cost"] += cost
        
        return result
    
    def create_tiered_pricing_rule(
        self,
        metric: str,
        tiers: List[Dict[str, Any]],
        graduated: bool = False,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None
    ) -> PricingRule:
        """
        Create a tiered pricing rule.
        
        Args:
            metric: Type of usage metric
            tiers: List of tier dictionaries with min_quantity, max_quantity, and price_per_unit
            graduated: Whether to use graduated pricing
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost
            
        Returns:
            Tiered pricing rule
        """
        pricing_tiers = []
        
        for tier_data in tiers:
            tier = PricingTier(
                min_quantity=tier_data["min_quantity"],
                max_quantity=tier_data.get("max_quantity"),
                price_per_unit=tier_data["price_per_unit"],
                flat_fee=tier_data.get("flat_fee", 0.0)
            )
            
            pricing_tiers.append(tier)
        
        # Sort tiers by min_quantity
        pricing_tiers.sort(key=lambda t: t.min_quantity)
        
        rule = PricingRule(
            metric=metric,
            model=PricingModel.GRADUATED if graduated else PricingModel.TIERED,
            tiers=pricing_tiers,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost
        )
        
        self.add_pricing_rule(rule)
        
        return rule
    
    def create_package_pricing_rule(
        self,
        metric: str,
        quantity: float,
        price: float,
        overage_price: Optional[float] = None,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None
    ) -> PricingRule:
        """
        Create a package pricing rule.
        
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
            Package pricing rule
        """
        package = PricingPackage(
            quantity=quantity,
            price=price,
            overage_price=overage_price
        )
        
        rule = PricingRule(
            metric=metric,
            model=PricingModel.PACKAGE,
            package=package,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost
        )
        
        self.add_pricing_rule(rule)
        
        return rule
    
    def create_flat_rate_pricing_rule(
        self,
        metric: str,
        flat_fee: float,
        category: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> PricingRule:
        """
        Create a flat rate pricing rule.
        
        Args:
            metric: Type of usage metric
            flat_fee: Flat fee
            category: Category of usage
            resource_type: Type of resource
            
        Returns:
            Flat rate pricing rule
        """
        rule = PricingRule(
            metric=metric,
            model=PricingModel.FLAT_RATE,
            flat_fee=flat_fee,
            category=category,
            resource_type=resource_type
        )
        
        self.add_pricing_rule(rule)
        
        return rule
    
    def create_per_unit_pricing_rule(
        self,
        metric: str,
        price_per_unit: float,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None
    ) -> PricingRule:
        """
        Create a per-unit pricing rule.
        
        Args:
            metric: Type of usage metric
            price_per_unit: Price per unit
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost
            
        Returns:
            Per-unit pricing rule
        """
        rule = PricingRule(
            metric=metric,
            model=PricingModel.PER_UNIT,
            price_per_unit=price_per_unit,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost
        )
        
        self.add_pricing_rule(rule)
        
        return rule


# Example usage
if __name__ == "__main__":
    from .usage_tracker import UsageTracker
    
    # Create a usage tracker
    tracker = UsageTracker()
    
    # Create a billing calculator
    calculator = BillingCalculator(usage_tracker=tracker)
    
    # Add pricing rules
    calculator.create_per_unit_pricing_rule(
        metric=UsageMetric.API_CALL,
        price_per_unit=0.01,
        category=UsageCategory.INFERENCE
    )
    
    calculator.create_tiered_pricing_rule(
        metric=UsageMetric.TOKEN,
        tiers=[
            {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.001},
            {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0008},
            {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.0005}
        ],
        graduated=True,
        category=UsageCategory.INFERENCE
    )
    
    calculator.create_package_pricing_rule(
        metric=UsageMetric.STORAGE,
        quantity=10.0,  # GB
        price=5.0,
        overage_price=0.5,  # per GB
        category=UsageCategory.STORAGE
    )
    
    # Calculate costs
    api_cost = calculator.calculate_cost(
        metric=UsageMetric.API_CALL,
        quantity=100,
        category=UsageCategory.INFERENCE
    )
    
    token_cost = calculator.calculate_cost(
        metric=UsageMetric.TOKEN,
        quantity=5000,
        category=UsageCategory.INFERENCE
    )
    
    storage_cost = calculator.calculate_cost(
        metric=UsageMetric.STORAGE,
        quantity=15.0,
        category=UsageCategory.STORAGE
    )
    
    print(f"API call cost: ${api_cost:.2f}")
    print(f"Token cost: ${token_cost:.2f}")
    print(f"Storage cost: ${storage_cost:.2f}")
    
    # Estimate total cost
    estimated_cost = calculator.estimate_cost({
        UsageMetric.API_CALL: {UsageCategory.INFERENCE: 100},
        UsageMetric.TOKEN: {UsageCategory.INFERENCE: 5000},
        UsageMetric.STORAGE: {UsageCategory.STORAGE: 15.0}
    })
    
    print(f"\nEstimated total cost: ${estimated_cost['total_cost']:.2f}")
    
    for item in estimated_cost["items"]:
        print(f"- {item['metric']} ({item['category']}): {item['quantity']} units, ${item['cost']:.2f}")
