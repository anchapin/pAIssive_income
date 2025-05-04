"""
"""
User subscription management for the pAIssive Income project.
User subscription management for the pAIssive Income project.


This module provides classes for managing user subscriptions, including
This module provides classes for managing user subscriptions, including
subscription creation, renewal, cancellation, and status tracking.
subscription creation, renewal, cancellation, and status tracking.
"""
"""




import json
import json
import uuid
import uuid
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .subscription import SubscriptionPlan, SubscriptionTier
from .subscription import SubscriptionPlan, SubscriptionTier




class SubscriptionStatus:
    class SubscriptionStatus:
    from .subscription import SubscriptionPlan
    from .subscription import SubscriptionPlan






    :
    :
    """Enumeration of subscription statuses."""

    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    CANCELED = "canceled"
    EXPIRED = "expired"
    PAUSED = "paused"


    class Subscription:
    """
    """
    Class for managing user subscriptions.
    Class for managing user subscriptions.


    A subscription represents a user's subscription to a specific plan and tier,
    A subscription represents a user's subscription to a specific plan and tier,
    including status, billing information, and usage data.
    including status, billing information, and usage data.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    user_id: str,
    user_id: str,
    plan: SubscriptionPlan,
    plan: SubscriptionPlan,
    tier_id: str,
    tier_id: str,
    billing_cycle: str = "monthly",
    billing_cycle: str = "monthly",
    start_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a subscription.
    Initialize a subscription.


    Args:
    Args:
    user_id: ID of the user
    user_id: ID of the user
    plan: Subscription plan
    plan: Subscription plan
    tier_id: ID of the subscription tier
    tier_id: ID of the subscription tier
    billing_cycle: Billing cycle (monthly, annual)
    billing_cycle: Billing cycle (monthly, annual)
    start_date: Start date of the subscription
    start_date: Start date of the subscription
    metadata: Additional metadata for the subscription
    metadata: Additional metadata for the subscription
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.user_id = user_id
    self.user_id = user_id
    self.plan_id = plan.id
    self.plan_id = plan.id
    self.plan = plan
    self.plan = plan
    self.tier_id = tier_id
    self.tier_id = tier_id


    # Validate tier exists in plan
    # Validate tier exists in plan
    tier = plan.get_tier(tier_id)
    tier = plan.get_tier(tier_id)
    if not tier:
    if not tier:
    raise ValueError(f"Tier with ID {tier_id} not found in plan {plan.name}")
    raise ValueError(f"Tier with ID {tier_id} not found in plan {plan.name}")


    # Validate billing cycle
    # Validate billing cycle
    if billing_cycle not in plan.billing_cycles:
    if billing_cycle not in plan.billing_cycles:
    raise ValueError(
    raise ValueError(
    f"Invalid billing cycle: {billing_cycle}. Valid options: {plan.billing_cycles}"
    f"Invalid billing cycle: {billing_cycle}. Valid options: {plan.billing_cycles}"
    )
    )


    self.billing_cycle = billing_cycle
    self.billing_cycle = billing_cycle
    self.start_date = start_date or datetime.now()
    self.start_date = start_date or datetime.now()


    # Calculate end date based on billing cycle
    # Calculate end date based on billing cycle
    if billing_cycle == "monthly":
    if billing_cycle == "monthly":
    self.end_date = self.start_date + timedelta(days=30)
    self.end_date = self.start_date + timedelta(days=30)
    elif billing_cycle == "annual":
    elif billing_cycle == "annual":
    self.end_date = self.start_date + timedelta(days=365)
    self.end_date = self.start_date + timedelta(days=365)
    else:
    else:
    # Default to monthly
    # Default to monthly
    self.end_date = self.start_date + timedelta(days=30)
    self.end_date = self.start_date + timedelta(days=30)


    # Set initial status
    # Set initial status
    self.status = SubscriptionStatus.ACTIVE
    self.status = SubscriptionStatus.ACTIVE


    # Check if tier has trial days
    # Check if tier has trial days
    if tier.get("trial_days", 0) > 0:
    if tier.get("trial_days", 0) > 0:
    self.status = SubscriptionStatus.TRIAL
    self.status = SubscriptionStatus.TRIAL
    self.trial_end_date = self.start_date + timedelta(
    self.trial_end_date = self.start_date + timedelta(
    days=tier.get("trial_days", 0)
    days=tier.get("trial_days", 0)
    )
    )
    else:
    else:
    self.trial_end_date = None
    self.trial_end_date = None


    # Initialize other properties
    # Initialize other properties
    self.canceled_at = None
    self.canceled_at = None
    self.current_period_start = self.start_date
    self.current_period_start = self.start_date
    self.current_period_end = self.end_date
    self.current_period_end = self.end_date
    self.metadata = metadata or {}
    self.metadata = metadata or {}
    self.status_history = [
    self.status_history = [
    {
    {
    "status": self.status,
    "status": self.status,
    "timestamp": self.start_date.isoformat(),
    "timestamp": self.start_date.isoformat(),
    "reason": "Subscription created",
    "reason": "Subscription created",
    }
    }
    ]
    ]


    # Calculate price based on tier and billing cycle
    # Calculate price based on tier and billing cycle
    if billing_cycle == "monthly":
    if billing_cycle == "monthly":
    self.price = tier["price_monthly"]
    self.price = tier["price_monthly"]
    elif billing_cycle == "annual":
    elif billing_cycle == "annual":
    self.price = tier["price_annual"]
    self.price = tier["price_annual"]
    else:
    else:
    self.price = tier["price_monthly"]
    self.price = tier["price_monthly"]


    # Initialize usage data
    # Initialize usage data
    self.usage = {}
    self.usage = {}


    # Set timestamps
    # Set timestamps
    self.created_at = datetime.now()
    self.created_at = datetime.now()
    self.updated_at = self.created_at
    self.updated_at = self.created_at


    @property
    @property
    def tier_name(self) -> str:
    def tier_name(self) -> str:
    """
    """
    Get the name of the subscription tier.
    Get the name of the subscription tier.


    Returns:
    Returns:
    Name of the subscription tier
    Name of the subscription tier
    """
    """
    tier = self.get_tier()
    tier = self.get_tier()
    if tier:
    if tier:
    if isinstance(tier, dict):
    if isinstance(tier, dict):
    return tier.get("name", "Unknown")
    return tier.get("name", "Unknown")
    return getattr(tier, "name", "Unknown")
    return getattr(tier, "name", "Unknown")
    return "Unknown"
    return "Unknown"


    def get_tier(self) -> Dict[str, Any]:
    def get_tier(self) -> Dict[str, Any]:
    """
    """
    Get the subscription tier.
    Get the subscription tier.


    Returns:
    Returns:
    The subscription tier
    The subscription tier
    """
    """
    return self.plan.get_tier(self.tier_id)
    return self.plan.get_tier(self.tier_id)


    def get_tier_object(self) -> SubscriptionTier:
    def get_tier_object(self) -> SubscriptionTier:
    """
    """
    Get the subscription tier as a SubscriptionTier object.
    Get the subscription tier as a SubscriptionTier object.


    Returns:
    Returns:
    SubscriptionTier object
    SubscriptionTier object
    """
    """
    return SubscriptionTier(self.plan, self.tier_id)
    return SubscriptionTier(self.plan, self.tier_id)


    def get_features(self) -> List[Dict[str, Any]]:
    def get_features(self) -> List[Dict[str, Any]]:
    """
    """
    Get the features included in this subscription.
    Get the features included in this subscription.


    Returns:
    Returns:
    List of features with their details
    List of features with their details
    """
    """
    return self.plan.get_tier_features(self.tier_id)
    return self.plan.get_tier_features(self.tier_id)


    def has_feature(self, feature_id: str) -> bool:
    def has_feature(self, feature_id: str) -> bool:
    """
    """
    Check if this subscription has a specific feature.
    Check if this subscription has a specific feature.


    Args:
    Args:
    feature_id: ID of the feature
    feature_id: ID of the feature


    Returns:
    Returns:
    True if the subscription has the feature, False otherwise
    True if the subscription has the feature, False otherwise
    """
    """
    tier = self.get_tier()
    tier = self.get_tier()


    for feature in tier["features"]:
    for feature in tier["features"]:
    if feature["feature_id"] == feature_id:
    if feature["feature_id"] == feature_id:
    return True
    return True


    return False
    return False


    def get_feature_value(self, feature_id: str) -> Optional[Any]:
    def get_feature_value(self, feature_id: str) -> Optional[Any]:
    """
    """
    Get the value of a feature for this subscription.
    Get the value of a feature for this subscription.


    Args:
    Args:
    feature_id: ID of the feature
    feature_id: ID of the feature


    Returns:
    Returns:
    Value of the feature or None if not found
    Value of the feature or None if not found
    """
    """
    tier = self.get_tier()
    tier = self.get_tier()


    for feature in tier["features"]:
    for feature in tier["features"]:
    if feature["feature_id"] == feature_id:
    if feature["feature_id"] == feature_id:
    return feature.get("value", True)
    return feature.get("value", True)


    return None
    return None


    def get_feature_limit(self, feature_id: str) -> Optional[int]:
    def get_feature_limit(self, feature_id: str) -> Optional[int]:
    """
    """
    Get the limit of a feature for this subscription.
    Get the limit of a feature for this subscription.


    Args:
    Args:
    feature_id: ID of the feature
    feature_id: ID of the feature


    Returns:
    Returns:
    Limit of the feature or None if not found or no limit
    Limit of the feature or None if not found or no limit
    """
    """
    tier = self.get_tier()
    tier = self.get_tier()


    for feature in tier["features"]:
    for feature in tier["features"]:
    if feature["feature_id"] == feature_id:
    if feature["feature_id"] == feature_id:
    return feature.get("limit")
    return feature.get("limit")


    return None
    return None


    def get_feature_usage(self, feature_id: str) -> int:
    def get_feature_usage(self, feature_id: str) -> int:
    """
    """
    Get the usage of a feature for this subscription.
    Get the usage of a feature for this subscription.


    Args:
    Args:
    feature_id: ID of the feature
    feature_id: ID of the feature


    Returns:
    Returns:
    Usage of the feature
    Usage of the feature
    """
    """
    return self.usage.get(feature_id, 0)
    return self.usage.get(feature_id, 0)


    def increment_feature_usage(self, feature_id: str, amount: int = 1) -> int:
    def increment_feature_usage(self, feature_id: str, amount: int = 1) -> int:
    """
    """
    Increment the usage of a feature for this subscription.
    Increment the usage of a feature for this subscription.


    Args:
    Args:
    feature_id: ID of the feature
    feature_id: ID of the feature
    amount: Amount to increment
    amount: Amount to increment


    Returns:
    Returns:
    New usage of the feature
    New usage of the feature
    """
    """
    if feature_id not in self.usage:
    if feature_id not in self.usage:
    self.usage[feature_id] = 0
    self.usage[feature_id] = 0


    self.usage[feature_id] += amount
    self.usage[feature_id] += amount
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    return self.usage[feature_id]
    return self.usage[feature_id]


    def reset_feature_usage(self, feature_id: str) -> None:
    def reset_feature_usage(self, feature_id: str) -> None:
    """
    """
    Reset the usage of a feature for this subscription.
    Reset the usage of a feature for this subscription.


    Args:
    Args:
    feature_id: ID of the feature
    feature_id: ID of the feature
    """
    """
    self.usage[feature_id] = 0
    self.usage[feature_id] = 0
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def reset_all_usage(self) -> None:
    def reset_all_usage(self) -> None:
    """Reset the usage of all features for this subscription."""
    self.usage = {}
    self.updated_at = datetime.now()

    def is_feature_limit_reached(self, feature_id: str) -> bool:
    """
    """
    Check if the usage of a feature has reached its limit.
    Check if the usage of a feature has reached its limit.


    Args:
    Args:
    feature_id: ID of the feature
    feature_id: ID of the feature


    Returns:
    Returns:
    True if the limit is reached, False otherwise
    True if the limit is reached, False otherwise
    """
    """
    limit = self.get_feature_limit(feature_id)
    limit = self.get_feature_limit(feature_id)


    if limit is None:
    if limit is None:
    return False
    return False


    usage = self.get_feature_usage(feature_id)
    usage = self.get_feature_usage(feature_id)


    return usage >= limit
    return usage >= limit


    def get_remaining_feature_usage(self, feature_id: str) -> Optional[int]:
    def get_remaining_feature_usage(self, feature_id: str) -> Optional[int]:
    """
    """
    Get the remaining usage of a feature for this subscription.
    Get the remaining usage of a feature for this subscription.


    Args:
    Args:
    feature_id: ID of the feature
    feature_id: ID of the feature


    Returns:
    Returns:
    Remaining usage of the feature or None if no limit
    Remaining usage of the feature or None if no limit
    """
    """
    limit = self.get_feature_limit(feature_id)
    limit = self.get_feature_limit(feature_id)


    if limit is None:
    if limit is None:
    return None
    return None


    usage = self.get_feature_usage(feature_id)
    usage = self.get_feature_usage(feature_id)


    return max(0, limit - usage)
    return max(0, limit - usage)


    def is_active(self) -> bool:
    def is_active(self) -> bool:
    """
    """
    Check if the subscription is active.
    Check if the subscription is active.


    Returns:
    Returns:
    True if the subscription is active, False otherwise
    True if the subscription is active, False otherwise
    """
    """
    return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]
    return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]


    def is_trial(self) -> bool:
    def is_trial(self) -> bool:
    """
    """
    Check if the subscription is in trial period.
    Check if the subscription is in trial period.


    Returns:
    Returns:
    True if the subscription is in trial period, False otherwise
    True if the subscription is in trial period, False otherwise
    """
    """
    return self.status == SubscriptionStatus.TRIAL
    return self.status == SubscriptionStatus.TRIAL


    def is_canceled(self) -> bool:
    def is_canceled(self) -> bool:
    """
    """
    Check if the subscription is canceled.
    Check if the subscription is canceled.


    Returns:
    Returns:
    True if the subscription is canceled, False otherwise
    True if the subscription is canceled, False otherwise
    """
    """
    return self.status == SubscriptionStatus.CANCELED
    return self.status == SubscriptionStatus.CANCELED


    def is_expired(self) -> bool:
    def is_expired(self) -> bool:
    """
    """
    Check if the subscription is expired.
    Check if the subscription is expired.


    Returns:
    Returns:
    True if the subscription is expired, False otherwise
    True if the subscription is expired, False otherwise
    """
    """
    return self.status == SubscriptionStatus.EXPIRED
    return self.status == SubscriptionStatus.EXPIRED


    def is_past_due(self) -> bool:
    def is_past_due(self) -> bool:
    """
    """
    Check if the subscription is past due.
    Check if the subscription is past due.


    Returns:
    Returns:
    True if the subscription is past due, False otherwise
    True if the subscription is past due, False otherwise
    """
    """
    return self.status == SubscriptionStatus.PAST_DUE
    return self.status == SubscriptionStatus.PAST_DUE


    def is_unpaid(self) -> bool:
    def is_unpaid(self) -> bool:
    """
    """
    Check if the subscription is unpaid.
    Check if the subscription is unpaid.


    Returns:
    Returns:
    True if the subscription is unpaid, False otherwise
    True if the subscription is unpaid, False otherwise
    """
    """
    return self.status == SubscriptionStatus.UNPAID
    return self.status == SubscriptionStatus.UNPAID


    def is_paused(self) -> bool:
    def is_paused(self) -> bool:
    """
    """
    Check if the subscription is paused.
    Check if the subscription is paused.


    Returns:
    Returns:
    True if the subscription is paused, False otherwise
    True if the subscription is paused, False otherwise
    """
    """
    return self.status == SubscriptionStatus.PAUSED
    return self.status == SubscriptionStatus.PAUSED


    def get_days_until_renewal(self) -> int:
    def get_days_until_renewal(self) -> int:
    """
    """
    Get the number of days until the subscription renews.
    Get the number of days until the subscription renews.


    Returns:
    Returns:
    Number of days until renewal
    Number of days until renewal
    """
    """
    now = datetime.now()
    now = datetime.now()


    if now > self.current_period_end:
    if now > self.current_period_end:
    return 0
    return 0


    return (self.current_period_end - now).days
    return (self.current_period_end - now).days


    def get_days_until_trial_end(self) -> Optional[int]:
    def get_days_until_trial_end(self) -> Optional[int]:
    """
    """
    Get the number of days until the trial ends.
    Get the number of days until the trial ends.


    Returns:
    Returns:
    Number of days until trial end or None if not in trial
    Number of days until trial end or None if not in trial
    """
    """
    if not self.is_trial() or not self.trial_end_date:
    if not self.is_trial() or not self.trial_end_date:
    return None
    return None


    now = datetime.now()
    now = datetime.now()


    if now > self.trial_end_date:
    if now > self.trial_end_date:
    return 0
    return 0


    return (self.trial_end_date - now).days
    return (self.trial_end_date - now).days


    def get_days_since_start(self) -> int:
    def get_days_since_start(self) -> int:
    """
    """
    Get the number of days since the subscription started.
    Get the number of days since the subscription started.


    Returns:
    Returns:
    Number of days since start
    Number of days since start
    """
    """
    now = datetime.now()
    now = datetime.now()
    return (now - self.start_date).days
    return (now - self.start_date).days


    def get_subscription_age_months(self) -> float:
    def get_subscription_age_months(self) -> float:
    """
    """
    Get the age of the subscription in months.
    Get the age of the subscription in months.


    Returns:
    Returns:
    Age of the subscription in months
    Age of the subscription in months
    """
    """
    now = datetime.now()
    now = datetime.now()
    days = (now - self.start_date).days
    days = (now - self.start_date).days
    return days / 30.0
    return days / 30.0


    def get_status_history(self) -> List[Dict[str, Any]]:
    def get_status_history(self) -> List[Dict[str, Any]]:
    """
    """
    Get the status history of the subscription.
    Get the status history of the subscription.


    Returns:
    Returns:
    List of status changes with timestamps and reasons
    List of status changes with timestamps and reasons
    """
    """
    return self.status_history
    return self.status_history


    def add_metadata(self, key: str, value: Any) -> None:
    def add_metadata(self, key: str, value: Any) -> None:
    """
    """
    Add metadata to the subscription.
    Add metadata to the subscription.


    Args:
    Args:
    key: Metadata key
    key: Metadata key
    value: Metadata value
    value: Metadata value
    """
    """
    self.metadata[key] = value
    self.metadata[key] = value
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def get_metadata(self, key: str, default: Any = None) -> Any:
    def get_metadata(self, key: str, default: Any = None) -> Any:
    """
    """
    Get metadata from the subscription.
    Get metadata from the subscription.


    Args:
    Args:
    key: Metadata key
    key: Metadata key
    default: Default value if key not found
    default: Default value if key not found


    Returns:
    Returns:
    Metadata value or default
    Metadata value or default
    """
    """
    return self.metadata.get(key, default)
    return self.metadata.get(key, default)


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the subscription to a dictionary.
    Convert the subscription to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the subscription
    Dictionary representation of the subscription
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "user_id": self.user_id,
    "user_id": self.user_id,
    "plan_id": self.plan_id,
    "plan_id": self.plan_id,
    "tier_id": self.tier_id,
    "tier_id": self.tier_id,
    "billing_cycle": self.billing_cycle,
    "billing_cycle": self.billing_cycle,
    "start_date": self.start_date.isoformat(),
    "start_date": self.start_date.isoformat(),
    "end_date": self.end_date.isoformat(),
    "end_date": self.end_date.isoformat(),
    "status": self.status,
    "status": self.status,
    "trial_end_date": (
    "trial_end_date": (
    self.trial_end_date.isoformat() if self.trial_end_date else None
    self.trial_end_date.isoformat() if self.trial_end_date else None
    ),
    ),
    "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
    "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
    "current_period_start": self.current_period_start.isoformat(),
    "current_period_start": self.current_period_start.isoformat(),
    "current_period_end": self.current_period_end.isoformat(),
    "current_period_end": self.current_period_end.isoformat(),
    "price": self.price,
    "price": self.price,
    "usage": self.usage,
    "usage": self.usage,
    "metadata": self.metadata,
    "metadata": self.metadata,
    "status_history": self.status_history,
    "status_history": self.status_history,
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
    Convert the subscription to a JSON string.
    Convert the subscription to a JSON string.


    Args:
    Args:
    indent: Number of spaces for indentation
    indent: Number of spaces for indentation


    Returns:
    Returns:
    JSON string representation of the subscription
    JSON string representation of the subscription
    """
    """
    return json.dumps(self.to_dict(), indent=indent)
    return json.dumps(self.to_dict(), indent=indent)


    def save_to_file(self, file_path: str) -> None:
    def save_to_file(self, file_path: str) -> None:
    """
    """
    Save the subscription to a JSON file.
    Save the subscription to a JSON file.


    Args:
    Args:
    file_path: Path to save the file
    file_path: Path to save the file
    """
    """
    with open(file_path, "w") as f:
    with open(file_path, "w") as f:
    f.write(self.to_json())
    f.write(self.to_json())


    @classmethod
    @classmethod
    def load_from_dict(
    def load_from_dict(
    cls, data: Dict[str, Any], plan: SubscriptionPlan
    cls, data: Dict[str, Any], plan: SubscriptionPlan
    ) -> "Subscription":
    ) -> "Subscription":
    """
    """
    Load a subscription from a dictionary.
    Load a subscription from a dictionary.


    Args:
    Args:
    data: Dictionary with subscription data
    data: Dictionary with subscription data
    plan: Subscription plan
    plan: Subscription plan


    Returns:
    Returns:
    Subscription instance
    Subscription instance
    """
    """
    # Create subscription with required fields
    # Create subscription with required fields
    subscription = cls(
    subscription = cls(
    user_id=data["user_id"],
    user_id=data["user_id"],
    plan=plan,
    plan=plan,
    tier_id=data["tier_id"],
    tier_id=data["tier_id"],
    billing_cycle=data["billing_cycle"],
    billing_cycle=data["billing_cycle"],
    start_date=datetime.fromisoformat(data["start_date"]),
    start_date=datetime.fromisoformat(data["start_date"]),
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    # Set additional fields
    # Set additional fields
    subscription.id = data["id"]
    subscription.id = data["id"]
    subscription.status = data["status"]
    subscription.status = data["status"]
    subscription.end_date = datetime.fromisoformat(data["end_date"])
    subscription.end_date = datetime.fromisoformat(data["end_date"])


    if data.get("trial_end_date"):
    if data.get("trial_end_date"):
    subscription.trial_end_date = datetime.fromisoformat(data["trial_end_date"])
    subscription.trial_end_date = datetime.fromisoformat(data["trial_end_date"])


    if data.get("canceled_at"):
    if data.get("canceled_at"):
    subscription.canceled_at = datetime.fromisoformat(data["canceled_at"])
    subscription.canceled_at = datetime.fromisoformat(data["canceled_at"])


    subscription.current_period_start = datetime.fromisoformat(
    subscription.current_period_start = datetime.fromisoformat(
    data["current_period_start"]
    data["current_period_start"]
    )
    )
    subscription.current_period_end = datetime.fromisoformat(
    subscription.current_period_end = datetime.fromisoformat(
    data["current_period_end"]
    data["current_period_end"]
    )
    )
    subscription.price = data["price"]
    subscription.price = data["price"]
    subscription.usage = data.get("usage", {})
    subscription.usage = data.get("usage", {})
    subscription.status_history = data.get("status_history", [])
    subscription.status_history = data.get("status_history", [])
    subscription.created_at = datetime.fromisoformat(data["created_at"])
    subscription.created_at = datetime.fromisoformat(data["created_at"])
    subscription.updated_at = datetime.fromisoformat(data["updated_at"])
    subscription.updated_at = datetime.fromisoformat(data["updated_at"])


    return subscription
    return subscription


    @classmethod
    @classmethod
    def load_from_file(cls, file_path: str, plan: SubscriptionPlan) -> "Subscription":
    def load_from_file(cls, file_path: str, plan: SubscriptionPlan) -> "Subscription":
    """
    """
    Load a subscription from a JSON file.
    Load a subscription from a JSON file.


    Args:
    Args:
    file_path: Path to the JSON file
    file_path: Path to the JSON file
    plan: Subscription plan
    plan: Subscription plan


    Returns:
    Returns:
    Subscription instance
    Subscription instance
    """
    """
    with open(file_path, "r") as f:
    with open(file_path, "r") as f:
    data = json.load(f)
    data = json.load(f)


    return cls.load_from_dict(data, plan)
    return cls.load_from_dict(data, plan)


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the subscription."""
    tier = self.get_tier()
    return f"Subscription({self.user_id}, {tier['name']}, {self.status})"

    def __repr__(self) -> str:
    """Detailed string representation of the subscription."""
    tier = self.get_tier()
    return f"Subscription(id={self.id}, user_id={self.user_id}, tier={tier['name']}, status={self.status})"


    # Example usage
    if __name__ == "__main__":
    # Create a subscription plan
    plan = SubscriptionPlan(
    name="AI Tool Subscription",
    description="Subscription plan for an AI-powered tool",
    )

    # Add features
    feature1 = plan.add_feature(
    name="Content Generation",
    description="Generate content using AI",
    type="quantity",
    category="core",
    )

    feature2 = plan.add_feature(
    name="API Access",
    description="Access to the API",
    type="boolean",
    category="integration",
    )

    # Add tiers
    basic_tier = plan.add_tier(
    name="Basic",
    description="Essential features for individuals",
    price_monthly=9.99,
    trial_days=14,
    )

    # Create a subscription
    user_id = "user123"
    subscription = Subscription(
    user_id=user_id, plan=plan, tier_id=basic_tier["id"], billing_cycle="monthly"
    )

    print(f"Subscription: {subscription}")
    print(f"Status: {subscription.status}")
    print(f"Price: ${subscription.price:.2f}/{subscription.billing_cycle}")

    if subscription.is_trial():
    days_left = subscription.get_days_until_trial_end()
    print(f"Trial ends in {days_left} days")

    # Check features
    print("\nFeatures:")
    for feature in subscription.get_features():
    limit_str = f" (Limit: {feature.get('limit')})" if "limit" in feature else ""
    print(f"- {feature['name']}: {feature['value']}{limit_str}")

    # Track usage
    subscription.increment_feature_usage(feature1["id"], 5)
    print(
    f"\nContent Generation usage: {subscription.get_feature_usage(feature1['id'])}"
    )
    print(f"Remaining: {subscription.get_remaining_feature_usage(feature1['id'])}")

    # Add metadata
    subscription.add_metadata("referral_source", "website")
    print(f"\nReferral source: {subscription.get_metadata('referral_source')}")

    # Convert to dictionary
    subscription_dict = subscription.to_dict()
    print(f"\nSubscription ID: {subscription_dict['id']}")
    print(f"Created at: {subscription_dict['created_at']}")