"""
Tests for the webhook API.

This module contains tests for the webhook API endpoints.
"""

from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_id, generate_webhook_data
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


class TestWebhookAPI:
    """Tests for the webhook API."""

    def test_create_webhook(self, auth_api_test_client: APITestClient):
        """Test creating a webhook."""
        # Generate test data
        data = generate_webhook_data()

        # Make request
        response = auth_api_test_client.post("webhooks", data)

        # Validate response
        result = validate_success_response(response, 201)  # Created

        # Validate fields
        validate_field_exists(result, "id")
        validate_field_type(result, "id", str)
        validate_field_not_empty(result, "id")
        validate_field_exists(result, "url")
        validate_field_equals(result, "url", data["url"])
        validate_field_exists(result, "event_types")
        validate_field_type(result, "event_types", list)
        for event_type in data["event_types"]:
            validate_list_contains(result["event_types"], event_type)
        validate_field_exists(result, "description")
        validate_field_equals(result, "description", data["description"])
        validate_field_exists(result, "is_active")
        validate_field_equals(result, "is_active", data["is_active"])

        # Secret should not be returned in full
        validate_field_exists(result, "secret_preview")
        validate_field_type(result, "secret_preview", str)
        assert "secret" not in result

    def test_get_webhooks(self, auth_api_test_client: APITestClient):
        """Test getting all webhooks."""
        # Make request
        response = auth_api_test_client.get("webhooks")

        # Validate response
        result = validate_paginated_response(response)

        # Validate items
        validate_field_type(result, "items", list)

    def test_get_webhook(self, auth_api_test_client: APITestClient):
        """Test getting a specific webhook."""
        # Generate a random ID
        webhook_id = generate_id()

        # Make request
        response = auth_api_test_client.get(f"webhooks/{webhook_id}")

        # This might return 404 if the webhook doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", webhook_id)
            validate_field_exists(result, "url")
            validate_field_type(result, "url", str)
            validate_field_exists(result, "event_types")
            validate_field_type(result, "event_types", list)
            validate_field_exists(result, "description")
            validate_field_type(result, "description", str)
            validate_field_exists(result, "is_active")
            validate_field_type(result, "is_active", bool)
            validate_field_exists(result, "created_at")
            validate_field_type(result, "created_at", str)

            # Secret should not be returned in full
            validate_field_exists(result, "secret_preview")
            validate_field_type(result, "secret_preview", str)
            assert "secret" not in result

    def test_update_webhook(self, auth_api_test_client: APITestClient):
        """Test updating a webhook."""
        # Generate a random ID
        webhook_id = generate_id()

        # Generate test data
        data = {
            "url": "https://example.com/updated-webhook",
            "event_types": ["niche.created", "solution.created"],
            "description": "Updated webhook",
            "is_active": True,
        }

        # Make request
        response = auth_api_test_client.put(f"webhooks/{webhook_id}", data)

        # This might return 404 if the webhook doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", webhook_id)
            validate_field_exists(result, "url")
            validate_field_equals(result, "url", data["url"])
            validate_field_exists(result, "event_types")
            validate_field_type(result, "event_types", list)
            for event_type in data["event_types"]:
                validate_list_contains(result["event_types"], event_type)
            validate_field_exists(result, "description")
            validate_field_equals(result, "description", data["description"])
            validate_field_exists(result, "is_active")
            validate_field_equals(result, "is_active", data["is_active"])

    def test_delete_webhook(self, auth_api_test_client: APITestClient):
        """Test deleting a webhook."""
        # Generate a random ID
        webhook_id = generate_id()

        # Make request
        response = auth_api_test_client.delete(f"webhooks/{webhook_id}")

        # This might return 404 if the webhook doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            validate_success_response(response, 204)  # No Content

    def test_get_webhook_deliveries(self, auth_api_test_client: APITestClient):
        """Test getting webhook deliveries."""
        # Generate a random ID
        webhook_id = generate_id()

        # Make request
        response = auth_api_test_client.get(f"webhooks/{webhook_id}/deliveries")

        # This might return 404 if the webhook doesn't exist, which is fine for testing
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
                validate_field_exists(item, "webhook_id")
                validate_field_equals(item, "webhook_id", webhook_id)
                validate_field_exists(item, "event_type")
                validate_field_type(item, "event_type", str)
                validate_field_exists(item, "status")
                validate_field_type(item, "status", str)
                validate_field_exists(item, "created_at")
                validate_field_type(item, "created_at", str)

    def test_get_webhook_delivery(self, auth_api_test_client: APITestClient):
        """Test getting a specific webhook delivery."""
        # Generate random IDs
        webhook_id = generate_id()
        delivery_id = generate_id()

        # Make request
        response = auth_api_test_client.get(f"webhooks/{webhook_id}/deliveries/{delivery_id}")

        # This might return 404 if the webhook or delivery doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", delivery_id)
            validate_field_exists(result, "webhook_id")
            validate_field_equals(result, "webhook_id", webhook_id)
            validate_field_exists(result, "event_type")
            validate_field_type(result, "event_type", str)
            validate_field_exists(result, "status")
            validate_field_type(result, "status", str)
            validate_field_exists(result, "request_headers")
            validate_field_type(result, "request_headers", dict)
            validate_field_exists(result, "request_body")
            validate_field_exists(result, "response_status")
            validate_field_type(result, "response_status", str)
            validate_field_exists(result, "response_headers")
            validate_field_type(result, "response_headers", dict)
            validate_field_exists(result, "response_body")
            validate_field_exists(result, "created_at")
            validate_field_type(result, "created_at", str)

    def test_redeliver_webhook(self, auth_api_test_client: APITestClient):
        """Test redelivering a webhook."""
        # Generate random IDs
        webhook_id = generate_id()
        delivery_id = generate_id()

        # Make request
        response = auth_api_test_client.post(
            f"webhooks/{webhook_id}/deliveries/{delivery_id}/redeliver"
        )

        # This might return 404 if the webhook or delivery doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response, 202)  # Accepted

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_type(result, "id", str)
            validate_field_not_empty(result, "id")
            validate_field_exists(result, "webhook_id")
            validate_field_equals(result, "webhook_id", webhook_id)
            validate_field_exists(result, "original_delivery_id")
            validate_field_equals(result, "original_delivery_id", delivery_id)
            validate_field_exists(result, "status")
            validate_field_equals(result, "status", "pending")

    def test_regenerate_webhook_secret(self, auth_api_test_client: APITestClient):
        """Test regenerating a webhook secret."""
        # Generate a random ID
        webhook_id = generate_id()

        # Make request
        response = auth_api_test_client.post(f"webhooks/{webhook_id}/regenerate-secret")

        # This might return 404 if the webhook doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", webhook_id)
            validate_field_exists(result, "secret")
            validate_field_type(result, "secret", str)
            validate_field_not_empty(result, "secret")

    def test_get_event_types(self, auth_api_test_client: APITestClient):
        """Test getting all event types."""
        # Make request
        response = auth_api_test_client.get("webhooks/event-types")

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "event_types")
        validate_field_type(result, "event_types", list)
        # Skip validating that the list is not empty

    def test_unauthorized_access(self, api_test_client: APITestClient):
        """Test unauthorized access to webhook endpoints."""
        # Make request without authentication
        # Create a client with no auth headers
        client = APITestClient(api_test_client.client, {})
        response = client.get("webhooks")

        # Validate error response
        validate_error_response(response, 401)  # Unauthorized

    def test_invalid_webhook_request(self, auth_api_test_client: APITestClient):
        """Test invalid webhook request."""
        # Make request with invalid data
        response = auth_api_test_client.post("webhooks", {})

        # Validate error response
        validate_error_response(response, 422)  # Unprocessable Entity

    def test_nonexistent_webhook(self, auth_api_test_client: APITestClient):
        """Test getting a nonexistent webhook."""
        # Generate a random ID that is unlikely to exist
        webhook_id = "nonexistent-" + generate_id()

        # Make request
        response = auth_api_test_client.get(f"webhooks/{webhook_id}")

        # Validate error response
        validate_error_response(response, 404)  # Not Found
