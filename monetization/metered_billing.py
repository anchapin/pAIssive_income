"""metered_billing.py - Module for .monetization."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, Union

logger = logging.getLogger(__name__)


class UsageRecord:
    """Represents a single usage record for metered billing."""

    def __init__(self, timestamp: datetime, quantity: float, unit: str) -> None:
        """
        Initialize a usage record.

        Args:
            timestamp: When the usage occurred
            quantity: Amount of usage
            unit: Unit of measurement (e.g., 'requests', 'GB', 'minutes')

        """
        self.timestamp = timestamp
        self.quantity = quantity
        self.unit = unit


class MeteredBilling:
    """Handles metered billing calculations and usage tracking."""

    def __init__(self, price_per_unit: float, unit: str) -> None:
        """
        Initialize metered billing.

        Args:
            price_per_unit: Cost per unit of usage
            unit: Unit of measurement (e.g., 'requests', 'GB', 'minutes')

        """
        self.price_per_unit = price_per_unit
        self.unit = unit
        self.usage_records: list[UsageRecord] = []

    def record_usage(self, quantity: float, timestamp: Optional[datetime] = None) -> None:
        """
        Record a usage event.

        Args:
            quantity: Amount of usage
            timestamp: When the usage occurred (defaults to current time)

        """
        if timestamp is None:
            timestamp = datetime.now()

        if quantity < 0:
            raise ValueError("Usage quantity cannot be negative")

        record = UsageRecord(timestamp, quantity, self.unit)
        self.usage_records.append(record)
        logger.info("Recorded usage: %.2f %s at %s", quantity, self.unit, timestamp)

    def get_usage_for_period(self, start_time: datetime, end_time: datetime) -> float:
        """
        Calculate total usage for a given time period.

        Args:
            start_time: Start of the period
            end_time: End of the period

        Returns:
            float: Total usage in the period

        """
        if start_time > end_time:
            raise ValueError("Start time must be before end time")

        total_usage = sum(
            record.quantity
            for record in self.usage_records
            if start_time <= record.timestamp <= end_time
        )
        return total_usage

    def calculate_bill(self, start_time: datetime, end_time: datetime) -> float:
        """
        Calculate the bill for a given time period.

        Args:
            start_time: Start of the billing period
            end_time: End of the billing period

        Returns:
            float: Total bill amount

        """
        usage = self.get_usage_for_period(start_time, end_time)
        bill_amount = usage * self.price_per_unit
        logger.info(
            "Calculated bill: $%.2f for %.2f %s",
            bill_amount,
            usage,
            self.unit
        )
        return bill_amount

    def get_usage_summary(self) -> dict[str, Union[float, int]]:
        """
        Get a summary of all usage records.

        Returns:
            Dict containing usage statistics

        """
        if not self.usage_records:
            return {
                "total_usage": 0.0,
                "record_count": 0,
                "average_usage": 0.0
            }

        total_usage = sum(record.quantity for record in self.usage_records)
        return {
            "total_usage": total_usage,
            "record_count": len(self.usage_records),
            "average_usage": total_usage / len(self.usage_records)
        }
