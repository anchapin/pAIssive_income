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
        logger.warning("Memory backend not yet implemented for key: %s", key)
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
        logger.warning("Memory backend not yet implemented for key: %s", key)
        # Use value in a no-op to avoid unused argument warning
        if value:
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
        logger.warning("Memory backend not yet implemented for key: %s", key)
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
        logger.warning("Memory backend not yet implemented")
        error_msg = "The memory backend is not currently supported."
        raise NotImplementedError(error_msg)
