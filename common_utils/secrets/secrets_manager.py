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

# Import backends lazily to avoid circular imports
# These will be imported when needed


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
        # Don't log the actual key name as it might reveal sensitive information
        logger.debug(f"Getting secret from {backend.value} backend")

        if backend == SecretsBackend.ENV:
            return os.environ.get(key)
        elif backend == SecretsBackend.FILE:
            try:
                from .file_backend import FileBackend

                file_backend = FileBackend()
                return file_backend.get_secret(key)
            except NotImplementedError:
                logger.warning("File backend not yet fully implemented")
                return None
        elif backend == SecretsBackend.MEMORY:
            try:
                from .memory_backend import MemoryBackend

                memory_backend = MemoryBackend()
                return memory_backend.get_secret(key)
            except NotImplementedError:
                logger.warning("Memory backend not yet fully implemented")
                return None
        elif backend == SecretsBackend.VAULT:
            try:
                from .vault_backend import VaultBackend

                vault_backend = VaultBackend()
                return vault_backend.get_secret(key)
            except NotImplementedError:
                logger.warning("Vault backend not yet fully implemented")
                return None
        else:
            logger.error("Unknown backend specified")
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
        # Don't log the actual key name as it might reveal sensitive information
        logger.debug(f"Setting secret in {backend.value} backend")

        if backend == SecretsBackend.ENV:
            os.environ[key] = value
            return True
        elif backend == SecretsBackend.FILE:
            try:
                from .file_backend import FileBackend

                file_backend = FileBackend()
                return file_backend.set_secret(key, value)
            except NotImplementedError:
                logger.warning("File backend not yet fully implemented")
                return False
        elif backend == SecretsBackend.MEMORY:
            try:
                from .memory_backend import MemoryBackend

                memory_backend = MemoryBackend()
                return memory_backend.set_secret(key, value)
            except NotImplementedError:
                logger.warning("Memory backend not yet fully implemented")
                return False
        elif backend == SecretsBackend.VAULT:
            try:
                from .vault_backend import VaultBackend

                vault_backend = VaultBackend()
                return vault_backend.set_secret(key, value)
            except NotImplementedError:
                logger.warning("Vault backend not yet fully implemented")
                return False
        else:
            logger.error("Unknown backend specified")
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
        # Don't log the actual key name as it might reveal sensitive information
        logger.debug(f"Deleting secret from {backend.value} backend")

        if backend == SecretsBackend.ENV:
            if key in os.environ:
                del os.environ[key]
                return True
            return False
        elif backend == SecretsBackend.FILE:
            try:
                from .file_backend import FileBackend

                file_backend = FileBackend()
                return file_backend.delete_secret(key)
            except NotImplementedError:
                logger.warning("File backend not yet fully implemented")
                return False
        elif backend == SecretsBackend.MEMORY:
            try:
                from .memory_backend import MemoryBackend

                memory_backend = MemoryBackend()
                return memory_backend.delete_secret(key)
            except NotImplementedError:
                logger.warning("Memory backend not yet fully implemented")
                return False
        elif backend == SecretsBackend.VAULT:
            try:
                from .vault_backend import VaultBackend

                vault_backend = VaultBackend()
                return vault_backend.delete_secret(key)
            except NotImplementedError:
                logger.warning("Vault backend not yet fully implemented")
                return False
        else:
            logger.error("Unknown backend specified")
            return False

    def list_secrets(self, backend: Optional[SecretsBackend] = None) -> Dict[str, Any]:
        """List all secrets in the specified backend.

        Args:
        ----
            backend: The backend to use (defaults to the default backend)

        Returns:
        -------
            Dict[str, Any]: Dictionary of secrets with sensitive information masked

        Security:
        --------
            This method never returns actual secret values, only metadata about secrets
            such as key names (when safe) and an indication of their presence.

        """
        backend = backend or self.default_backend
        logger.debug(f"Listing secrets from {backend.value} backend")

        if backend == SecretsBackend.ENV:
            # Import secure logging utilities with enhanced sensitive field patterns
            from common_utils.logging.secure_logging import (
                is_sensitive_key,
                mask_sensitive_data,
            )

            # Create a filtered and sanitized view of environment variables
            safe_env_vars: Dict[str, Any] = {}

            # Define additional patterns to catch more sensitive content
            additional_sensitive_patterns = [
                "token",
                "secret",
                "password",
                "credential",
                "auth",
                "key",
                "cert",
                "private",
                "ssh",
                "access",
                "api",
                "security",
            ]

            # Process each environment variable
            for key, _ in os.environ.items():
                # Skip environment variables that are clearly not secrets
                if key.startswith(
                    ("PATH", "PYTHON", "SYSTEM", "OS_", "COMPUTERNAME", "USERNAME")
                ):
                    continue

                # Determine if this key potentially contains sensitive information
                is_sensitive = is_sensitive_key(key) or any(
                    pattern in key.lower() for pattern in additional_sensitive_patterns
                )

                # For sensitive keys, mask both key and value appropriately
                if is_sensitive:
                    # For highly sensitive keys, use consistent masking
                    # that doesn't reveal any part of the key
                    if any(
                        high_risk in key.lower()
                        for high_risk in [
                            "password",
                            "secret",
                            "token",
                            "key",
                            "credential",
                        ]
                    ):
                        # Don't include any part of the original key
                        # in the masked version
                        masked_key = f"***SENSITIVE_KEY_{hash(key) % 10000:04d}***"
                        safe_env_vars[masked_key] = "********"
                    else:
                        # For moderate risk, keep key but mask value
                        safe_env_vars[key] = "********"
                else:
                    # For regular environment variables, just indicate presence
                    # without revealing length
                    safe_env_vars[key] = "<VALUE_PRESENT>"

            # Apply final sanitization to catch any missed sensitive data
            masked_result = mask_sensitive_data(safe_env_vars)
            # Ensure we return a Dict[str, Any] as specified in the return type
            if isinstance(masked_result, dict):
                # mypy should recognize this is a dict after the isinstance check
                return masked_result
            return safe_env_vars  # Fallback to original if somehow not a dict
        elif backend == SecretsBackend.FILE:
            try:
                from .file_backend import FileBackend

                file_backend = FileBackend()
                # Ensure the returned secrets are properly sanitized
                secrets = file_backend.list_secrets()
                sanitized_secrets = self._sanitize_secrets_dict(secrets)
                return sanitized_secrets
            except NotImplementedError:
                logger.warning("File backend not yet fully implemented")
                return {}
        elif backend == SecretsBackend.MEMORY:
            try:
                from .memory_backend import MemoryBackend

                memory_backend = MemoryBackend()
                # Ensure the returned secrets are properly sanitized
                secrets = memory_backend.list_secrets()
                sanitized_secrets = self._sanitize_secrets_dict(secrets)
                return sanitized_secrets
            except NotImplementedError:
                logger.warning("Memory backend not yet fully implemented")
                return {}
        elif backend == SecretsBackend.VAULT:
            try:
                from .vault_backend import VaultBackend

                vault_backend = VaultBackend()
                # Ensure the returned secrets are properly sanitized
                secrets = vault_backend.list_secrets()
                sanitized_secrets = self._sanitize_secrets_dict(secrets)
                return sanitized_secrets
            except NotImplementedError:
                logger.warning("Vault backend not yet fully implemented")
                return {}
        else:
            logger.error("Unknown backend specified")
            return {}

    def _sanitize_secrets_dict(self, secrets: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize a dictionary of secrets to ensure no sensitive data is exposed.

        Args:
        ----
            secrets: Dictionary of secrets

        Returns:
        -------
            Dict[str, Any]: Sanitized dictionary with masked sensitive values

        """
        if not secrets:
            return {}

        # Import secure logging utility

        # Create a sanitized copy
        safe_secrets: Dict[str, Any] = {}

        for key, value in secrets.items():
            if isinstance(value, str):
                # Always mask the actual value
                safe_secrets[key] = "********"
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                safe_secrets[key] = self._sanitize_secrets_dict(value)
            else:
                # For non-string, non-dict values, convert to string and mask
                safe_secrets[key] = "********"

        return safe_secrets


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
            logger.error("Invalid backend specified")
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
            logger.error("Invalid backend specified")
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
            logger.error("Invalid backend specified")
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
            logger.error("Invalid backend specified")
            return {}

    return _secrets_manager.list_secrets(backend)
