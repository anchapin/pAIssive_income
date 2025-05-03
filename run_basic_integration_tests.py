"""
Basic integration tests for webhook security features.
"""

import base64
import hashlib
import hmac
import json
import sys
import time
import unittest
from typing import Any, Dict, List, Optional, Set


class WebhookSignatureVerifier:
    """Webhook signature verification."""

    @staticmethod
    def create_signature(secret: str, payload: str) -> str:
        """Create a signature for a webhook payload."""
        signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
        return base64.b64encode(signature).decode()

    @staticmethod
    def verify_signature(secret: str, payload: str, signature: str) -> bool:
        """Verify a webhook signature."""
        expected_signature = WebhookSignatureVerifier.create_signature(secret, payload)

        # Use constant - time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature)

    @staticmethod
    def verify_request_signature(
        secret: str,
        payload: str,
        headers: Dict[str, str],
        signature_header: str = "X - Webhook - Signature",
    ) -> bool:
        """Verify a webhook request signature from headers."""
        # Get signature from headers (case - insensitive)
        signature = None
        for header, value in headers.items():
            if header.lower() == signature_header.lower():
                signature = value
                break

        if not signature:
            return False

        return WebhookSignatureVerifier.verify_signature(secret, payload, signature)


class WebhookIPAllowlist:
    """IP allowlisting for webhook endpoints."""

    def __init__(self):
        """Initialize the IP allowlist."""
        self.allowlisted_ips: Set[str] = set()

    def add_ip(self, ip: str) -> bool:
        """Add an IP address to the allowlist."""
        self.allowlisted_ips.add(ip)
        return True

    def remove_ip(self, ip: str) -> bool:
        """Remove an IP address from the allowlist."""
        if ip in self.allowlisted_ips:
            self.allowlisted_ips.remove(ip)
            return True
        return False

    def is_allowed(self, ip: str) -> bool:
        """Check if an IP address is allowed."""
        # If no allowlist is configured, allow all IPs
        if not self.allowlisted_ips:
            return True

        # Check if IP is directly in the allowlist
        if ip in self.allowlisted_ips:
            return True

        return False


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
            t for t in self.requests[key] if current_time - t <= self.window_seconds
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
            t for t in self.requests[key] if current_time - t <= self.window_seconds
        ]

    def get_remaining_requests(self, key: str) -> int:
        """Get the number of remaining requests allowed."""
        current_time = time.time()

        # Initialize if key doesn't exist
        if key not in self.requests:
            return self.limit

        # Remove requests outside the time window
        self.requests[key] = [
            t for t in self.requests[key] if current_time - t <= self.window_seconds
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


class TestWebhookSecurityIntegration(unittest.TestCase):
    """Integration tests for webhook security features."""

    def test_signature_verification(self):
        """Test signature verification."""
        # Create a secret
        secret = "test - secret - key"

        # Create a payload
        payload = json.dumps(
            {
                "id": "evt - 123",
                "type": "user.created",
                "created_at": "2025 - 04 - 30T21:30:00Z",
                "data": {"user_id": "user - 123", "username": "testuser"},
            }
        )

        # Create a signature
        signature = WebhookSignatureVerifier.create_signature(secret, payload)

        # Verify the signature
        self.assertTrue(WebhookSignatureVerifier.verify_signature(secret, payload, 
            signature))

        # Verify with headers
        headers = {"Content - Type": "application / json", 
            "X - Webhook - Signature": signature}
        self.assertTrue(WebhookSignatureVerifier.verify_request_signature(secret, 
            payload, headers))

        # Test invalid signature
        invalid_signature = WebhookSignatureVerifier.create_signature("wrong - secret", 
            payload)
        self.assertFalse(
            WebhookSignatureVerifier.verify_signature(secret, payload, 
                invalid_signature)
        )

        # Test invalid payload
        modified_payload = payload + "modified"
        self.assertFalse(
            WebhookSignatureVerifier.verify_signature(secret, modified_payload, 
                signature)
        )

    def test_ip_allowlist(self):
        """Test IP allowlisting."""
        # Create an IP allowlist
        ip_allowlist = WebhookIPAllowlist()

        # Initially all IPs are allowed
        self.assertTrue(ip_allowlist.is_allowed("192.168.1.1"))

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

    def test_rate_limiting(self):
        """Test rate limiting."""
        # Create a rate limiter
        rate_limiter = WebhookRateLimiter(limit=3, window_seconds=1)

        # Initially not rate limited
        self.assertFalse(rate_limiter.is_rate_limited("test - key"))
        self.assertEqual(rate_limiter.get_remaining_requests("test - key"), 3)

        # Add requests
        rate_limiter.add_request("test - key")
        self.assertFalse(rate_limiter.is_rate_limited("test - key"))
        self.assertEqual(rate_limiter.get_remaining_requests("test - key"), 2)

        rate_limiter.add_request("test - key")
        self.assertFalse(rate_limiter.is_rate_limited("test - key"))
        self.assertEqual(rate_limiter.get_remaining_requests("test - key"), 1)

        rate_limiter.add_request("test - key")
        self.assertTrue(rate_limiter.is_rate_limited("test - key"))
        self.assertEqual(rate_limiter.get_remaining_requests("test - key"), 0)

        # Different key should not be rate limited
        self.assertFalse(rate_limiter.is_rate_limited("other - key"))
        self.assertEqual(rate_limiter.get_remaining_requests("other - key"), 3)

        # Get reset time
        reset_time = rate_limiter.get_reset_time("test - key")
        self.assertIsNotNone(reset_time)

        # Wait for the rate limit to reset
        time.sleep(1.1)

        # Should not be rate limited anymore
        self.assertFalse(rate_limiter.is_rate_limited("test - key"))
        self.assertEqual(rate_limiter.get_remaining_requests("test - key"), 3)

    def test_security_integration(self):
        """Test integration of security features."""
        # Create security components
        ip_allowlist = WebhookIPAllowlist()
        rate_limiter = WebhookRateLimiter(limit=3, window_seconds=1)

        # Add an IP to the allowlist
        ip_allowlist.add_ip("192.168.1.1")

        # Check if request is allowed and not rate limited
        client_ip = "192.168.1.1"
        request_key = f"{client_ip}:/webhooks / test"

        # Check IP allowlist
        is_allowed = ip_allowlist.is_allowed(client_ip)
        self.assertTrue(is_allowed)

        # Check rate limit
        is_rate_limited = rate_limiter.is_rate_limited(request_key)
        self.assertFalse(is_rate_limited)

        # Add requests up to the limit
        for _ in range(3):
            rate_limiter.add_request(request_key)

        # Should be rate limited now
        is_rate_limited = rate_limiter.is_rate_limited(request_key)
        self.assertTrue(is_rate_limited)

        # Create a payload and signature
        secret = "test - secret - key"
        payload = json.dumps({"test": "data"})
        signature = WebhookSignatureVerifier.create_signature(secret, payload)

        # Create headers
        headers = {"Content - Type": "application / json", 
            "X - Webhook - Signature": signature}

        # Verify signature
        is_valid = WebhookSignatureVerifier.verify_request_signature(secret, payload, 
            headers)
        self.assertTrue(is_valid)

        # Simulate a complete request check
        can_proceed = (
            ip_allowlist.is_allowed(client_ip)
            and not rate_limiter.is_rate_limited(request_key)
            and WebhookSignatureVerifier.verify_request_signature(secret, payload, 
                headers)
        )

        # Should not proceed due to rate limiting
        self.assertFalse(can_proceed)

        # Wait for rate limit to reset
        time.sleep(1.1)

        # Should be able to proceed now
        can_proceed = (
            ip_allowlist.is_allowed(client_ip)
            and not rate_limiter.is_rate_limited(request_key)
            and WebhookSignatureVerifier.verify_request_signature(secret, payload, 
                headers)
        )

        self.assertTrue(can_proceed)


def run_tests():
    """Run the integration tests."""
    print("Running basic webhook integration tests...")

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    loader = unittest.TestLoader()
    test_suite.addTest(loader.loadTestsFromTestCase(TestWebhookSecurityIntegration))

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
