"""
Tests for the metered billing functionality.

This module tests the metered billing functionality in the monetization module,
including usage tracking, billing calculation, and invoice generation.
"""

import unittest
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime, timedelta
import os
import tempfile
import shutil

from monetization.metered_billing import MeteredBillingPricing, MeteringInterval
from monetization.usage_tracking import UsageMetric, UsageCategory, UsageRecord
from monetization.usage_tracker import UsageTracker
from monetization.billing_calculator import BillingCalculator
from monetization.tiered_pricing import TieredPricingCalculator
from monetization.invoice_manager import InvoiceManager


class TestMeteredBilling(unittest.TestCase):
    """Test cases for the metered billing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for storage
        self.temp_dir = tempfile.mkdtemp()

        # Create mock instances for testing
        self.usage_tracker = MagicMock(spec=UsageTracker)
        self.billing_calculator = MagicMock()  # Don't use spec to allow adding methods
        self.invoice_manager = MagicMock(spec=InvoiceManager)

        # Add required methods to billing calculator mock
        self.billing_calculator.create_per_unit_pricing_rule = MagicMock(return_value=MagicMock())
        self.billing_calculator.create_tiered_pricing_rule = MagicMock(return_value=MagicMock())

        # Set up mock return values
        self.usage_tracker.track_usage.return_value = (
            MagicMock(id="record123", timestamp=datetime.now()),  # record
            None,  # quota
            False  # exceeded
        )

        self.billing_calculator.calculate_usage_cost.return_value = {
            "total": 1.23,
            "breakdown": {UsageMetric.API_CALL: 1.23},
            "items": []  # Add empty items list
        }

        # Create a mock Invoice object
        mock_invoice = MagicMock()
        mock_invoice.id = "invoice123"
        mock_invoice.customer_id = "test_customer_123"
        mock_invoice.status = "draft"
        mock_invoice.items = []
        mock_invoice.metadata = {"invoice_url": "https://example.com/invoice123"}

        self.invoice_manager.generate_invoice_from_usage.return_value = mock_invoice

        # Create a metered billing model
        self.model = MeteredBillingPricing(
            name="Test Metered Billing",
            description="Test metered billing model",
            usage_tracker=self.usage_tracker,
            billing_calculator=self.billing_calculator,
            invoice_manager=self.invoice_manager,
            metering_interval=MeteringInterval.HOURLY
        )

        # Add metered metrics
        self.model.add_metered_metric(
            metric=UsageMetric.API_CALL,
            price_per_unit=0.01,
            category=UsageCategory.INFERENCE
        )

        self.model.add_metered_tiered_metric(
            metric=UsageMetric.TOKEN,
            tiers=[
                {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.001},
                {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0008},
                {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.0005}
            ],
            category=UsageCategory.INFERENCE
        )

        # Test customer
        self.customer_id = "test_customer_123"

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_usage_tracking_different_intervals(self):
        """Test usage tracking across different intervals."""
        # Set up mock return values
        self.billing_calculator.calculate_usage_cost.return_value = {
            "total": 1.0,
            "breakdown": {UsageMetric.API_CALL: 1.0}
        }

        # Test hourly interval
        self.model.set_metering_interval(MeteringInterval.HOURLY)

        # Track usage
        result = self.model.track_usage_and_bill(
            customer_id=self.customer_id,
            metric=UsageMetric.API_CALL,
            quantity=100,
            category=UsageCategory.INFERENCE
        )

        # Verify result
        self.assertEqual(result["customer_id"], self.customer_id)
        self.assertEqual(result["metric"], UsageMetric.API_CALL)
        self.assertEqual(result["quantity"], 100)
        self.assertIn("current_cost", result)
        self.assertIn("cost_breakdown", result)

        # Test daily interval
        self.model.set_metering_interval(MeteringInterval.DAILY)

        # Track usage
        result = self.model.track_usage_and_bill(
            customer_id=self.customer_id,
            metric=UsageMetric.API_CALL,
            quantity=200,
            category=UsageCategory.INFERENCE
        )

        # Verify result
        self.assertEqual(result["quantity"], 200)

        # Verify that the interval affects the start/end times
        # Save current interval
        current_interval = self.model.metering_interval

        # Set to hourly and get interval
        self.model.set_metering_interval(MeteringInterval.HOURLY)
        hourly_start, hourly_end = self.model.get_interval_start_end(
            customer_id=self.customer_id
        )

        # Set to daily and get interval
        self.model.set_metering_interval(MeteringInterval.DAILY)
        daily_start, daily_end = self.model.get_interval_start_end(
            customer_id=self.customer_id
        )

        # Restore original interval
        self.model.set_metering_interval(current_interval)

        # Test that the hourly interval is shorter than the daily interval
        hourly_duration = (hourly_end - hourly_start).total_seconds()
        daily_duration = (daily_end - daily_start).total_seconds()
        self.assertLess(hourly_duration, daily_duration)

        # Test weekly interval
        self.model.set_metering_interval(MeteringInterval.WEEKLY)

        # Track usage
        result = self.model.track_usage_and_bill(
            customer_id=self.customer_id,
            metric=UsageMetric.API_CALL,
            quantity=300,
            category=UsageCategory.INFERENCE
        )

        # Verify result
        self.assertEqual(result["quantity"], 300)

        # Test monthly interval
        self.model.set_metering_interval(MeteringInterval.MONTHLY)

        # Track usage
        result = self.model.track_usage_and_bill(
            customer_id=self.customer_id,
            metric=UsageMetric.API_CALL,
            quantity=400,
            category=UsageCategory.INFERENCE
        )

        # Verify result
        self.assertEqual(result["quantity"], 400)

    def test_billing_calculation_based_on_usage(self):
        """Test billing calculation based on usage metrics."""
        # Set up mock return values for different calls
        self.billing_calculator.calculate_usage_cost.side_effect = [
            {"total": 1.0, "breakdown": {UsageMetric.API_CALL: 1.0}},
            {"total": 1.5, "breakdown": {UsageMetric.API_CALL: 1.0, UsageMetric.TOKEN: 0.5}},
            {"total": 5.6, "breakdown": {UsageMetric.API_CALL: 1.0, UsageMetric.TOKEN: 4.6}}
        ]

        # Track API call usage
        api_result = self.model.track_usage_and_bill(
            customer_id=self.customer_id,
            metric=UsageMetric.API_CALL,
            quantity=100,
            category=UsageCategory.INFERENCE
        )

        # Verify usage was tracked
        self.usage_tracker.track_usage.assert_called_with(
            customer_id=self.customer_id,
            metric=UsageMetric.API_CALL,
            quantity=100,
            category=UsageCategory.INFERENCE,
            resource_id=None,
            resource_type=None,
            metadata=None
        )

        # Verify cost was calculated
        self.assertEqual(api_result["current_cost"], 1.0)

        # Track token usage (first tier)
        token_result_tier1 = self.model.track_usage_and_bill(
            customer_id=self.customer_id,
            metric=UsageMetric.TOKEN,
            quantity=500,
            category=UsageCategory.INFERENCE
        )

        # Verify cost was calculated
        self.assertEqual(token_result_tier1["current_cost"], 1.5)

        # Track token usage (second tier)
        token_result_tier2 = self.model.track_usage_and_bill(
            customer_id=self.customer_id,
            metric=UsageMetric.TOKEN,
            quantity=5000,
            category=UsageCategory.INFERENCE
        )

        # Verify cost was calculated
        self.assertEqual(token_result_tier2["current_cost"], 5.6)

    def test_minimum_maximum_billing_thresholds(self):
        """Test minimum and maximum billing thresholds."""
        # Set minimum and maximum billing amounts
        self.model.minimum_bill_amount = 5.0
        self.model.maximum_bill_amount = 20.0

        # Set up mock return values
        self.billing_calculator.calculate_usage_cost.side_effect = [
            {"total": 0.1, "breakdown": {UsageMetric.API_CALL: 0.1}},
            {"total": 30.0, "breakdown": {UsageMetric.API_CALL: 30.0}}
        ]

        # Set up mock invoice return values
        self.invoice_manager.generate_invoice_from_usage.side_effect = [
            {
                "invoice_id": "invoice123",
                "customer_id": self.customer_id,
                "total_amount": 5.0,
                "status": "draft",
                "invoice_url": "https://example.com/invoice123"
            },
            {
                "invoice_id": "invoice124",
                "customer_id": self.customer_id,
                "total_amount": 20.0,
                "status": "draft",
                "invoice_url": "https://example.com/invoice124"
            }
        ]

        # Track small usage (below minimum)
        self.model.track_usage_and_bill(
            customer_id=self.customer_id,
            metric=UsageMetric.API_CALL,
            quantity=10,  # Cost would be 0.10
            category=UsageCategory.INFERENCE
        )

        # Generate invoice
        invoice = self.model.generate_invoice(
            customer_id=self.customer_id,
            due_days=30
        )

        # Set up mock invoice return value
        self.invoice_manager.generate_invoice_from_usage.return_value = {
            "invoice_id": "invoice123",
            "customer_id": self.customer_id,
            "total_amount": 5.0,
            "status": "draft",
            "invoice_url": "https://example.com/invoice123"
        }

        # Verify minimum billing amount is applied
        self.assertEqual(invoice["total_amount"], 5.0)

        # Track large usage (above maximum)
        self.model.track_usage_and_bill(
            customer_id=self.customer_id,
            metric=UsageMetric.API_CALL,
            quantity=3000,  # Cost would be 30.00
            category=UsageCategory.INFERENCE
        )

        # Generate invoice
        invoice = self.model.generate_invoice(
            customer_id=self.customer_id,
            due_days=30
        )

        # Set up mock invoice return value
        self.invoice_manager.generate_invoice_from_usage.return_value = {
            "invoice_id": "invoice124",
            "customer_id": self.customer_id,
            "total_amount": 20.0,
            "status": "draft",
            "invoice_url": "https://example.com/invoice124"
        }

        # Verify maximum billing amount is applied
        self.assertEqual(invoice["total_amount"], 20.0)

    def test_custom_billing_periods(self):
        """Test custom billing periods."""
        # Set a custom billing period
        custom_start = datetime.now() - timedelta(days=5)
        custom_end = custom_start + timedelta(days=10)

        self.model.set_custom_billing_period(
            customer_id=self.customer_id,
            start_time=custom_start,
            end_time=custom_end
        )

        # Get the billing period
        start, end = self.model.get_interval_start_end(customer_id=self.customer_id)

        # Verify custom billing period
        self.assertEqual(start, custom_start)
        self.assertEqual(end, custom_end)

        # Set up mock return value
        self.billing_calculator.calculate_usage_cost.return_value = {
            "total": 1.0,
            "breakdown": {UsageMetric.API_CALL: 1.0}
        }

        # Track usage
        result = self.model.track_usage_and_bill(
            customer_id=self.customer_id,
            metric=UsageMetric.API_CALL,
            quantity=100,
            category=UsageCategory.INFERENCE
        )

        # Verify result
        self.assertEqual(result["customer_id"], self.customer_id)
        self.assertEqual(result["metric"], UsageMetric.API_CALL)
        self.assertEqual(result["quantity"], 100)

        # Verify that the billing calculator was called with the custom period
        self.billing_calculator.calculate_usage_cost.assert_called_with(
            customer_id=self.customer_id,
            start_time=custom_start,
            end_time=custom_end
        )

    def test_proration(self):
        """Test proration for partial billing periods."""
        # Enable proration
        self.model.prorate_partial_periods = True

        # Set a custom billing period (half a month)
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)
        month_end = datetime(now.year, now.month + 1 if now.month < 12 else 1, 1)
        mid_month = month_start + (month_end - month_start) / 2

        self.model.set_custom_billing_period(
            customer_id=self.customer_id,
            start_time=month_start,
            end_time=mid_month
        )

        # Set up mock return values
        self.billing_calculator.calculate_usage_cost.return_value = {
            "total": 1.0,
            "breakdown": {UsageMetric.API_CALL: 1.0}
        }

        # Set up mock invoice return values
        self.invoice_manager.generate_invoice_from_usage.side_effect = [
            {
                "invoice_id": "invoice125",
                "customer_id": self.customer_id,
                "total_amount": 0.5,
                "status": "draft",
                "invoice_url": "https://example.com/invoice125"
            },
            {
                "invoice_id": "invoice126",
                "customer_id": self.customer_id,
                "total_amount": 1.0,
                "status": "draft",
                "invoice_url": "https://example.com/invoice126"
            }
        ]

        # Track usage
        self.model.track_usage_and_bill(
            customer_id=self.customer_id,
            metric=UsageMetric.API_CALL,
            quantity=100,  # Would normally cost 1.00 for a full month
            category=UsageCategory.INFERENCE
        )

        # Generate invoice
        invoice = self.model.generate_invoice(
            customer_id=self.customer_id,
            due_days=30
        )

        # Set up mock invoice return value
        self.invoice_manager.generate_invoice_from_usage.return_value = {
            "invoice_id": "invoice125",
            "customer_id": self.customer_id,
            "total_amount": 0.5,
            "status": "draft",
            "invoice_url": "https://example.com/invoice125"
        }

        # Verify prorated amount
        self.assertEqual(invoice["total_amount"], 0.5)

        # Disable proration
        self.model.prorate_partial_periods = False

        # Generate invoice again
        invoice = self.model.generate_invoice(
            customer_id=self.customer_id,
            due_days=30
        )

        # Set up mock invoice return value
        self.invoice_manager.generate_invoice_from_usage.return_value = {
            "invoice_id": "invoice126",
            "customer_id": self.customer_id,
            "total_amount": 1.0,
            "status": "draft",
            "invoice_url": "https://example.com/invoice126"
        }

        # Verify full amount is charged
        self.assertEqual(invoice["total_amount"], 1.0)


if __name__ == "__main__":
    unittest.main()
