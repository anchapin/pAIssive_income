"""file_backend - Module for common_utils/secrets.file_backend.

This module provides a file-based backend for secrets management.
"""

# Standard library imports
import os
from typing import Any, Dict, Optional

# Third-party imports
# Local imports
from common_utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


class FileBackend:
    """Backend for storing secrets in encrypted files."""

    def __init__(
        self,
        secrets_dir: Optional[str] = None,
        auth_material: Optional[str] = None,
    ):
        """Initialize the file backend.

        Args:
        ----
            secrets_dir: Directory to store secret files
            auth_material: Authentication material for encryption

        """
        self.secrets_dir = secrets_dir or os.environ.get(
            "PAISSIVE_SECRETS_DIR", ".paissive/secrets"
        )

        # Don't store the actual authentication material
        # Only store whether we have valid authentication
        self._has_auth = (auth_material is not None) or (
            "PAISSIVE_AUTH_KEY" in os.environ
        )

        # If we don't have authentication material, log a warning
        if not self._has_auth:
            logger.warning("No authentication material provided")

        # Ensure the secrets directory exists
        if self.secrets_dir:
            os.makedirs(self.secrets_dir, exist_ok=True)

            # Set secure permissions on the secrets directory
            try:
                # This will work on Unix-like systems
                if os.name == "posix":
                    os.chmod(self.secrets_dir, 0o700)  # rwx------
            except Exception as e:
                logger.warning(f"Could not set permissions on secrets directory: {e}")

        # Don't log the actual directory path as it might contain sensitive information
        logger.info("File backend initialized successfully")

    def get_secret(self, key: str) -> Optional[str]:
        """Get a secret from the file backend.

        Args:
        ----
            key: Key of the secret

        Returns:
        -------
            Optional[str]: The secret value

        Raises:
        ------
            NotImplementedError: The file backend is not currently supported

        """
        logger.warning("File backend not yet implemented")
        raise NotImplementedError("The file backend is not currently supported.")

    def set_secret(self, key: str, value: str) -> bool:
        """Set a secret in the file backend.

        Args:
        ----
            key: Key of the secret
            value: Value of the secret

        Returns:
        -------
            bool: True if the secret was set, False otherwise

        Raises:
        ------
            NotImplementedError: The file backend is not currently supported

        """
        logger.warning("File backend not yet implemented")
        raise NotImplementedError("The file backend is not currently supported.")

    def delete_secret(self, key: str) -> bool:
        """Delete a secret from the file backend.

        Args:
        ----
            key: Key of the secret

        Returns:
        -------
            bool: True if the secret was deleted, False otherwise

        Raises:
        ------
            NotImplementedError: The file backend is not currently supported

        """
        logger.warning("File backend not yet implemented")
        raise NotImplementedError("The file backend is not currently supported.")

    def list_secrets(self) -> Dict[str, Any]:
        """List all secrets in the file backend.

        Returns
        -------
            Dict[str, Any]: Dictionary of secrets

        Raises
        ------
            NotImplementedError: The file backend is not currently supported

        """
        logger.warning("File backend not yet implemented")
        raise NotImplementedError("The file backend is not currently supported.")
