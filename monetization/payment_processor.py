"""
Payment processor interface for the pAIssive Income project.

This module provides an abstract base class for payment processors and
common utility methods for payment processing.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid


def get_payment_gateway(
    gateway_type: str = "stripe", config: Optional[Dict[str, Any]] = None
):
    """
    Get a payment gateway of the specified type.

    Args:
        gateway_type: Type of gateway to get (e.g., "stripe", "paypal")
        config: Optional configuration for the gateway

    Returns:
        A payment gateway instance
    """
    from tests.mocks.mock_payment_apis import create_payment_gateway

    return create_payment_gateway(gateway_type, config)


class PaymentProcessor(ABC):
    """
    Abstract base class for payment processors.

    This class defines the interface that all payment processors must implement.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize a payment processor.

        Args:
            config: Configuration for the payment processor
        """
        self.id = str(uuid.uuid4())
        self.name = config.get("name", "Payment Processor")
        self.config = config
        self.created_at = datetime.now()

    @abstractmethod
    def process_payment(
        self,
        amount: float,
        currency: str,
        payment_method_id: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a payment.

        Args:
            amount: Amount to charge
            currency: Currency code (e.g., USD)
            payment_method_id: ID of the payment method
            description: Description of the payment
            metadata: Additional metadata for the payment

        Returns:
            Dictionary with payment result
        """
        pass

    @abstractmethod
    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Refund a payment.

        Args:
            payment_id: ID of the payment to refund
            amount: Amount to refund (if None, refund the full amount)
            reason: Reason for the refund

        Returns:
            Dictionary with refund result
        """
        pass

    @abstractmethod
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Get information about a payment.

        Args:
            payment_id: ID of the payment

        Returns:
            Dictionary with payment information
        """
        pass

    @abstractmethod
    def list_payments(
        self,
        customer_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List payments.

        Args:
            customer_id: ID of the customer
            start_date: Start date for payments
            end_date: End date for payments
            limit: Maximum number of payments to return

        Returns:
            List of payments
        """
        pass

    @abstractmethod
    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a customer.

        Args:
            email: Email of the customer
            name: Name of the customer
            metadata: Additional metadata for the customer

        Returns:
            Dictionary with customer information
        """
        pass

    @abstractmethod
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Get information about a customer.

        Args:
            customer_id: ID of the customer

        Returns:
            Dictionary with customer information
        """
        pass

    @abstractmethod
    def update_customer(
        self,
        customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a customer.

        Args:
            customer_id: ID of the customer
            email: New email of the customer
            name: New name of the customer
            metadata: New metadata for the customer

        Returns:
            Dictionary with updated customer information
        """
        pass

    @abstractmethod
    def delete_customer(self, customer_id: str) -> bool:
        """
        Delete a customer.

        Args:
            customer_id: ID of the customer

        Returns:
            True if the customer was deleted, False otherwise
        """
        pass

    @abstractmethod
    def create_payment_method(
        self,
        customer_id: str,
        payment_type: str,
        payment_details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a payment method.

        Args:
            customer_id: ID of the customer
            payment_type: Type of payment method (e.g., card, bank_account)
            payment_details: Details of the payment method
            metadata: Additional metadata for the payment method

        Returns:
            Dictionary with payment method information
        """
        pass

    @abstractmethod
    def get_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        """
        Get information about a payment method.

        Args:
            payment_method_id: ID of the payment method

        Returns:
            Dictionary with payment method information
        """
        pass

    @abstractmethod
    def list_payment_methods(
        self, customer_id: str, payment_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List payment methods for a customer.

        Args:
            customer_id: ID of the customer
            payment_type: Type of payment methods to list

        Returns:
            List of payment methods
        """
        pass

    @abstractmethod
    def update_payment_method(
        self,
        payment_method_id: str,
        payment_details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a payment method.

        Args:
            payment_method_id: ID of the payment method
            payment_details: New details of the payment method
            metadata: New metadata for the payment method

        Returns:
            Dictionary with updated payment method information
        """
        pass

    @abstractmethod
    def delete_payment_method(self, payment_method_id: str) -> bool:
        """
        Delete a payment method.

        Args:
            payment_method_id: ID of the payment method

        Returns:
            True if the payment method was deleted, False otherwise
        """
        pass

    @abstractmethod
    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        payment_method_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a subscription.

        Args:
            customer_id: ID of the customer
            plan_id: ID of the plan
            payment_method_id: ID of the payment method
            metadata: Additional metadata for the subscription

        Returns:
            Dictionary with subscription information
        """
        pass

    @abstractmethod
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get information about a subscription.

        Args:
            subscription_id: ID of the subscription

        Returns:
            Dictionary with subscription information
        """
        pass

    @abstractmethod
    def update_subscription(
        self,
        subscription_id: str,
        plan_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a subscription.

        Args:
            subscription_id: ID of the subscription
            plan_id: New ID of the plan
            payment_method_id: New ID of the payment method
            metadata: New metadata for the subscription

        Returns:
            Dictionary with updated subscription information
        """
        pass

    @abstractmethod
    def cancel_subscription(
        self, subscription_id: str, cancel_at_period_end: bool = True
    ) -> Dict[str, Any]:
        """
        Cancel a subscription.

        Args:
            subscription_id: ID of the subscription
            cancel_at_period_end: Whether to cancel at the end of the billing period

        Returns:
            Dictionary with updated subscription information
        """
        pass

    @abstractmethod
    def list_subscriptions(
        self,
        customer_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List subscriptions.

        Args:
            customer_id: ID of the customer
            plan_id: ID of the plan
            status: Status of the subscriptions
            limit: Maximum number of subscriptions to return

        Returns:
            List of subscriptions
        """
        pass

    def format_amount(self, amount: float, currency: str) -> str:
        """
        Format an amount with currency symbol.

        Args:
            amount: Amount to format
            currency: Currency code

        Returns:
            Formatted amount with currency symbol
        """
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CAD": "C$",
            "AUD": "A$",
        }

        symbol = currency_symbols.get(currency, currency)

        if currency == "JPY":
            # JPY doesn't use decimal places
            return f"{symbol}{int(amount):,}"
        else:
            return f"{symbol}{amount:,.2f}"

    def validate_card_number(self, card_number: str) -> bool:
        """
        Validate a credit card number using the Luhn algorithm.

        Args:
            card_number: Credit card number to validate

        Returns:
            True if the card number is valid, False otherwise
        """
        # Remove spaces and dashes
        card_number = card_number.replace(" ", "").replace("-", "")

        # Check if the card number contains only digits
        if not card_number.isdigit():
            return False

        # Check length (most card numbers are 13-19 digits)
        if not (13 <= len(card_number) <= 19):
            return False

        # Luhn algorithm
        digits = [int(d) for d in card_number]
        checksum = 0

        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9

            checksum += digit

        return checksum % 10 == 0

    def mask_card_number(self, card_number: str) -> str:
        """
        Mask a credit card number for display.

        Args:
            card_number: Credit card number to mask

        Returns:
            Masked card number
        """
        # Remove spaces and dashes
        card_number = card_number.replace(" ", "").replace("-", "")

        # Keep first 6 and last 4 digits, mask the rest
        if len(card_number) <= 10:
            # For short numbers, just mask all but the last 4
            return "****" + card_number[-4:]
        else:
            return card_number[:6] + "*" * (len(card_number) - 10) + card_number[-4:]

    def get_card_type(self, card_number: str) -> str:
        """
        Get the type of a credit card based on its number.

        Args:
            card_number: Credit card number

        Returns:
            Type of the credit card (e.g., Visa, Mastercard)
        """
        # Remove spaces and dashes
        card_number = card_number.replace(" ", "").replace("-", "")

        # Check for common card types based on prefix
        if card_number.startswith("4"):
            return "Visa"
        elif card_number.startswith(
            ("51", "52", "53", "54", "55")
        ) or card_number.startswith(
            (
                "2221",
                "2222",
                "2223",
                "2224",
                "2225",
                "2226",
                "2227",
                "2228",
                "2229",
                "223",
                "224",
                "225",
                "226",
                "227",
                "228",
                "229",
                "23",
                "24",
                "25",
                "26",
                "270",
                "271",
                "2720",
            )
        ):
            return "Mastercard"
        elif card_number.startswith(("34", "37")):
            return "American Express"
        elif card_number.startswith(
            ("300", "301", "302", "303", "304", "305", "36", "38")
        ):
            return "Diners Club"
        elif card_number.startswith(
            ("6011", "644", "645", "646", "647", "648", "649", "65")
        ):
            return "Discover"
        elif card_number.startswith(("35")):
            return "JCB"
        else:
            return "Unknown"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the payment processor to a dictionary.

        Returns:
            Dictionary representation of the payment processor
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.__class__.__name__,
            "created_at": self.created_at.isoformat(),
        }

    def __str__(self) -> str:
        """String representation of the payment processor."""
        return f"{self.name} ({self.__class__.__name__})"

    def __repr__(self) -> str:
        """Detailed string representation of the payment processor."""
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
