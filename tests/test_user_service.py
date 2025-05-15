"""test_user_service - Test module for user service."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from users.services import UserExistsError, UserService


# Mock the flask.models module to avoid import issues
class MockUser:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def query(cls):
        return MagicMock()


class MockDB:
    def __init__(self):
        self.session = MagicMock()

    # Add methods needed by the UserService
    def add(self, obj):
        pass

    def commit(self):
        pass


# Create patch for app_flask.models
patch("app_flask.models.User", MockUser).start()
patch("app_flask.models.db", MockDB()).start()


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def app_context(app):
    """Create an application context for testing."""
    with app.app_context():
        yield


@pytest.fixture
def user_service(app_context):
    """Create a UserService instance for testing."""
    return UserService(token_secret="test_secret")


def test_create_user(user_service):
    """Test creating a user."""
    # Create a mock user instance
    mock_user_instance = MockUser(
        id=1,
        username="testuser",
        email="test@example.com",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Set up the mocks
    with patch.object(MockUser, "query") as mock_query, patch.object(MockDB, "session"):
        # Mock the query to check if user exists
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.return_value.filter.return_value = mock_filter

        # Mock the User constructor
        with patch.object(MockUser, "__new__", return_value=mock_user_instance):
            # Call the method
            result = user_service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential="password123",
            )

            # Assertions
            assert result["username"] == "testuser"
            assert result["email"] == "test@example.com"
            assert "id" in result
            assert "auth_hash" not in result
            assert "password_hash" not in result


def test_create_user_existing_username(user_service):
    """Test creating a user with an existing username."""
    # Create a mock existing user
    existing_user = MockUser(username="testuser", email="existing@example.com")

    # Set up the mocks
    with patch.object(MockUser, "query") as mock_query:
        # Set up the mock to simulate existing user
        mock_filter = MagicMock()
        mock_filter.first.return_value = existing_user
        mock_query.return_value.filter.return_value = mock_filter

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
    # Create a mock user
    user = MockUser(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
    )

    # Set up the mocks
    with patch.object(MockUser, "query") as mock_query, patch(
        "users.auth.verify_credential"
    ) as mock_verify:
        # Set up the mocks
        mock_filter = MagicMock()
        mock_filter.first.return_value = user
        mock_query.return_value.filter.return_value = mock_filter
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
    # Create a mock user
    user = MockUser(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
    )

    # Set up the mocks
    with patch.object(MockUser, "query") as mock_query, patch(
        "users.auth.verify_credential"
    ) as mock_verify:
        # Set up the mocks
        mock_filter = MagicMock()
        mock_filter.first.return_value = user
        mock_query.return_value.filter.return_value = mock_filter
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
    # Set up the mocks
    with patch.object(MockUser, "query") as mock_query:
        # Set up the mock to return None (user not found)
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.return_value.filter.return_value = mock_filter

        # Call the method
        success, result = user_service.authenticate_user(
            username_or_email="nonexistent", auth_credential="password123"
        )

        # Assertions
        assert success is False
        assert result is None
