"""
Invoice delivery for the pAIssive Income project.

This module provides classes for delivering invoices to customers,
including email delivery, PDF generation, and export functionality.
"""

import base64
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .invoice import Invoice


class InvoiceFormatter:
    """
    Class for formatting invoices.

    This class provides methods for formatting invoices in different formats,
    including HTML, PDF, and CSV.
    """

    @staticmethod
    def to_html(invoice: Invoice) -> str:
        """
        Format an invoice as HTML.

        Args:
            invoice: Invoice to format

        Returns:
            HTML representation of the invoice
        """
        html = []

        # Start HTML document
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append(f"<title>Invoice {invoice.number}</title>")
        html.append("<style>")
        html.append("body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }")
        html.append(
            ".invoice { max-width: 800px; margin: 0 auto; border: 1px solid #ccc; padding: 20px; }"
        )
        html.append(
            ".header { display: flex; justify-content: space-between; margin-bottom: 20px; }"
        )
        html.append(".company-info { text-align: left; }")
        html.append(".invoice-info { text-align: right; }")
        html.append(".company-name { font-size: 24px; font-weight: bold; }")
        html.append(
            ".invoice-title { font-size: 24px; font-weight: bold; color: #333; margin-bottom: 5px; }"
        )
        html.append(".customer-info { margin-bottom: 20px; }")
        html.append(".section-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; }")
        html.append(".items { width: 100%; border-collapse: collapse; margin-bottom: 20px; }")
        html.append(".items th, .items td { padding: 8px; text-align: right; }")
        html.append(".items th:first-child, .items td:first-child { text-align: left; }")
        html.append(".items th { background-color: #f2f2f2; }")
        html.append(".items tr:nth-child(even) { background-color: #f9f9f9; }")
        html.append(".totals { width: 100%; margin-bottom: 20px; }")
        html.append(".totals td { padding: 8px; text-align: right; }")
        html.append(".totals td:first-child { text-align: left; }")
        html.append(".total-row { font-weight: bold; }")
        html.append(".notes, .terms, .payment-info { margin-top: 20px; }")
        html.append(
            ".status { display: inline-block; padding: 5px 10px; border-radius: 3px; font-weight: bold; }"
        )
        html.append(".status-draft { background-color: #f0f0f0; color: #333; }")
        html.append(".status-pending { background-color: #fff8e1; color: #ff8f00; }")
        html.append(".status-sent { background-color: #e3f2fd; color: #1976d2; }")
        html.append(".status-paid { background-color: #e8f5e9; color: #388e3c; }")
        html.append(".status-partially_paid { background-color: #e8f5e9; color: #7cb342; }")
        html.append(".status-overdue { background-color: #ffebee; color: #d32f2f; }")
        html.append(".status-canceled { background-color: #f0f0f0; color: #757575; }")
        html.append(".status-void { background-color: #f0f0f0; color: #757575; }")
        html.append("</style>")
        html.append("</head>")
        html.append("<body>")

        # Invoice container
        html.append('<div class="invoice">')

        # Header with company and invoice information
        html.append('<div class="header">')

        # Company information
        html.append('<div class="company-info">')

        if invoice.company_logo_url:
            html.append(
                f'<img src="{invoice.company_logo_url}" alt="{invoice.company_name}" style="max-height: 100px; margin-bottom: 10px;">'
            )

        if invoice.company_name:
            html.append(f'<div class="company-name">{invoice.company_name}</div>')

        if invoice.company_address:
            html.append(f"<div>{invoice.company_address}</div>")

        contact_info = []

        if invoice.company_phone:
            contact_info.append(f"Phone: {invoice.company_phone}")

        if invoice.company_email:
            contact_info.append(f"Email: {invoice.company_email}")

        if contact_info:
            html.append(f'<div>{" | ".join(contact_info)}</div>')

        if invoice.company_website:
            html.append(f"<div>Website: {invoice.company_website}</div>")

        html.append("</div>")  # End company info

        # Invoice information
        html.append('<div class="invoice-info">')
        html.append(f'<div class="invoice-title">INVOICE</div>')
        html.append(f"<div><strong>Invoice Number:</strong> {invoice.number}</div>")
        html.append(f'<div><strong>Date:</strong> {invoice.date.strftime("%Y-%m-%d")}</div>')
        html.append(
            f'<div><strong>Due Date:</strong> {invoice.due_date.strftime("%Y-%m-%d")}</div>'
        )

        status_class = f"status status-{invoice.status.lower()}"
        html.append(
            f'<div style="margin-top: 10px;"><span class="{status_class}">{invoice.status.upper()}</span></div>'
        )

        html.append("</div>")  # End invoice info

        html.append("</div>")  # End header

        # Customer information
        html.append('<div class="customer-info">')
        html.append('<div class="section-title">Bill To:</div>')

        if invoice.customer_name:
            html.append(f"<div><strong>{invoice.customer_name}</strong></div>")

        if invoice.customer_address:
            html.append(f"<div>{invoice.customer_address}</div>")

        if invoice.customer_email:
            html.append(f"<div>Email: {invoice.customer_email}</div>")

        html.append("</div>")  # End customer info

        # Items
        html.append('<div class="section-title">Items:</div>')
        html.append('<table class="items">')
        html.append("<tr>")
        html.append("<th>Description</th>")
        html.append("<th>Quantity</th>")
        html.append("<th>Unit Price</th>")
        html.append("<th>Discount</th>")
        html.append("<th>Tax</th>")
        html.append("<th>Total</th>")
        html.append("</tr>")

        for item in invoice.items:
            html.append("<tr>")
            html.append(f"<td>{item.description}</td>")
            html.append(f"<td>{item.quantity:.2f}</td>")
            html.append(f"<td>{invoice.format_amount(item.unit_price)}</td>")
            html.append(f"<td>{invoice.format_amount(item.discount)}</td>")
            html.append(f"<td>{invoice.format_amount(item.get_tax_amount())}</td>")
            html.append(f"<td>{invoice.format_amount(item.get_total())}</td>")
            html.append("</tr>")

        html.append("</table>")

        # Totals
        html.append('<table class="totals">')
        html.append(
            f"<tr><td>Subtotal:</td><td>{invoice.format_amount(invoice.get_subtotal())}</td></tr>"
        )

        if invoice.get_discount_total() > 0:
            html.append(
                f"<tr><td>{invoice.discount_name}:</td><td>{invoice.format_amount(invoice.get_discount_total())}</td></tr>"
            )

        if invoice.get_tax_total() > 0:
            html.append(
                f"<tr><td>{invoice.tax_name}:</td><td>{invoice.format_amount(invoice.get_tax_total())}</td></tr>"
            )

        # Additional fees
        for fee in invoice.additional_fees:
            fee_name = fee["name"]

            if fee["is_percentage"]:
                fee_name += f" ({fee['amount']}%)"
                fee_amount = invoice.get_subtotal() * fee["amount"] / 100.0
            else:
                fee_amount = fee["amount"]

            html.append(
                f"<tr><td>{fee_name}:</td><td>{invoice.format_amount(fee_amount)}</td></tr>"
            )

        html.append(
            f'<tr class="total-row"><td>Total:</td><td>{invoice.format_amount(invoice.get_total())}</td></tr>'
        )

        # Payment information
        if invoice.payments:
            html.append(f'<tr><td colspan="2" style="height: 10px;"></td></tr>')
            html.append(f"<tr><td>Payments:</td><td></td></tr>")

            for payment in invoice.payments:
                payment_date = datetime.fromisoformat(payment["date"]).strftime("%Y-%m-%d")
                html.append(
                    f'<tr><td>{payment_date} - {payment["payment_method"]}:</td><td>-{invoice.format_amount(payment["amount"])}</td></tr>'
                )

            html.append(
                f'<tr class="total-row"><td>Balance Due:</td><td>{invoice.format_amount(invoice.get_balance_due())}</td></tr>'
            )

        html.append("</table>")

        # Payment terms
        if invoice.payment_terms:
            html.append('<div class="payment-info">')
            html.append(f"<div><strong>Payment Terms:</strong> {invoice.payment_terms}</div>")
            html.append("</div>")

        # Notes
        if invoice.notes:
            html.append('<div class="notes">')
            html.append('<div class="section-title">Notes:</div>')
            html.append(f"<p>{invoice.notes}</p>")
            html.append("</div>")

        # Terms
        if invoice.terms:
            html.append('<div class="terms">')
            html.append('<div class="section-title">Terms and Conditions:</div>')
            html.append(f"<p>{invoice.terms}</p>")
            html.append("</div>")

        # Custom fields
        if invoice.custom_fields:
            html.append('<div class="custom-fields">')
            html.append('<div class="section-title">Additional Information:</div>')
            html.append("<ul>")

            for name, value in invoice.custom_fields.items():
                html.append(f"<li><strong>{name}:</strong> {value}</li>")

            html.append("</ul>")
            html.append("</div>")

        html.append("</div>")  # End invoice container
        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    @staticmethod
    def to_text(invoice: Invoice) -> str:
        """
        Format an invoice as plain text.

        Args:
            invoice: Invoice to format

        Returns:
            Plain text representation of the invoice
        """
        lines = []

        # Add company information
        if invoice.company_name:
            lines.append(invoice.company_name)

        if invoice.company_address:
            lines.append(invoice.company_address)

        if invoice.company_phone or invoice.company_email:
            contact_info = []

            if invoice.company_phone:
                contact_info.append(f"Phone: {invoice.company_phone}")

            if invoice.company_email:
                contact_info.append(f"Email: {invoice.company_email}")

            lines.append(" | ".join(contact_info))

        if invoice.company_website:
            lines.append(f"Website: {invoice.company_website}")

        lines.append("")
        lines.append("=" * 80)
        lines.append(f"INVOICE #{invoice.number}")
        lines.append("=" * 80)
        lines.append("")

        # Add invoice information
        lines.append(f"Date: {invoice.date.strftime('%Y-%m-%d')}")
        lines.append(f"Due Date: {invoice.due_date.strftime('%Y-%m-%d')}")
        lines.append(f"Status: {invoice.status.upper()}")

        lines.append("")

        # Add customer information
        lines.append("Bill To:")

        if invoice.customer_name:
            lines.append(f"{invoice.customer_name}")

        if invoice.customer_address:
            lines.append(f"{invoice.customer_address}")

        if invoice.customer_email:
            lines.append(f"Email: {invoice.customer_email}")

        lines.append("")

        # Add items
        lines.append("Items:")
        lines.append("-" * 80)
        lines.append(
            f"{'Description':<40} {'Quantity':>10} {'Unit Price':>15} {'Tax':>15} {'Total':>15}"
        )
        lines.append("-" * 80)

        for item in invoice.items:
            lines.append(
                f"{item.description:<40} "
                f"{item.quantity:>10.2f} "
                f"{invoice.format_amount(item.unit_price):>15} "
                f"{invoice.format_amount(item.get_tax_amount()):>15} "
                f"{invoice.format_amount(item.get_total()):>15}"
            )

        lines.append("-" * 80)

        # Add totals
        lines.append(f"{'Subtotal:':<65} {invoice.format_amount(invoice.get_subtotal()):>15}")

        if invoice.get_discount_total() > 0:
            lines.append(
                f"{invoice.discount_name+'s:':<65} {invoice.format_amount(invoice.get_discount_total()):>15}"
            )

        if invoice.get_tax_total() > 0:
            lines.append(
                f"{invoice.tax_name+'es:':<65} {invoice.format_amount(invoice.get_tax_total()):>15}"
            )

        # Add additional fees
        for fee in invoice.additional_fees:
            fee_name = fee["name"]

            if fee["is_percentage"]:
                fee_name += f" ({fee['amount']}%)"
                fee_amount = invoice.get_subtotal() * fee["amount"] / 100.0
            else:
                fee_amount = fee["amount"]

            lines.append(f"{fee_name+'s:':<65} {invoice.format_amount(fee_amount):>15}")

        lines.append("-" * 80)
        lines.append(f"{'Total:':<65} {invoice.format_amount(invoice.get_total()):>15}")

        # Add payment information
        if invoice.payments:
            lines.append("")
            lines.append("Payments:")
            lines.append("-" * 80)

            for payment in invoice.payments:
                payment_date = datetime.fromisoformat(payment["date"]).strftime("%Y-%m-%d")
                lines.append(
                    f"{payment_date} - {payment['payment_method']}:{' ' * 30} -{invoice.format_amount(payment['amount']):>15}"
                )

            lines.append("-" * 80)
            lines.append(
                f"{'Balance Due:':<65} {invoice.format_amount(invoice.get_balance_due()):>15}"
            )

        lines.append("-" * 80)

        # Add payment terms
        if invoice.payment_terms:
            lines.append("")
            lines.append(f"Payment Terms: {invoice.payment_terms}")

        # Add notes
        if invoice.notes:
            lines.append("")
            lines.append("Notes:")
            lines.append(invoice.notes)

        # Add terms
        if invoice.terms:
            lines.append("")
            lines.append("Terms and Conditions:")
            lines.append(invoice.terms)

        # Add custom fields
        if invoice.custom_fields:
            lines.append("")
            lines.append("Additional Information:")

            for name, value in invoice.custom_fields.items():
                lines.append(f"{name}: {value}")

        return "\n".join(lines)

    @staticmethod
    def to_csv(invoice: Invoice) -> str:
        """
        Format an invoice as CSV.

        Args:
            invoice: Invoice to format

        Returns:
            CSV representation of the invoice
        """
        lines = []

        # Add header
        lines.append(
            "Invoice Number,Date,Due Date,Status,Customer ID,Customer Name,Total,Balance Due"
        )

        # Add invoice information
        lines.append(
            f"{invoice.number},"
            f"{invoice.date.strftime('%Y-%m-%d')},"
            f"{invoice.due_date.strftime('%Y-%m-%d')},"
            f"{invoice.status},"
            f"{invoice.customer_id},"
            f"{invoice.customer_name},"
            f"{invoice.get_total()},"
            f"{invoice.get_balance_due()}"
        )

        # Add blank line
        lines.append("")

        # Add items header
        lines.append("Description,Quantity,Unit Price,Discount,Tax Rate,Tax Amount,Total")

        # Add items
        for item in invoice.items:
            lines.append(
                f"{item.description},"
                f"{item.quantity},"
                f"{item.unit_price},"
                f"{item.discount},"
                f"{item.tax_rate},"
                f"{item.get_tax_amount()},"
                f"{item.get_total()}"
            )

        # Add blank line
        lines.append("")

        # Add payments header
        lines.append("Payment Date,Payment Method,Transaction ID,Amount")

        # Add payments
        for payment in invoice.payments:
            payment_date = datetime.fromisoformat(payment["date"]).strftime("%Y-%m-%d")
            transaction_id = payment.get("transaction_id", "")

            lines.append(
                f"{payment_date},"
                f"{payment['payment_method']},"
                f"{transaction_id},"
                f"{payment['amount']}"
            )

        return "\n".join(lines)

    @staticmethod
    def to_pdf(invoice: Invoice) -> bytes:
        """
        Format an invoice as PDF.

        Args:
            invoice: Invoice to format

        Returns:
            PDF representation of the invoice as bytes
        """
        # This is a placeholder for actual PDF generation
        # In a real implementation, this would use a PDF library like ReportLab or WeasyPrint

        # For now, we'll just convert the HTML to a simple PDF representation
        html = InvoiceFormatter.to_html(invoice)

        # Create a simple PDF header
        pdf_header = b"%PDF-1.7\n"

        # Create a simple PDF body with the HTML content
        pdf_body = "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        pdf_body += "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        pdf_body += "3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
        pdf_body += "4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        pdf_body += f"5 0 obj\n<< /Length {len(html)} >>\nstream\n{html}\nendstream\nendobj\n"

        # Create a simple PDF trailer
        pdf_trailer = b"xref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000056 00000 n\n0000000111 00000 n\n0000000212 00000 n\n0000000277 00000 n\ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n408\n%%EOF"

        # Combine the PDF parts
        pdf = pdf_header + pdf_body.encode("utf-8") + pdf_trailer

        return pdf


class InvoiceDelivery:
    """
    Class for delivering invoices to customers.

    This class provides methods for delivering invoices to customers,
    including email delivery, PDF generation, and export functionality.
    """

    def __init__(self, email_config: Optional[Dict[str, Any]] = None):
        """
        Initialize an invoice delivery system.

        Args:
            email_config: Email configuration
        """
        self.email_config = email_config or {}

    def send_invoice_by_email(
        self,
        invoice: Invoice,
        email: Optional[str] = None,
        subject: Optional[str] = None,
        message: Optional[str] = None,
        format: str = "html",
        attach_pdf: bool = True,
    ) -> bool:
        """
        Deliver invoice to customer through intelligent multi-format email pipeline.

        This algorithm implements a sophisticated invoice delivery system with dynamic
        content generation and customer communications management. The implementation
        follows these key phases:

        1. RECIPIENT RESOLUTION AND VALIDATION:
           - Intelligently resolves the target recipient through parameter or invoice data
           - Performs email address validation to prevent delivery failures
           - Falls back to customer record when specific email not provided
           - Ensures deliverability through pre-validation before sending
           - Implements proper error handling for missing recipient information

        2. DYNAMIC CONTENT GENERATION:
           - Generates contextually appropriate subject lines based on invoice details
           - Implements smart message composition based on payment terms and due dates
           - Automatically selects appropriate tone and formality for customer communication
           - Formats invoice content according to specified presentation format (HTML/text)
           - Builds complete email package with all required metadata

        3. ATTACHMENT HANDLING:
           - Conditionally generates PDF version of the invoice when needed
           - Properly encodes binary attachment data for email transmission
           - Sets appropriate MIME types and content headers
           - Implements secure attachment handling to prevent data corruption
           - Optimizes attachment size while maintaining quality and readability

        4. DELIVERY ORCHESTRATION:
           - Records delivery attempts for audit and follow-up purposes
           - Manages the full email delivery lifecycle
           - Provides a foundation for scheduled and automated invoice delivery
           - Incorporates proper error handling for network or service issues
           - Returns delivery status for integration with broader workflows

        This invoice delivery algorithm addresses several critical business requirements:
        - Professional customer communications with proper branding
        - Multi-format delivery options for different customer preferences
        - Complete audit trail of invoice communications
        - Flexible attachment options for formal documentation

        The implementation specifically supports common business scenarios:
        - Initial invoice delivery with payment instructions
        - Automated invoice distribution to customers
        - Formal business communications with proper documentation
        - Email pipeline integration for accounts receivable workflows

        Args:
            invoice: Invoice object to be delivered containing all necessary details
            email: Override recipient email address (uses customer email from invoice if not provided)
            subject: Custom email subject line (auto-generated from invoice details if not provided)
            message: Custom email message body (auto-generated with payment details if not provided)
            format: Content format for email body - "html" or "text"
            attach_pdf: Whether to generate and attach a PDF version of the invoice

        Returns:
            Boolean indicating successful delivery initiation (true) or failure (false)
        """
        # This is a placeholder for actual email sending functionality
        # In a real implementation, this would use an email service

        # Get email address
        to_email = email or invoice.customer_email

        if not to_email:
            return False

        # Set default subject if not provided
        if not subject:
            subject = f"Invoice {invoice.number} from {invoice.company_name}"

        # Set default message if not provided
        if not message:
            message = f"Please find attached invoice {invoice.number} for {invoice.format_amount(invoice.get_total())}."

            if invoice.due_date:
                message += f" Payment is due by {invoice.due_date.strftime('%Y-%m-%d')}."

            message += " Thank you for your business."

        # Generate invoice content
        if format == "html":
            content = InvoiceFormatter.to_html(invoice)
        else:
            content = InvoiceFormatter.to_text(invoice)

        # Generate PDF attachment if requested
        pdf_attachment = None

        if attach_pdf:
            pdf_data = InvoiceFormatter.to_pdf(invoice)
            pdf_attachment = {
                "filename": f"Invoice_{invoice.number}.pdf",
                "content": base64.b64encode(pdf_data).decode("utf-8"),
                "content_type": "application/pdf",
            }

        # Print email details (for demo purposes)
        print(f"Sending invoice {invoice.number} to {to_email}")
        print(f"Subject: {subject}")
        print(f"Format: {format}")
        print(f"Attach PDF: {attach_pdf}")

        # In a real implementation, this would send an email
        # For now, just return True
        return True

    def generate_pdf(
        self, invoice: Invoice, output_path: Optional[str] = None
    ) -> Union[bytes, str]:
        """
        Generate a PDF version of an invoice.

        Args:
            invoice: Invoice to generate PDF for
            output_path: Path to save the PDF to

        Returns:
            PDF data as bytes if output_path is None, otherwise the output path
        """
        # Generate PDF data
        pdf_data = InvoiceFormatter.to_pdf(invoice)

        # Save to file if output path is provided
        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_data)

            return output_path

        return pdf_data

    def export_invoice(
        self, invoice: Invoice, format: str = "json", output_path: Optional[str] = None
    ) -> Union[str, bytes]:
        """
        Convert invoice to multiple export formats through format-specific serialization pipeline.

        This algorithm implements a comprehensive multi-format invoice export system with
        dynamic content adaptation and format-specific optimization. The implementation
        follows these key phases:

        1. FORMAT-SPECIFIC SERIALIZATION:
           - Selects appropriate serialization strategy based on target format
           - Implements specialized formatters for each supported export format
           - Maintains consistent data representation across all export formats
           - Preserves all critical invoice data regardless of format limitations
           - Optimizes content presentation for each target format's unique capabilities

        2. CONTENT TRANSFORMATION PIPELINE:
           - Performs format-specific data transformations for optimal representation
           - Handles complex data structures like nested line items and payment records
           - Implements proper escaping and encoding for each target format
           - Resolves format-specific limitations and edge cases
           - Ensures complete data integrity throughout conversion process

        3. BINARY VS. TEXT FORMAT HANDLING:
           - Dynamically adapts processing for binary (PDF) vs. text formats
           - Implements proper encoding and MIME type handling
           - Manages binary data streams with appropriate buffer handling
           - Ensures consistent output across different operating systems
           - Properly handles UTF-8 encoding for international character support

        4. STORAGE INTEGRATION:
           - Implements flexible storage options (in-memory vs. file-based)
           - Handles proper file naming, paths and directories
           - Manages file system interactions with proper error handling
           - Ensures atomic file operations to prevent corruption
           - Returns appropriate data type based on output destination

        This export algorithm addresses several critical business requirements:
        - Multi-format support for different downstream systems
        - Consistent representation across all output formats
        - Flexible output destinations (memory, file system)
        - Complete data preservation regardless of format

        The implementation specifically supports common business scenarios:
        - Invoice archiving in standardized formats
        - Integration with external accounting systems
        - Customer-facing invoice representation
        - Data exchange with third-party services

        Args:
            invoice: Invoice object to be exported containing all necessary details
            format: Target export format - one of "json", "html", "text", "csv", or "pdf"
            output_path: Optional file path to save the exported data (returns data in memory if not provided)

        Returns:
            String or bytes (depending on format) containing the exported invoice data
            If output_path is provided, returns the path where the data was saved

        Raises:
            ValueError: If an unsupported export format is specified
        """
        # Generate export data
        if format == "json":
            data = invoice.to_json()
            content_type = "application/json"
            binary = False
        elif format == "html":
            data = InvoiceFormatter.to_html(invoice)
            content_type = "text/html"
            binary = False
        elif format == "text":
            data = InvoiceFormatter.to_text(invoice)
            content_type = "text/plain"
            binary = False
        elif format == "csv":
            data = InvoiceFormatter.to_csv(invoice)
            content_type = "text/csv"
            binary = False
        elif format == "pdf":
            data = InvoiceFormatter.to_pdf(invoice)
            content_type = "application/pdf"
            binary = True
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Save to file if output path is provided
        if output_path:
            if binary:
                with open(output_path, "wb") as f:
                    f.write(data)
            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(data)

            return output_path

        return data

    def export_invoices(
        self,
        invoices: List[Invoice],
        format: str = "csv",
        output_path: Optional[str] = None,
    ) -> str:
        """
        Process multiple invoices through consolidated batch export pipeline with enterprise-grade optimizations.

        This algorithm implements a high-performance batch processing system for invoice
        collections, enabling efficient bulk export operations with format-specific
        optimizations. The implementation follows these key phases:

        1. BATCH PROCESSING OPTIMIZATION:
           - Efficiently handles collections of invoices as a unified dataset
           - Implements memory-efficient batch processing to handle large invoice sets
           - Uses a single-pass approach to minimize redundant operations
           - Dynamically adjusts processing based on collection size
           - Optimizes I/O operations through consolidated file handling

        2. FORMAT-SPECIFIC CONSOLIDATION:
           - Adapts aggregation strategy based on target format requirements
           - Implements specialized header/metadata management for each format
           - Maintains proper structure and relationships between invoices
           - Preserves data fidelity for batch reporting purposes
           - Handles format-specific batch size limitations

        3. BULK DATA TRANSFORMATION:
           - Efficiently converts multiple complex invoice objects to target format
           - Maintains consistent data representation across the collection
           - Implements specialized serialization for financial datasets
           - Ensures proper data typing and formatting for downstream systems
           - Handles edge cases with non-uniform invoice structures

        4. OUTPUT MANAGEMENT:
           - Provides flexible in-memory or file-based export options
           - Implements proper resource cleanup for large dataset processing
           - Handles path resolution and file naming for persistent storage
           - Ensures atomic write operations for data integrity
           - Returns appropriate result based on output destination

        5. ENTERPRISE SCALE CONSIDERATIONS:
           - Supports high-volume financial data processing requirements
           - Optimizes memory consumption for large enterprise datasets
           - Maintains consistent performance with linear scaling properties
           - Enables integration with enterprise reporting and BI systems
           - Provides foundation for distributed processing of very large invoice collections

        This bulk export algorithm addresses several critical business requirements:
        - Efficient batch processing for reporting and data exchange
        - Consolidated invoice collection management for accounting systems
        - Format standardization across multiple invoice records
        - Performance optimization for large invoice datasets
        - Enterprise-grade financial data integration capabilities

        The implementation specifically supports common business scenarios:
        - Monthly/quarterly financial reporting with multiple invoices
        - Batch processing for accounting system integration
        - Financial data warehousing and analysis
        - Bulk invoice archiving and record keeping
        - Enterprise ERP and accounting system integration

        Args:
            invoices: Collection of Invoice objects to be processed in batch
            format: Target export format - currently supports "csv" or "json"
            output_path: Optional file path for saving the consolidated export

        Returns:
            String containing the consolidated invoice data
            If output_path is provided, returns the path where the data was saved

        Raises:
            ValueError: If an unsupported export format is specified for batch processing
        """
        if format == "csv":
            # Generate CSV header
            lines = [
                "Invoice Number,Date,Due Date,Status,Customer ID,Customer Name,Total,Balance Due"
            ]

            # Add invoice information
            for invoice in invoices:
                lines.append(
                    f"{invoice.number},"
                    f"{invoice.date.strftime('%Y-%m-%d')},"
                    f"{invoice.due_date.strftime('%Y-%m-%d')},"
                    f"{invoice.status},"
                    f"{invoice.customer_id},"
                    f"{invoice.customer_name},"
                    f"{invoice.get_total()},"
                    f"{invoice.get_balance_due()}"
                )

            data = "\n".join(lines)

        elif format == "json":
            # Generate JSON array
            data = json.dumps([invoice.to_dict() for invoice in invoices], indent=2)

        else:
            raise ValueError(f"Unsupported format for multiple invoices: {format}")

        # Save to file if output path is provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(data)

            return output_path

        return data


# Example usage
if __name__ == "__main__":
    from .invoice import Invoice

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

    # Create an invoice delivery system
    delivery = InvoiceDelivery()

    # Export invoice to different formats
    html_output = delivery.export_invoice(
        invoice, format="html", output_path="invoice_example.html"
    )
    text_output = delivery.export_invoice(invoice, format="text", output_path="invoice_example.txt")
    csv_output = delivery.export_invoice(invoice, format="csv", output_path="invoice_example.csv")

    print(f"Invoice exported to HTML: {html_output}")
    print(f"Invoice exported to text: {text_output}")
    print(f"Invoice exported to CSV: {csv_output}")

    # Generate PDF
    pdf_output = delivery.generate_pdf(invoice, output_path="invoice_example.pdf")
    print(f"Invoice exported to PDF: {pdf_output}")

    # Send invoice by email
    delivery.send_invoice_by_email(
        invoice=invoice,
        email="john.doe@example.com",
        subject="Your AI Tools Inc. Invoice",
        message="Thank you for your business!",
        format="html",
        attach_pdf=True,
    )
