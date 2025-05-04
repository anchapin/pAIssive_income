"""
Tests for payment gateway integration.

This module tests the payment gateway integration functionality in the monetization module,
including payment processing, subscription lifecycle, refund handling, 
    and error scenarios.
"""

import os
import shutil
import tempfile
import unittest

from monetization.mock_payment_processor import MockPaymentProcessor
from monetization.transaction import TransactionStatus
from monetization.transaction_manager import TransactionManager

class TestPaymentGatewayIntegration(unittest.TestCase):
    """Test cases for payment gateway integration."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for storage
        self.temp_dir = tempfile.mkdtemp()

        # Create a mock payment processor
        self.processor = MockPaymentProcessor(
            {
                "name": "Test Payment Processor",
                "success_rate": 1.0,  # Always succeed for tests
                "refund_success_rate": 1.0,
                "simulate_network_errors": False,
            }
        )

        # Create a transaction manager
        self.transaction_manager = TransactionManager(
            payment_processor=self.processor,
            storage_dir=os.path.join(self.temp_dir, "transactions"),
        )

        # Create a test customer
        self.customer = self.processor.create_customer(
            email="test @ example.com", name="Test Customer"
        )

        # Create a test payment method
        self.payment_method = self.processor.create_payment_method(
            customer_id=self.customer["id"],
            payment_type="card",
            payment_details={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": 2030,
                "cvc": "123",
            },
        )

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_payment_processing_workflow(self):
        """Test the complete payment processing workflow."""
        # Process a payment
        payment = self.processor.process_payment(
            amount=19.99,
            currency="USD",
            payment_method_id=self.payment_method["id"],
            description="Test payment",
            metadata={"test": True},
        )

        # Verify payment
        self.assertIsNotNone(payment)
        self.assertIn("id", payment)
        self.assertEqual(payment["amount"], 19.99)
        self.assertEqual(payment["currency"], "USD")
        self.assertEqual(payment["status"], "succeeded")

        # Create a transaction
        transaction = self.transaction_manager.create_transaction(
            amount=19.99,
            currency="USD",
            customer_id=self.customer["id"],
            payment_method_id=self.payment_method["id"],
            description="Test transaction",
            metadata={"test": True},
        )

        # Verify transaction
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.amount, 19.99)
        self.assertEqual(transaction.currency, "USD")
        self.assertEqual(transaction.customer_id, self.customer["id"])
        self.assertEqual(transaction.payment_method_id, self.payment_method["id"])
        self.assertEqual(transaction.status, TransactionStatus.PENDING)

        # Process the transaction
        processed_transaction = \
            self.transaction_manager.process_transaction(transaction.id)

        # Verify processed transaction
        self.assertEqual(processed_transaction.status, TransactionStatus.COMPLETED)
        self.assertIsNotNone(processed_transaction.payment_id)

        # Get transaction by ID
        retrieved_transaction = self.transaction_manager.get_transaction(transaction.id)

        # Verify retrieved transaction
        self.assertEqual(retrieved_transaction.id, transaction.id)
        self.assertEqual(retrieved_transaction.status, TransactionStatus.COMPLETED)

    def test_subscription_lifecycle(self):
        """Test subscription lifecycle (creation, modification, cancellation)."""
        # Create a subscription
        subscription = self.processor.create_subscription(
            customer_id=self.customer["id"],
            payment_method_id=self.payment_method["id"],
            plan_id="test_plan",
            quantity=1,
            metadata={"test": True},
        )

        # Verify subscription
        self.assertIsNotNone(subscription)
        self.assertIn("id", subscription)
        self.assertEqual(subscription["customer_id"], self.customer["id"])
        self.assertEqual(subscription["plan_id"], "test_plan")
        self.assertEqual(subscription["status"], "active")

        # Modify subscription
        modified_subscription = self.processor.update_subscription(
            subscription_id=subscription["id"],
            quantity=2,
            metadata={"test": True, "modified": True},
        )

        # Verify modified subscription
        self.assertEqual(modified_subscription["id"], subscription["id"])
        self.assertEqual(modified_subscription["quantity"], 2)
        self.assertEqual(modified_subscription["metadata"]["modified"], True)

        # Cancel subscription
        canceled_subscription = self.processor.cancel_subscription(
            subscription_id=subscription["id"]
        )

        # Verify canceled subscription
        self.assertEqual(canceled_subscription["id"], subscription["id"])
        self.assertEqual(canceled_subscription["status"], "canceled")

    def test_refund_and_credit_handling(self):
        """Test refund and credit handling."""
        # Process a payment
        payment = self.processor.process_payment(
            amount=29.99,
            currency="USD",
            payment_method_id=self.payment_method["id"],
            description="Test payment for refund",
            metadata={"test": True},
        )

        # Verify payment
        self.assertEqual(payment["status"], "succeeded")

        # Process a full refund
        refund = self.processor.process_refund(
            payment_id=payment["id"], amount=29.99, reason="customer_requested"
        )

        # Verify refund
        self.assertIsNotNone(refund)
        self.assertIn("id", refund)
        self.assertEqual(refund["payment_id"], payment["id"])
        self.assertEqual(refund["amount"], 29.99)
        self.assertEqual(refund["status"], "succeeded")

        # Process another payment for partial refund
        payment2 = self.processor.process_payment(
            amount=49.99,
            currency="USD",
            payment_method_id=self.payment_method["id"],
            description="Test payment for partial refund",
            metadata={"test": True},
        )

        # Process a partial refund
        partial_refund = self.processor.process_refund(
            payment_id=payment2["id"], amount=25.00, reason="partial_refund"
        )

        # Verify partial refund
        self.assertEqual(partial_refund["payment_id"], payment2["id"])
        self.assertEqual(partial_refund["amount"], 25.00)
        self.assertEqual(partial_refund["status"], "succeeded")

        # Issue a credit to the customer
        credit = self.processor.issue_credit(
            customer_id=self.customer["id"],
            amount=10.00,
            currency="USD",
            description="Goodwill credit",
            metadata={"test": True},
        )

        # Verify credit
        self.assertIsNotNone(credit)
        self.assertIn("id", credit)
        self.assertEqual(credit["customer_id"], self.customer["id"])
        self.assertEqual(credit["amount"], 10.00)
        self.assertEqual(credit["currency"], "USD")

    def test_payment_failure_scenarios(self):
        """Test payment failure scenarios and retry logic."""
        # Create a processor with a low success rate
        failing_processor = MockPaymentProcessor(
            {
                "name": "Failing Payment Processor",
                "success_rate": 0.0,  # Always fail
                "simulate_network_errors": False,
            }
        )

        # Create a customer
        customer = failing_processor.create_customer(
            email="failing @ example.com", name="Failing Customer"
        )

        # Create a payment method
        payment_method = failing_processor.create_payment_method(
            customer_id=customer["id"],
            payment_type="card",
            payment_details={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": 2030,
                "cvc": "123",
            },
        )

        # Create a transaction manager
        failing_transaction_manager = TransactionManager(
            payment_processor=failing_processor,
            storage_dir=os.path.join(self.temp_dir, "failing_transactions"),
            max_retry_attempts=3,
            retry_delay=1,  # 1 second delay between retries
        )

        # Create a transaction
        transaction = failing_transaction_manager.create_transaction(
            amount=19.99,
            currency="USD",
            customer_id=customer["id"],
            payment_method_id=payment_method["id"],
            description="Failing transaction",
            metadata={"test": True},
        )

        # Process the transaction (should fail)
        with self.assertRaises(Exception):
            failing_transaction_manager.process_transaction(transaction.id)

        # Verify transaction status
        failed_transaction = failing_transaction_manager.get_transaction(transaction.id)
        self.assertEqual(failed_transaction.status, TransactionStatus.FAILED)
        self.assertEqual(failed_transaction.retry_count, 3)  # Should have tried 3 times

        # Test retry logic
        retry_result = failing_transaction_manager.retry_transaction(transaction.id)
        self.assertFalse(retry_result)  # Should return False for failed retry

        # Verify transaction status after retry
        retried_transaction = \
            failing_transaction_manager.get_transaction(transaction.id)
        self.assertEqual(retried_transaction.status, TransactionStatus.FAILED)
        self.assertEqual(retried_transaction.retry_count, 
            4)  # Should have tried 4 times total

        # Now test with a processor that succeeds on retry
        retry_processor = MockPaymentProcessor(
            {
                "name": "Retry Payment Processor",
                "success_rate": 0.0,  # Fail initially
                "simulate_network_errors": False,
            }
        )

        # Create a transaction manager
        retry_transaction_manager = TransactionManager(
            payment_processor=retry_processor,
            storage_dir=os.path.join(self.temp_dir, "retry_transactions"),
            max_retry_attempts=3,
            retry_delay=1,  # 1 second delay between retries
        )

        # Create a customer and payment method
        retry_customer = retry_processor.create_customer(
            email="retry @ example.com", name="Retry Customer"
        )

        retry_payment_method = retry_processor.create_payment_method(
            customer_id=retry_customer["id"],
            payment_type="card",
            payment_details={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": 2030,
                "cvc": "123",
            },
        )

        # Create a transaction
        retry_transaction = retry_transaction_manager.create_transaction(
            amount=19.99,
            currency="USD",
            customer_id=retry_customer["id"],
            payment_method_id=retry_payment_method["id"],
            description="Retry transaction",
            metadata={"test": True},
        )

        # Process the transaction (should fail)
        with self.assertRaises(Exception):
            retry_transaction_manager.process_transaction(retry_transaction.id)

        # Now make the processor succeed
        retry_processor.success_rate = 1.0  # Always succeed now

        # Retry the transaction
        retry_result = retry_transaction_manager.retry_transaction(retry_transaction.id)
        self.assertTrue(retry_result)  # Should return True for successful retry

        # Verify transaction status after successful retry
        successful_transaction = \
            retry_transaction_manager.get_transaction(retry_transaction.id)
        self.assertEqual(successful_transaction.status, TransactionStatus.COMPLETED)

if __name__ == "__main__":
    unittest.main()
