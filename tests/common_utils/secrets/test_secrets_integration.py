"""Integration tests for the secrets management system."""

import os
import tempfile
import json
from unittest.mock import patch, MagicMock

import pytest

from common_utils.secrets.secrets_manager import (
    SecretsBackend,
    get_secret,
    set_secret,
    delete_secret,
    list_secrets,
)
from common_utils.secrets.config import SecretConfig
from common_utils.secrets.cli import handle_set, handle_get, handle_delete, handle_list


class TestSecretsIntegration:
    """Integration tests for the secrets management system."""

    def setup_method(self):
        """Set up test environment."""
        # Create a temporary directory for config files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.temp_dir.name, "config.json")

        # Create an empty config file
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump({}, f)

        # Clear any environment variables that might interfere with tests
        if "TEST_SECRET_KEY" in os.environ:
            del os.environ["TEST_SECRET_KEY"]

        # Create a patch for _check_auth to always return True for CLI tests
        self.auth_patcher = patch("common_utils.secrets.cli._check_auth", return_value=True)
        self.mock_auth = self.auth_patcher.start()

    def teardown_method(self):
        """Clean up after tests."""
        # Clean up temporary directory
        self.temp_dir.cleanup()

        # Clean up any environment variables set during tests
        if "TEST_SECRET_KEY" in os.environ:
            del os.environ["TEST_SECRET_KEY"]

        # Stop the auth patcher
        self.auth_patcher.stop()

    def test_config_with_secrets_manager(self):
        """Test integration between SecretConfig and SecretsManager."""
        # Create a config
        config = SecretConfig(self.config_file)

        # Set a config value that uses a secret
        config.set("app.secret", "test_secret_value", use_secret=True)

        # The config should now contain a secret reference
        assert "app" in config.config
        assert "secret" in config.config["app"]
        assert config.config["app"]["secret"].startswith("secret:")

        # Get the secret value through the config
        secret_value = config.get("app.secret", use_secret=True)
        assert secret_value == "test_secret_value"

        # Delete the config entry
        config.delete("app.secret", use_secret=True)

        # The config entry should be gone
        assert "secret" not in config.config["app"]

    def test_cli_with_secrets_manager(self):
        """Test integration between CLI and SecretsManager."""
        # Set up CLI args for setting a secret
        set_args = MagicMock()
        set_args.key = "TEST_SECRET_KEY"
        set_args.backend = "env"

        # Set the secret using the CLI handler
        with patch("common_utils.secrets.cli.get_secret_value", return_value="test_secret_value"):
            handle_set(set_args)

        # Verify the secret was set
        assert get_secret("TEST_SECRET_KEY") == "test_secret_value"

        # Set up CLI args for getting the secret
        get_args = MagicMock()
        get_args.key = "TEST_SECRET_KEY"
        get_args.backend = "env"

        # Get the secret using the CLI handler
        with patch("common_utils.secrets.cli.logger") as mock_logger:
            handle_get(get_args)
            # Check that logger.info was called with a message about retrieving the secret
            assert any("retrieved successfully" in str(call) for call in mock_logger.info.call_args_list)

        # Set up CLI args for listing secrets
        list_args = MagicMock()
        list_args.backend = "env"

        # List secrets using the CLI handler
        with patch("common_utils.secrets.cli.logger") as mock_logger:
            handle_list(list_args)
            # Check that logger.info was called at least once
            assert mock_logger.info.call_count > 0

        # Set up CLI args for deleting the secret
        delete_args = MagicMock()
        delete_args.key = "TEST_SECRET_KEY"
        delete_args.backend = "env"

        # Delete the secret using the CLI handler
        with patch("builtins.input", return_value="yes"):
            handle_delete(delete_args)

        # Verify the secret was deleted
        assert get_secret("TEST_SECRET_KEY") is None

    def test_config_with_cli(self):
        """Test integration between SecretConfig and CLI."""
        # Create a config
        config = SecretConfig(self.config_file)

        # Set a secret using the CLI handler
        set_args = MagicMock()
        set_args.key = "CONFIG_SECRET"
        set_args.backend = "env"

        with patch("common_utils.secrets.cli.get_secret_value", return_value="config_secret_value"):
            handle_set(set_args)

        # Set a config value that references the secret directly
        config.set("app.config_secret", "config_secret_value", use_secret=True)

        # Verify the secret was set in the environment
        assert get_secret("CONFIG_SECRET") == "config_secret_value"

        # Get the secret value through the config
        secret_value = config.get("app.config_secret", use_secret=True)
        assert secret_value == "config_secret_value"

        # Delete the config entry
        config.delete("app.config_secret", use_secret=True)

        # The config entry should be gone
        assert "config_secret" not in config.config["app"]
