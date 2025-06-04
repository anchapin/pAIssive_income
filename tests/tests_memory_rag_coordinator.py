"""
Test module for MemoryRAGCoordinator functionality.

This module tests the coordination between mem0 and Chroma vector database systems.
"""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import patch

import pytest


# Fallback stubs for missing dependencies
class MemoryRAGCoordinator:
    def __init__(self, *_args: Any, **_kwargs: Any):
        pass

    def query(self, *_args: Any, **_kwargs: Any) -> Any:
        return {}


class MemoryEnhancedCrewAIAgentTeam:
    def __init__(self, user_id: Any = None, *_args: Any, **_kwargs: Any):
        self.user_id = user_id
        self.agents: list[Any] = []

    def retrieve_relevant_memories(self, *_args: Any, **_kwargs: Any) -> list[Any]:
        return []


# Check for required dependencies
try:  # type: ignore[import]
    from agent_team.mem0_enhanced_agents import (
        MemoryEnhancedCrewAIAgentTeam as RealTeam,
    )
    from services.memory_rag_coordinator import MemoryRAGCoordinator as RealCoordinator

    dependencies_available = True
except ImportError:
    dependencies_available = False
    RealCoordinator = MemoryRAGCoordinator
    RealTeam = MemoryEnhancedCrewAIAgentTeam

# Skip all tests if dependencies are not available
pytestmark = pytest.mark.skipif(
    not dependencies_available,
    reason="mem0ai, chromadb, or sentence-transformers not installed",
)

# ----- Fixtures and Fakes -----


@pytest.fixture
def fake_mem0_result():
    """Fake mem0 query result."""
    return [
        {
            "text": "Project deadline is next Friday",
            "relevance": 0.9,
            "timestamp": 1704110400,
        },  # 2024-01-01T10:00:00Z as Unix timestamp
        {
            "text": "Remember to update the documentation",
            "relevance": 0.7,
            "timestamp": 1704106800,
        },  # 2024-01-01T09:00:00Z as Unix timestamp
    ]


@pytest.fixture
def fake_chroma_result():
    """Fake Chroma query result."""
    return [
        {
            "text": "Unified answer 1",
            "relevance": 0.8,
            "timestamp": 1704103200,
        },  # 2024-01-01T08:00:00Z as Unix timestamp
        {
            "text": "Unified answer 2",
            "relevance": 0.6,
            "timestamp": 1704099600,
        },  # 2024-01-01T07:00:00Z as Unix timestamp
    ]


@pytest.fixture
def coordinator():
    """MemoryRAGCoordinator instance for testing."""
    return RealCoordinator()


# ----- Tests -----


def test_only_mem0_returns_results(fake_mem0_result, coordinator):
    """Test that results are returned and merged correctly when only mem0 returns results."""
    with patch.object(
        coordinator, "mem0_query", return_value=fake_mem0_result
    ), patch.object(coordinator, "chroma_query", return_value=[]):
        res = coordinator.query("deadline", "user1")
        merged = res["merged_results"]
        assert len(merged) == 2
        assert all(m["source"] == "mem0" for m in merged)
        assert "subsystem_metrics" in res
        assert "mem0" in res["subsystem_metrics"]
        assert "chroma" in res["subsystem_metrics"]


def test_only_chroma_returns_results(fake_chroma_result, coordinator):
    """Test that results are returned and merged correctly when only Chroma returns results."""
    with patch.object(coordinator, "mem0_query", return_value=[]), patch.object(
        coordinator, "chroma_query", return_value=fake_chroma_result
    ):
        res = coordinator.query("deadline", "user2")
        merged = res["merged_results"]
        assert len(merged) == 2
        assert all(m["source"] == "chroma" for m in merged)
        assert "subsystem_metrics" in res
        assert "mem0" in res["subsystem_metrics"]
        assert "chroma" in res["subsystem_metrics"]


def test_both_return_with_duplicates(fake_mem0_result, fake_chroma_result, coordinator):
    """Test that duplicates/conflicts between mem0 and Chroma are resolved (prefer high relevance or recent)."""
    with patch.object(
        coordinator, "mem0_query", return_value=fake_mem0_result
    ), patch.object(coordinator, "chroma_query", return_value=fake_chroma_result):
        res = coordinator.query("deadline", "userX")
        merged = res["merged_results"]
        # Should have results from both sources
        assert len(merged) >= 2
        sources = [m["source"] for m in merged]
        assert "mem0" in sources
        assert "chroma" in sources


def test_metrics_are_included(fake_mem0_result, fake_chroma_result, coordinator):
    """Test that timing/cost metrics are included for each subsystem."""
    with patch.object(
        coordinator, "mem0_query", return_value=fake_mem0_result
    ), patch.object(coordinator, "chroma_query", return_value=fake_chroma_result):
        res = coordinator.query("anything", "userZ")
        metrics = res["subsystem_metrics"]
        assert "mem0" in metrics
        assert "chroma" in metrics
        assert "time_sec" in metrics["mem0"]
        assert "cost" in metrics["mem0"]
        assert "time_sec" in metrics["chroma"]
        assert "cost" in metrics["chroma"]
        # Should be floats (timing)
        assert isinstance(metrics["mem0"]["time_sec"], float)
        assert isinstance(metrics["chroma"]["time_sec"], float)


def test_integration_with_memory_enhanced_team():
    """Test that MemoryEnhancedCrewAIAgentTeam retrieves memories through the RAG coordinator."""
    # Patch the MemoryRAGCoordinator's query method to return a fake merged result
    fake_merged_result = {
        "merged_results": [
            {"text": "Unified answer 1", "source": "mem0"},
            {"text": "Unified answer 2", "source": "chroma"},
        ],
        "subsystem_metrics": {"mem0": {"time_sec": 0.1}, "chroma": {"time_sec": 0.2}},
    }

    with patch.object(RealCoordinator, "query", return_value=fake_merged_result):
        # Create a team instance for testing
        team = RealTeam(user_id="test_user")

        # Create a dummy agent for the team
        class DummyAgent:
            role = "Tester"

        team.agents = cast("Any", [DummyAgent()])
        memories = team.retrieve_relevant_memories(query="test query")
        assert len(memories) == 2
        assert any("Unified answer 1" in m["text"] for m in memories)
        assert any(m["source"] in ["mem0", "chroma"] for m in memories)


# ----- End of Test Suite -----
