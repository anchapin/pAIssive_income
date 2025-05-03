"""
Subscription analytics demo for the pAIssive Income project.

This script demonstrates how to use the subscription analytics functionality.
"""


import random
from datetime import datetime, timedelta

from .subscription import SubscriptionPlan
from .subscription_analytics import 
from .subscription_manager import SubscriptionManager
from .user_subscription import SubscriptionStatus


def print_separator():
    (
    ChurnAnalysis,
    SubscriptionForecasting,
    SubscriptionMetrics,
)
():
    """Print a separator line."""
    print("\n" + "-" * 80 + "\n")


def run_demo():
    """Run the subscription analytics demo."""
    print("Subscription Analytics Demo")
    print_separator()

# Create a subscription manager
    manager = SubscriptionManager()

# Create subscription plans
    basic_plan = SubscriptionPlan(
        name="Basic Plan", description="Essential features for individuals"
    )

# Add tiers to basic plan
    basic_tier = basic_plan.add_tier(
        name="Basic", description="Core features", price_monthly=9.99, trial_days=14
    )

plus_tier = basic_plan.add_tier(
        name="Plus",
        description="Additional features",
        price_monthly=19.99,
        is_popular=True,
    )

# Create premium plan
    premium_plan = SubscriptionPlan(
        name="Premium Plan", description="Advanced features for professionals"
    )

# Add tiers to premium plan
    pro_tier = premium_plan.add_tier(
        name="Pro", description="Professional features", price_monthly=49.99
    )

enterprise_tier = premium_plan.add_tier(
        name="Enterprise", description="Enterprise-grade features", price_monthly=99.99
    )

# Add plans to manager
    manager.add_plan(basic_plan)
    manager.add_plan(premium_plan)

print("Created subscription plans:")
    print(f"- {basic_plan.name}")
    print(f"  - {basic_tier['name']}: ${basic_tier['price_monthly']:.2f}/month")
    print(f"  - {plus_tier['name']}: ${plus_tier['price_monthly']:.2f}/month")
    print(f"- {premium_plan.name}")
    print(f"  - {pro_tier['name']}: ${pro_tier['price_monthly']:.2f}/month")
    print(
        f"  - {enterprise_tier['name']}: ${enterprise_tier['price_monthly']:.2f}/month"
    )

print_separator()

# Create subscriptions
    print("Creating sample subscriptions...")

# Create active subscriptions
    for i in range(50):
        user_id = f"user{i+1}"

# Determine plan and tier
        if i < 30:  # 60% basic plan
            plan = basic_plan
            if i < 20:  # 40% basic tier
                tier = basic_tier
            else:  # 20% plus tier
                tier = plus_tier
        else:  # 40% premium plan
            plan = premium_plan
            if i < 45:  # 30% pro tier
                tier = pro_tier
            else:  # 10% enterprise tier
                tier = enterprise_tier

# Create subscription
        subscription = manager.create_subscription(
            user_id=user_id,
            plan_id=plan.id,
            tier_id=tier["id"],
            billing_cycle="monthly",
        )

# Set some subscriptions to trial
        if i < 10:
            subscription.status = SubscriptionStatus.TRIAL
            subscription.trial_end = datetime.now() + timedelta(days=14)

# Create canceled subscriptions
    for i in range(10):
        user_id = f"canceled_user{i+1}"

# Create subscription
        subscription = manager.create_subscription(
            user_id=user_id,
            plan_id=basic_plan.id,
            tier_id=basic_tier["id"],
            billing_cycle="monthly",
        )

# Cancel subscription
        subscription.status = SubscriptionStatus.CANCELED
        subscription.canceled_at = datetime.now() - timedelta(
            days=random.randint(1, 30)
        )

# Add cancellation reason to some subscriptions
        if i < 5:
            reasons = [
                "Too expensive for my needs",
                "Missing features I need",
                "Found a better alternative",
                "Difficult to use",
                "Poor customer support",
            ]
            subscription.set_metadata("cancellation_reason", reasons[i])

# Create past due subscriptions
    for i in range(5):
        user_id = f"pastdue_user{i+1}"

# Create subscription
        subscription = manager.create_subscription(
            user_id=user_id,
            plan_id=basic_plan.id,
            tier_id=basic_tier["id"],
            billing_cycle="monthly",
        )

# Set to past due
        subscription.status = SubscriptionStatus.PAST_DUE

print(f"Created {len(manager.subscriptions)} subscriptions")

print_separator()

# Create metrics calculator
    metrics = SubscriptionMetrics(manager)

# Calculate basic metrics
    active_count = metrics.get_active_subscription_count()
    trial_count = metrics.get_trial_subscription_count()
    canceled_count = metrics.get_canceled_subscription_count()

mrr = metrics.get_monthly_recurring_revenue()
    arr = metrics.get_annual_recurring_revenue()
    arpu = metrics.get_average_revenue_per_user()

print("Basic Subscription Metrics:")
    print(f"Active subscriptions: {active_count}")
    print(f"Trial subscriptions: {trial_count}")
    print(f"Canceled subscriptions: {canceled_count}")
    print(f"MRR: ${mrr:.2f}")
    print(f"ARR: ${arr:.2f}")
    print(f"ARPU: ${arpu:.2f}")

# Get revenue by plan
    revenue_by_plan = metrics.get_revenue_by_plan()

print("\nRevenue by Plan:")
    for plan_id, revenue in revenue_by_plan.items():
        plan = manager.get_plan(plan_id)
        print(f"- {plan.name}: ${revenue:.2f}/month")

# Get subscription distribution
    distribution = metrics.get_subscription_distribution()

print("\nSubscription Distribution:")
    for plan_id, tiers in distribution.items():
        plan = manager.get_plan(plan_id)
        print(f"- {plan.name}:")

for tier_id, count in tiers.items():
            tier = plan.get_tier(tier_id)
            print(f"  - {tier['name']}: {count} subscriptions")

print_separator()

# Create churn analysis
    churn = ChurnAnalysis(manager)

# Calculate churn metrics
    churn_rate = churn.get_churn_rate()
    retention_rate = churn.get_retention_rate()

print("Churn Analysis:")
    print(f"Churn rate: {churn_rate:.2f}%")
    print(f"Retention rate: {retention_rate:.2f}%")

# Get churn by plan
    churn_by_plan = churn.get_churn_by_plan()

print("\nChurn by Plan:")
    for plan_id, rate in churn_by_plan.items():
        plan = manager.get_plan(plan_id)
        print(f"- {plan.name}: {rate:.2f}%")

# Get churn reasons
    churn_reasons = churn.get_churn_reasons()

print("\nChurn Reasons:")
    for reason, count in churn_reasons.items():
        print(f"- {reason}: {count}")

# Get lifetime value
    ltv = churn.get_lifetime_value()

print(f"\nCustomer Lifetime Value: ${ltv:.2f}")

# Get at-risk subscriptions
    at_risk = churn.get_at_risk_subscriptions()

print(f"\nAt-Risk Subscriptions: {len(at_risk)}")
    for i, subscription in enumerate(at_risk[:3]):
        print(
            f"- User {subscription['user_id']}: {subscription['churn_probability']:.2f}% probability of churning"
        )

print_separator()

# Create forecasting
    forecasting = SubscriptionForecasting(manager, metrics, churn)

# Forecast subscriptions
    subscription_forecast = forecasting.forecast_subscriptions(periods=12)

print("Subscription Forecast:")
    print(f"Current: {active_count} subscriptions")
    print(f"Month 3: {subscription_forecast[2]['subscriptions']} subscriptions")
    print(f"Month 6: {subscription_forecast[5]['subscriptions']} subscriptions")
    print(f"Month 12: {subscription_forecast[11]['subscriptions']} subscriptions")

# Forecast revenue
    revenue_forecast = forecasting.forecast_revenue(periods=12)

print("\nRevenue Forecast:")
    print(f"Current: ${mrr:.2f}/month")
    print(f"Month 3: ${revenue_forecast[2]['revenue']:.2f}/month")
    print(f"Month 6: ${revenue_forecast[5]['revenue']:.2f}/month")
    print(f"Month 12: ${revenue_forecast[11]['revenue']:.2f}/month")

# Forecast scenarios
    scenarios = forecasting.forecast_revenue_scenarios(periods=12)

print("\nRevenue Scenarios (Month 12):")
    for scenario_name, forecast in scenarios.items():
        print(f"- {scenario_name}: ${forecast[11]['revenue']:.2f}/month")

# Forecast breakeven
    breakeven = forecasting.forecast_breakeven(
        fixed_costs=5000.0, variable_cost_per_user=2.0, periods=24
    )

if breakeven:
        print(
            f"\nBreakeven Point: Month {breakeven['period']} with ${breakeven['revenue']:.2f} revenue"
        )
    else:
        print("\nNo breakeven point found within 24 months")

print_separator()

# Get forecast summary
    summary = forecasting.forecast_summary()

print("Forecast Summary:")
    print(f"Current MRR: ${summary['current']['mrr']:.2f}")
    print(f"Current Churn Rate: {summary['current']['churn_rate']:.2f}%")
    print(f"Current LTV: ${summary['current']['ltv']:.2f}")

print("\nMonth 12 Projections:")
    print(f"Subscriptions: {summary['forecast']['subscriptions'][11]['subscriptions']}")
    print(f"MRR: ${summary['forecast']['revenue'][11]['revenue']:.2f}")
    print(f"Churn Rate: {summary['forecast']['churn'][11]['churn_rate']:.2f}%")
    print(f"LTV: ${summary['forecast']['ltv'][11]['ltv']:.2f}")

print_separator()

print("Demo completed successfully!")


if __name__ == "__main__":
    run_demo()