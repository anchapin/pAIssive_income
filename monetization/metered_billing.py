"""
"""
Metered billing for the pAIssive Income project.
Metered billing for the pAIssive Income project.


This module provides classes for implementing metered billing models,
This module provides classes for implementing metered billing models,
where customers are charged based on their actual measured usage of a service
where customers are charged based on their actual measured usage of a service
over a specific time period.
over a specific time period.
"""
"""


import time
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from typing import Any, Dict, List, Optional, Tuple


from .invoice_manager import InvoiceManager
from .invoice_manager import InvoiceManager
from .usage_based_pricing import UsageBasedPricing
from .usage_based_pricing import UsageBasedPricing
from .usage_tracker import UsageTracker
from .usage_tracker import UsageTracker
from .usage_tracking import UsageCategory, UsageMetric
from .usage_tracking import UsageCategory, UsageMetric




class MeteringInterval
class MeteringInterval


(
(
BillingCalculator,
BillingCalculator,
PricingRule,
PricingRule,
)
)
:
    :
    """Enumeration of metering intervals."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


    class MeteredBillingPricing(UsageBasedPricing):
    """
    """
    Metered billing pricing model.
    Metered billing pricing model.


    This model implements metered billing, where customers are charged based on
    This model implements metered billing, where customers are charged based on
    their actual measured usage of a service over a specific time period. The
    their actual measured usage of a service over a specific time period. The
    model supports different metering intervals and can generate invoices based
    model supports different metering intervals and can generate invoices based
    on the metered usage.
    on the metered usage.


    Key features:
    Key features:
    - Real-time usage tracking and cost calculation
    - Real-time usage tracking and cost calculation
    - Support for different metering intervals (hourly, daily, monthly)
    - Support for different metering intervals (hourly, daily, monthly)
    - Automatic invoice generation based on metered usage
    - Automatic invoice generation based on metered usage
    - Flexible pricing rules for different usage metrics
    - Flexible pricing rules for different usage metrics
    - Support for minimum and maximum billing amounts
    - Support for minimum and maximum billing amounts
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    name: str = "Metered Billing",
    name: str = "Metered Billing",
    description: str = "Pay only for what you use with precise metering",
    description: str = "Pay only for what you use with precise metering",
    billing_calculator: Optional[BillingCalculator] = None,
    billing_calculator: Optional[BillingCalculator] = None,
    usage_tracker: Optional[UsageTracker] = None,
    usage_tracker: Optional[UsageTracker] = None,
    invoice_manager: Optional[InvoiceManager] = None,
    invoice_manager: Optional[InvoiceManager] = None,
    metering_interval: str = MeteringInterval.MONTHLY,
    metering_interval: str = MeteringInterval.MONTHLY,
    minimum_bill_amount: float = 0.0,
    minimum_bill_amount: float = 0.0,
    maximum_bill_amount: Optional[float] = None,
    maximum_bill_amount: Optional[float] = None,
    auto_invoice: bool = True,
    auto_invoice: bool = True,
    prorate_partial_periods: bool = True,
    prorate_partial_periods: bool = True,
    ):
    ):
    """
    """
    Initialize a metered billing pricing model.
    Initialize a metered billing pricing model.


    Args:
    Args:
    name: Name of the pricing model
    name: Name of the pricing model
    description: Description of the pricing model
    description: Description of the pricing model
    billing_calculator: Billing calculator to use
    billing_calculator: Billing calculator to use
    usage_tracker: Usage tracker to use
    usage_tracker: Usage tracker to use
    invoice_manager: Invoice manager to use
    invoice_manager: Invoice manager to use
    metering_interval: Interval for metering (e.g., HOURLY, DAILY, MONTHLY)
    metering_interval: Interval for metering (e.g., HOURLY, DAILY, MONTHLY)
    minimum_bill_amount: Minimum amount to bill
    minimum_bill_amount: Minimum amount to bill
    maximum_bill_amount: Maximum amount to bill
    maximum_bill_amount: Maximum amount to bill
    auto_invoice: Whether to automatically generate invoices
    auto_invoice: Whether to automatically generate invoices
    prorate_partial_periods: Whether to prorate charges for partial periods
    prorate_partial_periods: Whether to prorate charges for partial periods
    """
    """
    super().__init__(
    super().__init__(
    name=name,
    name=name,
    description=description,
    description=description,
    billing_calculator=billing_calculator,
    billing_calculator=billing_calculator,
    usage_tracker=usage_tracker,
    usage_tracker=usage_tracker,
    )
    )


    self.invoice_manager = invoice_manager or InvoiceManager()
    self.invoice_manager = invoice_manager or InvoiceManager()
    self.metering_interval = metering_interval
    self.metering_interval = metering_interval
    self.minimum_bill_amount = minimum_bill_amount
    self.minimum_bill_amount = minimum_bill_amount
    self.maximum_bill_amount = maximum_bill_amount
    self.maximum_bill_amount = maximum_bill_amount
    self.auto_invoice = auto_invoice
    self.auto_invoice = auto_invoice
    self.prorate_partial_periods = prorate_partial_periods
    self.prorate_partial_periods = prorate_partial_periods
    self.billing_periods = {}  # Track billing periods by customer
    self.billing_periods = {}  # Track billing periods by customer


    def add_metered_metric(
    def add_metered_metric(
    self,
    self,
    metric: str,
    metric: str,
    price_per_unit: float,
    price_per_unit: float,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    ) -> PricingRule:
    ) -> PricingRule:
    """
    """
    Add a metered metric to the pricing model.
    Add a metered metric to the pricing model.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    price_per_unit: Price per unit
    price_per_unit: Price per unit
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource
    minimum_cost: Minimum cost for this metric
    minimum_cost: Minimum cost for this metric
    maximum_cost: Maximum cost for this metric
    maximum_cost: Maximum cost for this metric


    Returns:
    Returns:
    The created pricing rule
    The created pricing rule
    """
    """
    return self.add_per_unit_pricing(
    return self.add_per_unit_pricing(
    metric=metric,
    metric=metric,
    price_per_unit=price_per_unit,
    price_per_unit=price_per_unit,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    minimum_cost=minimum_cost,
    minimum_cost=minimum_cost,
    maximum_cost=maximum_cost,
    maximum_cost=maximum_cost,
    )
    )


    def add_metered_tiered_metric(
    def add_metered_tiered_metric(
    self,
    self,
    metric: str,
    metric: str,
    tiers: List[Dict[str, Any]],
    tiers: List[Dict[str, Any]],
    graduated: bool = True,
    graduated: bool = True,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    minimum_cost: float = 0.0,
    minimum_cost: float = 0.0,
    maximum_cost: Optional[float] = None,
    maximum_cost: Optional[float] = None,
    ) -> PricingRule:
    ) -> PricingRule:
    """
    """
    Add a metered metric with tiered pricing.
    Add a metered metric with tiered pricing.


    Args:
    Args:
    metric: Type of usage metric
    metric: Type of usage metric
    tiers: List of pricing tiers
    tiers: List of pricing tiers
    graduated: Whether to use graduated pricing
    graduated: Whether to use graduated pricing
    category: Category of usage
    category: Category of usage
    resource_type: Type of resource
    resource_type: Type of resource
    minimum_cost: Minimum cost for this metric
    minimum_cost: Minimum cost for this metric
    maximum_cost: Maximum cost for this metric
    maximum_cost: Maximum cost for this metric


    Returns:
    Returns:
    The created pricing rule
    The created pricing rule
    """
    """
    return self.add_tiered_pricing(
    return self.add_tiered_pricing(
    metric=metric,
    metric=metric,
    tiers=tiers,
    tiers=tiers,
    graduated=graduated,
    graduated=graduated,
    category=category,
    category=category,
    resource_type=resource_type,
    resource_type=resource_type,
    minimum_cost=minimum_cost,
    minimum_cost=minimum_cost,
    maximum_cost=maximum_cost,
    maximum_cost=maximum_cost,
    )
    )


    def set_metering_interval(self, interval: str) -> None:
    def set_metering_interval(self, interval: str) -> None:
    """
    """
    Set the metering interval.
    Set the metering interval.


    Args:
    Args:
    interval: Metering interval (e.g., HOURLY, DAILY, MONTHLY)
    interval: Metering interval (e.g., HOURLY, DAILY, MONTHLY)
    """
    """
    self.metering_interval = interval
    self.metering_interval = interval


    def get_interval_start_end(
    def get_interval_start_end(
    self,
    self,
    reference_time: Optional[datetime] = None,
    reference_time: Optional[datetime] = None,
    customer_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    ) -> Tuple[datetime, datetime]:
    ) -> Tuple[datetime, datetime]:
    """
    """
    Get the start and end times for the current metering interval.
    Get the start and end times for the current metering interval.


    Args:
    Args:
    reference_time: Reference time (defaults to now)
    reference_time: Reference time (defaults to now)
    customer_id: Customer ID for custom billing periods
    customer_id: Customer ID for custom billing periods


    Returns:
    Returns:
    Tuple of (start_time, end_time)
    Tuple of (start_time, end_time)
    """
    """
    now = reference_time or datetime.now()
    now = reference_time or datetime.now()


    # Check for custom billing period for this customer
    # Check for custom billing period for this customer
    if customer_id and customer_id in self.billing_periods:
    if customer_id and customer_id in self.billing_periods:
    period = self.billing_periods[customer_id]
    period = self.billing_periods[customer_id]
    if now >= period["start"] and now <= period["end"]:
    if now >= period["start"] and now <= period["end"]:
    return period["start"], period["end"]
    return period["start"], period["end"]


    # Calculate based on standard intervals
    # Calculate based on standard intervals
    if self.metering_interval == MeteringInterval.HOURLY:
    if self.metering_interval == MeteringInterval.HOURLY:
    start = datetime(now.year, now.month, now.day, now.hour)
    start = datetime(now.year, now.month, now.day, now.hour)
    end = start + timedelta(hours=1)
    end = start + timedelta(hours=1)
    elif self.metering_interval == MeteringInterval.DAILY:
    elif self.metering_interval == MeteringInterval.DAILY:
    start = datetime(now.year, now.month, now.day)
    start = datetime(now.year, now.month, now.day)
    end = start + timedelta(days=1)
    end = start + timedelta(days=1)
    elif self.metering_interval == MeteringInterval.WEEKLY:
    elif self.metering_interval == MeteringInterval.WEEKLY:
    # Start from Monday of the current week
    # Start from Monday of the current week
    start = datetime(now.year, now.month, now.day) - timedelta(
    start = datetime(now.year, now.month, now.day) - timedelta(
    days=now.weekday()
    days=now.weekday()
    )
    )
    end = start + timedelta(days=7)
    end = start + timedelta(days=7)
    elif self.metering_interval == MeteringInterval.MONTHLY:
    elif self.metering_interval == MeteringInterval.MONTHLY:
    start = datetime(now.year, now.month, 1)
    start = datetime(now.year, now.month, 1)
    # Calculate end of month
    # Calculate end of month
    if now.month == 12:
    if now.month == 12:
    end = datetime(now.year + 1, 1, 1)
    end = datetime(now.year + 1, 1, 1)
    else:
    else:
    end = datetime(now.year, now.month + 1, 1)
    end = datetime(now.year, now.month + 1, 1)
    else:
    else:
    # Default to daily if unknown interval
    # Default to daily if unknown interval
    start = datetime(now.year, now.month, now.day)
    start = datetime(now.year, now.month, now.day)
    end = start + timedelta(days=1)
    end = start + timedelta(days=1)


    return start, end
    return start, end


    def set_custom_billing_period(
    def set_custom_billing_period(
    self, customer_id: str, start_time: datetime, end_time: datetime
    self, customer_id: str, start_time: datetime, end_time: datetime
    ) -> None:
    ) -> None:
    """
    """
    Set a custom billing period for a customer.
    Set a custom billing period for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    start_time: Start time for the billing period
    start_time: Start time for the billing period
    end_time: End time for the billing period
    end_time: End time for the billing period
    """
    """
    self.billing_periods[customer_id] = {"start": start_time, "end": end_time}
    self.billing_periods[customer_id] = {"start": start_time, "end": end_time}


    def calculate_current_usage_cost(
    def calculate_current_usage_cost(
    self, customer_id: str, reference_time: Optional[datetime] = None
    self, customer_id: str, reference_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Calculate the cost for a customer's current usage period.
    Calculate the cost for a customer's current usage period.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    reference_time: Reference time (defaults to now)
    reference_time: Reference time (defaults to now)


    Returns:
    Returns:
    Dictionary with cost information
    Dictionary with cost information
    """
    """
    start_time, end_time = self.get_interval_start_end(
    start_time, end_time = self.get_interval_start_end(
    reference_time=reference_time, customer_id=customer_id
    reference_time=reference_time, customer_id=customer_id
    )
    )


    return self.calculate_cost(
    return self.calculate_cost(
    customer_id=customer_id, start_time=start_time, end_time=end_time
    customer_id=customer_id, start_time=start_time, end_time=end_time
    )
    )


    def generate_invoice(
    def generate_invoice(
    self,
    self,
    customer_id: str,
    customer_id: str,
    reference_time: Optional[datetime] = None,
    reference_time: Optional[datetime] = None,
    due_days: int = 30,
    due_days: int = 30,
    customer_info: Optional[Dict[str, str]] = None,
    customer_info: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Generate an invoice for a customer's usage.
    Generate an invoice for a customer's usage.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    reference_time: Reference time (defaults to now)
    reference_time: Reference time (defaults to now)
    due_days: Number of days until the invoice is due
    due_days: Number of days until the invoice is due
    customer_info: Customer information for the invoice
    customer_info: Customer information for the invoice
    metadata: Additional metadata for the invoice
    metadata: Additional metadata for the invoice


    Returns:
    Returns:
    Dictionary with invoice information
    Dictionary with invoice information
    """
    """
    # Get the billing period
    # Get the billing period
    start_time, end_time = self.get_interval_start_end(
    start_time, end_time = self.get_interval_start_end(
    reference_time=reference_time, customer_id=customer_id
    reference_time=reference_time, customer_id=customer_id
    )
    )


    # Calculate the cost
    # Calculate the cost
    cost = self.calculate_cost(
    cost = self.calculate_cost(
    customer_id=customer_id, start_time=start_time, end_time=end_time
    customer_id=customer_id, start_time=start_time, end_time=end_time
    )
    )


    # Apply minimum and maximum bill amounts
    # Apply minimum and maximum bill amounts
    total_cost = cost["total"]
    total_cost = cost["total"]
    if total_cost < self.minimum_bill_amount:
    if total_cost < self.minimum_bill_amount:
    total_cost = self.minimum_bill_amount
    total_cost = self.minimum_bill_amount


    if (
    if (
    self.maximum_bill_amount is not None
    self.maximum_bill_amount is not None
    and total_cost > self.maximum_bill_amount
    and total_cost > self.maximum_bill_amount
    ):
    ):
    total_cost = self.maximum_bill_amount
    total_cost = self.maximum_bill_amount


    # Calculate due date
    # Calculate due date
    due_date = datetime.now() + timedelta(days=due_days)
    due_date = datetime.now() + timedelta(days=due_days)


    # Generate the invoice
    # Generate the invoice
    invoice = self.invoice_manager.generate_invoice_from_usage(
    invoice = self.invoice_manager.generate_invoice_from_usage(
    customer_id=customer_id,
    customer_id=customer_id,
    start_time=start_time,
    start_time=start_time,
    end_time=end_time,
    end_time=end_time,
    due_date=due_date,
    due_date=due_date,
    customer_info=customer_info,
    customer_info=customer_info,
    metadata=metadata,
    metadata=metadata,
    )
    )


    if invoice:
    if invoice:
    return {
    return {
    "invoice_id": invoice.id,
    "invoice_id": invoice.id,
    "customer_id": customer_id,
    "customer_id": customer_id,
    "start_time": start_time,
    "start_time": start_time,
    "end_time": end_time,
    "end_time": end_time,
    "total_amount": total_cost,
    "total_amount": total_cost,
    "due_date": due_date,
    "due_date": due_date,
    "status": invoice.status,
    "status": invoice.status,
    "items": [
    "items": [
    {"description": item.description, "amount": item.amount}
    {"description": item.description, "amount": item.amount}
    for item in invoice.items
    for item in invoice.items
    ],
    ],
    "invoice_url": invoice.metadata.get("invoice_url"),
    "invoice_url": invoice.metadata.get("invoice_url"),
    }
    }


    return {
    return {
    "error": "Failed to generate invoice",
    "error": "Failed to generate invoice",
    "customer_id": customer_id,
    "customer_id": customer_id,
    "start_time": start_time,
    "start_time": start_time,
    "end_time": end_time,
    "end_time": end_time,
    "total_amount": total_cost,
    "total_amount": total_cost,
    }
    }


    def track_usage_and_bill(
    def track_usage_and_bill(
    self,
    self,
    customer_id: str,
    customer_id: str,
    metric: str,
    metric: str,
    quantity: float,
    quantity: float,
    category: Optional[str] = None,
    category: Optional[str] = None,
    resource_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Track usage and calculate the current bill.
    Track usage and calculate the current bill.


    This method tracks usage for a customer and returns the current bill amount.
    This method tracks usage for a customer and returns the current bill amount.
    If auto_invoice is enabled and the billing period has ended, it will also
    If auto_invoice is enabled and the billing period has ended, it will also
    generate an invoice.
    generate an invoice.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    metric: Type of usage metric
    metric: Type of usage metric
    quantity: Quantity of usage
    quantity: Quantity of usage
    category: Category of usage
    category: Category of usage
    resource_id: ID of the resource being used
    resource_id: ID of the resource being used
    resource_type: Type of resource being used
    resource_type: Type of resource being used
    metadata: Additional metadata for the usage record
    metadata: Additional metadata for the usage record


    Returns:
    Returns:
    Dictionary with usage and billing information
    Dictionary with usage and billing information
    """
    """
    # Track the usage
    # Track the usage
    record, quota, exceeded = self.usage_tracker.track_usage(
    record, quota, exceeded = self.usage_tracker.track_usage(
    customer_id=customer_id,
    customer_id=customer_id,
    metric=metric,
    metric=metric,
    quantity=quantity,
    quantity=quantity,
    category=category or UsageCategory.INFERENCE,
    category=category or UsageCategory.INFERENCE,
    resource_id=resource_id,
    resource_id=resource_id,
    resource_type=resource_type,
    resource_type=resource_type,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Calculate the current cost
    # Calculate the current cost
    cost = self.calculate_current_usage_cost(customer_id=customer_id)
    cost = self.calculate_current_usage_cost(customer_id=customer_id)


    result = {
    result = {
    "usage_record_id": record.id,
    "usage_record_id": record.id,
    "customer_id": customer_id,
    "customer_id": customer_id,
    "metric": metric,
    "metric": metric,
    "quantity": quantity,
    "quantity": quantity,
    "timestamp": record.timestamp,
    "timestamp": record.timestamp,
    "current_cost": cost["total"],
    "current_cost": cost["total"],
    "cost_breakdown": cost["breakdown"],
    "cost_breakdown": cost["breakdown"],
    }
    }


    # Check if we need to generate an invoice
    # Check if we need to generate an invoice
    if self.auto_invoice:
    if self.auto_invoice:
    now = datetime.now()
    now = datetime.now()
    _, period_end = self.get_interval_start_end(
    _, period_end = self.get_interval_start_end(
    reference_time=now, customer_id=customer_id
    reference_time=now, customer_id=customer_id
    )
    )


    # If we're at the end of the billing period, generate an invoice
    # If we're at the end of the billing period, generate an invoice
    if now >= period_end - timedelta(minutes=5):  # 5-minute buffer
    if now >= period_end - timedelta(minutes=5):  # 5-minute buffer
    invoice_result = self.generate_invoice(customer_id=customer_id)
    invoice_result = self.generate_invoice(customer_id=customer_id)
    result["invoice"] = invoice_result
    result["invoice"] = invoice_result


    return result
    return result




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a metered billing model
    # Create a metered billing model
    model = MeteredBillingPricing(
    model = MeteredBillingPricing(
    name="API Metered Billing",
    name="API Metered Billing",
    description="Pay only for the API calls you make",
    description="Pay only for the API calls you make",
    metering_interval=MeteringInterval.DAILY,
    metering_interval=MeteringInterval.DAILY,
    )
    )


    # Add metered metrics
    # Add metered metrics
    model.add_metered_metric(
    model.add_metered_metric(
    metric=UsageMetric.API_CALL,
    metric=UsageMetric.API_CALL,
    price_per_unit=0.01,
    price_per_unit=0.01,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    )
    )


    model.add_metered_tiered_metric(
    model.add_metered_tiered_metric(
    metric=UsageMetric.TOKEN,
    metric=UsageMetric.TOKEN,
    tiers=[
    tiers=[
    {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.001},
    {"min_quantity": 0, "max_quantity": 1000, "price_per_unit": 0.001},
    {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0008},
    {"min_quantity": 1000, "max_quantity": 10000, "price_per_unit": 0.0008},
    {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.0005},
    {"min_quantity": 10000, "max_quantity": None, "price_per_unit": 0.0005},
    ],
    ],
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    )
    )


    # Track some usage
    # Track some usage
    customer_id = "customer123"
    customer_id = "customer123"


    result = model.track_usage_and_bill(
    result = model.track_usage_and_bill(
    customer_id=customer_id,
    customer_id=customer_id,
    metric=UsageMetric.API_CALL,
    metric=UsageMetric.API_CALL,
    quantity=100,
    quantity=100,
    category=UsageCategory.INFERENCE,
    category=UsageCategory.INFERENCE,
    resource_id="model_gpt4",
    resource_id="model_gpt4",
    resource_type="model",
    resource_type="model",
    metadata={"endpoint": "/v1/completions"},
    metadata={"endpoint": "/v1/completions"},
    )
    )


    print(f"Tracked usage: {result['quantity']} {result['metric']}")
    print(f"Tracked usage: {result['quantity']} {result['metric']}")
    print(f"Current cost: ${result['current_cost']:.2f}")
    print(f"Current cost: ${result['current_cost']:.2f}")
    print(f"Cost breakdown: {result['cost_breakdown']}")
    print(f"Cost breakdown: {result['cost_breakdown']}")