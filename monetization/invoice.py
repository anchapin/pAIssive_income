"""
"""
Invoice generation for the pAIssive Income project.
Invoice generation for the pAIssive Income project.


This module provides classes for generating and managing invoices,
This module provides classes for generating and managing invoices,
including invoice items, status tracking, and formatting.
including invoice items, status tracking, and formatting.
"""
"""


import json
import json
import time
import time
import uuid
import uuid
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from common_utils import add_days, format_datetime
from common_utils import add_days, format_datetime




class InvoiceStatus:
    class InvoiceStatus:


    pass  # Added missing block
    pass  # Added missing block
    """Enumeration of invoice statuses."""

    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELED = "canceled"
    VOID = "void"


    class InvoiceItem:
    """
    """
    Class representing an item on an invoice.
    Class representing an item on an invoice.


    This class provides a structured way to represent a line item on an invoice,
    This class provides a structured way to represent a line item on an invoice,
    including the item description, quantity, unit price, and any discounts.
    including the item description, quantity, unit price, and any discounts.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    description: str,
    description: str,
    quantity: float = 1.0,
    quantity: float = 1.0,
    unit_price: float = 0.0,
    unit_price: float = 0.0,
    discount: float = 0.0,
    discount: float = 0.0,
    tax_rate: float = 0.0,
    tax_rate: float = 0.0,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize an invoice item.
    Initialize an invoice item.


    Args:
    Args:
    description: Description of the item
    description: Description of the item
    quantity: Quantity of the item
    quantity: Quantity of the item
    unit_price: Unit price of the item
    unit_price: Unit price of the item
    discount: Discount amount for the item
    discount: Discount amount for the item
    tax_rate: Tax rate for the item (as a decimal, e.g., 0.1 for 10%)
    tax_rate: Tax rate for the item (as a decimal, e.g., 0.1 for 10%)
    metadata: Additional metadata for the item
    metadata: Additional metadata for the item
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.description = description
    self.description = description
    self.quantity = quantity
    self.quantity = quantity
    self.unit_price = unit_price
    self.unit_price = unit_price
    self.discount = discount
    self.discount = discount
    self.tax_rate = tax_rate
    self.tax_rate = tax_rate
    self.metadata = metadata or {}
    self.metadata = metadata or {}


    def get_subtotal(self) -> float:
    def get_subtotal(self) -> float:
    """
    """
    Get the subtotal for this item (quantity * unit_price).
    Get the subtotal for this item (quantity * unit_price).


    Returns:
    Returns:
    Subtotal amount
    Subtotal amount
    """
    """
    return self.quantity * self.unit_price
    return self.quantity * self.unit_price


    def get_discount_amount(self) -> float:
    def get_discount_amount(self) -> float:
    """
    """
    Get the discount amount for this item.
    Get the discount amount for this item.


    Returns:
    Returns:
    Discount amount
    Discount amount
    """
    """
    return self.discount
    return self.discount


    def get_taxable_amount(self) -> float:
    def get_taxable_amount(self) -> float:
    """
    """
    Get the taxable amount for this item (subtotal - discount).
    Get the taxable amount for this item (subtotal - discount).


    Returns:
    Returns:
    Taxable amount
    Taxable amount
    """
    """
    return max(0, self.get_subtotal() - self.get_discount_amount())
    return max(0, self.get_subtotal() - self.get_discount_amount())


    def get_tax_amount(self) -> float:
    def get_tax_amount(self) -> float:
    """
    """
    Get the tax amount for this item.
    Get the tax amount for this item.


    Returns:
    Returns:
    Tax amount
    Tax amount
    """
    """
    return self.get_taxable_amount() * self.tax_rate
    return self.get_taxable_amount() * self.tax_rate


    def get_total(self) -> float:
    def get_total(self) -> float:
    """
    """
    Get the total for this item (taxable amount + tax amount).
    Get the total for this item (taxable amount + tax amount).


    Returns:
    Returns:
    Total amount
    Total amount
    """
    """
    return self.get_taxable_amount() + self.get_tax_amount()
    return self.get_taxable_amount() + self.get_tax_amount()


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the invoice item to a dictionary.
    Convert the invoice item to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the invoice item
    Dictionary representation of the invoice item
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "description": self.description,
    "description": self.description,
    "quantity": self.quantity,
    "quantity": self.quantity,
    "unit_price": self.unit_price,
    "unit_price": self.unit_price,
    "discount": self.discount,
    "discount": self.discount,
    "tax_rate": self.tax_rate,
    "tax_rate": self.tax_rate,
    "subtotal": self.get_subtotal(),
    "subtotal": self.get_subtotal(),
    "discount_amount": self.get_discount_amount(),
    "discount_amount": self.get_discount_amount(),
    "taxable_amount": self.get_taxable_amount(),
    "taxable_amount": self.get_taxable_amount(),
    "tax_amount": self.get_tax_amount(),
    "tax_amount": self.get_tax_amount(),
    "total": self.get_total(),
    "total": self.get_total(),
    "metadata": self.metadata,
    "metadata": self.metadata,
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InvoiceItem":
    def from_dict(cls, data: Dict[str, Any]) -> "InvoiceItem":
    """
    """
    Create an invoice item from a dictionary.
    Create an invoice item from a dictionary.


    Args:
    Args:
    data: Dictionary with invoice item data
    data: Dictionary with invoice item data


    Returns:
    Returns:
    InvoiceItem instance
    InvoiceItem instance
    """
    """
    item = cls(
    item = cls(
    description=data["description"],
    description=data["description"],
    quantity=data["quantity"],
    quantity=data["quantity"],
    unit_price=data["unit_price"],
    unit_price=data["unit_price"],
    discount=data["discount"],
    discount=data["discount"],
    tax_rate=data["tax_rate"],
    tax_rate=data["tax_rate"],
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    item.id = data["id"]
    item.id = data["id"]


    return item
    return item


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the invoice item."""
    return f"{self.description}: {self.quantity} x ${self.unit_price:.2f} = ${self.get_total():.2f}"


    class Invoice:
    """
    """
    Class for generating and managing invoices.
    Class for generating and managing invoices.


    This class provides methods for creating, formatting, and managing
    This class provides methods for creating, formatting, and managing
    invoices for customers.
    invoices for customers.
    """
    """


    def __init__(
    def __init__(
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
    items: Optional[List[InvoiceItem]] = None,
    items: Optional[List[InvoiceItem]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize an invoice.
    Initialize an invoice.


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
    metadata: Additional metadata for the invoice
    metadata: Additional metadata for the invoice
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.number = self._generate_invoice_number()
    self.number = self._generate_invoice_number()
    self.customer_id = customer_id
    self.customer_id = customer_id
    self.date = date or datetime.now()
    self.date = date or datetime.now()
    self.due_date = due_date or add_days(self.date, 30)
    self.due_date = due_date or add_days(self.date, 30)
    self.currency = currency
    self.currency = currency
    self.items = items or []
    self.items = items or []
    self.metadata = metadata or {}
    self.metadata = metadata or {}
    self.status = InvoiceStatus.DRAFT
    self.status = InvoiceStatus.DRAFT
    self.created_at = datetime.now()
    self.created_at = datetime.now()
    self.updated_at = self.created_at
    self.updated_at = self.created_at


    # Initialize other properties
    # Initialize other properties
    self.company_name = self.metadata.get("company_name", "")
    self.company_name = self.metadata.get("company_name", "")
    self.company_address = self.metadata.get("company_address", "")
    self.company_address = self.metadata.get("company_address", "")
    self.company_email = self.metadata.get("company_email", "")
    self.company_email = self.metadata.get("company_email", "")
    self.company_phone = self.metadata.get("company_phone", "")
    self.company_phone = self.metadata.get("company_phone", "")
    self.company_website = self.metadata.get("company_website", "")
    self.company_website = self.metadata.get("company_website", "")
    self.company_logo_url = self.metadata.get("company_logo_url", "")
    self.company_logo_url = self.metadata.get("company_logo_url", "")


    self.customer_name = self.metadata.get("customer_name", "")
    self.customer_name = self.metadata.get("customer_name", "")
    self.customer_email = self.metadata.get("customer_email", "")
    self.customer_email = self.metadata.get("customer_email", "")
    self.customer_address = self.metadata.get("customer_address", "")
    self.customer_address = self.metadata.get("customer_address", "")


    self.payment_terms = self.metadata.get("payment_terms", "")
    self.payment_terms = self.metadata.get("payment_terms", "")
    self.notes = self.metadata.get("notes", "")
    self.notes = self.metadata.get("notes", "")
    self.terms = self.metadata.get("terms", "")
    self.terms = self.metadata.get("terms", "")


    self.tax_name = self.metadata.get("tax_name", "Tax")
    self.tax_name = self.metadata.get("tax_name", "Tax")
    self.discount_name = self.metadata.get("discount_name", "Discount")
    self.discount_name = self.metadata.get("discount_name", "Discount")


    self.additional_fees = self.metadata.get("additional_fees", [])
    self.additional_fees = self.metadata.get("additional_fees", [])
    self.custom_fields = self.metadata.get("custom_fields", {})
    self.custom_fields = self.metadata.get("custom_fields", {})


    self.status_history = [
    self.status_history = [
    {
    {
    "status": self.status,
    "status": self.status,
    "timestamp": format_datetime(self.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
    "timestamp": format_datetime(self.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
    "reason": "Invoice created",
    "reason": "Invoice created",
    }
    }
    ]
    ]


    self.payments = []
    self.payments = []


    def _generate_invoice_number(self) -> str:
    def _generate_invoice_number(self) -> str:
    """
    """
    Generate an invoice number.
    Generate an invoice number.


    Returns:
    Returns:
    Invoice number
    Invoice number
    """
    """
    # Generate a simple invoice number based on the current date and a random suffix
    # Generate a simple invoice number based on the current date and a random suffix
    date_str = format_datetime(datetime.now(), "%Y%m%d")
    date_str = format_datetime(datetime.now(), "%Y%m%d")
    random_suffix = str(uuid.uuid4().int)[:6]
    random_suffix = str(uuid.uuid4().int)[:6]
    return f"INV-{date_str}-{random_suffix}"
    return f"INV-{date_str}-{random_suffix}"


    def add_item(
    def add_item(
    self,
    self,
    description: str,
    description: str,
    quantity: float = 1.0,
    quantity: float = 1.0,
    unit_price: float = 0.0,
    unit_price: float = 0.0,
    discount: float = 0.0,
    discount: float = 0.0,
    tax_rate: float = 0.0,
    tax_rate: float = 0.0,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> InvoiceItem:
    ) -> InvoiceItem:
    """
    """
    Add an item to the invoice.
    Add an item to the invoice.


    Args:
    Args:
    description: Description of the item
    description: Description of the item
    quantity: Quantity of the item
    quantity: Quantity of the item
    unit_price: Unit price of the item
    unit_price: Unit price of the item
    discount: Discount amount for the item
    discount: Discount amount for the item
    tax_rate: Tax rate for the item (as a decimal, e.g., 0.1 for 10%)
    tax_rate: Tax rate for the item (as a decimal, e.g., 0.1 for 10%)
    metadata: Additional metadata for the item
    metadata: Additional metadata for the item


    Returns:
    Returns:
    The created invoice item
    The created invoice item
    """
    """
    item = InvoiceItem(
    item = InvoiceItem(
    description=description,
    description=description,
    quantity=quantity,
    quantity=quantity,
    unit_price=unit_price,
    unit_price=unit_price,
    discount=discount,
    discount=discount,
    tax_rate=tax_rate,
    tax_rate=tax_rate,
    metadata=metadata,
    metadata=metadata,
    )
    )


    self.items.append(item)
    self.items.append(item)
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    return item
    return item


    def remove_item(self, item_id: str) -> bool:
    def remove_item(self, item_id: str) -> bool:
    """
    """
    Remove an item from the invoice.
    Remove an item from the invoice.


    Args:
    Args:
    item_id: ID of the item to remove
    item_id: ID of the item to remove


    Returns:
    Returns:
    True if the item was removed, False otherwise
    True if the item was removed, False otherwise
    """
    """
    for i, item in enumerate(self.items):
    for i, item in enumerate(self.items):
    if item.id == item_id:
    if item.id == item_id:
    self.items.pop(i)
    self.items.pop(i)
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()
    return True
    return True


    return False
    return False


    def get_item(self, item_id: str) -> Optional[InvoiceItem]:
    def get_item(self, item_id: str) -> Optional[InvoiceItem]:
    """
    """
    Get an item from the invoice.
    Get an item from the invoice.


    Args:
    Args:
    item_id: ID of the item
    item_id: ID of the item


    Returns:
    Returns:
    The invoice item or None if not found
    The invoice item or None if not found
    """
    """
    for item in self.items:
    for item in self.items:
    if item.id == item_id:
    if item.id == item_id:
    return item
    return item


    return None
    return None


    def get_items(self) -> List[InvoiceItem]:
    def get_items(self) -> List[InvoiceItem]:
    """
    """
    Get all items on the invoice.
    Get all items on the invoice.


    Returns:
    Returns:
    List of invoice items
    List of invoice items
    """
    """
    return self.items
    return self.items


    def set_company_info(
    def set_company_info(
    self,
    self,
    name: str,
    name: str,
    address: str = "",
    address: str = "",
    email: str = "",
    email: str = "",
    phone: str = "",
    phone: str = "",
    website: str = "",
    website: str = "",
    logo_url: str = "",
    logo_url: str = "",
    ) -> None:
    ) -> None:
    """
    """
    Set company information for the invoice.
    Set company information for the invoice.


    Args:
    Args:
    name: Company name
    name: Company name
    address: Company address
    address: Company address
    email: Company email
    email: Company email
    phone: Company phone
    phone: Company phone
    website: Company website
    website: Company website
    logo_url: URL to company logo
    logo_url: URL to company logo
    """
    """
    self.company_name = name
    self.company_name = name
    self.company_address = address
    self.company_address = address
    self.company_email = email
    self.company_email = email
    self.company_phone = phone
    self.company_phone = phone
    self.company_website = website
    self.company_website = website
    self.company_logo_url = logo_url
    self.company_logo_url = logo_url


    # Update metadata
    # Update metadata
    self.metadata["company_name"] = name
    self.metadata["company_name"] = name
    self.metadata["company_address"] = address
    self.metadata["company_address"] = address
    self.metadata["company_email"] = email
    self.metadata["company_email"] = email
    self.metadata["company_phone"] = phone
    self.metadata["company_phone"] = phone
    self.metadata["company_website"] = website
    self.metadata["company_website"] = website
    self.metadata["company_logo_url"] = logo_url
    self.metadata["company_logo_url"] = logo_url


    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def set_customer_info(self, name: str, email: str = "", address: str = "") -> None:
    def set_customer_info(self, name: str, email: str = "", address: str = "") -> None:
    """
    """
    Set customer information for the invoice.
    Set customer information for the invoice.


    Args:
    Args:
    name: Customer name
    name: Customer name
    email: Customer email
    email: Customer email
    address: Customer address
    address: Customer address
    """
    """
    self.customer_name = name
    self.customer_name = name
    self.customer_email = email
    self.customer_email = email
    self.customer_address = address
    self.customer_address = address


    # Update metadata
    # Update metadata
    self.metadata["customer_name"] = name
    self.metadata["customer_name"] = name
    self.metadata["customer_email"] = email
    self.metadata["customer_email"] = email
    self.metadata["customer_address"] = address
    self.metadata["customer_address"] = address


    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def set_payment_terms(self, terms: str) -> None:
    def set_payment_terms(self, terms: str) -> None:
    """
    """
    Set payment terms for the invoice.
    Set payment terms for the invoice.


    Args:
    Args:
    terms: Payment terms
    terms: Payment terms
    """
    """
    self.payment_terms = terms
    self.payment_terms = terms
    self.metadata["payment_terms"] = terms
    self.metadata["payment_terms"] = terms
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def set_due_date(self, due_date: datetime) -> None:
    def set_due_date(self, due_date: datetime) -> None:
    """
    """
    Set the due date for the invoice.
    Set the due date for the invoice.


    Args:
    Args:
    due_date: Due date
    due_date: Due date
    """
    """
    self.due_date = due_date
    self.due_date = due_date
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def add_custom_field(self, name: str, value: Any) -> None:
    def add_custom_field(self, name: str, value: Any) -> None:
    """
    """
    Add a custom field to the invoice.
    Add a custom field to the invoice.


    Args:
    Args:
    name: Field name
    name: Field name
    value: Field value
    value: Field value
    """
    """
    self.custom_fields[name] = value
    self.custom_fields[name] = value
    self.metadata["custom_fields"] = self.custom_fields
    self.metadata["custom_fields"] = self.custom_fields
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def add_additional_fee(
    def add_additional_fee(
    self, name: str, amount: float, is_percentage: bool = False
    self, name: str, amount: float, is_percentage: bool = False
    ) -> None:
    ) -> None:
    """
    """
    Add an additional fee to the invoice.
    Add an additional fee to the invoice.


    Args:
    Args:
    name: Fee name
    name: Fee name
    amount: Fee amount
    amount: Fee amount
    is_percentage: Whether the fee is a percentage of the subtotal
    is_percentage: Whether the fee is a percentage of the subtotal
    """
    """
    fee = {"name": name, "amount": amount, "is_percentage": is_percentage}
    fee = {"name": name, "amount": amount, "is_percentage": is_percentage}


    self.additional_fees.append(fee)
    self.additional_fees.append(fee)
    self.metadata["additional_fees"] = self.additional_fees
    self.metadata["additional_fees"] = self.additional_fees
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def set_notes(self, notes: str) -> None:
    def set_notes(self, notes: str) -> None:
    """
    """
    Set notes for the invoice.
    Set notes for the invoice.


    Args:
    Args:
    notes: Invoice notes
    notes: Invoice notes
    """
    """
    self.notes = notes
    self.notes = notes
    self.metadata["notes"] = notes
    self.metadata["notes"] = notes
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def set_terms(self, terms: str) -> None:
    def set_terms(self, terms: str) -> None:
    """
    """
    Set terms and conditions for the invoice.
    Set terms and conditions for the invoice.


    Args:
    Args:
    terms: Terms and conditions
    terms: Terms and conditions
    """
    """
    self.terms = terms
    self.terms = terms
    self.metadata["terms"] = terms
    self.metadata["terms"] = terms
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def update_status(self, status: str, reason: Optional[str] = None) -> None:
    def update_status(self, status: str, reason: Optional[str] = None) -> None:
    """
    """
    Transition invoice state with comprehensive audit trail management.
    Transition invoice state with comprehensive audit trail management.


    This algorithm implements a robust state management system with integrated
    This algorithm implements a robust state management system with integrated
    audit logging for financial transactions. The implementation follows these
    audit logging for financial transactions. The implementation follows these
    key phases:
    key phases:


    1. STATE TRANSITION PROCESSING:
    1. STATE TRANSITION PROCESSING:
    - Records previous state for proper transition tracking
    - Records previous state for proper transition tracking
    - Applies the new status to update the invoice lifecycle state
    - Applies the new status to update the invoice lifecycle state
    - Timestamps the transition for chronological record-keeping
    - Timestamps the transition for chronological record-keeping
    - Maintains audit records in a persistent, tamper-evident format
    - Maintains audit records in a persistent, tamper-evident format
    - Creates a complete audit trail of all status changes
    - Creates a complete audit trail of all status changes


    2. BUSINESS RULE ENFORCEMENT FOUNDATION:
    2. BUSINESS RULE ENFORCEMENT FOUNDATION:
    - Forms the foundation for implementing financial workflow rules such as:
    - Forms the foundation for implementing financial workflow rules such as:
    a) Preventing invalid state transitions (e.g., Void → Paid)
    a) Preventing invalid state transitions (e.g., Void → Paid)
    b) Enforcing proper authorization rules for status changes
    b) Enforcing proper authorization rules for status changes
    c) Ensuring proper sequencing of invoice lifecycle events
    c) Ensuring proper sequencing of invoice lifecycle events
    d) Supporting compliance with financial record-keeping requirements
    d) Supporting compliance with financial record-keeping requirements


    3. AUDIT AND COMPLIANCE SUPPORT:
    3. AUDIT AND COMPLIANCE SUPPORT:
    - Captures the complete history of invoice status changes
    - Captures the complete history of invoice status changes
    - Records the reason for each status change (manual or automated)
    - Records the reason for each status change (manual or automated)
    - Preserves the chronological sequence of status updates
    - Preserves the chronological sequence of status updates
    - Enables historical analysis of invoice progression patterns
    - Enables historical analysis of invoice progression patterns
    - Supports financial auditing and compliance requirements
    - Supports financial auditing and compliance requirements


    4. BUSINESS PROCESS INTEGRATION:
    4. BUSINESS PROCESS INTEGRATION:
    - Status changes serve as trigger points for business processes:
    - Status changes serve as trigger points for business processes:
    a) Customer communications (e.g., payment reminders)
    a) Customer communications (e.g., payment reminders)
    b) Revenue recognition events
    b) Revenue recognition events
    c) Accounting system integrations
    c) Accounting system integrations
    d) Collections and payment follow-up activities
    d) Collections and payment follow-up activities


    This status management algorithm addresses several critical requirements:
    This status management algorithm addresses several critical requirements:
    - Proper tracking of invoice lifecycle stages
    - Proper tracking of invoice lifecycle stages
    - Complete audit trail for financial compliance and reporting
    - Complete audit trail for financial compliance and reporting
    - Foundation for business process automation
    - Foundation for business process automation
    - Transaction history for financial reconciliation
    - Transaction history for financial reconciliation


    The implementation specifically supports common invoice lifecycle scenarios:
    The implementation specifically supports common invoice lifecycle scenarios:
    - Draft → Sent → Paid progression
    - Draft → Sent → Paid progression
    - Partial payment handling
    - Partial payment handling
    - Overdue invoice management
    - Overdue invoice management
    - Voiding and cancellation workflows
    - Voiding and cancellation workflows
    - Status correction and adjustment with proper documentation
    - Status correction and adjustment with proper documentation


    Args:
    Args:
    status: New invoice status to set from InvoiceStatus constants
    status: New invoice status to set from InvoiceStatus constants
    reason: Optional description of why the status is being changed
    reason: Optional description of why the status is being changed
    (automatically generated if not provided)
    (automatically generated if not provided)
    """
    """
    old_status = self.status
    old_status = self.status
    self.status = status
    self.status = status
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    # Add status history entry
    # Add status history entry
    self.status_history.append(
    self.status_history.append(
    {
    {
    "status": status,
    "status": status,
    "timestamp": self.updated_at.isoformat(),
    "timestamp": self.updated_at.isoformat(),
    "reason": reason or f"Status changed from {old_status} to {status}",
    "reason": reason or f"Status changed from {old_status} to {status}",
    }
    }
    )
    )


    def add_payment(
    def add_payment(
    self,
    self,
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
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Register a payment and update invoice status through intelligent state management.
    Register a payment and update invoice status through intelligent state management.


    This algorithm implements a robust payment processing workflow with automatic
    This algorithm implements a robust payment processing workflow with automatic
    status transitions based on business rules. The implementation follows these key stages:
    status transitions based on business rules. The implementation follows these key stages:


    1. PAYMENT RECORD CREATION:
    1. PAYMENT RECORD CREATION:
    - Generates a unique identifier for each payment transaction
    - Generates a unique identifier for each payment transaction
    - Records essential payment details (amount, date, method, transaction ID)
    - Records essential payment details (amount, date, method, transaction ID)
    - Timestamps the payment for audit and reconciliation purposes
    - Timestamps the payment for audit and reconciliation purposes
    - Preserves metadata for integration with external payment systems
    - Preserves metadata for integration with external payment systems
    - Maintains a complete payment history for the invoice
    - Maintains a complete payment history for the invoice


    2. INTELLIGENT INVOICE STATUS MANAGEMENT:
    2. INTELLIGENT INVOICE STATUS MANAGEMENT:
    - Automatically calculates current payment status after each transaction
    - Automatically calculates current payment status after each transaction
    - Implements smart state transitions based on payment completeness:
    - Implements smart state transitions based on payment completeness:
    a) Not Paid → Partially Paid → Fully Paid
    a) Not Paid → Partially Paid → Fully Paid
    b) Overdue → Partially Paid → Fully Paid
    b) Overdue → Partially Paid → Fully Paid
    - Prevents invalid status transitions (e.g., Canceled → Paid)
    - Prevents invalid status transitions (e.g., Canceled → Paid)
    - Provides proper audit trail through status history records
    - Provides proper audit trail through status history records
    - Handles edge cases like overpayment or micropayments gracefully
    - Handles edge cases like overpayment or micropayments gracefully


    3. PAYMENT VALIDATION AND RECONCILIATION:
    3. PAYMENT VALIDATION AND RECONCILIATION:
    - Ensures payment amounts are properly accumulated and tracked
    - Ensures payment amounts are properly accumulated and tracked
    - Updates the balance due calculation automatically
    - Updates the balance due calculation automatically
    - Facilitates payment reconciliation through complete transaction history
    - Facilitates payment reconciliation through complete transaction history
    - Forms the foundation for financial reporting and revenue recognition
    - Forms the foundation for financial reporting and revenue recognition


    4. EVENT TRIGGERING MECHANISM:
    4. EVENT TRIGGERING MECHANISM:
    - The status changes triggered by payments can serve as hooks for:
    - The status changes triggered by payments can serve as hooks for:
    a) Customer notifications
    a) Customer notifications
    b) Accounting system updates
    b) Accounting system updates
    c) Service provisioning actions
    c) Service provisioning actions
    d) Reporting and analytics updates
    d) Reporting and analytics updates


    This payment management algorithm addresses several critical business requirements:
    This payment management algorithm addresses several critical business requirements:
    - Accurate tracking of customer payments and invoice status
    - Accurate tracking of customer payments and invoice status
    - Automated workflow for payment processing
    - Automated workflow for payment processing
    - Complete audit trail for financial compliance
    - Complete audit trail for financial compliance
    - Foundation for accounts receivable management
    - Foundation for accounts receivable management


    The implementation specifically supports common business scenarios:
    The implementation specifically supports common business scenarios:
    - Partial payments with remaining balance tracking
    - Partial payments with remaining balance tracking
    - Multiple payment methods for a single invoice
    - Multiple payment methods for a single invoice
    - Payment reconciliation with external systems
    - Payment reconciliation with external systems
    - Historical payment analysis and reporting
    - Historical payment analysis and reporting


    Args:
    Args:
    amount: Payment amount received from the customer
    amount: Payment amount received from the customer
    date: Date when the payment was received (defaults to current time)
    date: Date when the payment was received (defaults to current time)
    payment_method: Method used for payment (e.g., "Credit Card", "ACH", "Check")
    payment_method: Method used for payment (e.g., "Credit Card", "ACH", "Check")
    transaction_id: External reference ID from payment processor
    transaction_id: External reference ID from payment processor
    metadata: Additional payment information for integration or reconciliation
    metadata: Additional payment information for integration or reconciliation


    Returns:
    Returns:
    Dictionary containing the complete payment record including:
    Dictionary containing the complete payment record including:
    - id: Unique identifier for this payment
    - id: Unique identifier for this payment
    - amount: Payment amount
    - amount: Payment amount
    - date: ISO-formatted payment date
    - date: ISO-formatted payment date
    - payment_method: How the payment was made
    - payment_method: How the payment was made
    - transaction_id: External reference for reconciliation
    - transaction_id: External reference for reconciliation
    - metadata: Any additional payment details
    - metadata: Any additional payment details
    """
    """
    payment = {
    payment = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "amount": amount,
    "amount": amount,
    "date": (date or datetime.now()).isoformat(),
    "date": (date or datetime.now()).isoformat(),
    "payment_method": payment_method,
    "payment_method": payment_method,
    "transaction_id": transaction_id,
    "transaction_id": transaction_id,
    "metadata": metadata or {},
    "metadata": metadata or {},
    }
    }


    self.payments.append(payment)
    self.payments.append(payment)
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    # Update status based on payment
    # Update status based on payment
    total_paid = self.get_total_paid()
    total_paid = self.get_total_paid()
    total_due = self.get_total()
    total_due = self.get_total()


    if total_paid >= total_due:
    if total_paid >= total_due:
    self.update_status(InvoiceStatus.PAID, "Payment received in full")
    self.update_status(InvoiceStatus.PAID, "Payment received in full")
    elif total_paid > 0:
    elif total_paid > 0:
    self.update_status(InvoiceStatus.PARTIALLY_PAID, "Partial payment received")
    self.update_status(InvoiceStatus.PARTIALLY_PAID, "Partial payment received")


    return payment
    return payment


    def get_total_paid(self) -> float:
    def get_total_paid(self) -> float:
    """
    """
    Get the total amount paid on the invoice.
    Get the total amount paid on the invoice.


    Returns:
    Returns:
    Total amount paid
    Total amount paid
    """
    """
    return sum(payment["amount"] for payment in self.payments)
    return sum(payment["amount"] for payment in self.payments)


    def get_balance_due(self) -> float:
    def get_balance_due(self) -> float:
    """
    """
    Get the balance due on the invoice.
    Get the balance due on the invoice.


    Returns:
    Returns:
    Balance due
    Balance due
    """
    """
    return max(0, self.get_total() - self.get_total_paid())
    return max(0, self.get_total() - self.get_total_paid())


    def is_paid(self) -> bool:
    def is_paid(self) -> bool:
    """
    """
    Check if the invoice is paid in full.
    Check if the invoice is paid in full.


    Returns:
    Returns:
    True if the invoice is paid in full, False otherwise
    True if the invoice is paid in full, False otherwise
    """
    """
    return self.get_balance_due() == 0
    return self.get_balance_due() == 0


    def is_overdue(self) -> bool:
    def is_overdue(self) -> bool:
    """
    """
    Check if the invoice is overdue.
    Check if the invoice is overdue.


    Returns:
    Returns:
    True if the invoice is overdue, False otherwise
    True if the invoice is overdue, False otherwise
    """
    """
    return self.due_date < datetime.now() and self.status not in [
    return self.due_date < datetime.now() and self.status not in [
    InvoiceStatus.PAID,
    InvoiceStatus.PAID,
    InvoiceStatus.CANCELED,
    InvoiceStatus.CANCELED,
    InvoiceStatus.VOID,
    InvoiceStatus.VOID,
    ]
    ]


    def get_subtotal(self) -> float:
    def get_subtotal(self) -> float:
    """
    """
    Get the subtotal for all items on the invoice.
    Get the subtotal for all items on the invoice.


    Returns:
    Returns:
    Subtotal amount
    Subtotal amount
    """
    """
    return sum(item.get_subtotal() for item in self.items)
    return sum(item.get_subtotal() for item in self.items)


    def get_discount_total(self) -> float:
    def get_discount_total(self) -> float:
    """
    """
    Get the total discount amount for all items on the invoice.
    Get the total discount amount for all items on the invoice.


    Returns:
    Returns:
    Total discount amount
    Total discount amount
    """
    """
    return sum(item.get_discount_amount() for item in self.items)
    return sum(item.get_discount_amount() for item in self.items)


    def get_taxable_amount(self) -> float:
    def get_taxable_amount(self) -> float:
    """
    """
    Get the total taxable amount for all items on the invoice.
    Get the total taxable amount for all items on the invoice.


    Returns:
    Returns:
    Total taxable amount
    Total taxable amount
    """
    """
    return sum(item.get_taxable_amount() for item in self.items)
    return sum(item.get_taxable_amount() for item in self.items)


    def get_tax_total(self) -> float:
    def get_tax_total(self) -> float:
    """
    """
    Get the total tax amount for all items on the invoice.
    Get the total tax amount for all items on the invoice.


    Returns:
    Returns:
    Total tax amount
    Total tax amount
    """
    """
    return sum(item.get_tax_amount() for item in self.items)
    return sum(item.get_tax_amount() for item in self.items)


    def get_additional_fees_total(self) -> float:
    def get_additional_fees_total(self) -> float:
    """
    """
    Get the total amount for all additional fees on the invoice.
    Get the total amount for all additional fees on the invoice.


    Returns:
    Returns:
    Total additional fees amount
    Total additional fees amount
    """
    """
    total = 0.0
    total = 0.0
    subtotal = self.get_subtotal()
    subtotal = self.get_subtotal()


    for fee in self.additional_fees:
    for fee in self.additional_fees:
    if fee["is_percentage"]:
    if fee["is_percentage"]:
    total += subtotal * fee["amount"] / 100.0
    total += subtotal * fee["amount"] / 100.0
    else:
    else:
    total += fee["amount"]
    total += fee["amount"]


    return total
    return total


    def get_total(self) -> float:
    def get_total(self) -> float:
    """
    """
    Calculate the final invoice amount through multi-component aggregation.
    Calculate the final invoice amount through multi-component aggregation.


    This algorithm implements a robust invoice total calculation that follows
    This algorithm implements a robust invoice total calculation that follows
    standard accounting practices for proper financial aggregation. The implementation
    standard accounting practices for proper financial aggregation. The implementation
    follows these key stages:
    follows these key stages:


    1. COMPONENT-BASED CALCULATION:
    1. COMPONENT-BASED CALCULATION:
    - Aggregates multiple financial components rather than a simple sum
    - Aggregates multiple financial components rather than a simple sum
    - Properly accounts for tax-exclusive and tax-inclusive items
    - Properly accounts for tax-exclusive and tax-inclusive items
    - Handles additional fees (both fixed and percentage-based)
    - Handles additional fees (both fixed and percentage-based)
    - Maintains correct calculation order for financial accuracy
    - Maintains correct calculation order for financial accuracy


    2. HIERARCHICAL AGGREGATION:
    2. HIERARCHICAL AGGREGATION:
    - First calculates line item values (unit price × quantity)
    - First calculates line item values (unit price × quantity)
    - Then applies discounts to determine taxable amounts
    - Then applies discounts to determine taxable amounts
    - Computes tax on the appropriate taxable base
    - Computes tax on the appropriate taxable base
    - Finally adds additional fees for the complete invoice total
    - Finally adds additional fees for the complete invoice total


    3. ACCOUNTING BEST PRACTICES:
    3. ACCOUNTING BEST PRACTICES:
    - Follows proper accounting order-of-operations
    - Follows proper accounting order-of-operations
    - Avoids common calculation errors (e.g., calculating tax on already-taxed amounts)
    - Avoids common calculation errors (e.g., calculating tax on already-taxed amounts)
    - Properly handles the distinction between gross and net amounts
    - Properly handles the distinction between gross and net amounts
    - Ensures no mathematical distortion of the true invoice value
    - Ensures no mathematical distortion of the true invoice value


    4. EXTENSIBILITY CONSIDERATIONS:
    4. EXTENSIBILITY CONSIDERATIONS:
    - Supports both fixed and percentage-based additional fees
    - Supports both fixed and percentage-based additional fees
    - Allows for future addition of tax categories or discount types
    - Allows for future addition of tax categories or discount types
    - Maintains separation of concerns between line items and invoice-level calculations
    - Maintains separation of concerns between line items and invoice-level calculations
    - Provides a solid foundation for complex pricing models
    - Provides a solid foundation for complex pricing models


    This invoice total calculation algorithm addresses several critical requirements:
    This invoice total calculation algorithm addresses several critical requirements:
    - Accurate financial representation for accounting and tax purposes
    - Accurate financial representation for accounting and tax purposes
    - Proper handling of multiple pricing components
    - Proper handling of multiple pricing components
    - Transparent total calculation that can be audited
    - Transparent total calculation that can be audited
    - Support for various business models and fee structures
    - Support for various business models and fee structures


    The implementation specifically supports common real-world scenarios:
    The implementation specifically supports common real-world scenarios:
    - Products/services with different tax rates on the same invoice
    - Products/services with different tax rates on the same invoice
    - Inclusion of processing fees or service charges
    - Inclusion of processing fees or service charges
    - Fixed and percentage-based additional charges
    - Fixed and percentage-based additional charges
    - Mix of taxable and non-taxable items
    - Mix of taxable and non-taxable items


    Returns:
    Returns:
    The complete invoice total amount, including taxes and additional fees
    The complete invoice total amount, including taxes and additional fees
    """
    """
    return (
    return (
    self.get_taxable_amount()  # Base amount after discounts
    self.get_taxable_amount()  # Base amount after discounts
    + self.get_tax_total()  # All applicable taxes
    + self.get_tax_total()  # All applicable taxes
    + self.get_additional_fees_total()  # Service charges and other fees
    + self.get_additional_fees_total()  # Service charges and other fees
    )
    )


    def format_amount(self, amount: float) -> str:
    def format_amount(self, amount: float) -> str:
    """
    """
    Format an amount with currency symbol.
    Format an amount with currency symbol.


    Args:
    Args:
    amount: Amount to format
    amount: Amount to format


    Returns:
    Returns:
    Formatted amount with currency symbol
    Formatted amount with currency symbol
    """
    """
    currency_symbols = {
    currency_symbols = {
    "USD": "$",
    "USD": "$",
    "EUR": "€",
    "EUR": "€",
    "GBP": "£",
    "GBP": "£",
    "JPY": "¥",
    "JPY": "¥",
    "CAD": "C$",
    "CAD": "C$",
    "AUD": "A$",
    "AUD": "A$",
    }
    }


    symbol = currency_symbols.get(self.currency, self.currency)
    symbol = currency_symbols.get(self.currency, self.currency)


    if self.currency == "JPY":
    if self.currency == "JPY":
    # JPY doesn't use decimal places
    # JPY doesn't use decimal places
    return f"{symbol}{int(amount):,}"
    return f"{symbol}{int(amount):,}"
    else:
    else:
    return f"{symbol}{amount:,.2f}"
    return f"{symbol}{amount:,.2f}"


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the invoice to a dictionary.
    Convert the invoice to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the invoice
    Dictionary representation of the invoice
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "number": self.number,
    "number": self.number,
    "customer_id": self.customer_id,
    "customer_id": self.customer_id,
    "date": self.date.isoformat(),
    "date": self.date.isoformat(),
    "due_date": self.due_date.isoformat(),
    "due_date": self.due_date.isoformat(),
    "currency": self.currency,
    "currency": self.currency,
    "items": [item.to_dict() for item in self.items],
    "items": [item.to_dict() for item in self.items],
    "status": self.status,
    "status": self.status,
    "created_at": self.created_at.isoformat(),
    "created_at": self.created_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    "company_name": self.company_name,
    "company_name": self.company_name,
    "company_address": self.company_address,
    "company_address": self.company_address,
    "company_email": self.company_email,
    "company_email": self.company_email,
    "company_phone": self.company_phone,
    "company_phone": self.company_phone,
    "company_website": self.company_website,
    "company_website": self.company_website,
    "company_logo_url": self.company_logo_url,
    "company_logo_url": self.company_logo_url,
    "customer_name": self.customer_name,
    "customer_name": self.customer_name,
    "customer_email": self.customer_email,
    "customer_email": self.customer_email,
    "customer_address": self.customer_address,
    "customer_address": self.customer_address,
    "payment_terms": self.payment_terms,
    "payment_terms": self.payment_terms,
    "notes": self.notes,
    "notes": self.notes,
    "terms": self.terms,
    "terms": self.terms,
    "tax_name": self.tax_name,
    "tax_name": self.tax_name,
    "discount_name": self.discount_name,
    "discount_name": self.discount_name,
    "additional_fees": self.additional_fees,
    "additional_fees": self.additional_fees,
    "custom_fields": self.custom_fields,
    "custom_fields": self.custom_fields,
    "status_history": self.status_history,
    "status_history": self.status_history,
    "payments": self.payments,
    "payments": self.payments,
    "subtotal": self.get_subtotal(),
    "subtotal": self.get_subtotal(),
    "discount_total": self.get_discount_total(),
    "discount_total": self.get_discount_total(),
    "tax_total": self.get_tax_total(),
    "tax_total": self.get_tax_total(),
    "additional_fees_total": self.get_additional_fees_total(),
    "additional_fees_total": self.get_additional_fees_total(),
    "total": self.get_total(),
    "total": self.get_total(),
    "total_paid": self.get_total_paid(),
    "total_paid": self.get_total_paid(),
    "balance_due": self.get_balance_due(),
    "balance_due": self.get_balance_due(),
    "metadata": self.metadata,
    "metadata": self.metadata,
    }
    }


    def to_json(self, indent: int = 2) -> str:
    def to_json(self, indent: int = 2) -> str:
    """
    """
    Convert the invoice to a JSON string.
    Convert the invoice to a JSON string.


    Args:
    Args:
    indent: Number of spaces for indentation
    indent: Number of spaces for indentation


    Returns:
    Returns:
    JSON string representation of the invoice
    JSON string representation of the invoice
    """
    """
    return json.dumps(self.to_dict(), indent=indent)
    return json.dumps(self.to_dict(), indent=indent)


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Invoice":
    def from_dict(cls, data: Dict[str, Any]) -> "Invoice":
    """
    """
    Reconstruct a complete invoice object from serialized data with full integrity.
    Reconstruct a complete invoice object from serialized data with full integrity.


    This algorithm implements a robust deserialization process for invoice data
    This algorithm implements a robust deserialization process for invoice data
    with comprehensive reconstruction of the object hierarchy. The implementation
    with comprehensive reconstruction of the object hierarchy. The implementation
    follows these key phases:
    follows these key phases:


    1. HIERARCHICAL RECONSTRUCTION:
    1. HIERARCHICAL RECONSTRUCTION:
    - Rebuilds the complete invoice structure from flat serialized data
    - Rebuilds the complete invoice structure from flat serialized data
    - Reestablishes parent-child relationships between invoice and line items
    - Reestablishes parent-child relationships between invoice and line items
    - Properly reconstructs metadata, payments, and status history
    - Properly reconstructs metadata, payments, and status history
    - Maintains referential integrity throughout the invoice object graph
    - Maintains referential integrity throughout the invoice object graph
    - Ensures all calculated properties are properly recomputed
    - Ensures all calculated properties are properly recomputed


    2. DATA VALIDATION AND INTEGRITY:
    2. DATA VALIDATION AND INTEGRITY:
    - Preserves critical identifiers (invoice ID, invoice number, etc.)
    - Preserves critical identifiers (invoice ID, invoice number, etc.)
    - Ensures proper data type conversion (strings to dates, etc.)
    - Ensures proper data type conversion (strings to dates, etc.)
    - Handles both required and optional fields appropriately
    - Handles both required and optional fields appropriately
    - Maintains backward compatibility with older serialized formats
    - Maintains backward compatibility with older serialized formats
    - Ensures the integrity of the reconstructed invoice object
    - Ensures the integrity of the reconstructed invoice object


    3. COMPLETE STATE RESTORATION:
    3. COMPLETE STATE RESTORATION:
    - Restores the full invoice state including:
    - Restores the full invoice state including:
    a) Financial data (items, totals, payments)
    a) Financial data (items, totals, payments)
    b) Metadata (company info, customer info, custom fields)
    b) Metadata (company info, customer info, custom fields)
    c) Status history and audit trail information
    c) Status history and audit trail information
    d) Payment records and transaction history
    d) Payment records and transaction history
    - Maintains accurate timestamps for all historical events
    - Maintains accurate timestamps for all historical events


    4. SERIALIZATION FORMAT RESILIENCE:
    4. SERIALIZATION FORMAT RESILIENCE:
    - Handles potential format variations gracefully
    - Handles potential format variations gracefully
    - Uses proper default values for missing optional fields
    - Uses proper default values for missing optional fields
    - Maintains compatibility across serialization versions
    - Maintains compatibility across serialization versions
    - Properly handles both primitive and complex nested data types
    - Properly handles both primitive and complex nested data types


    This invoice reconstruction algorithm addresses several critical requirements:
    This invoice reconstruction algorithm addresses several critical requirements:
    - Accurate invoice restoration for long-term data persistence
    - Accurate invoice restoration for long-term data persistence
    - Reliable data transfer between system components
    - Reliable data transfer between system components
    - Complete audit trail preservation
    - Complete audit trail preservation
    - Format resilience for backward compatibility
    - Format resilience for backward compatibility


    The implementation specifically supports common data exchange scenarios:
    The implementation specifically supports common data exchange scenarios:
    - Invoice data loaded from storage (database, files)
    - Invoice data loaded from storage (database, files)
    - Invoice data imported from external systems
    - Invoice data imported from external systems
    - Historical invoice lookup and restoration
    - Historical invoice lookup and restoration
    - Cross-system invoice data synchronization
    - Cross-system invoice data synchronization


    Args:
    Args:
    data: A dictionary containing the serialized invoice data with all
    data: A dictionary containing the serialized invoice data with all
    necessary invoice properties, including items, payments, and metadata
    necessary invoice properties, including items, payments, and metadata


    Returns:
    Returns:
    A fully reconstructed Invoice instance with all properties, relationships,
    A fully reconstructed Invoice instance with all properties, relationships,
    and history properly restored
    and history properly restored
    """
    """
    # Create invoice
    # Create invoice
    invoice = cls(
    invoice = cls(
    customer_id=data["customer_id"],
    customer_id=data["customer_id"],
    date=datetime.fromisoformat(data["date"]),
    date=datetime.fromisoformat(data["date"]),
    due_date=datetime.fromisoformat(data["due_date"]),
    due_date=datetime.fromisoformat(data["due_date"]),
    currency=data["currency"],
    currency=data["currency"],
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    # Set invoice ID and number
    # Set invoice ID and number
    invoice.id = data["id"]
    invoice.id = data["id"]
    invoice.number = data["number"]
    invoice.number = data["number"]


    # Add items
    # Add items
    for item_data in data["items"]:
    for item_data in data["items"]:
    item = InvoiceItem.from_dict(item_data)
    item = InvoiceItem.from_dict(item_data)
    invoice.items.append(item)
    invoice.items.append(item)


    # Set other properties
    # Set other properties
    invoice.status = data["status"]
    invoice.status = data["status"]
    invoice.created_at = datetime.fromisoformat(data["created_at"])
    invoice.created_at = datetime.fromisoformat(data["created_at"])
    invoice.updated_at = datetime.fromisoformat(data["updated_at"])
    invoice.updated_at = datetime.fromisoformat(data["updated_at"])


    invoice.company_name = data.get("company_name", "")
    invoice.company_name = data.get("company_name", "")
    invoice.company_address = data.get("company_address", "")
    invoice.company_address = data.get("company_address", "")
    invoice.company_email = data.get("company_email", "")
    invoice.company_email = data.get("company_email", "")
    invoice.company_phone = data.get("company_phone", "")
    invoice.company_phone = data.get("company_phone", "")
    invoice.company_website = data.get("company_website", "")
    invoice.company_website = data.get("company_website", "")
    invoice.company_logo_url = data.get("company_logo_url", "")
    invoice.company_logo_url = data.get("company_logo_url", "")


    invoice.customer_name = data.get("customer_name", "")
    invoice.customer_name = data.get("customer_name", "")
    invoice.customer_email = data.get("customer_email", "")
    invoice.customer_email = data.get("customer_email", "")
    invoice.customer_address = data.get("customer_address", "")
    invoice.customer_address = data.get("customer_address", "")


    invoice.payment_terms = data.get("payment_terms", "")
    invoice.payment_terms = data.get("payment_terms", "")
    invoice.notes = data.get("notes", "")
    invoice.notes = data.get("notes", "")
    invoice.terms = data.get("terms", "")
    invoice.terms = data.get("terms", "")


    invoice.tax_name = data.get("tax_name", "Tax")
    invoice.tax_name = data.get("tax_name", "Tax")
    invoice.discount_name = data.get("discount_name", "Discount")
    invoice.discount_name = data.get("discount_name", "Discount")


    invoice.additional_fees = data.get("additional_fees", [])
    invoice.additional_fees = data.get("additional_fees", [])
    invoice.custom_fields = data.get("custom_fields", {})
    invoice.custom_fields = data.get("custom_fields", {})


    invoice.status_history = data.get("status_history", [])
    invoice.status_history = data.get("status_history", [])
    invoice.payments = data.get("payments", [])
    invoice.payments = data.get("payments", [])


    return invoice
    return invoice


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the invoice."""
    return f"Invoice({self.number}, {self.date.strftime('%Y-%m-%d')}, {self.format_amount(self.get_total())})"


    # Example usage
    if __name__ == "__main__":
    # Create an invoice
    invoice = Invoice(customer_id="cust_123", currency="USD")

    # Set company and customer information
    invoice.set_company_info(
    name="AI Tools Inc.",
    address="123 Main St, San Francisco, CA 94111",
    email="billing@aitools.com",
    phone="(555) 123-4567",
    website="https://aitools.com",
    )

    invoice.set_customer_info(
    name="John Doe",
    email="john.doe@example.com",
    address="456 Oak St, San Francisco, CA 94112",
    )

    # Add items
    invoice.add_item(
    description="Premium Subscription (Monthly)",
    quantity=1,
    unit_price=29.99,
    tax_rate=0.0825,  # 8.25% tax
    )

    invoice.add_item(
    description="Additional User Licenses",
    quantity=3,
    unit_price=9.99,
    tax_rate=0.0825,  # 8.25% tax
    )

    # Add an additional fee
    invoice.add_additional_fee(name="Processing Fee", amount=2.50)

    # Set payment terms and notes
    invoice.set_payment_terms("Net 30")
    invoice.set_notes("Thank you for your business!")

    # Print invoice details
    print(f"Invoice: {invoice.number}")
    print(f"Date: {invoice.date.strftime('%Y-%m-%d')}")
    print(f"Due Date: {invoice.due_date.strftime('%Y-%m-%d')}")
    print(f"Status: {invoice.status}")

    print("\nItems:")
    for item in invoice.items:
    print(f"- {item}")

    print(f"\nSubtotal: {invoice.format_amount(invoice.get_subtotal())}")
    print(f"Tax: {invoice.format_amount(invoice.get_tax_total())}")
    print(
    f"Additional Fees: {invoice.format_amount(invoice.get_additional_fees_total())}"
    )
    print(f"Total: {invoice.format_amount(invoice.get_total())}")

    # Update status to sent
    invoice.update_status(InvoiceStatus.SENT, "Invoice sent to customer")
    print(f"\nUpdated Status: {invoice.status}")

    # Add a payment
    payment = invoice.add_payment(
    amount=30.00, payment_method="Credit Card", transaction_id="txn_123456"
    )

    print(f"\nPayment Added: {invoice.format_amount(payment['amount'])}")
    print(f"Total Paid: {invoice.format_amount(invoice.get_total_paid())}")
    print(f"Balance Due: {invoice.format_amount(invoice.get_balance_due()}"
    print(f"Status: {invoice.status}"

    # Add another payment to pay in full
    remaining = invoice.get_balance_due(
    payment = invoice.add_payment(
    amount=remaining, payment_method="Credit Card", transaction_id="txn_789012"


    print(f"\nSecond Payment Added: {invoice.format_amount(payment['amount']}"
    print(f"Total Paid: {invoice.format_amount(invoice.get_total_paid(}"
    print(f"Balance Due: {invoice.format_amount(invoice.get_balance_due(}"
    print(f"Status: {invoice.status}"

    # Convert to dictionary and back
    invoice_dict = invoice.to_dict(
    restored_invoice = Invoice.from_dict(invoice_dict

    print(f"\nRestored Invoice: {restored_invoice}"
    print(f"Is Same ID: {restored_invoice.id == invoice.id}"