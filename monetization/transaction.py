"""
"""
Transaction handling for the pAIssive Income project.
Transaction handling for the pAIssive Income project.


This module provides classes for managing payment transactions, including
This module provides classes for managing payment transactions, including
creation, processing, and status tracking.
creation, processing, and status tracking.
"""
"""




import json
import json
import uuid
import uuid
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional




class TransactionStatus:
    class TransactionStatus:


    pass  # Added missing block
    pass  # Added missing block
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

    CHARGE = "charge"
    REFUND = "refund"
    AUTHORIZATION = "authorization"
    CAPTURE = "capture"
    VOID = "void"


    class Transaction:
    """
    """
    Class for managing payment transactions.
    Class for managing payment transactions.


    This class provides methods for creating, processing, and tracking
    This class provides methods for creating, processing, and tracking
    payment transactions.
    payment transactions.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    amount: float,
    amount: float,
    currency: str,
    currency: str,
    customer_id: str,
    customer_id: str,
    payment_method_id: str,
    payment_method_id: str,
    description: str,
    description: str,
    transaction_type: str = TransactionType.CHARGE,
    transaction_type: str = TransactionType.CHARGE,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize a transaction.
    Initialize a transaction.


    Args:
    Args:
    amount: Amount of the transaction
    amount: Amount of the transaction
    currency: Currency code (e.g., USD)
    currency: Currency code (e.g., USD)
    customer_id: ID of the customer
    customer_id: ID of the customer
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method
    description: Description of the transaction
    description: Description of the transaction
    transaction_type: Type of transaction
    transaction_type: Type of transaction
    metadata: Additional metadata for the transaction
    metadata: Additional metadata for the transaction
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.amount = amount
    self.amount = amount
    self.currency = currency
    self.currency = currency
    self.customer_id = customer_id
    self.customer_id = customer_id
    self.payment_method_id = payment_method_id
    self.payment_method_id = payment_method_id
    self.description = description
    self.description = description
    self.transaction_type = transaction_type
    self.transaction_type = transaction_type
    self.metadata = metadata or {}
    self.metadata = metadata or {}


    # Set initial status
    # Set initial status
    self.status = TransactionStatus.PENDING
    self.status = TransactionStatus.PENDING


    # Initialize other properties
    # Initialize other properties
    self.created_at = datetime.now()
    self.created_at = datetime.now()
    self.updated_at = self.created_at
    self.updated_at = self.created_at
    self.processed_at = None
    self.processed_at = None
    self.error = None
    self.error = None
    self.refunds = []
    self.refunds = []
    self.parent_id = None
    self.parent_id = None
    self.status_history = [
    self.status_history = [
    {
    {
    "status": self.status,
    "status": self.status,
    "timestamp": self.created_at.isoformat(),
    "timestamp": self.created_at.isoformat(),
    "reason": "Transaction created",
    "reason": "Transaction created",
    }
    }
    ]
    ]


    def update_status(self, status: str, reason: Optional[str] = None) -> None:
    def update_status(self, status: str, reason: Optional[str] = None) -> None:
    """
    """
    Update the transaction status.
    Update the transaction status.


    Args:
    Args:
    status: New status
    status: New status
    reason: Reason for the status change
    reason: Reason for the status change
    """
    """
    old_status = self.status
    old_status = self.status
    self.status = status
    self.status = status
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    # Add status history entry
    # Add status history entry
    self.status_history.append(
    self.status_history.append(
    {
    {
    "status": status,
    "status": status,
    "timestamp": self.updated_at.isoformat(),
    "timestamp": self.updated_at.isoformat(),
    "reason": reason or f"Status changed from {old_status} to {status}",
    "reason": reason or f"Status changed from {old_status} to {status}",
    }
    }
    )
    )


    # Set processed_at if the transaction is now complete
    # Set processed_at if the transaction is now complete
    if (
    if (
    status in [TransactionStatus.SUCCEEDED, TransactionStatus.FAILED]
    status in [TransactionStatus.SUCCEEDED, TransactionStatus.FAILED]
    and not self.processed_at
    and not self.processed_at
    ):
    ):
    self.processed_at = self.updated_at
    self.processed_at = self.updated_at


    def set_error(self, error_code: str, error_message: str) -> None:
    def set_error(self, error_code: str, error_message: str) -> None:
    """
    """
    Set an error on the transaction.
    Set an error on the transaction.


    Args:
    Args:
    error_code: Error code
    error_code: Error code
    error_message: Error message
    error_message: Error message
    """
    """
    self.error = {
    self.error = {
    "code": error_code,
    "code": error_code,
    "message": error_message,
    "message": error_message,
    "timestamp": datetime.now().isoformat(),
    "timestamp": datetime.now().isoformat(),
    }
    }


    # Update status to failed
    # Update status to failed
    self.update_status(TransactionStatus.FAILED, f"Error: {error_message}")
    self.update_status(TransactionStatus.FAILED, f"Error: {error_message}")


    def add_refund(
    def add_refund(
    self,
    self,
    amount: float,
    amount: float,
    reason: Optional[str] = None,
    reason: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Add a refund to the transaction.
    Add a refund to the transaction.


    Args:
    Args:
    amount: Amount to refund
    amount: Amount to refund
    reason: Reason for the refund
    reason: Reason for the refund
    metadata: Additional metadata for the refund
    metadata: Additional metadata for the refund


    Returns:
    Returns:
    Dictionary with refund information
    Dictionary with refund information
    """
    """
    # Validate refund amount
    # Validate refund amount
    if amount <= 0:
    if amount <= 0:
    raise ValueError("Refund amount must be positive")
    raise ValueError("Refund amount must be positive")


    # Calculate total refunded amount
    # Calculate total refunded amount
    total_refunded = sum(refund["amount"] for refund in self.refunds)
    total_refunded = sum(refund["amount"] for refund in self.refunds)


    if total_refunded + amount > self.amount:
    if total_refunded + amount > self.amount:
    raise ValueError(
    raise ValueError(
    f"Cannot refund more than the transaction amount ({self.amount})"
    f"Cannot refund more than the transaction amount ({self.amount})"
    )
    )


    # Create refund
    # Create refund
    refund = {
    refund = {
    "id": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "amount": amount,
    "amount": amount,
    "currency": self.currency,
    "currency": self.currency,
    "reason": reason or "requested_by_customer",
    "reason": reason or "requested_by_customer",
    "status": TransactionStatus.SUCCEEDED,
    "status": TransactionStatus.SUCCEEDED,
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "metadata": metadata or {},
    "metadata": metadata or {},
    }
    }


    # Add refund to list
    # Add refund to list
    self.refunds.append(refund)
    self.refunds.append(refund)


    # Update transaction status
    # Update transaction status
    if total_refunded + amount == self.amount:
    if total_refunded + amount == self.amount:
    self.update_status(TransactionStatus.REFUNDED, "Fully refunded")
    self.update_status(TransactionStatus.REFUNDED, "Fully refunded")
    else:
    else:
    self.update_status(
    self.update_status(
    TransactionStatus.PARTIALLY_REFUNDED, "Partially refunded"
    TransactionStatus.PARTIALLY_REFUNDED, "Partially refunded"
    )
    )


    return refund
    return refund


    def get_refunded_amount(self) -> float:
    def get_refunded_amount(self) -> float:
    """
    """
    Get the total refunded amount.
    Get the total refunded amount.


    Returns:
    Returns:
    Total refunded amount
    Total refunded amount
    """
    """
    return sum(refund["amount"] for refund in self.refunds)
    return sum(refund["amount"] for refund in self.refunds)


    def get_net_amount(self) -> float:
    def get_net_amount(self) -> float:
    """
    """
    Get the net amount after refunds.
    Get the net amount after refunds.


    Returns:
    Returns:
    Net amount
    Net amount
    """
    """
    return self.amount - self.get_refunded_amount()
    return self.amount - self.get_refunded_amount()


    def is_refundable(self) -> bool:
    def is_refundable(self) -> bool:
    """
    """
    Check if the transaction is refundable.
    Check if the transaction is refundable.


    Returns:
    Returns:
    True if the transaction is refundable, False otherwise
    True if the transaction is refundable, False otherwise
    """
    """
    # Transaction must be successful and not fully refunded
    # Transaction must be successful and not fully refunded
    if self.status not in [
    if self.status not in [
    TransactionStatus.SUCCEEDED,
    TransactionStatus.SUCCEEDED,
    TransactionStatus.PARTIALLY_REFUNDED,
    TransactionStatus.PARTIALLY_REFUNDED,
    ]:
    ]:
    return False
    return False


    # Transaction must have a positive net amount
    # Transaction must have a positive net amount
    return self.get_net_amount() > 0
    return self.get_net_amount() > 0


    def is_successful(self) -> bool:
    def is_successful(self) -> bool:
    """
    """
    Check if the transaction was successful.
    Check if the transaction was successful.


    Returns:
    Returns:
    True if the transaction was successful, False otherwise
    True if the transaction was successful, False otherwise
    """
    """
    return self.status in [
    return self.status in [
    TransactionStatus.SUCCEEDED,
    TransactionStatus.SUCCEEDED,
    TransactionStatus.PARTIALLY_REFUNDED,
    TransactionStatus.PARTIALLY_REFUNDED,
    TransactionStatus.REFUNDED,
    TransactionStatus.REFUNDED,
    ]
    ]


    def is_pending(self) -> bool:
    def is_pending(self) -> bool:
    """
    """
    Check if the transaction is pending.
    Check if the transaction is pending.


    Returns:
    Returns:
    True if the transaction is pending, False otherwise
    True if the transaction is pending, False otherwise
    """
    """
    return self.status in [TransactionStatus.PENDING, TransactionStatus.PROCESSING]
    return self.status in [TransactionStatus.PENDING, TransactionStatus.PROCESSING]


    def is_failed(self) -> bool:
    def is_failed(self) -> bool:
    """
    """
    Check if the transaction failed.
    Check if the transaction failed.


    Returns:
    Returns:
    True if the transaction failed, False otherwise
    True if the transaction failed, False otherwise
    """
    """
    return self.status in [TransactionStatus.FAILED, TransactionStatus.CANCELED]
    return self.status in [TransactionStatus.FAILED, TransactionStatus.CANCELED]


    def is_refunded(self) -> bool:
    def is_refunded(self) -> bool:
    """
    """
    Check if the transaction is refunded.
    Check if the transaction is refunded.


    Returns:
    Returns:
    True if the transaction is refunded, False otherwise
    True if the transaction is refunded, False otherwise
    """
    """
    return self.status == TransactionStatus.REFUNDED
    return self.status == TransactionStatus.REFUNDED


    def is_partially_refunded(self) -> bool:
    def is_partially_refunded(self) -> bool:
    """
    """
    Check if the transaction is partially refunded.
    Check if the transaction is partially refunded.


    Returns:
    Returns:
    True if the transaction is partially refunded, False otherwise
    True if the transaction is partially refunded, False otherwise
    """
    """
    return self.status == TransactionStatus.PARTIALLY_REFUNDED
    return self.status == TransactionStatus.PARTIALLY_REFUNDED


    def format_amount(self) -> str:
    def format_amount(self) -> str:
    """
    """
    Format the transaction amount with currency symbol.
    Format the transaction amount with currency symbol.


    Returns:
    Returns:
    Formatted amount with currency symbol
    Formatted amount with currency symbol
    """
    """
    currency_symbols = {
    currency_symbols = {
    "USD": "$",
    "USD": "$",
    "EUR": "€",
    "EUR": "€",
    "GBP": "£",
    "GBP": "£",
    "JPY": "¥",
    "JPY": "¥",
    "CAD": "C$",
    "CAD": "C$",
    "AUD": "A$",
    "AUD": "A$",
    }
    }


    symbol = currency_symbols.get(self.currency, self.currency)
    symbol = currency_symbols.get(self.currency, self.currency)


    if self.currency == "JPY":
    if self.currency == "JPY":
    # JPY doesn't use decimal places
    # JPY doesn't use decimal places
    return f"{symbol}{int(self.amount):,}"
    return f"{symbol}{int(self.amount):,}"
    else:
    else:
    return f"{symbol}{self.amount:,.2f}"
    return f"{symbol}{self.amount:,.2f}"


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the transaction to a dictionary.
    Convert the transaction to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the transaction
    Dictionary representation of the transaction
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "amount": self.amount,
    "amount": self.amount,
    "currency": self.currency,
    "currency": self.currency,
    "customer_id": self.customer_id,
    "customer_id": self.customer_id,
    "payment_method_id": self.payment_method_id,
    "payment_method_id": self.payment_method_id,
    "description": self.description,
    "description": self.description,
    "transaction_type": self.transaction_type,
    "transaction_type": self.transaction_type,
    "status": self.status,
    "status": self.status,
    "created_at": self.created_at.isoformat(),
    "created_at": self.created_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    "processed_at": (
    "processed_at": (
    self.processed_at.isoformat() if self.processed_at else None
    self.processed_at.isoformat() if self.processed_at else None
    ),
    ),
    "error": self.error,
    "error": self.error,
    "refunds": self.refunds,
    "refunds": self.refunds,
    "parent_id": self.parent_id,
    "parent_id": self.parent_id,
    "metadata": self.metadata,
    "metadata": self.metadata,
    "status_history": self.status_history,
    "status_history": self.status_history,
    }
    }


    def to_json(self, indent: int = 2) -> str:
    def to_json(self, indent: int = 2) -> str:
    """
    """
    Convert the transaction to a JSON string.
    Convert the transaction to a JSON string.


    Args:
    Args:
    indent: Number of spaces for indentation
    indent: Number of spaces for indentation


    Returns:
    Returns:
    JSON string representation of the transaction
    JSON string representation of the transaction
    """
    """
    return json.dumps(self.to_dict(), indent=indent)
    return json.dumps(self.to_dict(), indent=indent)


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
    """
    """
    Create a transaction from a dictionary.
    Create a transaction from a dictionary.


    Args:
    Args:
    data: Dictionary with transaction data
    data: Dictionary with transaction data


    Returns:
    Returns:
    Transaction instance
    Transaction instance
    """
    """
    # Create a new transaction
    # Create a new transaction
    transaction = cls(
    transaction = cls(
    amount=data["amount"],
    amount=data["amount"],
    currency=data["currency"],
    currency=data["currency"],
    customer_id=data["customer_id"],
    customer_id=data["customer_id"],
    payment_method_id=data["payment_method_id"],
    payment_method_id=data["payment_method_id"],
    description=data["description"],
    description=data["description"],
    transaction_type=data["transaction_type"],
    transaction_type=data["transaction_type"],
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    # Set additional fields
    # Set additional fields
    transaction.id = data["id"]
    transaction.id = data["id"]
    transaction.status = data["status"]
    transaction.status = data["status"]
    transaction.created_at = datetime.fromisoformat(data["created_at"])
    transaction.created_at = datetime.fromisoformat(data["created_at"])
    transaction.updated_at = datetime.fromisoformat(data["updated_at"])
    transaction.updated_at = datetime.fromisoformat(data["updated_at"])


    if data.get("processed_at"):
    if data.get("processed_at"):
    transaction.processed_at = datetime.fromisoformat(data["processed_at"])
    transaction.processed_at = datetime.fromisoformat(data["processed_at"])


    transaction.error = data.get("error")
    transaction.error = data.get("error")
    transaction.refunds = data.get("refunds", [])
    transaction.refunds = data.get("refunds", [])
    transaction.parent_id = data.get("parent_id")
    transaction.parent_id = data.get("parent_id")
    transaction.status_history = data.get("status_history", [])
    transaction.status_history = data.get("status_history", [])


    return transaction
    return transaction


    def __str__(self) -> str:
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