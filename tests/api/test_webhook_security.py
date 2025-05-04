"""
"""
Tests for webhook security features.
Tests for webhook security features.


This module tests the security enhancements for the webhook system:
    This module tests the security enhancements for the webhook system:
    1. IP allowlisting
    1. IP allowlisting
    2. Webhook signature verification
    2. Webhook signature verification
    3. Rate limiting
    3. Rate limiting
    """
    """


    import time
    import time


    from api.services.webhook_security import (WebhookIPAllowlist,
    from api.services.webhook_security import (WebhookIPAllowlist,
    WebhookRateLimiter,
    WebhookRateLimiter,
    WebhookSignatureVerifier)
    WebhookSignatureVerifier)




    class TestWebhookIPAllowlist:
    class TestWebhookIPAllowlist:
    """Tests for the WebhookIPAllowlist class."""

    def test_add_ip(self):
    """Test adding an IP address to the allowlist."""
    allowlist = WebhookIPAllowlist()

    # Add valid IP addresses
    assert allowlist.add_ip("192.168.1.1") is True
    assert allowlist.add_ip("10.0.0.1") is True
    assert allowlist.add_ip("2001:db8::1") is True

    # Add invalid IP address
    assert allowlist.add_ip("not-an-ip") is False

    # Check allowlisted IPs
    assert "192.168.1.1" in allowlist.allowlisted_ips
    assert "10.0.0.1" in allowlist.allowlisted_ips
    assert "2001:db8::1" in allowlist.allowlisted_ips
    assert "not-an-ip" not in allowlist.allowlisted_ips

    def test_add_network(self):
    """Test adding an IP network to the allowlist."""
    allowlist = WebhookIPAllowlist()

    # Add valid networks
    assert allowlist.add_network("192.168.1.0/24") is True
    assert allowlist.add_network("10.0.0.0/8") is True
    assert allowlist.add_network("2001:db8::/32") is True

    # Add invalid network
    assert allowlist.add_network("not-a-network") is False

    # Check allowlisted networks
    assert len(allowlist.allowlisted_networks) == 2  # IPv4 networks
    assert len(allowlist.allowlisted_networks_v6) == 1  # IPv6 networks

    def test_remove_ip(self):
    """Test removing an IP address from the allowlist."""
    allowlist = WebhookIPAllowlist()

    # Add IPs
    allowlist.add_ip("192.168.1.1")
    allowlist.add_ip("10.0.0.1")

    # Remove IPs
    assert allowlist.remove_ip("192.168.1.1") is True
    assert allowlist.remove_ip("10.0.0.1") is True
    assert allowlist.remove_ip("192.168.1.2") is False  # Not in allowlist

    # Check allowlisted IPs
    assert "192.168.1.1" not in allowlist.allowlisted_ips
    assert "10.0.0.1" not in allowlist.allowlisted_ips

    def test_remove_network(self):
    """Test removing an IP network from the allowlist."""
    allowlist = WebhookIPAllowlist()

    # Add networks
    allowlist.add_network("192.168.1.0/24")
    allowlist.add_network("10.0.0.0/8")
    allowlist.add_network("2001:db8::/32")

    # Remove networks
    assert allowlist.remove_network("192.168.1.0/24") is True
    assert allowlist.remove_network("10.0.0.0/8") is True
    assert allowlist.remove_network("2001:db8::/32") is True
    assert allowlist.remove_network("172.16.0.0/12") is False  # Not in allowlist

    # Check allowlisted networks
    assert len(allowlist.allowlisted_networks) == 0
    assert len(allowlist.allowlisted_networks_v6) == 0

    def test_is_allowed(self):
    """Test checking if an IP address is allowed."""
    allowlist = WebhookIPAllowlist()

    # Empty allowlist allows all IPs
    assert allowlist.is_allowed("192.168.1.1") is True

    # Add specific IPs
    allowlist.add_ip("192.168.1.1")
    allowlist.add_ip("10.0.0.1")

    # Add networks
    allowlist.add_network("172.16.0.0/12")
    allowlist.add_network("2001:db8::/32")

    # Check allowed IPs
    assert allowlist.is_allowed("192.168.1.1") is True  # Directly allowlisted
    assert allowlist.is_allowed("10.0.0.1") is True  # Directly allowlisted
    assert allowlist.is_allowed("172.16.1.1") is True  # In allowlisted network
    assert allowlist.is_allowed("2001:db8::1234") is True  # In allowlisted network

    # Check disallowed IPs
    assert allowlist.is_allowed("192.168.1.2") is False  # Not allowlisted
    assert allowlist.is_allowed("8.8.8.8") is False  # Not allowlisted
    assert allowlist.is_allowed("2001:4860:4860::8888") is False  # Not allowlisted

    # Check invalid IP
    assert allowlist.is_allowed("not-an-ip") is False


    class TestWebhookSignatureVerifier:

    def test_create_signature(self):
    """Test creating a signature."""
    secret = "test-secret"
    payload = '{"event":"test","data":{"id":"123"}}'

    signature = WebhookSignatureVerifier.create_signature(secret, payload)

    # Signature should be a non-empty string
    assert isinstance(signature, str)
    assert len(signature) > 0

    # Same inputs should produce same signature
    signature2 = WebhookSignatureVerifier.create_signature(secret, payload)
    assert signature == signature2

    # Different inputs should produce different signatures
    signature3 = WebhookSignatureVerifier.create_signature(
    secret, payload + "modified"
    )
    assert signature != signature3

    signature4 = WebhookSignatureVerifier.create_signature(
    "different-secret", payload
    )
    assert signature != signature4

    def test_verify_signature(self):
    """Test verifying a signature."""
    secret = "test-secret"
    payload = '{"event":"test","data":{"id":"123"}}'

    # Create a valid signature
    signature = WebhookSignatureVerifier.create_signature(secret, payload)

    # Verify valid signature
    assert (
    WebhookSignatureVerifier.verify_signature(secret, payload, signature)
    is True
    )

    # Verify invalid signatures
    assert (
    WebhookSignatureVerifier.verify_signature(
    secret, payload + "modified", signature
    )
    is False
    )
    assert (
    WebhookSignatureVerifier.verify_signature(
    "different-secret", payload, signature
    )
    is False
    )
    assert (
    WebhookSignatureVerifier.verify_signature(
    secret, payload, signature + "modified"
    )
    is False
    )

    def test_verify_request_signature(self):
    """Test verifying a signature from request headers."""
    secret = "test-secret"
    payload = '{"event":"test","data":{"id":"123"}}'

    # Create a valid signature
    signature = WebhookSignatureVerifier.create_signature(secret, payload)

    # Create headers with signature
    headers = {"Content-Type": "application/json", "X-Webhook-Signature": signature}

    # Verify valid signature
    assert (
    WebhookSignatureVerifier.verify_request_signature(secret, payload, headers)
    is True
    )

    # Verify with custom header name
    headers_custom = {
    "Content-Type": "application/json",
    "X-Custom-Signature": signature,
    }
    assert (
    WebhookSignatureVerifier.verify_request_signature(
    secret, payload, headers_custom, "X-Custom-Signature"
    )
    is True
    )

    # Verify with missing signature header
    headers_missing = {"Content-Type": "application/json"}
    assert (
    WebhookSignatureVerifier.verify_request_signature(
    secret, payload, headers_missing
    )
    is False
    )

    # Verify with invalid signature
    headers_invalid = {
    "Content-Type": "application/json",
    "X-Webhook-Signature": "invalid-signature",
    }
    assert (
    WebhookSignatureVerifier.verify_request_signature(
    secret, payload, headers_invalid
    )
    is False
    )


    class TestWebhookRateLimiter:

    def test_is_rate_limited(self):
    """Test checking if a key is rate limited."""
    # Create rate limiter with limit of 3 requests per 1 second
    rate_limiter = WebhookRateLimiter(limit=3, window_seconds=1)

    # Initially not rate limited
    assert rate_limiter.is_rate_limited("test-key") is False

    # Add requests
    rate_limiter.add_request("test-key")
    assert rate_limiter.is_rate_limited("test-key") is False

    rate_limiter.add_request("test-key")
    assert rate_limiter.is_rate_limited("test-key") is False

    rate_limiter.add_request("test-key")
    assert rate_limiter.is_rate_limited("test-key") is True  # Limit reached

    # Different key should not be rate limited
    assert rate_limiter.is_rate_limited("other-key") is False

    def test_get_remaining_requests(self):
    """Test getting the number of remaining requests."""
    # Create rate limiter with limit of 5 requests per 1 second
    rate_limiter = WebhookRateLimiter(limit=5, window_seconds=1)

    # Initially all requests available
    assert rate_limiter.get_remaining_requests("test-key") == 5

    # Add requests
    rate_limiter.add_request("test-key")
    assert rate_limiter.get_remaining_requests("test-key") == 4

    rate_limiter.add_request("test-key")
    assert rate_limiter.get_remaining_requests("test-key") == 3

    # Different key should have full limit
    assert rate_limiter.get_remaining_requests("other-key") == 5

    def test_window_expiration(self):
    """Test that requests outside the time window are not counted."""
    # Create rate limiter with limit of 2 requests per 0.5 seconds
    rate_limiter = WebhookRateLimiter(limit=2, window_seconds=0.5)

    # Add requests
    rate_limiter.add_request("test-key")
    rate_limiter.add_request("test-key")

    # Should be rate limited now
    assert rate_limiter.is_rate_limited("test-key") is True

    # Wait for window to expire
    time.sleep(0.6)

    # Should not be rate limited anymore
    assert rate_limiter.is_rate_limited("test-key") is False
    assert rate_limiter.get_remaining_requests("test-key") == 2

    def test_get_reset_time(self):
    """Test getting the time when the rate limit will reset."""
    # Create rate limiter with limit of 2 requests per 1 second
    rate_limiter = WebhookRateLimiter(limit=2, window_seconds=1)

    # Initially no reset time
    assert rate_limiter.get_reset_time("test-key") is None

    # Add a request
    current_time = time.time()
    rate_limiter.add_request("test-key")

    # Reset time should be approximately 1 second from now
    reset_time = rate_limiter.get_reset_time("test-key")
    assert reset_time is not None
    assert (
    abs((reset_time - current_time) - 1.0) < 0.1
    )  # Within 0.1 seconds of expected
