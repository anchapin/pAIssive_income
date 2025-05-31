"""Comprehensive test module for common_utils.secrets.config."""

import json
import os
import tempfile
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, mock_open, patch

import pytest

from common_utils.secrets.config import SecretConfig
from common_utils.secrets.secrets_manager import SecretsBackend, delete_secret


class TestSecretConfigComprehensive:
    """Comprehensive test suite for SecretConfig class."""

    def setup_method(self):
        """Set up test environment."""
        # Create a temporary file for config data
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()

        # Save the original environment
        self.original_env = os.environ.copy()

    def teardown_method(self):
        """Clean up test environment."""
        # Delete the temporary file
        os.unlink(self.temp_file.name)

        # Restore the original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_init_default(self):
        """Test initialization with default parameters."""
        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("pathlib.Path.exists", return_value=True):
                config = SecretConfig()
                assert config.config_file == "config.json"
                assert config.secrets_backend == SecretsBackend.ENV
                assert config.config == {}

    def test_init_with_custom_config_file(self):
        """Test initialization with a custom config file."""
        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("pathlib.Path.exists", return_value=True):
                config = SecretConfig(config_file=self.temp_file.name)
                assert config.config_file == self.temp_file.name
                assert config.secrets_backend == SecretsBackend.ENV
                assert config.config == {}

    def test_init_with_custom_backend(self):
        """Test initialization with a custom secrets backend."""
        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("pathlib.Path.exists", return_value=True):
                config = SecretConfig(secrets_backend=SecretsBackend.FILE)
                assert config.config_file == "config.json"
                assert config.secrets_backend == SecretsBackend.FILE
                assert config.config == {}

    def test_init_with_backend_string(self):
        """Test initialization with a backend string."""
        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("pathlib.Path.exists", return_value=True):
                config = SecretConfig(secrets_backend="file")
                assert config.config_file == "config.json"
                assert config.secrets_backend == SecretsBackend.FILE
                assert config.config == {}

    def test_init_with_invalid_backend_string(self):
        """Test initialization with an invalid backend string."""
        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("pathlib.Path.exists", return_value=True):
                config = SecretConfig(secrets_backend="invalid")
                assert config.config_file == "config.json"
                assert config.secrets_backend == SecretsBackend.ENV
                assert config.config == {}

    def test_init_with_env_config_file(self):
        """Test initialization with config file from environment variable."""
        os.environ["PAISSIVE_CONFIG_FILE"] = self.temp_file.name
        with patch("builtins.open", mock_open(read_data="{}")):
            with patch("pathlib.Path.exists", return_value=True):
                config = SecretConfig()
                assert config.config_file == self.temp_file.name
                assert config.secrets_backend == SecretsBackend.ENV
                assert config.config == {}

    def test_init_with_nonexistent_file(self):
        """Test initialization with a nonexistent config file."""
        with patch("pathlib.Path.exists", return_value=False):
            config = SecretConfig(config_file="nonexistent.json")
            assert config.config_file == "nonexistent.json"
            assert config.secrets_backend == SecretsBackend.ENV
            assert config.config == {}

    def test_init_with_invalid_json(self):
        """Test initialization with an invalid JSON file."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("pathlib.Path.exists", return_value=True):
                config = SecretConfig(config_file=self.temp_file.name)
                assert config.config_file == self.temp_file.name
                assert config.secrets_backend == SecretsBackend.ENV
                assert config.config == {}

    def test_is_secret_reference_true(self):
        """Test _is_secret_reference with a secret reference."""
        config = SecretConfig()
        assert config._is_secret_reference("secret:test") is True

    def test_is_secret_reference_false(self):
        """Test _is_secret_reference with a non-secret reference."""
        config = SecretConfig()
        assert config._is_secret_reference("test") is False
        assert config._is_secret_reference(123) is False
        assert config._is_secret_reference(None) is False
        assert config._is_secret_reference({"key": "value"}) is False

    def test_extract_secret_key_valid(self):
        """Test _extract_secret_key with a valid secret reference."""
        config = SecretConfig()
        assert config._extract_secret_key("secret:test") == "test"

    def test_extract_secret_key_invalid(self):
        """Test _extract_secret_key with an invalid secret reference."""
        config = SecretConfig()
        assert config._extract_secret_key("test") is None
        assert config._extract_secret_key(123) is None
        assert config._extract_secret_key(None) is None
        assert config._extract_secret_key({"key": "value"}) is None

    def test_load_config_success(self):
        """Test _load_config with a valid config file."""
        # Create a config file
        config_data = {"app": {"name": "test"}}
        with open(self.temp_file.name, "w") as f:
            json.dump(config_data, f)

        # Create a config instance
        config = SecretConfig(config_file=self.temp_file.name)

        # Verify the config was loaded
        assert config.config == config_data

    def test_load_config_no_file(self):
        """Test _load_config with no config file."""
        config = SecretConfig(config_file=None)
        assert config.config == {}

    def test_save_config_success(self):
        """Test _save_config with a valid config file."""
        # Create a config instance
        config = SecretConfig(config_file=self.temp_file.name)
        config.config = {"app": {"name": "test"}}

        # Save the config
        config._save_config()

        # Verify the config was saved
        with open(self.temp_file.name) as f:
            saved_data = json.load(f)
        assert saved_data == config.config

    def test_save_config_no_file(self):
        """Test _save_config with no config file."""
        config = SecretConfig(config_file=None)
        config.config = {"app": {"name": "test"}}

        # Save the config (should not raise an exception)
        config._save_config()

    def test_get_empty_key(self):
        """Test get with an empty key."""
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}

        # Get with an empty key
        result = config.get("")

        # Verify the result
        assert result == config.config

    def test_get_from_env(self):
        """Test get with a key from environment variables."""
        # Set an environment variable
        os.environ["APP_NAME"] = "test_env"

        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"name": "test_config"}}

        # Get the value
        result = config.get("app.name")

        # Verify the result
        assert result == "test_env"

    def test_get_from_config(self):
        """Test get with a key from the config file."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"name": "test_config"}}

        # Get the value
        result = config.get("app.name")

        # Verify the result
        assert result == "test_config"

    def test_get_nested_key(self):
        """Test get with a nested key."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"settings": {"debug": True}}}

        # Get the value
        result = config.get("app.settings.debug")

        # Verify the result
        assert result is True

    def test_get_missing_key(self):
        """Test get with a missing key."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}

        # Get the value
        result = config.get("app.version")

        # Verify the result
        assert result is None

    def test_get_missing_key_with_default(self):
        """Test get with a missing key and a default value."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}

        # Get the value
        result = config.get("app.version", default="1.0")

        # Verify the result
        assert result == "1.0"

    def test_get_secret_reference(self):
        """Test get with a secret reference."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"api_key": "secret:API_KEY"}}

        # Mock get_secret
        with patch("common_utils.secrets.config.get_secret") as mock_get_secret:
            mock_get_secret.return_value = "test_secret"

            # Get the value
            result = config.get("app.api_key", use_secret=True)

            # Verify the result
            assert result == "test_secret"
            mock_get_secret.assert_called_once_with("API_KEY", SecretsBackend.ENV)

    def test_set_empty_key_dict(self):
        """Test set with an empty key and a dict value."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}

        # Set the value
        new_config = {"new": {"key": "value"}}
        config.set("", new_config)

        # Verify the result
        assert config.config == new_config

    def test_set_empty_key_non_dict(self):
        """Test set with an empty key and a non-dict value."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}

        # Set the value
        config.set("", "not a dict")

        # Verify the result (should not change)
        assert config.config == {"app": {"name": "test"}}

    def test_set_new_key(self):
        """Test set with a new key."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}

        # Set the value
        config.set("app.version", "1.0")

        # Verify the result
        assert config.config == {"app": {"name": "test", "version": "1.0"}}

    def test_set_existing_key(self):
        """Test set with an existing key."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}

        # Set the value
        config.set("app.name", "new_test")

        # Verify the result
        assert config.config == {"app": {"name": "new_test"}}

    def test_set_nested_key(self):
        """Test set with a nested key."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"settings": {"debug": True}}}

        # Set the value
        config.set("app.settings.debug", False)

        # Verify the result
        assert config.config == {"app": {"settings": {"debug": False}}}

    def test_set_secret(self):
        """Test set with use_secret=True."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}

        # Mock set_secret
        with patch("common_utils.secrets.config.set_secret") as mock_set_secret:
            # Set the value
            config.set("app.api_key", "test_secret", use_secret=True)

            # Verify the result
            assert config.config == {"app": {"name": "test", "api_key": "secret:app.api_key"}}
            mock_set_secret.assert_called_once_with("app.api_key", "test_secret", SecretsBackend.ENV)

    def test_delete_empty_key(self):
        """Test delete with an empty key."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}

        # Delete the key
        result = config.delete("")

        # Verify the result
        assert result is True
        assert config.config == {}

    def test_delete_existing_key(self):
        """Test delete with an existing key."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"name": "test", "version": "1.0"}}

        # Delete the key
        result = config.delete("app.name")

        # Verify the result
        assert result is True
        assert config.config == {"app": {"version": "1.0"}}

    def test_delete_missing_key(self):
        """Test delete with a missing key."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}

        # Delete the key
        result = config.delete("app.version")

        # Verify the result
        assert result is False
        assert config.config == {"app": {"name": "test"}}

    def test_delete_secret_reference(self):
        """Test delete with a secret reference."""
        # Create a config instance
        config = SecretConfig()
        config.config = {"app": {"api_key": "secret:API_KEY"}}

        # Mock delete_secret
        with patch("common_utils.secrets.config.delete_secret") as mock_delete_secret:
            mock_delete_secret.return_value = True

            # Delete the key
            result = config.delete("app.api_key", use_secret=True)

            # Verify the result
            assert result is True
            assert config.config == {"app": {}}
            mock_delete_secret.assert_called_once_with("API_KEY", SecretsBackend.ENV)
