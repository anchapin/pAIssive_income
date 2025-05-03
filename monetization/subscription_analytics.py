"""
Subscription analytics for the pAIssive Income project.

This module provides classes for analyzing subscription data, including
metrics calculation, churn analysis, and revenue forecasting.
"""

import time


from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .subscription import SubscriptionPlan
from .subscription_manager import SubscriptionManager
from .user_subscription import Subscription, SubscriptionStatus


class SubscriptionMetrics
    from .subscription import SubscriptionPlan
    from .subscription_manager import SubscriptionManager
    from .user_subscription import Subscription

    

:
    """
    Class for calculating basic subscription metrics.

This class provides methods for calculating various subscription metrics,
    such as active subscriptions, revenue, and growth rates.
    """

def __init__(self, subscription_manager: SubscriptionManager):
        """
        Initialize subscription metrics.

Args:
            subscription_manager: Subscription manager instance
        """
        self.subscription_manager = subscription_manager

def get_active_subscriptions(
        self, date: Optional[datetime] = None, plan_id: Optional[str] = None
    ) -> List[Subscription]:
        """
        Get active subscriptions at a specific date.

Args:
            date: Date to check (defaults to now)
            plan_id: Filter by plan ID

Returns:
            List of active subscriptions
        """
        date = date or datetime.now()

active_subscriptions = []

for subscription in self.subscription_manager.subscriptions.values():
            # Check if subscription was active at the given date
            if (
                subscription.start_date <= date
                and (not subscription.end_date or subscription.end_date >= date)
                and subscription.is_active()
            ):

# Filter by plan ID if provided
                if plan_id and subscription.plan_id != plan_id:
                    continue

active_subscriptions.append(subscription)

            return active_subscriptions

def get_subscription_count(
        self,
        status: Optional[str] = None,
        plan_id: Optional[str] = None,
        tier_id: Optional[str] = None,
        date: Optional[datetime] = None,
    ) -> int:
        """
        Get the count of subscriptions with a specific status.

Args:
            status: Status to filter by (defaults to all)
            plan_id: Plan ID to filter by
            tier_id: Tier ID to filter by
            date: Date to check (defaults to now)

Returns:
            Count of subscriptions
        """
        date = date or datetime.now()
        count = 0

for subscription in self.subscription_manager.subscriptions.values():
            # Check if subscription existed at the given date
            if subscription.start_date > date:
                continue

# Filter by status if provided
            if status and subscription.status != status:
                continue

# Filter by plan ID if provided
            if plan_id and subscription.plan_id != plan_id:
                continue

# Filter by tier ID if provided
            if tier_id and subscription.tier_id != tier_id:
                continue

count += 1

            return count

def get_active_subscription_count(
        self,
        plan_id: Optional[str] = None,
        tier_id: Optional[str] = None,
        date: Optional[datetime] = None,
    ) -> int:
        """
        Get the count of active subscriptions.

Args:
            plan_id: Plan ID to filter by
            tier_id: Tier ID to filter by
            date: Date to check (defaults to now)

Returns:
            Count of active subscriptions
        """
        active_statuses = [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]

date = date or datetime.now()
        count = 0

for subscription in self.subscription_manager.subscriptions.values():
            # Check if subscription was active at the given date
            if (
                subscription.start_date <= date
                and (not subscription.end_date or subscription.end_date >= date)
                and subscription.status in active_statuses
            ):

# Filter by plan ID if provided
                if plan_id and subscription.plan_id != plan_id:
                    continue

# Filter by tier ID if provided
                if tier_id and subscription.tier_id != tier_id:
                    continue

count += 1

            return count

def get_trial_subscription_count(
        self,
        plan_id: Optional[str] = None,
        tier_id: Optional[str] = None,
        date: Optional[datetime] = None,
    ) -> int:
        """
        Get the count of trial subscriptions.

Args:
            plan_id: Plan ID to filter by
            tier_id: Tier ID to filter by
            date: Date to check (defaults to now)

Returns:
            Count of trial subscriptions
        """
                    return self.get_subscription_count(
            status=SubscriptionStatus.TRIAL, plan_id=plan_id, tier_id=tier_id, date=date
        )

def get_canceled_subscription_count(
        self,
        plan_id: Optional[str] = None,
        tier_id: Optional[str] = None,
        date: Optional[datetime] = None,
    ) -> int:
        """
        Get the count of canceled subscriptions.

Args:
            plan_id: Plan ID to filter by
            tier_id: Tier ID to filter by
            date: Date to check (defaults to now)

Returns:
            Count of canceled subscriptions
        """
                    return self.get_subscription_count(
            status=SubscriptionStatus.CANCELED,
            plan_id=plan_id,
            tier_id=tier_id,
            date=date,
        )

def get_monthly_recurring_revenue(
        self,
        date: Optional[datetime] = None,
        plan_id: Optional[str] = None,
        tier_id: Optional[str] = None,
    ) -> float:
        """
        Calculate monthly recurring revenue (MRR).

Args:
            date: Date to calculate MRR for (defaults to now)
            plan_id: Plan ID to filter by
            tier_id: Tier ID to filter by

Returns:
            Monthly recurring revenue
        """
        date = date or datetime.now()
        mrr = 0.0

for subscription in self.get_active_subscriptions(date, plan_id):
            # Filter by tier ID if provided
            if tier_id and subscription.tier_id != tier_id:
                continue

# Skip trial subscriptions with no payment
            if (
                subscription.status == SubscriptionStatus.TRIAL
                and subscription.price == 0
            ):
                continue

# Calculate monthly equivalent price
            if subscription.billing_cycle == "monthly":
                mrr += subscription.price
            elif subscription.billing_cycle == "annual":
                mrr += subscription.price / 12
            else:
                # Default to monthly
                mrr += subscription.price

            return mrr

def get_annual_recurring_revenue(
        self,
        date: Optional[datetime] = None,
        plan_id: Optional[str] = None,
        tier_id: Optional[str] = None,
    ) -> float:
        """
        Calculate annual recurring revenue (ARR).

Args:
            date: Date to calculate ARR for (defaults to now)
            plan_id: Plan ID to filter by
            tier_id: Tier ID to filter by

Returns:
            Annual recurring revenue
        """
        mrr = self.get_monthly_recurring_revenue(date, plan_id, tier_id)
                    return mrr * 12

def get_average_revenue_per_user(
        self, date: Optional[datetime] = None, plan_id: Optional[str] = None
    ) -> float:
        """
        Calculate average revenue per user (ARPU).

Args:
            date: Date to calculate ARPU for (defaults to now)
            plan_id: Plan ID to filter by

Returns:
            Average revenue per user
        """
        date = date or datetime.now()
        active_count = self.get_active_subscription_count(plan_id, date=date)

if active_count == 0:
                        return 0.0

mrr = self.get_monthly_recurring_revenue(date, plan_id)
                    return mrr / active_count

def get_revenue_by_plan(self, date: Optional[datetime] = None) -> Dict[str, float]:
        """
        Get revenue breakdown by plan.

Args:
            date: Date to calculate revenue for (defaults to now)

Returns:
            Dictionary mapping plan IDs to revenue
        """
        date = date or datetime.now()
        revenue_by_plan = {}

for plan in self.subscription_manager.plans.values():
            mrr = self.get_monthly_recurring_revenue(date, plan.id)
            revenue_by_plan[plan.id] = mrr

            return revenue_by_plan

def get_revenue_by_tier(
        self, plan_id: str, date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Get revenue breakdown by tier for a specific plan.

Args:
            plan_id: Plan ID
            date: Date to calculate revenue for (defaults to now)

Returns:
            Dictionary mapping tier IDs to revenue
        """
        date = date or datetime.now()
        revenue_by_tier = {}

plan = self.subscription_manager.get_plan(plan_id)

if not plan:
                        return {}

for tier in plan.tiers:
            tier_id = tier["id"]
            mrr = self.get_monthly_recurring_revenue(date, plan_id, tier_id)
            revenue_by_tier[tier_id] = mrr

            return revenue_by_tier

def get_subscription_growth_rate(
        self,
        period: str = "month",
        plan_id: Optional[str] = None,
        end_date: Optional[datetime] = None,
    ) -> float:
        """
        Calculate subscription growth rate.

Args:
            period: Period to calculate growth rate for (day, week, month, year)
            plan_id: Plan ID to filter by
            end_date: End date for the calculation (defaults to now)

Returns:
            Growth rate as a percentage
        """
        end_date = end_date or datetime.now()

# Calculate start date based on period
        if period == "day":
            start_date = end_date - timedelta(days=1)
        elif period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            # Approximate a month as 30 days
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            # Approximate a year as 365 days
            start_date = end_date - timedelta(days=365)
        else:
            # Default to month
            start_date = end_date - timedelta(days=30)

# Get subscription counts
        start_count = self.get_active_subscription_count(plan_id, date=start_date)
        end_count = self.get_active_subscription_count(plan_id, date=end_date)

# Calculate growth rate
        if start_count == 0:
                        return 0.0 if end_count == 0 else 100.0

growth_rate = ((end_count - start_count) / start_count) * 100
                    return growth_rate

def get_revenue_growth_rate(
        self,
        period: str = "month",
        plan_id: Optional[str] = None,
        end_date: Optional[datetime] = None,
    ) -> float:
        """
        Calculate revenue growth rate.

Args:
            period: Period to calculate growth rate for (day, week, month, year)
            plan_id: Plan ID to filter by
            end_date: End date for the calculation (defaults to now)

Returns:
            Growth rate as a percentage
        """
        end_date = end_date or datetime.now()

# Calculate start date based on period
        if period == "day":
            start_date = end_date - timedelta(days=1)
        elif period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            # Approximate a month as 30 days
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            # Approximate a year as 365 days
            start_date = end_date - timedelta(days=365)
        else:
            # Default to month
            start_date = end_date - timedelta(days=30)

# Get revenue
        start_mrr = self.get_monthly_recurring_revenue(start_date, plan_id)
        end_mrr = self.get_monthly_recurring_revenue(end_date, plan_id)

# Calculate growth rate
        if start_mrr == 0:
                        return 0.0 if end_mrr == 0 else 100.0

growth_rate = ((end_mrr - start_mrr) / start_mrr) * 100
                    return growth_rate

def get_subscription_distribution(
        self, date: Optional[datetime] = None
    ) -> Dict[str, Dict[str, int]]:
        """
        Get distribution of subscriptions by plan and tier.

Args:
            date: Date to calculate distribution for (defaults to now)

Returns:
            Dictionary mapping plan IDs to dictionaries mapping tier IDs to counts
        """
        date = date or datetime.now()
        distribution = {}

for plan in self.subscription_manager.plans.values():
            plan_distribution = {}

for tier in plan.tiers:
                tier_id = tier["id"]
                count = self.get_active_subscription_count(plan.id, tier_id, date)
                plan_distribution[tier_id] = count

distribution[plan.id] = plan_distribution

            return distribution

def get_subscription_history(
        self,
        interval: str = "month",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        plan_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get subscription count history over time.

Args:
            interval: Time interval (day, week, month)
            start_date: Start date for the history
            end_date: End date for the history (defaults to now)
            plan_id: Plan ID to filter by

Returns:
            List of dictionaries with date and count
        """
        end_date = end_date or datetime.now()

# Set default start date if not provided
        if start_date is None:
            if interval == "day":
                start_date = end_date - timedelta(days=30)
            elif interval == "week":
                start_date = end_date - timedelta(days=90)
            else:  # month
                start_date = end_date - timedelta(days=365)

# Generate date points
        date_points = []
        current_date = start_date

while current_date <= end_date:
            date_points.append(current_date)

if interval == "day":
                current_date = current_date + timedelta(days=1)
            elif interval == "week":
                current_date = current_date + timedelta(days=7)
            else:  # month
                # Approximate a month as 30 days
                current_date = current_date + timedelta(days=30)

# Calculate subscription counts for each date point
        history = []

for date in date_points:
            count = self.get_active_subscription_count(plan_id, date=date)

history.append({"date": date.isoformat(), "count": count})

            return history

def get_revenue_history(
        self,
        interval: str = "month",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        plan_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get revenue history over time.

Args:
            interval: Time interval (day, week, month)
            start_date: Start date for the history
            end_date: End date for the history (defaults to now)
            plan_id: Plan ID to filter by

Returns:
            List of dictionaries with date and revenue
        """
        end_date = end_date or datetime.now()

# Set default start date if not provided
        if start_date is None:
            if interval == "day":
                start_date = end_date - timedelta(days=30)
            elif interval == "week":
                start_date = end_date - timedelta(days=90)
            else:  # month
                start_date = end_date - timedelta(days=365)

# Generate date points
        date_points = []
        current_date = start_date

while current_date <= end_date:
            date_points.append(current_date)

if interval == "day":
                current_date = current_date + timedelta(days=1)
            elif interval == "week":
                current_date = current_date + timedelta(days=7)
            else:  # month
                # Approximate a month as 30 days
                current_date = current_date + timedelta(days=30)

# Calculate revenue for each date point
        history = []

for date in date_points:
            mrr = self.get_monthly_recurring_revenue(date, plan_id)

history.append({"date": date.isoformat(), "revenue": mrr})

            return history

def get_subscription_summary(
        self, date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get a summary of subscription metrics.

Args:
            date: Date to calculate metrics for (defaults to now)

Returns:
            Dictionary with subscription metrics
        """
        date = date or datetime.now()

# Calculate metrics
        total_count = self.get_subscription_count(date=date)
        active_count = self.get_active_subscription_count(date=date)
        trial_count = self.get_trial_subscription_count(date=date)
        canceled_count = self.get_canceled_subscription_count(date=date)

mrr = self.get_monthly_recurring_revenue(date)
        arr = self.get_annual_recurring_revenue(date)
        arpu = self.get_average_revenue_per_user(date)

# Calculate growth rates
        subscription_growth = self.get_subscription_growth_rate("month", end_date=date)
        revenue_growth = self.get_revenue_growth_rate("month", end_date=date)

# Get distribution
        distribution = self.get_subscription_distribution(date)

# Create summary
        summary = {
            "date": date.isoformat(),
            "total_count": total_count,
            "active_count": active_count,
            "trial_count": trial_count,
            "canceled_count": canceled_count,
            "mrr": mrr,
            "arr": arr,
            "arpu": arpu,
            "subscription_growth": subscription_growth,
            "revenue_growth": revenue_growth,
            "distribution": distribution,
        }

            return summary


class ChurnAnalysis:
    """
    Class for analyzing subscription churn and retention.

This class provides methods for calculating churn rates, retention rates,
    and performing cohort analysis.
    """

def __init__(self, subscription_manager: SubscriptionManager):
        """
        Initialize churn analysis.

Args:
            subscription_manager: Subscription manager instance
        """
        self.subscription_manager = subscription_manager
        self.metrics = SubscriptionMetrics(subscription_manager)

def get_churn_rate(
        self,
        period: str = "month",
        plan_id: Optional[str] = None,
        end_date: Optional[datetime] = None,
    ) -> float:
        """
        Calculate churn rate for a specific period.

Args:
            period: Period to calculate churn rate for (day, week, month, year)
            plan_id: Plan ID to filter by
            end_date: End date for the calculation (defaults to now)

Returns:
            Churn rate as a percentage
        """
        end_date = end_date or datetime.now()

# Calculate start date based on period
        if period == "day":
            start_date = end_date - timedelta(days=1)
        elif period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            # Approximate a month as 30 days
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            # Approximate a year as 365 days
            start_date = end_date - timedelta(days=365)
        else:
            # Default to month
            start_date = end_date - timedelta(days=30)

# Get active subscriptions at start date
        active_at_start = self.metrics.get_active_subscriptions(start_date, plan_id)

if not active_at_start:
                        return 0.0

# Count how many of those subscriptions are no longer active at end date
        churned_count = 0

for subscription in active_at_start:
            # Check if subscription is still active at end date
            if subscription.status not in [
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.TRIAL,
            ]:
                churned_count += 1
                continue

# Check if subscription has an end date before the end_date
            if subscription.end_date and subscription.end_date < end_date:
                churned_count += 1

# Calculate churn rate
        churn_rate = (churned_count / len(active_at_start)) * 100
                    return churn_rate

def get_retention_rate(
        self,
        period: str = "month",
        plan_id: Optional[str] = None,
        end_date: Optional[datetime] = None,
    ) -> float:
        """
        Calculate retention rate for a specific period.

Args:
            period: Period to calculate retention rate for (day, week, month, year)
            plan_id: Plan ID to filter by
            end_date: End date for the calculation (defaults to now)

Returns:
            Retention rate as a percentage
        """
        churn_rate = self.get_churn_rate(period, plan_id, end_date)
                    return 100.0 - churn_rate

def get_churn_by_plan(
        self, period: str = "month", end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Get churn rate breakdown by plan.

Args:
            period: Period to calculate churn rate for (day, week, month, year)
            end_date: End date for the calculation (defaults to now)

Returns:
            Dictionary mapping plan IDs to churn rates
        """
        end_date = end_date or datetime.now()
        churn_by_plan = {}

for plan in self.subscription_manager.plans.values():
            churn_rate = self.get_churn_rate(period, plan.id, end_date)
            churn_by_plan[plan.id] = churn_rate

            return churn_by_plan

def get_churn_by_tier(
        self, plan_id: str, period: str = "month", end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Get churn rate breakdown by tier for a specific plan.

Args:
            plan_id: Plan ID
            period: Period to calculate churn rate for (day, week, month, year)
            end_date: End date for the calculation (defaults to now)

Returns:
            Dictionary mapping tier IDs to churn rates
        """
        end_date = end_date or datetime.now()
        churn_by_tier = {}

plan = self.subscription_manager.get_plan(plan_id)

if not plan:
                        return {}

# Calculate start date based on period
        if period == "day":
            start_date = end_date - timedelta(days=1)
        elif period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            # Approximate a month as 30 days
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            # Approximate a year as 365 days
            start_date = end_date - timedelta(days=365)
        else:
            # Default to month
            start_date = end_date - timedelta(days=30)

for tier in plan.tiers:
            tier_id = tier["id"]

# Get active subscriptions at start date for this tier
            active_at_start = []

for subscription in self.metrics.get_active_subscriptions(
                start_date, plan_id
            ):
                if subscription.tier_id == tier_id:
                    active_at_start.append(subscription)

if not active_at_start:
                churn_by_tier[tier_id] = 0.0
                continue

# Count how many of those subscriptions are no longer active at end date
            churned_count = 0

for subscription in active_at_start:
                # Check if subscription is still active at end date
                if subscription.status not in [
                    SubscriptionStatus.ACTIVE,
                    SubscriptionStatus.TRIAL,
                ]:
                    churned_count += 1
                    continue

# Check if subscription has an end date before the end_date
                if subscription.end_date and subscription.end_date < end_date:
                    churned_count += 1

# Calculate churn rate
            churn_rate = (churned_count / len(active_at_start)) * 100
            churn_by_tier[tier_id] = churn_rate

            return churn_by_tier

def get_churn_history(
        self,
        interval: str = "month",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        plan_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get churn rate history over time.

Args:
            interval: Time interval (day, week, month)
            start_date: Start date for the history
            end_date: End date for the history (defaults to now)
            plan_id: Plan ID to filter by

Returns:
            List of dictionaries with date and churn rate
        """
        end_date = end_date or datetime.now()

# Set default start date if not provided
        if start_date is None:
            if interval == "day":
                start_date = end_date - timedelta(days=30)
            elif interval == "week":
                start_date = end_date - timedelta(days=90)
            else:  # month
                start_date = end_date - timedelta(days=365)

# Generate date points
        date_points = []
        current_date = start_date

while current_date <= end_date:
            date_points.append(current_date)

if interval == "day":
                current_date = current_date + timedelta(days=1)
            elif interval == "week":
                current_date = current_date + timedelta(days=7)
            else:  # month
                # Approximate a month as 30 days
                current_date = current_date + timedelta(days=30)

# Calculate churn rate for each date point
        history = []

for date in date_points:
            churn_rate = self.get_churn_rate(interval, plan_id, date)

history.append({"date": date.isoformat(), "churn_rate": churn_rate})

            return history

def get_cohort_retention(
        self,
        cohort_interval: str = "month",
        periods: int = 6,
        end_date: Optional[datetime] = None,
        plan_id: Optional[str] = None,
    ) -> Dict[str, List[float]]:
        """
        Perform cohort analysis for retention rates.

Args:
            cohort_interval: Interval for cohorts (week, month)
            periods: Number of periods to analyze
            end_date: End date for the analysis (defaults to now)
            plan_id: Plan ID to filter by

Returns:
            Dictionary mapping cohort dates to lists of retention rates
        """
        end_date = end_date or datetime.now()

# Calculate cohort start dates
        cohort_dates = []
        current_date = end_date

for _ in range(periods):
            if cohort_interval == "week":
                current_date = current_date - timedelta(days=7)
            else:  # month
                # Approximate a month as 30 days
                current_date = current_date - timedelta(days=30)

cohort_dates.append(current_date)

# Reverse dates so they're in chronological order
        cohort_dates.reverse()

# Calculate retention rates for each cohort
        cohort_retention = {}

for cohort_date in cohort_dates:
            # Get subscriptions that started in this cohort
            cohort_subscriptions = []

for subscription in self.subscription_manager.subscriptions.values():
                # Check if subscription started in this cohort
                if cohort_interval == "week":
                    cohort_start = cohort_date
                    cohort_end = cohort_date + timedelta(days=7)
                else:  # month
                    cohort_start = cohort_date
                    cohort_end = cohort_date + timedelta(days=30)

if (
                    subscription.start_date >= cohort_start
                    and subscription.start_date < cohort_end
                ):

# Filter by plan ID if provided
                    if plan_id and subscription.plan_id != plan_id:
                        continue

cohort_subscriptions.append(subscription)

if not cohort_subscriptions:
                continue

# Calculate retention rates for each period
            retention_rates = []

for period in range(periods):
                if cohort_interval == "week":
                    period_date = cohort_date + timedelta(days=7 * (period + 1))
                else:  # month
                    period_date = cohort_date + timedelta(days=30 * (period + 1))

# Skip future periods
                if period_date > end_date:
                    retention_rates.append(None)
                    continue

# Count how many subscriptions are still active at this period
                active_count = 0

for subscription in cohort_subscriptions:
                    # Check if subscription is still active at this period
                    if subscription.status in [
                        SubscriptionStatus.ACTIVE,
                        SubscriptionStatus.TRIAL,
                    ] and (
                        not subscription.end_date
                        or subscription.end_date >= period_date
                    ):
                        active_count += 1

# Calculate retention rate
                retention_rate = (active_count / len(cohort_subscriptions)) * 100
                retention_rates.append(retention_rate)

# Add cohort to results
            cohort_retention[cohort_date.isoformat()] = retention_rates

            return cohort_retention

def get_lifetime_value(
        self,
        plan_id: Optional[str] = None,
        tier_id: Optional[str] = None,
        churn_rate: Optional[float] = None,
        discount_rate: float = 0.1,
    ) -> float:
        """
        Calculate customer lifetime value (LTV).

Args:
            plan_id: Plan ID to filter by
            tier_id: Tier ID to filter by
            churn_rate: Churn rate to use (if None, calculated from data)
            discount_rate: Discount rate for future revenue

Returns:
            Customer lifetime value
        """
        # Get average revenue per user
        arpu = self.metrics.get_average_revenue_per_user(plan_id=plan_id)

# Get churn rate if not provided
        if churn_rate is None:
            churn_rate = self.get_churn_rate("month", plan_id)

# Convert churn rate to decimal
        churn_rate_decimal = churn_rate / 100.0

# Avoid division by zero
        if churn_rate_decimal <= 0:
            churn_rate_decimal = 0.01

# Calculate LTV using the formula: ARPU / churn_rate
        ltv = arpu / churn_rate_decimal

# Apply discount rate
        ltv = ltv * (1 - discount_rate)

            return ltv

def get_churn_reasons(self) -> Dict[str, int]:
        """
        Get distribution of churn reasons.

Returns:
            Dictionary mapping reason categories to counts
        """
        reasons = defaultdict(int)

for subscription in self.subscription_manager.subscriptions.values():
            if subscription.status != SubscriptionStatus.CANCELED:
                continue

# Get cancellation reason from metadata
            reason = subscription.get_metadata("cancellation_reason")

if not reason:
                reasons["Unknown"] += 1
                continue

# Categorize reasons
            if (
                "price" in reason.lower()
                or "expensive" in reason.lower()
                or "cost" in reason.lower()
            ):
                reasons["Price"] += 1
            elif (
                "feature" in reason.lower()
                or "missing" in reason.lower()
                or "lack" in reason.lower()
            ):
                reasons["Missing Features"] += 1
            elif "competitor" in reason.lower() or "alternative" in reason.lower():
                reasons["Competitor"] += 1
            elif (
                "difficult" in reason.lower()
                or "complex" in reason.lower()
                or "confusing" in reason.lower()
            ):
                reasons["Usability"] += 1
            elif (
                "support" in reason.lower()
                or "help" in reason.lower()
                or "service" in reason.lower()
            ):
                reasons["Support"] += 1
            elif (
                "temporary" in reason.lower()
                or "pause" in reason.lower()
                or "break" in reason.lower()
            ):
                reasons["Temporary"] += 1
            elif (
                "business" in reason.lower()
                or "company" in reason.lower()
                or "project" in reason.lower()
            ):
                reasons["Business Changes"] += 1
            else:
                reasons["Other"] += 1

            return dict(reasons)

def get_churn_prediction(self, subscription_id: str) -> float:
        """
        Predict the likelihood of churn for a specific subscription.

Args:
            subscription_id: ID of the subscription

Returns:
            Churn probability (0-100)
        """
        subscription = self.subscription_manager.get_subscription(subscription_id)

if not subscription:
                        return 0.0

# Simple heuristic-based prediction
        churn_probability = 0.0

# Factor 1: Subscription age
        age_months = subscription.get_subscription_age_months()

if age_months < 1:
            churn_probability += 30  # New subscriptions have higher churn
        elif age_months < 3:
            churn_probability += 20
        elif age_months < 6:
            churn_probability += 10

# Factor 2: Usage patterns
        usage_sum = sum(subscription.usage.values())

if usage_sum == 0:
            churn_probability += 40  # No usage is a strong indicator of churn
        elif usage_sum < 10:
            churn_probability += 20  # Low usage

# Factor 3: Payment issues
        if subscription.status == SubscriptionStatus.PAST_DUE:
            churn_probability += 50
        elif subscription.status == SubscriptionStatus.UNPAID:
            churn_probability += 70

# Factor 4: Previous cancellation attempts
        if subscription.get_metadata("previous_cancellation_attempt"):
            churn_probability += 40

# Cap probability at 100%
                    return min(100.0, churn_probability)

def get_at_risk_subscriptions(
        self, threshold: float = 50.0, plan_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get subscriptions at risk of churning.

Args:
            threshold: Churn probability threshold
            plan_id: Plan ID to filter by

Returns:
            List of dictionaries with subscription ID and churn probability
        """
        at_risk = []

for subscription in self.subscription_manager.subscriptions.values():
            # Filter by plan ID if provided
            if plan_id and subscription.plan_id != plan_id:
                continue

# Skip non-active subscriptions
            if not subscription.is_active():
                continue

# Calculate churn probability
            churn_probability = self.get_churn_prediction(subscription.id)

if churn_probability >= threshold:
                at_risk.append(
                    {
                        "subscription_id": subscription.id,
                        "user_id": subscription.user_id,
                        "plan_id": subscription.plan_id,
                        "tier_id": subscription.tier_id,
                        "churn_probability": churn_probability,
                    }
                )

# Sort by churn probability (highest first)
        at_risk.sort(key=lambda x: x["churn_probability"], reverse=True)

            return at_risk

def get_churn_summary(
        self, period: str = "month", end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get a summary of churn metrics.

Args:
            period: Period to calculate metrics for (day, week, month, year)
            end_date: End date for the calculation (defaults to now)

Returns:
            Dictionary with churn metrics
        """
        end_date = end_date or datetime.now()

# Calculate metrics
        churn_rate = self.get_churn_rate(period, end_date=end_date)
        retention_rate = self.get_retention_rate(period, end_date=end_date)

# Get churn by plan
        churn_by_plan = self.get_churn_by_plan(period, end_date)

# Get churn reasons
        churn_reasons = self.get_churn_reasons()

# Get at-risk subscriptions
        at_risk = self.get_at_risk_subscriptions()

# Calculate lifetime value
        ltv = self.get_lifetime_value()

# Create summary
        summary = {
            "date": end_date.isoformat(),
            "period": period,
            "churn_rate": churn_rate,
            "retention_rate": retention_rate,
            "churn_by_plan": churn_by_plan,
            "churn_reasons": churn_reasons,
            "at_risk_count": len(at_risk),
            "lifetime_value": ltv,
        }

            return summary


class SubscriptionForecasting:
    """
    Class for forecasting subscription metrics.

This class provides methods for forecasting subscription growth,
    revenue, and other metrics.
    """

def __init__(
        self,
        subscription_manager: SubscriptionManager,
        metrics: Optional[SubscriptionMetrics] = None,
        churn_analysis: Optional[ChurnAnalysis] = None,
    ):
        """
        Initialize subscription forecasting.

Args:
            subscription_manager: Subscription manager instance
            metrics: Subscription metrics instance (optional)
            churn_analysis: Churn analysis instance (optional)
        """
        self.subscription_manager = subscription_manager
        self.metrics = metrics or SubscriptionMetrics(subscription_manager)
        self.churn_analysis = churn_analysis or ChurnAnalysis(subscription_manager)

def forecast_subscriptions(
        self,
        periods: int = 12,
        period_type: str = "month",
        growth_rate: Optional[float] = None,
        churn_rate: Optional[float] = None,
        plan_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Forecast subscription count for future periods.

Args:
            periods: Number of periods to forecast
            period_type: Type of period (day, week, month, year)
            growth_rate: Monthly growth rate as a percentage (if None, calculated from data)
            churn_rate: Monthly churn rate as a percentage (if None, calculated from data)
            plan_id: Plan ID to filter by

Returns:
            List of dictionaries with period and forecasted subscription count
        """
        # Get current subscription count
        current_count = self.metrics.get_active_subscription_count(plan_id=plan_id)

# Get growth rate if not provided
        if growth_rate is None:
            growth_rate = self.metrics.get_subscription_growth_rate("month", plan_id)

# Get churn rate if not provided
        if churn_rate is None:
            churn_rate = self.churn_analysis.get_churn_rate("month", plan_id)

# Convert rates to decimal
        growth_rate_decimal = growth_rate / 100.0
        churn_rate_decimal = churn_rate / 100.0

# Calculate net growth rate
        net_growth_rate = growth_rate_decimal - churn_rate_decimal

# Generate forecast
        forecast = []
        current_date = datetime.now()

for i in range(periods):
            # Calculate next period date
            if period_type == "day":
                period_date = current_date + timedelta(days=i + 1)
            elif period_type == "week":
                period_date = current_date + timedelta(days=(i + 1) * 7)
            elif period_type == "month":
                # Approximate a month as 30 days
                period_date = current_date + timedelta(days=(i + 1) * 30)
            elif period_type == "year":
                # Approximate a year as 365 days
                period_date = current_date + timedelta(days=(i + 1) * 365)
            else:
                # Default to month
                period_date = current_date + timedelta(days=(i + 1) * 30)

# Calculate forecasted count
            forecasted_count = current_count * (1 + net_growth_rate) ** (i + 1)

# Round to nearest integer
            forecasted_count = round(forecasted_count)

# Add to forecast
            forecast.append(
                {
                    "period": i + 1,
                    "date": period_date.isoformat(),
                    "subscriptions": forecasted_count,
                }
            )

            return forecast

def forecast_revenue(
        self,
        periods: int = 12,
        period_type: str = "month",
        growth_rate: Optional[float] = None,
        churn_rate: Optional[float] = None,
        arpu_change_rate: float = 0.0,
        plan_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Forecast revenue for future periods.

Args:
            periods: Number of periods to forecast
            period_type: Type of period (day, week, month, year)
            growth_rate: Monthly growth rate as a percentage (if None, calculated from data)
            churn_rate: Monthly churn rate as a percentage (if None, calculated from data)
            arpu_change_rate: Monthly ARPU change rate as a percentage
            plan_id: Plan ID to filter by

Returns:
            List of dictionaries with period and forecasted revenue
        """
        # Get current MRR
        self.metrics.get_monthly_recurring_revenue(plan_id=plan_id)

# Get current ARPU
        current_arpu = self.metrics.get_average_revenue_per_user(plan_id=plan_id)

# Get subscription forecast
        subscription_forecast = self.forecast_subscriptions(
            periods=periods,
            period_type=period_type,
            growth_rate=growth_rate,
            churn_rate=churn_rate,
            plan_id=plan_id,
        )

# Convert ARPU change rate to decimal
        arpu_change_rate_decimal = arpu_change_rate / 100.0

# Generate forecast
        forecast = []

for i, period in enumerate(subscription_forecast):
            # Calculate forecasted ARPU
            forecasted_arpu = current_arpu * (1 + arpu_change_rate_decimal) ** (i + 1)

# Calculate forecasted revenue
            forecasted_revenue = period["subscriptions"] * forecasted_arpu

# Add to forecast
            forecast.append(
                {
                    "period": period["period"],
                    "date": period["date"],
                    "subscriptions": period["subscriptions"],
                    "arpu": forecasted_arpu,
                    "revenue": forecasted_revenue,
                }
            )

            return forecast

def forecast_ltv(
        self,
        periods: int = 12,
        churn_rate: Optional[float] = None,
        arpu_change_rate: float = 0.0,
        discount_rate: float = 0.1,
        plan_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Forecast customer lifetime value for future periods.

Args:
            periods: Number of periods to forecast
            churn_rate: Monthly churn rate as a percentage (if None, calculated from data)
            arpu_change_rate: Monthly ARPU change rate as a percentage
            discount_rate: Discount rate for future revenue
            plan_id: Plan ID to filter by

Returns:
            List of dictionaries with period and forecasted LTV
        """
        # Get current ARPU
        current_arpu = self.metrics.get_average_revenue_per_user(plan_id=plan_id)

# Get churn rate if not provided
        if churn_rate is None:
            churn_rate = self.churn_analysis.get_churn_rate("month", plan_id)

# Convert rates to decimal
        churn_rate_decimal = churn_rate / 100.0
        arpu_change_rate_decimal = arpu_change_rate / 100.0

# Avoid division by zero
        if churn_rate_decimal <= 0:
            churn_rate_decimal = 0.01

# Generate forecast
        forecast = []
        current_date = datetime.now()

for i in range(periods):
            # Calculate period date
            period_date = current_date + timedelta(days=(i + 1) * 30)

# Calculate forecasted ARPU
            forecasted_arpu = current_arpu * (1 + arpu_change_rate_decimal) ** (i + 1)

# Calculate forecasted LTV
            forecasted_ltv = forecasted_arpu / churn_rate_decimal

# Apply discount rate
            forecasted_ltv = forecasted_ltv * (1 - discount_rate)

# Add to forecast
            forecast.append(
                {
                    "period": i + 1,
                    "date": period_date.isoformat(),
                    "arpu": forecasted_arpu,
                    "ltv": forecasted_ltv,
                }
            )

            return forecast

def forecast_churn(
        self,
        periods: int = 12,
        period_type: str = "month",
        churn_rate: Optional[float] = None,
        churn_change_rate: float = 0.0,
        plan_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Forecast churn rate for future periods.

Args:
            periods: Number of periods to forecast
            period_type: Type of period (day, week, month, year)
            churn_rate: Monthly churn rate as a percentage (if None, calculated from data)
            churn_change_rate: Monthly churn rate change as a percentage
            plan_id: Plan ID to filter by

Returns:
            List of dictionaries with period and forecasted churn rate
        """
        # Get churn rate if not provided
        if churn_rate is None:
            churn_rate = self.churn_analysis.get_churn_rate("month", plan_id)

# Convert churn change rate to decimal
        churn_change_rate_decimal = churn_change_rate / 100.0

# Generate forecast
        forecast = []
        current_date = datetime.now()

for i in range(periods):
            # Calculate period date
            if period_type == "day":
                period_date = current_date + timedelta(days=i + 1)
            elif period_type == "week":
                period_date = current_date + timedelta(days=(i + 1) * 7)
            elif period_type == "month":
                # Approximate a month as 30 days
                period_date = current_date + timedelta(days=(i + 1) * 30)
            elif period_type == "year":
                # Approximate a year as 365 days
                period_date = current_date + timedelta(days=(i + 1) * 365)
            else:
                # Default to month
                period_date = current_date + timedelta(days=(i + 1) * 30)

# Calculate forecasted churn rate
            forecasted_churn_rate = churn_rate * (1 + churn_change_rate_decimal) ** (
                i + 1
            )

# Add to forecast
            forecast.append(
                {
                    "period": i + 1,
                    "date": period_date.isoformat(),
                    "churn_rate": forecasted_churn_rate,
                }
            )

            return forecast

def forecast_growth_scenarios(
        self,
        periods: int = 12,
        period_type: str = "month",
        scenarios: List[Dict[str, Any]] = None,
        plan_id: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Forecast subscription growth under different scenarios.

Args:
            periods: Number of periods to forecast
            period_type: Type of period (day, week, month, year)
            scenarios: List of scenario dictionaries with name, growth_rate, and churn_rate
            plan_id: Plan ID to filter by

Returns:
            Dictionary mapping scenario names to forecasts
        """
        # Set default scenarios if not provided
        if scenarios is None:
            # Get current growth and churn rates
            current_growth_rate = self.metrics.get_subscription_growth_rate(
                "month", plan_id
            )
            current_churn_rate = self.churn_analysis.get_churn_rate("month", plan_id)

scenarios = [
                {
                    "name": "Pessimistic",
                    "growth_rate": max(0, current_growth_rate - 5),
                    "churn_rate": current_churn_rate + 2,
                },
                {
                    "name": "Realistic",
                    "growth_rate": current_growth_rate,
                    "churn_rate": current_churn_rate,
                },
                {
                    "name": "Optimistic",
                    "growth_rate": current_growth_rate + 5,
                    "churn_rate": max(0, current_churn_rate - 2),
                },
            ]

# Generate forecasts for each scenario
        forecasts = {}

for scenario in scenarios:
            forecast = self.forecast_subscriptions(
                periods=periods,
                period_type=period_type,
                growth_rate=scenario["growth_rate"],
                churn_rate=scenario["churn_rate"],
                plan_id=plan_id,
            )

forecasts[scenario["name"]] = forecast

            return forecasts

def forecast_revenue_scenarios(
        self,
        periods: int = 12,
        period_type: str = "month",
        scenarios: List[Dict[str, Any]] = None,
        plan_id: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Forecast revenue under different scenarios.

Args:
            periods: Number of periods to forecast
            period_type: Type of period (day, week, month, year)
            scenarios: List of scenario dictionaries with name, growth_rate, churn_rate, and arpu_change_rate
            plan_id: Plan ID to filter by

Returns:
            Dictionary mapping scenario names to forecasts
        """
        # Set default scenarios if not provided
        if scenarios is None:
            # Get current growth and churn rates
            current_growth_rate = self.metrics.get_subscription_growth_rate(
                "month", plan_id
            )
            current_churn_rate = self.churn_analysis.get_churn_rate("month", plan_id)

scenarios = [
                {
                    "name": "Pessimistic",
                    "growth_rate": max(0, current_growth_rate - 5),
                    "churn_rate": current_churn_rate + 2,
                    "arpu_change_rate": -1.0,
                },
                {
                    "name": "Realistic",
                    "growth_rate": current_growth_rate,
                    "churn_rate": current_churn_rate,
                    "arpu_change_rate": 0.0,
                },
                {
                    "name": "Optimistic",
                    "growth_rate": current_growth_rate + 5,
                    "churn_rate": max(0, current_churn_rate - 2),
                    "arpu_change_rate": 2.0,
                },
            ]

# Generate forecasts for each scenario
        forecasts = {}

for scenario in scenarios:
            forecast = self.forecast_revenue(
                periods=periods,
                period_type=period_type,
                growth_rate=scenario["growth_rate"],
                churn_rate=scenario["churn_rate"],
                arpu_change_rate=scenario.get("arpu_change_rate", 0.0),
                plan_id=plan_id,
            )

forecasts[scenario["name"]] = forecast

            return forecasts

def forecast_breakeven(
        self,
        fixed_costs: float,
        variable_cost_per_user: float,
        periods: int = 24,
        period_type: str = "month",
        growth_rate: Optional[float] = None,
        churn_rate: Optional[float] = None,
        arpu_change_rate: float = 0.0,
        plan_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Forecast when the business will break even.

Args:
            fixed_costs: Monthly fixed costs
            variable_cost_per_user: Variable cost per user per month
            periods: Number of periods to forecast
            period_type: Type of period (day, week, month, year)
            growth_rate: Monthly growth rate as a percentage (if None, calculated from data)
            churn_rate: Monthly churn rate as a percentage (if None, calculated from data)
            arpu_change_rate: Monthly ARPU change rate as a percentage
            plan_id: Plan ID to filter by

Returns:
            Dictionary with breakeven period information or None if not found
        """
        # Get revenue forecast
        revenue_forecast = self.forecast_revenue(
            periods=periods,
            period_type=period_type,
            growth_rate=growth_rate,
            churn_rate=churn_rate,
            arpu_change_rate=arpu_change_rate,
            plan_id=plan_id,
        )

# Calculate costs and profit for each period
        for period in revenue_forecast:
            # Calculate variable costs
            variable_costs = period["subscriptions"] * variable_cost_per_user

# Calculate total costs
            total_costs = fixed_costs + variable_costs

# Calculate profit
            profit = period["revenue"] - total_costs

# Add to forecast
            period["fixed_costs"] = fixed_costs
            period["variable_costs"] = variable_costs
            period["total_costs"] = total_costs
            period["profit"] = profit

# Check if breakeven
            if profit >= 0:
                            return period

# No breakeven found within forecast period
                    return None

def forecast_summary(
        self,
        periods: int = 12,
        period_type: str = "month",
        plan_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get a summary of forecasted metrics.

Args:
            periods: Number of periods to forecast
            period_type: Type of period (day, week, month, year)
            plan_id: Plan ID to filter by

Returns:
            Dictionary with forecasted metrics
        """
        # Get current metrics
        current_subscriptions = self.metrics.get_active_subscription_count(
            plan_id=plan_id
        )
        current_mrr = self.metrics.get_monthly_recurring_revenue(plan_id=plan_id)
        current_arpu = self.metrics.get_average_revenue_per_user(plan_id=plan_id)
        current_churn_rate = self.churn_analysis.get_churn_rate("month", plan_id)
        current_ltv = self.churn_analysis.get_lifetime_value(plan_id=plan_id)

# Get forecasts
        subscription_forecast = self.forecast_subscriptions(
            periods=periods, period_type=period_type, plan_id=plan_id
        )

revenue_forecast = self.forecast_revenue(
            periods=periods, period_type=period_type, plan_id=plan_id
        )

churn_forecast = self.forecast_churn(
            periods=periods, period_type=period_type, plan_id=plan_id
        )

ltv_forecast = self.forecast_ltv(periods=periods, plan_id=plan_id)

# Get scenario forecasts
        growth_scenarios = self.forecast_growth_scenarios(
            periods=periods, period_type=period_type, plan_id=plan_id
        )

revenue_scenarios = self.forecast_revenue_scenarios(
            periods=periods, period_type=period_type, plan_id=plan_id
        )

# Create summary
        summary = {
            "current": {
                "subscriptions": current_subscriptions,
                "mrr": current_mrr,
                "arpu": current_arpu,
                "churn_rate": current_churn_rate,
                "ltv": current_ltv,
            },
            "forecast": {
                "subscriptions": subscription_forecast,
                "revenue": revenue_forecast,
                "churn": churn_forecast,
                "ltv": ltv_forecast,
            },
            "scenarios": {"growth": growth_scenarios, "revenue": revenue_scenarios},
        }

            return summary


# Example usage
if __name__ == "__main__":
# Create a subscription manager
    manager = SubscriptionManager()

# Create a subscription plan
    plan = SubscriptionPlan(
        name="AI Tool Subscription",
        description="Subscription plan for an AI-powered tool",
    )

# Add tiers
    basic_tier = plan.add_tier(
        name="Basic",
        description="Essential features for individuals",
        price_monthly=9.99,
        trial_days=14,
    )

pro_tier = plan.add_tier(
        name="Pro",
        description="Advanced features for professionals",
        price_monthly=19.99,
        is_popular=True,
    )

# Add plan to manager
    manager.add_plan(plan)

# Create subscriptions
    for i in range(10):
        user_id = f"user{i+1}"
        tier_id = basic_tier["id"] if i < 7 else pro_tier["id"]

subscription = manager.create_subscription(
            user_id=user_id, plan_id=plan.id, tier_id=tier_id, billing_cycle="monthly"
        )

# Create metrics calculator
    metrics = SubscriptionMetrics(manager)

# Calculate metrics
    active_count = metrics.get_active_subscription_count()
    mrr = metrics.get_monthly_recurring_revenue()
    arr = metrics.get_annual_recurring_revenue()
    arpu = metrics.get_average_revenue_per_user()

print(f"Active subscriptions: {active_count}")
    print(f"MRR: ${mrr:.2f}")
    print(f"ARR: ${arr:.2f}")
    print(f"ARPU: ${arpu:.2f}")

# Get distribution
    distribution = metrics.get_subscription_distribution()

print("\nSubscription distribution:")
    for plan_id, tiers in distribution.items():
        plan_name = manager.get_plan(plan_id).name
        print(f"- {plan_name}:")

for tier_id, count in tiers.items():
            tier = manager.get_plan(plan_id).get_tier(tier_id)
            print(f"  - {tier['name']}: {count}")

# Get summary
    summary = metrics.get_subscription_summary()

print("\nSubscription summary:")
    print(f"Total subscriptions: {summary['total_count']}")
    print(f"Active subscriptions: {summary['active_count']}")
    print(f"Trial subscriptions: {summary['trial_count']}")
    print(f"MRR: ${summary['mrr']:.2f}")
    print(f"ARR: ${summary['arr']:.2f}")
    print(f"ARPU: ${summary['arpu']:.2f}")
    print(f"Subscription growth: {summary['subscription_growth']:.2f}%")
    print(f"Revenue growth: {summary['revenue_growth']:.2f}%")

# Create churn analysis
    churn = ChurnAnalysis(manager)

# Calculate churn metrics
    churn_rate = churn.get_churn_rate()
    retention_rate = churn.get_retention_rate()

print(f"\nChurn rate: {churn_rate:.2f}%")
    print(f"Retention rate: {retention_rate:.2f}%")

# Get churn by plan
    churn_by_plan = churn.get_churn_by_plan()

print("\nChurn by plan:")
    for plan_id, rate in churn_by_plan.items():
        plan_name = manager.get_plan(plan_id).name
        print(f"- {plan_name}: {rate:.2f}%")

# Get lifetime value
    ltv = churn.get_lifetime_value()

print(f"\nCustomer lifetime value: ${ltv:.2f}")

# Create forecasting
    forecasting = SubscriptionForecasting(manager, metrics, churn)

# Forecast subscriptions
    subscription_forecast = forecasting.forecast_subscriptions(periods=12)

print("\nSubscription forecast:")
    for period in subscription_forecast:
        print(
            f"Period {period['period']} ({period['date'][:10]}): {period['subscriptions']} subscriptions"
        )

# Forecast revenue
    revenue_forecast = forecasting.forecast_revenue(periods=12)

print("\nRevenue forecast:")
    for period in revenue_forecast:
        print(
            f"Period {period['period']} ({period['date'][:10]}): ${period['revenue']:.2f}"
        )

# Forecast scenarios
    scenarios = forecasting.forecast_revenue_scenarios(periods=12)

print("\nRevenue scenarios:")
    for scenario_name, forecast in scenarios.items():
        print(f"- {scenario_name}:")
        print(
            f"  Period 12 ({forecast[11]['date'][:10]}): ${forecast[11]['revenue']:.2f}"
        )