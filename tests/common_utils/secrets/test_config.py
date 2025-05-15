"""Tests for the secrets config module."""

import os
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock

from common_utils.secrets.config import SecretConfig
from common_utils.secrets.secrets_manager import SecretsBackend


class TestSecretConfig:
    """Tests for the SecretConfig class."""

    def setup_method(self):
        """Set up test environment."""
        # Clear any environment variables that might interfere with tests
        if "PAISSIVE_CONFIG_FILE" in os.environ:
            del os.environ["PAISSIVE_CONFIG_FILE"]
        if "TEST_CONFIG_KEY" in os.environ:
            del os.environ["TEST_CONFIG_KEY"]

    def teardown_method(self):
        """Clean up after tests."""
        # Clean up any environment variables set during tests
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

    @patch("builtins.open", new_callable=mock_open, read_data='invalid json')
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

    @patch("builtins.open", new_callable=mock_open, read_data='{"app": {"name": "test"}}')
    @patch("os.path.exists", return_value=True)
    def test_get_nested_config(self, mock_exists, mock_file):
        """Test getting a nested config value."""
        config = SecretConfig()
        assert config.get("app") == {"name": "test"}

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
    def test_set_config_with_existing_non_dict(self, mock_json_dump, mock_exists, mock_file):
        """Test setting a config value when the parent is not a dict."""
        config = SecretConfig()
        config.config = {"app": "not_a_dict"}
        config.set("app.server.host", "localhost")
        assert config.config == {"app": {"server": {"host": "localhost"}}}
        mock_file.assert_called_with("config.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_get_config_with_non_dict_parent(self, mock_exists, mock_file):
        """Test getting a config value when the parent is not a dict."""
        config = SecretConfig()
        config.config = {"app": "not_a_dict"}
        assert config.get("app.server.host", default="default_value") == "default_value"

    @patch("common_utils.secrets.config.get_secret")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_get_secret_with_non_string_value(self, mock_exists, mock_file, mock_get_secret):
        """Test getting a secret value when the value is not a string."""
        config = SecretConfig()
        config.config = {"app": {"secret": 123}}  # Not a string
        result = config.get("app.secret", use_secret=True)
        assert result == 123
        mock_get_secret.assert_not_called()

    @patch("common_utils.secrets.secrets_manager.delete_secret")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    @patch("json.dump")
    def test_delete_config_with_secret(self, mock_json_dump, mock_exists, mock_file, mock_delete_secret):
        """Test deleting a config value that is a secret reference."""
        config = SecretConfig()
        config.config = {"app": {"secret": "secret:app.secret"}}
        config.delete("app.secret", use_secret=True)
        assert "secret" not in config.config["app"]
        mock_delete_secret.assert_called_once_with("app.secret", SecretsBackend.ENV)
        mock_file.assert_called_with("config.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    @patch("json.dump")
    def test_delete_config_without_secret(self, mock_json_dump, mock_exists, mock_file):
        """Test deleting a config value that is not a secret reference."""
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}
        config.delete("app.name")
        assert "name" not in config.config["app"]
        mock_file.assert_called_with("config.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_delete_nonexistent_config(self, mock_exists, mock_file):
        """Test deleting a config value that doesn't exist."""
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}
        # This should not raise an exception
        config.delete("app.nonexistent")
        assert config.config == {"app": {"name": "test"}}

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_delete_with_invalid_path(self, mock_exists, mock_file):
        """Test deleting a config value with an invalid path."""
        config = SecretConfig()
        config.config = {"app": "not_a_dict"}
        # This should not raise an exception
        config.delete("app.name")
        assert config.config == {"app": "not_a_dict"}

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    @patch("json.dump")
    def test_save_config(self, mock_json_dump, mock_exists, mock_file):
        """Test saving the configuration to file."""
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}
        config._save_config()
        mock_file.assert_called_with("config.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once_with({"app": {"name": "test"}}, mock_file(), indent=2)

    @patch("builtins.open", side_effect=IOError("Test error"))
    @patch("os.path.exists", return_value=True)
    def test_save_config_with_error(self, mock_exists, mock_file):
        """Test saving the configuration with an error."""
        config = SecretConfig()
        config.config = {"app": {"name": "test"}}
        # This should not raise an exception
        with patch("common_utils.secrets.config.logger") as mock_logger:
            config._save_config()
            mock_logger.exception.assert_called_once()
