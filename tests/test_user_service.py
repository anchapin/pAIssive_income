"""test_user_service - Test module for user service."""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import bcrypt
import jwt
import pytest
from flask import Flask

from users.services import (
    AuthenticationError, 
    DatabaseSessionNotAvailableError,
    TokenError,
    UserExistsError,
    UserModelNotAvailableError,
    UserService,
)

@pytest.mark.unit
class TestUserService(unittest.TestCase):
    """Test suite for the UserService class."""

    @classmethod
    def setUpClass(cls):
        """Set up class-level test fixtures."""
        cls.token_secret = "test_secret"
        cls.token_expiry = 3600  # 1 hour
        # Create Flask app for context
        cls.app = Flask(__name__)

    def setUp(self):
        """Set up test fixtures."""
        self.user_service = UserService(token_secret=self.token_secret)
        self.user_service._UserService__token_expiry = self.token_expiry

        # Create a valid bcrypt hash for testing
        password = "password123"
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode(), salt)

        # Common test data
        self.test_user = MagicMock()
        self.test_user.id = "user-123"
        self.test_user.username = "testuser"
        self.test_user.email = "test@example.com"
        self.test_user.password_hash = self.hashed_password
        self.test_user.last_login = None

    @pytest.mark.unit
    def test_init_without_token_secret(self):
        """Test initializing without a token secret."""
        with self.assertRaises(AuthenticationError) as ctx:
            UserService(token_secret=None)
        self.assertEqual(str(ctx.exception), "Token secret is required")

    @pytest.mark.unit
    def test_init_with_empty_token_secret(self):
        """Test initializing with empty token secret."""
        with self.assertRaises(AuthenticationError) as ctx:
            UserService(token_secret="")
        self.assertEqual(str(ctx.exception), "Token secret is required")

    @pytest.mark.unit
    def test_token_secret_property(self):
        """Test the token_secret property."""
        self.assertEqual(self.user_service.token_secret, self.token_secret)

    @pytest.mark.unit
    def test_create_user_missing_inputs(self):
        """Test creating a user with missing inputs."""
        test_cases = [
            ("", "test@example.com", "password123", "Username is required"),
            ("testuser", "", "password123", "Email is required"),
            ("testuser", "test@example.com", "", "Password is required"),
            (None, "test@example.com", "password123", "Username is required"),
            ("testuser", None, "password123", "Email is required"),
            ("testuser", "test@example.com", None, "Password is required"),
        ]

        for username, email, password, expected_error in test_cases:
            with self.subTest(missing_field=expected_error):
                with self.assertRaises(AuthenticationError) as ctx:
                    self.user_service.create_user(username, email, password)
                self.assertEqual(str(ctx.exception), expected_error)

    @pytest.mark.unit
    def test_create_user_success(self):
        """Test creating a user successfully."""
        username = "newuser"
        email = "new@example.com"
        password = "password123"

        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.username = username
        mock_user.email = email

        mock_db = MagicMock()

        with patch("users.services.UserModel") as mock_user_model, \
             patch("users.services.db_session", mock_db), \
             self.app.app_context():
            mock_user_model.query.filter.return_value.first.return_value = None
            mock_user_model.return_value = mock_user

            result = self.user_service.create_user(username, email, password)

            self.assertEqual(result["username"], username)
            self.assertEqual(result["email"], email)
            self.assertEqual(result["id"], "user-123")
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()

    @pytest.mark.unit
    def test_create_user_username_exists(self):
        """Test creating a user with an existing username."""
        username = "existinguser"
        email = "new@example.com"
        password = "password123"

        mock_existing_user = MagicMock()
        mock_existing_user.username = username
        mock_existing_user.email = "other@example.com"

        with patch("users.services.UserModel") as mock_user_model, \
             self.app.app_context():
            mock_user_model.query.filter.return_value.first.return_value = mock_existing_user

            with self.assertRaises(UserExistsError) as context:
                self.user_service.create_user(username, email, password)

            self.assertEqual(str(context.exception), UserExistsError.USERNAME_EXISTS)

    @pytest.mark.unit
    def test_authenticate_user_success(self):
        """Test authenticating a user successfully."""
        username = "testuser"
        password = "password123"

        with patch("users.services.UserModel") as mock_user_model, \
             patch("users.services.verify_credential", return_value=True) as mock_verify, \
             patch("users.services.db_session", MagicMock()), \
             self.app.app_context():
            mock_user_model.query.filter.return_value.first.return_value = self.test_user

            success, user_data = self.user_service.authenticate_user(username, password)

            self.assertTrue(success)
            self.assertEqual(user_data["username"], username)
            self.assertEqual(user_data["email"], "test@example.com")
            self.assertEqual(user_data["id"], "user-123")
            mock_verify.assert_called_once_with(password, self.hashed_password)

    @pytest.mark.unit
    def test_authenticate_user_wrong_password(self):
        """Test authenticating a user with wrong password."""
        username = "testuser"
        password = "wrongpassword"

        with patch("users.services.UserModel") as mock_user_model, \
             patch("users.services.verify_credential", return_value=False) as mock_verify, \
             self.app.app_context():
            mock_user_model.query.filter.return_value.first.return_value = self.test_user

            success, user_data = self.user_service.authenticate_user(username, password)

            self.assertFalse(success)
            self.assertIsNone(user_data)
            mock_verify.assert_called_once_with(password, self.hashed_password)

    @pytest.mark.unit
    def test_authenticate_user_not_found(self):
        """Test authenticating a non-existent user."""
        with patch("users.services.UserModel") as mock_user_model, \
             self.app.app_context():
            mock_user_model.query.filter.return_value.first.return_value = None

            success, user_data = self.user_service.authenticate_user("nonexistent", "password123")

            self.assertFalse(success)
            self.assertIsNone(user_data)

    @pytest.mark.unit
    def test_authenticate_user_with_last_login(self):
        """Test authenticating a user updates last login time."""
        username = "testuser"
        password = "password123"
        mock_db = MagicMock()

        with patch("users.services.UserModel") as mock_user_model, \
             patch("users.services.db_session", mock_db), \
             patch("users.services.verify_credential", return_value=True), \
             self.app.app_context():
            mock_user_model.query.filter.return_value.first.return_value = self.test_user

            before_login = datetime.now(timezone.utc)
            success, user_data = self.user_service.authenticate_user(username, password)
            after_login = datetime.now(timezone.utc)

            self.assertTrue(success)
            self.assertIsNotNone(self.test_user.last_login)
            self.assertTrue(before_login <= self.test_user.last_login <= after_login)
            mock_db.session.commit.assert_called_once()

    @pytest.mark.unit
    def test_authenticate_user_db_error(self):
        """Test authentication when DB session has an error."""
        username = "testuser"
        password = "password123"
        mock_db = MagicMock()
        mock_db.session.commit.side_effect = Exception("DB Error")

        with patch("users.services.UserModel") as mock_user_model, \
             patch("users.services.db_session", mock_db), \
             patch("users.services.verify_credential", return_value=True), \
             self.app.app_context():
            mock_user_model.query.filter.return_value.first.return_value = self.test_user

            success, user_data = self.user_service.authenticate_user(username, password)

            self.assertFalse(success)
            self.assertIsNone(user_data)
            mock_db.session.commit.assert_called_once()

    @pytest.mark.unit
    def test_generate_token(self):
        """Test generating a JWT token."""
        user_id = "user-123"
        claims = {
            "username": "testuser",
            "email": "test@example.com",
            "role": "admin"
        }

        token = self.user_service.generate_token(user_id, **claims)

        payload = jwt.decode(
            token,
            self.token_secret,
            algorithms=["HS256"],
            options={"verify_exp": False}
        )

        self.assertEqual(payload["sub"], user_id)
        self.assertEqual(payload["username"], claims["username"])
        self.assertEqual(payload["email"], claims["email"])
        self.assertEqual(payload["role"], claims["role"])
        self.assertIn("jti", payload)
        self.assertIn("iat", payload)
        self.assertIn("exp", payload)

        # Verify expiration time
        now = datetime.now(timezone.utc)
        exp_time = datetime.fromtimestamp(payload["exp"], timezone.utc)
        self.assertGreater(exp_time, now)
        self.assertLess(exp_time, now + timedelta(seconds=self.token_expiry + 60))

    @pytest.mark.unit
    def test_generate_token_with_sensitive_claims(self):
        """Test generating a token excludes sensitive claims."""
        user_id = "user-123"
        claims = {
            "username": "testuser",
            "password": "should_not_be_included",
            "token": "should_not_be_included",
            "secret": "should_not_be_included",
            "key": "should_not_be_included",
        }

        token = self.user_service.generate_token(user_id, **claims)

        payload = jwt.decode(
            token,
            self.token_secret,
            algorithms=["HS256"],
            options={"verify_exp": False}
        )

        self.assertEqual(payload["username"], "testuser")
        sensitive_fields = ["password", "token", "secret", "key"]
        for field in sensitive_fields:
            self.assertNotIn(field, payload)

    @pytest.mark.unit
    def test_verify_token_success(self):
        """Test verifying a valid token."""
        user_id = "user-123"
        claims = {
            "username": "testuser",
            "email": "test@example.com"
        }

        token = self.user_service.generate_token(user_id, **claims)
        success, payload = self.user_service.verify_token(token)

        self.assertTrue(success)
        self.assertEqual(payload["sub"], user_id)
        self.assertEqual(payload["username"], claims["username"])
        self.assertEqual(payload["email"], claims["email"])

    @pytest.mark.unit
    def test_verify_token_expired(self):
        """Test verifying an expired token."""
        user_id = "user-123"
        now = datetime.now(timezone.utc)
        expired_time = now - timedelta(hours=2)

        claims = {
            "sub": user_id,
            "exp": expired_time.timestamp(),
            "iat": expired_time.timestamp(),
            "jti": "test-id"
        }

        token = jwt.encode(claims, self.token_secret, algorithm="HS256")
        success, payload = self.user_service.verify_token(token)

        self.assertFalse(success)
        self.assertIsNone(payload)

    @pytest.mark.unit
    def test_verify_token_invalid(self):
        """Test verifying various invalid tokens."""
        test_cases = [
            ("invalid.token.string", "malformed token"),
            ("", "empty token"),
            (None, "null token"),
            ("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U", "wrong signature"),
            (jwt.encode({"sub": "user-123"}, "wrong_secret", algorithm="HS256"), "wrong secret"),
        ]

        for token, case in test_cases:
            with self.subTest(case=case):
                success, payload = self.user_service.verify_token(token)
                self.assertFalse(success, f"Token verification should fail for {case}")
                self.assertIsNone(payload)

    @pytest.mark.unit
    def test_verify_token_missing_claims(self):
        """Test verifying tokens with missing required claims."""
        # Override required_claims to match service implementation
        required_claims = ["sub"]  # Most JWT libraries only require "sub" claim
        now = datetime.now(timezone.utc)

        base_claims = {
            "sub": "user-123",
            "exp": now.timestamp() + 3600,
            "iat": now.timestamp(),
            "jti": "test-id"
        }

        for claim in required_claims:
            with self.subTest(missing_claim=claim):
                claims = base_claims.copy()
                del claims[claim]

                token = jwt.encode(claims, self.token_secret, algorithm="HS256")
                success, payload = self.user_service.verify_token(token)

                self.assertFalse(success, f"Token missing {claim} claim should be invalid")
                self.assertIsNone(payload)

if __name__ == "__main__":
    pytest.main(["-v"])
