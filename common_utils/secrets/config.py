"""config - Module for common_utils/secrets.config.

This module provides a configuration manager that can handle secret references.
"""

# Standard library imports
import json
import os

from typing import Any
from typing import Optional

# Third-party imports
# Local imports
from common_utils.logging import get_logger

from .secrets_manager import SecretsBackend
from .secrets_manager import get_secret
from .secrets_manager import set_secret

# Initialize logger
logger = get_logger(__name__)


class SecretConfig:
    """Configuration manager that can handle secret references."""

    def __init__(
        self,
        config_file: Optional[str] = None,
        secrets_backend: Optional[SecretsBackend] = None,
    ):
        """Initialize the configuration manager.

        Args:
        ----
            config_file: Path to the configuration file
            secrets_backend: Backend to use for secrets

        """
        self.config_file = config_file or os.environ.get(
            "PAISSIVE_CONFIG_FILE", "config.json"
        )
        self.secrets_backend = secrets_backend or SecretsBackend.ENV
        self.config: dict[str, Any] = {}
        self._load_config()
        logger.info(f"Configuration manager initialized with file: {self.config_file}")

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

        if not os.path.exists(self.config_file):
            logger.warning(f"Configuration file {self.config_file} not found")
            return

        try:
            with open(self.config_file, encoding="utf-8") as f:
                self.config = json.load(f)
            logger.debug(f"Loaded configuration from {self.config_file}")
        except Exception:
            logger.exception("Error loading configuration")

    def _save_config(self) -> None:
        """Save the configuration to the file."""
        if self.config_file is None:
            logger.warning("No configuration file specified")
            return

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            logger.debug(f"Saved configuration to {self.config_file}")
        except Exception:
            logger.exception("Error saving configuration")

    def get(self, key: str, default: Any = None, use_secret: bool = False) -> Any:
        """Get a configuration value.

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
        if use_secret and isinstance(value_to_check, str):
            # Check for secret reference prefix
            if self._is_secret_reference(value_to_check):
                # Extract the key and get the secret
                secret_key = self._extract_secret_key(value_to_check)
                if secret_key:
                    logger.debug("Getting secret from configuration")
                    secret_value = get_secret(secret_key, self.secrets_backend)
                    # If the secret is not found, return the default value
                    if secret_value is None:
                        return default
                    return secret_value

        # Don't log the actual key name as it might reveal sensitive information
        logger.debug("Got configuration value from config file")
        return value

    def set(self, key: str, value: Any, use_secret: bool = False) -> None:
        """Set a configuration value.

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
            success = set_secret(key, str(value), self.secrets_backend)
            if not success:
                logger.error("Failed to set secret in backend")
                return
            value = f"secret:{key}"

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
        """Delete a configuration value.

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
        if use_secret and isinstance(value_to_check, str):
            # Check for secret reference prefix
            if self._is_secret_reference(value_to_check):
                # Extract the key and delete the secret
                secret_key = self._extract_secret_key(value_to_check)
                if secret_key:
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
