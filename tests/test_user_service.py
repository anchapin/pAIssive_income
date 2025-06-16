"""test_user_service - Test module for user service."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

# Import at the top level
from tests.constants import TEST_SECRET
from users.models import db
from users.services import AuthenticationError, UserExistsError, UserService


# Mock the app_flask module to avoid import issues
class MockUser:
    """Mock user class for testing without database dependencies."""

    def __init__(self, user_id=None, username=None, email=None, password_hash=None):
        """Initialize mock user."""
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def query():
        """Mock query method."""
        return MagicMock()


class TestableUserService(UserService):
    """Testable version of UserService that skips database requirements."""

    def __init__(self, token_secret: str = TEST_SECRET):
        """Initialize testable user service."""
        super().__init__(token_secret=token_secret)
        # Additional test-specific initialization can go here


# Add methods needed by the UserService
def add(self, obj):
    pass


# Create patch for flask.models
patch("users.models.User", MockUser).start()

# Patch the db object itself since it's a session
patch("users.models.db", MagicMock()).start()

# Mock Flask app context
patch("flask.has_app_context", MagicMock(return_value=True)).start()
patch("flask.current_app", MagicMock()).start()


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
def user_service():
    """Create a UserService instance for testing."""
    return UserService(token_secret="test_secret")  # noqa: S106 - Test data only


@patch("users.services.hash_credential", return_value="hashed_credential")
def test_create_user(mock_hash):
    """Test creating a user."""
    # Create a mock user instance (not used but kept for clarity)
    _ = MockUser(
        user_id=1,
        username="testuser",
        email="test@example.com",
    )

    # Set up the mocks
    with patch("users.services.UserModel", MockUser), patch(
        "users.services.db_session"
    ), patch.object(MockUser, "query") as mock_query:
        # Create a mock filter that returns None for first() to indicate no existing user
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter

        # Test user creation
        service = TestableUserService()
        service.create_user(
            username="testuser",
            email="test@example.com",
            auth_credential="test_credential",
        )


def test_create_user_with_duplicate_email():
    """Test creating a user with duplicate email raises UserExistsError."""
    service = TestableUserService()

    # Mock the UserModel.query().filter().first() to return an existing user
    with patch("users.services.UserModel") as mock_user_model:
        mock_query = MagicMock()
        mock_filter = MagicMock()
        existing_user = MockUser(user_id=1, email="test@example.com")
        mock_filter.first.return_value = existing_user
        mock_query.filter.return_value = mock_filter
        mock_user_model.query.return_value = mock_query

        # This should raise UserExistsError
        with pytest.raises(UserExistsError) as excinfo:
            service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential="test_credential",
            )

        assert "User already exists" in str(excinfo.value)


def test_create_user_with_duplicate_username():
    """Test creating a user with duplicate username raises UserExistsError."""
    service = TestableUserService()

    # Mock the UserModel.query().filter().first() to return an existing user
    with patch("users.services.UserModel") as mock_user_model:
        mock_query = MagicMock()
        mock_filter = MagicMock()
        existing_user = MockUser(user_id=1, username="testuser")
        mock_filter.first.return_value = existing_user
        mock_query.filter.return_value = mock_filter
        mock_user_model.query.return_value = mock_query

        # This should raise UserExistsError
        with pytest.raises(UserExistsError) as excinfo:
            service.create_user(
                username="testuser",
                email="new@example.com",
                auth_credential="test_credential",
            )

        assert "User already exists" in str(excinfo.value)


def test_create_user_with_both_duplicate():
    """Test creating a user with duplicate username and email."""
    service = TestableUserService()

    # Mock the UserModel.query().filter().first() to return an existing user
    with patch("users.services.UserModel") as mock_user_model:
        mock_query = MagicMock()
        mock_filter = MagicMock()
        existing_user = MockUser(
            user_id=1, username="testuser", email="test@example.com"
        )
        mock_filter.first.return_value = existing_user
        mock_query.filter.return_value = mock_filter
        mock_user_model.query.return_value = mock_query

        # This should raise UserExistsError
        with pytest.raises(UserExistsError) as excinfo:
            service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential="test_credential",
            )

        # Should mention email since that's checked first
        assert "Email already exists" in str(excinfo.value)


class TestUserService:
    """Test cases for UserService."""

    @patch("users.services.hash_credential", return_value="hashed_credential")
    @patch("users.services.UserModel")
    def test_create_user_success(self, mock_user_model, mock_hash):
        """Test creating a user successfully."""
        # Setup mocks
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None  # No existing user
        mock_query.filter.return_value = mock_filter
        mock_user_model.query.return_value = mock_query

        # Create service and call method
        service = UserService(token_secret=TEST_SECRET)

        # Mock the database session
        with patch("users.services.db_session") as mock_session:
            service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential="test_credential",
            )

            # Verify mocks were called
            mock_hash.assert_called_once_with("test_credential")
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    @patch("users.services.verify_credential", return_value=False)
    @patch("users.services.UserModel")
    def test_authenticate_user_invalid_credentials(self, mock_user_model, mock_verify):
        """Test authenticating a user with invalid credentials."""
        # Setup mocks
        mock_user = MagicMock()
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_user_model.query.return_value = mock_query

        # Create service and call method
        service = UserService(token_secret=TEST_SECRET)
        success, result = service.authenticate_user(
            username_or_email="testuser", auth_credential="wrong_credential"
        )

        # Verify mocks
        mock_verify.assert_called_once()

        # Assertions
        assert success is False
        assert result is None


def test_authenticate_user_not_found():
    """Test authenticating a non-existent user."""
    # Set up the mocks
    with patch("users.services.UserModel") as mock_user_model:
        # Set up the mock to return None (user not found)
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_user_model.query.return_value = mock_query

        # Create service and call method
        service = UserService(token_secret=TEST_SECRET)
        success, result = service.authenticate_user(
            username_or_email="nonexistent", auth_credential="test_credential"
        )

        # Assertions
        assert success is False
        assert result is None


def test_user_service_initialization_without_token_secret():
    """Test that UserService raises error when no token secret is provided."""
    with pytest.raises(AuthenticationError):
        UserService(token_secret=None)


def test_user_service_initialization_with_token_secret():
    """Test that UserService initializes correctly with token secret."""
    # The following test credentials are safe for use in test code only.
    service = UserService(token_secret=TEST_SECRET)
    assert service.token_secret == TEST_SECRET
    assert service.token_expiry == 3600  # Default value
