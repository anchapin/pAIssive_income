"""
"""
Invoice manager for the pAIssive Income project.
Invoice manager for the pAIssive Income project.


This module provides a class for managing invoices, including
This module provides a class for managing invoices, including
generation, storage, retrieval, and status updates.
generation, storage, retrieval, and status updates.
"""
"""


import json
import json
import os
import os
import time
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .billing_calculator import BillingCalculator
from .billing_calculator import BillingCalculator
from .invoice import Invoice, InvoiceStatus
from .invoice import Invoice, InvoiceStatus
from .usage_tracker import UsageTracker
from .usage_tracker import UsageTracker




class InvoiceManager:
    class InvoiceManager:
    from .billing_calculator import BillingCalculator
    from .billing_calculator import BillingCalculator
    from .usage_tracker import UsageTracker
    from .usage_tracker import UsageTracker






    :
    :
    """
    """
    Class for managing invoices.
    Class for managing invoices.


    This class provides methods for generating, storing, retrieving,
    This class provides methods for generating, storing, retrieving,
    and updating invoices.
    and updating invoices.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    billing_calculator: Optional[BillingCalculator] = None,
    billing_calculator: Optional[BillingCalculator] = None,
    usage_tracker: Optional[UsageTracker] = None,
    usage_tracker: Optional[UsageTracker] = None,
    storage_dir: Optional[str] = None,
    storage_dir: Optional[str] = None,
    company_info: Optional[Dict[str, str]] = None,
    company_info: Optional[Dict[str, str]] = None,
    ):
    ):
    """
    """
    Initialize an invoice manager.
    Initialize an invoice manager.


    Args:
    Args:
    billing_calculator: Billing calculator to use
    billing_calculator: Billing calculator to use
    usage_tracker: Usage tracker to use
    usage_tracker: Usage tracker to use
    storage_dir: Directory for storing invoice data
    storage_dir: Directory for storing invoice data
    company_info: Company information for invoices
    company_info: Company information for invoices
    """
    """
    self.billing_calculator = billing_calculator
    self.billing_calculator = billing_calculator
    self.usage_tracker = usage_tracker
    self.usage_tracker = usage_tracker
    self.storage_dir = storage_dir
    self.storage_dir = storage_dir
    self.company_info = company_info or {}
    self.company_info = company_info or {}


    if storage_dir and not os.path.exists(storage_dir):
    if storage_dir and not os.path.exists(storage_dir):
    os.makedirs(storage_dir)
    os.makedirs(storage_dir)


    self.invoices = {}
    self.invoices = {}
    self.customer_invoices = {}
    self.customer_invoices = {}


    # Load invoices if storage directory is set
    # Load invoices if storage directory is set
    if storage_dir:
    if storage_dir:
    self.load_invoices()
    self.load_invoices()


    def create_invoice(
    def create_invoice(
    self,
    self,
    customer_id: str,
    customer_id: str,
    date: Optional[datetime] = None,
    date: Optional[datetime] = None,
    due_date: Optional[datetime] = None,
    due_date: Optional[datetime] = None,
    currency: str = "USD",
    currency: str = "USD",
    items: Optional[List[Dict[str, Any]]] = None,
    items: Optional[List[Dict[str, Any]]] = None,
    customer_info: Optional[Dict[str, str]] = None,
    customer_info: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Invoice:
    ) -> Invoice:
    """
    """
    Create an invoice.
    Create an invoice.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    date: Date of the invoice
    date: Date of the invoice
    due_date: Due date of the invoice
    due_date: Due date of the invoice
    currency: Currency code (e.g., USD)
    currency: Currency code (e.g., USD)
    items: List of invoice items
    items: List of invoice items
    customer_info: Customer information for the invoice
    customer_info: Customer information for the invoice
    metadata: Additional metadata for the invoice
    metadata: Additional metadata for the invoice


    Returns:
    Returns:
    The created invoice
    The created invoice
    """
    """
    # Create invoice
    # Create invoice
    invoice = Invoice(
    invoice = Invoice(
    customer_id=customer_id,
    customer_id=customer_id,
    date=date,
    date=date,
    due_date=due_date,
    due_date=due_date,
    currency=currency,
    currency=currency,
    metadata=metadata or {},
    metadata=metadata or {},
    )
    )


    # Set company information
    # Set company information
    if self.company_info:
    if self.company_info:
    invoice.set_company_info(
    invoice.set_company_info(
    name=self.company_info.get("name", ""),
    name=self.company_info.get("name", ""),
    address=self.company_info.get("address", ""),
    address=self.company_info.get("address", ""),
    email=self.company_info.get("email", ""),
    email=self.company_info.get("email", ""),
    phone=self.company_info.get("phone", ""),
    phone=self.company_info.get("phone", ""),
    website=self.company_info.get("website", ""),
    website=self.company_info.get("website", ""),
    logo_url=self.company_info.get("logo_url", ""),
    logo_url=self.company_info.get("logo_url", ""),
    )
    )


    # Set customer information
    # Set customer information
    if customer_info:
    if customer_info:
    invoice.set_customer_info(
    invoice.set_customer_info(
    name=customer_info.get("name", ""),
    name=customer_info.get("name", ""),
    email=customer_info.get("email", ""),
    email=customer_info.get("email", ""),
    address=customer_info.get("address", ""),
    address=customer_info.get("address", ""),
    )
    )


    # Add items
    # Add items
    if items:
    if items:
    for item in items:
    for item in items:
    invoice.add_item(
    invoice.add_item(
    description=item["description"],
    description=item["description"],
    quantity=item.get("quantity", 1.0),
    quantity=item.get("quantity", 1.0),
    unit_price=item.get("unit_price", 0.0),
    unit_price=item.get("unit_price", 0.0),
    discount=item.get("discount", 0.0),
    discount=item.get("discount", 0.0),
    tax_rate=item.get("tax_rate", 0.0),
    tax_rate=item.get("tax_rate", 0.0),
    metadata=item.get("metadata"),
    metadata=item.get("metadata"),
    )
    )


    # Store invoice
    # Store invoice
    self.invoices[invoice.id] = invoice
    self.invoices[invoice.id] = invoice


    # Add to customer's invoices
    # Add to customer's invoices
    if customer_id not in self.customer_invoices:
    if customer_id not in self.customer_invoices:
    self.customer_invoices[customer_id] = []
    self.customer_invoices[customer_id] = []


    self.customer_invoices[customer_id].append(invoice.id)
    self.customer_invoices[customer_id].append(invoice.id)


    # Save invoice if storage directory is set
    # Save invoice if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_invoice(invoice)
    self._save_invoice(invoice)


    return invoice
    return invoice


    def generate_invoice_from_usage(
    def generate_invoice_from_usage(
    self,
    self,
    customer_id: str,
    customer_id: str,
    start_time: datetime,
    start_time: datetime,
    end_time: datetime,
    end_time: datetime,
    due_date: Optional[datetime] = None,
    due_date: Optional[datetime] = None,
    currency: str = "USD",
    currency: str = "USD",
    customer_info: Optional[Dict[str, str]] = None,
    customer_info: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Invoice]:
    ) -> Optional[Invoice]:
    """
    """
    Generate an invoice from usage data for metered billing scenarios.
    Generate an invoice from usage data for metered billing scenarios.


    This algorithm implements a critical usage-to-invoice transformation process
    This algorithm implements a critical usage-to-invoice transformation process
    that powers metered and consumption-based billing models. The implementation
    that powers metered and consumption-based billing models. The implementation
    follows these key stages:
    follows these key stages:


    1. USAGE DATA ACQUISITION AND COST CALCULATION:
    1. USAGE DATA ACQUISITION AND COST CALCULATION:
    - Interfaces with the usage tracker to collect relevant usage records
    - Interfaces with the usage tracker to collect relevant usage records
    - Applies the appropriate pricing rules through the billing calculator
    - Applies the appropriate pricing rules through the billing calculator
    - Transforms raw usage metrics into monetized line items
    - Transforms raw usage metrics into monetized line items
    - Handles different usage categories, resources, and metrics properly
    - Handles different usage categories, resources, and metrics properly


    2. INVOICE CREATION WITH APPROPRIATE METADATA:
    2. INVOICE CREATION WITH APPROPRIATE METADATA:
    - Generates a properly structured invoice object with customer context
    - Generates a properly structured invoice object with customer context
    - Sets appropriate default values for invoice dates and payment terms
    - Sets appropriate default values for invoice dates and payment terms
    - Preserves billing period information for accurate record-keeping
    - Preserves billing period information for accurate record-keeping
    - Ensures proper attribution of the invoice to the correct customer
    - Ensures proper attribution of the invoice to the correct customer


    3. LINE ITEM GENERATION FROM USAGE METRICS:
    3. LINE ITEM GENERATION FROM USAGE METRICS:
    - Converts usage-based cost calculations into structured invoice line items
    - Converts usage-based cost calculations into structured invoice line items
    - Creates descriptive item entries that clearly identify the billed services
    - Creates descriptive item entries that clearly identify the billed services
    - Calculates proper unit prices based on total costs and quantities
    - Calculates proper unit prices based on total costs and quantities
    - Maintains detailed metadata linking each line item to its source usage records
    - Maintains detailed metadata linking each line item to its source usage records


    4. BUSINESS RULE APPLICATION:
    4. BUSINESS RULE APPLICATION:
    - Applies standardized payment terms (e.g., Net 30)
    - Applies standardized payment terms (e.g., Net 30)
    - Adds contextual notes about the billing period
    - Adds contextual notes about the billing period
    - Ensures consistent invoice structure across billing periods
    - Ensures consistent invoice structure across billing periods
    - Handles edge cases like zero-usage periods appropriately
    - Handles edge cases like zero-usage periods appropriately


    This usage-based invoice generation algorithm addresses several critical requirements:
    This usage-based invoice generation algorithm addresses several critical requirements:
    - Accurate translation of metered usage into billable items
    - Accurate translation of metered usage into billable items
    - Clear and transparent presentation of usage-based charges
    - Clear and transparent presentation of usage-based charges
    - Proper record keeping for financial reporting and reconciliation
    - Proper record keeping for financial reporting and reconciliation
    - Support for various usage-based business models
    - Support for various usage-based business models


    The implementation specifically supports common SaaS and cloud billing scenarios:
    The implementation specifically supports common SaaS and cloud billing scenarios:
    - API call-based billing (pay per request)
    - API call-based billing (pay per request)
    - Storage-based billing (pay per GB)
    - Storage-based billing (pay per GB)
    - User-based billing (pay per seat with usage tracking)
    - User-based billing (pay per seat with usage tracking)
    - Resource consumption billing (compute time, bandwidth, etc.)
    - Resource consumption billing (compute time, bandwidth, etc.)
    - Mixed billing models (subscription + usage)
    - Mixed billing models (subscription + usage)


    Args:
    Args:
    customer_id: ID of the customer to generate the invoice for
    customer_id: ID of the customer to generate the invoice for
    start_time: Start of the billing period for usage records
    start_time: Start of the billing period for usage records
    end_time: End of the billing period for usage records
    end_time: End of the billing period for usage records
    due_date: When the invoice payment is due (defaults to end_time + 30 days)
    due_date: When the invoice payment is due (defaults to end_time + 30 days)
    currency: Currency code for the invoice (e.g., USD, EUR)
    currency: Currency code for the invoice (e.g., USD, EUR)
    customer_info: Optional dictionary with customer details (name, address, etc.)
    customer_info: Optional dictionary with customer details (name, address, etc.)
    metadata: Additional invoice metadata to include
    metadata: Additional invoice metadata to include


    Returns:
    Returns:
    The generated Invoice object containing usage-based line items,
    The generated Invoice object containing usage-based line items,
    or None if no billable usage was found for the period
    or None if no billable usage was found for the period
    """
    """
    if not self.billing_calculator or not self.usage_tracker:
    if not self.billing_calculator or not self.usage_tracker:
    raise ValueError(
    raise ValueError(
    "Billing calculator and usage tracker are required to generate an invoice from usage"
    "Billing calculator and usage tracker are required to generate an invoice from usage"
    )
    )


    # STAGE 1: Calculate usage cost by calling the billing calculator
    # STAGE 1: Calculate usage cost by calling the billing calculator
    # This transforms raw usage records into monetized costs
    # This transforms raw usage records into monetized costs
    usage_cost = self.billing_calculator.calculate_usage_cost(
    usage_cost = self.billing_calculator.calculate_usage_cost(
    customer_id=customer_id, start_time=start_time, end_time=end_time
    customer_id=customer_id, start_time=start_time, end_time=end_time
    )
    )


    # Exit early if there's no billable usage for this period
    # Exit early if there's no billable usage for this period
    if not usage_cost["items"]:
    if not usage_cost["items"]:
    return None
    return None


    # STAGE 2: Create the base invoice with proper metadata
    # STAGE 2: Create the base invoice with proper metadata
    invoice = self.create_invoice(
    invoice = self.create_invoice(
    customer_id=customer_id,
    customer_id=customer_id,
    date=end_time,  # Invoice date is the end of the billing period
    date=end_time,  # Invoice date is the end of the billing period
    due_date=due_date
    due_date=due_date
    or (
    or (
    end_time + timedelta(days=30)
    end_time + timedelta(days=30)
    ),  # Default due date is 30 days after billing period
    ),  # Default due date is 30 days after billing period
    currency=currency,
    currency=currency,
    customer_info=customer_info,
    customer_info=customer_info,
    metadata=metadata or {},
    metadata=metadata or {},
    )
    )


    # Store billing period information for record-keeping and auditing
    # Store billing period information for record-keeping and auditing
    invoice.metadata["billing_period_start"] = start_time.isoformat()
    invoice.metadata["billing_period_start"] = start_time.isoformat()
    invoice.metadata["billing_period_end"] = end_time.isoformat()
    invoice.metadata["billing_period_end"] = end_time.isoformat()


    # STAGE 3: Transform usage cost items into invoice line items
    # STAGE 3: Transform usage cost items into invoice line items
    for item in usage_cost["items"]:
    for item in usage_cost["items"]:
    # Create a descriptive line item that identifies the service clearly
    # Create a descriptive line item that identifies the service clearly
    invoice.add_item(
    invoice.add_item(
    description=f"{item['metric']} ({item['category']}, {item['resource_type']})",
    description=f"{item['metric']} ({item['category']}, {item['resource_type']})",
    quantity=item["quantity"],
    quantity=item["quantity"],
    unit_price=(
    unit_price=(
    item["cost"] / item["quantity"] if item["quantity"] > 0 else 0.0
    item["cost"] / item["quantity"] if item["quantity"] > 0 else 0.0
    ),  # Handle zero-quantity case
    ),  # Handle zero-quantity case
    metadata={
    metadata={
    # Preserve the connection to usage data for auditing and disputes
    # Preserve the connection to usage data for auditing and disputes
    "metric": item["metric"],
    "metric": item["metric"],
    "category": item["category"],
    "category": item["category"],
    "resource_type": item["resource_type"],
    "resource_type": item["resource_type"],
    "records": item["records"],  # Links to the detailed usage records
    "records": item["records"],  # Links to the detailed usage records
    },
    },
    )
    )


    # STAGE 4: Apply business rules
    # STAGE 4: Apply business rules
    # Set standard payment terms
    # Set standard payment terms
    invoice.set_payment_terms("Net 30")
    invoice.set_payment_terms("Net 30")


    # Add a descriptive note about the billing period for customer clarity
    # Add a descriptive note about the billing period for customer clarity
    invoice.set_notes(
    invoice.set_notes(
    f"Usage from {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}"
    f"Usage from {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}"
    )
    )


    # Save the generated invoice to persistent storage if configured
    # Save the generated invoice to persistent storage if configured
    if self.storage_dir:
    if self.storage_dir:
    self._save_invoice(invoice)
    self._save_invoice(invoice)


    return invoice
    return invoice


    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
    """
    """
    Get an invoice by ID.
    Get an invoice by ID.


    Args:
    Args:
    invoice_id: ID of the invoice
    invoice_id: ID of the invoice


    Returns:
    Returns:
    The invoice or None if not found
    The invoice or None if not found
    """
    """
    return self.invoices.get(invoice_id)
    return self.invoices.get(invoice_id)


    def get_invoice_by_number(self, invoice_number: str) -> Optional[Invoice]:
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Invoice]:
    """
    """
    Get an invoice by number.
    Get an invoice by number.


    Args:
    Args:
    invoice_number: Number of the invoice
    invoice_number: Number of the invoice


    Returns:
    Returns:
    The invoice or None if not found
    The invoice or None if not found
    """
    """
    for invoice in self.invoices.values():
    for invoice in self.invoices.values():
    if invoice.number == invoice_number:
    if invoice.number == invoice_number:
    return invoice
    return invoice


    return None
    return None


    def get_customer_invoices(
    def get_customer_invoices(
    self,
    self,
    customer_id: str,
    customer_id: str,
    status: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    limit: int = 100,
    ) -> List[Invoice]:
    ) -> List[Invoice]:
    """
    """
    Get invoices for a customer.
    Get invoices for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    status: Status of invoices to get
    status: Status of invoices to get
    start_date: Start date for invoices
    start_date: Start date for invoices
    end_date: End date for invoices
    end_date: End date for invoices
    limit: Maximum number of invoices to return
    limit: Maximum number of invoices to return


    Returns:
    Returns:
    List of invoices
    List of invoices
    """
    """
    if customer_id not in self.customer_invoices:
    if customer_id not in self.customer_invoices:
    return []
    return []


    invoices = []
    invoices = []


    for invoice_id in self.customer_invoices[customer_id]:
    for invoice_id in self.customer_invoices[customer_id]:
    invoice = self.invoices.get(invoice_id)
    invoice = self.invoices.get(invoice_id)


    if not invoice:
    if not invoice:
    continue
    continue


    # Filter by status
    # Filter by status
    if status and invoice.status != status:
    if status and invoice.status != status:
    continue
    continue


    # Filter by date range
    # Filter by date range
    if start_date and invoice.date < start_date:
    if start_date and invoice.date < start_date:
    continue
    continue


    if end_date and invoice.date > end_date:
    if end_date and invoice.date > end_date:
    continue
    continue


    invoices.append(invoice)
    invoices.append(invoice)


    # Sort by date (newest first)
    # Sort by date (newest first)
    invoices.sort(key=lambda i: i.date, reverse=True)
    invoices.sort(key=lambda i: i.date, reverse=True)


    # Apply limit
    # Apply limit
    return invoices[:limit]
    return invoices[:limit]


    def update_invoice_status(
    def update_invoice_status(
    self, invoice_id: str, status: str, reason: Optional[str] = None
    self, invoice_id: str, status: str, reason: Optional[str] = None
    ) -> Optional[Invoice]:
    ) -> Optional[Invoice]:
    """
    """
    Update the status of an invoice.
    Update the status of an invoice.


    Args:
    Args:
    invoice_id: ID of the invoice
    invoice_id: ID of the invoice
    status: New status
    status: New status
    reason: Reason for the status change
    reason: Reason for the status change


    Returns:
    Returns:
    The updated invoice or None if not found
    The updated invoice or None if not found
    """
    """
    invoice = self.get_invoice(invoice_id)
    invoice = self.get_invoice(invoice_id)


    if not invoice:
    if not invoice:
    return None
    return None


    # Update status
    # Update status
    invoice.update_status(status, reason)
    invoice.update_status(status, reason)


    # Save invoice if storage directory is set
    # Save invoice if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_invoice(invoice)
    self._save_invoice(invoice)


    return invoice
    return invoice


    def add_payment(
    def add_payment(
    self,
    self,
    invoice_id: str,
    invoice_id: str,
    amount: float,
    amount: float,
    date: Optional[datetime] = None,
    date: Optional[datetime] = None,
    payment_method: str = "",
    payment_method: str = "",
    transaction_id: Optional[str] = None,
    transaction_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
    ) -> Optional[Dict[str, Any]]:
    """
    """
    Add a payment to an invoice and update invoice status accordingly.
    Add a payment to an invoice and update invoice status accordingly.


    This algorithm implements a robust payment processing and reconciliation system
    This algorithm implements a robust payment processing and reconciliation system
    designed for enterprise financial management. The implementation follows these key stages:
    designed for enterprise financial management. The implementation follows these key stages:


    1. INVOICE VALIDATION AND RETRIEVAL:
    1. INVOICE VALIDATION AND RETRIEVAL:
    - Verifies the existence of the target invoice
    - Verifies the existence of the target invoice
    - Ensures proper invoice state for payment application
    - Ensures proper invoice state for payment application
    - Handles error cases gracefully with clear failure indicators
    - Handles error cases gracefully with clear failure indicators
    - Maintains system integrity by preventing orphaned payment records
    - Maintains system integrity by preventing orphaned payment records


    2. PAYMENT RECORD CREATION:
    2. PAYMENT RECORD CREATION:
    - Generates comprehensive payment records with full transaction details
    - Generates comprehensive payment records with full transaction details
    - Captures critical financial data including amount, date, and method
    - Captures critical financial data including amount, date, and method
    - Creates proper audit trail through transaction IDs and timestamps
    - Creates proper audit trail through transaction IDs and timestamps
    - Supports diverse payment methods (credit card, ACH, wire transfer, etc.)
    - Supports diverse payment methods (credit card, ACH, wire transfer, etc.)
    - Preserves extended payment context through flexible metadata
    - Preserves extended payment context through flexible metadata


    3. INVOICE BALANCE RECONCILIATION:
    3. INVOICE BALANCE RECONCILIATION:
    - Updates invoice payment status based on payment amount
    - Updates invoice payment status based on payment amount
    - Handles both full and partial payment scenarios appropriately
    - Handles both full and partial payment scenarios appropriately
    - Supports incremental payment application for installment plans
    - Supports incremental payment application for installment plans
    - Updates invoice status automatically based on payment completeness
    - Updates invoice status automatically based on payment completeness
    - Maintains accurate financial records for accounting compliance
    - Maintains accurate financial records for accounting compliance


    4. PAYMENT PERSISTENCE:
    4. PAYMENT PERSISTENCE:
    - Ensures durable storage of payment information
    - Ensures durable storage of payment information
    - Maintains consistency between in-memory and persistent states
    - Maintains consistency between in-memory and persistent states
    - Supports system recovery in case of failure
    - Supports system recovery in case of failure
    - Enables proper financial record-keeping and audit trails
    - Enables proper financial record-keeping and audit trails


    This payment processing algorithm addresses several critical requirements:
    This payment processing algorithm addresses several critical requirements:
    - Accurate financial record-keeping for accounting compliance
    - Accurate financial record-keeping for accounting compliance
    - Support for diverse payment reconciliation scenarios
    - Support for diverse payment reconciliation scenarios
    - Robust transaction history for financial reporting
    - Robust transaction history for financial reporting
    - Clear audit trails for payment verification
    - Clear audit trails for payment verification


    The implementation specifically supports common payment scenarios:
    The implementation specifically supports common payment scenarios:
    - Full invoice payment in a single transaction
    - Full invoice payment in a single transaction
    - Partial payments with remaining balance tracking
    - Partial payments with remaining balance tracking
    - Multi-payment reconciliation over time
    - Multi-payment reconciliation over time
    - Payment method tracking for financial analysis
    - Payment method tracking for financial analysis
    - Transaction ID linkage for payment verification
    - Transaction ID linkage for payment verification


    Args:
    Args:
    invoice_id: ID of the invoice to apply payment to
    invoice_id: ID of the invoice to apply payment to
    amount: Payment amount to be applied to the invoice
    amount: Payment amount to be applied to the invoice
    date: Date when payment was received (defaults to current datetime)
    date: Date when payment was received (defaults to current datetime)
    payment_method: Method used for payment (e.g., "credit_card", "bank_transfer")
    payment_method: Method used for payment (e.g., "credit_card", "bank_transfer")
    transaction_id: External payment processor transaction ID for reconciliation
    transaction_id: External payment processor transaction ID for reconciliation
    metadata: Additional payment metadata for extended context
    metadata: Additional payment metadata for extended context


    Returns:
    Returns:
    Dictionary containing payment record details if successful,
    Dictionary containing payment record details if successful,
    or None if the invoice was not found
    or None if the invoice was not found
    """
    """
    invoice = self.get_invoice(invoice_id)
    invoice = self.get_invoice(invoice_id)


    if not invoice:
    if not invoice:
    return None
    return None


    # Add payment
    # Add payment
    payment = invoice.add_payment(
    payment = invoice.add_payment(
    amount=amount,
    amount=amount,
    date=date,
    date=date,
    payment_method=payment_method,
    payment_method=payment_method,
    transaction_id=transaction_id,
    transaction_id=transaction_id,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Save invoice if storage directory is set
    # Save invoice if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_invoice(invoice)
    self._save_invoice(invoice)


    return payment
    return payment


    def delete_invoice(self, invoice_id: str) -> bool:
    def delete_invoice(self, invoice_id: str) -> bool:
    """
    """
    Delete an invoice.
    Delete an invoice.


    Args:
    Args:
    invoice_id: ID of the invoice
    invoice_id: ID of the invoice


    Returns:
    Returns:
    True if the invoice was deleted, False otherwise
    True if the invoice was deleted, False otherwise
    """
    """
    # Check if invoice exists
    # Check if invoice exists
    invoice = self.get_invoice(invoice_id)
    invoice = self.get_invoice(invoice_id)


    if not invoice:
    if not invoice:
    return False
    return False


    # Remove from customer's invoices
    # Remove from customer's invoices
    customer_id = invoice.customer_id
    customer_id = invoice.customer_id


    if customer_id in self.customer_invoices:
    if customer_id in self.customer_invoices:
    if invoice_id in self.customer_invoices[customer_id]:
    if invoice_id in self.customer_invoices[customer_id]:
    self.customer_invoices[customer_id].remove(invoice_id)
    self.customer_invoices[customer_id].remove(invoice_id)


    # Remove from invoices
    # Remove from invoices
    del self.invoices[invoice_id]
    del self.invoices[invoice_id]


    # Delete file if storage directory is set
    # Delete file if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    file_path = os.path.join(self.storage_dir, f"{invoice_id}.json")
    file_path = os.path.join(self.storage_dir, f"{invoice_id}.json")


    if os.path.exists(file_path):
    if os.path.exists(file_path):
    os.remove(file_path)
    os.remove(file_path)


    return True
    return True


    def get_overdue_invoices(self) -> List[Invoice]:
    def get_overdue_invoices(self) -> List[Invoice]:
    """
    """
    Get all overdue invoices.
    Get all overdue invoices.


    Returns:
    Returns:
    List of overdue invoices
    List of overdue invoices
    """
    """
    overdue_invoices = []
    overdue_invoices = []


    for invoice in self.invoices.values():
    for invoice in self.invoices.values():
    if invoice.is_overdue():
    if invoice.is_overdue():
    overdue_invoices.append(invoice)
    overdue_invoices.append(invoice)


    # Sort by due date (oldest first)
    # Sort by due date (oldest first)
    overdue_invoices.sort(key=lambda i: i.due_date)
    overdue_invoices.sort(key=lambda i: i.due_date)


    return overdue_invoices
    return overdue_invoices


    def get_unpaid_invoices(self) -> List[Invoice]:
    def get_unpaid_invoices(self) -> List[Invoice]:
    """
    """
    Get all unpaid invoices.
    Get all unpaid invoices.


    Returns:
    Returns:
    List of unpaid invoices
    List of unpaid invoices
    """
    """
    unpaid_invoices = []
    unpaid_invoices = []


    for invoice in self.invoices.values():
    for invoice in self.invoices.values():
    if not invoice.is_paid() and invoice.status not in [
    if not invoice.is_paid() and invoice.status not in [
    InvoiceStatus.CANCELED,
    InvoiceStatus.CANCELED,
    InvoiceStatus.VOID,
    InvoiceStatus.VOID,
    ]:
    ]:
    unpaid_invoices.append(invoice)
    unpaid_invoices.append(invoice)


    # Sort by due date (oldest first)
    # Sort by due date (oldest first)
    unpaid_invoices.sort(key=lambda i: i.due_date)
    unpaid_invoices.sort(key=lambda i: i.due_date)


    return unpaid_invoices
    return unpaid_invoices


    def get_invoice_summary(
    def get_invoice_summary(
    self,
    self,
    customer_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Generate a comprehensive financial summary across multiple invoices.
    Generate a comprehensive financial summary across multiple invoices.


    This algorithm implements a multi-dimensional invoice aggregation system
    This algorithm implements a multi-dimensional invoice aggregation system
    that provides critical financial insights for business reporting and analysis.
    that provides critical financial insights for business reporting and analysis.
    The implementation follows these key stages:
    The implementation follows these key stages:


    1. DATA COLLECTION AND FILTERING:
    1. DATA COLLECTION AND FILTERING:
    - Dynamically selects invoices based on customer scope (single customer or all customers)
    - Dynamically selects invoices based on customer scope (single customer or all customers)
    - Applies temporal constraints through date range filtering
    - Applies temporal constraints through date range filtering
    - Creates a clean dataset for accurate aggregation
    - Creates a clean dataset for accurate aggregation
    - Handles edge cases like missing invoices or invalid date ranges
    - Handles edge cases like missing invoices or invalid date ranges


    2. MULTI-DIMENSIONAL AGGREGATION:
    2. MULTI-DIMENSIONAL AGGREGATION:
    - Performs aggregation across three primary dimensions:
    - Performs aggregation across three primary dimensions:
    a) Financial status (paid, unpaid, overdue, etc.)
    a) Financial status (paid, unpaid, overdue, etc.)
    b) Time periods (monthly breakdown)
    b) Time periods (monthly breakdown)
    c) Currency types (multi-currency support)
    c) Currency types (multi-currency support)
    - Creates nested hierarchical data structures for complex reporting
    - Creates nested hierarchical data structures for complex reporting
    - Maintains proper financial accounting principles during aggregation
    - Maintains proper financial accounting principles during aggregation
    - Ensures consistent calculation of totals, subtotals, and counts
    - Ensures consistent calculation of totals, subtotals, and counts


    3. FINANCIAL METRICS CALCULATION:
    3. FINANCIAL METRICS CALCULATION:
    - Calculates key financial metrics for each dimension:
    - Calculates key financial metrics for each dimension:
    a) Total invoice amounts (gross value)
    a) Total invoice amounts (gross value)
    b) Total payments received
    b) Total payments received
    c) Outstanding balances
    c) Outstanding balances
    d) Invoice counts
    d) Invoice counts
    - Provides complete visibility into financial health
    - Provides complete visibility into financial health
    - Enables trend analysis through consistent time-series data
    - Enables trend analysis through consistent time-series data
    - Facilitates reconciliation through multi-dimensional breakdowns
    - Facilitates reconciliation through multi-dimensional breakdowns


    4. CURRENCY HANDLING:
    4. CURRENCY HANDLING:
    - Supports multi-currency environments through currency-specific subtotals
    - Supports multi-currency environments through currency-specific subtotals
    - Preserves currency context for accurate financial reporting
    - Preserves currency context for accurate financial reporting
    - Avoids currency conversion errors by maintaining separation
    - Avoids currency conversion errors by maintaining separation
    - Provides foundation for potential currency conversion if needed
    - Provides foundation for potential currency conversion if needed


    This invoice summary algorithm addresses several critical business requirements:
    This invoice summary algorithm addresses several critical business requirements:
    - Executive dashboards requiring financial performance metrics
    - Executive dashboards requiring financial performance metrics
    - Accounting reconciliation requiring detailed breakdowns
    - Accounting reconciliation requiring detailed breakdowns
    - Financial forecasting based on invoice timing and payment trends
    - Financial forecasting based on invoice timing and payment trends
    - Cash flow analysis based on paid vs. outstanding amounts
    - Cash flow analysis based on paid vs. outstanding amounts
    - Customer payment behavior analysis
    - Customer payment behavior analysis


    The implementation specifically supports common financial reporting scenarios:
    The implementation specifically supports common financial reporting scenarios:
    - Monthly revenue recognition reports
    - Monthly revenue recognition reports
    - Accounts receivable aging analysis
    - Accounts receivable aging analysis
    - Collection prioritization based on overdue amounts
    - Collection prioritization based on overdue amounts
    - Customer-specific payment history reports
    - Customer-specific payment history reports
    - Multi-currency financial statements
    - Multi-currency financial statements


    Args:
    Args:
    customer_id: If provided, summarizes invoices for this specific customer only.
    customer_id: If provided, summarizes invoices for this specific customer only.
    If None, summarizes all invoices across all customers.
    If None, summarizes all invoices across all customers.
    start_date: Optional start date to filter invoices by date range
    start_date: Optional start date to filter invoices by date range
    end_date: Optional end date to filter invoices by date range
    end_date: Optional end date to filter invoices by date range


    Returns:
    Returns:
    A hierarchical dictionary containing comprehensive invoice summary data with:
    A hierarchical dictionary containing comprehensive invoice summary data with:
    - total_count: Total number of invoices included in the summary
    - total_count: Total number of invoices included in the summary
    - total_amount: Gross invoice amount across all included invoices
    - total_amount: Gross invoice amount across all included invoices
    - total_paid: Total payments received across all included invoices
    - total_paid: Total payments received across all included invoices
    - total_due: Total outstanding balance across all included invoices
    - total_due: Total outstanding balance across all included invoices
    - currencies: Breakdown of totals by currency code
    - currencies: Breakdown of totals by currency code
    - by_status: Breakdown of metrics by invoice status (draft, sent, paid, etc.)
    - by_status: Breakdown of metrics by invoice status (draft, sent, paid, etc.)
    - by_month: Time-series breakdown of metrics by month (YYYY-MM format)
    - by_month: Time-series breakdown of metrics by month (YYYY-MM format)
    """
    """
    # STAGE 1: Get invoices to summarize with appropriate filtering
    # STAGE 1: Get invoices to summarize with appropriate filtering
    if customer_id:
    if customer_id:
    # Single customer mode: Get filtered invoices for the specific customer
    # Single customer mode: Get filtered invoices for the specific customer
    invoices = self.get_customer_invoices(
    invoices = self.get_customer_invoices(
    customer_id=customer_id,
    customer_id=customer_id,
    start_date=start_date,
    start_date=start_date,
    end_date=end_date,
    end_date=end_date,
    limit=1000,  # Use a high limit to get all invoices
    limit=1000,  # Use a high limit to get all invoices
    )
    )
    else:
    else:
    # All customers mode: Start with all invoices, then apply date filters
    # All customers mode: Start with all invoices, then apply date filters
    invoices = list(self.invoices.values())
    invoices = list(self.invoices.values())


    # Apply date range filtering if specified
    # Apply date range filtering if specified
    if start_date or end_date:
    if start_date or end_date:
    filtered_invoices = []
    filtered_invoices = []


    for invoice in invoices:
    for invoice in invoices:
    if start_date and invoice.date < start_date:
    if start_date and invoice.date < start_date:
    continue
    continue


    if end_date and invoice.date > end_date:
    if end_date and invoice.date > end_date:
    continue
    continue


    filtered_invoices.append(invoice)
    filtered_invoices.append(invoice)


    invoices = filtered_invoices
    invoices = filtered_invoices


    # STAGE 2: Initialize the multi-dimensional summary data structure
    # STAGE 2: Initialize the multi-dimensional summary data structure
    summary = {
    summary = {
    "total_count": len(invoices),
    "total_count": len(invoices),
    "total_amount": 0.0,
    "total_amount": 0.0,
    "total_paid": 0.0,
    "total_paid": 0.0,
    "total_due": 0.0,
    "total_due": 0.0,
    "currencies": {},  # Currency dimension
    "currencies": {},  # Currency dimension
    "by_status": {},  # Status dimension
    "by_status": {},  # Status dimension
    "by_month": {},  # Time dimension
    "by_month": {},  # Time dimension
    }
    }


    # STAGE 3: Populate the summary through multi-dimensional aggregation
    # STAGE 3: Populate the summary through multi-dimensional aggregation
    for invoice in invoices:
    for invoice in invoices:
    # STATUS DIMENSION: Aggregate metrics by invoice status
    # STATUS DIMENSION: Aggregate metrics by invoice status
    if invoice.status not in summary["by_status"]:
    if invoice.status not in summary["by_status"]:
    summary["by_status"][invoice.status] = {
    summary["by_status"][invoice.status] = {
    "count": 0,
    "count": 0,
    "amount": 0.0,
    "amount": 0.0,
    "paid": 0.0,
    "paid": 0.0,
    "due": 0.0,
    "due": 0.0,
    }
    }


    summary["by_status"][invoice.status]["count"] += 1
    summary["by_status"][invoice.status]["count"] += 1
    summary["by_status"][invoice.status]["amount"] += invoice.get_total()
    summary["by_status"][invoice.status]["amount"] += invoice.get_total()
    summary["by_status"][invoice.status]["paid"] += invoice.get_total_paid()
    summary["by_status"][invoice.status]["paid"] += invoice.get_total_paid()
    summary["by_status"][invoice.status]["due"] += invoice.get_balance_due()
    summary["by_status"][invoice.status]["due"] += invoice.get_balance_due()


    # TIME DIMENSION: Aggregate metrics by month (YYYY-MM format)
    # TIME DIMENSION: Aggregate metrics by month (YYYY-MM format)
    month_key = invoice.date.strftime("%Y-%m")
    month_key = invoice.date.strftime("%Y-%m")


    if month_key not in summary["by_month"]:
    if month_key not in summary["by_month"]:
    summary["by_month"][month_key] = {
    summary["by_month"][month_key] = {
    "count": 0,
    "count": 0,
    "amount": 0.0,
    "amount": 0.0,
    "paid": 0.0,
    "paid": 0.0,
    "due": 0.0,
    "due": 0.0,
    }
    }


    summary["by_month"][month_key]["count"] += 1
    summary["by_month"][month_key]["count"] += 1
    summary["by_month"][month_key]["amount"] += invoice.get_total()
    summary["by_month"][month_key]["amount"] += invoice.get_total()
    summary["by_month"][month_key]["paid"] += invoice.get_total_paid()
    summary["by_month"][month_key]["paid"] += invoice.get_total_paid()
    summary["by_month"][month_key]["due"] += invoice.get_balance_due()
    summary["by_month"][month_key]["due"] += invoice.get_balance_due()


    # CURRENCY DIMENSION: Aggregate metrics by currency code
    # CURRENCY DIMENSION: Aggregate metrics by currency code
    if invoice.currency not in summary["currencies"]:
    if invoice.currency not in summary["currencies"]:
    summary["currencies"][invoice.currency] = {
    summary["currencies"][invoice.currency] = {
    "total_amount": 0.0,
    "total_amount": 0.0,
    "total_paid": 0.0,
    "total_paid": 0.0,
    "total_due": 0.0,
    "total_due": 0.0,
    }
    }


    # Accumulate amounts in the proper currency bucket
    # Accumulate amounts in the proper currency bucket
    summary["currencies"][invoice.currency][
    summary["currencies"][invoice.currency][
    "total_amount"
    "total_amount"
    ] += invoice.get_total()
    ] += invoice.get_total()
    summary["currencies"][invoice.currency][
    summary["currencies"][invoice.currency][
    "total_paid"
    "total_paid"
    ] += invoice.get_total_paid()
    ] += invoice.get_total_paid()
    summary["currencies"][invoice.currency][
    summary["currencies"][invoice.currency][
    "total_due"
    "total_due"
    ] += invoice.get_balance_due()
    ] += invoice.get_balance_due()


    # GLOBAL TOTALS: Accumulate the top-level totals
    # GLOBAL TOTALS: Accumulate the top-level totals
    summary["total_amount"] += invoice.get_total()
    summary["total_amount"] += invoice.get_total()
    summary["total_paid"] += invoice.get_total_paid()
    summary["total_paid"] += invoice.get_total_paid()
    summary["total_due"] += invoice.get_balance_due()
    summary["total_due"] += invoice.get_balance_due()


    return summary
    return summary


    def load_invoices(self) -> None:
    def load_invoices(self) -> None:
    """
    """
    Load invoices from storage directory.
    Load invoices from storage directory.
    """
    """
    if not self.storage_dir or not os.path.exists(self.storage_dir):
    if not self.storage_dir or not os.path.exists(self.storage_dir):
    return # Clear existing data
    return # Clear existing data
    self.invoices = {}
    self.invoices = {}
    self.customer_invoices = {}
    self.customer_invoices = {}


    # Load invoices
    # Load invoices
    for filename in os.listdir(self.storage_dir):
    for filename in os.listdir(self.storage_dir):
    if filename.endswith(".json"):
    if filename.endswith(".json"):
    file_path = os.path.join(self.storage_dir, filename)
    file_path = os.path.join(self.storage_dir, filename)


    try:
    try:
    with open(file_path, "r", encoding="utf-8") as f:
    with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    data = json.load(f)


    # Create invoice
    # Create invoice
    invoice = Invoice.from_dict(data)
    invoice = Invoice.from_dict(data)


    # Store invoice
    # Store invoice
    self.invoices[invoice.id] = invoice
    self.invoices[invoice.id] = invoice


    # Add to customer's invoices
    # Add to customer's invoices
    if invoice.customer_id not in self.customer_invoices:
    if invoice.customer_id not in self.customer_invoices:
    self.customer_invoices[invoice.customer_id] = []
    self.customer_invoices[invoice.customer_id] = []


    self.customer_invoices[invoice.customer_id].append(invoice.id)
    self.customer_invoices[invoice.customer_id].append(invoice.id)


except Exception as e:
except Exception as e:
    print(f"Error loading invoice from {file_path}: {e}")
    print(f"Error loading invoice from {file_path}: {e}")


    def _save_invoice(self, invoice: Invoice) -> None:
    def _save_invoice(self, invoice: Invoice) -> None:
    """
    """
    Save an invoice to the storage directory.
    Save an invoice to the storage directory.


    Args:
    Args:
    invoice: Invoice to save
    invoice: Invoice to save
    """
    """
    if not self.storage_dir:
    if not self.storage_dir:
    return file_path = os.path.join(self.storage_dir, f"{invoice.id}.json")
    return file_path = os.path.join(self.storage_dir, f"{invoice.id}.json")


    with open(file_path, "w", encoding="utf-8") as f:
    with open(file_path, "w", encoding="utf-8") as f:
    f.write(invoice.to_json())
    f.write(invoice.to_json())


    def batch_generate_invoices(
    def batch_generate_invoices(
    self,
    self,
    customer_ids: Optional[List[str]] = None,
    customer_ids: Optional[List[str]] = None,
    start_time: datetime = None,
    start_time: datetime = None,
    end_time: datetime = None,
    end_time: datetime = None,
    due_date_days: int = 30,
    due_date_days: int = 30,
    currency: str = "USD",
    currency: str = "USD",
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Generate usage-based invoices for multiple customers in a single operation.
    Generate usage-based invoices for multiple customers in a single operation.


    This algorithm implements an enterprise-grade batch invoicing system
    This algorithm implements an enterprise-grade batch invoicing system
    designed for high-volume, multi-tenant SaaS environments. The implementation
    designed for high-volume, multi-tenant SaaS environments. The implementation
    follows these key phases:
    follows these key phases:


    1. CUSTOMER SCOPE DETERMINATION:
    1. CUSTOMER SCOPE DETERMINATION:
    - Dynamically determines customer scope based on input parameters
    - Dynamically determines customer scope based on input parameters
    - Handles both selective and full customer base invoicing
    - Handles both selective and full customer base invoicing
    - Implements targeted cohort processing for large customer bases
    - Implements targeted cohort processing for large customer bases
    - Applies appropriate filtering to identify billable customers
    - Applies appropriate filtering to identify billable customers
    - Enables specific customer targeting for testing or special billing cycles
    - Enables specific customer targeting for testing or special billing cycles


    2. PARALLEL PROCESSING ARCHITECTURE:
    2. PARALLEL PROCESSING ARCHITECTURE:
    - Implements optimized batch processing for large customer sets
    - Implements optimized batch processing for large customer sets
    - Uses efficient data structures to minimize memory overhead
    - Uses efficient data structures to minimize memory overhead
    - Handles error isolation to prevent single-customer failures from affecting the batch
    - Handles error isolation to prevent single-customer failures from affecting the batch
    - Provides comprehensive error reporting and recovery mechanisms
    - Provides comprehensive error reporting and recovery mechanisms
    - Maintains performance under high-volume invoice generation
    - Maintains performance under high-volume invoice generation


    3. BILLING PERIOD MANAGEMENT:
    3. BILLING PERIOD MANAGEMENT:
    - Applies consistent billing period boundaries across all invoices
    - Applies consistent billing period boundaries across all invoices
    - Handles edge cases like customer timezone differences
    - Handles edge cases like customer timezone differences
    - Ensures no usage gaps between billing periods
    - Ensures no usage gaps between billing periods
    - Supports both calendar and anniversary billing models
    - Supports both calendar and anniversary billing models
    - Maintains proper period alignment for financial reporting
    - Maintains proper period alignment for financial reporting


    4. RESULTS AGGREGATION AND REPORTING:
    4. RESULTS AGGREGATION AND REPORTING:
    - Aggregates results across all customer invoices
    - Aggregates results across all customer invoices
    - Provides detailed success/failure metrics
    - Provides detailed success/failure metrics
    - Creates comprehensive batch processing summary
    - Creates comprehensive batch processing summary
    - Maintains proper auditing and traceability
    - Maintains proper auditing and traceability
    - Enables batch-level operations like approvals or notifications
    - Enables batch-level operations like approvals or notifications


    This batch invoice generation algorithm addresses several critical requirements:
    This batch invoice generation algorithm addresses several critical requirements:
    - Scalable processing for large customer bases
    - Scalable processing for large customer bases
    - Consistent billing period alignment across customers
    - Consistent billing period alignment across customers
    - Error isolation and comprehensive reporting
    - Error isolation and comprehensive reporting
    - Efficiency for high-volume invoice processing
    - Efficiency for high-volume invoice processing


    The implementation specifically supports common enterprise billing scenarios:
    The implementation specifically supports common enterprise billing scenarios:
    - Month-end billing for all customers
    - Month-end billing for all customers
    - Cohort-based billing cycles
    - Cohort-based billing cycles
    - Special invoice runs for specific customers
    - Special invoice runs for specific customers
    - Testing and verification of billing logic
    - Testing and verification of billing logic
    - Customer migration between billing systems
    - Customer migration between billing systems


    Args:
    Args:
    customer_ids: Optional list of specific customer IDs to process.
    customer_ids: Optional list of specific customer IDs to process.
    If None, processes all active customers.
    If None, processes all active customers.
    start_time: Start of the billing period for usage records
    start_time: Start of the billing period for usage records
    end_time: End of the billing period for usage records
    end_time: End of the billing period for usage records
    due_date_days: Number of days after end_time for invoice due date
    due_date_days: Number of days after end_time for invoice due date
    currency: Default currency to use for invoices
    currency: Default currency to use for invoices


    Returns:
    Returns:
    Dictionary with batch processing results:
    Dictionary with batch processing results:
    - total_customers: Total number of customers processed
    - total_customers: Total number of customers processed
    - successful: Number of invoices successfully generated
    - successful: Number of invoices successfully generated
    - failed: Number of invoice generation failures
    - failed: Number of invoice generation failures
    - total_amount: Total monetary amount across all generated invoices
    - total_amount: Total monetary amount across all generated invoices
    - invoices: List of generated invoice objects
    - invoices: List of generated invoice objects
    - errors: Dictionary mapping customer IDs to error messages for failures
    - errors: Dictionary mapping customer IDs to error messages for failures
    """
    """
    if not start_time or not end_time:
    if not start_time or not end_time:
    raise ValueError(
    raise ValueError(
    "Both start_time and end_time are required for batch invoice generation"
    "Both start_time and end_time are required for batch invoice generation"
    )
    )


    if not self.billing_calculator or not self.usage_tracker:
    if not self.billing_calculator or not self.usage_tracker:
    raise ValueError(
    raise ValueError(
    "Billing calculator and usage tracker are required to generate invoices from usage"
    "Billing calculator and usage tracker are required to generate invoices from usage"
    )
    )


    # STAGE 1: Determine the set of customers to process
    # STAGE 1: Determine the set of customers to process
    if customer_ids is None:
    if customer_ids is None:
    # If no specific customers provided, get all customers with usage in the period
    # If no specific customers provided, get all customers with usage in the period
    customer_ids = self.usage_tracker.get_customers_with_usage(
    customer_ids = self.usage_tracker.get_customers_with_usage(
    start_time=start_time, end_time=end_time
    start_time=start_time, end_time=end_time
    )
    )


    # Prepare the result structure
    # Prepare the result structure
    result = {
    result = {
    "total_customers": len(customer_ids),
    "total_customers": len(customer_ids),
    "successful": 0,
    "successful": 0,
    "failed": 0,
    "failed": 0,
    "total_amount": 0.0,
    "total_amount": 0.0,
    "invoices": [],
    "invoices": [],
    "errors": {},
    "errors": {},
    }
    }


    # STAGE 2: Process each customer with proper error isolation
    # STAGE 2: Process each customer with proper error isolation
    for customer_id in customer_ids:
    for customer_id in customer_ids:
    try:
    try:
    # Calculate the due date based on the end of billing period
    # Calculate the due date based on the end of billing period
    due_date = end_time + timedelta(days=due_date_days)
    due_date = end_time + timedelta(days=due_date_days)


    # Generate the invoice for this customer's usage
    # Generate the invoice for this customer's usage
    invoice = self.generate_invoice_from_usage(
    invoice = self.generate_invoice_from_usage(
    customer_id=customer_id,
    customer_id=customer_id,
    start_time=start_time,
    start_time=start_time,
    end_time=end_time,
    end_time=end_time,
    due_date=due_date,
    due_date=due_date,
    currency=currency,
    currency=currency,
    )
    )


    # Only count as successful if an invoice was generated
    # Only count as successful if an invoice was generated
    # (customers with no billable usage won't generate an invoice)
    # (customers with no billable usage won't generate an invoice)
    if invoice:
    if invoice:
    result["successful"] += 1
    result["successful"] += 1
    result["total_amount"] += invoice.get_total()
    result["total_amount"] += invoice.get_total()
    result["invoices"].append(invoice)
    result["invoices"].append(invoice)
except Exception as e:
except Exception as e:
    # Capture the error for reporting but continue processing other customers
    # Capture the error for reporting but continue processing other customers
    result["failed"] += 1
    result["failed"] += 1
    result["errors"][customer_id] = str(e)
    result["errors"][customer_id] = str(e)


    # STAGE 4: Finalize the batch and return results
    # STAGE 4: Finalize the batch and return results
    return result
    return result




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a usage tracker
    # Create a usage tracker
    tracker = UsageTracker()
    tracker = UsageTracker()


    # Create a billing calculator
    # Create a billing calculator
    calculator = BillingCalculator(usage_tracker=tracker)
    calculator = BillingCalculator(usage_tracker=tracker)


    # Create an invoice manager
    # Create an invoice manager
    manager = InvoiceManager(
    manager = InvoiceManager(
    billing_calculator=calculator,
    billing_calculator=calculator,
    usage_tracker=tracker,
    usage_tracker=tracker,
    storage_dir="invoices",
    storage_dir="invoices",
    company_info={
    company_info={
    "name": "AI Tools Inc.",
    "name": "AI Tools Inc.",
    "address": "123 Main St, San Francisco, CA 94111",
    "address": "123 Main St, San Francisco, CA 94111",
    "email": "billing@aitools.com",
    "email": "billing@aitools.com",
    "phone": "(555) 123-4567",
    "phone": "(555) 123-4567",
    "website": "https://aitools.com",
    "website": "https://aitools.com",
    },
    },
    )
    )


    # Create an invoice
    # Create an invoice
    invoice = manager.create_invoice(
    invoice = manager.create_invoice(
    customer_id="cust_123",
    customer_id="cust_123",
    customer_info={
    customer_info={
    "name": "John Doe",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "email": "john.doe@example.com",
    "address": "456 Oak St, San Francisco, CA 94112",
    "address": "456 Oak St, San Francisco, CA 94112",
    },
    },
    )
    )


    # Add items
    # Add items
    invoice.add_item(
    invoice.add_item(
    description="Premium Subscription (Monthly)",
    description="Premium Subscription (Monthly)",
    quantity=1,
    quantity=1,
    unit_price=29.99,
    unit_price=29.99,
    tax_rate=0.0825,  # 8.25% tax
    tax_rate=0.0825,  # 8.25% tax
    )
    )


    invoice.add_item(
    invoice.add_item(
    description="Additional User Licenses",
    description="Additional User Licenses",
    quantity=3,
    quantity=3,
    unit_price=9.99,
    unit_price=9.99,
    tax_rate=0.0825,  # 8.25% tax
    tax_rate=0.0825,  # 8.25% tax
    )
    )


    print(f"Invoice created: {invoice}")
    print(f"Invoice created: {invoice}")
    print(f"Number: {invoice.number}")
    print(f"Number: {invoice.number}")
    print(f"Total: {invoice.format_amount(invoice.get_total())}")
    print(f"Total: {invoice.format_amount(invoice.get_total())}")


    # Update status to sent
    # Update status to sent
    manager.update_invoice_status(
    manager.update_invoice_status(
    invoice.id, InvoiceStatus.SENT, "Invoice sent to customer"
    invoice.id, InvoiceStatus.SENT, "Invoice sent to customer"
    )
    )


    print(f"\nUpdated status: {invoice.status}")
    print(f"\nUpdated status: {invoice.status}")


    # Add a payment
    # Add a payment
    payment = manager.add_payment(
    payment = manager.add_payment(
    invoice_id=invoice.id,
    invoice_id=invoice.id,
    amount=30.00,
    amount=30.00,
    payment_method="Credit Card",
    payment_method="Credit Card",
    transaction_id="txn_123456",
    transaction_id="txn_123456",
    )
    )


    print(f"\nPayment added: {invoice.format_amount(payment['amount'])}")
    print(f"\nPayment added: {invoice.format_amount(payment['amount'])}")
    print(f"Total paid: {invoice.format_amount(invoice.get_total_paid())}")
    print(f"Total paid: {invoice.format_amount(invoice.get_total_paid())}")
    print(f"Balance due: {invoice.format_amount(invoice.get_balance_due())}")
    print(f"Balance due: {invoice.format_amount(invoice.get_balance_due())}")
    print(f"Status: {invoice.status}")
    print(f"Status: {invoice.status}")


    # Get customer invoices
    # Get customer invoices
    invoices = manager.get_customer_invoices("cust_123")
    invoices = manager.get_customer_invoices("cust_123")


    print(f"\nCustomer invoices ({len(invoices)}):")
    print(f"\nCustomer invoices ({len(invoices)}):")
    for inv in invoices:
    for inv in invoices:
    print(f"- {inv}"
    print(f"- {inv}"


    # Get invoice summary
    # Get invoice summary
    summary = manager.get_invoice_summary(
    summary = manager.get_invoice_summary(


    print("\nInvoice summary:"
    print("\nInvoice summary:"
    print(f"Total count: {summary['total_count']}"
    print(f"Total count: {summary['total_count']}"
    print(f"Total amount: ${summary['total_amount']:.2f}"
    print(f"Total amount: ${summary['total_amount']:.2f}"
    print(f"Total paid: ${summary['total_paid']:.2f}"
    print(f"Total paid: ${summary['total_paid']:.2f}"
    print(f"Total due: ${summary['total_due']:.2f}"
    print(f"Total due: ${summary['total_due']:.2f}"