"""
Unified integration layer for agent retrieval from multiple knowledge sources.

Usage Example:
---------------
from interfaces.knowledge_interfaces import (
    Mem0KnowledgeSource,
    VectorRAGKnowledgeSource,
    KnowledgeIntegrationLayer,
)

# Stub/mock clients for demo purposes
class DummyMem0Client:
    def search(self, query, user_id, **kwargs):
        return [{"source": "mem0", "content": f"dummy mem0 for '{query}'"}]
    def add(self, content, user_id, **kwargs):
        return {"status": "added", "content": content}

class DummyVectorClient:
    def query(self, query, user_id, **kwargs):
        return [{"source": "vector_rag", "content": f"dummy vector for '{query}'"}]
    def add(self, content, user_id, **kwargs):
        return {"status": "added", "content": content}

mem0_source = Mem0KnowledgeSource(DummyMem0Client())
vector_rag_source = VectorRAGKnowledgeSource(DummyVectorClient())

# Fallback strategy: returns from mem0 if available, otherwise from vector_rag
integration_fallback = KnowledgeIntegrationLayer(
    sources=[mem0_source, vector_rag_source],
    strategy=KnowledgeStrategy.FALLBACK
)
results_fallback = integration_fallback.search("your query here", user_id="user123")

# Aggregation strategy: combines results from all sources
integration_aggregate = KnowledgeIntegrationLayer(
    sources=[mem0_source, vector_rag_source],
    strategy=KnowledgeStrategy.AGGREGATE
)
results_aggregate = integration_aggregate.search("your query here", user_id="user123")

Provides:
- Abstract base class (KnowledgeSource) for knowledge sources.
- Concrete implementations for Mem0 and Vector RAG (e.g., ChromaDB).
- KnowledgeIntegrationLayer that handles fallback and aggregation logic.
- Extensible and decoupled design.

KnowledgeIntegrationLayer uses the KnowledgeStrategy Enum for setting the strategy,
making it robust and type-safe.

Note:
- This code stubs out Mem0 and ChromaDB initializations; see actual integration guides for details.
- No code references files or directories in .gitignore.

"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List


class KnowledgeSource(ABC):
    """
    Abstract base class for a knowledge source (e.g., mem0, vector database).
    To add a new knowledge source, subclass this and implement all methods.
    """

    @abstractmethod
    def search(self, query: str, user_id: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for relevant information given a query and user context.

        Args:
            query: The search string.
            user_id: Unique identifier for the user or agent.
            kwargs: Additional parameters for source-specific queries.

        Returns:
            A list of dictionaries with search results.

        """

    @abstractmethod
    def add(self, content: str, user_id: str, **kwargs) -> Any:
        """
        Add new knowledge/content to the source.

        Args:
            content: The content to add.
            user_id: Unique identifier for the user or agent.
            kwargs: Additional parameters for source-specific add logic.

        Returns:
            Source-specific result or metadata.

        """

    def update(self, content_id: str, new_content: str, user_id: str, **kwargs) -> Any:
        """
        Optionally update existing knowledge entry.

        Args:
            content_id: Identifier of content to update.
            new_content: Updated content.
            user_id: Unique identifier for the user or agent.
            kwargs: Additional parameters.

        Returns:
            Source-specific result or metadata.

        """
        raise NotImplementedError("Update not implemented for this source.")

    def delete(self, content_id: str, user_id: str, **kwargs) -> Any:
        """
        Optionally delete an entry.

        Args:
            content_id: Identifier of content to delete.
            user_id: Unique identifier for the user or agent.
            kwargs: Additional parameters.

        Returns:
            Source-specific result or metadata.

        """
        raise NotImplementedError("Delete not implemented for this source.")


class Mem0KnowledgeSource(KnowledgeSource):
    """
    Concrete implementation of KnowledgeSource for mem0 (Memory API).
    """

    def __init__(self, mem0_client: Any):
        """
        Args:
            mem0_client: Initialized client for mem0's Memory API.

        """
        self.mem0_client = mem0_client  # Stub: Replace with actual mem0 client

    def search(self, query: str, user_id: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search mem0 for relevant memories.
        """
        # Stub: Replace with actual call to mem0's Memory API
        # Example:
        # return self.mem0_client.search(query, user_id, **kwargs)
        return [{"source": "mem0", "content": f"Stub memory for '{query}'"}]

    def add(self, content: str, user_id: str, **kwargs) -> Any:
        """
        Add new content to mem0.
        """
        # Stub: Replace with actual call to mem0's add API
        # Example:
        # return self.mem0_client.add(content, user_id, **kwargs)
        return {"source": "mem0", "status": "added", "content": content}


class VectorRAGKnowledgeSource(KnowledgeSource):
    """
    Concrete implementation of KnowledgeSource for vector database RAG (e.g., ChromaDB).
    """

    def __init__(self, vector_client: Any):
        """
        Args:
            vector_client: Initialized vector DB client (e.g., ChromaDB).

        """
        self.vector_client = vector_client  # Stub: Replace with actual vector DB client

    def search(self, query: str, user_id: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search vector DB for relevant documents.
        """
        # Stub: Replace with actual vector DB search
        # Example:
        # return self.vector_client.query(query, user_id, **kwargs)
        return [{"source": "vector_rag", "content": f"Stub vector match for '{query}'"}]

    def add(self, content: str, user_id: str, **kwargs) -> Any:
        """
        Add new content to vector DB.
        """
        # Stub: Replace with actual vector DB add
        # Example:
        # return self.vector_client.add(content, user_id, **kwargs)
        return {"source": "vector_rag", "status": "added", "content": content}


class KnowledgeStrategy(Enum):
    """
    Enum for strategy options in KnowledgeIntegrationLayer.
    """

    FALLBACK = "fallback"
    AGGREGATE = "aggregate"


class KnowledgeIntegrationLayer:
    """
    Aggregates/cascades calls to multiple knowledge sources, with options for fallback or aggregation logic.

    Example usage:
        mem0_source = Mem0KnowledgeSource(mem0_client)
        rag_source = VectorRAGKnowledgeSource(vector_client)
        integration = KnowledgeIntegrationLayer([mem0_source, rag_source], strategy=KnowledgeStrategy.FALLBACK)
    """

    def __init__(
        self,
        sources: List[KnowledgeSource],
        strategy: "KnowledgeStrategy" = KnowledgeStrategy.FALLBACK,
    ):
        """
        Args:
            sources: List of KnowledgeSource implementations.
            strategy: Aggregation logic. One of:
                - KnowledgeStrategy.FALLBACK: Try sources in order, return first with results.
                - KnowledgeStrategy.AGGREGATE: Query all sources and merge results.

        """
        self.sources = sources
        if isinstance(strategy, str):
            # Accept string for backward compatibility, but prefer Enum usage
            try:
                self.strategy = KnowledgeStrategy(strategy.lower())
            except ValueError:
                raise ValueError(f"Unknown integration strategy: {strategy}")
        elif isinstance(strategy, KnowledgeStrategy):
            self.strategy = strategy
        else:
            raise TypeError(f"Invalid strategy type: {type(strategy)}")

    def search(self, query: str, user_id: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search using the configured integration strategy.

        Returns:
            List of search results (may be merged across sources).

        """
        if self.strategy == KnowledgeStrategy.FALLBACK:
            for source in self.sources:
                results = source.search(query, user_id, **kwargs)
                if results:
                    return results
            return []
        if self.strategy == KnowledgeStrategy.AGGREGATE:
            aggregated: List[Dict[str, Any]] = []
            for source in self.sources:
                aggregated.extend(source.search(query, user_id, **kwargs))
            return aggregated
        raise ValueError(f"Unknown integration strategy: {self.strategy}")

    def add(self, content: str, user_id: str, **kwargs) -> List[Any]:
        """
        Add content to all sources.

        Returns:
            List of source-specific add results.

        """
        results = []
        for source in self.sources:
            results.append(source.add(content, user_id, **kwargs))
        return results

    # Optionally implement update/delete as integration logic demands

    # Extensibility notes:
    # - To add a new knowledge source, create a subclass of KnowledgeSource and add it to the sources list.
    # - To add new integration strategies, extend logic in search/add/etc.
