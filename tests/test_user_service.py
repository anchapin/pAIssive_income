"""test_user_service - Test module for user service."""

import logging
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, Mock

import pytest

from users.services import UserExistsError, UserService, AuthenticationError, UserModelNotAvailableError, DatabaseSessionNotAvailableError


class TestUserService(unittest.TestCase):
    """Test suite for the UserService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.token_secret = "test_secret"  # noqa: S105 - Test data only
        self.user_service = UserService(token_secret=self.token_secret)

    def test_token_secret_property(self):
        """Test the token_secret property."""
        assert self.user_service.token_secret == self.token_secret

    def test_init_without_token_secret(self):
        """Test UserService initialization without token secret."""
        with pytest.raises(AuthenticationError):
            UserService(token_secret=None)

    def test_init_with_empty_token_secret(self):
        """Test UserService initialization with empty token secret."""
        with pytest.raises(AuthenticationError):
            UserService(token_secret="")

    @patch('users.services.UserModel', None)
    def test_create_user_no_user_model(self):
        """Test creating a user when UserModel is not available."""
        with pytest.raises(UserModelNotAvailableError):
            self.user_service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential="password123"
            )

    @patch('users.services.db_session', None)
    @patch('users.services.UserModel')
    def test_create_user_no_db_session(self, mock_user_model):
        """Test creating a user when db_session is not available."""
        # Mock the query to return no existing user
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_user_model.query = mock_query

        with patch('users.services.hash_credential', return_value="hashed_password"):
            with pytest.raises(DatabaseSessionNotAvailableError):
                self.user_service.create_user(
                    username="testuser",
                    email="test@example.com",
                    auth_credential="password123"
                )

    def test_create_user_missing_username(self):
        """Test creating a user without username."""
        with pytest.raises(AuthenticationError) as exc_info:
            self.user_service.create_user(
                username="",
                email="test@example.com",
                auth_credential="password123"
            )
        assert "Username is required" in str(exc_info.value)

    def test_create_user_missing_email(self):
        """Test creating a user without email."""
        with pytest.raises(AuthenticationError) as exc_info:
            self.user_service.create_user(
                username="testuser",
                email="",
                auth_credential="password123"
            )
        assert "Email is required" in str(exc_info.value)

    def test_create_user_missing_password(self):
        """Test creating a user without password."""
        with pytest.raises(AuthenticationError) as exc_info:
            self.user_service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential=""
            )
        assert "Password is required" in str(exc_info.value)

    @patch('users.services.hash_credential')
    @patch('users.services.UserModel')
    @patch('users.services.db_session')
    def test_create_user_success(self, mock_db_session, mock_user_model, mock_hash):
        """Test successful user creation."""
        # Setup mocks
        mock_hash.return_value = "hashed_password"

        # Mock the query to return no existing user
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_user_model.query = mock_query

        # Mock user instance
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.created_at = datetime.now(timezone.utc)
        mock_user.updated_at = datetime.now(timezone.utc)
        mock_user_model.return_value = mock_user

        # Mock db session
        mock_session = MagicMock()
        mock_db_session.session = mock_session

        # Call the method
        result = self.user_service.create_user(
            username="testuser",
            email="test@example.com",
            auth_credential="password123"
        )

        # Assertions
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert result["id"] == "user123"
        assert "password_hash" not in result

        # Verify method calls
        mock_hash.assert_called_once_with("password123")
        mock_session.add.assert_called_once_with(mock_user)
        mock_session.commit.assert_called_once()

    @patch('users.services.UserModel')
    def test_create_user_existing_username(self, mock_user_model):
        """Test creating a user with existing username."""
        # Mock existing user
        existing_user = MagicMock()
        existing_user.username = "testuser"
        existing_user.email = "existing@example.com"

        # Mock the query to return existing user
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = existing_user
        mock_user_model.query = mock_query

        with pytest.raises(UserExistsError) as exc_info:
            self.user_service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential="password123"
            )
        assert "Username already exists" in str(exc_info.value)

    @patch('users.services.UserModel')
    def test_create_user_existing_email(self, mock_user_model):
        """Test creating a user with existing email."""
        # Mock existing user
        existing_user = MagicMock()
        existing_user.username = "existinguser"
        existing_user.email = "test@example.com"

        # Mock the query to return existing user
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = existing_user
        mock_user_model.query = mock_query

        with pytest.raises(UserExistsError) as exc_info:
            self.user_service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential="password123"
            )
        assert "Email already exists" in str(exc_info.value)

    @patch('users.services.UserModel', None)
    def test_authenticate_user_no_user_model(self):
        """Test authenticating a user when UserModel is not available."""
        with pytest.raises(UserModelNotAvailableError):
            self.user_service.authenticate_user("testuser", "password123")

    @patch('users.services.UserModel')
    def test_authenticate_user_not_found(self, mock_user_model):
        """Test authenticating a non-existent user."""
        # Mock the query to return None (user not found)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_user_model.query = mock_query

        success, result = self.user_service.authenticate_user("nonexistent", "password123")

        assert success is False
        assert result is None

    @patch('users.services.verify_credential')
    @patch('users.services.UserModel')
    def test_authenticate_user_wrong_password(self, mock_user_model, mock_verify):
        """Test authenticating a user with wrong password."""
        # Mock user
        mock_user = MagicMock()
        mock_user.password_hash = "hashed_password"

        # Mock the query to return user
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query

        # Mock verify_credential to return False
        mock_verify.return_value = False

        success, result = self.user_service.authenticate_user("testuser", "wrongpassword")

        assert success is False
        assert result is None
        mock_verify.assert_called_once_with("wrongpassword", "hashed_password")

    @patch('users.services.verify_credential')
    @patch('users.services.UserModel')
    @patch('users.services.db_session')
    def test_authenticate_user_success(self, mock_db_session, mock_user_model, mock_verify):
        """Test successful user authentication."""
        # Mock user
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.password_hash = "hashed_password"
        mock_user.created_at = datetime.now(timezone.utc)
        mock_user.updated_at = datetime.now(timezone.utc)
        mock_user.last_login = None

        # Mock the query to return user
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query

        # Mock verify_credential to return True
        mock_verify.return_value = True

        # Mock db session
        mock_session = MagicMock()
        mock_db_session.session = mock_session

        success, result = self.user_service.authenticate_user("testuser", "password123")

        assert success is True
        assert result is not None
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert result["id"] == "user123"
        assert "password_hash" not in result

        mock_verify.assert_called_once_with("password123", "hashed_password")
        mock_session.commit.assert_called_once()

    def test_generate_token(self):
        """Test JWT token generation."""
        user_id = "user123"
        token = self.user_service.generate_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_with_claims(self):
        """Test JWT token generation with additional claims."""
        user_id = "user123"
        additional_claims = {"role": "admin", "permissions": "read,write"}
        token = self.user_service.generate_token(user_id, **additional_claims)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_filters_sensitive_claims(self):
        """Test that sensitive claims are filtered out."""
        user_id = "user123"
        # These should be filtered out
        sensitive_claims = {
            "password": "secret",
            "token": "another_token",
            "secret": "top_secret",
            "credential": "creds",
            "key": "api_key",
            "auth": "auth_data"
        }
        token = self.user_service.generate_token(user_id, **sensitive_claims)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_empty(self):
        """Test verifying an empty token."""
        success, payload = self.user_service.verify_token("")
        assert success is False
        assert payload is None

    def test_verify_token_none(self):
        """Test verifying a None token."""
        success, payload = self.user_service.verify_token(None)
        assert success is False
        assert payload is None

    def test_verify_token_invalid(self):
        """Test verifying an invalid token."""
        success, payload = self.user_service.verify_token("invalid_token")
        assert success is False
        assert payload is None

    def test_verify_token_valid(self):
        """Test verifying a valid token."""
        user_id = "user123"
        token = self.user_service.generate_token(user_id)

        success, payload = self.user_service.verify_token(token)

        assert success is True
        assert payload is not None
        assert payload["sub"] == user_id
        assert "iat" in payload
        assert "exp" in payload
        assert "jti" in payload


if __name__ == "__main__":
    pytest.main(["-v"])
