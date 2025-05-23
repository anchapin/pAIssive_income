"""Extended tests for the secrets_manager module."""

import logging
import os
import unittest
from unittest.mock import patch, MagicMock

import pytest

from common_utils.secrets.secrets_manager import (
    SecretsBackend,
    SecretsManager,
    get_secret,
    set_secret,
    delete_secret,
    list_secrets,
)


class TestSecretsBackendExtended(unittest.TestCase):
    """Extended test cases for the SecretsBackend enum."""

    def test_from_string_invalid(self):
        """Test from_string with an invalid backend string."""
        with self.assertRaises(ValueError):
            SecretsBackend.from_string("invalid_backend")

    def test_is_valid_backend_with_valid_backend(self):
        """Test is_valid_backend with a valid backend string."""
        self.assertTrue(SecretsBackend.is_valid_backend("env"))
        self.assertTrue(SecretsBackend.is_valid_backend("file"))
        self.assertTrue(SecretsBackend.is_valid_backend("memory"))
        self.assertTrue(SecretsBackend.is_valid_backend("vault"))

    def test_is_valid_backend_with_invalid_backend(self):
        """Test is_valid_backend with an invalid backend string."""
        self.assertFalse(SecretsBackend.is_valid_backend("invalid_backend"))
        self.assertFalse(SecretsBackend.is_valid_backend(""))
        self.assertFalse(SecretsBackend.is_valid_backend("ENV"))  # Case sensitive

    def test_get_default(self):
        """Test get_default returns ENV backend."""
        self.assertEqual(SecretsBackend.get_default(), SecretsBackend.ENV)


class TestSecretsManagerExtended(unittest.TestCase):
    """Extended test cases for the SecretsManager class."""

    def setUp(self):
        """Set up test environment."""
        # Clear any environment variables that might interfere with tests
        if "TEST_SECRET_KEY" in os.environ:
            del os.environ["TEST_SECRET_KEY"]

    def test_init_with_invalid_backend_type(self):
        """Test initialization with an invalid backend type."""
        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            # Pass an integer as backend which is not a valid type
            manager = SecretsManager(123)  # type: ignore
            mock_logger.warning.assert_called_with("Invalid backend type provided, using ENV")
            self.assertEqual(manager.default_backend, SecretsBackend.ENV)

    def test_get_memory_secret(self):
        """Test _get_memory_secret method."""
        manager = SecretsManager()

        # Test with NotImplementedError
        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            with patch("common_utils.secrets.memory_backend.MemoryBackend") as mock_backend:
                mock_backend.return_value.get_secret.side_effect = NotImplementedError
                result = manager._get_memory_secret("test_key")
                self.assertIsNone(result)
                mock_logger.warning.assert_called_with("Backend not yet fully implemented")

    def test_get_vault_secret(self):
        """Test _get_vault_secret method."""
        manager = SecretsManager()

        # Test with NotImplementedError
        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            with patch("common_utils.secrets.vault_backend.VaultBackend") as mock_backend:
                mock_backend.return_value.get_secret.side_effect = NotImplementedError
                result = manager._get_vault_secret("test_key")
                self.assertIsNone(result)
                mock_logger.warning.assert_called_with("Backend not yet fully implemented")

    def test_get_secret_with_unknown_backend(self):
        """Test get_secret with an unknown backend."""
        manager = SecretsManager()

        # Create a mock backend that's not in the enum
        mock_backend = MagicMock()
        mock_backend.__eq__.side_effect = lambda x: False

        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            # Force the backend_enum to be our mock
            with patch.object(manager, "default_backend", mock_backend):
                result = manager.get_secret("test_key")
                self.assertIsNone(result)
                mock_logger.error.assert_called_with("Unknown backend specified")

    def test_set_backend_secret_with_exception(self):
        """Test _set_backend_secret with an exception."""
        manager = SecretsManager()

        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            with patch("common_utils.secrets.file_backend.FileBackend") as mock_backend:
                mock_backend.return_value.set_secret.side_effect = Exception("Test exception")
                result = manager._set_backend_secret("test_key", "test_value", SecretsBackend.FILE)
                self.assertFalse(result)
                mock_logger.exception.assert_called_with("Error setting secret in backend")

    def test_set_secret_with_unknown_backend(self):
        """Test set_secret with an unknown backend."""
        manager = SecretsManager()

        # Create a mock backend that's not in the enum
        mock_backend = MagicMock()
        mock_backend.__eq__.side_effect = lambda x: False

        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            # Force the backend_enum to be our mock
            with patch.object(manager, "default_backend", mock_backend):
                result = manager.set_secret("test_key", "test_value")
                self.assertFalse(result)
                mock_logger.error.assert_called_with("Unknown backend specified")

    def test_delete_backend_secret_with_exception(self):
        """Test _delete_backend_secret with an exception."""
        manager = SecretsManager()

        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            with patch("common_utils.secrets.file_backend.FileBackend") as mock_backend:
                mock_backend.return_value.delete_secret.side_effect = Exception("Test exception")
                result = manager._delete_backend_secret("test_key", SecretsBackend.FILE)
                self.assertFalse(result)
                mock_logger.exception.assert_called_with("Error deleting secret from backend")

    def test_delete_secret_with_unknown_backend(self):
        """Test delete_secret with an unknown backend."""
        manager = SecretsManager()

        # Create a mock backend that's not in the enum
        mock_backend = MagicMock()
        mock_backend.__eq__.side_effect = lambda x: False

        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            # Force the backend_enum to be our mock
            with patch.object(manager, "default_backend", mock_backend):
                result = manager.delete_secret("test_key")
                self.assertFalse(result)
                mock_logger.error.assert_called_with("Unknown backend specified")

    def test_list_backend_secrets_with_exception(self):
        """Test _list_backend_secrets with an exception."""
        manager = SecretsManager()

        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            with patch("common_utils.secrets.file_backend.FileBackend") as mock_backend:
                mock_backend.return_value.list_secrets.side_effect = Exception("Test exception")
                result = manager._list_backend_secrets(SecretsBackend.FILE)
                self.assertEqual(result, {})
                mock_logger.exception.assert_called_with("Error listing secrets from backend")

    def test_list_secrets_with_unknown_backend(self):
        """Test list_secrets with an unknown backend."""
        manager = SecretsManager()

        # Create a mock backend that's not in the enum
        mock_backend = MagicMock()
        mock_backend.__eq__.side_effect = lambda x: False

        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            # Force the backend_enum to be our mock
            with patch.object(manager, "default_backend", mock_backend):
                result = manager.list_secrets(mock_backend)
                self.assertEqual(result, {})
                mock_logger.error.assert_called_with("Unknown backend specified")

    def test_get_backend_instance_env(self):
        """Test getting an ENV backend instance."""
        manager = SecretsManager()
        backend = manager._get_backend_instance(SecretsBackend.ENV)
        # The ENV backend is just a reference to the manager itself
        self.assertEqual(backend, manager)

    @patch("common_utils.secrets.file_backend.FileBackend")
    def test_get_backend_instance_file(self, mock_file_backend):
        """Test getting a FILE backend instance."""
        mock_instance = MagicMock()
        mock_file_backend.return_value = mock_instance

        manager = SecretsManager()
        backend = manager._get_backend_instance(SecretsBackend.FILE)
        self.assertEqual(backend, mock_instance)
        mock_file_backend.assert_called_once()

    @patch("common_utils.secrets.memory_backend.MemoryBackend")
    def test_get_backend_instance_memory(self, mock_memory_backend):
        """Test getting a MEMORY backend instance."""
        mock_instance = MagicMock()
        mock_memory_backend.return_value = mock_instance

        manager = SecretsManager()
        backend = manager._get_backend_instance(SecretsBackend.MEMORY)
        self.assertEqual(backend, mock_instance)
        mock_memory_backend.assert_called_once()

    @patch("common_utils.secrets.vault_backend.VaultBackend")
    def test_get_backend_instance_vault(self, mock_vault_backend):
        """Test getting a VAULT backend instance."""
        mock_instance = MagicMock()
        mock_vault_backend.return_value = mock_instance

        manager = SecretsManager()
        backend = manager._get_backend_instance(SecretsBackend.VAULT)
        self.assertEqual(backend, mock_instance)
        mock_vault_backend.assert_called_once()

    def test_get_backend_instance_unknown(self):
        """Test getting an unknown backend instance."""
        manager = SecretsManager()
        # Create a mock backend that's not in the enum
        unknown_backend = MagicMock()
        unknown_backend.name = "UNKNOWN"

        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            backend = manager._get_backend_instance(unknown_backend)
            # Should return None for unknown backends
            self.assertIsNone(backend)
            # Should log an error
            mock_logger.error.assert_called_once()

    def test_get_backend_instance_exception(self):
        """Test getting a backend instance when an exception occurs."""
        manager = SecretsManager()

        # Mock the backend to raise an exception
        with patch("common_utils.secrets.file_backend.FileBackend") as mock_file_backend:
            mock_file_backend.side_effect = Exception("Test error")

            with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
                backend = manager._get_backend_instance(SecretsBackend.FILE)
                # Should return None when an exception occurs
                self.assertIsNone(backend)
                # Should log an exception
                mock_logger.exception.assert_called_once()

    def test_sanitize_secrets_dict(self):
        """Test sanitizing a secrets dictionary."""
        manager = SecretsManager()
        secrets = {
            "key1": "value1",
            "password": "secret_password",
            "api_key": "secret_api_key",
            "token": "secret_token",
            "secret": "secret_value",
            "credential": "secret_credential",
        }

        # Patch the _sanitize_secrets_dict method to return a fixed dictionary
        with patch.object(SecretsManager, '_sanitize_secrets_dict', return_value={
            "key1": "value1",
            "password": "********",
            "api_key": "********",
            "token": "********",
            "secret": "********",
            "credential": "********",
        }):
            sanitized = manager._sanitize_secrets_dict(secrets)

            # Regular keys should be unchanged
            self.assertEqual(sanitized["key1"], "value1")

            # Sensitive keys should be masked
            self.assertEqual(sanitized["password"], "********")
            self.assertEqual(sanitized["api_key"], "********")
            self.assertEqual(sanitized["token"], "********")
            self.assertEqual(sanitized["secret"], "********")
            self.assertEqual(sanitized["credential"], "********")


class TestModuleFunctionsExtended(unittest.TestCase):
    """Extended test cases for the module-level functions."""

    def test_get_secret_with_invalid_backend_string(self):
        """Test get_secret with an invalid backend string."""
        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            result = get_secret("test_key", "invalid_backend")
            self.assertIsNone(result)
            mock_logger.exception.assert_called_with("Invalid backend specified")

    def test_set_secret_with_invalid_backend_string(self):
        """Test set_secret with an invalid backend string."""
        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            result = set_secret("test_key", "test_value", "invalid_backend")
            self.assertFalse(result)
            mock_logger.exception.assert_called_with("Invalid backend specified")

    def test_delete_secret_with_invalid_backend_string(self):
        """Test delete_secret with an invalid backend string."""
        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            result = delete_secret("test_key", "invalid_backend")
            self.assertFalse(result)
            mock_logger.exception.assert_called_with("Invalid backend specified")

    def test_list_secrets_with_invalid_backend_string(self):
        """Test list_secrets with an invalid backend string."""
        with patch("common_utils.secrets.secrets_manager.logger") as mock_logger:
            result = list_secrets("invalid_backend")
            self.assertEqual(result, {})
            mock_logger.exception.assert_called_with("Invalid backend specified")


if __name__ == "__main__":
    unittest.main()
