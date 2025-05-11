"""rotation - Module for common_utils/secrets.rotation.

This module provides utilities for rotating secrets.
"""

# Standard library imports
import datetime
import json
import os
from typing import Optional

# Third-party imports
# Local imports
from common_utils.logging import get_logger

from .secrets_manager import SecretsBackend, get_secret, set_secret

# Initialize logger
logger = get_logger(__name__)


class SecretRotation:
    """Utility for rotating secrets."""

    def __init__(
        self,
        rotation_file: Optional[str] = None,
        secrets_backend: Optional[SecretsBackend] = None,
    ):
        """Initialize the secret rotation utility.

        Args:
        ----
            rotation_file: Path to the rotation file
            secrets_backend: Backend to use for secrets

        """
        self.rotation_file = rotation_file or os.environ.get(
            "PAISSIVE_ROTATION_FILE", "secret_rotation.json"
        )
        self.secrets_backend = secrets_backend or SecretsBackend.ENV
        self.rotation_data: dict[str, dict] = {}
        self._load_rotation_data()
        logger.info(f"Secret rotation initialized with file: {self.rotation_file}")

    def _load_rotation_data(self) -> None:
        """Load the rotation data from the file."""
        if self.rotation_file is None:
            logger.warning("No rotation file specified")
            return

        if not os.path.exists(self.rotation_file):
            logger.warning(f"Rotation file {self.rotation_file} not found")
            return

        try:
            with open(self.rotation_file, encoding="utf-8") as f:
                self.rotation_data = json.load(f)
            logger.debug(f"Loaded rotation data from {self.rotation_file}")
        except Exception:
            logger.exception("Error loading rotation data")

    def _save_rotation_data(self) -> None:
        """Save the rotation data to the file."""
        if self.rotation_file is None:
            logger.warning("No rotation file specified")
            return

        try:
            with open(self.rotation_file, "w", encoding="utf-8") as f:
                json.dump(self.rotation_data, f, indent=2)
            logger.debug(f"Saved rotation data to {self.rotation_file}")
        except Exception:
            logger.exception("Error saving rotation data")

    def schedule_rotation(
        self, key: str, interval_days: int, generator_func: Optional[str] = None
    ) -> None:
        """Schedule a secret for rotation.

        Args:
        ----
            key: The key of the secret
            interval_days: The interval in days between rotations
            generator_func: The name of a function to generate a new secret value

        """
        now = datetime.datetime.now().isoformat()
        self.rotation_data[key] = {
            "last_rotated": now,
            "interval_days": interval_days,
            "generator_func": generator_func,
        }
        self._save_rotation_data()
        logger.info(f"Scheduled rotation for {key} every {interval_days} days")

    def get_secrets_due_for_rotation(self) -> list[str]:
        """Get a list of secrets that are due for rotation.

        Returns
        -------
            List[str]: List of secret keys due for rotation

        """
        now = datetime.datetime.now()
        due_for_rotation = []

        for key, data in self.rotation_data.items():
            last_rotated = datetime.datetime.fromisoformat(data["last_rotated"])
            interval_days = data["interval_days"]
            next_rotation = last_rotated + datetime.timedelta(days=interval_days)

            if now >= next_rotation:
                due_for_rotation.append(key)

        return due_for_rotation

    def rotate_secret(self, key: str, new_value: Optional[str] = None) -> bool:
        """Rotate a secret.

        Args:
        ----
            key: The key of the secret
            new_value: The new value for the secret (optional)

        Returns:
        -------
            bool: True if the secret was rotated, False otherwise

        """
        if key not in self.rotation_data:
            logger.warning(f"Secret {key} not scheduled for rotation")
            return False

        # Get the current value
        current_value = get_secret(key, self.secrets_backend)
        if current_value is None:
            logger.warning(f"Secret {key} not found")
            return False

        # Set the new value
        if new_value is None:
            # Use a simple default if no generator function is specified
            new_value = f"{current_value}_rotated_{datetime.datetime.now().isoformat()}"

        # Set the new value
        if not set_secret(key, new_value, self.secrets_backend):
            logger.error(f"Failed to set new value for {key}")
            return False

        # Update the rotation data
        self.rotation_data[key]["last_rotated"] = datetime.datetime.now().isoformat()
        self._save_rotation_data()
        logger.info(f"Rotated secret {key}")
        return True

    def rotate_all_due(self) -> tuple[int, list[str]]:
        """Rotate all secrets that are due for rotation.

        Returns
        -------
            Tuple[int, List[str]]: Number of secrets rotated and list of keys

        """
        due_for_rotation = self.get_secrets_due_for_rotation()
        rotated = []

        for key in due_for_rotation:
            if self.rotate_secret(key):
                rotated.append(key)

        return len(rotated), rotated
