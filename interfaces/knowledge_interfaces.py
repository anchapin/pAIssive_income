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

from __future__ import annotations  # Already present, but good to ensure

import logging  # Added logging import
from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol

logger = logging.getLogger(__name__)  # Added module-level logger


class Mem0ClientProtocol(Protocol):
    """
    Protocol definition for mem0 client interface.

    This protocol defines the expected interface for mem0 clients,
    improving type safety and making the expected API explicit.
    """

    def search(
        self, query: str, user_id: str, **kwargs: str | int | bool | None
    ) -> list[dict[str, str | int | bool | None]]:
        """
        Search for memories based on query and user context.

        Args:
            query: The search query string
            user_id: Unique identifier for the user
            **kwargs: Additional search parameters

        Returns:
            List of memory results as dictionaries

        """
        ...

    def add(
        self,
        content: str | list[dict[str, str]],
        user_id: str,
        **kwargs: Any,
    ) -> Any:
        """
        Add new memory content.

        Args:
            content: Content to store (string or conversation messages)
            user_id: Unique identifier for the user
            **kwargs: Additional parameters (e.g., metadata)

        Returns:
            Result of the add operation

        """
        ...


class VectorClientProtocol(Protocol):
    """
    Protocol definition for vector database client interface.

    This protocol defines the expected interface for vector database clients,
    improving type safety and making the expected API explicit.
    """

    def query(
        self, query: str, user_id: str, **kwargs: str | int | bool | None
    ) -> list[dict[str, str | int | bool | None]]:
        """
        Query the vector database for relevant documents.

        Args:
            query: The search query string
            user_id: Unique identifier for the user
            **kwargs: Additional query parameters (e.g., limit, filters)

        Returns:
            List of relevant documents as dictionaries

        """
        ...

    def add(
        self, content: str, user_id: str, **kwargs: str | int | bool | None
    ) -> dict[str, str | int | bool | None] | str | None:
        """
        Add new content to the vector database.

        Args:
            content: Content to store
            user_id: Unique identifier for the user
            **kwargs: Additional parameters (e.g., metadata, embeddings)

        Returns:
            Result of the add operation

        """
        ...


class KnowledgeSource(ABC):
    """
    Abstract base class for a knowledge source (e.g., mem0, vector database).

    To add a new knowledge source, subclass this and implement all methods.
    """

    @abstractmethod
    def search(
        self, query: str, user_id: str, **kwargs: str | int | bool | None
    ) -> list[dict[str, str | int | bool | None]]:
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
    def add(
        self, content: str, user_id: str, **kwargs: str | int | bool | None
    ) -> dict[str, str | int | bool | None] | str | None:
        """
        Add new knowledge/content to the source.

        Args:
            content: The content to add.
            user_id: Unique identifier for the user or agent.
            kwargs: Additional parameters for source-specific add logic.

        Returns:
            Source-specific result or metadata.

        """

    def update(
        self, content_id: str, new_content: str, user_id: str, **kwargs: Any
    ) -> Any:
        """
        Update existing knowledge entry.

        Args:
            content_id: Identifier of content to update.
            new_content: Updated content.
            user_id: Unique identifier for the user or agent.
            kwargs: Additional parameters.

        Returns:
            Source-specific result or metadata.

        """
        msg = "Update not implemented for this source."
        raise NotImplementedError(msg)

    def delete(
        self, content_id: str, user_id: str, **kwargs: str | int | bool | None
    ) -> dict[str, str | int | bool | None] | str | None:
        """
        Delete an entry.

        Args:
            content_id: Identifier of content to delete.
            user_id: Unique identifier for the user or agent.
            kwargs: Additional parameters.

        Returns:
            Source-specific result or metadata.

        """
        msg = "Delete not implemented for this source."
        raise NotImplementedError(msg)


class Mem0KnowledgeSource(KnowledgeSource):
    """Concrete implementation of KnowledgeSource for mem0 (Memory API)."""

    def __init__(self, mem0_client: Mem0ClientProtocol) -> None:
        """
        Initialize Mem0KnowledgeSource.

        Args:
            mem0_client: Initialized client for mem0's Memory API that implements Mem0ClientProtocol.

        """
        self.mem0_client = mem0_client

    def search(
        self, query: str, user_id: str, **kwargs: str | int | bool | None
    ) -> list[dict[str, str | int | bool | None]]:
        """Search mem0 for relevant memories."""
        try:
            return self.mem0_client.search(query, user_id, **kwargs)
        except Exception:
            logger.exception("Error searching mem0 memories")
            return []

    def add(
        self, content: str, user_id: str, **kwargs: str | int | bool | None
    ) -> dict[str, str | int | bool | None] | str | None:
        """Add new content to mem0."""
        try:
            return self.mem0_client.add(content, user_id, **kwargs)
        except Exception:
            logger.exception("Error adding content to mem0")
            return {"source": "mem0", "status": "error", "content": content}


class VectorRAGKnowledgeSource(KnowledgeSource):
    """Concrete implementation of KnowledgeSource for vector database RAG (e.g., ChromaDB)."""

    def __init__(self, vector_client: VectorClientProtocol) -> None:
        """
        Initialize VectorRAGKnowledgeSource.

        Args:
            vector_client: Initialized vector DB client (e.g., ChromaDB) that implements VectorClientProtocol.

        """
        self.vector_client = vector_client

    def search(
        self, query: str, user_id: str, **kwargs: str | int | bool | None
    ) -> list[dict[str, str | int | bool | None]]:
        """Search vector DB for relevant documents."""
        try:
            return self.vector_client.query(query, user_id, **kwargs)
        except Exception:
            logger.exception("Error searching vector database")
            return []

    def add(
        self, content: str, user_id: str, **kwargs: str | int | bool | None
    ) -> dict[str, str | int | bool | None] | str | None:
        """Add new content to vector DB."""
        try:
            return self.vector_client.add(content, user_id, **kwargs)
        except Exception:
            logger.exception("Error adding content to vector database")
            return {"source": "vector_rag", "status": "error", "content": content}


class KnowledgeStrategy(Enum):
    """Enum for strategy options in KnowledgeIntegrationLayer."""

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
        sources: list[KnowledgeSource],
        strategy: KnowledgeStrategy = KnowledgeStrategy.FALLBACK,
    ) -> None:
        """
        Initialize KnowledgeIntegrationLayer.

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
            except ValueError as e:
                msg = f"Unknown integration strategy: {strategy}"
                raise ValueError(msg) from e
        elif isinstance(strategy, KnowledgeStrategy):
            self.strategy = strategy
        else:
            msg = f"Invalid strategy type: {type(strategy)}"
            raise TypeError(msg)

    def search(
        self, query: str, user_id: str, **kwargs: str | int | bool | None
    ) -> list[dict[str, str | int | bool | None]]:
        """Search using the configured integration strategy."""
        if self.strategy == KnowledgeStrategy.FALLBACK:
            for source in self.sources:
                results = source.search(query, user_id, **kwargs)
                if results:
                    return results
            return []
        if self.strategy == KnowledgeStrategy.AGGREGATE:
            aggregated: list[dict[str, str | int | bool | None]] = []
            for source in self.sources:
                aggregated.extend(source.search(query, user_id, **kwargs))
            return aggregated
        msg = f"Unknown integration strategy: {self.strategy}"
        raise ValueError(msg)

    def add(
        self, content: str, user_id: str, **kwargs: str | int | bool | None
    ) -> list[dict[str, str | int | bool | None] | str | None]:
        """Add content to all sources."""
        return [source.add(content, user_id, **kwargs) for source in self.sources]
