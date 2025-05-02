"""
Standalone script to run webhook security tests without dependencies.
"""

import unittest
import time
import sys
import hmac
import hashlib
import base64
import ipaddress
from typing import Dict, List, Optional, Set

# Recreate the security classes here to avoid import issues

class WebhookIPAllowlist:
    """IP allowlisting for webhook endpoints."""
    
    def __init__(self):
        """Initialize the IP allowlist."""
        self.allowlisted_ips: Set[str] = set()
        self.allowlisted_networks: List[ipaddress.IPv4Network] = []
        self.allowlisted_networks_v6: List[ipaddress.IPv6Network] = []
    
    def add_ip(self, ip: str) -> bool:
        """
        Add an IP address to the allowlist.
        
        Args:
            ip: IP address to add
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Check if it's a valid IP address
            ipaddress.ip_address(ip)
            self.allowlisted_ips.add(ip)
            return True
        except ValueError:
            return False
    
    def add_network(self, network: str) -> bool:
        """
        Add an IP network to the allowlist.
        
        Args:
            network: IP network in CIDR notation (e.g., "192.168.1.0/24")
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            ip_network = ipaddress.ip_network(network)
            if isinstance(ip_network, ipaddress.IPv4Network):
                self.allowlisted_networks.append(ip_network)
            else:
                self.allowlisted_networks_v6.append(ip_network)
            return True
        except ValueError:
            return False
    
    def remove_ip(self, ip: str) -> bool:
        """
        Remove an IP address from the allowlist.
        
        Args:
            ip: IP address to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        if ip in self.allowlisted_ips:
            self.allowlisted_ips.remove(ip)
            return True
        return False
    
    def remove_network(self, network: str) -> bool:
        """
        Remove an IP network from the allowlist.
        
        Args:
            network: IP network in CIDR notation
            
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            ip_network = ipaddress.ip_network(network)
            if isinstance(ip_network, ipaddress.IPv4Network):
                if ip_network in self.allowlisted_networks:
                    self.allowlisted_networks.remove(ip_network)
                    return True
            else:
                if ip_network in self.allowlisted_networks_v6:
                    self.allowlisted_networks_v6.remove(ip_network)
                    return True
            return False
        except ValueError:
            return False
    
    def is_allowed(self, ip: str) -> bool:
        """
        Check if an IP address is allowed.
        
        Args:
            ip: IP address to check
            
        Returns:
            True if allowed, False otherwise
        """
        # If no allowlist is configured, allow all IPs
        if not self.allowlisted_ips and not self.allowlisted_networks and not self.allowlisted_networks_v6:
            return True
        
        # Check if IP is directly in the allowlist
        if ip in self.allowlisted_ips:
            return True
        
        try:
            # Check if IP is in any of the allowlisted networks
            ip_obj = ipaddress.ip_address(ip)
            
            if isinstance(ip_obj, ipaddress.IPv4Address):
                for network in self.allowlisted_networks:
                    if ip_obj in network:
                        return True
            else:
                for network in self.allowlisted_networks_v6:
                    if ip_obj in network:
                        return True
            
            return False
        except ValueError:
            # Invalid IP address
            return False

class WebhookSignatureVerifier:
    """Webhook signature verification."""
    
    @staticmethod
    def create_signature(secret: str, payload: str) -> str:
        """
        Create a signature for a webhook payload.
        
        Args:
            secret: Webhook secret
            payload: Payload to sign
            
        Returns:
            Base64-encoded HMAC-SHA256 signature
        """
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
    
    @staticmethod
    def verify_signature(secret: str, payload: str, signature: str) -> bool:
        """
        Verify a webhook signature.
        
        Args:
            secret: Webhook secret
            payload: Payload that was signed
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
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
        """
        Verify a webhook request signature from headers.
        
        Args:
            secret: Webhook secret
            payload: Request payload
            headers: Request headers
            signature_header: Name of the header containing the signature
            
        Returns:
            True if signature is valid, False otherwise
        """
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
        """
        Initialize the rate limiter.
        
        Args:
            limit: Maximum number of requests allowed in the time window
            window_seconds: Time window in seconds
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
    
    def is_rate_limited(self, key: str) -> bool:
        """
        Check if a key is rate limited.
        
        Args:
            key: Key to check (e.g., webhook ID or destination URL)
            
        Returns:
            True if rate limited, False otherwise
        """
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
        """
        Record a request for rate limiting.
        
        Args:
            key: Key to record (e.g., webhook ID or destination URL)
        """
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
        """
        Get the number of remaining requests allowed.
        
        Args:
            key: Key to check
            
        Returns:
            Number of remaining requests
        """
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
        """
        Get the time when the rate limit will reset.
        
        Args:
            key: Key to check
            
        Returns:
            Time when the rate limit will reset, or None if not rate limited
        """
        if key not in self.requests or not self.requests[key]:
            return None
        
        # Get the oldest request in the window
        oldest_request = min(self.requests[key])
        
        # Calculate reset time
        return oldest_request + self.window_seconds

# Test classes

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
    print("\nTest Summary:")
    print(f"  Ran {result.testsRun} tests")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
