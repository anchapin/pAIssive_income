"""
Usage tracking for the pAIssive Income project.

This module provides classes for tracking usage of API calls and resources,
including usage limits, quota management, and analytics.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class UsageMetric:
    """Enumeration of usage metric types."""

    API_CALL = "api_call"
    COMPUTE_TIME = "compute_time"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    TOKEN = "token"
    CREDIT = "credit"
    CUSTOM = "custom"


class UsageCategory:
    """Enumeration of usage categories."""

    INFERENCE = "inference"
    TRAINING = "training"
    FINE_TUNING = "fine_tuning"
    EMBEDDING = "embedding"
    STORAGE = "storage"
    DATA_TRANSFER = "data_transfer"
    CUSTOM = "custom"


class UsageRecordSchema(BaseModel):
    id: str = Field(..., description="Unique identifier for the usage record")
    customer_id: str = Field(..., description="ID of the customer")
    metric: str = Field(..., description="Type of usage metric (e.g., API_CALL, COMPUTE_TIME)")
    quantity: float = Field(..., description="Quantity of usage")
    category: str = Field(..., description="Category of usage (e.g., INFERENCE, TRAINING)")
    timestamp: datetime = Field(..., description="Timestamp of the usage")
    resource_id: Optional[str] = Field(None, description="ID of the resource being used")
    resource_type: Optional[str] = Field(None, description="Type of resource being used")
    subscription_id: Optional[str] = Field(None, description="ID of the subscription")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for the usage record"
    )
    created_at: datetime = Field(..., description="Creation timestamp")


class UsageRecord:
    """
    Class representing a usage record.

    This class provides a structured way to represent usage of API calls and resources,
    including the quantity, timestamp, and associated metadata.
    """

    def __init__(
        self,
        customer_id: str,
        metric: str,
        quantity: float,
        category: str = UsageCategory.INFERENCE,
        timestamp: Optional[datetime] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        subscription_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a usage record.

        Args:
            customer_id: ID of the customer
            metric: Type of usage metric (e.g., API_CALL, COMPUTE_TIME)
            quantity: Quantity of usage
            category: Category of usage (e.g., INFERENCE, TRAINING)
            timestamp: Timestamp of the usage
            resource_id: ID of the resource being used
            resource_type: Type of resource being used
            subscription_id: ID of the subscription
            metadata: Additional metadata for the usage record
        """
        self.id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.metric = metric
        self.quantity = quantity
        self.category = category
        self.timestamp = timestamp or datetime.now()
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.subscription_id = subscription_id
        self.metadata = metadata or {}
        self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the usage record to a dictionary.

        Returns:
            Dictionary representation of the usage record
        """
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "metric": self.metric,
            "quantity": self.quantity,
            "category": self.category,
            "timestamp": self.timestamp.isoformat(),
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "subscription_id": self.subscription_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the usage record to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the usage record
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageRecord":
        """
        Create a usage record from a dictionary.

        Args:
            data: Dictionary with usage record data

        Returns:
            UsageRecord instance
        """
        record = cls(
            customer_id=data["customer_id"],
            metric=data["metric"],
            quantity=data["quantity"],
            category=data["category"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            resource_id=data.get("resource_id"),
            resource_type=data.get("resource_type"),
            subscription_id=data.get("subscription_id"),
            metadata=data.get("metadata", {}),
        )

        record.id = data["id"]
        record.created_at = datetime.fromisoformat(data["created_at"])

        return record

    def __str__(self) -> str:
        """String representation of the usage record."""
        return f"UsageRecord({self.id}, {self.customer_id}, {self.metric}, {self.quantity}, {self.timestamp.isoformat()})"


class UsageLimit:
    """
    Class representing a usage limit.

    This class provides a structured way to represent limits on usage of API calls
    and resources, including the maximum quantity, time period, and associated metadata.
    """

    # Time period types
    PERIOD_HOURLY = "hourly"
    PERIOD_DAILY = "daily"
    PERIOD_WEEKLY = "weekly"
    PERIOD_MONTHLY = "monthly"
    PERIOD_QUARTERLY = "quarterly"
    PERIOD_YEARLY = "yearly"

    def __init__(
        self,
        customer_id: str,
        metric: str,
        max_quantity: float,
        period: str = PERIOD_MONTHLY,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        subscription_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a usage limit.

        Args:
            customer_id: ID of the customer
            metric: Type of usage metric (e.g., API_CALL, COMPUTE_TIME)
            max_quantity: Maximum quantity allowed
            period: Time period for the limit (e.g., DAILY, MONTHLY)
            category: Category of usage (e.g., INFERENCE, TRAINING)
            resource_type: Type of resource being limited
            subscription_id: ID of the subscription
            metadata: Additional metadata for the usage limit
        """
        self.id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.metric = metric
        self.max_quantity = max_quantity
        self.period = period
        self.category = category
        self.resource_type = resource_type
        self.subscription_id = subscription_id
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def get_period_start(self, reference_time: Optional[datetime] = None) -> datetime:
        """
        Get the start of the current period.

        Args:
            reference_time: Reference time (defaults to now)

        Returns:
            Start of the current period
        """
        if reference_time is None:
            reference_time = datetime.now()

        if self.period == self.PERIOD_HOURLY:
            return datetime(
                reference_time.year,
                reference_time.month,
                reference_time.day,
                reference_time.hour,
            )
        elif self.period == self.PERIOD_DAILY:
            return datetime(reference_time.year, reference_time.month, reference_time.day)
        elif self.period == self.PERIOD_WEEKLY:
            # Start of the week (Monday)
            days_since_monday = reference_time.weekday()
            return datetime(
                reference_time.year, reference_time.month, reference_time.day
            ) - timedelta(days=days_since_monday)
        elif self.period == self.PERIOD_MONTHLY:
            return datetime(reference_time.year, reference_time.month, 1)
        elif self.period == self.PERIOD_QUARTERLY:
            # Start of the quarter
            quarter = (reference_time.month - 1) // 3
            return datetime(reference_time.year, quarter * 3 + 1, 1)
        elif self.period == self.PERIOD_YEARLY:
            return datetime(reference_time.year, 1, 1)
        else:
            raise ValueError(f"Invalid period: {self.period}")

    def get_period_end(self, reference_time: Optional[datetime] = None) -> datetime:
        """
        Get the end of the current period.

        Args:
            reference_time: Reference time (defaults to now)

        Returns:
            End of the current period
        """
        if reference_time is None:
            reference_time = datetime.now()

        if self.period == self.PERIOD_HOURLY:
            return (
                self.get_period_start(reference_time)
                + timedelta(hours=1)
                - timedelta(microseconds=1)
            )
        elif self.period == self.PERIOD_DAILY:
            return (
                self.get_period_start(reference_time)
                + timedelta(days=1)
                - timedelta(microseconds=1)
            )
        elif self.period == self.PERIOD_WEEKLY:
            return (
                self.get_period_start(reference_time)
                + timedelta(days=7)
                - timedelta(microseconds=1)
            )
        elif self.period == self.PERIOD_MONTHLY:
            # Last day of the month
            start = self.get_period_start(reference_time)
            if start.month == 12:
                next_month = datetime(start.year + 1, 1, 1)
            else:
                next_month = datetime(start.year, start.month + 1, 1)
            return next_month - timedelta(microseconds=1)
        elif self.period == self.PERIOD_QUARTERLY:
            # Last day of the quarter
            start = self.get_period_start(reference_time)
            if start.month >= 10:
                next_quarter = datetime(start.year + 1, 1, 1)
            else:
                next_quarter = datetime(start.year, start.month + 3, 1)
            return next_quarter - timedelta(microseconds=1)
        elif self.period == self.PERIOD_YEARLY:
            # Last day of the year
            start = self.get_period_start(reference_time)
            return datetime(start.year + 1, 1, 1) - timedelta(microseconds=1)
        else:
            raise ValueError(f"Invalid period: {self.period}")

    def is_within_period(
        self, timestamp: datetime, reference_time: Optional[datetime] = None
    ) -> bool:
        """
        Check if a timestamp is within the current period.

        Args:
            timestamp: Timestamp to check
            reference_time: Reference time (defaults to now)

        Returns:
            True if the timestamp is within the current period, False otherwise
        """
        if reference_time is None:
            reference_time = datetime.now()

        period_start = self.get_period_start(reference_time)
        period_end = self.get_period_end(reference_time)

        return period_start <= timestamp <= period_end

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the usage limit to a dictionary.

        Returns:
            Dictionary representation of the usage limit
        """
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "metric": self.metric,
            "max_quantity": self.max_quantity,
            "period": self.period,
            "category": self.category,
            "resource_type": self.resource_type,
            "subscription_id": self.subscription_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the usage limit to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the usage limit
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageLimit":
        """
        Create a usage limit from a dictionary.

        Args:
            data: Dictionary with usage limit data

        Returns:
            UsageLimit instance
        """
        limit = cls(
            customer_id=data["customer_id"],
            metric=data["metric"],
            max_quantity=data["max_quantity"],
            period=data["period"],
            category=data.get("category"),
            resource_type=data.get("resource_type"),
            subscription_id=data.get("subscription_id"),
            metadata=data.get("metadata", {}),
        )

        limit.id = data["id"]
        limit.created_at = datetime.fromisoformat(data["created_at"])
        limit.updated_at = datetime.fromisoformat(data["updated_at"])

        return limit

    def __str__(self) -> str:
        """String representation of the usage limit."""
        return f"UsageLimit({self.id}, {self.customer_id}, {self.metric}, {self.max_quantity}, {self.period})"


class UsageQuota:
    """
    Class representing a usage quota.

    This class provides a structured way to represent quotas for usage of API calls
    and resources, including the allocated quantity, time period, and associated metadata.
    """

    def __init__(
        self,
        customer_id: str,
        metric: str,
        allocated_quantity: float,
        used_quantity: float = 0.0,
        period: str = UsageLimit.PERIOD_MONTHLY,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        subscription_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a usage quota.

        Args:
            customer_id: ID of the customer
            metric: Type of usage metric (e.g., API_CALL, COMPUTE_TIME)
            allocated_quantity: Allocated quantity
            used_quantity: Used quantity
            period: Time period for the quota (e.g., DAILY, MONTHLY)
            category: Category of usage (e.g., INFERENCE, TRAINING)
            resource_type: Type of resource
            subscription_id: ID of the subscription
            metadata: Additional metadata for the usage quota
        """
        self.id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.metric = metric
        self.allocated_quantity = allocated_quantity
        self.used_quantity = used_quantity
        self.period = period
        self.category = category
        self.resource_type = resource_type
        self.subscription_id = subscription_id
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.reset_at = self._calculate_reset_time()

    def _calculate_reset_time(self) -> datetime:
        """
        Calculate the next reset time for the quota.

        Returns:
            Next reset time
        """
        now = datetime.now()

        if self.period == UsageLimit.PERIOD_HOURLY:
            # Start of the next hour
            return datetime(now.year, now.month, now.day, now.hour) + timedelta(hours=1)
        elif self.period == UsageLimit.PERIOD_DAILY:
            # Start of the next day
            return datetime(now.year, now.month, now.day) + timedelta(days=1)
        elif self.period == UsageLimit.PERIOD_WEEKLY:
            # Start of the next week (Monday)
            days_since_monday = now.weekday()
            days_to_next_monday = 7 - days_since_monday
            return datetime(now.year, now.month, now.day) + timedelta(days=days_to_next_monday)
        elif self.period == UsageLimit.PERIOD_MONTHLY:
            # Start of the next month
            if now.month == 12:
                return datetime(now.year + 1, 1, 1)
            else:
                return datetime(now.year, now.month + 1, 1)
        elif self.period == UsageLimit.PERIOD_QUARTERLY:
            # Start of the next quarter
            quarter = (now.month - 1) // 3
            if quarter == 3:
                return datetime(now.year + 1, 1, 1)
            else:
                return datetime(now.year, quarter * 3 + 4, 1)
        elif self.period == UsageLimit.PERIOD_YEARLY:
            # Start of the next year
            return datetime(now.year + 1, 1, 1)
        else:
            raise ValueError(f"Invalid period: {self.period}")

    def get_remaining_quantity(self) -> float:
        """
        Get the remaining quantity in the quota.

        Returns:
            Remaining quantity
        """
        return max(0, self.allocated_quantity - self.used_quantity)

    def get_usage_percentage(self) -> float:
        """
        Get the percentage of the quota that has been used.

        Returns:
            Usage percentage (0-100)
        """
        if self.allocated_quantity == 0:
            return 100.0

        return min(100.0, (self.used_quantity / self.allocated_quantity) * 100.0)

    def is_exceeded(self) -> bool:
        """
        Check if the quota has been exceeded.

        Returns:
            True if the quota has been exceeded, False otherwise
        """
        return self.used_quantity >= self.allocated_quantity

    def is_near_limit(self, threshold_percentage: float = 80.0) -> bool:
        """
        Check if the quota is near its limit.

        Args:
            threshold_percentage: Percentage threshold (0-100)

        Returns:
            True if the quota is near its limit, False otherwise
        """
        return self.get_usage_percentage() >= threshold_percentage

    def is_reset_due(self) -> bool:
        """
        Check if the quota is due for a reset.

        Returns:
            True if the quota is due for a reset, False otherwise
        """
        return datetime.now() >= self.reset_at

    def add_usage(self, quantity: float) -> float:
        """
        Add usage to the quota.

        Args:
            quantity: Quantity to add

        Returns:
            New used quantity
        """
        # Check if reset is due
        if self.is_reset_due():
            self.reset_usage()

        self.used_quantity += quantity
        self.updated_at = datetime.now()

        return self.used_quantity

    def reset_usage(self) -> None:
        """Reset the used quantity and update the reset time."""
        self.used_quantity = 0.0
        self.reset_at = self._calculate_reset_time()
        self.updated_at = datetime.now()

    def update_allocation(self, allocated_quantity: float) -> None:
        """
        Update the allocated quantity.

        Args:
            allocated_quantity: New allocated quantity
        """
        self.allocated_quantity = allocated_quantity
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the usage quota to a dictionary.

        Returns:
            Dictionary representation of the usage quota
        """
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "metric": self.metric,
            "allocated_quantity": self.allocated_quantity,
            "used_quantity": self.used_quantity,
            "period": self.period,
            "category": self.category,
            "resource_type": self.resource_type,
            "subscription_id": self.subscription_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "reset_at": self.reset_at.isoformat(),
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the usage quota to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the usage quota
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageQuota":
        """
        Create a usage quota from a dictionary.

        Args:
            data: Dictionary with usage quota data

        Returns:
            UsageQuota instance
        """
        quota = cls(
            customer_id=data["customer_id"],
            metric=data["metric"],
            allocated_quantity=data["allocated_quantity"],
            used_quantity=data["used_quantity"],
            period=data["period"],
            category=data.get("category"),
            resource_type=data.get("resource_type"),
            subscription_id=data.get("subscription_id"),
            metadata=data.get("metadata", {}),
        )

        quota.id = data["id"]
        quota.created_at = datetime.fromisoformat(data["created_at"])
        quota.updated_at = datetime.fromisoformat(data["updated_at"])
        quota.reset_at = datetime.fromisoformat(data["reset_at"])

        return quota

    def __str__(self) -> str:
        """String representation of the usage quota."""
        return f"UsageQuota({self.id}, {self.customer_id}, {self.metric}, {self.used_quantity}/{self.allocated_quantity}, {self.period})"


# Example usage
if __name__ == "__main__":
    # Create a usage record
    record = UsageRecord(
        customer_id="cust_123",
        metric=UsageMetric.API_CALL,
        quantity=1,
        category=UsageCategory.INFERENCE,
        resource_id="model_gpt4",
        resource_type="model",
        metadata={"endpoint": "/v1/completions"},
    )

    print(f"Usage record: {record}")
    print(f"Metric: {record.metric}")
    print(f"Quantity: {record.quantity}")
    print(f"Timestamp: {record.timestamp}")

    # Create a usage limit
    limit = UsageLimit(
        customer_id="cust_123",
        metric=UsageMetric.API_CALL,
        max_quantity=1000,
        period=UsageLimit.PERIOD_MONTHLY,
        category=UsageCategory.INFERENCE,
        resource_type="model",
        metadata={"tier": "basic"},
    )

    print(f"\nUsage limit: {limit}")
    print(f"Max quantity: {limit.max_quantity}")
    print(f"Period: {limit.period}")
    print(f"Period start: {limit.get_period_start()}")
    print(f"Period end: {limit.get_period_end()}")

    # Create a usage quota
    quota = UsageQuota(
        customer_id="cust_123",
        metric=UsageMetric.API_CALL,
        allocated_quantity=1000,
        period=UsageLimit.PERIOD_MONTHLY,
        category=UsageCategory.INFERENCE,
        resource_type="model",
        metadata={"tier": "basic"},
    )

    print(f"\nUsage quota: {quota}")
    print(f"Allocated quantity: {quota.allocated_quantity}")
    print(f"Used quantity: {quota.used_quantity}")
    print(f"Remaining quantity: {quota.get_remaining_quantity()}")
    print(f"Usage percentage: {quota.get_usage_percentage():.2f}%")
    print(f"Reset at: {quota.reset_at}")

    # Add usage to the quota
    quota.add_usage(100)
    print(f"\nAfter adding usage:")
    print(f"Used quantity: {quota.used_quantity}")
    print(f"Remaining quantity: {quota.get_remaining_quantity()}")
    print(f"Usage percentage: {quota.get_usage_percentage():.2f}%")
    print(f"Is exceeded: {quota.is_exceeded()}")
    print(f"Is near limit: {quota.is_near_limit()}")
