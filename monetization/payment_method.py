"""
"""
Payment method management for the pAIssive Income project.
Payment method management for the pAIssive Income project.


This module provides classes for managing payment methods, including
This module provides classes for managing payment methods, including
creation, validation, and storage.
creation, validation, and storage.
"""
"""




import json
import json
import re
import re
import uuid
import uuid
from datetime import datetime
from datetime import datetime
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional




class PaymentMethod:
    class PaymentMethod:


    pass  # Added missing block
    pass  # Added missing block
    """
    """
    Class for managing payment methods.
    Class for managing payment methods.


    This class provides methods for creating, validating, and managing
    This class provides methods for creating, validating, and managing
    payment methods such as credit cards and bank accounts.
    payment methods such as credit cards and bank accounts.
    """
    """


    # Payment method types
    # Payment method types
    TYPE_CARD = "card"
    TYPE_CARD = "card"
    TYPE_BANK_ACCOUNT = "bank_account"
    TYPE_BANK_ACCOUNT = "bank_account"
    TYPE_PAYPAL = "paypal"
    TYPE_PAYPAL = "paypal"
    TYPE_CRYPTO = "crypto"
    TYPE_CRYPTO = "crypto"


    # Card brands
    # Card brands
    CARD_VISA = "visa"
    CARD_VISA = "visa"
    CARD_MASTERCARD = "mastercard"
    CARD_MASTERCARD = "mastercard"
    CARD_AMEX = "amex"
    CARD_AMEX = "amex"
    CARD_DISCOVER = "discover"
    CARD_DISCOVER = "discover"
    CARD_DINERS = "diners"
    CARD_DINERS = "diners"
    CARD_JCB = "jcb"
    CARD_JCB = "jcb"
    CARD_UNIONPAY = "unionpay"
    CARD_UNIONPAY = "unionpay"


    def __init__(
    def __init__(
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
    ):
    ):
    """
    """
    Initialize a payment method.
    Initialize a payment method.


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
    """
    """
    self.id = str(uuid.uuid4())
    self.id = str(uuid.uuid4())
    self.customer_id = customer_id
    self.customer_id = customer_id
    self.payment_type = payment_type
    self.payment_type = payment_type
    self.metadata = metadata or {}
    self.metadata = metadata or {}
    self.created_at = datetime.now()
    self.created_at = datetime.now()
    self.updated_at = self.created_at
    self.updated_at = self.created_at
    self.is_default = False
    self.is_default = False


    # Validate and process payment details
    # Validate and process payment details
    if payment_type == self.TYPE_CARD:
    if payment_type == self.TYPE_CARD:
    self.details = self._process_card_details(payment_details)
    self.details = self._process_card_details(payment_details)
    elif payment_type == self.TYPE_BANK_ACCOUNT:
    elif payment_type == self.TYPE_BANK_ACCOUNT:
    self.details = self._process_bank_account_details(payment_details)
    self.details = self._process_bank_account_details(payment_details)
    elif payment_type == self.TYPE_PAYPAL:
    elif payment_type == self.TYPE_PAYPAL:
    self.details = self._process_paypal_details(payment_details)
    self.details = self._process_paypal_details(payment_details)
    elif payment_type == self.TYPE_CRYPTO:
    elif payment_type == self.TYPE_CRYPTO:
    self.details = self._process_crypto_details(payment_details)
    self.details = self._process_crypto_details(payment_details)
    else:
    else:
    raise ValueError(f"Unsupported payment type: {payment_type}")
    raise ValueError(f"Unsupported payment type: {payment_type}")


    def _process_card_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
    def _process_card_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Process and validate credit card details.
    Process and validate credit card details.


    Args:
    Args:
    details: Credit card details
    details: Credit card details


    Returns:
    Returns:
    Processed card details
    Processed card details
    """
    """
    # Validate required fields
    # Validate required fields
    if "number" not in details:
    if "number" not in details:
    raise ValueError("Card number is required")
    raise ValueError("Card number is required")


    if "exp_month" not in details or "exp_year" not in details:
    if "exp_month" not in details or "exp_year" not in details:
    raise ValueError("Card expiration date is required")
    raise ValueError("Card expiration date is required")


    if "cvc" not in details:
    if "cvc" not in details:
    raise ValueError("Card CVC is required")
    raise ValueError("Card CVC is required")


    # Validate card number
    # Validate card number
    card_number = details["number"].replace(" ", "").replace("-", "")
    card_number = details["number"].replace(" ", "").replace("-", "")
    if not self.validate_card_number(card_number):
    if not self.validate_card_number(card_number):
    raise ValueError("Invalid card number")
    raise ValueError("Invalid card number")


    # Validate expiration date
    # Validate expiration date
    exp_month = int(details["exp_month"])
    exp_month = int(details["exp_month"])
    exp_year = int(details["exp_year"])
    exp_year = int(details["exp_year"])


    if not (1 <= exp_month <= 12):
    if not (1 <= exp_month <= 12):
    raise ValueError("Invalid expiration month")
    raise ValueError("Invalid expiration month")


    current_year = datetime.now().year
    current_year = datetime.now().year
    if exp_year < current_year:
    if exp_year < current_year:
    raise ValueError("Card has expired")
    raise ValueError("Card has expired")


    # Get card type
    # Get card type
    card_brand = self.get_card_type(card_number)
    card_brand = self.get_card_type(card_number)


    # Mask card number
    # Mask card number
    masked_number = self.mask_card_number(card_number)
    masked_number = self.mask_card_number(card_number)


    # Create processed details
    # Create processed details
    processed_details = {
    processed_details = {
    "last4": card_number[-4:],
    "last4": card_number[-4:],
    "brand": card_brand,
    "brand": card_brand,
    "exp_month": exp_month,
    "exp_month": exp_month,
    "exp_year": exp_year,
    "exp_year": exp_year,
    "masked_number": masked_number,
    "masked_number": masked_number,
    }
    }


    # Add optional fields
    # Add optional fields
    if "name" in details:
    if "name" in details:
    processed_details["name"] = details["name"]
    processed_details["name"] = details["name"]


    if "address" in details:
    if "address" in details:
    processed_details["address"] = details["address"]
    processed_details["address"] = details["address"]


    return processed_details
    return processed_details


    def _process_bank_account_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
    def _process_bank_account_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Process and validate bank account details.
    Process and validate bank account details.


    Args:
    Args:
    details: Bank account details
    details: Bank account details


    Returns:
    Returns:
    Processed bank account details
    Processed bank account details
    """
    """
    # Validate required fields
    # Validate required fields
    if "account_number" not in details:
    if "account_number" not in details:
    raise ValueError("Account number is required")
    raise ValueError("Account number is required")


    if "routing_number" not in details:
    if "routing_number" not in details:
    raise ValueError("Routing number is required")
    raise ValueError("Routing number is required")


    # Validate account number
    # Validate account number
    account_number = details["account_number"].replace(" ", "").replace("-", "")
    account_number = details["account_number"].replace(" ", "").replace("-", "")
    if not account_number.isdigit():
    if not account_number.isdigit():
    raise ValueError("Account number must contain only digits")
    raise ValueError("Account number must contain only digits")


    # Validate routing number
    # Validate routing number
    routing_number = details["routing_number"].replace(" ", "").replace("-", "")
    routing_number = details["routing_number"].replace(" ", "").replace("-", "")
    if not routing_number.isdigit() or len(routing_number) != 9:
    if not routing_number.isdigit() or len(routing_number) != 9:
    raise ValueError("Invalid routing number")
    raise ValueError("Invalid routing number")


    # Mask account number
    # Mask account number
    masked_account = "****" + account_number[-4:]
    masked_account = "****" + account_number[-4:]


    # Create processed details
    # Create processed details
    processed_details = {
    processed_details = {
    "last4": account_number[-4:],
    "last4": account_number[-4:],
    "routing_number": routing_number,
    "routing_number": routing_number,
    "account_type": details.get("account_type", "checking"),
    "account_type": details.get("account_type", "checking"),
    "bank_name": details.get("bank_name", ""),
    "bank_name": details.get("bank_name", ""),
    "masked_account": masked_account,
    "masked_account": masked_account,
    }
    }


    # Add optional fields
    # Add optional fields
    if "name" in details:
    if "name" in details:
    processed_details["name"] = details["name"]
    processed_details["name"] = details["name"]


    if "country" in details:
    if "country" in details:
    processed_details["country"] = details["country"]
    processed_details["country"] = details["country"]


    return processed_details
    return processed_details


    def _process_paypal_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
    def _process_paypal_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Process and validate PayPal details.
    Process and validate PayPal details.


    Args:
    Args:
    details: PayPal details
    details: PayPal details


    Returns:
    Returns:
    Processed PayPal details
    Processed PayPal details
    """
    """
    # Validate required fields
    # Validate required fields
    if "email" not in details:
    if "email" not in details:
    raise ValueError("PayPal email is required")
    raise ValueError("PayPal email is required")


    # Validate email
    # Validate email
    email = details["email"]
    email = details["email"]
    if not self.validate_email(email):
    if not self.validate_email(email):
    raise ValueError("Invalid email address")
    raise ValueError("Invalid email address")


    # Create processed details
    # Create processed details
    processed_details = {
    processed_details = {
    "email": email,
    "email": email,
    "account_id": details.get("account_id", ""),
    "account_id": details.get("account_id", ""),
    }
    }


    return processed_details
    return processed_details


    def _process_crypto_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
    def _process_crypto_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Process and validate cryptocurrency details.
    Process and validate cryptocurrency details.


    Args:
    Args:
    details: Cryptocurrency details
    details: Cryptocurrency details


    Returns:
    Returns:
    Processed cryptocurrency details
    Processed cryptocurrency details
    """
    """
    # Validate required fields
    # Validate required fields
    if "currency" not in details:
    if "currency" not in details:
    raise ValueError("Cryptocurrency type is required")
    raise ValueError("Cryptocurrency type is required")


    if "address" not in details:
    if "address" not in details:
    raise ValueError("Cryptocurrency address is required")
    raise ValueError("Cryptocurrency address is required")


    # Create processed details
    # Create processed details
    processed_details = {
    processed_details = {
    "currency": details["currency"],
    "currency": details["currency"],
    "address": details["address"],
    "address": details["address"],
    "network": details.get("network", ""),
    "network": details.get("network", ""),
    }
    }


    return processed_details
    return processed_details


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
    return self.CARD_VISA
    return self.CARD_VISA
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
    return self.CARD_MASTERCARD
    return self.CARD_MASTERCARD
    elif card_number.startswith(("34", "37")):
    elif card_number.startswith(("34", "37")):
    return self.CARD_AMEX
    return self.CARD_AMEX
    elif card_number.startswith(
    elif card_number.startswith(
    ("300", "301", "302", "303", "304", "305", "36", "38")
    ("300", "301", "302", "303", "304", "305", "36", "38")
    ):
    ):
    return self.CARD_DINERS
    return self.CARD_DINERS
    elif card_number.startswith(
    elif card_number.startswith(
    ("6011", "644", "645", "646", "647", "648", "649", "65")
    ("6011", "644", "645", "646", "647", "648", "649", "65")
    ):
    ):
    return self.CARD_DISCOVER
    return self.CARD_DISCOVER
    elif card_number.startswith(("35")):
    elif card_number.startswith(("35")):
    return self.CARD_JCB
    return self.CARD_JCB
    elif card_number.startswith(("62")):
    elif card_number.startswith(("62")):
    return self.CARD_UNIONPAY
    return self.CARD_UNIONPAY
    else:
    else:
    return "unknown"
    return "unknown"


    def validate_email(self, email: str) -> bool:
    def validate_email(self, email: str) -> bool:
    """
    """
    Validate an email address.
    Validate an email address.


    Args:
    Args:
    email: Email address to validate
    email: Email address to validate


    Returns:
    Returns:
    True if the email is valid, False otherwise
    True if the email is valid, False otherwise
    """
    """
    # Simple email validation regex
    # Simple email validation regex
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))
    return bool(re.match(pattern, email))


    def is_expired(self) -> bool:
    def is_expired(self) -> bool:
    """
    """
    Check if the payment method is expired.
    Check if the payment method is expired.


    Returns:
    Returns:
    True if the payment method is expired, False otherwise
    True if the payment method is expired, False otherwise
    """
    """
    if self.payment_type != self.TYPE_CARD:
    if self.payment_type != self.TYPE_CARD:
    return False
    return False


    now = datetime.now()
    now = datetime.now()
    exp_month = self.details.get("exp_month", 0)
    exp_month = self.details.get("exp_month", 0)
    exp_year = self.details.get("exp_year", 0)
    exp_year = self.details.get("exp_year", 0)


    # Card expires at the end of the expiration month
    # Card expires at the end of the expiration month
    exp_date = datetime(exp_year, exp_month, 1)
    exp_date = datetime(exp_year, exp_month, 1)
    exp_date = datetime(exp_date.year, exp_date.month + 1, 1)
    exp_date = datetime(exp_date.year, exp_date.month + 1, 1)


    return now >= exp_date
    return now >= exp_date


    def will_expire_soon(self, days: int = 30) -> bool:
    def will_expire_soon(self, days: int = 30) -> bool:
    """
    """
    Check if the payment method will expire soon.
    Check if the payment method will expire soon.


    Args:
    Args:
    days: Number of days to consider as "soon"
    days: Number of days to consider as "soon"


    Returns:
    Returns:
    True if the payment method will expire soon, False otherwise
    True if the payment method will expire soon, False otherwise
    """
    """
    if self.payment_type != self.TYPE_CARD:
    if self.payment_type != self.TYPE_CARD:
    return False
    return False


    now = datetime.now()
    now = datetime.now()
    exp_month = self.details.get("exp_month", 0)
    exp_month = self.details.get("exp_month", 0)
    exp_year = self.details.get("exp_year", 0)
    exp_year = self.details.get("exp_year", 0)


    # Card expires at the end of the expiration month
    # Card expires at the end of the expiration month
    exp_date = datetime(exp_year, exp_month, 1)
    exp_date = datetime(exp_year, exp_month, 1)
    exp_date = datetime(exp_date.year, exp_date.month + 1, 1)
    exp_date = datetime(exp_date.year, exp_date.month + 1, 1)


    # Check if expiration is within the specified number of days
    # Check if expiration is within the specified number of days
    return 0 <= (exp_date - now).days <= days
    return 0 <= (exp_date - now).days <= days


    def update_details(self, details: Dict[str, Any]) -> None:
    def update_details(self, details: Dict[str, Any]) -> None:
    """
    """
    Update payment method details.
    Update payment method details.


    Args:
    Args:
    details: New payment details
    details: New payment details
    """
    """
    if self.payment_type == self.TYPE_CARD:
    if self.payment_type == self.TYPE_CARD:
    # Only allow updating expiration date and address
    # Only allow updating expiration date and address
    if "exp_month" in details:
    if "exp_month" in details:
    self.details["exp_month"] = int(details["exp_month"])
    self.details["exp_month"] = int(details["exp_month"])


    if "exp_year" in details:
    if "exp_year" in details:
    self.details["exp_year"] = int(details["exp_year"])
    self.details["exp_year"] = int(details["exp_year"])


    if "address" in details:
    if "address" in details:
    self.details["address"] = details["address"]
    self.details["address"] = details["address"]


    if "name" in details:
    if "name" in details:
    self.details["name"] = details["name"]
    self.details["name"] = details["name"]


    elif self.payment_type == self.TYPE_BANK_ACCOUNT:
    elif self.payment_type == self.TYPE_BANK_ACCOUNT:
    # Only allow updating account type and bank name
    # Only allow updating account type and bank name
    if "account_type" in details:
    if "account_type" in details:
    self.details["account_type"] = details["account_type"]
    self.details["account_type"] = details["account_type"]


    if "bank_name" in details:
    if "bank_name" in details:
    self.details["bank_name"] = details["bank_name"]
    self.details["bank_name"] = details["bank_name"]


    if "name" in details:
    if "name" in details:
    self.details["name"] = details["name"]
    self.details["name"] = details["name"]


    elif self.payment_type == self.TYPE_PAYPAL:
    elif self.payment_type == self.TYPE_PAYPAL:
    # PayPal details cannot be updated
    # PayPal details cannot be updated
    pass
    pass


    elif self.payment_type == self.TYPE_CRYPTO:
    elif self.payment_type == self.TYPE_CRYPTO:
    # Only allow updating network
    # Only allow updating network
    if "network" in details:
    if "network" in details:
    self.details["network"] = details["network"]
    self.details["network"] = details["network"]


    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def update_metadata(self, metadata: Dict[str, Any]) -> None:
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
    """
    """
    Update payment method metadata.
    Update payment method metadata.


    Args:
    Args:
    metadata: New metadata
    metadata: New metadata
    """
    """
    self.metadata.update(metadata)
    self.metadata.update(metadata)
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def set_as_default(self, is_default: bool = True) -> None:
    def set_as_default(self, is_default: bool = True) -> None:
    """
    """
    Set this payment method as the default.
    Set this payment method as the default.


    Args:
    Args:
    is_default: Whether this payment method is the default
    is_default: Whether this payment method is the default
    """
    """
    self.is_default = is_default
    self.is_default = is_default
    self.updated_at = datetime.now()
    self.updated_at = datetime.now()


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the payment method to a dictionary.
    Convert the payment method to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the payment method
    Dictionary representation of the payment method
    """
    """
    return {
    return {
    "id": self.id,
    "id": self.id,
    "customer_id": self.customer_id,
    "customer_id": self.customer_id,
    "type": self.payment_type,
    "type": self.payment_type,
    "details": self.details,
    "details": self.details,
    "metadata": self.metadata,
    "metadata": self.metadata,
    "is_default": self.is_default,
    "is_default": self.is_default,
    "created_at": self.created_at.isoformat(),
    "created_at": self.created_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    "updated_at": self.updated_at.isoformat(),
    }
    }


    def to_json(self, indent: int = 2) -> str:
    def to_json(self, indent: int = 2) -> str:
    """
    """
    Convert the payment method to a JSON string.
    Convert the payment method to a JSON string.


    Args:
    Args:
    indent: Number of spaces for indentation
    indent: Number of spaces for indentation


    Returns:
    Returns:
    JSON string representation of the payment method
    JSON string representation of the payment method
    """
    """
    return json.dumps(self.to_dict(), indent=indent)
    return json.dumps(self.to_dict(), indent=indent)


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaymentMethod":
    def from_dict(cls, data: Dict[str, Any]) -> "PaymentMethod":
    """
    """
    Create a payment method from a dictionary.
    Create a payment method from a dictionary.


    Args:
    Args:
    data: Dictionary with payment method data
    data: Dictionary with payment method data


    Returns:
    Returns:
    PaymentMethod instance
    PaymentMethod instance
    """
    """
    # Create a new payment method
    # Create a new payment method
    payment_method = cls(
    payment_method = cls(
    customer_id=data["customer_id"],
    customer_id=data["customer_id"],
    payment_type=data["type"],
    payment_type=data["type"],
    payment_details=data["details"],
    payment_details=data["details"],
    metadata=data.get("metadata", {}),
    metadata=data.get("metadata", {}),
    )
    )


    # Set additional fields
    # Set additional fields
    payment_method.id = data["id"]
    payment_method.id = data["id"]
    payment_method.is_default = data.get("is_default", False)
    payment_method.is_default = data.get("is_default", False)
    payment_method.created_at = datetime.fromisoformat(data["created_at"])
    payment_method.created_at = datetime.fromisoformat(data["created_at"])
    payment_method.updated_at = datetime.fromisoformat(data["updated_at"])
    payment_method.updated_at = datetime.fromisoformat(data["updated_at"])


    return payment_method
    return payment_method


    def __str__(self) -> str:
    def __str__(self) -> str:
    """String representation of the payment method."""
    if self.payment_type == self.TYPE_CARD:
    return f"Card ending in {self.details['last4']} ({self.details['brand']})"
    elif self.payment_type == self.TYPE_BANK_ACCOUNT:
    return f"Bank account ending in {self.details['last4']}"
    elif self.payment_type == self.TYPE_PAYPAL:
    return f"PayPal ({self.details['email']})"
    elif self.payment_type == self.TYPE_CRYPTO:
    return f"Crypto ({self.details['currency']})"
    else:
    return f"Payment method ({self.payment_type})"

    def __repr__(self) -> str:
    """Detailed string representation of the payment method."""
    return f"PaymentMethod(id={self.id}, type={self.payment_type}, customer_id={self.customer_id})"


    # Example usage
    if __name__ == "__main__":
    # Create a credit card payment method
    card_payment = PaymentMethod(
    customer_id="cust_123",
    payment_type=PaymentMethod.TYPE_CARD,
    payment_details={
    "number": "4242424242424242",
    "exp_month": 12,
    "exp_year": 2030,
    "cvc": "123",
    "name": "John Doe",
    "address": {
    "line1": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94111",
    "country": "US",
    },
    },
    )

    print(f"Card payment method: {card_payment}")
    print(f"Card details: {card_payment.details}")
    print(f"Is expired: {card_payment.is_expired()}")
    print(f"Will expire soon: {card_payment.will_expire_soon()}")

    # Create a bank account payment method
    bank_payment = PaymentMethod(
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

    print(f"\nBank payment method: {bank_payment}")
    print(f"Bank details: {bank_payment.details}")

    # Create a PayPal payment method
    paypal_payment = PaymentMethod(
    customer_id="cust_123",
    payment_type=PaymentMethod.TYPE_PAYPAL,
    payment_details={"email": "john.doe@example.com", "account_id": "paypal_123"},
    )

    print(f"\nPayPal payment method: {paypal_payment}")
    print(f"PayPal details: {paypal_payment.details}")

    # Convert to dictionary and back
    payment_dict = card_payment.to_dict()
    print(f"\nPayment method dictionary: {payment_dict}")

    restored_payment = PaymentMethod.from_dict(payment_dict)
    print(f"Restored payment method: {restored_payment}")
    print(f"Is same ID: {restored_payment.id == card_payment.id}")