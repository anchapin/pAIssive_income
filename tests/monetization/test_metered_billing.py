"""
Tests for metered billing functionality.

This module contains tests for the metered billing system, including
usage tracking, billing calculation, and billing thresholds.
"""


from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from monetization.metered_billing import 

(
    BillingCalculator,
    BillingConfig,
    BillingPeriod,
    BillingThreshold,
    MeteredBillingService,
    UsageTracker,
)


class TestMeteredBilling:
    """Tests for metered billing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create billing configuration
        self.billing_config = BillingConfig(
            base_rate=Decimal("10.00"),  # $10 base rate
            usage_rates={
                "api_calls": Decimal("0.001"),  # $0.001 per API call
                "storage_gb": Decimal("0.10"),  # $0.10 per GB
                "compute_hours": Decimal("0.50"),  # $0.50 per compute hour
            },
            minimum_charge=Decimal("5.00"),  # $5 minimum
            maximum_charge=Decimal("1000.00"),  # $1000 maximum
            free_tier_limits={
                "api_calls": 1000,  # 1000 free API calls
                "storage_gb": 1,  # 1 GB free storage
                "compute_hours": 10,  # 10 free compute hours
            },
        )

        # Create billing service
        self.billing_service = MeteredBillingService(self.billing_config)

        # Create usage tracker
        self.usage_tracker = UsageTracker()

        # Create billing calculator
        self.billing_calculator = BillingCalculator(self.billing_config)

        # Test customer data
        self.test_customers = {
            "customer1": {
                "id": "customer1",
                "name": "Test Customer 1",
                "plan": "basic",
                "billing_period": BillingPeriod.MONTHLY,
                "billing_day": 1,  # Bill on the 1st of each month
                "payment_method": "credit_card",
                "email": "customer1@example.com",
            },
            "customer2": {
                "id": "customer2",
                "name": "Test Customer 2",
                "plan": "premium",
                "billing_period": BillingPeriod.MONTHLY,
                "billing_day": 15,  # Bill on the 15th of each month
                "payment_method": "bank_transfer",
                "email": "customer2@example.com",
            },
            "customer3": {
                "id": "customer3",
                "name": "Test Customer 3",
                "plan": "enterprise",
                "billing_period": BillingPeriod.QUARTERLY,
                "billing_day": 1,  # Bill on the 1st of each quarter
                "payment_method": "invoice",
                "email": "customer3@example.com",
            },
        }

    def test_usage_tracking(self):
        """Test usage tracking across different intervals."""
        customer_id = "customer1"

        # Track usage for different metrics
        usage_data = [
            # API calls
            {"metric": "api_calls", "quantity": 100, "timestamp": datetime.utcnow()},
            {
                "metric": "api_calls",
                "quantity": 200,
                "timestamp": datetime.utcnow() - timedelta(hours=1),
            },
            {
                "metric": "api_calls",
                "quantity": 300,
                "timestamp": datetime.utcnow() - timedelta(days=1),
            },
            # Storage
            {"metric": "storage_gb", "quantity": 2.5, "timestamp": datetime.utcnow()},
            {
                "metric": "storage_gb",
                "quantity": 1.5,
                "timestamp": datetime.utcnow() - timedelta(days=2),
            },
            # Compute hours
            {"metric": "compute_hours", "quantity": 5, "timestamp": datetime.utcnow()},
            {
                "metric": "compute_hours",
                "quantity": 8,
                "timestamp": datetime.utcnow() - timedelta(days=3),
            },
        ]

        # Record usage
        for usage in usage_data:
            self.usage_tracker.track_usage(
                customer_id=customer_id,
                metric=usage["metric"],
                quantity=usage["quantity"],
                timestamp=usage["timestamp"],
            )

        # Test hourly usage
        hourly_usage = self.usage_tracker.get_usage(
            customer_id=customer_id,
            metric="api_calls",
            start_time=datetime.utcnow() - timedelta(hours=1),
            end_time=datetime.utcnow(),
        )
        assert hourly_usage == 100  # Only the most recent API calls

        # Test daily usage
        daily_usage = self.usage_tracker.get_usage(
            customer_id=customer_id,
            metric="api_calls",
            start_time=datetime.utcnow() - timedelta(days=1),
            end_time=datetime.utcnow(),
        )
        assert daily_usage == 600  # All API calls within the last day

        # Test monthly usage
        monthly_usage = self.usage_tracker.get_usage(
            customer_id=customer_id,
            metric="api_calls",
            start_time=datetime.utcnow() - timedelta(days=30),
            end_time=datetime.utcnow(),
        )
        assert monthly_usage == 600  # All API calls

        # Test storage usage (latest value)
        storage_usage = self.usage_tracker.get_latest_usage(
            customer_id=customer_id, metric="storage_gb"
        )
        assert storage_usage == 2.5  # Latest storage value

        # Test compute hours (cumulative)
        compute_usage = self.usage_tracker.get_usage(
            customer_id=customer_id,
            metric="compute_hours",
            start_time=datetime.utcnow() - timedelta(days=30),
            end_time=datetime.utcnow(),
        )
        assert compute_usage == 13  # All compute hours

        # Test usage summary
        usage_summary = self.usage_tracker.get_usage_summary(
            customer_id=customer_id,
            start_time=datetime.utcnow() - timedelta(days=30),
            end_time=datetime.utcnow(),
        )
        assert usage_summary["api_calls"] == 600
        assert usage_summary["storage_gb"] == 2.5
        assert usage_summary["compute_hours"] == 13

    def test_billing_calculation(self):
        """Test billing calculation based on usage metrics."""
        customer_id = "customer1"

        # Define test usage
        usage = {
            "api_calls": 5000,  # 4000 billable (after free tier)
            "storage_gb": 5,  # 4 billable (after free tier)
            "compute_hours": 20,  # 10 billable (after free tier)
        }

        # Calculate billing amount
        billing_amount = self.billing_calculator.calculate_bill(
            customer_id=customer_id, usage=usage
        )

        # Expected calculation:
        # Base rate: $10.00
        # API calls: 4000 * $0.001 = $4.00
        # Storage: 4 GB * $0.10 = $0.40
        # Compute: 10 hours * $0.50 = $5.00
        # Total: $10.00 + $4.00 + $0.40 + $5.00 = $19.40
        expected_amount = Decimal("19.40")

        assert billing_amount == expected_amount

        # Test itemized bill
        itemized_bill = self.billing_calculator.calculate_itemized_bill(
            customer_id=customer_id, usage=usage
        )

        assert itemized_bill["base_rate"] == Decimal("10.00")
        assert itemized_bill["usage_charges"]["api_calls"] == Decimal("4.00")
        assert itemized_bill["usage_charges"]["storage_gb"] == Decimal("0.40")
        assert itemized_bill["usage_charges"]["compute_hours"] == Decimal("5.00")
        assert itemized_bill["total"] == expected_amount

        # Test with usage below free tier
        low_usage = {
            "api_calls": 500,  # Below free tier
            "storage_gb": 0.5,  # Below free tier
            "compute_hours": 5,  # Below free tier
        }

        # Calculate billing amount
        low_billing_amount = self.billing_calculator.calculate_bill(
            customer_id=customer_id, usage=low_usage
        )

        # Expected calculation:
        # Base rate: $10.00
        # No usage charges (all within free tier)
        # Total: $10.00
        expected_low_amount = Decimal("10.00")

        assert low_billing_amount == expected_low_amount

    def test_billing_thresholds(self):
        """Test minimum/maximum billing thresholds."""
        customer_id = "customer1"

        # Test minimum threshold
        # Set usage very low
        low_usage = {"api_calls": 100, "storage_gb": 0.1, "compute_hours": 1}

        # Override base rate to test minimum threshold
        self.billing_calculator.config.base_rate = Decimal("0.00")

        # Calculate billing amount
        low_billing_amount = self.billing_calculator.calculate_bill(
            customer_id=customer_id, usage=low_usage
        )

        # Should be minimum charge
        assert low_billing_amount == self.billing_config.minimum_charge

        # Test maximum threshold
        # Set usage very high
        high_usage = {
            "api_calls": 2000000,  # 2 million API calls
            "storage_gb": 5000,  # 5 TB
            "compute_hours": 2000,  # 2000 hours
        }

        # Reset base rate
        self.billing_calculator.config.base_rate = Decimal("10.00")

        # Calculate billing amount
        high_billing_amount = self.billing_calculator.calculate_bill(
            customer_id=customer_id, usage=high_usage
        )

        # Should be maximum charge
        assert high_billing_amount == self.billing_config.maximum_charge

        # Test custom thresholds for specific customer
        # Create custom threshold
        custom_threshold = BillingThreshold(
            customer_id="customer2",
            minimum_charge=Decimal("20.00"),
            maximum_charge=Decimal("500.00"),
        )

        # Register custom threshold
        self.billing_calculator.register_custom_threshold(custom_threshold)

        # Calculate billing for customer with custom threshold
        custom_billing_amount = self.billing_calculator.calculate_bill(
            customer_id="customer2", usage=low_usage  # Low usage to trigger minimum
        )

        # Should use custom minimum
        assert custom_billing_amount == Decimal("20.00")

        # Calculate with high usage
        custom_high_amount = self.billing_calculator.calculate_bill(
            customer_id="customer2", usage=high_usage  # High usage to trigger maximum
        )

        # Should use custom maximum
        assert custom_high_amount == Decimal("500.00")

    def test_custom_billing_periods(self):
        """Test custom billing periods and proration."""
        # Test monthly billing
        monthly_customer = "customer1"
        monthly_period = self.billing_service.get_billing_period(
            customer_id=monthly_customer
        )

        assert monthly_period["type"] == BillingPeriod.MONTHLY
        assert monthly_period["billing_day"] == 1

        # Test quarterly billing
        quarterly_customer = "customer3"
        quarterly_period = self.billing_service.get_billing_period(
            customer_id=quarterly_customer
        )

        assert quarterly_period["type"] == BillingPeriod.QUARTERLY
        assert quarterly_period["billing_day"] == 1

        # Test proration for plan change
        # Mock current date
        current_date = datetime(2023, 7, 15)

        # Calculate prorated amount for plan change
        prorated_amount = self.billing_service.calculate_prorated_amount(
            customer_id=monthly_customer,
            old_plan="basic",
            new_plan="premium",
            change_date=current_date,
            current_date=current_date,
        )

        # For monthly billing on the 1st, changing on the 15th
        # 16 days remaining in 31-day month (July)
        # Premium plan costs more, so additional charge
        expected_proration = Decimal("16.13")  # (Premium - Basic) * (16/31)

        assert abs(prorated_amount - expected_proration) < Decimal("0.01")

        # Test mid-period usage calculation
        # Record usage for first half of month
        first_half_usage = {"api_calls": 2000, "storage_gb": 2, "compute_hours": 10}

        # Record usage for second half of month
        second_half_usage = {"api_calls": 3000, "storage_gb": 3, "compute_hours": 15}

        # Mock usage tracker
        with patch.object(self.usage_tracker, "get_usage_summary") as mock_usage:
            # Return different usage based on date range
            def mock_usage_summary(customer_id, start_time, end_time):
                if start_time.day == 1 and end_time.day == 15:
                            return first_half_usage
                elif start_time.day == 16 and end_time.day == 31:
                            return second_half_usage
                else:
                            return {"api_calls": 5000, "storage_gb": 5, "compute_hours": 25}

            mock_usage.side_effect = mock_usage_summary

            # Calculate bill for partial period
            partial_bill = self.billing_service.calculate_partial_bill(
                customer_id=monthly_customer,
                start_date=datetime(2023, 7, 1),
                end_date=datetime(2023, 7, 15),
            )

            # Verify partial bill calculation
            assert partial_bill > Decimal("0.00")

            # Calculate bill for full period
            full_bill = self.billing_service.calculate_bill(
                customer_id=monthly_customer, billing_date=datetime(2023, 7, 31)
            )

            # Verify full bill is approximately sum of partial bills
            partial_bill2 = self.billing_service.calculate_partial_bill(
                customer_id=monthly_customer,
                start_date=datetime(2023, 7, 16),
                end_date=datetime(2023, 7, 31),
            )

            # Full bill should be close to sum of partial bills
            assert abs(full_bill - (partial_bill + partial_bill2)) < Decimal("0.10")

    def test_billing_integration(self):
        """Test complete billing workflow."""
        customer_id = "customer1"

        # Mock current date
        current_date = datetime(2023, 7, 31)

        # Record usage
        usage_data = [
            {
                "metric": "api_calls",
                "quantity": 1000,
                "timestamp": datetime(2023, 7, 5),
            },
            {
                "metric": "api_calls",
                "quantity": 2000,
                "timestamp": datetime(2023, 7, 15),
            },
            {
                "metric": "api_calls",
                "quantity": 3000,
                "timestamp": datetime(2023, 7, 25),
            },
            {"metric": "storage_gb", "quantity": 5, "timestamp": datetime(2023, 7, 10)},
            {
                "metric": "compute_hours",
                "quantity": 25,
                "timestamp": datetime(2023, 7, 20),
            },
        ]

        # Record usage
        for usage in usage_data:
            self.usage_tracker.track_usage(
                customer_id=customer_id,
                metric=usage["metric"],
                quantity=usage["quantity"],
                timestamp=usage["timestamp"],
            )

        # Mock payment gateway
        payment_gateway = MagicMock()
        payment_gateway.charge.return_value = {
            "success": True,
            "transaction_id": "txn_123456",
            "amount": "29.50",
            "currency": "USD",
            "timestamp": current_date.isoformat(),
        }

        # Set up billing service with mocks
        self.billing_service.usage_tracker = self.usage_tracker
        self.billing_service.billing_calculator = self.billing_calculator
        self.billing_service.payment_gateway = payment_gateway

        # Generate and process bill
        bill = self.billing_service.generate_bill(
            customer_id=customer_id, billing_date=current_date
        )

        # Verify bill details
        assert bill["customer_id"] == customer_id
        assert bill["billing_date"] == current_date.isoformat()
        assert "total_amount" in bill
        assert "usage_summary" in bill
        assert "line_items" in bill

        # Process payment
        payment_result = self.billing_service.process_payment(bill)

        # Verify payment was processed
        assert payment_result["success"] is True
        assert payment_result["transaction_id"] == "txn_123456"

        # Verify payment gateway was called with correct amount
        payment_gateway.charge.assert_called_once()
        call_args = payment_gateway.charge.call_args[1]
        assert call_args["customer_id"] == customer_id
        assert call_args["amount"] == bill["total_amount"]

        # Test invoice generation
        invoice = self.billing_service.generate_invoice(bill)

        # Verify invoice details
        assert invoice["invoice_number"] is not None
        assert invoice["customer_id"] == customer_id
        assert invoice["billing_date"] == bill["billing_date"]
        assert invoice["total_amount"] == bill["total_amount"]
        assert "line_items" in invoice
        assert "usage_summary" in invoice


if __name__ == "__main__":
    pytest.main(["-v", "test_metered_billing.py"])