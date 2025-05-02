"""
Receipt manager for the pAIssive Income project.

This module provides a class for managing receipts, including
generation, storage, and retrieval.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from common_utils import (
    create_directory,
    file_exists,
    get_file_path,
    is_date_in_range,
    load_from_json_file,
)

from .payment_method import PaymentMethod
from .payment_method_manager import PaymentMethodManager
from .receipt import Receipt
from .transaction import Transaction
from .transaction_manager import TransactionManager


class ReceiptManager:
    """
    Class for managing receipts.

    This class provides methods for generating, storing, and retrieving
    receipts for transactions.
    """

    def __init__(
        self,
        transaction_manager: Optional[TransactionManager] = None,
        payment_method_manager: Optional[PaymentMethodManager] = None,
        storage_dir: Optional[str] = None,
        company_info: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize a receipt manager.

        Args:
            transaction_manager: Transaction manager to use
            payment_method_manager: Payment method manager to use
            storage_dir: Directory for storing receipt data
            company_info: Company information for receipts
        """
        self.transaction_manager = transaction_manager
        self.payment_method_manager = payment_method_manager
        self.storage_dir = storage_dir
        self.company_info = company_info or {}

        if storage_dir:
            create_directory(storage_dir)

        self.receipts = {}
        self.transaction_receipts = {}
        self.customer_receipts = {}

        # Load receipts if storage directory is set
        if storage_dir:
            self.load_receipts()

    def generate_receipt(
        self,
        transaction: Union[Transaction, str],
        customer_info: Optional[Dict[str, str]] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Receipt:
        """
        Generate a receipt for a transaction.

        Args:
            transaction: Transaction or transaction ID
            customer_info: Customer information for the receipt
            items: List of items to include on the receipt
            metadata: Additional metadata for the receipt

        Returns:
            The generated receipt
        """
        # Get transaction if ID was provided
        if isinstance(transaction, str):
            if not self.transaction_manager:
                raise ValueError(
                    "Transaction manager is required to get transaction by ID"
                )

            transaction_obj = self.transaction_manager.get_transaction(transaction)

            if not transaction_obj:
                raise ValueError(f"Transaction not found: {transaction}")

            transaction = transaction_obj

        # Create receipt
        receipt = Receipt(
            transaction_id=transaction.id,
            customer_id=transaction.customer_id,
            date=transaction.processed_at or transaction.created_at,
            currency=transaction.currency,
            metadata=metadata or {},
        )

        # Set company information
        if self.company_info:
            receipt.set_company_info(
                name=self.company_info.get("name", ""),
                address=self.company_info.get("address", ""),
                email=self.company_info.get("email", ""),
                phone=self.company_info.get("phone", ""),
                website=self.company_info.get("website", ""),
                logo_url=self.company_info.get("logo_url", ""),
            )

        # Set customer information
        if customer_info:
            receipt.set_customer_info(
                name=customer_info.get("name", ""),
                email=customer_info.get("email", ""),
                address=customer_info.get("address", ""),
            )

        # Set payment information
        payment_method_id = transaction.payment_method_id
        payment_method_info = "Credit Card"  # Default

        if self.payment_method_manager and payment_method_id:
            payment_method = self.payment_method_manager.get_payment_method(
                payment_method_id
            )

            if payment_method:
                if payment_method.payment_type == PaymentMethod.TYPE_CARD:
                    card_brand = payment_method.details.get("brand", "Card")
                    last4 = payment_method.details.get("last4", "")
                    payment_method_info = f"{card_brand} ending in {last4}"
                elif payment_method.payment_type == PaymentMethod.TYPE_BANK_ACCOUNT:
                    bank_name = payment_method.details.get("bank_name", "Bank")
                    last4 = payment_method.details.get("last4", "")
                    payment_method_info = f"{bank_name} account ending in {last4}"
                elif payment_method.payment_type == PaymentMethod.TYPE_PAYPAL:
                    email = payment_method.details.get("email", "")
                    payment_method_info = f"PayPal ({email})"
                else:
                    payment_method_info = payment_method.payment_type.capitalize()

        receipt.set_payment_info(method=payment_method_info, payment_id=transaction.id)

        # Add items
        if items:
            for item in items:
                receipt.add_item(
                    description=item["description"],
                    quantity=item.get("quantity", 1.0),
                    unit_price=item.get("unit_price", 0.0),
                    discount=item.get("discount", 0.0),
                    tax_rate=item.get("tax_rate", 0.0),
                    metadata=item.get("metadata"),
                )
        else:
            # Add a single item based on the transaction
            receipt.add_item(
                description=transaction.description,
                quantity=1.0,
                unit_price=transaction.amount,
                discount=0.0,
                tax_rate=0.0,
            )

        # Store receipt
        self.receipts[receipt.id] = receipt

        # Add to transaction's receipts
        if transaction.id not in self.transaction_receipts:
            self.transaction_receipts[transaction.id] = []

        self.transaction_receipts[transaction.id].append(receipt.id)

        # Add to customer's receipts
        if transaction.customer_id not in self.customer_receipts:
            self.customer_receipts[transaction.customer_id] = []

        self.customer_receipts[transaction.customer_id].append(receipt.id)

        # Save receipt if storage directory is set
        if self.storage_dir:
            self._save_receipt(receipt)

        return receipt

    def get_receipt(self, receipt_id: str) -> Optional[Receipt]:
        """
        Get a receipt by ID.

        Args:
            receipt_id: ID of the receipt

        Returns:
            The receipt or None if not found
        """
        return self.receipts.get(receipt_id)

    def get_transaction_receipts(self, transaction_id: str) -> List[Receipt]:
        """
        Get receipts for a transaction.

        Args:
            transaction_id: ID of the transaction

        Returns:
            List of receipts
        """
        if transaction_id not in self.transaction_receipts:
            return []

        receipts = []

        for receipt_id in self.transaction_receipts[transaction_id]:
            receipt = self.receipts.get(receipt_id)

            if receipt:
                receipts.append(receipt)

        return receipts

    def get_customer_receipts(
        self,
        customer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Receipt]:
        """
        Get receipts for a customer.

        Args:
            customer_id: ID of the customer
            start_date: Start date for receipts
            end_date: End date for receipts
            limit: Maximum number of receipts to return

        Returns:
            List of receipts
        """
        if customer_id not in self.customer_receipts:
            return []

        receipts = []

        for receipt_id in self.customer_receipts[customer_id]:
            receipt = self.receipts.get(receipt_id)

            if not receipt:
                continue

            # Filter by date range
            if not is_date_in_range(
                receipt.date, start_date or datetime.min, end_date or datetime.max
            ):
                continue

            receipts.append(receipt)

        # Sort by date (newest first)
        receipts.sort(key=lambda r: r.date, reverse=True)

        # Apply limit
        return receipts[:limit]

    def delete_receipt(self, receipt_id: str) -> bool:
        """
        Delete a receipt.

        Args:
            receipt_id: ID of the receipt

        Returns:
            True if the receipt was deleted, False otherwise
        """
        # Check if receipt exists
        receipt = self.get_receipt(receipt_id)

        if not receipt:
            return False

        # Remove from transaction's receipts
        transaction_id = receipt.transaction_id

        if transaction_id in self.transaction_receipts:
            if receipt_id in self.transaction_receipts[transaction_id]:
                self.transaction_receipts[transaction_id].remove(receipt_id)

        # Remove from customer's receipts
        customer_id = receipt.customer_id

        if customer_id in self.customer_receipts:
            if receipt_id in self.customer_receipts[customer_id]:
                self.customer_receipts[customer_id].remove(receipt_id)

        # Remove from receipts
        del self.receipts[receipt_id]

        # Delete file if storage directory is set
        if self.storage_dir:
            file_path = get_file_path(self.storage_dir, f"{receipt_id}.json")

            if file_exists(file_path):
                os.remove(file_path)

        return True

    def send_receipt(
        self,
        receipt_id: str,
        email: str,
        subject: Optional[str] = None,
        message: Optional[str] = None,
        format: str = "html",
    ) -> bool:
        """
        Send a receipt by email.

        Args:
            receipt_id: ID of the receipt
            email: Email address to send to
            subject: Email subject
            message: Email message
            format: Receipt format (text, html)

        Returns:
            True if the receipt was sent, False otherwise
        """
        # This is a placeholder for actual email sending functionality
        # In a real implementation, this would use an email service

        # Check if receipt exists
        receipt = self.get_receipt(receipt_id)

        if not receipt:
            return False

        # Generate receipt content
        if format == "text":
            receipt.to_text()
        elif format == "html":
            receipt.to_html()
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Set default subject if not provided
        if not subject:
            subject = f"Receipt {receipt.id} for your purchase"

        # Set default message if not provided
        if not message:
            message = "Thank you for your purchase. Please find your receipt attached."

        # Print email details (for demo purposes)
        print(f"Sending receipt {receipt.id} to {email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print(f"Format: {format}")

        # In a real implementation, this would send an email
        # For now, just return True
        return True

    def load_receipts(self) -> None:
        """
        Load receipts from storage directory.
        """
        if not self.storage_dir or not file_exists(self.storage_dir):
            return

        # Clear existing data
        self.receipts = {}
        self.transaction_receipts = {}
        self.customer_receipts = {}

        # Load receipts
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                file_path = get_file_path(self.storage_dir, filename)

                try:
                    # Load receipt data
                    data = load_from_json_file(file_path)

                    # Create receipt
                    receipt = Receipt.from_dict(data)

                    # Store receipt
                    self.receipts[receipt.id] = receipt

                    # Add to transaction's receipts
                    if receipt.transaction_id not in self.transaction_receipts:
                        self.transaction_receipts[receipt.transaction_id] = []

                    self.transaction_receipts[receipt.transaction_id].append(receipt.id)

                    # Add to customer's receipts
                    if receipt.customer_id not in self.customer_receipts:
                        self.customer_receipts[receipt.customer_id] = []

                    self.customer_receipts[receipt.customer_id].append(receipt.id)

                except Exception as e:
                    print(f"Error loading receipt from {file_path}: {e}")

    def _save_receipt(self, receipt: Receipt) -> None:
        """
        Save a receipt to the storage directory.

        Args:
            receipt: Receipt to save
        """
        if not self.storage_dir:
            return

        file_path = get_file_path(self.storage_dir, f"{receipt.id}.json")
        receipt.save_to_file(file_path, format="json")


# Example usage
if __name__ == "__main__":
    from .transaction import Transaction, TransactionStatus

    # Create a transaction
    transaction = Transaction(
        amount=29.99,
        currency="USD",
        customer_id="cust_123",
        payment_method_id="pm_456",
        description="Premium subscription payment",
        metadata={"subscription_id": "sub_789"},
    )

    # Set transaction as successful
    transaction.update_status(TransactionStatus.SUCCEEDED, "Payment successful")

    # Create a receipt manager
    manager = ReceiptManager(
        company_info={
            "name": "AI Tools Inc.",
            "address": "123 Main St, San Francisco, CA 94111",
            "email": "support@aitools.com",
            "phone": "(555) 123-4567",
            "website": "https://aitools.com",
        },
        storage_dir="receipts",
    )

    # Generate a receipt
    receipt = manager.generate_receipt(
        transaction=transaction,
        customer_info={
            "name": "John Doe",
            "email": "john.doe@example.com",
            "address": "456 Oak St, San Francisco, CA 94112",
        },
        items=[
            {
                "description": "Premium Subscription (Monthly)",
                "quantity": 1,
                "unit_price": 29.99,
                "tax_rate": 0.0825,  # 8.25% tax
            }
        ],
    )

    print(f"Receipt generated: {receipt}")
    print(f"Total amount: {receipt.format_amount(receipt.get_total())}")

    # Save receipt to file
    receipt.save_to_file("receipt_example.txt", format="text")
    receipt.save_to_file("receipt_example.html", format="html")

    print("\nReceipt saved to files: receipt_example.txt and receipt_example.html")

    # Get customer receipts
    customer_receipts = manager.get_customer_receipts("cust_123")

    print(f"\nCustomer receipts ({len(customer_receipts)}):")
    for r in customer_receipts:
        print(f"- {r}")

    # Send receipt by email
    manager.send_receipt(
        receipt_id=receipt.id,
        email="john.doe@example.com",
        subject="Your AI Tools Inc. Receipt",
        format="html",
    )
