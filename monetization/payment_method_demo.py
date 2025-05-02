"""
Payment method management demo for the pAIssive Income project.

This script demonstrates how to use the payment method management system.
"""

from .payment_method import PaymentMethod
from .payment_method_manager import PaymentMethodManager


def print_separator():
    """Print a separator line."""
    print("\n" + "-" * 80 + "\n")


def run_demo():
    """Run the payment method management demo."""
    print("Payment Method Management Demo")
    print_separator()

    # Create a payment method manager
    manager = PaymentMethodManager()

    print("Creating payment methods for a customer...")

    # Create a customer ID
    customer_id = "cust_demo_123"

    # Add a credit card payment method
    card_payment = manager.add_payment_method(
        customer_id=customer_id,
        payment_type=PaymentMethod.TYPE_CARD,
        payment_details={
            "number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "name": "Demo Customer",
        },
        set_as_default=True,
        metadata={"source": "demo"},
    )

    print(f"Added card payment method: {card_payment}")
    print(f"Card details: {card_payment.details}")
    print(f"Is default: {card_payment.is_default}")

    # Add a bank account payment method
    bank_payment = manager.add_payment_method(
        customer_id=customer_id,
        payment_type=PaymentMethod.TYPE_BANK_ACCOUNT,
        payment_details={
            "account_number": "000123456789",
            "routing_number": "110000000",
            "account_type": "checking",
            "bank_name": "Demo Bank",
            "name": "Demo Customer",
        },
        metadata={"source": "demo"},
    )

    print(f"\nAdded bank payment method: {bank_payment}")
    print(f"Bank details: {bank_payment.details}")
    print(f"Is default: {bank_payment.is_default}")

    # Add a PayPal payment method
    paypal_payment = manager.add_payment_method(
        customer_id=customer_id,
        payment_type=PaymentMethod.TYPE_PAYPAL,
        payment_details={
            "email": "demo.customer@example.com",
            "account_id": "paypal_123",
        },
        metadata={"source": "demo"},
    )

    print(f"\nAdded PayPal payment method: {paypal_payment}")
    print(f"PayPal details: {paypal_payment.details}")
    print(f"Is default: {paypal_payment.is_default}")

    print_separator()

    # Get all payment methods for the customer
    payment_methods = manager.get_customer_payment_methods(customer_id)

    print(f"Customer payment methods ({len(payment_methods)}):")
    for pm in payment_methods:
        default_str = " (default)" if pm.is_default else ""
        print(f"- {pm}{default_str}")

    print_separator()

    # Get default payment method
    default_pm = manager.get_default_payment_method(customer_id)

    print(f"Default payment method: {default_pm}")

    # Set bank account as default
    print("\nSetting bank account as default...")
    updated_pm = manager.set_default_payment_method(customer_id, bank_payment.id)

    print(f"Updated payment method: {updated_pm}")
    print(f"Is default: {updated_pm.is_default}")

    # Get new default payment method
    default_pm = manager.get_default_payment_method(customer_id)

    print(f"\nNew default payment method: {default_pm}")

    print_separator()

    # Update payment method
    print("Updating card payment method...")
    updated_pm = manager.update_payment_method(
        payment_method_id=card_payment.id,
        payment_details={"exp_month": 11, "exp_year": 2031},
        metadata={"updated": True},
    )

    print(f"Updated payment method: {updated_pm}")
    print(
        f"New expiration: {updated_pm.details['exp_month']}/{updated_pm.details['exp_year']}"
    )
    print(f"Metadata: {updated_pm.metadata}")

    print_separator()

    # Check for expiring payment methods
    print("Checking for payment methods expiring in the next 5 years...")
    expiring_pms = manager.check_for_expiring_payment_methods(days=365 * 5)  # 5 years

    if expiring_pms:
        print("Expiring payment methods:")
        for cust_id, pms in expiring_pms.items():
            print(f"Customer {cust_id}:")
            for pm in pms:
                if pm.payment_type == PaymentMethod.TYPE_CARD:
                    print(
                        f"- {pm} (expires {pm.details['exp_month']}/{pm.details['exp_year']})"
                    )
    else:
        print("No payment methods expiring in the next 5 years.")

    print_separator()

    # Delete a payment method
    print("Deleting PayPal payment method...")
    deleted = manager.delete_payment_method(paypal_payment.id)

    print(f"Deleted payment method: {deleted}")

    # Get remaining payment methods
    payment_methods = manager.get_customer_payment_methods(customer_id)

    print(f"\nRemaining payment methods ({len(payment_methods)}):")
    for pm in payment_methods:
        default_str = " (default)" if pm.is_default else ""
        print(f"- {pm}{default_str}")

    print_separator()

    # Delete all customer payment methods
    print("Deleting all payment methods for the customer...")
    deleted_count = manager.delete_customer_payment_methods(customer_id)

    print(f"Deleted {deleted_count} payment methods for customer")

    # Verify all payment methods are deleted
    payment_methods = manager.get_customer_payment_methods(customer_id)

    print(f"Remaining payment methods: {len(payment_methods)}")

    print_separator()

    print("Demo completed successfully!")


if __name__ == "__main__":
    run_demo()
