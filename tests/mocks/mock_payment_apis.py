"""
"""
Mock implementations of external payment APIs for testing.
Mock implementations of external payment APIs for testing.


This module provides mock implementations of various payment gateway APIs
This module provides mock implementations of various payment gateway APIs
that can be used for consistent testing without external dependencies.
that can be used for consistent testing without external dependencies.
"""
"""




import copy
import copy
import logging
import logging
import random
import random
import uuid
import uuid
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from enum import Enum
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from typing import Any, Dict, List, Optional, Union


logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class PaymentStatus(str, Enum):
    class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PENDING = "pending"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


    class MockPaymentGateway:

    def __init__(self, config: Optional[Dict[str, Any]] = None):
    """
    """
    Initialize the mock payment gateway.
    Initialize the mock payment gateway.


    Args:
    Args:
    config: Optional configuration for the payment gateway
    config: Optional configuration for the payment gateway
    """
    """
    self.config = config or {}
    self.config = config or {}


    # Initialize storage
    # Initialize storage
    self.customers = {}
    self.customers = {}
    self.payment_methods = {}
    self.payment_methods = {}
    self.payments = {}
    self.payments = {}
    self.subscriptions = {}
    self.subscriptions = {}
    self.plans = {}
    self.plans = {}
    self.refunds = {}
    self.refunds = {}


    # Set default configuration
    # Set default configuration
    self.success_rate = self.config.get("success_rate", 0.95)
    self.success_rate = self.config.get("success_rate", 0.95)
    self.refund_success_rate = self.config.get("refund_success_rate", 0.98)
    self.refund_success_rate = self.config.get("refund_success_rate", 0.98)
    self.network_error_rate = self.config.get("network_error_rate", 0.01)
    self.network_error_rate = self.config.get("network_error_rate", 0.01)


    # Set supported payment types
    # Set supported payment types
    self.supported_payment_types = self.config.get(
    self.supported_payment_types = self.config.get(
    "supported_payment_types", ["card", "bank_account"]
    "supported_payment_types", ["card", "bank_account"]
    )
    )


    # Set supported currencies
    # Set supported currencies
    self.supported_currencies = self.config.get(
    self.supported_currencies = self.config.get(
    "supported_currencies", ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
    "supported_currencies", ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
    )
    )


    # Track call history for assertions
    # Track call history for assertions
    self.call_history = []
    self.call_history = []


    def _generate_id(self, prefix: str) -> str:
    def _generate_id(self, prefix: str) -> str:
    """Generate a random ID with a prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

    def _simulate_success(self, success_rate: Optional[float] = None) -> bool:
    """Simulate a success or failure based on success rate."""
    rate = success_rate if success_rate is not None else self.success_rate
    return random.random() < rate

    def _simulate_network_error(self) -> bool:
    """Simulate a network error based on error rate."""
    if self.config.get("simulate_network_errors", True) is False:
    return False
    return random.random() < self.network_error_rate

    def record_call(self, method_name: str, **kwargs):
    """Record a method call for testing assertions."""
    self.call_history.append(
    {
    "method": method_name,
    "timestamp": datetime.now().isoformat(),
    "args": kwargs,
    }
    )

    def get_call_history(
    self, method_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
    """Get the call history, optionally filtered by method name."""
    if method_name:
    return [call for call in self.call_history if call["method"] == method_name]
    return self.call_history

    def clear_call_history(self):
    """Clear the call history."""
    self.call_history = []

    def validate_card_number(self, card_number: str) -> bool:
    """
    """
    Validate a credit card number using the Luhn algorithm.
    Validate a credit card number using the Luhn algorithm.


    Args:
    Args:
    card_number: Credit card number to validate
    card_number: Credit card number to validate


    Returns:
    Returns:
    True if the card number is valid, False otherwise
    True if the card number is valid, False otherwise
    """
    """
    # Remove any spaces or dashes
    # Remove any spaces or dashes
    card_number = card_number.replace(" ", "").replace("-", "")
    card_number = card_number.replace(" ", "").replace("-", "")


    # Check if the number contains only digits
    # Check if the number contains only digits
    if not card_number.isdigit():
    if not card_number.isdigit():
    return False
    return False


    # Check if the length is valid (most cards are 13-19 digits)
    # Check if the length is valid (most cards are 13-19 digits)
    if not (13 <= len(card_number) <= 19):
    if not (13 <= len(card_number) <= 19):
    return False
    return False


    # Apply the Luhn algorithm
    # Apply the Luhn algorithm
    total = 0
    total = 0
    reverse = card_number[::-1]
    reverse = card_number[::-1]


    for i, digit in enumerate(reverse):
    for i, digit in enumerate(reverse):
    digit = int(digit)
    digit = int(digit)
    if i % 2 == 1:
    if i % 2 == 1:
    digit *= 2
    digit *= 2
    if digit > 9:
    if digit > 9:
    digit -= 9
    digit -= 9
    total += digit
    total += digit


    return total % 10 == 0
    return total % 10 == 0


    def get_card_type(self, card_number: str) -> str:
    def get_card_type(self, card_number: str) -> str:
    """
    """
    Determine the card type based on the card number.
    Determine the card type based on the card number.


    Args:
    Args:
    card_number: Credit card number
    card_number: Credit card number


    Returns:
    Returns:
    Card type (visa, mastercard, amex, etc.)
    Card type (visa, mastercard, amex, etc.)
    """
    """
    # Remove any spaces or dashes
    # Remove any spaces or dashes
    card_number = card_number.replace(" ", "").replace("-", "")
    card_number = card_number.replace(" ", "").replace("-", "")


    # Simplified card type detection based on prefix and length
    # Simplified card type detection based on prefix and length
    if card_number.startswith("4"):
    if card_number.startswith("4"):
    return "visa"
    return "visa"
    elif card_number.startswith(("51", "52", "53", "54", "55")) or (
    elif card_number.startswith(("51", "52", "53", "54", "55")) or (
    51 <= int(card_number[:2]) <= 55
    51 <= int(card_number[:2]) <= 55
    ):
    ):
    return "mastercard"
    return "mastercard"
    elif card_number.startswith(("34", "37")):
    elif card_number.startswith(("34", "37")):
    return "amex"
    return "amex"
    elif card_number.startswith(
    elif card_number.startswith(
    ("6011", "644", "645", "646", "647", "648", "649", "65")
    ("6011", "644", "645", "646", "647", "648", "649", "65")
    ):
    ):
    return "discover"
    return "discover"
    else:
    else:
    return "unknown"
    return "unknown"


    def mask_card_number(self, card_number: str) -> str:
    def mask_card_number(self, card_number: str) -> str:
    """
    """
    Mask a credit card number for display.
    Mask a credit card number for display.


    Args:
    Args:
    card_number: Credit card number to mask
    card_number: Credit card number to mask


    Returns:
    Returns:
    Masked credit card number
    Masked credit card number
    """
    """
    # Remove any spaces or dashes
    # Remove any spaces or dashes
    card_number = card_number.replace(" ", "").replace("-", "")
    card_number = card_number.replace(" ", "").replace("-", "")


    # Determine how many digits to show
    # Determine how many digits to show
    if card_number.startswith(("34", "37")):
    if card_number.startswith(("34", "37")):
    # Amex: show first 6 and last 4
    # Amex: show first 6 and last 4
    return card_number[:6] + "X" * (len(card_number) - 10) + card_number[-4:]
    return card_number[:6] + "X" * (len(card_number) - 10) + card_number[-4:]
    else:
    else:
    # Other cards: show first 4 and last 4
    # Other cards: show first 4 and last 4
    return card_number[:4] + "X" * (len(card_number) - 8) + card_number[-4:]
    return card_number[:4] + "X" * (len(card_number) - 8) + card_number[-4:]


    def create_customer(
    def create_customer(
    self,
    self,
    email: str,
    email: str,
    name: Optional[str] = None,
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a new customer.
    Create a new customer.


    Args:
    Args:
    email: Customer email
    email: Customer email
    name: Customer name
    name: Customer name
    metadata: Additional metadata
    metadata: Additional metadata


    Returns:
    Returns:
    Created customer object
    Created customer object
    """
    """
    self.record_call("create_customer", email=email, name=name, metadata=metadata)
    self.record_call("create_customer", email=email, name=name, metadata=metadata)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while creating customer")
    raise ConnectionError("Network error while creating customer")


    # Generate customer ID
    # Generate customer ID
    customer_id = self._generate_id("cust")
    customer_id = self._generate_id("cust")


    # Create customer
    # Create customer
    customer = {
    customer = {
    "id": customer_id,
    "id": customer_id,
    "email": email,
    "email": email,
    "name": name or "",
    "name": name or "",
    "metadata": metadata or {},
    "metadata": metadata or {},
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    }
    }


    # Store customer
    # Store customer
    self.customers[customer_id] = customer
    self.customers[customer_id] = customer


    return copy.deepcopy(customer)
    return copy.deepcopy(customer)


    def get_customer(self, customer_id: str) -> Dict[str, Any]:
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
    """
    """
    Get a customer by ID.
    Get a customer by ID.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer


    Returns:
    Returns:
    Customer object
    Customer object
    """
    """
    self.record_call("get_customer", customer_id=customer_id)
    self.record_call("get_customer", customer_id=customer_id)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while retrieving customer")
    raise ConnectionError("Network error while retrieving customer")


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    return copy.deepcopy(self.customers[customer_id])
    return copy.deepcopy(self.customers[customer_id])


    def update_customer(
    def update_customer(
    self,
    self,
    customer_id: str,
    customer_id: str,
    email: Optional[str] = None,
    email: Optional[str] = None,
    name: Optional[str] = None,
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Update a customer's information.
    Update a customer's information.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    email: New customer email
    email: New customer email
    name: New customer name
    name: New customer name
    metadata: New metadata
    metadata: New metadata


    Returns:
    Returns:
    Updated customer object
    Updated customer object
    """
    """
    self.record_call(
    self.record_call(
    "update_customer",
    "update_customer",
    customer_id=customer_id,
    customer_id=customer_id,
    email=email,
    email=email,
    name=name,
    name=name,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while updating customer")
    raise ConnectionError("Network error while updating customer")


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    # Get customer
    # Get customer
    customer = self.customers[customer_id]
    customer = self.customers[customer_id]


    # Update fields
    # Update fields
    if email is not None:
    if email is not None:
    customer["email"] = email
    customer["email"] = email


    if name is not None:
    if name is not None:
    customer["name"] = name
    customer["name"] = name


    if metadata is not None:
    if metadata is not None:
    customer["metadata"] = metadata
    customer["metadata"] = metadata


    customer["updated_at"] = datetime.now().isoformat()
    customer["updated_at"] = datetime.now().isoformat()


    return copy.deepcopy(customer)
    return copy.deepcopy(customer)


    def list_customers(
    def list_customers(
    self, email: Optional[str] = None, limit: int = 100
    self, email: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    List customers with optional filtering.
    List customers with optional filtering.


    Args:
    Args:
    email: Filter by email
    email: Filter by email
    limit: Maximum number of customers to return
    limit: Maximum number of customers to return


    Returns:
    Returns:
    List of customer objects
    List of customer objects
    """
    """
    self.record_call("list_customers", email=email, limit=limit)
    self.record_call("list_customers", email=email, limit=limit)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while listing customers")
    raise ConnectionError("Network error while listing customers")


    # Filter customers
    # Filter customers
    filtered_customers = []
    filtered_customers = []


    for customer in self.customers.values():
    for customer in self.customers.values():
    # Apply email filter if provided
    # Apply email filter if provided
    if email and customer["email"] != email:
    if email and customer["email"] != email:
    continue
    continue


    filtered_customers.append(customer)
    filtered_customers.append(customer)


    # Stop if limit is reached
    # Stop if limit is reached
    if len(filtered_customers) >= limit:
    if len(filtered_customers) >= limit:
    break
    break


    return copy.deepcopy(filtered_customers)
    return copy.deepcopy(filtered_customers)


    def delete_customer(self, customer_id: str) -> bool:
    def delete_customer(self, customer_id: str) -> bool:
    """
    """
    Delete a customer.
    Delete a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer


    Returns:
    Returns:
    True if the customer was deleted, False otherwise
    True if the customer was deleted, False otherwise
    """
    """
    self.record_call("delete_customer", customer_id=customer_id)
    self.record_call("delete_customer", customer_id=customer_id)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while deleting customer")
    raise ConnectionError("Network error while deleting customer")


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    # Check if customer has active subscriptions
    # Check if customer has active subscriptions
    for subscription in self.subscriptions.values():
    for subscription in self.subscriptions.values():
    if (
    if (
    subscription["customer_id"] == customer_id
    subscription["customer_id"] == customer_id
    and subscription["status"] == "active"
    and subscription["status"] == "active"
    ):
    ):
    raise ValueError("Cannot delete customer with active subscriptions")
    raise ValueError("Cannot delete customer with active subscriptions")


    # Delete customer
    # Delete customer
    del self.customers[customer_id]
    del self.customers[customer_id]


    # Delete customer's payment methods
    # Delete customer's payment methods
    payment_methods_to_delete = []
    payment_methods_to_delete = []
    for payment_method_id, payment_method in self.payment_methods.items():
    for payment_method_id, payment_method in self.payment_methods.items():
    if payment_method["customer_id"] == customer_id:
    if payment_method["customer_id"] == customer_id:
    payment_methods_to_delete.append(payment_method_id)
    payment_methods_to_delete.append(payment_method_id)


    for payment_method_id in payment_methods_to_delete:
    for payment_method_id in payment_methods_to_delete:
    del self.payment_methods[payment_method_id]
    del self.payment_methods[payment_method_id]


    return True
    return True


    def create_payment_method(
    def create_payment_method(
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
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a new payment method for a customer.
    Create a new payment method for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    payment_type: Type of payment method (card, bank_account, etc.)
    payment_type: Type of payment method (card, bank_account, etc.)
    payment_details: Details of the payment method
    payment_details: Details of the payment method
    metadata: Additional metadata
    metadata: Additional metadata


    Returns:
    Returns:
    Created payment method object
    Created payment method object
    """
    """
    self.record_call(
    self.record_call(
    "create_payment_method",
    "create_payment_method",
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


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while creating payment method")
    raise ConnectionError("Network error while creating payment method")


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    # Check if payment type is supported
    # Check if payment type is supported
    if payment_type not in self.supported_payment_types:
    if payment_type not in self.supported_payment_types:
    raise ValueError(f"Payment type not supported: {payment_type}")
    raise ValueError(f"Payment type not supported: {payment_type}")


    # Process payment details based on payment type
    # Process payment details based on payment type
    payment_details_copy = {}
    payment_details_copy = {}


    if payment_type == "card":
    if payment_type == "card":
    # Validate card details
    # Validate card details
    if "number" not in payment_details:
    if "number" not in payment_details:
    raise ValueError("Card number is required")
    raise ValueError("Card number is required")


    if "exp_month" not in payment_details or "exp_year" not in payment_details:
    if "exp_month" not in payment_details or "exp_year" not in payment_details:
    raise ValueError("Card expiration date is required")
    raise ValueError("Card expiration date is required")


    if "cvc" not in payment_details:
    if "cvc" not in payment_details:
    raise ValueError("Card CVC is required")
    raise ValueError("Card CVC is required")


    # Validate card number
    # Validate card number
    if not self.validate_card_number(payment_details["number"]):
    if not self.validate_card_number(payment_details["number"]):
    raise ValueError("Invalid card number")
    raise ValueError("Invalid card number")


    # Get card type
    # Get card type
    card_type = self.get_card_type(payment_details["number"])
    card_type = self.get_card_type(payment_details["number"])


    # Mask card number
    # Mask card number
    masked_number = self.mask_card_number(payment_details["number"])
    masked_number = self.mask_card_number(payment_details["number"])


    # Create payment details
    # Create payment details
    payment_details_copy = {
    payment_details_copy = {
    "last4": payment_details["number"][-4:],
    "last4": payment_details["number"][-4:],
    "brand": card_type,
    "brand": card_type,
    "exp_month": payment_details["exp_month"],
    "exp_month": payment_details["exp_month"],
    "exp_year": payment_details["exp_year"],
    "exp_year": payment_details["exp_year"],
    "masked_number": masked_number,
    "masked_number": masked_number,
    }
    }


    elif payment_type == "bank_account":
    elif payment_type == "bank_account":
    # Validate bank account details
    # Validate bank account details
    if "account_number" not in payment_details:
    if "account_number" not in payment_details:
    raise ValueError("Account number is required")
    raise ValueError("Account number is required")


    if "routing_number" not in payment_details:
    if "routing_number" not in payment_details:
    raise ValueError("Routing number is required")
    raise ValueError("Routing number is required")


    # Mask account number
    # Mask account number
    masked_account = "****" + payment_details["account_number"][-4:]
    masked_account = "****" + payment_details["account_number"][-4:]


    # Create payment details
    # Create payment details
    payment_details_copy = {
    payment_details_copy = {
    "last4": payment_details["account_number"][-4:],
    "last4": payment_details["account_number"][-4:],
    "bank_name": payment_details.get("bank_name", ""),
    "bank_name": payment_details.get("bank_name", ""),
    "account_type": payment_details.get("account_type", "checking"),
    "account_type": payment_details.get("account_type", "checking"),
    "masked_account": masked_account,
    "masked_account": masked_account,
    }
    }
    else:
    else:
    # For other payment types, just copy the details
    # For other payment types, just copy the details
    payment_details_copy = copy.deepcopy(payment_details)
    payment_details_copy = copy.deepcopy(payment_details)


    # Generate payment method ID
    # Generate payment method ID
    payment_method_id = self._generate_id("pm")
    payment_method_id = self._generate_id("pm")


    # Create payment method
    # Create payment method
    payment_method = {
    payment_method = {
    "id": payment_method_id,
    "id": payment_method_id,
    "customer_id": customer_id,
    "customer_id": customer_id,
    "type": payment_type,
    "type": payment_type,
    "details": payment_details_copy,
    "details": payment_details_copy,
    "metadata": metadata or {},
    "metadata": metadata or {},
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    }
    }


    # Store payment method
    # Store payment method
    self.payment_methods[payment_method_id] = payment_method
    self.payment_methods[payment_method_id] = payment_method


    return copy.deepcopy(payment_method)
    return copy.deepcopy(payment_method)


    def get_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
    def get_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
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
    Payment method object
    Payment method object
    """
    """
    self.record_call("get_payment_method", payment_method_id=payment_method_id)
    self.record_call("get_payment_method", payment_method_id=payment_method_id)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while retrieving payment method")
    raise ConnectionError("Network error while retrieving payment method")


    # Check if payment method exists
    # Check if payment method exists
    if payment_method_id not in self.payment_methods:
    if payment_method_id not in self.payment_methods:
    raise ValueError(f"Payment method not found: {payment_method_id}")
    raise ValueError(f"Payment method not found: {payment_method_id}")


    return copy.deepcopy(self.payment_methods[payment_method_id])
    return copy.deepcopy(self.payment_methods[payment_method_id])


    def list_payment_methods(
    def list_payment_methods(
    self, customer_id: str, payment_type: Optional[str] = None
    self, customer_id: str, payment_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    List payment methods for a customer.
    List payment methods for a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    payment_type: Filter by payment type
    payment_type: Filter by payment type


    Returns:
    Returns:
    List of payment method objects
    List of payment method objects
    """
    """
    self.record_call(
    self.record_call(
    "list_payment_methods", customer_id=customer_id, payment_type=payment_type
    "list_payment_methods", customer_id=customer_id, payment_type=payment_type
    )
    )


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while listing payment methods")
    raise ConnectionError("Network error while listing payment methods")


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    # Filter payment methods
    # Filter payment methods
    filtered_methods = []
    filtered_methods = []


    for payment_method in self.payment_methods.values():
    for payment_method in self.payment_methods.values():
    # Filter by customer ID
    # Filter by customer ID
    if payment_method["customer_id"] != customer_id:
    if payment_method["customer_id"] != customer_id:
    continue
    continue


    # Filter by payment type if provided
    # Filter by payment type if provided
    if payment_type and payment_method["type"] != payment_type:
    if payment_type and payment_method["type"] != payment_type:
    continue
    continue


    filtered_methods.append(payment_method)
    filtered_methods.append(payment_method)


    return copy.deepcopy(filtered_methods)
    return copy.deepcopy(filtered_methods)


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
    self.record_call("delete_payment_method", payment_method_id=payment_method_id)
    self.record_call("delete_payment_method", payment_method_id=payment_method_id)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while deleting payment method")
    raise ConnectionError("Network error while deleting payment method")


    # Check if payment method exists
    # Check if payment method exists
    if payment_method_id not in self.payment_methods:
    if payment_method_id not in self.payment_methods:
    raise ValueError(f"Payment method not found: {payment_method_id}")
    raise ValueError(f"Payment method not found: {payment_method_id}")


    # Check if payment method is being used in an active subscription
    # Check if payment method is being used in an active subscription
    for subscription in self.subscriptions.values():
    for subscription in self.subscriptions.values():
    if (
    if (
    subscription["payment_method_id"] == payment_method_id
    subscription["payment_method_id"] == payment_method_id
    and subscription["status"] == "active"
    and subscription["status"] == "active"
    ):
    ):
    raise ValueError(
    raise ValueError(
    "Cannot delete payment method being used in active subscription"
    "Cannot delete payment method being used in active subscription"
    )
    )


    # Delete payment method
    # Delete payment method
    del self.payment_methods[payment_method_id]
    del self.payment_methods[payment_method_id]


    return True
    return True


    def create_payment(
    def create_payment(
    self,
    self,
    amount: float,
    amount: float,
    currency: str,
    currency: str,
    payment_method_id: str,
    payment_method_id: str,
    description: str,
    description: str,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Process a payment.
    Process a payment.


    Args:
    Args:
    amount: Payment amount
    amount: Payment amount
    currency: Payment currency code
    currency: Payment currency code
    payment_method_id: ID of the payment method to use
    payment_method_id: ID of the payment method to use
    description: Description of the payment
    description: Description of the payment
    metadata: Additional metadata
    metadata: Additional metadata


    Returns:
    Returns:
    Payment object
    Payment object
    """
    """
    self.record_call(
    self.record_call(
    "create_payment",
    "create_payment",
    amount=amount,
    amount=amount,
    currency=currency,
    currency=currency,
    payment_method_id=payment_method_id,
    payment_method_id=payment_method_id,
    description=description,
    description=description,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while processing payment")
    raise ConnectionError("Network error while processing payment")


    # Check if payment method exists
    # Check if payment method exists
    if payment_method_id not in self.payment_methods:
    if payment_method_id not in self.payment_methods:
    raise ValueError(f"Payment method not found: {payment_method_id}")
    raise ValueError(f"Payment method not found: {payment_method_id}")


    # Check if currency is supported
    # Check if currency is supported
    if currency not in self.supported_currencies:
    if currency not in self.supported_currencies:
    raise ValueError(f"Currency not supported: {currency}")
    raise ValueError(f"Currency not supported: {currency}")


    # Get payment method
    # Get payment method
    payment_method = self.payment_methods[payment_method_id]
    payment_method = self.payment_methods[payment_method_id]


    # Get customer
    # Get customer
    customer_id = payment_method["customer_id"]
    customer_id = payment_method["customer_id"]
    customer = self.customers.get(customer_id)
    customer = self.customers.get(customer_id)


    if not customer:
    if not customer:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    # Simulate payment success or failure
    # Simulate payment success or failure
    success = self._simulate_success()
    success = self._simulate_success()


    # Generate payment ID
    # Generate payment ID
    payment_id = self._generate_id("pay")
    payment_id = self._generate_id("pay")


    # Create payment
    # Create payment
    payment = {
    payment = {
    "id": payment_id,
    "id": payment_id,
    "amount": amount,
    "amount": amount,
    "currency": currency,
    "currency": currency,
    "customer_id": customer_id,
    "customer_id": customer_id,
    "payment_method_id": payment_method_id,
    "payment_method_id": payment_method_id,
    "description": description,
    "description": description,
    "metadata": metadata or {},
    "metadata": metadata or {},
    "status": PaymentStatus.SUCCEEDED if success else PaymentStatus.FAILED,
    "status": PaymentStatus.SUCCEEDED if success else PaymentStatus.FAILED,
    "error": (
    "error": (
    None
    None
    if success
    if success
    else {"code": "card_declined", "message": "Your card was declined."}
    else {"code": "card_declined", "message": "Your card was declined."}
    ),
    ),
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    }
    }


    # Store payment
    # Store payment
    self.payments[payment_id] = payment
    self.payments[payment_id] = payment


    # If payment failed, raise an exception
    # If payment failed, raise an exception
    if not success:
    if not success:
    raise ValueError("Payment failed: Your card was declined.")
    raise ValueError("Payment failed: Your card was declined.")


    return copy.deepcopy(payment)
    return copy.deepcopy(payment)


    def get_payment(self, payment_id: str) -> Dict[str, Any]:
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
    """
    """
    Get a payment by ID.
    Get a payment by ID.


    Args:
    Args:
    payment_id: ID of the payment
    payment_id: ID of the payment


    Returns:
    Returns:
    Payment object
    Payment object
    """
    """
    self.record_call("get_payment", payment_id=payment_id)
    self.record_call("get_payment", payment_id=payment_id)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while retrieving payment")
    raise ConnectionError("Network error while retrieving payment")


    # Check if payment exists
    # Check if payment exists
    if payment_id not in self.payments:
    if payment_id not in self.payments:
    raise ValueError(f"Payment not found: {payment_id}")
    raise ValueError(f"Payment not found: {payment_id}")


    return copy.deepcopy(self.payments[payment_id])
    return copy.deepcopy(self.payments[payment_id])


    def list_payments(
    def list_payments(
    self,
    self,
    customer_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    payment_method_id: Optional[str] = None,
    payment_method_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    limit: int = 100,
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    List payments with optional filtering.
    List payments with optional filtering.


    Args:
    Args:
    customer_id: Filter by customer ID
    customer_id: Filter by customer ID
    payment_method_id: Filter by payment method ID
    payment_method_id: Filter by payment method ID
    start_date: Filter by start date
    start_date: Filter by start date
    end_date: Filter by end date
    end_date: Filter by end date
    status: Filter by payment status
    status: Filter by payment status
    limit: Maximum number of payments to return
    limit: Maximum number of payments to return


    Returns:
    Returns:
    List of payment objects
    List of payment objects
    """
    """
    self.record_call(
    self.record_call(
    "list_payments",
    "list_payments",
    customer_id=customer_id,
    customer_id=customer_id,
    payment_method_id=payment_method_id,
    payment_method_id=payment_method_id,
    start_date=start_date,
    start_date=start_date,
    end_date=end_date,
    end_date=end_date,
    status=status,
    status=status,
    limit=limit,
    limit=limit,
    )
    )


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while listing payments")
    raise ConnectionError("Network error while listing payments")


    # Filter payments
    # Filter payments
    filtered_payments = []
    filtered_payments = []


    for payment in self.payments.values():
    for payment in self.payments.values():
    # Filter by customer ID if provided
    # Filter by customer ID if provided
    if customer_id and payment["customer_id"] != customer_id:
    if customer_id and payment["customer_id"] != customer_id:
    continue
    continue


    # Filter by payment method ID if provided
    # Filter by payment method ID if provided
    if payment_method_id and payment["payment_method_id"] != payment_method_id:
    if payment_method_id and payment["payment_method_id"] != payment_method_id:
    continue
    continue


    # Filter by status if provided
    # Filter by status if provided
    if status and payment["status"] != status:
    if status and payment["status"] != status:
    continue
    continue


    # Filter by date range if provided
    # Filter by date range if provided
    if start_date or end_date:
    if start_date or end_date:
    payment_date = datetime.fromisoformat(payment["created_at"])
    payment_date = datetime.fromisoformat(payment["created_at"])


    if start_date and payment_date < start_date:
    if start_date and payment_date < start_date:
    continue
    continue


    if end_date and payment_date > end_date:
    if end_date and payment_date > end_date:
    continue
    continue


    filtered_payments.append(payment)
    filtered_payments.append(payment)


    # Apply limit
    # Apply limit
    if len(filtered_payments) >= limit:
    if len(filtered_payments) >= limit:
    break
    break


    # Sort by created_at (newest first)
    # Sort by created_at (newest first)
    filtered_payments.sort(key=lambda p: p["created_at"], reverse=True)
    filtered_payments.sort(key=lambda p: p["created_at"], reverse=True)


    return copy.deepcopy(filtered_payments)
    return copy.deepcopy(filtered_payments)


    def refund_payment(
    def refund_payment(
    self,
    self,
    payment_id: str,
    payment_id: str,
    amount: Optional[float] = None,
    amount: Optional[float] = None,
    reason: Optional[str] = None,
    reason: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Refund a payment.
    Refund a payment.


    Args:
    Args:
    payment_id: ID of the payment to refund
    payment_id: ID of the payment to refund
    amount: Amount to refund (defaults to full payment amount)
    amount: Amount to refund (defaults to full payment amount)
    reason: Reason for the refund
    reason: Reason for the refund


    Returns:
    Returns:
    Refund object
    Refund object
    """
    """
    self.record_call(
    self.record_call(
    "refund_payment", payment_id=payment_id, amount=amount, reason=reason
    "refund_payment", payment_id=payment_id, amount=amount, reason=reason
    )
    )


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while refunding payment")
    raise ConnectionError("Network error while refunding payment")


    # Check if payment exists
    # Check if payment exists
    if payment_id not in self.payments:
    if payment_id not in self.payments:
    raise ValueError(f"Payment not found: {payment_id}")
    raise ValueError(f"Payment not found: {payment_id}")


    # Get the payment
    # Get the payment
    payment = self.payments[payment_id]
    payment = self.payments[payment_id]


    # Check if payment can be refunded
    # Check if payment can be refunded
    if payment["status"] != PaymentStatus.SUCCEEDED:
    if payment["status"] != PaymentStatus.SUCCEEDED:
    raise ValueError(f"Payment cannot be refunded: {payment['status']}")
    raise ValueError(f"Payment cannot be refunded: {payment['status']}")


    # Determine refund amount
    # Determine refund amount
    refund_amount = amount if amount is not None else payment["amount"]
    refund_amount = amount if amount is not None else payment["amount"]


    # Check if refund amount is valid
    # Check if refund amount is valid
    if refund_amount <= 0 or refund_amount > payment["amount"]:
    if refund_amount <= 0 or refund_amount > payment["amount"]:
    raise ValueError(f"Invalid refund amount: {refund_amount}")
    raise ValueError(f"Invalid refund amount: {refund_amount}")


    # Simulate refund success or failure
    # Simulate refund success or failure
    success = self._simulate_success(self.refund_success_rate)
    success = self._simulate_success(self.refund_success_rate)


    # Generate refund ID
    # Generate refund ID
    refund_id = self._generate_id("ref")
    refund_id = self._generate_id("ref")


    # Create refund
    # Create refund
    refund = {
    refund = {
    "id": refund_id,
    "id": refund_id,
    "payment_id": payment_id,
    "payment_id": payment_id,
    "amount": refund_amount,
    "amount": refund_amount,
    "currency": payment["currency"],
    "currency": payment["currency"],
    "reason": reason or "requested_by_customer",
    "reason": reason or "requested_by_customer",
    "status": PaymentStatus.SUCCEEDED if success else PaymentStatus.FAILED,
    "status": PaymentStatus.SUCCEEDED if success else PaymentStatus.FAILED,
    "error": (
    "error": (
    None
    None
    if success
    if success
    else {
    else {
    "code": "refund_failed",
    "code": "refund_failed",
    "message": "The refund could not be processed.",
    "message": "The refund could not be processed.",
    }
    }
    ),
    ),
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    }
    }


    # Store refund
    # Store refund
    self.refunds[refund_id] = refund
    self.refunds[refund_id] = refund


    # Update payment status if refund was successful
    # Update payment status if refund was successful
    if success:
    if success:
    if refund_amount == payment["amount"]:
    if refund_amount == payment["amount"]:
    payment["status"] = PaymentStatus.REFUNDED
    payment["status"] = PaymentStatus.REFUNDED
    else:
    else:
    payment["status"] = PaymentStatus.PARTIALLY_REFUNDED
    payment["status"] = PaymentStatus.PARTIALLY_REFUNDED


    payment["updated_at"] = datetime.now().isoformat()
    payment["updated_at"] = datetime.now().isoformat()


    # If refund failed, raise an exception
    # If refund failed, raise an exception
    if not success:
    if not success:
    raise ValueError("Refund failed: The refund could not be processed.")
    raise ValueError("Refund failed: The refund could not be processed.")


    return copy.deepcopy(refund)
    return copy.deepcopy(refund)


    def get_refund(self, refund_id: str) -> Dict[str, Any]:
    def get_refund(self, refund_id: str) -> Dict[str, Any]:
    """
    """
    Get a refund by ID.
    Get a refund by ID.


    Args:
    Args:
    refund_id: ID of the refund
    refund_id: ID of the refund


    Returns:
    Returns:
    Refund object
    Refund object
    """
    """
    self.record_call("get_refund", refund_id=refund_id)
    self.record_call("get_refund", refund_id=refund_id)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while retrieving refund")
    raise ConnectionError("Network error while retrieving refund")


    # Check if refund exists
    # Check if refund exists
    if refund_id not in self.refunds:
    if refund_id not in self.refunds:
    raise ValueError(f"Refund not found: {refund_id}")
    raise ValueError(f"Refund not found: {refund_id}")


    return copy.deepcopy(self.refunds[refund_id])
    return copy.deepcopy(self.refunds[refund_id])


    def list_refunds(
    def list_refunds(
    self, payment_id: Optional[str] = None, limit: int = 100
    self, payment_id: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    List refunds with optional filtering.
    List refunds with optional filtering.


    Args:
    Args:
    payment_id: Filter by payment ID
    payment_id: Filter by payment ID
    limit: Maximum number of refunds to return
    limit: Maximum number of refunds to return


    Returns:
    Returns:
    List of refund objects
    List of refund objects
    """
    """
    self.record_call("list_refunds", payment_id=payment_id, limit=limit)
    self.record_call("list_refunds", payment_id=payment_id, limit=limit)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while listing refunds")
    raise ConnectionError("Network error while listing refunds")


    # Filter refunds
    # Filter refunds
    filtered_refunds = []
    filtered_refunds = []


    for refund in self.refunds.values():
    for refund in self.refunds.values():
    # Filter by payment ID if provided
    # Filter by payment ID if provided
    if payment_id and refund["payment_id"] != payment_id:
    if payment_id and refund["payment_id"] != payment_id:
    continue
    continue


    filtered_refunds.append(refund)
    filtered_refunds.append(refund)


    # Apply limit
    # Apply limit
    if len(filtered_refunds) >= limit:
    if len(filtered_refunds) >= limit:
    break
    break


    # Sort by created_at (newest first)
    # Sort by created_at (newest first)
    filtered_refunds.sort(key=lambda r: r["created_at"], reverse=True)
    filtered_refunds.sort(key=lambda r: r["created_at"], reverse=True)


    return copy.deepcopy(filtered_refunds)
    return copy.deepcopy(filtered_refunds)


    def create_plan(
    def create_plan(
    self,
    self,
    name: str,
    name: str,
    currency: str,
    currency: str,
    interval: str,
    interval: str,
    amount: float,
    amount: float,
    product_id: Optional[str] = None,
    product_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a billing plan.
    Create a billing plan.


    Args:
    Args:
    name: Plan name
    name: Plan name
    currency: Plan currency code
    currency: Plan currency code
    interval: Billing interval (day, week, month, year)
    interval: Billing interval (day, week, month, year)
    amount: Plan amount
    amount: Plan amount
    product_id: ID of the associated product
    product_id: ID of the associated product
    metadata: Additional metadata
    metadata: Additional metadata


    Returns:
    Returns:
    Plan object
    Plan object
    """
    """
    self.record_call(
    self.record_call(
    "create_plan",
    "create_plan",
    name=name,
    name=name,
    currency=currency,
    currency=currency,
    interval=interval,
    interval=interval,
    amount=amount,
    amount=amount,
    product_id=product_id,
    product_id=product_id,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while creating plan")
    raise ConnectionError("Network error while creating plan")


    # Check if currency is supported
    # Check if currency is supported
    if currency not in self.supported_currencies:
    if currency not in self.supported_currencies:
    raise ValueError(f"Currency not supported: {currency}")
    raise ValueError(f"Currency not supported: {currency}")


    # Check if interval is valid
    # Check if interval is valid
    valid_intervals = ["day", "week", "month", "year"]
    valid_intervals = ["day", "week", "month", "year"]
    if interval not in valid_intervals:
    if interval not in valid_intervals:
    raise ValueError(
    raise ValueError(
    f"Invalid interval: {interval}. Must be one of: {', '.join(valid_intervals)}"
    f"Invalid interval: {interval}. Must be one of: {', '.join(valid_intervals)}"
    )
    )


    # Generate plan ID
    # Generate plan ID
    plan_id = self._generate_id("plan")
    plan_id = self._generate_id("plan")


    # Create plan
    # Create plan
    plan = {
    plan = {
    "id": plan_id,
    "id": plan_id,
    "name": name,
    "name": name,
    "currency": currency,
    "currency": currency,
    "interval": interval,
    "interval": interval,
    "amount": amount,
    "amount": amount,
    "product_id": product_id,
    "product_id": product_id,
    "metadata": metadata or {},
    "metadata": metadata or {},
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    }
    }


    # Store plan
    # Store plan
    self.plans[plan_id] = plan
    self.plans[plan_id] = plan


    return copy.deepcopy(plan)
    return copy.deepcopy(plan)


    def get_plan(self, plan_id: str) -> Dict[str, Any]:
    def get_plan(self, plan_id: str) -> Dict[str, Any]:
    """
    """
    Get a plan by ID.
    Get a plan by ID.


    Args:
    Args:
    plan_id: ID of the plan
    plan_id: ID of the plan


    Returns:
    Returns:
    Plan object
    Plan object
    """
    """
    self.record_call("get_plan", plan_id=plan_id)
    self.record_call("get_plan", plan_id=plan_id)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while retrieving plan")
    raise ConnectionError("Network error while retrieving plan")


    # Check if plan exists
    # Check if plan exists
    if plan_id not in self.plans:
    if plan_id not in self.plans:
    raise ValueError(f"Plan not found: {plan_id}")
    raise ValueError(f"Plan not found: {plan_id}")


    return copy.deepcopy(self.plans[plan_id])
    return copy.deepcopy(self.plans[plan_id])


    def list_plans(self, limit: int = 100) -> List[Dict[str, Any]]:
    def list_plans(self, limit: int = 100) -> List[Dict[str, Any]]:
    """
    """
    List all plans.
    List all plans.


    Args:
    Args:
    limit: Maximum number of plans to return
    limit: Maximum number of plans to return


    Returns:
    Returns:
    List of plan objects
    List of plan objects
    """
    """
    self.record_call("list_plans", limit=limit)
    self.record_call("list_plans", limit=limit)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while listing plans")
    raise ConnectionError("Network error while listing plans")


    # Get all plans up to the limit
    # Get all plans up to the limit
    plans_list = list(self.plans.values())[:limit]
    plans_list = list(self.plans.values())[:limit]


    return copy.deepcopy(plans_list)
    return copy.deepcopy(plans_list)


    def create_subscription(
    def create_subscription(
    self,
    self,
    customer_id: str,
    customer_id: str,
    plan_id: str,
    plan_id: str,
    payment_method_id: str,
    payment_method_id: str,
    trial_end: Optional[datetime] = None,
    trial_end: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Create a subscription.
    Create a subscription.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    plan_id: ID of the plan
    plan_id: ID of the plan
    payment_method_id: ID of the payment method to use
    payment_method_id: ID of the payment method to use
    trial_end: End date of the trial period
    trial_end: End date of the trial period
    metadata: Additional metadata
    metadata: Additional metadata


    Returns:
    Returns:
    Subscription object
    Subscription object
    """
    """
    self.record_call(
    self.record_call(
    "create_subscription",
    "create_subscription",
    customer_id=customer_id,
    customer_id=customer_id,
    plan_id=plan_id,
    plan_id=plan_id,
    payment_method_id=payment_method_id,
    payment_method_id=payment_method_id,
    trial_end=trial_end,
    trial_end=trial_end,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while creating subscription")
    raise ConnectionError("Network error while creating subscription")


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    # Check if plan exists
    # Check if plan exists
    if plan_id not in self.plans:
    if plan_id not in self.plans:
    raise ValueError(f"Plan not found: {plan_id}")
    raise ValueError(f"Plan not found: {plan_id}")


    # Check if payment method exists
    # Check if payment method exists
    if payment_method_id not in self.payment_methods:
    if payment_method_id not in self.payment_methods:
    raise ValueError(f"Payment method not found: {payment_method_id}")
    raise ValueError(f"Payment method not found: {payment_method_id}")


    # Check if payment method belongs to customer
    # Check if payment method belongs to customer
    payment_method = self.payment_methods[payment_method_id]
    payment_method = self.payment_methods[payment_method_id]
    if payment_method["customer_id"] != customer_id:
    if payment_method["customer_id"] != customer_id:
    raise ValueError(
    raise ValueError(
    f"Payment method {payment_method_id} does not belong to customer {customer_id}"
    f"Payment method {payment_method_id} does not belong to customer {customer_id}"
    )
    )


    # Get plan
    # Get plan
    plan = self.plans[plan_id]
    plan = self.plans[plan_id]


    # Determine interval in days
    # Determine interval in days
    interval_days = {"day": 1, "week": 7, "month": 30, "year": 365}
    interval_days = {"day": 1, "week": 7, "month": 30, "year": 365}
    days = interval_days.get(plan["interval"], 30)
    days = interval_days.get(plan["interval"], 30)


    # Calculate current period dates
    # Calculate current period dates
    now = datetime.now()
    now = datetime.now()
    current_period_start = now
    current_period_start = now
    current_period_end = now + timedelta(days=days)
    current_period_end = now + timedelta(days=days)


    # Generate subscription ID
    # Generate subscription ID
    subscription_id = self._generate_id("sub")
    subscription_id = self._generate_id("sub")


    # Determine status based on trial
    # Determine status based on trial
    if trial_end and trial_end > now:
    if trial_end and trial_end > now:
    status = "trialing"
    status = "trialing"
    else:
    else:
    status = "active"
    status = "active"


    # Process initial payment if not in trial
    # Process initial payment if not in trial
    try:
    try:
    self.create_payment(
    self.create_payment(
    amount=plan["amount"],
    amount=plan["amount"],
    currency=plan["currency"],
    currency=plan["currency"],
    payment_method_id=payment_method_id,
    payment_method_id=payment_method_id,
    description=f"Initial payment for subscription {subscription_id}",
    description=f"Initial payment for subscription {subscription_id}",
    metadata={"subscription_id": subscription_id},
    metadata={"subscription_id": subscription_id},
    )
    )
except ValueError:
except ValueError:
    # If payment fails, return subscription with status "incomplete"
    # If payment fails, return subscription with status "incomplete"
    status = "incomplete"
    status = "incomplete"


    # Create subscription
    # Create subscription
    subscription = {
    subscription = {
    "id": subscription_id,
    "id": subscription_id,
    "customer_id": customer_id,
    "customer_id": customer_id,
    "plan_id": plan_id,
    "plan_id": plan_id,
    "payment_method_id": payment_method_id,
    "payment_method_id": payment_method_id,
    "status": status,
    "status": status,
    "current_period_start": current_period_start.isoformat(),
    "current_period_start": current_period_start.isoformat(),
    "current_period_end": current_period_end.isoformat(),
    "current_period_end": current_period_end.isoformat(),
    "trial_start": now.isoformat() if trial_end else None,
    "trial_start": now.isoformat() if trial_end else None,
    "trial_end": trial_end.isoformat() if trial_end else None,
    "trial_end": trial_end.isoformat() if trial_end else None,
    "cancel_at_period_end": False,
    "cancel_at_period_end": False,
    "canceled_at": None,
    "canceled_at": None,
    "ended_at": None,
    "ended_at": None,
    "metadata": metadata or {},
    "metadata": metadata or {},
    "created_at": now.isoformat(),
    "created_at": now.isoformat(),
    "updated_at": now.isoformat(),
    "updated_at": now.isoformat(),
    }
    }


    # Store subscription
    # Store subscription
    self.subscriptions[subscription_id] = subscription
    self.subscriptions[subscription_id] = subscription


    return copy.deepcopy(subscription)
    return copy.deepcopy(subscription)


    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
    """
    """
    Get a subscription by ID.
    Get a subscription by ID.


    Args:
    Args:
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription


    Returns:
    Returns:
    Subscription object
    Subscription object
    """
    """
    self.record_call("get_subscription", subscription_id=subscription_id)
    self.record_call("get_subscription", subscription_id=subscription_id)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while retrieving subscription")
    raise ConnectionError("Network error while retrieving subscription")


    # Check if subscription exists
    # Check if subscription exists
    if subscription_id not in self.subscriptions:
    if subscription_id not in self.subscriptions:
    raise ValueError(f"Subscription not found: {subscription_id}")
    raise ValueError(f"Subscription not found: {subscription_id}")


    return copy.deepcopy(self.subscriptions[subscription_id])
    return copy.deepcopy(self.subscriptions[subscription_id])


    def update_subscription(
    def update_subscription(
    self,
    self,
    subscription_id: str,
    subscription_id: str,
    plan_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    payment_method_id: Optional[str] = None,
    payment_method_id: Optional[str] = None,
    trial_end: Optional[datetime] = None,
    trial_end: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Update a subscription.
    Update a subscription.


    Args:
    Args:
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription
    plan_id: New plan ID
    plan_id: New plan ID
    payment_method_id: New payment method ID
    payment_method_id: New payment method ID
    trial_end: New trial end date
    trial_end: New trial end date
    metadata: New metadata
    metadata: New metadata


    Returns:
    Returns:
    Updated subscription object
    Updated subscription object
    """
    """
    self.record_call(
    self.record_call(
    "update_subscription",
    "update_subscription",
    subscription_id=subscription_id,
    subscription_id=subscription_id,
    plan_id=plan_id,
    plan_id=plan_id,
    payment_method_id=payment_method_id,
    payment_method_id=payment_method_id,
    trial_end=trial_end,
    trial_end=trial_end,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while updating subscription")
    raise ConnectionError("Network error while updating subscription")


    # Check if subscription exists
    # Check if subscription exists
    if subscription_id not in self.subscriptions:
    if subscription_id not in self.subscriptions:
    raise ValueError(f"Subscription not found: {subscription_id}")
    raise ValueError(f"Subscription not found: {subscription_id}")


    # Get subscription
    # Get subscription
    subscription = self.subscriptions[subscription_id]
    subscription = self.subscriptions[subscription_id]


    # Check if subscription is active
    # Check if subscription is active
    if subscription["status"] not in ["active", "trialing", "past_due"]:
    if subscription["status"] not in ["active", "trialing", "past_due"]:
    raise ValueError(
    raise ValueError(
    f"Cannot update subscription with status: {subscription['status']}"
    f"Cannot update subscription with status: {subscription['status']}"
    )
    )


    # Update plan if provided
    # Update plan if provided
    if plan_id is not None:
    if plan_id is not None:
    # Check if plan exists
    # Check if plan exists
    if plan_id not in self.plans:
    if plan_id not in self.plans:
    raise ValueError(f"Plan not found: {plan_id}")
    raise ValueError(f"Plan not found: {plan_id}")


    subscription["plan_id"] = plan_id
    subscription["plan_id"] = plan_id


    # Update payment method if provided
    # Update payment method if provided
    if payment_method_id is not None:
    if payment_method_id is not None:
    # Check if payment method exists
    # Check if payment method exists
    if payment_method_id not in self.payment_methods:
    if payment_method_id not in self.payment_methods:
    raise ValueError(f"Payment method not found: {payment_method_id}")
    raise ValueError(f"Payment method not found: {payment_method_id}")


    # Check if payment method belongs to customer
    # Check if payment method belongs to customer
    payment_method = self.payment_methods[payment_method_id]
    payment_method = self.payment_methods[payment_method_id]
    if payment_method["customer_id"] != subscription["customer_id"]:
    if payment_method["customer_id"] != subscription["customer_id"]:
    raise ValueError(
    raise ValueError(
    f"Payment method {payment_method_id} does not belong to customer {subscription['customer_id']}"
    f"Payment method {payment_method_id} does not belong to customer {subscription['customer_id']}"
    )
    )


    subscription["payment_method_id"] = payment_method_id
    subscription["payment_method_id"] = payment_method_id


    # Update trial end if provided
    # Update trial end if provided
    if trial_end is not None:
    if trial_end is not None:
    now = datetime.now()
    now = datetime.now()


    # If trial end is in the future, set subscription to trialing
    # If trial end is in the future, set subscription to trialing
    if trial_end > now:
    if trial_end > now:
    subscription["status"] = "trialing"
    subscription["status"] = "trialing"
    subscription["trial_end"] = trial_end.isoformat()
    subscription["trial_end"] = trial_end.isoformat()


    # If trial end is in the past, end trial and set to active
    # If trial end is in the past, end trial and set to active
    elif subscription["status"] == "trialing":
    elif subscription["status"] == "trialing":
    subscription["status"] = "active"
    subscription["status"] = "active"
    subscription["trial_end"] = trial_end.isoformat()
    subscription["trial_end"] = trial_end.isoformat()


    # Update metadata if provided
    # Update metadata if provided
    if metadata is not None:
    if metadata is not None:
    subscription["metadata"] = metadata
    subscription["metadata"] = metadata


    subscription["updated_at"] = datetime.now().isoformat()
    subscription["updated_at"] = datetime.now().isoformat()


    return copy.deepcopy(subscription)
    return copy.deepcopy(subscription)


    def cancel_subscription(
    def cancel_subscription(
    self, subscription_id: str, cancel_at_period_end: bool = True
    self, subscription_id: str, cancel_at_period_end: bool = True
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Cancel a subscription.
    Cancel a subscription.


    Args:
    Args:
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription
    cancel_at_period_end: Whether to cancel at the end of the current period
    cancel_at_period_end: Whether to cancel at the end of the current period


    Returns:
    Returns:
    Updated subscription object
    Updated subscription object
    """
    """
    self.record_call(
    self.record_call(
    "cancel_subscription",
    "cancel_subscription",
    subscription_id=subscription_id,
    subscription_id=subscription_id,
    cancel_at_period_end=cancel_at_period_end,
    cancel_at_period_end=cancel_at_period_end,
    )
    )


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while canceling subscription")
    raise ConnectionError("Network error while canceling subscription")


    # Check if subscription exists
    # Check if subscription exists
    if subscription_id not in self.subscriptions:
    if subscription_id not in self.subscriptions:
    raise ValueError(f"Subscription not found: {subscription_id}")
    raise ValueError(f"Subscription not found: {subscription_id}")


    # Get subscription
    # Get subscription
    subscription = self.subscriptions[subscription_id]
    subscription = self.subscriptions[subscription_id]


    # Check if subscription is active or trialing
    # Check if subscription is active or trialing
    if subscription["status"] not in ["active", "trialing", "past_due"]:
    if subscription["status"] not in ["active", "trialing", "past_due"]:
    raise ValueError(
    raise ValueError(
    f"Cannot cancel subscription with status: {subscription['status']}"
    f"Cannot cancel subscription with status: {subscription['status']}"
    )
    )


    # Update subscription
    # Update subscription
    subscription["canceled_at"] = datetime.now().isoformat()
    subscription["canceled_at"] = datetime.now().isoformat()


    if cancel_at_period_end:
    if cancel_at_period_end:
    subscription["cancel_at_period_end"] = True
    subscription["cancel_at_period_end"] = True
    else:
    else:
    subscription["status"] = "canceled"
    subscription["status"] = "canceled"
    subscription["ended_at"] = datetime.now().isoformat()
    subscription["ended_at"] = datetime.now().isoformat()


    subscription["updated_at"] = datetime.now().isoformat()
    subscription["updated_at"] = datetime.now().isoformat()


    return copy.deepcopy(subscription)
    return copy.deepcopy(subscription)


    def resume_subscription(self, subscription_id: str) -> Dict[str, Any]:
    def resume_subscription(self, subscription_id: str) -> Dict[str, Any]:
    """
    """
    Resume a canceled subscription.
    Resume a canceled subscription.


    Args:
    Args:
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription


    Returns:
    Returns:
    Updated subscription object
    Updated subscription object
    """
    """
    self.record_call("resume_subscription", subscription_id=subscription_id)
    self.record_call("resume_subscription", subscription_id=subscription_id)


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while resuming subscription")
    raise ConnectionError("Network error while resuming subscription")


    # Check if subscription exists
    # Check if subscription exists
    if subscription_id not in self.subscriptions:
    if subscription_id not in self.subscriptions:
    raise ValueError(f"Subscription not found: {subscription_id}")
    raise ValueError(f"Subscription not found: {subscription_id}")


    # Get subscription
    # Get subscription
    subscription = self.subscriptions[subscription_id]
    subscription = self.subscriptions[subscription_id]


    # Check if subscription can be resumed
    # Check if subscription can be resumed
    if (
    if (
    subscription["status"] != "canceled"
    subscription["status"] != "canceled"
    and not subscription["cancel_at_period_end"]
    and not subscription["cancel_at_period_end"]
    ):
    ):
    raise ValueError(f"Subscription is not canceled: {subscription['status']}")
    raise ValueError(f"Subscription is not canceled: {subscription['status']}")


    # Update subscription
    # Update subscription
    if subscription["status"] == "canceled":
    if subscription["status"] == "canceled":
    # If already canceled, recreate subscription
    # If already canceled, recreate subscription
    subscription["status"] = "active"
    subscription["status"] = "active"
    subscription["ended_at"] = None
    subscription["ended_at"] = None


    # Calculate new period dates
    # Calculate new period dates
    now = datetime.now()
    now = datetime.now()


    # Get plan
    # Get plan
    plan = self.plans.get(subscription["plan_id"])
    plan = self.plans.get(subscription["plan_id"])
    if not plan:
    if not plan:
    raise ValueError(f"Plan not found: {subscription['plan_id']}")
    raise ValueError(f"Plan not found: {subscription['plan_id']}")


    # Determine interval in days
    # Determine interval in days
    interval_days = {"day": 1, "week": 7, "month": 30, "year": 365}
    interval_days = {"day": 1, "week": 7, "month": 30, "year": 365}
    days = interval_days.get(plan["interval"], 30)
    days = interval_days.get(plan["interval"], 30)


    subscription["current_period_start"] = now.isoformat()
    subscription["current_period_start"] = now.isoformat()
    subscription["current_period_end"] = (
    subscription["current_period_end"] = (
    now + timedelta(days=days)
    now + timedelta(days=days)
    ).isoformat()
    ).isoformat()


    # Clear cancellation
    # Clear cancellation
    subscription["cancel_at_period_end"] = False
    subscription["cancel_at_period_end"] = False
    subscription["canceled_at"] = None
    subscription["canceled_at"] = None
    subscription["updated_at"] = datetime.now().isoformat()
    subscription["updated_at"] = datetime.now().isoformat()


    return copy.deepcopy(subscription)
    return copy.deepcopy(subscription)


    def list_subscriptions(
    def list_subscriptions(
    self,
    self,
    customer_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    status: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    limit: int = 100,
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    List subscriptions with optional filtering.
    List subscriptions with optional filtering.


    Args:
    Args:
    customer_id: Filter by customer ID
    customer_id: Filter by customer ID
    plan_id: Filter by plan ID
    plan_id: Filter by plan ID
    status: Filter by subscription status
    status: Filter by subscription status
    limit: Maximum number of subscriptions to return
    limit: Maximum number of subscriptions to return


    Returns:
    Returns:
    List of subscription objects
    List of subscription objects
    """
    """
    self.record_call(
    self.record_call(
    "list_subscriptions",
    "list_subscriptions",
    customer_id=customer_id,
    customer_id=customer_id,
    plan_id=plan_id,
    plan_id=plan_id,
    status=status,
    status=status,
    limit=limit,
    limit=limit,
    )
    )


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while listing subscriptions")
    raise ConnectionError("Network error while listing subscriptions")


    # Filter subscriptions
    # Filter subscriptions
    filtered_subscriptions = []
    filtered_subscriptions = []


    for subscription in self.subscriptions.values():
    for subscription in self.subscriptions.values():
    # Filter by customer ID if provided
    # Filter by customer ID if provided
    if customer_id and subscription["customer_id"] != customer_id:
    if customer_id and subscription["customer_id"] != customer_id:
    continue
    continue


    # Filter by plan ID if provided
    # Filter by plan ID if provided
    if plan_id and subscription["plan_id"] != plan_id:
    if plan_id and subscription["plan_id"] != plan_id:
    continue
    continue


    # Filter by status if provided
    # Filter by status if provided
    if status and subscription["status"] != status:
    if status and subscription["status"] != status:
    continue
    continue


    filtered_subscriptions.append(subscription)
    filtered_subscriptions.append(subscription)


    # Apply limit
    # Apply limit
    if len(filtered_subscriptions) >= limit:
    if len(filtered_subscriptions) >= limit:
    break
    break


    # Sort by created_at (newest first)
    # Sort by created_at (newest first)
    filtered_subscriptions.sort(key=lambda s: s["created_at"], reverse=True)
    filtered_subscriptions.sort(key=lambda s: s["created_at"], reverse=True)


    return copy.deepcopy(filtered_subscriptions)
    return copy.deepcopy(filtered_subscriptions)




    class MockStripeGateway(MockPaymentGateway):
    class MockStripeGateway(MockPaymentGateway):
    """Mock implementation of Stripe payment gateway."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
    """Initialize the mock Stripe gateway."""
    super().__init__(config)

    # Set Stripe-specific properties
    self.gateway_name = "stripe"
    self.api_version = "2023-10-16"

    def create_token(
    self, payment_type: str, payment_details: Dict[str, Any]
    ) -> Dict[str, Any]:
    """
    """
    Create a payment token.
    Create a payment token.


    Args:
    Args:
    payment_type: Type of payment method
    payment_type: Type of payment method
    payment_details: Payment details
    payment_details: Payment details


    Returns:
    Returns:
    Token object
    Token object
    """
    """
    self.record_call(
    self.record_call(
    "create_token", payment_type=payment_type, payment_details=payment_details
    "create_token", payment_type=payment_type, payment_details=payment_details
    )
    )


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while creating token")
    raise ConnectionError("Network error while creating token")


    # Check if payment type is supported
    # Check if payment type is supported
    if payment_type not in self.supported_payment_types:
    if payment_type not in self.supported_payment_types:
    raise ValueError(f"Payment type not supported: {payment_type}")
    raise ValueError(f"Payment type not supported: {payment_type}")


    # Process payment details based on payment type
    # Process payment details based on payment type
    token_details = {}
    token_details = {}


    if payment_type == "card":
    if payment_type == "card":
    # Validate card details
    # Validate card details
    if "number" not in payment_details:
    if "number" not in payment_details:
    raise ValueError("Card number is required")
    raise ValueError("Card number is required")


    if "exp_month" not in payment_details or "exp_year" not in payment_details:
    if "exp_month" not in payment_details or "exp_year" not in payment_details:
    raise ValueError("Card expiration date is required")
    raise ValueError("Card expiration date is required")


    if "cvc" not in payment_details:
    if "cvc" not in payment_details:
    raise ValueError("Card CVC is required")
    raise ValueError("Card CVC is required")


    # Validate card number
    # Validate card number
    if not self.validate_card_number(payment_details["number"]):
    if not self.validate_card_number(payment_details["number"]):
    raise ValueError("Invalid card number")
    raise ValueError("Invalid card number")


    # Get card type
    # Get card type
    card_type = self.get_card_type(payment_details["number"])
    card_type = self.get_card_type(payment_details["number"])


    # Mask card number
    # Mask card number
    self.mask_card_number(payment_details["number"])
    self.mask_card_number(payment_details["number"])


    # Create token details
    # Create token details
    token_details = {
    token_details = {
    "last4": payment_details["number"][-4:],
    "last4": payment_details["number"][-4:],
    "brand": card_type,
    "brand": card_type,
    "exp_month": payment_details["exp_month"],
    "exp_month": payment_details["exp_month"],
    "exp_year": payment_details["exp_year"],
    "exp_year": payment_details["exp_year"],
    "fingerprint": f"fingerprint_{uuid.uuid4().hex[:8]}",
    "fingerprint": f"fingerprint_{uuid.uuid4().hex[:8]}",
    }
    }
    elif payment_type == "bank_account":
    elif payment_type == "bank_account":
    # Similar processing for bank accounts
    # Similar processing for bank accounts
    token_details = {
    token_details = {
    "last4": payment_details["account_number"][-4:],
    "last4": payment_details["account_number"][-4:],
    "bank_name": payment_details.get("bank_name", ""),
    "bank_name": payment_details.get("bank_name", ""),
    "account_type": payment_details.get("account_type", "checking"),
    "account_type": payment_details.get("account_type", "checking"),
    "country": payment_details.get("country", "US"),
    "country": payment_details.get("country", "US"),
    "currency": payment_details.get("currency", "usd"),
    "currency": payment_details.get("currency", "usd"),
    "fingerprint": f"fingerprint_{uuid.uuid4().hex[:8]}",
    "fingerprint": f"fingerprint_{uuid.uuid4().hex[:8]}",
    }
    }


    # Generate token ID
    # Generate token ID
    token_id = self._generate_id("tok")
    token_id = self._generate_id("tok")


    # Create token
    # Create token
    token = {
    token = {
    "id": token_id,
    "id": token_id,
    "object": "token",
    "object": "token",
    "type": payment_type,
    "type": payment_type,
    "details": token_details,
    "details": token_details,
    "created": int(datetime.now().timestamp()),
    "created": int(datetime.now().timestamp()),
    "livemode": False,
    "livemode": False,
    "used": False,
    "used": False,
    }
    }


    return token
    return token




    class MockPayPalGateway(MockPaymentGateway):
    class MockPayPalGateway(MockPaymentGateway):
    """Mock implementation of PayPal payment gateway."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
    """Initialize the mock PayPal gateway."""
    super().__init__(config)

    # Set PayPal-specific properties
    self.gateway_name = "paypal"

    def create_billing_agreement(
    self,
    description: str,
    customer_id: str,
    start_date: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    """
    """
    Create a billing agreement.
    Create a billing agreement.


    Args:
    Args:
    description: Agreement description
    description: Agreement description
    customer_id: ID of the customer
    customer_id: ID of the customer
    start_date: Start date of the agreement
    start_date: Start date of the agreement
    metadata: Additional metadata
    metadata: Additional metadata


    Returns:
    Returns:
    Billing agreement object
    Billing agreement object
    """
    """
    self.record_call(
    self.record_call(
    "create_billing_agreement",
    "create_billing_agreement",
    description=description,
    description=description,
    customer_id=customer_id,
    customer_id=customer_id,
    start_date=start_date,
    start_date=start_date,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Check if a network error should be simulated
    # Check if a network error should be simulated
    if self._simulate_network_error():
    if self._simulate_network_error():
    raise ConnectionError("Network error while creating billing agreement")
    raise ConnectionError("Network error while creating billing agreement")


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    # Set start date if not provided
    # Set start date if not provided
    if start_date is None:
    if start_date is None:
    start_date = datetime.now()
    start_date = datetime.now()


    # Generate agreement ID
    # Generate agreement ID
    agreement_id = self._generate_id("ba")
    agreement_id = self._generate_id("ba")


    # Create agreement
    # Create agreement
    agreement = {
    agreement = {
    "id": agreement_id,
    "id": agreement_id,
    "customer_id": customer_id,
    "customer_id": customer_id,
    "description": description,
    "description": description,
    "status": "active",
    "status": "active",
    "start_date": start_date.isoformat(),
    "start_date": start_date.isoformat(),
    "metadata": metadata or {},
    "metadata": metadata or {},
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    }
    }


    return agreement
    return agreement




    # Create factory function for payment gateways
    # Create factory function for payment gateways
    def create_payment_gateway(
    def create_payment_gateway(
    gateway_type: str, config: Optional[Dict[str, Any]] = None
    gateway_type: str, config: Optional[Dict[str, Any]] = None
    ) -> Union[MockStripeGateway, MockPayPalGateway]:
    ) -> Union[MockStripeGateway, MockPayPalGateway]:
    """
    """
    Create a mock payment gateway of the specified type.
    Create a mock payment gateway of the specified type.


    Args:
    Args:
    gateway_type: Type of gateway to create ("stripe" or "paypal")
    gateway_type: Type of gateway to create ("stripe" or "paypal")
    config: Optional configuration for the gateway
    config: Optional configuration for the gateway


    Returns:
    Returns:
    A mock payment gateway instance
    A mock payment gateway instance
    """
    """
    gateways = {"stripe": MockStripeGateway, "paypal": MockPayPalGateway}
    gateways = {"stripe": MockStripeGateway, "paypal": MockPayPalGateway}


    gateway_class = gateways.get(gateway_type.lower())
    gateway_class = gateways.get(gateway_type.lower())
    if not gateway_class:
    if not gateway_class:
    raise ValueError(f"Unknown gateway type: {gateway_type}")
    raise ValueError(f"Unknown gateway type: {gateway_type}")


    return gateway_class(config)
    return gateway_class(config)