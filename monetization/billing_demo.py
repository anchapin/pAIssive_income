"""
Billing calculation demo for the pAIssive Income project.

This script demonstrates how to use the billing calculation system.
"""

import random
from datetime import datetime, timedelta

from .prorated_billing import ProratedBilling
from .tiered_pricing import TieredPricingCalculator
from .usage_tracker import UsageTracker
from .usage_tracking import (
    UsageCategory,
    UsageLimit,
    UsageMetric,
)


def print_separator():
    """Print a separator line."""
    print("\n" + " - " * 80 + "\n")


def run_demo():
    """Run the billing calculation demo."""
    print("Billing Calculation Demo")
    print_separator()

    # Create a usage tracker
    tracker = UsageTracker(storage_dir="usage_data")

    # Create a customer
    customer_id = "cust_demo_123"

    print(f"Setting up usage tracking for customer: {customer_id}")

    # Add usage limits
    limits = [
        UsageLimit(
            customer_id=customer_id,
            metric=UsageMetric.API_CALL,
            max_quantity=1000,
            period=UsageLimit.PERIOD_MONTHLY,
            category=UsageCategory.INFERENCE,
            resource_type="model",
            metadata={"tier": "basic"},
        ),
        UsageLimit(
            customer_id=customer_id,
            metric=UsageMetric.TOKEN,
            max_quantity=100000,
            period=UsageLimit.PERIOD_MONTHLY,
            category=UsageCategory.INFERENCE,
            resource_type="model",
            metadata={"tier": "basic"},
        ),
        UsageLimit(
            customer_id=customer_id,
            metric=UsageMetric.STORAGE,
            max_quantity=10.0,  # GB
            period=UsageLimit.PERIOD_MONTHLY,
            category=UsageCategory.STORAGE,
            resource_type="storage",
            metadata={"tier": "basic"},
        ),
    ]

    for limit in limits:
        tracker.add_limit(limit)
        print(f"Added limit: {limit}")

    print_separator()

    # Generate random usage data
    print("Generating random usage data...")

    # Define metrics and categories
    metrics = [UsageMetric.API_CALL, UsageMetric.TOKEN, UsageMetric.STORAGE]

    categories = [
        UsageCategory.INFERENCE,
        UsageCategory.TRAINING,
        UsageCategory.STORAGE,
    ]

    resource_types = ["model", "storage"]

    # Generate random usage records
    now = datetime.now()
    start_date = now - timedelta(days=30)

    for i in range(100):
        # Random timestamp within the last 30 days
        days_ago = random.uniform(0, 30)
        timestamp = now - timedelta(days=days_ago)

        # Random metric, category, and resource type
        metric = random.choice(metrics)

        if metric == UsageMetric.STORAGE:
            category = UsageCategory.STORAGE
            resource_type = "storage"
        else:
            category = random.choice([UsageCategory.INFERENCE, UsageCategory.TRAINING])
            resource_type = "model"

        # Random quantity
        if metric == UsageMetric.API_CALL:
            quantity = random.randint(1, 10)
        elif metric == UsageMetric.TOKEN:
            quantity = random.randint(100, 1000)
        elif metric == UsageMetric.STORAGE:
            quantity = random.uniform(0.1, 0.5)
        else:
            quantity = random.uniform(1, 10)

        # Track usage
        tracker.track_usage(
            customer_id=customer_id,
            metric=metric,
            quantity=quantity,
            category=category,
            resource_type=resource_type,
            timestamp=timestamp,
            check_quota=False,  # Don't check quota for historical data
        )

    print("Generated 100 random usage records")

    print_separator()

    # Create a billing calculator
    print("Setting up billing calculator...")

    calculator = TieredPricingCalculator(usage_tracker=tracker)

    # Add pricing rules
    calculator.create_per_unit_pricing_rule(
        metric=UsageMetric.API_CALL,
        price_per_unit=0.01,
        category=UsageCategory.INFERENCE,
        resource_type="model",
    )

    calculator.create_per_unit_pricing_rule(
        metric=UsageMetric.API_CALL,
        price_per_unit=0.02,
        category=UsageCategory.TRAINING,
        resource_type="model",
    )

    calculator.create_tiered_pricing_rule_with_discounts(
        metric=UsageMetric.TOKEN,
        tiers=[
            {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.001},
            {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0008},
            {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.0005},
        ],
        volume_discounts=[
            {"min_quantity": 100000, "discount_percentage": 10},
            {"min_quantity": 1000000, "discount_percentage": 20},
        ],
        graduated=True,
        category=UsageCategory.INFERENCE,
        resource_type="model",
    )

    calculator.create_tiered_pricing_rule(
        metric=UsageMetric.TOKEN,
        tiers=[
            {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.002},
            {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0015},
            {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.001},
        ],
        graduated=True,
        category=UsageCategory.TRAINING,
        resource_type="model",
    )

    calculator.create_package_pricing_rule(
        metric=UsageMetric.STORAGE,
        quantity=10.0,  # GB
        price=5.0,
        overage_price=0.5,  # per GB
        category=UsageCategory.STORAGE,
        resource_type="storage",
    )

    print("Added pricing rules")

    print_separator()

    # Calculate usage cost
    print("Calculating usage cost...")

    usage_cost = calculator.calculate_usage_cost(
        customer_id=customer_id, start_time=start_date, end_time=now
    )

    print(f"Usage cost for {customer_id}:")
    print(f"Total cost: ${usage_cost['total_cost']:.2f}")

    print("\nCost breakdown:")
    for item in usage_cost["items"]:
        print(
            f"- {item['metric']} ({item['category']}, 
                {item['resource_type']}): {item['quantity']} units, ${item['cost']:.2f}"
        )

    print_separator()

    # Get detailed cost breakdown for tokens
    token_usage = sum(
        item["quantity"]
        for item in usage_cost["items"]
        if item["metric"] == \
            UsageMetric.TOKEN and item["category"] == UsageCategory.INFERENCE
    )

    print(f"Detailed cost breakdown for {token_usage} tokens (inference):")

    breakdown = calculator.calculate_tiered_cost_breakdown(
        metric=UsageMetric.TOKEN,
        quantity=token_usage,
        category=UsageCategory.INFERENCE,
        resource_type="model",
    )

    print(f"Model: {breakdown['model']}")

    print("\nTiers:")
    for tier in breakdown["tiers"]:
        max_str = str(tier["max_quantity"]) if tier["max_quantity"] is not None else "∞"
        print(
            f"- {tier['min_quantity']}-{max_str}: {tier['quantity']} units at ${tier['price_per_unit']}/unit = ${tier['cost']:.2f}"
        )

    print(f"\nSubtotal: ${breakdown['subtotal']:.2f}")

    if breakdown["volume_discount"]:
        discount = breakdown["volume_discount"]
        print(
            f"Volume discount: {discount['discount_percentage']}% off for {discount['min_quantity']}+ units = -${discount['discount_amount']:.2f}"
        )

    print(f"Total: ${breakdown['total']:.2f}")

    print_separator()

    # Demonstrate prorated billing
    print("Demonstrating prorated billing...")

    # Calculate prorated billing for an upgrade
    upgrade_result = ProratedBilling.calculate_plan_change(
        old_plan_amount=10.0,
        new_plan_amount=20.0,
        current_date=datetime.now(),
        period_start_date=datetime(datetime.now().year, datetime.now().month, 1),
        period="monthly",
    )

    print("Upgrade Example:")
    print(f"Old plan: ${upgrade_result['old_plan_amount']:.2f}")
    print(f"New plan: ${upgrade_result['new_plan_amount']:.2f}")
    print(f"Days in period: {upgrade_result['days_in_period']}")
    print(f"Days used: {upgrade_result['days_used']}")
    print(f"Days remaining: {upgrade_result['days_remaining']}")
    print(f"Old plan used: ${upgrade_result['old_plan_used']:.2f}")
    print(f"Old plan remaining: ${upgrade_result['old_plan_remaining']:.2f}")
    print(f"New plan remaining: ${upgrade_result['new_plan_remaining']:.2f}")
    print(f"Difference: ${upgrade_result['difference']:.2f}")
    print(f"Action: {upgrade_result['action']} ${upgrade_result['amount']:.2f}")

    print_separator()

    # Estimate future costs
    print("Estimating future costs...")

    estimated_cost = calculator.estimate_cost(
        {
            UsageMetric.API_CALL: {
                UsageCategory.INFERENCE: 5000,
                UsageCategory.TRAINING: 1000,
            },
            UsageMetric.TOKEN: {
                UsageCategory.INFERENCE: 500000,
                UsageCategory.TRAINING: 100000,
            },
            UsageMetric.STORAGE: {UsageCategory.STORAGE: 15.0},
        }
    )

    print(f"Estimated total cost: ${estimated_cost['total_cost']:.2f}")

    print("\nCost breakdown:")
    for item in estimated_cost["items"]:
        print(
            f"- {item['metric']} ({item['category']}): {item['quantity']} units, 
                ${item['cost']:.2f}"
        )

    print_separator()

    print("Demo completed successfully!")


if __name__ == "__main__":
    run_demo()
