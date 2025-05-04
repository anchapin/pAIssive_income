"""
"""
Payment processor interface for the pAIssive Income project.
Payment processor interface for the pAIssive Income project.


This module provides an abstract base class for payment processors and
This module provides an abstract base class for payment processors and
common utility methods for payment processing.
common utility methods for payment processing.
"""
"""




import uuid
import uuid
from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional




def get_payment_gateway():
    def get_payment_gateway():
    from tests.mocks.mock_payment_apis import create_payment_gateway
    from tests.mocks.mock_payment_apis import create_payment_gateway


    return create_payment_gateway
    return create_payment_gateway


    (
    (
    gateway_type: str = "stripe", config: Optional[Dict[str, Any]] = None
    gateway_type: str = "stripe", config: Optional[Dict[str, Any]] = None
    ):
    ):
    """
    """
    Get a payment gateway of the specified type.
    Get a payment gateway of the specified type.


    Args:
    Args:
    gateway_type: Type of gateway to get (e.g., "stripe", "paypal")
    gateway_type: Type of gateway to get (e.g., "stripe", "paypal")
    config: Optional configuration for the gateway
    config: Optional configuration for the gateway


    Returns:
    Returns:
    A payment gateway instance
    A payment gateway instance
    """
    """
    (gateway_type, config)
    (gateway_type, config)




    class PaymentProcessor(ABC):
    class PaymentProcessor(ABC):
    """
    """
    Abstract base class for payment processors.
    Abstract base class for payment processors.


    This class defines the interface that all payment processors must implement.
    This class defines the interface that all payment processors must implement.
    """
    """


    def __init__(self, config: Dict[str, Any]):
    def __init__(self, config: Dict[str, Any]):
    """
    """
    Initialize a payment processor.
    Initialize a payment processor.


    Args:
    Args:
    config: Configuration for the payment processor
    config: Configuration for the payment processor
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.name = config.get("name", "Payment Processor")
    self.name = config.get("name", "Payment Processor")
    self.config = config
    self.config = config
    self.created_at = datetime.now()
    self.created_at = datetime.now()


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    @abstractmethod
    @abstractmethod
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
    pass
    pass


    def format_amount(self, amount: float, currency: str) -> str:
    def format_amount(self, amount: float, currency: str) -> str:
    """
    """
    Format an amount with currency symbol.
    Format an amount with currency symbol.


    Args:
    Args:
    amount: Amount to format
    amount: Amount to format
    currency: Currency code
    currency: Currency code


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


    symbol = currency_symbols.get(currency, currency)
    symbol = currency_symbols.get(currency, currency)


    if currency == "JPY":
    if currency == "JPY":
    # JPY doesn't use decimal places
    # JPY doesn't use decimal places
    return f"{symbol}{int(amount):,}"
    return f"{symbol}{int(amount):,}"
    else:
    else:
    return f"{symbol}{amount:,.2f}"
    return f"{symbol}{amount:,.2f}"


    def validate_card_number(self, card_number: str) -> bool:
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
    # Remove spaces and dashes
    # Remove spaces and dashes
    card_number = card_number.replace(" ", "").replace("-", "")
    card_number = card_number.replace(" ", "").replace("-", "")


    # Check if the card number contains only digits
    # Check if the card number contains only digits
    if not card_number.isdigit():
    if not card_number.isdigit():
    return False
    return False


    # Check length (most card numbers are 13-19 digits)
    # Check length (most card numbers are 13-19 digits)
    if not (13 <= len(card_number) <= 19):
    if not (13 <= len(card_number) <= 19):
    return False
    return False


    # Luhn algorithm
    # Luhn algorithm
    digits = [int(d) for d in card_number]
    digits = [int(d) for d in card_number]
    checksum = 0
    checksum = 0


    for i, digit in enumerate(reversed(digits)):
    for i, digit in enumerate(reversed(digits)):
    if i % 2 == 1:
    if i % 2 == 1:
    digit *= 2
    digit *= 2
    if digit > 9:
    if digit > 9:
    digit -= 9
    digit -= 9


    checksum += digit
    checksum += digit


    return checksum % 10 == 0
    return checksum % 10 == 0


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
    Masked card number
    Masked card number
    """
    """
    # Remove spaces and dashes
    # Remove spaces and dashes
    card_number = card_number.replace(" ", "").replace("-", "")
    card_number = card_number.replace(" ", "").replace("-", "")


    # Keep first 6 and last 4 digits, mask the rest
    # Keep first 6 and last 4 digits, mask the rest
    if len(card_number) <= 10:
    if len(card_number) <= 10:
    # For short numbers, just mask all but the last 4
    # For short numbers, just mask all but the last 4
    return "****" + card_number[-4:]
    return "****" + card_number[-4:]
    else:
    else:
    return card_number[:6] + "*" * (len(card_number) - 10) + card_number[-4:]
    return card_number[:6] + "*" * (len(card_number) - 10) + card_number[-4:]


    def get_card_type(self, card_number: str) -> str:
    def get_card_type(self, card_number: str) -> str:
    """
    """
    Get the type of a credit card based on its number.
    Get the type of a credit card based on its number.


    Args:
    Args:
    card_number: Credit card number
    card_number: Credit card number


    Returns:
    Returns:
    Type of the credit card (e.g., Visa, Mastercard)
    Type of the credit card (e.g., Visa, Mastercard)
    """
    """
    # Remove spaces and dashes
    # Remove spaces and dashes
    card_number = card_number.replace(" ", "").replace("-", "")
    card_number = card_number.replace(" ", "").replace("-", "")


    # Check for common card types based on prefix
    # Check for common card types based on prefix
    if card_number.startswith("4"):
    if card_number.startswith("4"):
    return "Visa"
    return "Visa"
    elif card_number.startswith(
    elif card_number.startswith(
    ("51", "52", "53", "54", "55")
    ("51", "52", "53", "54", "55")
    ) or card_number.startswith(
    ) or card_number.startswith(
    (
    (
    "2221",
    "2221",
    "2222",
    "2222",
    "2223",
    "2223",
    "2224",
    "2224",
    "2225",
    "2225",
    "2226",
    "2226",
    "2227",
    "2227",
    "2228",
    "2228",
    "2229",
    "2229",
    "223",
    "223",
    "224",
    "224",
    "225",
    "225",
    "226",
    "226",
    "227",
    "227",
    "228",
    "228",
    "229",
    "229",
    "23",
    "23",
    "24",
    "24",
    "25",
    "25",
    "26",
    "26",
    "270",
    "270",
    "271",
    "271",
    "2720",
    "2720",
    )
    )
    ):
    ):
    return "Mastercard"
    return "Mastercard"
    elif card_number.startswith(("34", "37")):
    elif card_number.startswith(("34", "37")):
    return "American Express"
    return "American Express"
    elif card_number.startswith(
    elif card_number.startswith(
    ("300", "301", "302", "303", "304", "305", "36", "38")
    ("300", "301", "302", "303", "304", "305", "36", "38")
    ):
    ):
    return "Diners Club"
    return "Diners Club"
    elif card_number.startswith(
    elif card_number.startswith(
    ("6011", "644", "645", "646", "647", "648", "649", "65")
    ("6011", "644", "645", "646", "647", "648", "649", "65")
    ):
    ):
    return "Discover"
    return "Discover"
    elif card_number.startswith(("35")):
    elif card_number.startswith(("35")):
    return "JCB"
    return "JCB"
    else:
    else:
    return "Unknown"
    return "Unknown"


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the payment processor to a dictionary.
    Convert the payment processor to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the payment processor
    Dictionary representation of the payment processor
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "name": self.name,
    "name": self.name,
    "type": self.__class__.__name__,
    "type": self.__class__.__name__,
    "created_at": self.created_at.isoformat(),
    "created_at": self.created_at.isoformat(),
    }
    }


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the payment processor."""
    return f"{self.name} ({self.__class__.__name__})"

    def __repr__(self) -> str:
    """Detailed string representation of the payment processor."""
    return f"{self.__class__.__name__}(id={self.id}, name={self.name})"