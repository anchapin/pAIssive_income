"""Tests for the rotation module."""

import logging
import datetime
import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock, mock_open

import pytest

from common_utils.secrets.rotation import SecretRotation
from common_utils.secrets.secrets_manager import SecretsBackend


class TestSecretRotation(unittest.TestCase):
    """Test cases for the SecretRotation class."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary file for rotation data
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()

        # Initialize rotation data
        self.rotation_data = {
            "test_secret": {
                "last_rotated": datetime.datetime.now().isoformat(),
                "interval_days": 30,
                "generator_func": None,
            },
            "due_secret": {
                "last_rotated": (datetime.datetime.now() - datetime.timedelta(days=60)).isoformat(),
                "interval_days": 30,
                "generator_func": None,
            }
        }

        # Write rotation data to the file
        with open(self.temp_file.name, "w", encoding="utf-8") as f:
            json.dump(self.rotation_data, f)

    def tearDown(self):
        """Clean up test environment."""
        os.unlink(self.temp_file.name)

    def test_init_with_file(self):
        """Test initialization with a rotation file."""
        rotation = SecretRotation(rotation_file=self.temp_file.name)
        self.assertEqual(rotation.rotation_file, self.temp_file.name)
        self.assertEqual(rotation.secrets_backend, SecretsBackend.ENV)
        self.assertEqual(rotation.rotation_data, self.rotation_data)

    def test_init_without_file(self):
        """Test initialization without a rotation file."""
        with patch("os.environ.get", return_value="default_file.json"):
            rotation = SecretRotation()
            self.assertEqual(rotation.rotation_file, "default_file.json")

    def test_init_with_nonexistent_file(self):
        """Test initialization with a nonexistent file."""
        rotation = SecretRotation(rotation_file="nonexistent_file.json")
        self.assertEqual(rotation.rotation_data, {})

    def test_init_with_invalid_file(self):
        """Test initialization with an invalid file."""
        with open(self.temp_file.name, "w", encoding="utf-8") as f:
            f.write("invalid json")

        with patch("common_utils.secrets.rotation.logger") as mock_logger:
            rotation = SecretRotation(rotation_file=self.temp_file.name)
            self.assertEqual(rotation.rotation_data, {})
            mock_logger.exception.assert_called_once()

    def test_schedule_rotation(self):
        """Test schedule_rotation method."""
        rotation = SecretRotation(rotation_file=self.temp_file.name)

        # Schedule a new rotation
        with patch("datetime.datetime") as mock_datetime:
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T00:00:00"
            mock_datetime.now.return_value = mock_now

            rotation.schedule_rotation("new_secret", 15, "generate_func")

            # Check that the rotation data was updated
            self.assertIn("new_secret", rotation.rotation_data)
            self.assertEqual(rotation.rotation_data["new_secret"]["last_rotated"], "2023-01-01T00:00:00")
            self.assertEqual(rotation.rotation_data["new_secret"]["interval_days"], 15)
            self.assertEqual(rotation.rotation_data["new_secret"]["generator_func"], "generate_func")

            # Check that the rotation data was saved
            with open(self.temp_file.name, encoding="utf-8") as f:
                saved_data = json.load(f)
                self.assertIn("new_secret", saved_data)

    def test_get_secrets_due_for_rotation(self):
        """Test get_secrets_due_for_rotation method."""
        rotation = SecretRotation(rotation_file=self.temp_file.name)

        # Get secrets due for rotation
        due_secrets = rotation.get_secrets_due_for_rotation()

        # Check that only the due secret is returned
        self.assertEqual(len(due_secrets), 1)
        self.assertIn("due_secret", due_secrets)
        self.assertNotIn("test_secret", due_secrets)

    def test_rotate_secret_with_new_value(self):
        """Test rotate_secret method with a new value."""
        rotation = SecretRotation(rotation_file=self.temp_file.name)

        # Mock get_secret and set_secret
        with patch("common_utils.secrets.rotation.get_secret", return_value="old_value"), \
             patch("common_utils.secrets.rotation.set_secret", return_value=True), \
             patch("datetime.datetime") as mock_datetime:

            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T00:00:00"
            mock_datetime.now.return_value = mock_now

            # Rotate the secret
            result = rotation.rotate_secret("test_secret", "new_value")

            # Check the result
            self.assertTrue(result)

            # Check that the rotation data was updated
            self.assertEqual(rotation.rotation_data["test_secret"]["last_rotated"], "2023-01-01T00:00:00")

    def test_rotate_secret_without_new_value(self):
        """Test rotate_secret method without a new value."""
        rotation = SecretRotation(rotation_file=self.temp_file.name)

        # Mock get_secret and set_secret
        with patch("common_utils.secrets.rotation.get_secret", return_value="old_value"), \
             patch("common_utils.secrets.rotation.set_secret", return_value=True), \
             patch("datetime.datetime") as mock_datetime:

            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T00:00:00"
            mock_datetime.now.return_value = mock_now

            # Rotate the secret
            result = rotation.rotate_secret("test_secret")

            # Check the result
            self.assertTrue(result)

            # Check that the rotation data was updated
            self.assertEqual(rotation.rotation_data["test_secret"]["last_rotated"], "2023-01-01T00:00:00")

    def test_rotate_secret_not_scheduled(self):
        """Test rotate_secret method with a secret not scheduled for rotation."""
        rotation = SecretRotation(rotation_file=self.temp_file.name)

        # Rotate a secret that is not scheduled
        result = rotation.rotate_secret("not_scheduled")

        # Check the result
        self.assertFalse(result)

    def test_rotate_secret_not_found(self):
        """Test rotate_secret method with a secret that is not found."""
        rotation = SecretRotation(rotation_file=self.temp_file.name)

        # Mock get_secret to return None
        with patch("common_utils.secrets.rotation.get_secret", return_value=None):
            # Rotate the secret
            result = rotation.rotate_secret("test_secret")

            # Check the result
            self.assertFalse(result)

    def test_rotate_secret_set_failed(self):
        """Test rotate_secret method when set_secret fails."""
        rotation = SecretRotation(rotation_file=self.temp_file.name)

        # Mock get_secret and set_secret
        with patch("common_utils.secrets.rotation.get_secret", return_value="old_value"), \
             patch("common_utils.secrets.rotation.set_secret", return_value=False):

            # Rotate the secret
            result = rotation.rotate_secret("test_secret", "new_value")

            # Check the result
            self.assertFalse(result)

    def test_rotate_all_due(self):
        """Test rotate_all_due method."""
        rotation = SecretRotation(rotation_file=self.temp_file.name)

        # Mock rotate_secret
        with patch.object(rotation, "rotate_secret", side_effect=[True, False]):
            # Rotate all due secrets
            count, rotated = rotation.rotate_all_due()

            # Check the result
            self.assertEqual(count, 1)
            self.assertEqual(rotated, ["due_secret"])


if __name__ == "__main__":
    unittest.main()
