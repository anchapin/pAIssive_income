"""
secrets_manager - Module for common_utils/secrets.secrets_manager.

This module provides a unified interface for managing secrets across different backends.
"""

from __future__ import annotations

# Standard library imports
import enum
import os
from typing import Any, Protocol

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

    @classmethod
    def from_string(cls, backend_str: str) -> SecretsBackend:
        """
        Create a SecretsBackend from a string.

        Args:
            backend_str: The string representation of the backend

        Returns:
            SecretsBackend: The corresponding SecretsBackend enum value

        Raises:
            ValueError: If the string does not match any backend

        """
        # Simply call the constructor directly
        # If it raises ValueError, let it propagate up
        return cls(backend_str)

    @classmethod
    def is_valid_backend(cls, backend_str: str) -> bool:
        """
        Check if a string is a valid backend.

        Args:
            backend_str: The string representation of the backend

        Returns:
            bool: True if the string is a valid backend, False otherwise

        """
        try:
            cls(backend_str)
        except ValueError:
            return False
        else:
            return True

    @classmethod
    def get_default(cls) -> SecretsBackend:
        """
        Get the default backend.

        Returns:
            SecretsBackend: The default backend (ENV)

        """
        # Return the enum value directly
        return cls.ENV  # type: ignore[return-value]


class SecretBackendProtocol(Protocol):
    """Protocol for secret backend implementations."""

    def get_secret(self) -> str | None:
        """Get a secret from the backend."""
        ...

    def set_secret(self) -> bool:
        """Set a secret in the backend."""
        ...

    def delete_secret(self) -> bool:
        """Delete a secret from the backend."""
        ...

    def list_secrets(self) -> dict[str, Any]:
        """List secrets in the backend."""
        ...


class SecretsManager:
    """Manager for handling secrets across different backends."""  # Define class variable for type checking

    default_backend: SecretsBackend

    def __init__(self, default_backend: SecretsBackend | str | None = None) -> None:
        """
        Initialize the secrets manager.

        Args:
        ----
            default_backend: The default backend to use for secrets

        """
        # Initialize with the default backend
        self.default_backend = SecretsBackend.get_default()

        # Determine the actual backend to use
        if default_backend is None:
            # Use ENV as default if none provided
            pass  # Keep the default ENV value
        elif isinstance(default_backend, SecretsBackend):
            # Use the provided backend directly
            self.default_backend = default_backend
        elif isinstance(default_backend, str):
            # Convert string to enum
            try:
                self.default_backend = SecretsBackend.from_string(default_backend)
            except ValueError:
                logger.warning("Invalid backend string provided, using ENV")
                # Keep the default ENV value
        else:
            # This branch should never be reached with proper type checking
            logger.warning("Invalid backend type provided, using ENV")
            # Keep the default ENV value

        # Now self.default_backend is guaranteed to be a SecretsBackend instance
        # Don't log the actual backend value as it might contain sensitive information
        logger.info("Secrets manager initialized with default backend")

    def _get_env_secret(self, key: str) -> str | None:
        """
        Get a secret from environment variables.

        Args:
            key: The key of the secret

        Returns:
            Optional[str]: The secret value, or None if not found

        """
        return os.environ.get(key) if key in os.environ else None

    def _get_file_secret(self, key: str) -> str | None:
        """
        Get a secret from the file backend.

        Args:
            key: The key of the secret

        Returns:
            Optional[str]: The secret value, or None if not found

        """
        try:
            from .file_backend import FileBackend

            file_backend = FileBackend()
            result: str | None = file_backend.get_secret(key)
        except NotImplementedError:
            logger.warning("Backend not yet fully implemented")
            return None
        else:
            return result

    def _get_memory_secret(self, _key: str) -> str | None:
        """
        Get a secret from the memory backend.

        Args:
            _key: The key of the secret (unused in current implementation)

        Returns:
            Optional[str]: The secret value, or None if not found

        """
        try:
            from .memory_backend import MemoryBackend

            memory_backend = MemoryBackend()
            # The memory backend get_secret method requires a key parameter
            result: str | None = memory_backend.get_secret(_key)
        except NotImplementedError:
            logger.warning("Backend not yet fully implemented")
            return None
        else:
            return result

    def _get_vault_secret(self, _key: str) -> str | None:
        """
        Get a secret from the vault backend.

        Args:
            _key: The key of the secret (unused in current implementation)

        Returns:
            Optional[str]: The secret value, or None if not found

        """
        try:
            from .vault_backend import VaultBackend

            vault_backend = VaultBackend()
            # The vault backend get_secret method requires a key parameter
            result: str | None = vault_backend.get_secret(_key)
        except NotImplementedError:
            logger.warning("Backend not yet fully implemented")
            return None
        else:
            return result

    def get_secret(self, key: str, backend: SecretsBackend | None = None) -> str | None:
        """
        Get a secret from the specified backend.

        Args:
        ----
            key: The key of the secret
            backend: The backend to use (defaults to the default backend)

        Returns:
        -------
            Optional[str]: The secret value, or None if not found

        """
        # Ensure backend is a SecretsBackend instance
        backend_enum: SecretsBackend  # Explicitly annotate the type

        if isinstance(backend, str):
            try:
                backend_enum = SecretsBackend.from_string(backend)
            except ValueError:
                # Don't log the actual backend value as it might contain sensitive information
                logger.exception("Invalid backend specified")
                return None
        elif isinstance(backend, SecretsBackend):
            backend_enum = backend
        else:
            # If backend is None, use default
            # Use the default_backend directly as it's already a SecretsBackend
            backend_enum = self.default_backend
        # Don't log the actual key name or backend as it might reveal sensitive information
        # backend_enum is guaranteed to be a SecretsBackend instance at this point
        logger.debug("Getting secret from backend")

        # Use the appropriate backend to get the secret
        if backend_enum == SecretsBackend.ENV:
            return self._get_env_secret(key)
        if backend_enum == SecretsBackend.FILE:
            return self._get_file_secret(key)
        if backend_enum == SecretsBackend.MEMORY:
            return self._get_memory_secret(key)
        if backend_enum == SecretsBackend.VAULT:
            return self._get_vault_secret(key)
        logger.error("Unknown backend specified")
        return None

    def _set_env_secret(self, key: str, value: str) -> bool:
        """
        Set a secret in the environment variables.

        Args:
            key: The key of the secret
            value: The value of the secret

        Returns:
            bool: True if the secret was set successfully

        """
        os.environ[key] = value
        return True

    def _set_backend_secret(
        self, _key: str, _value: str, backend_type: SecretsBackend
    ) -> bool:
        """
        Set a secret in a specific backend.

        Args:
            key: The key of the secret
            value: The value of the secret
            backend_type: The backend type to use

        Returns:
            bool: True if the secret was set successfully, False otherwise

        """
        try:
            # Import backends
            from .file_backend import FileBackend
            from .memory_backend import MemoryBackend
            from .vault_backend import VaultBackend

            # Create the appropriate backend instance
            if backend_type == SecretsBackend.FILE:
                file_backend = FileBackend()
                result: bool = file_backend.set_secret(_key, _value)
            elif backend_type == SecretsBackend.MEMORY:
                memory_backend = MemoryBackend()
                result = bool(memory_backend.set_secret(_key, _value))
            elif backend_type == SecretsBackend.VAULT:
                vault_backend = VaultBackend()
                result = bool(vault_backend.set_secret(_key, _value))
            else:
                # Don't log the actual backend type as it might contain sensitive information
                logger.error("Unsupported backend type")
                return False
        except NotImplementedError:
            # Don't log the actual backend type value as it might contain sensitive information
            logger.warning("Backend not yet fully implemented")
            return False
        except Exception:
            # Don't log the actual backend type value as it might contain sensitive information
            logger.exception("Error setting secret in backend")
            return False
        else:
            return result

    def set_secret(
        self, key: str, value: str, backend: SecretsBackend | None = None
    ) -> bool:
        """
        Set a secret in the specified backend.

        Args:
        ----
            key: The key of the secret
            value: The value of the secret
            backend: The backend to use (defaults to the default backend)

        Returns:
        -------
            bool: True if the secret was set successfully, False otherwise

        """
        # Ensure backend is a SecretsBackend instance
        backend_enum: SecretsBackend  # Explicitly annotate the type

        if isinstance(backend, str):
            try:
                backend_enum = SecretsBackend.from_string(backend)
            except ValueError:
                # Don't log the actual backend value as it might contain sensitive information
                logger.exception("Invalid backend specified")
                return False
        elif isinstance(backend, SecretsBackend):
            backend_enum = backend
        else:
            # If backend is None, use default
            # Use the default_backend directly as it's already a SecretsBackend
            backend_enum = self.default_backend
        # Don't log the actual key name or backend as it might reveal sensitive information
        # backend_enum is guaranteed to be a SecretsBackend instance at this point
        logger.debug("Setting secret in backend")

        if backend_enum == SecretsBackend.ENV:
            return self._set_env_secret(key, value)
        if backend_enum in (
            SecretsBackend.FILE,
            SecretsBackend.MEMORY,
            SecretsBackend.VAULT,
        ):
            return self._set_backend_secret(key, value, backend_enum)
        logger.error("Unknown backend specified")
        return False

    def _delete_env_secret(self, key: str) -> bool:
        """
        Delete a secret from environment variables.

        Args:
            key: The key of the secret

        Returns:
            bool: True if the secret was deleted successfully, False otherwise

        """
        if key in os.environ:
            del os.environ[key]
            return True
        return False

    def _delete_backend_secret(self, _key: str, backend_type: SecretsBackend) -> bool:
        """
        Delete a secret from a specific backend.

        Args:
            key: The key of the secret
            backend_type: The backend type to use

        Returns:
            bool: True if the secret was deleted successfully, False otherwise

        """
        try:
            # Import backends
            from .file_backend import FileBackend
            from .memory_backend import MemoryBackend
            from .vault_backend import VaultBackend

            # Create the appropriate backend instance
            if backend_type == SecretsBackend.FILE:
                file_backend = FileBackend()
                result: bool = file_backend.delete_secret(_key)
            elif backend_type == SecretsBackend.MEMORY:
                memory_backend = MemoryBackend()
                result = bool(memory_backend.delete_secret(_key))
            elif backend_type == SecretsBackend.VAULT:
                vault_backend = VaultBackend()
                result = bool(vault_backend.delete_secret(_key))
            else:
                # Don't log the actual backend type as it might contain sensitive information
                logger.error("Unsupported backend type")
                return False
        except NotImplementedError:
            # Don't log the actual backend type value as it might contain sensitive information
            logger.warning("Backend not yet fully implemented")
            return False
        except Exception:
            # Don't log the actual backend type value as it might contain sensitive information
            logger.exception("Error deleting secret from backend")
            return False
        else:
            return result

    def delete_secret(self, key: str, backend: SecretsBackend | None = None) -> bool:
        """
        Delete a secret from the specified backend.

        Args:
        ----
            key: The key of the secret
            backend: The backend to use (defaults to the default backend)

        Returns:
        -------
            bool: True if the secret was deleted successfully, False otherwise

        """
        # Ensure backend is a SecretsBackend instance
        backend_enum: SecretsBackend  # Explicitly annotate the type

        if isinstance(backend, str):
            try:
                backend_enum = SecretsBackend.from_string(backend)
            except ValueError:
                # Don't log the actual backend value as it might contain sensitive information
                logger.exception("Invalid backend specified")
                return False
        elif isinstance(backend, SecretsBackend):
            backend_enum = backend
        else:
            # If backend is None, use default
            # Use the default_backend directly as it's already a SecretsBackend
            backend_enum = self.default_backend
        # Don't log the actual key name or backend as it might reveal sensitive information
        # backend_enum is guaranteed to be a SecretsBackend instance at this point
        logger.debug("Deleting secret from backend")

        if backend_enum == SecretsBackend.ENV:
            return self._delete_env_secret(key)
        if backend_enum in (
            SecretsBackend.FILE,
            SecretsBackend.MEMORY,
            SecretsBackend.VAULT,
        ):
            return self._delete_backend_secret(key, backend_enum)
        logger.error("Unknown backend specified")
        return False

    def _list_env_secrets(self) -> dict[str, Any]:
        """
        List secrets from environment variables.

        Returns:
            dict[str, Any]: Dictionary of environment variables with sensitive information masked

        """
        # Import secure logging utilities with enhanced sensitive field patterns
        from common_utils.logging.secure_logging import (
            is_sensitive_key,
            mask_sensitive_data,
        )

        # Create a filtered and sanitized view of environment variables
        safe_env_vars: dict[str, Any] = {}

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
        for key in os.environ:
            # Skip environment variables that are clearly not secrets
            if key.startswith(
                (
                    "PATH",
                    "PYTHON",
                    "SYSTEM",
                    "OS_",
                    "COMPUTERNAME",
                    "USERNAME",
                )
            ):
                continue

            # Determine if this key potentially contains sensitive information
            is_sensitive = is_sensitive_key(key) or any(
                pattern in key.lower() for pattern in additional_sensitive_patterns
            )

            # Process the key based on sensitivity
            safe_env_vars = self._process_env_key(key, is_sensitive, safe_env_vars)

        # Apply final sanitization to catch any missed sensitive data
        masked_result = mask_sensitive_data(safe_env_vars)

        # Ensure we return a Dict[str, Any] as specified in the return type
        if isinstance(masked_result, dict):
            # mypy should recognize this is a dict after the isinstance check
            return masked_result
        return safe_env_vars  # Fallback to original if somehow not a dict

    def _process_env_key(
        self, key: str, is_sensitive: bool, safe_env_vars: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Process an environment variable key based on its sensitivity.

        Args:
            key: The environment variable key
            is_sensitive: Whether the key is sensitive
            safe_env_vars: Dictionary to update with the processed key

        Returns:
            dict[str, Any]: Updated dictionary with the processed key

        """
        if is_sensitive:
            # For highly sensitive keys, use consistent masking
            # This approach doesn't reveal any part of the original key
            high_risk_patterns = ["password", "secret", "token", "key", "credential"]
            if any(high_risk in key.lower() for high_risk in high_risk_patterns):
                # Don't include any part of the original key in the masked version
                # Create a hash-based key identifier
                masked_key = f"***SENSITIVE_KEY_{hash(key) % 10000:04d}***"
                safe_env_vars[masked_key] = "********"
            else:
                # For moderate risk, keep key but mask value
                safe_env_vars[key] = "********"
        else:
            # For regular environment variables, just indicate presence without revealing length
            safe_env_vars[key] = "<VALUE_PRESENT>"

        return safe_env_vars

    def _list_backend_secrets(self, backend_type: SecretsBackend) -> dict[str, Any]:
        """
        List secrets from a specific backend.

        Args:
            backend_type: The backend type to use

        Returns:
            dict[str, Any]: Dictionary of secrets with sensitive information masked

        """
        try:
            # Import backends
            from .file_backend import FileBackend
            from .memory_backend import MemoryBackend
            from .vault_backend import VaultBackend

            # Create the appropriate backend instance and get secrets
            if backend_type == SecretsBackend.FILE:
                file_backend = FileBackend()
                secrets = file_backend.list_secrets()
            elif backend_type == SecretsBackend.MEMORY:
                memory_backend = MemoryBackend()
                secrets = memory_backend.list_secrets()
            elif backend_type == SecretsBackend.VAULT:
                vault_backend = VaultBackend()
                secrets = vault_backend.list_secrets()
            else:
                # Don't log the actual backend type as it might contain sensitive information
                logger.error("Unsupported backend type")
                return {}

            # Ensure we sanitize the secrets before returning them
            sanitized_secrets = self._sanitize_secrets_dict(secrets)
            logger.debug("Sanitized secrets from backend")
            return sanitized_secrets

        except NotImplementedError:
            # Don't log the actual backend type value as it might contain sensitive information
            logger.warning("Backend not yet fully implemented")
            return {}
        except Exception:
            # Don't log the actual backend type value as it might contain sensitive information
            logger.exception("Error listing secrets from backend")
            return {}

    def list_secrets(self, backend: SecretsBackend | None = None) -> dict[str, Any]:
        """
        List all secrets in the specified backend.

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
        # Ensure backend is a SecretsBackend instance
        backend_enum: SecretsBackend  # Explicitly annotate the type

        if isinstance(backend, str):
            try:
                backend_enum = SecretsBackend.from_string(backend)
            except ValueError:
                # Don't log the actual backend value as it might contain sensitive information
                logger.exception("Invalid backend specified")
                return {}
        elif isinstance(backend, SecretsBackend):
            backend_enum = backend
        else:
            # If backend is None, use default
            # Use the default_backend directly as it's already a SecretsBackend
            backend_enum = self.default_backend
        # backend_enum is guaranteed to be a SecretsBackend instance at this point
        # Don't log the actual backend as it might reveal sensitive information
        logger.debug("Listing secrets from backend")

        if backend_enum == SecretsBackend.ENV:
            return self._list_env_secrets()
        if backend_enum in (
            SecretsBackend.FILE,
            SecretsBackend.MEMORY,
            SecretsBackend.VAULT,
        ):
            return self._list_backend_secrets(backend_enum)
        logger.error("Unknown backend specified")
        return {}

    def _sanitize_secrets_dict(
        self, secrets: dict[str, Any]
    ) -> dict[str, str | dict[str, Any]]:
        """
        Sanitize a dictionary of secrets to ensure no sensitive data is exposed.

        Args:
        ----
            secrets: Dictionary of secrets

        Returns:
        -------
            dict[str, str | dict[str, Any]]: Sanitized dictionary with masked sensitive values

        """
        if not secrets:
            return {}

        # Import secure logging utility
        from common_utils.logging.secure_logging import mask_sensitive_data

        # Create a sanitized copy
        safe_secrets: dict[str, str | dict[str, Any]] = {}

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

        # Apply additional masking for sensitive keys
        return mask_sensitive_data(safe_secrets)


# Create a singleton instance of the secrets manager
_secrets_manager = SecretsManager()


def get_secret(key: str, backend: SecretsBackend | str | None = None) -> str | None:
    """
    Get a secret from the specified backend.

    Args:
    ----
        key: The key of the secret
        backend: The backend to use (defaults to the default backend)

    Returns:
    -------
        str | None: The secret value, or None if not found

    """
    if isinstance(backend, str):
        try:
            backend = SecretsBackend.from_string(backend)
        except ValueError:
            # Don't log the actual backend value as it might contain sensitive information
            logger.exception("Invalid backend specified")
            return None

    return _secrets_manager.get_secret(key, backend)


def set_secret(
    key: str, value: str, backend: SecretsBackend | str | None = None
) -> bool:
    """
    Set a secret in the specified backend.

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
            backend = SecretsBackend.from_string(backend)
        except ValueError:
            # Don't log the actual backend value as it might contain sensitive information
            logger.exception("Invalid backend specified")
            return False

    return _secrets_manager.set_secret(key, value, backend)


def delete_secret(key: str, backend: SecretsBackend | str | None = None) -> bool:
    """
    Delete a secret from the specified backend.

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
            backend = SecretsBackend.from_string(backend)
        except ValueError:
            # Don't log the actual backend value as it might contain sensitive information
            logger.exception("Invalid backend specified")
            return False

    return _secrets_manager.delete_secret(key, backend)


def list_secrets(
    backend: SecretsBackend | str | None = None,
) -> dict[str, str | dict[str, Any]]:
    """
    List all secrets in the specified backend.

    Args:
    ----
        backend: The backend to use (defaults to the default backend)

    Returns:
    -------
        Dict[str, Any]: Dictionary of secrets

    """
    if isinstance(backend, str):
        try:
            backend = SecretsBackend.from_string(backend)
        except ValueError:
            # Don't log the actual backend value as it might contain sensitive information
            logger.exception("Invalid backend specified")
            return {}

    return _secrets_manager.list_secrets(backend)
