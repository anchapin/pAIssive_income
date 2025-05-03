"""
Tests for payment gateway integration.
"""


import unittest
from datetime import datetime

from monetization.mock_payment_processor import MockPaymentProcessor


class TestPaymentGateway

(unittest.TestCase):
    """Test cases for payment gateway integration."""

def setUp(self):
        """Set up test fixtures."""
        self.processor = MockPaymentProcessor()
        self.customer_id = None
        self.payment_method_id = None
        self.subscription_id = None

def create_test_customer(self):
        """Helper to create a test customer with payment method."""
        customer = self.processor.create_customer(
            email="test@example.com", name="Test Customer"
        )
        self.customer_id = customer["id"]

payment_method = self.processor.create_payment_method(
            customer_id=self.customer_id,
            payment_type="card",
            payment_details={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": datetime.now().year + 1,
                "cvc": "123",
            },
        )
        self.payment_method_id = payment_method["id"]
                    return customer, payment_method

def test_payment_processing_workflow(self):
        """Test complete payment processing workflow."""
        # Create customer and payment method
        customer, payment_method = self.create_test_customer()

# Process a successful payment
        payment = self.processor.process_payment(
            amount=19.99,
            currency="USD",
            payment_method_id=payment_method["id"],
            description="Test payment",
        )
        self.assertEqual(payment["status"], "succeeded")
        self.assertEqual(payment["amount"], 19.99)

# Process a payment with invalid amount
        with self.assertRaises(ValueError):
            self.processor.process_payment(
                amount=-10.0,
                currency="USD",
                payment_method_id=payment_method["id"],
                description="Invalid payment",
            )

# Process a payment with invalid currency
        with self.assertRaises(ValueError):
            self.processor.process_payment(
                amount=19.99,
                currency="INVALID",
                payment_method_id=payment_method["id"],
                description="Invalid currency payment",
            )

def test_subscription_lifecycle(self):
        """Test complete subscription lifecycle."""
        # Create customer and payment method
        customer, payment_method = self.create_test_customer()

# Create a subscription
        subscription = self.processor.create_subscription(
            customer_id=customer["id"],
            plan_id="plan_monthly",
            payment_method_id=payment_method["id"],
            metadata={"type": "test"},
        )
        self.subscription_id = subscription["id"]

self.assertEqual(subscription["status"], "active")
        self.assertIsNotNone(subscription["current_period_end"])

# Update subscription
        updated_subscription = self.processor.update_subscription(
            subscription_id=subscription["id"],
            plan_id="plan_annual",
            metadata={"type": "test_updated"},
        )
        self.assertEqual(updated_subscription["plan_id"], "plan_annual")

# Cancel subscription at period end
        canceled_subscription = self.processor.cancel_subscription(
            subscription_id=subscription["id"], cancel_at_period_end=True
        )
        self.assertTrue(canceled_subscription["cancel_at_period_end"])
        self.assertEqual(canceled_subscription["status"], "active")

# Immediate cancellation
        canceled_subscription = self.processor.cancel_subscription(
            subscription_id=subscription["id"], cancel_at_period_end=False
        )
        self.assertEqual(canceled_subscription["status"], "canceled")

def test_refund_and_credit_handling(self):
        """Test refund and credit handling."""
        # Create customer and payment method
        customer, payment_method = self.create_test_customer()

# Process a payment to refund
        payment = self.processor.process_payment(
            amount=50.00,
            currency="USD",
            payment_method_id=payment_method["id"],
            description="Refundable payment",
        )

# Full refund
        refund = self.processor.refund_payment(
            payment_id=payment["id"], reason="Customer request"
        )
        self.assertEqual(refund["amount"], 50.00)
        self.assertEqual(refund["status"], "succeeded")

# Process another payment for partial refund
        payment = self.processor.process_payment(
            amount=100.00,
            currency="USD",
            payment_method_id=payment_method["id"],
            description="Partial refund payment",
        )

# Partial refund
        partial_refund = self.processor.refund_payment(
            payment_id=payment["id"], amount=25.00, reason="Partial refund request"
        )
        self.assertEqual(partial_refund["amount"], 25.00)
        self.assertEqual(partial_refund["status"], "succeeded")

# Try to refund more than original payment
        with self.assertRaises(ValueError):
            self.processor.refund_payment(payment_id=payment["id"], amount=200.00)

def test_payment_failure_scenarios(self):
        """Test payment failure scenarios and retry logic."""
        # Create customer and payment method
        customer, payment_method = self.create_test_customer()

# Test payment with expired card
        expired_payment_method = self.processor.create_payment_method(
            customer_id=customer["id"],
            payment_type="card",
            payment_details={
                "number": "4242424242424242",
                "exp_month": 1,
                "exp_year": datetime.now().year - 1,  # Expired
                "cvc": "123",
            },
        )

with self.assertRaises(ValueError):
            self.processor.process_payment(
                amount=19.99,
                currency="USD",
                payment_method_id=expired_payment_method["id"],
                description="Payment with expired card",
            )

# Test payment with insufficient funds
        # Note: In mock implementation, we'll consider any amount >= 10000 as triggering insufficient funds
        with self.assertRaises(ValueError):
            self.processor.process_payment(
                amount=10000.00,
                currency="USD",
                payment_method_id=payment_method["id"],
                description="Payment with insufficient funds",
            )

# Test subscription with failed payment
        with self.assertRaises(ValueError):
            self.processor.create_subscription(
                customer_id=customer["id"],
                plan_id="plan_expensive",  # Assumes this plan costs >= 10000
                payment_method_id=payment_method["id"],
            )

def tearDown(self):
        """Clean up test fixtures."""
        # Clean up created resources
        if self.subscription_id:
            try:
                self.processor.cancel_subscription(
                    self.subscription_id, cancel_at_period_end=False
                )
            except Exception:
                pass

if self.payment_method_id:
            try:
                self.processor.delete_payment_method(self.payment_method_id)
            except Exception:
                pass

if self.customer_id:
            try:
                self.processor.delete_customer(self.customer_id)
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()