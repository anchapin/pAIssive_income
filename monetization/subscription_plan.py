"""
Subscription plans for the pAIssive Income project.

This module provides classes for defining and managing subscription plans,
including features, pricing, and billing intervals.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional



class BillingInterval:
    """Enumeration of billing intervals."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PlanFeature:
    """
    Class representing a feature in a subscription plan.

    This class provides a structured way to represent a feature in a subscription plan,
    including the feature name, description, and limits.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        included: bool = True,
        limit: Optional[float] = None,
        metric: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a plan feature.

        Args:
            name: Name of the feature
            description: Description of the feature
            included: Whether the feature is included in the plan
            limit: Usage limit for the feature (if applicable)
            metric: Metric for the usage limit (if applicable)
            metadata: Additional metadata for the feature
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.included = included
        self.limit = limit
        self.metric = metric
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the plan feature to a dictionary.

        Returns:
            Dictionary representation of the plan feature
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "included": self.included,
            "limit": self.limit,
            "metric": self.metric,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanFeature":
        """
        Create a plan feature from a dictionary.

        Args:
            data: Dictionary with plan feature data

        Returns:
            PlanFeature instance
        """
        feature = cls(
            name=data["name"],
            description=data.get("description", ""),
            included=data.get("included", True),
            limit=data.get("limit"),
            metric=data.get("metric"),
            metadata=data.get("metadata", {}),
        )

        feature.id = data["id"]

        return feature

    def __str__(self) -> str:
        """String representation of the plan feature."""
        if not self.included:
            return f"{self.name}: Not included"

        if self.limit is not None and self.metric:
            return f"{self.name}: {self.limit} {self.metric}"

        return f"{self.name}: Included"


class SubscriptionPlan:
    """
    Class representing a subscription plan.

    This class provides a structured way to represent a subscription plan,
    including the plan name, description, pricing, and features.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        price: float = 0.0,
        currency: str = "USD",
        billing_interval: str = BillingInterval.MONTHLY,
        features: Optional[List[PlanFeature]] = None,
        trial_days: int = 0,
        is_active: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a subscription plan.

        Args:
            name: Name of the plan
            description: Description of the plan
            price: Price of the plan
            currency: Currency code (e.g., USD)
            billing_interval: Billing interval (e.g., MONTHLY)
            features: List of plan features
            trial_days: Number of trial days
            is_active: Whether the plan is active
            metadata: Additional metadata for the plan
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.price = price
        self.currency = currency
        self.billing_interval = billing_interval
        self.features = features or []
        self.trial_days = trial_days
        self.is_active = is_active
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def add_feature(
        self,
        name: str,
        description: str = "",
        included: bool = True,
        limit: Optional[float] = None,
        metric: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PlanFeature:
        """
        Add a feature to the plan.

        Args:
            name: Name of the feature
            description: Description of the feature
            included: Whether the feature is included in the plan
            limit: Usage limit for the feature (if applicable)
            metric: Metric for the usage limit (if applicable)
            metadata: Additional metadata for the feature

        Returns:
            The created plan feature
        """
        feature = PlanFeature(
            name=name,
            description=description,
            included=included,
            limit=limit,
            metric=metric,
            metadata=metadata,
        )

        self.features.append(feature)
        self.updated_at = datetime.now()

        return feature

    def remove_feature(self, feature_id: str) -> bool:
        """
        Remove a feature from the plan.

        Args:
            feature_id: ID of the feature to remove

        Returns:
            True if the feature was removed, False otherwise
        """
        for i, feature in enumerate(self.features):
            if feature.id == feature_id:
                self.features.pop(i)
                self.updated_at = datetime.now()
                return True

        return False

    def get_feature(self, feature_id: str) -> Optional[PlanFeature]:
        """
        Get a feature from the plan.

        Args:
            feature_id: ID of the feature

        Returns:
            The plan feature or None if not found
        """
        for feature in self.features:
            if feature.id == feature_id:
                return feature

        return None

    def get_feature_by_name(self, name: str) -> Optional[PlanFeature]:
        """
        Get a feature from the plan by name.

        Args:
            name: Name of the feature

        Returns:
            The plan feature or None if not found
        """
        for feature in self.features:
            if feature.name == name:
                return feature

        return None

    def has_feature(self, name: str) -> bool:
        """
        Check if the plan has a feature.

        Args:
            name: Name of the feature

        Returns:
            True if the plan has the feature, False otherwise
        """
        feature = self.get_feature_by_name(name)
        return feature is not None and feature.included

    def get_feature_limit(self, name: str) -> Optional[float]:
        """
        Get the limit for a feature.

        Args:
            name: Name of the feature

        Returns:
            The feature limit or None if the feature is not found or has no limit
        """
        feature = self.get_feature_by_name(name)

        if feature and feature.included and feature.limit is not None:
            return feature.limit

        return None

    def format_price(self) -> str:
        """
        Format the price with currency symbol.

        Returns:
            Formatted price with currency symbol
        """
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CAD": "C$",
            "AUD": "A$",
        }

        symbol = currency_symbols.get(self.currency, self.currency)

        if self.currency == "JPY":
            # JPY doesn't use decimal places
            return f"{symbol}{int(self.price):,}"
        else:
            return f"{symbol}{self.price:,.2f}"

    def get_billing_interval_days(self) -> int:
        """
        Get the number of days in the billing interval.

        Returns:
            Number of days in the billing interval
        """
        if self.billing_interval == BillingInterval.DAILY:
            return 1
        elif self.billing_interval == BillingInterval.WEEKLY:
            return 7
        elif self.billing_interval == BillingInterval.MONTHLY:
            return 30  # Approximate
        elif self.billing_interval == BillingInterval.QUARTERLY:
            return 90  # Approximate
        elif self.billing_interval == BillingInterval.YEARLY:
            return 365  # Approximate
        else:
            return 30  # Default to monthly

    def get_price_per_day(self) -> float:
        """
        Get the price per day.

        Returns:
            Price per day
        """
        days = self.get_billing_interval_days()

        if days <= 0:
            return 0.0

        return self.price / days

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the subscription plan to a dictionary.

        Returns:
            Dictionary representation of the subscription plan
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "currency": self.currency,
            "billing_interval": self.billing_interval,
            "features": [feature.to_dict() for feature in self.features],
            "trial_days": self.trial_days,
            "is_active": self.is_active,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the subscription plan to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the subscription plan
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubscriptionPlan":
        """
        Create a subscription plan from a dictionary.

        Args:
            data: Dictionary with subscription plan data

        Returns:
            SubscriptionPlan instance
        """
        # Create plan
        plan = cls(
            name=data["name"],
            description=data.get("description", ""),
            price=data["price"],
            currency=data.get("currency", "USD"),
            billing_interval=data.get("billing_interval", BillingInterval.MONTHLY),
            trial_days=data.get("trial_days", 0),
            is_active=data.get("is_active", True),
            metadata=data.get("metadata", {}),
        )

        # Set plan ID
        plan.id = data["id"]

        # Add features
        for feature_data in data.get("features", []):
            feature = PlanFeature.from_dict(feature_data)
            plan.features.append(feature)

        # Set timestamps
        plan.created_at = datetime.fromisoformat(data["created_at"])
        plan.updated_at = datetime.fromisoformat(data["updated_at"])

        return plan

    def __str__(self) -> str:
        """String representation of the subscription plan."""
        return f"{self.name}: {self.format_price()}/{self.billing_interval}"


class SubscriptionStatus:
    """Enumeration of subscription statuses."""

    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    CANCELED = "canceled"
    EXPIRED = "expired"
    PAUSED = "paused"


class Subscription:
    """
    Class representing a subscription.

    This class provides a structured way to represent a subscription,
    including the subscription plan, customer, and status.
    """

    def __init__(
        self,
        customer_id: str,
        plan_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: str = SubscriptionStatus.ACTIVE,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a subscription.

        Args:
            customer_id: ID of the customer
            plan_id: ID of the subscription plan
            start_date: Start date of the subscription
            end_date: End date of the subscription
            status: Status of the subscription
            metadata: Additional metadata for the subscription
        """
        self.id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.plan_id = plan_id
        self.start_date = start_date or datetime.now()
        self.end_date = end_date
        self.status = status
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = self.created_at

        # Initialize other properties
        self.canceled_at = None
        self.trial_end = None
        self.current_period_start = self.start_date
        self.current_period_end = None
        self.next_billing_date = None
        self.pause_collection = False
        self.pause_reason = None
        self.resume_at = None
        self.status_history = [
            {
                "status": self.status,
                "timestamp": self.created_at.isoformat(),
                "reason": "Subscription created",
            }
        ]
        self.invoices = []
        self.usage_records = []

    def update_status(self, status: str, reason: Optional[str] = None) -> None:
        """
        Update the status of the subscription.

        Args:
            status: New status
            reason: Reason for the status change
        """
        old_status = self.status
        self.status = status
        self.updated_at = datetime.now()

        # Add status history entry
        self.status_history.append(
            {
                "status": status,
                "timestamp": self.updated_at.isoformat(),
                "reason": reason or f"Status changed from {old_status} to {status}",
            }
        )

        # Update other properties based on status
        if status == SubscriptionStatus.CANCELED:
            self.canceled_at = self.updated_at
        elif status == SubscriptionStatus.PAUSED:
            self.pause_collection = True
            self.pause_reason = reason

    def cancel(self, reason: Optional[str] = None) -> None:
        """
        Cancel the subscription.

        Args:
            reason: Reason for cancellation
        """
        self.update_status(SubscriptionStatus.CANCELED, reason or "Subscription canceled")

    def pause(self, reason: Optional[str] = None, resume_at: Optional[datetime] = None) -> None:
        """
        Pause the subscription.

        Args:
            reason: Reason for pausing
            resume_at: Date to resume the subscription
        """
        self.update_status(SubscriptionStatus.PAUSED, reason or "Subscription paused")
        self.resume_at = resume_at

    def resume(self, reason: Optional[str] = None) -> None:
        """
        Resume the subscription.

        Args:
            reason: Reason for resuming
        """
        self.update_status(SubscriptionStatus.ACTIVE, reason or "Subscription resumed")
        self.pause_collection = False
        self.pause_reason = None
        self.resume_at = None

    def set_trial_end(self, trial_end: datetime) -> None:
        """
        Set the trial end date.

        Args:
            trial_end: Trial end date
        """
        self.trial_end = trial_end

        if self.status == SubscriptionStatus.ACTIVE:
            self.update_status(SubscriptionStatus.TRIALING, "Trial started")

    def set_current_period(self, start: datetime, end: datetime) -> None:
        """
        Set the current billing period.

        Args:
            start: Start date of the period
            end: End date of the period
        """
        self.current_period_start = start
        self.current_period_end = end
        self.next_billing_date = end

    def add_invoice(self, invoice_id: str) -> None:
        """
        Add an invoice to the subscription.

        Args:
            invoice_id: ID of the invoice
        """
        self.invoices.append(invoice_id)

    def add_usage_record(self, record_id: str) -> None:
        """
        Add a usage record to the subscription.

        Args:
            record_id: ID of the usage record
        """
        self.usage_records.append(record_id)

    def is_active(self) -> bool:
        """
        Check if the subscription is active.

        Returns:
            True if the subscription is active, False otherwise
        """
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]

    def is_trialing(self) -> bool:
        """
        Check if the subscription is in trial.

        Returns:
            True if the subscription is in trial, False otherwise
        """
        return self.status == SubscriptionStatus.TRIALING

    def is_canceled(self) -> bool:
        """
        Check if the subscription is canceled.

        Returns:
            True if the subscription is canceled, False otherwise
        """
        return self.status == SubscriptionStatus.CANCELED

    def is_past_due(self) -> bool:
        """
        Check if the subscription is past due.

        Returns:
            True if the subscription is past due, False otherwise
        """
        return self.status == SubscriptionStatus.PAST_DUE

    def is_paused(self) -> bool:
        """
        Check if the subscription is paused.

        Returns:
            True if the subscription is paused, False otherwise
        """
        return self.status == SubscriptionStatus.PAUSED

    def get_days_until_next_billing(self) -> Optional[int]:
        """
        Get the number of days until the next billing date.

        Returns:
            Number of days until the next billing date or None if not applicable
        """
        if not self.next_billing_date:
            return None

        days = (self.next_billing_date - datetime.now()).days
        return max(0, days)

    def get_days_in_current_period(self) -> Optional[int]:
        """
        Get the number of days in the current billing period.

        Returns:
            Number of days in the current billing period or None if not applicable
        """
        if not self.current_period_start or not self.current_period_end:
            return None

        return (self.current_period_end - self.current_period_start).days

    def get_days_remaining_in_current_period(self) -> Optional[int]:
        """
        Get the number of days remaining in the current billing period.

        Returns:
            Number of days remaining in the current billing period or None if not applicable
        """
        if not self.current_period_end:
            return None

        days = (self.current_period_end - datetime.now()).days
        return max(0, days)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the subscription to a dictionary.

        Returns:
            Dictionary representation of the subscription
        """
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "plan_id": self.plan_id,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
            "trial_end": self.trial_end.isoformat() if self.trial_end else None,
            "current_period_start": self.current_period_start.isoformat(),
            "current_period_end": (
                self.current_period_end.isoformat() if self.current_period_end else None
            ),
            "next_billing_date": (
                self.next_billing_date.isoformat() if self.next_billing_date else None
            ),
            "pause_collection": self.pause_collection,
            "pause_reason": self.pause_reason,
            "resume_at": self.resume_at.isoformat() if self.resume_at else None,
            "status_history": self.status_history,
            "invoices": self.invoices,
            "usage_records": self.usage_records,
            "metadata": self.metadata,
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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Subscription":
        """
        Create a subscription from a dictionary.

        Args:
            data: Dictionary with subscription data

        Returns:
            Subscription instance
        """
        # Create subscription
        subscription = cls(
            customer_id=data["customer_id"],
            plan_id=data["plan_id"],
            start_date=datetime.fromisoformat(data["start_date"]),
            end_date=(datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None),
            status=data["status"],
            metadata=data.get("metadata", {}),
        )

        # Set subscription ID
        subscription.id = data["id"]

        # Set timestamps
        subscription.created_at = datetime.fromisoformat(data["created_at"])
        subscription.updated_at = datetime.fromisoformat(data["updated_at"])
        subscription.canceled_at = (
            datetime.fromisoformat(data["canceled_at"]) if data.get("canceled_at") else None
        )
        subscription.trial_end = (
            datetime.fromisoformat(data["trial_end"]) if data.get("trial_end") else None
        )
        subscription.current_period_start = datetime.fromisoformat(data["current_period_start"])
        subscription.current_period_end = (
            datetime.fromisoformat(data["current_period_end"])
            if data.get("current_period_end")
            else None
        )
        subscription.next_billing_date = (
            datetime.fromisoformat(data["next_billing_date"])
            if data.get("next_billing_date")
            else None
        )
        subscription.resume_at = (
            datetime.fromisoformat(data["resume_at"]) if data.get("resume_at") else None
        )

        # Set other properties
        subscription.pause_collection = data.get("pause_collection", False)
        subscription.pause_reason = data.get("pause_reason")
        subscription.status_history = data.get("status_history", [])
        subscription.invoices = data.get("invoices", [])
        subscription.usage_records = data.get("usage_records", [])

        return subscription

    def __str__(self) -> str:
        """String representation of the subscription."""
        return f"Subscription({self.id}, {self.customer_id}, {self.plan_id}, {self.status})"


# Example usage
if __name__ == "__main__":
    # Create a subscription plan
    plan = SubscriptionPlan(
        name="Basic Plan",
        description="Basic subscription plan",
        price=9.99,
        currency="USD",
        billing_interval=BillingInterval.MONTHLY,
        trial_days=14,
    )

    # Add features
    plan.add_feature(
        name="API Calls",
        description="Number of API calls per month",
        limit=1000,
        metric="calls",
    )

    plan.add_feature(name="Storage", description="Storage space", limit=5, metric="GB")

    plan.add_feature(name="Advanced Analytics", included=False)

    print(f"Plan: {plan}")
    print(f"Price: {plan.format_price()}/{plan.billing_interval}")
    print(f"Trial days: {plan.trial_days}")

    print("\nFeatures:")
    for feature in plan.features:
        print(f"- {feature}")

    # Create a subscription
    subscription = Subscription(
        customer_id="cust_123", plan_id=plan.id, status=SubscriptionStatus.TRIALING
    )

    # Set trial end date
    trial_end = datetime.now() + timedelta(days=plan.trial_days)
    subscription.set_trial_end(trial_end)

    # Set current period
    period_end = datetime.now() + timedelta(days=30)
    subscription.set_current_period(datetime.now(), period_end)

    print(f"\nSubscription: {subscription}")
    print(f"Status: {subscription.status}")
    print(
        f"Trial end: {subscription.trial_end.strftime('%Y-%m-%d') if subscription.trial_end else 'N/A'}"
    )
    print(
        f"Current period: {subscription.current_period_start.strftime('%Y-%m-%d')} to {subscription.current_period_end.strftime('%Y-%m-%d') if subscription.current_period_end else 'N/A'}"
    )
    print(
        f"Next billing date: {subscription.next_billing_date.strftime('%Y-%m-%d') if subscription.next_billing_date else 'N/A'}"
    )
    print(f"Days until next billing: {subscription.get_days_until_next_billing()}")

    # Cancel subscription
    subscription.cancel("Customer requested cancellation")

    print(f"\nAfter cancellation:")
    print(f"Status: {subscription.status}")
    print(
        f"Canceled at: {subscription.canceled_at.strftime('%Y-%m-%d %H:%M:%S') if subscription.canceled_at else 'N/A'}"
    )

    # Convert to dictionary and back
    plan_dict = plan.to_dict()
    restored_plan = SubscriptionPlan.from_dict(plan_dict)

    print(f"\nRestored plan: {restored_plan}")
    print(f"Is same ID: {restored_plan.id == plan.id}")

    subscription_dict = subscription.to_dict()
    restored_subscription = Subscription.from_dict(subscription_dict)

    print(f"\nRestored subscription: {restored_subscription}")
    print(f"Is same ID: {restored_subscription.id == subscription.id}")
