"""test_user_service - Test module for user service."""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from users.services import (
    UserService,
    AuthenticationError,
    UserExistsError,
    UserNotFoundError,
    TokenError,
)


@pytest.fixture
def user_service():
    """Create a UserService instance for testing."""
    return UserService(token_secret="test_secret")


def test_create_user(user_service):
    """Test creating a user."""
    # Mock the User model and db session
    with patch("flask.models.User") as mock_user, patch(
        "flask.models.db.session"
    ) as mock_session:
        # Set up the mock
        mock_user_instance = MagicMock()
        mock_user.return_value = mock_user_instance
        mock_user_instance.id = 1
        mock_user_instance.username = "testuser"
        mock_user_instance.email = "test@example.com"
        mock_user_instance.created_at = datetime.utcnow()
        mock_user_instance.updated_at = datetime.utcnow()

        # Mock the query to check if user exists
        mock_user.query.filter.return_value.first.return_value = None

        # Call the method
        result = user_service.create_user(
            username="testuser", email="test@example.com", auth_credential="password123"
        )

        # Assertions
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert "id" in result
        assert "auth_hash" not in result
        assert "password_hash" not in result
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


def test_create_user_existing_username(user_service):
    """Test creating a user with an existing username."""
    # Mock the User model and db session
    with patch("flask.models.User") as mock_user:
        # Set up the mock to simulate existing user
        existing_user = MagicMock()
        existing_user.username = "testuser"
        existing_user.email = "existing@example.com"
        mock_user.query.filter.return_value.first.return_value = existing_user

        # Call the method and expect an exception
        with pytest.raises(UserExistsError) as excinfo:
            user_service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential="password123",
            )

        assert "Username already exists" in str(excinfo.value)


def test_authenticate_user_success(user_service):
    """Test authenticating a user successfully."""
    # Mock the User model
    with patch("flask.models.User") as mock_user, patch(
        "users.auth.verify_credential"
    ) as mock_verify:
        # Set up the mocks
        user = MagicMock()
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.password_hash = "hashed_password"
        mock_user.query.filter.return_value.first.return_value = user
        mock_verify.return_value = True

        # Call the method
        success, result = user_service.authenticate_user(
            username_or_email="testuser", auth_credential="password123"
        )

        # Assertions
        assert success is True
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert "id" in result
        assert "password_hash" not in result


def test_authenticate_user_failure(user_service):
    """Test authenticating a user with invalid credentials."""
    # Mock the User model
    with patch("flask.models.User") as mock_user, patch(
        "users.auth.verify_credential"
    ) as mock_verify:
        # Set up the mocks
        user = MagicMock()
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.password_hash = "hashed_password"
        mock_user.query.filter.return_value.first.return_value = user
        mock_verify.return_value = False

        # Call the method
        success, result = user_service.authenticate_user(
            username_or_email="testuser", auth_credential="wrong_password"
        )

        # Assertions
        assert success is False
        assert result is None


def test_authenticate_user_not_found(user_service):
    """Test authenticating a non-existent user."""
    # Mock the User model
    with patch("flask.models.User") as mock_user:
        # Set up the mock to return None (user not found)
        mock_user.query.filter.return_value.first.return_value = None

        # Call the method
        success, result = user_service.authenticate_user(
            username_or_email="nonexistent", auth_credential="password123"
        )

        # Assertions
        assert success is False
        assert result is None
