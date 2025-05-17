"""Tests for the users.services module."""

import logging
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import uuid
import jwt

import pytest

from users.services import (
    UserService,
    AuthenticationError,
    DatabaseSessionNotAvailableError,
    UserExistsError,
    UserModelNotAvailableError,
    TokenError,
)


class TestUserService(unittest.TestCase):
    """Test cases for the UserService class."""

    def setUp(self):
        """Set up test environment."""
        self.token_secret = "test_secret_key"
        self.service = UserService(self.token_secret)

    def test_init_with_token_secret(self):
        """Test initialization with token secret."""
        service = UserService(self.token_secret)
        self.assertEqual(service.token_secret, self.token_secret)

    def test_init_without_token_secret(self):
        """Test initialization without token secret."""
        with self.assertRaises(AuthenticationError):
            UserService("")

    @patch("users.services.UserModel")
    @patch("users.services.db")
    def test_create_user_success(self, mock_db, mock_user_model):
        """Test create_user with success."""
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
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["username"], "testuser")
        self.assertEqual(result["email"], "test@example.com")

        # Verify that the user was added and committed
        mock_db.session.add.assert_called_once_with(mock_new_user)
        mock_db.session.commit.assert_called_once()

    def test_create_user_missing_username(self):
        """Test create_user with missing username."""
        with self.assertRaises(AuthenticationError) as context:
            self.service.create_user("", "test@example.com", "password123")
        self.assertEqual(str(context.exception), AuthenticationError.USERNAME_REQUIRED)

    def test_create_user_missing_email(self):
        """Test create_user with missing email."""
        with self.assertRaises(AuthenticationError) as context:
            self.service.create_user("testuser", "", "password123")
        self.assertEqual(str(context.exception), AuthenticationError.EMAIL_REQUIRED)

    def test_create_user_missing_password(self):
        """Test create_user with missing password."""
        with self.assertRaises(AuthenticationError) as context:
            self.service.create_user("testuser", "test@example.com", "")
        self.assertEqual(str(context.exception), AuthenticationError.PASSWORD_REQUIRED)

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
        with self.assertRaises(UserExistsError) as context:
            self.service.create_user("testuser", "test@example.com", "password123")
        self.assertEqual(str(context.exception), UserExistsError.USERNAME_EXISTS)

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
        with self.assertRaises(UserExistsError) as context:
            self.service.create_user("testuser", "test@example.com", "password123")
        self.assertEqual(str(context.exception), UserExistsError.EMAIL_EXISTS)

    @patch("users.services.UserModel")
    @patch("users.services.db")
    def test_create_user_database_error(self, mock_db, mock_user_model):
        """Test create_user with database error."""
        # Mock the query to return no existing user
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_user_model.query = mock_query

        # Mock the session to raise an SQLAlchemyError
        from sqlalchemy.exc import SQLAlchemyError
        mock_db.session.commit.side_effect = SQLAlchemyError("Database error")

        # Call the method and verify the exception
        with self.assertRaises(DatabaseSessionNotAvailableError):
            self.service.create_user("testuser", "test@example.com", "password123")

        # Verify that rollback was called
        mock_db.session.rollback.assert_called_once()

    @patch("users.services.UserModel")
    @patch("users.services.verify_credential")
    @patch("users.services.db")
    def test_authenticate_user_success(self, mock_db, mock_verify_credential, mock_user_model):
        """Test authenticate_user with success."""
        # Mock the query to return a user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.password_hash = "hashed_password"
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query

        # Mock verify_credential to return True
        mock_verify_credential.return_value = True

        # Call the method
        success, user_data = self.service.authenticate_user("testuser", "password123")

        # Verify the result
        self.assertTrue(success)
        self.assertEqual(user_data["id"], 1)
        self.assertEqual(user_data["username"], "testuser")
        self.assertEqual(user_data["email"], "test@example.com")

        # Verify that verify_credential was called
        mock_verify_credential.assert_called_once_with("password123", "hashed_password")

        # Verify that db.session.commit was called
        mock_db.session.commit.assert_called_once()

    @patch("users.services.UserModel")
    def test_authenticate_user_missing_credentials(self, mock_user_model):
        """Test authenticate_user with missing credentials."""
        # Call the method with missing username
        success1, user_data1 = self.service.authenticate_user("", "password123")
        self.assertFalse(success1)
        self.assertIsNone(user_data1)

        # Call the method with missing password
        success2, user_data2 = self.service.authenticate_user("testuser", "")
        self.assertFalse(success2)
        self.assertIsNone(user_data2)

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
        self.assertFalse(success)
        self.assertIsNone(user_data)

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
        self.assertFalse(success)
        self.assertIsNone(user_data)

    @patch("users.services.UserModel")
    @patch("users.services.verify_credential")
    @patch("users.services.db")
    def test_authenticate_user_update_error(self, mock_db, mock_verify_credential, mock_user_model):
        """Test authenticate_user with error updating last login."""
        # Mock the query to return a user
        mock_user = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_model.query = mock_query

        # Mock verify_credential to return True
        mock_verify_credential.return_value = True

        # Mock the session to raise an exception
        mock_db.session.commit.side_effect = Exception("Database error")

        # Call the method
        success, user_data = self.service.authenticate_user("testuser", "password123")

        # Verify the result
        self.assertFalse(success)
        self.assertIsNone(user_data)

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
        self.assertEqual(payload["sub"], "user123")
        self.assertEqual(payload["iat"], mock_now.timestamp())
        self.assertEqual(payload["exp"], mock_now.timestamp() + 3600)
        self.assertEqual(payload["jti"], "test-uuid")
        self.assertEqual(payload["role"], "admin")
        self.assertEqual(payload["name"], "Test User")

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
        self.assertTrue(success)
        self.assertEqual(decoded_payload["sub"], "user123")
        self.assertEqual(decoded_payload["role"], "admin")

    def test_verify_token_missing_token(self):
        """Test verify_token with missing token."""
        # Call the method
        success, payload = self.service.verify_token("")

        # Verify the result
        self.assertFalse(success)
        self.assertIsNone(payload)

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
        self.assertFalse(success)
        self.assertIsNone(decoded_payload)

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
        self.assertFalse(success)
        self.assertIsNone(decoded_payload)

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
        self.assertFalse(success)
        self.assertIsNone(decoded_payload)


if __name__ == "__main__":
    unittest.main()
