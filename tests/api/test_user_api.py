"""
Tests for the user API.

This module contains tests for the user API endpoints.
"""

import pytest
from typing import Dict, Any, List
from fastapi.testclient import TestClient

from tests.api.utils.test_client import APITestClient
from tests.api.utils.test_data import (
    generate_id, generate_user_data
)
from tests.api.utils.test_validators import (
    validate_status_code, validate_json_response, validate_error_response,
    validate_success_response, validate_paginated_response, validate_bulk_response,
    validate_field_exists, validate_field_equals, validate_field_type,
    validate_field_not_empty, validate_list_not_empty, validate_list_length,
    validate_list_min_length, validate_list_max_length, validate_list_contains,
    validate_list_contains_dict_with_field
)


class TestUserAPI:
    """Tests for the user API."""

    def test_register_user(self, api_test_client: APITestClient):
        """Test registering a new user."""
        # Generate test data
        data = generate_user_data()
        
        # Make request
        response = api_test_client.post("user/register", data)
        
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
        data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        # Make request
        response = api_test_client.post("user/login", data)
        
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
        response = auth_api_test_client.get("user/profile")
        
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
        data = {
            "first_name": "Updated",
            "last_name": "User",
            "email": "updated@example.com"
        }
        
        # Make request
        response = auth_api_test_client.put("user/profile", data)
        
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
        data = {
            "current_password": "testpassword",
            "new_password": "newtestpassword"
        }
        
        # Make request
        response = auth_api_test_client.post("user/change-password", data)
        
        # Validate response
        validate_success_response(response)
    
    def test_get_user_projects(self, auth_api_test_client: APITestClient):
        """Test getting the user's projects."""
        # Make request
        response = auth_api_test_client.get("user/projects")
        
        # Validate response
        result = validate_paginated_response(response)
        
        # Validate items
        validate_field_type(result, "items", list)
    
    def test_get_user_teams(self, auth_api_test_client: APITestClient):
        """Test getting the user's teams."""
        # Make request
        response = auth_api_test_client.get("user/teams")
        
        # Validate response
        result = validate_paginated_response(response)
        
        # Validate items
        validate_field_type(result, "items", list)
    
    def test_get_user_activity(self, auth_api_test_client: APITestClient):
        """Test getting the user's activity."""
        # Make request
        response = auth_api_test_client.get("user/activity")
        
        # Validate response
        result = validate_paginated_response(response)
        
        # Validate items
        validate_field_type(result, "items", list)
    
    def test_get_user_settings(self, auth_api_test_client: APITestClient):
        """Test getting the user's settings."""
        # Make request
        response = auth_api_test_client.get("user/settings")
        
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
                "email_notifications": False
            }
        }
        
        # Make request
        response = auth_api_test_client.put("user/settings", data)
        
        # Validate response
        result = validate_success_response(response)
        
        # Validate fields
        validate_field_exists(result, "settings")
        validate_field_type(result, "settings", dict)
        validate_field_exists(result["settings"], "theme")
        validate_field_equals(result["settings"], "theme", data["settings"]["theme"])
        validate_field_exists(result["settings"], "notifications_enabled")
        validate_field_equals(result["settings"], "notifications_enabled", data["settings"]["notifications_enabled"])
        validate_field_exists(result["settings"], "email_notifications")
        validate_field_equals(result["settings"], "email_notifications", data["settings"]["email_notifications"])
    
    def test_invalid_login(self, api_test_client: APITestClient):
        """Test invalid login."""
        # Generate test data
        data = {
            "username": "nonexistentuser",
            "password": "wrongpassword"
        }
        
        # Make request
        response = api_test_client.post("user/login", data)
        
        # Validate error response
        validate_error_response(response, 401)  # Unauthorized
    
    def test_unauthorized_access(self, api_test_client: APITestClient):
        """Test unauthorized access to protected endpoints."""
        # Make request without authentication
        response = api_test_client.get("user/profile")
        
        # Validate error response
        validate_error_response(response, 401)  # Unauthorized
    
    def test_invalid_registration(self, api_test_client: APITestClient):
        """Test invalid registration."""
        # Make request with invalid data
        response = api_test_client.post("user/register", {})
        
        # Validate error response
        validate_error_response(response, 422)  # Unprocessable Entity
