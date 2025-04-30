"""
Transaction manager for the pAIssive Income project.

This module provides a class for managing payment transactions, including
storage, retrieval, and processing.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import os
import copy

from common_utils import (
    file_exists,
    create_directory,
    get_file_path,
    load_from_json_file,
    is_date_in_range,
)
from .transaction import Transaction, TransactionStatus, TransactionType
from .payment_method import PaymentMethod
from .payment_method_manager import PaymentMethodManager
from .payment_processor import PaymentProcessor


class TransactionManager:
    """
    Class for managing payment transactions.

    This class provides methods for storing, retrieving, and processing
    payment transactions.
    """

    def __init__(
        self,
        payment_processor: Optional[PaymentProcessor] = None,
        payment_method_manager: Optional[PaymentMethodManager] = None,
        storage_dir: Optional[str] = None,
    ):
        """
        Initialize a transaction manager.

        Args:
            payment_processor: Payment processor to use
            payment_method_manager: Payment method manager to use
            storage_dir: Directory for storing transaction data
        """
        self.payment_processor = payment_processor
        self.payment_method_manager = payment_method_manager
        self.storage_dir = storage_dir

        if storage_dir:
            create_directory(storage_dir)

        self.transactions = {}
        self.customer_transactions = {}

        # Load transactions if storage directory is set
        if storage_dir:
            self.load_transactions()

    def create_transaction(
        self,
        amount: float,
        currency: str,
        customer_id: str,
        payment_method_id: str,
        description: str,
        transaction_type: str = TransactionType.CHARGE,
        metadata: Optional[Dict[str, Any]] = None,
        auto_process: bool = False,
    ) -> Transaction:
        """
        Create a transaction.

        Args:
            amount: Amount of the transaction
            currency: Currency code (e.g., USD)
            customer_id: ID of the customer
            payment_method_id: ID of the payment method
            description: Description of the transaction
            transaction_type: Type of transaction
            metadata: Additional metadata for the transaction
            auto_process: Whether to automatically process the transaction

        Returns:
            The created transaction
        """
        # Create transaction
        transaction = Transaction(
            amount=amount,
            currency=currency,
            customer_id=customer_id,
            payment_method_id=payment_method_id,
            description=description,
            transaction_type=transaction_type,
            metadata=metadata,
        )

        # Store transaction
        self.transactions[transaction.id] = transaction

        # Add to customer's transactions
        if customer_id not in self.customer_transactions:
            self.customer_transactions[customer_id] = []

        self.customer_transactions[customer_id].append(transaction.id)

        # Save transaction if storage directory is set
        if self.storage_dir:
            self._save_transaction(transaction)

        # Process transaction if requested
        if auto_process:
            self.process_transaction(transaction.id)

        return transaction

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """
        Get a transaction by ID.

        Args:
            transaction_id: ID of the transaction

        Returns:
            The transaction or None if not found
        """
        return self.transactions.get(transaction_id)

    def get_customer_transactions(
        self,
        customer_id: str,
        status: Optional[str] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Transaction]:
        """
        Get transactions for a customer.

        Args:
            customer_id: ID of the customer
            status: Status of transactions to get
            transaction_type: Type of transactions to get
            start_date: Start date for transactions
            end_date: End date for transactions
            limit: Maximum number of transactions to return

        Returns:
            List of transactions
        """
        if customer_id not in self.customer_transactions:
            return []

        transactions = []

        for transaction_id in self.customer_transactions[customer_id]:
            transaction = self.transactions.get(transaction_id)

            if not transaction:
                continue

            # Filter by status
            if status and transaction.status != status:
                continue

            # Filter by transaction type
            if transaction_type and transaction.transaction_type != transaction_type:
                continue

            # Filter by date range
            if not is_date_in_range(
                transaction.created_at,
                start_date or datetime.min,
                end_date or datetime.max,
            ):
                continue

            transactions.append(transaction)

        # Sort by created_at (newest first)
        transactions.sort(key=lambda t: t.created_at, reverse=True)

        # Apply limit
        return transactions[:limit]

    def process_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """
        Process a transaction.

        Args:
            transaction_id: ID of the transaction

        Returns:
            The updated transaction or None if not found
        """
        # Check if transaction exists
        transaction = self.get_transaction(transaction_id)

        if not transaction:
            return None

        # Check if transaction is already processed
        if not transaction.is_pending():
            return transaction

        # Check if payment processor is available
        if not self.payment_processor:
            transaction.set_error(
                "processor_unavailable", "Payment processor is not available"
            )

            # Save transaction if storage directory is set
            if self.storage_dir:
                self._save_transaction(transaction)

            return transaction

        # Update status to processing
        transaction.update_status(TransactionStatus.PROCESSING, "Processing payment")

        try:
            # Process payment
            if transaction.transaction_type == TransactionType.CHARGE:
                payment_result = self.payment_processor.process_payment(
                    amount=transaction.amount,
                    currency=transaction.currency,
                    payment_method_id=transaction.payment_method_id,
                    description=transaction.description,
                    metadata=transaction.metadata,
                )

                # Update transaction status
                transaction.update_status(
                    TransactionStatus.SUCCEEDED, "Payment successful"
                )

                # Add payment ID to metadata
                transaction.metadata["payment_id"] = payment_result["id"]

            elif transaction.transaction_type == TransactionType.REFUND:
                # Check if parent transaction exists
                parent_id = transaction.parent_id

                if not parent_id or parent_id not in self.transactions:
                    transaction.set_error(
                        "parent_not_found", "Parent transaction not found"
                    )
                    return transaction

                parent_transaction = self.transactions[parent_id]

                # Check if parent transaction has a payment ID
                payment_id = parent_transaction.metadata.get("payment_id")

                if not payment_id:
                    transaction.set_error(
                        "payment_id_not_found",
                        "Payment ID not found in parent transaction",
                    )
                    return transaction

                # Process refund
                refund_result = self.payment_processor.refund_payment(
                    payment_id=payment_id,
                    amount=transaction.amount,
                    reason=transaction.metadata.get("reason"),
                )

                # Update transaction status
                transaction.update_status(
                    TransactionStatus.SUCCEEDED, "Refund successful"
                )

                # Add refund ID to metadata
                transaction.metadata["refund_id"] = refund_result["id"]

                # Update parent transaction
                parent_transaction.add_refund(
                    amount=transaction.amount,
                    reason=transaction.metadata.get("reason"),
                    metadata={"refund_transaction_id": transaction.id},
                )

                # Save parent transaction if storage directory is set
                if self.storage_dir:
                    self._save_transaction(parent_transaction)

            else:
                transaction.set_error(
                    "unsupported_transaction_type",
                    f"Unsupported transaction type: {transaction.transaction_type}",
                )

        except Exception as e:
            # Handle payment error
            transaction.set_error("payment_failed", str(e))

        # Save transaction if storage directory is set
        if self.storage_dir:
            self._save_transaction(transaction)

        return transaction

    def refund_transaction(
        self,
        transaction_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Transaction]:
        """
        Refund a transaction.

        Args:
            transaction_id: ID of the transaction to refund
            amount: Amount to refund (if None, refund the full amount)
            reason: Reason for the refund
            metadata: Additional metadata for the refund

        Returns:
            The refund transaction or None if the original transaction is not found
        """
        # Check if transaction exists
        transaction = self.get_transaction(transaction_id)

        if not transaction:
            return None

        # Check if transaction is refundable
        if not transaction.is_successful():
            raise ValueError(f"Transaction is not refundable: {transaction.status}")

        # Determine refund amount
        refund_amount = amount if amount is not None else transaction.get_net_amount()

        # Check if refund amount is valid
        if refund_amount <= 0:
            raise ValueError("Refund amount must be positive")

        if refund_amount > transaction.get_net_amount():
            raise ValueError(
                f"Cannot refund more than the net amount ({transaction.get_net_amount()})"
            )

        # Create refund metadata
        refund_metadata = {
            "parent_transaction_id": transaction_id,
            "reason": reason or "requested_by_customer",
        }

        if metadata:
            refund_metadata.update(metadata)

        # Create refund transaction
        refund_transaction = self.create_transaction(
            amount=refund_amount,
            currency=transaction.currency,
            customer_id=transaction.customer_id,
            payment_method_id=transaction.payment_method_id,
            description=f"Refund: {transaction.description}",
            transaction_type=TransactionType.REFUND,
            metadata=refund_metadata,
        )

        # Set parent ID
        refund_transaction.parent_id = transaction_id

        # Process refund
        return self.process_transaction(refund_transaction.id)

    def get_transaction_history(self, transaction_id: str) -> List[Dict[str, Any]]:
        """
        Get the history of a transaction.

        Args:
            transaction_id: ID of the transaction

        Returns:
            List of status changes with timestamps and reasons
        """
        transaction = self.get_transaction(transaction_id)

        if not transaction:
            return []

        return transaction.status_history

    def get_related_transactions(self, transaction_id: str) -> List[Transaction]:
        """
        Get transactions related to a transaction.

        Args:
            transaction_id: ID of the transaction

        Returns:
            List of related transactions
        """
        transaction = self.get_transaction(transaction_id)

        if not transaction:
            return []

        related_transactions = []

        # If this is a parent transaction, find refund transactions
        for t in self.transactions.values():
            if t.parent_id == transaction_id:
                related_transactions.append(t)

        # If this is a refund transaction, find the parent transaction
        if transaction.parent_id:
            parent = self.get_transaction(transaction.parent_id)

            if parent:
                related_transactions.append(parent)

        return related_transactions

    def get_transaction_summary(
        self,
        customer_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get a summary of transactions.

        Args:
            customer_id: ID of the customer (if None, summarize all transactions)
            start_date: Start date for transactions
            end_date: End date for transactions

        Returns:
            Dictionary with transaction summary
        """
        # Get transactions to summarize
        if customer_id:
            transactions = self.get_customer_transactions(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date,
                limit=1000,  # Use a high limit to get all transactions
            )
        else:
            transactions = list(self.transactions.values())

            # Filter by date range
            if start_date or end_date:
                filtered_transactions = []

                for transaction in transactions:
                    if not is_date_in_range(
                        transaction.created_at,
                        start_date or datetime.min,
                        end_date or datetime.max,
                    ):
                        continue

                    filtered_transactions.append(transaction)

                transactions = filtered_transactions

        # Initialize summary
        summary = {
            "total_count": len(transactions),
            "successful_count": 0,
            "failed_count": 0,
            "pending_count": 0,
            "refunded_count": 0,
            "total_amount": 0.0,
            "refunded_amount": 0.0,
            "net_amount": 0.0,
            "currencies": {},
            "by_status": {},
            "by_type": {},
        }

        # Calculate summary
        for transaction in transactions:
            # Skip refund transactions (they're counted in the refunded_amount)
            if transaction.transaction_type == TransactionType.REFUND:
                continue

            # Count by status
            if transaction.status not in summary["by_status"]:
                summary["by_status"][transaction.status] = 0

            summary["by_status"][transaction.status] += 1

            # Count by type
            if transaction.transaction_type not in summary["by_type"]:
                summary["by_type"][transaction.transaction_type] = 0

            summary["by_type"][transaction.transaction_type] += 1

            # Count by success/failure
            if transaction.is_successful():
                summary["successful_count"] += 1
            elif transaction.is_failed():
                summary["failed_count"] += 1
            elif transaction.is_pending():
                summary["pending_count"] += 1

            # Count refunded transactions
            if transaction.is_refunded() or transaction.is_partially_refunded():
                summary["refunded_count"] += 1

            # Track amounts by currency
            if transaction.currency not in summary["currencies"]:
                summary["currencies"][transaction.currency] = {
                    "total_amount": 0.0,
                    "refunded_amount": 0.0,
                    "net_amount": 0.0,
                }

            # Add amounts
            if transaction.is_successful():
                summary["currencies"][transaction.currency][
                    "total_amount"
                ] += transaction.amount
                summary["currencies"][transaction.currency][
                    "refunded_amount"
                ] += transaction.get_refunded_amount()
                summary["currencies"][transaction.currency][
                    "net_amount"
                ] += transaction.get_net_amount()

                summary["total_amount"] += transaction.amount
                summary["refunded_amount"] += transaction.get_refunded_amount()
                summary["net_amount"] += transaction.get_net_amount()

        return summary

    def delete_transaction(self, transaction_id: str) -> bool:
        """
        Delete a transaction.

        Args:
            transaction_id: ID of the transaction

        Returns:
            True if the transaction was deleted, False otherwise
        """
        # Check if transaction exists
        transaction = self.get_transaction(transaction_id)

        if not transaction:
            return False

        # Remove from customer's transactions
        customer_id = transaction.customer_id

        if customer_id in self.customer_transactions:
            if transaction_id in self.customer_transactions[customer_id]:
                self.customer_transactions[customer_id].remove(transaction_id)

        # Remove from transactions
        del self.transactions[transaction_id]

        # Delete file if storage directory is set
        if self.storage_dir:
            file_path = os.path.join(self.storage_dir, f"{transaction_id}.json")

            if os.path.exists(file_path):
                os.remove(file_path)

        return True

    def load_transactions(self) -> None:
        """
        Load transactions from storage directory.
        """
        if not self.storage_dir or not file_exists(self.storage_dir):
            return

        # Clear existing data
        self.transactions = {}
        self.customer_transactions = {}

        # Load transactions
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                file_path = get_file_path(self.storage_dir, filename)

                try:
                    # Load transaction data
                    data = load_from_json_file(file_path)

                    # Create transaction
                    transaction = Transaction.from_dict(data)

                    # Store transaction
                    self.transactions[transaction.id] = transaction

                    # Add to customer's transactions
                    customer_id = transaction.customer_id

                    if customer_id not in self.customer_transactions:
                        self.customer_transactions[customer_id] = []

                    self.customer_transactions[customer_id].append(transaction.id)

                except Exception as e:
                    print(f"Error loading transaction from {file_path}: {e}")

    def _save_transaction(self, transaction: Transaction) -> None:
        """
        Save a transaction to the storage directory.

        Args:
            transaction: Transaction to save
        """
        if not self.storage_dir:
            return

        file_path = get_file_path(self.storage_dir, f"{transaction.id}.json")
        transaction.save_to_file(file_path)


# Example usage
if __name__ == "__main__":
    from .mock_payment_processor import MockPaymentProcessor

    # Create a payment processor
    processor = MockPaymentProcessor({"name": "Test Processor", "success_rate": 0.95})

    # Create a transaction manager
    manager = TransactionManager(
        payment_processor=processor, storage_dir="transactions"
    )

    # Create a transaction
    transaction = manager.create_transaction(
        amount=19.99,
        currency="USD",
        customer_id="cust_123",
        payment_method_id="pm_456",
        description="Monthly subscription payment",
        metadata={"subscription_id": "sub_789"},
    )

    print(f"Transaction created: {transaction}")
    print(f"Amount: {transaction.format_amount()}")
    print(f"Status: {transaction.status}")

    # Process the transaction
    processed_transaction = manager.process_transaction(transaction.id)

    print(f"\nProcessed transaction: {processed_transaction}")
    print(f"Status: {processed_transaction.status}")

    if processed_transaction.is_successful():
        print("Payment was successful!")
    elif processed_transaction.error:
        print(f"Payment failed: {processed_transaction.error['message']}")

    # If successful, create a partial refund
    if processed_transaction.is_successful():
        refund_transaction = manager.refund_transaction(
            transaction_id=transaction.id, amount=5.00, reason="Customer request"
        )

        print(f"\nRefund transaction: {refund_transaction}")
        print(f"Status: {refund_transaction.status}")

        # Get related transactions
        related = manager.get_related_transactions(transaction.id)

        print(f"\nRelated transactions ({len(related)}):")
        for t in related:
            print(f"- {t}")

        # Get transaction history
        history = manager.get_transaction_history(transaction.id)

        print(f"\nTransaction history:")
        for entry in history:
            print(f"- {entry['timestamp']}: {entry['status']} ({entry['reason']})")

    # Get transaction summary
    summary = manager.get_transaction_summary()

    print(f"\nTransaction Summary:")
    print(f"Total count: {summary['total_count']}")
    print(f"Successful: {summary['successful_count']}")
    print(f"Failed: {summary['failed_count']}")
    print(f"Pending: {summary['pending_count']}")
    print(f"Refunded: {summary['refunded_count']}")
    print(f"Total amount: ${summary['total_amount']:.2f}")
    print(f"Refunded amount: ${summary['refunded_amount']:.2f}")
    print(f"Net amount: ${summary['net_amount']:.2f}")
