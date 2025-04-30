"""
Mock implementations of external payment APIs for testing.

This module provides mock implementations of various payment gateway APIs
that can be used for consistent testing without external dependencies.
"""

import json
import logging
import random
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import copy

logger = logging.getLogger(__name__)


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PENDING = "pending"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class MockPaymentGateway:
    """Base class for mock payment gateways."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the mock payment gateway.

        Args:
            config: Optional configuration for the payment gateway
        """
        self.config = config or {}

        # Initialize storage
        self.customers = {}
        self.payment_methods = {}
        self.payments = {}
        self.subscriptions = {}
        self.plans = {}
        self.refunds = {}

        # Set default configuration
        self.success_rate = self.config.get("success_rate", 0.95)
        self.refund_success_rate = self.config.get("refund_success_rate", 0.98)
        self.network_error_rate = self.config.get("network_error_rate", 0.01)

        # Set supported payment types
        self.supported_payment_types = self.config.get(
            "supported_payment_types", ["card", "bank_account"]
        )

        # Set supported currencies
        self.supported_currencies = self.config.get(
            "supported_currencies", ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
        )

        # Track call history for assertions
        self.call_history = []

    def _generate_id(self, prefix: str) -> str:
        """Generate a random ID with a prefix."""
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    def _simulate_success(self, success_rate: Optional[float] = None) -> bool:
        """Simulate a success or failure based on success rate."""
        rate = success_rate if success_rate is not None else self.success_rate
        return random.random() < rate

    def _simulate_network_error(self) -> bool:
        """Simulate a network error based on error rate."""
        if self.config.get("simulate_network_errors", True) == False:
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
        Validate a credit card number using the Luhn algorithm.

        Args:
            card_number: Credit card number to validate

        Returns:
            True if the card number is valid, False otherwise
        """
        # Remove any spaces or dashes
        card_number = card_number.replace(" ", "").replace("-", "")

        # Check if the number contains only digits
        if not card_number.isdigit():
            return False

        # Check if the length is valid (most cards are 13-19 digits)
        if not (13 <= len(card_number) <= 19):
            return False

        # Apply the Luhn algorithm
        total = 0
        reverse = card_number[::-1]

        for i, digit in enumerate(reverse):
            digit = int(digit)
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit

        return total % 10 == 0

    def get_card_type(self, card_number: str) -> str:
        """
        Determine the card type based on the card number.

        Args:
            card_number: Credit card number

        Returns:
            Card type (visa, mastercard, amex, etc.)
        """
        # Remove any spaces or dashes
        card_number = card_number.replace(" ", "").replace("-", "")

        # Simplified card type detection based on prefix and length
        if card_number.startswith("4"):
            return "visa"
        elif card_number.startswith(("51", "52", "53", "54", "55")) or (
            51 <= int(card_number[:2]) <= 55
        ):
            return "mastercard"
        elif card_number.startswith(("34", "37")):
            return "amex"
        elif card_number.startswith(
            ("6011", "644", "645", "646", "647", "648", "649", "65")
        ):
            return "discover"
        else:
            return "unknown"

    def mask_card_number(self, card_number: str) -> str:
        """
        Mask a credit card number for display.

        Args:
            card_number: Credit card number to mask

        Returns:
            Masked credit card number
        """
        # Remove any spaces or dashes
        card_number = card_number.replace(" ", "").replace("-", "")

        # Determine how many digits to show
        if card_number.startswith(("34", "37")):
            # Amex: show first 6 and last 4
            return card_number[:6] + "X" * (len(card_number) - 10) + card_number[-4:]
        else:
            # Other cards: show first 4 and last 4
            return card_number[:4] + "X" * (len(card_number) - 8) + card_number[-4:]

    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new customer.

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata

        Returns:
            Created customer object
        """
        self.record_call("create_customer", email=email, name=name, metadata=metadata)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while creating customer")

        # Generate customer ID
        customer_id = self._generate_id("cust")

        # Create customer
        customer = {
            "id": customer_id,
            "email": email,
            "name": name or "",
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Store customer
        self.customers[customer_id] = customer

        return copy.deepcopy(customer)

    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Get a customer by ID.

        Args:
            customer_id: ID of the customer

        Returns:
            Customer object
        """
        self.record_call("get_customer", customer_id=customer_id)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while retrieving customer")

        # Check if customer exists
        if customer_id not in self.customers:
            raise ValueError(f"Customer not found: {customer_id}")

        return copy.deepcopy(self.customers[customer_id])

    def update_customer(
        self,
        customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a customer's information.

        Args:
            customer_id: ID of the customer
            email: New customer email
            name: New customer name
            metadata: New metadata

        Returns:
            Updated customer object
        """
        self.record_call(
            "update_customer",
            customer_id=customer_id,
            email=email,
            name=name,
            metadata=metadata,
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while updating customer")

        # Check if customer exists
        if customer_id not in self.customers:
            raise ValueError(f"Customer not found: {customer_id}")

        # Get customer
        customer = self.customers[customer_id]

        # Update fields
        if email is not None:
            customer["email"] = email

        if name is not None:
            customer["name"] = name

        if metadata is not None:
            customer["metadata"] = metadata

        customer["updated_at"] = datetime.now().isoformat()

        return copy.deepcopy(customer)

    def list_customers(
        self, email: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List customers with optional filtering.

        Args:
            email: Filter by email
            limit: Maximum number of customers to return

        Returns:
            List of customer objects
        """
        self.record_call("list_customers", email=email, limit=limit)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while listing customers")

        # Filter customers
        filtered_customers = []

        for customer in self.customers.values():
            # Apply email filter if provided
            if email and customer["email"] != email:
                continue

            filtered_customers.append(customer)

            # Stop if limit is reached
            if len(filtered_customers) >= limit:
                break

        return copy.deepcopy(filtered_customers)

    def delete_customer(self, customer_id: str) -> bool:
        """
        Delete a customer.

        Args:
            customer_id: ID of the customer

        Returns:
            True if the customer was deleted, False otherwise
        """
        self.record_call("delete_customer", customer_id=customer_id)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while deleting customer")

        # Check if customer exists
        if customer_id not in self.customers:
            raise ValueError(f"Customer not found: {customer_id}")

        # Check if customer has active subscriptions
        for subscription in self.subscriptions.values():
            if (
                subscription["customer_id"] == customer_id
                and subscription["status"] == "active"
            ):
                raise ValueError(f"Cannot delete customer with active subscriptions")

        # Delete customer
        del self.customers[customer_id]

        # Delete customer's payment methods
        payment_methods_to_delete = []
        for payment_method_id, payment_method in self.payment_methods.items():
            if payment_method["customer_id"] == customer_id:
                payment_methods_to_delete.append(payment_method_id)

        for payment_method_id in payment_methods_to_delete:
            del self.payment_methods[payment_method_id]

        return True

    def create_payment_method(
        self,
        customer_id: str,
        payment_type: str,
        payment_details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new payment method for a customer.

        Args:
            customer_id: ID of the customer
            payment_type: Type of payment method (card, bank_account, etc.)
            payment_details: Details of the payment method
            metadata: Additional metadata

        Returns:
            Created payment method object
        """
        self.record_call(
            "create_payment_method",
            customer_id=customer_id,
            payment_type=payment_type,
            payment_details=payment_details,
            metadata=metadata,
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while creating payment method")

        # Check if customer exists
        if customer_id not in self.customers:
            raise ValueError(f"Customer not found: {customer_id}")

        # Check if payment type is supported
        if payment_type not in self.supported_payment_types:
            raise ValueError(f"Payment type not supported: {payment_type}")

        # Process payment details based on payment type
        payment_details_copy = {}

        if payment_type == "card":
            # Validate card details
            if "number" not in payment_details:
                raise ValueError("Card number is required")

            if "exp_month" not in payment_details or "exp_year" not in payment_details:
                raise ValueError("Card expiration date is required")

            if "cvc" not in payment_details:
                raise ValueError("Card CVC is required")

            # Validate card number
            if not self.validate_card_number(payment_details["number"]):
                raise ValueError("Invalid card number")

            # Get card type
            card_type = self.get_card_type(payment_details["number"])

            # Mask card number
            masked_number = self.mask_card_number(payment_details["number"])

            # Create payment details
            payment_details_copy = {
                "last4": payment_details["number"][-4:],
                "brand": card_type,
                "exp_month": payment_details["exp_month"],
                "exp_year": payment_details["exp_year"],
                "masked_number": masked_number,
            }

        elif payment_type == "bank_account":
            # Validate bank account details
            if "account_number" not in payment_details:
                raise ValueError("Account number is required")

            if "routing_number" not in payment_details:
                raise ValueError("Routing number is required")

            # Mask account number
            masked_account = "****" + payment_details["account_number"][-4:]

            # Create payment details
            payment_details_copy = {
                "last4": payment_details["account_number"][-4:],
                "bank_name": payment_details.get("bank_name", ""),
                "account_type": payment_details.get("account_type", "checking"),
                "masked_account": masked_account,
            }
        else:
            # For other payment types, just copy the details
            payment_details_copy = copy.deepcopy(payment_details)

        # Generate payment method ID
        payment_method_id = self._generate_id("pm")

        # Create payment method
        payment_method = {
            "id": payment_method_id,
            "customer_id": customer_id,
            "type": payment_type,
            "details": payment_details_copy,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Store payment method
        self.payment_methods[payment_method_id] = payment_method

        return copy.deepcopy(payment_method)

    def get_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        """
        Get a payment method by ID.

        Args:
            payment_method_id: ID of the payment method

        Returns:
            Payment method object
        """
        self.record_call("get_payment_method", payment_method_id=payment_method_id)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while retrieving payment method")

        # Check if payment method exists
        if payment_method_id not in self.payment_methods:
            raise ValueError(f"Payment method not found: {payment_method_id}")

        return copy.deepcopy(self.payment_methods[payment_method_id])

    def list_payment_methods(
        self, customer_id: str, payment_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List payment methods for a customer.

        Args:
            customer_id: ID of the customer
            payment_type: Filter by payment type

        Returns:
            List of payment method objects
        """
        self.record_call(
            "list_payment_methods", customer_id=customer_id, payment_type=payment_type
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while listing payment methods")

        # Check if customer exists
        if customer_id not in self.customers:
            raise ValueError(f"Customer not found: {customer_id}")

        # Filter payment methods
        filtered_methods = []

        for payment_method in self.payment_methods.values():
            # Filter by customer ID
            if payment_method["customer_id"] != customer_id:
                continue

            # Filter by payment type if provided
            if payment_type and payment_method["type"] != payment_type:
                continue

            filtered_methods.append(payment_method)

        return copy.deepcopy(filtered_methods)

    def delete_payment_method(self, payment_method_id: str) -> bool:
        """
        Delete a payment method.

        Args:
            payment_method_id: ID of the payment method

        Returns:
            True if the payment method was deleted, False otherwise
        """
        self.record_call("delete_payment_method", payment_method_id=payment_method_id)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while deleting payment method")

        # Check if payment method exists
        if payment_method_id not in self.payment_methods:
            raise ValueError(f"Payment method not found: {payment_method_id}")

        # Check if payment method is being used in an active subscription
        for subscription in self.subscriptions.values():
            if (
                subscription["payment_method_id"] == payment_method_id
                and subscription["status"] == "active"
            ):
                raise ValueError(
                    f"Cannot delete payment method being used in active subscription"
                )

        # Delete payment method
        del self.payment_methods[payment_method_id]

        return True

    def create_payment(
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
            amount: Payment amount
            currency: Payment currency code
            payment_method_id: ID of the payment method to use
            description: Description of the payment
            metadata: Additional metadata

        Returns:
            Payment object
        """
        self.record_call(
            "create_payment",
            amount=amount,
            currency=currency,
            payment_method_id=payment_method_id,
            description=description,
            metadata=metadata,
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while processing payment")

        # Check if payment method exists
        if payment_method_id not in self.payment_methods:
            raise ValueError(f"Payment method not found: {payment_method_id}")

        # Check if currency is supported
        if currency not in self.supported_currencies:
            raise ValueError(f"Currency not supported: {currency}")

        # Get payment method
        payment_method = self.payment_methods[payment_method_id]

        # Get customer
        customer_id = payment_method["customer_id"]
        customer = self.customers.get(customer_id)

        if not customer:
            raise ValueError(f"Customer not found: {customer_id}")

        # Simulate payment success or failure
        success = self._simulate_success()

        # Generate payment ID
        payment_id = self._generate_id("pay")

        # Create payment
        payment = {
            "id": payment_id,
            "amount": amount,
            "currency": currency,
            "customer_id": customer_id,
            "payment_method_id": payment_method_id,
            "description": description,
            "metadata": metadata or {},
            "status": PaymentStatus.SUCCEEDED if success else PaymentStatus.FAILED,
            "error": (
                None
                if success
                else {"code": "card_declined", "message": "Your card was declined."}
            ),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Store payment
        self.payments[payment_id] = payment

        # If payment failed, raise an exception
        if not success:
            raise ValueError("Payment failed: Your card was declined.")

        return copy.deepcopy(payment)

    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Get a payment by ID.

        Args:
            payment_id: ID of the payment

        Returns:
            Payment object
        """
        self.record_call("get_payment", payment_id=payment_id)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while retrieving payment")

        # Check if payment exists
        if payment_id not in self.payments:
            raise ValueError(f"Payment not found: {payment_id}")

        return copy.deepcopy(self.payments[payment_id])

    def list_payments(
        self,
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List payments with optional filtering.

        Args:
            customer_id: Filter by customer ID
            payment_method_id: Filter by payment method ID
            start_date: Filter by start date
            end_date: Filter by end date
            status: Filter by payment status
            limit: Maximum number of payments to return

        Returns:
            List of payment objects
        """
        self.record_call(
            "list_payments",
            customer_id=customer_id,
            payment_method_id=payment_method_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            limit=limit,
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while listing payments")

        # Filter payments
        filtered_payments = []

        for payment in self.payments.values():
            # Filter by customer ID if provided
            if customer_id and payment["customer_id"] != customer_id:
                continue

            # Filter by payment method ID if provided
            if payment_method_id and payment["payment_method_id"] != payment_method_id:
                continue

            # Filter by status if provided
            if status and payment["status"] != status:
                continue

            # Filter by date range if provided
            if start_date or end_date:
                payment_date = datetime.fromisoformat(payment["created_at"])

                if start_date and payment_date < start_date:
                    continue

                if end_date and payment_date > end_date:
                    continue

            filtered_payments.append(payment)

            # Apply limit
            if len(filtered_payments) >= limit:
                break

        # Sort by created_at (newest first)
        filtered_payments.sort(key=lambda p: p["created_at"], reverse=True)

        return copy.deepcopy(filtered_payments)

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
            amount: Amount to refund (defaults to full payment amount)
            reason: Reason for the refund

        Returns:
            Refund object
        """
        self.record_call(
            "refund_payment", payment_id=payment_id, amount=amount, reason=reason
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while refunding payment")

        # Check if payment exists
        if payment_id not in self.payments:
            raise ValueError(f"Payment not found: {payment_id}")

        # Get the payment
        payment = self.payments[payment_id]

        # Check if payment can be refunded
        if payment["status"] != PaymentStatus.SUCCEEDED:
            raise ValueError(f"Payment cannot be refunded: {payment['status']}")

        # Determine refund amount
        refund_amount = amount if amount is not None else payment["amount"]

        # Check if refund amount is valid
        if refund_amount <= 0 or refund_amount > payment["amount"]:
            raise ValueError(f"Invalid refund amount: {refund_amount}")

        # Simulate refund success or failure
        success = self._simulate_success(self.refund_success_rate)

        # Generate refund ID
        refund_id = self._generate_id("ref")

        # Create refund
        refund = {
            "id": refund_id,
            "payment_id": payment_id,
            "amount": refund_amount,
            "currency": payment["currency"],
            "reason": reason or "requested_by_customer",
            "status": PaymentStatus.SUCCEEDED if success else PaymentStatus.FAILED,
            "error": (
                None
                if success
                else {
                    "code": "refund_failed",
                    "message": "The refund could not be processed.",
                }
            ),
            "created_at": datetime.now().isoformat(),
        }

        # Store refund
        self.refunds[refund_id] = refund

        # Update payment status if refund was successful
        if success:
            if refund_amount == payment["amount"]:
                payment["status"] = PaymentStatus.REFUNDED
            else:
                payment["status"] = PaymentStatus.PARTIALLY_REFUNDED

            payment["updated_at"] = datetime.now().isoformat()

        # If refund failed, raise an exception
        if not success:
            raise ValueError("Refund failed: The refund could not be processed.")

        return copy.deepcopy(refund)

    def get_refund(self, refund_id: str) -> Dict[str, Any]:
        """
        Get a refund by ID.

        Args:
            refund_id: ID of the refund

        Returns:
            Refund object
        """
        self.record_call("get_refund", refund_id=refund_id)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while retrieving refund")

        # Check if refund exists
        if refund_id not in self.refunds:
            raise ValueError(f"Refund not found: {refund_id}")

        return copy.deepcopy(self.refunds[refund_id])

    def list_refunds(
        self, payment_id: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List refunds with optional filtering.

        Args:
            payment_id: Filter by payment ID
            limit: Maximum number of refunds to return

        Returns:
            List of refund objects
        """
        self.record_call("list_refunds", payment_id=payment_id, limit=limit)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while listing refunds")

        # Filter refunds
        filtered_refunds = []

        for refund in self.refunds.values():
            # Filter by payment ID if provided
            if payment_id and refund["payment_id"] != payment_id:
                continue

            filtered_refunds.append(refund)

            # Apply limit
            if len(filtered_refunds) >= limit:
                break

        # Sort by created_at (newest first)
        filtered_refunds.sort(key=lambda r: r["created_at"], reverse=True)

        return copy.deepcopy(filtered_refunds)

    def create_plan(
        self,
        name: str,
        currency: str,
        interval: str,
        amount: float,
        product_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a billing plan.

        Args:
            name: Plan name
            currency: Plan currency code
            interval: Billing interval (day, week, month, year)
            amount: Plan amount
            product_id: ID of the associated product
            metadata: Additional metadata

        Returns:
            Plan object
        """
        self.record_call(
            "create_plan",
            name=name,
            currency=currency,
            interval=interval,
            amount=amount,
            product_id=product_id,
            metadata=metadata,
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while creating plan")

        # Check if currency is supported
        if currency not in self.supported_currencies:
            raise ValueError(f"Currency not supported: {currency}")

        # Check if interval is valid
        valid_intervals = ["day", "week", "month", "year"]
        if interval not in valid_intervals:
            raise ValueError(
                f"Invalid interval: {interval}. Must be one of: {', '.join(valid_intervals)}"
            )

        # Generate plan ID
        plan_id = self._generate_id("plan")

        # Create plan
        plan = {
            "id": plan_id,
            "name": name,
            "currency": currency,
            "interval": interval,
            "amount": amount,
            "product_id": product_id,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Store plan
        self.plans[plan_id] = plan

        return copy.deepcopy(plan)

    def get_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Get a plan by ID.

        Args:
            plan_id: ID of the plan

        Returns:
            Plan object
        """
        self.record_call("get_plan", plan_id=plan_id)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while retrieving plan")

        # Check if plan exists
        if plan_id not in self.plans:
            raise ValueError(f"Plan not found: {plan_id}")

        return copy.deepcopy(self.plans[plan_id])

    def list_plans(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all plans.

        Args:
            limit: Maximum number of plans to return

        Returns:
            List of plan objects
        """
        self.record_call("list_plans", limit=limit)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while listing plans")

        # Get all plans up to the limit
        plans_list = list(self.plans.values())[:limit]

        return copy.deepcopy(plans_list)

    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        payment_method_id: str,
        trial_end: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a subscription.

        Args:
            customer_id: ID of the customer
            plan_id: ID of the plan
            payment_method_id: ID of the payment method to use
            trial_end: End date of the trial period
            metadata: Additional metadata

        Returns:
            Subscription object
        """
        self.record_call(
            "create_subscription",
            customer_id=customer_id,
            plan_id=plan_id,
            payment_method_id=payment_method_id,
            trial_end=trial_end,
            metadata=metadata,
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while creating subscription")

        # Check if customer exists
        if customer_id not in self.customers:
            raise ValueError(f"Customer not found: {customer_id}")

        # Check if plan exists
        if plan_id not in self.plans:
            raise ValueError(f"Plan not found: {plan_id}")

        # Check if payment method exists
        if payment_method_id not in self.payment_methods:
            raise ValueError(f"Payment method not found: {payment_method_id}")

        # Check if payment method belongs to customer
        payment_method = self.payment_methods[payment_method_id]
        if payment_method["customer_id"] != customer_id:
            raise ValueError(
                f"Payment method {payment_method_id} does not belong to customer {customer_id}"
            )

        # Get plan
        plan = self.plans[plan_id]

        # Determine interval in days
        interval_days = {"day": 1, "week": 7, "month": 30, "year": 365}
        days = interval_days.get(plan["interval"], 30)

        # Calculate current period dates
        now = datetime.now()
        current_period_start = now
        current_period_end = now + timedelta(days=days)

        # Generate subscription ID
        subscription_id = self._generate_id("sub")

        # Determine status based on trial
        if trial_end and trial_end > now:
            status = "trialing"
        else:
            status = "active"

            # Process initial payment if not in trial
            try:
                self.create_payment(
                    amount=plan["amount"],
                    currency=plan["currency"],
                    payment_method_id=payment_method_id,
                    description=f"Initial payment for subscription {subscription_id}",
                    metadata={"subscription_id": subscription_id},
                )
            except ValueError:
                # If payment fails, return subscription with status "incomplete"
                status = "incomplete"

        # Create subscription
        subscription = {
            "id": subscription_id,
            "customer_id": customer_id,
            "plan_id": plan_id,
            "payment_method_id": payment_method_id,
            "status": status,
            "current_period_start": current_period_start.isoformat(),
            "current_period_end": current_period_end.isoformat(),
            "trial_start": now.isoformat() if trial_end else None,
            "trial_end": trial_end.isoformat() if trial_end else None,
            "cancel_at_period_end": False,
            "canceled_at": None,
            "ended_at": None,
            "metadata": metadata or {},
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        # Store subscription
        self.subscriptions[subscription_id] = subscription

        return copy.deepcopy(subscription)

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get a subscription by ID.

        Args:
            subscription_id: ID of the subscription

        Returns:
            Subscription object
        """
        self.record_call("get_subscription", subscription_id=subscription_id)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while retrieving subscription")

        # Check if subscription exists
        if subscription_id not in self.subscriptions:
            raise ValueError(f"Subscription not found: {subscription_id}")

        return copy.deepcopy(self.subscriptions[subscription_id])

    def update_subscription(
        self,
        subscription_id: str,
        plan_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        trial_end: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a subscription.

        Args:
            subscription_id: ID of the subscription
            plan_id: New plan ID
            payment_method_id: New payment method ID
            trial_end: New trial end date
            metadata: New metadata

        Returns:
            Updated subscription object
        """
        self.record_call(
            "update_subscription",
            subscription_id=subscription_id,
            plan_id=plan_id,
            payment_method_id=payment_method_id,
            trial_end=trial_end,
            metadata=metadata,
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while updating subscription")

        # Check if subscription exists
        if subscription_id not in self.subscriptions:
            raise ValueError(f"Subscription not found: {subscription_id}")

        # Get subscription
        subscription = self.subscriptions[subscription_id]

        # Check if subscription is active
        if subscription["status"] not in ["active", "trialing", "past_due"]:
            raise ValueError(
                f"Cannot update subscription with status: {subscription['status']}"
            )

        # Update plan if provided
        if plan_id is not None:
            # Check if plan exists
            if plan_id not in self.plans:
                raise ValueError(f"Plan not found: {plan_id}")

            subscription["plan_id"] = plan_id

        # Update payment method if provided
        if payment_method_id is not None:
            # Check if payment method exists
            if payment_method_id not in self.payment_methods:
                raise ValueError(f"Payment method not found: {payment_method_id}")

            # Check if payment method belongs to customer
            payment_method = self.payment_methods[payment_method_id]
            if payment_method["customer_id"] != subscription["customer_id"]:
                raise ValueError(
                    f"Payment method {payment_method_id} does not belong to customer {subscription['customer_id']}"
                )

            subscription["payment_method_id"] = payment_method_id

        # Update trial end if provided
        if trial_end is not None:
            now = datetime.now()

            # If trial end is in the future, set subscription to trialing
            if trial_end > now:
                subscription["status"] = "trialing"
                subscription["trial_end"] = trial_end.isoformat()

            # If trial end is in the past, end trial and set to active
            elif subscription["status"] == "trialing":
                subscription["status"] = "active"
                subscription["trial_end"] = trial_end.isoformat()

        # Update metadata if provided
        if metadata is not None:
            subscription["metadata"] = metadata

        subscription["updated_at"] = datetime.now().isoformat()

        return copy.deepcopy(subscription)

    def cancel_subscription(
        self, subscription_id: str, cancel_at_period_end: bool = True
    ) -> Dict[str, Any]:
        """
        Cancel a subscription.

        Args:
            subscription_id: ID of the subscription
            cancel_at_period_end: Whether to cancel at the end of the current period

        Returns:
            Updated subscription object
        """
        self.record_call(
            "cancel_subscription",
            subscription_id=subscription_id,
            cancel_at_period_end=cancel_at_period_end,
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while canceling subscription")

        # Check if subscription exists
        if subscription_id not in self.subscriptions:
            raise ValueError(f"Subscription not found: {subscription_id}")

        # Get subscription
        subscription = self.subscriptions[subscription_id]

        # Check if subscription is active or trialing
        if subscription["status"] not in ["active", "trialing", "past_due"]:
            raise ValueError(
                f"Cannot cancel subscription with status: {subscription['status']}"
            )

        # Update subscription
        subscription["canceled_at"] = datetime.now().isoformat()

        if cancel_at_period_end:
            subscription["cancel_at_period_end"] = True
        else:
            subscription["status"] = "canceled"
            subscription["ended_at"] = datetime.now().isoformat()

        subscription["updated_at"] = datetime.now().isoformat()

        return copy.deepcopy(subscription)

    def resume_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Resume a canceled subscription.

        Args:
            subscription_id: ID of the subscription

        Returns:
            Updated subscription object
        """
        self.record_call("resume_subscription", subscription_id=subscription_id)

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while resuming subscription")

        # Check if subscription exists
        if subscription_id not in self.subscriptions:
            raise ValueError(f"Subscription not found: {subscription_id}")

        # Get subscription
        subscription = self.subscriptions[subscription_id]

        # Check if subscription can be resumed
        if (
            subscription["status"] != "canceled"
            and not subscription["cancel_at_period_end"]
        ):
            raise ValueError(f"Subscription is not canceled: {subscription['status']}")

        # Update subscription
        if subscription["status"] == "canceled":
            # If already canceled, recreate subscription
            subscription["status"] = "active"
            subscription["ended_at"] = None

            # Calculate new period dates
            now = datetime.now()

            # Get plan
            plan = self.plans.get(subscription["plan_id"])
            if not plan:
                raise ValueError(f"Plan not found: {subscription['plan_id']}")

            # Determine interval in days
            interval_days = {"day": 1, "week": 7, "month": 30, "year": 365}
            days = interval_days.get(plan["interval"], 30)

            subscription["current_period_start"] = now.isoformat()
            subscription["current_period_end"] = (
                now + timedelta(days=days)
            ).isoformat()

        # Clear cancellation
        subscription["cancel_at_period_end"] = False
        subscription["canceled_at"] = None
        subscription["updated_at"] = datetime.now().isoformat()

        return copy.deepcopy(subscription)

    def list_subscriptions(
        self,
        customer_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List subscriptions with optional filtering.

        Args:
            customer_id: Filter by customer ID
            plan_id: Filter by plan ID
            status: Filter by subscription status
            limit: Maximum number of subscriptions to return

        Returns:
            List of subscription objects
        """
        self.record_call(
            "list_subscriptions",
            customer_id=customer_id,
            plan_id=plan_id,
            status=status,
            limit=limit,
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while listing subscriptions")

        # Filter subscriptions
        filtered_subscriptions = []

        for subscription in self.subscriptions.values():
            # Filter by customer ID if provided
            if customer_id and subscription["customer_id"] != customer_id:
                continue

            # Filter by plan ID if provided
            if plan_id and subscription["plan_id"] != plan_id:
                continue

            # Filter by status if provided
            if status and subscription["status"] != status:
                continue

            filtered_subscriptions.append(subscription)

            # Apply limit
            if len(filtered_subscriptions) >= limit:
                break

        # Sort by created_at (newest first)
        filtered_subscriptions.sort(key=lambda s: s["created_at"], reverse=True)

        return copy.deepcopy(filtered_subscriptions)


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
        Create a payment token.

        Args:
            payment_type: Type of payment method
            payment_details: Payment details

        Returns:
            Token object
        """
        self.record_call(
            "create_token", payment_type=payment_type, payment_details=payment_details
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while creating token")

        # Check if payment type is supported
        if payment_type not in self.supported_payment_types:
            raise ValueError(f"Payment type not supported: {payment_type}")

        # Process payment details based on payment type
        token_details = {}

        if payment_type == "card":
            # Validate card details
            if "number" not in payment_details:
                raise ValueError("Card number is required")

            if "exp_month" not in payment_details or "exp_year" not in payment_details:
                raise ValueError("Card expiration date is required")

            if "cvc" not in payment_details:
                raise ValueError("Card CVC is required")

            # Validate card number
            if not self.validate_card_number(payment_details["number"]):
                raise ValueError("Invalid card number")

            # Get card type
            card_type = self.get_card_type(payment_details["number"])

            # Mask card number
            masked_number = self.mask_card_number(payment_details["number"])

            # Create token details
            token_details = {
                "last4": payment_details["number"][-4:],
                "brand": card_type,
                "exp_month": payment_details["exp_month"],
                "exp_year": payment_details["exp_year"],
                "fingerprint": f"fingerprint_{uuid.uuid4().hex[:8]}",
            }
        elif payment_type == "bank_account":
            # Similar processing for bank accounts
            token_details = {
                "last4": payment_details["account_number"][-4:],
                "bank_name": payment_details.get("bank_name", ""),
                "account_type": payment_details.get("account_type", "checking"),
                "country": payment_details.get("country", "US"),
                "currency": payment_details.get("currency", "usd"),
                "fingerprint": f"fingerprint_{uuid.uuid4().hex[:8]}",
            }

        # Generate token ID
        token_id = self._generate_id("tok")

        # Create token
        token = {
            "id": token_id,
            "object": "token",
            "type": payment_type,
            "details": token_details,
            "created": int(datetime.now().timestamp()),
            "livemode": False,
            "used": False,
        }

        return token


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
        Create a billing agreement.

        Args:
            description: Agreement description
            customer_id: ID of the customer
            start_date: Start date of the agreement
            metadata: Additional metadata

        Returns:
            Billing agreement object
        """
        self.record_call(
            "create_billing_agreement",
            description=description,
            customer_id=customer_id,
            start_date=start_date,
            metadata=metadata,
        )

        # Check if a network error should be simulated
        if self._simulate_network_error():
            raise ConnectionError("Network error while creating billing agreement")

        # Check if customer exists
        if customer_id not in self.customers:
            raise ValueError(f"Customer not found: {customer_id}")

        # Set start date if not provided
        if start_date is None:
            start_date = datetime.now()

        # Generate agreement ID
        agreement_id = self._generate_id("ba")

        # Create agreement
        agreement = {
            "id": agreement_id,
            "customer_id": customer_id,
            "description": description,
            "status": "active",
            "start_date": start_date.isoformat(),
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        return agreement


# Create factory function for payment gateways
def create_payment_gateway(
    gateway_type: str, config: Optional[Dict[str, Any]] = None
) -> Union[MockStripeGateway, MockPayPalGateway]:
    """
    Create a mock payment gateway of the specified type.

    Args:
        gateway_type: Type of gateway to create ("stripe" or "paypal")
        config: Optional configuration for the gateway

    Returns:
        A mock payment gateway instance
    """
    gateways = {"stripe": MockStripeGateway, "paypal": MockPayPalGateway}

    gateway_class = gateways.get(gateway_type.lower())
    if not gateway_class:
        raise ValueError(f"Unknown gateway type: {gateway_type}")

    return gateway_class(config)
