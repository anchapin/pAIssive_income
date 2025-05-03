"""
Tests for the monetization API.

This module contains tests for the monetization API endpoints.
"""

from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import (
    generate_id,
    generate_monetization_data,
    generate_revenue_projection_data,
)
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


class TestMonetizationAPI:
    """Tests for the monetization API."""

    def test_create_subscription_model(self, api_test_client: APITestClient):
        """Test creating a subscription model."""
        # Generate test data
        data = generate_monetization_data()

        # Make request
        response = api_test_client.post("monetization / subscription - models", data)

        # Validate response
        result = validate_success_response(response, 201)  # Created

        # Validate fields
        validate_field_exists(result, "id")
        validate_field_type(result, "id", str)
        validate_field_not_empty(result, "id")
        validate_field_exists(result, "subscription_type")
        validate_field_equals(result, "subscription_type", data["subscription_type"])
        validate_field_exists(result, "billing_period")
        validate_field_equals(result, "billing_period", data["billing_period"])
        validate_field_exists(result, "base_price")
        assert isinstance(result["base_price"], (int, float))
        validate_field_exists(result, "features")
        validate_field_type(result, "features", list)
        validate_field_exists(result, "tiers")
        validate_field_type(result, "tiers", list)

    def test_get_subscription_models(self, api_test_client: APITestClient):
        """Test getting all subscription models."""
        # Make request
        response = api_test_client.get("monetization / subscription - models")

        # Validate response
        result = validate_paginated_response(response)

        # Validate items
        validate_field_type(result, "items", list)

    def test_get_subscription_model(self, api_test_client: APITestClient):
        """Test getting a specific subscription model."""
        # Generate a random ID
        model_id = generate_id()

        # Make request
        response = api_test_client.get(f"monetization / subscription - models/{model_id}")

        # This might return 404 if the model doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", model_id)
            validate_field_exists(result, "subscription_type")
            validate_field_type(result, "subscription_type", str)
            validate_field_exists(result, "billing_period")
            validate_field_type(result, "billing_period", str)
            validate_field_exists(result, "base_price")
            assert isinstance(result["base_price"], (int, float))
            validate_field_exists(result, "features")
            validate_field_type(result, "features", list)
            validate_field_exists(result, "tiers")
            validate_field_type(result, "tiers", list)

    def test_update_subscription_model(self, api_test_client: APITestClient):
        """Test updating a subscription model."""
        # Generate a random ID
        model_id = generate_id()

        # Generate test data
        data = generate_monetization_data()

        # Make request
        response = api_test_client.put(f"monetization / subscription - models/{model_id}", data)

        # This might return 404 if the model doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", model_id)
            validate_field_exists(result, "subscription_type")
            validate_field_equals(result, "subscription_type", data["subscription_type"])
            validate_field_exists(result, "billing_period")
            validate_field_equals(result, "billing_period", data["billing_period"])
            validate_field_exists(result, "base_price")
            assert isinstance(result["base_price"], (int, float))
            validate_field_exists(result, "features")
            validate_field_type(result, "features", list)
            validate_field_exists(result, "tiers")
            validate_field_type(result, "tiers", list)

    def test_delete_subscription_model(self, api_test_client: APITestClient):
        """Test deleting a subscription model."""
        # Generate a random ID
        model_id = generate_id()

        # Make request
        response = api_test_client.delete(f"monetization / subscription - models/{model_id}")

        # This might return 404 if the model doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            validate_success_response(response, 204)  # No Content

    def test_create_revenue_projection(self, api_test_client: APITestClient):
        """Test creating a revenue projection."""
        # Generate test data
        data = generate_revenue_projection_data()

        # Make request
        response = api_test_client.post("monetization / revenue - projections", data)

        # Validate response
        result = validate_success_response(response, 201)  # Created

        # Validate fields
        validate_field_exists(result, "id")
        validate_field_type(result, "id", str)
        validate_field_not_empty(result, "id")
        validate_field_exists(result, "subscription_model_id")
        validate_field_equals(result, "subscription_model_id", data["subscription_model_id"])
        validate_field_exists(result, "initial_users")
        validate_field_equals(result, "initial_users", data["initial_users"])
        validate_field_exists(result, "growth_rate")
        assert isinstance(result["growth_rate"], (int, float))
        validate_field_exists(result, "churn_rate")
        assert isinstance(result["churn_rate"], (int, float))
        validate_field_exists(result, "time_period_months")
        validate_field_equals(result, "time_period_months", data["time_period_months"])
        validate_field_exists(result, "projections")
        validate_field_type(result, "projections", list)

    def test_get_revenue_projections(self, api_test_client: APITestClient):
        """Test getting all revenue projections."""
        # Make request
        response = api_test_client.get("monetization / revenue - projections")

        # Validate response
        result = validate_paginated_response(response)

        # Validate items
        validate_field_type(result, "items", list)

    def test_get_revenue_projection(self, api_test_client: APITestClient):
        """Test getting a specific revenue projection."""
        # Generate a random ID
        projection_id = generate_id()

        # Make request
        response = api_test_client.get(f"monetization / revenue - projections/{projection_id}")

        # This might return 404 if the projection doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", projection_id)
            validate_field_exists(result, "subscription_model_id")
            validate_field_type(result, "subscription_model_id", str)
            validate_field_exists(result, "initial_users")
            validate_field_type(result, "initial_users", int)
            validate_field_exists(result, "growth_rate")
            assert isinstance(result["growth_rate"], (int, float))
            validate_field_exists(result, "churn_rate")
            assert isinstance(result["churn_rate"], (int, float))
            validate_field_exists(result, "time_period_months")
            validate_field_type(result, "time_period_months", int)
            validate_field_exists(result, "projections")
            validate_field_type(result, "projections", list)

    def test_bulk_create_subscription_models(self, api_test_client: APITestClient):
        """Test bulk creating subscription models."""
        # Generate test data
        models = [generate_monetization_data() for _ in range(3)]

        # Make request
        response = api_test_client.bulk_create("monetization / subscription - models", models)

        # Validate response
        result = validate_bulk_response(response, 201)  # Created

        # Validate stats
        validate_field_equals(result["stats"], "total", 3)

    def test_filter_subscription_models(self, api_test_client: APITestClient):
        """Test filtering subscription models."""
        # Make request with filter
        response = api_test_client.get(
            "monetization / subscription - models",
            params={
                "filter": "subscription_type:eq:freemium",
                "sort": "base_price:asc",
                "page": 1,
                "page_size": 10,
            },
        )

        # Validate response
        result = validate_paginated_response(response)

        # Validate items
        validate_field_type(result, "items", list)

        # If there are items, validate that they match the filter
        if result["items"]:
            for item in result["items"]:
                validate_field_exists(item, "subscription_type")
                validate_field_equals(item, "subscription_type", "freemium")

    def test_invalid_subscription_model_request(self, api_test_client: APITestClient):
        """Test invalid subscription model request."""
        # Make request with invalid data
        response = api_test_client.post("monetization / subscription - models", {})

        # Validate error response
        validate_error_response(response, 422)  # Unprocessable Entity

    def test_nonexistent_subscription_model(self, api_test_client: APITestClient):
        """Test getting a nonexistent subscription model."""
        # Generate a random ID that is unlikely to exist
        model_id = "nonexistent - " + generate_id()

        # Make request
        response = api_test_client.get(f"monetization / subscription - models/{model_id}")

        # Validate error response
        validate_error_response(response, 404)  # Not Found

    def test_track_metered_usage(self, api_test_client: APITestClient):
        """Test tracking metered usage."""
        # Generate test data
        data = {
            "subscription_id": generate_id(),
            "metric": "api_calls",
            "value": 100,
            "timestamp": "2025 - 04 - 29T10:00:00Z",
        }

        # Make request
        response = api_test_client.post("monetization / usage / track", data)

        # Validate response
        result = validate_success_response(response, 201)  # Created

        # Validate fields
        validate_field_exists(result, "id")
        validate_field_type(result, "id", str)
        validate_field_not_empty(result, "id")
        validate_field_exists(result, "subscription_id")
        validate_field_equals(result, "subscription_id", data["subscription_id"])
        validate_field_exists(result, "metric")
        validate_field_equals(result, "metric", data["metric"])
        validate_field_exists(result, "value")
        validate_field_equals(result, "value", data["value"])
        validate_field_exists(result, "timestamp")
        validate_field_equals(result, "timestamp", data["timestamp"])

    def test_get_metered_usage(self, api_test_client: APITestClient):
        """Test getting metered usage."""
        # Generate a subscription ID
        subscription_id = generate_id()

        # Make request
        response = api_test_client.get(
            f"monetization / usage/{subscription_id}",
            params={
                "metric": "api_calls",
                "start_date": "2025 - 04 - 01T00:00:00Z",
                "end_date": "2025 - 04 - 30T23:59:59Z",
            },
        )

        # This might return 404 if the subscription doesn't exist
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "subscription_id")
            validate_field_equals(result, "subscription_id", subscription_id)
            validate_field_exists(result, "metric")
            validate_field_equals(result, "metric", "api_calls")
            validate_field_exists(result, "total_usage")
            validate_field_type(result, "total_usage", int)
            validate_field_exists(result, "usage_periods")
            validate_field_type(result, "usage_periods", list)

    def test_calculate_metered_billing(self, api_test_client: APITestClient):
        """Test calculating metered billing."""
        # Generate a subscription ID
        subscription_id = generate_id()

        # Make request
        response = api_test_client.get(
            f"monetization / billing/{subscription_id}/calculate",
            params={"billing_period": "2025 - 04"},
        )

        # This might return 404 if the subscription doesn't exist
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "subscription_id")
            validate_field_equals(result, "subscription_id", subscription_id)
            validate_field_exists(result, "billing_period")
            validate_field_equals(result, "billing_period", "2025 - 04")
            validate_field_exists(result, "total_amount")
            assert isinstance(result["total_amount"], (int, float))
            validate_field_exists(result, "currency")
            validate_field_type(result, "currency", str)
            validate_field_exists(result, "line_items")
            validate_field_type(result, "line_items", list)

            # Validate line items if they exist
            if result["line_items"]:
                item = result["line_items"][0]
                validate_field_exists(item, "metric")
                validate_field_type(item, "metric", str)
                validate_field_exists(item, "usage")
                validate_field_type(item, "usage", int)
                validate_field_exists(item, "rate")
                assert isinstance(item["rate"], (int, float))
                validate_field_exists(item, "amount")
                assert isinstance(item["amount"], (int, float))

    def test_test_billing_threshold_alerts(self, api_test_client: APITestClient):
        """Test billing threshold alerts."""
        # Generate test data
        data = {
            "subscription_id": generate_id(),
            "metric": "api_calls",
            "threshold": 1000,
            "alert_type": "usage",
            "notification_channels": ["email", "webhook"],
        }

        # Make request
        response = api_test_client.post("monetization / billing / alerts", data)

        # Validate response
        result = validate_success_response(response, 201)  # Created

        # Validate fields
        validate_field_exists(result, "id")
        validate_field_type(result, "id", str)
        validate_field_not_empty(result, "id")
        validate_field_exists(result, "subscription_id")
        validate_field_equals(result, "subscription_id", data["subscription_id"])
        validate_field_exists(result, "metric")
        validate_field_equals(result, "metric", data["metric"])
        validate_field_exists(result, "threshold")
        validate_field_equals(result, "threshold", data["threshold"])
        validate_field_exists(result, "alert_type")
        validate_field_equals(result, "alert_type", data["alert_type"])
        validate_field_exists(result, "notification_channels")
        validate_field_type(result, "notification_channels", list)
        validate_field_equals(result, "status", "active")

    def test_get_billing_alerts(self, api_test_client: APITestClient):
        """Test getting billing alerts."""
        # Generate a subscription ID
        subscription_id = generate_id()

        # Make request
        response = api_test_client.get(f"monetization / billing/{subscription_id}/alerts")

        # This might return 404 if the subscription doesn't exist
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_paginated_response(response)

            # Validate items
            validate_field_type(result, "items", list)

            # If there are items, validate their structure
            if result["items"]:
                item = result["items"][0]
                validate_field_exists(item, "id")
                validate_field_type(item, "id", str)
                validate_field_exists(item, "subscription_id")
                validate_field_equals(item, "subscription_id", subscription_id)
                validate_field_exists(item, "metric")
                validate_field_type(item, "metric", str)
                validate_field_exists(item, "threshold")
                assert isinstance(item["threshold"], (int, float))
                validate_field_exists(item, "alert_type")
                validate_field_type(item, "alert_type", str)
                validate_field_exists(item, "status")
                validate_field_type(item, "status", str)
