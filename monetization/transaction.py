"""
Transaction handling for the pAIssive Income project.

This module provides classes for managing payment transactions, including
creation, processing, and status tracking.
"""


import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional


class TransactionStatus

:
    """Enumeration of transaction statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    CANCELED = "canceled"


class TransactionType:
    """Enumeration of transaction types."""

    CHARGE = "charge"
    REFUND = "refund"
    AUTHORIZATION = "authorization"
    CAPTURE = "capture"
    VOID = "void"


class Transaction:
    """
    Class for managing payment transactions.

    This class provides methods for creating, processing, and tracking
    payment transactions.
    """

    def __init__(
        self,
        amount: float,
        currency: str,
        customer_id: str,
        payment_method_id: str,
        description: str,
        transaction_type: str = TransactionType.CHARGE,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a transaction.

        Args:
            amount: Amount of the transaction
            currency: Currency code (e.g., USD)
            customer_id: ID of the customer
            payment_method_id: ID of the payment method
            description: Description of the transaction
            transaction_type: Type of transaction
            metadata: Additional metadata for the transaction
        """
        self.id = str(uuid.uuid4())
        self.amount = amount
        self.currency = currency
        self.customer_id = customer_id
        self.payment_method_id = payment_method_id
        self.description = description
        self.transaction_type = transaction_type
        self.metadata = metadata or {}

        # Set initial status
        self.status = TransactionStatus.PENDING

        # Initialize other properties
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.processed_at = None
        self.error = None
        self.refunds = []
        self.parent_id = None
        self.status_history = [
            {
                "status": self.status,
                "timestamp": self.created_at.isoformat(),
                "reason": "Transaction created",
            }
        ]

    def update_status(self, status: str, reason: Optional[str] = None) -> None:
        """
        Update the transaction status.

        Args:
            status: New status
            reason: Reason for the status change
        """
        old_status = self.status
        self.status = status
        self.updated_at = datetime.now()

        # Add status history entry
        self.status_history.append(
            {
                "status": status,
                "timestamp": self.updated_at.isoformat(),
                "reason": reason or f"Status changed from {old_status} to {status}",
            }
        )

        # Set processed_at if the transaction is now complete
        if (
            status in [TransactionStatus.SUCCEEDED, TransactionStatus.FAILED]
            and not self.processed_at
        ):
            self.processed_at = self.updated_at

    def set_error(self, error_code: str, error_message: str) -> None:
        """
        Set an error on the transaction.

        Args:
            error_code: Error code
            error_message: Error message
        """
        self.error = {
            "code": error_code,
            "message": error_message,
            "timestamp": datetime.now().isoformat(),
        }

        # Update status to failed
        self.update_status(TransactionStatus.FAILED, f"Error: {error_message}")

    def add_refund(
        self,
        amount: float,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a refund to the transaction.

        Args:
            amount: Amount to refund
            reason: Reason for the refund
            metadata: Additional metadata for the refund

        Returns:
            Dictionary with refund information
        """
        # Validate refund amount
        if amount <= 0:
            raise ValueError("Refund amount must be positive")

        # Calculate total refunded amount
        total_refunded = sum(refund["amount"] for refund in self.refunds)

        if total_refunded + amount > self.amount:
            raise ValueError(
                f"Cannot refund more than the transaction amount ({self.amount})"
            )

        # Create refund
        refund = {
            "id": str(uuid.uuid4()),
            "amount": amount,
            "currency": self.currency,
            "reason": reason or "requested_by_customer",
            "status": TransactionStatus.SUCCEEDED,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        # Add refund to list
        self.refunds.append(refund)

        # Update transaction status
        if total_refunded + amount == self.amount:
            self.update_status(TransactionStatus.REFUNDED, "Fully refunded")
        else:
            self.update_status(
                TransactionStatus.PARTIALLY_REFUNDED, "Partially refunded"
            )

        return refund

    def get_refunded_amount(self) -> float:
        """
        Get the total refunded amount.

        Returns:
            Total refunded amount
        """
        return sum(refund["amount"] for refund in self.refunds)

    def get_net_amount(self) -> float:
        """
        Get the net amount after refunds.

        Returns:
            Net amount
        """
        return self.amount - self.get_refunded_amount()

    def is_refundable(self) -> bool:
        """
        Check if the transaction is refundable.

        Returns:
            True if the transaction is refundable, False otherwise
        """
        # Transaction must be successful and not fully refunded
        if self.status not in [
            TransactionStatus.SUCCEEDED,
            TransactionStatus.PARTIALLY_REFUNDED,
        ]:
            return False

        # Transaction must have a positive net amount
        return self.get_net_amount() > 0

    def is_successful(self) -> bool:
        """
        Check if the transaction was successful.

        Returns:
            True if the transaction was successful, False otherwise
        """
        return self.status in [
            TransactionStatus.SUCCEEDED,
            TransactionStatus.PARTIALLY_REFUNDED,
            TransactionStatus.REFUNDED,
        ]

    def is_pending(self) -> bool:
        """
        Check if the transaction is pending.

        Returns:
            True if the transaction is pending, False otherwise
        """
        return self.status in [TransactionStatus.PENDING, TransactionStatus.PROCESSING]

    def is_failed(self) -> bool:
        """
        Check if the transaction failed.

        Returns:
            True if the transaction failed, False otherwise
        """
        return self.status in [TransactionStatus.FAILED, TransactionStatus.CANCELED]

    def is_refunded(self) -> bool:
        """
        Check if the transaction is refunded.

        Returns:
            True if the transaction is refunded, False otherwise
        """
        return self.status == TransactionStatus.REFUNDED

    def is_partially_refunded(self) -> bool:
        """
        Check if the transaction is partially refunded.

        Returns:
            True if the transaction is partially refunded, False otherwise
        """
        return self.status == TransactionStatus.PARTIALLY_REFUNDED

    def format_amount(self) -> str:
        """
        Format the transaction amount with currency symbol.

        Returns:
            Formatted amount with currency symbol
        """
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CAD": "C$",
            "AUD": "A$",
        }

        symbol = currency_symbols.get(self.currency, self.currency)

        if self.currency == "JPY":
            # JPY doesn't use decimal places
            return f"{symbol}{int(self.amount):,}"
        else:
            return f"{symbol}{self.amount:,.2f}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the transaction to a dictionary.

        Returns:
            Dictionary representation of the transaction
        """
        return {
            "id": self.id,
            "amount": self.amount,
            "currency": self.currency,
            "customer_id": self.customer_id,
            "payment_method_id": self.payment_method_id,
            "description": self.description,
            "transaction_type": self.transaction_type,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "processed_at": (
                self.processed_at.isoformat() if self.processed_at else None
            ),
            "error": self.error,
            "refunds": self.refunds,
            "parent_id": self.parent_id,
            "metadata": self.metadata,
            "status_history": self.status_history,
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the transaction to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the transaction
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """
        Create a transaction from a dictionary.

        Args:
            data: Dictionary with transaction data

        Returns:
            Transaction instance
        """
        # Create a new transaction
        transaction = cls(
            amount=data["amount"],
            currency=data["currency"],
            customer_id=data["customer_id"],
            payment_method_id=data["payment_method_id"],
            description=data["description"],
            transaction_type=data["transaction_type"],
            metadata=data.get("metadata", {}),
        )

        # Set additional fields
        transaction.id = data["id"]
        transaction.status = data["status"]
        transaction.created_at = datetime.fromisoformat(data["created_at"])
        transaction.updated_at = datetime.fromisoformat(data["updated_at"])

        if data.get("processed_at"):
            transaction.processed_at = datetime.fromisoformat(data["processed_at"])

        transaction.error = data.get("error")
        transaction.refunds = data.get("refunds", [])
        transaction.parent_id = data.get("parent_id")
        transaction.status_history = data.get("status_history", [])

        return transaction

    def __str__(self) -> str:
        """String representation of the transaction."""
        return f"Transaction({self.id}, {self.format_amount()}, {self.status})"

    def __repr__(self) -> str:
        """Detailed string representation of the transaction."""
        return f"Transaction(id={self.id}, amount={self.amount}, currency={self.currency}, status={self.status})"


# Example usage
if __name__ == "__main__":
    # Create a transaction
    transaction = Transaction(
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
    transaction.update_status(TransactionStatus.PROCESSING, "Processing payment")
    print(f"\nUpdated status: {transaction.status}")

    # Simulate successful payment
    transaction.update_status(TransactionStatus.SUCCEEDED, "Payment successful")
    print(f"Updated status: {transaction.status}")
    print(f"Processed at: {transaction.processed_at}")

    # Add a partial refund
    refund = transaction.add_refund(
        amount=5.00,
        reason="Customer request",
        metadata={"refund_reason": "partial_dissatisfaction"},
    )

    print(f"\nRefund added: {refund['id']}")
    print(f"Refund amount: ${refund['amount']:.2f}")
    print(f"Transaction status: {transaction.status}")
    print(f"Refunded amount: ${transaction.get_refunded_amount():.2f}")
    print(f"Net amount: ${transaction.get_net_amount():.2f}")

    # Add another refund to fully refund the transaction
    refund = transaction.add_refund(amount=14.99, reason="Customer cancellation")

    print(f"\nSecond refund added: {refund['id']}")
    print(f"Transaction status: {transaction.status}")
    print(f"Refunded amount: ${transaction.get_refunded_amount():.2f}")
    print(f"Net amount: ${transaction.get_net_amount():.2f}")

    # Check if the transaction is refundable
    print(f"\nIs refundable: {transaction.is_refundable()}")

    # Convert to dictionary and back
    transaction_dict = transaction.to_dict()
    print(f"\nTransaction dictionary: {transaction_dict}")

    restored_transaction = Transaction.from_dict(transaction_dict)
    print(f"Restored transaction: {restored_transaction}")
    print(f"Is same ID: {restored_transaction.id == transaction.id}")