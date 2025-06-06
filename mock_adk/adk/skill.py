"""Mock skill class for ADK."""

from __future__ import annotations

from typing import Any # Retain Any if it's still used for the return type


class Skill:
    """Base skill class."""

    def run(self, *args: object, **kwargs: object) -> Any:
        """Execute the skill. Override in subclasses."""
