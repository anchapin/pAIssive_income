"""test_password_reset - Test module for users.password_reset."""

# Standard library imports
import logging
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

# Third-party imports
import pytest

# Local imports
from users.password_reset import (
    PasswordResetService,
    UserRepository,
    generate_reset_code,
)


class MockUserRepository(UserRepository):
    """Mock implementation of UserRepository for testing."""

    def __init__(self):
        """Initialize with empty user data."""
        self.users = {}
        self.updates = {}

    def find_by_email(self, email):
        """Find a user by email."""
        for _, user in self.users.items():
            if user.get("email") == email:
                return user
        return None

    def find_by_reset_token(self, token):
        """Find a user by reset token."""
        for _, user in self.users.items():
            if user.get("auth_reset_token") == token:
                return user
        return None

    def update(self, user_id, data):
        """Update a user."""
        if user_id not in self.users:
            return False

        # Store the update for verification
        if user_id not in self.updates:
            self.updates[user_id] = []
        self.updates[user_id].append(data)

        # Update the user data
        for key, value in data.items():
            self.users[user_id][key] = value

        return True

    def add_user(self, user_id, user_data):
        """Add a user for testing."""
        self.users[user_id] = user_data


class TestGenerateResetCode(unittest.TestCase):
    """Test suite for generate_reset_code function."""

    def test_generate_reset_code_default_length(self):
        """Test generating a reset code with default length."""
        # Act
        code = generate_reset_code()

        # Assert
        assert len(code) == 32
        assert all(c.isalnum() for c in code)

    def test_generate_reset_code_custom_length(self):
        """Test generating a reset code with custom length."""
        # Arrange
        length = 16

        # Act
        code = generate_reset_code(length)

        # Assert
        assert len(code) == length
        assert all(c.isalnum() for c in code)

    def test_generate_reset_code_uniqueness(self):
        """Test that generated reset codes are unique."""
        # Act
        code1 = generate_reset_code()
        code2 = generate_reset_code()

        # Assert
        assert code1 != code2


class TestPasswordResetService(unittest.TestCase):
    """Test suite for PasswordResetService."""

    def setUp(self):
        """Set up test fixtures."""
        self.user_repository = MockUserRepository()
        self.service = PasswordResetService(
            user_repository=self.user_repository,
            code_expiry=3600,  # 1 hour
        )

        # Add a test user
        self.test_user = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "auth_hash": "hashed_password",
            "auth_reset_token": None,
            "auth_reset_expires": None,
        }
        self.user_repository.add_user(1, self.test_user.copy())

    def test_init_with_defaults(self):
        """Test initializing with default values."""
        # Act
        service = PasswordResetService()

        # Assert
        assert service.user_repository is None
        assert service.code_expiry == 3600  # Default is 1 hour

    def test_init_with_custom_values(self):
        """Test initializing with custom values."""
        # Arrange
        repo = MockUserRepository()
        expiry = 7200  # 2 hours

        # Act
        service = PasswordResetService(user_repository=repo, code_expiry=expiry)

        # Assert
        assert service.user_repository == repo
        assert service.code_expiry == expiry

    @patch("users.password_reset.generate_reset_code")
    @patch("users.password_reset.datetime")
    def test_request_reset_success(self, mock_datetime, mock_generate_code):
        """Test requesting a reset successfully."""
        # Arrange
        email = "test@example.com"
        reset_code = "test_reset_code"
        mock_generate_code.return_value = reset_code

        # Mock datetime.now to return a fixed timezone-aware datetime
        fixed_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_now

        # Calculate expiry based on the fixed time
        expiry = fixed_now + timedelta(seconds=3600)

        # Act
        success, masked_code = self.service.request_reset(email)

        # Assert
        assert success
        # The actual masked code length depends on the reset_code length (48 chars in the implementation)
        # Just check that it starts with "te" and ends with "de" and has asterisks in between
        assert masked_code.startswith("te")
        assert masked_code.endswith("de")
        assert "*" in masked_code

        # Check that the user was updated correctly
        updates = self.user_repository.updates.get(1, [])
        assert len(updates) == 1

        # Check that the reset token was hashed
        import hashlib
        expected_hash = hashlib.sha256(reset_code.encode()).hexdigest()
        assert updates[0]["auth_reset_token"] == expected_hash
        assert updates[0]["auth_reset_expires"] == expiry.isoformat()

    def test_request_reset_no_repository(self):
        """Test requesting a reset with no repository."""
        # Arrange
        service = PasswordResetService(user_repository=None)

        # Act
        success, masked_code = service.request_reset("test@example.com")

        # Assert
        assert not success
        assert masked_code is None

    def test_request_reset_user_not_found(self):
        """Test requesting a reset for a non-existent user."""
        # Arrange
        email = "nonexistent@example.com"

        # Act
        with patch("time.sleep") as mock_sleep:  # Mock sleep to speed up test
            success, masked_code = self.service.request_reset(email)

        # Assert
        assert not success
        assert masked_code is None
        mock_sleep.assert_called_once_with(0.2)  # Check that sleep was called

    @patch("users.password_reset.hash_credential")
    def test_reset_auth_credential_success(self, mock_hash_credential):
        """Test resetting an authentication credential successfully."""
        # Arrange
        reset_code = "test_reset_code"
        new_credential = "new_password"
        hashed_credential = "hashed_new_password"
        mock_hash_credential.return_value = hashed_credential

        # Set up the user with a valid reset token
        import hashlib
        hashed_token = hashlib.sha256(reset_code.encode()).hexdigest()
        expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        self.user_repository.update(1, {
            "auth_reset_token": hashed_token,
            "auth_reset_expires": expiry.isoformat(),
        })

        # Act
        success = self.service.reset_auth_credential(reset_code, new_credential)

        # Assert
        assert success

        # Check that the user was updated correctly
        updates = self.user_repository.updates.get(1, [])
        assert len(updates) == 2  # First update for setup, second for reset

        # Check the second update (the actual reset)
        assert updates[1]["auth_hash"] == hashed_credential
        assert updates[1]["auth_reset_token"] is None
        assert updates[1]["auth_reset_expires"] is None
        assert updates[1]["updated_at"] is not None

    def test_reset_auth_credential_no_repository(self):
        """Test resetting a credential with no repository."""
        # Arrange
        service = PasswordResetService(user_repository=None)

        # Act
        success = service.reset_auth_credential("code", "new_password")

        # Assert
        assert not success

    def test_reset_auth_credential_invalid_code(self):
        """Test resetting a credential with an invalid code."""
        # Arrange
        reset_code = "invalid_code"
        new_credential = "new_password"

        # Act
        success = self.service.reset_auth_credential(reset_code, new_credential)

        # Assert
        assert not success

    def test_reset_auth_credential_expired_code(self):
        """Test resetting a credential with an expired code."""
        # Arrange
        reset_code = "test_reset_code"
        new_credential = "new_password"

        # Set up the user with an expired reset token
        import hashlib
        hashed_token = hashlib.sha256(reset_code.encode()).hexdigest()
        expiry = datetime.now(timezone.utc) - timedelta(hours=1)  # Expired 1 hour ago
        self.user_repository.update(1, {
            "auth_reset_token": hashed_token,
            "auth_reset_expires": expiry.isoformat(),
        })

        # Act
        success = self.service.reset_auth_credential(reset_code, new_credential)

        # Assert
        assert not success

    def test_reset_auth_credential_no_expiry(self):
        """Test resetting a credential with no expiry date."""
        # Arrange
        reset_code = "test_reset_code"
        new_credential = "new_password"

        # Set up the user with a reset token but no expiry
        import hashlib
        hashed_token = hashlib.sha256(reset_code.encode()).hexdigest()
        self.user_repository.update(1, {
            "auth_reset_token": hashed_token,
            "auth_reset_expires": None,
        })

        # Act
        success = self.service.reset_auth_credential(reset_code, new_credential)

        # Assert
        assert not success
