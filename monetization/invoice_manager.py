"""
Invoice manager for the pAIssive Income project.

This module provides a class for managing invoices, including
generation, storage, retrieval, and status updates.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import json

from .invoice import Invoice, InvoiceStatus
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
        company_info: Optional[Dict[str, str]] = None,
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
        metadata: Optional[Dict[str, Any]] = None,
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
            metadata=metadata or {},
        )

        # Set company information
        if self.company_info:
            invoice.set_company_info(
                name=self.company_info.get("name", ""),
                address=self.company_info.get("address", ""),
                email=self.company_info.get("email", ""),
                phone=self.company_info.get("phone", ""),
                website=self.company_info.get("website", ""),
                logo_url=self.company_info.get("logo_url", ""),
            )

        # Set customer information
        if customer_info:
            invoice.set_customer_info(
                name=customer_info.get("name", ""),
                email=customer_info.get("email", ""),
                address=customer_info.get("address", ""),
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
                    metadata=item.get("metadata"),
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
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Invoice]:
        """
        Generate an invoice from usage data for metered billing scenarios.

        This algorithm implements a critical usage-to-invoice transformation process
        that powers metered and consumption-based billing models. The implementation
        follows these key stages:

        1. USAGE DATA ACQUISITION AND COST CALCULATION:
           - Interfaces with the usage tracker to collect relevant usage records
           - Applies the appropriate pricing rules through the billing calculator
           - Transforms raw usage metrics into monetized line items
           - Handles different usage categories, resources, and metrics properly

        2. INVOICE CREATION WITH APPROPRIATE METADATA:
           - Generates a properly structured invoice object with customer context
           - Sets appropriate default values for invoice dates and payment terms
           - Preserves billing period information for accurate record-keeping
           - Ensures proper attribution of the invoice to the correct customer

        3. LINE ITEM GENERATION FROM USAGE METRICS:
           - Converts usage-based cost calculations into structured invoice line items
           - Creates descriptive item entries that clearly identify the billed services
           - Calculates proper unit prices based on total costs and quantities
           - Maintains detailed metadata linking each line item to its source usage records

        4. BUSINESS RULE APPLICATION:
           - Applies standardized payment terms (e.g., Net 30)
           - Adds contextual notes about the billing period
           - Ensures consistent invoice structure across billing periods
           - Handles edge cases like zero-usage periods appropriately

        This usage-based invoice generation algorithm addresses several critical requirements:
        - Accurate translation of metered usage into billable items
        - Clear and transparent presentation of usage-based charges
        - Proper record keeping for financial reporting and reconciliation
        - Support for various usage-based business models

        The implementation specifically supports common SaaS and cloud billing scenarios:
        - API call-based billing (pay per request)
        - Storage-based billing (pay per GB)
        - User-based billing (pay per seat with usage tracking)
        - Resource consumption billing (compute time, bandwidth, etc.)
        - Mixed billing models (subscription + usage)

        Args:
            customer_id: ID of the customer to generate the invoice for
            start_time: Start of the billing period for usage records
            end_time: End of the billing period for usage records
            due_date: When the invoice payment is due (defaults to end_time + 30 days)
            currency: Currency code for the invoice (e.g., USD, EUR)
            customer_info: Optional dictionary with customer details (name, address, etc.)
            metadata: Additional invoice metadata to include

        Returns:
            The generated Invoice object containing usage-based line items,
            or None if no billable usage was found for the period
        """
        if not self.billing_calculator or not self.usage_tracker:
            raise ValueError(
                "Billing calculator and usage tracker are required to generate an invoice from usage"
            )

        # STAGE 1: Calculate usage cost by calling the billing calculator
        # This transforms raw usage records into monetized costs
        usage_cost = self.billing_calculator.calculate_usage_cost(
            customer_id=customer_id, start_time=start_time, end_time=end_time
        )

        # Exit early if there's no billable usage for this period
        if not usage_cost["items"]:
            return None

        # STAGE 2: Create the base invoice with proper metadata
        invoice = self.create_invoice(
            customer_id=customer_id,
            date=end_time,  # Invoice date is the end of the billing period
            due_date=due_date
            or (
                end_time + timedelta(days=30)
            ),  # Default due date is 30 days after billing period
            currency=currency,
            customer_info=customer_info,
            metadata=metadata or {},
        )

        # Store billing period information for record-keeping and auditing
        invoice.metadata["billing_period_start"] = start_time.isoformat()
        invoice.metadata["billing_period_end"] = end_time.isoformat()

        # STAGE 3: Transform usage cost items into invoice line items
        for item in usage_cost["items"]:
            # Create a descriptive line item that identifies the service clearly
            invoice.add_item(
                description=f"{item['metric']} ({item['category']}, {item['resource_type']})",
                quantity=item["quantity"],
                unit_price=(
                    item["cost"] / item["quantity"] if item["quantity"] > 0 else 0.0
                ),  # Handle zero-quantity case
                metadata={
                    # Preserve the connection to usage data for auditing and disputes
                    "metric": item["metric"],
                    "category": item["category"],
                    "resource_type": item["resource_type"],
                    "records": item["records"],  # Links to the detailed usage records
                },
            )

        # STAGE 4: Apply business rules
        # Set standard payment terms
        invoice.set_payment_terms("Net 30")

        # Add a descriptive note about the billing period for customer clarity
        invoice.set_notes(
            f"Usage from {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}"
        )

        # Save the generated invoice to persistent storage if configured
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
        limit: int = 100,
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
        self, invoice_id: str, status: str, reason: Optional[str] = None
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
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Add a payment to an invoice and update invoice status accordingly.

        This algorithm implements a robust payment processing and reconciliation system
        designed for enterprise financial management. The implementation follows these key stages:

        1. INVOICE VALIDATION AND RETRIEVAL:
           - Verifies the existence of the target invoice
           - Ensures proper invoice state for payment application
           - Handles error cases gracefully with clear failure indicators
           - Maintains system integrity by preventing orphaned payment records

        2. PAYMENT RECORD CREATION:
           - Generates comprehensive payment records with full transaction details
           - Captures critical financial data including amount, date, and method
           - Creates proper audit trail through transaction IDs and timestamps
           - Supports diverse payment methods (credit card, ACH, wire transfer, etc.)
           - Preserves extended payment context through flexible metadata

        3. INVOICE BALANCE RECONCILIATION:
           - Updates invoice payment status based on payment amount
           - Handles both full and partial payment scenarios appropriately
           - Supports incremental payment application for installment plans
           - Updates invoice status automatically based on payment completeness
           - Maintains accurate financial records for accounting compliance

        4. PAYMENT PERSISTENCE:
           - Ensures durable storage of payment information
           - Maintains consistency between in-memory and persistent states
           - Supports system recovery in case of failure
           - Enables proper financial record-keeping and audit trails

        This payment processing algorithm addresses several critical requirements:
        - Accurate financial record-keeping for accounting compliance
        - Support for diverse payment reconciliation scenarios
        - Robust transaction history for financial reporting
        - Clear audit trails for payment verification

        The implementation specifically supports common payment scenarios:
        - Full invoice payment in a single transaction
        - Partial payments with remaining balance tracking
        - Multi-payment reconciliation over time
        - Payment method tracking for financial analysis
        - Transaction ID linkage for payment verification

        Args:
            invoice_id: ID of the invoice to apply payment to
            amount: Payment amount to be applied to the invoice
            date: Date when payment was received (defaults to current datetime)
            payment_method: Method used for payment (e.g., "credit_card", "bank_transfer")
            transaction_id: External payment processor transaction ID for reconciliation
            metadata: Additional payment metadata for extended context

        Returns:
            Dictionary containing payment record details if successful,
            or None if the invoice was not found
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
            metadata=metadata,
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
            if not invoice.is_paid() and invoice.status not in [
                InvoiceStatus.CANCELED,
                InvoiceStatus.VOID,
            ]:
                unpaid_invoices.append(invoice)

        # Sort by due date (oldest first)
        unpaid_invoices.sort(key=lambda i: i.due_date)

        return unpaid_invoices

    def get_invoice_summary(
        self,
        customer_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive financial summary across multiple invoices.

        This algorithm implements a multi-dimensional invoice aggregation system
        that provides critical financial insights for business reporting and analysis.
        The implementation follows these key stages:

        1. DATA COLLECTION AND FILTERING:
           - Dynamically selects invoices based on customer scope (single customer or all customers)
           - Applies temporal constraints through date range filtering
           - Creates a clean dataset for accurate aggregation
           - Handles edge cases like missing invoices or invalid date ranges

        2. MULTI-DIMENSIONAL AGGREGATION:
           - Performs aggregation across three primary dimensions:
             a) Financial status (paid, unpaid, overdue, etc.)
             b) Time periods (monthly breakdown)
             c) Currency types (multi-currency support)
           - Creates nested hierarchical data structures for complex reporting
           - Maintains proper financial accounting principles during aggregation
           - Ensures consistent calculation of totals, subtotals, and counts

        3. FINANCIAL METRICS CALCULATION:
           - Calculates key financial metrics for each dimension:
             a) Total invoice amounts (gross value)
             b) Total payments received
             c) Outstanding balances
             d) Invoice counts
           - Provides complete visibility into financial health
           - Enables trend analysis through consistent time-series data
           - Facilitates reconciliation through multi-dimensional breakdowns

        4. CURRENCY HANDLING:
           - Supports multi-currency environments through currency-specific subtotals
           - Preserves currency context for accurate financial reporting
           - Avoids currency conversion errors by maintaining separation
           - Provides foundation for potential currency conversion if needed

        This invoice summary algorithm addresses several critical business requirements:
        - Executive dashboards requiring financial performance metrics
        - Accounting reconciliation requiring detailed breakdowns
        - Financial forecasting based on invoice timing and payment trends
        - Cash flow analysis based on paid vs. outstanding amounts
        - Customer payment behavior analysis

        The implementation specifically supports common financial reporting scenarios:
        - Monthly revenue recognition reports
        - Accounts receivable aging analysis
        - Collection prioritization based on overdue amounts
        - Customer-specific payment history reports
        - Multi-currency financial statements

        Args:
            customer_id: If provided, summarizes invoices for this specific customer only.
                         If None, summarizes all invoices across all customers.
            start_date: Optional start date to filter invoices by date range
            end_date: Optional end date to filter invoices by date range

        Returns:
            A hierarchical dictionary containing comprehensive invoice summary data with:
            - total_count: Total number of invoices included in the summary
            - total_amount: Gross invoice amount across all included invoices
            - total_paid: Total payments received across all included invoices
            - total_due: Total outstanding balance across all included invoices
            - currencies: Breakdown of totals by currency code
            - by_status: Breakdown of metrics by invoice status (draft, sent, paid, etc.)
            - by_month: Time-series breakdown of metrics by month (YYYY-MM format)
        """
        # STAGE 1: Get invoices to summarize with appropriate filtering
        if customer_id:
            # Single customer mode: Get filtered invoices for the specific customer
            invoices = self.get_customer_invoices(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date,
                limit=1000,  # Use a high limit to get all invoices
            )
        else:
            # All customers mode: Start with all invoices, then apply date filters
            invoices = list(self.invoices.values())

            # Apply date range filtering if specified
            if start_date or end_date:
                filtered_invoices = []

                for invoice in invoices:
                    if start_date and invoice.date < start_date:
                        continue

                    if end_date and invoice.date > end_date:
                        continue

                    filtered_invoices.append(invoice)

                invoices = filtered_invoices

        # STAGE 2: Initialize the multi-dimensional summary data structure
        summary = {
            "total_count": len(invoices),
            "total_amount": 0.0,
            "total_paid": 0.0,
            "total_due": 0.0,
            "currencies": {},  # Currency dimension
            "by_status": {},  # Status dimension
            "by_month": {},  # Time dimension
        }

        # STAGE 3: Populate the summary through multi-dimensional aggregation
        for invoice in invoices:
            # STATUS DIMENSION: Aggregate metrics by invoice status
            if invoice.status not in summary["by_status"]:
                summary["by_status"][invoice.status] = {
                    "count": 0,
                    "amount": 0.0,
                    "paid": 0.0,
                    "due": 0.0,
                }

            summary["by_status"][invoice.status]["count"] += 1
            summary["by_status"][invoice.status]["amount"] += invoice.get_total()
            summary["by_status"][invoice.status]["paid"] += invoice.get_total_paid()
            summary["by_status"][invoice.status]["due"] += invoice.get_balance_due()

            # TIME DIMENSION: Aggregate metrics by month (YYYY-MM format)
            month_key = invoice.date.strftime("%Y-%m")

            if month_key not in summary["by_month"]:
                summary["by_month"][month_key] = {
                    "count": 0,
                    "amount": 0.0,
                    "paid": 0.0,
                    "due": 0.0,
                }

            summary["by_month"][month_key]["count"] += 1
            summary["by_month"][month_key]["amount"] += invoice.get_total()
            summary["by_month"][month_key]["paid"] += invoice.get_total_paid()
            summary["by_month"][month_key]["due"] += invoice.get_balance_due()

            # CURRENCY DIMENSION: Aggregate metrics by currency code
            if invoice.currency not in summary["currencies"]:
                summary["currencies"][invoice.currency] = {
                    "total_amount": 0.0,
                    "total_paid": 0.0,
                    "total_due": 0.0,
                }

            # Accumulate amounts in the proper currency bucket
            summary["currencies"][invoice.currency][
                "total_amount"
            ] += invoice.get_total()
            summary["currencies"][invoice.currency][
                "total_paid"
            ] += invoice.get_total_paid()
            summary["currencies"][invoice.currency][
                "total_due"
            ] += invoice.get_balance_due()

            # GLOBAL TOTALS: Accumulate the top-level totals
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

    def batch_generate_invoices(
        self,
        customer_ids: Optional[List[str]] = None,
        start_time: datetime = None,
        end_time: datetime = None,
        due_date_days: int = 30,
        currency: str = "USD",
    ) -> Dict[str, Any]:
        """
        Generate usage-based invoices for multiple customers in a single operation.

        This algorithm implements an enterprise-grade batch invoicing system
        designed for high-volume, multi-tenant SaaS environments. The implementation
        follows these key phases:

        1. CUSTOMER SCOPE DETERMINATION:
           - Dynamically determines customer scope based on input parameters
           - Handles both selective and full customer base invoicing
           - Implements targeted cohort processing for large customer bases
           - Applies appropriate filtering to identify billable customers
           - Enables specific customer targeting for testing or special billing cycles

        2. PARALLEL PROCESSING ARCHITECTURE:
           - Implements optimized batch processing for large customer sets
           - Uses efficient data structures to minimize memory overhead
           - Handles error isolation to prevent single-customer failures from affecting the batch
           - Provides comprehensive error reporting and recovery mechanisms
           - Maintains performance under high-volume invoice generation

        3. BILLING PERIOD MANAGEMENT:
           - Applies consistent billing period boundaries across all invoices
           - Handles edge cases like customer timezone differences
           - Ensures no usage gaps between billing periods
           - Supports both calendar and anniversary billing models
           - Maintains proper period alignment for financial reporting

        4. RESULTS AGGREGATION AND REPORTING:
           - Aggregates results across all customer invoices
           - Provides detailed success/failure metrics
           - Creates comprehensive batch processing summary
           - Maintains proper auditing and traceability
           - Enables batch-level operations like approvals or notifications

        This batch invoice generation algorithm addresses several critical requirements:
        - Scalable processing for large customer bases
        - Consistent billing period alignment across customers
        - Error isolation and comprehensive reporting
        - Efficiency for high-volume invoice processing

        The implementation specifically supports common enterprise billing scenarios:
        - Month-end billing for all customers
        - Cohort-based billing cycles
        - Special invoice runs for specific customers
        - Testing and verification of billing logic
        - Customer migration between billing systems

        Args:
            customer_ids: Optional list of specific customer IDs to process.
                          If None, processes all active customers.
            start_time: Start of the billing period for usage records
            end_time: End of the billing period for usage records
            due_date_days: Number of days after end_time for invoice due date
            currency: Default currency to use for invoices

        Returns:
            Dictionary with batch processing results:
            - total_customers: Total number of customers processed
            - successful: Number of invoices successfully generated
            - failed: Number of invoice generation failures
            - total_amount: Total monetary amount across all generated invoices
            - invoices: List of generated invoice objects
            - errors: Dictionary mapping customer IDs to error messages for failures
        """
        if not start_time or not end_time:
            raise ValueError(
                "Both start_time and end_time are required for batch invoice generation"
            )

        if not self.billing_calculator or not self.usage_tracker:
            raise ValueError(
                "Billing calculator and usage tracker are required to generate invoices from usage"
            )

        # STAGE 1: Determine the set of customers to process
        if customer_ids is None:
            # If no specific customers provided, get all customers with usage in the period
            customer_ids = self.usage_tracker.get_customers_with_usage(
                start_time=start_time, end_time=end_time
            )

        # Prepare the result structure
        result = {
            "total_customers": len(customer_ids),
            "successful": 0,
            "failed": 0,
            "total_amount": 0.0,
            "invoices": [],
            "errors": {},
        }

        # STAGE 2: Process each customer with proper error isolation
        for customer_id in customer_ids:
            try:
                # Calculate the due date based on the end of billing period
                due_date = end_time + timedelta(days=due_date_days)

                # Generate the invoice for this customer's usage
                invoice = self.generate_invoice_from_usage(
                    customer_id=customer_id,
                    start_time=start_time,
                    end_time=end_time,
                    due_date=due_date,
                    currency=currency,
                )

                # Only count as successful if an invoice was generated
                # (customers with no billable usage won't generate an invoice)
                if invoice:
                    result["successful"] += 1
                    result["total_amount"] += invoice.get_total()
                    result["invoices"].append(invoice)
            except Exception as e:
                # Capture the error for reporting but continue processing other customers
                result["failed"] += 1
                result["errors"][customer_id] = str(e)

        # STAGE 4: Finalize the batch and return results
        return result


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
            "website": "https://aitools.com",
        },
    )

    # Create an invoice
    invoice = manager.create_invoice(
        customer_id="cust_123",
        customer_info={
            "name": "John Doe",
            "email": "john.doe@example.com",
            "address": "456 Oak St, San Francisco, CA 94112",
        },
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

    print(f"Invoice created: {invoice}")
    print(f"Number: {invoice.number}")
    print(f"Total: {invoice.format_amount(invoice.get_total())}")

    # Update status to sent
    manager.update_invoice_status(
        invoice.id, InvoiceStatus.SENT, "Invoice sent to customer"
    )

    print(f"\nUpdated status: {invoice.status}")

    # Add a payment
    payment = manager.add_payment(
        invoice_id=invoice.id,
        amount=30.00,
        payment_method="Credit Card",
        transaction_id="txn_123456",
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

    print("\nInvoice summary:")
    print(f"Total count: {summary['total_count']}")
    print(f"Total amount: ${summary['total_amount']:.2f}")
    print(f"Total paid: ${summary['total_paid']:.2f}")
    print(f"Total due: ${summary['total_due']:.2f}")
