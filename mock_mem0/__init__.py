"""
Mock mem0ai module for CI environments.
Provides mock implementations of mem0ai classes to prevent import errors.
"""

__version__ = "0.1.100"

import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class MockMemory:
    """Mock implementation of mem0ai.Memory."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize mock memory."""
        self.config = config or {}
        logger.info("Initialized mock mem0ai.Memory")

    def add(
        self,
        content: Union[str, list[str]],
        user_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs
    ) -> dict[str, Any]:
        """Mock add method."""
        logger.info(f"Mock mem0 add: {str(content)[:50]}...")
        return {
            "id": "mock-memory-id",
            "content": content,
            "user_id": user_id,
            "metadata": metadata or {},
            "status": "success"
        }

    def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10,
        **kwargs
    ) -> list[dict[str, Any]]:
        """Mock search method."""
        logger.info(f"Mock mem0 search: {query[:50]}...")
        return [
            {
                "id": "mock-result-1",
                "content": f"Mock memory result for query: {query}",
                "score": 0.95,
                "metadata": {},
                "user_id": user_id
            }
        ]

    def get(
        self,
        memory_id: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Optional[dict[str, Any]]:
        """Mock get method."""
        logger.info(f"Mock mem0 get: {memory_id}")
        return {
            "id": memory_id,
            "content": f"Mock memory content for ID: {memory_id}",
            "metadata": {},
            "user_id": user_id
        }

    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs
    ) -> dict[str, Any]:
        """Mock update method."""
        logger.info(f"Mock mem0 update: {memory_id}")
        return {
            "id": memory_id,
            "content": content,
            "metadata": metadata or {},
            "status": "updated"
        }

    def delete(
        self,
        memory_id: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> dict[str, Any]:
        """Mock delete method."""
        logger.info(f"Mock mem0 delete: {memory_id}")
        return {
            "id": memory_id,
            "status": "deleted"
        }

    def get_all(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        **kwargs
    ) -> list[dict[str, Any]]:
        """Mock get_all method."""
        logger.info(f"Mock mem0 get_all for user: {user_id}")
        return [
            {
                "id": "mock-memory-1",
                "content": "Mock memory 1",
                "metadata": {},
                "user_id": user_id
            },
            {
                "id": "mock-memory-2",
                "content": "Mock memory 2",
                "metadata": {},
                "user_id": user_id
            }
        ]

    def reset(self, user_id: Optional[str] = None, **kwargs) -> dict[str, Any]:
        """Mock reset method."""
        logger.info(f"Mock mem0 reset for user: {user_id}")
        return {"status": "reset", "user_id": user_id}


# Export the main classes
Memory = MockMemory

# For backward compatibility
class MemoryClient(MockMemory):
    """Alias for MockMemory."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize MemoryClient with same interface as MockMemory."""
        super().__init__(config)


class Client(MockMemory):
    """Another alias for MockMemory for different import patterns."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize Client with same interface as MockMemory."""
        super().__init__(config)



# Mock configuration classes
class Config:
    """Mock configuration class."""

    def __init__(self, **kwargs):
        self.config = kwargs
        logger.info("Initialized mock mem0ai.Config")


# Mock embedding classes
class EmbeddingModel:
    """Mock embedding model class."""

    def __init__(self, model_name: str = "mock-embedding-model"):
        self.model_name = model_name
        logger.info(f"Initialized mock embedding model: {model_name}")

    def embed(self, text: str) -> list[float]:
        """Mock embedding method."""
        # Return a mock embedding vector
        return [0.1] * 384  # Mock 384-dimensional embedding


# Mock vector store classes
class VectorStore:
    """Mock vector store class."""

    def __init__(self, **kwargs):
        self.config = kwargs
        logger.info("Initialized mock mem0ai.VectorStore")


# Mock LLM classes
class LLM:
    """Mock LLM class."""

    def __init__(self, **kwargs):
        self.config = kwargs
        logger.info("Initialized mock mem0ai.LLM")


# Export all mock classes
__all__ = [
    "Client",
    "Config",
    "EmbeddingModel",
    "LLM",
    "Memory",
    "MemoryClient",
    "MockMemory",
    "VectorStore",
    "__version__"
]

logger.info("Mock mem0ai module loaded successfully")
