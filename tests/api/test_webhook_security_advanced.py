"""
Advanced tests for webhook security features.

This module tests advanced security features for the webhook system:
1. Handling of replayed webhook signatures
2. Rate limit behavior during partial system outages
3. IP allowlist updates during active connections
4. Signature verification with tampered payloads
5. Signature verification with expired timestamps
6. Signature verification with incorrect secrets
7. IP allowlist with CIDR range boundaries
8. Rate limiting with concurrent requests
9. Rate limiting headers in responses
"""

import asyncio
import ipaddress
import json
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request, Response, status
from fastapi.testclient import TestClient

from api.middleware.webhook_security import WebhookIPAllowlistMiddleware, 
    WebhookRateLimitMiddleware
from api.services.webhook_security import (
    WebhookIPAllowlist,
    WebhookRateLimiter,
    WebhookSignatureVerifier,
)


class TestReplayedSignatures:
    """Tests for handling replayed webhook signatures."""

    def test_replay_protection_with_timestamp(self):
        """Test protection against replayed signatures using timestamps."""
        # Create a timestamp - based signature verifier
        verifier = WebhookSignatureVerifier()

        # Create a payload with timestamp
        payload = {
            "id": "event - 123",
            "type": "user.created",
            "timestamp": int(time.time()),
            "data": {"user_id": "user - 123"},
        }
        payload_str = json.dumps(payload)

        # Create a signature with a secret
        secret = "test - secret"
        signature = verifier.create_signature(secret, payload_str)

        # Verify the signature (should pass)
        assert verifier.verify_signature(secret, payload_str, signature) is True

        # Simulate a replay attack by using an old timestamp
        old_payload = payload.copy()
        old_payload["timestamp"] = int(time.time()) - 600  # 10 minutes old
        old_payload_str = json.dumps(old_payload)
        old_signature = verifier.create_signature(secret, old_payload_str)

        # Create a timestamp - aware verifier with a 5 - minute tolerance
        class TimestampAwareVerifier(WebhookSignatureVerifier):
            def verify_signature(self, secret, payload, signature, max_age_minutes=5):
                # First verify the signature itself
                if not super().verify_signature(secret, payload, signature):
                    return False

                # Then check the timestamp
                try:
                    payload_data = json.loads(payload)
                    timestamp = payload_data.get("timestamp")

                    if timestamp is None:
                        return False

                    # Check if the timestamp is too old
                    current_time = int(time.time())
                    max_age_seconds = max_age_minutes * 60

                    if current_time - timestamp > max_age_seconds:
                        return False

                    return True
                except (json.JSONDecodeError, TypeError, ValueError):
                    return False

        # Create the timestamp - aware verifier
        ts_verifier = TimestampAwareVerifier()

        # Verify the current signature (should pass)
        assert ts_verifier.verify_signature(secret, payload_str, signature) is True

        # Verify the old signature (should fail due to timestamp)
        assert ts_verifier.verify_signature(secret, old_payload_str, 
            old_signature) is False

    def test_replay_protection_with_nonce(self):
        """Test protection against replayed signatures using nonces."""
        # Create a nonce - based signature verifier
        verifier = WebhookSignatureVerifier()

        # Create a payload with nonce
        nonce = "unique - nonce - 123"
        payload = {
            "id": "event - 123",
            "type": "user.created",
            "nonce": nonce,
            "data": {"user_id": "user - 123"},
        }
        payload_str = json.dumps(payload)

        # Create a signature with a secret
        secret = "test - secret"
        signature = verifier.create_signature(secret, payload_str)

        # Create a mock nonce store
        used_nonces = set()

        # Create a nonce - aware verifier
        class NonceAwareVerifier(WebhookSignatureVerifier):
            def verify_signature_with_nonce(self, secret, payload, signature, 
                nonce_store):
                # First verify the signature itself
                if not super().verify_signature(secret, payload, signature):
                    return False

                # Then check the nonce
                try:
                    payload_data = json.loads(payload)
                    nonce = payload_data.get("nonce")

                    if nonce is None:
                        return False

                    # Check if the nonce has been used before
                    if nonce in nonce_store:
                        return False

                    # Add the nonce to the store
                    nonce_store.add(nonce)

                    return True
                except (json.JSONDecodeError, TypeError, ValueError):
                    return False

        # Create the nonce - aware verifier
        nonce_verifier = NonceAwareVerifier()

        # Verify the signature (should pass and add nonce to store)
        assert (
            nonce_verifier.verify_signature_with_nonce(secret, payload_str, signature, 
                used_nonces)
            is True
        )
        assert nonce in used_nonces

        # Try to verify the same signature again (should fail due to used nonce)
        assert (
            nonce_verifier.verify_signature_with_nonce(secret, payload_str, signature, 
                used_nonces)
            is False
        )


class TestRateLimitBehavior:
    """Tests for rate limit behavior during partial system outages."""

    def test_rate_limit_during_outage(self):
        """Test rate limiting behavior during simulated partial system outage."""
        # Create a rate limiter
        rate_limiter = WebhookRateLimiter(limit=5, window_seconds=60)

        # Create a mock storage backend that can fail
        class UnreliableStorage:
            def __init__(self, failure_rate=0.0):
                self.failure_rate = failure_rate
                self.data = {}

            def get(self, key):
                if self.failure_rate > 0 and random.random() < self.failure_rate:
                    raise Exception("Storage backend failure")
                return self.data.get(key, [])

            def set(self, key, value):
                if self.failure_rate > 0 and random.random() < self.failure_rate:
                    raise Exception("Storage backend failure")
                self.data[key] = value

        # Create a rate limiter that uses the unreliable storage
        class RobustRateLimiter(WebhookRateLimiter):
            def __init__(self, limit, window_seconds, storage):
                super().__init__(limit, window_seconds)
                self.storage = storage
                self.local_cache = {}
                self.last_sync = {}

            def is_rate_limited(self, key):
                try:
                    # Try to get from storage
                    self.requests[key] = self.storage.get(key)
                    current_time = time.time()

                    # Remove requests outside the time window
                    self.requests[key] = [
                        t for t in self.requests[key] if current_time - \
                            t <= self.window_seconds
                    ]

                    # Update storage
                    self.storage.set(key, self.requests[key])

                    # Check if limit is exceeded
                    return len(self.requests[key]) >= self.limit
                except Exception:
                    # Fall back to local cache if storage fails
                    if key not in self.local_cache:
                        self.local_cache[key] = []

                    current_time = time.time()

                    # Remove requests outside the time window
                    self.local_cache[key] = [
                        t for t in self.local_cache[key] if current_time - \
                            t <= self.window_seconds
                    ]

                    # Use a more conservative limit during outage
                    conservative_limit = max(1, self.limit // 2)

                    # Check if conservative limit is exceeded
                    return len(self.local_cache[key]) >= conservative_limit

            def add_request(self, key):
                current_time = time.time()

                try:
                    # Try to get from storage
                    self.requests[key] = self.storage.get(key)

                    # Add current request
                    self.requests[key].append(current_time)

                    # Remove requests outside the time window
                    self.requests[key] = [
                        t for t in self.requests[key] if current_time - \
                            t <= self.window_seconds
                    ]

                    # Update storage
                    self.storage.set(key, self.requests[key])
                except Exception:
                    # Fall back to local cache if storage fails
                    if key not in self.local_cache:
                        self.local_cache[key] = []

                    # Add current request
                    self.local_cache[key].append(current_time)

                    # Remove requests outside the time window
                    self.local_cache[key] = [
                        t for t in self.local_cache[key] if current_time - \
                            t <= self.window_seconds
                    ]

        # Test with working storage
        import random

        random.seed(42)  # For reproducible tests
        storage = UnreliableStorage(failure_rate=0.0)
        limiter = RobustRateLimiter(limit=5, window_seconds=60, storage=storage)

        # Add requests
        for i in range(4):
            limiter.add_request("test - key")

        # Should not be rate limited yet
        assert limiter.is_rate_limited("test - key") is False

        # Add one more request
        limiter.add_request("test - key")

        # Should be rate limited now
        assert limiter.is_rate_limited("test - key") is True

        # Test with failing storage
        storage = UnreliableStorage(failure_rate=1.0)  # Always fail
        limiter = RobustRateLimiter(limit=5, window_seconds=60, storage=storage)

        # Add requests
        for i in range(2):
            limiter.add_request("test - key")

        # Should not be rate limited yet (using conservative limit of 2)
        assert limiter.is_rate_limited("test - key") is False

        # Add one more request
        limiter.add_request("test - key")

        # Should be rate limited now (conservative limit of 2)
        assert limiter.is_rate_limited("test - key") is True


class TestIPAllowlistUpdates:
    """Tests for IP allowlist updates during active connections."""

    def test_ip_allowlist_updates_during_connections(self):
        """Test updating IP allowlist while connections are active."""
        # Create an IP allowlist
        allowlist = WebhookIPAllowlist()

        # Add some IPs to the allowlist
        allowlist.add_ip("192.168.1.1")
        allowlist.add_cidr("10.0.0.0 / 24")

        # Create a FastAPI app with the allowlist middleware
        app = FastAPI()
        app.add_middleware(
            WebhookIPAllowlistMiddleware, allowlist=allowlist, 
                webhook_path_prefix=" / webhooks"
        )

        # Add a test route
        @app.post(" / webhooks / test")
        async def test_webhook(request: Request):
            return {"status": "success"}

        # Create a test client
        client = TestClient(app)

        # Test with an allowed IP
        with patch("fastapi.Request.client") as mock_client:
            mock_client.host = "192.168.1.1"
            response = client.post(" / webhooks / test")
            assert response.status_code == 200

        # Test with another allowed IP in CIDR range
        with patch("fastapi.Request.client") as mock_client:
            mock_client.host = "10.0.0.5"
            response = client.post(" / webhooks / test")
            assert response.status_code == 200

        # Test with a blocked IP
        with patch("fastapi.Request.client") as mock_client:
            mock_client.host = "172.16.0.1"
            response = client.post(" / webhooks / test")
            assert response.status_code == 403

        # Update the allowlist during "active connections"
        allowlist.remove_ip("192.168.1.1")
        allowlist.add_ip("172.16.0.1")

        # Test with the now - blocked IP
        with patch("fastapi.Request.client") as mock_client:
            mock_client.host = "192.168.1.1"
            response = client.post(" / webhooks / test")
            assert response.status_code == 403

        # Test with the now - allowed IP
        with patch("fastapi.Request.client") as mock_client:
            mock_client.host = "172.16.0.1"
            response = client.post(" / webhooks / test")
            assert response.status_code == 200

        # Test with an IP that's still allowed via CIDR
        with patch("fastapi.Request.client") as mock_client:
            mock_client.host = "10.0.0.10"
            response = client.post(" / webhooks / test")
            assert response.status_code == 200


class TestSignatureVerification:
    """Tests for signature verification with various edge cases."""

    def test_tampered_payload(self):
        """Test signature verification with tampered payloads."""
        # Create a signature verifier
        verifier = WebhookSignatureVerifier()

        # Create a payload
        payload = {
            "id": "event - 123",
            "type": "user.created",
            "data": {"user_id": "user - 123", "email": "user @ example.com"},
        }
        payload_str = json.dumps(payload)

        # Create a signature with a secret
        secret = "test - secret"
        signature = verifier.create_signature(secret, payload_str)

        # Verify the signature (should pass)
        assert verifier.verify_signature(secret, payload_str, signature) is True

        # Tamper with the payload
        tampered_payload = payload.copy()
        tampered_payload["data"]["email"] = "hacker @ evil.com"
        tampered_payload_str = json.dumps(tampered_payload)

        # Verify the signature with tampered payload (should fail)
        assert verifier.verify_signature(secret, tampered_payload_str, 
            signature) is False

        # Test with minimal tampering (just whitespace changes)
        whitespace_payload_str = json.dumps(payload, indent=2)

        # Verify the signature with whitespace changes (should fail)
        assert verifier.verify_signature(secret, whitespace_payload_str, 
            signature) is False

    def test_expired_timestamps(self):
        """Test signature verification with expired timestamps."""

        # Create a timestamp - based signature verifier
        class TimestampVerifier(WebhookSignatureVerifier):
            def create_signature_with_timestamp(self, secret, payload, timestamp=None):
                if timestamp is None:
                    timestamp = int(time.time())

                # Add timestamp to the signature string
                signature_payload = f"{timestamp}:{payload}"

                # Create the signature
                signature = self.create_signature(secret, signature_payload)

                # Return both the signature and the timestamp
                return f"t={timestamp},v1={signature}"

            def verify_signature_with_timestamp(
                self, secret, payload, signature_header, max_age_minutes=5
            ):
                try:
                    # Parse the signature header
                    parts = {}
                    for part in signature_header.split(","):
                        key, value = part.split("=", 1)
                        parts[key] = value

                    # Get the timestamp and signature
                    timestamp = int(parts.get("t", 0))
                    signature = parts.get("v1", "")

                    # Check if the timestamp is too old
                    current_time = int(time.time())
                    max_age_seconds = max_age_minutes * 60

                    if current_time - timestamp > max_age_seconds:
                        return False

                    # Verify the signature
                    signature_payload = f"{timestamp}:{payload}"
                    return self.verify_signature(secret, signature_payload, signature)
                except (ValueError, KeyError):
                    return False

        # Create the verifier
        verifier = TimestampVerifier()

        # Create a payload
        payload = json.dumps({"id": "event - 123", "type": "user.created"})

        # Create a signature with current timestamp
        secret = "test - secret"
        current_signature = verifier.create_signature_with_timestamp(secret, payload)

        # Verify the signature (should pass)
        assert verifier.verify_signature_with_timestamp(secret, payload, 
            current_signature) is True

        # Create a signature with old timestamp
        old_timestamp = int(time.time()) - 600  # 10 minutes old
        old_signature = verifier.create_signature_with_timestamp(secret, payload, 
            old_timestamp)

        # Verify the signature with old timestamp (should fail)
        assert verifier.verify_signature_with_timestamp(secret, payload, 
            old_signature) is False

        # Verify with a custom max age that allows the old timestamp
        assert (
            verifier.verify_signature_with_timestamp(
                secret, payload, old_signature, max_age_minutes=15
            )
            is True
        )

    def test_incorrect_secrets(self):
        """Test signature verification with incorrect secrets."""
        # Create a signature verifier
        verifier = WebhookSignatureVerifier()

        # Create a payload
        payload = json.dumps({"id": "event - 123", "type": "user.created"})

        # Create a signature with the correct secret
        correct_secret = "correct - secret"
        signature = verifier.create_signature(correct_secret, payload)

        # Verify the signature with the correct secret (should pass)
        assert verifier.verify_signature(correct_secret, payload, signature) is True

        # Verify with an incorrect secret (should fail)
        incorrect_secret = "incorrect - secret"
        assert verifier.verify_signature(incorrect_secret, payload, signature) is False

        # Verify with a similar but slightly different secret (should fail)
        similar_secret = "correct - secre"  # Missing the last 't'
        assert verifier.verify_signature(similar_secret, payload, signature) is False

        # Verify with an empty secret (should fail)
        empty_secret = ""
        assert verifier.verify_signature(empty_secret, payload, signature) is False


class TestIPAllowlistCIDR:
    """Tests for IP allowlist with CIDR range boundaries."""

    def test_cidr_range_boundaries(self):
        """Test IP allowlist with CIDR range boundaries."""
        # Create an IP allowlist
        allowlist = WebhookIPAllowlist()

        # Add a CIDR range
        allowlist.add_cidr("192.168.1.0 / 24")

        # Test IPs within the range
        assert allowlist.is_allowed("192.168.1.0") is True  # First IP in range
        assert allowlist.is_allowed("192.168.1.1") is True
        assert allowlist.is_allowed("192.168.1.254") is True
        assert allowlist.is_allowed("192.168.1.255") is True  # Last IP in range

        # Test IPs outside the range
        assert allowlist.is_allowed("192.168.0.255") is False  # Just before range
        assert allowlist.is_allowed("192.168.2.0") is False  # Just after range

        # Test with a smaller CIDR range
        allowlist.clear()
        allowlist.add_cidr("10.0.0.0 / 30")  # Only 4 IPs: 10.0.0.0 - 10.0.0.3

        # Test IPs within the range
        assert allowlist.is_allowed("10.0.0.0") is True
        assert allowlist.is_allowed("10.0.0.1") is True
        assert allowlist.is_allowed("10.0.0.2") is True
        assert allowlist.is_allowed("10.0.0.3") is True

        # Test IPs outside the range
        assert allowlist.is_allowed("10.0.0.4") is False

        # Test with overlapping CIDR ranges
        allowlist.clear()
        allowlist.add_cidr("10.0.0.0 / 24")  # 10.0.0.0 - 10.0.0.255
        allowlist.add_cidr("10.0.0.128 / 25")  # 10.0.0.128 - 10.0.0.255 (overlaps)

        # Test IPs in both ranges
        assert allowlist.is_allowed("10.0.0.0") is True
        assert allowlist.is_allowed("10.0.0.127") is True
        assert allowlist.is_allowed("10.0.0.128") is True
        assert allowlist.is_allowed("10.0.0.255") is True

        # Test removing a CIDR range
        allowlist.remove_cidr("10.0.0.0 / 24")

        # Test IPs after removal
        assert allowlist.is_allowed("10.0.0.0") is False
        assert allowlist.is_allowed("10.0.0.127") is False
        assert allowlist.is_allowed(
            "10.0.0.128") is True  # Still allowed by the other range
        assert allowlist.is_allowed(
            "10.0.0.255") is True  # Still allowed by the other range


class TestRateLimitingConcurrent:
    """Tests for rate limiting with concurrent requests."""

    @pytest.mark.asyncio
    async def test_concurrent_rate_limiting(self):
        """Test rate limiting with concurrent requests."""
        # Create a rate limiter
        rate_limiter = WebhookRateLimiter(limit=5, window_seconds=60)

        # Create a FastAPI app with the rate limit middleware
        app = FastAPI()
        app.add_middleware(
            WebhookRateLimitMiddleware, rate_limiter=rate_limiter, 
                webhook_path_prefix=" / webhooks"
        )

        # Add a test route
        @app.post(" / webhooks / test")
        async def test_webhook(request: Request):
            return {"status": "success"}

        # Create a test client
        client = TestClient(app)

        # Create a function to make a request with a specific client IP
        async def make_request(client_ip):
            with patch("fastapi.Request.client") as mock_client:
                mock_client.host = client_ip
                return client.post(" / webhooks / test")

        # Make concurrent requests from the same IP
        client_ip = "192.168.1.1"
        tasks = [make_request(client_ip) for _ in range(10)]

        # Run the tasks concurrently
        responses = await asyncio.gather(*tasks)

        # Count the responses by status code
        status_counts = {}
        for response in responses:
            status = response.status_code
            status_counts[status] = status_counts.get(status, 0) + 1

        # We should have 5 successful responses (200) and 5 rate limited responses (429)
        assert status_counts.get(200, 0) == 5
        assert status_counts.get(429, 0) == 5

        # Make requests from different IPs
        client_ips = [f"192.168.1.{i}" for i in range(1, 11)]
        tasks = [make_request(ip) for ip in client_ips]

        # Run the tasks concurrently
        responses = await asyncio.gather(*tasks)

        # All requests should succeed because they're from different IPs
        for response in responses:
            assert response.status_code == 200


class TestRateLimitingHeaders:
    """Tests for rate limiting headers in responses."""

    def test_rate_limit_headers(self):
        """Test rate limiting headers in responses."""
        # Create a rate limiter
        rate_limiter = WebhookRateLimiter(limit=5, window_seconds=60)

        # Create a FastAPI app with the rate limit middleware
        app = FastAPI()
        app.add_middleware(
            WebhookRateLimitMiddleware, rate_limiter=rate_limiter, 
                webhook_path_prefix=" / webhooks"
        )

        # Add a test route
        @app.post(" / webhooks / test")
        async def test_webhook(request: Request):
            return {"status": "success"}

        # Create a test client
        client = TestClient(app)

        # Make requests and check headers
        client_ip = "192.168.1.1"

        # First request
        with patch("fastapi.Request.client") as mock_client:
            mock_client.host = client_ip
            response = client.post(" / webhooks / test")

        # Check headers
        assert response.status_code == 200
        assert "X - RateLimit - Limit" in response.headers
        assert "X - RateLimit - Remaining" in response.headers
        assert "X - RateLimit - Reset" in response.headers

        assert int(response.headers["X - RateLimit - Limit"]) == 5
        assert int(response.headers["X - RateLimit - Remaining"]) == 4

        # Make more requests until rate limited
        for i in range(4):
            with patch("fastapi.Request.client") as mock_client:
                mock_client.host = client_ip
                response = client.post(" / webhooks / test")

        # This request should be rate limited
        with patch("fastapi.Request.client") as mock_client:
            mock_client.host = client_ip
            response = client.post(" / webhooks / test")

        # Check headers for rate limited response
        assert response.status_code == 429
        assert "X - RateLimit - Limit" in response.headers
        assert "X - RateLimit - Remaining" in response.headers
        assert "X - RateLimit - Reset" in response.headers
        assert "Retry - After" in response.headers

        assert int(response.headers["X - RateLimit - Limit"]) == 5
        assert int(response.headers["X - RateLimit - Remaining"]) == 0
        assert int(response.headers["Retry - After"]) > 0
