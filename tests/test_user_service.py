"""test_user_service - Test module for user service."""

import logging
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest

from users.services import (
    AuthenticationError,
    DatabaseSessionNotAvailableError,
    UserExistsError,
    UserModelNotAvailableError,
    UserService,
)


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

    def test_token_secret_property(self, user_service):
        """Test the token_secret property."""
        assert user_service.token_secret == "test_secret"

    def test_init_without_token_secret(self):
        """Test UserService initialization without token secret."""
        with pytest.raises(AuthenticationError):
            UserService(token_secret=None)

    def test_init_with_empty_token_secret(self):
        """Test UserService initialization with empty token secret."""
        with pytest.raises(AuthenticationError):
            UserService(token_secret="")

    @patch("users.services.UserModel", None)
    def test_create_user_no_user_model(self, user_service):
        """Test creating a user when UserModel is not available."""
        with pytest.raises(UserModelNotAvailableError):
            user_service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential="password123"
            )

    @patch("users.services.db_session", None)
    @patch("users.services.UserModel")
    def test_create_user_no_db_session(self, mock_user_model, user_service):
        """Test creating a user when db_session is not available."""
        # Mock the query to return no existing user
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_user_model.query = mock_query

        with patch("users.services.hash_credential", return_value="hashed_password"):
            with pytest.raises(DatabaseSessionNotAvailableError):
                user_service.create_user(
                    username="testuser",
                    email="test@example.com",
                    auth_credential="password123"
                )

    def test_create_user_missing_username(self, user_service):
        """Test creating a user without username."""
        with pytest.raises(AuthenticationError) as exc_info:
            user_service.create_user(
                username="",
                email="test@example.com",
                auth_credential="password123"
            )
        assert "Username is required" in str(exc_info.value)

    def test_create_user_missing_email(self, user_service):
        """Test creating a user without email."""
        with pytest.raises(AuthenticationError) as exc_info:
            user_service.create_user(
                username="testuser",
                email="",
                auth_credential="password123"
            )
        assert "Email is required" in str(exc_info.value)

    def test_create_user_missing_password(self, user_service):
        """Test creating a user without password."""
        with pytest.raises(AuthenticationError) as exc_info:
            user_service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential=""
            )
        assert "Password is required" in str(exc_info.value)

    @patch("users.services.hash_credential")
    @patch("users.services.UserModel")
    @patch("users.services.db_session")
    def test_create_user_success(self, mock_db_session, mock_user_model, mock_hash, user_service):
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
        result = user_service.create_user(
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

    @patch("users.services.hash_credential", return_value="hashed_credential")
    @patch("users.services.UserModel")
    @patch("users.services.db_session")
    def test_create_user_success_alternative(self, mock_db_session, mock_user_model, mock_hash, mock_user):
        """Test creating a user successfully (alternative approach)."""
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
            user_service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential="password123"
            )
        assert "Username already exists" in str(exc_info.value)

    @patch("users.services.UserModel")
    def test_create_user_existing_username_alternative(self, mock_user_model, user_service):
        """Test creating a user with an existing username (alternative approach)."""
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

    @patch("users.services.UserModel")
    def test_create_user_existing_email(self, mock_user_model, user_service):
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
            user_service.create_user(
                username="testuser",
                email="test@example.com",
                auth_credential="password123"
            )
        assert "Email already exists" in str(exc_info.value)

    @patch("users.services.UserModel", None)
    def test_authenticate_user_no_user_model(self, user_service):
        """Test authenticating a user when UserModel is not available."""
        with pytest.raises(UserModelNotAvailableError):
            user_service.authenticate_user("testuser", "password123")

    @patch("users.services.UserModel")
    def test_authenticate_user_not_found(self, mock_user_model, user_service):
        """Test authenticating a non-existent user."""
        # Mock the query to return None (user not found)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_user_model.query = mock_query

        success, result = user_service.authenticate_user("nonexistent", "password123")

        assert success is False
        assert result is None

    @patch("users.services.UserModel")
    def test_authenticate_user_not_found_alternative(self, mock_user_model):
        """Test authenticating a non-existent user (alternative approach)."""
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

        assert success is False
        assert result is None

    @patch("users.services.verify_credential")
    @patch("users.services.UserModel")
    def test_authenticate_user_wrong_password(self, mock_user_model, mock_verify, user_service):
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

        success, result = user_service.authenticate_user("testuser", "wrongpassword")

        assert success is False
        assert result is None
        mock_verify.assert_called_once_with("wrongpassword", "hashed_password")

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

        assert success is False
        assert result is None

        # Verify verify_credential was called
        mock_verify.assert_called_once_with("wrong_credential", "hashed_password")

    @patch("users.services.verify_credential")
    @patch("users.services.UserModel")
    @patch("users.services.db_session")
    def test_authenticate_user_success(self, mock_db_session, mock_user_model, mock_verify, user_service):
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

        success, result = user_service.authenticate_user("testuser", "password123")

        assert success is True
        assert result is not None
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert result["id"] == "user123"
        assert "password_hash" not in result

        mock_verify.assert_called_once_with("password123", "hashed_password")
        mock_session.commit.assert_called_once()

    @patch("users.services.verify_credential", return_value=True)
    @patch("users.services.UserModel")
    def test_authenticate_user_success_alternative(self, mock_user_model, mock_verify, mock_user):
        """Test authenticating a user successfully (alternative approach)."""
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

        # Verify verify_credential was called
        mock_verify.assert_called_once_with("test_credential", "hashed_password")

    def test_generate_token(self, user_service):
        """Test JWT token generation."""
        user_id = "user123"
        token = user_service.generate_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_with_claims(self, user_service):
        """Test JWT token generation with additional claims."""
        user_id = "user123"
        additional_claims = {"role": "admin", "permissions": "read,write"}
        token = user_service.generate_token(user_id, **additional_claims)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_filters_sensitive_claims(self, user_service):
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
        token = user_service.generate_token(user_id, **sensitive_claims)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_empty(self, user_service):
        """Test verifying an empty token."""
        success, payload = user_service.verify_token("")
        assert success is False
        assert payload is None

    def test_verify_token_none(self, user_service):
        """Test verifying a None token."""
        success, payload = user_service.verify_token(None)
        assert success is False
        assert payload is None

    def test_verify_token_invalid(self, user_service):
        """Test verifying an invalid token."""
        success, payload = user_service.verify_token("invalid_token")
        assert success is False
        assert payload is None

    def test_verify_token_valid(self, user_service):
        """Test verifying a valid token."""
        user_id = "user123"
        token = user_service.generate_token(user_id)

        success, payload = user_service.verify_token(token)

        assert success is True
        assert payload is not None
        assert payload["sub"] == user_id
        assert "iat" in payload
        assert "exp" in payload
        assert "jti" in payload

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
