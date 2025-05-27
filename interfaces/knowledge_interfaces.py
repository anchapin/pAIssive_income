"""
Knowledge interfaces for integrating multiple knowledge sources.

This module provides abstract base classes and concrete implementations
for integrating various knowledge sources like mem0 and vector databases.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class KnowledgeStrategy(Enum):
    """Strategy for combining results from multiple knowledge sources."""

    FALLBACK = "fallback"
    AGGREGATE = "aggregate"


class KnowledgeSource(ABC):
    """
    Abstract base class for a knowledge source (e.g., mem0, vector database).

    To add a new knowledge source, subclass this and implement all methods.
    """

    @abstractmethod
    def search(self, query: str, user_id: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Search for relevant information given a query and user context.

        Args:
            query: The search query string.
            user_id: User identifier for context.
            **kwargs: Additional search parameters.

        Returns:
            List of dictionaries containing search results.

        """

    @abstractmethod
    def add(self, content: str, user_id: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Add new knowledge/content to the source.

        Args:
            content: The content to add.
            user_id: User identifier for context.
            **kwargs: Additional parameters.

        Returns:
            Dictionary containing the result of the add operation.

        """

    def update(self, content_id: str, new_content: str, user_id: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Optionally update existing knowledge entry.

        Args:
            content_id: Identifier of the content to update.
            new_content: New content to replace the old.
            user_id: User identifier for context.
            **kwargs: Additional parameters.

        Returns:
            Dictionary containing the result of the update operation.

        """
        msg = "Update not implemented for this knowledge source"
        raise NotImplementedError(msg)

    def delete(self, content_id: str, user_id: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Optionally delete an entry.

        Args:
            content_id: Identifier of the content to delete.
            user_id: User identifier for context.
            **kwargs: Additional parameters.

        Returns:
            Dictionary containing the result of the delete operation.

        """
        msg = "Delete not implemented for this knowledge source"
        raise NotImplementedError(msg)


class Mem0KnowledgeSource(KnowledgeSource):
    """Concrete implementation of KnowledgeSource for mem0 (Memory API)."""

    def __init__(self, mem0_client: Any) -> None:  # noqa: ANN401
        """
        Initialize the mem0 knowledge source.

        Args:
            mem0_client: Initialized client for mem0's Memory API.

        """
        self.mem0_client = mem0_client

    def search(self, query: str, user_id: str, **kwargs: Any) -> List[Dict[str, Any]]:  # noqa: ARG002
        """Search mem0 for relevant memories."""
        return [{"source": "mem0", "content": f"Stub memory for '{query}'"}]

    def add(self, content: str, user_id: str, **kwargs: Any) -> Dict[str, Any]:  # noqa: ARG002
        """Add new content to mem0."""
        return {"source": "mem0", "status": "added", "content": content}


class VectorRAGKnowledgeSource(KnowledgeSource):
    """Concrete implementation of KnowledgeSource for vector database RAG (e.g., ChromaDB)."""

    def __init__(self, vector_client: Any) -> None:  # noqa: ANN401
        """
        Initialize the vector RAG knowledge source.

        Args:
            vector_client: Initialized vector DB client (e.g., ChromaDB).

        """
        self.vector_client = vector_client

    def search(self, query: str, user_id: str, **kwargs: Any) -> List[Dict[str, Any]]:  # noqa: ARG002
        """Search vector DB for relevant documents."""
        return [{"source": "vector_rag", "content": f"Stub vector match for '{query}'"}]

    def add(self, content: str, user_id: str, **kwargs: Any) -> Dict[str, Any]:  # noqa: ARG002
        """Add new content to vector DB."""
        return {"source": "vector_rag", "status": "added", "content": content}


class KnowledgeIntegrationLayer:
    """
    Unified interface for querying multiple knowledge sources.

    This layer abstracts away the complexity of managing multiple knowledge sources
    and provides different strategies for combining their results.
    """

    def __init__(
        self,
        sources: List[KnowledgeSource],
        strategy: KnowledgeStrategy = KnowledgeStrategy.FALLBACK,
    ) -> None:
        """
        Initialize the knowledge integration layer.

        Args:
            sources: List of KnowledgeSource implementations.
            strategy: Aggregation logic. One of:
                - KnowledgeStrategy.FALLBACK: Try sources in order, return first with results.
                - KnowledgeStrategy.AGGREGATE: Query all sources and merge results.

        """
        self.sources = sources
        if isinstance(strategy, str):
            try:
                self.strategy = KnowledgeStrategy(strategy)
            except ValueError as err:
                msg = f"Unknown integration strategy: {strategy}"
                raise ValueError(msg) from err
        elif isinstance(strategy, KnowledgeStrategy):
            self.strategy = strategy
        else:
            msg = f"Invalid strategy type: {type(strategy)}"
            raise TypeError(msg)

    def search(self, query: str, user_id: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Search using the configured integration strategy.

        Args:
            query: The search query string.
            user_id: User identifier for context.
            **kwargs: Additional search parameters.

        Returns:
            List of dictionaries containing search results.

        """
        if not self.sources:
            return []
        if self.strategy == KnowledgeStrategy.AGGREGATE:
            aggregated: List[Dict[str, Any]] = []
            for source in self.sources:
                aggregated.extend(source.search(query, user_id, **kwargs))
            return aggregated
        # FALLBACK strategy
        for source in self.sources:
            results = source.search(query, user_id, **kwargs)
            if results:
                return results
        return []

    def add(self, content: str, user_id: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Add content to all sources.

        Args:
            content: The content to add.
            user_id: User identifier for context.
            **kwargs: Additional parameters.

        Returns:
            List of dictionaries containing results from each source.

        """
        return [source.add(content, user_id, **kwargs) for source in self.sources]
