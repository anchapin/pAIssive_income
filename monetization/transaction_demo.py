"""
"""
Transaction management demo for the pAIssive Income project.
Transaction management demo for the pAIssive Income project.


This script demonstrates how to use the transaction management system.
This script demonstrates how to use the transaction management system.
"""
"""




from .mock_payment_processor import MockPaymentProcessor
from .mock_payment_processor import MockPaymentProcessor
from .transaction_manager import TransactionManager
from .transaction_manager import TransactionManager




def print_separator():
    def print_separator():
    ():
    ():
    """Print a separator line."""
    print("\n" + "-" * 80 + "\n")


    def run_demo():
    """Run the transaction management demo."""
    print("Transaction Management Demo")
    print_separator()

    # Create a payment processor
    processor = MockPaymentProcessor(
    {
    "name": "Demo Processor",
    "success_rate": 1.0,  # Always succeed for demo
    "simulate_network_errors": False,
    }
    )

    # Create a transaction manager
    manager = TransactionManager(payment_processor=processor)

    print("Creating and processing transactions...")

    # Create customer and payment method IDs
    customer_id = "cust_demo_123"
    payment_method_id = "pm_demo_456"

    # Create a transaction
    transaction = manager.create_transaction(
    amount=29.99,
    currency="USD",
    customer_id=customer_id,
    payment_method_id=payment_method_id,
    description="Premium subscription payment",
    metadata={"subscription_id": "sub_demo_789"},
    )

    print(f"Transaction created: {transaction}")
    print(f"Amount: {transaction.format_amount()}")
    print(f"Status: {transaction.status}")

    # Process the transaction
    print("\nProcessing transaction...")
    processed_transaction = manager.process_transaction(transaction.id)

    print(f"Processed transaction: {processed_transaction}")
    print(f"Status: {processed_transaction.status}")

    if processed_transaction.is_successful():
    print("Payment was successful!")
    elif processed_transaction.error:
    print(f"Payment failed: {processed_transaction.error['message']}")

    print_separator()

    # Create another transaction
    transaction2 = manager.create_transaction(
    amount=9.99,
    currency="USD",
    customer_id=customer_id,
    payment_method_id=payment_method_id,
    description="Add-on purchase",
    metadata={"product_id": "prod_demo_123"},
    )

    print(f"Second transaction created: {transaction2}")

    # Process the transaction
    processed_transaction2 = manager.process_transaction(transaction2.id)

    print(f"Processed transaction: {processed_transaction2}")
    print(f"Status: {processed_transaction2.status}")

    print_separator()

    # Get customer transactions
    transactions = manager.get_customer_transactions(customer_id)

    print(f"Customer transactions ({len(transactions)}):")
    for t in transactions:
    print(f"- {t}")

    print_separator()

    # Create a partial refund for the first transaction
    print("Creating a partial refund...")
    refund_transaction = manager.refund_transaction(
    transaction_id=transaction.id, amount=10.00, reason="Customer request"
    )

    print(f"Refund transaction: {refund_transaction}")
    print(f"Status: {refund_transaction.status}")

    # Get the original transaction to see the updated status
    updated_transaction = manager.get_transaction(transaction.id)

    print(f"\nOriginal transaction after refund: {updated_transaction}")
    print(f"Status: {updated_transaction.status}")
    print(f"Refunded amount: {updated_transaction.get_refunded_amount():.2f}")
    print(f"Net amount: {updated_transaction.get_net_amount():.2f}")

    print_separator()

    # Get related transactions
    related = manager.get_related_transactions(transaction.id)

    print(f"Transactions related to {transaction.id} ({len(related)}):")
    for t in related:
    print(f"- {t}")

    print_separator()

    # Get transaction history
    history = manager.get_transaction_history(transaction.id)

    print(f"Transaction history for {transaction.id}:")
    for entry in history:
    print(f"- {entry['timestamp']}: {entry['status']} ({entry['reason']})")

    print_separator()

    # Get transaction summary
    summary = manager.get_transaction_summary()

    print("Transaction Summary:")
    print(f"Total count: {summary['total_count']}")
    print(f"Successful: {summary['successful_count']}")
    print(f"Failed: {summary['failed_count']}")
    print(f"Pending: {summary['pending_count']}")
    print(f"Refunded: {summary['refunded_count']}")

    for currency, amounts in summary["currencies"].items():
    print(f"\n{currency} Amounts:")
    print(f"Total: {amounts['total_amount']:.2f}")
    print(f"Refunded: {amounts['refunded_amount']:.2f}")
    print(f"Net: {amounts['net_amount']:.2f}")

    print_separator()

    print("Demo completed successfully!")


    if __name__ == "__main__":
    run_demo()