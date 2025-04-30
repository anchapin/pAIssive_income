"""
User subscription management for the pAIssive Income project.

This module provides classes for managing user subscriptions, including
subscription creation, renewal, cancellation, and status tracking.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import uuid
import json
import copy

from .subscription import SubscriptionPlan, SubscriptionTier


class SubscriptionStatus:
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
    Class for managing user subscriptions.

    A subscription represents a user's subscription to a specific plan and tier,
    including status, billing information, and usage data.
    """

    def __init__(
        self,
        user_id: str,
        plan: SubscriptionPlan,
        tier_id: str,
        billing_cycle: str = "monthly",
        start_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a subscription.

        Args:
            user_id: ID of the user
            plan: Subscription plan
            tier_id: ID of the subscription tier
            billing_cycle: Billing cycle (monthly, annual)
            start_date: Start date of the subscription
            metadata: Additional metadata for the subscription
        """
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.plan_id = plan.id
        self.plan = plan
        self.tier_id = tier_id

        # Validate tier exists in plan
        tier = plan.get_tier(tier_id)
        if not tier:
            raise ValueError(f"Tier with ID {tier_id} not found in plan {plan.name}")

        # Validate billing cycle
        if billing_cycle not in plan.billing_cycles:
            raise ValueError(
                f"Invalid billing cycle: {billing_cycle}. Valid options: {plan.billing_cycles}"
            )

        self.billing_cycle = billing_cycle
        self.start_date = start_date or datetime.now()

        # Calculate end date based on billing cycle
        if billing_cycle == "monthly":
            self.end_date = self.start_date + timedelta(days=30)
        elif billing_cycle == "annual":
            self.end_date = self.start_date + timedelta(days=365)
        else:
            # Default to monthly
            self.end_date = self.start_date + timedelta(days=30)

        # Set initial status
        self.status = SubscriptionStatus.ACTIVE

        # Check if tier has trial days
        if tier.get("trial_days", 0) > 0:
            self.status = SubscriptionStatus.TRIAL
            self.trial_end_date = self.start_date + timedelta(
                days=tier.get("trial_days", 0)
            )
        else:
            self.trial_end_date = None

        # Initialize other properties
        self.canceled_at = None
        self.current_period_start = self.start_date
        self.current_period_end = self.end_date
        self.metadata = metadata or {}
        self.status_history = [
            {
                "status": self.status,
                "timestamp": self.start_date.isoformat(),
                "reason": "Subscription created",
            }
        ]

        # Calculate price based on tier and billing cycle
        if billing_cycle == "monthly":
            self.price = tier["price_monthly"]
        elif billing_cycle == "annual":
            self.price = tier["price_annual"]
        else:
            self.price = tier["price_monthly"]

        # Initialize usage data
        self.usage = {}

        # Set timestamps
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    @property
    def tier_name(self) -> str:
        """
        Get the name of the subscription tier.

        Returns:
            Name of the subscription tier
        """
        tier = self.get_tier()
        if tier:
            if isinstance(tier, dict):
                return tier.get("name", "Unknown")
            return getattr(tier, "name", "Unknown")
        return "Unknown"

    def get_tier(self) -> Dict[str, Any]:
        """
        Get the subscription tier.

        Returns:
            The subscription tier
        """
        return self.plan.get_tier(self.tier_id)

    def get_tier_object(self) -> SubscriptionTier:
        """
        Get the subscription tier as a SubscriptionTier object.

        Returns:
            SubscriptionTier object
        """
        return SubscriptionTier(self.plan, self.tier_id)

    def get_features(self) -> List[Dict[str, Any]]:
        """
        Get the features included in this subscription.

        Returns:
            List of features with their details
        """
        return self.plan.get_tier_features(self.tier_id)

    def has_feature(self, feature_id: str) -> bool:
        """
        Check if this subscription has a specific feature.

        Args:
            feature_id: ID of the feature

        Returns:
            True if the subscription has the feature, False otherwise
        """
        tier = self.get_tier()

        for feature in tier["features"]:
            if feature["feature_id"] == feature_id:
                return True

        return False

    def get_feature_value(self, feature_id: str) -> Optional[Any]:
        """
        Get the value of a feature for this subscription.

        Args:
            feature_id: ID of the feature

        Returns:
            Value of the feature or None if not found
        """
        tier = self.get_tier()

        for feature in tier["features"]:
            if feature["feature_id"] == feature_id:
                return feature.get("value", True)

        return None

    def get_feature_limit(self, feature_id: str) -> Optional[int]:
        """
        Get the limit of a feature for this subscription.

        Args:
            feature_id: ID of the feature

        Returns:
            Limit of the feature or None if not found or no limit
        """
        tier = self.get_tier()

        for feature in tier["features"]:
            if feature["feature_id"] == feature_id:
                return feature.get("limit")

        return None

    def get_feature_usage(self, feature_id: str) -> int:
        """
        Get the usage of a feature for this subscription.

        Args:
            feature_id: ID of the feature

        Returns:
            Usage of the feature
        """
        return self.usage.get(feature_id, 0)

    def increment_feature_usage(self, feature_id: str, amount: int = 1) -> int:
        """
        Increment the usage of a feature for this subscription.

        Args:
            feature_id: ID of the feature
            amount: Amount to increment

        Returns:
            New usage of the feature
        """
        if feature_id not in self.usage:
            self.usage[feature_id] = 0

        self.usage[feature_id] += amount
        self.updated_at = datetime.now()

        return self.usage[feature_id]

    def reset_feature_usage(self, feature_id: str) -> None:
        """
        Reset the usage of a feature for this subscription.

        Args:
            feature_id: ID of the feature
        """
        self.usage[feature_id] = 0
        self.updated_at = datetime.now()

    def reset_all_usage(self) -> None:
        """Reset the usage of all features for this subscription."""
        self.usage = {}
        self.updated_at = datetime.now()

    def is_feature_limit_reached(self, feature_id: str) -> bool:
        """
        Check if the usage of a feature has reached its limit.

        Args:
            feature_id: ID of the feature

        Returns:
            True if the limit is reached, False otherwise
        """
        limit = self.get_feature_limit(feature_id)

        if limit is None:
            return False

        usage = self.get_feature_usage(feature_id)

        return usage >= limit

    def get_remaining_feature_usage(self, feature_id: str) -> Optional[int]:
        """
        Get the remaining usage of a feature for this subscription.

        Args:
            feature_id: ID of the feature

        Returns:
            Remaining usage of the feature or None if no limit
        """
        limit = self.get_feature_limit(feature_id)

        if limit is None:
            return None

        usage = self.get_feature_usage(feature_id)

        return max(0, limit - usage)

    def is_active(self) -> bool:
        """
        Check if the subscription is active.

        Returns:
            True if the subscription is active, False otherwise
        """
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]

    def is_trial(self) -> bool:
        """
        Check if the subscription is in trial period.

        Returns:
            True if the subscription is in trial period, False otherwise
        """
        return self.status == SubscriptionStatus.TRIAL

    def is_canceled(self) -> bool:
        """
        Check if the subscription is canceled.

        Returns:
            True if the subscription is canceled, False otherwise
        """
        return self.status == SubscriptionStatus.CANCELED

    def is_expired(self) -> bool:
        """
        Check if the subscription is expired.

        Returns:
            True if the subscription is expired, False otherwise
        """
        return self.status == SubscriptionStatus.EXPIRED

    def is_past_due(self) -> bool:
        """
        Check if the subscription is past due.

        Returns:
            True if the subscription is past due, False otherwise
        """
        return self.status == SubscriptionStatus.PAST_DUE

    def is_unpaid(self) -> bool:
        """
        Check if the subscription is unpaid.

        Returns:
            True if the subscription is unpaid, False otherwise
        """
        return self.status == SubscriptionStatus.UNPAID

    def is_paused(self) -> bool:
        """
        Check if the subscription is paused.

        Returns:
            True if the subscription is paused, False otherwise
        """
        return self.status == SubscriptionStatus.PAUSED

    def get_days_until_renewal(self) -> int:
        """
        Get the number of days until the subscription renews.

        Returns:
            Number of days until renewal
        """
        now = datetime.now()

        if now > self.current_period_end:
            return 0

        return (self.current_period_end - now).days

    def get_days_until_trial_end(self) -> Optional[int]:
        """
        Get the number of days until the trial ends.

        Returns:
            Number of days until trial end or None if not in trial
        """
        if not self.is_trial() or not self.trial_end_date:
            return None

        now = datetime.now()

        if now > self.trial_end_date:
            return 0

        return (self.trial_end_date - now).days

    def get_days_since_start(self) -> int:
        """
        Get the number of days since the subscription started.

        Returns:
            Number of days since start
        """
        now = datetime.now()
        return (now - self.start_date).days

    def get_subscription_age_months(self) -> float:
        """
        Get the age of the subscription in months.

        Returns:
            Age of the subscription in months
        """
        now = datetime.now()
        days = (now - self.start_date).days
        return days / 30.0

    def get_status_history(self) -> List[Dict[str, Any]]:
        """
        Get the status history of the subscription.

        Returns:
            List of status changes with timestamps and reasons
        """
        return self.status_history

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the subscription.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.updated_at = datetime.now()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata from the subscription.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the subscription to a dictionary.

        Returns:
            Dictionary representation of the subscription
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "tier_id": self.tier_id,
            "billing_cycle": self.billing_cycle,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": self.status,
            "trial_end_date": (
                self.trial_end_date.isoformat() if self.trial_end_date else None
            ),
            "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
            "current_period_start": self.current_period_start.isoformat(),
            "current_period_end": self.current_period_end.isoformat(),
            "price": self.price,
            "usage": self.usage,
            "metadata": self.metadata,
            "status_history": self.status_history,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the subscription to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the subscription
        """
        return json.dumps(self.to_dict(), indent=indent)

    def save_to_file(self, file_path: str) -> None:
        """
        Save the subscription to a JSON file.

        Args:
            file_path: Path to save the file
        """
        with open(file_path, "w") as f:
            f.write(self.to_json())

    @classmethod
    def load_from_dict(
        cls, data: Dict[str, Any], plan: SubscriptionPlan
    ) -> "Subscription":
        """
        Load a subscription from a dictionary.

        Args:
            data: Dictionary with subscription data
            plan: Subscription plan

        Returns:
            Subscription instance
        """
        # Create subscription with required fields
        subscription = cls(
            user_id=data["user_id"],
            plan=plan,
            tier_id=data["tier_id"],
            billing_cycle=data["billing_cycle"],
            start_date=datetime.fromisoformat(data["start_date"]),
            metadata=data.get("metadata", {}),
        )

        # Set additional fields
        subscription.id = data["id"]
        subscription.status = data["status"]
        subscription.end_date = datetime.fromisoformat(data["end_date"])

        if data.get("trial_end_date"):
            subscription.trial_end_date = datetime.fromisoformat(data["trial_end_date"])

        if data.get("canceled_at"):
            subscription.canceled_at = datetime.fromisoformat(data["canceled_at"])

        subscription.current_period_start = datetime.fromisoformat(
            data["current_period_start"]
        )
        subscription.current_period_end = datetime.fromisoformat(
            data["current_period_end"]
        )
        subscription.price = data["price"]
        subscription.usage = data.get("usage", {})
        subscription.status_history = data.get("status_history", [])
        subscription.created_at = datetime.fromisoformat(data["created_at"])
        subscription.updated_at = datetime.fromisoformat(data["updated_at"])

        return subscription

    @classmethod
    def load_from_file(cls, file_path: str, plan: SubscriptionPlan) -> "Subscription":
        """
        Load a subscription from a JSON file.

        Args:
            file_path: Path to the JSON file
            plan: Subscription plan

        Returns:
            Subscription instance
        """
        with open(file_path, "r") as f:
            data = json.load(f)

        return cls.load_from_dict(data, plan)

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
    from .subscription import SubscriptionPlan

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
