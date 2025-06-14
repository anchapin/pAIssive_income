"""Mock memory class for ADK."""

from __future__ import annotations


class SimpleMemory:
    """Simple in-memory storage."""

    def __init__(self) -> None:
        """Initialize memory."""
        self.storage: dict[str, list[object]] = {}

    def store(self, key: str, value: object) -> None:
        """Store a value."""
        if key not in self.storage:
            self.storage[key] = []
        self.storage[key].append(value)

    def retrieve(self, key: str) -> list[object]:
        """Retrieve values for a key."""
        return self.storage.get(key, [])
