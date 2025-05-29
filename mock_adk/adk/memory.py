"""Mock memory class for ADK."""

from __future__ import annotations

from typing import Any # Keep Any for storage value and retrieve return
# Dict and List will be replaced


class SimpleMemory:
    """Simple in-memory storage."""

    def __init__(self) -> None:
        """Initialize memory."""
        self.storage: dict[str, list[Any]] = {}

    def store(self, key: str, value: Any) -> None:
        """Store a value."""
        if key not in self.storage:
            self.storage[key] = []
        self.storage[key].append(value)

    def retrieve(self, key: str) -> list[Any]:
        """Retrieve values for a key."""
        return self.storage.get(key, [])
