"""Mock mem0 module."""
__version__ = "0.1.100"

class Memory:
    def __init__(self, config=None):
        self.config = config or {}
        self.storage = {}
    
    def add(self, text, user_id="default", **kwargs):
        memory_id = f"mock-memory-{len(self.storage)}"
        self.storage[memory_id] = {"text": text, "user_id": user_id, **kwargs}
        return {"id": memory_id}
    
    def search(self, query, user_id="default", **kwargs):
        return [
            {"id": "mock-1", "text": f"Mock memory result for: {query}", "score": 0.9},
            {"id": "mock-2", "text": f"Another mock result for: {query}", "score": 0.8}
        ]
    
    def get(self, memory_id):
        return self.storage.get(memory_id)
    
    def delete(self, memory_id):
        return self.storage.pop(memory_id, None) is not None
