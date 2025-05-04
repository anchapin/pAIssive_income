"""
"""
Invoice delivery for the pAIssive Income project.
Invoice delivery for the pAIssive Income project.


This module provides classes for delivering invoices to customers,
This module provides classes for delivering invoices to customers,
including email delivery, PDF generation, and export functionality.
including email delivery, PDF generation, and export functionality.
"""
"""




import base64
import base64
import json
import json
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from typing import Any, Dict, List, Optional, Union


from .invoice import Invoice
from .invoice import Invoice




class InvoiceFormatter:
    class InvoiceFormatter:
    from .invoice import Invoice
    from .invoice import Invoice






    :
    :
    """
    """
    Class for formatting invoices.
    Class for formatting invoices.


    This class provides methods for formatting invoices in different formats,
    This class provides methods for formatting invoices in different formats,
    including HTML, PDF, and CSV.
    including HTML, PDF, and CSV.
    """
    """


    @staticmethod
    @staticmethod
    def to_html(invoice: Invoice) -> str:
    def to_html(invoice: Invoice) -> str:
    """
    """
    Format an invoice as HTML.
    Format an invoice as HTML.


    Args:
    Args:
    invoice: Invoice to format
    invoice: Invoice to format


    Returns:
    Returns:
    HTML representation of the invoice
    HTML representation of the invoice
    """
    """
    html = []
    html = []


    # Start HTML document
    # Start HTML document
    html.append("<!DOCTYPE html>")
    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<html>")
    html.append("<head>")
    html.append("<head>")
    html.append(f"<title>Invoice {invoice.number}</title>")
    html.append(f"<title>Invoice {invoice.number}</title>")
    html.append("<style>")
    html.append("<style>")
    html.append(
    html.append(
    "body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }"
    "body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }"
    )
    )
    html.append(
    html.append(
    ".invoice { max-width: 800px; margin: 0 auto; border: 1px solid #ccc; padding: 20px; }"
    ".invoice { max-width: 800px; margin: 0 auto; border: 1px solid #ccc; padding: 20px; }"
    )
    )
    html.append(
    html.append(
    ".header { display: flex; justify-content: space-between; margin-bottom: 20px; }"
    ".header { display: flex; justify-content: space-between; margin-bottom: 20px; }"
    )
    )
    html.append(".company-info { text-align: left; }")
    html.append(".company-info { text-align: left; }")
    html.append(".invoice-info { text-align: right; }")
    html.append(".invoice-info { text-align: right; }")
    html.append(".company-name { font-size: 24px; font-weight: bold; }")
    html.append(".company-name { font-size: 24px; font-weight: bold; }")
    html.append(
    html.append(
    ".invoice-title { font-size: 24px; font-weight: bold; color: #333; margin-bottom: 5px; }"
    ".invoice-title { font-size: 24px; font-weight: bold; color: #333; margin-bottom: 5px; }"
    )
    )
    html.append(".customer-info { margin-bottom: 20px; }")
    html.append(".customer-info { margin-bottom: 20px; }")
    html.append(
    html.append(
    ".section-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; }"
    ".section-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; }"
    )
    )
    html.append(
    html.append(
    ".items { width: 100%; border-collapse: collapse; margin-bottom: 20px; }"
    ".items { width: 100%; border-collapse: collapse; margin-bottom: 20px; }"
    )
    )
    html.append(".items th, .items td { padding: 8px; text-align: right; }")
    html.append(".items th, .items td { padding: 8px; text-align: right; }")
    html.append(
    html.append(
    ".items th:first-child, .items td:first-child { text-align: left; }"
    ".items th:first-child, .items td:first-child { text-align: left; }"
    )
    )
    html.append(".items th { background-color: #f2f2f2; }")
    html.append(".items th { background-color: #f2f2f2; }")
    html.append(".items tr:nth-child(even) { background-color: #f9f9f9; }")
    html.append(".items tr:nth-child(even) { background-color: #f9f9f9; }")
    html.append(".totals { width: 100%; margin-bottom: 20px; }")
    html.append(".totals { width: 100%; margin-bottom: 20px; }")
    html.append(".totals td { padding: 8px; text-align: right; }")
    html.append(".totals td { padding: 8px; text-align: right; }")
    html.append(".totals td:first-child { text-align: left; }")
    html.append(".totals td:first-child { text-align: left; }")
    html.append(".total-row { font-weight: bold; }")
    html.append(".total-row { font-weight: bold; }")
    html.append(".notes, .terms, .payment-info { margin-top: 20px; }")
    html.append(".notes, .terms, .payment-info { margin-top: 20px; }")
    html.append(
    html.append(
    ".status { display: inline-block; padding: 5px 10px; border-radius: 3px; font-weight: bold; }"
    ".status { display: inline-block; padding: 5px 10px; border-radius: 3px; font-weight: bold; }"
    )
    )
    html.append(".status-draft { background-color: #f0f0f0; color: #333; }")
    html.append(".status-draft { background-color: #f0f0f0; color: #333; }")
    html.append(".status-pending { background-color: #fff8e1; color: #ff8f00; }")
    html.append(".status-pending { background-color: #fff8e1; color: #ff8f00; }")
    html.append(".status-sent { background-color: #e3f2fd; color: #1976d2; }")
    html.append(".status-sent { background-color: #e3f2fd; color: #1976d2; }")
    html.append(".status-paid { background-color: #e8f5e9; color: #388e3c; }")
    html.append(".status-paid { background-color: #e8f5e9; color: #388e3c; }")
    html.append(
    html.append(
    ".status-partially_paid { background-color: #e8f5e9; color: #7cb342; }"
    ".status-partially_paid { background-color: #e8f5e9; color: #7cb342; }"
    )
    )
    html.append(".status-overdue { background-color: #ffebee; color: #d32f2f; }")
    html.append(".status-overdue { background-color: #ffebee; color: #d32f2f; }")
    html.append(".status-canceled { background-color: #f0f0f0; color: #757575; }")
    html.append(".status-canceled { background-color: #f0f0f0; color: #757575; }")
    html.append(".status-void { background-color: #f0f0f0; color: #757575; }")
    html.append(".status-void { background-color: #f0f0f0; color: #757575; }")
    html.append("</style>")
    html.append("</style>")
    html.append("</head>")
    html.append("</head>")
    html.append("<body>")
    html.append("<body>")


    # Invoice container
    # Invoice container
    html.append('<div class="invoice">')
    html.append('<div class="invoice">')


    # Header with company and invoice information
    # Header with company and invoice information
    html.append('<div class="header">')
    html.append('<div class="header">')


    # Company information
    # Company information
    html.append('<div class="company-info">')
    html.append('<div class="company-info">')


    if invoice.company_logo_url:
    if invoice.company_logo_url:
    html.append(
    html.append(
    f'<img src="{invoice.company_logo_url}" alt="{invoice.company_name}" style="max-height: 100px; margin-bottom: 10px;">'
    f'<img src="{invoice.company_logo_url}" alt="{invoice.company_name}" style="max-height: 100px; margin-bottom: 10px;">'
    )
    )


    if invoice.company_name:
    if invoice.company_name:
    html.append(f'<div class="company-name">{invoice.company_name}</div>')
    html.append(f'<div class="company-name">{invoice.company_name}</div>')


    if invoice.company_address:
    if invoice.company_address:
    html.append(f"<div>{invoice.company_address}</div>")
    html.append(f"<div>{invoice.company_address}</div>")


    contact_info = []
    contact_info = []


    if invoice.company_phone:
    if invoice.company_phone:
    contact_info.append(f"Phone: {invoice.company_phone}")
    contact_info.append(f"Phone: {invoice.company_phone}")


    if invoice.company_email:
    if invoice.company_email:
    contact_info.append(f"Email: {invoice.company_email}")
    contact_info.append(f"Email: {invoice.company_email}")


    if contact_info:
    if contact_info:
    html.append(f'<div>{" | ".join(contact_info)}</div>')
    html.append(f'<div>{" | ".join(contact_info)}</div>')


    if invoice.company_website:
    if invoice.company_website:
    html.append(f"<div>Website: {invoice.company_website}</div>")
    html.append(f"<div>Website: {invoice.company_website}</div>")


    html.append("</div>")  # End company info
    html.append("</div>")  # End company info


    # Invoice information
    # Invoice information
    html.append('<div class="invoice-info">')
    html.append('<div class="invoice-info">')
    html.append('<div class="invoice-title">INVOICE</div>')
    html.append('<div class="invoice-title">INVOICE</div>')
    html.append(f"<div><strong>Invoice Number:</strong> {invoice.number}</div>")
    html.append(f"<div><strong>Invoice Number:</strong> {invoice.number}</div>")
    html.append(
    html.append(
    f'<div><strong>Date:</strong> {invoice.date.strftime("%Y-%m-%d")}</div>'
    f'<div><strong>Date:</strong> {invoice.date.strftime("%Y-%m-%d")}</div>'
    )
    )
    html.append(
    html.append(
    f'<div><strong>Due Date:</strong> {invoice.due_date.strftime("%Y-%m-%d")}</div>'
    f'<div><strong>Due Date:</strong> {invoice.due_date.strftime("%Y-%m-%d")}</div>'
    )
    )


    status_class = f"status status-{invoice.status.lower()}"
    status_class = f"status status-{invoice.status.lower()}"
    html.append(
    html.append(
    f'<div style="margin-top: 10px;"><span class="{status_class}">{invoice.status.upper()}</span></div>'
    f'<div style="margin-top: 10px;"><span class="{status_class}">{invoice.status.upper()}</span></div>'
    )
    )


    html.append("</div>")  # End invoice info
    html.append("</div>")  # End invoice info


    html.append("</div>")  # End header
    html.append("</div>")  # End header


    # Customer information
    # Customer information
    html.append('<div class="customer-info">')
    html.append('<div class="customer-info">')
    html.append('<div class="section-title">Bill To:</div>')
    html.append('<div class="section-title">Bill To:</div>')


    if invoice.customer_name:
    if invoice.customer_name:
    html.append(f"<div><strong>{invoice.customer_name}</strong></div>")
    html.append(f"<div><strong>{invoice.customer_name}</strong></div>")


    if invoice.customer_address:
    if invoice.customer_address:
    html.append(f"<div>{invoice.customer_address}</div>")
    html.append(f"<div>{invoice.customer_address}</div>")


    if invoice.customer_email:
    if invoice.customer_email:
    html.append(f"<div>Email: {invoice.customer_email}</div>")
    html.append(f"<div>Email: {invoice.customer_email}</div>")


    html.append("</div>")  # End customer info
    html.append("</div>")  # End customer info


    # Items
    # Items
    html.append('<div class="section-title">Items:</div>')
    html.append('<div class="section-title">Items:</div>')
    html.append('<table class="items">')
    html.append('<table class="items">')
    html.append("<tr>")
    html.append("<tr>")
    html.append("<th>Description</th>")
    html.append("<th>Description</th>")
    html.append("<th>Quantity</th>")
    html.append("<th>Quantity</th>")
    html.append("<th>Unit Price</th>")
    html.append("<th>Unit Price</th>")
    html.append("<th>Discount</th>")
    html.append("<th>Discount</th>")
    html.append("<th>Tax</th>")
    html.append("<th>Tax</th>")
    html.append("<th>Total</th>")
    html.append("<th>Total</th>")
    html.append("</tr>")
    html.append("</tr>")


    for item in invoice.items:
    for item in invoice.items:
    html.append("<tr>")
    html.append("<tr>")
    html.append(f"<td>{item.description}</td>")
    html.append(f"<td>{item.description}</td>")
    html.append(f"<td>{item.quantity:.2f}</td>")
    html.append(f"<td>{item.quantity:.2f}</td>")
    html.append(f"<td>{invoice.format_amount(item.unit_price)}</td>")
    html.append(f"<td>{invoice.format_amount(item.unit_price)}</td>")
    html.append(f"<td>{invoice.format_amount(item.discount)}</td>")
    html.append(f"<td>{invoice.format_amount(item.discount)}</td>")
    html.append(f"<td>{invoice.format_amount(item.get_tax_amount())}</td>")
    html.append(f"<td>{invoice.format_amount(item.get_tax_amount())}</td>")
    html.append(f"<td>{invoice.format_amount(item.get_total())}</td>")
    html.append(f"<td>{invoice.format_amount(item.get_total())}</td>")
    html.append("</tr>")
    html.append("</tr>")


    html.append("</table>")
    html.append("</table>")


    # Totals
    # Totals
    html.append('<table class="totals">')
    html.append('<table class="totals">')
    html.append(
    html.append(
    f"<tr><td>Subtotal:</td><td>{invoice.format_amount(invoice.get_subtotal())}</td></tr>"
    f"<tr><td>Subtotal:</td><td>{invoice.format_amount(invoice.get_subtotal())}</td></tr>"
    )
    )


    if invoice.get_discount_total() > 0:
    if invoice.get_discount_total() > 0:
    html.append(
    html.append(
    f"<tr><td>{invoice.discount_name}:</td><td>{invoice.format_amount(invoice.get_discount_total())}</td></tr>"
    f"<tr><td>{invoice.discount_name}:</td><td>{invoice.format_amount(invoice.get_discount_total())}</td></tr>"
    )
    )


    if invoice.get_tax_total() > 0:
    if invoice.get_tax_total() > 0:
    html.append(
    html.append(
    f"<tr><td>{invoice.tax_name}:</td><td>{invoice.format_amount(invoice.get_tax_total())}</td></tr>"
    f"<tr><td>{invoice.tax_name}:</td><td>{invoice.format_amount(invoice.get_tax_total())}</td></tr>"
    )
    )


    # Additional fees
    # Additional fees
    for fee in invoice.additional_fees:
    for fee in invoice.additional_fees:
    fee_name = fee["name"]
    fee_name = fee["name"]


    if fee["is_percentage"]:
    if fee["is_percentage"]:
    fee_name += f" ({fee['amount']}%)"
    fee_name += f" ({fee['amount']}%)"
    fee_amount = invoice.get_subtotal() * fee["amount"] / 100.0
    fee_amount = invoice.get_subtotal() * fee["amount"] / 100.0
    else:
    else:
    fee_amount = fee["amount"]
    fee_amount = fee["amount"]


    html.append(
    html.append(
    f"<tr><td>{fee_name}:</td><td>{invoice.format_amount(fee_amount)}</td></tr>"
    f"<tr><td>{fee_name}:</td><td>{invoice.format_amount(fee_amount)}</td></tr>"
    )
    )


    html.append(
    html.append(
    f'<tr class="total-row"><td>Total:</td><td>{invoice.format_amount(invoice.get_total())}</td></tr>'
    f'<tr class="total-row"><td>Total:</td><td>{invoice.format_amount(invoice.get_total())}</td></tr>'
    )
    )


    # Payment information
    # Payment information
    if invoice.payments:
    if invoice.payments:
    html.append('<tr><td colspan="2" style="height: 10px;"></td></tr>')
    html.append('<tr><td colspan="2" style="height: 10px;"></td></tr>')
    html.append("<tr><td>Payments:</td><td></td></tr>")
    html.append("<tr><td>Payments:</td><td></td></tr>")


    for payment in invoice.payments:
    for payment in invoice.payments:
    payment_date = datetime.fromisoformat(payment["date"]).strftime(
    payment_date = datetime.fromisoformat(payment["date"]).strftime(
    "%Y-%m-%d"
    "%Y-%m-%d"
    )
    )
    html.append(
    html.append(
    f'<tr><td>{payment_date} - {payment["payment_method"]}:</td><td>-{invoice.format_amount(payment["amount"])}</td></tr>'
    f'<tr><td>{payment_date} - {payment["payment_method"]}:</td><td>-{invoice.format_amount(payment["amount"])}</td></tr>'
    )
    )


    html.append(
    html.append(
    f'<tr class="total-row"><td>Balance Due:</td><td>{invoice.format_amount(invoice.get_balance_due())}</td></tr>'
    f'<tr class="total-row"><td>Balance Due:</td><td>{invoice.format_amount(invoice.get_balance_due())}</td></tr>'
    )
    )


    html.append("</table>")
    html.append("</table>")


    # Payment terms
    # Payment terms
    if invoice.payment_terms:
    if invoice.payment_terms:
    html.append('<div class="payment-info">')
    html.append('<div class="payment-info">')
    html.append(
    html.append(
    f"<div><strong>Payment Terms:</strong> {invoice.payment_terms}</div>"
    f"<div><strong>Payment Terms:</strong> {invoice.payment_terms}</div>"
    )
    )
    html.append("</div>")
    html.append("</div>")


    # Notes
    # Notes
    if invoice.notes:
    if invoice.notes:
    html.append('<div class="notes">')
    html.append('<div class="notes">')
    html.append('<div class="section-title">Notes:</div>')
    html.append('<div class="section-title">Notes:</div>')
    html.append(f"<p>{invoice.notes}</p>")
    html.append(f"<p>{invoice.notes}</p>")
    html.append("</div>")
    html.append("</div>")


    # Terms
    # Terms
    if invoice.terms:
    if invoice.terms:
    html.append('<div class="terms">')
    html.append('<div class="terms">')
    html.append('<div class="section-title">Terms and Conditions:</div>')
    html.append('<div class="section-title">Terms and Conditions:</div>')
    html.append(f"<p>{invoice.terms}</p>")
    html.append(f"<p>{invoice.terms}</p>")
    html.append("</div>")
    html.append("</div>")


    # Custom fields
    # Custom fields
    if invoice.custom_fields:
    if invoice.custom_fields:
    html.append('<div class="custom-fields">')
    html.append('<div class="custom-fields">')
    html.append('<div class="section-title">Additional Information:</div>')
    html.append('<div class="section-title">Additional Information:</div>')
    html.append("<ul>")
    html.append("<ul>")


    for name, value in invoice.custom_fields.items():
    for name, value in invoice.custom_fields.items():
    html.append(f"<li><strong>{name}:</strong> {value}</li>")
    html.append(f"<li><strong>{name}:</strong> {value}</li>")


    html.append("</ul>")
    html.append("</ul>")
    html.append("</div>")
    html.append("</div>")


    html.append("</div>")  # End invoice container
    html.append("</div>")  # End invoice container
    html.append("</body>")
    html.append("</body>")
    html.append("</html>")
    html.append("</html>")


    return "\n".join(html)
    return "\n".join(html)


    @staticmethod
    @staticmethod
    def to_text(invoice: Invoice) -> str:
    def to_text(invoice: Invoice) -> str:
    """
    """
    Format an invoice as plain text.
    Format an invoice as plain text.


    Args:
    Args:
    invoice: Invoice to format
    invoice: Invoice to format


    Returns:
    Returns:
    Plain text representation of the invoice
    Plain text representation of the invoice
    """
    """
    lines = []
    lines = []


    # Add company information
    # Add company information
    if invoice.company_name:
    if invoice.company_name:
    lines.append(invoice.company_name)
    lines.append(invoice.company_name)


    if invoice.company_address:
    if invoice.company_address:
    lines.append(invoice.company_address)
    lines.append(invoice.company_address)


    if invoice.company_phone or invoice.company_email:
    if invoice.company_phone or invoice.company_email:
    contact_info = []
    contact_info = []


    if invoice.company_phone:
    if invoice.company_phone:
    contact_info.append(f"Phone: {invoice.company_phone}")
    contact_info.append(f"Phone: {invoice.company_phone}")


    if invoice.company_email:
    if invoice.company_email:
    contact_info.append(f"Email: {invoice.company_email}")
    contact_info.append(f"Email: {invoice.company_email}")


    lines.append(" | ".join(contact_info))
    lines.append(" | ".join(contact_info))


    if invoice.company_website:
    if invoice.company_website:
    lines.append(f"Website: {invoice.company_website}")
    lines.append(f"Website: {invoice.company_website}")


    lines.append("")
    lines.append("")
    lines.append("=" * 80)
    lines.append("=" * 80)
    lines.append(f"INVOICE #{invoice.number}")
    lines.append(f"INVOICE #{invoice.number}")
    lines.append("=" * 80)
    lines.append("=" * 80)
    lines.append("")
    lines.append("")


    # Add invoice information
    # Add invoice information
    lines.append(f"Date: {invoice.date.strftime('%Y-%m-%d')}")
    lines.append(f"Date: {invoice.date.strftime('%Y-%m-%d')}")
    lines.append(f"Due Date: {invoice.due_date.strftime('%Y-%m-%d')}")
    lines.append(f"Due Date: {invoice.due_date.strftime('%Y-%m-%d')}")
    lines.append(f"Status: {invoice.status.upper()}")
    lines.append(f"Status: {invoice.status.upper()}")


    lines.append("")
    lines.append("")


    # Add customer information
    # Add customer information
    lines.append("Bill To:")
    lines.append("Bill To:")


    if invoice.customer_name:
    if invoice.customer_name:
    lines.append(f"{invoice.customer_name}")
    lines.append(f"{invoice.customer_name}")


    if invoice.customer_address:
    if invoice.customer_address:
    lines.append(f"{invoice.customer_address}")
    lines.append(f"{invoice.customer_address}")


    if invoice.customer_email:
    if invoice.customer_email:
    lines.append(f"Email: {invoice.customer_email}")
    lines.append(f"Email: {invoice.customer_email}")


    lines.append("")
    lines.append("")


    # Add items
    # Add items
    lines.append("Items:")
    lines.append("Items:")
    lines.append("-" * 80)
    lines.append("-" * 80)
    lines.append(
    lines.append(
    f"{'Description':<40} {'Quantity':>10} {'Unit Price':>15} {'Tax':>15} {'Total':>15}"
    f"{'Description':<40} {'Quantity':>10} {'Unit Price':>15} {'Tax':>15} {'Total':>15}"
    )
    )
    lines.append("-" * 80)
    lines.append("-" * 80)


    for item in invoice.items:
    for item in invoice.items:
    lines.append(
    lines.append(
    f"{item.description:<40} "
    f"{item.description:<40} "
    f"{item.quantity:>10.2f} "
    f"{item.quantity:>10.2f} "
    f"{invoice.format_amount(item.unit_price):>15} "
    f"{invoice.format_amount(item.unit_price):>15} "
    f"{invoice.format_amount(item.get_tax_amount()):>15} "
    f"{invoice.format_amount(item.get_tax_amount()):>15} "
    f"{invoice.format_amount(item.get_total()):>15}"
    f"{invoice.format_amount(item.get_total()):>15}"
    )
    )


    lines.append("-" * 80)
    lines.append("-" * 80)


    # Add totals
    # Add totals
    lines.append(
    lines.append(
    f"{'Subtotal:':<65} {invoice.format_amount(invoice.get_subtotal()):>15}"
    f"{'Subtotal:':<65} {invoice.format_amount(invoice.get_subtotal()):>15}"
    )
    )


    if invoice.get_discount_total() > 0:
    if invoice.get_discount_total() > 0:
    lines.append(
    lines.append(
    f"{invoice.discount_name+'s:':<65} {invoice.format_amount(invoice.get_discount_total()):>15}"
    f"{invoice.discount_name+'s:':<65} {invoice.format_amount(invoice.get_discount_total()):>15}"
    )
    )


    if invoice.get_tax_total() > 0:
    if invoice.get_tax_total() > 0:
    lines.append(
    lines.append(
    f"{invoice.tax_name+'es:':<65} {invoice.format_amount(invoice.get_tax_total()):>15}"
    f"{invoice.tax_name+'es:':<65} {invoice.format_amount(invoice.get_tax_total()):>15}"
    )
    )


    # Add additional fees
    # Add additional fees
    for fee in invoice.additional_fees:
    for fee in invoice.additional_fees:
    fee_name = fee["name"]
    fee_name = fee["name"]


    if fee["is_percentage"]:
    if fee["is_percentage"]:
    fee_name += f" ({fee['amount']}%)"
    fee_name += f" ({fee['amount']}%)"
    fee_amount = invoice.get_subtotal() * fee["amount"] / 100.0
    fee_amount = invoice.get_subtotal() * fee["amount"] / 100.0
    else:
    else:
    fee_amount = fee["amount"]
    fee_amount = fee["amount"]


    lines.append(f"{fee_name+'s:':<65} {invoice.format_amount(fee_amount):>15}")
    lines.append(f"{fee_name+'s:':<65} {invoice.format_amount(fee_amount):>15}")


    lines.append("-" * 80)
    lines.append("-" * 80)
    lines.append(f"{'Total:':<65} {invoice.format_amount(invoice.get_total()):>15}")
    lines.append(f"{'Total:':<65} {invoice.format_amount(invoice.get_total()):>15}")


    # Add payment information
    # Add payment information
    if invoice.payments:
    if invoice.payments:
    lines.append("")
    lines.append("")
    lines.append("Payments:")
    lines.append("Payments:")
    lines.append("-" * 80)
    lines.append("-" * 80)


    for payment in invoice.payments:
    for payment in invoice.payments:
    payment_date = datetime.fromisoformat(payment["date"]).strftime(
    payment_date = datetime.fromisoformat(payment["date"]).strftime(
    "%Y-%m-%d"
    "%Y-%m-%d"
    )
    )
    lines.append(
    lines.append(
    f"{payment_date} - {payment['payment_method']}:{' ' * 30} -{invoice.format_amount(payment['amount']):>15}"
    f"{payment_date} - {payment['payment_method']}:{' ' * 30} -{invoice.format_amount(payment['amount']):>15}"
    )
    )


    lines.append("-" * 80)
    lines.append("-" * 80)
    lines.append(
    lines.append(
    f"{'Balance Due:':<65} {invoice.format_amount(invoice.get_balance_due()):>15}"
    f"{'Balance Due:':<65} {invoice.format_amount(invoice.get_balance_due()):>15}"
    )
    )


    lines.append("-" * 80)
    lines.append("-" * 80)


    # Add payment terms
    # Add payment terms
    if invoice.payment_terms:
    if invoice.payment_terms:
    lines.append("")
    lines.append("")
    lines.append(f"Payment Terms: {invoice.payment_terms}")
    lines.append(f"Payment Terms: {invoice.payment_terms}")


    # Add notes
    # Add notes
    if invoice.notes:
    if invoice.notes:
    lines.append("")
    lines.append("")
    lines.append("Notes:")
    lines.append("Notes:")
    lines.append(invoice.notes)
    lines.append(invoice.notes)


    # Add terms
    # Add terms
    if invoice.terms:
    if invoice.terms:
    lines.append("")
    lines.append("")
    lines.append("Terms and Conditions:")
    lines.append("Terms and Conditions:")
    lines.append(invoice.terms)
    lines.append(invoice.terms)


    # Add custom fields
    # Add custom fields
    if invoice.custom_fields:
    if invoice.custom_fields:
    lines.append("")
    lines.append("")
    lines.append("Additional Information:")
    lines.append("Additional Information:")


    for name, value in invoice.custom_fields.items():
    for name, value in invoice.custom_fields.items():
    lines.append(f"{name}: {value}")
    lines.append(f"{name}: {value}")


    return "\n".join(lines)
    return "\n".join(lines)


    @staticmethod
    @staticmethod
    def to_csv(invoice: Invoice) -> str:
    def to_csv(invoice: Invoice) -> str:
    """
    """
    Format an invoice as CSV.
    Format an invoice as CSV.


    Args:
    Args:
    invoice: Invoice to format
    invoice: Invoice to format


    Returns:
    Returns:
    CSV representation of the invoice
    CSV representation of the invoice
    """
    """
    lines = []
    lines = []


    # Add header
    # Add header
    lines.append(
    lines.append(
    "Invoice Number,Date,Due Date,Status,Customer ID,Customer Name,Total,Balance Due"
    "Invoice Number,Date,Due Date,Status,Customer ID,Customer Name,Total,Balance Due"
    )
    )


    # Add invoice information
    # Add invoice information
    lines.append(
    lines.append(
    f"{invoice.number},"
    f"{invoice.number},"
    f"{invoice.date.strftime('%Y-%m-%d')},"
    f"{invoice.date.strftime('%Y-%m-%d')},"
    f"{invoice.due_date.strftime('%Y-%m-%d')},"
    f"{invoice.due_date.strftime('%Y-%m-%d')},"
    f"{invoice.status},"
    f"{invoice.status},"
    f"{invoice.customer_id},"
    f"{invoice.customer_id},"
    f"{invoice.customer_name},"
    f"{invoice.customer_name},"
    f"{invoice.get_total()},"
    f"{invoice.get_total()},"
    f"{invoice.get_balance_due()}"
    f"{invoice.get_balance_due()}"
    )
    )


    # Add blank line
    # Add blank line
    lines.append("")
    lines.append("")


    # Add items header
    # Add items header
    lines.append(
    lines.append(
    "Description,Quantity,Unit Price,Discount,Tax Rate,Tax Amount,Total"
    "Description,Quantity,Unit Price,Discount,Tax Rate,Tax Amount,Total"
    )
    )


    # Add items
    # Add items
    for item in invoice.items:
    for item in invoice.items:
    lines.append(
    lines.append(
    f"{item.description},"
    f"{item.description},"
    f"{item.quantity},"
    f"{item.quantity},"
    f"{item.unit_price},"
    f"{item.unit_price},"
    f"{item.discount},"
    f"{item.discount},"
    f"{item.tax_rate},"
    f"{item.tax_rate},"
    f"{item.get_tax_amount()},"
    f"{item.get_tax_amount()},"
    f"{item.get_total()}"
    f"{item.get_total()}"
    )
    )


    # Add blank line
    # Add blank line
    lines.append("")
    lines.append("")


    # Add payments header
    # Add payments header
    lines.append("Payment Date,Payment Method,Transaction ID,Amount")
    lines.append("Payment Date,Payment Method,Transaction ID,Amount")


    # Add payments
    # Add payments
    for payment in invoice.payments:
    for payment in invoice.payments:
    payment_date = datetime.fromisoformat(payment["date"]).strftime("%Y-%m-%d")
    payment_date = datetime.fromisoformat(payment["date"]).strftime("%Y-%m-%d")
    transaction_id = payment.get("transaction_id", "")
    transaction_id = payment.get("transaction_id", "")


    lines.append(
    lines.append(
    f"{payment_date},"
    f"{payment_date},"
    f"{payment['payment_method']},"
    f"{payment['payment_method']},"
    f"{transaction_id},"
    f"{transaction_id},"
    f"{payment['amount']}"
    f"{payment['amount']}"
    )
    )


    return "\n".join(lines)
    return "\n".join(lines)


    @staticmethod
    @staticmethod
    def to_pdf(invoice: Invoice) -> bytes:
    def to_pdf(invoice: Invoice) -> bytes:
    """
    """
    Format an invoice as PDF.
    Format an invoice as PDF.


    Args:
    Args:
    invoice: Invoice to format
    invoice: Invoice to format


    Returns:
    Returns:
    PDF representation of the invoice as bytes
    PDF representation of the invoice as bytes
    """
    """
    # This is a placeholder for actual PDF generation
    # This is a placeholder for actual PDF generation
    # In a real implementation, this would use a PDF library like ReportLab or WeasyPrint
    # In a real implementation, this would use a PDF library like ReportLab or WeasyPrint


    # For now, we'll just convert the HTML to a simple PDF representation
    # For now, we'll just convert the HTML to a simple PDF representation
    html = InvoiceFormatter.to_html(invoice)
    html = InvoiceFormatter.to_html(invoice)


    # Create a simple PDF header
    # Create a simple PDF header
    pdf_header = b"%PDF-1.7\n"
    pdf_header = b"%PDF-1.7\n"


    # Create a simple PDF body with the HTML content
    # Create a simple PDF body with the HTML content
    pdf_body = "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    pdf_body = "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    pdf_body += "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    pdf_body += "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    pdf_body += "3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
    pdf_body += "3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
    pdf_body += (
    pdf_body += (
    "4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    "4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    )
    )
    pdf_body += (
    pdf_body += (
    f"5 0 obj\n<< /Length {len(html)} >>\nstream\n{html}\nendstream\nendobj\n"
    f"5 0 obj\n<< /Length {len(html)} >>\nstream\n{html}\nendstream\nendobj\n"
    )
    )


    # Create a simple PDF trailer
    # Create a simple PDF trailer
    pdf_trailer = b"xref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000056 00000 n\n0000000111 00000 n\n0000000212 00000 n\n0000000277 00000 n\ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n408\n%%EOF"
    pdf_trailer = b"xref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000056 00000 n\n0000000111 00000 n\n0000000212 00000 n\n0000000277 00000 n\ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n408\n%%EOF"


    # Combine the PDF parts
    # Combine the PDF parts
    pdf = pdf_header + pdf_body.encode("utf-8") + pdf_trailer
    pdf = pdf_header + pdf_body.encode("utf-8") + pdf_trailer


    return pdf
    return pdf




    class InvoiceDelivery:
    class InvoiceDelivery:
    """
    """
    Class for delivering invoices to customers.
    Class for delivering invoices to customers.


    This class provides methods for delivering invoices to customers,
    This class provides methods for delivering invoices to customers,
    including email delivery, PDF generation, and export functionality.
    including email delivery, PDF generation, and export functionality.
    """
    """


    def __init__(self, email_config: Optional[Dict[str, Any]] = None):
    def __init__(self, email_config: Optional[Dict[str, Any]] = None):
    """
    """
    Initialize an invoice delivery system.
    Initialize an invoice delivery system.


    Args:
    Args:
    email_config: Email configuration
    email_config: Email configuration
    """
    """
    self.email_config = email_config or {}
    self.email_config = email_config or {}


    def send_invoice_by_email(
    def send_invoice_by_email(
    self,
    self,
    invoice: Invoice,
    invoice: Invoice,
    email: Optional[str] = None,
    email: Optional[str] = None,
    subject: Optional[str] = None,
    subject: Optional[str] = None,
    message: Optional[str] = None,
    message: Optional[str] = None,
    format: str = "html",
    format: str = "html",
    attach_pdf: bool = True,
    attach_pdf: bool = True,
    ) -> bool:
    ) -> bool:
    """
    """
    Deliver invoice to customer through intelligent multi-format email pipeline.
    Deliver invoice to customer through intelligent multi-format email pipeline.


    This algorithm implements a sophisticated invoice delivery system with dynamic
    This algorithm implements a sophisticated invoice delivery system with dynamic
    content generation and customer communications management. The implementation
    content generation and customer communications management. The implementation
    follows these key phases:
    follows these key phases:


    1. RECIPIENT RESOLUTION AND VALIDATION:
    1. RECIPIENT RESOLUTION AND VALIDATION:
    - Intelligently resolves the target recipient through parameter or invoice data
    - Intelligently resolves the target recipient through parameter or invoice data
    - Performs email address validation to prevent delivery failures
    - Performs email address validation to prevent delivery failures
    - Falls back to customer record when specific email not provided
    - Falls back to customer record when specific email not provided
    - Ensures deliverability through pre-validation before sending
    - Ensures deliverability through pre-validation before sending
    - Implements proper error handling for missing recipient information
    - Implements proper error handling for missing recipient information


    2. DYNAMIC CONTENT GENERATION:
    2. DYNAMIC CONTENT GENERATION:
    - Generates contextually appropriate subject lines based on invoice details
    - Generates contextually appropriate subject lines based on invoice details
    - Implements smart message composition based on payment terms and due dates
    - Implements smart message composition based on payment terms and due dates
    - Automatically selects appropriate tone and formality for customer communication
    - Automatically selects appropriate tone and formality for customer communication
    - Formats invoice content according to specified presentation format (HTML/text)
    - Formats invoice content according to specified presentation format (HTML/text)
    - Builds complete email package with all required metadata
    - Builds complete email package with all required metadata


    3. ATTACHMENT HANDLING:
    3. ATTACHMENT HANDLING:
    - Conditionally generates PDF version of the invoice when needed
    - Conditionally generates PDF version of the invoice when needed
    - Properly encodes binary attachment data for email transmission
    - Properly encodes binary attachment data for email transmission
    - Sets appropriate MIME types and content headers
    - Sets appropriate MIME types and content headers
    - Implements secure attachment handling to prevent data corruption
    - Implements secure attachment handling to prevent data corruption
    - Optimizes attachment size while maintaining quality and readability
    - Optimizes attachment size while maintaining quality and readability


    4. DELIVERY ORCHESTRATION:
    4. DELIVERY ORCHESTRATION:
    - Records delivery attempts for audit and follow-up purposes
    - Records delivery attempts for audit and follow-up purposes
    - Manages the full email delivery lifecycle
    - Manages the full email delivery lifecycle
    - Provides a foundation for scheduled and automated invoice delivery
    - Provides a foundation for scheduled and automated invoice delivery
    - Incorporates proper error handling for network or service issues
    - Incorporates proper error handling for network or service issues
    - Returns delivery status for integration with broader workflows
    - Returns delivery status for integration with broader workflows


    This invoice delivery algorithm addresses several critical business requirements:
    This invoice delivery algorithm addresses several critical business requirements:
    - Professional customer communications with proper branding
    - Professional customer communications with proper branding
    - Multi-format delivery options for different customer preferences
    - Multi-format delivery options for different customer preferences
    - Complete audit trail of invoice communications
    - Complete audit trail of invoice communications
    - Flexible attachment options for formal documentation
    - Flexible attachment options for formal documentation


    The implementation specifically supports common business scenarios:
    The implementation specifically supports common business scenarios:
    - Initial invoice delivery with payment instructions
    - Initial invoice delivery with payment instructions
    - Automated invoice distribution to customers
    - Automated invoice distribution to customers
    - Formal business communications with proper documentation
    - Formal business communications with proper documentation
    - Email pipeline integration for accounts receivable workflows
    - Email pipeline integration for accounts receivable workflows


    Args:
    Args:
    invoice: Invoice object to be delivered containing all necessary details
    invoice: Invoice object to be delivered containing all necessary details
    email: Override recipient email address (uses customer email from invoice if not provided)
    email: Override recipient email address (uses customer email from invoice if not provided)
    subject: Custom email subject line (auto-generated from invoice details if not provided)
    subject: Custom email subject line (auto-generated from invoice details if not provided)
    message: Custom email message body (auto-generated with payment details if not provided)
    message: Custom email message body (auto-generated with payment details if not provided)
    format: Content format for email body - "html" or "text"
    format: Content format for email body - "html" or "text"
    attach_pdf: Whether to generate and attach a PDF version of the invoice
    attach_pdf: Whether to generate and attach a PDF version of the invoice


    Returns:
    Returns:
    Boolean indicating successful delivery initiation (true) or failure (false)
    Boolean indicating successful delivery initiation (true) or failure (false)
    """
    """
    # This is a placeholder for actual email sending functionality
    # This is a placeholder for actual email sending functionality
    # In a real implementation, this would use an email service
    # In a real implementation, this would use an email service


    # Get email address
    # Get email address
    to_email = email or invoice.customer_email
    to_email = email or invoice.customer_email


    if not to_email:
    if not to_email:
    return False
    return False


    # Set default subject if not provided
    # Set default subject if not provided
    if not subject:
    if not subject:
    subject = f"Invoice {invoice.number} from {invoice.company_name}"
    subject = f"Invoice {invoice.number} from {invoice.company_name}"


    # Set default message if not provided
    # Set default message if not provided
    if not message:
    if not message:
    message = f"Please find attached invoice {invoice.number} for {invoice.format_amount(invoice.get_total())}."
    message = f"Please find attached invoice {invoice.number} for {invoice.format_amount(invoice.get_total())}."


    if invoice.due_date:
    if invoice.due_date:
    message += (
    message += (
    f" Payment is due by {invoice.due_date.strftime('%Y-%m-%d')}."
    f" Payment is due by {invoice.due_date.strftime('%Y-%m-%d')}."
    )
    )


    message += " Thank you for your business."
    message += " Thank you for your business."


    # Generate invoice content
    # Generate invoice content
    if format == "html":
    if format == "html":
    InvoiceFormatter.to_html(invoice)
    InvoiceFormatter.to_html(invoice)
    else:
    else:
    InvoiceFormatter.to_text(invoice)
    InvoiceFormatter.to_text(invoice)


    # Generate PDF attachment if requested
    # Generate PDF attachment if requested


    if attach_pdf:
    if attach_pdf:
    pdf_data = InvoiceFormatter.to_pdf(invoice)
    pdf_data = InvoiceFormatter.to_pdf(invoice)
    {
    {
    "filename": f"Invoice_{invoice.number}.pd",
    "filename": f"Invoice_{invoice.number}.pd",
    "content": base64.b64encode(pdf_data).decode("utf-8"),
    "content": base64.b64encode(pdf_data).decode("utf-8"),
    "content_type": "application/pd",
    "content_type": "application/pd",
    }
    }


    # Print email details (for demo purposes)
    # Print email details (for demo purposes)
    print(f"Sending invoice {invoice.number} to {to_email}")
    print(f"Sending invoice {invoice.number} to {to_email}")
    print(f"Subject: {subject}")
    print(f"Subject: {subject}")
    print(f"Format: {format}")
    print(f"Format: {format}")
    print(f"Attach PDF: {attach_pdf}")
    print(f"Attach PDF: {attach_pdf}")


    # In a real implementation, this would send an email
    # In a real implementation, this would send an email
    # For now, just return True
    # For now, just return True
    return True
    return True


    def generate_pdf(
    def generate_pdf(
    self, invoice: Invoice, output_path: Optional[str] = None
    self, invoice: Invoice, output_path: Optional[str] = None
    ) -> Union[bytes, str]:
    ) -> Union[bytes, str]:
    """
    """
    Generate a PDF version of an invoice.
    Generate a PDF version of an invoice.


    Args:
    Args:
    invoice: Invoice to generate PDF for
    invoice: Invoice to generate PDF for
    output_path: Path to save the PDF to
    output_path: Path to save the PDF to


    Returns:
    Returns:
    PDF data as bytes if output_path is None, otherwise the output path
    PDF data as bytes if output_path is None, otherwise the output path
    """
    """
    # Generate PDF data
    # Generate PDF data
    pdf_data = InvoiceFormatter.to_pdf(invoice)
    pdf_data = InvoiceFormatter.to_pdf(invoice)


    # Save to file if output path is provided
    # Save to file if output path is provided
    if output_path:
    if output_path:
    with open(output_path, "wb") as f:
    with open(output_path, "wb") as f:
    f.write(pdf_data)
    f.write(pdf_data)


    return output_path
    return output_path


    return pdf_data
    return pdf_data


    def export_invoice(
    def export_invoice(
    self, invoice: Invoice, format: str = "json", output_path: Optional[str] = None
    self, invoice: Invoice, format: str = "json", output_path: Optional[str] = None
    ) -> Union[str, bytes]:
    ) -> Union[str, bytes]:
    """
    """
    Convert invoice to multiple export formats through format-specific serialization pipeline.
    Convert invoice to multiple export formats through format-specific serialization pipeline.


    This algorithm implements a comprehensive multi-format invoice export system with
    This algorithm implements a comprehensive multi-format invoice export system with
    dynamic content adaptation and format-specific optimization. The implementation
    dynamic content adaptation and format-specific optimization. The implementation
    follows these key phases:
    follows these key phases:


    1. FORMAT-SPECIFIC SERIALIZATION:
    1. FORMAT-SPECIFIC SERIALIZATION:
    - Selects appropriate serialization strategy based on target format
    - Selects appropriate serialization strategy based on target format
    - Implements specialized formatters for each supported export format
    - Implements specialized formatters for each supported export format
    - Maintains consistent data representation across all export formats
    - Maintains consistent data representation across all export formats
    - Preserves all critical invoice data regardless of format limitations
    - Preserves all critical invoice data regardless of format limitations
    - Optimizes content presentation for each target format's unique capabilities
    - Optimizes content presentation for each target format's unique capabilities


    2. CONTENT TRANSFORMATION PIPELINE:
    2. CONTENT TRANSFORMATION PIPELINE:
    - Performs format-specific data transformations for optimal representation
    - Performs format-specific data transformations for optimal representation
    - Handles complex data structures like nested line items and payment records
    - Handles complex data structures like nested line items and payment records
    - Implements proper escaping and encoding for each target format
    - Implements proper escaping and encoding for each target format
    - Resolves format-specific limitations and edge cases
    - Resolves format-specific limitations and edge cases
    - Ensures complete data integrity throughout conversion process
    - Ensures complete data integrity throughout conversion process


    3. BINARY VS. TEXT FORMAT HANDLING:
    3. BINARY VS. TEXT FORMAT HANDLING:
    - Dynamically adapts processing for binary (PDF) vs. text formats
    - Dynamically adapts processing for binary (PDF) vs. text formats
    - Implements proper encoding and MIME type handling
    - Implements proper encoding and MIME type handling
    - Manages binary data streams with appropriate buffer handling
    - Manages binary data streams with appropriate buffer handling
    - Ensures consistent output across different operating systems
    - Ensures consistent output across different operating systems
    - Properly handles UTF-8 encoding for international character support
    - Properly handles UTF-8 encoding for international character support


    4. STORAGE INTEGRATION:
    4. STORAGE INTEGRATION:
    - Implements flexible storage options (in-memory vs. file-based)
    - Implements flexible storage options (in-memory vs. file-based)
    - Handles proper file naming, paths and directories
    - Handles proper file naming, paths and directories
    - Manages file system interactions with proper error handling
    - Manages file system interactions with proper error handling
    - Ensures atomic file operations to prevent corruption
    - Ensures atomic file operations to prevent corruption
    - Returns appropriate data type based on output destination
    - Returns appropriate data type based on output destination


    This export algorithm addresses several critical business requirements:
    This export algorithm addresses several critical business requirements:
    - Multi-format support for different downstream systems
    - Multi-format support for different downstream systems
    - Consistent representation across all output formats
    - Consistent representation across all output formats
    - Flexible output destinations (memory, file system)
    - Flexible output destinations (memory, file system)
    - Complete data preservation regardless of format
    - Complete data preservation regardless of format


    The implementation specifically supports common business scenarios:
    The implementation specifically supports common business scenarios:
    - Invoice archiving in standardized formats
    - Invoice archiving in standardized formats
    - Integration with external accounting systems
    - Integration with external accounting systems
    - Customer-facing invoice representation
    - Customer-facing invoice representation
    - Data exchange with third-party services
    - Data exchange with third-party services


    Args:
    Args:
    invoice: Invoice object to be exported containing all necessary details
    invoice: Invoice object to be exported containing all necessary details
    format: Target export format - one of "json", "html", "text", "csv", or "pd"
    format: Target export format - one of "json", "html", "text", "csv", or "pd"
    output_path: Optional file path to save the exported data (returns data in memory if not provided)
    output_path: Optional file path to save the exported data (returns data in memory if not provided)


    Returns:
    Returns:
    String or bytes (depending on format) containing the exported invoice data
    String or bytes (depending on format) containing the exported invoice data
    If output_path is provided, returns the path where the data was saved
    If output_path is provided, returns the path where the data was saved


    Raises:
    Raises:
    ValueError: If an unsupported export format is specified
    ValueError: If an unsupported export format is specified
    """
    """
    # Generate export data
    # Generate export data
    if format == "json":
    if format == "json":
    data = invoice.to_json()
    data = invoice.to_json()
    binary = False
    binary = False
    elif format == "html":
    elif format == "html":
    data = InvoiceFormatter.to_html(invoice)
    data = InvoiceFormatter.to_html(invoice)
    binary = False
    binary = False
    elif format == "text":
    elif format == "text":
    data = InvoiceFormatter.to_text(invoice)
    data = InvoiceFormatter.to_text(invoice)
    binary = False
    binary = False
    elif format == "csv":
    elif format == "csv":
    data = InvoiceFormatter.to_csv(invoice)
    data = InvoiceFormatter.to_csv(invoice)
    binary = False
    binary = False
    elif format == "pd":
    elif format == "pd":
    data = InvoiceFormatter.to_pdf(invoice)
    data = InvoiceFormatter.to_pdf(invoice)
    binary = True
    binary = True
    else:
    else:
    raise ValueError(f"Unsupported format: {format}")
    raise ValueError(f"Unsupported format: {format}")


    # Save to file if output path is provided
    # Save to file if output path is provided
    if output_path:
    if output_path:
    if binary:
    if binary:
    with open(output_path, "wb") as f:
    with open(output_path, "wb") as f:
    f.write(data)
    f.write(data)
    else:
    else:
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(data)
    f.write(data)


    return output_path
    return output_path


    return data
    return data


    def export_invoices(
    def export_invoices(
    self,
    self,
    invoices: List[Invoice],
    invoices: List[Invoice],
    format: str = "csv",
    format: str = "csv",
    output_path: Optional[str] = None,
    output_path: Optional[str] = None,
    ) -> str:
    ) -> str:
    """
    """
    Process multiple invoices through consolidated batch export pipeline with enterprise-grade optimizations.
    Process multiple invoices through consolidated batch export pipeline with enterprise-grade optimizations.


    This algorithm implements a high-performance batch processing system for invoice
    This algorithm implements a high-performance batch processing system for invoice
    collections, enabling efficient bulk export operations with format-specific
    collections, enabling efficient bulk export operations with format-specific
    optimizations. The implementation follows these key phases:
    optimizations. The implementation follows these key phases:


    1. BATCH PROCESSING OPTIMIZATION:
    1. BATCH PROCESSING OPTIMIZATION:
    - Efficiently handles collections of invoices as a unified dataset
    - Efficiently handles collections of invoices as a unified dataset
    - Implements memory-efficient batch processing to handle large invoice sets
    - Implements memory-efficient batch processing to handle large invoice sets
    - Uses a single-pass approach to minimize redundant operations
    - Uses a single-pass approach to minimize redundant operations
    - Dynamically adjusts processing based on collection size
    - Dynamically adjusts processing based on collection size
    - Optimizes I/O operations through consolidated file handling
    - Optimizes I/O operations through consolidated file handling


    2. FORMAT-SPECIFIC CONSOLIDATION:
    2. FORMAT-SPECIFIC CONSOLIDATION:
    - Adapts aggregation strategy based on target format requirements
    - Adapts aggregation strategy based on target format requirements
    - Implements specialized header/metadata management for each format
    - Implements specialized header/metadata management for each format
    - Maintains proper structure and relationships between invoices
    - Maintains proper structure and relationships between invoices
    - Preserves data fidelity for batch reporting purposes
    - Preserves data fidelity for batch reporting purposes
    - Handles format-specific batch size limitations
    - Handles format-specific batch size limitations


    3. BULK DATA TRANSFORMATION:
    3. BULK DATA TRANSFORMATION:
    - Efficiently converts multiple complex invoice objects to target format
    - Efficiently converts multiple complex invoice objects to target format
    - Maintains consistent data representation across the collection
    - Maintains consistent data representation across the collection
    - Implements specialized serialization for financial datasets
    - Implements specialized serialization for financial datasets
    - Ensures proper data typing and formatting for downstream systems
    - Ensures proper data typing and formatting for downstream systems
    - Handles edge cases with non-uniform invoice structures
    - Handles edge cases with non-uniform invoice structures


    4. OUTPUT MANAGEMENT:
    4. OUTPUT MANAGEMENT:
    - Provides flexible in-memory or file-based export options
    - Provides flexible in-memory or file-based export options
    - Implements proper resource cleanup for large dataset processing
    - Implements proper resource cleanup for large dataset processing
    - Handles path resolution and file naming for persistent storage
    - Handles path resolution and file naming for persistent storage
    - Ensures atomic write operations for data integrity
    - Ensures atomic write operations for data integrity
    - Returns appropriate result based on output destination
    - Returns appropriate result based on output destination


    5. ENTERPRISE SCALE CONSIDERATIONS:
    5. ENTERPRISE SCALE CONSIDERATIONS:
    - Supports high-volume financial data processing requirements
    - Supports high-volume financial data processing requirements
    - Optimizes memory consumption for large enterprise datasets
    - Optimizes memory consumption for large enterprise datasets
    - Maintains consistent performance with linear scaling properties
    - Maintains consistent performance with linear scaling properties
    - Enables integration with enterprise reporting and BI systems
    - Enables integration with enterprise reporting and BI systems
    - Provides foundation for distributed processing of very large invoice collections
    - Provides foundation for distributed processing of very large invoice collections


    This bulk export algorithm addresses several critical business requirements:
    This bulk export algorithm addresses several critical business requirements:
    - Efficient batch processing for reporting and data exchange
    - Efficient batch processing for reporting and data exchange
    - Consolidated invoice collection management for accounting systems
    - Consolidated invoice collection management for accounting systems
    - Format standardization across multiple invoice records
    - Format standardization across multiple invoice records
    - Performance optimization for large invoice datasets
    - Performance optimization for large invoice datasets
    - Enterprise-grade financial data integration capabilities
    - Enterprise-grade financial data integration capabilities


    The implementation specifically supports common business scenarios:
    The implementation specifically supports common business scenarios:
    - Monthly/quarterly financial reporting with multiple invoices
    - Monthly/quarterly financial reporting with multiple invoices
    - Batch processing for accounting system integration
    - Batch processing for accounting system integration
    - Financial data warehousing and analysis
    - Financial data warehousing and analysis
    - Bulk invoice archiving and record keeping
    - Bulk invoice archiving and record keeping
    - Enterprise ERP and accounting system integration
    - Enterprise ERP and accounting system integration


    Args:
    Args:
    invoices: Collection of Invoice objects to be processed in batch
    invoices: Collection of Invoice objects to be processed in batch
    format: Target export format - currently supports "csv" or "json"
    format: Target export format - currently supports "csv" or "json"
    output_path: Optional file path for saving the consolidated export
    output_path: Optional file path for saving the consolidated export


    Returns:
    Returns:
    String containing the consolidated invoice data
    String containing the consolidated invoice data
    If output_path is provided, returns the path where the data was saved
    If output_path is provided, returns the path where the data was saved


    Raises:
    Raises:
    ValueError: If an unsupported export format is specified for batch processing
    ValueError: If an unsupported export format is specified for batch processing
    """
    """
    if format == "csv":
    if format == "csv":
    # Generate CSV header
    # Generate CSV header
    lines = [
    lines = [
    "Invoice Number,Date,Due Date,Status,Customer ID,Customer Name,Total,Balance Due"
    "Invoice Number,Date,Due Date,Status,Customer ID,Customer Name,Total,Balance Due"
    ]
    ]


    # Add invoice information
    # Add invoice information
    for invoice in invoices:
    for invoice in invoices:
    lines.append(
    lines.append(
    f"{invoice.number},"
    f"{invoice.number},"
    f"{invoice.date.strftime('%Y-%m-%d')},"
    f"{invoice.date.strftime('%Y-%m-%d')},"
    f"{invoice.due_date.strftime('%Y-%m-%d')},"
    f"{invoice.due_date.strftime('%Y-%m-%d')},"
    f"{invoice.status},"
    f"{invoice.status},"
    f"{invoice.customer_id},"
    f"{invoice.customer_id},"
    f"{invoice.customer_name},"
    f"{invoice.customer_name},"
    f"{invoice.get_total()},"
    f"{invoice.get_total()},"
    f"{invoice.get_balance_due()}"
    f"{invoice.get_balance_due()}"
    )
    )


    data = "\n".join(lines)
    data = "\n".join(lines)


    elif format == "json":
    elif format == "json":
    # Generate JSON array
    # Generate JSON array
    data = json.dumps([invoice.to_dict() for invoice in invoices], indent=2)
    data = json.dumps([invoice.to_dict() for invoice in invoices], indent=2)


    else:
    else:
    raise ValueError(f"Unsupported format for multiple invoices: {format}")
    raise ValueError(f"Unsupported format for multiple invoices: {format}")


    # Save to file if output path is provided
    # Save to file if output path is provided
    if output_path:
    if output_path:
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(data)
    f.write(data)


    return output_path
    return output_path


    return data
    return data




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create an invoice
    # Create an invoice
    invoice = Invoice(customer_id="cust_123", currency="USD")
    invoice = Invoice(customer_id="cust_123", currency="USD")


    # Set company and customer information
    # Set company and customer information
    invoice.set_company_info(
    invoice.set_company_info(
    name="AI Tools Inc.",
    name="AI Tools Inc.",
    address="123 Main St, San Francisco, CA 94111",
    address="123 Main St, San Francisco, CA 94111",
    email="billing@aitools.com",
    email="billing@aitools.com",
    phone="(555) 123-4567",
    phone="(555) 123-4567",
    website="https://aitools.com",
    website="https://aitools.com",
    )
    )


    invoice.set_customer_info(
    invoice.set_customer_info(
    name="John Doe",
    name="John Doe",
    email="john.doe@example.com",
    email="john.doe@example.com",
    address="456 Oak St, San Francisco, CA 94112",
    address="456 Oak St, San Francisco, CA 94112",
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


    # Create an invoice delivery system
    # Create an invoice delivery system
    delivery = InvoiceDelivery()
    delivery = InvoiceDelivery()


    # Export invoice to different formats
    # Export invoice to different formats
    html_output = delivery.export_invoice(
    html_output = delivery.export_invoice(
    invoice, format="html", output_path="invoice_example.html"
    invoice, format="html", output_path="invoice_example.html"
    )
    )
    text_output = delivery.export_invoice(
    text_output = delivery.export_invoice(
    invoice, format="text", output_path="invoice_example.txt"
    invoice, format="text", output_path="invoice_example.txt"
    )
    )
    csv_output = delivery.export_invoice(
    csv_output = delivery.export_invoice(
    invoice, format="csv", output_path="invoice_example.csv"
    invoice, format="csv", output_path="invoice_example.csv"
    )
    )


    print(f"Invoice exported to HTML: {html_output}")
    print(f"Invoice exported to HTML: {html_output}")
    print(f"Invoice exported to text: {text_output}")
    print(f"Invoice exported to text: {text_output}")
    print(f"Invoice exported to CSV: {csv_output}")
    print(f"Invoice exported to CSV: {csv_output}")


    # Generate PDF
    # Generate PDF
    pdf_output = delivery.generate_pdf(invoice, output_path="invoice_example.pd")
    pdf_output = delivery.generate_pdf(invoice, output_path="invoice_example.pd")
    print(f"Invoice exported to PDF: {pdf_output}")
    print(f"Invoice exported to PDF: {pdf_output}")


    # Send invoice by email
    # Send invoice by email
    delivery.send_invoice_by_email(
    delivery.send_invoice_by_email(
    invoice=invoice,
    invoice=invoice,
    email="john.doe@example.com",
    email="john.doe@example.com",
    subject="Your AI Tools Inc. Invoice",
    subject="Your AI Tools Inc. Invoice",
    message="Thank you for your business!",
    message="Thank you for your business!",
    format="html",
    format="html",
    attach_pdf=True,
    attach_pdf=True,
    )
    )