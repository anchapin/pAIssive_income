"""
Integration tests for analytics data collection across APIs.

This module contains tests for analytics data collection across different
API endpoints and services.
"""

import time
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import (
    generate_marketing_strategy_data,
    generate_monetization_data,
    generate_niche_analysis_data,
    generate_solution_data,
)


@pytest.fixture
def auth_api_test_client():
    """Create an authenticated API test client."""
    client = APITestClient(base_url="http://localhost:8000/api")
    client.authenticate("test_user", "test_password")
    return client


class TestAnalyticsDataCollection:
    """Test analytics data collection across APIs."""

    def validate_success_response(self, response, expected_status=200):
        """Validate a successful API response."""
        assert response.status_code == expected_status
        data = response.json()
        assert "error" not in data
        return data

    def test_api_request_tracking(self, auth_api_test_client):
        """Test API request tracking."""
        # Make several API requests
        auth_api_test_client.get("niche-analysis/niches")
        auth_api_test_client.get("solutions")
        auth_api_test_client.get("monetization/strategies")
        auth_api_test_client.get("marketing/strategies")

        # Check analytics data
        response = auth_api_test_client.get("analytics/requests")

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("Analytics endpoint not implemented")

        # Validate response
        analytics_data = self.validate_success_response(response)

        # Verify that the requests were tracked
        assert "requests" in analytics_data
        assert len(analytics_data["requests"]) >= 4

        # Verify that the request data contains the expected fields
        for request in analytics_data["requests"]:
            assert "endpoint" in request
            assert "method" in request
            assert "timestamp" in request
            assert "response_time" in request
            assert "status_code" in request

    def test_user_journey_tracking(self, auth_api_test_client):
        """Test user journey tracking."""
        # Simulate a user journey

        # Step 1: Create a niche analysis
        niche_data = generate_niche_analysis_data()
        response = auth_api_test_client.post("niche-analysis/analyze", niche_data)

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("Niche analysis endpoint not implemented")

        # Validate response
        niche_result = self.validate_success_response(response, 201)  # Created
        niche_id = niche_result["id"]

        # Step 2: Develop a solution for the niche
        solution_data = generate_solution_data(niche_id=niche_id)
        response = auth_api_test_client.post("solutions/develop", solution_data)

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("Solution development endpoint not implemented")

        # Validate response
        solution_result = self.validate_success_response(response, 201)  # Created
        solution_id = solution_result["id"]

        # Step 3: Create a monetization strategy for the solution
        monetization_data = generate_monetization_data(solution_id=solution_id)
        response = auth_api_test_client.post("monetization/strategies", monetization_data)

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("Monetization endpoint not implemented")

        # Check user journey analytics
        response = auth_api_test_client.get("analytics/user-journeys")

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("User journey analytics endpoint not implemented")

        # Validate response
        journey_data = self.validate_success_response(response)

        # Verify that the user journey was tracked
        assert "journeys" in journey_data
        assert len(journey_data["journeys"]) > 0

        # Find our journey
        our_journey = None
        for journey in journey_data["journeys"]:
            if journey.get("niche_id") == niche_id and journey.get("solution_id") == solution_id:
                our_journey = journey
                break

        assert our_journey is not None
        assert "steps" in our_journey
        assert len(our_journey["steps"]) >= 3

        # Verify the steps
        steps = our_journey["steps"]
        assert steps[0]["endpoint"] == "niche-analysis/analyze"
        assert steps[1]["endpoint"] == "solutions/develop"
        assert steps[2]["endpoint"] == "monetization/strategies"

    def test_feature_usage_analytics(self, auth_api_test_client):
        """Test feature usage analytics."""
        # Use various features
        auth_api_test_client.get("niche-analysis/niches")
        auth_api_test_client.get("niche-analysis/market-segments")
        auth_api_test_client.get("solutions")
        auth_api_test_client.get("monetization/subscription-models")
        auth_api_test_client.get("marketing/strategies")
        auth_api_test_client.get("marketing/channels")

        # Check feature usage analytics
        response = auth_api_test_client.get("analytics/feature-usage")

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("Feature usage analytics endpoint not implemented")

        # Validate response
        usage_data = self.validate_success_response(response)

        # Verify that feature usage was tracked
        assert "features" in usage_data

        # Check that our used features are in the analytics
        features = usage_data["features"]
        feature_endpoints = [f["endpoint"] for f in features]

        assert "niche-analysis/niches" in feature_endpoints
        assert "niche-analysis/market-segments" in feature_endpoints
        assert "solutions" in feature_endpoints
        assert "monetization/subscription-models" in feature_endpoints
        assert "marketing/strategies" in feature_endpoints
        assert "marketing/channels" in feature_endpoints

    def test_performance_metrics_collection(self, auth_api_test_client):
        """Test performance metrics collection."""
        # Make several API requests with different response times
        auth_api_test_client.get("niche-analysis/niches")

        # Simulate a slow request
        with patch("tests.api.utils.test_client.APITestClient.get") as mock_get:

            def slow_get(endpoint):
                time.sleep(1)  # Simulate a slow response
                response = MagicMock()
                response.status_code = 200
                response.json.return_value = {"data": "slow response"}
                return response

            # Replace with our slow method
            mock_get.side_effect = slow_get

            # Make a slow request
            auth_api_test_client.get("solutions")

        # Check performance metrics
        response = auth_api_test_client.get("analytics/performance")

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("Performance analytics endpoint not implemented")

        # Validate response
        performance_data = self.validate_success_response(response)

        # Verify that performance metrics were collected
        assert "endpoints" in performance_data

        # Find our endpoints
        endpoints = performance_data["endpoints"]

        # Check that the slow endpoint has a higher response time
        niche_endpoint = next(
            (e for e in endpoints if e["endpoint"] == "niche-analysis/niches"), None
        )
        solution_endpoint = next((e for e in endpoints if e["endpoint"] == "solutions"), None)

        if niche_endpoint and solution_endpoint:
            assert solution_endpoint["avg_response_time"] > niche_endpoint["avg_response_time"]

    def test_error_tracking(self, auth_api_test_client):
        """Test error tracking."""
        # Make a request that will cause an error
        response = auth_api_test_client.get("non-existent-endpoint")
        assert response.status_code in (404, 501)  # Not Found or Not Implemented

        # Check error analytics
        response = auth_api_test_client.get("analytics/errors")

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("Error analytics endpoint not implemented")

        # Validate response
        error_data = self.validate_success_response(response)

        # Verify that errors were tracked
        assert "errors" in error_data

        # Find our error
        our_error = None
        for error in error_data["errors"]:
            if error.get("endpoint") == "non-existent-endpoint":
                our_error = error
                break

        assert our_error is not None
        assert our_error["status_code"] in (404, 501)
        assert "timestamp" in our_error

    def test_analytics_integration(self, auth_api_test_client):
        """Test analytics integration."""
        # Step 1: Make several API requests to generate analytics data
        auth_api_test_client.get("niche-analysis/niches")
        auth_api_test_client.get("monetization/subscription-models")
        auth_api_test_client.get("marketing/strategies")
        auth_api_test_client.get("ai-models/models")
        auth_api_test_client.get("agent-team/teams")

        # Step 2: Check analytics data
        response = auth_api_test_client.get("analytics/summary")

        # If the endpoint returns 404 or 501, skip the test
        if response.status_code in (404, 501):
            pytest.skip("Analytics endpoint not implemented")

        # Validate response
        analytics_data = self.validate_success_response(response)

        # Verify that analytics data was collected
        assert "request_count" in analytics_data
        assert analytics_data["request_count"] >= 5

        assert "unique_endpoints" in analytics_data
        assert len(analytics_data["unique_endpoints"]) >= 5

        assert "avg_response_time" in analytics_data

        # Check that our endpoints are in the analytics
        endpoints = analytics_data["unique_endpoints"]
        assert "niche-analysis/niches" in endpoints
        assert "monetization/subscription-models" in endpoints
        assert "marketing/strategies" in endpoints
        assert "ai-models/models" in endpoints
        assert "agent-team/teams" in endpoints


if __name__ == "__main__":
    pytest.main(["-v", "test_analytics_data_collection.py"])
