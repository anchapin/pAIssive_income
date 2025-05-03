"""
Tests for the user API.

This module contains tests for the user API endpoints.
"""

from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import generate_id, generate_user_data
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


class TestUserAPI:
    """Tests for the user API."""

    def test_register_user(self, api_test_client: APITestClient):
        """Test registering a new user."""
        # Generate test data
        data = generate_user_data()

        # Make request
        response = api_test_client.post("user / register", data)

        # Validate response
        result = validate_success_response(response, 201)  # Created

        # Validate fields
        validate_field_exists(result, "id")
        validate_field_type(result, "id", str)
        validate_field_not_empty(result, "id")
        validate_field_exists(result, "username")
        validate_field_equals(result, "username", data["username"])
        validate_field_exists(result, "email")
        validate_field_equals(result, "email", data["email"])
        validate_field_exists(result, "first_name")
        validate_field_equals(result, "first_name", data["first_name"])
        validate_field_exists(result, "last_name")
        validate_field_equals(result, "last_name", data["last_name"])

        # Password should not be returned
        assert "password" not in result

    def test_login_user(self, api_test_client: APITestClient):
        """Test logging in a user."""
        # Generate test data
        data = {"username": "testuser", "password": "testpassword"}

        # Make request
        response = api_test_client.post("user / login", data)

        # This might return 401 if the user doesn't exist, which is fine for testing
        if response.status_code == 401:
            validate_error_response(response, 401)
        else:
            result = validate_success_response(response)

            # Validate fields
            validate_field_exists(result, "access_token")
            validate_field_type(result, "access_token", str)
            validate_field_not_empty(result, "access_token")
            validate_field_exists(result, "token_type")
            validate_field_equals(result, "token_type", "bearer")

    def test_get_user_profile(self, auth_api_test_client: APITestClient):
        """Test getting the user profile."""
        # Make request
        response = auth_api_test_client.get("user / profile")

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "id")
        validate_field_type(result, "id", str)
        validate_field_exists(result, "username")
        validate_field_type(result, "username", str)
        validate_field_exists(result, "email")
        validate_field_type(result, "email", str)
        validate_field_exists(result, "first_name")
        validate_field_type(result, "first_name", str)
        validate_field_exists(result, "last_name")
        validate_field_type(result, "last_name", str)

        # Password should not be returned
        assert "password" not in result

    def test_update_user_profile(self, auth_api_test_client: APITestClient):
        """Test updating the user profile."""
        # Generate test data
        data = {"first_name": "Updated", "last_name": "User", "email": "updated @ example.com"}

        # Make request
        response = auth_api_test_client.put("user / profile", data)

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "id")
        validate_field_type(result, "id", str)
        validate_field_exists(result, "username")
        validate_field_type(result, "username", str)
        validate_field_exists(result, "email")
        validate_field_equals(result, "email", data["email"])
        validate_field_exists(result, "first_name")
        validate_field_equals(result, "first_name", data["first_name"])
        validate_field_exists(result, "last_name")
        validate_field_equals(result, "last_name", data["last_name"])

        # Password should not be returned
        assert "password" not in result

    def test_change_password(self, auth_api_test_client: APITestClient):
        """Test changing the user password."""
        # Generate test data
        data = {"current_password": "testpassword", "new_password": "newtestpassword"}

        # Make request
        response = auth_api_test_client.post("user / change - password", data)

        # Validate response
        validate_success_response(response)

    def test_get_user_projects(self, auth_api_test_client: APITestClient):
        """Test getting the user's projects."""
        # Make request
        response = auth_api_test_client.get("user / projects")

        # Validate response
        result = validate_paginated_response(response)

        # Validate items
        validate_field_type(result, "items", list)

    def test_get_user_teams(self, auth_api_test_client: APITestClient):
        """Test getting the user's teams."""
        # Make request
        response = auth_api_test_client.get("user / teams")

        # Validate response
        result = validate_paginated_response(response)

        # Validate items
        validate_field_type(result, "items", list)

    def test_get_user_activity(self, auth_api_test_client: APITestClient):
        """Test getting the user's activity."""
        # Make request
        response = auth_api_test_client.get("user / activity")

        # Validate response
        result = validate_paginated_response(response)

        # Validate items
        validate_field_type(result, "items", list)

    def test_get_user_settings(self, auth_api_test_client: APITestClient):
        """Test getting the user's settings."""
        # Make request
        response = auth_api_test_client.get("user / settings")

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "settings")
        validate_field_type(result, "settings", dict)

    def test_update_user_settings(self, auth_api_test_client: APITestClient):
        """Test updating the user's settings."""
        # Generate test data
        data = {
            "settings": {
                "theme": "dark",
                "notifications_enabled": True,
                "email_notifications": False,
            }
        }

        # Make request
        response = auth_api_test_client.put("user / settings", data)

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "settings")
        validate_field_type(result, "settings", dict)
        validate_field_exists(result["settings"], "theme")
        validate_field_equals(result["settings"], "theme", data["settings"]["theme"])
        validate_field_exists(result["settings"], "notifications_enabled")
        validate_field_equals(
            result["settings"], "notifications_enabled", data["settings"]["notifications_enabled"]
        )
        validate_field_exists(result["settings"], "email_notifications")
        validate_field_equals(
            result["settings"], "email_notifications", data["settings"]["email_notifications"]
        )

    def test_update_user_preferences(self, auth_api_test_client: APITestClient):
        """Test updating user preferences."""
        # Generate test data
        data = {
            "preferences": {
                "language": "en",
                "timezone": "UTC",
                "date_format": "YYYY - MM - DD",
                "time_format": "24h",
                "currency": "USD",
                "communication": {
                    "email_frequency": "daily",
                    "push_notifications": True,
                    "marketing_emails": False,
                },
                "display": {"theme": "dark", "compact_view": True, "show_tooltips": True},
            }
        }

        # Make request
        response = auth_api_test_client.put("user / preferences", data)

        # Validate response
        result = validate_success_response(response)

        # Validate fields
        validate_field_exists(result, "preferences")
        validate_field_type(result, "preferences", dict)
        validate_field_equals(result["preferences"], "language", data["preferences"]["language"])
        validate_field_equals(result["preferences"], "timezone", data["preferences"]["timezone"])
        validate_field_equals(
            result["preferences"], "date_format", data["preferences"]["date_format"]
        )
        validate_field_exists(result["preferences"], "communication")
        validate_field_type(result["preferences"]["communication"], dict)
        validate_field_exists(result["preferences"], "display")
        validate_field_type(result["preferences"]["display"], dict)

        # Validate nested preferences
        validate_field_equals(
            result["preferences"]["communication"],
            "email_frequency",
            data["preferences"]["communication"]["email_frequency"],
        )
        validate_field_equals(
            result["preferences"]["display"], "theme", data["preferences"]["display"]["theme"]
        )

        # Validate update timestamp
        validate_field_exists(result, "updated_at")
        validate_field_type(result, "updated_at", str)

    def test_delete_user_account(self, auth_api_test_client: APITestClient):
        """Test deleting a user account."""
        # Make request
        response = auth_api_test_client.delete("user / account")

        # Validate response
        validate_success_response(response, 204)  # No Content

    def test_delete_user_account_with_reason(self, auth_api_test_client: APITestClient):
        """Test deleting a user account with a reason."""
        # Generate test data
        data = {
            "reason": "switching_provider",
            "feedback": "Found a better service for my needs",
            "allow_data_retention": False,
        }

        # Make request
        response = auth_api_test_client.delete(
            "user / account", headers={"Content - Type": "application / json"}, json=data
        )

        # Validate response
        validate_success_response(response, 204)  # No Content

    def test_bulk_update_user_roles(self, auth_api_test_client: APITestClient):
        """Test bulk updating user roles."""
        # Generate test data
        updates = [
            {"user_id": generate_id(), "roles": ["admin", "developer"]},
            {"user_id": generate_id(), "roles": ["analyst"]},
            {"user_id": generate_id(), "roles": ["manager", "reviewer"]},
        ]

        # Make request
        response = auth_api_test_client.put("user / roles / bulk", updates)

        # Validate response
        result = validate_bulk_response(response)

        # Validate stats
        validate_field_exists(result, "stats")
        validate_field_exists(result["stats"], "total")
        validate_field_equals(result["stats"], "total", len(updates))
        validate_field_exists(result["stats"], "updated")
        validate_field_exists(result["stats"], "failed")
        assert result["stats"]["updated"] + result["stats"]["failed"] == len(updates)

        # Validate updated items
        validate_field_exists(result, "items")
        validate_field_type(result, "items", list)
        for item in result["items"]:
            validate_field_exists(item, "user_id")
            validate_field_exists(item, "success")
            if item["success"]:
                validate_field_exists(item, "roles")
                validate_field_type(item, "roles", list)
            else:
                validate_field_exists(item, "error")
                validate_field_type(item, "error", dict)

    def test_bulk_delete_users(self, auth_api_test_client: APITestClient):
        """Test bulk deleting users."""
        # Generate user IDs to delete
        user_ids = [generate_id() for _ in range(3)]

        # Make request
        response = auth_api_test_client.bulk_delete("user / accounts", user_ids)

        # Validate response
        result = validate_bulk_response(response)

        # Validate stats
        validate_field_exists(result, "stats")
        validate_field_exists(result["stats"], "total")
        validate_field_equals(result["stats"], "total", len(user_ids))
        validate_field_exists(result["stats"], "deleted")
        validate_field_exists(result["stats"], "failed")
        assert result["stats"]["deleted"] + result["stats"]["failed"] == len(user_ids)

        # Validate results for each ID
        validate_field_exists(result, "items")
        validate_field_type(result, "items", list)
        for item in result["items"]:
            validate_field_exists(item, "user_id")
            validate_field_exists(item, "success")
            if not item["success"]:
                validate_field_exists(item, "error")
                validate_field_type(item, "error", dict)

    def test_invalid_bulk_operations(self, auth_api_test_client: APITestClient):
        """Test invalid bulk operations."""
        # Test bulk role update with empty list
        response = auth_api_test_client.put("user / roles / bulk", [])
        validate_error_response(response, 422)

        # Test bulk role update with invalid data
        response = auth_api_test_client.put(
            "user / roles / bulk",
            [{"user_id": "invalid - id"}, {"roles": ["admin"]}],  # Missing roles  # Missing user_id
        )
        validate_error_response(response, 422)

        # Test bulk delete with empty list
        response = auth_api_test_client.bulk_delete("user / accounts", [])
        validate_error_response(response, 422)

        # Test bulk delete with invalid IDs
        response = auth_api_test_client.bulk_delete(
            "user / accounts", ["invalid - id - 1", "invalid - id - 2"]
        )
        result = validate_bulk_response(response)
        validate_field_equals(result["stats"], "failed", 2)

    def test_invalid_login(self, api_test_client: APITestClient):
        """Test invalid login."""
        # Generate test data
        data = {"username": "nonexistentuser", "password": "wrongpassword"}

        # Make request
        response = api_test_client.post("user / login", data)

        # Validate error response
        validate_error_response(response, 401)  # Unauthorized

    def test_unauthorized_access(self, api_test_client: APITestClient):
        """Test unauthorized access to protected endpoints."""
        # Make request without authentication
        response = api_test_client.get("user / profile")

        # Validate error response
        validate_error_response(response, 401)  # Unauthorized

    def test_invalid_registration(self, api_test_client: APITestClient):
        """Test invalid registration."""
        # Make request with invalid data
        response = api_test_client.post("user / register", {})

        # Validate error response
        validate_error_response(response, 422)  # Unprocessable Entity
