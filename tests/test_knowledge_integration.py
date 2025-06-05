"""
Tests for KnowledgeIntegrationLayer fallback and aggregation logic.

Mocks KnowledgeSource implementations to simulate different retrieval behaviors.
"""

from __future__ import annotations

from typing import Any

import pytest

from interfaces.knowledge_interfaces import (
    KnowledgeIntegrationLayer,
    KnowledgeSource,
    KnowledgeStrategy,
)


class AlwaysReturnsSource(KnowledgeSource):
    """Mock source that always returns a result."""

    def search(
        self,
        query: str,
        user_id: str,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        """Search for content."""
        return [{"source": "mem0", "content": f"mem0 hit for {query}"}]

    def add(self, content: str, user_id: str, **kwargs: object) -> Any:  # noqa: ARG002
        """Add content."""
        return {"source": "mem0", "status": "added"}


class NeverReturnsSource(KnowledgeSource):
    """Mock source that never returns a result."""

    def search(
        self,
        query: str,  # noqa: ARG002
        user_id: str,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        """Search for content."""
        return []

    def add(self, content: str, user_id: str, **kwargs: object) -> Any:  # noqa: ARG002
        """Add content."""
        return {"source": "never", "status": "added"}


class OnlyOnFallbackSource(KnowledgeSource):
    """Mock source that only returns on fallback (second in chain)."""

    def search(
        self,
        query: str,
        user_id: str,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        """Search for content."""
        return [{"source": "vector_rag", "content": f"vector_rag fallback for {query}"}]

    def add(self, content: str, user_id: str, **kwargs: object) -> Any:  # noqa: ARG002
        """Add content."""
        return {"source": "vector_rag", "status": "added"}


@pytest.fixture
def sources_mem0_first():
    """Fixture: mem0 (returns), then vector_rag (fallback)."""
    return [AlwaysReturnsSource(), OnlyOnFallbackSource()]


@pytest.fixture
def sources_mem0_never_vector_rag_fallback():
    """Fixture: never returns, then vector_rag (fallback)."""
    return [NeverReturnsSource(), OnlyOnFallbackSource()]


def test_fallback_returns_first_source(sources_mem0_first):
    """Test that fallback strategy returns results from the first source if available."""
    integration = KnowledgeIntegrationLayer(
        sources=sources_mem0_first, strategy=KnowledgeStrategy.FALLBACK
    )
    results = integration.search(query="foo", user_id="user1")
    assert results
    assert all(r["source"] == "mem0" for r in results)
    assert results[0]["content"] == "mem0 hit for foo"


def test_fallback_returns_next_on_empty(sources_mem0_never_vector_rag_fallback):
    """Test that fallback strategy returns results from the next source if the first yields nothing."""
    integration = KnowledgeIntegrationLayer(
        sources=sources_mem0_never_vector_rag_fallback,
        strategy=KnowledgeStrategy.FALLBACK,
    )
    results = integration.search(query="bar", user_id="user2")
    assert results
    assert all(r["source"] == "vector_rag" for r in results)
    assert results[0]["content"] == "vector_rag fallback for bar"


def test_aggregation_combines_all(sources_mem0_first):
    """Test that aggregation strategy returns combined results from all sources."""
    integration = KnowledgeIntegrationLayer(
        sources=sources_mem0_first, strategy=KnowledgeStrategy.AGGREGATE
    )
    results = integration.search(query="baz", user_id="user3")
    assert results
    sources = {r["source"] for r in results}
    assert "mem0" in sources
    assert "vector_rag" in sources
    assert any(r["content"] == "mem0 hit for baz" for r in results)
    assert any(r["content"] == "vector_rag fallback for baz" for r in results)
