"""
"""
Payment method manager for the pAIssive Income project.
Payment method manager for the pAIssive Income project.


This module provides a class for managing payment methods, including
This module provides a class for managing payment methods, including
storage, retrieval, and default payment method management.
storage, retrieval, and default payment method management.
"""
"""




import copy
import copy
import json
import json
import os
import os
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .payment_method import PaymentMethod
from .payment_method import PaymentMethod




class PaymentMethodManager:
    class PaymentMethodManager:


    pass  # Added missing block
    pass  # Added missing block
    """
    """
    Class for managing payment methods.
    Class for managing payment methods.


    This class provides methods for storing, retrieving, and managing
    This class provides methods for storing, retrieving, and managing
    payment methods for customers.
    payment methods for customers.
    """
    """


    def __init__(self, storage_dir: Optional[str] = None):
    def __init__(self, storage_dir: Optional[str] = None):
    """
    """
    Initialize a payment method manager.
    Initialize a payment method manager.


    Args:
    Args:
    storage_dir: Directory for storing payment method data
    storage_dir: Directory for storing payment method data
    """
    """
    self.storage_dir = storage_dir
    self.storage_dir = storage_dir


    if storage_dir and not os.path.exists(storage_dir):
    if storage_dir and not os.path.exists(storage_dir):
    os.makedirs(storage_dir)
    os.makedirs(storage_dir)


    self.payment_methods = {}
    self.payment_methods = {}
    self.customer_payment_methods = {}
    self.customer_payment_methods = {}


    # Load payment methods if storage directory is set
    # Load payment methods if storage directory is set
    if storage_dir:
    if storage_dir:
    self.load_payment_methods()
    self.load_payment_methods()


    def add_payment_method(
    def add_payment_method(
    self,
    self,
    customer_id: str,
    customer_id: str,
    payment_type: str,
    payment_type: str,
    payment_details: Dict[str, Any],
    payment_details: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    set_as_default: bool = False,
    set_as_default: bool = False,
    ) -> PaymentMethod:
    ) -> PaymentMethod:
    """
    """
    Add a payment method.
    Add a payment method.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    payment_type: Type of payment method
    payment_type: Type of payment method
    payment_details: Details of the payment method
    payment_details: Details of the payment method
    metadata: Additional metadata for the payment method
    metadata: Additional metadata for the payment method
    set_as_default: Whether to set this as the default payment method
    set_as_default: Whether to set this as the default payment method


    Returns:
    Returns:
    The created payment method
    The created payment method
    """
    """
    # Create payment method
    # Create payment method
    payment_method = PaymentMethod(
    payment_method = PaymentMethod(
    customer_id=customer_id,
    customer_id=customer_id,
    payment_type=payment_type,
    payment_type=payment_type,
    payment_details=payment_details,
    payment_details=payment_details,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Set as default if requested or if this is the first payment method for the customer
    # Set as default if requested or if this is the first payment method for the customer
    if set_as_default or customer_id not in self.customer_payment_methods:
    if set_as_default or customer_id not in self.customer_payment_methods:
    payment_method.set_as_default(True)
    payment_method.set_as_default(True)


    # If there are existing payment methods for this customer, unset them as default
    # If there are existing payment methods for this customer, unset them as default
    if customer_id in self.customer_payment_methods:
    if customer_id in self.customer_payment_methods:
    for pm_id in self.customer_payment_methods[customer_id]:
    for pm_id in self.customer_payment_methods[customer_id]:
    if pm_id != payment_method.id:
    if pm_id != payment_method.id:
    pm = self.payment_methods.get(pm_id)
    pm = self.payment_methods.get(pm_id)
    if pm and pm.is_default:
    if pm and pm.is_default:
    pm.set_as_default(False)
    pm.set_as_default(False)


    # Store payment method
    # Store payment method
    self.payment_methods[payment_method.id] = payment_method
    self.payment_methods[payment_method.id] = payment_method


    # Add to customer's payment methods
    # Add to customer's payment methods
    if customer_id not in self.customer_payment_methods:
    if customer_id not in self.customer_payment_methods:
    self.customer_payment_methods[customer_id] = []
    self.customer_payment_methods[customer_id] = []


    self.customer_payment_methods[customer_id].append(payment_method.id)
    self.customer_payment_methods[customer_id].append(payment_method.id)


    # Save payment method if storage directory is set
    # Save payment method if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_payment_method(payment_method)
    self._save_payment_method(payment_method)


    return payment_method
    return payment_method


    def get_payment_method(self, payment_method_id: str) -> Optional[PaymentMethod]:
    def get_payment_method(self, payment_method_id: str) -> Optional[PaymentMethod]:
    """
    """
    Get a payment method by ID.
    Get a payment method by ID.


    Args:
    Args:
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method


    Returns:
    Returns:
    The payment method or None if not found
    The payment method or None if not found
    """
    """
    return self.payment_methods.get(payment_method_id)
    return self.payment_methods.get(payment_method_id)


    def get_customer_payment_methods(
    def get_customer_payment_methods(
    self, customer_id: str, payment_type: Optional[str] = None
    self, customer_id: str, payment_type: Optional[str] = None
    ) -> List[PaymentMethod]:
    ) -> List[PaymentMethod]:
    """
    """
    Get all payment methods for a customer.
    Get all payment methods for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    payment_type: Type of payment methods to get
    payment_type: Type of payment methods to get


    Returns:
    Returns:
    List of payment methods
    List of payment methods
    """
    """
    if customer_id not in self.customer_payment_methods:
    if customer_id not in self.customer_payment_methods:
    return []
    return []


    payment_methods = []
    payment_methods = []


    for pm_id in self.customer_payment_methods[customer_id]:
    for pm_id in self.customer_payment_methods[customer_id]:
    pm = self.payment_methods.get(pm_id)
    pm = self.payment_methods.get(pm_id)


    if pm and (payment_type is None or pm.payment_type == payment_type):
    if pm and (payment_type is None or pm.payment_type == payment_type):
    payment_methods.append(pm)
    payment_methods.append(pm)


    return payment_methods
    return payment_methods


    def get_default_payment_method(self, customer_id: str) -> Optional[PaymentMethod]:
    def get_default_payment_method(self, customer_id: str) -> Optional[PaymentMethod]:
    """
    """
    Get the default payment method for a customer.
    Get the default payment method for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer


    Returns:
    Returns:
    The default payment method or None if not found
    The default payment method or None if not found
    """
    """
    if customer_id not in self.customer_payment_methods:
    if customer_id not in self.customer_payment_methods:
    return None
    return None


    for pm_id in self.customer_payment_methods[customer_id]:
    for pm_id in self.customer_payment_methods[customer_id]:
    pm = self.payment_methods.get(pm_id)
    pm = self.payment_methods.get(pm_id)


    if pm and pm.is_default:
    if pm and pm.is_default:
    return pm
    return pm


    # If no default is set but there are payment methods, return the first one
    # If no default is set but there are payment methods, return the first one
    if self.customer_payment_methods[customer_id]:
    if self.customer_payment_methods[customer_id]:
    return self.payment_methods.get(
    return self.payment_methods.get(
    self.customer_payment_methods[customer_id][0]
    self.customer_payment_methods[customer_id][0]
    )
    )


    return None
    return None


    def set_default_payment_method(
    def set_default_payment_method(
    self, customer_id: str, payment_method_id: str
    self, customer_id: str, payment_method_id: str
    ) -> Optional[PaymentMethod]:
    ) -> Optional[PaymentMethod]:
    """
    """
    Set the default payment method for a customer.
    Set the default payment method for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    payment_method_id: ID of the payment method to set as default
    payment_method_id: ID of the payment method to set as default


    Returns:
    Returns:
    The updated payment method or None if not found
    The updated payment method or None if not found
    """
    """
    # Check if payment method exists
    # Check if payment method exists
    payment_method = self.get_payment_method(payment_method_id)
    payment_method = self.get_payment_method(payment_method_id)


    if not payment_method:
    if not payment_method:
    return None
    return None


    # Check if payment method belongs to customer
    # Check if payment method belongs to customer
    if payment_method.customer_id != customer_id:
    if payment_method.customer_id != customer_id:
    return None
    return None


    # Unset current default payment method
    # Unset current default payment method
    for pm_id in self.customer_payment_methods.get(customer_id, []):
    for pm_id in self.customer_payment_methods.get(customer_id, []):
    pm = self.payment_methods.get(pm_id)
    pm = self.payment_methods.get(pm_id)


    if pm and pm.is_default:
    if pm and pm.is_default:
    pm.set_as_default(False)
    pm.set_as_default(False)


    # Save payment method if storage directory is set
    # Save payment method if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_payment_method(pm)
    self._save_payment_method(pm)


    # Set new default payment method
    # Set new default payment method
    payment_method.set_as_default(True)
    payment_method.set_as_default(True)


    # Save payment method if storage directory is set
    # Save payment method if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_payment_method(payment_method)
    self._save_payment_method(payment_method)


    return payment_method
    return payment_method


    def update_payment_method(
    def update_payment_method(
    self,
    self,
    payment_method_id: str,
    payment_method_id: str,
    payment_details: Optional[Dict[str, Any]] = None,
    payment_details: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[PaymentMethod]:
    ) -> Optional[PaymentMethod]:
    """
    """
    Update a payment method.
    Update a payment method.


    Args:
    Args:
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method
    payment_details: New payment details
    payment_details: New payment details
    metadata: New metadata
    metadata: New metadata


    Returns:
    Returns:
    The updated payment method or None if not found
    The updated payment method or None if not found
    """
    """
    # Check if payment method exists
    # Check if payment method exists
    payment_method = self.get_payment_method(payment_method_id)
    payment_method = self.get_payment_method(payment_method_id)


    if not payment_method:
    if not payment_method:
    return None
    return None


    # Update payment details
    # Update payment details
    if payment_details:
    if payment_details:
    payment_method.update_details(payment_details)
    payment_method.update_details(payment_details)


    # Update metadata
    # Update metadata
    if metadata:
    if metadata:
    payment_method.update_metadata(metadata)
    payment_method.update_metadata(metadata)


    # Save payment method if storage directory is set
    # Save payment method if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_payment_method(payment_method)
    self._save_payment_method(payment_method)


    return payment_method
    return payment_method


    def delete_payment_method(self, payment_method_id: str) -> bool:
    def delete_payment_method(self, payment_method_id: str) -> bool:
    """
    """
    Delete a payment method.
    Delete a payment method.


    Args:
    Args:
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method


    Returns:
    Returns:
    True if the payment method was deleted, False otherwise
    True if the payment method was deleted, False otherwise
    """
    """
    # Check if payment method exists
    # Check if payment method exists
    payment_method = self.get_payment_method(payment_method_id)
    payment_method = self.get_payment_method(payment_method_id)


    if not payment_method:
    if not payment_method:
    return False
    return False


    # Remove from customer's payment methods
    # Remove from customer's payment methods
    customer_id = payment_method.customer_id
    customer_id = payment_method.customer_id


    if customer_id in self.customer_payment_methods:
    if customer_id in self.customer_payment_methods:
    if payment_method_id in self.customer_payment_methods[customer_id]:
    if payment_method_id in self.customer_payment_methods[customer_id]:
    self.customer_payment_methods[customer_id].remove(payment_method_id)
    self.customer_payment_methods[customer_id].remove(payment_method_id)


    # Remove from payment methods
    # Remove from payment methods
    del self.payment_methods[payment_method_id]
    del self.payment_methods[payment_method_id]


    # Delete file if storage directory is set
    # Delete file if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    file_path = os.path.join(self.storage_dir, f"{payment_method_id}.json")
    file_path = os.path.join(self.storage_dir, f"{payment_method_id}.json")


    if os.path.exists(file_path):
    if os.path.exists(file_path):
    os.remove(file_path)
    os.remove(file_path)


    # If this was the default payment method, set a new default
    # If this was the default payment method, set a new default
    if payment_method.is_default and customer_id in self.customer_payment_methods:
    if payment_method.is_default and customer_id in self.customer_payment_methods:
    if self.customer_payment_methods[customer_id]:
    if self.customer_payment_methods[customer_id]:
    new_default_id = self.customer_payment_methods[customer_id][0]
    new_default_id = self.customer_payment_methods[customer_id][0]
    new_default = self.payment_methods.get(new_default_id)
    new_default = self.payment_methods.get(new_default_id)


    if new_default:
    if new_default:
    new_default.set_as_default(True)
    new_default.set_as_default(True)


    # Save payment method if storage directory is set
    # Save payment method if storage directory is set
    if self.storage_dir:
    if self.storage_dir:
    self._save_payment_method(new_default)
    self._save_payment_method(new_default)


    return True
    return True


    def delete_customer_payment_methods(self, customer_id: str) -> int:
    def delete_customer_payment_methods(self, customer_id: str) -> int:
    """
    """
    Delete all payment methods for a customer.
    Delete all payment methods for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer


    Returns:
    Returns:
    Number of payment methods deleted
    Number of payment methods deleted
    """
    """
    if customer_id not in self.customer_payment_methods:
    if customer_id not in self.customer_payment_methods:
    return 0
    return 0


    # Get payment method IDs
    # Get payment method IDs
    payment_method_ids = copy.copy(self.customer_payment_methods[customer_id])
    payment_method_ids = copy.copy(self.customer_payment_methods[customer_id])


    # Delete each payment method
    # Delete each payment method
    deleted_count = 0
    deleted_count = 0


    for pm_id in payment_method_ids:
    for pm_id in payment_method_ids:
    if self.delete_payment_method(pm_id):
    if self.delete_payment_method(pm_id):
    deleted_count += 1
    deleted_count += 1


    return deleted_count
    return deleted_count


    def check_for_expiring_payment_methods(
    def check_for_expiring_payment_methods(
    self, days: int = 30
    self, days: int = 30
    ) -> Dict[str, List[PaymentMethod]]:
    ) -> Dict[str, List[PaymentMethod]]:
    """
    """
    Check for payment methods that will expire soon.
    Check for payment methods that will expire soon.


    Args:
    Args:
    days: Number of days to consider as "soon"
    days: Number of days to consider as "soon"


    Returns:
    Returns:
    Dictionary mapping customer IDs to lists of expiring payment methods
    Dictionary mapping customer IDs to lists of expiring payment methods
    """
    """
    expiring_payment_methods = {}
    expiring_payment_methods = {}


    for pm in self.payment_methods.values():
    for pm in self.payment_methods.values():
    if pm.payment_type == PaymentMethod.TYPE_CARD and pm.will_expire_soon(days):
    if pm.payment_type == PaymentMethod.TYPE_CARD and pm.will_expire_soon(days):
    customer_id = pm.customer_id
    customer_id = pm.customer_id


    if customer_id not in expiring_payment_methods:
    if customer_id not in expiring_payment_methods:
    expiring_payment_methods[customer_id] = []
    expiring_payment_methods[customer_id] = []


    expiring_payment_methods[customer_id].append(pm)
    expiring_payment_methods[customer_id].append(pm)


    return expiring_payment_methods
    return expiring_payment_methods


    def load_payment_methods(self) -> None:
    def load_payment_methods(self) -> None:
    """
    """
    Load payment methods from storage directory.
    Load payment methods from storage directory.
    """
    """
    if not self.storage_dir or not os.path.exists(self.storage_dir):
    if not self.storage_dir or not os.path.exists(self.storage_dir):
    return # Clear existing data
    return # Clear existing data
    self.payment_methods = {}
    self.payment_methods = {}
    self.customer_payment_methods = {}
    self.customer_payment_methods = {}


    # Load payment methods
    # Load payment methods
    for filename in os.listdir(self.storage_dir):
    for filename in os.listdir(self.storage_dir):
    if filename.endswith(".json"):
    if filename.endswith(".json"):
    file_path = os.path.join(self.storage_dir, filename)
    file_path = os.path.join(self.storage_dir, filename)


    try:
    try:
    with open(file_path, "r") as f:
    with open(file_path, "r") as f:
    data = json.load(f)
    data = json.load(f)


    # Create payment method
    # Create payment method
    payment_method = PaymentMethod.from_dict(data)
    payment_method = PaymentMethod.from_dict(data)


    # Store payment method
    # Store payment method
    self.payment_methods[payment_method.id] = payment_method
    self.payment_methods[payment_method.id] = payment_method


    # Add to customer's payment methods
    # Add to customer's payment methods
    customer_id = payment_method.customer_id
    customer_id = payment_method.customer_id


    if customer_id not in self.customer_payment_methods:
    if customer_id not in self.customer_payment_methods:
    self.customer_payment_methods[customer_id] = []
    self.customer_payment_methods[customer_id] = []


    self.customer_payment_methods[customer_id].append(payment_method.id)
    self.customer_payment_methods[customer_id].append(payment_method.id)


except Exception as e:
except Exception as e:
    print(f"Error loading payment method from {file_path}: {e}")
    print(f"Error loading payment method from {file_path}: {e}")


    def _save_payment_method(self, payment_method: PaymentMethod) -> None:
    def _save_payment_method(self, payment_method: PaymentMethod) -> None:
    """
    """
    Save a payment method to the storage directory.
    Save a payment method to the storage directory.


    Args:
    Args:
    payment_method: Payment method to save
    payment_method: Payment method to save
    """
    """
    if not self.storage_dir:
    if not self.storage_dir:
    return file_path = os.path.join(self.storage_dir, f"{payment_method.id}.json")
    return file_path = os.path.join(self.storage_dir, f"{payment_method.id}.json")


    with open(file_path, "w") as f:
    with open(file_path, "w") as f:
    f.write(payment_method.to_json())
    f.write(payment_method.to_json())




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Create a payment method manager
    # Create a payment method manager
    manager = PaymentMethodManager(storage_dir="payment_methods")
    manager = PaymentMethodManager(storage_dir="payment_methods")


    # Add a credit card payment method
    # Add a credit card payment method
    card_payment = manager.add_payment_method(
    card_payment = manager.add_payment_method(
    customer_id="cust_123",
    customer_id="cust_123",
    payment_type=PaymentMethod.TYPE_CARD,
    payment_type=PaymentMethod.TYPE_CARD,
    payment_details={
    payment_details={
    "number": "4242424242424242",
    "number": "4242424242424242",
    "exp_month": 12,
    "exp_month": 12,
    "exp_year": 2030,
    "exp_year": 2030,
    "cvc": "123",
    "cvc": "123",
    "name": "John Doe",
    "name": "John Doe",
    },
    },
    set_as_default=True,
    set_as_default=True,
    )
    )


    print(f"Added card payment method: {card_payment}")
    print(f"Added card payment method: {card_payment}")


    # Add a bank account payment method
    # Add a bank account payment method
    bank_payment = manager.add_payment_method(
    bank_payment = manager.add_payment_method(
    customer_id="cust_123",
    customer_id="cust_123",
    payment_type=PaymentMethod.TYPE_BANK_ACCOUNT,
    payment_type=PaymentMethod.TYPE_BANK_ACCOUNT,
    payment_details={
    payment_details={
    "account_number": "000123456789",
    "account_number": "000123456789",
    "routing_number": "110000000",
    "routing_number": "110000000",
    "account_type": "checking",
    "account_type": "checking",
    "bank_name": "Test Bank",
    "bank_name": "Test Bank",
    "name": "John Doe",
    "name": "John Doe",
    },
    },
    )
    )


    print(f"Added bank payment method: {bank_payment}")
    print(f"Added bank payment method: {bank_payment}")


    # Get customer payment methods
    # Get customer payment methods
    payment_methods = manager.get_customer_payment_methods("cust_123")
    payment_methods = manager.get_customer_payment_methods("cust_123")


    print(f"\nCustomer payment methods ({len(payment_methods)}):")
    print(f"\nCustomer payment methods ({len(payment_methods)}):")
    for pm in payment_methods:
    for pm in payment_methods:
    default_str = " (default)" if pm.is_default else ""
    default_str = " (default)" if pm.is_default else ""
    print(f"- {pm}{default_str}")
    print(f"- {pm}{default_str}")


    # Get default payment method
    # Get default payment method
    default_pm = manager.get_default_payment_method("cust_123")
    default_pm = manager.get_default_payment_method("cust_123")


    print(f"\nDefault payment method: {default_pm}")
    print(f"\nDefault payment method: {default_pm}")


    # Set bank account as default
    # Set bank account as default
    updated_pm = manager.set_default_payment_method("cust_123", bank_payment.id)
    updated_pm = manager.set_default_payment_method("cust_123", bank_payment.id)


    print(f"\nSet bank account as default: {updated_pm}")
    print(f"\nSet bank account as default: {updated_pm}")
    print(f"Is default: {updated_pm.is_default}")
    print(f"Is default: {updated_pm.is_default}")


    # Get new default payment method
    # Get new default payment method
    default_pm = manager.get_default_payment_method("cust_123")
    default_pm = manager.get_default_payment_method("cust_123")


    print(f"\nNew default payment method: {default_pm}")
    print(f"\nNew default payment method: {default_pm}")


    # Update payment method
    # Update payment method
    updated_pm = manager.update_payment_method(
    updated_pm = manager.update_payment_method(
    payment_method_id=card_payment.id,
    payment_method_id=card_payment.id,
    payment_details={"exp_month": 11, "exp_year": 2031},
    payment_details={"exp_month": 11, "exp_year": 2031},
    metadata={"updated": True},
    metadata={"updated": True},
    )
    )


    print(f"\nUpdated payment method: {updated_pm}")
    print(f"\nUpdated payment method: {updated_pm}")
    print(
    print(
    f"New expiration: {updated_pm.details['exp_month']}/{updated_pm.details['exp_year']}"
    f"New expiration: {updated_pm.details['exp_month']}/{updated_pm.details['exp_year']}"
    )
    )
    print(f"Metadata: {updated_pm.metadata}")
    print(f"Metadata: {updated_pm.metadata}")


    # Check for expiring payment methods
    # Check for expiring payment methods
    expiring_pms = manager.check_for_expiring_payment_methods(days=365 * 10)  # 10 years
    expiring_pms = manager.check_for_expiring_payment_methods(days=365 * 10)  # 10 years


    print("\nExpiring payment methods:")
    print("\nExpiring payment methods:")
    for customer_id, pms in expiring_pms.items():
    for customer_id, pms in expiring_pms.items():
    print(f"Customer {customer_id}:")
    print(f"Customer {customer_id}:")
    for pm in pms:
    for pm in pms:
    print(
    print(
    f"- {pm} (expires {pm.details['exp_month']}/{pm.details['exp_year']})"
    f"- {pm} (expires {pm.details['exp_month']}/{pm.details['exp_year']})"
    )
    )


    # Delete a payment method
    # Delete a payment method
    deleted = manager.delete_payment_method(card_payment.id)
    deleted = manager.delete_payment_method(card_payment.id)


    print(f"\nDeleted payment method: {deleted}")
    print(f"\nDeleted payment method: {deleted}")


    # Get remaining payment methods
    # Get remaining payment methods
    payment_methods = manager.get_customer_payment_methods("cust_123")
    payment_methods = manager.get_customer_payment_methods("cust_123")


    print(f"\nRemaining payment methods ({len(payment_methods)}):")
    print(f"\nRemaining payment methods ({len(payment_methods)}):")
    for pm in payment_methods:
    for pm in payment_methods:
    default_str = " (default)" if pm.is_default else ""
    default_str = " (default)" if pm.is_default else ""
    print(f"- {pm}{default_str}")
    print(f"- {pm}{default_str}")


    # Delete all customer payment methods
    # Delete all customer payment methods
    deleted_count = manager.delete_customer_payment_methods("cust_123")
    deleted_count = manager.delete_customer_payment_methods("cust_123")


    print(f"\nDeleted {deleted_count} payment methods for customer")
    print(f"\nDeleted {deleted_count} payment methods for customer")


    # Verify all payment methods are deleted
    # Verify all payment methods are deleted
    payment_methods = manager.get_customer_payment_methods("cust_123")
    payment_methods = manager.get_customer_payment_methods("cust_123")


    print(f"\nRemaining payment methods: {len(payment_methods)}")
    print(f"\nRemaining payment methods: {len(payment_methods)}")