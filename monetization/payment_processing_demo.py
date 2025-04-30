"""
Payment processing demo for the pAIssive Income project.

This script demonstrates how to use the payment processing system.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from .payment_processor import PaymentProcessor
from .mock_payment_processor import MockPaymentProcessor
from .payment_processor_factory import factory


def print_separator():
    """Print a separator line."""
    print("\n" + "-" * 80 + "\n")


def run_demo():
    """Run the payment processing demo."""
    print("Payment Processing Demo")
    print_separator()

    # Create a mock payment processor
    processor = factory.create_processor(
        processor_type="mock",
        processor_id="demo",
        config={
            "name": "Demo Payment Processor",
            "success_rate": 1.0,  # Always succeed for demo
            "simulate_network_errors": False,
        },
    )

    print(f"Created payment processor: {processor}")
    print_separator()

    # Create a customer
    print("Creating customer...")
    customer = processor.create_customer(
        email="customer@example.com", name="Demo Customer", metadata={"source": "demo"}
    )

    print(f"Customer created: {customer['id']}")
    print(f"Name: {customer['name']}")
    print(f"Email: {customer['email']}")
    print_separator()

    # Create a payment method
    print("Creating payment method...")
    payment_method = processor.create_payment_method(
        customer_id=customer["id"],
        payment_type="card",
        payment_details={
            "number": "4242424242424242",  # Valid test card number
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
        },
    )

    print(f"Payment method created: {payment_method['id']}")
    print(f"Type: {payment_method['type']}")
    print(
        f"Card: {payment_method['details']['masked_number']} ({payment_method['details']['brand']})"
    )
    print(
        f"Expiration: {payment_method['details']['exp_month']}/{payment_method['details']['exp_year']}"
    )
    print_separator()

    # Process a payment
    print("Processing payment...")
    try:
        payment = processor.process_payment(
            amount=19.99,
            currency="USD",
            payment_method_id=payment_method["id"],
            description="Monthly subscription payment",
            metadata={"subscription_id": "sub_123"},
        )

        print(f"Payment processed: {payment['id']}")
        print(
            f"Amount: {processor.format_amount(payment['amount'], payment['currency'])}"
        )
        print(f"Status: {payment['status']}")
        print(f"Description: {payment['description']}")
    except ValueError as e:
        print(f"Payment failed: {e}")

    print_separator()

    # Create a subscription
    print("Creating subscription...")
    subscription = processor.create_subscription(
        customer_id=customer["id"],
        plan_id="plan_premium",
        payment_method_id=payment_method["id"],
        metadata={"promotion_code": "WELCOME"},
    )

    print(f"Subscription created: {subscription['id']}")
    print(f"Status: {subscription['status']}")
    print(
        f"Current period: {subscription['current_period_start']} to {subscription['current_period_end']}"
    )
    print_separator()

    # Update subscription
    print("Updating subscription...")
    updated_subscription = processor.update_subscription(
        subscription_id=subscription["id"],
        plan_id="plan_enterprise",
        metadata={"updated_by": "demo"},
    )

    print(f"Subscription updated: {updated_subscription['id']}")
    print(f"New plan: {updated_subscription['plan_id']}")
    print_separator()

    # Cancel subscription
    print("Canceling subscription...")
    canceled_subscription = processor.cancel_subscription(
        subscription_id=subscription["id"], cancel_at_period_end=True
    )

    print(f"Subscription canceled: {canceled_subscription['id']}")
    print(f"Cancel at period end: {canceled_subscription['cancel_at_period_end']}")
    print(f"Canceled at: {canceled_subscription['canceled_at']}")
    print_separator()

    # List payments
    print("Listing payments...")
    payments = processor.list_payments(customer_id=customer["id"])

    print(f"Found {len(payments)} payments:")
    for payment in payments:
        print(
            f"- {payment['id']}: {processor.format_amount(payment['amount'], payment['currency'])} ({payment['status']})"
        )

    print_separator()

    # List subscriptions
    print("Listing subscriptions...")
    subscriptions = processor.list_subscriptions(customer_id=customer["id"])

    print(f"Found {len(subscriptions)} subscriptions:")
    for subscription in subscriptions:
        print(
            f"- {subscription['id']}: {subscription['plan_id']} ({subscription['status']})"
        )

    print_separator()

    print("Demo completed successfully!")


if __name__ == "__main__":
    run_demo()
