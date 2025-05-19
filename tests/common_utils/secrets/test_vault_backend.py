"""Tests for the vault backend module."""

import logging
import os
import pytest
from unittest.mock import patch

from common_utils.secrets.vault_backend import VaultBackend


class TestVaultBackend:
    """Tests for the VaultBackend class."""

    def setup_method(self):
        """Set up test environment."""
        pass

    def teardown_method(self):
        """Clean up after tests."""
        pass

    def test_init_default(self):
        """Test initializing with default values."""
        backend = VaultBackend()
        assert backend.vault_url is None
        assert backend._has_auth is False

    def test_init_custom_url_auth(self):
        """Test initializing with custom URL and auth material."""
        backend = VaultBackend(vault_url="http://localhost:8200", auth_material="test_auth")
        assert backend.vault_url == "http://localhost:8200"
        assert backend._has_auth is True

    def test_is_authenticated(self):
        """Test the is_authenticated property."""
        backend = VaultBackend()
        assert backend.is_authenticated is False

        backend = VaultBackend(vault_url="http://localhost:8200", auth_material="test_auth")
        assert backend.is_authenticated is True

    def test_get_secret_not_implemented(self):
        """Test that get_secret raises NotImplementedError."""
        backend = VaultBackend()
        with pytest.raises(NotImplementedError):
            backend.get_secret("test_key")

    def test_set_secret_not_implemented(self):
        """Test that set_secret raises NotImplementedError."""
        backend = VaultBackend()
        with pytest.raises(NotImplementedError):
            backend.set_secret("test_key", "test_value")

    def test_delete_secret_not_implemented(self):
        """Test that delete_secret raises NotImplementedError."""
        backend = VaultBackend()
        with pytest.raises(NotImplementedError):
            backend.delete_secret("test_key")

    def test_list_secrets_not_implemented(self):
        """Test that list_secrets raises NotImplementedError."""
        backend = VaultBackend()
        with pytest.raises(NotImplementedError):
            backend.list_secrets()
