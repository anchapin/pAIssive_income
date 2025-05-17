"""
config - Module for common_utils/secrets.config.

This module provides a configuration manager that can handle secret references.
"""

# Standard library imports
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Third-party imports
# Local imports
from common_utils.logging import get_logger

from .secrets_manager import SecretsBackend, get_secret, set_secret

# Initialize logger
logger = get_logger(__name__)


class SecretConfig:
    """Configuration manager that can handle secret references."""

    # Constants
    SECRET_PREFIX = "secret:"  # noqa: S105

    def __init__(
        self,
        config_file: str | None = None,
        secrets_backend: SecretsBackend | str | None = None,
    ) -> None:
        """
        Initialize the configuration manager.

        Args:
        ----
            config_file: Path to the configuration file
            secrets_backend: Backend to use for secrets (SecretsBackend enum, string, or None)

        """
        self.config_file = config_file or os.environ.get(
            "PAISSIVE_CONFIG_FILE", "config.json"
        )

        # Handle different types for secrets_backend
        if secrets_backend is None:
            self.secrets_backend = SecretsBackend.ENV
        elif isinstance(secrets_backend, str):
            try:
                self.secrets_backend = SecretsBackend.from_string(secrets_backend)
            except ValueError:
                logger.warning("Invalid backend string provided, using ENV")
                self.secrets_backend = SecretsBackend.ENV
        else:
            self.secrets_backend = secrets_backend
        self.config: dict[str, Any] = {}
        self._load_config()
        logger.info("Configuration manager initialized with file: %s", self.config_file)

    def _is_secret_reference(self, value: Any) -> bool:
        """Check if a value is a secret reference.

        Args:
            value: The value to check

        Returns:
            bool: True if the value is a secret reference, False otherwise
        """
        if not isinstance(value, str):
            return False
        return value.startswith("secret:")

    def _extract_secret_key(self, value: Any) -> Optional[str]:
        """Extract the key from a secret reference.

        Args:
            value: The value to extract the key from

        Returns:
            Optional[str]: The extracted key, or None if the value is not a secret reference
        """
        if not self._is_secret_reference(value):
            return None
        # Extract the key by removing the "secret:" prefix
        return value[len("secret:"):]

    def _load_config(self) -> None:
        """Load the configuration from the file."""
        if self.config_file is None:
            logger.warning("No configuration file specified")
            return

        config_path = Path(self.config_file)
        if not config_path.exists():
            logger.warning("Configuration file %s not found", self.config_file)
            return

        try:
            with config_path.open(encoding="utf-8") as f:
                self.config = json.load(f)
            logger.debug("Loaded configuration from %s", self.config_file)
        except Exception:
            logger.exception("Error loading configuration")

    def _save_config(self) -> None:
        """Save the configuration to the file."""
        if self.config_file is None:
            logger.warning("No configuration file specified")
            return

        try:
            config_path = Path(self.config_file)
            with config_path.open("w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            logger.debug("Saved configuration to %s", self.config_file)
        except Exception:
            logger.exception("Error saving configuration")

    def get(self, key: str, default: object = None, use_secret: bool = False) -> object:
        """
        Get a configuration value.

        Args:
        ----
            key: The key to get
            default: The default value to return if the key is not found
            use_secret: Whether to treat the value as a secret

        Returns:
        -------
            Any: The configuration value

        """
        # Handle empty key - return the entire config
        if not key:
            logger.debug("Empty key provided, returning entire config")
            return self.config

        # First try to get from environment variables
        env_key = key.replace(".", "_").upper()
        env_value = os.environ.get(env_key)
        if env_value is not None:
            # Don't log the actual key name as it might reveal sensitive information
            logger.debug("Got configuration value from environment")
            return env_value

        # Then try to get from the configuration file
        parts = key.split(".")
        value = self.config
        for part in parts:
            if not isinstance(value, dict) or part not in value:
                # Don't log the actual key name as it might reveal sensitive information
                logger.debug("Configuration key not found, using default")
                return default
            value = value[part]

        # Process secret references if requested and value is a string
        # Explicitly annotate value to help mypy understand the type
        value_to_check: Any = value
        if (
            use_secret
            and isinstance(value_to_check, str)
            and value_to_check.startswith(self.SECRET_PREFIX)
        ):
            # Extract the key and get the secret
            secret_key = value_to_check[len(self.SECRET_PREFIX) :]
            logger.debug("Getting secret from configuration")
            return get_secret(secret_key, self.secrets_backend)

        # Don't log the actual key name as it might reveal sensitive information
        logger.debug("Got configuration value from config file")
        return value

    def set(self, key: str, value: object, use_secret: bool = False) -> None:
        """
        Set a configuration value.

        Args:
        ----
            key: The key to set
            value: The value to set
            use_secret: Whether to treat the value as a secret

        """
        # Handle empty key - replace the entire config
        if not key:
            if isinstance(value, dict):
                self.config = value
                self._save_config()
                logger.debug("Replaced entire configuration")
                return
            else:
                logger.warning("Cannot set non-dict value as entire configuration")
                return

        if use_secret:
            # Store the value as a secret and save a reference
            # Don't log the actual key name as it might reveal sensitive information
            logger.debug("Setting secret in configuration")
            set_secret(key, str(value), self.secrets_backend)
            value = f"{self.SECRET_PREFIX}{key}"

        # Set in the configuration file
        parts = key.split(".")
        config = self.config
        for part in parts[:-1]:
            if part not in config or not isinstance(config[part], dict):
                config[part] = {}
            config = config[part]
        config[parts[-1]] = value

        # Save the configuration
        self._save_config()
        # Don't log the actual key name as it might reveal sensitive information
        logger.debug("Set configuration value")

    def delete(self, key: str, use_secret: bool = False) -> bool:
        """
        Delete a configuration value.

        Args:
        ----
            key: The key to delete
            use_secret: Whether to treat the value as a secret

        Returns:
        -------
            bool: True if the key was deleted, False otherwise

        """
        # Handle empty key - clear the entire config
        if not key:
            self.config = {}
            self._save_config()
            logger.debug("Cleared entire configuration")
            return True

        # Delete from the configuration file
        parts = key.split(".")
        config = self.config
        for part in parts[:-1]:
            if part not in config or not isinstance(config[part], dict):
                # Don't log the actual key name as it might reveal sensitive information
                logger.debug("Configuration key not found")
                return False
            config = config[part]

        if parts[-1] not in config:
            # Don't log the actual key name as it might reveal sensitive information
            logger.debug("Configuration key not found")
            return False

        # If it's a secret reference, delete the actual secret
        value = config[parts[-1]]
        # Process secret references if requested and value is a string
        # Explicitly annotate value to help mypy understand the type
        value_to_check: Any = value
        if (
            use_secret
            and isinstance(value_to_check, str)
            and value_to_check.startswith(self.SECRET_PREFIX)
        ):
            # Extract the key and delete the secret
            secret_key = value_to_check[len(self.SECRET_PREFIX) :]
            logger.debug("Deleting secret from configuration")
            from .secrets_manager import delete_secret

            # Delete the secret
            delete_result = delete_secret(secret_key, self.secrets_backend)
            # Log the result
            if delete_result:
                logger.debug("Secret deleted successfully")
            else:
                logger.debug("Failed to delete secret")

        # Delete from the configuration
        del config[parts[-1]]
        self._save_config()
        # Don't log the actual key name as it might reveal sensitive information
        logger.debug("Deleted configuration value")
        return True
