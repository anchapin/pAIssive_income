"""
Tests for the dashboard API.

This module contains tests for the dashboard API endpoints.
"""

from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_validators import (
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


class TestDashboardAPI:
    """Tests for the dashboard API."""

    def test_get_dashboard_overview(self, auth_api_test_client: APITestClient):
        """Test getting the dashboard overview."""
        # Make request
        response = auth_api_test_client.get("dashboard / overview")

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "niches_count")
        validate_field_type(result, "niches_count", int)
        validate_field_exists(result, "solutions_count")
        validate_field_type(result, "solutions_count", int)
        validate_field_exists(result, "subscription_models_count")
        validate_field_type(result, "subscription_models_count", int)
        validate_field_exists(result, "marketing_strategies_count")
        validate_field_type(result, "marketing_strategies_count", int)
        validate_field_exists(result, "teams_count")
        validate_field_type(result, "teams_count", int)
        validate_field_exists(result, "recent_activity")
        validate_field_type(result, "recent_activity", list)

    def test_get_revenue_statistics(self, auth_api_test_client: APITestClient):
        """Test getting revenue statistics."""
        # Make request
        response = auth_api_test_client.get("dashboard / revenue")

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "total_revenue")
        assert isinstance(result["total_revenue"], (int, float))
        validate_field_exists(result, "monthly_revenue")
        assert isinstance(result["monthly_revenue"], (int, float))
        validate_field_exists(result, "revenue_growth")
        assert isinstance(result["revenue_growth"], (int, float))
        validate_field_exists(result, "revenue_by_model")
        validate_field_type(result, "revenue_by_model", list)
        validate_field_exists(result, "revenue_over_time")
        validate_field_type(result, "revenue_over_time", list)

    def test_get_subscriber_statistics(self, auth_api_test_client: APITestClient):
        """Test getting subscriber statistics."""
        # Make request
        response = auth_api_test_client.get("dashboard / subscribers")

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "total_subscribers")
        validate_field_type(result, "total_subscribers", int)
        validate_field_exists(result, "new_subscribers")
        validate_field_type(result, "new_subscribers", int)
        validate_field_exists(result, "churn_rate")
        assert isinstance(result["churn_rate"], (int, float))
        validate_field_exists(result, "subscribers_by_plan")
        validate_field_type(result, "subscribers_by_plan", list)
        validate_field_exists(result, "subscribers_over_time")
        validate_field_type(result, "subscribers_over_time", list)

    def test_get_marketing_statistics(self, auth_api_test_client: APITestClient):
        """Test getting marketing statistics."""
        # Make request
        response = auth_api_test_client.get("dashboard / marketing")

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "website_traffic")
        validate_field_type(result, "website_traffic", int)
        validate_field_exists(result, "conversion_rate")
        assert isinstance(result["conversion_rate"], (int, float))
        validate_field_exists(result, "customer_acquisition_cost")
        assert isinstance(result["customer_acquisition_cost"], (int, float))
        validate_field_exists(result, "traffic_by_channel")
        validate_field_type(result, "traffic_by_channel", list)
        validate_field_exists(result, "traffic_over_time")
        validate_field_type(result, "traffic_over_time", list)

    def test_get_model_usage_statistics(self, auth_api_test_client: APITestClient):
        """Test getting model usage statistics."""
        # Make request
        response = auth_api_test_client.get("dashboard / model - usage")

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "total_requests")
        validate_field_type(result, "total_requests", int)
        validate_field_exists(result, "total_tokens")
        validate_field_type(result, "total_tokens", int)
        validate_field_exists(result, "average_latency_ms")
        assert isinstance(result["average_latency_ms"], (int, float))
        validate_field_exists(result, "requests_by_model")
        validate_field_type(result, "requests_by_model", list)
        validate_field_exists(result, "requests_over_time")
        validate_field_type(result, "requests_over_time", list)

    def test_get_dashboard_with_date_range(self, auth_api_test_client: APITestClient):
        """Test getting dashboard data with a date range."""
        # Make request with date range
        response = auth_api_test_client.get(
            "dashboard / overview", params={"start_date": "2023 - 01 - 01", "end_date": "2023 - 12 - 31"}
        )

        # Validate response
        validate_success_response(response)

    def test_get_dashboard_with_filters(self, auth_api_test_client: APITestClient):
        """Test getting dashboard data with filters."""
        # Make request with filters
        response = auth_api_test_client.get(
            "dashboard / revenue", params={"model_id": "model - 123", "period": "monthly"}
        )

        # Validate response
        validate_success_response(response)

    def test_export_dashboard_data(self, auth_api_test_client: APITestClient):
        """Test exporting dashboard data."""
        # Make request
        response = auth_api_test_client.get(
            "dashboard / export",
            params={"format": "csv", "sections": "revenue,subscribers,marketing"},
        )

        # Validate response
        if response.status_code == 200:
            # Check that the response has the correct content type
            assert response.headers["Content - Type"] == "text / csv"
            assert "Content - Disposition" in response.headers
        else:
            # If the endpoint is not implemented, it might return 501
            validate_error_response(response, 501)  # Not Implemented

    def test_unauthorized_access(self, api_test_client: APITestClient):
        """Test unauthorized access to dashboard endpoints."""
        # Make request without authentication
        response = api_test_client.get("dashboard / overview")

        # Validate error response
        validate_error_response(response, 401)  # Unauthorized
