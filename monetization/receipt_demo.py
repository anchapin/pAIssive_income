"""
Receipt generation demo for the pAIssive Income project.

This script demonstrates how to use the receipt generation system.
"""

from .receipt_manager import ReceiptManager
from .transaction import Transaction, TransactionStatus


def print_separator():
    """Print a separator line."""
    print("\n" + "-" * 80 + "\n")


def run_demo():
    """Run the receipt generation demo."""
    print("Receipt Generation Demo")
    print_separator()

    # Create a transaction
    transaction = Transaction(
        amount=49.99,
        currency="USD",
        customer_id="cust_demo_123",
        payment_method_id="pm_demo_456",
        description="Annual subscription payment",
        metadata={"subscription_id": "sub_demo_789"},
    )

    # Set transaction as successful
    transaction.update_status(TransactionStatus.SUCCEEDED, "Payment successful")

    print(f"Created transaction: {transaction}")
    print(f"Amount: {transaction.amount} {transaction.currency}")
    print(f"Status: {transaction.status}")

    print_separator()

    # Create a receipt manager
    manager = ReceiptManager(
        company_info={
            "name": "AI Tools Inc.",
            "address": "123 Main St, San Francisco, CA 94111",
            "email": "support@aitools.com",
            "phone": "(555) 123-4567",
            "website": "https://aitools.com",
            "logo_url": "https://example.com/logo.png",
        }
    )

    print("Generating receipt...")

    # Generate a receipt
    receipt = manager.generate_receipt(
        transaction=transaction,
        customer_info={
            "name": "Demo Customer",
            "email": "demo.customer@example.com",
            "address": "456 Oak St, San Francisco, CA 94112",
        },
        items=[
            {
                "description": "Premium Subscription (Annual)",
                "quantity": 1,
                "unit_price": 49.99,
                "tax_rate": 0.0825,  # 8.25% tax
            }
        ],
    )

    print(f"Receipt generated: {receipt}")
    print(f"Subtotal: {receipt.format_amount(receipt.get_subtotal())}")
    print(f"Tax: {receipt.format_amount(receipt.get_tax_total())}")
    print(f"Total: {receipt.format_amount(receipt.get_total())}")

    print_separator()

    # Add a custom field to the receipt
    receipt.add_custom_field("Subscription Period", "Jan 1, 2023 - Dec 31, 2023")

    # Add terms to the receipt
    receipt.set_terms("This subscription is subject to our Terms of Service and Privacy Policy.")

    # Add notes to the receipt
    receipt.set_notes(
        "Thank you for your business! Your subscription will automatically renew next year."
    )

    # Add an additional fee
    receipt.add_additional_fee("Processing Fee", 2.50)

    print("Updated receipt with additional information:")
    print(f"Total with fees: {receipt.format_amount(receipt.get_total())}")

    print_separator()

    # Save receipt to files
    print("Saving receipt to files...")

    receipt.save_to_file("receipt_demo_text.txt", format="text")
    receipt.save_to_file("receipt_demo_html.html", format="html")
    receipt.save_to_file("receipt_demo_json.json", format="json")

    print("Receipt saved to files:")
    print("- receipt_demo_text.txt")
    print("- receipt_demo_html.html")
    print("- receipt_demo_json.json")

    print_separator()

    # Display receipt in text format
    print("Receipt in text format:")
    print("-" * 80)
    print(receipt.to_text())

    print_separator()

    # Simulate sending receipt by email
    print("Sending receipt by email...")

    manager.send_receipt(
        receipt_id=receipt.id,
        email="demo.customer@example.com",
        subject="Your AI Tools Inc. Receipt",
        message="Thank you for your purchase! Please find your receipt attached.",
        format="html",
    )

    print_separator()

    # Create a receipt with multiple items
    print("Creating a receipt with multiple items...")

    # Create another transaction
    transaction2 = Transaction(
        amount=79.98,
        currency="USD",
        customer_id="cust_demo_123",
        payment_method_id="pm_demo_456",
        description="Software purchase",
        metadata={"order_id": "order_demo_123"},
    )

    # Set transaction as successful
    transaction2.update_status(TransactionStatus.SUCCEEDED, "Payment successful")

    # Generate a receipt with multiple items
    receipt2 = manager.generate_receipt(
        transaction=transaction2,
        customer_info={
            "name": "Demo Customer",
            "email": "demo.customer@example.com",
            "address": "456 Oak St, San Francisco, CA 94112",
        },
        items=[
            {
                "description": "AI Content Generator",
                "quantity": 1,
                "unit_price": 49.99,
                "tax_rate": 0.0825,
            },
            {
                "description": "Premium Templates Pack",
                "quantity": 1,
                "unit_price": 29.99,
                "tax_rate": 0.0825,
            },
            {
                "description": "Loyalty Discount",
                "quantity": 1,
                "unit_price": 0,
                "discount": 10.00,
                "tax_rate": 0,
            },
        ],
    )

    print(f"Receipt generated: {receipt2}")
    print(f"Items: {len(receipt2.items)}")
    print(f"Subtotal: {receipt2.format_amount(receipt2.get_subtotal())}")
    print(f"Discount: {receipt2.format_amount(receipt2.get_discount_total())}")
    print(f"Tax: {receipt2.format_amount(receipt2.get_tax_total())}")
    print(f"Total: {receipt2.format_amount(receipt2.get_total())}")

    print_separator()

    # Get customer receipts
    customer_receipts = manager.get_customer_receipts("cust_demo_123")

    print(f"Customer receipts ({len(customer_receipts)}):")
    for r in customer_receipts:
        print(f"- {r}")

    print_separator()

    print("Demo completed successfully!")


if __name__ == "__main__":
    run_demo()
