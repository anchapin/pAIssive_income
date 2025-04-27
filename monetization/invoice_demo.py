"""
Invoice generation and management demo for the pAIssive Income project.

This script demonstrates how to use the invoice generation and management system.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import os

from .usage_tracking import UsageMetric, UsageCategory
from .usage_tracker import UsageTracker
from .billing_calculator import BillingCalculator
from .invoice import Invoice, InvoiceStatus, InvoiceItem
from .invoice_manager import InvoiceManager
from .invoice_delivery import InvoiceDelivery, InvoiceFormatter


def print_separator():
    """Print a separator line."""
    print("\n" + "-" * 80 + "\n")


def run_demo():
    """Run the invoice generation and management demo."""
    print("Invoice Generation and Management Demo")
    print_separator()
    
    # Create a usage tracker
    tracker = UsageTracker(storage_dir="usage_data")
    
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
    
    # Create an invoice delivery system
    delivery = InvoiceDelivery()
    
    # Create a customer
    customer_id = "cust_demo_123"
    customer_info = {
        "name": "Demo Customer",
        "email": "demo.customer@example.com",
        "address": "456 Oak St, San Francisco, CA 94112"
    }
    
    print(f"Creating invoice for customer: {customer_info['name']}")
    
    # Create an invoice
    invoice = manager.create_invoice(
        customer_id=customer_id,
        customer_info=customer_info
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
    
    # Add an additional fee
    invoice.add_additional_fee(
        name="Processing Fee",
        amount=2.50
    )
    
    # Set payment terms and notes
    invoice.set_payment_terms("Net 30")
    invoice.set_notes("Thank you for your business!")
    
    print(f"Invoice created: {invoice}")
    print(f"Number: {invoice.number}")
    print(f"Date: {invoice.date.strftime('%Y-%m-%d')}")
    print(f"Due Date: {invoice.due_date.strftime('%Y-%m-%d')}")
    print(f"Status: {invoice.status}")
    
    print("\nItems:")
    for item in invoice.items:
        print(f"- {item}")
    
    print(f"\nSubtotal: {invoice.format_amount(invoice.get_subtotal())}")
    print(f"Tax: {invoice.format_amount(invoice.get_tax_total())}")
    print(f"Additional Fees: {invoice.format_amount(invoice.get_additional_fees_total())}")
    print(f"Total: {invoice.format_amount(invoice.get_total())}")
    
    print_separator()
    
    # Update status to sent
    print("Updating invoice status to SENT...")
    manager.update_invoice_status(invoice.id, InvoiceStatus.SENT, "Invoice sent to customer")
    print(f"Updated status: {invoice.status}")
    
    print_separator()
    
    # Add a payment
    print("Adding a partial payment...")
    payment = manager.add_payment(
        invoice_id=invoice.id,
        amount=30.00,
        payment_method="Credit Card",
        transaction_id="txn_123456"
    )
    
    print(f"Payment added: {invoice.format_amount(payment['amount'])}")
    print(f"Total paid: {invoice.format_amount(invoice.get_total_paid())}")
    print(f"Balance due: {invoice.format_amount(invoice.get_balance_due())}")
    print(f"Status: {invoice.status}")
    
    print_separator()
    
    # Export invoice to different formats
    print("Exporting invoice to different formats...")
    
    # Create output directory if it doesn't exist
    os.makedirs("invoice_exports", exist_ok=True)
    
    html_output = delivery.export_invoice(invoice, format="html", output_path="invoice_exports/invoice_example.html")
    text_output = delivery.export_invoice(invoice, format="text", output_path="invoice_exports/invoice_example.txt")
    csv_output = delivery.export_invoice(invoice, format="csv", output_path="invoice_exports/invoice_example.csv")
    json_output = delivery.export_invoice(invoice, format="json", output_path="invoice_exports/invoice_example.json")
    
    print(f"Invoice exported to HTML: {html_output}")
    print(f"Invoice exported to text: {text_output}")
    print(f"Invoice exported to CSV: {csv_output}")
    print(f"Invoice exported to JSON: {json_output}")
    
    print_separator()
    
    # Generate PDF
    print("Generating PDF invoice...")
    pdf_output = delivery.generate_pdf(invoice, output_path="invoice_exports/invoice_example.pdf")
    print(f"Invoice exported to PDF: {pdf_output}")
    
    print_separator()
    
    # Send invoice by email
    print("Sending invoice by email...")
    delivery.send_invoice_by_email(
        invoice=invoice,
        email="demo.customer@example.com",
        subject="Your AI Tools Inc. Invoice",
        message="Thank you for your business!",
        format="html",
        attach_pdf=True
    )
    
    print_separator()
    
    # Create multiple invoices for demo
    print("Creating multiple invoices for demo...")
    
    for i in range(3):
        # Create invoice
        inv = manager.create_invoice(
            customer_id=customer_id,
            customer_info=customer_info,
            date=datetime.now() - timedelta(days=30 * i)
        )
        
        # Add random items
        num_items = random.randint(1, 3)
        
        for j in range(num_items):
            inv.add_item(
                description=f"Service {j+1}",
                quantity=random.randint(1, 5),
                unit_price=random.uniform(10, 100),
                tax_rate=0.0825
            )
        
        # Update status
        if i == 0:
            manager.update_invoice_status(inv.id, InvoiceStatus.PENDING)
        elif i == 1:
            manager.update_invoice_status(inv.id, InvoiceStatus.PAID)
            manager.add_payment(
                invoice_id=inv.id,
                amount=inv.get_total(),
                payment_method="Bank Transfer"
            )
        else:
            manager.update_invoice_status(inv.id, InvoiceStatus.OVERDUE)
    
    print("Created 3 additional invoices with different statuses")
    
    print_separator()
    
    # Get customer invoices
    customer_invoices = manager.get_customer_invoices(customer_id)
    
    print(f"Customer invoices ({len(customer_invoices)}):")
    for inv in customer_invoices:
        print(f"- {inv.number} ({inv.date.strftime('%Y-%m-%d')}): {inv.format_amount(inv.get_total())} - {inv.status}")
    
    print_separator()
    
    # Get invoice summary
    summary = manager.get_invoice_summary()
    
    print(f"Invoice summary:")
    print(f"Total count: {summary['total_count']}")
    print(f"Total amount: ${summary['total_amount']:.2f}")
    print(f"Total paid: ${summary['total_paid']:.2f}")
    print(f"Total due: ${summary['total_due']:.2f}")
    
    print("\nBy status:")
    for status, data in summary["by_status"].items():
        print(f"- {status}: {data['count']} invoices, ${data['amount']:.2f} total, ${data['due']:.2f} due")
    
    print("\nBy month:")
    for month, data in sorted(summary["by_month"].items()):
        print(f"- {month}: {data['count']} invoices, ${data['amount']:.2f} total, ${data['due']:.2f} due")
    
    print_separator()
    
    # Export all invoices
    print("Exporting all invoices to CSV...")
    csv_all = delivery.export_invoices(customer_invoices, format="csv", output_path="invoice_exports/all_invoices.csv")
    print(f"All invoices exported to CSV: {csv_all}")
    
    print_separator()
    
    # Get overdue invoices
    overdue_invoices = manager.get_overdue_invoices()
    
    print(f"Overdue invoices ({len(overdue_invoices)}):")
    for inv in overdue_invoices:
        print(f"- {inv.number} ({inv.date.strftime('%Y-%m-%d')}): {inv.format_amount(inv.get_total())} - {inv.status}")
    
    print_separator()
    
    print("Demo completed successfully!")


if __name__ == "__main__":
    run_demo()
