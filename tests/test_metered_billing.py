"""test_metered_billing - Module for tests.test_metered_billing."""

import logging
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from monetization.metered_billing import MeteredBilling, UsageRecord


class TestUsageRecord(unittest.TestCase):
    """Test cases for the UsageRecord class."""

    def test_usage_record_initialization(self):
        """Test basic usage record initialization."""
        timestamp = datetime.now()
        record = UsageRecord(timestamp, 10.5, "requests")
        assert record.timestamp == timestamp
        assert record.quantity == 10.5
        assert record.unit == "requests"


class TestMeteredBilling(unittest.TestCase):
    """Test cases for the MeteredBilling class."""

    def setUp(self):
        """Set up test fixtures."""
        self.billing = MeteredBilling(price_per_unit=0.01, unit="requests")
        self.start_time = datetime(2024, 1, 1, 0, 0, 0)
        self.end_time = datetime(2024, 1, 2, 0, 0, 0)

    def test_initialization(self):
        """Test metered billing initialization."""
        assert self.billing.price_per_unit == 0.01
        assert self.billing.unit == "requests"
        assert len(self.billing.usage_records) == 0

    def test_record_usage(self):
        """Test recording usage."""
        with patch("logging.Logger.info") as mock_info:
            self.billing.record_usage(10.5)
            assert len(self.billing.usage_records) == 1
            assert self.billing.usage_records[0].quantity == 10.5
            mock_info.assert_called_once()

    def test_record_usage_with_timestamp(self):
        """Test recording usage with specific timestamp."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        self.billing.record_usage(10.5, timestamp)
        assert self.billing.usage_records[0].timestamp == timestamp

    def test_record_usage_negative_quantity(self):
        """Test recording negative usage quantity."""
        with pytest.raises(ValueError):
            self.billing.record_usage(-10.5)

    def test_get_usage_for_period(self):
        """Test getting usage for a specific period."""
        # Record usage within period
        self.billing.record_usage(10.5, self.start_time + timedelta(hours=1))
        # Record usage outside period
        self.billing.record_usage(5.5, self.end_time + timedelta(hours=1))

        usage = self.billing.get_usage_for_period(self.start_time, self.end_time)
        assert usage == 10.5

    def test_get_usage_for_period_invalid_dates(self):
        """Test getting usage with invalid date range."""
        with pytest.raises(ValueError):
            self.billing.get_usage_for_period(self.end_time, self.start_time)

    def test_calculate_bill(self):
        """Test bill calculation."""
        self.billing.record_usage(100, self.start_time + timedelta(hours=1))
        self.billing.record_usage(50, self.start_time + timedelta(hours=2))

        with patch("logging.Logger.info") as mock_info:
            bill = self.billing.calculate_bill(self.start_time, self.end_time)
            assert bill == 1.5  # (100 + 50) * 0.01
            mock_info.assert_called_once()

    def test_get_usage_summary_empty(self):
        """Test getting usage summary with no records."""
        summary = self.billing.get_usage_summary()
        assert summary["total_usage"] == 0.0
        assert summary["record_count"] == 0
        assert summary["average_usage"] == 0.0

    def test_get_usage_summary_with_records(self):
        """Test getting usage summary with records."""
        self.billing.record_usage(100)
        self.billing.record_usage(200)
        self.billing.record_usage(300)

        summary = self.billing.get_usage_summary()
        assert summary["total_usage"] == 600.0
        assert summary["record_count"] == 3
        assert summary["average_usage"] == 200.0

    def test_multiple_units(self):
        """Test handling multiple units of measurement."""
        billing = MeteredBilling(price_per_unit=0.5, unit="GB")
        billing.record_usage(10.5)
        assert billing.unit == "GB"
        assert billing.usage_records[0].unit == "GB"


if __name__ == "__main__":
    unittest.main()
