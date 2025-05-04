"""
Metered billing demo for the pAIssive Income project.

This script demonstrates how to use the metered billing model
to implement usage-based billing with precise metering.
"""


import random
import time
from datetime import datetime, timedelta

from .metered_billing import MeteredBillingPricing, MeteringInterval
from .usage_tracking import UsageCategory, UsageMetric


def print_section():
    (title: str) -> None:
    """Print a section title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


    def print_separator() -> None:
    """Print a separator line."""
    print("\n" + "-" * 80 + "\n")


    def simulate_real_time_usage(
    model: MeteredBillingPricing,
    customer_id: str,
    duration_seconds: int = 60,
    interval_seconds: int = 5,
    ) -> None:
    """
    Simulate real-time usage over a period of time.

    Args:
    model: Metered billing model
    customer_id: ID of the customer
    duration_seconds: Duration of the simulation in seconds
    interval_seconds: Interval between usage events in seconds
    """
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=duration_seconds)

    print(f"Simulating real-time usage for {duration_seconds} seconds...")
    print(f"Start time: {start_time}")
    print(f"End time: {end_time}")

    iteration = 0

    while datetime.now() < end_time:
    iteration += 1

    # Simulate API calls
    api_calls = random.randint(1, 10)

    # Track usage
    result = model.track_usage_and_bill(
    customer_id=customer_id,
    metric=UsageMetric.API_CALL,
    quantity=api_calls,
    category=UsageCategory.INFERENCE,
    resource_id="model_gpt4",
    resource_type="model",
    metadata={"endpoint": "/v1/completions", "iteration": iteration},
    )

    # Simulate token usage
    tokens = api_calls * random.randint(50, 200)

    # Track usage
    token_result = model.track_usage_and_bill(
    customer_id=customer_id,
    metric=UsageMetric.TOKEN,
    quantity=tokens,
    category=UsageCategory.INFERENCE,
    resource_id="model_gpt4",
    resource_type="model",
    metadata={"endpoint": "/v1/completions", "iteration": iteration},
    )

    # Update result with token cost
    result["current_cost"] = token_result["current_cost"]
    result["cost_breakdown"] = token_result["cost_breakdown"]

    # Print progress
    elapsed = (datetime.now() - start_time).total_seconds()
    progress = min(100, elapsed / duration_seconds * 100)

    print(
    f"[{progress:.1f}%] Iteration {iteration}: {api_calls} API calls, {tokens} tokens"
    )
    print(f"Current cost: ${result['current_cost']:.4f}")
    print(f"Cost breakdown: {result['cost_breakdown']}")

    if "invoice" in result:
    print(f"Invoice generated: {result['invoice']}")

    print()

    # Wait for the next interval
    time.sleep(interval_seconds)


    def simulate_different_metering_intervals(customer_id: str) -> None:
    """
    Simulate different metering intervals.

    Args:
    customer_id: ID of the customer
    """
    intervals = [
    MeteringInterval.HOURLY,
    MeteringInterval.DAILY,
    MeteringInterval.WEEKLY,
    MeteringInterval.MONTHLY,
    ]

    for interval in intervals:
    print_separator()
    print(f"Metering interval: {interval}")

    # Create a metered billing model with this interval
    model = MeteredBillingPricing(
    name=f"{interval.capitalize()} Metered Billing",
    description=f"Pay only for what you use with {interval} metering",
    metering_interval=interval,
    )

    # Add metered metrics
    model.add_metered_metric(
    metric=UsageMetric.API_CALL,
    price_per_unit=0.01,
    category=UsageCategory.INFERENCE,
    )

    # Get the current billing period
    start_time, end_time = model.get_interval_start_end(customer_id=customer_id)

    print(f"Current billing period: {start_time} to {end_time}")
    print(f"Duration: {(end_time - start_time).total_seconds() / 3600:.1f} hours")

    # Track some usage
    result = model.track_usage_and_bill(
    customer_id=customer_id,
    metric=UsageMetric.API_CALL,
    quantity=100,
    category=UsageCategory.INFERENCE,
    )

    print(f"Tracked usage: {result['quantity']} {result['metric']}")
    print(f"Current cost: ${result['current_cost']:.2f}")


    def demonstrate_minimum_maximum_billing(customer_id: str) -> None:
    """
    Demonstrate minimum and maximum billing amounts.

    Args:
    customer_id: ID of the customer
    """
    print_separator()
    print("Minimum and Maximum Billing Amounts")

    # Create a metered billing model with minimum and maximum amounts
    model = MeteredBillingPricing(
    name="Bounded Metered Billing",
    description="Pay only for what you use, with minimum and maximum limits",
    metering_interval=MeteringInterval.DAILY,
    minimum_bill_amount=5.0,
    maximum_bill_amount=20.0,
    )

    # Add metered metrics
    model.add_metered_metric(
    metric=UsageMetric.API_CALL,
    price_per_unit=0.01,
    category=UsageCategory.INFERENCE,
    )

    # Test with low usage (below minimum)
    low_result = model.track_usage_and_bill(
    customer_id=customer_id,
    metric=UsageMetric.API_CALL,
    quantity=10,  # $0.10 worth of usage
    category=UsageCategory.INFERENCE,
    )

    print("Low usage scenario (below minimum):")
    print(f"Tracked usage: {low_result['quantity']} {low_result['metric']}")
    print(f"Raw cost: ${low_result['cost_breakdown'].get(UsageMetric.API_CALL, 0):.2f}")

    # Generate invoice to see minimum applied
    low_invoice = model.generate_invoice(customer_id=customer_id)
    print(f"Invoice amount (with minimum applied): ${low_invoice['total_amount']:.2f}")

    # Test with high usage (above maximum)
    high_result = model.track_usage_and_bill(
    customer_id=customer_id,
    metric=UsageMetric.API_CALL,
    quantity=3000,  # $30.00 worth of usage
    category=UsageCategory.INFERENCE,
    )

    print("\nHigh usage scenario (above maximum):")
    print(f"Tracked usage: {high_result['quantity']} {high_result['metric']}")
    print(
    f"Raw cost: ${high_result['cost_breakdown'].get(UsageMetric.API_CALL, 0):.2f}"
    )

    # Generate invoice to see maximum applied
    high_invoice = model.generate_invoice(customer_id=customer_id)
    print(f"Invoice amount (with maximum applied): ${high_invoice['total_amount']:.2f}")


    def demonstrate_custom_billing_period(customer_id: str) -> None:
    """
    Demonstrate custom billing periods.

    Args:
    customer_id: ID of the customer
    """
    print_separator()
    print("Custom Billing Periods")

    # Create a metered billing model
    model = MeteredBillingPricing(
    name="Custom Period Billing",
    description="Pay only for what you use with custom billing periods",
    metering_interval=MeteringInterval.MONTHLY,
    )

    # Add metered metrics
    model.add_metered_metric(
    metric=UsageMetric.API_CALL,
    price_per_unit=0.01,
    category=UsageCategory.INFERENCE,
    )

    # Get the default billing period
    default_start, default_end = model.get_interval_start_end(customer_id=customer_id)

    print(f"Default billing period: {default_start} to {default_end}")

    # Set a custom billing period
    custom_start = datetime.now() - timedelta(days=5)
    custom_end = custom_start + timedelta(days=10)

    model.set_custom_billing_period(
    customer_id=customer_id, start_time=custom_start, end_time=custom_end
    )

    # Get the custom billing period
    custom_start_result, custom_end_result = model.get_interval_start_end(
    customer_id=customer_id
    )

    print(f"Custom billing period: {custom_start_result} to {custom_end_result}")

    # Track some usage
    result = model.track_usage_and_bill(
    customer_id=customer_id,
    metric=UsageMetric.API_CALL,
    quantity=100,
    category=UsageCategory.INFERENCE,
    )

    print(f"Tracked usage: {result['quantity']} {result['metric']}")
    print(f"Current cost: ${result['current_cost']:.2f}")


    def main() -> None:
    """Run the metered billing demo."""
    print_section("Metered Billing Demo")

    # Create a customer
    customer_id = "customer123"

    # Create a metered billing model
    model = MeteredBillingPricing(
    name="API Metered Billing",
    description="Pay only for the API calls you make",
    metering_interval=MeteringInterval.HOURLY,
    )

    # Add metered metrics
    model.add_metered_metric(
    metric=UsageMetric.API_CALL,
    price_per_unit=0.01,
    category=UsageCategory.INFERENCE,
    )

    model.add_metered_tiered_metric(
    metric=UsageMetric.TOKEN,
    tiers=[
    {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.001},
    {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0008},
    {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.0005},
    ],
    category=UsageCategory.INFERENCE,
    )

    # Demonstrate real-time usage tracking
    print_section("Real-Time Usage Tracking")
    simulate_real_time_usage(
    model, customer_id, duration_seconds=30, interval_seconds=5
    )

    # Demonstrate different metering intervals
    print_section("Different Metering Intervals")
    simulate_different_metering_intervals(customer_id)

    # Demonstrate minimum and maximum billing
    print_section("Minimum and Maximum Billing")
    demonstrate_minimum_maximum_billing(customer_id)

    # Demonstrate custom billing periods
    print_section("Custom Billing Periods")
    demonstrate_custom_billing_period(customer_id)

    print_section("Demo Complete")


    if __name__ == "__main__":
    main()