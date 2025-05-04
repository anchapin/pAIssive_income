"""
Tests for the rate limiting functionality.

This module contains tests for rate limiting and throttling endpoints.
"""

import time
from concurrent.futures import ThreadPoolExecutor

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_id
    validate_bulk_response,
    validate_error_response,
    validate_field_equals,
    validate_field_exists,
    validate_field_not_empty,
    validate_field_type,
    validate_json_response,
    validate_list_contains,
    validate_list_contains_dict_with_field,
    validate_list_length,
    validate_list_max_length,
    validate_list_min_length,
    validate_list_not_empty,
    validate_paginated_response,
    validate_status_code,
    validate_success_response,
)

class TestRateLimitingAPI:
    """Tests for the rate limiting API."""

    def test_rate_limit_enforcement(self, api_test_client: APITestClient):
        """Test that rate limits are properly enforced."""
        endpoint = "test - rate - limit"

        # Make multiple requests in quick succession
        responses = []
        for _ in range(5):  # Attempt more requests than default rate limit
            response = api_test_client.get(f"rate - limiting/{endpoint}")
            responses.append(response)

        # Validate that some requests succeeded and some were rate limited
        successful = [r for r in responses if r.status_code == 200]
        rate_limited = [r for r in responses if r.status_code == 429]

        assert len(successful) > 0, "Expected some requests to succeed"
        assert len(rate_limited) > 0, "Expected some requests to be rate limited"

        # Validate rate limit headers in successful responses
        for response in successful:
            assert "X - RateLimit - Limit" in response.headers
            assert "X - RateLimit - Remaining" in response.headers
            assert "X - RateLimit - Reset" in response.headers

            # Validate that remaining count decreases
            remaining = int(response.headers["X - RateLimit - Remaining"])
            assert remaining >= 0, "Remaining requests should not be negative"

        # Validate rate limited response
        for response in rate_limited:
            result = validate_error_response(response, 429)  # Too Many Requests
            assert "Retry - After" in response.headers

            # Validate error response structure
            validate_field_exists(result, "error")
            validate_field_exists(result["error"], "message")
            validate_field_exists(result["error"], "retry_after")

    def test_rate_limit_reset(self, api_test_client: APITestClient):
        """Test that rate limits reset after the specified window."""
        endpoint = "test - rate - limit - reset"

        # Step 1: Make requests until rate limited
        responses = []
        while True:
            response = api_test_client.get(f"rate - limiting/{endpoint}")
            if response.status_code == 429:
                break
            responses.append(response)

        # Get reset time from last successful response
        last_successful = responses[-1]
        reset_after = int(last_successful.headers["X - RateLimit - Reset"])

        # Step 2: Wait for rate limit window to reset
        time.sleep(reset_after + 1)

        # Step 3: Try another request
        response = api_test_client.get(f"rate - limiting/{endpoint}")
        validate_success_response(response)

        # Validate new rate limit window
        assert "X - RateLimit - Limit" in response.headers
        assert int(response.headers["X - RateLimit - Remaining"]) > 0

    def test_custom_rate_limits(self, auth_api_test_client: APITestClient):
        """Test custom rate limits for different user tiers."""
        # Configure test rate limits
        config_data = {
            "tier": "premium",
            "limits": {
                "requests_per_second": 10,
                "requests_per_minute": 100,
                "requests_per_hour": 1000,
            },
        }

        # Apply custom rate limits
        response = auth_api_test_client.post("rate - limiting / config", config_data)
        validate_success_response(response)

        # Test the custom limits
        endpoint = "test - custom - rate - limit"
        responses = []

        # Make requests at the configured rate
        for _ in range(15):  # More than requests_per_second
            response = auth_api_test_client.get(f"rate - limiting/{endpoint}")
            responses.append(response)

        # Validate that limits were enforced according to tier
        successful = len([r for r in responses if r.status_code == 200])
        assert successful <= config_data["limits"]["requests_per_second"]

    def test_rate_limit_by_ip(self, api_test_client: APITestClient):
        """Test rate limiting by IP address."""
        endpoint = "test - ip - rate - limit"

        # Test with different IP addresses
        ips = ["192.168.1.1", "192.168.1.2"]

        for ip in ips:
            # Make requests with specific IP
            headers = {"X - Forwarded - For": ip}
            responses = []

            for _ in range(5):
                response = api_test_client.get(f"rate - limiting/{endpoint}", 
                    headers=headers)
                responses.append(response)

            # Validate rate limits are tracked separately per IP
            successful = len([r for r in responses if r.status_code == 200])
            assert successful > 0, f"Expected some requests to succeed for IP {ip}"

    def test_concurrent_request_throttling(self, api_test_client: APITestClient):
        """Test throttling of concurrent requests."""
        endpoint = "test - concurrent - throttling"

        # Configure throttling
        config = {"max_concurrent_requests": 3, "timeout_seconds": 5}

        response = api_test_client.post("rate - limiting / throttle - config", config)
        validate_success_response(response)

        # Make concurrent requests
        from concurrent.futures import ThreadPoolExecutor

        def make_request():
            return api_test_client.get(f"rate - limiting/{endpoint}")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [f.result() for f in futures]

        # Validate that some requests were throttled
        successful = len([r for r in responses if r.status_code == 200])
        throttled = len([r for r in responses if r.status_code == 429])

        assert successful <= config["max_concurrent_requests"]
        assert throttled > 0

    def test_degradation_under_load(self, api_test_client: APITestClient):
        """Test graceful degradation under load."""
        endpoint = "test - degradation"

        # Make requests with increasing concurrency
        concurrent_requests = [1, 5, 10, 20]
        response_times = []

        for concurrency in concurrent_requests:
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [
                    executor.submit(api_test_client.get, f"rate - limiting/{endpoint}")
                    for _ in range(concurrency)
                ]
                responses = [f.result() for f in futures]

                # Calculate average response time
                successful_responses = [
                    r
                    for r in responses
                    if r.status_code in (200, 429)  # Include rate limited responses
                ]

                for response in successful_responses:
                    assert "X - Response - Time" in response.headers
                    response_times.append(float(response.headers["X - \
                        Response - Time"]))

        # Validate graceful degradation
        # Response times should increase gradually, not exponentially
        for i in range(1, len(response_times)):
            ratio = response_times[i] / response_times[i - 1]
            assert ratio < 5, "Response time increased too dramatically"

    def test_custom_quota_limits(self, auth_api_test_client: APITestClient):
        """Test customer - specific quota limits."""
        # Set up custom quota
        quota_data = {
            "customer_id": generate_id(),
            "daily_limit": 1000,
            "monthly_limit": 10000,
            "overage_allowed": True,
            "overage_rate": 1.5,
        }

        response = auth_api_test_client.post("rate - limiting / quota", quota_data)
        validate_success_response(response)

        # Test quota enforcement
        endpoint = "test - quota - limit"

        # Make requests and track quota usage
        responses = []
        quota_headers = []

        for _ in range(5):
            response = auth_api_test_client.get(f"rate - limiting/{endpoint}")
            responses.append(response)

            if response.status_code == 200:
                assert "X - Daily - Quota - Remaining" in response.headers
                assert "X - Monthly - Quota - Remaining" in response.headers
                quota_headers.append(
                    {
                        "daily": int(response.headers["X - Daily - Quota - Remaining"]),
                        "monthly": int(response.headers["X - Monthly - Quota - Remaining"]),
                    }
                )

        # Validate quota tracking
        for i in range(1, len(quota_headers)):
            assert quota_headers[i]["daily"] < quota_headers[i - 1]["daily"]
            assert quota_headers[i]["monthly"] < quota_headers[i - 1]["monthly"]
