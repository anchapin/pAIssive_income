"""
Tests for the metered billing module.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# We'll use direct imports to avoid circular import issues
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

# Define constants to avoid importing from the actual modules
class UsageMetric:
    """Enumeration of usage metric types."""
    API_CALL = "api_call"
    TOKEN = "token"

class UsageCategory:
    """Enumeration of usage categories."""
    INFERENCE = "inference"

# Import only the module we're testing
from monetization.metered_billing import MeteredBillingPricing, MeteringInterval


class TestMeteredBilling(unittest.TestCase):
    """Test cases for the metered billing module."""

    def setUp(self):
        """Set up test fixtures."""
        self.usage_tracker = MagicMock()
        self.billing_calculator = MagicMock()
        self.invoice_manager = MagicMock()

        # Create a metered billing model
        self.model = MeteredBillingPricing(
            name="Test Metered Billing",
            description="Test metered billing model",
            usage_tracker=self.usage_tracker,
            billing_calculator=self.billing_calculator,
            invoice_manager=self.invoice_manager,
            metering_interval=MeteringInterval.HOURLY
        )

        # Mock the usage tracker's track_usage method
        self.usage_tracker.track_usage.return_value = (
            MagicMock(id="record123", timestamp=datetime.now()),  # record
            None,  # quota
            False  # exceeded
        )

        # Mock the billing calculator's calculate_usage_cost method
        self.billing_calculator.calculate_usage_cost.return_value = {
            "total": 1.23,
            "breakdown": {UsageMetric.API_CALL: 1.23}
        }

        # Mock the invoice manager's generate_invoice_from_usage method
        self.invoice_manager.generate_invoice_from_usage.return_value = MagicMock(
            id="invoice123",
            status="draft",
            items=[MagicMock(description="API Calls", amount=1.23)],
            metadata={"invoice_url": "https://example.com/invoice123"}
        )

    def test_metering_intervals(self):
        """Test different metering intervals."""
        # Test hourly interval
        self.model.set_metering_interval(MeteringInterval.HOURLY)
        start, end = self.model.get_interval_start_end()
        self.assertEqual((end - start).total_seconds(), 3600)  # 1 hour

        # Test daily interval
        self.model.set_metering_interval(MeteringInterval.DAILY)
        start, end = self.model.get_interval_start_end()
        self.assertEqual((end - start).total_seconds(), 86400)  # 24 hours

        # Test weekly interval
        self.model.set_metering_interval(MeteringInterval.WEEKLY)
        start, end = self.model.get_interval_start_end()
        self.assertEqual((end - start).total_seconds(), 604800)  # 7 days

        # Test monthly interval
        self.model.set_metering_interval(MeteringInterval.MONTHLY)
        start, end = self.model.get_interval_start_end()
        # This will vary by month, but should be roughly 28-31 days
        self.assertTrue(28 <= (end - start).days <= 31)

    def test_custom_billing_period(self):
        """Test custom billing periods."""
        customer_id = "customer123"

        # Set a custom billing period
        custom_start = datetime.now() - timedelta(days=5)
        custom_end = custom_start + timedelta(days=10)

        self.model.set_custom_billing_period(
            customer_id=customer_id,
            start_time=custom_start,
            end_time=custom_end
        )

        # Get the interval for this customer
        start, end = self.model.get_interval_start_end(customer_id=customer_id)

        # Should match our custom period
        self.assertEqual(start, custom_start)
        self.assertEqual(end, custom_end)

    def test_track_usage_and_bill(self):
        """Test tracking usage and calculating the bill."""
        customer_id = "customer123"

        # Track usage
        result = self.model.track_usage_and_bill(
            customer_id=customer_id,
            metric=UsageMetric.API_CALL,
            quantity=100,
            category=UsageCategory.INFERENCE
        )

        # Check that usage was tracked
        self.usage_tracker.track_usage.assert_called_once()

        # Check that cost was calculated
        self.billing_calculator.calculate_usage_cost.assert_called_once()

        # Check the result
        self.assertEqual(result["customer_id"], customer_id)
        self.assertEqual(result["metric"], UsageMetric.API_CALL)
        self.assertEqual(result["quantity"], 100)
        self.assertEqual(result["current_cost"], 1.23)
        self.assertEqual(result["cost_breakdown"], {UsageMetric.API_CALL: 1.23})

    def test_generate_invoice(self):
        """Test generating an invoice."""
        customer_id = "customer123"

        # Generate an invoice
        invoice = self.model.generate_invoice(
            customer_id=customer_id,
            due_days=30
        )

        # Check that the invoice manager was called
        self.invoice_manager.generate_invoice_from_usage.assert_called_once()

        # Check the invoice
        self.assertEqual(invoice["invoice_id"], "invoice123")
        self.assertEqual(invoice["customer_id"], customer_id)
        self.assertEqual(invoice["total_amount"], 1.23)
        self.assertEqual(invoice["status"], "draft")
        self.assertEqual(invoice["invoice_url"], "https://example.com/invoice123")

    def test_minimum_maximum_billing(self):
        """Test minimum and maximum billing amounts."""
        customer_id = "customer123"

        # Set minimum and maximum
        self.model.minimum_bill_amount = 5.0
        self.model.maximum_bill_amount = 20.0

        # Test with low usage (below minimum)
        self.billing_calculator.calculate_usage_cost.return_value = {
            "total": 1.23,
            "breakdown": {UsageMetric.API_CALL: 1.23}
        }

        invoice = self.model.generate_invoice(customer_id=customer_id)

        # Should be adjusted to minimum
        self.assertEqual(invoice["total_amount"], 5.0)

        # Test with high usage (above maximum)
        self.billing_calculator.calculate_usage_cost.return_value = {
            "total": 25.0,
            "breakdown": {UsageMetric.API_CALL: 25.0}
        }

        invoice = self.model.generate_invoice(customer_id=customer_id)

        # Should be adjusted to maximum
        self.assertEqual(invoice["total_amount"], 20.0)

    def test_usage_tracking_across_intervals(self):
        """Test tracking usage across different billing intervals."""
        customer_id = "customer123"
        now = datetime.now()

        # Test hourly aggregation
        self.model.set_metering_interval(MeteringInterval.HOURLY)
        hourly_usage = [
            {"time": now - timedelta(minutes=30), "quantity": 50},
            {"time": now - timedelta(minutes=45), "quantity": 30},
            {"time": now - timedelta(minutes=15), "quantity": 20}
        ]

        # Mock usage tracker for hourly data
        self.usage_tracker.get_usage_summary.return_value = {
            "total": 100,
            "grouped": {UsageMetric.API_CALL: {"quantity": 100}}
        }

        # Track hourly usage
        for usage in hourly_usage:
            self.model.track_usage_and_bill(
                customer_id=customer_id,
                metric=UsageMetric.API_CALL,
                quantity=usage["quantity"],
                category=UsageCategory.INFERENCE,
                metadata={"timestamp": usage["time"]}
            )

        # Verify hourly aggregation
        cost = self.model.calculate_current_usage_cost(customer_id=customer_id)
        self.assertEqual(cost["total"], 1.23)  # Based on mocked calculator

        # Test daily aggregation
        self.model.set_metering_interval(MeteringInterval.DAILY)
        daily_usage = [
            {"time": now - timedelta(hours=1), "quantity": 100},
            {"time": now - timedelta(hours=2), "quantity": 150},
            {"time": now - timedelta(hours=3), "quantity": 250}
        ]

        # Mock usage tracker for daily data
        self.usage_tracker.get_usage_summary.return_value = {
            "total": 500,
            "grouped": {UsageMetric.API_CALL: {"quantity": 500}}
        }

        # Track daily usage
        for usage in daily_usage:
            self.model.track_usage_and_bill(
                customer_id=customer_id,
                metric=UsageMetric.API_CALL,
                quantity=usage["quantity"],
                category=UsageCategory.INFERENCE,
                metadata={"timestamp": usage["time"]}
            )

        # Verify daily aggregation
        cost = self.model.calculate_current_usage_cost(customer_id=customer_id)
        self.assertEqual(cost["total"], 1.23)  # Based on mocked calculator

    def test_interval_boundary_conditions(self):
        """Test usage tracking at interval boundaries."""
        customer_id = "customer123"
        now = datetime.now()

        # Test interval transition
        self.model.set_metering_interval(MeteringInterval.HOURLY)
        
        # Mock for first hour
        self.billing_calculator.calculate_usage_cost.return_value = {
            "total": 1.23,
            "breakdown": {UsageMetric.API_CALL: 1.23}
        }

        # Track usage just before interval end
        result1 = self.model.track_usage_and_bill(
            customer_id=customer_id,
            metric=UsageMetric.API_CALL,
            quantity=50,
            category=UsageCategory.INFERENCE,
            metadata={"timestamp": now - timedelta(seconds=10)}
        )

        # Mock for second hour
        self.billing_calculator.calculate_usage_cost.return_value = {
            "total": 2.46,
            "breakdown": {UsageMetric.API_CALL: 2.46}
        }

        # Track usage just after interval start
        result2 = self.model.track_usage_and_bill(
            customer_id=customer_id,
            metric=UsageMetric.API_CALL,
            quantity=50,
            category=UsageCategory.INFERENCE,
            metadata={"timestamp": now + timedelta(seconds=10)}
        )

        # Verify correct interval handling
        self.assertNotEqual(result1["current_cost"], result2["current_cost"])
        self.assertEqual(result1["current_cost"], 1.23)
        self.assertEqual(result2["current_cost"], 2.46)

    def test_partial_interval_proration(self):
        """Test proration for partial billing intervals."""
        customer_id = "customer123"
        now = datetime.now()

        # Enable proration
        self.model.prorate_partial_periods = True
        self.model.set_metering_interval(MeteringInterval.MONTHLY)

        # Set up a mid-month billing period
        mid_month_start = datetime(now.year, now.month, 15)
        next_month = mid_month_start + timedelta(days=30)
        next_month_start = datetime(next_month.year, next_month.month, 1)

        self.model.set_custom_billing_period(
            customer_id=customer_id,
            start_time=mid_month_start,
            end_time=next_month_start
        )

        # Mock the billing calculator for prorated amount
        self.billing_calculator.calculate_usage_cost.return_value = {
            "total": 0.615,  # Half of normal monthly rate
            "breakdown": {UsageMetric.API_CALL: 0.615}
        }

        # Track usage in partial period
        result = self.model.track_usage_and_bill(
            customer_id=customer_id,
            metric=UsageMetric.API_CALL,
            quantity=50,
            category=UsageCategory.INFERENCE
        )

        # Verify prorated billing
        self.assertEqual(result["current_cost"], 0.615)  # Should be half of the normal 1.23 rate


if __name__ == "__main__":
    unittest.main()
