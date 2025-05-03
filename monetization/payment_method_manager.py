"""
Payment method manager for the pAIssive Income project.

This module provides a class for managing payment methods, including
storage, retrieval, and default payment method management.
"""


import copy
import json
import os
from typing import Any, Dict, List, Optional

from .payment_method import PaymentMethod


class PaymentMethodManager

:
    """
    Class for managing payment methods.

This class provides methods for storing, retrieving, and managing
    payment methods for customers.
    """

def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize a payment method manager.

Args:
            storage_dir: Directory for storing payment method data
        """
        self.storage_dir = storage_dir

if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

self.payment_methods = {}
        self.customer_payment_methods = {}

# Load payment methods if storage directory is set
        if storage_dir:
            self.load_payment_methods()

def add_payment_method(
        self,
        customer_id: str,
        payment_type: str,
        payment_details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        set_as_default: bool = False,
    ) -> PaymentMethod:
        """
        Add a payment method.

Args:
            customer_id: ID of the customer
            payment_type: Type of payment method
            payment_details: Details of the payment method
            metadata: Additional metadata for the payment method
            set_as_default: Whether to set this as the default payment method

Returns:
            The created payment method
        """
        # Create payment method
        payment_method = PaymentMethod(
            customer_id=customer_id,
            payment_type=payment_type,
            payment_details=payment_details,
            metadata=metadata,
        )

# Set as default if requested or if this is the first payment method for the customer
        if set_as_default or customer_id not in self.customer_payment_methods:
            payment_method.set_as_default(True)

# If there are existing payment methods for this customer, unset them as default
            if customer_id in self.customer_payment_methods:
                for pm_id in self.customer_payment_methods[customer_id]:
                    if pm_id != payment_method.id:
                        pm = self.payment_methods.get(pm_id)
                        if pm and pm.is_default:
                            pm.set_as_default(False)

# Store payment method
        self.payment_methods[payment_method.id] = payment_method

# Add to customer's payment methods
        if customer_id not in self.customer_payment_methods:
            self.customer_payment_methods[customer_id] = []

self.customer_payment_methods[customer_id].append(payment_method.id)

# Save payment method if storage directory is set
        if self.storage_dir:
            self._save_payment_method(payment_method)

            return payment_method

def get_payment_method(self, payment_method_id: str) -> Optional[PaymentMethod]:
        """
        Get a payment method by ID.

Args:
            payment_method_id: ID of the payment method

Returns:
            The payment method or None if not found
        """
                    return self.payment_methods.get(payment_method_id)

def get_customer_payment_methods(
        self, customer_id: str, payment_type: Optional[str] = None
    ) -> List[PaymentMethod]:
        """
        Get all payment methods for a customer.

Args:
            customer_id: ID of the customer
            payment_type: Type of payment methods to get

Returns:
            List of payment methods
        """
        if customer_id not in self.customer_payment_methods:
                        return []

payment_methods = []

for pm_id in self.customer_payment_methods[customer_id]:
            pm = self.payment_methods.get(pm_id)

if pm and (payment_type is None or pm.payment_type == payment_type):
                payment_methods.append(pm)

            return payment_methods

def get_default_payment_method(self, customer_id: str) -> Optional[PaymentMethod]:
        """
        Get the default payment method for a customer.

Args:
            customer_id: ID of the customer

Returns:
            The default payment method or None if not found
        """
        if customer_id not in self.customer_payment_methods:
                        return None

for pm_id in self.customer_payment_methods[customer_id]:
            pm = self.payment_methods.get(pm_id)

if pm and pm.is_default:
                            return pm

# If no default is set but there are payment methods, return the first one
        if self.customer_payment_methods[customer_id]:
                        return self.payment_methods.get(
                self.customer_payment_methods[customer_id][0]
            )

            return None

def set_default_payment_method(
        self, customer_id: str, payment_method_id: str
    ) -> Optional[PaymentMethod]:
        """
        Set the default payment method for a customer.

Args:
            customer_id: ID of the customer
            payment_method_id: ID of the payment method to set as default

Returns:
            The updated payment method or None if not found
        """
        # Check if payment method exists
        payment_method = self.get_payment_method(payment_method_id)

if not payment_method:
                        return None

# Check if payment method belongs to customer
        if payment_method.customer_id != customer_id:
                        return None

# Unset current default payment method
        for pm_id in self.customer_payment_methods.get(customer_id, []):
            pm = self.payment_methods.get(pm_id)

if pm and pm.is_default:
                pm.set_as_default(False)

# Save payment method if storage directory is set
                if self.storage_dir:
                    self._save_payment_method(pm)

# Set new default payment method
        payment_method.set_as_default(True)

# Save payment method if storage directory is set
        if self.storage_dir:
            self._save_payment_method(payment_method)

            return payment_method

def update_payment_method(
        self,
        payment_method_id: str,
        payment_details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[PaymentMethod]:
        """
        Update a payment method.

Args:
            payment_method_id: ID of the payment method
            payment_details: New payment details
            metadata: New metadata

Returns:
            The updated payment method or None if not found
        """
        # Check if payment method exists
        payment_method = self.get_payment_method(payment_method_id)

if not payment_method:
                        return None

# Update payment details
        if payment_details:
            payment_method.update_details(payment_details)

# Update metadata
        if metadata:
            payment_method.update_metadata(metadata)

# Save payment method if storage directory is set
        if self.storage_dir:
            self._save_payment_method(payment_method)

            return payment_method

def delete_payment_method(self, payment_method_id: str) -> bool:
        """
        Delete a payment method.

Args:
            payment_method_id: ID of the payment method

Returns:
            True if the payment method was deleted, False otherwise
        """
        # Check if payment method exists
        payment_method = self.get_payment_method(payment_method_id)

if not payment_method:
                        return False

# Remove from customer's payment methods
        customer_id = payment_method.customer_id

if customer_id in self.customer_payment_methods:
            if payment_method_id in self.customer_payment_methods[customer_id]:
                self.customer_payment_methods[customer_id].remove(payment_method_id)

# Remove from payment methods
        del self.payment_methods[payment_method_id]

# Delete file if storage directory is set
        if self.storage_dir:
            file_path = os.path.join(self.storage_dir, f"{payment_method_id}.json")

if os.path.exists(file_path):
                os.remove(file_path)

# If this was the default payment method, set a new default
        if payment_method.is_default and customer_id in self.customer_payment_methods:
            if self.customer_payment_methods[customer_id]:
                new_default_id = self.customer_payment_methods[customer_id][0]
                new_default = self.payment_methods.get(new_default_id)

if new_default:
                    new_default.set_as_default(True)

# Save payment method if storage directory is set
                    if self.storage_dir:
                        self._save_payment_method(new_default)

            return True

def delete_customer_payment_methods(self, customer_id: str) -> int:
        """
        Delete all payment methods for a customer.

Args:
            customer_id: ID of the customer

Returns:
            Number of payment methods deleted
        """
        if customer_id not in self.customer_payment_methods:
                        return 0

# Get payment method IDs
        payment_method_ids = copy.copy(self.customer_payment_methods[customer_id])

# Delete each payment method
        deleted_count = 0

for pm_id in payment_method_ids:
            if self.delete_payment_method(pm_id):
                deleted_count += 1

            return deleted_count

def check_for_expiring_payment_methods(
        self, days: int = 30
    ) -> Dict[str, List[PaymentMethod]]:
        """
        Check for payment methods that will expire soon.

Args:
            days: Number of days to consider as "soon"

Returns:
            Dictionary mapping customer IDs to lists of expiring payment methods
        """
        expiring_payment_methods = {}

for pm in self.payment_methods.values():
            if pm.payment_type == PaymentMethod.TYPE_CARD and pm.will_expire_soon(days):
                customer_id = pm.customer_id

if customer_id not in expiring_payment_methods:
                    expiring_payment_methods[customer_id] = []

expiring_payment_methods[customer_id].append(pm)

            return expiring_payment_methods

def load_payment_methods(self) -> None:
        """
        Load payment methods from storage directory.
        """
        if not self.storage_dir or not os.path.exists(self.storage_dir):
                        return # Clear existing data
        self.payment_methods = {}
        self.customer_payment_methods = {}

# Load payment methods
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.storage_dir, filename)

try:
                    with open(file_path, "r") as f:
                        data = json.load(f)

# Create payment method
                    payment_method = PaymentMethod.from_dict(data)

# Store payment method
                    self.payment_methods[payment_method.id] = payment_method

# Add to customer's payment methods
                    customer_id = payment_method.customer_id

if customer_id not in self.customer_payment_methods:
                        self.customer_payment_methods[customer_id] = []

self.customer_payment_methods[customer_id].append(payment_method.id)

except Exception as e:
                    print(f"Error loading payment method from {file_path}: {e}")

def _save_payment_method(self, payment_method: PaymentMethod) -> None:
        """
        Save a payment method to the storage directory.

Args:
            payment_method: Payment method to save
        """
        if not self.storage_dir:
                        return file_path = os.path.join(self.storage_dir, f"{payment_method.id}.json")

with open(file_path, "w") as f:
            f.write(payment_method.to_json())


# Example usage
if __name__ == "__main__":
    # Create a payment method manager
    manager = PaymentMethodManager(storage_dir="payment_methods")

# Add a credit card payment method
    card_payment = manager.add_payment_method(
        customer_id="cust_123",
        payment_type=PaymentMethod.TYPE_CARD,
        payment_details={
            "number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "name": "John Doe",
        },
        set_as_default=True,
    )

print(f"Added card payment method: {card_payment}")

# Add a bank account payment method
    bank_payment = manager.add_payment_method(
        customer_id="cust_123",
        payment_type=PaymentMethod.TYPE_BANK_ACCOUNT,
        payment_details={
            "account_number": "000123456789",
            "routing_number": "110000000",
            "account_type": "checking",
            "bank_name": "Test Bank",
            "name": "John Doe",
        },
    )

print(f"Added bank payment method: {bank_payment}")

# Get customer payment methods
    payment_methods = manager.get_customer_payment_methods("cust_123")

print(f"\nCustomer payment methods ({len(payment_methods)}):")
    for pm in payment_methods:
        default_str = " (default)" if pm.is_default else ""
        print(f"- {pm}{default_str}")

# Get default payment method
    default_pm = manager.get_default_payment_method("cust_123")

print(f"\nDefault payment method: {default_pm}")

# Set bank account as default
    updated_pm = manager.set_default_payment_method("cust_123", bank_payment.id)

print(f"\nSet bank account as default: {updated_pm}")
    print(f"Is default: {updated_pm.is_default}")

# Get new default payment method
    default_pm = manager.get_default_payment_method("cust_123")

print(f"\nNew default payment method: {default_pm}")

# Update payment method
    updated_pm = manager.update_payment_method(
        payment_method_id=card_payment.id,
        payment_details={"exp_month": 11, "exp_year": 2031},
        metadata={"updated": True},
    )

print(f"\nUpdated payment method: {updated_pm}")
    print(
        f"New expiration: {updated_pm.details['exp_month']}/{updated_pm.details['exp_year']}"
    )
    print(f"Metadata: {updated_pm.metadata}")

# Check for expiring payment methods
    expiring_pms = manager.check_for_expiring_payment_methods(days=365 * 10)  # 10 years

print("\nExpiring payment methods:")
    for customer_id, pms in expiring_pms.items():
        print(f"Customer {customer_id}:")
        for pm in pms:
            print(
                f"- {pm} (expires {pm.details['exp_month']}/{pm.details['exp_year']})"
            )

# Delete a payment method
    deleted = manager.delete_payment_method(card_payment.id)

print(f"\nDeleted payment method: {deleted}")

# Get remaining payment methods
    payment_methods = manager.get_customer_payment_methods("cust_123")

print(f"\nRemaining payment methods ({len(payment_methods)}):")
    for pm in payment_methods:
        default_str = " (default)" if pm.is_default else ""
        print(f"- {pm}{default_str}")

# Delete all customer payment methods
    deleted_count = manager.delete_customer_payment_methods("cust_123")

print(f"\nDeleted {deleted_count} payment methods for customer")

# Verify all payment methods are deleted
    payment_methods = manager.get_customer_payment_methods("cust_123")

print(f"\nRemaining payment methods: {len(payment_methods)}")