"""
Tests for payment gateway integration.

This module contains tests for payment gateway integration, including
payment processing, subscription lifecycle, and refund handling.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest

from monetization.payment_gateway import (
    PaymentGateway,
    PaymentMethod,
    PaymentProcessor,
    PaymentStatus,
    RefundReason,
    SubscriptionManager,
    SubscriptionStatus,
)


class TestPaymentGateway:
    """Tests for payment gateway integration."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create payment gateway
        self.payment_gateway = PaymentGateway()

        # Create payment processor
        self.payment_processor = PaymentProcessor()

        # Create subscription manager
        self.subscription_manager = SubscriptionManager()

        # Test customer data
        self.test_customers = {
            "customer1": {
                "id": "customer1",
                "name": "Test Customer 1",
                "email": "customer1@example.com",
                "payment_methods": [
                    {
                        "id": "pm_card_visa",
                        "type": PaymentMethod.CREDIT_CARD,
                        "details": {
                            "last4": "4242",
                            "brand": "Visa",
                            "exp_month": 12,
                            "exp_year": 2025,
                        },
                        "is_default": True,
                    }
                ],
            },
            "customer2": {
                "id": "customer2",
                "name": "Test Customer 2",
                "email": "customer2@example.com",
                "payment_methods": [
                    {
                        "id": "pm_bank_account",
                        "type": PaymentMethod.BANK_ACCOUNT,
                        "details": {
                            "last4": "6789",
                            "bank_name": "Test Bank",
                            "account_type": "checking",
                        },
                        "is_default": True,
                    }
                ],
            },
        }

        # Test subscription plans
        self.test_plans = {
            "basic": {
                "id": "plan_basic",
                "name": "Basic Plan",
                "amount": Decimal("10.00"),
                "currency": "USD",
                "interval": "month",
                "features": ["feature1", "feature2"],
            },
            "premium": {
                "id": "plan_premium",
                "name": "Premium Plan",
                "amount": Decimal("50.00"),
                "currency": "USD",
                "interval": "month",
                "features": ["feature1", "feature2", "feature3", "feature4"],
            },
            "enterprise": {
                "id": "plan_enterprise",
                "name": "Enterprise Plan",
                "amount": Decimal("200.00"),
                "currency": "USD",
                "interval": "month",
                "features": [
                    "feature1",
                    "feature2",
                    "feature3",
                    "feature4",
                    "feature5",
                ],
            },
        }

    def test_payment_processing(self):
        """Test payment processing workflows."""
        customer_id = "customer1"
        customer = self.test_customers[customer_id]
        payment_method = customer["payment_methods"][0]

        # Test one-time payment
        payment_amount = Decimal("25.99")
        payment_currency = "USD"
        payment_description = "Test payment"

        # Mock payment processor
        with patch.object(self.payment_processor, "process_payment") as mock_process:
            mock_process.return_value = {
                "success": True,
                "transaction_id": "txn_123456",
                "amount": payment_amount,
                "currency": payment_currency,
                "status": PaymentStatus.COMPLETED,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Process payment
            payment_result = self.payment_gateway.charge(
                customer_id=customer_id,
                amount=payment_amount,
                currency=payment_currency,
                payment_method_id=payment_method["id"],
                description=payment_description,
            )

            # Verify payment result
            assert payment_result["success"] is True
            assert payment_result["transaction_id"] == "txn_123456"
            assert payment_result["amount"] == payment_amount
            assert payment_result["currency"] == payment_currency
            assert payment_result["status"] == PaymentStatus.COMPLETED

            # Verify payment processor was called with correct parameters
            mock_process.assert_called_once()
            call_args = mock_process.call_args[1]
            assert call_args["customer_id"] == customer_id
            assert call_args["amount"] == payment_amount
            assert call_args["currency"] == payment_currency
            assert call_args["payment_method_id"] == payment_method["id"]

        # Test payment failure
        with patch.object(self.payment_processor, "process_payment") as mock_process:
            mock_process.return_value = {
                "success": False,
                "error_code": "card_declined",
                "error_message": "Your card was declined",
                "status": PaymentStatus.FAILED,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Process payment
            payment_result = self.payment_gateway.charge(
                customer_id=customer_id,
                amount=payment_amount,
                currency=payment_currency,
                payment_method_id=payment_method["id"],
                description=payment_description,
            )

            # Verify payment result
            assert payment_result["success"] is False
            assert payment_result["error_code"] == "card_declined"
            assert payment_result["status"] == PaymentStatus.FAILED

        # Test payment with retry
        with patch.object(self.payment_processor, "process_payment") as mock_process:
            # First attempt fails, second succeeds
            mock_process.side_effect = [
                {
                    "success": False,
                    "error_code": "processing_error",
                    "error_message": "Temporary processing error",
                    "status": PaymentStatus.FAILED,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                {
                    "success": True,
                    "transaction_id": "txn_789012",
                    "amount": payment_amount,
                    "currency": payment_currency,
                    "status": PaymentStatus.COMPLETED,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            ]

            # Process payment with retry
            payment_result = self.payment_gateway.charge_with_retry(
                customer_id=customer_id,
                amount=payment_amount,
                currency=payment_currency,
                payment_method_id=payment_method["id"],
                description=payment_description,
                max_retries=3,
                retry_delay=0.1,  # Short delay for testing
            )

            # Verify payment result
            assert payment_result["success"] is True
            assert payment_result["transaction_id"] == "txn_789012"
            assert payment_result["status"] == PaymentStatus.COMPLETED

            # Verify payment processor was called twice
            assert mock_process.call_count == 2

    def test_subscription_lifecycle(self):
        """Test subscription lifecycle (creation, modification, cancellation)."""
        customer_id = "customer1"
        customer = self.test_customers[customer_id]
        payment_method = customer["payment_methods"][0]
        plan = self.test_plans["basic"]

        # Test subscription creation
        with patch.object(
            self.subscription_manager, "create_subscription"
        ) as mock_create:
            mock_create.return_value = {
                "subscription_id": "sub_123456",
                "customer_id": customer_id,
                "plan_id": plan["id"],
                "status": SubscriptionStatus.ACTIVE,
                "current_period_start": datetime.utcnow().isoformat(),
                "current_period_end": (
                    datetime.utcnow() + timedelta(days=30)
                ).isoformat(),
                "payment_method_id": payment_method["id"],
                "created_at": datetime.utcnow().isoformat(),
            }

            # Create subscription
            subscription = self.payment_gateway.create_subscription(
                customer_id=customer_id,
                plan_id=plan["id"],
                payment_method_id=payment_method["id"],
            )

            # Verify subscription
            assert subscription["subscription_id"] == "sub_123456"
            assert subscription["customer_id"] == customer_id
            assert subscription["plan_id"] == plan["id"]
            assert subscription["status"] == SubscriptionStatus.ACTIVE

            # Verify subscription manager was called with correct parameters
            mock_create.assert_called_once()
            call_args = mock_create.call_args[1]
            assert call_args["customer_id"] == customer_id
            assert call_args["plan_id"] == plan["id"]
            assert call_args["payment_method_id"] == payment_method["id"]

        # Test subscription modification
        new_plan = self.test_plans["premium"]

        with patch.object(
            self.subscription_manager, "update_subscription"
        ) as mock_update:
            mock_update.return_value = {
                "subscription_id": "sub_123456",
                "customer_id": customer_id,
                "plan_id": new_plan["id"],
                "status": SubscriptionStatus.ACTIVE,
                "current_period_start": datetime.utcnow().isoformat(),
                "current_period_end": (
                    datetime.utcnow() + timedelta(days=30)
                ).isoformat(),
                "payment_method_id": payment_method["id"],
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Update subscription
            updated_subscription = self.payment_gateway.update_subscription(
                subscription_id="sub_123456", plan_id=new_plan["id"]
            )

            # Verify updated subscription
            assert updated_subscription["subscription_id"] == "sub_123456"
            assert updated_subscription["plan_id"] == new_plan["id"]
            assert updated_subscription["status"] == SubscriptionStatus.ACTIVE

            # Verify subscription manager was called with correct parameters
            mock_update.assert_called_once()
            call_args = mock_update.call_args[1]
            assert call_args["subscription_id"] == "sub_123456"
            assert call_args["plan_id"] == new_plan["id"]

        # Test subscription cancellation
        with patch.object(
            self.subscription_manager, "cancel_subscription"
        ) as mock_cancel:
            mock_cancel.return_value = {
                "subscription_id": "sub_123456",
                "customer_id": customer_id,
                "plan_id": new_plan["id"],
                "status": SubscriptionStatus.CANCELED,
                "canceled_at": datetime.utcnow().isoformat(),
                "cancel_at_period_end": True,
            }

            # Cancel subscription
            canceled_subscription = self.payment_gateway.cancel_subscription(
                subscription_id="sub_123456", cancel_at_period_end=True
            )

            # Verify canceled subscription
            assert canceled_subscription["subscription_id"] == "sub_123456"
            assert canceled_subscription["status"] == SubscriptionStatus.CANCELED
            assert canceled_subscription["cancel_at_period_end"] is True

            # Verify subscription manager was called with correct parameters
            mock_cancel.assert_called_once()
            call_args = mock_cancel.call_args[1]
            assert call_args["subscription_id"] == "sub_123456"
            assert call_args["cancel_at_period_end"] is True

    def test_refund_handling(self):
        """Test refund and credit handling."""
        customer_id = "customer1"
        transaction_id = "txn_123456"
        refund_amount = Decimal("15.99")
        refund_reason = RefundReason.CUSTOMER_REQUEST

        # Test full refund
        with patch.object(self.payment_processor, "process_refund") as mock_refund:
            mock_refund.return_value = {
                "success": True,
                "refund_id": "ref_123456",
                "transaction_id": transaction_id,
                "amount": refund_amount,
                "status": PaymentStatus.REFUNDED,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Process refund
            refund_result = self.payment_gateway.refund(
                transaction_id=transaction_id,
                amount=refund_amount,
                reason=refund_reason,
            )

            # Verify refund result
            assert refund_result["success"] is True
            assert refund_result["refund_id"] == "ref_123456"
            assert refund_result["transaction_id"] == transaction_id
            assert refund_result["amount"] == refund_amount
            assert refund_result["status"] == PaymentStatus.REFUNDED

            # Verify payment processor was called with correct parameters
            mock_refund.assert_called_once()
            call_args = mock_refund.call_args[1]
            assert call_args["transaction_id"] == transaction_id
            assert call_args["amount"] == refund_amount
            assert call_args["reason"] == refund_reason

        # Test partial refund
        partial_amount = Decimal("5.99")

        with patch.object(self.payment_processor, "process_refund") as mock_refund:
            mock_refund.return_value = {
                "success": True,
                "refund_id": "ref_789012",
                "transaction_id": transaction_id,
                "amount": partial_amount,
                "status": PaymentStatus.PARTIALLY_REFUNDED,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Process partial refund
            refund_result = self.payment_gateway.refund(
                transaction_id=transaction_id,
                amount=partial_amount,
                reason=RefundReason.DUPLICATE_PAYMENT,
            )

            # Verify refund result
            assert refund_result["success"] is True
            assert refund_result["refund_id"] == "ref_789012"
            assert refund_result["transaction_id"] == transaction_id
            assert refund_result["amount"] == partial_amount
            assert refund_result["status"] == PaymentStatus.PARTIALLY_REFUNDED

        # Test refund failure
        with patch.object(self.payment_processor, "process_refund") as mock_refund:
            mock_refund.return_value = {
                "success": False,
                "error_code": "refund_failed",
                "error_message": "Refund failed: transaction already refunded",
                "status": PaymentStatus.FAILED,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Process refund
            refund_result = self.payment_gateway.refund(
                transaction_id=transaction_id,
                amount=refund_amount,
                reason=refund_reason,
            )

            # Verify refund result
            assert refund_result["success"] is False
            assert refund_result["error_code"] == "refund_failed"
            assert refund_result["status"] == PaymentStatus.FAILED

        # Test account credit
        credit_amount = Decimal("10.00")
        credit_description = "Goodwill credit"

        with patch.object(self.payment_processor, "add_account_credit") as mock_credit:
            mock_credit.return_value = {
                "success": True,
                "credit_id": "cr_123456",
                "customer_id": customer_id,
                "amount": credit_amount,
                "description": credit_description,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Add account credit
            credit_result = self.payment_gateway.add_credit(
                customer_id=customer_id,
                amount=credit_amount,
                description=credit_description,
            )

            # Verify credit result
            assert credit_result["success"] is True
            assert credit_result["credit_id"] == "cr_123456"
            assert credit_result["customer_id"] == customer_id
            assert credit_result["amount"] == credit_amount
            assert credit_result["description"] == credit_description

            # Verify payment processor was called with correct parameters
            mock_credit.assert_called_once()
            call_args = mock_credit.call_args[1]
            assert call_args["customer_id"] == customer_id
            assert call_args["amount"] == credit_amount
            assert call_args["description"] == credit_description

    def test_payment_failure_scenarios(self):
        """Test payment failure scenarios and retry logic."""
        customer_id = "customer1"
        customer = self.test_customers[customer_id]
        payment_method = customer["payment_methods"][0]
        payment_amount = Decimal("25.99")

        # Test different failure scenarios
        failure_scenarios = [
            {
                "error_code": "card_declined",
                "error_message": "Your card was declined",
                "should_retry": False,
            },
            {
                "error_code": "insufficient_funds",
                "error_message": "Your card has insufficient funds",
                "should_retry": False,
            },
            {
                "error_code": "processing_error",
                "error_message": "An error occurred while processing your card",
                "should_retry": True,
            },
            {
                "error_code": "network_error",
                "error_message": "Network error occurred",
                "should_retry": True,
            },
        ]

        for scenario in failure_scenarios:
            # Mock payment processor
            with patch.object(
                self.payment_processor, "process_payment"
            ) as mock_process:
                mock_process.return_value = {
                    "success": False,
                    "error_code": scenario["error_code"],
                    "error_message": scenario["error_message"],
                    "status": PaymentStatus.FAILED,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                # Process payment with retry logic
                if scenario["should_retry"]:
                    # For retryable errors, mock success on second attempt
                    mock_process.side_effect = [
                        {
                            "success": False,
                            "error_code": scenario["error_code"],
                            "error_message": scenario["error_message"],
                            "status": PaymentStatus.FAILED,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                        {
                            "success": True,
                            "transaction_id": "txn_retry",
                            "amount": payment_amount,
                            "currency": "USD",
                            "status": PaymentStatus.COMPLETED,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    ]

                # Process payment
                payment_result = self.payment_gateway.charge_with_retry(
                    customer_id=customer_id,
                    amount=payment_amount,
                    currency="USD",
                    payment_method_id=payment_method["id"],
                    description="Test payment",
                    max_retries=3 if scenario["should_retry"] else 0,
                    retry_delay=0.1,  # Short delay for testing
                )

                # Verify payment result
                if scenario["should_retry"]:
                    assert payment_result["success"] is True
                    assert payment_result["transaction_id"] == "txn_retry"
                    assert payment_result["status"] == PaymentStatus.COMPLETED
                    assert mock_process.call_count == 2
                else:
                    assert payment_result["success"] is False
                    assert payment_result["error_code"] == scenario["error_code"]
                    assert payment_result["status"] == PaymentStatus.FAILED
                    assert mock_process.call_count == 1


if __name__ == "__main__":
    pytest.main(["-v", "test_payment_gateway.py"])
