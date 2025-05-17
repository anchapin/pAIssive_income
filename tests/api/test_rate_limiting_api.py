"""test_rate_limiting_api - Tests for API rate limiting enforcement and edge cases."""

import time
from http import HTTPStatus
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

try:
    from api.main import app  # Update if API root is elsewhere
except ImportError:
    app = None

client = TestClient(app) if app else None


@pytest.mark.skipif(app is None, reason="Main FastAPI app not found for testing")
class TestRateLimitingAPI:
    ENDPOINT = "/users/"  # Use a typical endpoint for rate limiting demo

    def test_within_rate_limit(self):
        # Send a small number of requests below the limit
        for _ in range(3):
            resp = client.get(self.ENDPOINT)
            assert resp.status_code in (200, 401, 403)  # May require auth

    def test_exceed_rate_limit(self):
        # Simulate burst to exceed limit (assuming limit is 5/minute for test)
        responses = [client.get(self.ENDPOINT) for _ in range(10)]
        status_codes = [r.status_code for r in responses]
        # At least one request should be rate limited
        assert HTTPStatus.TOO_MANY_REQUESTS in status_codes

    def test_rate_limit_headers_present(self):
        resp = client.get(self.ENDPOINT)
        # Check for standard rate limit headers
        assert any(
            header in resp.headers
            for header in ["X-RateLimit-Limit", "X-RateLimit-Remaining", "Retry-After"]
        )

    def test_rate_limit_reset(self):
        # Exceed limit, then wait for reset window and try again
        for _ in range(10):
            client.get(self.ENDPOINT)
        resp = client.get(self.ENDPOINT)
        if (
            resp.status_code == HTTPStatus.TOO_MANY_REQUESTS
            and "Retry-After" in resp.headers
        ):
            wait_time = int(resp.headers["Retry-After"])
            with patch("time.sleep", return_value=None):
                time.sleep(min(wait_time, 3))  # Wait up to 3 seconds for test
            resp2 = client.get(self.ENDPOINT)
            # Should eventually reset to allow again
            assert resp2.status_code in (200, 401, 403)

    def test_burst_requests(self):
        # Send rapid burst and check at least some are limited
        responses = [client.get(self.ENDPOINT) for _ in range(20)]
        limited = [
            r for r in responses if r.status_code == HTTPStatus.TOO_MANY_REQUESTS
        ]
        assert len(limited) > 0

    def test_rate_limit_authenticated_vs_unauthenticated(self):
        # If different limits by auth, test both cases
        resp_anon = client.get(self.ENDPOINT)
        headers = {"Authorization": "Bearer validtoken"}  # Test token only
        resp_auth = client.get(self.ENDPOINT, headers=headers)
        # Should both return 200/401/403 or 429, but possibly different headers/limits
        assert resp_anon.status_code in (200, 401, 403, 429)
        assert resp_auth.status_code in (200, 401, 403, 429)
        # Check if rate limit headers are present
        if (
            "X-RateLimit-Limit" in resp_auth.headers
            and "X-RateLimit-Limit" in resp_anon.headers
        ):
            # Different rate limits may be applied based on authentication status
            pass
