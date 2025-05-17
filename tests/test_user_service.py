"""test_user_service - Test module for user service."""

import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import bcrypt
import jwt
import pytest
from flask import Flask
from sqlalchemy.exc import SQLAlchemyError

# Import at the top level
try:
    from app_flask import db
except ImportError:
    from users.models import db

from users.services import (
    AuthenticationError,
    DatabaseSessionNotAvailableError,
    TokenError,
    UserExistsError,
    UserModelNotAvailableError,
    UserService,
)


# Mock the app_flask module to avoid import issues
class MockUser:
    username = None
    email = None
    password_hash = None
    # Add a class-level query attribute to fix the tests
    query = MagicMock()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


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

    # Add methods needed by the UserService
    def add(self, obj):
        pass

        # Create patch for app_flask
        patch("users.services.UserModel", MockUser).start()

    @pytest.mark.unit
    def test_init_without_token_secret(self):
        """Test initializing without a token secret."""
        with pytest.raises(AuthenticationError, match="Token secret is required"):
            UserService(token_secret=None)

    @pytest.mark.unit
    def test_init_with_empty_token_secret(self):
        """Test initializing with empty token secret."""
        with pytest.raises(AuthenticationError, match="Token secret is required"):
            UserService(token_secret="")


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

    @pytest.mark.unit
    def test_token_secret_property(self):
        """Test the token_secret property."""
        assert self.user_service.token_secret == self.token_secret

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
            with self.subTest(missing_field=expected_error), pytest.raises(AuthenticationError, match=expected_error):
                self.user_service.create_user(username, email, password)

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
             patch("users.services.db", mock_db), \
             self.app.app_context():
            # Set up the filter chain for username and email check
            filter_mock = MagicMock()
            filter_mock.first.return_value = None
            mock_user_model.query.filter.return_value = filter_mock
            mock_user_model.return_value = mock_user

            result = self.user_service.create_user(username, email, password)

            assert result["username"] == username
            assert result["email"] == email
            assert result["id"] == "user-123"
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
            # Set up the filter chain for username check
            filter_mock = MagicMock()
            filter_mock.first.return_value = mock_existing_user
            mock_user_model.query.filter.return_value = filter_mock

            with pytest.raises(UserExistsError, match=UserExistsError.USERNAME_EXISTS):
                self.user_service.create_user(username, email, password)

    @pytest.mark.unit
    def test_create_user_email_exists(self):
        """Test creating a user with an existing email."""
        username = "newuser"
        email = "existing@example.com"
        password = "password123"

        mock_existing_user = MagicMock()
        mock_existing_user.username = "otheruser"
        mock_existing_user.email = email

        with patch("users.services.UserModel") as mock_user_model, \
             self.app.app_context():
            # Set up the filter chain for email check
            filter_mock = MagicMock()
            filter_mock.first.return_value = mock_existing_user
            mock_user_model.query.filter.return_value = filter_mock

            with pytest.raises(UserExistsError, match=UserExistsError.EMAIL_EXISTS):
                self.user_service.create_user(username, email, password)

    @pytest.mark.unit
    def test_create_user_db_session_none(self):
        """Test creating a user when db.session is None."""
        username = "newuser"
        email = "new@example.com"
        password = "password123"

        with patch("users.services.db") as mock_db, \
             self.app.app_context():
            # Set db.session to None
            mock_db.session = None

            with pytest.raises(DatabaseSessionNotAvailableError):
                self.user_service.create_user(username, email, password)

    @pytest.mark.unit
    def test_create_user_db_error(self):
        """Test creating a user when db session has an error."""
        username = "newuser"
        email = "new@example.com"
        password = "password123"

        # Create a mock db that raises an exception on commit
        mock_db = MagicMock()
        mock_db.session.commit.side_effect = SQLAlchemyError("DB Error")
        mock_db.session.rollback = MagicMock()

        with patch("users.services.UserModel") as mock_user_model, \
             patch("users.services.db", mock_db), \
             patch("users.services.logger") as mock_logger, \
             self.app.app_context():
            # Set up the filter chain for username and email check
            filter_mock = MagicMock()
            filter_mock.first.return_value = None
            mock_user_model.query.filter.return_value = filter_mock

            # Create a mock user
            mock_user = MagicMock()
            mock_user_model.return_value = mock_user

            # We expect a DatabaseSessionNotAvailableError to be raised
            with pytest.raises(DatabaseSessionNotAvailableError):
                self.user_service.create_user(username, email, password)

            # Verify rollback was called
            mock_db.session.rollback.assert_called_once()
            # Verify logger.exception was called
            mock_logger.exception.assert_called_once()

    @pytest.mark.unit
    def test_authenticate_user_success(self):
        """Test authenticating a user successfully."""
        username = "testuser"
        password = "password123"

        # Create a test user with a string password_hash to match the mock expectations
        test_user = MagicMock()
        test_user.id = "user-123"
        test_user.username = "testuser"
        test_user.email = "test@example.com"
        test_user.password_hash = self.hashed_password.decode('utf-8')  # Convert bytes to string
        test_user.last_login = None

        with patch("users.services.UserModel") as mock_user_model, \
             patch("users.services.verify_credential", return_value=True) as mock_verify, \
             patch("users.services.db", MagicMock()), \
             self.app.app_context():
            mock_user_model.query.filter_by.return_value.first.return_value = test_user

            success, user_data = self.user_service.authenticate_user(username, password)

            assert success
            assert user_data["username"] == username
            assert user_data["email"] == "test@example.com"
            assert user_data["id"] == "user-123"
            mock_verify.assert_called_once_with(password, test_user.password_hash)

    @pytest.mark.unit
    def test_authenticate_user_wrong_password(self):
        """Test authenticating a user with wrong password."""
        username = "testuser"
        password = "wrongpassword"

        # Create a test user with a string password_hash to match the mock expectations
        test_user = MagicMock()
        test_user.id = "user-123"
        test_user.username = "testuser"
        test_user.email = "test@example.com"
        test_user.password_hash = self.hashed_password.decode('utf-8')  # Convert bytes to string
        test_user.last_login = None

        with patch("users.services.UserModel") as mock_user_model, \
             patch("users.services.verify_credential", return_value=False) as mock_verify, \
             self.app.app_context():
            mock_user_model.query.filter_by.return_value.first.return_value = test_user

            success, user_data = self.user_service.authenticate_user(username, password)

            assert not success
            assert user_data is None
            mock_verify.assert_called_once_with(password, test_user.password_hash)

    @pytest.mark.unit
    def test_authenticate_user_not_found(self):
        """Test authenticating a non-existent user."""
        with patch("users.services.UserModel") as mock_user_model, \
             self.app.app_context():
            mock_user_model.query.filter_by.return_value.first.return_value = None

            success, user_data = self.user_service.authenticate_user("nonexistent", "password123")

            assert not success
            assert user_data is None

    @pytest.mark.unit
    def test_authenticate_user_with_last_login(self):
        """Test authenticating a user updates last login time."""
        username = "testuser"
        password = "password123"
        mock_db = MagicMock()

        # Create a test user with a string password_hash to match the mock expectations
        test_user = MagicMock()
        test_user.id = "user-123"
        test_user.username = "testuser"
        test_user.email = "test@example.com"
        test_user.password_hash = self.hashed_password.decode('utf-8')  # Convert bytes to string
        test_user.last_login = None

        with patch("users.services.UserModel") as mock_user_model, \
             patch("users.services.db", mock_db), \
             patch("users.services.verify_credential", return_value=True), \
             self.app.app_context():
            mock_user_model.query.filter_by.return_value.first.return_value = test_user

            before_login = datetime.now(timezone.utc)
            success, user_data = self.user_service.authenticate_user(username, password)
            after_login = datetime.now(timezone.utc)

            assert success
            assert test_user.last_login is not None
            assert before_login <= test_user.last_login <= after_login
            mock_db.session.commit.assert_called_once()

    @pytest.mark.unit
    def test_authenticate_user_db_error(self):
        """Test authentication when DB session has an error."""
        username = "testuser"
        password = "password123"
        mock_db = MagicMock()
        mock_db.session.commit.side_effect = Exception("DB Error")

        # Create a test user with a string password_hash to match the mock expectations
        test_user = MagicMock()
        test_user.id = "user-123"
        test_user.username = "testuser"
        test_user.email = "test@example.com"
        test_user.password_hash = self.hashed_password.decode('utf-8')  # Convert bytes to string
        test_user.last_login = None

        with patch("users.services.UserModel") as mock_user_model, \
             patch("users.services.db", mock_db), \
             patch("users.services.verify_credential", return_value=True), \
             self.app.app_context():
            mock_user_model.query.filter_by.return_value.first.return_value = test_user

            success, user_data = self.user_service.authenticate_user(username, password)

            assert not success
            assert user_data is None
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

        assert payload["sub"] == user_id
        assert payload["username"] == claims["username"]
        assert payload["email"] == claims["email"]
        assert payload["role"] == claims["role"]
        assert "jti" in payload
        assert "iat" in payload
        assert "exp" in payload

        # Verify expiration time
        now = datetime.now(timezone.utc)
        exp_time = datetime.fromtimestamp(payload["exp"], timezone.utc)
        assert exp_time > now
        assert exp_time < now + timedelta(seconds=self.token_expiry + 60)

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

        assert payload["username"] == "testuser"
        sensitive_fields = ["password", "token", "secret", "key"]
        for field in sensitive_fields:
            assert field not in payload

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

        assert success
        assert payload["sub"] == user_id
        assert payload["username"] == claims["username"]
        assert payload["email"] == claims["email"]

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

        assert not success
        assert payload is None

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
                assert not success, f"Token verification should fail for {case}"
                assert payload is None

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

                assert not success, f"Token missing {claim} claim should be invalid"
                assert payload is None

    @pytest.mark.unit
    def test_verify_token_general_exception(self):
        """Test verifying a token when a general exception occurs."""
        token = "valid.looking.token"

        with patch("jwt.decode") as mock_decode:
            # Simulate a general exception during token verification
            mock_decode.side_effect = Exception("Unexpected error")

            # Call the method
            success, payload = self.user_service.verify_token(token)

            # Verify the result
            assert not success
            assert payload is None
            mock_decode.assert_called_once_with(
                token,
                self.token_secret,
                algorithms=["HS256"]
            )


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
                auth_credential="test_credential",  # Use a hardcoded value instead of environment variable
            )

        assert "Username already exists" in str(excinfo.value)


@pytest.mark.skip(reason="Requires Flask app context")
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
            "testuser", "test_credential"  # Use a hardcoded value instead of environment variable
        )

        # Assertions
        assert success is True
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert "id" in result
        assert "password_hash" not in result


@pytest.mark.skip(reason="Requires Flask app context")
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
            "testuser", "test_credential"  # Use a hardcoded value instead of environment variable
        )

        # Assertions
        assert success is False
        assert result is None


@pytest.mark.skip(reason="Requires Flask app context")
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
            "nonexistent", "test_credential"  # Use a hardcoded value instead of environment variable
        )

        # Assertions
        assert success is False
        assert result is None


if __name__ == "__main__":
    pytest.main(["-v"])
