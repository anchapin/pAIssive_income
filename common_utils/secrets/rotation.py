"""
rotation - Module for common_utils/secrets.rotation.

This module provides utilities for rotating secrets.
"""

from __future__ import annotations

# Standard library imports
import datetime
import json
import os
from pathlib import Path

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
        rotation_file: str | None = None,
        secrets_backend: SecretsBackend | str | None = None,
    ) -> None:
        """
        Initialize the secret rotation utility.

        Args:
        ----
            rotation_file: Path to the rotation file
            secrets_backend: Backend to use for secrets (SecretsBackend enum, string, or None)

        """
        self.rotation_file = rotation_file or os.environ.get(
            "PAISSIVE_ROTATION_FILE", "secret_rotation.json"
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
        self.rotation_data: dict[str, dict] = {}
        self._load_rotation_data()
        logger.info("Secret rotation initialized with file: %s", self.rotation_file)

    def _load_rotation_data(self) -> None:
        """Load the rotation data from the file."""
        if self.rotation_file is None:
            logger.warning("No rotation file specified")
            return

        rotation_path = Path(self.rotation_file)
        if not rotation_path.exists():
            logger.warning("Rotation file %s not found", self.rotation_file)
            return

        try:
            with rotation_path.open(encoding="utf-8") as f:
                self.rotation_data = json.load(f)
            logger.debug("Loaded rotation data from %s", self.rotation_file)
        except Exception:
            logger.exception("Error loading rotation data")

    def _save_rotation_data(self) -> None:
        """Save the rotation data to the file."""
        if self.rotation_file is None:
            logger.warning("No rotation file specified")
            return

        try:
            rotation_path = Path(self.rotation_file)
            with rotation_path.open("w", encoding="utf-8") as f:
                json.dump(self.rotation_data, f, indent=2)
            logger.debug("Saved rotation data to %s", self.rotation_file)
        except Exception:
            logger.exception("Error saving rotation data")

    def schedule_rotation(
        self, key: str, interval_days: int, generator_func: str | None = None
    ) -> None:
        """
        Schedule a secret for rotation.

        Args:
        ----
            key: The key of the secret
            interval_days: The interval in days between rotations
            generator_func: The name of a function to generate a new secret value

        Raises:
        ------
            InvalidRotationIntervalError: If the interval is less than MIN_ROTATION_INTERVAL
                or greater than MAX_ROTATION_INTERVAL
        """
        # Define constants for validation
        MIN_ROTATION_INTERVAL = 1  # Minimum rotation interval in days
        MAX_ROTATION_INTERVAL = 365  # Maximum rotation interval in days

        # Validate the rotation interval
        if interval_days < MIN_ROTATION_INTERVAL:
            logger.error("Rotation interval %s is too small (minimum: %s)",
                        interval_days, MIN_ROTATION_INTERVAL)
            from common_utils.exceptions import InvalidRotationIntervalError
            raise InvalidRotationIntervalError(
                f"Rotation interval must be at least {MIN_ROTATION_INTERVAL} day(s)"
            )

        if interval_days > MAX_ROTATION_INTERVAL:
            logger.error("Rotation interval %s is too large (maximum: %s)",
                        interval_days, MAX_ROTATION_INTERVAL)
            from common_utils.exceptions import InvalidRotationIntervalError
            raise InvalidRotationIntervalError(
                f"Rotation interval must be at most {MAX_ROTATION_INTERVAL} days"
            )

        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        self.rotation_data[key] = {
            "last_rotated": now,
            "interval_days": interval_days,
            "generator_func": generator_func,
        }
        self._save_rotation_data()
        logger.info("Scheduled rotation for %s every %s days", key, interval_days)

    def get_secrets_due_for_rotation(self) -> list[str]:
        """
        Get a list of secrets that are due for rotation.

        Returns
        -------
            List[str]: List of secret keys due for rotation

        """
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        due_for_rotation = []

        for key, data in self.rotation_data.items():
            last_rotated = datetime.datetime.fromisoformat(data["last_rotated"])
            interval_days = data["interval_days"]
            next_rotation = last_rotated + datetime.timedelta(days=interval_days)

            if now >= next_rotation:
                due_for_rotation.append(key)

        return due_for_rotation

    def rotate_secret(self, key: str, new_value: str | None = None) -> bool:
        """
        Rotate a secret.

        Args:
        ----
            key: The key of the secret
            new_value: The new value for the secret (optional)

        Returns:
        -------
            bool: True if the secret was rotated, False otherwise

        """
        if key not in self.rotation_data:
            logger.warning("Secret %s not scheduled for rotation", key)
            return False

        # Get the current value
        current_value = get_secret(key, self.secrets_backend)
        if current_value is None:
            logger.warning("Secret %s not found", key)
            return False

        # Set the new value
        if new_value is None:
            # Use a simple default if no generator function is specified
            now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
            new_value = f"{current_value}_rotated_{now}"

        # Set the new value
        if not set_secret(key, new_value, self.secrets_backend):
            logger.error("Failed to set new value for %s", key)
            return False

        # Update the rotation data
        self.rotation_data[key]["last_rotated"] = datetime.datetime.now(
            tz=datetime.timezone.utc
        ).isoformat()
        self._save_rotation_data()
        logger.info("Rotated secret %s", key)
        return True

    def rotate_all_due(self) -> tuple[int, list[str]]:
        """
        Rotate all secrets that are due for rotation.

        Returns
        -------
            Tuple[int, List[str]]: Number of secrets rotated and list of keys

        """
        due_for_rotation = self.get_secrets_due_for_rotation()
        rotated = [key for key in due_for_rotation if self.rotate_secret(key)]
        return len(rotated), rotated
