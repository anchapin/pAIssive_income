"""
Script to run webhook integration tests.
"""

import asyncio
import json
import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from api.schemas.webhook import WebhookDeliveryStatus, WebhookEventType
    WebhookIPAllowlist,
    WebhookRateLimiter,
    WebhookSignatureVerifier,
)

# Import the necessary modules
from api.services.webhook_service import WebhookService

# Test data
TEST_WEBHOOK_ID = "test - webhook - 123"
TEST_WEBHOOK = {
    "id": TEST_WEBHOOK_ID,
    "url": "https://example.com / webhook",
    "events": [WebhookEventType.USER_CREATED, WebhookEventType.PAYMENT_RECEIVED],
    "description": "Test webhook",
    "headers": {"Authorization": "Bearer test - token"},
    "is_active": True,
    "created_at": datetime.now(timezone.utc),
    "last_called_at": None,
    "secret": "test - secret - key",
}

TEST_EVENT = {
    "type": WebhookEventType.USER_CREATED,
    "data": {
        "user_id": "user - 123",
        "username": "testuser",
        "email": "test @ example.com",
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
}

class TestWebhookSecurityIntegration(unittest.TestCase):
    """Integration tests for webhook security features."""

    def test_signature_verification_with_webhook_service(self):
        """Test signature verification with the webhook service."""
        # Create a webhook service
        webhook_service = WebhookService()

        # Create a webhook
        webhook_data = {
            "url": "https://example.com / webhook",
            "events": [WebhookEventType.USER_CREATED],
            "description": "Test webhook",
            "headers": {"Authorization": "Bearer test - token"},
            "is_active": True,
        }

        # Mock the register_webhook method to return a test webhook
        with patch.object(webhook_service, "register_webhook", 
            return_value=TEST_WEBHOOK):
            webhook = asyncio.run(webhook_service.register_webhook(webhook_data))

        # Create a payload
        payload = json.dumps(
            {
                "id": "evt - 123",
                "type": WebhookEventType.USER_CREATED,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "data": {"user_id": "user - 123", "username": "testuser"},
            }
        )

        # Create a signature
        signature = WebhookSignatureVerifier.create_signature(webhook["secret"], 
            payload)

        # Verify the signature
        self.assertTrue(
            WebhookSignatureVerifier.verify_signature(webhook["secret"], payload, 
                signature)
        )

        # Verify with headers
        headers = {"Content - Type": "application / json", 
            "X - Webhook - Signature": signature}
        self.assertTrue(
            WebhookSignatureVerifier.verify_request_signature(webhook["secret"], payload, 
                headers)
        )

    def test_webhook_delivery_with_security(self):
        """Test webhook delivery with security features."""
        # Create a webhook service
        webhook_service = WebhookService()

        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.raise_for_status = MagicMock()

        # Create a mock for httpx.AsyncClient.post
        async def mock_post(url, headers=None, json=None, **kwargs):
            # Verify that the signature header is present
            self.assertIn("X - Webhook - Signature", headers)

            # Verify the signature
            payload = json_dumps(json)
            signature = headers["X - Webhook - Signature"]
            self.assertTrue(
                WebhookSignatureVerifier.verify_signature(
                    TEST_WEBHOOK["secret"], payload, signature
                )
            )

            return mock_response

        # Helper function to match json.dumps behavior in the service
        def json_dumps(obj):
            return json.dumps(obj)

        # Patch the httpx.AsyncClient.post method
        with patch("httpx.AsyncClient.post", mock_post):
            # Patch the get_webhook method to return our test webhook
            with patch.object(webhook_service, "get_webhook", 
                return_value=TEST_WEBHOOK):
                # Deliver an event
                delivery = asyncio.run(
                    webhook_service.deliver_event(
                        webhook_id=TEST_WEBHOOK_ID,
                        event_type=WebhookEventType.USER_CREATED,
                        event_data=TEST_EVENT["data"],
                    )
                )

                # Check delivery status
                self.assertEqual(delivery["status"], WebhookDeliveryStatus.SUCCESS)
                self.assertEqual(len(delivery["attempts"]), 1)
                self.assertEqual(delivery["attempts"][0]["status"], 
                    WebhookDeliveryStatus.SUCCESS)

class TestWebhookRateLimitIntegration(unittest.TestCase):
    """Integration tests for webhook rate limiting."""

    async def _test_webhook_service_with_rate_limiting(self):
        """Test webhook service with rate limiting."""
        # Create services
        webhook_service = WebhookService()
        rate_limiter = WebhookRateLimiter(limit=3, window_seconds=1)

        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.raise_for_status = MagicMock()

        # Patch the httpx.AsyncClient.post method
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            # Patch the get_webhook method to return our test webhook
            with patch.object(webhook_service, "get_webhook", 
                return_value=TEST_WEBHOOK):
                # Make requests up to the limit
                for _ in range(3):
                    # Check if rate limited
                    if rate_limiter.is_rate_limited(TEST_WEBHOOK["url"]):
                        break

                    # Add request to rate limiter
                    rate_limiter.add_request(TEST_WEBHOOK["url"])

                    # Deliver an event
                    await webhook_service.deliver_event(
                        webhook_id=TEST_WEBHOOK_ID,
                        event_type=WebhookEventType.USER_CREATED,
                        event_data=TEST_EVENT["data"],
                    )

                # Next request should be rate limited
                self.assertTrue(rate_limiter.is_rate_limited(TEST_WEBHOOK["url"]))

                # Get remaining requests
                remaining = rate_limiter.get_remaining_requests(TEST_WEBHOOK["url"])
                self.assertEqual(remaining, 0)

                # Get reset time
                reset_time = rate_limiter.get_reset_time(TEST_WEBHOOK["url"])
                self.assertIsNotNone(reset_time)

    def test_webhook_service_with_rate_limiting(self):
        """Run the async test."""
        asyncio.run(self._test_webhook_service_with_rate_limiting())

def run_tests():
    """Run the integration tests."""
    print("Running webhook integration tests...")

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestWebhookSecurityIntegration))
    test_suite.addTest(unittest.makeSuite(TestWebhookRateLimitIntegration))

    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Print summary
    print(f"\nTest Summary:")
    print(f"  Ran {result.testsRun} tests")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")

    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
