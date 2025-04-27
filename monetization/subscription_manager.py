"""
Subscription lifecycle management for the pAIssive Income project.

This module provides classes for managing the subscription lifecycle,
including creation, renewal, cancellation, and upgrades/downgrades.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import uuid
import json
import copy
import os

from .subscription import SubscriptionPlan, SubscriptionTier
from .user_subscription import Subscription, SubscriptionStatus


class SubscriptionManager:
    """
    Class for managing subscription lifecycles.
    
    This class provides methods for creating, renewing, canceling, and
    upgrading/downgrading subscriptions.
    """
    
    def __init__(
        self,
        storage_dir: Optional[str] = None,
        plans: Optional[Dict[str, SubscriptionPlan]] = None
    ):
        """
        Initialize a subscription manager.
        
        Args:
            storage_dir: Directory for storing subscription data
            plans: Dictionary of subscription plans
        """
        self.storage_dir = storage_dir
        
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        
        self.plans = plans or {}
        self.subscriptions = {}
        self.events = []
    
    def add_plan(self, plan: SubscriptionPlan) -> None:
        """
        Add a subscription plan.
        
        Args:
            plan: Subscription plan to add
        """
        self.plans[plan.id] = plan
    
    def get_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """
        Get a subscription plan by ID.
        
        Args:
            plan_id: ID of the plan
            
        Returns:
            The subscription plan or None if not found
        """
        return self.plans.get(plan_id)
    
    def list_plans(self) -> List[SubscriptionPlan]:
        """
        List all subscription plans.
        
        Returns:
            List of subscription plans
        """
        return list(self.plans.values())
    
    def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        tier_id: str,
        billing_cycle: str = "monthly",
        start_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        payment_method_id: Optional[str] = None
    ) -> Optional[Subscription]:
        """
        Create a new subscription.
        
        Args:
            user_id: ID of the user
            plan_id: ID of the subscription plan
            tier_id: ID of the subscription tier
            billing_cycle: Billing cycle (monthly, annual)
            start_date: Start date of the subscription
            metadata: Additional metadata for the subscription
            payment_method_id: ID of the payment method
            
        Returns:
            The created subscription or None if plan not found
        """
        # Get the plan
        plan = self.get_plan(plan_id)
        
        if not plan:
            return None
        
        # Create the subscription
        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            tier_id=tier_id,
            billing_cycle=billing_cycle,
            start_date=start_date,
            metadata=metadata or {}
        )
        
        # Add payment method if provided
        if payment_method_id:
            subscription.add_metadata("payment_method_id", payment_method_id)
        
        # Store the subscription
        self.subscriptions[subscription.id] = subscription
        
        # Save the subscription if storage directory is set
        if self.storage_dir:
            self._save_subscription(subscription)
        
        # Record event
        self._record_event(
            event_type="subscription_created",
            subscription_id=subscription.id,
            user_id=user_id,
            plan_id=plan_id,
            tier_id=tier_id,
            billing_cycle=billing_cycle
        )
        
        return subscription
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """
        Get a subscription by ID.
        
        Args:
            subscription_id: ID of the subscription
            
        Returns:
            The subscription or None if not found
        """
        return self.subscriptions.get(subscription_id)
    
    def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """
        Get all subscriptions for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of subscriptions for the user
        """
        return [
            subscription for subscription in self.subscriptions.values()
            if subscription.user_id == user_id
        ]
    
    def get_active_subscription(self, user_id: str, plan_id: Optional[str] = None) -> Optional[Subscription]:
        """
        Get the active subscription for a user.
        
        Args:
            user_id: ID of the user
            plan_id: ID of the plan (optional)
            
        Returns:
            The active subscription or None if not found
        """
        subscriptions = self.get_user_subscriptions(user_id)
        
        for subscription in subscriptions:
            if subscription.is_active():
                if plan_id is None or subscription.plan_id == plan_id:
                    return subscription
        
        return None
    
    def cancel_subscription(
        self,
        subscription_id: str,
        cancel_at_period_end: bool = True,
        reason: Optional[str] = None
    ) -> Optional[Subscription]:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: ID of the subscription
            cancel_at_period_end: Whether to cancel at the end of the billing period
            reason: Reason for cancellation
            
        Returns:
            The updated subscription or None if not found
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            return None
        
        # Set cancellation timestamp
        subscription.canceled_at = datetime.now()
        
        # Update status if not canceling at period end
        if not cancel_at_period_end:
            subscription.status = SubscriptionStatus.CANCELED
            
            # Add status history entry
            subscription.status_history.append({
                "status": subscription.status,
                "timestamp": datetime.now().isoformat(),
                "reason": reason or "Subscription canceled"
            })
        
        # Add cancellation metadata
        subscription.add_metadata("cancel_at_period_end", cancel_at_period_end)
        subscription.add_metadata("cancellation_reason", reason)
        
        # Save the subscription if storage directory is set
        if self.storage_dir:
            self._save_subscription(subscription)
        
        # Record event
        self._record_event(
            event_type="subscription_canceled",
            subscription_id=subscription_id,
            user_id=subscription.user_id,
            cancel_at_period_end=cancel_at_period_end,
            reason=reason
        )
        
        return subscription
    
    def reactivate_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """
        Reactivate a canceled subscription.
        
        Args:
            subscription_id: ID of the subscription
            
        Returns:
            The updated subscription or None if not found or not canceled
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            return None
        
        # Check if subscription is canceled
        if not subscription.is_canceled() and not subscription.get_metadata("cancel_at_period_end"):
            return None
        
        # Clear cancellation data
        subscription.canceled_at = None
        subscription.add_metadata("cancel_at_period_end", False)
        subscription.add_metadata("cancellation_reason", None)
        
        # Restore status to active or trial
        if subscription.trial_end_date and datetime.now() < subscription.trial_end_date:
            subscription.status = SubscriptionStatus.TRIAL
        else:
            subscription.status = SubscriptionStatus.ACTIVE
        
        # Add status history entry
        subscription.status_history.append({
            "status": subscription.status,
            "timestamp": datetime.now().isoformat(),
            "reason": "Subscription reactivated"
        })
        
        # Save the subscription if storage directory is set
        if self.storage_dir:
            self._save_subscription(subscription)
        
        # Record event
        self._record_event(
            event_type="subscription_reactivated",
            subscription_id=subscription_id,
            user_id=subscription.user_id
        )
        
        return subscription
    
    def change_subscription_tier(
        self,
        subscription_id: str,
        new_tier_id: str,
        prorate: bool = True,
        effective_date: Optional[datetime] = None
    ) -> Optional[Subscription]:
        """
        Change the tier of a subscription.
        
        Args:
            subscription_id: ID of the subscription
            new_tier_id: ID of the new tier
            prorate: Whether to prorate the price
            effective_date: Date when the change takes effect
            
        Returns:
            The updated subscription or None if not found
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            return None
        
        # Get the plan
        plan = self.get_plan(subscription.plan_id)
        
        if not plan:
            return None
        
        # Get the new tier
        new_tier = plan.get_tier(new_tier_id)
        
        if not new_tier:
            return None
        
        # Get the old tier
        old_tier = plan.get_tier(subscription.tier_id)
        
        if not old_tier:
            return None
        
        # Set effective date
        if effective_date is None:
            effective_date = datetime.now()
        
        # Calculate price difference for proration
        old_price = subscription.price
        
        if subscription.billing_cycle == "monthly":
            new_price = new_tier["price_monthly"]
        else:
            new_price = new_tier["price_annual"]
        
        price_difference = new_price - old_price
        
        # Calculate prorated amount if needed
        prorated_amount = 0
        
        if prorate and price_difference > 0:
            # Calculate days left in billing period
            days_left = (subscription.current_period_end - effective_date).days
            days_in_period = (subscription.current_period_end - subscription.current_period_start).days
            
            # Calculate prorated amount
            prorated_amount = price_difference * (days_left / days_in_period)
        
        # Update subscription
        old_tier_id = subscription.tier_id
        subscription.tier_id = new_tier_id
        subscription.price = new_price
        
        # Add metadata
        subscription.add_metadata("tier_change", {
            "old_tier_id": old_tier_id,
            "new_tier_id": new_tier_id,
            "effective_date": effective_date.isoformat(),
            "prorate": prorate,
            "prorated_amount": prorated_amount
        })
        
        # Add status history entry
        subscription.status_history.append({
            "status": subscription.status,
            "timestamp": datetime.now().isoformat(),
            "reason": f"Subscription tier changed from {old_tier['name']} to {new_tier['name']}"
        })
        
        # Save the subscription if storage directory is set
        if self.storage_dir:
            self._save_subscription(subscription)
        
        # Record event
        self._record_event(
            event_type="subscription_tier_changed",
            subscription_id=subscription_id,
            user_id=subscription.user_id,
            old_tier_id=old_tier_id,
            new_tier_id=new_tier_id,
            prorate=prorate,
            prorated_amount=prorated_amount
        )
        
        return subscription
    
    def change_billing_cycle(
        self,
        subscription_id: str,
        new_billing_cycle: str,
        prorate: bool = True
    ) -> Optional[Subscription]:
        """
        Change the billing cycle of a subscription.
        
        Args:
            subscription_id: ID of the subscription
            new_billing_cycle: New billing cycle (monthly, annual)
            prorate: Whether to prorate the price
            
        Returns:
            The updated subscription or None if not found
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            return None
        
        # Get the plan
        plan = self.get_plan(subscription.plan_id)
        
        if not plan:
            return None
        
        # Validate billing cycle
        if new_billing_cycle not in plan.billing_cycles:
            return None
        
        # Get the tier
        tier = plan.get_tier(subscription.tier_id)
        
        if not tier:
            return None
        
        # Set effective date
        effective_date = datetime.now()
        
        # Calculate price difference for proration
        old_price = subscription.price
        old_billing_cycle = subscription.billing_cycle
        
        if new_billing_cycle == "monthly":
            new_price = tier["price_monthly"]
            new_period_end = effective_date + timedelta(days=30)
        else:
            new_price = tier["price_annual"]
            new_period_end = effective_date + timedelta(days=365)
        
        # Calculate prorated amount if needed
        prorated_amount = 0
        
        if prorate:
            # Calculate days left in billing period
            days_left = (subscription.current_period_end - effective_date).days
            days_in_period = (subscription.current_period_end - subscription.current_period_start).days
            
            # Calculate prorated amount for remaining days in old cycle
            prorated_amount = old_price * (days_left / days_in_period)
        
        # Update subscription
        subscription.billing_cycle = new_billing_cycle
        subscription.price = new_price
        subscription.current_period_start = effective_date
        subscription.current_period_end = new_period_end
        
        # Add metadata
        subscription.add_metadata("billing_cycle_change", {
            "old_billing_cycle": old_billing_cycle,
            "new_billing_cycle": new_billing_cycle,
            "effective_date": effective_date.isoformat(),
            "prorate": prorate,
            "prorated_amount": prorated_amount
        })
        
        # Add status history entry
        subscription.status_history.append({
            "status": subscription.status,
            "timestamp": datetime.now().isoformat(),
            "reason": f"Billing cycle changed from {old_billing_cycle} to {new_billing_cycle}"
        })
        
        # Save the subscription if storage directory is set
        if self.storage_dir:
            self._save_subscription(subscription)
        
        # Record event
        self._record_event(
            event_type="subscription_billing_cycle_changed",
            subscription_id=subscription_id,
            user_id=subscription.user_id,
            old_billing_cycle=old_billing_cycle,
            new_billing_cycle=new_billing_cycle,
            prorate=prorate,
            prorated_amount=prorated_amount
        )
        
        return subscription
    
    def renew_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """
        Renew a subscription for another billing period.
        
        Args:
            subscription_id: ID of the subscription
            
        Returns:
            The updated subscription or None if not found
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            return None
        
        # Check if subscription is active
        if not subscription.is_active():
            return None
        
        # Check if subscription is set to cancel at period end
        if subscription.canceled_at and subscription.get_metadata("cancel_at_period_end"):
            return None
        
        # Set new period dates
        old_period_end = subscription.current_period_end
        subscription.current_period_start = old_period_end
        
        if subscription.billing_cycle == "monthly":
            subscription.current_period_end = old_period_end + timedelta(days=30)
        else:
            subscription.current_period_end = old_period_end + timedelta(days=365)
        
        # Update end date
        subscription.end_date = subscription.current_period_end
        
        # Ensure status is active (not trial)
        if subscription.status == SubscriptionStatus.TRIAL:
            subscription.status = SubscriptionStatus.ACTIVE
            
            # Add status history entry
            subscription.status_history.append({
                "status": subscription.status,
                "timestamp": datetime.now().isoformat(),
                "reason": "Trial period ended, subscription now active"
            })
        
        # Reset usage if needed
        if subscription.get_metadata("reset_usage_on_renewal", True):
            subscription.reset_all_usage()
        
        # Add metadata
        subscription.add_metadata("last_renewal", datetime.now().isoformat())
        
        # Save the subscription if storage directory is set
        if self.storage_dir:
            self._save_subscription(subscription)
        
        # Record event
        self._record_event(
            event_type="subscription_renewed",
            subscription_id=subscription_id,
            user_id=subscription.user_id,
            new_period_start=subscription.current_period_start.isoformat(),
            new_period_end=subscription.current_period_end.isoformat()
        )
        
        return subscription
    
    def update_subscription_status(
        self,
        subscription_id: str,
        new_status: str,
        reason: Optional[str] = None
    ) -> Optional[Subscription]:
        """
        Update the status of a subscription.
        
        Args:
            subscription_id: ID of the subscription
            new_status: New status
            reason: Reason for the status change
            
        Returns:
            The updated subscription or None if not found
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            return None
        
        # Validate status
        valid_statuses = [
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIAL,
            SubscriptionStatus.PAST_DUE,
            SubscriptionStatus.UNPAID,
            SubscriptionStatus.CANCELED,
            SubscriptionStatus.EXPIRED
        ]
        
        if new_status not in valid_statuses:
            return None
        
        # Update status
        old_status = subscription.status
        subscription.status = new_status
        
        # Add status history entry
        subscription.status_history.append({
            "status": new_status,
            "timestamp": datetime.now().isoformat(),
            "reason": reason or f"Status changed from {old_status} to {new_status}"
        })
        
        # Save the subscription if storage directory is set
        if self.storage_dir:
            self._save_subscription(subscription)
        
        # Record event
        self._record_event(
            event_type="subscription_status_changed",
            subscription_id=subscription_id,
            user_id=subscription.user_id,
            old_status=old_status,
            new_status=new_status,
            reason=reason
        )
        
        return subscription
    
    def check_trial_expirations(self) -> List[Subscription]:
        """
        Check for trial expirations and update subscription statuses.
        
        Returns:
            List of subscriptions that were updated
        """
        updated_subscriptions = []
        now = datetime.now()
        
        for subscription in self.subscriptions.values():
            if (subscription.status == SubscriptionStatus.TRIAL and
                subscription.trial_end_date and
                now >= subscription.trial_end_date):
                
                # Update status to active
                subscription.status = SubscriptionStatus.ACTIVE
                
                # Add status history entry
                subscription.status_history.append({
                    "status": subscription.status,
                    "timestamp": now.isoformat(),
                    "reason": "Trial period ended, subscription now active"
                })
                
                # Save the subscription if storage directory is set
                if self.storage_dir:
                    self._save_subscription(subscription)
                
                # Record event
                self._record_event(
                    event_type="trial_ended",
                    subscription_id=subscription.id,
                    user_id=subscription.user_id
                )
                
                updated_subscriptions.append(subscription)
        
        return updated_subscriptions
    
    def check_period_expirations(self) -> List[Subscription]:
        """
        Check for period expirations and update subscription statuses.
        
        Returns:
            List of subscriptions that were updated
        """
        updated_subscriptions = []
        now = datetime.now()
        
        for subscription in self.subscriptions.values():
            if subscription.is_active() and now >= subscription.current_period_end:
                # Check if subscription is set to cancel at period end
                if subscription.canceled_at and subscription.get_metadata("cancel_at_period_end"):
                    # Cancel subscription
                    subscription.status = SubscriptionStatus.CANCELED
                    
                    # Add status history entry
                    subscription.status_history.append({
                        "status": subscription.status,
                        "timestamp": now.isoformat(),
                        "reason": "Subscription canceled at period end"
                    })
                    
                    # Save the subscription if storage directory is set
                    if self.storage_dir:
                        self._save_subscription(subscription)
                    
                    # Record event
                    self._record_event(
                        event_type="subscription_canceled_at_period_end",
                        subscription_id=subscription.id,
                        user_id=subscription.user_id
                    )
                    
                    updated_subscriptions.append(subscription)
                else:
                    # Renew subscription
                    renewed_subscription = self.renew_subscription(subscription.id)
                    
                    if renewed_subscription:
                        updated_subscriptions.append(renewed_subscription)
        
        return updated_subscriptions
    
    def load_subscriptions(self) -> None:
        """
        Load subscriptions from storage directory.
        """
        if not self.storage_dir or not os.path.exists(self.storage_dir):
            return
        
        # Load subscriptions
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.storage_dir, filename)
                
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    
                    # Get plan
                    plan = self.get_plan(data["plan_id"])
                    
                    if plan:
                        # Create subscription
                        subscription = Subscription.load_from_dict(data, plan)
                        self.subscriptions[subscription.id] = subscription
                
                except Exception as e:
                    print(f"Error loading subscription from {file_path}: {e}")
    
    def _save_subscription(self, subscription: Subscription) -> None:
        """
        Save a subscription to the storage directory.
        
        Args:
            subscription: Subscription to save
        """
        if not self.storage_dir:
            return
        
        file_path = os.path.join(self.storage_dir, f"{subscription.id}.json")
        subscription.save_to_file(file_path)
    
    def _record_event(self, event_type: str, **kwargs) -> None:
        """
        Record a subscription event.
        
        Args:
            event_type: Type of event
            **kwargs: Event data
        """
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": kwargs
        }
        
        self.events.append(event)
    
    def get_events(
        self,
        event_type: Optional[str] = None,
        subscription_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get subscription events.
        
        Args:
            event_type: Type of events to get
            subscription_id: ID of the subscription
            user_id: ID of the user
            start_date: Start date for events
            end_date: End date for events
            
        Returns:
            List of events
        """
        filtered_events = []
        
        for event in self.events:
            # Filter by event type
            if event_type and event["type"] != event_type:
                continue
            
            # Filter by subscription ID
            if subscription_id and event["data"].get("subscription_id") != subscription_id:
                continue
            
            # Filter by user ID
            if user_id and event["data"].get("user_id") != user_id:
                continue
            
            # Filter by date range
            event_date = datetime.fromisoformat(event["timestamp"])
            
            if start_date and event_date < start_date:
                continue
            
            if end_date and event_date > end_date:
                continue
            
            filtered_events.append(event)
        
        return filtered_events


# Example usage
if __name__ == "__main__":
    from .subscription import SubscriptionPlan
    
    # Create a subscription manager
    manager = SubscriptionManager(storage_dir="subscriptions")
    
    # Create a subscription plan
    plan = SubscriptionPlan(
        name="AI Tool Subscription",
        description="Subscription plan for an AI-powered tool"
    )
    
    # Add features
    feature1 = plan.add_feature(
        name="Content Generation",
        description="Generate content using AI",
        type="quantity",
        category="core"
    )
    
    feature2 = plan.add_feature(
        name="API Access",
        description="Access to the API",
        type="boolean",
        category="integration"
    )
    
    # Add tiers
    basic_tier = plan.add_tier(
        name="Basic",
        description="Essential features for individuals",
        price_monthly=9.99,
        trial_days=14
    )
    
    pro_tier = plan.add_tier(
        name="Pro",
        description="Advanced features for professionals",
        price_monthly=19.99,
        is_popular=True
    )
    
    # Add features to tiers
    plan.add_feature_to_tier(basic_tier["id"], feature1["id"], value=True, limit=100)
    plan.add_feature_to_tier(pro_tier["id"], feature1["id"], value=True, limit=1000)
    
    plan.add_feature_to_tier(basic_tier["id"], feature2["id"], value=True)
    plan.add_feature_to_tier(pro_tier["id"], feature2["id"], value=True)
    
    # Add plan to manager
    manager.add_plan(plan)
    
    # Create a subscription
    user_id = "user123"
    subscription = manager.create_subscription(
        user_id=user_id,
        plan_id=plan.id,
        tier_id=basic_tier["id"],
        billing_cycle="monthly"
    )
    
    print(f"Subscription created: {subscription}")
    
    # Upgrade to Pro tier
    upgraded_subscription = manager.change_subscription_tier(
        subscription_id=subscription.id,
        new_tier_id=pro_tier["id"],
        prorate=True
    )
    
    print(f"Subscription upgraded: {upgraded_subscription}")
    print(f"New tier: {upgraded_subscription.get_tier()['name']}")
    print(f"New price: ${upgraded_subscription.price:.2f}/{upgraded_subscription.billing_cycle}")
    
    # Change billing cycle
    annual_subscription = manager.change_billing_cycle(
        subscription_id=subscription.id,
        new_billing_cycle="annual",
        prorate=True
    )
    
    print(f"Billing cycle changed: {annual_subscription}")
    print(f"New price: ${annual_subscription.price:.2f}/{annual_subscription.billing_cycle}")
    
    # Cancel subscription
    canceled_subscription = manager.cancel_subscription(
        subscription_id=subscription.id,
        cancel_at_period_end=True,
        reason="No longer needed"
    )
    
    print(f"Subscription canceled: {canceled_subscription}")
    print(f"Cancel at period end: {canceled_subscription.get_metadata('cancel_at_period_end')}")
    print(f"Cancellation reason: {canceled_subscription.get_metadata('cancellation_reason')}")
    
    # Reactivate subscription
    reactivated_subscription = manager.reactivate_subscription(
        subscription_id=subscription.id
    )
    
    print(f"Subscription reactivated: {reactivated_subscription}")
    
    # Get events
    events = manager.get_events(user_id=user_id)
    
    print("\nSubscription Events:")
    for event in events:
        print(f"- {event['type']} at {event['timestamp']}")
