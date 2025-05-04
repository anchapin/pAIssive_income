"""
"""
Receipt manager for the pAIssive Income project.
Receipt manager for the pAIssive Income project.


This module provides a class for managing receipts, including
This module provides a class for managing receipts, including
generation, storage, and retrieval.
generation, storage, and retrieval.
"""
"""




import os
import os
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from typing import Any, Dict, List, Optional, Union


from .payment_method import PaymentMethod
from .payment_method import PaymentMethod
from .payment_method_manager import PaymentMethodManager
from .payment_method_manager import PaymentMethodManager
from .receipt import Receipt
from .receipt import Receipt
from .transaction import Transaction
from .transaction import Transaction
from .transaction_manager import TransactionManager
from .transaction_manager import TransactionManager




class ReceiptManager
class ReceiptManager
from .transaction import Transaction, TransactionStatus
from .transaction import Transaction, TransactionStatus






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
    Class for managing receipts.
    Class for managing receipts.


    This class provides methods for generating, storing, and retrieving
    This class provides methods for generating, storing, and retrieving
    receipts for transactions.
    receipts for transactions.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    transaction_manager: Optional[TransactionManager] = None,
    transaction_manager: Optional[TransactionManager] = None,
    payment_method_manager: Optional[PaymentMethodManager] = None,
    payment_method_manager: Optional[PaymentMethodManager] = None,
    storage_dir: Optional[str] = None,
    storage_dir: Optional[str] = None,
    company_info: Optional[Dict[str, str]] = None,
    company_info: Optional[Dict[str, str]] = None,
    ):
    ):
    """
    """
    Initialize a receipt manager.
    Initialize a receipt manager.


    Args:
    Args:
    transaction_manager: Transaction manager to use
    transaction_manager: Transaction manager to use
    payment_method_manager: Payment method manager to use
    payment_method_manager: Payment method manager to use
    storage_dir: Directory for storing receipt data
    storage_dir: Directory for storing receipt data
    company_info: Company information for receipts
    company_info: Company information for receipts
    """
    """
    self.transaction_manager = transaction_manager
    self.transaction_manager = transaction_manager
    self.payment_method_manager = payment_method_manager
    self.payment_method_manager = payment_method_manager
    self.storage_dir = storage_dir
    self.storage_dir = storage_dir
    self.company_info = company_info or {}
    self.company_info = company_info or {}


    if storage_dir:
    if storage_dir:
    create_directory(storage_dir)
    create_directory(storage_dir)


    self.receipts = {}
    self.receipts = {}
    self.transaction_receipts = {}
    self.transaction_receipts = {}
    self.customer_receipts = {}
    self.customer_receipts = {}


    # Load receipts if storage directory is set
    # Load receipts if storage directory is set
    if storage_dir:
    if storage_dir:
    self.load_receipts()
    self.load_receipts()


    def generate_receipt(
    def generate_receipt(
    self,
    self,
    transaction: Union[Transaction, str],
    transaction: Union[Transaction, str],
    customer_info: Optional[Dict[str, str]] = None,
    customer_info: Optional[Dict[str, str]] = None,
    items: Optional[List[Dict[str, Any]]] = None,
    items: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Receipt:
    ) -> Receipt:
    """
    """
    Generate a receipt for a transaction.
    Generate a receipt for a transaction.


    Args:
    Args:
    transaction: Transaction or transaction ID
    transaction: Transaction or transaction ID
    customer_info: Customer information for the receipt
    customer_info: Customer information for the receipt
    items: List of items to include on the receipt
    items: List of items to include on the receipt
    metadata: Additional metadata for the receipt
    metadata: Additional metadata for the receipt


    Returns:
    Returns:
    The generated receipt
    The generated receipt
    """
    """
    # Get transaction if ID was provided
    # Get transaction if ID was provided
    if isinstance(transaction, str):
    if isinstance(transaction, str):
    if not self.transaction_manager:
    if not self.transaction_manager:
    raise ValueError(
    raise ValueError(
    "Transaction manager is required to get transaction by ID"
    "Transaction manager is required to get transaction by ID"
    )
    )


    transaction_obj = self.transaction_manager.get_transaction(transaction)
    transaction_obj = self.transaction_manager.get_transaction(transaction)


    if not transaction_obj:
    if not transaction_obj:
    raise ValueError(f"Transaction not found: {transaction}")
    raise ValueError(f"Transaction not found: {transaction}")


    transaction = transaction_obj
    transaction = transaction_obj


    # Create receipt
    # Create receipt
    receipt = Receipt(
    receipt = Receipt(
    transaction_id=transaction.id,
    transaction_id=transaction.id,
    customer_id=transaction.customer_id,
    customer_id=transaction.customer_id,
    date=transaction.processed_at or transaction.created_at,
    date=transaction.processed_at or transaction.created_at,
    currency=transaction.currency,
    currency=transaction.currency,
    metadata=metadata or {},
    metadata=metadata or {},
    )
    )


    # Set company information
    # Set company information
    if self.company_info:
    if self.company_info:
    receipt.set_company_info(
    receipt.set_company_info(
    name=self.company_info.get("name", ""),
    name=self.company_info.get("name", ""),
    address=self.company_info.get("address", ""),
    address=self.company_info.get("address", ""),
    email=self.company_info.get("email", ""),
    email=self.company_info.get("email", ""),
    phone=self.company_info.get("phone", ""),
    phone=self.company_info.get("phone", ""),
    website=self.company_info.get("website", ""),
    website=self.company_info.get("website", ""),
    logo_url=self.company_info.get("logo_url", ""),
    logo_url=self.company_info.get("logo_url", ""),
    )
    )


    # Set customer information
    # Set customer information
    if customer_info:
    if customer_info:
    receipt.set_customer_info(
    receipt.set_customer_info(
    name=customer_info.get("name", ""),
    name=customer_info.get("name", ""),
    email=customer_info.get("email", ""),
    email=customer_info.get("email", ""),
    address=customer_info.get("address", ""),
    address=customer_info.get("address", ""),
    )
    )


    # Set payment information
    # Set payment information
    payment_method_id = transaction.payment_method_id
    payment_method_id = transaction.payment_method_id
    payment_method_info = "Credit Card"  # Default
    payment_method_info = "Credit Card"  # Default


    if self.payment_method_manager and payment_method_id:
    if self.payment_method_manager and payment_method_id:
    payment_method = self.payment_method_manager.get_payment_method(
    payment_method = self.payment_method_manager.get_payment_method(
    payment_method_id
    payment_method_id
    )
    )


    if payment_method:
    if payment_method:
    if payment_method.payment_type == PaymentMethod.TYPE_CARD:
    if payment_method.payment_type == PaymentMethod.TYPE_CARD:
    card_brand = payment_method.details.get("brand", "Card")
    card_brand = payment_method.details.get("brand", "Card")
    last4 = payment_method.details.get("last4", "")
    last4 = payment_method.details.get("last4", "")
    payment_method_info = f"{card_brand} ending in {last4}"
    payment_method_info = f"{card_brand} ending in {last4}"
    elif payment_method.payment_type == PaymentMethod.TYPE_BANK_ACCOUNT:
    elif payment_method.payment_type == PaymentMethod.TYPE_BANK_ACCOUNT:
    bank_name = payment_method.details.get("bank_name", "Bank")
    bank_name = payment_method.details.get("bank_name", "Bank")
    last4 = payment_method.details.get("last4", "")
    last4 = payment_method.details.get("last4", "")
    payment_method_info = f"{bank_name} account ending in {last4}"
    payment_method_info = f"{bank_name} account ending in {last4}"
    elif payment_method.payment_type == PaymentMethod.TYPE_PAYPAL:
    elif payment_method.payment_type == PaymentMethod.TYPE_PAYPAL:
    email = payment_method.details.get("email", "")
    email = payment_method.details.get("email", "")
    payment_method_info = f"PayPal ({email})"
    payment_method_info = f"PayPal ({email})"
    else:
    else:
    payment_method_info = payment_method.payment_type.capitalize()
    payment_method_info = payment_method.payment_type.capitalize()


    receipt.set_payment_info(method=payment_method_info, payment_id=transaction.id)
    receipt.set_payment_info(method=payment_method_info, payment_id=transaction.id)


    # Add items
    # Add items
    if items:
    if items:
    for item in items:
    for item in items:
    receipt.add_item(
    receipt.add_item(
    description=item["description"],
    description=item["description"],
    quantity=item.get("quantity", 1.0),
    quantity=item.get("quantity", 1.0),
    unit_price=item.get("unit_price", 0.0),
    unit_price=item.get("unit_price", 0.0),
    discount=item.get("discount", 0.0),
    discount=item.get("discount", 0.0),
    tax_rate=item.get("tax_rate", 0.0),
    tax_rate=item.get("tax_rate", 0.0),
    metadata=item.get("metadata"),
    metadata=item.get("metadata"),
    )
    )
    else:
    else:
    # Add a single item based on the transaction
    # Add a single item based on the transaction
    receipt.add_item(
    receipt.add_item(
    description=transaction.description,
    description=transaction.description,
    quantity=1.0,
    quantity=1.0,
    unit_price=transaction.amount,
    unit_price=transaction.amount,
    discount=0.0,
    discount=0.0,
    tax_rate=0.0,
    tax_rate=0.0,
    )
    )


    # Store receipt
    # Store receipt
    self.receipts[receipt.id] = receipt
    self.receipts[receipt.id] = receipt


    # Add to transaction's receipts
    # Add to transaction's receipts
    if transaction.id not in self.transaction_receipts:
    if transaction.id not in self.transaction_receipts:
    self.transaction_receipts[transaction.id] = []
    self.transaction_receipts[transaction.id] = []


    self.transaction_receipts[transaction.id].append(receipt.id)
    self.transaction_receipts[transaction.id].append(receipt.id)


    # Add to customer's receipts
    # Add to customer's receipts
    if transaction.customer_id not in self.customer_receipts:
    if transaction.customer_id not in self.customer_receipts:
    self.customer_receipts[transaction.customer_id] = []
    self.customer_receipts[transaction.customer_id] = []


    self.customer_receipts[transaction.customer_id].append(receipt.id)
    self.customer_receipts[transaction.customer_id].append(receipt.id)


    # Save receipt if storage directory is set
    # Save receipt if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_receipt(receipt)
    self._save_receipt(receipt)


    return receipt
    return receipt


    def get_receipt(self, receipt_id: str) -> Optional[Receipt]:
    def get_receipt(self, receipt_id: str) -> Optional[Receipt]:
    """
    """
    Get a receipt by ID.
    Get a receipt by ID.


    Args:
    Args:
    receipt_id: ID of the receipt
    receipt_id: ID of the receipt


    Returns:
    Returns:
    The receipt or None if not found
    The receipt or None if not found
    """
    """
    return self.receipts.get(receipt_id)
    return self.receipts.get(receipt_id)


    def get_transaction_receipts(self, transaction_id: str) -> List[Receipt]:
    def get_transaction_receipts(self, transaction_id: str) -> List[Receipt]:
    """
    """
    Get receipts for a transaction.
    Get receipts for a transaction.


    Args:
    Args:
    transaction_id: ID of the transaction
    transaction_id: ID of the transaction


    Returns:
    Returns:
    List of receipts
    List of receipts
    """
    """
    if transaction_id not in self.transaction_receipts:
    if transaction_id not in self.transaction_receipts:
    return []
    return []


    receipts = []
    receipts = []


    for receipt_id in self.transaction_receipts[transaction_id]:
    for receipt_id in self.transaction_receipts[transaction_id]:
    receipt = self.receipts.get(receipt_id)
    receipt = self.receipts.get(receipt_id)


    if receipt:
    if receipt:
    receipts.append(receipt)
    receipts.append(receipt)


    return receipts
    return receipts


    def get_customer_receipts(
    def get_customer_receipts(
    self,
    self,
    customer_id: str,
    customer_id: str,
    start_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    limit: int = 100,
    ) -> List[Receipt]:
    ) -> List[Receipt]:
    """
    """
    Get receipts for a customer.
    Get receipts for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    start_date: Start date for receipts
    start_date: Start date for receipts
    end_date: End date for receipts
    end_date: End date for receipts
    limit: Maximum number of receipts to return
    limit: Maximum number of receipts to return


    Returns:
    Returns:
    List of receipts
    List of receipts
    """
    """
    if customer_id not in self.customer_receipts:
    if customer_id not in self.customer_receipts:
    return []
    return []


    receipts = []
    receipts = []


    for receipt_id in self.customer_receipts[customer_id]:
    for receipt_id in self.customer_receipts[customer_id]:
    receipt = self.receipts.get(receipt_id)
    receipt = self.receipts.get(receipt_id)


    if not receipt:
    if not receipt:
    continue
    continue


    # Filter by date range
    # Filter by date range
    if not is_date_in_range(
    if not is_date_in_range(
    receipt.date, start_date or datetime.min, end_date or datetime.max
    receipt.date, start_date or datetime.min, end_date or datetime.max
    ):
    ):
    continue
    continue


    receipts.append(receipt)
    receipts.append(receipt)


    # Sort by date (newest first)
    # Sort by date (newest first)
    receipts.sort(key=lambda r: r.date, reverse=True)
    receipts.sort(key=lambda r: r.date, reverse=True)


    # Apply limit
    # Apply limit
    return receipts[:limit]
    return receipts[:limit]


    def delete_receipt(self, receipt_id: str) -> bool:
    def delete_receipt(self, receipt_id: str) -> bool:
    """
    """
    Delete a receipt.
    Delete a receipt.


    Args:
    Args:
    receipt_id: ID of the receipt
    receipt_id: ID of the receipt


    Returns:
    Returns:
    True if the receipt was deleted, False otherwise
    True if the receipt was deleted, False otherwise
    """
    """
    # Check if receipt exists
    # Check if receipt exists
    receipt = self.get_receipt(receipt_id)
    receipt = self.get_receipt(receipt_id)


    if not receipt:
    if not receipt:
    return False
    return False


    # Remove from transaction's receipts
    # Remove from transaction's receipts
    transaction_id = receipt.transaction_id
    transaction_id = receipt.transaction_id


    if transaction_id in self.transaction_receipts:
    if transaction_id in self.transaction_receipts:
    if receipt_id in self.transaction_receipts[transaction_id]:
    if receipt_id in self.transaction_receipts[transaction_id]:
    self.transaction_receipts[transaction_id].remove(receipt_id)
    self.transaction_receipts[transaction_id].remove(receipt_id)


    # Remove from customer's receipts
    # Remove from customer's receipts
    customer_id = receipt.customer_id
    customer_id = receipt.customer_id


    if customer_id in self.customer_receipts:
    if customer_id in self.customer_receipts:
    if receipt_id in self.customer_receipts[customer_id]:
    if receipt_id in self.customer_receipts[customer_id]:
    self.customer_receipts[customer_id].remove(receipt_id)
    self.customer_receipts[customer_id].remove(receipt_id)


    # Remove from receipts
    # Remove from receipts
    del self.receipts[receipt_id]
    del self.receipts[receipt_id]


    # Delete file if storage directory is set
    # Delete file if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    file_path = get_file_path(self.storage_dir, f"{receipt_id}.json")
    file_path = get_file_path(self.storage_dir, f"{receipt_id}.json")


    if file_exists(file_path):
    if file_exists(file_path):
    os.remove(file_path)
    os.remove(file_path)


    return True
    return True


    def send_receipt(
    def send_receipt(
    self,
    self,
    receipt_id: str,
    receipt_id: str,
    email: str,
    email: str,
    subject: Optional[str] = None,
    subject: Optional[str] = None,
    message: Optional[str] = None,
    message: Optional[str] = None,
    format: str = "html",
    format: str = "html",
    ) -> bool:
    ) -> bool:
    """
    """
    Send a receipt by email.
    Send a receipt by email.


    Args:
    Args:
    receipt_id: ID of the receipt
    receipt_id: ID of the receipt
    email: Email address to send to
    email: Email address to send to
    subject: Email subject
    subject: Email subject
    message: Email message
    message: Email message
    format: Receipt format (text, html)
    format: Receipt format (text, html)


    Returns:
    Returns:
    True if the receipt was sent, False otherwise
    True if the receipt was sent, False otherwise
    """
    """
    # This is a placeholder for actual email sending functionality
    # This is a placeholder for actual email sending functionality
    # In a real implementation, this would use an email service
    # In a real implementation, this would use an email service


    # Check if receipt exists
    # Check if receipt exists
    receipt = self.get_receipt(receipt_id)
    receipt = self.get_receipt(receipt_id)


    if not receipt:
    if not receipt:
    return False
    return False


    # Generate receipt content
    # Generate receipt content
    if format == "text":
    if format == "text":
    receipt.to_text()
    receipt.to_text()
    elif format == "html":
    elif format == "html":
    receipt.to_html()
    receipt.to_html()
    else:
    else:
    raise ValueError(f"Unsupported format: {format}")
    raise ValueError(f"Unsupported format: {format}")


    # Set default subject if not provided
    # Set default subject if not provided
    if not subject:
    if not subject:
    subject = f"Receipt {receipt.id} for your purchase"
    subject = f"Receipt {receipt.id} for your purchase"


    # Set default message if not provided
    # Set default message if not provided
    if not message:
    if not message:
    message = "Thank you for your purchase. Please find your receipt attached."
    message = "Thank you for your purchase. Please find your receipt attached."


    # Print email details (for demo purposes)
    # Print email details (for demo purposes)
    print(f"Sending receipt {receipt.id} to {email}")
    print(f"Sending receipt {receipt.id} to {email}")
    print(f"Subject: {subject}")
    print(f"Subject: {subject}")
    print(f"Message: {message}")
    print(f"Message: {message}")
    print(f"Format: {format}")
    print(f"Format: {format}")


    # In a real implementation, this would send an email
    # In a real implementation, this would send an email
    # For now, just return True
    # For now, just return True
    return True
    return True


    def load_receipts(self) -> None:
    def load_receipts(self) -> None:
    """
    """
    Load receipts from storage directory.
    Load receipts from storage directory.
    """
    """
    if not self.storage_dir or not file_exists(self.storage_dir):
    if not self.storage_dir or not file_exists(self.storage_dir):
    return # Clear existing data
    return # Clear existing data
    self.receipts = {}
    self.receipts = {}
    self.transaction_receipts = {}
    self.transaction_receipts = {}
    self.customer_receipts = {}
    self.customer_receipts = {}


    # Load receipts
    # Load receipts
    for filename in os.listdir(self.storage_dir):
    for filename in os.listdir(self.storage_dir):
    if filename.endswith(".json"):
    if filename.endswith(".json"):
    file_path = get_file_path(self.storage_dir, filename)
    file_path = get_file_path(self.storage_dir, filename)


    try:
    try:
    # Load receipt data
    # Load receipt data
    data = load_from_json_file(file_path)
    data = load_from_json_file(file_path)


    # Create receipt
    # Create receipt
    receipt = Receipt.from_dict(data)
    receipt = Receipt.from_dict(data)


    # Store receipt
    # Store receipt
    self.receipts[receipt.id] = receipt
    self.receipts[receipt.id] = receipt


    # Add to transaction's receipts
    # Add to transaction's receipts
    if receipt.transaction_id not in self.transaction_receipts:
    if receipt.transaction_id not in self.transaction_receipts:
    self.transaction_receipts[receipt.transaction_id] = []
    self.transaction_receipts[receipt.transaction_id] = []


    self.transaction_receipts[receipt.transaction_id].append(receipt.id)
    self.transaction_receipts[receipt.transaction_id].append(receipt.id)


    # Add to customer's receipts
    # Add to customer's receipts
    if receipt.customer_id not in self.customer_receipts:
    if receipt.customer_id not in self.customer_receipts:
    self.customer_receipts[receipt.customer_id] = []
    self.customer_receipts[receipt.customer_id] = []


    self.customer_receipts[receipt.customer_id].append(receipt.id)
    self.customer_receipts[receipt.customer_id].append(receipt.id)


except Exception as e:
except Exception as e:
    print(f"Error loading receipt from {file_path}: {e}")
    print(f"Error loading receipt from {file_path}: {e}")


    def _save_receipt(self, receipt: Receipt) -> None:
    def _save_receipt(self, receipt: Receipt) -> None:
    """
    """
    Save a receipt to the storage directory.
    Save a receipt to the storage directory.


    Args:
    Args:
    receipt: Receipt to save
    receipt: Receipt to save
    """
    """
    if not self.storage_dir:
    if not self.storage_dir:
    return file_path = get_file_path(self.storage_dir, f"{receipt.id}.json")
    return file_path = get_file_path(self.storage_dir, f"{receipt.id}.json")
    receipt.save_to_file(file_path, format="json")
    receipt.save_to_file(file_path, format="json")




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a transaction
    # Create a transaction
    transaction = Transaction(
    transaction = Transaction(
    amount=29.99,
    amount=29.99,
    currency="USD",
    currency="USD",
    customer_id="cust_123",
    customer_id="cust_123",
    payment_method_id="pm_456",
    payment_method_id="pm_456",
    description="Premium subscription payment",
    description="Premium subscription payment",
    metadata={"subscription_id": "sub_789"},
    metadata={"subscription_id": "sub_789"},
    )
    )


    # Set transaction as successful
    # Set transaction as successful
    transaction.update_status(TransactionStatus.SUCCEEDED, "Payment successful")
    transaction.update_status(TransactionStatus.SUCCEEDED, "Payment successful")


    # Create a receipt manager
    # Create a receipt manager
    manager = ReceiptManager(
    manager = ReceiptManager(
    company_info={
    company_info={
    "name": "AI Tools Inc.",
    "name": "AI Tools Inc.",
    "address": "123 Main St, San Francisco, CA 94111",
    "address": "123 Main St, San Francisco, CA 94111",
    "email": "support@aitools.com",
    "email": "support@aitools.com",
    "phone": "(555) 123-4567",
    "phone": "(555) 123-4567",
    "website": "https://aitools.com",
    "website": "https://aitools.com",
    },
    },
    storage_dir="receipts",
    storage_dir="receipts",
    )
    )


    # Generate a receipt
    # Generate a receipt
    receipt = manager.generate_receipt(
    receipt = manager.generate_receipt(
    transaction=transaction,
    transaction=transaction,
    customer_info={
    customer_info={
    "name": "John Doe",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "email": "john.doe@example.com",
    "address": "456 Oak St, San Francisco, CA 94112",
    "address": "456 Oak St, San Francisco, CA 94112",
    },
    },
    items=[
    items=[
    {
    {
    "description": "Premium Subscription (Monthly)",
    "description": "Premium Subscription (Monthly)",
    "quantity": 1,
    "quantity": 1,
    "unit_price": 29.99,
    "unit_price": 29.99,
    "tax_rate": 0.0825,  # 8.25% tax
    "tax_rate": 0.0825,  # 8.25% tax
    }
    }
    ],
    ],
    )
    )


    print(f"Receipt generated: {receipt}")
    print(f"Receipt generated: {receipt}")
    print(f"Total amount: {receipt.format_amount(receipt.get_total())}")
    print(f"Total amount: {receipt.format_amount(receipt.get_total())}")


    # Save receipt to file
    # Save receipt to file
    receipt.save_to_file("receipt_example.txt", format="text")
    receipt.save_to_file("receipt_example.txt", format="text")
    receipt.save_to_file("receipt_example.html", format="html")
    receipt.save_to_file("receipt_example.html", format="html")


    print("\nReceipt saved to files: receipt_example.txt and receipt_example.html")
    print("\nReceipt saved to files: receipt_example.txt and receipt_example.html")


    # Get customer receipts
    # Get customer receipts
    customer_receipts = manager.get_customer_receipts("cust_123")
    customer_receipts = manager.get_customer_receipts("cust_123")


    print(f"\nCustomer receipts ({len(customer_receipts)}):")
    print(f"\nCustomer receipts ({len(customer_receipts)}):")
    for r in customer_receipts:
    for r in customer_receipts:
    print(f"- {r}")
    print(f"- {r}")


    # Send receipt by email
    # Send receipt by email
    manager.send_receipt(
    manager.send_receipt(
    receipt_id=receipt.id,
    receipt_id=receipt.id,
    email="john.doe@example.com",
    email="john.doe@example.com",
    subject="Your AI Tools Inc. Receipt",
    subject="Your AI Tools Inc. Receipt",
    format="html",
    format="html",
    )
    )