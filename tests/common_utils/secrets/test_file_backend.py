"""Tests for the file backend module."""

import logging
import os
from unittest.mock import patch

import pytest

from common_utils.secrets.file_backend import FileBackend


class TestFileBackend:
    """Tests for the FileBackend class."""

    def setup_method(self):
        """Set up test environment."""
        # Clear any environment variables that might interfere with tests
        if "PAISSIVE_SECRETS_DIR" in os.environ:
            del os.environ["PAISSIVE_SECRETS_DIR"]
        if "PAISSIVE_AUTH_KEY" in os.environ:
            del os.environ["PAISSIVE_AUTH_KEY"]

    def teardown_method(self):
        """Clean up after tests."""
        # Clean up any environment variables set during tests
        if "PAISSIVE_SECRETS_DIR" in os.environ:
            del os.environ["PAISSIVE_SECRETS_DIR"]
        if "PAISSIVE_AUTH_KEY" in os.environ:
            del os.environ["PAISSIVE_AUTH_KEY"]

    def test_init_default(self):
        """Test initializing with default values."""
        backend = FileBackend()
        assert backend.secrets_dir == ".paissive/secrets"
        assert backend._has_auth is False

    def test_init_custom_dir(self):
        """Test initializing with custom directory."""
        backend = FileBackend(secrets_dir="custom/dir")
        assert backend.secrets_dir == "custom/dir"

    def test_init_env_dir(self):
        """Test initializing with directory from environment variable."""
        os.environ["PAISSIVE_SECRETS_DIR"] = "env/dir"
        backend = FileBackend()
        assert backend.secrets_dir == "env/dir"

    def test_init_with_auth_material(self):
        """Test initializing with authentication material."""
        backend = FileBackend(auth_material="test_auth")
        assert backend._has_auth is True

    def test_init_with_env_auth(self):
        """Test initializing with authentication material from environment variable."""
        os.environ["PAISSIVE_AUTH_KEY"] = "env_auth"
        backend = FileBackend()
        assert backend._has_auth is True

    def test_has_auth(self):
        """Test the _has_auth property."""
        backend = FileBackend()
        assert backend._has_auth is False

        backend = FileBackend(auth_material="test_auth")
        assert backend._has_auth is True

    def test_get_secret_not_implemented(self):
        """Test that get_secret raises NotImplementedError."""
        backend = FileBackend()
        with pytest.raises(NotImplementedError):
            backend.get_secret("test_key")

    def test_set_secret_not_implemented(self):
        """Test that set_secret raises NotImplementedError."""
        backend = FileBackend()
        with pytest.raises(NotImplementedError):
            backend.set_secret("test_key", "test_value")

    def test_delete_secret_not_implemented(self):
        """Test that delete_secret raises NotImplementedError."""
        backend = FileBackend()
        with pytest.raises(NotImplementedError):
            backend.delete_secret("test_key")

    def test_list_secrets_not_implemented(self):
        """Test that list_secrets raises NotImplementedError."""
        backend = FileBackend()
        with pytest.raises(NotImplementedError):
            backend.list_secrets()
