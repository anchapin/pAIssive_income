"""test_user_service - Test module for user service."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from users.services import AuthenticationError, UserExistsError, UserService


class MockUser:
    """Mock User model for testing."""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.username = kwargs.get("username", "testuser")
        self.email = kwargs.get("email", "test@example.com")
        self.password_hash = kwargs.get("password_hash", "hashed_password")
        self.created_at = kwargs.get("created_at", datetime.now(tz=timezone.utc))
        self.updated_at = kwargs.get("updated_at", datetime.now(tz=timezone.utc))

    @classmethod
    def query(cls):
        """Mock query method."""
        return MagicMock()


@pytest.fixture
def user_service():
    """Create a UserService instance for testing."""
    return UserService(token_secret="test_secret")  # noqa: S106 - Test data only


@pytest.fixture
def mock_user():
    """Create a mock user instance."""
    return MockUser(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",  # noqa: S106 - Test data only
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )


class TestUserService:
    """Test cases for UserService."""

    @patch("users.services.hash_credential", return_value="hashed_credential")
    @patch("users.services.UserModel")
    @patch("users.services.db_session")
    def test_create_user_success(self, mock_db_session, mock_user_model, mock_hash, mock_user):
        """Test creating a user successfully."""
        # Setup mocks
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None  # No existing user
        mock_query.filter.return_value = mock_filter
        mock_user_model.query = mock_query
        mock_user_model.return_value = mock_user

        # Mock db_session with session attribute (matching actual implementation)
        mock_session = MagicMock()
        mock_db_session.session = mock_session

        # Create service and call method
        service = UserService(token_secret="test_secret")  # noqa: S106 - Test data only
        result = service.create_user(
            username="testuser",
            email="test@example.com",
            auth_credential="test_credential"
        )

        # Assertions
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert "id" in result
        assert "password_hash" not in result
        assert "auth_hash" not in result

        # Verify mocks were called
        mock_hash.assert_called_once_with("test_credential")
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch("users.services.UserModel")
    def test_create_user_existing_username(self, mock_user_model, user_service):
        """Test creating a user with an existing username."""
        # Setup mock to return existing user
        existing_user = MockUser(username="testuser", email="existing@example.com")
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = existing_user
        mock_query.filter.return_value = mock_filter
        mock_user_model.query = mock_query

        # Call method and expect exception
        with pytest.raises(UserExistsError, match="already exists"):
            user_service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential="test_credential"
            )

    @patch("users.services.verify_credential", return_value=True)
    @patch("users.services.UserModel")
    def test_authenticate_user_success(self, mock_user_model, mock_verify, mock_user):
        """Test authenticating a user successfully."""
        # Setup mocks
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_user_model.query = mock_query

        # Create service and call method
        service = UserService(token_secret="test_secret")  # noqa: S106 - Test data only
        success, result = service.authenticate_user(
            username_or_email="testuser",
            auth_credential="test_credential"
        )

        # Assertions
        assert success is True
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert "id" in result
        assert "password_hash" not in result

        # Verify verify_credential was called
        mock_verify.assert_called_once_with("test_credential", "hashed_password")

    @patch("users.services.verify_credential", return_value=False)
    @patch("users.services.UserModel")
    def test_authenticate_user_invalid_credentials(self, mock_user_model, mock_verify, mock_user):
        """Test authenticating a user with invalid credentials."""
        # Setup mocks
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_user_model.query = mock_query

        # Create service and call method
        service = UserService(token_secret="test_secret")  # noqa: S106 - Test data only
        success, result = service.authenticate_user(
            username_or_email="testuser",
            auth_credential="wrong_credential"
        )

        # Assertions
        assert success is False
        assert result is None

        # Verify verify_credential was called
        mock_verify.assert_called_once_with("wrong_credential", "hashed_password")

    @patch("users.services.UserModel")
    def test_authenticate_user_not_found(self, mock_user_model):
        """Test authenticating a non-existent user."""
        # Setup mock to return None (user not found)
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_user_model.query = mock_query

        # Create service and call method
        service = UserService(token_secret="test_secret")  # noqa: S106 - Test data only
        success, result = service.authenticate_user(
            username_or_email="nonexistent",
            auth_credential="test_credential"
        )

        # Assertions
        assert success is False
        assert result is None

    def test_user_service_initialization_without_token_secret(self):
        """Test that UserService raises error when no token secret is provided."""
        with pytest.raises(AuthenticationError):
            UserService(token_secret=None)

    def test_user_service_initialization_with_token_secret(self):
        """Test that UserService initializes correctly with token secret."""
        test_secret = "test_secret"  # noqa: S105 - Test data only
        service = UserService(token_secret=test_secret)
        assert service.token_secret == test_secret
        assert service.token_expiry == 3600  # Default value
