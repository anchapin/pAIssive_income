"""
Invoice manager for the pAIssive Income project.

This module provides a class for managing invoices, including
generation, storage, retrieval, and status updates.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import os
import json
import copy

from .invoice import Invoice, InvoiceStatus, InvoiceItem
from .billing_calculator import BillingCalculator
from .usage_tracker import UsageTracker


class InvoiceManager:
    """
    Class for managing invoices.
    
    This class provides methods for generating, storing, retrieving,
    and updating invoices.
    """
    
    def __init__(
        self,
        billing_calculator: Optional[BillingCalculator] = None,
        usage_tracker: Optional[UsageTracker] = None,
        storage_dir: Optional[str] = None,
        company_info: Optional[Dict[str, str]] = None
    ):
        """
        Initialize an invoice manager.
        
        Args:
            billing_calculator: Billing calculator to use
            usage_tracker: Usage tracker to use
            storage_dir: Directory for storing invoice data
            company_info: Company information for invoices
        """
        self.billing_calculator = billing_calculator
        self.usage_tracker = usage_tracker
        self.storage_dir = storage_dir
        self.company_info = company_info or {}
        
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        
        self.invoices = {}
        self.customer_invoices = {}
        
        # Load invoices if storage directory is set
        if storage_dir:
            self.load_invoices()
    
    def create_invoice(
        self,
        customer_id: str,
        date: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
        currency: str = "USD",
        items: Optional[List[Dict[str, Any]]] = None,
        customer_info: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Invoice:
        """
        Create an invoice.
        
        Args:
            customer_id: ID of the customer
            date: Date of the invoice
            due_date: Due date of the invoice
            currency: Currency code (e.g., USD)
            items: List of invoice items
            customer_info: Customer information for the invoice
            metadata: Additional metadata for the invoice
            
        Returns:
            The created invoice
        """
        # Create invoice
        invoice = Invoice(
            customer_id=customer_id,
            date=date,
            due_date=due_date,
            currency=currency,
            metadata=metadata or {}
        )
        
        # Set company information
        if self.company_info:
            invoice.set_company_info(
                name=self.company_info.get("name", ""),
                address=self.company_info.get("address", ""),
                email=self.company_info.get("email", ""),
                phone=self.company_info.get("phone", ""),
                website=self.company_info.get("website", ""),
                logo_url=self.company_info.get("logo_url", "")
            )
        
        # Set customer information
        if customer_info:
            invoice.set_customer_info(
                name=customer_info.get("name", ""),
                email=customer_info.get("email", ""),
                address=customer_info.get("address", "")
            )
        
        # Add items
        if items:
            for item in items:
                invoice.add_item(
                    description=item["description"],
                    quantity=item.get("quantity", 1.0),
                    unit_price=item.get("unit_price", 0.0),
                    discount=item.get("discount", 0.0),
                    tax_rate=item.get("tax_rate", 0.0),
                    metadata=item.get("metadata")
                )
        
        # Store invoice
        self.invoices[invoice.id] = invoice
        
        # Add to customer's invoices
        if customer_id not in self.customer_invoices:
            self.customer_invoices[customer_id] = []
        
        self.customer_invoices[customer_id].append(invoice.id)
        
        # Save invoice if storage directory is set
        if self.storage_dir:
            self._save_invoice(invoice)
        
        return invoice
    
    def generate_invoice_from_usage(
        self,
        customer_id: str,
        start_time: datetime,
        end_time: datetime,
        due_date: Optional[datetime] = None,
        currency: str = "USD",
        customer_info: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Invoice]:
        """
        Generate an invoice from usage data.
        
        Args:
            customer_id: ID of the customer
            start_time: Start time for usage records
            end_time: End time for usage records
            due_date: Due date of the invoice
            currency: Currency code (e.g., USD)
            customer_info: Customer information for the invoice
            metadata: Additional metadata for the invoice
            
        Returns:
            The generated invoice or None if no usage data is available
        """
        if not self.billing_calculator or not self.usage_tracker:
            raise ValueError("Billing calculator and usage tracker are required to generate an invoice from usage")
        
        # Calculate usage cost
        usage_cost = self.billing_calculator.calculate_usage_cost(
            customer_id=customer_id,
            start_time=start_time,
            end_time=end_time
        )
        
        # Check if there are any items
        if not usage_cost["items"]:
            return None
        
        # Create invoice
        invoice = self.create_invoice(
            customer_id=customer_id,
            date=end_time,
            due_date=due_date or (end_time + timedelta(days=30)),
            currency=currency,
            customer_info=customer_info,
            metadata=metadata or {}
        )
        
        # Add billing period to metadata
        invoice.metadata["billing_period_start"] = start_time.isoformat()
        invoice.metadata["billing_period_end"] = end_time.isoformat()
        
        # Add items from usage cost
        for item in usage_cost["items"]:
            invoice.add_item(
                description=f"{item['metric']} ({item['category']}, {item['resource_type']})",
                quantity=item["quantity"],
                unit_price=item["cost"] / item["quantity"] if item["quantity"] > 0 else 0.0,
                metadata={
                    "metric": item["metric"],
                    "category": item["category"],
                    "resource_type": item["resource_type"],
                    "records": item["records"]
                }
            )
        
        # Set payment terms
        invoice.set_payment_terms("Net 30")
        
        # Set notes
        invoice.set_notes(f"Usage from {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}")
        
        # Save invoice if storage directory is set
        if self.storage_dir:
            self._save_invoice(invoice)
        
        return invoice
    
    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """
        Get an invoice by ID.
        
        Args:
            invoice_id: ID of the invoice
            
        Returns:
            The invoice or None if not found
        """
        return self.invoices.get(invoice_id)
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """
        Get an invoice by number.
        
        Args:
            invoice_number: Number of the invoice
            
        Returns:
            The invoice or None if not found
        """
        for invoice in self.invoices.values():
            if invoice.number == invoice_number:
                return invoice
        
        return None
    
    def get_customer_invoices(
        self,
        customer_id: str,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Invoice]:
        """
        Get invoices for a customer.
        
        Args:
            customer_id: ID of the customer
            status: Status of invoices to get
            start_date: Start date for invoices
            end_date: End date for invoices
            limit: Maximum number of invoices to return
            
        Returns:
            List of invoices
        """
        if customer_id not in self.customer_invoices:
            return []
        
        invoices = []
        
        for invoice_id in self.customer_invoices[customer_id]:
            invoice = self.invoices.get(invoice_id)
            
            if not invoice:
                continue
            
            # Filter by status
            if status and invoice.status != status:
                continue
            
            # Filter by date range
            if start_date and invoice.date < start_date:
                continue
            
            if end_date and invoice.date > end_date:
                continue
            
            invoices.append(invoice)
        
        # Sort by date (newest first)
        invoices.sort(key=lambda i: i.date, reverse=True)
        
        # Apply limit
        return invoices[:limit]
    
    def update_invoice_status(
        self,
        invoice_id: str,
        status: str,
        reason: Optional[str] = None
    ) -> Optional[Invoice]:
        """
        Update the status of an invoice.
        
        Args:
            invoice_id: ID of the invoice
            status: New status
            reason: Reason for the status change
            
        Returns:
            The updated invoice or None if not found
        """
        invoice = self.get_invoice(invoice_id)
        
        if not invoice:
            return None
        
        # Update status
        invoice.update_status(status, reason)
        
        # Save invoice if storage directory is set
        if self.storage_dir:
            self._save_invoice(invoice)
        
        return invoice
    
    def add_payment(
        self,
        invoice_id: str,
        amount: float,
        date: Optional[datetime] = None,
        payment_method: str = "",
        transaction_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Add a payment to an invoice.
        
        Args:
            invoice_id: ID of the invoice
            amount: Payment amount
            date: Payment date
            payment_method: Payment method
            transaction_id: Transaction ID
            metadata: Additional metadata for the payment
            
        Returns:
            Dictionary with payment information or None if the invoice is not found
        """
        invoice = self.get_invoice(invoice_id)
        
        if not invoice:
            return None
        
        # Add payment
        payment = invoice.add_payment(
            amount=amount,
            date=date,
            payment_method=payment_method,
            transaction_id=transaction_id,
            metadata=metadata
        )
        
        # Save invoice if storage directory is set
        if self.storage_dir:
            self._save_invoice(invoice)
        
        return payment
    
    def delete_invoice(self, invoice_id: str) -> bool:
        """
        Delete an invoice.
        
        Args:
            invoice_id: ID of the invoice
            
        Returns:
            True if the invoice was deleted, False otherwise
        """
        # Check if invoice exists
        invoice = self.get_invoice(invoice_id)
        
        if not invoice:
            return False
        
        # Remove from customer's invoices
        customer_id = invoice.customer_id
        
        if customer_id in self.customer_invoices:
            if invoice_id in self.customer_invoices[customer_id]:
                self.customer_invoices[customer_id].remove(invoice_id)
        
        # Remove from invoices
        del self.invoices[invoice_id]
        
        # Delete file if storage directory is set
        if self.storage_dir:
            file_path = os.path.join(self.storage_dir, f"{invoice_id}.json")
            
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return True
    
    def get_overdue_invoices(self) -> List[Invoice]:
        """
        Get all overdue invoices.
        
        Returns:
            List of overdue invoices
        """
        overdue_invoices = []
        
        for invoice in self.invoices.values():
            if invoice.is_overdue():
                overdue_invoices.append(invoice)
        
        # Sort by due date (oldest first)
        overdue_invoices.sort(key=lambda i: i.due_date)
        
        return overdue_invoices
    
    def get_unpaid_invoices(self) -> List[Invoice]:
        """
        Get all unpaid invoices.
        
        Returns:
            List of unpaid invoices
        """
        unpaid_invoices = []
        
        for invoice in self.invoices.values():
            if not invoice.is_paid() and invoice.status not in [InvoiceStatus.CANCELED, InvoiceStatus.VOID]:
                unpaid_invoices.append(invoice)
        
        # Sort by due date (oldest first)
        unpaid_invoices.sort(key=lambda i: i.due_date)
        
        return unpaid_invoices
    
    def get_invoice_summary(
        self,
        customer_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get a summary of invoices.
        
        Args:
            customer_id: ID of the customer (if None, summarize all invoices)
            start_date: Start date for invoices
            end_date: End date for invoices
            
        Returns:
            Dictionary with invoice summary
        """
        # Get invoices to summarize
        if customer_id:
            invoices = self.get_customer_invoices(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date,
                limit=1000  # Use a high limit to get all invoices
            )
        else:
            invoices = list(self.invoices.values())
            
            # Filter by date range
            if start_date or end_date:
                filtered_invoices = []
                
                for invoice in invoices:
                    if start_date and invoice.date < start_date:
                        continue
                    
                    if end_date and invoice.date > end_date:
                        continue
                    
                    filtered_invoices.append(invoice)
                
                invoices = filtered_invoices
        
        # Initialize summary
        summary = {
            "total_count": len(invoices),
            "total_amount": 0.0,
            "total_paid": 0.0,
            "total_due": 0.0,
            "currencies": {},
            "by_status": {},
            "by_month": {}
        }
        
        # Calculate summary
        for invoice in invoices:
            # Count by status
            if invoice.status not in summary["by_status"]:
                summary["by_status"][invoice.status] = {
                    "count": 0,
                    "amount": 0.0,
                    "paid": 0.0,
                    "due": 0.0
                }
            
            summary["by_status"][invoice.status]["count"] += 1
            summary["by_status"][invoice.status]["amount"] += invoice.get_total()
            summary["by_status"][invoice.status]["paid"] += invoice.get_total_paid()
            summary["by_status"][invoice.status]["due"] += invoice.get_balance_due()
            
            # Count by month
            month_key = invoice.date.strftime("%Y-%m")
            
            if month_key not in summary["by_month"]:
                summary["by_month"][month_key] = {
                    "count": 0,
                    "amount": 0.0,
                    "paid": 0.0,
                    "due": 0.0
                }
            
            summary["by_month"][month_key]["count"] += 1
            summary["by_month"][month_key]["amount"] += invoice.get_total()
            summary["by_month"][month_key]["paid"] += invoice.get_total_paid()
            summary["by_month"][month_key]["due"] += invoice.get_balance_due()
            
            # Track amounts by currency
            if invoice.currency not in summary["currencies"]:
                summary["currencies"][invoice.currency] = {
                    "total_amount": 0.0,
                    "total_paid": 0.0,
                    "total_due": 0.0
                }
            
            # Add amounts
            summary["currencies"][invoice.currency]["total_amount"] += invoice.get_total()
            summary["currencies"][invoice.currency]["total_paid"] += invoice.get_total_paid()
            summary["currencies"][invoice.currency]["total_due"] += invoice.get_balance_due()
            
            summary["total_amount"] += invoice.get_total()
            summary["total_paid"] += invoice.get_total_paid()
            summary["total_due"] += invoice.get_balance_due()
        
        return summary
    
    def load_invoices(self) -> None:
        """
        Load invoices from storage directory.
        """
        if not self.storage_dir or not os.path.exists(self.storage_dir):
            return
        
        # Clear existing data
        self.invoices = {}
        self.customer_invoices = {}
        
        # Load invoices
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.storage_dir, filename)
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    # Create invoice
                    invoice = Invoice.from_dict(data)
                    
                    # Store invoice
                    self.invoices[invoice.id] = invoice
                    
                    # Add to customer's invoices
                    if invoice.customer_id not in self.customer_invoices:
                        self.customer_invoices[invoice.customer_id] = []
                    
                    self.customer_invoices[invoice.customer_id].append(invoice.id)
                
                except Exception as e:
                    print(f"Error loading invoice from {file_path}: {e}")
    
    def _save_invoice(self, invoice: Invoice) -> None:
        """
        Save an invoice to the storage directory.
        
        Args:
            invoice: Invoice to save
        """
        if not self.storage_dir:
            return
        
        file_path = os.path.join(self.storage_dir, f"{invoice.id}.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(invoice.to_json())


# Example usage
if __name__ == "__main__":
    from .billing_calculator import BillingCalculator
    from .usage_tracker import UsageTracker
    
    # Create a usage tracker
    tracker = UsageTracker()
    
    # Create a billing calculator
    calculator = BillingCalculator(usage_tracker=tracker)
    
    # Create an invoice manager
    manager = InvoiceManager(
        billing_calculator=calculator,
        usage_tracker=tracker,
        storage_dir="invoices",
        company_info={
            "name": "AI Tools Inc.",
            "address": "123 Main St, San Francisco, CA 94111",
            "email": "billing@aitools.com",
            "phone": "(555) 123-4567",
            "website": "https://aitools.com"
        }
    )
    
    # Create an invoice
    invoice = manager.create_invoice(
        customer_id="cust_123",
        customer_info={
            "name": "John Doe",
            "email": "john.doe@example.com",
            "address": "456 Oak St, San Francisco, CA 94112"
        }
    )
    
    # Add items
    invoice.add_item(
        description="Premium Subscription (Monthly)",
        quantity=1,
        unit_price=29.99,
        tax_rate=0.0825  # 8.25% tax
    )
    
    invoice.add_item(
        description="Additional User Licenses",
        quantity=3,
        unit_price=9.99,
        tax_rate=0.0825  # 8.25% tax
    )
    
    print(f"Invoice created: {invoice}")
    print(f"Number: {invoice.number}")
    print(f"Total: {invoice.format_amount(invoice.get_total())}")
    
    # Update status to sent
    manager.update_invoice_status(invoice.id, InvoiceStatus.SENT, "Invoice sent to customer")
    
    print(f"\nUpdated status: {invoice.status}")
    
    # Add a payment
    payment = manager.add_payment(
        invoice_id=invoice.id,
        amount=30.00,
        payment_method="Credit Card",
        transaction_id="txn_123456"
    )
    
    print(f"\nPayment added: {invoice.format_amount(payment['amount'])}")
    print(f"Total paid: {invoice.format_amount(invoice.get_total_paid())}")
    print(f"Balance due: {invoice.format_amount(invoice.get_balance_due())}")
    print(f"Status: {invoice.status}")
    
    # Get customer invoices
    invoices = manager.get_customer_invoices("cust_123")
    
    print(f"\nCustomer invoices ({len(invoices)}):")
    for inv in invoices:
        print(f"- {inv}")
    
    # Get invoice summary
    summary = manager.get_invoice_summary()
    
    print(f"\nInvoice summary:")
    print(f"Total count: {summary['total_count']}")
    print(f"Total amount: ${summary['total_amount']:.2f}")
    print(f"Total paid: ${summary['total_paid']:.2f}")
    print(f"Total due: ${summary['total_due']:.2f}")
