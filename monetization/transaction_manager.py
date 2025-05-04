"""
"""
Transaction manager for the pAIssive Income project.
Transaction manager for the pAIssive Income project.


This module provides a class for managing payment transactions, including
This module provides a class for managing payment transactions, including
storage, retrieval, and processing.
storage, retrieval, and processing.
"""
"""




import os
import os
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .payment_method_manager import PaymentMethodManager
from .payment_method_manager import PaymentMethodManager
from .payment_processor import PaymentProcessor
from .payment_processor import PaymentProcessor
from .transaction import Transaction, TransactionStatus, TransactionType
from .transaction import Transaction, TransactionStatus, TransactionType




class TransactionManager
class TransactionManager
from .mock_payment_processor import MockPaymentProcessor
from .mock_payment_processor import MockPaymentProcessor






(
(
create_directory,
create_directory,
file_exists,
file_exists,
get_file_path,
get_file_path,
is_date_in_range,
is_date_in_range,
load_from_json_file,
load_from_json_file,
)
)
:
    :
    """
    """
    Class for managing payment transactions.
    Class for managing payment transactions.


    This class provides methods for storing, retrieving, and processing
    This class provides methods for storing, retrieving, and processing
    payment transactions.
    payment transactions.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    payment_processor: Optional[PaymentProcessor] = None,
    payment_processor: Optional[PaymentProcessor] = None,
    payment_method_manager: Optional[PaymentMethodManager] = None,
    payment_method_manager: Optional[PaymentMethodManager] = None,
    storage_dir: Optional[str] = None,
    storage_dir: Optional[str] = None,
    ):
    ):
    """
    """
    Initialize a transaction manager.
    Initialize a transaction manager.


    Args:
    Args:
    payment_processor: Payment processor to use
    payment_processor: Payment processor to use
    payment_method_manager: Payment method manager to use
    payment_method_manager: Payment method manager to use
    storage_dir: Directory for storing transaction data
    storage_dir: Directory for storing transaction data
    """
    """
    self.payment_processor = payment_processor
    self.payment_processor = payment_processor
    self.payment_method_manager = payment_method_manager
    self.payment_method_manager = payment_method_manager
    self.storage_dir = storage_dir
    self.storage_dir = storage_dir


    if storage_dir:
    if storage_dir:
    create_directory(storage_dir)
    create_directory(storage_dir)


    self.transactions = {}
    self.transactions = {}
    self.customer_transactions = {}
    self.customer_transactions = {}


    # Load transactions if storage directory is set
    # Load transactions if storage directory is set
    if storage_dir:
    if storage_dir:
    self.load_transactions()
    self.load_transactions()


    def create_transaction(
    def create_transaction(
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
    auto_process: bool = False,
    auto_process: bool = False,
    ) -> Transaction:
    ) -> Transaction:
    """
    """
    Create a transaction.
    Create a transaction.


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
    auto_process: Whether to automatically process the transaction
    auto_process: Whether to automatically process the transaction


    Returns:
    Returns:
    The created transaction
    The created transaction
    """
    """
    # Create transaction
    # Create transaction
    transaction = Transaction(
    transaction = Transaction(
    amount=amount,
    amount=amount,
    currency=currency,
    currency=currency,
    customer_id=customer_id,
    customer_id=customer_id,
    payment_method_id=payment_method_id,
    payment_method_id=payment_method_id,
    description=description,
    description=description,
    transaction_type=transaction_type,
    transaction_type=transaction_type,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Store transaction
    # Store transaction
    self.transactions[transaction.id] = transaction
    self.transactions[transaction.id] = transaction


    # Add to customer's transactions
    # Add to customer's transactions
    if customer_id not in self.customer_transactions:
    if customer_id not in self.customer_transactions:
    self.customer_transactions[customer_id] = []
    self.customer_transactions[customer_id] = []


    self.customer_transactions[customer_id].append(transaction.id)
    self.customer_transactions[customer_id].append(transaction.id)


    # Save transaction if storage directory is set
    # Save transaction if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_transaction(transaction)
    self._save_transaction(transaction)


    # Process transaction if requested
    # Process transaction if requested
    if auto_process:
    if auto_process:
    self.process_transaction(transaction.id)
    self.process_transaction(transaction.id)


    return transaction
    return transaction


    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
    """
    """
    Get a transaction by ID.
    Get a transaction by ID.


    Args:
    Args:
    transaction_id: ID of the transaction
    transaction_id: ID of the transaction


    Returns:
    Returns:
    The transaction or None if not found
    The transaction or None if not found
    """
    """
    return self.transactions.get(transaction_id)
    return self.transactions.get(transaction_id)


    def get_customer_transactions(
    def get_customer_transactions(
    self,
    self,
    customer_id: str,
    customer_id: str,
    status: Optional[str] = None,
    status: Optional[str] = None,
    transaction_type: Optional[str] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    limit: int = 100,
    ) -> List[Transaction]:
    ) -> List[Transaction]:
    """
    """
    Get transactions for a customer.
    Get transactions for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    status: Status of transactions to get
    status: Status of transactions to get
    transaction_type: Type of transactions to get
    transaction_type: Type of transactions to get
    start_date: Start date for transactions
    start_date: Start date for transactions
    end_date: End date for transactions
    end_date: End date for transactions
    limit: Maximum number of transactions to return
    limit: Maximum number of transactions to return


    Returns:
    Returns:
    List of transactions
    List of transactions
    """
    """
    if customer_id not in self.customer_transactions:
    if customer_id not in self.customer_transactions:
    return []
    return []


    transactions = []
    transactions = []


    for transaction_id in self.customer_transactions[customer_id]:
    for transaction_id in self.customer_transactions[customer_id]:
    transaction = self.transactions.get(transaction_id)
    transaction = self.transactions.get(transaction_id)


    if not transaction:
    if not transaction:
    continue
    continue


    # Filter by status
    # Filter by status
    if status and transaction.status != status:
    if status and transaction.status != status:
    continue
    continue


    # Filter by transaction type
    # Filter by transaction type
    if transaction_type and transaction.transaction_type != transaction_type:
    if transaction_type and transaction.transaction_type != transaction_type:
    continue
    continue


    # Filter by date range
    # Filter by date range
    if not is_date_in_range(
    if not is_date_in_range(
    transaction.created_at,
    transaction.created_at,
    start_date or datetime.min,
    start_date or datetime.min,
    end_date or datetime.max,
    end_date or datetime.max,
    ):
    ):
    continue
    continue


    transactions.append(transaction)
    transactions.append(transaction)


    # Sort by created_at (newest first)
    # Sort by created_at (newest first)
    transactions.sort(key=lambda t: t.created_at, reverse=True)
    transactions.sort(key=lambda t: t.created_at, reverse=True)


    # Apply limit
    # Apply limit
    return transactions[:limit]
    return transactions[:limit]


    def process_transaction(self, transaction_id: str) -> Optional[Transaction]:
    def process_transaction(self, transaction_id: str) -> Optional[Transaction]:
    """
    """
    Process a transaction.
    Process a transaction.


    Args:
    Args:
    transaction_id: ID of the transaction
    transaction_id: ID of the transaction


    Returns:
    Returns:
    The updated transaction or None if not found
    The updated transaction or None if not found
    """
    """
    # Check if transaction exists
    # Check if transaction exists
    transaction = self.get_transaction(transaction_id)
    transaction = self.get_transaction(transaction_id)


    if not transaction:
    if not transaction:
    return None
    return None


    # Check if transaction is already processed
    # Check if transaction is already processed
    if not transaction.is_pending():
    if not transaction.is_pending():
    return transaction
    return transaction


    # Check if payment processor is available
    # Check if payment processor is available
    if not self.payment_processor:
    if not self.payment_processor:
    transaction.set_error(
    transaction.set_error(
    "processor_unavailable", "Payment processor is not available"
    "processor_unavailable", "Payment processor is not available"
    )
    )


    # Save transaction if storage directory is set
    # Save transaction if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_transaction(transaction)
    self._save_transaction(transaction)


    return transaction
    return transaction


    # Update status to processing
    # Update status to processing
    transaction.update_status(TransactionStatus.PROCESSING, "Processing payment")
    transaction.update_status(TransactionStatus.PROCESSING, "Processing payment")


    try:
    try:
    # Process payment
    # Process payment
    if transaction.transaction_type == TransactionType.CHARGE:
    if transaction.transaction_type == TransactionType.CHARGE:
    payment_result = self.payment_processor.process_payment(
    payment_result = self.payment_processor.process_payment(
    amount=transaction.amount,
    amount=transaction.amount,
    currency=transaction.currency,
    currency=transaction.currency,
    payment_method_id=transaction.payment_method_id,
    payment_method_id=transaction.payment_method_id,
    description=transaction.description,
    description=transaction.description,
    metadata=transaction.metadata,
    metadata=transaction.metadata,
    )
    )


    # Update transaction status
    # Update transaction status
    transaction.update_status(
    transaction.update_status(
    TransactionStatus.SUCCEEDED, "Payment successful"
    TransactionStatus.SUCCEEDED, "Payment successful"
    )
    )


    # Add payment ID to metadata
    # Add payment ID to metadata
    transaction.metadata["payment_id"] = payment_result["id"]
    transaction.metadata["payment_id"] = payment_result["id"]


    elif transaction.transaction_type == TransactionType.REFUND:
    elif transaction.transaction_type == TransactionType.REFUND:
    # Check if parent transaction exists
    # Check if parent transaction exists
    parent_id = transaction.parent_id
    parent_id = transaction.parent_id


    if not parent_id or parent_id not in self.transactions:
    if not parent_id or parent_id not in self.transactions:
    transaction.set_error(
    transaction.set_error(
    "parent_not_found", "Parent transaction not found"
    "parent_not_found", "Parent transaction not found"
    )
    )
    return transaction
    return transaction


    parent_transaction = self.transactions[parent_id]
    parent_transaction = self.transactions[parent_id]


    # Check if parent transaction has a payment ID
    # Check if parent transaction has a payment ID
    payment_id = parent_transaction.metadata.get("payment_id")
    payment_id = parent_transaction.metadata.get("payment_id")


    if not payment_id:
    if not payment_id:
    transaction.set_error(
    transaction.set_error(
    "payment_id_not_found",
    "payment_id_not_found",
    "Payment ID not found in parent transaction",
    "Payment ID not found in parent transaction",
    )
    )
    return transaction
    return transaction


    # Process refund
    # Process refund
    refund_result = self.payment_processor.refund_payment(
    refund_result = self.payment_processor.refund_payment(
    payment_id=payment_id,
    payment_id=payment_id,
    amount=transaction.amount,
    amount=transaction.amount,
    reason=transaction.metadata.get("reason"),
    reason=transaction.metadata.get("reason"),
    )
    )


    # Update transaction status
    # Update transaction status
    transaction.update_status(
    transaction.update_status(
    TransactionStatus.SUCCEEDED, "Refund successful"
    TransactionStatus.SUCCEEDED, "Refund successful"
    )
    )


    # Add refund ID to metadata
    # Add refund ID to metadata
    transaction.metadata["refund_id"] = refund_result["id"]
    transaction.metadata["refund_id"] = refund_result["id"]


    # Update parent transaction
    # Update parent transaction
    parent_transaction.add_refund(
    parent_transaction.add_refund(
    amount=transaction.amount,
    amount=transaction.amount,
    reason=transaction.metadata.get("reason"),
    reason=transaction.metadata.get("reason"),
    metadata={"refund_transaction_id": transaction.id},
    metadata={"refund_transaction_id": transaction.id},
    )
    )


    # Save parent transaction if storage directory is set
    # Save parent transaction if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_transaction(parent_transaction)
    self._save_transaction(parent_transaction)


    else:
    else:
    transaction.set_error(
    transaction.set_error(
    "unsupported_transaction_type",
    "unsupported_transaction_type",
    f"Unsupported transaction type: {transaction.transaction_type}",
    f"Unsupported transaction type: {transaction.transaction_type}",
    )
    )


except Exception as e:
except Exception as e:
    # Handle payment error
    # Handle payment error
    transaction.set_error("payment_failed", str(e))
    transaction.set_error("payment_failed", str(e))


    # Save transaction if storage directory is set
    # Save transaction if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_transaction(transaction)
    self._save_transaction(transaction)


    return transaction
    return transaction


    def refund_transaction(
    def refund_transaction(
    self,
    self,
    transaction_id: str,
    transaction_id: str,
    amount: Optional[float] = None,
    amount: Optional[float] = None,
    reason: Optional[str] = None,
    reason: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Transaction]:
    ) -> Optional[Transaction]:
    """
    """
    Refund a transaction.
    Refund a transaction.


    Args:
    Args:
    transaction_id: ID of the transaction to refund
    transaction_id: ID of the transaction to refund
    amount: Amount to refund (if None, refund the full amount)
    amount: Amount to refund (if None, refund the full amount)
    reason: Reason for the refund
    reason: Reason for the refund
    metadata: Additional metadata for the refund
    metadata: Additional metadata for the refund


    Returns:
    Returns:
    The refund transaction or None if the original transaction is not found
    The refund transaction or None if the original transaction is not found
    """
    """
    # Check if transaction exists
    # Check if transaction exists
    transaction = self.get_transaction(transaction_id)
    transaction = self.get_transaction(transaction_id)


    if not transaction:
    if not transaction:
    return None
    return None


    # Check if transaction is refundable
    # Check if transaction is refundable
    if not transaction.is_successful():
    if not transaction.is_successful():
    raise ValueError(f"Transaction is not refundable: {transaction.status}")
    raise ValueError(f"Transaction is not refundable: {transaction.status}")


    # Determine refund amount
    # Determine refund amount
    refund_amount = amount if amount is not None else transaction.get_net_amount()
    refund_amount = amount if amount is not None else transaction.get_net_amount()


    # Check if refund amount is valid
    # Check if refund amount is valid
    if refund_amount <= 0:
    if refund_amount <= 0:
    raise ValueError("Refund amount must be positive")
    raise ValueError("Refund amount must be positive")


    if refund_amount > transaction.get_net_amount():
    if refund_amount > transaction.get_net_amount():
    raise ValueError(
    raise ValueError(
    f"Cannot refund more than the net amount ({transaction.get_net_amount()})"
    f"Cannot refund more than the net amount ({transaction.get_net_amount()})"
    )
    )


    # Create refund metadata
    # Create refund metadata
    refund_metadata = {
    refund_metadata = {
    "parent_transaction_id": transaction_id,
    "parent_transaction_id": transaction_id,
    "reason": reason or "requested_by_customer",
    "reason": reason or "requested_by_customer",
    }
    }


    if metadata:
    if metadata:
    refund_metadata.update(metadata)
    refund_metadata.update(metadata)


    # Create refund transaction
    # Create refund transaction
    refund_transaction = self.create_transaction(
    refund_transaction = self.create_transaction(
    amount=refund_amount,
    amount=refund_amount,
    currency=transaction.currency,
    currency=transaction.currency,
    customer_id=transaction.customer_id,
    customer_id=transaction.customer_id,
    payment_method_id=transaction.payment_method_id,
    payment_method_id=transaction.payment_method_id,
    description=f"Refund: {transaction.description}",
    description=f"Refund: {transaction.description}",
    transaction_type=TransactionType.REFUND,
    transaction_type=TransactionType.REFUND,
    metadata=refund_metadata,
    metadata=refund_metadata,
    )
    )


    # Set parent ID
    # Set parent ID
    refund_transaction.parent_id = transaction_id
    refund_transaction.parent_id = transaction_id


    # Process refund
    # Process refund
    return self.process_transaction(refund_transaction.id)
    return self.process_transaction(refund_transaction.id)


    def get_transaction_history(self, transaction_id: str) -> List[Dict[str, Any]]:
    def get_transaction_history(self, transaction_id: str) -> List[Dict[str, Any]]:
    """
    """
    Get the history of a transaction.
    Get the history of a transaction.


    Args:
    Args:
    transaction_id: ID of the transaction
    transaction_id: ID of the transaction


    Returns:
    Returns:
    List of status changes with timestamps and reasons
    List of status changes with timestamps and reasons
    """
    """
    transaction = self.get_transaction(transaction_id)
    transaction = self.get_transaction(transaction_id)


    if not transaction:
    if not transaction:
    return []
    return []


    return transaction.status_history
    return transaction.status_history


    def get_related_transactions(self, transaction_id: str) -> List[Transaction]:
    def get_related_transactions(self, transaction_id: str) -> List[Transaction]:
    """
    """
    Get transactions related to a transaction.
    Get transactions related to a transaction.


    Args:
    Args:
    transaction_id: ID of the transaction
    transaction_id: ID of the transaction


    Returns:
    Returns:
    List of related transactions
    List of related transactions
    """
    """
    transaction = self.get_transaction(transaction_id)
    transaction = self.get_transaction(transaction_id)


    if not transaction:
    if not transaction:
    return []
    return []


    related_transactions = []
    related_transactions = []


    # If this is a parent transaction, find refund transactions
    # If this is a parent transaction, find refund transactions
    for t in self.transactions.values():
    for t in self.transactions.values():
    if t.parent_id == transaction_id:
    if t.parent_id == transaction_id:
    related_transactions.append(t)
    related_transactions.append(t)


    # If this is a refund transaction, find the parent transaction
    # If this is a refund transaction, find the parent transaction
    if transaction.parent_id:
    if transaction.parent_id:
    parent = self.get_transaction(transaction.parent_id)
    parent = self.get_transaction(transaction.parent_id)


    if parent:
    if parent:
    related_transactions.append(parent)
    related_transactions.append(parent)


    return related_transactions
    return related_transactions


    def get_transaction_summary(
    def get_transaction_summary(
    self,
    self,
    customer_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get a summary of transactions.
    Get a summary of transactions.


    Args:
    Args:
    customer_id: ID of the customer (if None, summarize all transactions)
    customer_id: ID of the customer (if None, summarize all transactions)
    start_date: Start date for transactions
    start_date: Start date for transactions
    end_date: End date for transactions
    end_date: End date for transactions


    Returns:
    Returns:
    Dictionary with transaction summary
    Dictionary with transaction summary
    """
    """
    # Get transactions to summarize
    # Get transactions to summarize
    if customer_id:
    if customer_id:
    transactions = self.get_customer_transactions(
    transactions = self.get_customer_transactions(
    customer_id=customer_id,
    customer_id=customer_id,
    start_date=start_date,
    start_date=start_date,
    end_date=end_date,
    end_date=end_date,
    limit=1000,  # Use a high limit to get all transactions
    limit=1000,  # Use a high limit to get all transactions
    )
    )
    else:
    else:
    transactions = list(self.transactions.values())
    transactions = list(self.transactions.values())


    # Filter by date range
    # Filter by date range
    if start_date or end_date:
    if start_date or end_date:
    filtered_transactions = []
    filtered_transactions = []


    for transaction in transactions:
    for transaction in transactions:
    if not is_date_in_range(
    if not is_date_in_range(
    transaction.created_at,
    transaction.created_at,
    start_date or datetime.min,
    start_date or datetime.min,
    end_date or datetime.max,
    end_date or datetime.max,
    ):
    ):
    continue
    continue


    filtered_transactions.append(transaction)
    filtered_transactions.append(transaction)


    transactions = filtered_transactions
    transactions = filtered_transactions


    # Initialize summary
    # Initialize summary
    summary = {
    summary = {
    "total_count": len(transactions),
    "total_count": len(transactions),
    "successful_count": 0,
    "successful_count": 0,
    "failed_count": 0,
    "failed_count": 0,
    "pending_count": 0,
    "pending_count": 0,
    "refunded_count": 0,
    "refunded_count": 0,
    "total_amount": 0.0,
    "total_amount": 0.0,
    "refunded_amount": 0.0,
    "refunded_amount": 0.0,
    "net_amount": 0.0,
    "net_amount": 0.0,
    "currencies": {},
    "currencies": {},
    "by_status": {},
    "by_status": {},
    "by_type": {},
    "by_type": {},
    }
    }


    # Calculate summary
    # Calculate summary
    for transaction in transactions:
    for transaction in transactions:
    # Skip refund transactions (they're counted in the refunded_amount)
    # Skip refund transactions (they're counted in the refunded_amount)
    if transaction.transaction_type == TransactionType.REFUND:
    if transaction.transaction_type == TransactionType.REFUND:
    continue
    continue


    # Count by status
    # Count by status
    if transaction.status not in summary["by_status"]:
    if transaction.status not in summary["by_status"]:
    summary["by_status"][transaction.status] = 0
    summary["by_status"][transaction.status] = 0


    summary["by_status"][transaction.status] += 1
    summary["by_status"][transaction.status] += 1


    # Count by type
    # Count by type
    if transaction.transaction_type not in summary["by_type"]:
    if transaction.transaction_type not in summary["by_type"]:
    summary["by_type"][transaction.transaction_type] = 0
    summary["by_type"][transaction.transaction_type] = 0


    summary["by_type"][transaction.transaction_type] += 1
    summary["by_type"][transaction.transaction_type] += 1


    # Count by success/failure
    # Count by success/failure
    if transaction.is_successful():
    if transaction.is_successful():
    summary["successful_count"] += 1
    summary["successful_count"] += 1
    elif transaction.is_failed():
    elif transaction.is_failed():
    summary["failed_count"] += 1
    summary["failed_count"] += 1
    elif transaction.is_pending():
    elif transaction.is_pending():
    summary["pending_count"] += 1
    summary["pending_count"] += 1


    # Count refunded transactions
    # Count refunded transactions
    if transaction.is_refunded() or transaction.is_partially_refunded():
    if transaction.is_refunded() or transaction.is_partially_refunded():
    summary["refunded_count"] += 1
    summary["refunded_count"] += 1


    # Track amounts by currency
    # Track amounts by currency
    if transaction.currency not in summary["currencies"]:
    if transaction.currency not in summary["currencies"]:
    summary["currencies"][transaction.currency] = {
    summary["currencies"][transaction.currency] = {
    "total_amount": 0.0,
    "total_amount": 0.0,
    "refunded_amount": 0.0,
    "refunded_amount": 0.0,
    "net_amount": 0.0,
    "net_amount": 0.0,
    }
    }


    # Add amounts
    # Add amounts
    if transaction.is_successful():
    if transaction.is_successful():
    summary["currencies"][transaction.currency][
    summary["currencies"][transaction.currency][
    "total_amount"
    "total_amount"
    ] += transaction.amount
    ] += transaction.amount
    summary["currencies"][transaction.currency][
    summary["currencies"][transaction.currency][
    "refunded_amount"
    "refunded_amount"
    ] += transaction.get_refunded_amount()
    ] += transaction.get_refunded_amount()
    summary["currencies"][transaction.currency][
    summary["currencies"][transaction.currency][
    "net_amount"
    "net_amount"
    ] += transaction.get_net_amount()
    ] += transaction.get_net_amount()


    summary["total_amount"] += transaction.amount
    summary["total_amount"] += transaction.amount
    summary["refunded_amount"] += transaction.get_refunded_amount()
    summary["refunded_amount"] += transaction.get_refunded_amount()
    summary["net_amount"] += transaction.get_net_amount()
    summary["net_amount"] += transaction.get_net_amount()


    return summary
    return summary


    def delete_transaction(self, transaction_id: str) -> bool:
    def delete_transaction(self, transaction_id: str) -> bool:
    """
    """
    Delete a transaction.
    Delete a transaction.


    Args:
    Args:
    transaction_id: ID of the transaction
    transaction_id: ID of the transaction


    Returns:
    Returns:
    True if the transaction was deleted, False otherwise
    True if the transaction was deleted, False otherwise
    """
    """
    # Check if transaction exists
    # Check if transaction exists
    transaction = self.get_transaction(transaction_id)
    transaction = self.get_transaction(transaction_id)


    if not transaction:
    if not transaction:
    return False
    return False


    # Remove from customer's transactions
    # Remove from customer's transactions
    customer_id = transaction.customer_id
    customer_id = transaction.customer_id


    if customer_id in self.customer_transactions:
    if customer_id in self.customer_transactions:
    if transaction_id in self.customer_transactions[customer_id]:
    if transaction_id in self.customer_transactions[customer_id]:
    self.customer_transactions[customer_id].remove(transaction_id)
    self.customer_transactions[customer_id].remove(transaction_id)


    # Remove from transactions
    # Remove from transactions
    del self.transactions[transaction_id]
    del self.transactions[transaction_id]


    # Delete file if storage directory is set
    # Delete file if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    file_path = os.path.join(self.storage_dir, f"{transaction_id}.json")
    file_path = os.path.join(self.storage_dir, f"{transaction_id}.json")


    if os.path.exists(file_path):
    if os.path.exists(file_path):
    os.remove(file_path)
    os.remove(file_path)


    return True
    return True


    def load_transactions(self) -> None:
    def load_transactions(self) -> None:
    """
    """
    Load transactions from storage directory.
    Load transactions from storage directory.
    """
    """
    if not self.storage_dir or not file_exists(self.storage_dir):
    if not self.storage_dir or not file_exists(self.storage_dir):
    return # Clear existing data
    return # Clear existing data
    self.transactions = {}
    self.transactions = {}
    self.customer_transactions = {}
    self.customer_transactions = {}


    # Load transactions
    # Load transactions
    for filename in os.listdir(self.storage_dir):
    for filename in os.listdir(self.storage_dir):
    if filename.endswith(".json"):
    if filename.endswith(".json"):
    file_path = get_file_path(self.storage_dir, filename)
    file_path = get_file_path(self.storage_dir, filename)


    try:
    try:
    # Load transaction data
    # Load transaction data
    data = load_from_json_file(file_path)
    data = load_from_json_file(file_path)


    # Create transaction
    # Create transaction
    transaction = Transaction.from_dict(data)
    transaction = Transaction.from_dict(data)


    # Store transaction
    # Store transaction
    self.transactions[transaction.id] = transaction
    self.transactions[transaction.id] = transaction


    # Add to customer's transactions
    # Add to customer's transactions
    customer_id = transaction.customer_id
    customer_id = transaction.customer_id


    if customer_id not in self.customer_transactions:
    if customer_id not in self.customer_transactions:
    self.customer_transactions[customer_id] = []
    self.customer_transactions[customer_id] = []


    self.customer_transactions[customer_id].append(transaction.id)
    self.customer_transactions[customer_id].append(transaction.id)


except Exception as e:
except Exception as e:
    print(f"Error loading transaction from {file_path}: {e}")
    print(f"Error loading transaction from {file_path}: {e}")


    def _save_transaction(self, transaction: Transaction) -> None:
    def _save_transaction(self, transaction: Transaction) -> None:
    """
    """
    Save a transaction to the storage directory.
    Save a transaction to the storage directory.


    Args:
    Args:
    transaction: Transaction to save
    transaction: Transaction to save
    """
    """
    if not self.storage_dir:
    if not self.storage_dir:
    return file_path = get_file_path(self.storage_dir, f"{transaction.id}.json")
    return file_path = get_file_path(self.storage_dir, f"{transaction.id}.json")
    transaction.save_to_file(file_path)
    transaction.save_to_file(file_path)




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a payment processor
    # Create a payment processor
    processor = MockPaymentProcessor({"name": "Test Processor", "success_rate": 0.95})
    processor = MockPaymentProcessor({"name": "Test Processor", "success_rate": 0.95})


    # Create a transaction manager
    # Create a transaction manager
    manager = TransactionManager(
    manager = TransactionManager(
    payment_processor=processor, storage_dir="transactions"
    payment_processor=processor, storage_dir="transactions"
    )
    )


    # Create a transaction
    # Create a transaction
    transaction = manager.create_transaction(
    transaction = manager.create_transaction(
    amount=19.99,
    amount=19.99,
    currency="USD",
    currency="USD",
    customer_id="cust_123",
    customer_id="cust_123",
    payment_method_id="pm_456",
    payment_method_id="pm_456",
    description="Monthly subscription payment",
    description="Monthly subscription payment",
    metadata={"subscription_id": "sub_789"},
    metadata={"subscription_id": "sub_789"},
    )
    )


    print(f"Transaction created: {transaction}")
    print(f"Transaction created: {transaction}")
    print(f"Amount: {transaction.format_amount()}")
    print(f"Amount: {transaction.format_amount()}")
    print(f"Status: {transaction.status}")
    print(f"Status: {transaction.status}")


    # Process the transaction
    # Process the transaction
    processed_transaction = manager.process_transaction(transaction.id)
    processed_transaction = manager.process_transaction(transaction.id)


    print(f"\nProcessed transaction: {processed_transaction}")
    print(f"\nProcessed transaction: {processed_transaction}")
    print(f"Status: {processed_transaction.status}")
    print(f"Status: {processed_transaction.status}")


    if processed_transaction.is_successful():
    if processed_transaction.is_successful():
    print("Payment was successful!")
    print("Payment was successful!")
    elif processed_transaction.error:
    elif processed_transaction.error:
    print(f"Payment failed: {processed_transaction.error['message']}")
    print(f"Payment failed: {processed_transaction.error['message']}")


    # If successful, create a partial refund
    # If successful, create a partial refund
    if processed_transaction.is_successful():
    if processed_transaction.is_successful():
    refund_transaction = manager.refund_transaction(
    refund_transaction = manager.refund_transaction(
    transaction_id=transaction.id, amount=5.00, reason="Customer request"
    transaction_id=transaction.id, amount=5.00, reason="Customer request"
    )
    )


    print(f"\nRefund transaction: {refund_transaction}")
    print(f"\nRefund transaction: {refund_transaction}")
    print(f"Status: {refund_transaction.status}")
    print(f"Status: {refund_transaction.status}")


    # Get related transactions
    # Get related transactions
    related = manager.get_related_transactions(transaction.id)
    related = manager.get_related_transactions(transaction.id)


    print(f"\nRelated transactions ({len(related)}):")
    print(f"\nRelated transactions ({len(related)}):")
    for t in related:
    for t in related:
    print(f"- {t}")
    print(f"- {t}")


    # Get transaction history
    # Get transaction history
    history = manager.get_transaction_history(transaction.id)
    history = manager.get_transaction_history(transaction.id)


    print("\nTransaction history:")
    print("\nTransaction history:")
    for entry in history:
    for entry in history:
    print(f"- {entry['timestamp']}: {entry['status']} ({entry['reason']})")
    print(f"- {entry['timestamp']}: {entry['status']} ({entry['reason']})")


    # Get transaction summary
    # Get transaction summary
    summary = manager.get_transaction_summary()
    summary = manager.get_transaction_summary()


    print("\nTransaction Summary:")
    print("\nTransaction Summary:")
    print(f"Total count: {summary['total_count']}")
    print(f"Total count: {summary['total_count']}")
    print(f"Successful: {summary['successful_count']}")
    print(f"Successful: {summary['successful_count']}")
    print(f"Failed: {summary['failed_count']}")
    print(f"Failed: {summary['failed_count']}")
    print(f"Pending: {summary['pending_count']}")
    print(f"Pending: {summary['pending_count']}")
    print(f"Refunded: {summary['refunded_count']}")
    print(f"Refunded: {summary['refunded_count']}")
    print(f"Total amount: ${summary['total_amount']:.2f}")
    print(f"Total amount: ${summary['total_amount']:.2f}")
    print(f"Refunded amount: ${summary['refunded_amount']:.2f}")
    print(f"Refunded amount: ${summary['refunded_amount']:.2f}")
    print(f"Net amount: ${summary['net_amount']:.2f}")
    print(f"Net amount: ${summary['net_amount']:.2f}")