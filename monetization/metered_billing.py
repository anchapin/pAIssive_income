"""
Metered billing for the pAIssive Income project.

This module provides classes for implementing metered billing models,
where customers are charged based on their actual measured usage of a service
over a specific time period.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from .billing_calculator import (
    PricingRule,
    BillingCalculator,
)
from .usage_tracking import UsageMetric, UsageCategory
from .usage_tracker import UsageTracker
from .usage_based_pricing import UsageBasedPricing
from .invoice_manager import InvoiceManager


class MeteringInterval:
    """Enumeration of metering intervals."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class MeteredBillingPricing(UsageBasedPricing):
    """
    Metered billing pricing model.

    This model implements metered billing, where customers are charged based on
    their actual measured usage of a service over a specific time period. The
    model supports different metering intervals and can generate invoices based
    on the metered usage.

    Key features:
    - Real-time usage tracking and cost calculation
    - Support for different metering intervals (hourly, daily, monthly)
    - Automatic invoice generation based on metered usage
    - Flexible pricing rules for different usage metrics
    - Support for minimum and maximum billing amounts
    """

    def __init__(
        self,
        name: str = "Metered Billing",
        description: str = "Pay only for what you use with precise metering",
        billing_calculator: Optional[BillingCalculator] = None,
        usage_tracker: Optional[UsageTracker] = None,
        invoice_manager: Optional[InvoiceManager] = None,
        metering_interval: str = MeteringInterval.MONTHLY,
        minimum_bill_amount: float = 0.0,
        maximum_bill_amount: Optional[float] = None,
        auto_invoice: bool = True,
        prorate_partial_periods: bool = True,
    ):
        """
        Initialize a metered billing pricing model.

        Args:
            name: Name of the pricing model
            description: Description of the pricing model
            billing_calculator: Billing calculator to use
            usage_tracker: Usage tracker to use
            invoice_manager: Invoice manager to use
            metering_interval: Interval for metering (e.g., HOURLY, DAILY, MONTHLY)
            minimum_bill_amount: Minimum amount to bill
            maximum_bill_amount: Maximum amount to bill
            auto_invoice: Whether to automatically generate invoices
            prorate_partial_periods: Whether to prorate charges for partial periods
        """
        super().__init__(
            name=name,
            description=description,
            billing_calculator=billing_calculator,
            usage_tracker=usage_tracker,
        )

        self.invoice_manager = invoice_manager or InvoiceManager()
        self.metering_interval = metering_interval
        self.minimum_bill_amount = minimum_bill_amount
        self.maximum_bill_amount = maximum_bill_amount
        self.auto_invoice = auto_invoice
        self.prorate_partial_periods = prorate_partial_periods
        self.billing_periods = {}  # Track billing periods by customer

    def add_metered_metric(
        self,
        metric: str,
        price_per_unit: float,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
    ) -> PricingRule:
        """
        Add a metered metric to the pricing model.

        Args:
            metric: Type of usage metric
            price_per_unit: Price per unit
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost for this metric
            maximum_cost: Maximum cost for this metric

        Returns:
            The created pricing rule
        """
        return self.add_per_unit_pricing(
            metric=metric,
            price_per_unit=price_per_unit,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
        )

    def add_metered_tiered_metric(
        self,
        metric: str,
        tiers: List[Dict[str, Any]],
        graduated: bool = True,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        minimum_cost: float = 0.0,
        maximum_cost: Optional[float] = None,
    ) -> PricingRule:
        """
        Add a metered metric with tiered pricing.

        Args:
            metric: Type of usage metric
            tiers: List of pricing tiers
            graduated: Whether to use graduated pricing
            category: Category of usage
            resource_type: Type of resource
            minimum_cost: Minimum cost for this metric
            maximum_cost: Maximum cost for this metric

        Returns:
            The created pricing rule
        """
        return self.add_tiered_pricing(
            metric=metric,
            tiers=tiers,
            graduated=graduated,
            category=category,
            resource_type=resource_type,
            minimum_cost=minimum_cost,
            maximum_cost=maximum_cost,
        )

    def set_metering_interval(self, interval: str) -> None:
        """
        Set the metering interval.

        Args:
            interval: Metering interval (e.g., HOURLY, DAILY, MONTHLY)
        """
        self.metering_interval = interval

    def get_interval_start_end(
        self,
        reference_time: Optional[datetime] = None,
        customer_id: Optional[str] = None,
    ) -> Tuple[datetime, datetime]:
        """
        Get the start and end times for the current metering interval.

        Args:
            reference_time: Reference time (defaults to now)
            customer_id: Customer ID for custom billing periods

        Returns:
            Tuple of (start_time, end_time)
        """
        now = reference_time or datetime.now()

        # Check for custom billing period for this customer
        if customer_id and customer_id in self.billing_periods:
            period = self.billing_periods[customer_id]
            if now >= period["start"] and now <= period["end"]:
                return period["start"], period["end"]

        # Calculate based on standard intervals
        if self.metering_interval == MeteringInterval.HOURLY:
            start = datetime(now.year, now.month, now.day, now.hour)
            end = start + timedelta(hours=1)
        elif self.metering_interval == MeteringInterval.DAILY:
            start = datetime(now.year, now.month, now.day)
            end = start + timedelta(days=1)
        elif self.metering_interval == MeteringInterval.WEEKLY:
            # Start from Monday of the current week
            start = datetime(now.year, now.month, now.day) - timedelta(
                days=now.weekday()
            )
            end = start + timedelta(days=7)
        elif self.metering_interval == MeteringInterval.MONTHLY:
            start = datetime(now.year, now.month, 1)
            # Calculate end of month
            if now.month == 12:
                end = datetime(now.year + 1, 1, 1)
            else:
                end = datetime(now.year, now.month + 1, 1)
        else:
            # Default to daily if unknown interval
            start = datetime(now.year, now.month, now.day)
            end = start + timedelta(days=1)

        return start, end

    def set_custom_billing_period(
        self, customer_id: str, start_time: datetime, end_time: datetime
    ) -> None:
        """
        Set a custom billing period for a customer.

        Args:
            customer_id: ID of the customer
            start_time: Start time for the billing period
            end_time: End time for the billing period
        """
        self.billing_periods[customer_id] = {"start": start_time, "end": end_time}

    def calculate_current_usage_cost(
        self, customer_id: str, reference_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate the cost for a customer's current usage period.

        Args:
            customer_id: ID of the customer
            reference_time: Reference time (defaults to now)

        Returns:
            Dictionary with cost information
        """
        start_time, end_time = self.get_interval_start_end(
            reference_time=reference_time, customer_id=customer_id
        )

        return self.calculate_cost(
            customer_id=customer_id, start_time=start_time, end_time=end_time
        )

    def generate_invoice(
        self,
        customer_id: str,
        reference_time: Optional[datetime] = None,
        due_days: int = 30,
        customer_info: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate an invoice for a customer's usage.

        Args:
            customer_id: ID of the customer
            reference_time: Reference time (defaults to now)
            due_days: Number of days until the invoice is due
            customer_info: Customer information for the invoice
            metadata: Additional metadata for the invoice

        Returns:
            Dictionary with invoice information
        """
        # Get the billing period
        start_time, end_time = self.get_interval_start_end(
            reference_time=reference_time, customer_id=customer_id
        )

        # Calculate the cost
        cost = self.calculate_cost(
            customer_id=customer_id, start_time=start_time, end_time=end_time
        )

        # Apply minimum and maximum bill amounts
        total_cost = cost["total"]
        if total_cost < self.minimum_bill_amount:
            total_cost = self.minimum_bill_amount

        if (
            self.maximum_bill_amount is not None
            and total_cost > self.maximum_bill_amount
        ):
            total_cost = self.maximum_bill_amount

        # Calculate due date
        due_date = datetime.now() + timedelta(days=due_days)

        # Generate the invoice
        invoice = self.invoice_manager.generate_invoice_from_usage(
            customer_id=customer_id,
            start_time=start_time,
            end_time=end_time,
            due_date=due_date,
            customer_info=customer_info,
            metadata=metadata,
        )

        if invoice:
            return {
                "invoice_id": invoice.id,
                "customer_id": customer_id,
                "start_time": start_time,
                "end_time": end_time,
                "total_amount": total_cost,
                "due_date": due_date,
                "status": invoice.status,
                "items": [
                    {"description": item.description, "amount": item.amount}
                    for item in invoice.items
                ],
                "invoice_url": invoice.metadata.get("invoice_url"),
            }

        return {
            "error": "Failed to generate invoice",
            "customer_id": customer_id,
            "start_time": start_time,
            "end_time": end_time,
            "total_amount": total_cost,
        }

    def track_usage_and_bill(
        self,
        customer_id: str,
        metric: str,
        quantity: float,
        category: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Track usage and calculate the current bill.

        This method tracks usage for a customer and returns the current bill amount.
        If auto_invoice is enabled and the billing period has ended, it will also
        generate an invoice.

        Args:
            customer_id: ID of the customer
            metric: Type of usage metric
            quantity: Quantity of usage
            category: Category of usage
            resource_id: ID of the resource being used
            resource_type: Type of resource being used
            metadata: Additional metadata for the usage record

        Returns:
            Dictionary with usage and billing information
        """
        # Track the usage
        record, quota, exceeded = self.usage_tracker.track_usage(
            customer_id=customer_id,
            metric=metric,
            quantity=quantity,
            category=category or UsageCategory.INFERENCE,
            resource_id=resource_id,
            resource_type=resource_type,
            metadata=metadata,
        )

        # Calculate the current cost
        cost = self.calculate_current_usage_cost(customer_id=customer_id)

        result = {
            "usage_record_id": record.id,
            "customer_id": customer_id,
            "metric": metric,
            "quantity": quantity,
            "timestamp": record.timestamp,
            "current_cost": cost["total"],
            "cost_breakdown": cost["breakdown"],
        }

        # Check if we need to generate an invoice
        if self.auto_invoice:
            now = datetime.now()
            _, period_end = self.get_interval_start_end(
                reference_time=now, customer_id=customer_id
            )

            # If we're at the end of the billing period, generate an invoice
            if now >= period_end - timedelta(minutes=5):  # 5-minute buffer
                invoice_result = self.generate_invoice(customer_id=customer_id)
                result["invoice"] = invoice_result

        return result


# Example usage
if __name__ == "__main__":
    # Create a metered billing model
    model = MeteredBillingPricing(
        name="API Metered Billing",
        description="Pay only for the API calls you make",
        metering_interval=MeteringInterval.DAILY,
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

    # Track some usage
    customer_id = "customer123"

    result = model.track_usage_and_bill(
        customer_id=customer_id,
        metric=UsageMetric.API_CALL,
        quantity=100,
        category=UsageCategory.INFERENCE,
        resource_id="model_gpt4",
        resource_type="model",
        metadata={"endpoint": "/v1/completions"},
    )

    print(f"Tracked usage: {result['quantity']} {result['metric']}")
    print(f"Current cost: ${result['current_cost']:.2f}")
    print(f"Cost breakdown: {result['cost_breakdown']}")
