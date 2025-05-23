"""
Test module for common_utils.secrets.memory_backend.

This module tests the MemoryBackend class for secure logging.
"""

import logging
from unittest.mock import patch

import pytest

from common_utils.secrets.memory_backend import MemoryBackend


class TestMemoryBackend:
    """Test cases for the MemoryBackend class."""

    @pytest.fixture
    def backend(self):
        """Create a MemoryBackend instance."""
        return MemoryBackend()

    @pytest.fixture
    def test_key(self):
        """Return a test secret key."""
        return "test_secret_key"

    @pytest.fixture
    def test_value(self):
        """Return a test secret value."""
        return "test_secret_value"

    @patch("common_utils.secrets.memory_backend.logger")
    def test_get_secret_secure_logging(self, mock_logger, backend, test_key):
        """Test that get_secret uses secure logging."""
        # This should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            backend.get_secret(test_key)

        # Verify that the logger was called with the correct parameters
        mock_logger.warning.assert_called_once()
        # Check that the key is not in the log message
        args, kwargs = mock_logger.warning.call_args
        assert args[0] == "Memory backend not yet implemented"
        assert "extra" in kwargs
        assert "operation" in kwargs["extra"]
        assert kwargs["extra"]["operation"] == "get_secret"
        # The actual key should not be in the log message at all
        assert test_key not in str(args)
        assert test_key not in str(kwargs)

    @patch("common_utils.secrets.memory_backend.logger")
    def test_set_secret_secure_logging(
        self, mock_logger, backend, test_key, test_value
    ):
        """Test that set_secret uses secure logging."""
        # This should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            backend.set_secret(test_key, test_value)

        # Verify that the logger was called with the correct parameters
        mock_logger.warning.assert_called_once()
        # Check that the key is not in the log message
        args, kwargs = mock_logger.warning.call_args
        assert args[0] == "Memory backend not yet implemented"
        assert "extra" in kwargs
        assert "operation" in kwargs["extra"]
        assert kwargs["extra"]["operation"] == "set_secret"
        # The actual key should not be in the log message at all
        assert test_key not in str(args)
        assert test_key not in str(kwargs)
        # The value should not be in the log message at all
        assert test_value not in str(args)
        assert test_value not in str(kwargs)

    @patch("common_utils.secrets.memory_backend.logger")
    def test_delete_secret_secure_logging(self, mock_logger, backend, test_key):
        """Test that delete_secret uses secure logging."""
        # This should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            backend.delete_secret(test_key)

        # Verify that the logger was called with the correct parameters
        mock_logger.warning.assert_called_once()
        # Check that the key is not in the log message
        args, kwargs = mock_logger.warning.call_args
        assert args[0] == "Memory backend not yet implemented"
        assert "extra" in kwargs
        assert "operation" in kwargs["extra"]
        assert kwargs["extra"]["operation"] == "delete_secret"
        # The actual key should not be in the log message at all
        assert test_key not in str(args)
        assert test_key not in str(kwargs)

    @patch("common_utils.secrets.memory_backend.logger")
    def test_list_secrets_secure_logging(self, mock_logger, backend):
        """Test that list_secrets uses secure logging."""
        # This should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            backend.list_secrets()

        # Verify that the logger was called with the correct parameters
        mock_logger.warning.assert_called_once()
        # Check that the log message is secure
        args, kwargs = mock_logger.warning.call_args
        assert args[0] == "Memory backend not yet implemented"
        assert "extra" in kwargs
        assert "operation" in kwargs["extra"]
        assert kwargs["extra"]["operation"] == "list_secrets"
