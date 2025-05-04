"""
"""
Usage tracking for the pAIssive Income project.
Usage tracking for the pAIssive Income project.


This module provides classes for tracking usage of API calls and resources,
This module provides classes for tracking usage of API calls and resources,
including usage limits, quota management, and analytics.
including usage limits, quota management, and analytics.
"""
"""


import json
import json
import time
import time
import uuid
import uuid
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional


from pydantic import BaseModel, ConfigDict, Field
from pydantic import BaseModel, ConfigDict, Field




class UsageMetric
class UsageMetric


:
    :
    """Enumeration of usage metric types."""

    API_CALL = "api_call"
    COMPUTE_TIME = "compute_time"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    TOKEN = "token"
    CREDIT = "credit"
    CUSTOM = "custom"


    class UsageCategory:

    INFERENCE = "inference"
    TRAINING = "training"
    FINE_TUNING = "fine_tuning"
    EMBEDDING = "embedding"
    STORAGE = "storage"
    DATA_TRANSFER = "data_transfer"
    CUSTOM = "custom"


    class UsageRecordSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    id: str = Field(..., description="Unique identifier for the usage record")
    customer_id: str = Field(..., description="ID of the customer")
    metric: str = Field(
    ..., description="Type of usage metric (e.g., API_CALL, COMPUTE_TIME)"
    )
    quantity: float = Field(..., description="Quantity of usage")
    category: str = Field(
    ..., description="Category of usage (e.g., INFERENCE, TRAINING)"
    )
    timestamp: datetime = Field(..., description="Timestamp of the usage")
    resource_id: Optional[str] = Field(
    None, description="ID of the resource being used"
    )
    resource_type: Optional[str] = Field(
    None, description="Type of resource being used"
    )
    subscription_id: Optional[str] = Field(None, description="ID of the subscription")
    metadata: Dict[str, Any] = Field(
    default_factory=dict, description="Additional metadata for the usage record"
    )
    created_at: datetime = Field(..., description="Creation timestamp")


    class UsageRecord:
    """
    """
    Class representing a usage record.
    Class representing a usage record.


    This class provides a structured way to represent usage of API calls and resources,
    This class provides a structured way to represent usage of API calls and resources,
    including the quantity, timestamp, and associated metadata.
    including the quantity, timestamp, and associated metadata.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    customer_id: str,
    customer_id: str,
    metric: str,
    metric: str,
    quantity: float,
    quantity: float,
    category: str = UsageCategory.INFERENCE,
    category: str = UsageCategory.INFERENCE,
    timestamp: Optional[datetime] = None,
    timestamp: Optional[datetime] = None,
    resource_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    subscription_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a usage record.
    Initialize a usage record.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    metric: Type of usage metric (e.g., API_CALL, COMPUTE_TIME)
    metric: Type of usage metric (e.g., API_CALL, COMPUTE_TIME)
    quantity: Quantity of usage
    quantity: Quantity of usage
    category: Category of usage (e.g., INFERENCE, TRAINING)
    category: Category of usage (e.g., INFERENCE, TRAINING)
    timestamp: Timestamp of the usage
    timestamp: Timestamp of the usage
    resource_id: ID of the resource being used
    resource_id: ID of the resource being used
    resource_type: Type of resource being used
    resource_type: Type of resource being used
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription
    metadata: Additional metadata for the usage record
    metadata: Additional metadata for the usage record
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.customer_id = customer_id
    self.customer_id = customer_id
    self.metric = metric
    self.metric = metric
    self.quantity = quantity
    self.quantity = quantity
    self.category = category
    self.category = category
    self.timestamp = timestamp or datetime.now()
    self.timestamp = timestamp or datetime.now()
    self.resource_id = resource_id
    self.resource_id = resource_id
    self.resource_type = resource_type
    self.resource_type = resource_type
    self.subscription_id = subscription_id
    self.subscription_id = subscription_id
    self.metadata = metadata or {}
    self.metadata = metadata or {}
    self.created_at = datetime.now()
    self.created_at = datetime.now()


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the usage record to a dictionary.
    Convert the usage record to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the usage record
    Dictionary representation of the usage record
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "customer_id": self.customer_id,
    "customer_id": self.customer_id,
    "metric": self.metric,
    "metric": self.metric,
    "quantity": self.quantity,
    "quantity": self.quantity,
    "category": self.category,
    "category": self.category,
    "timestamp": self.timestamp.isoformat(),
    "timestamp": self.timestamp.isoformat(),
    "resource_id": self.resource_id,
    "resource_id": self.resource_id,
    "resource_type": self.resource_type,
    "resource_type": self.resource_type,
    "subscription_id": self.subscription_id,
    "subscription_id": self.subscription_id,
    "metadata": self.metadata,
    "metadata": self.metadata,
    "created_at": self.created_at.isoformat(),
    "created_at": self.created_at.isoformat(),
    }
    }


    def to_json(self, indent: int = 2) -> str:
    def to_json(self, indent: int = 2) -> str:
    """
    """
    Convert the usage record to a JSON string.
    Convert the usage record to a JSON string.


    Args:
    Args:
    indent: Number of spaces for indentation
    indent: Number of spaces for indentation


    Returns:
    Returns:
    JSON string representation of the usage record
    JSON string representation of the usage record
    """
    """
    return json.dumps(self.to_dict(), indent=indent)
    return json.dumps(self.to_dict(), indent=indent)


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageRecord":
    def from_dict(cls, data: Dict[str, Any]) -> "UsageRecord":
    """
    """
    Create a usage record from a dictionary.
    Create a usage record from a dictionary.


    Args:
    Args:
    data: Dictionary with usage record data
    data: Dictionary with usage record data


    Returns:
    Returns:
    UsageRecord instance
    UsageRecord instance
    """
    """
    record = cls(
    record = cls(
    customer_id=data["customer_id"],
    customer_id=data["customer_id"],
    metric=data["metric"],
    metric=data["metric"],
    quantity=data["quantity"],
    quantity=data["quantity"],
    category=data["category"],
    category=data["category"],
    timestamp=datetime.fromisoformat(data["timestamp"]),
    timestamp=datetime.fromisoformat(data["timestamp"]),
    resource_id=data.get("resource_id"),
    resource_id=data.get("resource_id"),
    resource_type=data.get("resource_type"),
    resource_type=data.get("resource_type"),
    subscription_id=data.get("subscription_id"),
    subscription_id=data.get("subscription_id"),
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    record.id = data["id"]
    record.id = data["id"]
    record.created_at = datetime.fromisoformat(data["created_at"])
    record.created_at = datetime.fromisoformat(data["created_at"])


    return record
    return record


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the usage record."""
    return f"UsageRecord({self.id}, {self.customer_id}, {self.metric}, {self.quantity}, {self.timestamp.isoformat()})"


    class UsageLimit:
    """
    """
    Class representing a usage limit.
    Class representing a usage limit.


    This class provides a structured way to represent limits on usage of API calls
    This class provides a structured way to represent limits on usage of API calls
    and resources, including the maximum quantity, time period, and associated metadata.
    and resources, including the maximum quantity, time period, and associated metadata.
    """
    """


    # Time period types
    # Time period types
    PERIOD_HOURLY = "hourly"
    PERIOD_HOURLY = "hourly"
    PERIOD_DAILY = "daily"
    PERIOD_DAILY = "daily"
    PERIOD_WEEKLY = "weekly"
    PERIOD_WEEKLY = "weekly"
    PERIOD_MONTHLY = "monthly"
    PERIOD_MONTHLY = "monthly"
    PERIOD_QUARTERLY = "quarterly"
    PERIOD_QUARTERLY = "quarterly"
    PERIOD_YEARLY = "yearly"
    PERIOD_YEARLY = "yearly"


    def __init__(
    def __init__(
    self,
    self,
    customer_id: str,
    customer_id: str,
    metric: str,
    metric: str,
    max_quantity: float,
    max_quantity: float,
    period: str = PERIOD_MONTHLY,
    period: str = PERIOD_MONTHLY,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    subscription_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a usage limit.
    Initialize a usage limit.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    metric: Type of usage metric (e.g., API_CALL, COMPUTE_TIME)
    metric: Type of usage metric (e.g., API_CALL, COMPUTE_TIME)
    max_quantity: Maximum quantity allowed
    max_quantity: Maximum quantity allowed
    period: Time period for the limit (e.g., DAILY, MONTHLY)
    period: Time period for the limit (e.g., DAILY, MONTHLY)
    category: Category of usage (e.g., INFERENCE, TRAINING)
    category: Category of usage (e.g., INFERENCE, TRAINING)
    resource_type: Type of resource being limited
    resource_type: Type of resource being limited
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription
    metadata: Additional metadata for the usage limit
    metadata: Additional metadata for the usage limit
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.customer_id = customer_id
    self.customer_id = customer_id
    self.metric = metric
    self.metric = metric
    self.max_quantity = max_quantity
    self.max_quantity = max_quantity
    self.period = period
    self.period = period
    self.category = category
    self.category = category
    self.resource_type = resource_type
    self.resource_type = resource_type
    self.subscription_id = subscription_id
    self.subscription_id = subscription_id
    self.metadata = metadata or {}
    self.metadata = metadata or {}
    self.created_at = datetime.now()
    self.created_at = datetime.now()
    self.updated_at = self.created_at
    self.updated_at = self.created_at


    def get_period_start(self, reference_time: Optional[datetime] = None) -> datetime:
    def get_period_start(self, reference_time: Optional[datetime] = None) -> datetime:
    """
    """
    Get the start of the current period.
    Get the start of the current period.


    Args:
    Args:
    reference_time: Reference time (defaults to now)
    reference_time: Reference time (defaults to now)


    Returns:
    Returns:
    Start of the current period
    Start of the current period
    """
    """
    if reference_time is None:
    if reference_time is None:
    reference_time = datetime.now()
    reference_time = datetime.now()


    if self.period == self.PERIOD_HOURLY:
    if self.period == self.PERIOD_HOURLY:
    return datetime(
    return datetime(
    reference_time.year,
    reference_time.year,
    reference_time.month,
    reference_time.month,
    reference_time.day,
    reference_time.day,
    reference_time.hour,
    reference_time.hour,
    )
    )
    elif self.period == self.PERIOD_DAILY:
    elif self.period == self.PERIOD_DAILY:
    return datetime(
    return datetime(
    reference_time.year, reference_time.month, reference_time.day
    reference_time.year, reference_time.month, reference_time.day
    )
    )
    elif self.period == self.PERIOD_WEEKLY:
    elif self.period == self.PERIOD_WEEKLY:
    # Start of the week (Monday)
    # Start of the week (Monday)
    days_since_monday = reference_time.weekday()
    days_since_monday = reference_time.weekday()
    return datetime(
    return datetime(
    reference_time.year, reference_time.month, reference_time.day
    reference_time.year, reference_time.month, reference_time.day
    ) - timedelta(days=days_since_monday)
    ) - timedelta(days=days_since_monday)
    elif self.period == self.PERIOD_MONTHLY:
    elif self.period == self.PERIOD_MONTHLY:
    return datetime(reference_time.year, reference_time.month, 1)
    return datetime(reference_time.year, reference_time.month, 1)
    elif self.period == self.PERIOD_QUARTERLY:
    elif self.period == self.PERIOD_QUARTERLY:
    # Start of the quarter
    # Start of the quarter
    quarter = (reference_time.month - 1) // 3
    quarter = (reference_time.month - 1) // 3
    return datetime(reference_time.year, quarter * 3 + 1, 1)
    return datetime(reference_time.year, quarter * 3 + 1, 1)
    elif self.period == self.PERIOD_YEARLY:
    elif self.period == self.PERIOD_YEARLY:
    return datetime(reference_time.year, 1, 1)
    return datetime(reference_time.year, 1, 1)
    else:
    else:
    raise ValueError(f"Invalid period: {self.period}")
    raise ValueError(f"Invalid period: {self.period}")


    def get_period_end(self, reference_time: Optional[datetime] = None) -> datetime:
    def get_period_end(self, reference_time: Optional[datetime] = None) -> datetime:
    """
    """
    Get the end of the current period.
    Get the end of the current period.


    Args:
    Args:
    reference_time: Reference time (defaults to now)
    reference_time: Reference time (defaults to now)


    Returns:
    Returns:
    End of the current period
    End of the current period
    """
    """
    if reference_time is None:
    if reference_time is None:
    reference_time = datetime.now()
    reference_time = datetime.now()


    if self.period == self.PERIOD_HOURLY:
    if self.period == self.PERIOD_HOURLY:
    return (
    return (
    self.get_period_start(reference_time)
    self.get_period_start(reference_time)
    + timedelta(hours=1)
    + timedelta(hours=1)
    - timedelta(microseconds=1)
    - timedelta(microseconds=1)
    )
    )
    elif self.period == self.PERIOD_DAILY:
    elif self.period == self.PERIOD_DAILY:
    return (
    return (
    self.get_period_start(reference_time)
    self.get_period_start(reference_time)
    + timedelta(days=1)
    + timedelta(days=1)
    - timedelta(microseconds=1)
    - timedelta(microseconds=1)
    )
    )
    elif self.period == self.PERIOD_WEEKLY:
    elif self.period == self.PERIOD_WEEKLY:
    return (
    return (
    self.get_period_start(reference_time)
    self.get_period_start(reference_time)
    + timedelta(days=7)
    + timedelta(days=7)
    - timedelta(microseconds=1)
    - timedelta(microseconds=1)
    )
    )
    elif self.period == self.PERIOD_MONTHLY:
    elif self.period == self.PERIOD_MONTHLY:
    # Last day of the month
    # Last day of the month
    start = self.get_period_start(reference_time)
    start = self.get_period_start(reference_time)
    if start.month == 12:
    if start.month == 12:
    next_month = datetime(start.year + 1, 1, 1)
    next_month = datetime(start.year + 1, 1, 1)
    else:
    else:
    next_month = datetime(start.year, start.month + 1, 1)
    next_month = datetime(start.year, start.month + 1, 1)
    return next_month - timedelta(microseconds=1)
    return next_month - timedelta(microseconds=1)
    elif self.period == self.PERIOD_QUARTERLY:
    elif self.period == self.PERIOD_QUARTERLY:
    # Last day of the quarter
    # Last day of the quarter
    start = self.get_period_start(reference_time)
    start = self.get_period_start(reference_time)
    if start.month >= 10:
    if start.month >= 10:
    next_quarter = datetime(start.year + 1, 1, 1)
    next_quarter = datetime(start.year + 1, 1, 1)
    else:
    else:
    next_quarter = datetime(start.year, start.month + 3, 1)
    next_quarter = datetime(start.year, start.month + 3, 1)
    return next_quarter - timedelta(microseconds=1)
    return next_quarter - timedelta(microseconds=1)
    elif self.period == self.PERIOD_YEARLY:
    elif self.period == self.PERIOD_YEARLY:
    # Last day of the year
    # Last day of the year
    start = self.get_period_start(reference_time)
    start = self.get_period_start(reference_time)
    return datetime(start.year + 1, 1, 1) - timedelta(microseconds=1)
    return datetime(start.year + 1, 1, 1) - timedelta(microseconds=1)
    else:
    else:
    raise ValueError(f"Invalid period: {self.period}")
    raise ValueError(f"Invalid period: {self.period}")


    def is_within_period(
    def is_within_period(
    self, timestamp: datetime, reference_time: Optional[datetime] = None
    self, timestamp: datetime, reference_time: Optional[datetime] = None
    ) -> bool:
    ) -> bool:
    """
    """
    Check if a timestamp is within the current period.
    Check if a timestamp is within the current period.


    Args:
    Args:
    timestamp: Timestamp to check
    timestamp: Timestamp to check
    reference_time: Reference time (defaults to now)
    reference_time: Reference time (defaults to now)


    Returns:
    Returns:
    True if the timestamp is within the current period, False otherwise
    True if the timestamp is within the current period, False otherwise
    """
    """
    if reference_time is None:
    if reference_time is None:
    reference_time = datetime.now()
    reference_time = datetime.now()


    period_start = self.get_period_start(reference_time)
    period_start = self.get_period_start(reference_time)
    period_end = self.get_period_end(reference_time)
    period_end = self.get_period_end(reference_time)


    return period_start <= timestamp <= period_end
    return period_start <= timestamp <= period_end


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the usage limit to a dictionary.
    Convert the usage limit to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the usage limit
    Dictionary representation of the usage limit
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "customer_id": self.customer_id,
    "customer_id": self.customer_id,
    "metric": self.metric,
    "metric": self.metric,
    "max_quantity": self.max_quantity,
    "max_quantity": self.max_quantity,
    "period": self.period,
    "period": self.period,
    "category": self.category,
    "category": self.category,
    "resource_type": self.resource_type,
    "resource_type": self.resource_type,
    "subscription_id": self.subscription_id,
    "subscription_id": self.subscription_id,
    "metadata": self.metadata,
    "metadata": self.metadata,
    "created_at": self.created_at.isoformat(),
    "created_at": self.created_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    }
    }


    def to_json(self, indent: int = 2) -> str:
    def to_json(self, indent: int = 2) -> str:
    """
    """
    Convert the usage limit to a JSON string.
    Convert the usage limit to a JSON string.


    Args:
    Args:
    indent: Number of spaces for indentation
    indent: Number of spaces for indentation


    Returns:
    Returns:
    JSON string representation of the usage limit
    JSON string representation of the usage limit
    """
    """
    return json.dumps(self.to_dict(), indent=indent)
    return json.dumps(self.to_dict(), indent=indent)


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageLimit":
    def from_dict(cls, data: Dict[str, Any]) -> "UsageLimit":
    """
    """
    Create a usage limit from a dictionary.
    Create a usage limit from a dictionary.


    Args:
    Args:
    data: Dictionary with usage limit data
    data: Dictionary with usage limit data


    Returns:
    Returns:
    UsageLimit instance
    UsageLimit instance
    """
    """
    limit = cls(
    limit = cls(
    customer_id=data["customer_id"],
    customer_id=data["customer_id"],
    metric=data["metric"],
    metric=data["metric"],
    max_quantity=data["max_quantity"],
    max_quantity=data["max_quantity"],
    period=data["period"],
    period=data["period"],
    category=data.get("category"),
    category=data.get("category"),
    resource_type=data.get("resource_type"),
    resource_type=data.get("resource_type"),
    subscription_id=data.get("subscription_id"),
    subscription_id=data.get("subscription_id"),
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    limit.id = data["id"]
    limit.id = data["id"]
    limit.created_at = datetime.fromisoformat(data["created_at"])
    limit.created_at = datetime.fromisoformat(data["created_at"])
    limit.updated_at = datetime.fromisoformat(data["updated_at"])
    limit.updated_at = datetime.fromisoformat(data["updated_at"])


    return limit
    return limit


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the usage limit."""
    return f"UsageLimit({self.id}, {self.customer_id}, {self.metric}, {self.max_quantity}, {self.period})"


    class UsageQuota:
    """
    """
    Class representing a usage quota.
    Class representing a usage quota.


    This class provides a structured way to represent quotas for usage of API calls
    This class provides a structured way to represent quotas for usage of API calls
    and resources, including the allocated quantity, time period, and associated metadata.
    and resources, including the allocated quantity, time period, and associated metadata.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    customer_id: str,
    customer_id: str,
    metric: str,
    metric: str,
    allocated_quantity: float,
    allocated_quantity: float,
    used_quantity: float = 0.0,
    used_quantity: float = 0.0,
    period: str = UsageLimit.PERIOD_MONTHLY,
    period: str = UsageLimit.PERIOD_MONTHLY,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    subscription_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a usage quota.
    Initialize a usage quota.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    metric: Type of usage metric (e.g., API_CALL, COMPUTE_TIME)
    metric: Type of usage metric (e.g., API_CALL, COMPUTE_TIME)
    allocated_quantity: Allocated quantity
    allocated_quantity: Allocated quantity
    used_quantity: Used quantity
    used_quantity: Used quantity
    period: Time period for the quota (e.g., DAILY, MONTHLY)
    period: Time period for the quota (e.g., DAILY, MONTHLY)
    category: Category of usage (e.g., INFERENCE, TRAINING)
    category: Category of usage (e.g., INFERENCE, TRAINING)
    resource_type: Type of resource
    resource_type: Type of resource
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription
    metadata: Additional metadata for the usage quota
    metadata: Additional metadata for the usage quota
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.customer_id = customer_id
    self.customer_id = customer_id
    self.metric = metric
    self.metric = metric
    self.allocated_quantity = allocated_quantity
    self.allocated_quantity = allocated_quantity
    self.used_quantity = used_quantity
    self.used_quantity = used_quantity
    self.period = period
    self.period = period
    self.category = category
    self.category = category
    self.resource_type = resource_type
    self.resource_type = resource_type
    self.subscription_id = subscription_id
    self.subscription_id = subscription_id
    self.metadata = metadata or {}
    self.metadata = metadata or {}
    self.created_at = datetime.now()
    self.created_at = datetime.now()
    self.updated_at = self.created_at
    self.updated_at = self.created_at
    self.reset_at = self._calculate_reset_time()
    self.reset_at = self._calculate_reset_time()


    def _calculate_reset_time(self) -> datetime:
    def _calculate_reset_time(self) -> datetime:
    """
    """
    Calculate the next reset time for the quota.
    Calculate the next reset time for the quota.


    Returns:
    Returns:
    Next reset time
    Next reset time
    """
    """
    now = datetime.now()
    now = datetime.now()


    if self.period == UsageLimit.PERIOD_HOURLY:
    if self.period == UsageLimit.PERIOD_HOURLY:
    # Start of the next hour
    # Start of the next hour
    return datetime(now.year, now.month, now.day, now.hour) + timedelta(hours=1)
    return datetime(now.year, now.month, now.day, now.hour) + timedelta(hours=1)
    elif self.period == UsageLimit.PERIOD_DAILY:
    elif self.period == UsageLimit.PERIOD_DAILY:
    # Start of the next day
    # Start of the next day
    return datetime(now.year, now.month, now.day) + timedelta(days=1)
    return datetime(now.year, now.month, now.day) + timedelta(days=1)
    elif self.period == UsageLimit.PERIOD_WEEKLY:
    elif self.period == UsageLimit.PERIOD_WEEKLY:
    # Start of the next week (Monday)
    # Start of the next week (Monday)
    days_since_monday = now.weekday()
    days_since_monday = now.weekday()
    days_to_next_monday = 7 - days_since_monday
    days_to_next_monday = 7 - days_since_monday
    return datetime(now.year, now.month, now.day) + timedelta(
    return datetime(now.year, now.month, now.day) + timedelta(
    days=days_to_next_monday
    days=days_to_next_monday
    )
    )
    elif self.period == UsageLimit.PERIOD_MONTHLY:
    elif self.period == UsageLimit.PERIOD_MONTHLY:
    # Start of the next month
    # Start of the next month
    if now.month == 12:
    if now.month == 12:
    return datetime(now.year + 1, 1, 1)
    return datetime(now.year + 1, 1, 1)
    else:
    else:
    return datetime(now.year, now.month + 1, 1)
    return datetime(now.year, now.month + 1, 1)
    elif self.period == UsageLimit.PERIOD_QUARTERLY:
    elif self.period == UsageLimit.PERIOD_QUARTERLY:
    # Start of the next quarter
    # Start of the next quarter
    quarter = (now.month - 1) // 3
    quarter = (now.month - 1) // 3
    if quarter == 3:
    if quarter == 3:
    return datetime(now.year + 1, 1, 1)
    return datetime(now.year + 1, 1, 1)
    else:
    else:
    return datetime(now.year, quarter * 3 + 4, 1)
    return datetime(now.year, quarter * 3 + 4, 1)
    elif self.period == UsageLimit.PERIOD_YEARLY:
    elif self.period == UsageLimit.PERIOD_YEARLY:
    # Start of the next year
    # Start of the next year
    return datetime(now.year + 1, 1, 1)
    return datetime(now.year + 1, 1, 1)
    else:
    else:
    raise ValueError(f"Invalid period: {self.period}")
    raise ValueError(f"Invalid period: {self.period}")


    def get_remaining_quantity(self) -> float:
    def get_remaining_quantity(self) -> float:
    """
    """
    Get the remaining quantity in the quota.
    Get the remaining quantity in the quota.


    Returns:
    Returns:
    Remaining quantity
    Remaining quantity
    """
    """
    return max(0, self.allocated_quantity - self.used_quantity)
    return max(0, self.allocated_quantity - self.used_quantity)


    def get_usage_percentage(self) -> float:
    def get_usage_percentage(self) -> float:
    """
    """
    Get the percentage of the quota that has been used.
    Get the percentage of the quota that has been used.


    Returns:
    Returns:
    Usage percentage (0-100)
    Usage percentage (0-100)
    """
    """
    if self.allocated_quantity == 0:
    if self.allocated_quantity == 0:
    return 100.0
    return 100.0


    return min(100.0, (self.used_quantity / self.allocated_quantity) * 100.0)
    return min(100.0, (self.used_quantity / self.allocated_quantity) * 100.0)


    def is_exceeded(self) -> bool:
    def is_exceeded(self) -> bool:
    """
    """
    Check if the quota has been exceeded.
    Check if the quota has been exceeded.


    Returns:
    Returns:
    True if the quota has been exceeded, False otherwise
    True if the quota has been exceeded, False otherwise
    """
    """
    return self.used_quantity >= self.allocated_quantity
    return self.used_quantity >= self.allocated_quantity


    def is_near_limit(self, threshold_percentage: float = 80.0) -> bool:
    def is_near_limit(self, threshold_percentage: float = 80.0) -> bool:
    """
    """
    Check if the quota is near its limit.
    Check if the quota is near its limit.


    Args:
    Args:
    threshold_percentage: Percentage threshold (0-100)
    threshold_percentage: Percentage threshold (0-100)


    Returns:
    Returns:
    True if the quota is near its limit, False otherwise
    True if the quota is near its limit, False otherwise
    """
    """
    return self.get_usage_percentage() >= threshold_percentage
    return self.get_usage_percentage() >= threshold_percentage


    def is_reset_due(self) -> bool:
    def is_reset_due(self) -> bool:
    """
    """
    Check if the quota is due for a reset.
    Check if the quota is due for a reset.


    Returns:
    Returns:
    True if the quota is due for a reset, False otherwise
    True if the quota is due for a reset, False otherwise
    """
    """
    return datetime.now() >= self.reset_at
    return datetime.now() >= self.reset_at


    def add_usage(self, quantity: float) -> float:
    def add_usage(self, quantity: float) -> float:
    """
    """
    Add usage to the quota.
    Add usage to the quota.


    Args:
    Args:
    quantity: Quantity to add
    quantity: Quantity to add


    Returns:
    Returns:
    New used quantity
    New used quantity
    """
    """
    # Check if reset is due
    # Check if reset is due
    if self.is_reset_due():
    if self.is_reset_due():
    self.reset_usage()
    self.reset_usage()


    self.used_quantity += quantity
    self.used_quantity += quantity
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    return self.used_quantity
    return self.used_quantity


    def reset_usage(self) -> None:
    def reset_usage(self) -> None:
    """Reset the used quantity and update the reset time."""
    self.used_quantity = 0.0
    self.reset_at = self._calculate_reset_time()
    self.updated_at = datetime.now()

    def update_allocation(self, allocated_quantity: float) -> None:
    """
    """
    Update the allocated quantity.
    Update the allocated quantity.


    Args:
    Args:
    allocated_quantity: New allocated quantity
    allocated_quantity: New allocated quantity
    """
    """
    self.allocated_quantity = allocated_quantity
    self.allocated_quantity = allocated_quantity
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the usage quota to a dictionary.
    Convert the usage quota to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the usage quota
    Dictionary representation of the usage quota
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "customer_id": self.customer_id,
    "customer_id": self.customer_id,
    "metric": self.metric,
    "metric": self.metric,
    "allocated_quantity": self.allocated_quantity,
    "allocated_quantity": self.allocated_quantity,
    "used_quantity": self.used_quantity,
    "used_quantity": self.used_quantity,
    "period": self.period,
    "period": self.period,
    "category": self.category,
    "category": self.category,
    "resource_type": self.resource_type,
    "resource_type": self.resource_type,
    "subscription_id": self.subscription_id,
    "subscription_id": self.subscription_id,
    "metadata": self.metadata,
    "metadata": self.metadata,
    "created_at": self.created_at.isoformat(),
    "created_at": self.created_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    "reset_at": self.reset_at.isoformat(),
    "reset_at": self.reset_at.isoformat(),
    }
    }


    def to_json(self, indent: int = 2) -> str:
    def to_json(self, indent: int = 2) -> str:
    """
    """
    Convert the usage quota to a JSON string.
    Convert the usage quota to a JSON string.


    Args:
    Args:
    indent: Number of spaces for indentation
    indent: Number of spaces for indentation


    Returns:
    Returns:
    JSON string representation of the usage quota
    JSON string representation of the usage quota
    """
    """
    return json.dumps(self.to_dict(), indent=indent)
    return json.dumps(self.to_dict(), indent=indent)


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageQuota":
    def from_dict(cls, data: Dict[str, Any]) -> "UsageQuota":
    """
    """
    Create a usage quota from a dictionary.
    Create a usage quota from a dictionary.


    Args:
    Args:
    data: Dictionary with usage quota data
    data: Dictionary with usage quota data


    Returns:
    Returns:
    UsageQuota instance
    UsageQuota instance
    """
    """
    quota = cls(
    quota = cls(
    customer_id=data["customer_id"],
    customer_id=data["customer_id"],
    metric=data["metric"],
    metric=data["metric"],
    allocated_quantity=data["allocated_quantity"],
    allocated_quantity=data["allocated_quantity"],
    used_quantity=data["used_quantity"],
    used_quantity=data["used_quantity"],
    period=data["period"],
    period=data["period"],
    category=data.get("category"),
    category=data.get("category"),
    resource_type=data.get("resource_type"),
    resource_type=data.get("resource_type"),
    subscription_id=data.get("subscription_id"),
    subscription_id=data.get("subscription_id"),
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    quota.id = data["id"]
    quota.id = data["id"]
    quota.created_at = datetime.fromisoformat(data["created_at"])
    quota.created_at = datetime.fromisoformat(data["created_at"])
    quota.updated_at = datetime.fromisoformat(data["updated_at"])
    quota.updated_at = datetime.fromisoformat(data["updated_at"])
    quota.reset_at = datetime.fromisoformat(data["reset_at"])
    quota.reset_at = datetime.fromisoformat(data["reset_at"])


    return quota
    return quota


    def __str__(self) -> str:
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
    print("\nAfter adding usage:")
    print(f"Used quantity: {quota.used_quantity}")
    print(f"Remaining quantity: {quota.get_remaining_quantity()}")
    print(f"Usage percentage: {quota.get_usage_percentage():.2f}%")
    print(f"Is exceeded: {quota.is_exceeded()}")
    print(f"Is near limit: {quota.is_near_limit()}"