"""Comprehensive test module for common_utils.secrets.rotation."""

import datetime
import json
import os
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest

from common_utils.exceptions import InvalidRotationIntervalError
from common_utils.secrets.rotation import SecretRotation
from common_utils.secrets.secrets_manager import SecretsBackend

# Define constants for testing
DEFAULT_ROTATION_FILE = "secret_rotation.json"
MIN_ROTATION_INTERVAL = 1  # Minimum rotation interval in days
MAX_ROTATION_INTERVAL = 365  # Maximum rotation interval in days


class TestSecretRotationComprehensive:
    """Comprehensive test suite for SecretRotation class."""

    def setup_method(self):
        """Set up test environment."""
        # Create a temporary file for rotation data
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()

        # Create a SecretRotation instance with the temporary file
        self.rotation = SecretRotation(rotation_file=self.temp_file.name)

    def teardown_method(self):
        """Clean up test environment."""
        # Delete the temporary file
        os.unlink(self.temp_file.name)

    def test_init_default(self):
        """Test initialization with default parameters."""
        rotation = SecretRotation()
        assert rotation.rotation_file == DEFAULT_ROTATION_FILE
        assert rotation.secrets_backend == SecretsBackend.ENV
        assert rotation.rotation_data == {}

    def test_init_with_custom_file(self):
        """Test initialization with a custom rotation file."""
        rotation = SecretRotation(rotation_file=self.temp_file.name)
        assert rotation.rotation_file == self.temp_file.name
        assert rotation.secrets_backend == SecretsBackend.ENV
        assert rotation.rotation_data == {}

    def test_init_with_custom_backend(self):
        """Test initialization with a custom secrets backend."""
        rotation = SecretRotation(
            rotation_file=self.temp_file.name,
            secrets_backend=SecretsBackend.FILE
        )
        assert rotation.rotation_file == self.temp_file.name
        assert rotation.secrets_backend == SecretsBackend.FILE
        assert rotation.rotation_data == {}

    def test_init_with_existing_file(self):
        """Test initialization with an existing rotation file."""
        # Create rotation data
        rotation_data = {
            "API_KEY": {
                "last_rotated": "2023-01-01T00:00:00+00:00",
                "interval_days": 30,
                "generator_func": None
            }
        }

        # Write rotation data to the file
        with open(self.temp_file.name, "w") as f:
            json.dump(rotation_data, f)

        # Create a SecretRotation instance with the file
        rotation = SecretRotation(rotation_file=self.temp_file.name)

        # Verify the rotation data was loaded
        assert rotation.rotation_data == rotation_data

    def test_init_with_invalid_file(self):
        """Test initialization with an invalid rotation file."""
        # Write invalid JSON to the file
        with open(self.temp_file.name, "w") as f:
            f.write("invalid json")

        # Create a SecretRotation instance with the file
        rotation = SecretRotation(rotation_file=self.temp_file.name)

        # Verify the rotation data is empty
        assert rotation.rotation_data == {}

    def test_save_rotation_data(self):
        """Test _save_rotation_data method."""
        # Set rotation data
        self.rotation.rotation_data = {
            "API_KEY": {
                "last_rotated": "2023-01-01T00:00:00+00:00",
                "interval_days": 30,
                "generator_func": None
            }
        }

        # Save the rotation data
        self.rotation._save_rotation_data()

        # Verify the file was written
        with open(self.temp_file.name) as f:
            saved_data = json.load(f)

        assert saved_data == self.rotation.rotation_data

    def test_schedule_rotation_valid(self):
        """Test schedule_rotation with valid parameters."""
        # Schedule a rotation
        self.rotation.schedule_rotation("API_KEY", 30)

        # Verify the rotation was scheduled
        assert "API_KEY" in self.rotation.rotation_data
        assert self.rotation.rotation_data["API_KEY"]["interval_days"] == 30
        assert self.rotation.rotation_data["API_KEY"]["generator_func"] is None

        # Verify the last_rotated timestamp is in ISO format
        last_rotated = self.rotation.rotation_data["API_KEY"]["last_rotated"]
        try:
            datetime.datetime.fromisoformat(last_rotated)
        except ValueError:
            pytest.fail(f"Invalid ISO format for last_rotated: {last_rotated}")

    def test_schedule_rotation_with_generator(self):
        """Test schedule_rotation with a generator function."""
        # Schedule a rotation with a generator function
        self.rotation.schedule_rotation("API_KEY", 30, generator_func="generate_api_key")

        # Verify the rotation was scheduled
        assert "API_KEY" in self.rotation.rotation_data
        assert self.rotation.rotation_data["API_KEY"]["interval_days"] == 30
        assert self.rotation.rotation_data["API_KEY"]["generator_func"] == "generate_api_key"

    def test_schedule_rotation_invalid_interval_too_small(self):
        """Test schedule_rotation with an interval that is too small."""
        # Try to schedule a rotation with an interval that is too small
        with pytest.raises(InvalidRotationIntervalError):
            self.rotation.schedule_rotation("API_KEY", MIN_ROTATION_INTERVAL - 1)

    def test_schedule_rotation_invalid_interval_too_large(self):
        """Test schedule_rotation with an interval that is too large."""
        # Try to schedule a rotation with an interval that is too large
        with pytest.raises(InvalidRotationIntervalError):
            self.rotation.schedule_rotation("API_KEY", MAX_ROTATION_INTERVAL + 1)

    def test_get_secrets_due_for_rotation_none_due(self):
        """Test get_secrets_due_for_rotation when no secrets are due."""
        # Schedule a rotation for the future
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        future = now + datetime.timedelta(days=30)

        self.rotation.rotation_data = {
            "API_KEY": {
                "last_rotated": future.isoformat(),
                "interval_days": 30,
                "generator_func": None
            }
        }

        # Get secrets due for rotation
        due_secrets = self.rotation.get_secrets_due_for_rotation()

        # Verify no secrets are due
        assert due_secrets == []

    def test_get_secrets_due_for_rotation_one_due(self):
        """Test get_secrets_due_for_rotation when one secret is due."""
        # Schedule a rotation for the past
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        past = now - datetime.timedelta(days=31)

        self.rotation.rotation_data = {
            "API_KEY": {
                "last_rotated": past.isoformat(),
                "interval_days": 30,
                "generator_func": None
            }
        }

        # Get secrets due for rotation
        due_secrets = self.rotation.get_secrets_due_for_rotation()

        # Verify one secret is due
        assert due_secrets == ["API_KEY"]

    def test_get_secrets_due_for_rotation_multiple_due(self):
        """Test get_secrets_due_for_rotation when multiple secrets are due."""
        # Schedule rotations for the past
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        past1 = now - datetime.timedelta(days=31)
        past2 = now - datetime.timedelta(days=61)

        self.rotation.rotation_data = {
            "API_KEY": {
                "last_rotated": past1.isoformat(),
                "interval_days": 30,
                "generator_func": None
            },
            "DB_PASSWORD": {
                "last_rotated": past2.isoformat(),
                "interval_days": 60,
                "generator_func": None
            }
        }

        # Get secrets due for rotation
        due_secrets = self.rotation.get_secrets_due_for_rotation()

        # Verify both secrets are due
        assert set(due_secrets) == {"API_KEY", "DB_PASSWORD"}

    @patch("common_utils.secrets.rotation.get_secret")
    @patch("common_utils.secrets.rotation.set_secret")
    def test_rotate_secret_success(self, mock_set_secret, mock_get_secret):
        """Test rotate_secret with a successful rotation."""
        # Set up mocks
        mock_get_secret.return_value = "old_value"
        mock_set_secret.return_value = True

        # Schedule a rotation
        self.rotation.schedule_rotation("API_KEY", 30)

        # Rotate the secret
        result = self.rotation.rotate_secret("API_KEY")

        # Verify the rotation was successful
        assert result is True
        mock_get_secret.assert_called_once_with("API_KEY", self.rotation.secrets_backend)
        mock_set_secret.assert_called_once()

        # Verify the last_rotated timestamp was updated
        assert "last_rotated" in self.rotation.rotation_data["API_KEY"]
        last_rotated = self.rotation.rotation_data["API_KEY"]["last_rotated"]
        try:
            datetime.datetime.fromisoformat(last_rotated)
        except ValueError:
            pytest.fail(f"Invalid ISO format for last_rotated: {last_rotated}")

    @patch("common_utils.secrets.rotation.get_secret")
    def test_rotate_secret_not_scheduled(self, mock_get_secret):
        """Test rotate_secret with a secret that is not scheduled for rotation."""
        # Rotate a secret that is not scheduled
        result = self.rotation.rotate_secret("API_KEY")

        # Verify the rotation failed
        assert result is False
        mock_get_secret.assert_not_called()

    @patch("common_utils.secrets.rotation.get_secret")
    def test_rotate_secret_not_found(self, mock_get_secret):
        """Test rotate_secret with a secret that does not exist."""
        # Set up mock
        mock_get_secret.return_value = None

        # Schedule a rotation
        self.rotation.schedule_rotation("API_KEY", 30)

        # Rotate the secret
        result = self.rotation.rotate_secret("API_KEY")

        # Verify the rotation failed
        assert result is False
        mock_get_secret.assert_called_once_with("API_KEY", self.rotation.secrets_backend)

    @patch("common_utils.secrets.rotation.get_secret")
    @patch("common_utils.secrets.rotation.set_secret")
    def test_rotate_secret_set_failed(self, mock_set_secret, mock_get_secret):
        """Test rotate_secret when setting the new value fails."""
        # Set up mocks
        mock_get_secret.return_value = "old_value"
        mock_set_secret.return_value = False

        # Schedule a rotation
        self.rotation.schedule_rotation("API_KEY", 30)

        # Rotate the secret
        result = self.rotation.rotate_secret("API_KEY")

        # Verify the rotation failed
        assert result is False
        mock_get_secret.assert_called_once_with("API_KEY", self.rotation.secrets_backend)
        mock_set_secret.assert_called_once()

    @patch("common_utils.secrets.rotation.get_secret")
    @patch("common_utils.secrets.rotation.set_secret")
    def test_rotate_secret_with_custom_value(self, mock_set_secret, mock_get_secret):
        """Test rotate_secret with a custom new value."""
        # Set up mocks
        mock_get_secret.return_value = "old_value"
        mock_set_secret.return_value = True

        # Schedule a rotation
        self.rotation.schedule_rotation("API_KEY", 30)

        # Rotate the secret with a custom value
        result = self.rotation.rotate_secret("API_KEY", new_value="custom_value")

        # Verify the rotation was successful
        assert result is True
        mock_get_secret.assert_called_once_with("API_KEY", self.rotation.secrets_backend)
        mock_set_secret.assert_called_once_with("API_KEY", "custom_value", self.rotation.secrets_backend)

    @patch("common_utils.secrets.rotation.SecretRotation.rotate_secret")
    def test_rotate_all_due_none_due(self, mock_rotate_secret):
        """Test rotate_all_due when no secrets are due."""
        # Mock get_secrets_due_for_rotation to return an empty list
        with patch.object(self.rotation, "get_secrets_due_for_rotation", return_value=[]):
            # Rotate all due secrets
            count, rotated = self.rotation.rotate_all_due()

            # Verify no secrets were rotated
            assert count == 0
            assert rotated == []
            mock_rotate_secret.assert_not_called()

    @patch("common_utils.secrets.rotation.SecretRotation.rotate_secret")
    def test_rotate_all_due_all_success(self, mock_rotate_secret):
        """Test rotate_all_due when all rotations succeed."""
        # Mock get_secrets_due_for_rotation to return a list of secrets
        with patch.object(self.rotation, "get_secrets_due_for_rotation", return_value=["API_KEY", "DB_PASSWORD"]):
            # Mock rotate_secret to return True
            mock_rotate_secret.return_value = True

            # Rotate all due secrets
            count, rotated = self.rotation.rotate_all_due()

            # Verify all secrets were rotated
            assert count == 2
            assert set(rotated) == {"API_KEY", "DB_PASSWORD"}
            assert mock_rotate_secret.call_count == 2

    @patch("common_utils.secrets.rotation.SecretRotation.rotate_secret")
    def test_rotate_all_due_some_fail(self, mock_rotate_secret):
        """Test rotate_all_due when some rotations fail."""
        # Mock get_secrets_due_for_rotation to return a list of secrets
        with patch.object(self.rotation, "get_secrets_due_for_rotation", return_value=["API_KEY", "DB_PASSWORD"]):
            # Mock rotate_secret to return True for API_KEY and False for DB_PASSWORD
            mock_rotate_secret.side_effect = [True, False]

            # Rotate all due secrets
            count, rotated = self.rotation.rotate_all_due()

            # Verify only one secret was rotated
            assert count == 1
            assert rotated == ["API_KEY"]
            assert mock_rotate_secret.call_count == 2
