"""
Tests for the API key API.

This module contains tests for the API key API endpoints.
"""

import pytest
from typing import Dict, Any, List
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_id, generate_api_key_data
from tests.api.utils.test_validators import (
    validate_status_code,
    validate_json_response,
    validate_error_response,
    validate_success_response,
    validate_paginated_response,
    validate_bulk_response,
    validate_field_exists,
    validate_field_equals,
    validate_field_type,
    validate_field_not_empty,
    validate_list_not_empty,
    validate_list_length,
    validate_list_min_length,
    validate_list_max_length,
    validate_list_contains,
    validate_list_contains_dict_with_field,
)


class TestAPIKeyAPI:
    """Tests for the API key API."""

    def test_create_api_key(self, auth_api_test_client: APITestClient):
        """Test creating an API key."""
        # Generate test data
        data = generate_api_key_data()

        # Make request
        response = auth_api_test_client.post("api-keys", data)

        # Validate response
        result = validate_success_response(response, 201)  # Created

        # Validate fields
        validate_field_exists(result, "id")
        validate_field_type(result, "id", str)
        validate_field_not_empty(result, "id")
        validate_field_exists(result, "name")
        validate_field_equals(result, "name", data["name"])
        validate_field_exists(result, "description")
        validate_field_equals(result, "description", data["description"])
        validate_field_exists(result, "permissions")
        validate_field_type(result, "permissions", list)
        validate_field_exists(result, "key")
        validate_field_type(result, "key", str)
        validate_field_not_empty(result, "key")
        validate_field_exists(result, "expires_at")
        validate_field_type(result, "expires_at", str)
        validate_field_exists(result, "created_at")
        validate_field_type(result, "created_at", str)

    def test_get_api_keys(self, auth_api_test_client: APITestClient):
        """Test getting all API keys."""
        # Make request
        response = auth_api_test_client.get("api-keys")

        # Validate response
        result = validate_paginated_response(response)

        # Validate items
        validate_field_type(result, "items", list)

        # API key values should not be returned in the list
        if result["items"]:
            assert "key" not in result["items"][0]

    def test_get_api_key(self, auth_api_test_client: APITestClient):
        """Test getting a specific API key."""
        # Generate a random ID
        key_id = generate_id()

        # Make request
        response = auth_api_test_client.get(f"api-keys/{key_id}")

        # This might return 404 if the key doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", key_id)
            validate_field_exists(result, "name")
            validate_field_type(result, "name", str)
            validate_field_exists(result, "description")
            validate_field_type(result, "description", str)
            validate_field_exists(result, "permissions")
            validate_field_type(result, "permissions", list)
            validate_field_exists(result, "expires_at")
            validate_field_type(result, "expires_at", str)
            validate_field_exists(result, "created_at")
            validate_field_type(result, "created_at", str)

            # API key value should not be returned
            assert "key" not in result

    def test_update_api_key(self, auth_api_test_client: APITestClient):
        """Test updating an API key."""
        # Generate a random ID
        key_id = generate_id()

        # Generate test data
        data = {
            "name": "Updated Key",
            "description": "Updated description",
            "permissions": ["read", "write"],
        }

        # Make request
        response = auth_api_test_client.put(f"api-keys/{key_id}", data)

        # This might return 404 if the key doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", key_id)
            validate_field_exists(result, "name")
            validate_field_equals(result, "name", data["name"])
            validate_field_exists(result, "description")
            validate_field_equals(result, "description", data["description"])
            validate_field_exists(result, "permissions")
            validate_field_type(result, "permissions", list)
            for permission in data["permissions"]:
                validate_list_contains(result["permissions"], permission)

    def test_delete_api_key(self, auth_api_test_client: APITestClient):
        """Test deleting an API key."""
        # Generate a random ID
        key_id = generate_id()

        # Make request
        response = auth_api_test_client.delete(f"api-keys/{key_id}")

        # This might return 404 if the key doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            validate_success_response(response, 204)  # No Content

    def test_revoke_api_key(self, auth_api_test_client: APITestClient):
        """Test revoking an API key."""
        # Generate a random ID
        key_id = generate_id()

        # Make request
        response = auth_api_test_client.post(f"api-keys/{key_id}/revoke")

        # This might return 404 if the key doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            validate_success_response(response)

    def test_regenerate_api_key(self, auth_api_test_client: APITestClient):
        """Test regenerating an API key."""
        # Generate a random ID
        key_id = generate_id()

        # Make request
        response = auth_api_test_client.post(f"api-keys/{key_id}/regenerate")

        # This might return 404 if the key doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", key_id)
            validate_field_exists(result, "key")
            validate_field_type(result, "key", str)
            validate_field_not_empty(result, "key")

    def test_get_api_key_usage(self, auth_api_test_client: APITestClient):
        """Test getting API key usage."""
        # Generate a random ID
        key_id = generate_id()

        # Make request
        response = auth_api_test_client.get(f"api-keys/{key_id}/usage")

        # This might return 404 if the key doesn't exist, which is fine for testing
        if response.status_code == 404:
            validate_error_response(response, 404)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "id")
            validate_field_equals(result, "id", key_id)
            validate_field_exists(result, "request_count")
            validate_field_type(result, "request_count", int)
            validate_field_exists(result, "last_used_at")
            validate_field_type(result, "last_used_at", (str, type(None)))
            validate_field_exists(result, "endpoints")
            validate_field_type(result, "endpoints", list)

    def test_unauthorized_access(self, api_test_client: APITestClient):
        """Test unauthorized access to API key endpoints."""
        # Make request without authentication
        response = api_test_client.get("api-keys")

        # Validate error response
        validate_error_response(response, 401)  # Unauthorized

    def test_invalid_api_key_request(self, auth_api_test_client: APITestClient):
        """Test invalid API key request."""
        # Make request with invalid data
        response = auth_api_test_client.post("api-keys", {})

        # Validate error response
        validate_error_response(response, 422)  # Unprocessable Entity

    def test_nonexistent_api_key(self, auth_api_test_client: APITestClient):
        """Test getting a nonexistent API key."""
        # Generate a random ID that is unlikely to exist
        key_id = "nonexistent-" + generate_id()

        # Make request
        response = auth_api_test_client.get(f"api-keys/{key_id}")

        # Validate error response
        validate_error_response(response, 404)  # Not Found
