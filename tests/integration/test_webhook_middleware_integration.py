"""
Integration tests for webhook middleware.

This module tests the integration between webhook middleware and FastAPI.
"""

import time

import pytest
from fastapi import FastAPI, Request, Response, status
from fastapi.testclient import TestClient

from api.middleware.webhook_security import WebhookIPAllowlistMiddleware, WebhookRateLimitMiddleware
from api.services.webhook_security import WebhookIPAllowlist, WebhookRateLimiter


@pytest.fixture
def ip_allowlist():
    """Create an IP allowlist for testing."""
    allowlist = WebhookIPAllowlist()
    # Add some test IPs and networks
    allowlist.add_ip("127.0.0.1")
    allowlist.add_ip("testclient")  # TestClient uses this as the client IP
    allowlist.add_network("10.0.0.0 / 8")
    return allowlist


@pytest.fixture
def rate_limiter():
    """Create a rate limiter for testing."""
    return WebhookRateLimiter(limit=3, window_seconds=1)


@pytest.fixture
def app_with_ip_allowlist(ip_allowlist):
    """Create a FastAPI app with IP allowlist middleware."""
    app = FastAPI()

    # Add middleware
    app.add_middleware(
        WebhookIPAllowlistMiddleware, allowlist=ip_allowlist, webhook_path_prefix=" / webhooks"
    )

    # Add test routes
    @app.get(" / webhooks / test")
    async def test_webhook():
        return {"status": "success"}

    @app.get(" / api / other")
    async def other_endpoint():
        return {"status": "success"}

    return app


@pytest.fixture
def app_with_rate_limit(rate_limiter):
    """Create a FastAPI app with rate limit middleware."""
    app = FastAPI()

    # Add middleware
    app.add_middleware(
        WebhookRateLimitMiddleware, rate_limiter=rate_limiter, webhook_path_prefix=" / webhooks"
    )

    # Add test routes
    @app.get(" / webhooks / test")
    async def test_webhook():
        return {"status": "success"}

    @app.get(" / api / other")
    async def other_endpoint():
        return {"status": "success"}

    return app


@pytest.fixture
def app_with_both_middleware(ip_allowlist, rate_limiter):
    """Create a FastAPI app with both middleware."""
    app = FastAPI()

    # Add middleware (order matters - IP allowlist should be first)
    app.add_middleware(
        WebhookRateLimitMiddleware, rate_limiter=rate_limiter, webhook_path_prefix=" / webhooks"
    )
    app.add_middleware(
        WebhookIPAllowlistMiddleware, allowlist=ip_allowlist, webhook_path_prefix=" / webhooks"
    )

    # Add test routes
    @app.get(" / webhooks / test")
    async def test_webhook():
        return {"status": "success"}

    @app.get(" / api / other")
    async def other_endpoint():
        return {"status": "success"}

    # Add a route that returns client IP
    @app.get(" / client - ip")
    async def client_ip(request: Request):
        return {"client_ip": request.client.host}

    return app


class TestIPAllowlistMiddleware:
    """Tests for the IP allowlist middleware."""

    def test_allowed_ip(self, app_with_ip_allowlist):
        """Test that allowed IPs can access webhook endpoints."""
        client = TestClient(app_with_ip_allowlist)
        response = client.get(" / webhooks / test")
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_non_webhook_path(self, app_with_ip_allowlist):
        """Test that non - webhook paths are not affected by IP allowlisting."""
        client = TestClient(app_with_ip_allowlist)
        response = client.get(" / api / other")
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_disallowed_ip(self, app_with_ip_allowlist):
        """Test that disallowed IPs are blocked from webhook endpoints."""
        # Create a new allowlist with different IPs
        app_with_ip_allowlist.user_middleware[0].allowlist.allowlisted_ips.clear()
        app_with_ip_allowlist.user_middleware[0].allowlist.add_ip("192.168.1.1")

        client = TestClient(app_with_ip_allowlist)
        response = client.get(" / webhooks / test")
        assert response.status_code == 403
        assert "IP address not allowed" in response.json()["detail"]


class TestRateLimitMiddleware:
    """Tests for the rate limit middleware."""

    def test_rate_limit(self, app_with_rate_limit):
        """Test that rate limiting is applied to webhook endpoints."""
        client = TestClient(app_with_rate_limit)

        # Make requests up to the limit
        for _ in range(3):
            response = client.get(" / webhooks / test")
            assert response.status_code == 200
            assert "X - RateLimit - Remaining" in response.headers

        # Next request should be rate limited
        response = client.get(" / webhooks / test")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]
        assert "Retry - After" in response.headers
        assert "X - RateLimit - Reset" in response.headers

    def test_non_webhook_path(self, app_with_rate_limit):
        """Test that non - webhook paths are not affected by rate limiting."""
        client = TestClient(app_with_rate_limit)

        # Make many requests to a non - webhook path
        for _ in range(10):
            response = client.get(" / api / other")
            assert response.status_code == 200
            assert response.json()["status"] == "success"

    def test_rate_limit_reset(self, app_with_rate_limit):
        """Test that rate limits reset after the window expires."""
        client = TestClient(app_with_rate_limit)

        # Make requests up to the limit
        for _ in range(3):
            response = client.get(" / webhooks / test")
            assert response.status_code == 200

        # Next request should be rate limited
        response = client.get(" / webhooks / test")
        assert response.status_code == 429

        # Wait for the rate limit to reset
        time.sleep(1.1)

        # Should be able to make requests again
        response = client.get(" / webhooks / test")
        assert response.status_code == 200
        assert response.json()["status"] == "success"


class TestCombinedMiddleware:
    """Tests for both middleware together."""

    def test_allowed_ip_within_rate_limit(self, app_with_both_middleware):
        """Test that allowed IPs within rate limit can access webhook endpoints."""
        client = TestClient(app_with_both_middleware)

        # Check client IP
        response = client.get(" / client - ip")
        assert response.status_code == 200
        client_ip = response.json()["client_ip"]

        # Ensure IP is allowed
        app_with_both_middleware.user_middleware[0].allowlist.add_ip(client_ip)

        # Make requests up to the limit
        for _ in range(3):
            response = client.get(" / webhooks / test")
            assert response.status_code == 200
            assert response.json()["status"] == "success"

    def test_allowed_ip_rate_limited(self, app_with_both_middleware):
        """Test that allowed IPs are rate limited after exceeding the limit."""
        client = TestClient(app_with_both_middleware)

        # Check client IP
        response = client.get(" / client - ip")
        assert response.status_code == 200
        client_ip = response.json()["client_ip"]

        # Ensure IP is allowed
        app_with_both_middleware.user_middleware[0].allowlist.add_ip(client_ip)

        # Make requests up to the limit
        for _ in range(3):
            response = client.get(" / webhooks / test")
            assert response.status_code == 200

        # Next request should be rate limited
        response = client.get(" / webhooks / test")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    def test_disallowed_ip(self, app_with_both_middleware):
        """Test that disallowed IPs are blocked regardless of rate limit."""
        client = TestClient(app_with_both_middleware)

        # Check client IP
        response = client.get(" / client - ip")
        assert response.status_code == 200
        client_ip = response.json()["client_ip"]

        # Remove IP from allowlist
        app_with_both_middleware.user_middleware[0].allowlist.allowlisted_ips.clear()
        app_with_both_middleware.user_middleware[0].allowlist.add_ip("192.168.1.1")  # Different IP

        # Try to access webhook endpoint
        response = client.get(" / webhooks / test")
        assert response.status_code == 403
        assert "IP address not allowed" in response.json()["detail"]
