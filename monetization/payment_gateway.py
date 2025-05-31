"""payment_gateway.py - Module for payment gateway functionality."""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, Union

from common_utils.logging import get_logger

logger = get_logger(__name__)


class PaymentStatus(Enum):
    """Payment status enum."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(Enum):
    """Payment method enum."""

    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    CRYPTO = "crypto"


class PaymentGateway:
    """Base payment gateway class."""

    def __init__(self, api_key: str, is_test_mode: bool = False):
        """
        Initialize the payment gateway.

        Args:
            api_key: API key for the payment gateway
            is_test_mode: Whether to use test mode

        """
        self.api_key = api_key
        self.is_test_mode = is_test_mode
        self._validate_api_key()

    def _validate_api_key(self) -> None:
        """Validate the API key."""
        if not self.api_key:
            raise ValueError("API key is required")
        if len(self.api_key) < 10:
            raise ValueError("API key is too short")

    def process_payment(
        self,
        amount: Union[Decimal, float, str],
        currency: str,
        payment_method: PaymentMethod,
        description: str,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Process a payment.

        Args:
            amount: Payment amount
            currency: Currency code (e.g., USD)
            payment_method: Payment method
            description: Payment description
            metadata: Additional metadata

        Returns:
            Dictionary containing payment details

        """
        # Convert amount to Decimal
        amount = Decimal(str(amount))

        # Validate inputs
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if not currency:
            raise ValueError("Currency is required")
        if not description:
            raise ValueError("Description is required")

        # Create payment record
        payment = {
            "id": f"pay_{datetime.now(timezone.utc).timestamp()}",
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method.value,
            "description": description,
            "status": PaymentStatus.PENDING.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }

        # Process payment (mock implementation)
        try:
            # Simulate payment processing
            if self.is_test_mode:
                payment["status"] = PaymentStatus.COMPLETED.value
            else:
                # In real implementation, this would call the payment provider's API
                payment["status"] = PaymentStatus.COMPLETED.value

            logger.info(f"Payment processed successfully: {payment['id']}")
            return payment

        except Exception as e:
            payment["status"] = PaymentStatus.FAILED.value
            payment["error"] = str(e)
            logger.error(f"Payment failed: {payment['id']} - {e!s}")
            raise

    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[Union[Decimal, float, str]] = None,
        reason: Optional[str] = None,
    ) -> dict:
        """
        Refund a payment.

        Args:
            payment_id: ID of the payment to refund
            amount: Amount to refund (if None, refunds full amount)
            reason: Reason for refund

        Returns:
            Dictionary containing refund details

        """
        # Validate payment ID
        if not payment_id:
            raise ValueError("Payment ID is required")

        # Convert amount to Decimal if provided
        if amount is not None:
            amount = Decimal(str(amount))
            if amount <= 0:
                raise ValueError("Refund amount must be greater than 0")

        # Create refund record
        refund = {
            "id": f"ref_{datetime.now(timezone.utc).timestamp()}",
            "payment_id": payment_id,
            "amount": amount,
            "reason": reason,
            "status": PaymentStatus.PENDING.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Process refund (mock implementation)
        try:
            # Simulate refund processing
            if self.is_test_mode:
                refund["status"] = PaymentStatus.REFUNDED.value
            else:
                # In real implementation, this would call the payment provider's API
                refund["status"] = PaymentStatus.REFUNDED.value

            logger.info(f"Refund processed successfully: {refund['id']}")
            return refund

        except Exception as e:
            refund["status"] = PaymentStatus.FAILED.value
            refund["error"] = str(e)
            logger.error(f"Refund failed: {refund['id']} - {e!s}")
            raise

    def get_payment_status(self, payment_id: str) -> dict:
        """
        Get payment status.

        Args:
            payment_id: ID of the payment

        Returns:
            Dictionary containing payment status

        """
        # Validate payment ID
        if not payment_id:
            raise ValueError("Payment ID is required")

        # Mock implementation
        return {
            "id": payment_id,
            "status": PaymentStatus.COMPLETED.value,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
