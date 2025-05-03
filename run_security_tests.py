"""
Script to run webhook security tests.
"""

import sys
import time
import unittest

from api.services.webhook_security import (
    WebhookIPAllowlist,
    WebhookRateLimiter,
    WebhookSignatureVerifier,
)


class TestWebhookIPAllowlist(unittest.TestCase):
    """Tests for the WebhookIPAllowlist class."""
    
    def test_add_ip(self):
        """Test adding an IP address to the allowlist."""
        allowlist = WebhookIPAllowlist()
        
        # Add valid IP addresses
        self.assertTrue(allowlist.add_ip("192.168.1.1"))
        self.assertTrue(allowlist.add_ip("10.0.0.1"))
        self.assertTrue(allowlist.add_ip("2001:db8::1"))
        
        # Add invalid IP address
        self.assertFalse(allowlist.add_ip("not-an-ip"))
        
        # Check allowlisted IPs
        self.assertIn("192.168.1.1", allowlist.allowlisted_ips)
        self.assertIn("10.0.0.1", allowlist.allowlisted_ips)
        self.assertIn("2001:db8::1", allowlist.allowlisted_ips)
        self.assertNotIn("not-an-ip", allowlist.allowlisted_ips)
    
    def test_add_network(self):
        """Test adding an IP network to the allowlist."""
        allowlist = WebhookIPAllowlist()
        
        # Add valid networks
        self.assertTrue(allowlist.add_network("192.168.1.0/24"))
        self.assertTrue(allowlist.add_network("10.0.0.0/8"))
        self.assertTrue(allowlist.add_network("2001:db8::/32"))
        
        # Add invalid network
        self.assertFalse(allowlist.add_network("not-a-network"))
        
        # Check allowlisted networks
        self.assertEqual(len(allowlist.allowlisted_networks), 2)  # IPv4 networks
        self.assertEqual(len(allowlist.allowlisted_networks_v6), 1)  # IPv6 networks
    
    def test_remove_ip(self):
        """Test removing an IP address from the allowlist."""
        allowlist = WebhookIPAllowlist()
        
        # Add IPs
        allowlist.add_ip("192.168.1.1")
        allowlist.add_ip("10.0.0.1")
        
        # Remove IPs
        self.assertTrue(allowlist.remove_ip("192.168.1.1"))
        self.assertTrue(allowlist.remove_ip("10.0.0.1"))
        self.assertFalse(allowlist.remove_ip("192.168.1.2"))  # Not in allowlist
        
        # Check allowlisted IPs
        self.assertNotIn("192.168.1.1", allowlist.allowlisted_ips)
        self.assertNotIn("10.0.0.1", allowlist.allowlisted_ips)
    
    def test_remove_network(self):
        """Test removing an IP network from the allowlist."""
        allowlist = WebhookIPAllowlist()
        
        # Add networks
        allowlist.add_network("192.168.1.0/24")
        allowlist.add_network("10.0.0.0/8")
        allowlist.add_network("2001:db8::/32")
        
        # Remove networks
        self.assertTrue(allowlist.remove_network("192.168.1.0/24"))
        self.assertTrue(allowlist.remove_network("10.0.0.0/8"))
        self.assertTrue(allowlist.remove_network("2001:db8::/32"))
        self.assertFalse(allowlist.remove_network("172.16.0.0/12"))  # Not in allowlist
        
        # Check allowlisted networks
        self.assertEqual(len(allowlist.allowlisted_networks), 0)
        self.assertEqual(len(allowlist.allowlisted_networks_v6), 0)
    
    def test_is_allowed(self):
        """Test checking if an IP address is allowed."""
        allowlist = WebhookIPAllowlist()
        
        # Empty allowlist allows all IPs
        self.assertTrue(allowlist.is_allowed("192.168.1.1"))
        
        # Add specific IPs
        allowlist.add_ip("192.168.1.1")
        allowlist.add_ip("10.0.0.1")
        
        # Add networks
        allowlist.add_network("172.16.0.0/12")
        allowlist.add_network("2001:db8::/32")
        
        # Check allowed IPs
        self.assertTrue(allowlist.is_allowed("192.168.1.1"))  # Directly allowlisted
        self.assertTrue(allowlist.is_allowed("10.0.0.1"))  # Directly allowlisted
        self.assertTrue(allowlist.is_allowed("172.16.1.1"))  # In allowlisted network
        self.assertTrue(allowlist.is_allowed("2001:db8::1234"))  # In allowlisted network
        
        # Check disallowed IPs
        self.assertFalse(allowlist.is_allowed("192.168.1.2"))  # Not allowlisted
        self.assertFalse(allowlist.is_allowed("8.8.8.8"))  # Not allowlisted
        self.assertFalse(allowlist.is_allowed("2001:4860:4860::8888"))  # Not allowlisted
        
        # Check invalid IP
        self.assertFalse(allowlist.is_allowed("not-an-ip"))

class TestWebhookSignatureVerifier(unittest.TestCase):
    """Tests for the WebhookSignatureVerifier class."""
    
    def test_create_signature(self):
        """Test creating a signature."""
        secret = "test-secret"
        payload = '{"event":"test","data":{"id":"123"}}'
        
        signature = WebhookSignatureVerifier.create_signature(secret, payload)
        
        # Signature should be a non-empty string
        self.assertIsInstance(signature, str)
        self.assertGreater(len(signature), 0)
        
        # Same inputs should produce same signature
        signature2 = WebhookSignatureVerifier.create_signature(secret, payload)
        self.assertEqual(signature, signature2)
        
        # Different inputs should produce different signatures
        signature3 = WebhookSignatureVerifier.create_signature(secret, payload + "modified")
        self.assertNotEqual(signature, signature3)
        
        signature4 = WebhookSignatureVerifier.create_signature("different-secret", payload)
        self.assertNotEqual(signature, signature4)
    
    def test_verify_signature(self):
        """Test verifying a signature."""
        secret = "test-secret"
        payload = '{"event":"test","data":{"id":"123"}}'
        
        # Create a valid signature
        signature = WebhookSignatureVerifier.create_signature(secret, payload)
        
        # Verify valid signature
        self.assertTrue(WebhookSignatureVerifier.verify_signature(secret, payload, signature))
        
        # Verify invalid signatures
        self.assertFalse(WebhookSignatureVerifier.verify_signature(secret, payload + "modified", signature))
        self.assertFalse(WebhookSignatureVerifier.verify_signature("different-secret", payload, signature))
        self.assertFalse(WebhookSignatureVerifier.verify_signature(secret, payload, signature + "modified"))
    
    def test_verify_request_signature(self):
        """Test verifying a signature from request headers."""
        secret = "test-secret"
        payload = '{"event":"test","data":{"id":"123"}}'
        
        # Create a valid signature
        signature = WebhookSignatureVerifier.create_signature(secret, payload)
        
        # Create headers with signature
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature
        }
        
        # Verify valid signature
        self.assertTrue(WebhookSignatureVerifier.verify_request_signature(secret, payload, headers))
        
        # Verify with custom header name
        headers_custom = {
            "Content-Type": "application/json",
            "X-Custom-Signature": signature
        }
        self.assertTrue(WebhookSignatureVerifier.verify_request_signature(
            secret, payload, headers_custom, "X-Custom-Signature"
        ))
        
        # Verify with missing signature header
        headers_missing = {
            "Content-Type": "application/json"
        }
        self.assertFalse(WebhookSignatureVerifier.verify_request_signature(secret, payload, headers_missing))
        
        # Verify with invalid signature
        headers_invalid = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": "invalid-signature"
        }
        self.assertFalse(WebhookSignatureVerifier.verify_request_signature(secret, payload, headers_invalid))

class TestWebhookRateLimiter(unittest.TestCase):
    """Tests for the WebhookRateLimiter class."""
    
    def test_is_rate_limited(self):
        """Test checking if a key is rate limited."""
        # Create rate limiter with limit of 3 requests per 1 second
        rate_limiter = WebhookRateLimiter(limit=3, window_seconds=1)
        
        # Initially not rate limited
        self.assertFalse(rate_limiter.is_rate_limited("test-key"))
        
        # Add requests
        rate_limiter.add_request("test-key")
        self.assertFalse(rate_limiter.is_rate_limited("test-key"))
        
        rate_limiter.add_request("test-key")
        self.assertFalse(rate_limiter.is_rate_limited("test-key"))
        
        rate_limiter.add_request("test-key")
        self.assertTrue(rate_limiter.is_rate_limited("test-key"))  # Limit reached
        
        # Different key should not be rate limited
        self.assertFalse(rate_limiter.is_rate_limited("other-key"))
    
    def test_get_remaining_requests(self):
        """Test getting the number of remaining requests."""
        # Create rate limiter with limit of 5 requests per 1 second
        rate_limiter = WebhookRateLimiter(limit=5, window_seconds=1)
        
        # Initially all requests available
        self.assertEqual(rate_limiter.get_remaining_requests("test-key"), 5)
        
        # Add requests
        rate_limiter.add_request("test-key")
        self.assertEqual(rate_limiter.get_remaining_requests("test-key"), 4)
        
        rate_limiter.add_request("test-key")
        self.assertEqual(rate_limiter.get_remaining_requests("test-key"), 3)
        
        # Different key should have full limit
        self.assertEqual(rate_limiter.get_remaining_requests("other-key"), 5)
    
    def test_window_expiration(self):
        """Test that requests outside the time window are not counted."""
        # Create rate limiter with limit of 2 requests per 0.5 seconds
        rate_limiter = WebhookRateLimiter(limit=2, window_seconds=0.5)
        
        # Add requests
        rate_limiter.add_request("test-key")
        rate_limiter.add_request("test-key")
        
        # Should be rate limited now
        self.assertTrue(rate_limiter.is_rate_limited("test-key"))
        
        # Wait for window to expire
        time.sleep(0.6)
        
        # Should not be rate limited anymore
        self.assertFalse(rate_limiter.is_rate_limited("test-key"))
        self.assertEqual(rate_limiter.get_remaining_requests("test-key"), 2)
    
    def test_get_reset_time(self):
        """Test getting the time when the rate limit will reset."""
        # Create rate limiter with limit of 2 requests per 1 second
        rate_limiter = WebhookRateLimiter(limit=2, window_seconds=1)
        
        # Initially no reset time
        self.assertIsNone(rate_limiter.get_reset_time("test-key"))
        
        # Add a request
        current_time = time.time()
        rate_limiter.add_request("test-key")
        
        # Reset time should be approximately 1 second from now
        reset_time = rate_limiter.get_reset_time("test-key")
        self.assertIsNotNone(reset_time)
        self.assertAlmostEqual(reset_time - current_time, 1.0, delta=0.1)  # Within 0.1 seconds of expected

def run_tests():
    """Run the security tests."""
    print("Running webhook security tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestWebhookIPAllowlist))
    test_suite.addTest(unittest.makeSuite(TestWebhookSignatureVerifier))
    test_suite.addTest(unittest.makeSuite(TestWebhookRateLimiter))
    
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
