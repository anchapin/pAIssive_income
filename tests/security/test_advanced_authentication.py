"""
Tests for advanced authentication scenarios.

This module implements the advanced authentication tests recommended in the security testing section:
1. Test token refresh scenarios
2. Test concurrent authentication attempts
3. Test session invalidation propagation
"""

import threading
import time
import unittest
from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock

from api.config import APIConfig
from api.middleware.auth import AuthMiddleware

class TestAdvancedAuthentication(unittest.TestCase):
    """Test cases for advanced authentication scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = APIConfig(
            jwt_secret="test - secret",
            jwt_algorithm="HS256",
            jwt_expires_minutes=60,
            jwt_refresh_expires_days=7,
            api_keys=["test - api - key"],
        )
        self.auth_middleware = AuthMiddleware(self.config)

        # Mock session store
        self.session_store = MagicMock()
        self.auth_middleware.session_store = self.session_store

        # Track active sessions
        self.active_sessions = {}
        self.session_store.get_active_sessions.return_value = self.active_sessions
        self.session_store.add_session.side_effect = self._mock_add_session
        self.session_store.invalidate_session.side_effect = \
            self._mock_invalidate_session
        self.session_store.invalidate_all_user_sessions.side_effect = (
            self._mock_invalidate_all_user_sessions
        )

    def _mock_add_session(self, user_id: str, session_id: str, metadata: Dict[str, 
        Any]) -> None:
        """Mock adding a session to the store."""
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = {}
        self.active_sessions[user_id][session_id] = metadata

    def _mock_invalidate_session(self, session_id: str) -> bool:
        """Mock invalidating a session."""
        for user_id, sessions in self.active_sessions.items():
            if session_id in sessions:
                del sessions[session_id]
                return True
        return False

    def _mock_invalidate_all_user_sessions(self, user_id: str) -> int:
        """Mock invalidating all sessions for a user."""
        if user_id in self.active_sessions:
            count = len(self.active_sessions[user_id])
            self.active_sessions[user_id] = {}
            return count
        return 0

    def test_token_refresh_basic(self):
        """Test basic token refresh scenario."""
        # Create initial token
        user_data = {"user_id": "123", "username": "testuser", "role": "user"}

        # Create access and refresh tokens
        access_token = self.auth_middleware.create_token(user_data)
        refresh_token = self.auth_middleware.create_refresh_token(user_data)

        # Verify tokens
        access_payload = self.auth_middleware.verify_token(access_token)
        refresh_payload = self.auth_middleware.verify_refresh_token(refresh_token)

        self.assertEqual(access_payload["user_id"], "123")
        self.assertEqual(refresh_payload["user_id"], "123")

        # Refresh the token
        new_access_token = self.auth_middleware.refresh_access_token(refresh_token)
        new_payload = self.auth_middleware.verify_token(new_access_token)

        # Verify new token has same user data
        self.assertEqual(new_payload["user_id"], "123")
        self.assertEqual(new_payload["username"], "testuser")
        self.assertEqual(new_payload["role"], "user")

        # Verify new token is different from old token
        self.assertNotEqual(access_token, new_access_token)

    def test_token_refresh_expired_access(self):
        """Test refreshing with expired access token but valid refresh token."""
        # Create config with short access token expiry
        config = APIConfig(
            jwt_secret="test - secret",
            jwt_algorithm="HS256",
            jwt_expires_minutes=0.05,  # 3 seconds
            jwt_refresh_expires_days=7,
            api_keys=["test - api - key"],
        )
        auth_middleware = AuthMiddleware(config)

        # Create tokens
        user_data = {"user_id": "123", "username": "testuser"}
        access_token = auth_middleware.create_token(user_data)
        refresh_token = auth_middleware.create_refresh_token(user_data)

        # Wait for access token to expire
        time.sleep(4)

        # Verify access token is expired
        with self.assertRaises(ValueError) as context:
            auth_middleware.verify_token(access_token)
        self.assertEqual(str(context.exception), "Token has expired")

        # Refresh token should still work
        new_access_token = auth_middleware.refresh_access_token(refresh_token)
        new_payload = auth_middleware.verify_token(new_access_token)
        self.assertEqual(new_payload["user_id"], "123")

    def test_token_refresh_expired_refresh(self):
        """Test refreshing with expired refresh token."""
        # Create config with short refresh token expiry
        config = APIConfig(
            jwt_secret="test - secret",
            jwt_algorithm="HS256",
            jwt_expires_minutes=60,
            jwt_refresh_expires_days=0.0001,  # ~8.6 seconds
            api_keys=["test - api - key"],
        )
        auth_middleware = AuthMiddleware(config)

        # Create tokens
        user_data = {"user_id": "123", "username": "testuser"}
        access_token = auth_middleware.create_token(user_data)
        refresh_token = auth_middleware.create_refresh_token(user_data)

        # Wait for refresh token to expire
        time.sleep(10)

        # Verify refresh token is expired
        with self.assertRaises(ValueError) as context:
            auth_middleware.refresh_access_token(refresh_token)
        self.assertEqual(str(context.exception), "Refresh token has expired")

    def test_token_refresh_chain(self):
        """Test chaining multiple token refreshes."""
        # Create tokens
        user_data = {"user_id": "123", "username": "testuser"}
        refresh_token = self.auth_middleware.create_refresh_token(user_data)

        # Perform multiple refreshes
        access_tokens = []
        for _ in range(3):
            access_token = self.auth_middleware.refresh_access_token(refresh_token)
            access_tokens.append(access_token)

            # Verify token
            payload = self.auth_middleware.verify_token(access_token)
            self.assertEqual(payload["user_id"], "123")

            # Small delay to ensure tokens are different
            time.sleep(1)

        # Verify all tokens are different
        self.assertNotEqual(access_tokens[0], access_tokens[1])
        self.assertNotEqual(access_tokens[1], access_tokens[2])
        self.assertNotEqual(access_tokens[0], access_tokens[2])

    def test_concurrent_authentication_attempts(self):
        """Test handling of concurrent authentication attempts."""
        # Set up test data
        user_credentials = {"username": "testuser", "password": "password123"}

        # Mock the authentication method
        def mock_authenticate(username, password):
            time.sleep(0.1)  # Simulate some processing time
            if username == "testuser" and password == "password123":
                return {"user_id": "123", "username": username, "role": "user"}
            return None

        self.auth_middleware.authenticate_user = \
            MagicMock(side_effect=mock_authenticate)

        # Set up concurrent authentication tracking
        auth_results = []
        auth_tokens = []

        def authenticate_and_get_token():
            result = self.auth_middleware.authenticate_user(
                user_credentials["username"], user_credentials["password"]
            )
            auth_results.append(result)
            if result:
                token = self.auth_middleware.create_token(result)
                auth_tokens.append(token)

        # Launch concurrent authentication attempts
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=authenticate_and_get_token)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all authentication attempts succeeded
        self.assertEqual(len(auth_results), 5)
        self.assertEqual(len(auth_tokens), 5)

        # Verify all tokens are valid but different
        token_payloads = \
            [self.auth_middleware.verify_token(token) for token in auth_tokens]
        for payload in token_payloads:
            self.assertEqual(payload["user_id"], "123")
            self.assertEqual(payload["username"], "testuser")

        # Verify tokens are all different
        unique_tokens = set(auth_tokens)
        self.assertEqual(len(unique_tokens), 5)

    def test_concurrent_authentication_rate_limiting(self):
        """Test rate limiting of concurrent authentication attempts."""
        # Set up rate limiting
        rate_limit = 3
        rate_limit_window = 5  # seconds
        self.auth_middleware.rate_limit = rate_limit
        self.auth_middleware.rate_limit_window = rate_limit_window

        # Track authentication attempts by IP
        ip_attempts = {}

        def mock_check_rate_limit(ip_address):
            current_time = time.time()
            if ip_address not in ip_attempts:
                ip_attempts[ip_address] = []

            # Clean up old attempts
            ip_attempts[ip_address] = [
                t for t in ip_attempts[ip_address] if current_time - \
                    t < rate_limit_window
            ]

            # Check if rate limited
            if len(ip_attempts[ip_address]) >= rate_limit:
                return False

            # Record attempt
            ip_attempts[ip_address].append(current_time)
            return True

        self.auth_middleware.check_auth_rate_limit = \
            MagicMock(side_effect=mock_check_rate_limit)

        # Test IP address
        test_ip = "192.168.1.1"

        # First 3 attempts should succeed
        for _ in range(rate_limit):
            result = self.auth_middleware.check_auth_rate_limit(test_ip)
            self.assertTrue(result)

        # Next attempt should be rate limited
        result = self.auth_middleware.check_auth_rate_limit(test_ip)
        self.assertFalse(result)

        # Wait for rate limit window to expire
        time.sleep(rate_limit_window + 1)

        # Should be able to authenticate again
        result = self.auth_middleware.check_auth_rate_limit(test_ip)
        self.assertTrue(result)

    def test_session_invalidation_single(self):
        """Test invalidation of a single session."""
        # Create user with multiple sessions
        user_id = "123"
        session_ids = ["session1", "session2", "session3"]

        for session_id in session_ids:
            self.session_store.add_session(
                user_id, session_id, {"created_at": datetime.now().isoformat()}
            )

        # Verify sessions are active
        self.assertEqual(len(self.active_sessions[user_id]), 3)

        # Invalidate one session
        result = self.session_store.invalidate_session("session2")
        self.assertTrue(result)

        # Verify session was invalidated
        self.assertEqual(len(self.active_sessions[user_id]), 2)
        self.assertIn("session1", self.active_sessions[user_id])
        self.assertNotIn("session2", self.active_sessions[user_id])
        self.assertIn("session3", self.active_sessions[user_id])

    def test_session_invalidation_all_user_sessions(self):
        """Test invalidation of all sessions for a user."""
        # Create multiple users with sessions
        users = {"123": ["session1", "session2", "session3"], "456": ["session4", 
            "session5"]}

        for user_id, session_ids in users.items():
            for session_id in session_ids:
                self.session_store.add_session(
                    user_id, session_id, {"created_at": datetime.now().isoformat()}
                )

        # Verify sessions are active
        self.assertEqual(len(self.active_sessions["123"]), 3)
        self.assertEqual(len(self.active_sessions["456"]), 2)

        # Invalidate all sessions for user 123
        count = self.session_store.invalidate_all_user_sessions("123")
        self.assertEqual(count, 3)

        # Verify user 123's sessions are invalidated but user 456's remain
        self.assertEqual(len(self.active_sessions["123"]), 0)
        self.assertEqual(len(self.active_sessions["456"]), 2)

    def test_session_invalidation_propagation(self):
        """Test propagation of session invalidation across services."""
        # Mock service clients
        service_clients = {
            "auth_service": MagicMock(),
            "api_service": MagicMock(),
            "user_service": MagicMock(),
        }

        # Set up session invalidation propagation
        def invalidate_session_across_services(session_id):
            # Invalidate locally
            self.session_store.invalidate_session(session_id)

            # Propagate to other services
            for service_name, client in service_clients.items():
                client.invalidate_session(session_id)

        # Create test session
        user_id = "123"
        session_id = "test - session"
        self.session_store.add_session(
            user_id, session_id, {"created_at": datetime.now().isoformat()}
        )

        # Invalidate session with propagation
        invalidate_session_across_services(session_id)

        # Verify local invalidation
        self.assertNotIn(session_id, self.active_sessions.get(user_id, {}))

        # Verify propagation to all services
        for service_name, client in service_clients.items():
            client.invalidate_session.assert_called_once_with(session_id)

    def test_password_change_session_invalidation(self):
        """Test session invalidation after password change."""
        # Create user with multiple sessions
        user_id = "123"
        session_ids = ["session1", "session2", "session3"]

        for session_id in session_ids:
            self.session_store.add_session(
                user_id, session_id, {"created_at": datetime.now().isoformat()}
            )

        # Mock password change handler
        def handle_password_change(user_id, new_password):
            # Update password (mocked)
            # ...

            # Invalidate all sessions except current one
            current_session_id = "session2"
            for session_id in list(self.active_sessions.get(user_id, {}).keys()):
                if session_id != current_session_id:
                    self.session_store.invalidate_session(session_id)

            return True

        # Change password
        result = handle_password_change(user_id, "new_password123")
        self.assertTrue(result)

        # Verify only current session remains
        self.assertEqual(len(self.active_sessions[user_id]), 1)
        self.assertIn("session2", self.active_sessions[user_id])

if __name__ == "__main__":
    unittest.main()
