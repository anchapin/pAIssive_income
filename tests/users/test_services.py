"""Tests for the users.services module."""

import logging
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

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


class TestUserService(unittest.TestCase):
    """Test cases for the UserService class."""

    def setUp(self):
        """Set up test environment."""
        self.token_secret = "test_secret_key"
        self.service = UserService(token_secret=self.token_secret)
        # Create a Flask app for testing
        self.app = Flask(__name__)
        # Configure the app for testing
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        # Push an application context
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up after tests."""
        # Pop the application context
        self.app_context.pop()

    def test_init_with_token_secret(self):
        """Test initialization with token secret."""
        service = UserService(token_secret=self.token_secret)
        assert service.token_secret == self.token_secret

    def test_init_without_token_secret(self):
        """Test initialization without token secret."""
        with pytest.raises(AuthenticationError):
            UserService(token_secret="")

    @patch("users.services.hash_credential")
    @patch("users.services.UserModel")
    @patch("users.services.db_session")
    def test_create_user_success(self, mock_db_session, mock_user_model, mock_hash_credential):
        """Test create_user with success."""
        # Mock hash_credential to return a hashed password
        mock_hash_credential.return_value = "hashed_password"

        # Mock the query to return no existing user
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_user_model.query = mock_query

        # Mock the new user
        mock_new_user = MagicMock()
        mock_new_user.id = 1
        mock_new_user.username = "testuser"
        mock_new_user.email = "test@example.com"
        mock_user_model.return_value = mock_new_user

        # Call the method
        result = self.service.create_user("testuser", "test@example.com", "password123")

        # Verify the result
        assert result["id"] == 1
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"

        # Verify that hash_credential was called
        mock_hash_credential.assert_called_once_with("password123")

        # Verify that the user was added and committed
        mock_db_session.session.add.assert_called_once_with(mock_new_user)
        mock_db_session.session.commit.assert_called_once()

    def test_create_user_missing_username(self):
        """Test create_user with missing username."""
        with pytest.raises(AuthenticationError) as context:
            self.service.create_user("", "test@example.com", "password123")
        assert str(context.value) == AuthenticationError.USERNAME_REQUIRED

    def test_create_user_missing_email(self):
        """Test create_user with missing email."""
        with pytest.raises(AuthenticationError) as context:
            self.service.create_user("testuser", "", "password123")
        assert str(context.value) == AuthenticationError.EMAIL_REQUIRED

    def test_create_user_missing_password(self):
        """Test create_user with missing password."""
        with pytest.raises(AuthenticationError) as context:
            self.service.create_user("testuser", "test@example.com", "")
        assert str(context.value) == AuthenticationError.PASSWORD_REQUIRED

    @patch("users.services.UserModel")
    @patch("users.services.db")
    def test_create_user_username_exists(self, mock_db, mock_user_model):
        """Test create_user with existing username."""
        # Mock the query to return an existing user with the same username
        mock_existing_user = MagicMock()
        mock_existing_user.username = "testuser"
        mock_existing_user.email = "existing@example.com"
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_existing_user
        mock_user_model.query = mock_query

        # Call the method and verify the exception
        with pytest.raises(UserExistsError) as context:
            self.service.create_user("testuser", "test@example.com", "password123")
        assert str(context.value) == UserExistsError.USERNAME_EXISTS

    @patch("users.services.UserModel")
    @patch("users.services.db")
    def test_create_user_email_exists(self, mock_db, mock_user_model):
        """Test create_user with existing email."""
        # Mock the query to return an existing user with the same email
        mock_existing_user = MagicMock()
        mock_existing_user.username = "existinguser"
        mock_existing_user.email = "test@example.com"
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_existing_user
        mock_user_model.query = mock_query

        # Call the method and verify the exception
        with pytest.raises(UserExistsError) as context:
            self.service.create_user("testuser", "test@example.com", "password123")
        assert str(context.value) == UserExistsError.EMAIL_EXISTS

    @patch("users.services.hash_credential")
    @patch("users.services.UserModel")
    @patch("users.services.db_session")
    def test_create_user_database_error(self, mock_db_session, mock_user_model, mock_hash_credential):
        """Test create_user with database error."""
        # Mock hash_credential to return a hashed password
        mock_hash_credential.return_value = "hashed_password"

        # Mock the query to return no existing user
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_user_model.query = mock_query

        # Mock the new user
        mock_new_user = MagicMock()
        mock_user_model.return_value = mock_new_user

        # Mock the session to raise an SQLAlchemyError
        from sqlalchemy.exc import SQLAlchemyError
        mock_db_session.session.commit.side_effect = SQLAlchemyError("Database error")

        # Call the method and verify the exception
        with pytest.raises(DatabaseSessionNotAvailableError):
            self.service.create_user("testuser", "test@example.com", "password123")

        # Verify that rollback was called
        mock_db_session.session.rollback.assert_called_once()

    @patch("users.services.UserModel")
    @patch("users.services.verify_credential")
    @patch("users.services.db_session")
    def test_authenticate_user_success(self, mock_db_session, mock_verify_credential, mock_user_model):
        """Test authenticate_user with success."""
        # Mock the query to return a user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.password_hash = "hashed_password"
        # Add last_login attribute to trigger the update
        mock_user.last_login = None

        # Fix the filter method to use filter instead of filter_by
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query

        # Mock verify_credential to return True
        mock_verify_credential.return_value = True

        # Call the method
        success, user_data = self.service.authenticate_user("testuser", "password123")

        # Verify the result
        assert success
        assert user_data["id"] == 1
        assert user_data["username"] == "testuser"
        assert user_data["email"] == "test@example.com"

        # Verify that verify_credential was called
        mock_verify_credential.assert_called_once_with("password123", "hashed_password")

        # Verify that db.session.commit was called
        mock_db_session.session.commit.assert_called_once()

    @patch("users.services.UserModel")
    def test_authenticate_user_missing_credentials(self, mock_user_model):
        """Test authenticate_user with missing credentials."""
        # Call the method with missing username
        success1, user_data1 = self.service.authenticate_user("", "password123")
        assert not success1
        assert user_data1 is None

        # Call the method with missing password
        success2, user_data2 = self.service.authenticate_user("testuser", "")
        assert not success2
        assert user_data2 is None

    @patch("users.services.UserModel")
    def test_authenticate_user_user_not_found(self, mock_user_model):
        """Test authenticate_user with user not found."""
        # Mock the query to return no user
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_user_model.query = mock_query

        # Call the method
        success, user_data = self.service.authenticate_user("testuser", "password123")

        # Verify the result
        assert not success
        assert user_data is None

    @patch("users.services.UserModel")
    @patch("users.services.verify_credential")
    def test_authenticate_user_invalid_password(self, mock_verify_credential, mock_user_model):
        """Test authenticate_user with invalid password."""
        # Mock the query to return a user
        mock_user = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query

        # Mock verify_credential to return False
        mock_verify_credential.return_value = False

        # Call the method
        success, user_data = self.service.authenticate_user("testuser", "password123")

        # Verify the result
        assert not success
        assert user_data is None

    @patch("users.services.UserModel")
    @patch("users.services.verify_credential")
    @patch("users.services.db_session")
    def test_authenticate_user_update_error(self, mock_db_session, mock_verify_credential, mock_user_model):
        """Test authenticate_user with error updating last login."""
        # Mock the query to return a user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.password_hash = "hashed_password"
        # Add last_login attribute to trigger the update
        mock_user.last_login = None

        # Fix the filter method to use filter instead of filter_by
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query

        # Mock verify_credential to return True
        mock_verify_credential.return_value = True

        # Mock the session to raise an exception
        from sqlalchemy.exc import SQLAlchemyError
        mock_db_session.session.commit.side_effect = SQLAlchemyError("Database error")

        # Call the method
        success, user_data = self.service.authenticate_user("testuser", "password123")

        # Verify the result
        assert not success
        assert user_data is None

        # Verify rollback was called
        mock_db_session.session.rollback.assert_called_once()

    @patch("users.services.datetime")
    @patch("users.services.uuid")
    def test_generate_token(self, mock_uuid, mock_datetime):
        """Test generate_token."""
        # Mock datetime and uuid
        mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now
        mock_uuid.uuid4.return_value = "test-uuid"

        # Call the method
        token = self.service.generate_token("user123", role="admin", name="Test User")

        # Decode the token and verify the payload
        # Use the verify=False option to skip signature verification since we're testing token generation
        payload = jwt.decode(token, self.token_secret, algorithms=["HS256"], options={"verify_exp": False})
        assert payload["sub"] == "user123"
        assert payload["iat"] == mock_now.timestamp()
        assert payload["exp"] == mock_now.timestamp() + 3600
        assert payload["jti"] == "test-uuid"
        assert payload["role"] == "admin"
        assert payload["name"] == "Test User"

    def test_verify_token_valid(self):
        """Test verify_token with valid token."""
        # Generate a valid token
        payload = {
            "sub": "user123",
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": datetime.now(timezone.utc).timestamp() + 3600,
            "jti": str(uuid.uuid4()),
            "role": "admin"
        }
        token = jwt.encode(payload, self.token_secret, algorithm="HS256")

        # Call the method
        success, decoded_payload = self.service.verify_token(token)

        # Verify the result
        assert success
        assert decoded_payload["sub"] == "user123"
        assert decoded_payload["role"] == "admin"

    def test_verify_token_missing_token(self):
        """Test verify_token with missing token."""
        # Call the method
        success, payload = self.service.verify_token("")

        # Verify the result
        assert not success
        assert payload is None

    def test_verify_token_expired(self):
        """Test verify_token with expired token."""
        # Generate an expired token
        payload = {
            "sub": "user123",
            "iat": datetime.now(timezone.utc).timestamp() - 7200,
            "exp": datetime.now(timezone.utc).timestamp() - 3600,
            "jti": str(uuid.uuid4())
        }
        token = jwt.encode(payload, self.token_secret, algorithm="HS256")

        # Call the method
        success, decoded_payload = self.service.verify_token(token)

        # Verify the result
        assert not success
        assert decoded_payload is None

    def test_verify_token_invalid_signature(self):
        """Test verify_token with invalid signature."""
        # Generate a token with a different secret
        payload = {
            "sub": "user123",
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": datetime.now(timezone.utc).timestamp() + 3600,
            "jti": str(uuid.uuid4())
        }
        token = jwt.encode(payload, "different_secret", algorithm="HS256")

        # Call the method
        success, decoded_payload = self.service.verify_token(token)

        # Verify the result
        assert not success
        assert decoded_payload is None

    def test_verify_token_missing_required_claims(self):
        """Test verify_token with missing required claims."""
        # Generate a token without the 'sub' claim
        payload = {
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": datetime.now(timezone.utc).timestamp() + 3600,
            "jti": str(uuid.uuid4())
        }
        token = jwt.encode(payload, self.token_secret, algorithm="HS256")

        # Call the method
        success, decoded_payload = self.service.verify_token(token)

        # Verify the result
        assert not success
        assert decoded_payload is None


if __name__ == "__main__":
    unittest.main()
