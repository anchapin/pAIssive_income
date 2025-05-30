"""test_payment_gateway - Module for testing payment gateway functionality."""

from decimal import Decimal
import pytest

from monetization.payment_gateway import PaymentGateway, PaymentMethod, PaymentStatus


@pytest.fixture
def payment_gateway():
    """Create a payment gateway instance for testing."""
    return PaymentGateway(api_key="test_api_key_1234567890", is_test_mode=True)


def test_init_payment_gateway():
    """Test payment gateway initialization."""
    # Test valid initialization
    gateway = PaymentGateway(api_key="test_api_key_1234567890")
    assert gateway.api_key == "test_api_key_1234567890"
    assert gateway.is_test_mode is False

    # Test test mode
    gateway = PaymentGateway(api_key="test_api_key_1234567890", is_test_mode=True)
    assert gateway.is_test_mode is True

    # Test invalid API key
    with pytest.raises(ValueError, match="API key is required"):
        PaymentGateway(api_key="")

    with pytest.raises(ValueError, match="API key is too short"):
        PaymentGateway(api_key="short")


def test_process_payment(payment_gateway):
    """Test payment processing."""
    # Test successful payment
    payment = payment_gateway.process_payment(
        amount=100.50,
        currency="USD",
        payment_method=PaymentMethod.CREDIT_CARD,
        description="Test payment",
        metadata={"order_id": "123"}
    )

    assert payment["amount"] == Decimal("100.50")
    assert payment["currency"] == "USD"
    assert payment["payment_method"] == PaymentMethod.CREDIT_CARD.value
    assert payment["description"] == "Test payment"
    assert payment["status"] == PaymentStatus.COMPLETED.value
    assert payment["metadata"] == {"order_id": "123"}
    assert "id" in payment
    assert "created_at" in payment

    # Test invalid amount
    with pytest.raises(ValueError, match="Amount must be greater than 0"):
        payment_gateway.process_payment(
            amount=0,
            currency="USD",
            payment_method=PaymentMethod.CREDIT_CARD,
            description="Test payment"
        )

    with pytest.raises(ValueError, match="Amount must be greater than 0"):
        payment_gateway.process_payment(
            amount=-100,
            currency="USD",
            payment_method=PaymentMethod.CREDIT_CARD,
            description="Test payment"
        )

    # Test missing currency
    with pytest.raises(ValueError, match="Currency is required"):
        payment_gateway.process_payment(
            amount=100,
            currency="",
            payment_method=PaymentMethod.CREDIT_CARD,
            description="Test payment"
        )

    # Test missing description
    with pytest.raises(ValueError, match="Description is required"):
        payment_gateway.process_payment(
            amount=100,
            currency="USD",
            payment_method=PaymentMethod.CREDIT_CARD,
            description=""
        )


def test_refund_payment(payment_gateway):
    """Test payment refund."""
    # Process a payment first
    payment = payment_gateway.process_payment(
        amount=100,
        currency="USD",
        payment_method=PaymentMethod.CREDIT_CARD,
        description="Test payment"
    )

    # Test full refund
    refund = payment_gateway.refund_payment(
        payment_id=payment["id"],
        reason="Customer request"
    )

    assert refund["payment_id"] == payment["id"]
    assert refund["status"] == PaymentStatus.REFUNDED.value
    assert refund["reason"] == "Customer request"
    assert "id" in refund
    assert "created_at" in refund

    # Test partial refund
    refund = payment_gateway.refund_payment(
        payment_id=payment["id"],
        amount=50,
        reason="Partial refund"
    )

    assert refund["payment_id"] == payment["id"]
    assert refund["amount"] == Decimal("50")
    assert refund["status"] == PaymentStatus.REFUNDED.value
    assert refund["reason"] == "Partial refund"

    # Test invalid payment ID
    with pytest.raises(ValueError, match="Payment ID is required"):
        payment_gateway.refund_payment(payment_id="")

    # Test invalid refund amount
    with pytest.raises(ValueError, match="Refund amount must be greater than 0"):
        payment_gateway.refund_payment(
            payment_id=payment["id"],
            amount=0
        )

    with pytest.raises(ValueError, match="Refund amount must be greater than 0"):
        payment_gateway.refund_payment(
            payment_id=payment["id"],
            amount=-50
        )


def test_get_payment_status(payment_gateway):
    """Test getting payment status."""
    # Process a payment first
    payment = payment_gateway.process_payment(
        amount=100,
        currency="USD",
        payment_method=PaymentMethod.CREDIT_CARD,
        description="Test payment"
    )

    # Test getting status
    status = payment_gateway.get_payment_status(payment["id"])
    assert status["id"] == payment["id"]
    assert status["status"] == PaymentStatus.COMPLETED.value
    assert "last_updated" in status

    # Test invalid payment ID
    with pytest.raises(ValueError, match="Payment ID is required"):
        payment_gateway.get_payment_status("")


def test_payment_methods():
    """Test payment method enum."""
    assert PaymentMethod.CREDIT_CARD.value == "credit_card"
    assert PaymentMethod.BANK_TRANSFER.value == "bank_transfer"
    assert PaymentMethod.PAYPAL.value == "paypal"
    assert PaymentMethod.CRYPTO.value == "crypto"


def test_payment_statuses():
    """Test payment status enum."""
    assert PaymentStatus.PENDING.value == "pending"
    assert PaymentStatus.COMPLETED.value == "completed"
    assert PaymentStatus.FAILED.value == "failed"
    assert PaymentStatus.REFUNDED.value == "refunded"
