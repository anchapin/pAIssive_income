"""test_config_extended - Extended tests for common_utils/secrets/config.py."""

# Standard library imports
import json
import logging
import os
import unittest
from unittest.mock import MagicMock, mock_open, patch

# Third-party imports
import pytest

# Local imports
from common_utils.secrets.config import SecretConfig
from common_utils.secrets.secrets_manager import SecretsBackend


class TestSecretConfigExtended(unittest.TestCase):
    """Extended test suite for SecretConfig class."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear any environment variables that might interfere with tests
        if "PAISSIVE_CONFIG_FILE" in os.environ:
            del os.environ["PAISSIVE_CONFIG_FILE"]

    def tearDown(self):
        """Tear down test fixtures."""
        # Clear any environment variables set during tests
        if "PAISSIVE_CONFIG_FILE" in os.environ:
            del os.environ["PAISSIVE_CONFIG_FILE"]
        if "TEST_CONFIG_KEY" in os.environ:
            del os.environ["TEST_CONFIG_KEY"]

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_init_with_default_config_file(self, mock_exists, mock_file):
        """Test initializing with default config file."""
        config = SecretConfig()
        assert config.config_file == "config.json"
        assert config.secrets_backend == SecretsBackend.ENV
        assert config.config == {"app": {"name": "test"}}
        mock_file.assert_called_with("config.json", encoding="utf-8")

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_init_with_custom_config_file(self, mock_exists, mock_file):
        """Test initializing with custom config file."""
        config = SecretConfig("custom_config.json")
        assert config.config_file == "custom_config.json"
        assert config.secrets_backend == SecretsBackend.ENV
        assert config.config == {"app": {"name": "test"}}
        mock_file.assert_called_with("custom_config.json", encoding="utf-8")

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_init_with_custom_secrets_backend(self, mock_exists, mock_file):
        """Test initializing with custom secrets backend."""
        config = SecretConfig(secrets_backend=SecretsBackend.FILE)
        assert config.config_file == "config.json"
        assert config.secrets_backend == SecretsBackend.FILE
        assert config.config == {"app": {"name": "test"}}

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_init_with_env_config_file(self, mock_exists, mock_file):
        """Test initializing with config file from environment variable."""
        os.environ["PAISSIVE_CONFIG_FILE"] = "env_config.json"
        config = SecretConfig()
        assert config.config_file == "env_config.json"
        mock_file.assert_called_with("env_config.json", encoding="utf-8")

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=False)
    def test_init_with_nonexistent_config_file(self, mock_exists, mock_file):
        """Test initializing with nonexistent config file."""
        config = SecretConfig()
        assert config.config == {}
        mock_file.assert_not_called()

    @patch("builtins.open", new_callable=mock_open, read_data="invalid json")
    @patch("os.path.exists", return_value=True)
    def test_init_with_invalid_json(self, mock_exists, mock_file):
        """Test initializing with invalid JSON in config file."""
        config = SecretConfig()
        assert config.config == {}
        mock_file.assert_called_with("config.json", encoding="utf-8")

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_get_config_value(self, mock_exists, mock_file):
        """Test getting a config value."""
        config = SecretConfig()
        assert config.get("app.name") == "test"

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_get_config_value_with_default(self, mock_exists, mock_file):
        """Test getting a config value with default."""
        config = SecretConfig()
        assert config.get("app.version", default="1.0") == "1.0"

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_get_config_value_from_env(self, mock_exists, mock_file):
        """Test getting a config value from environment variable."""
        os.environ["TEST_CONFIG_KEY"] = "env_value"
        config = SecretConfig()
        assert config.get("TEST_CONFIG_KEY") == "env_value"

    @patch("common_utils.secrets.config.get_secret")
    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"secret": "secret:app.secret"}}')
    @patch("os.path.exists", return_value=True)
    def test_get_secret_value(self, mock_exists, mock_file, mock_get_secret):
        """Test getting a secret value."""
        mock_get_secret.return_value = "secret_value"
        config = SecretConfig()
        # First set up the config with a secret reference
        config.config = {"app": {"secret": "secret:app.secret"}}
        # Now get the secret value
        result = config.get("app.secret", use_secret=True)
        assert result == "secret_value"
        mock_get_secret.assert_called_once_with("app.secret", SecretsBackend.ENV)

    @patch("common_utils.secrets.config.get_secret")
    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_get_secret_value_with_default(self, mock_exists, mock_file, mock_get_secret):
        """Test getting a secret value with default."""
        # Set up the mock to return None to simulate a missing secret
        mock_get_secret.return_value = None
        config = SecretConfig()
        # First set up the config with a secret reference
        config.config = {"app": {"secret": "secret:app.secret"}}
        # Now get the secret value with default
        # The key needs to be the full path to the secret in the config
        result = config.get("app.secret", default="default_secret", use_secret=True)
        assert result == "default_secret"
        mock_get_secret.assert_called_once_with("app.secret", SecretsBackend.ENV)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    @patch("json.dump")
    def test_set_config_value(self, mock_json_dump, mock_exists, mock_file):
        """Test setting a config value."""
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}
        config.set("app.version", "1.0")
        assert config.config == {"app": {"name": "test", "version": "1.0"}}
        mock_file.assert_called_with("config.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch("common_utils.secrets.config.set_secret")
    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    @patch("json.dump")
    def test_set_secret_value(self, mock_json_dump, mock_exists, mock_file, mock_set_secret):
        """Test setting a secret value."""
        mock_set_secret.return_value = True
        config = SecretConfig()
        # The actual implementation doesn't return anything
        config.set("app.secret", "secret_value", use_secret=True)
        mock_set_secret.assert_called_once_with("app.secret", "secret_value", SecretsBackend.ENV)
        # Check that the config was updated with a secret reference
        assert config.config["app"]["secret"] == "secret:app.secret"

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    @patch("json.dump")
    def test_set_nested_config(self, mock_json_dump, mock_exists, mock_file):
        """Test setting a nested config value."""
        config = SecretConfig()
        config.config = {}
        config.set("app.server.host", "localhost")
        assert config.config == {"app": {"server": {"host": "localhost"}}}
        mock_file.assert_called_with("config.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    @patch("json.dump")
    def test_set_config_value_with_existing_non_dict(self, mock_json_dump, mock_exists, mock_file):
        """Test setting a config value when an intermediate key exists but is not a dict."""
        config = SecretConfig()
        config.config = {"app": "not_a_dict"}
        config.set("app.version", "1.0")
        assert config.config == {"app": {"version": "1.0"}}
        mock_file.assert_called_with("config.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    @patch("json.dump", side_effect=Exception("Test exception"))
    def test_set_config_value_with_exception(self, mock_json_dump, mock_exists, mock_file):
        """Test setting a config value when an exception occurs during save."""
        with patch("common_utils.secrets.config.logger") as mock_logger:
            config = SecretConfig()
            config.config = {"app": {"name": "test"}}
            config.set("app.version", "1.0")
            assert config.config == {"app": {"name": "test", "version": "1.0"}}
            mock_file.assert_called_with("config.json", "w", encoding="utf-8")
            mock_json_dump.assert_called_once()
            # The logger.exception is called twice - once during initialization and once during save
            assert mock_logger.exception.call_count == 2
            assert "Error saving configuration" in mock_logger.exception.call_args_list[1].args[0]

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_get_config_value_with_nonexistent_key(self, mock_exists, mock_file):
        """Test getting a config value with a nonexistent key."""
        config = SecretConfig()
        assert config.get("nonexistent.key") is None

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_get_config_value_with_nonexistent_intermediate_key(self, mock_exists, mock_file):
        """Test getting a config value with a nonexistent intermediate key."""
        config = SecretConfig()
        assert config.get("app.nonexistent.key") is None

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_get_config_value_with_non_dict_intermediate(self, mock_exists, mock_file):
        """Test getting a config value with a non-dict intermediate value."""
        config = SecretConfig()
        assert config.get("app.name.subkey") is None

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_get_with_empty_key(self, mock_exists, mock_file):
        """Test getting a config value with an empty key."""
        config = SecretConfig()
        # Empty key should return the entire config
        assert config.get("") == {"app": {"name": "test"}}

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    @patch("json.dump")
    def test_set_with_empty_key(self, mock_json_dump, mock_exists, mock_file):
        """Test setting a config value with an empty key."""
        config = SecretConfig()
        # Setting with empty key should replace the entire config
        config.set("", {"new": "config"})
        assert config.config == {"new": "config"}
        mock_file.assert_called_with("config.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    @patch("json.dump")
    def test_delete_with_empty_key(self, mock_json_dump, mock_exists, mock_file):
        """Test deleting a config value with an empty key."""
        config = SecretConfig()
        # Deleting with empty key should clear the entire config
        config.delete("")
        assert config.config == {}
        mock_file.assert_called_with("config.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch("common_utils.secrets.config.set_secret", return_value=False)
    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_set_secret_failure(self, mock_exists, mock_file, mock_set_secret):
        """Test setting a secret value when the operation fails."""
        config = SecretConfig()
        # When set_secret fails, the config should not be updated
        with patch("common_utils.secrets.config.logger") as mock_logger:
            config.set("app.secret", "secret_value", use_secret=True)
            mock_set_secret.assert_called_once_with("app.secret", "secret_value", SecretsBackend.ENV)
            # Check that the config was not updated
            assert "secret" not in config.config.get("app", {})
            # Check that an error was logged
            mock_logger.error.assert_called_once()

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"secret": "secret:app.secret"}}')
    @patch("os.path.exists", return_value=True)
    def test_is_secret_reference_true(self, mock_exists, mock_file):
        """Test checking if a value is a secret reference."""
        config = SecretConfig()
        # Check that a secret reference is correctly identified
        assert config._is_secret_reference("secret:app.secret") is True

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_is_secret_reference_false(self, mock_exists, mock_file):
        """Test checking if a value is not a secret reference."""
        config = SecretConfig()
        # Check that a non-secret reference is correctly identified
        assert config._is_secret_reference("not_a_secret") is False
        assert config._is_secret_reference(123) is False
        assert config._is_secret_reference(None) is False

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_extract_secret_key(self, mock_exists, mock_file):
        """Test extracting the key from a secret reference."""
        config = SecretConfig()
        # Check that the key is correctly extracted
        assert config._extract_secret_key("secret:app.secret") == "app.secret"

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_extract_secret_key_not_reference(self, mock_exists, mock_file):
        """Test extracting the key from a non-secret reference."""
        config = SecretConfig()
        # Check that None is returned for non-secret references
        assert config._extract_secret_key("not_a_secret") is None
