"""
Usage-based pricing demo for the pAIssive Income project.

This script demonstrates how to use the usage-based pricing models
to implement different pricing strategies.
"""

import random
from datetime import datetime, timedelta

from .usage_pricing_strategies import (
    ConsumptionBasedPricing,
    HybridUsagePricing,
    PayAsYouGoPricing,
    TieredUsagePricing,
)
from .usage_tracker import UsageTracker
from .usage_tracking import UsageCategory, UsageMetric


def print_separator():
    """Print a separator line."""
    print("\n" + "-" * 80 + "\n")


def print_section(title):
    """Print a section title."""
    print_separator()
    print(f"## {title}")
    print_separator()


def simulate_usage(tracker, customer_id, days=30):
    """
    Simulate usage for a customer over a period of days.

    Args:
        tracker: Usage tracker
        customer_id: Customer ID
        days: Number of days to simulate
    """
    start_date = datetime.now() - timedelta(days=days)

    # Simulate API calls
    for day in range(days):
        date = start_date + timedelta(days=day)

        # Simulate API calls (more on weekdays)
        is_weekend = date.weekday() >= 5
        api_calls = random.randint(10, 50) if is_weekend else random.randint(50, 200)

        tracker.record_usage(
            customer_id=customer_id,
            metric=UsageMetric.API_CALL,
            quantity=api_calls,
            timestamp=date,
            category=UsageCategory.INFERENCE,
        )

        # Simulate token usage
        tokens = api_calls * random.randint(50, 200)

        tracker.record_usage(
            customer_id=customer_id,
            metric=UsageMetric.TOKEN,
            quantity=tokens,
            timestamp=date,
            category=UsageCategory.INFERENCE,
        )

        # Simulate compute time
        compute_hours = api_calls * random.uniform(0.01, 0.05)

        tracker.record_usage(
            customer_id=customer_id,
            metric=UsageMetric.COMPUTE_TIME,
            quantity=compute_hours,
            timestamp=date,
            category=UsageCategory.COMPUTE,
            resource_type="cpu",
        )

        # Simulate storage (cumulative)
        storage_gb = 1.0 + (day * 0.2)  # Grows by 0.2 GB per day

        tracker.record_usage(
            customer_id=customer_id,
            metric=UsageMetric.STORAGE,
            quantity=storage_gb,
            timestamp=date,
            category=UsageCategory.STORAGE,
            resource_type="standard",
        )

        # Simulate bandwidth
        bandwidth_gb = api_calls * random.uniform(0.001, 0.005)

        tracker.record_usage(
            customer_id=customer_id,
            metric=UsageMetric.BANDWIDTH,
            quantity=bandwidth_gb,
            timestamp=date,
            category=UsageCategory.NETWORK,
            resource_type="outbound",
        )


def main():
    """Run the usage-based pricing demo."""
    print_section("Usage-Based Pricing Demo")

    # Create a usage tracker
    tracker = UsageTracker()

    # Create a customer
    customer_id = "customer123"

    # Simulate usage for the customer
    print("Simulating usage for customer...")
    simulate_usage(tracker, customer_id)

    # Get usage summary
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()

    usage_summary = tracker.get_usage_summary(
        customer_id=customer_id, start_time=start_date, end_time=end_date
    )

    print("Usage summary:")
    for metric, data in usage_summary.items():
        print(f"- {metric}: {data['total']} {data['unit']}")

    print_section("Pay-As-You-Go Pricing")

    # Create a pay-as-you-go pricing model
    payg_model = PayAsYouGoPricing()

    # Add pricing for API calls and tokens
    payg_model.add_metric_pricing(
        metric=UsageMetric.API_CALL,
        price_per_unit=0.01,
        category=UsageCategory.INFERENCE,
    )

    payg_model.add_metric_pricing(
        metric=UsageMetric.TOKEN,
        price_per_unit=0.0001,
        category=UsageCategory.INFERENCE,
    )

    # Calculate cost
    payg_cost = payg_model.calculate_cost(
        customer_id=customer_id, start_time=start_date, end_time=end_date
    )

    print(f"Pay-As-You-Go cost: ${payg_cost['total']:.2f}")
    print("Breakdown:")
    for metric, cost in payg_cost["breakdown"].items():
        print(f"- {metric}: ${cost:.2f}")

    print_section("Tiered Usage Pricing")

    # Create a tiered usage pricing model
    tiered_model = TieredUsagePricing(graduated=True)

    # Add tiered pricing for API calls
    tiered_model.add_metric_pricing(
        metric=UsageMetric.API_CALL,
        tiers=[
            {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.01},
            {"min_quantity": 1000, "max_quantity": 5000, "price_per_unit": 0.008},
            {"min_quantity": 5000, "max_quantity": None, "price_per_unit": 0.005},
        ],
        category=UsageCategory.INFERENCE,
    )

    # Add tiered pricing for tokens
    tiered_model.add_metric_pricing(
        metric=UsageMetric.TOKEN,
        tiers=[
            {"min_quantity": 0, "max_quantity": 100000, "price_per_unit": 0.0001},
            {"min_quantity": 100000, "max_quantity": 500000, "price_per_unit": 0.00008},
            {"min_quantity": 500000, "max_quantity": None, "price_per_unit": 0.00005},
        ],
        category=UsageCategory.INFERENCE,
    )

    # Calculate cost
    tiered_cost = tiered_model.calculate_cost(
        customer_id=customer_id, start_time=start_date, end_time=end_date
    )

    print(f"Tiered Usage cost: ${tiered_cost['total']:.2f}")
    print("Breakdown:")
    for metric, cost in tiered_cost["breakdown"].items():
        print(f"- {metric}: ${cost:.2f}")

    print_section("Consumption-Based Pricing")

    # Create a consumption-based pricing model
    consumption_model = ConsumptionBasedPricing()

    # Add pricing for compute, storage, and bandwidth
    consumption_model.add_compute_pricing(price_per_hour=0.10, resource_type="cpu")
    consumption_model.add_storage_pricing(price_per_gb=0.05, resource_type="standard")
    consumption_model.add_bandwidth_pricing(price_per_gb=0.08, resource_type="outbound")

    # Calculate cost
    consumption_cost = consumption_model.calculate_cost(
        customer_id=customer_id, start_time=start_date, end_time=end_date
    )

    print(f"Consumption-Based cost: ${consumption_cost['total']:.2f}")
    print("Breakdown:")
    for metric, cost in consumption_cost["breakdown"].items():
        print(f"- {metric}: ${cost:.2f}")

    print_section("Hybrid Usage Pricing")

    # Create a hybrid usage pricing model
    hybrid_model = HybridUsagePricing(base_fee=9.99)

    # Add included usage with overage pricing
    hybrid_model.add_included_usage(
        metric=UsageMetric.API_CALL,
        quantity=1000,
        overage_price=0.005,
        category=UsageCategory.INFERENCE,
    )

    hybrid_model.add_included_usage(
        metric=UsageMetric.TOKEN,
        quantity=100000,
        overage_price=0.00005,
        category=UsageCategory.INFERENCE,
    )

    hybrid_model.add_included_usage(
        metric=UsageMetric.STORAGE,
        quantity=5.0,  # GB
        overage_price=0.03,  # per GB
        category=UsageCategory.STORAGE,
    )

    # Calculate cost
    hybrid_cost = hybrid_model.calculate_cost(
        customer_id=customer_id, start_time=start_date, end_time=end_date
    )

    print(f"Hybrid Usage cost: ${hybrid_cost['total']:.2f}")
    print("Breakdown:")
    for metric, cost in hybrid_cost["breakdown"].items():
        print(f"- {metric}: ${cost:.2f}")

    print_section("Pricing Comparison")

    print(f"Pay-As-You-Go cost: ${payg_cost['total']:.2f}")
    print(f"Tiered Usage cost: ${tiered_cost['total']:.2f}")
    print(f"Consumption-Based cost: ${consumption_cost['total']:.2f}")
    print(f"Hybrid Usage cost: ${hybrid_cost['total']:.2f}")


if __name__ == "__main__":
    main()
