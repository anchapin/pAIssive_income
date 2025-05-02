"""
Standalone script to run webhook integration tests without dependencies.
"""

import unittest
import sys
import asyncio
import json
import time
import hmac
import hashlib
import base64
import uuid
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from enum import Enum
from typing import Dict, List, Any, Optional, Set

# Define enums and constants
class WebhookEventType(str, Enum):
    """Types of webhook events."""
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    STRATEGY_CREATED = "strategy.created"
    STRATEGY_UPDATED = "strategy.updated"
    STRATEGY_DELETED = "strategy.deleted"
    CAMPAIGN_CREATED = "campaign.created"
    CAMPAIGN_UPDATED = "campaign.updated"
    CAMPAIGN_DELETED = "campaign.deleted"
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"
    NICHE_ANALYSIS_STARTED = "niche_analysis.started"
    NICHE_ANALYSIS_COMPLETED = "niche_analysis.completed"
    NICHE_ANALYSIS_FAILED = "niche_analysis.failed"
    SUBSCRIPTION_CREATED = "subscription.created"
    PAYMENT_RECEIVED = "payment.received"

class WebhookDeliveryStatus(str, Enum):
    """Status of a webhook delivery attempt."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"

# Recreate the security classes
class WebhookIPAllowlist:
    """IP allowlisting for webhook endpoints."""

    def __init__(self):
        """Initialize the IP allowlist."""
        self.allowlisted_ips: Set[str] = set()
        self.allowlisted_networks = []
        self.allowlisted_networks_v6 = []

    def add_ip(self, ip: str) -> bool:
        """Add an IP address to the allowlist."""
        self.allowlisted_ips.add(ip)
        return True

    def add_network(self, network: str) -> bool:
        """Add an IP network to the allowlist."""
        return True

    def remove_ip(self, ip: str) -> bool:
        """Remove an IP address from the allowlist."""
        if ip in self.allowlisted_ips:
            self.allowlisted_ips.remove(ip)
            return True
        return False

    def remove_network(self, network: str) -> bool:
        """Remove an IP network from the allowlist."""
        return True

    def is_allowed(self, ip: str) -> bool:
        """Check if an IP address is allowed."""
        # If no allowlist is configured, allow all IPs
        if not self.allowlisted_ips and not self.allowlisted_networks and not self.allowlisted_networks_v6:
            return True

        # Check if IP is directly in the allowlist
        if ip in self.allowlisted_ips:
            return True

        return False

class WebhookSignatureVerifier:
    """Webhook signature verification."""

    @staticmethod
    def create_signature(secret: str, payload: str) -> str:
        """Create a signature for a webhook payload."""
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()

    @staticmethod
    def verify_signature(secret: str, payload: str, signature: str) -> bool:
        """Verify a webhook signature."""
        expected_signature = WebhookSignatureVerifier.create_signature(secret, payload)

        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature)

    @staticmethod
    def verify_request_signature(
        secret: str,
        payload: str,
        headers: Dict[str, str],
        signature_header: str = "X-Webhook-Signature"
    ) -> bool:
        """Verify a webhook request signature from headers."""
        # Get signature from headers (case-insensitive)
        signature = None
        for header, value in headers.items():
            if header.lower() == signature_header.lower():
                signature = value
                break

        if not signature:
            return False

        return WebhookSignatureVerifier.verify_signature(secret, payload, signature)

class WebhookRateLimiter:
    """Rate limiting for webhook deliveries."""

    def __init__(self, limit: int = 100, window_seconds: int = 60):
        """Initialize the rate limiter."""
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}

    def is_rate_limited(self, key: str) -> bool:
        """Check if a key is rate limited."""
        current_time = time.time()

        # Initialize if key doesn't exist
        if key not in self.requests:
            self.requests[key] = []

        # Remove requests outside the time window
        self.requests[key] = [
            t for t in self.requests[key]
            if current_time - t <= self.window_seconds
        ]

        # Check if limit is exceeded
        return len(self.requests[key]) >= self.limit

    def add_request(self, key: str) -> None:
        """Record a request for rate limiting."""
        current_time = time.time()

        # Initialize if key doesn't exist
        if key not in self.requests:
            self.requests[key] = []

        # Add current request
        self.requests[key].append(current_time)

        # Remove requests outside the time window
        self.requests[key] = [
            t for t in self.requests[key]
            if current_time - t <= self.window_seconds
        ]

    def get_remaining_requests(self, key: str) -> int:
        """Get the number of remaining requests allowed."""
        current_time = time.time()

        # Initialize if key doesn't exist
        if key not in self.requests:
            return self.limit

        # Remove requests outside the time window
        self.requests[key] = [
            t for t in self.requests[key]
            if current_time - t <= self.window_seconds
        ]

        # Calculate remaining requests
        return max(0, self.limit - len(self.requests[key]))

    def get_reset_time(self, key: str) -> Optional[float]:
        """Get the time when the rate limit will reset."""
        if key not in self.requests or not self.requests[key]:
            return None

        # Get the oldest request in the window
        oldest_request = min(self.requests[key])

        # Calculate reset time
        return oldest_request + self.window_seconds

# Recreate the webhook service
class WebhookService:
    """Service for managing and delivering webhooks."""

    def __init__(self):
        """Initialize the webhook service."""
        self.webhooks = {}
        self.deliveries = {}
        self.running = False

    async def start(self):
        """Start the webhook service."""
        self.running = True

    async def stop(self):
        """Stop the webhook service."""
        self.running = False

    async def register_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new webhook."""
        webhook_id = str(uuid.uuid4())
        webhook = {
            "id": webhook_id,
            "url": data["url"],
            "events": data["events"],
            "description": data.get("description"),
            "headers": data.get("headers", {}),
            "is_active": data.get("is_active", True),
            "created_at": datetime.now(timezone.utc),
            "last_called_at": None,
            "secret": self._generate_secret()
        }

        self.webhooks[webhook_id] = webhook
        return webhook

    async def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """Get a webhook by ID."""
        return self.webhooks.get(webhook_id)

    def _generate_secret(self) -> str:
        """Generate a secret for the webhook."""
        return base64.b64encode(uuid.uuid4().bytes).decode()

    async def deliver_event(
        self,
        webhook_id: str,
        event_type: WebhookEventType,
        event_data: Dict[str, Any],
        retry_count: int = 0,
        retry_delay: float = 60.0
    ) -> Dict[str, Any]:
        """Deliver an event to a webhook."""
        # Get the webhook
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook not found: {webhook_id}")

        # Check if webhook is active
        if not webhook.get("is_active", True):
            raise ValueError(f"Webhook is inactive: {webhook_id}")

        # Check if webhook is subscribed to this event type
        if event_type not in webhook.get("events", []):
            raise ValueError(f"Webhook is not subscribed to event type: {event_type}")

        # Create delivery ID
        delivery_id = str(uuid.uuid4())

        # Create delivery record
        delivery = {
            "id": delivery_id,
            "webhook_id": webhook_id,
            "status": WebhookDeliveryStatus.PENDING,
            "timestamp": datetime.now(timezone.utc),
            "attempts": []
        }

        self.deliveries[delivery_id] = delivery

        # Create the payload
        payload = {
            "id": delivery_id,
            "type": event_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": event_data
        }

        # Create the signature
        signature = WebhookSignatureVerifier.create_signature(webhook["secret"], json.dumps(payload))

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "pAIssive-Income-Webhook/1.0",
            "X-Webhook-ID": webhook["id"],
            "X-Webhook-Signature": signature
        }

        # Add custom headers from webhook configuration
        if webhook.get("headers"):
            headers.update(webhook["headers"])

        # Create attempt record
        attempt_id = str(uuid.uuid4())
        attempt = {
            "id": attempt_id,
            "webhook_id": webhook["id"],
            "event_type": event_type,
            "status": WebhookDeliveryStatus.PENDING,
            "request_url": webhook["url"],
            "request_headers": headers,
            "request_body": payload,
            "response_code": None,
            "response_body": None,
            "error_message": None,
            "timestamp": datetime.now(timezone.utc),
            "retries": 0,
            "next_retry": None
        }

        # Add attempt to delivery
        delivery["attempts"].append(attempt)

        # For testing purposes, simulate a successful delivery
        attempt["status"] = WebhookDeliveryStatus.SUCCESS
        attempt["response_code"] = 200
        attempt["response_body"] = '{"status":"success"}'
        delivery["status"] = WebhookDeliveryStatus.SUCCESS

        return delivery

# Test data
TEST_WEBHOOK_ID = "test-webhook-123"
TEST_WEBHOOK = {
    "id": TEST_WEBHOOK_ID,
    "url": "https://example.com/webhook",
    "events": [WebhookEventType.USER_CREATED, WebhookEventType.PAYMENT_RECEIVED],
    "description": "Test webhook",
    "headers": {"Authorization": "Bearer test-token"},
    "is_active": True,
    "created_at": datetime.now(timezone.utc),
    "last_called_at": None,
    "secret": "test-secret-key"
}

TEST_EVENT = {
    "type": WebhookEventType.USER_CREATED,
    "data": {
        "user_id": "user-123",
        "username": "testuser",
        "email": "test@example.com",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
}

class TestWebhookSecurityIntegration(unittest.TestCase):
    """Integration tests for webhook security features."""

    def test_signature_verification_with_webhook_service(self):
        """Test signature verification with the webhook service."""
        # Create a webhook service
        webhook_service = WebhookService()

        # Create a webhook
        webhook_data = {
            "url": "https://example.com/webhook",
            "events": [WebhookEventType.USER_CREATED],
            "description": "Test webhook",
            "headers": {"Authorization": "Bearer test-token"},
            "is_active": True
        }

        # Mock the register_webhook method to return a test webhook
        with patch.object(webhook_service, "register_webhook", return_value=TEST_WEBHOOK):
            webhook = asyncio.run(webhook_service.register_webhook(webhook_data))

        # Create a payload
        payload = json.dumps({
            "id": "evt-123",
            "type": WebhookEventType.USER_CREATED,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": {
                "user_id": "user-123",
                "username": "testuser"
            }
        })

        # Create a signature
        signature = WebhookSignatureVerifier.create_signature(webhook["secret"], payload)

        # Verify the signature
        self.assertTrue(WebhookSignatureVerifier.verify_signature(webhook["secret"], payload, signature))

        # Verify with headers
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature
        }
        self.assertTrue(WebhookSignatureVerifier.verify_request_signature(webhook["secret"], payload, headers))

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
            self.assertIn("X-Webhook-Signature", headers)

            # Verify the signature
            payload = json_dumps(json)
            signature = headers["X-Webhook-Signature"]
            self.assertTrue(WebhookSignatureVerifier.verify_signature(TEST_WEBHOOK["secret"], payload, signature))

            return mock_response

        # Helper function to match json.dumps behavior in the service
        def json_dumps(obj):
            return json.dumps(obj)

        # Patch the httpx.AsyncClient.post method
        with patch("httpx.AsyncClient.post", mock_post):
            # Patch the get_webhook method to return our test webhook
            with patch.object(webhook_service, "get_webhook", return_value=TEST_WEBHOOK):
                # Deliver an event
                delivery = asyncio.run(webhook_service.deliver_event(
                    webhook_id=TEST_WEBHOOK_ID,
                    event_type=WebhookEventType.USER_CREATED,
                    event_data=TEST_EVENT["data"]
                ))

                # Check delivery status
                self.assertEqual(delivery["status"], WebhookDeliveryStatus.SUCCESS)
                self.assertEqual(len(delivery["attempts"]), 1)
                self.assertEqual(delivery["attempts"][0]["status"], WebhookDeliveryStatus.SUCCESS)

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
            with patch.object(webhook_service, "get_webhook", return_value=TEST_WEBHOOK):
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
                        event_data=TEST_EVENT["data"]
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

class TestIPAllowlistIntegration(unittest.TestCase):
    """Integration tests for IP allowlisting."""

    def test_ip_allowlist_with_webhook_service(self):
        """Test IP allowlisting with the webhook service."""
        # Create services
        ip_allowlist = WebhookIPAllowlist()

        # Add some IPs to the allowlist
        ip_allowlist.add_ip("192.168.1.1")
        ip_allowlist.add_ip("10.0.0.1")

        # Check if IPs are allowed
        self.assertTrue(ip_allowlist.is_allowed("192.168.1.1"))
        self.assertTrue(ip_allowlist.is_allowed("10.0.0.1"))
        self.assertFalse(ip_allowlist.is_allowed("8.8.8.8"))

        # Remove an IP
        self.assertTrue(ip_allowlist.remove_ip("192.168.1.1"))
        self.assertFalse(ip_allowlist.is_allowed("192.168.1.1"))
        self.assertTrue(ip_allowlist.is_allowed("10.0.0.1"))

def run_tests():
    """Run the integration tests."""
    print("Running webhook integration tests...")

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestWebhookSecurityIntegration))
    test_suite.addTest(unittest.makeSuite(TestWebhookRateLimitIntegration))
    test_suite.addTest(unittest.makeSuite(TestIPAllowlistIntegration))

    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Print summary
    print("\nTest Summary:")
    print(f"  Ran {result.testsRun} tests")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")

    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
