"""
"""
Mock payment processor for the pAIssive Income project.
Mock payment processor for the pAIssive Income project.


This module provides a mock implementation of the payment processor interface
This module provides a mock implementation of the payment processor interface
for testing and development purposes.
for testing and development purposes.
"""
"""




import copy
import copy
import random
import random
import uuid
import uuid
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .payment_processor import PaymentProcessor
from .payment_processor import PaymentProcessor




class MockPaymentProcessor:
    class MockPaymentProcessor:


    pass  # Added missing block
    pass  # Added missing block
    """
    """
    Mock implementation of the payment processor interface.
    Mock implementation of the payment processor interface.


    This class provides a simulated payment processor for testing and development.
    This class provides a simulated payment processor for testing and development.
    It stores all data in memory and simulates payment processing behavior.
    It stores all data in memory and simulates payment processing behavior.
    """
    """


    def __init__(self, config: Dict[str, Any]):
    def __init__(self, config: Dict[str, Any]):
    """
    """
    Initialize a mock payment processor.
    Initialize a mock payment processor.


    Args:
    Args:
    config: Configuration for the payment processor
    config: Configuration for the payment processor
    """
    """
    super().__init__(config)
    super().__init__(config)


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


    # Set default configuration
    # Set default configuration
    self.success_rate = config.get("success_rate", 0.95)
    self.success_rate = config.get("success_rate", 0.95)
    self.refund_success_rate = config.get("refund_success_rate", 0.98)
    self.refund_success_rate = config.get("refund_success_rate", 0.98)
    self.simulate_network_errors = config.get("simulate_network_errors", False)
    self.simulate_network_errors = config.get("simulate_network_errors", False)
    self.network_error_rate = config.get("network_error_rate", 0.05)
    self.network_error_rate = config.get("network_error_rate", 0.05)


    # Set supported payment types
    # Set supported payment types
    self.supported_payment_types = config.get(
    self.supported_payment_types = config.get(
    "supported_payment_types", ["card", "bank_account"]
    "supported_payment_types", ["card", "bank_account"]
    )
    )


    # Set supported currencies
    # Set supported currencies
    self.supported_currencies = config.get(
    self.supported_currencies = config.get(
    "supported_currencies", ["USD", "EUR", "GBP"]
    "supported_currencies", ["USD", "EUR", "GBP"]
    )
    )


    def _generate_id(self, prefix: str) -> str:
    def _generate_id(self, prefix: str) -> str:
    """
    """
    Generate a unique ID with a prefix.
    Generate a unique ID with a prefix.


    Args:
    Args:
    prefix: Prefix for the ID
    prefix: Prefix for the ID


    Returns:
    Returns:
    Unique ID
    Unique ID
    """
    """
    return f"{prefix}_{str(uuid.uuid4())}"
    return f"{prefix}_{str(uuid.uuid4())}"


    def _simulate_network_error(self) -> bool:
    def _simulate_network_error(self) -> bool:
    """
    """
    Simulate a network error.
    Simulate a network error.


    Returns:
    Returns:
    True if a network error should be simulated, False otherwise
    True if a network error should be simulated, False otherwise
    """
    """
    if self.simulate_network_errors and random.random() < self.network_error_rate:
    if self.simulate_network_errors and random.random() < self.network_error_rate:
    raise ConnectionError("Simulated network error")
    raise ConnectionError("Simulated network error")


    return False
    return False


    def _simulate_payment_success(self) -> bool:
    def _simulate_payment_success(self) -> bool:
    """
    """
    Simulate payment success or failure.
    Simulate payment success or failure.


    Returns:
    Returns:
    True if the payment should succeed, False otherwise
    True if the payment should succeed, False otherwise
    """
    """
    return random.random() < self.success_rate
    return random.random() < self.success_rate


    def _simulate_refund_success(self) -> bool:
    def _simulate_refund_success(self) -> bool:
    """
    """
    Simulate refund success or failure.
    Simulate refund success or failure.


    Returns:
    Returns:
    True if the refund should succeed, False otherwise
    True if the refund should succeed, False otherwise
    """
    """
    return random.random() < self.refund_success_rate
    return random.random() < self.refund_success_rate


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
    Create a customer.
    Create a customer.


    Args:
    Args:
    email: Email of the customer
    email: Email of the customer
    name: Name of the customer
    name: Name of the customer
    metadata: Additional metadata for the customer
    metadata: Additional metadata for the customer


    Returns:
    Returns:
    Dictionary with customer information
    Dictionary with customer information
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


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
    Get information about a customer.
    Get information about a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer


    Returns:
    Returns:
    Dictionary with customer information
    Dictionary with customer information
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


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
    Update a customer.
    Update a customer.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    email: New email of the customer
    email: New email of the customer
    name: New name of the customer
    name: New name of the customer
    metadata: New metadata for the customer
    metadata: New metadata for the customer


    Returns:
    Returns:
    Dictionary with updated customer information
    Dictionary with updated customer information
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


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


    # Update customer
    # Update customer
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
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    return False
    return False


    # Delete customer
    # Delete customer
    del self.customers[customer_id]
    del self.customers[customer_id]


    # Delete associated payment methods
    # Delete associated payment methods
    payment_method_ids = [
    payment_method_ids = [
    pm_id
    pm_id
    for pm_id, pm in self.payment_methods.items()
    for pm_id, pm in self.payment_methods.items()
    if pm["customer_id"] == customer_id
    if pm["customer_id"] == customer_id
    ]
    ]


    for pm_id in payment_method_ids:
    for pm_id in payment_method_ids:
    del self.payment_methods[pm_id]
    del self.payment_methods[pm_id]


    # Delete associated subscriptions
    # Delete associated subscriptions
    subscription_ids = [
    subscription_ids = [
    sub_id
    sub_id
    for sub_id, sub in self.subscriptions.items()
    for sub_id, sub in self.subscriptions.items()
    if sub["customer_id"] == customer_id
    if sub["customer_id"] == customer_id
    ]
    ]


    for sub_id in subscription_ids:
    for sub_id in subscription_ids:
    del self.subscriptions[sub_id]
    del self.subscriptions[sub_id]


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
    Create a payment method.
    Create a payment method.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    payment_type: Type of payment method (e.g., card, bank_account)
    payment_type: Type of payment method (e.g., card, bank_account)
    payment_details: Details of the payment method
    payment_details: Details of the payment method
    metadata: Additional metadata for the payment method
    metadata: Additional metadata for the payment method


    Returns:
    Returns:
    Dictionary with payment method information
    Dictionary with payment method information
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


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
    raise ValueError(f"Unsupported payment type: {payment_type}")
    raise ValueError(f"Unsupported payment type: {payment_type}")


    # Validate payment details
    # Validate payment details
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
    Get information about a payment method.
    Get information about a payment method.


    Args:
    Args:
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method


    Returns:
    Returns:
    Dictionary with payment method information
    Dictionary with payment method information
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


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
    payment_type: Type of payment methods to list
    payment_type: Type of payment methods to list


    Returns:
    Returns:
    List of payment methods
    List of payment methods
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


    # Filter payment methods
    # Filter payment methods
    payment_methods = [
    payment_methods = [
    pm
    pm
    for pm in self.payment_methods.values()
    for pm in self.payment_methods.values()
    if pm["customer_id"] == customer_id
    if pm["customer_id"] == customer_id
    and (payment_type is None or pm["type"] == payment_type)
    and (payment_type is None or pm["type"] == payment_type)
    ]
    ]


    return copy.deepcopy(payment_methods)
    return copy.deepcopy(payment_methods)


    def update_payment_method(
    def update_payment_method(
    self,
    self,
    payment_method_id: str,
    payment_method_id: str,
    payment_details: Dict[str, Any],
    payment_details: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Update a payment method.
    Update a payment method.


    Args:
    Args:
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method
    payment_details: New details of the payment method
    payment_details: New details of the payment method
    metadata: New metadata for the payment method
    metadata: New metadata for the payment method


    Returns:
    Returns:
    Dictionary with updated payment method information
    Dictionary with updated payment method information
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


    # Check if payment method exists
    # Check if payment method exists
    if payment_method_id not in self.payment_methods:
    if payment_method_id not in self.payment_methods:
    raise ValueError(f"Payment method not found: {payment_method_id}")
    raise ValueError(f"Payment method not found: {payment_method_id}")


    # Get payment method
    # Get payment method
    payment_method = self.payment_methods[payment_method_id]
    payment_method = self.payment_methods[payment_method_id]


    # Update payment details
    # Update payment details
    if payment_details:
    if payment_details:
    payment_type = payment_method["type"]
    payment_type = payment_method["type"]


    if payment_type == "card":
    if payment_type == "card":
    # Update card details
    # Update card details
    if "exp_month" in payment_details:
    if "exp_month" in payment_details:
    payment_method["details"]["exp_month"] = payment_details[
    payment_method["details"]["exp_month"] = payment_details[
    "exp_month"
    "exp_month"
    ]
    ]


    if "exp_year" in payment_details:
    if "exp_year" in payment_details:
    payment_method["details"]["exp_year"] = payment_details["exp_year"]
    payment_method["details"]["exp_year"] = payment_details["exp_year"]
    elif payment_type == "bank_account":
    elif payment_type == "bank_account":
    # Update bank account details
    # Update bank account details
    if "bank_name" in payment_details:
    if "bank_name" in payment_details:
    payment_method["details"]["bank_name"] = payment_details[
    payment_method["details"]["bank_name"] = payment_details[
    "bank_name"
    "bank_name"
    ]
    ]


    if "account_type" in payment_details:
    if "account_type" in payment_details:
    payment_method["details"]["account_type"] = payment_details[
    payment_method["details"]["account_type"] = payment_details[
    "account_type"
    "account_type"
    ]
    ]
    else:
    else:
    # For other payment types, just update the details
    # For other payment types, just update the details
    payment_method["details"].update(payment_details)
    payment_method["details"].update(payment_details)


    # Update metadata
    # Update metadata
    if metadata is not None:
    if metadata is not None:
    payment_method["metadata"] = metadata
    payment_method["metadata"] = metadata


    payment_method["updated_at"] = datetime.now().isoformat()
    payment_method["updated_at"] = datetime.now().isoformat()


    return copy.deepcopy(payment_method)
    return copy.deepcopy(payment_method)


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
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


    # Check if payment method exists
    # Check if payment method exists
    if payment_method_id not in self.payment_methods:
    if payment_method_id not in self.payment_methods:
    return False
    return False


    # Delete payment method
    # Delete payment method
    del self.payment_methods[payment_method_id]
    del self.payment_methods[payment_method_id]


    return True
    return True


    def process_payment(
    def process_payment(
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
    amount: Amount to charge
    amount: Amount to charge
    currency: Currency code (e.g., USD)
    currency: Currency code (e.g., USD)
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method
    description: Description of the payment
    description: Description of the payment
    metadata: Additional metadata for the payment
    metadata: Additional metadata for the payment


    Returns:
    Returns:
    Dictionary with payment result
    Dictionary with payment result
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


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
    raise ValueError(f"Unsupported currency: {currency}")
    raise ValueError(f"Unsupported currency: {currency}")


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
    success = self._simulate_payment_success()
    success = self._simulate_payment_success()


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
    "status": "succeeded" if success else "failed",
    "status": "succeeded" if success else "failed",
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
    amount: Amount to refund (if None, refund the full amount)
    amount: Amount to refund (if None, refund the full amount)
    reason: Reason for the refund
    reason: Reason for the refund


    Returns:
    Returns:
    Dictionary with refund result
    Dictionary with refund result
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


    # Check if payment exists
    # Check if payment exists
    if payment_id not in self.payments:
    if payment_id not in self.payments:
    raise ValueError(f"Payment not found: {payment_id}")
    raise ValueError(f"Payment not found: {payment_id}")


    # Get payment
    # Get payment
    payment = self.payments[payment_id]
    payment = self.payments[payment_id]


    # Check if payment was successful
    # Check if payment was successful
    if payment["status"] != "succeeded":
    if payment["status"] != "succeeded":
    raise ValueError(f"Cannot refund payment with status: {payment['status']}")
    raise ValueError(f"Cannot refund payment with status: {payment['status']}")


    # Check if payment has already been refunded
    # Check if payment has already been refunded
    if payment.get("refunded"):
    if payment.get("refunded"):
    raise ValueError("Payment has already been refunded")
    raise ValueError("Payment has already been refunded")


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
    success = self._simulate_refund_success()
    success = self._simulate_refund_success()


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
    "status": "succeeded" if success else "failed",
    "status": "succeeded" if success else "failed",
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
    "message": "Refund could not be processed.",
    "message": "Refund could not be processed.",
    }
    }
    ),
    ),
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    }
    }


    # Update payment
    # Update payment
    if success:
    if success:
    payment["refunded"] = True
    payment["refunded"] = True
    payment["refund_id"] = refund_id
    payment["refund_id"] = refund_id
    payment["refund_amount"] = refund_amount
    payment["refund_amount"] = refund_amount
    payment["updated_at"] = datetime.now().isoformat()
    payment["updated_at"] = datetime.now().isoformat()


    # If refund failed, raise an exception
    # If refund failed, raise an exception
    if not success:
    if not success:
    raise ValueError("Refund failed: Refund could not be processed.")
    raise ValueError("Refund failed: Refund could not be processed.")


    return refund
    return refund


    def get_payment(self, payment_id: str) -> Dict[str, Any]:
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
    """
    """
    Get information about a payment.
    Get information about a payment.


    Args:
    Args:
    payment_id: ID of the payment
    payment_id: ID of the payment


    Returns:
    Returns:
    Dictionary with payment information
    Dictionary with payment information
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


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
    start_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    limit: int = 100,
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    List payments.
    List payments.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    start_date: Start date for payments
    start_date: Start date for payments
    end_date: End date for payments
    end_date: End date for payments
    limit: Maximum number of payments to return
    limit: Maximum number of payments to return


    Returns:
    Returns:
    List of payments
    List of payments
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


    # Filter payments
    # Filter payments
    filtered_payments = []
    filtered_payments = []


    for payment in self.payments.values():
    for payment in self.payments.values():
    # Filter by customer ID
    # Filter by customer ID
    if customer_id and payment["customer_id"] != customer_id:
    if customer_id and payment["customer_id"] != customer_id:
    continue
    continue


    # Filter by date range
    # Filter by date range
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


    # Sort by created_at (newest first)
    # Sort by created_at (newest first)
    filtered_payments.sort(key=lambda p: p["created_at"], reverse=True)
    filtered_payments.sort(key=lambda p: p["created_at"], reverse=True)


    # Apply limit
    # Apply limit
    filtered_payments = filtered_payments[:limit]
    filtered_payments = filtered_payments[:limit]


    return copy.deepcopy(filtered_payments)
    return copy.deepcopy(filtered_payments)


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
    payment_method_id: ID of the payment method
    payment_method_id: ID of the payment method
    metadata: Additional metadata for the subscription
    metadata: Additional metadata for the subscription


    Returns:
    Returns:
    Dictionary with subscription information
    Dictionary with subscription information
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


    # Check if customer exists
    # Check if customer exists
    if customer_id not in self.customers:
    if customer_id not in self.customers:
    raise ValueError(f"Customer not found: {customer_id}")
    raise ValueError(f"Customer not found: {customer_id}")


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


    # Generate subscription ID
    # Generate subscription ID
    subscription_id = self._generate_id("sub")
    subscription_id = self._generate_id("sub")


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
    "status": "active",
    "status": "active",
    "current_period_start": datetime.now().isoformat(),
    "current_period_start": datetime.now().isoformat(),
    "current_period_end": (datetime.now() + timedelta(days=30)).isoformat(),
    "current_period_end": (datetime.now() + timedelta(days=30)).isoformat(),
    "cancel_at_period_end": False,
    "cancel_at_period_end": False,
    "canceled_at": None,
    "canceled_at": None,
    "ended_at": None,
    "ended_at": None,
    "metadata": metadata or {},
    "metadata": metadata or {},
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
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
    Get information about a subscription.
    Get information about a subscription.


    Args:
    Args:
    subscription_id: ID of the subscription
    subscription_id: ID of the subscription


    Returns:
    Returns:
    Dictionary with subscription information
    Dictionary with subscription information
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


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
    plan_id: New ID of the plan
    plan_id: New ID of the plan
    payment_method_id: New ID of the payment method
    payment_method_id: New ID of the payment method
    metadata: New metadata for the subscription
    metadata: New metadata for the subscription


    Returns:
    Returns:
    Dictionary with updated subscription information
    Dictionary with updated subscription information
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


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
    if subscription["status"] != "active":
    if subscription["status"] != "active":
    raise ValueError(
    raise ValueError(
    f"Cannot update subscription with status: {subscription['status']}"
    f"Cannot update subscription with status: {subscription['status']}"
    )
    )


    # Update plan ID
    # Update plan ID
    if plan_id is not None:
    if plan_id is not None:
    subscription["plan_id"] = plan_id
    subscription["plan_id"] = plan_id


    # Update payment method ID
    # Update payment method ID
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


    # Update metadata
    # Update metadata
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
    cancel_at_period_end: Whether to cancel at the end of the billing period
    cancel_at_period_end: Whether to cancel at the end of the billing period


    Returns:
    Returns:
    Dictionary with updated subscription information
    Dictionary with updated subscription information
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


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
    if subscription["status"] != "active":
    if subscription["status"] != "active":
    raise ValueError(
    raise ValueError(
    f"Cannot cancel subscription with status: {subscription['status']}"
    f"Cannot cancel subscription with status: {subscription['status']}"
    )
    )


    # Update subscription
    # Update subscription
    subscription["cancel_at_period_end"] = cancel_at_period_end
    subscription["cancel_at_period_end"] = cancel_at_period_end
    subscription["canceled_at"] = datetime.now().isoformat()
    subscription["canceled_at"] = datetime.now().isoformat()


    if not cancel_at_period_end:
    if not cancel_at_period_end:
    subscription["status"] = "canceled"
    subscription["status"] = "canceled"
    subscription["ended_at"] = datetime.now().isoformat()
    subscription["ended_at"] = datetime.now().isoformat()


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
    List subscriptions.
    List subscriptions.


    Args:
    Args:
    customer_id: ID of the customer
    customer_id: ID of the customer
    plan_id: ID of the plan
    plan_id: ID of the plan
    status: Status of the subscriptions
    status: Status of the subscriptions
    limit: Maximum number of subscriptions to return
    limit: Maximum number of subscriptions to return


    Returns:
    Returns:
    List of subscriptions
    List of subscriptions
    """
    """
    # Simulate network error
    # Simulate network error
    self._simulate_network_error()
    self._simulate_network_error()


    # Filter subscriptions
    # Filter subscriptions
    filtered_subscriptions = []
    filtered_subscriptions = []


    for subscription in self.subscriptions.values():
    for subscription in self.subscriptions.values():
    # Filter by customer ID
    # Filter by customer ID
    if customer_id and subscription["customer_id"] != customer_id:
    if customer_id and subscription["customer_id"] != customer_id:
    continue
    continue


    # Filter by plan ID
    # Filter by plan ID
    if plan_id and subscription["plan_id"] != plan_id:
    if plan_id and subscription["plan_id"] != plan_id:
    continue
    continue


    # Filter by status
    # Filter by status
    if status and subscription["status"] != status:
    if status and subscription["status"] != status:
    continue
    continue


    filtered_subscriptions.append(subscription)
    filtered_subscriptions.append(subscription)


    # Sort by created_at (newest first)
    # Sort by created_at (newest first)
    filtered_subscriptions.sort(key=lambda s: s["created_at"], reverse=True)
    filtered_subscriptions.sort(key=lambda s: s["created_at"], reverse=True)


    # Apply limit
    # Apply limit
    filtered_subscriptions = filtered_subscriptions[:limit]
    filtered_subscriptions = filtered_subscriptions[:limit]


    return copy.deepcopy(filtered_subscriptions)
    return copy.deepcopy(filtered_subscriptions)