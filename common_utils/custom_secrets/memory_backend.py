"""
memory_backend - Module for common_utils/secrets.memory_backend.

This module provides an in-memory backend for secrets management, primarily for testing.
"""

from __future__ import annotations

# Standard library imports
from typing import Any

# Third-party imports
# Local imports
from common_utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


class MemoryBackend:
    """Backend for storing secrets in memory (for testing)."""

    def __init__(self) -> None:
        """Initialize the memory backend."""
        self.secrets: dict[str, str] = {}
        logger.info("Memory backend initialized")

    def _mask_key_for_logging(self, key: str) -> str:
        """
        Mask a key for logging to avoid exposing sensitive information.

        Args:
        ----
            key: The key to mask

        Returns:
        -------
            str: The masked key

        """
        # Constants for masking logic
        long_key_threshold = 8
        short_key_threshold = 3
        visible_chars = 3

        if not key:
            return "[empty]"

        # If key is longer than threshold, show first and last few characters
        if len(key) > long_key_threshold:
            return f"{key[:visible_chars]}...{key[-visible_chars:]}"
        # Otherwise, just replace middle characters with *
        if len(key) > short_key_threshold:
            return f"{key[0]}{'*' * (len(key) - 2)}{key[-1]}"
        # For very short keys, just use ***
        return "***"

    def get_secret(self, key: str) -> str | None:
        """
        Get a secret from memory.

        Args:
        ----
            key: Key of the secret

        Returns:
        -------
            str | None: The secret value

        Raises:
        ------
            NotImplementedError: The memory backend is not currently supported

        """
        # Don't log any information about the key, even masked versions
        # Use generic logging without exposing any sensitive information
        logger.warning(
            "Memory backend not yet implemented", extra={"operation": "get_secret"}
        )
        # Use key in a no-op to avoid unused argument warning
        if key:  # This prevents the unused argument warning
            pass
        error_msg = "The memory backend is not currently supported."
        raise NotImplementedError(error_msg)

    def set_secret(self, key: str, value: str) -> bool:
        """
        Set a secret in memory.

        Args:
        ----
            key: Key of the secret
            value: Value of the secret

        Returns:
        -------
            bool: True if the secret was set, False otherwise

        Raises:
        ------
            NotImplementedError: The memory backend is not currently supported

        """
        # Don't log any information about the key or value, even masked versions
        # Use generic logging without exposing any sensitive information
        logger.warning(
            "Memory backend not yet implemented", extra={"operation": "set_secret"}
        )
        # Use key and value in a no-op to avoid unused argument warning
        # Don't log the key or value, even in debug logs
        if key and value:  # This prevents the unused argument warning
            pass
        error_msg = "The memory backend is not currently supported."
        raise NotImplementedError(error_msg)

    def delete_secret(self, key: str) -> bool:
        """
        Delete a secret from memory.

        Args:
        ----
            key: Key of the secret

        Returns:
        -------
            bool: True if the secret was deleted, False otherwise

        Raises:
        ------
            NotImplementedError: The memory backend is not currently supported

        """
        # Don't log any information about the key, even masked versions
        # Use generic logging without exposing any sensitive information
        logger.warning(
            "Memory backend not yet implemented", extra={"operation": "delete_secret"}
        )
        # Use key in a no-op to avoid unused argument warning
        if key:  # This prevents the unused argument warning
            pass
        error_msg = "The memory backend is not currently supported."
        raise NotImplementedError(error_msg)

    def list_secrets(self) -> dict[str, Any]:
        """
        List all secrets in memory.

        Returns
        -------
            Dict[str, Any]: Dictionary of secrets

        Raises
        ------
            NotImplementedError: The memory backend is not currently supported

        """
        # Use structured logging without exposing any sensitive information
        logger.warning(
            "Memory backend not yet implemented", extra={"operation": "list_secrets"}
        )
        error_msg = "The memory backend is not currently supported."
        raise NotImplementedError(error_msg)
