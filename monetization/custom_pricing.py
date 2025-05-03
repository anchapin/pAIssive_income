"""
Custom pricing rules for the pAIssive Income project.

This module provides classes for implementing custom pricing rules,
where pricing is determined by complex conditions, formulas, or other
custom logic beyond standard pricing models.
"""

import copy
import json
import math
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .billing_calculator import BillingCalculator, PricingModel, PricingRule
from .usage_tracking import UsageCategory, UsageMetric


class CustomPricingRule(PricingRule):
    """
    Base class for custom pricing rules.

    This class extends the standard PricingRule to provide a framework for
    implementing custom pricing logic that goes beyond the standard pricing models.
    """

    def __init__(
        self,
        metric: str,
        name: str = "Custom Pricing Rule",
        description: str = "Custom pricing rule with specialized logic",
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a custom pricing rule.

        Args:
            metric: Type of usage metric
            name: Name of the custom pricing rule
            description: Description of the custom pricing rule
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost
            metadata: Additional metadata for the custom pricing rule
        """
        super().__init__(
            metric=metric,
            model=PricingModel.CUSTOM,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
            custom_calculator=self.calculate_custom_cost,
        )

        self.name = name
        self.description = description
        self.metadata = metadata or {}
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def calculate_custom_cost(self, quantity: float) -> float:
        """
        Calculate the cost using custom logic.

        This method should be overridden by subclasses to implement
        custom pricing logic.

        Args:
            quantity: Quantity to calculate cost for

        Returns:
            Cost for the quantity
        """
        # Default implementation returns 0
        return 0.0

    def get_context_data(self) -> Dict[str, Any]:
        """
        Get context data for the custom pricing rule.

        This method can be overridden by subclasses to provide
        additional context data for the custom pricing rule.

        Returns:
            Dictionary with context data
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "metric": self.metric,
            "category": self.category,
            "resource_type": self.resource_type,
            "minimum_cost": self.minimum_cost,
            "maximum_cost": self.maximum_cost,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the custom pricing rule to a dictionary.

        Returns:
            Dictionary representation of the custom pricing rule
        """
        result = super().to_dict()
        result.update(
            {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "metadata": self.metadata,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "rule_type": self.__class__.__name__,
            }
        )
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CustomPricingRule":
        """
        Create a custom pricing rule from a dictionary.

        Args:
            data: Dictionary with custom pricing rule data

        Returns:
            CustomPricingRule instance
        """
        instance = cls(
            metric=data["metric"],
            name=data.get("name", "Custom Pricing Rule"),
            description=data.get("description", "Custom pricing rule with specialized logic"),
            category=data.get("category"),
            resource_type=data.get("resource_type"),
            minimum_cost=data.get("minimum_cost", 0.0),
            maximum_cost=data.get("maximum_cost"),
            metadata=data.get("metadata", {}),
        )

        if "id" in data:
            instance.id = data["id"]

        if "created_at" in data:
            instance.created_at = datetime.fromisoformat(data["created_at"])

        if "updated_at" in data:
            instance.updated_at = datetime.fromisoformat(data["updated_at"])

        return instance

    def __str__(self) -> str:
        """String representation of the custom pricing rule."""
        return f"{self.__class__.__name__}({self.name}, {self.metric})"


class CustomPricingCalculator:
    """
    Calculator for custom pricing rules.

    This class provides methods for managing and applying custom pricing rules.
    """

    def __init__(
        self,
        billing_calculator: Optional[BillingCalculator] = None,
        custom_rules: Optional[List[CustomPricingRule]] = None,
    ):
        """
        Initialize a custom pricing calculator.

        Args:
            billing_calculator: Billing calculator to use
            custom_rules: List of custom pricing rules
        """
        self.billing_calculator = billing_calculator or BillingCalculator()
        self.custom_rules = custom_rules or []

    def add_custom_rule(self, rule: CustomPricingRule) -> None:
        """
        Add a custom pricing rule.

        Args:
            rule: Custom pricing rule to add
        """
        self.custom_rules.append(rule)
        self.billing_calculator.add_pricing_rule(rule)

    def remove_custom_rule(self, rule_id: str) -> bool:
        """
        Remove a custom pricing rule.

        Args:
            rule_id: ID of the custom pricing rule to remove

        Returns:
            True if the rule was removed, False otherwise
        """
        for i, rule in enumerate(self.custom_rules):
            if rule.id == rule_id:
                removed_rule = self.custom_rules.pop(i)

                # Also remove from billing calculator
                for j, bc_rule in enumerate(self.billing_calculator.pricing_rules):
                    if hasattr(bc_rule, "id") and bc_rule.id == rule_id:
                        self.billing_calculator.pricing_rules.pop(j)
                        break

                return True

        return False

    def get_custom_rule(self, rule_id: str) -> Optional[CustomPricingRule]:
        """
        Get a custom pricing rule by ID.

        Args:
            rule_id: ID of the custom pricing rule to get

        Returns:
            The custom pricing rule, or None if not found
        """
        for rule in self.custom_rules:
            if rule.id == rule_id:
                return rule

        return None

    def get_custom_rules_for_metric(
        self, metric: str, category: Optional[str] = None, resource_type: Optional[str] = None
    ) -> List[CustomPricingRule]:
        """
        Get custom pricing rules for a metric.

        Args:
            metric: Type of usage metric
            category: Category of usage
            resource_type: Type of resource

        Returns:
            List of custom pricing rules for the metric
        """
        matching_rules = []

        for rule in self.custom_rules:
            if rule.matches(metric, category, resource_type):
                matching_rules.append(rule)

        return matching_rules

    def calculate_cost(
        self,
        metric: str,
        quantity: float,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Calculate the cost for a quantity using custom pricing rules.

        Args:
            metric: Type of usage metric
            quantity: Quantity to calculate cost for
            category: Category of usage
            resource_type: Type of resource
            context: Additional context for the calculation

        Returns:
            Cost for the quantity
        """
        # Get matching rules
        matching_rules = self.get_custom_rules_for_metric(metric, category, resource_type)

        if not matching_rules:
            # No custom rules, use standard billing calculator
            return self.billing_calculator.calculate_cost(metric, quantity, category, resource_type)

        # Use the first matching custom rule
        # In a more complex implementation, we might want to combine rules or use a priority system
        rule = matching_rules[0]

        # Calculate cost using the custom rule
        cost = rule.calculate_custom_cost(quantity)

        # Apply minimum and maximum cost constraints
        if cost < rule.minimum_cost:
            cost = rule.minimum_cost

        if rule.maximum_cost is not None and cost > rule.maximum_cost:
            cost = rule.maximum_cost

        return cost

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the custom pricing calculator to a dictionary.

        Returns:
            Dictionary representation of the custom pricing calculator
        """
        return {"custom_rules": [rule.to_dict() for rule in self.custom_rules]}

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], billing_calculator: Optional[BillingCalculator] = None
    ) -> "CustomPricingCalculator":
        """
        Create a custom pricing calculator from a dictionary.

        Args:
            data: Dictionary with custom pricing calculator data
            billing_calculator: Billing calculator to use

        Returns:
            CustomPricingCalculator instance
        """
        instance = cls(billing_calculator=billing_calculator)

        if "custom_rules" in data:
            for rule_data in data["custom_rules"]:
                rule_type = rule_data.get("rule_type", "CustomPricingRule")

                # Import the rule class dynamically
                # This assumes all rule classes are defined in this module
                rule_class = globals().get(rule_type, CustomPricingRule)

                rule = rule_class.from_dict(rule_data)
                instance.add_custom_rule(rule)

        return instance


class TimeBasedPricingRule(CustomPricingRule):
    """
    Time-based pricing rule.

    This class implements a pricing rule that applies different rates
    based on the time of day, day of week, or other time-based factors.
    """

    def __init__(
        self,
        metric: str,
        time_rates: Dict[str, float],
        default_rate: float = 0.0,
        name: str = "Time-Based Pricing",
        description: str = "Pricing based on time of day or day of week",
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a time-based pricing rule.

        Args:
            metric: Type of usage metric
            time_rates: Dictionary mapping time patterns to rates
            default_rate: Default rate to use if no time pattern matches
            name: Name of the custom pricing rule
            description: Description of the custom pricing rule
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost
            metadata: Additional metadata for the custom pricing rule

        Time patterns can be specified in the following formats:
        - "weekday:1-5": Weekdays (Monday to Friday)
        - "weekend:6-7": Weekends (Saturday and Sunday)
        - "hour:9-17": Business hours (9 AM to 5 PM)
        - "hour:0-8,18-23": Non-business hours
        - "date:2023-12-25": Specific date
        - "month:12": Specific month (December)
        - "day:1": Specific day of month (1st)
        """
        super().__init__(
            metric=metric,
            name=name,
            description=description,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
            metadata=metadata,
        )

        self.time_rates = time_rates
        self.default_rate = default_rate

    def calculate_custom_cost(self, quantity: float, timestamp: Optional[datetime] = None) -> float:
        """
        Calculate the cost based on the time of usage.

        Args:
            quantity: Quantity to calculate cost for
            timestamp: Timestamp of the usage (defaults to now)

        Returns:
            Cost for the quantity
        """
        # Use current time if no timestamp is provided
        timestamp = timestamp or datetime.now()

        # Find the applicable rate
        rate = self.get_rate_for_time(timestamp)

        # Calculate cost
        return quantity * rate

    def get_rate_for_time(self, timestamp: datetime) -> float:
        """
        Get the rate applicable for a specific time.

        Args:
            timestamp: Timestamp to get rate for

        Returns:
            Applicable rate for the timestamp
        """
        # Check each time pattern
        for pattern, rate in self.time_rates.items():
            if self.matches_time_pattern(pattern, timestamp):
                return rate

        # Return default rate if no pattern matches
        return self.default_rate

    def matches_time_pattern(self, pattern: str, timestamp: datetime) -> bool:
        """
        Check if a timestamp matches a time pattern.

        Args:
            pattern: Time pattern to check
            timestamp: Timestamp to check

        Returns:
            True if the timestamp matches the pattern, False otherwise
        """
        # Split pattern into type and value
        if ":" not in pattern:
            return False

        pattern_type, pattern_value = pattern.split(":", 1)

        # Check weekday pattern (1=Monday, 7=Sunday)
        if pattern_type == "weekday":
            weekday = timestamp.isoweekday()
            return self.matches_range_pattern(pattern_value, weekday)

        # Check weekend pattern
        if pattern_type == "weekend":
            weekday = timestamp.isoweekday()
            is_weekend = weekday >= 6  # Saturday or Sunday
            return is_weekend

        # Check hour pattern (0-23)
        if pattern_type == "hour":
            hour = timestamp.hour
            return self.matches_range_pattern(pattern_value, hour)

        # Check date pattern (YYYY-MM-DD)
        if pattern_type == "date":
            date_str = timestamp.strftime("%Y-%m-%d")
            return date_str == pattern_value

        # Check month pattern (1-12)
        if pattern_type == "month":
            month = timestamp.month
            return self.matches_range_pattern(pattern_value, month)

        # Check day pattern (1-31)
        if pattern_type == "day":
            day = timestamp.day
            return self.matches_range_pattern(pattern_value, day)

        # Unknown pattern type
        return False

    def matches_range_pattern(self, pattern: str, value: int) -> bool:
        """
        Check if a value matches a range pattern.

        Args:
            pattern: Range pattern to check (e.g., "1-5", "1,3,5", "1-3,5-7")
            value: Value to check

        Returns:
            True if the value matches the pattern, False otherwise
        """
        # Split pattern into ranges
        ranges = pattern.split(",")

        for range_str in ranges:
            # Check if range has a min and max
            if "-" in range_str:
                range_min, range_max = map(int, range_str.split("-", 1))
                if range_min <= value <= range_max:
                    return True
            else:
                # Single value
                if value == int(range_str):
                    return True

        return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the time-based pricing rule to a dictionary.

        Returns:
            Dictionary representation of the time-based pricing rule
        """
        result = super().to_dict()
        result.update({"time_rates": self.time_rates, "default_rate": self.default_rate})
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeBasedPricingRule":
        """
        Create a time-based pricing rule from a dictionary.

        Args:
            data: Dictionary with time-based pricing rule data

        Returns:
            TimeBasedPricingRule instance
        """
        instance = cls(
            metric=data["metric"],
            time_rates=data.get("time_rates", {}),
            default_rate=data.get("default_rate", 0.0),
            name=data.get("name", "Time-Based Pricing"),
            description=data.get("description", "Pricing based on time of day or day of week"),
            category=data.get("category"),
            resource_type=data.get("resource_type"),
            minimum_cost=data.get("minimum_cost", 0.0),
            maximum_cost=data.get("maximum_cost"),
            metadata=data.get("metadata", {}),
        )

        if "id" in data:
            instance.id = data["id"]

        if "created_at" in data:
            instance.created_at = datetime.fromisoformat(data["created_at"])

        if "updated_at" in data:
            instance.updated_at = datetime.fromisoformat(data["updated_at"])

        return instance


class SeasonalPricingRule(CustomPricingRule):
    """
    Seasonal pricing rule.

    This class implements a pricing rule that applies different rates
    based on seasons, months, or other calendar-based factors.
    """

    def __init__(
        self,
        metric: str,
        seasonal_rates: Dict[str, float],
        default_rate: float = 0.0,
        name: str = "Seasonal Pricing",
        description: str = "Pricing based on seasons or months",
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a seasonal pricing rule.

        Args:
            metric: Type of usage metric
            seasonal_rates: Dictionary mapping season patterns to rates
            default_rate: Default rate to use if no season pattern matches
            name: Name of the custom pricing rule
            description: Description of the custom pricing rule
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost
            metadata: Additional metadata for the custom pricing rule

        Season patterns can be specified in the following formats:
        - "winter": Winter season (December, January, February)
        - "spring": Spring season (March, April, May)
        - "summer": Summer season (June, July, August)
        - "fall": Fall season (September, October, November)
        - "month:1": January
        - "month:6-8": Summer months (June, July, August)
        - "quarter:1": First quarter (January, February, March)
        - "holiday:christmas": Christmas holiday period
        - "holiday:thanksgiving": Thanksgiving holiday period
        """
        super().__init__(
            metric=metric,
            name=name,
            description=description,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
            metadata=metadata,
        )

        self.seasonal_rates = seasonal_rates
        self.default_rate = default_rate

        # Define seasons
        self.seasons = {
            "winter": [12, 1, 2],
            "spring": [3, 4, 5],
            "summer": [6, 7, 8],
            "fall": [9, 10, 11],
        }

        # Define quarters
        self.quarters = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}

        # Define holidays (month, day, duration in days)
        self.holidays = {
            "christmas": (12, 25, 7),
            "thanksgiving": (11, 26, 4),  # 4th Thursday of November (approximate)
            "newyear": (1, 1, 1),
            "independenceday": (7, 4, 1),
            "laborday": (9, 1, 3),  # 1st Monday of September (approximate)
            "memorialday": (5, 31, 3),  # Last Monday of May (approximate)
        }

    def calculate_custom_cost(self, quantity: float, timestamp: Optional[datetime] = None) -> float:
        """
        Calculate the cost based on the season.

        Args:
            quantity: Quantity to calculate cost for
            timestamp: Timestamp of the usage (defaults to now)

        Returns:
            Cost for the quantity
        """
        # Use current time if no timestamp is provided
        timestamp = timestamp or datetime.now()

        # Find the applicable rate
        rate = self.get_rate_for_season(timestamp)

        # Calculate cost
        return quantity * rate

    def get_rate_for_season(self, timestamp: datetime) -> float:
        """
        Get the rate applicable for a specific season.

        Args:
            timestamp: Timestamp to get rate for

        Returns:
            Applicable rate for the timestamp
        """
        # Check each season pattern
        for pattern, rate in self.seasonal_rates.items():
            if self.matches_season_pattern(pattern, timestamp):
                return rate

        # Return default rate if no pattern matches
        return self.default_rate

    def matches_season_pattern(self, pattern: str, timestamp: datetime) -> bool:
        """
        Check if a timestamp matches a season pattern.

        Args:
            pattern: Season pattern to check
            timestamp: Timestamp to check

        Returns:
            True if the timestamp matches the pattern, False otherwise
        """
        # Check season names
        if pattern in self.seasons:
            month = timestamp.month
            return month in self.seasons[pattern]

        # Check month pattern
        if pattern.startswith("month:"):
            month = timestamp.month
            month_pattern = pattern[6:]
            return self.matches_range_pattern(month_pattern, month)

        # Check quarter pattern
        if pattern.startswith("quarter:"):
            month = timestamp.month
            quarter = int(pattern[8:])
            return month in self.quarters.get(quarter, [])

        # Check holiday pattern
        if pattern.startswith("holiday:"):
            holiday = pattern[8:]
            if holiday in self.holidays:
                holiday_month, holiday_day, holiday_duration = self.holidays[holiday]

                # Create holiday start date for the current year
                holiday_start = datetime(timestamp.year, holiday_month, holiday_day)

                # Create holiday end date
                holiday_end = holiday_start + timedelta(days=holiday_duration)

                # Check if timestamp is within the holiday period
                return holiday_start <= timestamp <= holiday_end

        # Unknown pattern
        return False

    def matches_range_pattern(self, pattern: str, value: int) -> bool:
        """
        Check if a value matches a range pattern.

        Args:
            pattern: Range pattern to check (e.g., "1-5", "1,3,5", "1-3,5-7")
            value: Value to check

        Returns:
            True if the value matches the pattern, False otherwise
        """
        # Split pattern into ranges
        ranges = pattern.split(",")

        for range_str in ranges:
            # Check if range has a min and max
            if "-" in range_str:
                range_min, range_max = map(int, range_str.split("-", 1))
                if range_min <= value <= range_max:
                    return True
            else:
                # Single value
                if value == int(range_str):
                    return True

        return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the seasonal pricing rule to a dictionary.

        Returns:
            Dictionary representation of the seasonal pricing rule
        """
        result = super().to_dict()
        result.update({"seasonal_rates": self.seasonal_rates, "default_rate": self.default_rate})
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SeasonalPricingRule":
        """
        Create a seasonal pricing rule from a dictionary.

        Args:
            data: Dictionary with seasonal pricing rule data

        Returns:
            SeasonalPricingRule instance
        """
        instance = cls(
            metric=data["metric"],
            seasonal_rates=data.get("seasonal_rates", {}),
            default_rate=data.get("default_rate", 0.0),
            name=data.get("name", "Seasonal Pricing"),
            description=data.get("description", "Pricing based on seasons or months"),
            category=data.get("category"),
            resource_type=data.get("resource_type"),
            minimum_cost=data.get("minimum_cost", 0.0),
            maximum_cost=data.get("maximum_cost"),
            metadata=data.get("metadata", {}),
        )

        if "id" in data:
            instance.id = data["id"]

        if "created_at" in data:
            instance.created_at = datetime.fromisoformat(data["created_at"])

        if "updated_at" in data:
            instance.updated_at = datetime.fromisoformat(data["updated_at"])

        return instance


class CustomerSegmentPricingRule(CustomPricingRule):
    """
    Customer segment pricing rule.

    This class implements a pricing rule that applies different rates
    based on customer segments or attributes.
    """

    def __init__(
        self,
        metric: str,
        segment_rates: Dict[str, float],
        default_rate: float = 0.0,
        name: str = "Customer Segment Pricing",
        description: str = "Pricing based on customer segments",
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a customer segment pricing rule.

        Args:
            metric: Type of usage metric
            segment_rates: Dictionary mapping segment patterns to rates
            default_rate: Default rate to use if no segment pattern matches
            name: Name of the custom pricing rule
            description: Description of the custom pricing rule
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost
            metadata: Additional metadata for the custom pricing rule

        Segment patterns can be specified in the following formats:
        - "tier:free": Free tier customers
        - "tier:premium": Premium tier customers
        - "tier:enterprise": Enterprise tier customers
        - "industry:healthcare": Healthcare industry customers
        - "industry:finance": Finance industry customers
        - "size:small": Small businesses (e.g., 1-50 employees)
        - "size:medium": Medium businesses (e.g., 51-500 employees)
        - "size:large": Large businesses (e.g., 501+ employees)
        - "region:us": Customers in the United States
        - "region:eu": Customers in the European Union
        - "age:0-30": New customers (0-30 days)
        - "age:31-90": Recent customers (31-90 days)
        - "age:91+": Established customers (91+ days)
        - "usage:low": Low usage customers
        - "usage:medium": Medium usage customers
        - "usage:high": High usage customers
        """
        super().__init__(
            metric=metric,
            name=name,
            description=description,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
            metadata=metadata,
        )

        self.segment_rates = segment_rates
        self.default_rate = default_rate

    def calculate_custom_cost(
        self,
        quantity: float,
        customer_id: Optional[str] = None,
        customer_data: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Calculate the cost based on the customer segment.

        Args:
            quantity: Quantity to calculate cost for
            customer_id: ID of the customer
            customer_data: Additional customer data

        Returns:
            Cost for the quantity
        """
        # If no customer data is provided, use default rate
        if not customer_data:
            return quantity * self.default_rate

        # Find the applicable rate
        rate = self.get_rate_for_segment(customer_data)

        # Calculate cost
        return quantity * rate

    def get_rate_for_segment(self, customer_data: Dict[str, Any]) -> float:
        """
        Get the rate applicable for a specific customer segment.

        Args:
            customer_data: Customer data to determine segment

        Returns:
            Applicable rate for the customer segment
        """
        # Check each segment pattern
        for pattern, rate in self.segment_rates.items():
            if self.matches_segment_pattern(pattern, customer_data):
                return rate

        # Return default rate if no pattern matches
        return self.default_rate

    def matches_segment_pattern(self, pattern: str, customer_data: Dict[str, Any]) -> bool:
        """
        Check if customer data matches a segment pattern.

        Args:
            pattern: Segment pattern to check
            customer_data: Customer data to check

        Returns:
            True if the customer data matches the pattern, False otherwise
        """
        # Split pattern into type and value
        if ":" not in pattern:
            return False

        pattern_type, pattern_value = pattern.split(":", 1)

        # Check tier pattern
        if pattern_type == "tier":
            customer_tier = customer_data.get("tier", "").lower()
            return customer_tier == pattern_value.lower()

        # Check industry pattern
        if pattern_type == "industry":
            customer_industry = customer_data.get("industry", "").lower()
            return customer_industry == pattern_value.lower()

        # Check size pattern
        if pattern_type == "size":
            customer_size = customer_data.get("size", "").lower()
            return customer_size == pattern_value.lower()

        # Check region pattern
        if pattern_type == "region":
            customer_region = customer_data.get("region", "").lower()
            return customer_region == pattern_value.lower()

        # Check age pattern (days since customer creation)
        if pattern_type == "age":
            if "created_at" not in customer_data:
                return False

            try:
                created_at = datetime.fromisoformat(customer_data["created_at"])
                days_since_creation = (datetime.now() - created_at).days

                return self.matches_range_pattern(pattern_value, days_since_creation)
            except (ValueError, TypeError):
                return False

        # Check usage pattern
        if pattern_type == "usage":
            customer_usage = customer_data.get("usage_level", "").lower()
            return customer_usage == pattern_value.lower()

        # Unknown pattern type
        return False

    def matches_range_pattern(self, pattern: str, value: int) -> bool:
        """
        Check if a value matches a range pattern.

        Args:
            pattern: Range pattern to check (e.g., "1-5", "1,3,5", "1-3,5-7", "91+")
            value: Value to check

        Returns:
            True if the value matches the pattern, False otherwise
        """
        # Check for "X+" pattern (X or greater)
        if pattern.endswith("+"):
            try:
                min_value = int(pattern[:-1])
                return value >= min_value
            except ValueError:
                return False

        # Split pattern into ranges
        ranges = pattern.split(",")

        for range_str in ranges:
            # Check if range has a min and max
            if "-" in range_str:
                range_min, range_max = map(int, range_str.split("-", 1))
                if range_min <= value <= range_max:
                    return True
            else:
                # Single value
                try:
                    if value == int(range_str):
                        return True
                except ValueError:
                    continue

        return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the customer segment pricing rule to a dictionary.

        Returns:
            Dictionary representation of the customer segment pricing rule
        """
        result = super().to_dict()
        result.update({"segment_rates": self.segment_rates, "default_rate": self.default_rate})
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CustomerSegmentPricingRule":
        """
        Create a customer segment pricing rule from a dictionary.

        Args:
            data: Dictionary with customer segment pricing rule data

        Returns:
            CustomerSegmentPricingRule instance
        """
        instance = cls(
            metric=data["metric"],
            segment_rates=data.get("segment_rates", {}),
            default_rate=data.get("default_rate", 0.0),
            name=data.get("name", "Customer Segment Pricing"),
            description=data.get("description", "Pricing based on customer segments"),
            category=data.get("category"),
            resource_type=data.get("resource_type"),
            minimum_cost=data.get("minimum_cost", 0.0),
            maximum_cost=data.get("maximum_cost"),
            metadata=data.get("metadata", {}),
        )

        if "id" in data:
            instance.id = data["id"]

        if "created_at" in data:
            instance.created_at = datetime.fromisoformat(data["created_at"])

        if "updated_at" in data:
            instance.updated_at = datetime.fromisoformat(data["updated_at"])

        return instance


class ConditionalPricingRule(CustomPricingRule):
    """
    Conditional pricing rule.

    This class implements a pricing rule that applies different rates
    based on complex conditions involving multiple factors.
    """

    def __init__(
        self,
        metric: str,
        conditions: List[Dict[str, Any]],
        default_rate: float = 0.0,
        name: str = "Conditional Pricing",
        description: str = "Pricing based on complex conditions",
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a conditional pricing rule.

        Args:
            metric: Type of usage metric
            conditions: List of condition dictionaries
            default_rate: Default rate to use if no condition matches
            name: Name of the custom pricing rule
            description: Description of the custom pricing rule
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost
            metadata: Additional metadata for the custom pricing rule

        Each condition dictionary should have the following structure:
        {
            "condition": "expression",  # Condition expression
            "rate": 0.01  # Rate to apply if condition is met
        }

        Condition expressions can use the following variables:
        - quantity: The quantity being priced
        - customer.X: Customer attribute X (e.g., customer.tier)
        - time.X: Time attribute X (e.g., time.hour, time.weekday)
        - usage.X: Usage attribute X (e.g., usage.total, usage.average)

        Condition expressions can use the following operators:
        - Comparison: ==, !=, <, >, <=, >=
        - Logical: and, or, not
        - Arithmetic: +, -, *, /, %
        - Membership: in, not in

        Examples:
        - "quantity > 1000"
        - "customer.tier == 'premium'"
        - "time.weekday in [1, 2, 3, 4, 5]"
        - "usage.total > 10000 and customer.age > 90"
        """
        super().__init__(
            metric=metric,
            name=name,
            description=description,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
            metadata=metadata,
        )

        self.conditions = conditions
        self.default_rate = default_rate

    def calculate_custom_cost(
        self, quantity: float, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate the cost based on conditions.

        Args:
            quantity: Quantity to calculate cost for
            context: Additional context for condition evaluation

        Returns:
            Cost for the quantity
        """
        # If no context is provided, use default rate
        if not context:
            return quantity * self.default_rate

        # Find the applicable rate
        rate = self.get_rate_for_conditions(quantity, context)

        # Calculate cost
        return quantity * rate

    def get_rate_for_conditions(self, quantity: float, context: Dict[str, Any]) -> float:
        """
        Get the rate applicable based on conditions.

        Args:
            quantity: Quantity being priced
            context: Context for condition evaluation

        Returns:
            Applicable rate based on conditions
        """
        # Prepare evaluation context
        eval_context = self.prepare_eval_context(quantity, context)

        # Check each condition
        for condition_data in self.conditions:
            condition_expr = condition_data.get("condition", "False")
            rate = condition_data.get("rate", self.default_rate)

            try:
                # Evaluate the condition
                if self.evaluate_condition(condition_expr, eval_context):
                    return rate
            except Exception as e:
                # Log the error and continue to the next condition
                print(f"Error evaluating condition '{condition_expr}': {e}")
                continue

        # Return default rate if no condition matches
        return self.default_rate

    def prepare_eval_context(self, quantity: float, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare the evaluation context for condition expressions.

        Args:
            quantity: Quantity being priced
            context: Original context

        Returns:
            Prepared evaluation context
        """
        # Start with a clean context
        eval_context = {"quantity": quantity, "customer": {}, "time": {}, "usage": {}}

        # Add customer data
        if "customer" in context:
            eval_context["customer"] = context["customer"]

        # Add time data
        if "time" in context:
            eval_context["time"] = context["time"]
        else:
            # Add default time data
            now = datetime.now()
            eval_context["time"] = {
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second,
                "day": now.day,
                "month": now.month,
                "year": now.year,
                "weekday": now.isoweekday(),
                "is_weekend": now.isoweekday() >= 6,
            }

        # Add usage data
        if "usage" in context:
            eval_context["usage"] = context["usage"]

        return eval_context

    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition expression.

        Args:
            condition: Condition expression to evaluate
            context: Evaluation context

        Returns:
            True if the condition is met, False otherwise
        """
        # Replace variable references with dictionary lookups
        # For example, replace "customer.tier" with "context['customer']['tier']"
        pattern = r"(customer|time|usage)\.([a-zA-Z_][a-zA-Z0-9_]*)"

        def replace_var(match):
            category, attr = match.groups()
            return f"context['{category}'].get('{attr}')"

        expr = re.sub(pattern, replace_var, condition)

        # Add safety checks
        if "import" in expr or "exec" in expr or "__" in expr:
            raise ValueError(f"Unsafe expression: {expr}")

        # Evaluate the expression
        try:
            result = eval(expr, {"__builtins__": {}}, {"context": context})
            return bool(result)
        except Exception as e:
            raise ValueError(f"Error evaluating expression '{expr}': {e}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the conditional pricing rule to a dictionary.

        Returns:
            Dictionary representation of the conditional pricing rule
        """
        result = super().to_dict()
        result.update({"conditions": self.conditions, "default_rate": self.default_rate})
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConditionalPricingRule":
        """
        Create a conditional pricing rule from a dictionary.

        Args:
            data: Dictionary with conditional pricing rule data

        Returns:
            ConditionalPricingRule instance
        """
        instance = cls(
            metric=data["metric"],
            conditions=data.get("conditions", []),
            default_rate=data.get("default_rate", 0.0),
            name=data.get("name", "Conditional Pricing"),
            description=data.get("description", "Pricing based on complex conditions"),
            category=data.get("category"),
            resource_type=data.get("resource_type"),
            minimum_cost=data.get("minimum_cost", 0.0),
            maximum_cost=data.get("maximum_cost"),
            metadata=data.get("metadata", {}),
        )

        if "id" in data:
            instance.id = data["id"]

        if "created_at" in data:
            instance.created_at = datetime.fromisoformat(data["created_at"])

        if "updated_at" in data:
            instance.updated_at = datetime.fromisoformat(data["updated_at"])

        return instance


class FormulaBasedPricingRule(CustomPricingRule):
    """
    Formula-based pricing rule.

    This class implements a pricing rule that calculates costs using
    mathematical formulas or expressions.
    """

    def __init__(
        self,
        metric: str,
        formula: str,
        variables: Optional[Dict[str, Any]] = None,
        name: str = "Formula-Based Pricing",
        description: str = "Pricing based on mathematical formulas",
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a formula-based pricing rule.

        Args:
            metric: Type of usage metric
            formula: Formula expression for calculating cost
            variables: Dictionary of variables to use in the formula
            name: Name of the custom pricing rule
            description: Description of the custom pricing rule
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost
            maximum_cost: Maximum cost
            metadata: Additional metadata for the custom pricing rule

        Formula expressions can use the following variables:
        - q: The quantity being priced
        - Any variables defined in the variables dictionary

        Formula expressions can use the following operators and functions:
        - Arithmetic: +, -, *, /, %, **
        - Math functions: abs, min, max, round, floor, ceil, sqrt, log, log10, exp
        - Trigonometric functions: sin, cos, tan

        Examples:
        - "q * 0.01": Simple per-unit pricing
        - "10 + q * 0.005": Base fee plus per-unit pricing
        - "q * (1 - discount)": Discounted pricing
        - "base_price * (1 - volume_discount * (q / 1000))": Volume discount pricing
        - "min(q * 0.01, 100)": Capped pricing
        - "max(10, q * 0.005)": Minimum pricing
        - "q * rate * (1 - seasonal_discount)": Seasonal discount pricing
        """
        super().__init__(
            metric=metric,
            name=name,
            description=description,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
            metadata=metadata,
        )

        self.formula = formula
        self.variables = variables or {}

        # Validate the formula
        self.validate_formula()

    def validate_formula(self) -> None:
        """
        Validate the formula expression.

        Raises:
            ValueError: If the formula is invalid
        """
        try:
            # Test with a simple quantity
            self.evaluate_formula(10.0, self.variables)
        except Exception as e:
            raise ValueError(f"Invalid formula '{self.formula}': {e}")

    def calculate_custom_cost(
        self, quantity: float, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate the cost using the formula.

        Args:
            quantity: Quantity to calculate cost for
            context: Additional context for formula evaluation

        Returns:
            Cost for the quantity
        """
        # Prepare variables
        variables = self.prepare_variables(quantity, context)

        # Evaluate the formula
        return self.evaluate_formula(quantity, variables)

    def prepare_variables(
        self, quantity: float, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepare variables for formula evaluation.

        Args:
            quantity: Quantity being priced
            context: Additional context

        Returns:
            Dictionary of variables for formula evaluation
        """
        # Start with the base variables
        variables = dict(self.variables)

        # Add quantity variable
        variables["q"] = quantity

        # Add context variables if provided
        if context:
            # Add customer variables
            if "customer" in context:
                for key, value in context["customer"].items():
                    variables[f"customer_{key}"] = value

            # Add time variables
            if "time" in context:
                for key, value in context["time"].items():
                    variables[f"time_{key}"] = value

            # Add usage variables
            if "usage" in context:
                for key, value in context["usage"].items():
                    variables[f"usage_{key}"] = value

        return variables

    def evaluate_formula(self, quantity: float, variables: Dict[str, Any]) -> float:
        """
        Evaluate the formula expression.

        Args:
            quantity: Quantity being priced
            variables: Variables for formula evaluation

        Returns:
            Result of the formula evaluation
        """
        # Create a safe math environment
        safe_math = {
            # Basic math functions
            "abs": abs,
            "min": min,
            "max": max,
            "round": round,
            "floor": math.floor,
            "ceil": math.ceil,
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            # Trigonometric functions
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            # Constants
            "pi": math.pi,
            "e": math.e,
        }

        # Add variables to the environment
        safe_math.update(variables)

        # Add safety checks
        if "import" in self.formula or "exec" in self.formula or "__" in self.formula:
            raise ValueError(f"Unsafe formula: {self.formula}")

        # Evaluate the formula
        try:
            result = eval(self.formula, {"__builtins__": {}}, safe_math)
            return float(result)
        except Exception as e:
            raise ValueError(f"Error evaluating formula '{self.formula}': {e}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the formula-based pricing rule to a dictionary.

        Returns:
            Dictionary representation of the formula-based pricing rule
        """
        result = super().to_dict()
        result.update({"formula": self.formula, "variables": self.variables})
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FormulaBasedPricingRule":
        """
        Create a formula-based pricing rule from a dictionary.

        Args:
            data: Dictionary with formula-based pricing rule data

        Returns:
            FormulaBasedPricingRule instance
        """
        instance = cls(
            metric=data["metric"],
            formula=data.get("formula", "q * 0.01"),
            variables=data.get("variables", {}),
            name=data.get("name", "Formula-Based Pricing"),
            description=data.get("description", "Pricing based on mathematical formulas"),
            category=data.get("category"),
            resource_type=data.get("resource_type"),
            minimum_cost=data.get("minimum_cost", 0.0),
            maximum_cost=data.get("maximum_cost"),
            metadata=data.get("metadata", {}),
        )

        if "id" in data:
            instance.id = data["id"]

        if "created_at" in data:
            instance.created_at = datetime.fromisoformat(data["created_at"])

        if "updated_at" in data:
            instance.updated_at = datetime.fromisoformat(data["updated_at"])

        return instance


# Example usage
if __name__ == "__main__":
    # Create a time-based pricing rule
    time_rule = TimeBasedPricingRule(
        metric=UsageMetric.API_CALL,
        time_rates={
            "weekday:1-5": 0.01,  # $0.01 per API call on weekdays
            "weekend:6-7": 0.005,  # $0.005 per API call on weekends
            "hour:9-17": 0.015,  # $0.015 per API call during business hours
            "hour:0-8,18-23": 0.008,  # $0.008 per API call during non-business hours
        },
        default_rate=0.01,
        category=UsageCategory.INFERENCE,
    )

    # Create a seasonal pricing rule
    seasonal_rule = SeasonalPricingRule(
        metric=UsageMetric.STORAGE,
        seasonal_rates={
            "winter": 0.05,  # $0.05 per GB in winter
            "summer": 0.03,  # $0.03 per GB in summer
            "holiday:christmas": 0.02,  # $0.02 per GB during Christmas
        },
        default_rate=0.04,
        category=UsageCategory.STORAGE,
    )

    # Create a customer segment pricing rule
    segment_rule = CustomerSegmentPricingRule(
        metric=UsageMetric.TOKEN,
        segment_rates={
            "tier:free": 0.002,  # $0.002 per token for free tier
            "tier:premium": 0.0015,  # $0.0015 per token for premium tier
            "tier:enterprise": 0.001,  # $0.001 per token for enterprise tier
            "industry:education": 0.0012,  # $0.0012 per token for education industry
            "age:0-30": 0.0018,  # $0.0018 per token for new customers
        },
        default_rate=0.002,
        category=UsageCategory.INFERENCE,
    )

    # Create a conditional pricing rule
    conditional_rule = ConditionalPricingRule(
        metric=UsageMetric.COMPUTE_TIME,
        conditions=[
            {
                "condition": "quantity > 100 and customer.tier == 'premium'",
                "rate": 0.08,  # $0.08 per hour for premium customers with high usage
            },
            {
                "condition": "time.is_weekend and usage.total > 1000",
                "rate": 0.06,  # $0.06 per hour on weekends with high total usage
            },
            {
                "condition": "customer.industry == 'research' and time.hour >= 22",
                "rate": 0.05,  # $0.05 per hour for research customers during late hours
            },
        ],
        default_rate=0.1,  # $0.1 per hour by default
        category=UsageCategory.COMPUTE,
    )

    # Create a formula-based pricing rule
    formula_rule = FormulaBasedPricingRule(
        metric=UsageMetric.BANDWIDTH,
        formula="base_fee + q * rate * (1 - volume_discount * min(1, q / discount_threshold))",
        variables={
            "base_fee": 5.0,  # $5.00 base fee
            "rate": 0.1,  # $0.10 per GB
            "volume_discount": 0.2,  # 20% maximum volume discount
            "discount_threshold": 100.0,  # Discount threshold at 100 GB
        },
        category=UsageCategory.NETWORK,
    )

    # Create a custom pricing calculator
    calculator = CustomPricingCalculator()

    # Add the custom rules
    calculator.add_custom_rule(time_rule)
    calculator.add_custom_rule(seasonal_rule)
    calculator.add_custom_rule(segment_rule)
    calculator.add_custom_rule(conditional_rule)
    calculator.add_custom_rule(formula_rule)

    # Calculate cost for API calls
    api_cost = calculator.calculate_cost(
        metric=UsageMetric.API_CALL, quantity=100, category=UsageCategory.INFERENCE
    )

    # Calculate cost for storage
    storage_cost = calculator.calculate_cost(
        metric=UsageMetric.STORAGE, quantity=10, category=UsageCategory.STORAGE
    )

    # Calculate cost for tokens with customer data
    token_cost = calculator.calculate_cost(
        metric=UsageMetric.TOKEN,
        quantity=1000,
        category=UsageCategory.INFERENCE,
        context={
            "customer": {
                "tier": "premium",
                "industry": "education",
                "created_at": "2023-01-01T00:00:00",
            }
        },
    )

    # Calculate cost for compute time with complex context
    compute_cost = calculator.calculate_cost(
        metric=UsageMetric.COMPUTE_TIME,
        quantity=10,
        category=UsageCategory.COMPUTE,
        context={
            "customer": {"tier": "premium", "industry": "research"},
            "time": {"hour": 23, "is_weekend": True},
            "usage": {"total": 1500},
        },
    )

    # Calculate cost for bandwidth with formula
    bandwidth_cost = calculator.calculate_cost(
        metric=UsageMetric.BANDWIDTH, quantity=50, category=UsageCategory.NETWORK
    )

    print(f"API call cost: ${api_cost:.2f}")
    print(f"Storage cost: ${storage_cost:.2f}")
    print(f"Token cost: ${token_cost:.2f}")
    print(f"Compute time cost: ${compute_cost:.2f}")
    print(f"Bandwidth cost: ${bandwidth_cost:.2f}")
