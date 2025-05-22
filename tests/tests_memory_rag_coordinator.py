"""
Test suite for the MemoryRAGCoordinator class and its integration with MemoryEnhancedCrewAIAgentTeam.

Covers:
1. Only mem0 returns results
2. Only Chroma/RAG returns results
3. Both return (including duplicate/conflicting content)
4. Performance/cost metrics are included in the response
5. Integration with MemoryEnhancedCrewAIAgentTeam

Requires: uv, pytest
"""

import pytest
from unittest.mock import patch, MagicMock

from services.memory_rag_coordinator import MemoryRAGCoordinator
from agent_team.mem0_enhanced_agents import MemoryEnhancedCrewAIAgentTeam

# ----- Fixtures and Fakes -----

@pytest.fixture
def fake_mem0_result():
    return [
        {"text": "Project deadline is June 1.", "timestamp": 1000, "score": 0.95, "source": "mem0"},
        {"text": "The kickoff is May 1.", "timestamp": 800, "score": 0.90, "source": "mem0"},
    ]

@pytest.fixture
def fake_chroma_result():
    return [
        {"content": "Project deadline is June 1.", "score": 0.1, "timestamp": 995, "id": "abc", "source": "chroma"},
        {"content": "The planning phase ends April 30.", "score": 0.2, "timestamp": 700, "id": "def", "source": "chroma"},
    ]

@pytest.fixture
def coordinator():
    return MemoryRAGCoordinator()

# ----- Tests -----

def test_only_mem0_returns_results(monkeypatch, fake_mem0_result, coordinator):
    """Test that results are returned and merged correctly when only mem0 returns results."""
    monkeypatch.setattr("services.memory_rag_coordinator.mem0_query", lambda q, u: fake_mem0_result)
    monkeypatch.setattr("services.memory_rag_coordinator.chroma_query", lambda q, u=None: [])

    res = coordinator.query("deadline", "user1")
    merged = res["merged_results"]
    assert len(merged) == 2
    assert any("Project deadline is June 1." in m["text"] for m in merged)
    assert all(m["source"] == "mem0" for m in merged)
    assert "subsystem_metrics" in res
    assert "mem0" in res["subsystem_metrics"] and "chroma" in res["subsystem_metrics"]

def test_only_chroma_returns_results(monkeypatch, fake_chroma_result, coordinator):
    """Test that results are returned and merged correctly when only Chroma returns results."""
    monkeypatch.setattr("services.memory_rag_coordinator.mem0_query", lambda q, u: [])
    monkeypatch.setattr("services.memory_rag_coordinator.chroma_query", lambda q, u=None: fake_chroma_result)

    res = coordinator.query("deadline", "user2")
    merged = res["merged_results"]
    assert len(merged) == 2
    assert any("Project deadline is June 1." in m["text"] for m in merged)
    assert all(m["source"] == "chroma" for m in merged)
    assert "subsystem_metrics" in res
    assert "mem0" in res["subsystem_metrics"] and "chroma" in res["subsystem_metrics"]

def test_both_return_with_duplicates(monkeypatch, fake_mem0_result, fake_chroma_result, coordinator):
    """Test that duplicates/conflicts between mem0 and Chroma are resolved (prefer high relevance or recent)."""
    monkeypatch.setattr("services.memory_rag_coordinator.mem0_query", lambda q, u: fake_mem0_result)
    monkeypatch.setattr("services.memory_rag_coordinator.chroma_query", lambda q, u=None: fake_chroma_result)

    res = coordinator.query("deadline", "userX")
    merged = res["merged_results"]
    # Should deduplicate "Project deadline is June 1."
    texts = [m["text"] for m in merged]
    assert texts.count("Project deadline is June 1.") == 1
    # Check the merged result prefers higher relevance or more recent info
    top = merged[0]
    assert top["text"] == "Project deadline is June 1."
    assert "source" in top

def test_metrics_are_included(monkeypatch, fake_mem0_result, fake_chroma_result, coordinator):
    """Test that timing/cost metrics are included for each subsystem."""
    monkeypatch.setattr("services.memory_rag_coordinator.mem0_query", lambda q, u: fake_mem0_result)
    monkeypatch.setattr("services.memory_rag_coordinator.chroma_query", lambda q, u=None: fake_chroma_result)

    res = coordinator.query("anything", "userZ")
    metrics = res["subsystem_metrics"]
    assert "mem0" in metrics and "chroma" in metrics
    assert "time_sec" in metrics["mem0"] and "cost" in metrics["mem0"]
    assert "time_sec" in metrics["chroma"] and "cost" in metrics["chroma"]
    # Should be floats (timing)
    assert isinstance(metrics["mem0"]["time_sec"], float)
    assert isinstance(metrics["chroma"]["time_sec"], float)

def test_integration_with_memory_enhanced_team(monkeypatch, fake_mem0_result, fake_chroma_result):
    """Test that MemoryEnhancedCrewAIAgentTeam retrieves memories through the RAG coordinator."""
    # Patch the MemoryRAGCoordinator's query method to return a fake merged result
    fake_merged = [
        {"text": "Unified answer 1", "source": "mem0", "timestamp": 1234, "relevance": 0.99},
        {"text": "Unified answer 2", "source": "chroma", "timestamp": 1200, "relevance": 0.90},
    ]
    with patch("services.memory_rag_coordinator.MemoryRAGCoordinator.query", return_value={
        "merged_results": fake_merged,
        "subsystem_metrics": {"mem0": {"time_sec": 0.01, "cost": 0}, "chroma": {"time_sec": 0.01, "cost": 0}},
        "raw_mem0_results": [],
        "raw_chroma_results": [],
    }):
        team = MemoryEnhancedCrewAIAgentTeam(user_id="integration_test_user")
        # Add a fake agent to avoid errors
        class DummyAgent:
            role = "Tester"
        team.agents = [DummyAgent()]
        memories = team._retrieve_relevant_memories(query="test query")
        assert len(memories) == 2
        assert any("Unified answer 1" in m["text"] for m in memories)
        assert any(m["source"] in ["mem0", "chroma"] for m in memories)

# ----- End of Test Suite -----