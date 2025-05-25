"""Mock memory class for ADK."""
from typing import Any, Dict, List


class SimpleMemory:
    """Simple in-memory storage."""
    
    def __init__(self) -> None:
        """Initialize memory."""
        self.storage: Dict[str, List[Any]] = {}
        
    def store(self, key: str, value: Any) -> None:
        """Store a value."""
        if key not in self.storage:
            self.storage[key] = []
        self.storage[key].append(value)
        
    def retrieve(self, key: str) -> List[Any]:
        """Retrieve values for a key."""
        return self.storage.get(key, [])
