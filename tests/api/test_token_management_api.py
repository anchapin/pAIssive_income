"""
Tests for token management.

This module contains tests for token generation, validation, and renewal.
"""


import time

from tests.api.utils.test_client import APITestClient

(
validate_error_response,
validate_field_equals,
validate_field_exists,
validate_field_not_empty,
validate_field_type,
validate_success_response,
)


class TestTokenManagementAPI:
    """Tests for token management."""

    def test_token_generation(self, api_test_client: APITestClient):
    """Test generating access and refresh tokens."""
    # Generate test credentials
    data = {
    "username": "test_user",
    "password": "test_password",
    "grant_type": "password",
    }

    # Make request
    response = api_test_client.post("auth/token", data)

    # Validate response
    result = validate_success_response(response)

    # Validate token fields
    validate_field_exists(result, "access_token")
    validate_field_type(result, "access_token", str)
    validate_field_not_empty(result, "access_token")
    validate_field_exists(result, "refresh_token")
    validate_field_type(result, "refresh_token", str)
    validate_field_not_empty(result, "refresh_token")
    validate_field_exists(result, "token_type")
    validate_field_equals(result, "token_type", "bearer")
    validate_field_exists(result, "expires_in")
    validate_field_type(result, "expires_in", int)

    def test_token_validation(self, api_test_client: APITestClient):
    """Test token validation."""
    # First get a valid token
    auth_data = {
    "username": "test_user",
    "password": "test_password",
    "grant_type": "password",
    }

    auth_response = api_test_client.post("auth/token", auth_data)
    auth_result = validate_success_response(auth_response)
    token = auth_result["access_token"]

    # Test token validation
    validation_data = {"token": token}

    response = api_test_client.post("auth/validate", validation_data)
    result = validate_success_response(response)

    # Validate fields
    validate_field_exists(result, "valid")
    validate_field_equals(result, "valid", True)
    validate_field_exists(result, "claims")
    validate_field_type(result, "claims", dict)

    claims = result["claims"]
    validate_field_exists(claims, "sub")
    validate_field_exists(claims, "exp")
    validate_field_exists(claims, "iat")

    def test_token_renewal(self, api_test_client: APITestClient):
    """Test token renewal using refresh token."""
    # First get initial tokens
    auth_data = {
    "username": "test_user",
    "password": "test_password",
    "grant_type": "password",
    }

    auth_response = api_test_client.post("auth/token", auth_data)
    auth_result = validate_success_response(auth_response)
    refresh_token = auth_result["refresh_token"]

    # Test token renewal
    renewal_data = {"grant_type": "refresh_token", "refresh_token": refresh_token}

    response = api_test_client.post("auth/token", renewal_data)
    result = validate_success_response(response)

    # Validate new tokens
    validate_field_exists(result, "access_token")
    validate_field_type(result, "access_token", str)
    validate_field_not_empty(result, "access_token")
    validate_field_exists(result, "refresh_token")
    validate_field_type(result, "refresh_token", str)
    validate_field_not_empty(result, "refresh_token")

    # Verify that new tokens are different
    assert result["access_token"] != auth_result["access_token"]
    assert result["refresh_token"] != auth_result["refresh_token"]

    def test_token_expiration(self, api_test_client: APITestClient):
    """Test token expiration handling."""
    # Configure short-lived test token
    config_data = {"access_token_expire_minutes": 1, "refresh_token_expire_days": 1}

    config_response = api_test_client.post("auth/config", config_data)
    validate_success_response(config_response)

    # Get test token
    auth_data = {
    "username": "test_user",
    "password": "test_password",
    "grant_type": "password",
    }

    auth_response = api_test_client.post("auth/token", auth_data)
    auth_result = validate_success_response(auth_response)
    token = auth_result["access_token"]

    # Wait for token to expire
    time.sleep(70)  # Wait just over 1 minute

    # Try to use expired token
    headers = {"Authorization": f"Bearer {token}"}
    response = api_test_client.get("auth/test", headers=headers)

    # Should get 401 with specific error about token expiration
    result = validate_error_response(response, 401)
    validate_field_exists(result, "error")
    validate_field_equals(result["error"], "token_expired")

    def test_token_revocation(self, api_test_client: APITestClient):
    """Test token revocation."""
    # Get test token
    auth_data = {
    "username": "test_user",
    "password": "test_password",
    "grant_type": "password",
    }

    auth_response = api_test_client.post("auth/token", auth_data)
    auth_result = validate_success_response(auth_response)
    token = auth_result["access_token"]

    # Revoke token
    revoke_data = {"token": token}

    response = api_test_client.post("auth/revoke", revoke_data)
    validate_success_response(response)

    # Try to use revoked token
    headers = {"Authorization": f"Bearer {token}"}
    response = api_test_client.get("auth/test", headers=headers)

    # Should get 401 with specific error about token being revoked
    result = validate_error_response(response, 401)
    validate_field_exists(result, "error")
    validate_field_equals(result["error"], "token_revoked")

    def test_concurrent_sessions(self, api_test_client: APITestClient):
    """Test handling of concurrent sessions."""
    # Configure session limits
    config_data = {"max_concurrent_sessions": 2}

    config_response = api_test_client.post("auth/session-config", config_data)
    validate_success_response(config_response)

    # Create multiple sessions
    auth_data = {
    "username": "test_user",
    "password": "test_password",
    "grant_type": "password",
    }

    sessions = []
    for _ in range(3):  # Try to create more sessions than allowed
    response = api_test_client.post("auth/token", auth_data)
    if response.status_code == 200:
    sessions.append(response.json())

    # Verify session limit enforcement
    assert len(sessions) == 2, "Should only allow max_concurrent_sessions"

    # Try to create another session
    response = api_test_client.post("auth/token", auth_data)
    result = validate_error_response(response, 400)
    validate_field_exists(result, "error")
    validate_field_equals(result["error"], "max_sessions_exceeded")

    def test_token_claims(self, api_test_client: APITestClient):
    """Test custom token claims."""
    # Get token with custom claims
    auth_data = {
    "username": "test_user",
    "password": "test_password",
    "grant_type": "password",
    "claims": {
    "roles": ["admin", "user"],
    "permissions": ["read", "write"],
    "customer_id": "test_customer",
    },
    }

    response = api_test_client.post("auth/token", auth_data)
    result = validate_success_response(response)

    # Decode token and verify claims
    token = result["access_token"]
    validation_data = {"token": token}

    response = api_test_client.post("auth/validate", validation_data)
    result = validate_success_response(response)

    # Validate custom claims
    validate_field_exists(result, "claims")
    claims = result["claims"]
    validate_field_exists(claims, "roles")
    validate_field_type(claims["roles"], list)
    validate_field_exists(claims, "permissions")
    validate_field_type(claims["permissions"], list)
    validate_field_exists(claims, "customer_id")
    validate_field_equals(claims["customer_id"], auth_data["claims"]["customer_id"])