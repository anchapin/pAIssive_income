"""
Simple test script for the metered billing module.

This script tests the basic functionality of the metered billing module
without relying on the unittest framework.
"""

from datetime import datetime, timedelta

# Use absolute imports
from monetization.metered_billing import MeteredBillingPricing, MeteringInterval
from monetization.usage_tracking import UsageMetric, UsageCategory


def test_metering_intervals():
    """Test different metering intervals."""
    print("Testing metering intervals...")

    # Create a metered billing model
    model = MeteredBillingPricing(
        name="Test Metered Billing",
        description="Test metered billing model",
        metering_interval=MeteringInterval.HOURLY
    )

    # Test hourly interval
    model.set_metering_interval(MeteringInterval.HOURLY)
    start, end = model.get_interval_start_end()
    print(f"Hourly interval: {start} to {end}")
    print(f"Duration: {(end - start).total_seconds() / 3600:.1f} hours")

    # Test daily interval
    model.set_metering_interval(MeteringInterval.DAILY)
    start, end = model.get_interval_start_end()
    print(f"Daily interval: {start} to {end}")
    print(f"Duration: {(end - start).total_seconds() / 3600:.1f} hours")

    # Test weekly interval
    model.set_metering_interval(MeteringInterval.WEEKLY)
    start, end = model.get_interval_start_end()
    print(f"Weekly interval: {start} to {end}")
    print(f"Duration: {(end - start).total_seconds() / 3600:.1f} hours")

    # Test monthly interval
    model.set_metering_interval(MeteringInterval.MONTHLY)
    start, end = model.get_interval_start_end()
    print(f"Monthly interval: {start} to {end}")
    print(f"Duration: {(end - start).total_seconds() / 3600:.1f} hours")

    print("Metering intervals test completed.\n")


def test_custom_billing_period():
    """Test custom billing periods."""
    print("Testing custom billing periods...")

    # Create a metered billing model
    model = MeteredBillingPricing(
        name="Test Metered Billing",
        description="Test metered billing model",
        metering_interval=MeteringInterval.MONTHLY
    )

    customer_id = "customer123"

    # Get the default billing period
    default_start, default_end = model.get_interval_start_end(customer_id=customer_id)
    print(f"Default billing period: {default_start} to {default_end}")

    # Set a custom billing period
    custom_start = datetime.now() - timedelta(days=5)
    custom_end = custom_start + timedelta(days=10)

    model.set_custom_billing_period(
        customer_id=customer_id,
        start_time=custom_start,
        end_time=custom_end
    )

    # Get the custom billing period
    custom_start_result, custom_end_result = model.get_interval_start_end(customer_id=customer_id)
    print(f"Custom billing period: {custom_start_result} to {custom_end_result}")

    # Verify that the custom period is used
    if custom_start_result == custom_start and custom_end_result == custom_end:
        print("Custom billing period is working correctly.")
    else:
        print("Custom billing period is not working correctly.")

    print("Custom billing periods test completed.\n")


def main():
    """Run the tests."""
    print("=== Metered Billing Simple Tests ===\n")

    test_metering_intervals()
    test_custom_billing_period()

    print("All tests completed.")


if __name__ == "__main__":
    main()
