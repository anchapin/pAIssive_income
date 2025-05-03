"""
Tests for security features.
"""

import unittest
from datetime import datetime, timedelta
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import jwt

from api.config import APIConfig
from api.middleware.auth import AuthMiddleware
from api.services.api_key_service import APIKeyService


class TestSecurity(unittest.TestCase):
    """Test cases for security features."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = APIConfig(
            jwt_secret="test-secret",
            jwt_algorithm="HS256",
            jwt_expires_minutes=60,
            api_keys=["test-api-key"],
        )
        self.auth_middleware = AuthMiddleware(self.config)

    def test_jwt_token_lifecycle(self):
        """Test JWT token creation and verification."""
        # Test token creation
        user_data = {"user_id": "123", "username": "testuser", "role": "user"}
        token = self.auth_middleware.create_token(user_data)
        self.assertIsInstance(token, str)

        # Test token verification
        payload = self.auth_middleware.verify_token(token)
        self.assertEqual(payload["user_id"], "123")
        self.assertEqual(payload["username"], "testuser")
        self.assertEqual(payload["role"], "user")

        # Test expired token
        with patch("jwt.decode") as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError()
            with self.assertRaises(ValueError) as context:
                self.auth_middleware.verify_token("expired-token")
            self.assertEqual(str(context.exception), "Token has expired")

        # Test invalid token
        with patch("jwt.decode") as mock_decode:
            mock_decode.side_effect = jwt.InvalidTokenError()
            with self.assertRaises(ValueError) as context:
                self.auth_middleware.verify_token("invalid-token")
            self.assertEqual(str(context.exception), "Invalid token")

    def test_api_key_authentication(self):
        """Test API key authentication."""
        # Test valid API key
        self.assertTrue(self.auth_middleware.verify_api_key("test-api-key"))

        # Test invalid API key
        self.assertFalse(self.auth_middleware.verify_api_key("invalid-api-key"))

        # Test API key service verification
        mock_api_key_service = MagicMock(spec=APIKeyService)
        mock_api_key_service.verify_api_key.return_value = {"id": "key1", "active": True}
        self.auth_middleware.api_key_service = mock_api_key_service

        self.assertTrue(self.auth_middleware.verify_api_key("service-api-key"))
        mock_api_key_service.verify_api_key.assert_called_once_with("service-api-key")

    @patch("fastapi.Request")
    def test_authentication_middleware(self, mock_request):
        """Test authentication middleware."""
        # Mock request with valid API key
        mock_request.headers = {"X-API-Key": "test-api-key"}
        mock_request.url.path = "/api/test"

        # Test request with valid API key
        result = self.auth_middleware.verify_api_key(mock_request.headers["X-API-Key"])
        self.assertTrue(result)

        # Mock request with valid JWT
        token = self.auth_middleware.create_token({"user_id": "123"})
        mock_request.headers = {"Authorization": f"Bearer {token}"}

        # Test request with valid JWT
        payload = self.auth_middleware.verify_token(token)
        self.assertEqual(payload["user_id"], "123")

        # Test request with no authentication
        mock_request.headers = {}
        self.assertFalse(self.auth_middleware.verify_api_key(""))

    def test_authorization_rules(self):
        """Test authorization rules and permissions."""
        # Create a test user with roles and permissions
        user_data = {
            "user_id": "123",
            "username": "testuser",
            "role": "admin",
            "permissions": ["read", "write", "delete"],
        }
        token = self.auth_middleware.create_token(user_data)
        payload = self.auth_middleware.verify_token(token)

        # Verify admin role
        self.assertEqual(payload["role"], "admin")

        # Verify permissions
        self.assertIn("read", payload["permissions"])
        self.assertIn("write", payload["permissions"])
        self.assertIn("delete", payload["permissions"])

    def test_token_expiration(self):
        """Test token expiration handling."""
        # Create token with short expiration
        config = APIConfig(
            jwt_secret="test-secret",
            jwt_algorithm="HS256",
            jwt_expires_minutes=0.1,  # 6 seconds
            api_keys=["test-api-key"],
        )
        auth_middleware = AuthMiddleware(config)

        # Create token
        token = auth_middleware.create_token({"user_id": "123"})

        # Verify token works initially
        payload = auth_middleware.verify_token(token)
        self.assertEqual(payload["user_id"], "123")

        # Wait for token to expire
        import time

        time.sleep(7)

        # Verify token is now expired
        with self.assertRaises(ValueError) as context:
            auth_middleware.verify_token(token)
        self.assertEqual(str(context.exception), "Token has expired")

    def test_security_headers(self):
        """Test security-related headers."""
        # Test API key header
        headers = {"X-API-Key": "test-api-key"}
        self.assertTrue(self.auth_middleware.verify_api_key(headers["X-API-Key"]))

        # Test JWT auth header
        token = self.auth_middleware.create_token({"user_id": "123"})
        headers = {"Authorization": f"Bearer {token}"}
        extracted_token = headers["Authorization"].replace("Bearer ", "")
        payload = self.auth_middleware.verify_token(extracted_token)
        self.assertEqual(payload["user_id"], "123")

    def test_invalid_configurations(self):
        """Test handling of invalid security configurations."""
        # Test missing JWT secret
        config = APIConfig(jwt_algorithm="HS256", jwt_expires_minutes=60, api_keys=["test-api-key"])
        auth_middleware = AuthMiddleware(config)

        with self.assertRaises(ValueError) as context:
            auth_middleware.create_token({"user_id": "123"})
        self.assertEqual(str(context.exception), "JWT secret is not configured")

        # Test invalid JWT algorithm
        config = APIConfig(
            jwt_secret="test-secret",
            jwt_algorithm="invalid",
            jwt_expires_minutes=60,
            api_keys=["test-api-key"],
        )
        auth_middleware = AuthMiddleware(config)

        with self.assertRaises(jwt.InvalidAlgorithmError):
            auth_middleware.create_token({"user_id": "123"})


if __name__ == "__main__":
    unittest.main()
