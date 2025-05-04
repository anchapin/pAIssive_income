"""
"""
Custom pricing rules for the pAIssive Income project.
Custom pricing rules for the pAIssive Income project.


This module provides classes for implementing custom pricing rules,
This module provides classes for implementing custom pricing rules,
where pricing is determined by complex conditions, formulas, or other
where pricing is determined by complex conditions, formulas, or other
custom logic beyond standard pricing models.
custom logic beyond standard pricing models.
"""
"""


import math
import math
import re
import re
import time
import time
import uuid
import uuid
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .billing_calculator import BillingCalculator, PricingModel, PricingRule
from .billing_calculator import BillingCalculator, PricingModel, PricingRule
from .usage_tracking import UsageCategory, UsageMetric
from .usage_tracking import UsageCategory, UsageMetric




class CustomPricingRule:
    class CustomPricingRule:


    pass  # Added missing block
    pass  # Added missing block
    """
    """
    Base class for custom pricing rules.
    Base class for custom pricing rules.


    This class extends the standard PricingRule to provide a framework for
    This class extends the standard PricingRule to provide a framework for
    implementing custom pricing logic that goes beyond the standard pricing models.
    implementing custom pricing logic that goes beyond the standard pricing models.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    metric: str,
    metric: str,
    name: str = "Custom Pricing Rule",
    name: str = "Custom Pricing Rule",
    description: str = "Custom pricing rule with specialized logic",
    description: str = "Custom pricing rule with specialized logic",
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a custom pricing rule.
    Initialize a custom pricing rule.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    name: Name of the custom pricing rule
    name: Name of the custom pricing rule
    description: Description of the custom pricing rule
    description: Description of the custom pricing rule
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource
    minimum_cost: Minimum cost
    minimum_cost: Minimum cost
    maximum_cost: Maximum cost
    maximum_cost: Maximum cost
    metadata: Additional metadata for the custom pricing rule
    metadata: Additional metadata for the custom pricing rule
    """
    """
    super().__init__(
    super().__init__(
    metric=metric,
    metric=metric,
    model=PricingModel.CUSTOM,
    model=PricingModel.CUSTOM,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    minimum_cost=minimum_cost,
    minimum_cost=minimum_cost,
    maximum_cost=maximum_cost,
    maximum_cost=maximum_cost,
    custom_calculator=self.calculate_custom_cost,
    custom_calculator=self.calculate_custom_cost,
    )
    )


    self.name = name
    self.name = name
    self.description = description
    self.description = description
    self.metadata = metadata or {}
    self.metadata = metadata or {}
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.created_at = datetime.now()
    self.created_at = datetime.now()
    self.updated_at = self.created_at
    self.updated_at = self.created_at


    def calculate_custom_cost(self, quantity: float) -> float:
    def calculate_custom_cost(self, quantity: float) -> float:
    """
    """
    Calculate the cost using custom logic.
    Calculate the cost using custom logic.


    This method should be overridden by subclasses to implement
    This method should be overridden by subclasses to implement
    custom pricing logic.
    custom pricing logic.


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
    # Default implementation returns 0
    # Default implementation returns 0
    return 0.0
    return 0.0


    def get_context_data(self) -> Dict[str, Any]:
    def get_context_data(self) -> Dict[str, Any]:
    """
    """
    Get context data for the custom pricing rule.
    Get context data for the custom pricing rule.


    This method can be overridden by subclasses to provide
    This method can be overridden by subclasses to provide
    additional context data for the custom pricing rule.
    additional context data for the custom pricing rule.


    Returns:
    Returns:
    Dictionary with context data
    Dictionary with context data
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
    "metric": self.metric,
    "metric": self.metric,
    "category": self.category,
    "category": self.category,
    "resource_type": self.resource_type,
    "resource_type": self.resource_type,
    "minimum_cost": self.minimum_cost,
    "minimum_cost": self.minimum_cost,
    "maximum_cost": self.maximum_cost,
    "maximum_cost": self.maximum_cost,
    "metadata": self.metadata,
    "metadata": self.metadata,
    "created_at": self.created_at.isoformat(),
    "created_at": self.created_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    }
    }


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the custom pricing rule to a dictionary.
    Convert the custom pricing rule to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the custom pricing rule
    Dictionary representation of the custom pricing rule
    """
    """
    result = super().to_dict()
    result = super().to_dict()
    result.update(
    result.update(
    {
    {
    "id": self.id,
    "id": self.id,
    "name": self.name,
    "name": self.name,
    "description": self.description,
    "description": self.description,
    "metadata": self.metadata,
    "metadata": self.metadata,
    "created_at": self.created_at.isoformat(),
    "created_at": self.created_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    "rule_type": self.__class__.__name__,
    "rule_type": self.__class__.__name__,
    }
    }
    )
    )
    return result
    return result


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CustomPricingRule":
    def from_dict(cls, data: Dict[str, Any]) -> "CustomPricingRule":
    """
    """
    Create a custom pricing rule from a dictionary.
    Create a custom pricing rule from a dictionary.


    Args:
    Args:
    data: Dictionary with custom pricing rule data
    data: Dictionary with custom pricing rule data


    Returns:
    Returns:
    CustomPricingRule instance
    CustomPricingRule instance
    """
    """
    instance = cls(
    instance = cls(
    metric=data["metric"],
    metric=data["metric"],
    name=data.get("name", "Custom Pricing Rule"),
    name=data.get("name", "Custom Pricing Rule"),
    description=data.get(
    description=data.get(
    "description", "Custom pricing rule with specialized logic"
    "description", "Custom pricing rule with specialized logic"
    ),
    ),
    category=data.get("category"),
    category=data.get("category"),
    resource_type=data.get("resource_type"),
    resource_type=data.get("resource_type"),
    minimum_cost=data.get("minimum_cost", 0.0),
    minimum_cost=data.get("minimum_cost", 0.0),
    maximum_cost=data.get("maximum_cost"),
    maximum_cost=data.get("maximum_cost"),
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    if "id" in data:
    if "id" in data:
    instance.id = data["id"]
    instance.id = data["id"]


    if "created_at" in data:
    if "created_at" in data:
    instance.created_at = datetime.fromisoformat(data["created_at"])
    instance.created_at = datetime.fromisoformat(data["created_at"])


    if "updated_at" in data:
    if "updated_at" in data:
    instance.updated_at = datetime.fromisoformat(data["updated_at"])
    instance.updated_at = datetime.fromisoformat(data["updated_at"])


    return instance
    return instance


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the custom pricing rule."""
    return f"{self.__class__.__name__}({self.name}, {self.metric})"


    class CustomPricingCalculator:
    """
    """
    Calculator for custom pricing rules.
    Calculator for custom pricing rules.


    This class provides methods for managing and applying custom pricing rules.
    This class provides methods for managing and applying custom pricing rules.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    billing_calculator: Optional[BillingCalculator] = None,
    billing_calculator: Optional[BillingCalculator] = None,
    custom_rules: Optional[List[CustomPricingRule]] = None,
    custom_rules: Optional[List[CustomPricingRule]] = None,
    ):
    ):
    """
    """
    Initialize a custom pricing calculator.
    Initialize a custom pricing calculator.


    Args:
    Args:
    billing_calculator: Billing calculator to use
    billing_calculator: Billing calculator to use
    custom_rules: List of custom pricing rules
    custom_rules: List of custom pricing rules
    """
    """
    self.billing_calculator = billing_calculator or BillingCalculator()
    self.billing_calculator = billing_calculator or BillingCalculator()
    self.custom_rules = custom_rules or []
    self.custom_rules = custom_rules or []


    def add_custom_rule(self, rule: CustomPricingRule) -> None:
    def add_custom_rule(self, rule: CustomPricingRule) -> None:
    """
    """
    Add a custom pricing rule.
    Add a custom pricing rule.


    Args:
    Args:
    rule: Custom pricing rule to add
    rule: Custom pricing rule to add
    """
    """
    self.custom_rules.append(rule)
    self.custom_rules.append(rule)
    self.billing_calculator.add_pricing_rule(rule)
    self.billing_calculator.add_pricing_rule(rule)


    def remove_custom_rule(self, rule_id: str) -> bool:
    def remove_custom_rule(self, rule_id: str) -> bool:
    """
    """
    Remove a custom pricing rule.
    Remove a custom pricing rule.


    Args:
    Args:
    rule_id: ID of the custom pricing rule to remove
    rule_id: ID of the custom pricing rule to remove


    Returns:
    Returns:
    True if the rule was removed, False otherwise
    True if the rule was removed, False otherwise
    """
    """
    for i, rule in enumerate(self.custom_rules):
    for i, rule in enumerate(self.custom_rules):
    if rule.id == rule_id:
    if rule.id == rule_id:
    self.custom_rules.pop(i)
    self.custom_rules.pop(i)


    # Also remove from billing calculator
    # Also remove from billing calculator
    for j, bc_rule in enumerate(self.billing_calculator.pricing_rules):
    for j, bc_rule in enumerate(self.billing_calculator.pricing_rules):
    if hasattr(bc_rule, "id") and bc_rule.id == rule_id:
    if hasattr(bc_rule, "id") and bc_rule.id == rule_id:
    self.billing_calculator.pricing_rules.pop(j)
    self.billing_calculator.pricing_rules.pop(j)
    break
    break


    return True
    return True


    return False
    return False


    def get_custom_rule(self, rule_id: str) -> Optional[CustomPricingRule]:
    def get_custom_rule(self, rule_id: str) -> Optional[CustomPricingRule]:
    """
    """
    Get a custom pricing rule by ID.
    Get a custom pricing rule by ID.


    Args:
    Args:
    rule_id: ID of the custom pricing rule to get
    rule_id: ID of the custom pricing rule to get


    Returns:
    Returns:
    The custom pricing rule, or None if not found
    The custom pricing rule, or None if not found
    """
    """
    for rule in self.custom_rules:
    for rule in self.custom_rules:
    if rule.id == rule_id:
    if rule.id == rule_id:
    return rule
    return rule


    return None
    return None


    def get_custom_rules_for_metric(
    def get_custom_rules_for_metric(
    self,
    self,
    metric: str,
    metric: str,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    ) -> List[CustomPricingRule]:
    ) -> List[CustomPricingRule]:
    """
    """
    Get custom pricing rules for a metric.
    Get custom pricing rules for a metric.


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
    List of custom pricing rules for the metric
    List of custom pricing rules for the metric
    """
    """
    matching_rules = []
    matching_rules = []


    for rule in self.custom_rules:
    for rule in self.custom_rules:
    if rule.matches(metric, category, resource_type):
    if rule.matches(metric, category, resource_type):
    matching_rules.append(rule)
    matching_rules.append(rule)


    return matching_rules
    return matching_rules


    def calculate_cost(
    def calculate_cost(
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
    context: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    ) -> float:
    ) -> float:
    """
    """
    Calculate the cost for a quantity using custom pricing rules.
    Calculate the cost for a quantity using custom pricing rules.


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
    context: Additional context for the calculation
    context: Additional context for the calculation


    Returns:
    Returns:
    Cost for the quantity
    Cost for the quantity
    """
    """
    # Get matching rules
    # Get matching rules
    matching_rules = self.get_custom_rules_for_metric(
    matching_rules = self.get_custom_rules_for_metric(
    metric, category, resource_type
    metric, category, resource_type
    )
    )


    if not matching_rules:
    if not matching_rules:
    # No custom rules, use standard billing calculator
    # No custom rules, use standard billing calculator
    return self.billing_calculator.calculate_cost(
    return self.billing_calculator.calculate_cost(
    metric, quantity, category, resource_type
    metric, quantity, category, resource_type
    )
    )


    # Use the first matching custom rule
    # Use the first matching custom rule
    # In a more complex implementation, we might want to combine rules or use a priority system
    # In a more complex implementation, we might want to combine rules or use a priority system
    rule = matching_rules[0]
    rule = matching_rules[0]


    # Calculate cost using the custom rule
    # Calculate cost using the custom rule
    cost = rule.calculate_custom_cost(quantity)
    cost = rule.calculate_custom_cost(quantity)


    # Apply minimum and maximum cost constraints
    # Apply minimum and maximum cost constraints
    if cost < rule.minimum_cost:
    if cost < rule.minimum_cost:
    cost = rule.minimum_cost
    cost = rule.minimum_cost


    if rule.maximum_cost is not None and cost > rule.maximum_cost:
    if rule.maximum_cost is not None and cost > rule.maximum_cost:
    cost = rule.maximum_cost
    cost = rule.maximum_cost


    return cost
    return cost


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the custom pricing calculator to a dictionary.
    Convert the custom pricing calculator to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the custom pricing calculator
    Dictionary representation of the custom pricing calculator
    """
    """
    return {"custom_rules": [rule.to_dict() for rule in self.custom_rules]}
    return {"custom_rules": [rule.to_dict() for rule in self.custom_rules]}


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
    ) -> "CustomPricingCalculator":
    ) -> "CustomPricingCalculator":
    """
    """
    Create a custom pricing calculator from a dictionary.
    Create a custom pricing calculator from a dictionary.


    Args:
    Args:
    data: Dictionary with custom pricing calculator data
    data: Dictionary with custom pricing calculator data
    billing_calculator: Billing calculator to use
    billing_calculator: Billing calculator to use


    Returns:
    Returns:
    CustomPricingCalculator instance
    CustomPricingCalculator instance
    """
    """
    instance = cls(billing_calculator=billing_calculator)
    instance = cls(billing_calculator=billing_calculator)


    if "custom_rules" in data:
    if "custom_rules" in data:
    for rule_data in data["custom_rules"]:
    for rule_data in data["custom_rules"]:
    rule_type = rule_data.get("rule_type", "CustomPricingRule")
    rule_type = rule_data.get("rule_type", "CustomPricingRule")


    # Import the rule class dynamically
    # Import the rule class dynamically
    # This assumes all rule classes are defined in this module
    # This assumes all rule classes are defined in this module
    rule_class = globals().get(rule_type, CustomPricingRule)
    rule_class = globals().get(rule_type, CustomPricingRule)


    rule = rule_class.from_dict(rule_data)
    rule = rule_class.from_dict(rule_data)
    instance.add_custom_rule(rule)
    instance.add_custom_rule(rule)


    return instance
    return instance




    class TimeBasedPricingRule(CustomPricingRule):
    class TimeBasedPricingRule(CustomPricingRule):
    """
    """
    Time-based pricing rule.
    Time-based pricing rule.


    This class implements a pricing rule that applies different rates
    This class implements a pricing rule that applies different rates
    based on the time of day, day of week, or other time-based factors.
    based on the time of day, day of week, or other time-based factors.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    metric: str,
    metric: str,
    time_rates: Dict[str, float],
    time_rates: Dict[str, float],
    default_rate: float = 0.0,
    default_rate: float = 0.0,
    name: str = "Time-Based Pricing",
    name: str = "Time-Based Pricing",
    description: str = "Pricing based on time of day or day of week",
    description: str = "Pricing based on time of day or day of week",
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a time-based pricing rule.
    Initialize a time-based pricing rule.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    time_rates: Dictionary mapping time patterns to rates
    time_rates: Dictionary mapping time patterns to rates
    default_rate: Default rate to use if no time pattern matches
    default_rate: Default rate to use if no time pattern matches
    name: Name of the custom pricing rule
    name: Name of the custom pricing rule
    description: Description of the custom pricing rule
    description: Description of the custom pricing rule
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource
    minimum_cost: Minimum cost
    minimum_cost: Minimum cost
    maximum_cost: Maximum cost
    maximum_cost: Maximum cost
    metadata: Additional metadata for the custom pricing rule
    metadata: Additional metadata for the custom pricing rule


    Time patterns can be specified in the following formats:
    Time patterns can be specified in the following formats:
    - "weekday:1-5": Weekdays (Monday to Friday)
    - "weekday:1-5": Weekdays (Monday to Friday)
    - "weekend:6-7": Weekends (Saturday and Sunday)
    - "weekend:6-7": Weekends (Saturday and Sunday)
    - "hour:9-17": Business hours (9 AM to 5 PM)
    - "hour:9-17": Business hours (9 AM to 5 PM)
    - "hour:0-8,18-23": Non-business hours
    - "hour:0-8,18-23": Non-business hours
    - "date:2023-12-25": Specific date
    - "date:2023-12-25": Specific date
    - "month:12": Specific month (December)
    - "month:12": Specific month (December)
    - "day:1": Specific day of month (1st)
    - "day:1": Specific day of month (1st)
    """
    """
    super().__init__(
    super().__init__(
    metric=metric,
    metric=metric,
    name=name,
    name=name,
    description=description,
    description=description,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    minimum_cost=minimum_cost,
    minimum_cost=minimum_cost,
    maximum_cost=maximum_cost,
    maximum_cost=maximum_cost,
    metadata=metadata,
    metadata=metadata,
    )
    )


    self.time_rates = time_rates
    self.time_rates = time_rates
    self.default_rate = default_rate
    self.default_rate = default_rate


    def calculate_custom_cost(
    def calculate_custom_cost(
    self, quantity: float, timestamp: Optional[datetime] = None
    self, quantity: float, timestamp: Optional[datetime] = None
    ) -> float:
    ) -> float:
    """
    """
    Calculate the cost based on the time of usage.
    Calculate the cost based on the time of usage.


    Args:
    Args:
    quantity: Quantity to calculate cost for
    quantity: Quantity to calculate cost for
    timestamp: Timestamp of the usage (defaults to now)
    timestamp: Timestamp of the usage (defaults to now)


    Returns:
    Returns:
    Cost for the quantity
    Cost for the quantity
    """
    """
    # Use current time if no timestamp is provided
    # Use current time if no timestamp is provided
    timestamp = timestamp or datetime.now()
    timestamp = timestamp or datetime.now()


    # Find the applicable rate
    # Find the applicable rate
    rate = self.get_rate_for_time(timestamp)
    rate = self.get_rate_for_time(timestamp)


    # Calculate cost
    # Calculate cost
    return quantity * rate
    return quantity * rate


    def get_rate_for_time(self, timestamp: datetime) -> float:
    def get_rate_for_time(self, timestamp: datetime) -> float:
    """
    """
    Get the rate applicable for a specific time.
    Get the rate applicable for a specific time.


    Args:
    Args:
    timestamp: Timestamp to get rate for
    timestamp: Timestamp to get rate for


    Returns:
    Returns:
    Applicable rate for the timestamp
    Applicable rate for the timestamp
    """
    """
    # Check each time pattern
    # Check each time pattern
    for pattern, rate in self.time_rates.items():
    for pattern, rate in self.time_rates.items():
    if self.matches_time_pattern(pattern, timestamp):
    if self.matches_time_pattern(pattern, timestamp):
    return rate
    return rate


    # Return default rate if no pattern matches
    # Return default rate if no pattern matches
    return self.default_rate
    return self.default_rate


    def matches_time_pattern(self, pattern: str, timestamp: datetime) -> bool:
    def matches_time_pattern(self, pattern: str, timestamp: datetime) -> bool:
    """
    """
    Check if a timestamp matches a time pattern.
    Check if a timestamp matches a time pattern.


    Args:
    Args:
    pattern: Time pattern to check
    pattern: Time pattern to check
    timestamp: Timestamp to check
    timestamp: Timestamp to check


    Returns:
    Returns:
    True if the timestamp matches the pattern, False otherwise
    True if the timestamp matches the pattern, False otherwise
    """
    """
    # Split pattern into type and value
    # Split pattern into type and value
    if ":" not in pattern:
    if ":" not in pattern:
    return False
    return False


    pattern_type, pattern_value = pattern.split(":", 1)
    pattern_type, pattern_value = pattern.split(":", 1)


    # Check weekday pattern (1=Monday, 7=Sunday)
    # Check weekday pattern (1=Monday, 7=Sunday)
    if pattern_type == "weekday":
    if pattern_type == "weekday":
    weekday = timestamp.isoweekday()
    weekday = timestamp.isoweekday()
    return self.matches_range_pattern(pattern_value, weekday)
    return self.matches_range_pattern(pattern_value, weekday)


    # Check weekend pattern
    # Check weekend pattern
    if pattern_type == "weekend":
    if pattern_type == "weekend":
    weekday = timestamp.isoweekday()
    weekday = timestamp.isoweekday()
    is_weekend = weekday >= 6  # Saturday or Sunday
    is_weekend = weekday >= 6  # Saturday or Sunday
    return is_weekend
    return is_weekend


    # Check hour pattern (0-23)
    # Check hour pattern (0-23)
    if pattern_type == "hour":
    if pattern_type == "hour":
    hour = timestamp.hour
    hour = timestamp.hour
    return self.matches_range_pattern(pattern_value, hour)
    return self.matches_range_pattern(pattern_value, hour)


    # Check date pattern (YYYY-MM-DD)
    # Check date pattern (YYYY-MM-DD)
    if pattern_type == "date":
    if pattern_type == "date":
    date_str = timestamp.strftime("%Y-%m-%d")
    date_str = timestamp.strftime("%Y-%m-%d")
    return date_str == pattern_value
    return date_str == pattern_value


    # Check month pattern (1-12)
    # Check month pattern (1-12)
    if pattern_type == "month":
    if pattern_type == "month":
    month = timestamp.month
    month = timestamp.month
    return self.matches_range_pattern(pattern_value, month)
    return self.matches_range_pattern(pattern_value, month)


    # Check day pattern (1-31)
    # Check day pattern (1-31)
    if pattern_type == "day":
    if pattern_type == "day":
    day = timestamp.day
    day = timestamp.day
    return self.matches_range_pattern(pattern_value, day)
    return self.matches_range_pattern(pattern_value, day)


    # Unknown pattern type
    # Unknown pattern type
    return False
    return False


    def matches_range_pattern(self, pattern: str, value: int) -> bool:
    def matches_range_pattern(self, pattern: str, value: int) -> bool:
    """
    """
    Check if a value matches a range pattern.
    Check if a value matches a range pattern.


    Args:
    Args:
    pattern: Range pattern to check (e.g., "1-5", "1,3,5", "1-3,5-7")
    pattern: Range pattern to check (e.g., "1-5", "1,3,5", "1-3,5-7")
    value: Value to check
    value: Value to check


    Returns:
    Returns:
    True if the value matches the pattern, False otherwise
    True if the value matches the pattern, False otherwise
    """
    """
    # Split pattern into ranges
    # Split pattern into ranges
    ranges = pattern.split(",")
    ranges = pattern.split(",")


    for range_str in ranges:
    for range_str in ranges:
    # Check if range has a min and max
    # Check if range has a min and max
    if "-" in range_str:
    if "-" in range_str:
    range_min, range_max = map(int, range_str.split("-", 1))
    range_min, range_max = map(int, range_str.split("-", 1))
    if range_min <= value <= range_max:
    if range_min <= value <= range_max:
    return True
    return True
    else:
    else:
    # Single value
    # Single value
    if value == int(range_str):
    if value == int(range_str):
    return True
    return True


    return False
    return False


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the time-based pricing rule to a dictionary.
    Convert the time-based pricing rule to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the time-based pricing rule
    Dictionary representation of the time-based pricing rule
    """
    """
    result = super().to_dict()
    result = super().to_dict()
    result.update(
    result.update(
    {"time_rates": self.time_rates, "default_rate": self.default_rate}
    {"time_rates": self.time_rates, "default_rate": self.default_rate}
    )
    )
    return result
    return result


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeBasedPricingRule":
    def from_dict(cls, data: Dict[str, Any]) -> "TimeBasedPricingRule":
    """
    """
    Create a time-based pricing rule from a dictionary.
    Create a time-based pricing rule from a dictionary.


    Args:
    Args:
    data: Dictionary with time-based pricing rule data
    data: Dictionary with time-based pricing rule data


    Returns:
    Returns:
    TimeBasedPricingRule instance
    TimeBasedPricingRule instance
    """
    """
    instance = cls(
    instance = cls(
    metric=data["metric"],
    metric=data["metric"],
    time_rates=data.get("time_rates", {}),
    time_rates=data.get("time_rates", {}),
    default_rate=data.get("default_rate", 0.0),
    default_rate=data.get("default_rate", 0.0),
    name=data.get("name", "Time-Based Pricing"),
    name=data.get("name", "Time-Based Pricing"),
    description=data.get(
    description=data.get(
    "description", "Pricing based on time of day or day of week"
    "description", "Pricing based on time of day or day of week"
    ),
    ),
    category=data.get("category"),
    category=data.get("category"),
    resource_type=data.get("resource_type"),
    resource_type=data.get("resource_type"),
    minimum_cost=data.get("minimum_cost", 0.0),
    minimum_cost=data.get("minimum_cost", 0.0),
    maximum_cost=data.get("maximum_cost"),
    maximum_cost=data.get("maximum_cost"),
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    if "id" in data:
    if "id" in data:
    instance.id = data["id"]
    instance.id = data["id"]


    if "created_at" in data:
    if "created_at" in data:
    instance.created_at = datetime.fromisoformat(data["created_at"])
    instance.created_at = datetime.fromisoformat(data["created_at"])


    if "updated_at" in data:
    if "updated_at" in data:
    instance.updated_at = datetime.fromisoformat(data["updated_at"])
    instance.updated_at = datetime.fromisoformat(data["updated_at"])


    return instance
    return instance




    class SeasonalPricingRule(CustomPricingRule):
    class SeasonalPricingRule(CustomPricingRule):
    """
    """
    Seasonal pricing rule.
    Seasonal pricing rule.


    This class implements a pricing rule that applies different rates
    This class implements a pricing rule that applies different rates
    based on seasons, months, or other calendar-based factors.
    based on seasons, months, or other calendar-based factors.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    metric: str,
    metric: str,
    seasonal_rates: Dict[str, float],
    seasonal_rates: Dict[str, float],
    default_rate: float = 0.0,
    default_rate: float = 0.0,
    name: str = "Seasonal Pricing",
    name: str = "Seasonal Pricing",
    description: str = "Pricing based on seasons or months",
    description: str = "Pricing based on seasons or months",
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a seasonal pricing rule.
    Initialize a seasonal pricing rule.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    seasonal_rates: Dictionary mapping season patterns to rates
    seasonal_rates: Dictionary mapping season patterns to rates
    default_rate: Default rate to use if no season pattern matches
    default_rate: Default rate to use if no season pattern matches
    name: Name of the custom pricing rule
    name: Name of the custom pricing rule
    description: Description of the custom pricing rule
    description: Description of the custom pricing rule
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource
    minimum_cost: Minimum cost
    minimum_cost: Minimum cost
    maximum_cost: Maximum cost
    maximum_cost: Maximum cost
    metadata: Additional metadata for the custom pricing rule
    metadata: Additional metadata for the custom pricing rule


    Season patterns can be specified in the following formats:
    Season patterns can be specified in the following formats:
    - "winter": Winter season (December, January, February)
    - "winter": Winter season (December, January, February)
    - "spring": Spring season (March, April, May)
    - "spring": Spring season (March, April, May)
    - "summer": Summer season (June, July, August)
    - "summer": Summer season (June, July, August)
    - "fall": Fall season (September, October, November)
    - "fall": Fall season (September, October, November)
    - "month:1": January
    - "month:1": January
    - "month:6-8": Summer months (June, July, August)
    - "month:6-8": Summer months (June, July, August)
    - "quarter:1": First quarter (January, February, March)
    - "quarter:1": First quarter (January, February, March)
    - "holiday:christmas": Christmas holiday period
    - "holiday:christmas": Christmas holiday period
    - "holiday:thanksgiving": Thanksgiving holiday period
    - "holiday:thanksgiving": Thanksgiving holiday period
    """
    """
    super().__init__(
    super().__init__(
    metric=metric,
    metric=metric,
    name=name,
    name=name,
    description=description,
    description=description,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    minimum_cost=minimum_cost,
    minimum_cost=minimum_cost,
    maximum_cost=maximum_cost,
    maximum_cost=maximum_cost,
    metadata=metadata,
    metadata=metadata,
    )
    )


    self.seasonal_rates = seasonal_rates
    self.seasonal_rates = seasonal_rates
    self.default_rate = default_rate
    self.default_rate = default_rate


    # Define seasons
    # Define seasons
    self.seasons = {
    self.seasons = {
    "winter": [12, 1, 2],
    "winter": [12, 1, 2],
    "spring": [3, 4, 5],
    "spring": [3, 4, 5],
    "summer": [6, 7, 8],
    "summer": [6, 7, 8],
    "fall": [9, 10, 11],
    "fall": [9, 10, 11],
    }
    }


    # Define quarters
    # Define quarters
    self.quarters = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}
    self.quarters = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}


    # Define holidays (month, day, duration in days)
    # Define holidays (month, day, duration in days)
    self.holidays = {
    self.holidays = {
    "christmas": (12, 25, 7),
    "christmas": (12, 25, 7),
    "thanksgiving": (11, 26, 4),  # 4th Thursday of November (approximate)
    "thanksgiving": (11, 26, 4),  # 4th Thursday of November (approximate)
    "newyear": (1, 1, 1),
    "newyear": (1, 1, 1),
    "independenceday": (7, 4, 1),
    "independenceday": (7, 4, 1),
    "laborday": (9, 1, 3),  # 1st Monday of September (approximate)
    "laborday": (9, 1, 3),  # 1st Monday of September (approximate)
    "memorialday": (5, 31, 3),  # Last Monday of May (approximate)
    "memorialday": (5, 31, 3),  # Last Monday of May (approximate)
    }
    }


    def calculate_custom_cost(
    def calculate_custom_cost(
    self, quantity: float, timestamp: Optional[datetime] = None
    self, quantity: float, timestamp: Optional[datetime] = None
    ) -> float:
    ) -> float:
    """
    """
    Calculate the cost based on the season.
    Calculate the cost based on the season.


    Args:
    Args:
    quantity: Quantity to calculate cost for
    quantity: Quantity to calculate cost for
    timestamp: Timestamp of the usage (defaults to now)
    timestamp: Timestamp of the usage (defaults to now)


    Returns:
    Returns:
    Cost for the quantity
    Cost for the quantity
    """
    """
    # Use current time if no timestamp is provided
    # Use current time if no timestamp is provided
    timestamp = timestamp or datetime.now()
    timestamp = timestamp or datetime.now()


    # Find the applicable rate
    # Find the applicable rate
    rate = self.get_rate_for_season(timestamp)
    rate = self.get_rate_for_season(timestamp)


    # Calculate cost
    # Calculate cost
    return quantity * rate
    return quantity * rate


    def get_rate_for_season(self, timestamp: datetime) -> float:
    def get_rate_for_season(self, timestamp: datetime) -> float:
    """
    """
    Get the rate applicable for a specific season.
    Get the rate applicable for a specific season.


    Args:
    Args:
    timestamp: Timestamp to get rate for
    timestamp: Timestamp to get rate for


    Returns:
    Returns:
    Applicable rate for the timestamp
    Applicable rate for the timestamp
    """
    """
    # Check each season pattern
    # Check each season pattern
    for pattern, rate in self.seasonal_rates.items():
    for pattern, rate in self.seasonal_rates.items():
    if self.matches_season_pattern(pattern, timestamp):
    if self.matches_season_pattern(pattern, timestamp):
    return rate
    return rate


    # Return default rate if no pattern matches
    # Return default rate if no pattern matches
    return self.default_rate
    return self.default_rate


    def matches_season_pattern(self, pattern: str, timestamp: datetime) -> bool:
    def matches_season_pattern(self, pattern: str, timestamp: datetime) -> bool:
    """
    """
    Check if a timestamp matches a season pattern.
    Check if a timestamp matches a season pattern.


    Args:
    Args:
    pattern: Season pattern to check
    pattern: Season pattern to check
    timestamp: Timestamp to check
    timestamp: Timestamp to check


    Returns:
    Returns:
    True if the timestamp matches the pattern, False otherwise
    True if the timestamp matches the pattern, False otherwise
    """
    """
    # Check season names
    # Check season names
    if pattern in self.seasons:
    if pattern in self.seasons:
    month = timestamp.month
    month = timestamp.month
    return month in self.seasons[pattern]
    return month in self.seasons[pattern]


    # Check month pattern
    # Check month pattern
    if pattern.startswith("month:"):
    if pattern.startswith("month:"):
    month = timestamp.month
    month = timestamp.month
    month_pattern = pattern[6:]
    month_pattern = pattern[6:]
    return self.matches_range_pattern(month_pattern, month)
    return self.matches_range_pattern(month_pattern, month)


    # Check quarter pattern
    # Check quarter pattern
    if pattern.startswith("quarter:"):
    if pattern.startswith("quarter:"):
    month = timestamp.month
    month = timestamp.month
    quarter = int(pattern[8:])
    quarter = int(pattern[8:])
    return month in self.quarters.get(quarter, [])
    return month in self.quarters.get(quarter, [])


    # Check holiday pattern
    # Check holiday pattern
    if pattern.startswith("holiday:"):
    if pattern.startswith("holiday:"):
    holiday = pattern[8:]
    holiday = pattern[8:]
    if holiday in self.holidays:
    if holiday in self.holidays:
    holiday_month, holiday_day, holiday_duration = self.holidays[holiday]
    holiday_month, holiday_day, holiday_duration = self.holidays[holiday]


    # Create holiday start date for the current year
    # Create holiday start date for the current year
    holiday_start = datetime(timestamp.year, holiday_month, holiday_day)
    holiday_start = datetime(timestamp.year, holiday_month, holiday_day)


    # Create holiday end date
    # Create holiday end date
    holiday_end = holiday_start + timedelta(days=holiday_duration)
    holiday_end = holiday_start + timedelta(days=holiday_duration)


    # Check if timestamp is within the holiday period
    # Check if timestamp is within the holiday period
    return holiday_start <= timestamp <= holiday_end
    return holiday_start <= timestamp <= holiday_end


    # Unknown pattern
    # Unknown pattern
    return False
    return False


    def matches_range_pattern(self, pattern: str, value: int) -> bool:
    def matches_range_pattern(self, pattern: str, value: int) -> bool:
    """
    """
    Check if a value matches a range pattern.
    Check if a value matches a range pattern.


    Args:
    Args:
    pattern: Range pattern to check (e.g., "1-5", "1,3,5", "1-3,5-7")
    pattern: Range pattern to check (e.g., "1-5", "1,3,5", "1-3,5-7")
    value: Value to check
    value: Value to check


    Returns:
    Returns:
    True if the value matches the pattern, False otherwise
    True if the value matches the pattern, False otherwise
    """
    """
    # Split pattern into ranges
    # Split pattern into ranges
    ranges = pattern.split(",")
    ranges = pattern.split(",")


    for range_str in ranges:
    for range_str in ranges:
    # Check if range has a min and max
    # Check if range has a min and max
    if "-" in range_str:
    if "-" in range_str:
    range_min, range_max = map(int, range_str.split("-", 1))
    range_min, range_max = map(int, range_str.split("-", 1))
    if range_min <= value <= range_max:
    if range_min <= value <= range_max:
    return True
    return True
    else:
    else:
    # Single value
    # Single value
    if value == int(range_str):
    if value == int(range_str):
    return True
    return True


    return False
    return False


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the seasonal pricing rule to a dictionary.
    Convert the seasonal pricing rule to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the seasonal pricing rule
    Dictionary representation of the seasonal pricing rule
    """
    """
    result = super().to_dict()
    result = super().to_dict()
    result.update(
    result.update(
    {"seasonal_rates": self.seasonal_rates, "default_rate": self.default_rate}
    {"seasonal_rates": self.seasonal_rates, "default_rate": self.default_rate}
    )
    )
    return result
    return result


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SeasonalPricingRule":
    def from_dict(cls, data: Dict[str, Any]) -> "SeasonalPricingRule":
    """
    """
    Create a seasonal pricing rule from a dictionary.
    Create a seasonal pricing rule from a dictionary.


    Args:
    Args:
    data: Dictionary with seasonal pricing rule data
    data: Dictionary with seasonal pricing rule data


    Returns:
    Returns:
    SeasonalPricingRule instance
    SeasonalPricingRule instance
    """
    """
    instance = cls(
    instance = cls(
    metric=data["metric"],
    metric=data["metric"],
    seasonal_rates=data.get("seasonal_rates", {}),
    seasonal_rates=data.get("seasonal_rates", {}),
    default_rate=data.get("default_rate", 0.0),
    default_rate=data.get("default_rate", 0.0),
    name=data.get("name", "Seasonal Pricing"),
    name=data.get("name", "Seasonal Pricing"),
    description=data.get("description", "Pricing based on seasons or months"),
    description=data.get("description", "Pricing based on seasons or months"),
    category=data.get("category"),
    category=data.get("category"),
    resource_type=data.get("resource_type"),
    resource_type=data.get("resource_type"),
    minimum_cost=data.get("minimum_cost", 0.0),
    minimum_cost=data.get("minimum_cost", 0.0),
    maximum_cost=data.get("maximum_cost"),
    maximum_cost=data.get("maximum_cost"),
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    if "id" in data:
    if "id" in data:
    instance.id = data["id"]
    instance.id = data["id"]


    if "created_at" in data:
    if "created_at" in data:
    instance.created_at = datetime.fromisoformat(data["created_at"])
    instance.created_at = datetime.fromisoformat(data["created_at"])


    if "updated_at" in data:
    if "updated_at" in data:
    instance.updated_at = datetime.fromisoformat(data["updated_at"])
    instance.updated_at = datetime.fromisoformat(data["updated_at"])


    return instance
    return instance




    class CustomerSegmentPricingRule(CustomPricingRule):
    class CustomerSegmentPricingRule(CustomPricingRule):
    """
    """
    Customer segment pricing rule.
    Customer segment pricing rule.


    This class implements a pricing rule that applies different rates
    This class implements a pricing rule that applies different rates
    based on customer segments or attributes.
    based on customer segments or attributes.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    metric: str,
    metric: str,
    segment_rates: Dict[str, float],
    segment_rates: Dict[str, float],
    default_rate: float = 0.0,
    default_rate: float = 0.0,
    name: str = "Customer Segment Pricing",
    name: str = "Customer Segment Pricing",
    description: str = "Pricing based on customer segments",
    description: str = "Pricing based on customer segments",
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a customer segment pricing rule.
    Initialize a customer segment pricing rule.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    segment_rates: Dictionary mapping segment patterns to rates
    segment_rates: Dictionary mapping segment patterns to rates
    default_rate: Default rate to use if no segment pattern matches
    default_rate: Default rate to use if no segment pattern matches
    name: Name of the custom pricing rule
    name: Name of the custom pricing rule
    description: Description of the custom pricing rule
    description: Description of the custom pricing rule
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource
    minimum_cost: Minimum cost
    minimum_cost: Minimum cost
    maximum_cost: Maximum cost
    maximum_cost: Maximum cost
    metadata: Additional metadata for the custom pricing rule
    metadata: Additional metadata for the custom pricing rule


    Segment patterns can be specified in the following formats:
    Segment patterns can be specified in the following formats:
    - "tier:free": Free tier customers
    - "tier:free": Free tier customers
    - "tier:premium": Premium tier customers
    - "tier:premium": Premium tier customers
    - "tier:enterprise": Enterprise tier customers
    - "tier:enterprise": Enterprise tier customers
    - "industry:healthcare": Healthcare industry customers
    - "industry:healthcare": Healthcare industry customers
    - "industry:finance": Finance industry customers
    - "industry:finance": Finance industry customers
    - "size:small": Small businesses (e.g., 1-50 employees)
    - "size:small": Small businesses (e.g., 1-50 employees)
    - "size:medium": Medium businesses (e.g., 51-500 employees)
    - "size:medium": Medium businesses (e.g., 51-500 employees)
    - "size:large": Large businesses (e.g., 501+ employees)
    - "size:large": Large businesses (e.g., 501+ employees)
    - "region:us": Customers in the United States
    - "region:us": Customers in the United States
    - "region:eu": Customers in the European Union
    - "region:eu": Customers in the European Union
    - "age:0-30": New customers (0-30 days)
    - "age:0-30": New customers (0-30 days)
    - "age:31-90": Recent customers (31-90 days)
    - "age:31-90": Recent customers (31-90 days)
    - "age:91+": Established customers (91+ days)
    - "age:91+": Established customers (91+ days)
    - "usage:low": Low usage customers
    - "usage:low": Low usage customers
    - "usage:medium": Medium usage customers
    - "usage:medium": Medium usage customers
    - "usage:high": High usage customers
    - "usage:high": High usage customers
    """
    """
    super().__init__(
    super().__init__(
    metric=metric,
    metric=metric,
    name=name,
    name=name,
    description=description,
    description=description,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    minimum_cost=minimum_cost,
    minimum_cost=minimum_cost,
    maximum_cost=maximum_cost,
    maximum_cost=maximum_cost,
    metadata=metadata,
    metadata=metadata,
    )
    )


    self.segment_rates = segment_rates
    self.segment_rates = segment_rates
    self.default_rate = default_rate
    self.default_rate = default_rate


    def calculate_custom_cost(
    def calculate_custom_cost(
    self,
    self,
    quantity: float,
    quantity: float,
    customer_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    customer_data: Optional[Dict[str, Any]] = None,
    customer_data: Optional[Dict[str, Any]] = None,
    ) -> float:
    ) -> float:
    """
    """
    Calculate the cost based on the customer segment.
    Calculate the cost based on the customer segment.


    Args:
    Args:
    quantity: Quantity to calculate cost for
    quantity: Quantity to calculate cost for
    customer_id: ID of the customer
    customer_id: ID of the customer
    customer_data: Additional customer data
    customer_data: Additional customer data


    Returns:
    Returns:
    Cost for the quantity
    Cost for the quantity
    """
    """
    # If no customer data is provided, use default rate
    # If no customer data is provided, use default rate
    if not customer_data:
    if not customer_data:
    return quantity * self.default_rate
    return quantity * self.default_rate


    # Find the applicable rate
    # Find the applicable rate
    rate = self.get_rate_for_segment(customer_data)
    rate = self.get_rate_for_segment(customer_data)


    # Calculate cost
    # Calculate cost
    return quantity * rate
    return quantity * rate


    def get_rate_for_segment(self, customer_data: Dict[str, Any]) -> float:
    def get_rate_for_segment(self, customer_data: Dict[str, Any]) -> float:
    """
    """
    Get the rate applicable for a specific customer segment.
    Get the rate applicable for a specific customer segment.


    Args:
    Args:
    customer_data: Customer data to determine segment
    customer_data: Customer data to determine segment


    Returns:
    Returns:
    Applicable rate for the customer segment
    Applicable rate for the customer segment
    """
    """
    # Check each segment pattern
    # Check each segment pattern
    for pattern, rate in self.segment_rates.items():
    for pattern, rate in self.segment_rates.items():
    if self.matches_segment_pattern(pattern, customer_data):
    if self.matches_segment_pattern(pattern, customer_data):
    return rate
    return rate


    # Return default rate if no pattern matches
    # Return default rate if no pattern matches
    return self.default_rate
    return self.default_rate


    def matches_segment_pattern(
    def matches_segment_pattern(
    self, pattern: str, customer_data: Dict[str, Any]
    self, pattern: str, customer_data: Dict[str, Any]
    ) -> bool:
    ) -> bool:
    """
    """
    Check if customer data matches a segment pattern.
    Check if customer data matches a segment pattern.


    Args:
    Args:
    pattern: Segment pattern to check
    pattern: Segment pattern to check
    customer_data: Customer data to check
    customer_data: Customer data to check


    Returns:
    Returns:
    True if the customer data matches the pattern, False otherwise
    True if the customer data matches the pattern, False otherwise
    """
    """
    # Split pattern into type and value
    # Split pattern into type and value
    if ":" not in pattern:
    if ":" not in pattern:
    return False
    return False


    pattern_type, pattern_value = pattern.split(":", 1)
    pattern_type, pattern_value = pattern.split(":", 1)


    # Check tier pattern
    # Check tier pattern
    if pattern_type == "tier":
    if pattern_type == "tier":
    customer_tier = customer_data.get("tier", "").lower()
    customer_tier = customer_data.get("tier", "").lower()
    return customer_tier == pattern_value.lower()
    return customer_tier == pattern_value.lower()


    # Check industry pattern
    # Check industry pattern
    if pattern_type == "industry":
    if pattern_type == "industry":
    customer_industry = customer_data.get("industry", "").lower()
    customer_industry = customer_data.get("industry", "").lower()
    return customer_industry == pattern_value.lower()
    return customer_industry == pattern_value.lower()


    # Check size pattern
    # Check size pattern
    if pattern_type == "size":
    if pattern_type == "size":
    customer_size = customer_data.get("size", "").lower()
    customer_size = customer_data.get("size", "").lower()
    return customer_size == pattern_value.lower()
    return customer_size == pattern_value.lower()


    # Check region pattern
    # Check region pattern
    if pattern_type == "region":
    if pattern_type == "region":
    customer_region = customer_data.get("region", "").lower()
    customer_region = customer_data.get("region", "").lower()
    return customer_region == pattern_value.lower()
    return customer_region == pattern_value.lower()


    # Check age pattern (days since customer creation)
    # Check age pattern (days since customer creation)
    if pattern_type == "age":
    if pattern_type == "age":
    if "created_at" not in customer_data:
    if "created_at" not in customer_data:
    return False
    return False


    try:
    try:
    created_at = datetime.fromisoformat(customer_data["created_at"])
    created_at = datetime.fromisoformat(customer_data["created_at"])
    days_since_creation = (datetime.now() - created_at).days
    days_since_creation = (datetime.now() - created_at).days


    return self.matches_range_pattern(pattern_value, days_since_creation)
    return self.matches_range_pattern(pattern_value, days_since_creation)
except (ValueError, TypeError):
except (ValueError, TypeError):
    return False
    return False


    # Check usage pattern
    # Check usage pattern
    if pattern_type == "usage":
    if pattern_type == "usage":
    customer_usage = customer_data.get("usage_level", "").lower()
    customer_usage = customer_data.get("usage_level", "").lower()
    return customer_usage == pattern_value.lower()
    return customer_usage == pattern_value.lower()


    # Unknown pattern type
    # Unknown pattern type
    return False
    return False


    def matches_range_pattern(self, pattern: str, value: int) -> bool:
    def matches_range_pattern(self, pattern: str, value: int) -> bool:
    """
    """
    Check if a value matches a range pattern.
    Check if a value matches a range pattern.


    Args:
    Args:
    pattern: Range pattern to check (e.g., "1-5", "1,3,5", "1-3,5-7", "91+")
    pattern: Range pattern to check (e.g., "1-5", "1,3,5", "1-3,5-7", "91+")
    value: Value to check
    value: Value to check


    Returns:
    Returns:
    True if the value matches the pattern, False otherwise
    True if the value matches the pattern, False otherwise
    """
    """
    # Check for "X+" pattern (X or greater)
    # Check for "X+" pattern (X or greater)
    if pattern.endswith("+"):
    if pattern.endswith("+"):
    try:
    try:
    min_value = int(pattern[:-1])
    min_value = int(pattern[:-1])
    return value >= min_value
    return value >= min_value
except ValueError:
except ValueError:
    return False
    return False


    # Split pattern into ranges
    # Split pattern into ranges
    ranges = pattern.split(",")
    ranges = pattern.split(",")


    for range_str in ranges:
    for range_str in ranges:
    # Check if range has a min and max
    # Check if range has a min and max
    if "-" in range_str:
    if "-" in range_str:
    range_min, range_max = map(int, range_str.split("-", 1))
    range_min, range_max = map(int, range_str.split("-", 1))
    if range_min <= value <= range_max:
    if range_min <= value <= range_max:
    return True
    return True
    else:
    else:
    # Single value
    # Single value
    try:
    try:
    if value == int(range_str):
    if value == int(range_str):
    return True
    return True
except ValueError:
except ValueError:
    continue
    continue


    return False
    return False


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the customer segment pricing rule to a dictionary.
    Convert the customer segment pricing rule to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the customer segment pricing rule
    Dictionary representation of the customer segment pricing rule
    """
    """
    result = super().to_dict()
    result = super().to_dict()
    result.update(
    result.update(
    {"segment_rates": self.segment_rates, "default_rate": self.default_rate}
    {"segment_rates": self.segment_rates, "default_rate": self.default_rate}
    )
    )
    return result
    return result


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CustomerSegmentPricingRule":
    def from_dict(cls, data: Dict[str, Any]) -> "CustomerSegmentPricingRule":
    """
    """
    Create a customer segment pricing rule from a dictionary.
    Create a customer segment pricing rule from a dictionary.


    Args:
    Args:
    data: Dictionary with customer segment pricing rule data
    data: Dictionary with customer segment pricing rule data


    Returns:
    Returns:
    CustomerSegmentPricingRule instance
    CustomerSegmentPricingRule instance
    """
    """
    instance = cls(
    instance = cls(
    metric=data["metric"],
    metric=data["metric"],
    segment_rates=data.get("segment_rates", {}),
    segment_rates=data.get("segment_rates", {}),
    default_rate=data.get("default_rate", 0.0),
    default_rate=data.get("default_rate", 0.0),
    name=data.get("name", "Customer Segment Pricing"),
    name=data.get("name", "Customer Segment Pricing"),
    description=data.get("description", "Pricing based on customer segments"),
    description=data.get("description", "Pricing based on customer segments"),
    category=data.get("category"),
    category=data.get("category"),
    resource_type=data.get("resource_type"),
    resource_type=data.get("resource_type"),
    minimum_cost=data.get("minimum_cost", 0.0),
    minimum_cost=data.get("minimum_cost", 0.0),
    maximum_cost=data.get("maximum_cost"),
    maximum_cost=data.get("maximum_cost"),
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    if "id" in data:
    if "id" in data:
    instance.id = data["id"]
    instance.id = data["id"]


    if "created_at" in data:
    if "created_at" in data:
    instance.created_at = datetime.fromisoformat(data["created_at"])
    instance.created_at = datetime.fromisoformat(data["created_at"])


    if "updated_at" in data:
    if "updated_at" in data:
    instance.updated_at = datetime.fromisoformat(data["updated_at"])
    instance.updated_at = datetime.fromisoformat(data["updated_at"])


    return instance
    return instance




    class ConditionalPricingRule(CustomPricingRule):
    class ConditionalPricingRule(CustomPricingRule):
    """
    """
    Conditional pricing rule.
    Conditional pricing rule.


    This class implements a pricing rule that applies different rates
    This class implements a pricing rule that applies different rates
    based on complex conditions involving multiple factors.
    based on complex conditions involving multiple factors.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    metric: str,
    metric: str,
    conditions: List[Dict[str, Any]],
    conditions: List[Dict[str, Any]],
    default_rate: float = 0.0,
    default_rate: float = 0.0,
    name: str = "Conditional Pricing",
    name: str = "Conditional Pricing",
    description: str = "Pricing based on complex conditions",
    description: str = "Pricing based on complex conditions",
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a conditional pricing rule.
    Initialize a conditional pricing rule.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    conditions: List of condition dictionaries
    conditions: List of condition dictionaries
    default_rate: Default rate to use if no condition matches
    default_rate: Default rate to use if no condition matches
    name: Name of the custom pricing rule
    name: Name of the custom pricing rule
    description: Description of the custom pricing rule
    description: Description of the custom pricing rule
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource
    minimum_cost: Minimum cost
    minimum_cost: Minimum cost
    maximum_cost: Maximum cost
    maximum_cost: Maximum cost
    metadata: Additional metadata for the custom pricing rule
    metadata: Additional metadata for the custom pricing rule


    Each condition dictionary should have the following structure:
    Each condition dictionary should have the following structure:
    {
    {
    "condition": "expression",  # Condition expression
    "condition": "expression",  # Condition expression
    "rate": 0.01  # Rate to apply if condition is met
    "rate": 0.01  # Rate to apply if condition is met
    }
    }


    Condition expressions can use the following variables:
    Condition expressions can use the following variables:
    - quantity: The quantity being priced
    - quantity: The quantity being priced
    - customer.X: Customer attribute X (e.g., customer.tier)
    - customer.X: Customer attribute X (e.g., customer.tier)
    - time.X: Time attribute X (e.g., time.hour, time.weekday)
    - time.X: Time attribute X (e.g., time.hour, time.weekday)
    - usage.X: Usage attribute X (e.g., usage.total, usage.average)
    - usage.X: Usage attribute X (e.g., usage.total, usage.average)


    Condition expressions can use the following operators:
    Condition expressions can use the following operators:
    - Comparison: ==, !=, <, >, <=, >=
    - Comparison: ==, !=, <, >, <=, >=
    - Logical: and, or, not
    - Logical: and, or, not
    - Arithmetic: +, -, *, /, %
    - Arithmetic: +, -, *, /, %
    - Membership: in, not in
    - Membership: in, not in


    Examples:
    Examples:
    - "quantity > 1000"
    - "quantity > 1000"
    - "customer.tier == 'premium'"
    - "customer.tier == 'premium'"
    - "time.weekday in [1, 2, 3, 4, 5]"
    - "time.weekday in [1, 2, 3, 4, 5]"
    - "usage.total > 10000 and customer.age > 90"
    - "usage.total > 10000 and customer.age > 90"
    """
    """
    super().__init__(
    super().__init__(
    metric=metric,
    metric=metric,
    name=name,
    name=name,
    description=description,
    description=description,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    minimum_cost=minimum_cost,
    minimum_cost=minimum_cost,
    maximum_cost=maximum_cost,
    maximum_cost=maximum_cost,
    metadata=metadata,
    metadata=metadata,
    )
    )


    self.conditions = conditions
    self.conditions = conditions
    self.default_rate = default_rate
    self.default_rate = default_rate


    def calculate_custom_cost(
    def calculate_custom_cost(
    self, quantity: float, context: Optional[Dict[str, Any]] = None
    self, quantity: float, context: Optional[Dict[str, Any]] = None
    ) -> float:
    ) -> float:
    """
    """
    Calculate the cost based on conditions.
    Calculate the cost based on conditions.


    Args:
    Args:
    quantity: Quantity to calculate cost for
    quantity: Quantity to calculate cost for
    context: Additional context for condition evaluation
    context: Additional context for condition evaluation


    Returns:
    Returns:
    Cost for the quantity
    Cost for the quantity
    """
    """
    # If no context is provided, use default rate
    # If no context is provided, use default rate
    if not context:
    if not context:
    return quantity * self.default_rate
    return quantity * self.default_rate


    # Find the applicable rate
    # Find the applicable rate
    rate = self.get_rate_for_conditions(quantity, context)
    rate = self.get_rate_for_conditions(quantity, context)


    # Calculate cost
    # Calculate cost
    return quantity * rate
    return quantity * rate


    def get_rate_for_conditions(
    def get_rate_for_conditions(
    self, quantity: float, context: Dict[str, Any]
    self, quantity: float, context: Dict[str, Any]
    ) -> float:
    ) -> float:
    """
    """
    Get the rate applicable based on conditions.
    Get the rate applicable based on conditions.


    Args:
    Args:
    quantity: Quantity being priced
    quantity: Quantity being priced
    context: Context for condition evaluation
    context: Context for condition evaluation


    Returns:
    Returns:
    Applicable rate based on conditions
    Applicable rate based on conditions
    """
    """
    # Prepare evaluation context
    # Prepare evaluation context
    eval_context = self.prepare_eval_context(quantity, context)
    eval_context = self.prepare_eval_context(quantity, context)


    # Check each condition
    # Check each condition
    for condition_data in self.conditions:
    for condition_data in self.conditions:
    condition_expr = condition_data.get("condition", "False")
    condition_expr = condition_data.get("condition", "False")
    rate = condition_data.get("rate", self.default_rate)
    rate = condition_data.get("rate", self.default_rate)


    try:
    try:
    # Evaluate the condition
    # Evaluate the condition
    if self.evaluate_condition(condition_expr, eval_context):
    if self.evaluate_condition(condition_expr, eval_context):
    return rate
    return rate
except Exception as e:
except Exception as e:
    # Log the error and continue to the next condition
    # Log the error and continue to the next condition
    print(f"Error evaluating condition '{condition_expr}': {e}")
    print(f"Error evaluating condition '{condition_expr}': {e}")
    continue
    continue


    # Return default rate if no condition matches
    # Return default rate if no condition matches
    return self.default_rate
    return self.default_rate


    def prepare_eval_context(
    def prepare_eval_context(
    self, quantity: float, context: Dict[str, Any]
    self, quantity: float, context: Dict[str, Any]
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Prepare the evaluation context for condition expressions.
    Prepare the evaluation context for condition expressions.


    Args:
    Args:
    quantity: Quantity being priced
    quantity: Quantity being priced
    context: Original context
    context: Original context


    Returns:
    Returns:
    Prepared evaluation context
    Prepared evaluation context
    """
    """
    # Start with a clean context
    # Start with a clean context
    eval_context = {"quantity": quantity, "customer": {}, "time": {}, "usage": {}}
    eval_context = {"quantity": quantity, "customer": {}, "time": {}, "usage": {}}


    # Add customer data
    # Add customer data
    if "customer" in context:
    if "customer" in context:
    eval_context["customer"] = context["customer"]
    eval_context["customer"] = context["customer"]


    # Add time data
    # Add time data
    if "time" in context:
    if "time" in context:
    eval_context["time"] = context["time"]
    eval_context["time"] = context["time"]
    else:
    else:
    # Add default time data
    # Add default time data
    now = datetime.now()
    now = datetime.now()
    eval_context["time"] = {
    eval_context["time"] = {
    "hour": now.hour,
    "hour": now.hour,
    "minute": now.minute,
    "minute": now.minute,
    "second": now.second,
    "second": now.second,
    "day": now.day,
    "day": now.day,
    "month": now.month,
    "month": now.month,
    "year": now.year,
    "year": now.year,
    "weekday": now.isoweekday(),
    "weekday": now.isoweekday(),
    "is_weekend": now.isoweekday() >= 6,
    "is_weekend": now.isoweekday() >= 6,
    }
    }


    # Add usage data
    # Add usage data
    if "usage" in context:
    if "usage" in context:
    eval_context["usage"] = context["usage"]
    eval_context["usage"] = context["usage"]


    return eval_context
    return eval_context


    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
    """
    """
    Evaluate a condition expression.
    Evaluate a condition expression.


    Args:
    Args:
    condition: Condition expression to evaluate
    condition: Condition expression to evaluate
    context: Evaluation context
    context: Evaluation context


    Returns:
    Returns:
    True if the condition is met, False otherwise
    True if the condition is met, False otherwise
    """
    """
    # Replace variable references with dictionary lookups
    # Replace variable references with dictionary lookups
    # For example, replace "customer.tier" with "context['customer']['tier']"
    # For example, replace "customer.tier" with "context['customer']['tier']"
    pattern = r"(customer|time|usage)\.([a-zA-Z_][a-zA-Z0-9_]*)"
    pattern = r"(customer|time|usage)\.([a-zA-Z_][a-zA-Z0-9_]*)"


    def replace_var(match):
    def replace_var(match):
    category, attr = match.groups()
    category, attr = match.groups()
    return f"context['{category}'].get('{attr}')"
    return f"context['{category}'].get('{attr}')"


    expr = re.sub(pattern, replace_var, condition)
    expr = re.sub(pattern, replace_var, condition)


    # Add safety checks
    # Add safety checks
    if "import" in expr or "exec" in expr or "__" in expr:
    if "import" in expr or "exec" in expr or "__" in expr:
    raise ValueError(f"Unsafe expression: {expr}")
    raise ValueError(f"Unsafe expression: {expr}")


    # Evaluate the expression
    # Evaluate the expression
    try:
    try:
    result = eval(expr, {"__builtins__": {}}, {"context": context})
    result = eval(expr, {"__builtins__": {}}, {"context": context})
    return bool(result)
    return bool(result)
except Exception as e:
except Exception as e:
    raise ValueError(f"Error evaluating expression '{expr}': {e}")
    raise ValueError(f"Error evaluating expression '{expr}': {e}")


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the conditional pricing rule to a dictionary.
    Convert the conditional pricing rule to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the conditional pricing rule
    Dictionary representation of the conditional pricing rule
    """
    """
    result = super().to_dict()
    result = super().to_dict()
    result.update(
    result.update(
    {"conditions": self.conditions, "default_rate": self.default_rate}
    {"conditions": self.conditions, "default_rate": self.default_rate}
    )
    )
    return result
    return result


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConditionalPricingRule":
    def from_dict(cls, data: Dict[str, Any]) -> "ConditionalPricingRule":
    """
    """
    Create a conditional pricing rule from a dictionary.
    Create a conditional pricing rule from a dictionary.


    Args:
    Args:
    data: Dictionary with conditional pricing rule data
    data: Dictionary with conditional pricing rule data


    Returns:
    Returns:
    ConditionalPricingRule instance
    ConditionalPricingRule instance
    """
    """
    instance = cls(
    instance = cls(
    metric=data["metric"],
    metric=data["metric"],
    conditions=data.get("conditions", []),
    conditions=data.get("conditions", []),
    default_rate=data.get("default_rate", 0.0),
    default_rate=data.get("default_rate", 0.0),
    name=data.get("name", "Conditional Pricing"),
    name=data.get("name", "Conditional Pricing"),
    description=data.get("description", "Pricing based on complex conditions"),
    description=data.get("description", "Pricing based on complex conditions"),
    category=data.get("category"),
    category=data.get("category"),
    resource_type=data.get("resource_type"),
    resource_type=data.get("resource_type"),
    minimum_cost=data.get("minimum_cost", 0.0),
    minimum_cost=data.get("minimum_cost", 0.0),
    maximum_cost=data.get("maximum_cost"),
    maximum_cost=data.get("maximum_cost"),
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    if "id" in data:
    if "id" in data:
    instance.id = data["id"]
    instance.id = data["id"]


    if "created_at" in data:
    if "created_at" in data:
    instance.created_at = datetime.fromisoformat(data["created_at"])
    instance.created_at = datetime.fromisoformat(data["created_at"])


    if "updated_at" in data:
    if "updated_at" in data:
    instance.updated_at = datetime.fromisoformat(data["updated_at"])
    instance.updated_at = datetime.fromisoformat(data["updated_at"])


    return instance
    return instance




    class FormulaBasedPricingRule(CustomPricingRule):
    class FormulaBasedPricingRule(CustomPricingRule):
    """
    """
    Formula-based pricing rule.
    Formula-based pricing rule.


    This class implements a pricing rule that calculates costs using
    This class implements a pricing rule that calculates costs using
    mathematical formulas or expressions.
    mathematical formulas or expressions.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    metric: str,
    metric: str,
    formula: str,
    formula: str,
    variables: Optional[Dict[str, Any]] = None,
    variables: Optional[Dict[str, Any]] = None,
    name: str = "Formula-Based Pricing",
    name: str = "Formula-Based Pricing",
    description: str = "Pricing based on mathematical formulas",
    description: str = "Pricing based on mathematical formulas",
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a formula-based pricing rule.
    Initialize a formula-based pricing rule.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    formula: Formula expression for calculating cost
    formula: Formula expression for calculating cost
    variables: Dictionary of variables to use in the formula
    variables: Dictionary of variables to use in the formula
    name: Name of the custom pricing rule
    name: Name of the custom pricing rule
    description: Description of the custom pricing rule
    description: Description of the custom pricing rule
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource
    minimum_cost: Minimum cost
    minimum_cost: Minimum cost
    maximum_cost: Maximum cost
    maximum_cost: Maximum cost
    metadata: Additional metadata for the custom pricing rule
    metadata: Additional metadata for the custom pricing rule


    Formula expressions can use the following variables:
    Formula expressions can use the following variables:
    - q: The quantity being priced
    - q: The quantity being priced
    - Any variables defined in the variables dictionary
    - Any variables defined in the variables dictionary


    Formula expressions can use the following operators and functions:
    Formula expressions can use the following operators and functions:
    - Arithmetic: +, -, *, /, %, **
    - Arithmetic: +, -, *, /, %, **
    - Math functions: abs, min, max, round, floor, ceil, sqrt, log, log10, exp
    - Math functions: abs, min, max, round, floor, ceil, sqrt, log, log10, exp
    - Trigonometric functions: sin, cos, tan
    - Trigonometric functions: sin, cos, tan


    Examples:
    Examples:
    - "q * 0.01": Simple per-unit pricing
    - "q * 0.01": Simple per-unit pricing
    - "10 + q * 0.005": Base fee plus per-unit pricing
    - "10 + q * 0.005": Base fee plus per-unit pricing
    - "q * (1 - discount)": Discounted pricing
    - "q * (1 - discount)": Discounted pricing
    - "base_price * (1 - volume_discount * (q / 1000))": Volume discount pricing
    - "base_price * (1 - volume_discount * (q / 1000))": Volume discount pricing
    - "min(q * 0.01, 100)": Capped pricing
    - "min(q * 0.01, 100)": Capped pricing
    - "max(10, q * 0.005)": Minimum pricing
    - "max(10, q * 0.005)": Minimum pricing
    - "q * rate * (1 - seasonal_discount)": Seasonal discount pricing
    - "q * rate * (1 - seasonal_discount)": Seasonal discount pricing
    """
    """
    super().__init__(
    super().__init__(
    metric=metric,
    metric=metric,
    name=name,
    name=name,
    description=description,
    description=description,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    minimum_cost=minimum_cost,
    minimum_cost=minimum_cost,
    maximum_cost=maximum_cost,
    maximum_cost=maximum_cost,
    metadata=metadata,
    metadata=metadata,
    )
    )


    self.formula = formula
    self.formula = formula
    self.variables = variables or {}
    self.variables = variables or {}


    # Validate the formula
    # Validate the formula
    self.validate_formula()
    self.validate_formula()


    def validate_formula(self) -> None:
    def validate_formula(self) -> None:
    """
    """
    Validate the formula expression.
    Validate the formula expression.


    Raises:
    Raises:
    ValueError: If the formula is invalid
    ValueError: If the formula is invalid
    """
    """
    try:
    try:
    # Test with a simple quantity
    # Test with a simple quantity
    self.evaluate_formula(10.0, self.variables)
    self.evaluate_formula(10.0, self.variables)
except Exception as e:
except Exception as e:
    raise ValueError(f"Invalid formula '{self.formula}': {e}")
    raise ValueError(f"Invalid formula '{self.formula}': {e}")


    def calculate_custom_cost(
    def calculate_custom_cost(
    self, quantity: float, context: Optional[Dict[str, Any]] = None
    self, quantity: float, context: Optional[Dict[str, Any]] = None
    ) -> float:
    ) -> float:
    """
    """
    Calculate the cost using the formula.
    Calculate the cost using the formula.


    Args:
    Args:
    quantity: Quantity to calculate cost for
    quantity: Quantity to calculate cost for
    context: Additional context for formula evaluation
    context: Additional context for formula evaluation


    Returns:
    Returns:
    Cost for the quantity
    Cost for the quantity
    """
    """
    # Prepare variables
    # Prepare variables
    variables = self.prepare_variables(quantity, context)
    variables = self.prepare_variables(quantity, context)


    # Evaluate the formula
    # Evaluate the formula
    return self.evaluate_formula(quantity, variables)
    return self.evaluate_formula(quantity, variables)


    def prepare_variables(
    def prepare_variables(
    self, quantity: float, context: Optional[Dict[str, Any]] = None
    self, quantity: float, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Prepare variables for formula evaluation.
    Prepare variables for formula evaluation.


    Args:
    Args:
    quantity: Quantity being priced
    quantity: Quantity being priced
    context: Additional context
    context: Additional context


    Returns:
    Returns:
    Dictionary of variables for formula evaluation
    Dictionary of variables for formula evaluation
    """
    """
    # Start with the base variables
    # Start with the base variables
    variables = dict(self.variables)
    variables = dict(self.variables)


    # Add quantity variable
    # Add quantity variable
    variables["q"] = quantity
    variables["q"] = quantity


    # Add context variables if provided
    # Add context variables if provided
    if context:
    if context:
    # Add customer variables
    # Add customer variables
    if "customer" in context:
    if "customer" in context:
    for key, value in context["customer"].items():
    for key, value in context["customer"].items():
    variables[f"customer_{key}"] = value
    variables[f"customer_{key}"] = value


    # Add time variables
    # Add time variables
    if "time" in context:
    if "time" in context:
    for key, value in context["time"].items():
    for key, value in context["time"].items():
    variables[f"time_{key}"] = value
    variables[f"time_{key}"] = value


    # Add usage variables
    # Add usage variables
    if "usage" in context:
    if "usage" in context:
    for key, value in context["usage"].items():
    for key, value in context["usage"].items():
    variables[f"usage_{key}"] = value
    variables[f"usage_{key}"] = value


    return variables
    return variables


    def evaluate_formula(self, quantity: float, variables: Dict[str, Any]) -> float:
    def evaluate_formula(self, quantity: float, variables: Dict[str, Any]) -> float:
    """
    """
    Evaluate the formula expression.
    Evaluate the formula expression.


    Args:
    Args:
    quantity: Quantity being priced
    quantity: Quantity being priced
    variables: Variables for formula evaluation
    variables: Variables for formula evaluation


    Returns:
    Returns:
    Result of the formula evaluation
    Result of the formula evaluation
    """
    """
    # Create a safe math environment
    # Create a safe math environment
    safe_math = {
    safe_math = {
    # Basic math functions
    # Basic math functions
    "abs": abs,
    "abs": abs,
    "min": min,
    "min": min,
    "max": max,
    "max": max,
    "round": round,
    "round": round,
    "floor": math.floor,
    "floor": math.floor,
    "ceil": math.ceil,
    "ceil": math.ceil,
    "sqrt": math.sqrt,
    "sqrt": math.sqrt,
    "log": math.log,
    "log": math.log,
    "log10": math.log10,
    "log10": math.log10,
    "exp": math.exp,
    "exp": math.exp,
    # Trigonometric functions
    # Trigonometric functions
    "sin": math.sin,
    "sin": math.sin,
    "cos": math.cos,
    "cos": math.cos,
    "tan": math.tan,
    "tan": math.tan,
    # Constants
    # Constants
    "pi": math.pi,
    "pi": math.pi,
    "e": math.e,
    "e": math.e,
    }
    }


    # Add variables to the environment
    # Add variables to the environment
    safe_math.update(variables)
    safe_math.update(variables)


    # Add safety checks
    # Add safety checks
    if "import" in self.formula or "exec" in self.formula or "__" in self.formula:
    if "import" in self.formula or "exec" in self.formula or "__" in self.formula:
    raise ValueError(f"Unsafe formula: {self.formula}")
    raise ValueError(f"Unsafe formula: {self.formula}")


    # Evaluate the formula
    # Evaluate the formula
    try:
    try:
    result = eval(self.formula, {"__builtins__": {}}, safe_math)
    result = eval(self.formula, {"__builtins__": {}}, safe_math)
    return float(result)
    return float(result)
except Exception as e:
except Exception as e:
    raise ValueError(f"Error evaluating formula '{self.formula}': {e}")
    raise ValueError(f"Error evaluating formula '{self.formula}': {e}")


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the formula-based pricing rule to a dictionary.
    Convert the formula-based pricing rule to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the formula-based pricing rule
    Dictionary representation of the formula-based pricing rule
    """
    """
    result = super().to_dict()
    result = super().to_dict()
    result.update({"formula": self.formula, "variables": self.variables})
    result.update({"formula": self.formula, "variables": self.variables})
    return result
    return result


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FormulaBasedPricingRule":
    def from_dict(cls, data: Dict[str, Any]) -> "FormulaBasedPricingRule":
    """
    """
    Create a formula-based pricing rule from a dictionary.
    Create a formula-based pricing rule from a dictionary.


    Args:
    Args:
    data: Dictionary with formula-based pricing rule data
    data: Dictionary with formula-based pricing rule data


    Returns:
    Returns:
    FormulaBasedPricingRule instance
    FormulaBasedPricingRule instance
    """
    """
    instance = cls(
    instance = cls(
    metric=data["metric"],
    metric=data["metric"],
    formula=data.get("formula", "q * 0.01"),
    formula=data.get("formula", "q * 0.01"),
    variables=data.get("variables", {}),
    variables=data.get("variables", {}),
    name=data.get("name", "Formula-Based Pricing"),
    name=data.get("name", "Formula-Based Pricing"),
    description=data.get(
    description=data.get(
    "description", "Pricing based on mathematical formulas"
    "description", "Pricing based on mathematical formulas"
    ),
    ),
    category=data.get("category"),
    category=data.get("category"),
    resource_type=data.get("resource_type"),
    resource_type=data.get("resource_type"),
    minimum_cost=data.get("minimum_cost", 0.0),
    minimum_cost=data.get("minimum_cost", 0.0),
    maximum_cost=data.get("maximum_cost"),
    maximum_cost=data.get("maximum_cost"),
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    if "id" in data:
    if "id" in data:
    instance.id = data["id"]
    instance.id = data["id"]


    if "created_at" in data:
    if "created_at" in data:
    instance.created_at = datetime.fromisoformat(data["created_at"])
    instance.created_at = datetime.fromisoformat(data["created_at"])


    if "updated_at" in data:
    if "updated_at" in data:
    instance.updated_at = datetime.fromisoformat(data["updated_at"])
    instance.updated_at = datetime.fromisoformat(data["updated_at"])


    return instance
    return instance




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a time-based pricing rule
    # Create a time-based pricing rule
    time_rule = TimeBasedPricingRule(
    time_rule = TimeBasedPricingRule(
    metric=UsageMetric.API_CALL,
    metric=UsageMetric.API_CALL,
    time_rates={
    time_rates={
    "weekday:1-5": 0.01,  # $0.01 per API call on weekdays
    "weekday:1-5": 0.01,  # $0.01 per API call on weekdays
    "weekend:6-7": 0.005,  # $0.005 per API call on weekends
    "weekend:6-7": 0.005,  # $0.005 per API call on weekends
    "hour:9-17": 0.015,  # $0.015 per API call during business hours
    "hour:9-17": 0.015,  # $0.015 per API call during business hours
    "hour:0-8,18-23": 0.008,  # $0.008 per API call during non-business hours
    "hour:0-8,18-23": 0.008,  # $0.008 per API call during non-business hours
    },
    },
    default_rate=0.01,
    default_rate=0.01,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    )
    )


    # Create a seasonal pricing rule
    # Create a seasonal pricing rule
    seasonal_rule = SeasonalPricingRule(
    seasonal_rule = SeasonalPricingRule(
    metric=UsageMetric.STORAGE,
    metric=UsageMetric.STORAGE,
    seasonal_rates={
    seasonal_rates={
    "winter": 0.05,  # $0.05 per GB in winter
    "winter": 0.05,  # $0.05 per GB in winter
    "summer": 0.03,  # $0.03 per GB in summer
    "summer": 0.03,  # $0.03 per GB in summer
    "holiday:christmas": 0.02,  # $0.02 per GB during Christmas
    "holiday:christmas": 0.02,  # $0.02 per GB during Christmas
    },
    },
    default_rate=0.04,
    default_rate=0.04,
    category=UsageCategory.STORAGE,
    category=UsageCategory.STORAGE,
    )
    )


    # Create a customer segment pricing rule
    # Create a customer segment pricing rule
    segment_rule = CustomerSegmentPricingRule(
    segment_rule = CustomerSegmentPricingRule(
    metric=UsageMetric.TOKEN,
    metric=UsageMetric.TOKEN,
    segment_rates={
    segment_rates={
    "tier:free": 0.002,  # $0.002 per token for free tier
    "tier:free": 0.002,  # $0.002 per token for free tier
    "tier:premium": 0.0015,  # $0.0015 per token for premium tier
    "tier:premium": 0.0015,  # $0.0015 per token for premium tier
    "tier:enterprise": 0.001,  # $0.001 per token for enterprise tier
    "tier:enterprise": 0.001,  # $0.001 per token for enterprise tier
    "industry:education": 0.0012,  # $0.0012 per token for education industry
    "industry:education": 0.0012,  # $0.0012 per token for education industry
    "age:0-30": 0.0018,  # $0.0018 per token for new customers
    "age:0-30": 0.0018,  # $0.0018 per token for new customers
    },
    },
    default_rate=0.002,
    default_rate=0.002,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    )
    )


    # Create a conditional pricing rule
    # Create a conditional pricing rule
    conditional_rule = ConditionalPricingRule(
    conditional_rule = ConditionalPricingRule(
    metric=UsageMetric.COMPUTE_TIME,
    metric=UsageMetric.COMPUTE_TIME,
    conditions=[
    conditions=[
    {
    {
    "condition": "quantity > 100 and customer.tier == 'premium'",
    "condition": "quantity > 100 and customer.tier == 'premium'",
    "rate": 0.08,  # $0.08 per hour for premium customers with high usage
    "rate": 0.08,  # $0.08 per hour for premium customers with high usage
    },
    },
    {
    {
    "condition": "time.is_weekend and usage.total > 1000",
    "condition": "time.is_weekend and usage.total > 1000",
    "rate": 0.06,  # $0.06 per hour on weekends with high total usage
    "rate": 0.06,  # $0.06 per hour on weekends with high total usage
    },
    },
    {
    {
    "condition": "customer.industry == 'research' and time.hour >= 22",
    "condition": "customer.industry == 'research' and time.hour >= 22",
    "rate": 0.05,  # $0.05 per hour for research customers during late hours
    "rate": 0.05,  # $0.05 per hour for research customers during late hours
    },
    },
    ],
    ],
    default_rate=0.1,  # $0.1 per hour by default
    default_rate=0.1,  # $0.1 per hour by default
    category=UsageCategory.COMPUTE,
    category=UsageCategory.COMPUTE,
    )
    )


    # Create a formula-based pricing rule
    # Create a formula-based pricing rule
    formula_rule = FormulaBasedPricingRule(
    formula_rule = FormulaBasedPricingRule(
    metric=UsageMetric.BANDWIDTH,
    metric=UsageMetric.BANDWIDTH,
    formula="base_fee + q * rate * (1 - volume_discount * min(1, q / discount_threshold))",
    formula="base_fee + q * rate * (1 - volume_discount * min(1, q / discount_threshold))",
    variables={
    variables={
    "base_fee": 5.0,  # $5.00 base fee
    "base_fee": 5.0,  # $5.00 base fee
    "rate": 0.1,  # $0.10 per GB
    "rate": 0.1,  # $0.10 per GB
    "volume_discount": 0.2,  # 20% maximum volume discount
    "volume_discount": 0.2,  # 20% maximum volume discount
    "discount_threshold": 100.0,  # Discount threshold at 100 GB
    "discount_threshold": 100.0,  # Discount threshold at 100 GB
    },
    },
    category=UsageCategory.NETWORK,
    category=UsageCategory.NETWORK,
    )
    )


    # Create a custom pricing calculator
    # Create a custom pricing calculator
    calculator = CustomPricingCalculator()
    calculator = CustomPricingCalculator()


    # Add the custom rules
    # Add the custom rules
    calculator.add_custom_rule(time_rule)
    calculator.add_custom_rule(time_rule)
    calculator.add_custom_rule(seasonal_rule)
    calculator.add_custom_rule(seasonal_rule)
    calculator.add_custom_rule(segment_rule)
    calculator.add_custom_rule(segment_rule)
    calculator.add_custom_rule(conditional_rule)
    calculator.add_custom_rule(conditional_rule)
    calculator.add_custom_rule(formula_rule)
    calculator.add_custom_rule(formula_rule)


    # Calculate cost for API calls
    # Calculate cost for API calls
    api_cost = calculator.calculate_cost(
    api_cost = calculator.calculate_cost(
    metric=UsageMetric.API_CALL, quantity=100, category=UsageCategory.INFERENCE
    metric=UsageMetric.API_CALL, quantity=100, category=UsageCategory.INFERENCE
    )
    )


    # Calculate cost for storage
    # Calculate cost for storage
    storage_cost = calculator.calculate_cost(
    storage_cost = calculator.calculate_cost(
    metric=UsageMetric.STORAGE, quantity=10, category=UsageCategory.STORAGE
    metric=UsageMetric.STORAGE, quantity=10, category=UsageCategory.STORAGE
    )
    )


    # Calculate cost for tokens with customer data
    # Calculate cost for tokens with customer data
    token_cost = calculator.calculate_cost(
    token_cost = calculator.calculate_cost(
    metric=UsageMetric.TOKEN,
    metric=UsageMetric.TOKEN,
    quantity=1000,
    quantity=1000,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    context={
    context={
    "customer": {
    "customer": {
    "tier": "premium",
    "tier": "premium",
    "industry": "education",
    "industry": "education",
    "created_at": "2023-01-01T00:00:00",
    "created_at": "2023-01-01T00:00:00",
    }
    }
    },
    },
    )
    )


    # Calculate cost for compute time with complex context
    # Calculate cost for compute time with complex context
    compute_cost = calculator.calculate_cost(
    compute_cost = calculator.calculate_cost(
    metric=UsageMetric.COMPUTE_TIME,
    metric=UsageMetric.COMPUTE_TIME,
    quantity=10,
    quantity=10,
    category=UsageCategory.COMPUTE,
    category=UsageCategory.COMPUTE,
    context={
    context={
    "customer": {"tier": "premium", "industry": "research"},
    "customer": {"tier": "premium", "industry": "research"},
    "time": {"hour": 23, "is_weekend": True},
    "time": {"hour": 23, "is_weekend": True},
    "usage": {"total": 1500},
    "usage": {"total": 1500},
    },
    },
    )
    )


    # Calculate cost for bandwidth with formula
    # Calculate cost for bandwidth with formula
    bandwidth_cost = calculator.calculate_cost(
    bandwidth_cost = calculator.calculate_cost(
    metric=UsageMetric.BANDWIDTH, quantity=50, category=UsageCategory.NETWORK
    metric=UsageMetric.BANDWIDTH, quantity=50, category=UsageCategory.NETWORK
    )
    )


    print(f"API call cost: ${api_cost:.2f}")
    print(f"API call cost: ${api_cost:.2f}")
    print(f"Storage cost: ${storage_cost:.2f}")
    print(f"Storage cost: ${storage_cost:.2f}")
    print(f"Token cost: ${token_cost:.2f}")
    print(f"Token cost: ${token_cost:.2f}")
    print(f"Compute time cost: ${compute_cost:.2f}")
    print(f"Compute time cost: ${compute_cost:.2f}")
    print(f"Bandwidth cost: ${bandwidth_cost:.2f}")
    print(f"Bandwidth cost: ${bandwidth_cost:.2f}")