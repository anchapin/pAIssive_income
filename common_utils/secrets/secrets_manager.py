"""secrets_manager - Module for common_utils/secrets.secrets_manager.

This module provides a unified interface for managing secrets across different backends.
"""

# Standard library imports
import enum
import os
from typing import Any, Dict, Optional, Union

# Third-party imports
# Local imports
from common_utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


class SecretsBackend(enum.Enum):
    """Enum for supported secrets backends."""

    ENV = "env"
    FILE = "file"
    MEMORY = "memory"
    VAULT = "vault"


class SecretsManager:
    """Manager for handling secrets across different backends."""

    def __init__(self, default_backend: SecretsBackend = SecretsBackend.ENV):
        """Initialize the secrets manager.

        Args:
        ----
            default_backend: The default backend to use for secrets

        """
        self.default_backend = default_backend
        logger.info(
            f"Secrets manager initialized with default backend: {default_backend.value}"
        )

    def get_secret(
        self, key: str, backend: Optional[SecretsBackend] = None
    ) -> Optional[str]:
        """Get a secret from the specified backend.

        Args:
        ----
            key: The key of the secret
            backend: The backend to use (defaults to the default backend)

        Returns:
        -------
            Optional[str]: The secret value, or None if not found

        """
        backend = backend or self.default_backend
        logger.debug(f"Getting secret {key} from {backend.value} backend")

        if backend == SecretsBackend.ENV:
            return os.environ.get(key)
        elif backend == SecretsBackend.FILE:
            logger.warning("File backend not yet implemented")
            return None
        elif backend == SecretsBackend.MEMORY:
            logger.warning("Memory backend not yet implemented")
            return None
        elif backend == SecretsBackend.VAULT:
            logger.warning("Vault backend not yet implemented")
            return None
        else:
            logger.error(f"Unknown backend: {backend}")
            return None

    def set_secret(
        self, key: str, value: str, backend: Optional[SecretsBackend] = None
    ) -> bool:
        """Set a secret in the specified backend.

        Args:
        ----
            key: The key of the secret
            value: The value of the secret
            backend: The backend to use (defaults to the default backend)

        Returns:
        -------
            bool: True if the secret was set successfully, False otherwise

        """
        backend = backend or self.default_backend
        logger.debug(f"Setting secret {key} in {backend.value} backend")

        if backend == SecretsBackend.ENV:
            os.environ[key] = value
            return True
        elif backend == SecretsBackend.FILE:
            logger.warning("File backend not yet implemented")
            return False
        elif backend == SecretsBackend.MEMORY:
            logger.warning("Memory backend not yet implemented")
            return False
        elif backend == SecretsBackend.VAULT:
            logger.warning("Vault backend not yet implemented")
            return False
        else:
            logger.error(f"Unknown backend: {backend}")
            return False

    def delete_secret(self, key: str, backend: Optional[SecretsBackend] = None) -> bool:
        """Delete a secret from the specified backend.

        Args:
        ----
            key: The key of the secret
            backend: The backend to use (defaults to the default backend)

        Returns:
        -------
            bool: True if the secret was deleted successfully, False otherwise

        """
        backend = backend or self.default_backend
        logger.debug(f"Deleting secret {key} from {backend.value} backend")

        if backend == SecretsBackend.ENV:
            if key in os.environ:
                del os.environ[key]
                return True
            return False
        elif backend == SecretsBackend.FILE:
            logger.warning("File backend not yet implemented")
            return False
        elif backend == SecretsBackend.MEMORY:
            logger.warning("Memory backend not yet implemented")
            return False
        elif backend == SecretsBackend.VAULT:
            logger.warning("Vault backend not yet implemented")
            return False
        else:
            logger.error(f"Unknown backend: {backend}")
            return False

    def list_secrets(self, backend: Optional[SecretsBackend] = None) -> Dict[str, Any]:
        """List all secrets in the specified backend.

        Args:
        ----
            backend: The backend to use (defaults to the default backend)

        Returns:
        -------
            Dict[str, Any]: Dictionary of secrets

        """
        backend = backend or self.default_backend
        logger.debug(f"Listing secrets from {backend.value} backend")

        if backend == SecretsBackend.ENV:
            # Return a copy of the environment variables
            return dict(os.environ)
        elif backend == SecretsBackend.FILE:
            logger.warning("File backend not yet implemented")
            return {}
        elif backend == SecretsBackend.MEMORY:
            logger.warning("Memory backend not yet implemented")
            return {}
        elif backend == SecretsBackend.VAULT:
            logger.warning("Vault backend not yet implemented")
            return {}
        else:
            logger.error(f"Unknown backend: {backend}")
            return {}


# Create a singleton instance of the secrets manager
_secrets_manager = SecretsManager()


def get_secret(
    key: str, backend: Optional[Union[SecretsBackend, str]] = None
) -> Optional[str]:
    """Get a secret from the specified backend.

    Args:
    ----
        key: The key of the secret
        backend: The backend to use (defaults to the default backend)

    Returns:
    -------
        Optional[str]: The secret value, or None if not found

    """
    if isinstance(backend, str):
        try:
            backend = SecretsBackend(backend)
        except ValueError:
            logger.error(f"Invalid backend: {backend}")
            return None

    return _secrets_manager.get_secret(key, backend)


def set_secret(
    key: str, value: str, backend: Optional[Union[SecretsBackend, str]] = None
) -> bool:
    """Set a secret in the specified backend.

    Args:
    ----
        key: The key of the secret
        value: The value of the secret
        backend: The backend to use (defaults to the default backend)

    Returns:
    -------
        bool: True if the secret was set successfully, False otherwise

    """
    if isinstance(backend, str):
        try:
            backend = SecretsBackend(backend)
        except ValueError:
            logger.error(f"Invalid backend: {backend}")
            return False

    return _secrets_manager.set_secret(key, value, backend)


def delete_secret(
    key: str, backend: Optional[Union[SecretsBackend, str]] = None
) -> bool:
    """Delete a secret from the specified backend.

    Args:
    ----
        key: The key of the secret
        backend: The backend to use (defaults to the default backend)

    Returns:
    -------
        bool: True if the secret was deleted successfully, False otherwise

    """
    if isinstance(backend, str):
        try:
            backend = SecretsBackend(backend)
        except ValueError:
            logger.error(f"Invalid backend: {backend}")
            return False

    return _secrets_manager.delete_secret(key, backend)


def list_secrets(
    backend: Optional[Union[SecretsBackend, str]] = None,
) -> Dict[str, Any]:
    """List all secrets in the specified backend.

    Args:
    ----
        backend: The backend to use (defaults to the default backend)

    Returns:
    -------
        Dict[str, Any]: Dictionary of secrets

    """
    if isinstance(backend, str):
        try:
            backend = SecretsBackend(backend)
        except ValueError:
            logger.error(f"Invalid backend: {backend}")
            return {}

    return _secrets_manager.list_secrets(backend)
