# type: ignore[import, assignment]
import unittest
from unittest.mock import MagicMock, patch

import pytest

# Check for required dependencies with better error handling
crewai_available = False
mem0_available = False
imports_successful = False
try:
    from agent_team.mem0_enhanced_agents import (
        MemoryEnhancedCrewAIAgentTeam,
    )
    from agent_team.mem0_enhanced_agents import (
        crewai_available as _crewai_available,
    )
    from agent_team.mem0_enhanced_agents import (
        mem0_available as _mem0_available,
    )

    crewai_available = _crewai_available
    mem0_available = _mem0_available
    imports_successful = True
except ImportError:
    # Create mock class for when dependencies are missing
    class MemoryEnhancedCrewAIAgentTeam:
        pass


"""
Tests for mem0-enhanced agents.

These tests verify the functionality of the memory-enhanced agent implementations.
They use mocking to avoid actual API calls to mem0 or CrewAI.
"""


# Skip all tests if dependencies are not available
pytestmark = pytest.mark.skipif(
    not imports_successful or not crewai_available or not mem0_available,
    reason="CrewAI, mem0, or other required dependencies not installed",
)


class TestMemoryEnhancedCrewAIAgentTeam(unittest.TestCase):
    """Tests for the MemoryEnhancedCrewAIAgentTeam class."""

    def setUp(self):
        """Set up test fixtures for each test."""
        # Mock the Memory class to avoid actual mem0 calls
        self.memory_mock = MagicMock()
        self.memory_patcher = patch(
            "agent_team.mem0_enhanced_agents.Memory", return_value=self.memory_mock
        )
        self.memory_patcher.start()

        # Mock the MemoryRAGCoordinator to avoid dependency issues
        self.coordinator_mock = MagicMock()
        self.coordinator_patcher = patch(
            "agent_team.mem0_enhanced_agents.MemoryRAGCoordinator",
            return_value=self.coordinator_mock,
        )
        self.coordinator_patcher.start()

        # Create test instance
        self.team = MemoryEnhancedCrewAIAgentTeam(user_id="test_user")

    def tearDown(self):
        """Clean up test fixtures after each test."""
        self.memory_patcher.stop()
        self.coordinator_patcher.stop()

    def test_initialization(self):
        """Test that the team initializes correctly."""
        assert self.team.user_id == "test_user"
        assert hasattr(self.team, "rag_coordinator")

    def test_memory_storage(self):
        """Test memory storage functionality."""
        test_content = "Test memory content"
        self.team.store_memory(test_content)

        # Verify that memory.add was called
        self.memory_mock.add.assert_called_once()

    def test_memory_retrieval(self):
        """Test memory retrieval functionality."""
        # Mock the coordinator response
        mock_response = {
            "merged_results": [
                {"text": "Test memory", "source": "mem0"},
                {"text": "Test RAG result", "source": "chroma"},
            ],
            "subsystem_metrics": {
                "mem0": {"time_sec": 0.1},
                "chroma": {"time_sec": 0.2},
            },
        }
        self.coordinator_mock.query.return_value = mock_response

        # Test retrieval
        memories = self.team.retrieve_relevant_memories("test query")

        # Verify results
        assert len(memories) == 2
        assert any("Test memory" in m["text"] for m in memories)
        assert any("Test RAG result" in m["text"] for m in memories)

    def test_agent_addition_with_memory(self):
        """Test adding agents with memory enhancement."""
        # Mock agent creation
        with patch("agent_team.mem0_enhanced_agents.Agent") as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.role = "Test Agent"
            mock_agent_class.return_value = mock_agent

            # Add agent
            agent = self.team.add_agent(
                role="Test Agent", goal="Test goal", backstory="Test backstory"
            )

            # Verify agent was added
            assert agent is not None
            assert mock_agent in self.team.agents


if __name__ == "__main__":
    unittest.main()
