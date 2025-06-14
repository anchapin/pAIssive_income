import logging
import unittest
from unittest.mock import MagicMock, patch

import pytest

from agent_team.mem0_enhanced_agents import (
    CREWAI_AVAILABLE,
    MEM0_AVAILABLE,
    MemoryEnhancedCrewAIAgentTeam,
)

"""
Tests for mem0-enhanced agents.

These tests verify the functionality of the memory-enhanced agent implementations.
They use mocking to avoid actual API calls to mem0 or CrewAI.
"""


# Skip all tests if dependencies are not available
pytestmark = pytest.mark.skipif(
    not CREWAI_AVAILABLE or not MEM0_AVAILABLE,
    reason="CrewAI or mem0 not installed",
)


class TestMemoryEnhancedCrewAIAgentTeam(unittest.TestCase):
    """Tests for the MemoryEnhancedCrewAIAgentTeam class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock Memory class
        self.memory_mock = MagicMock()
        self.memory_mock.add.return_value = {"id": "test-memory-id"}
        self.memory_mock.search.return_value = [
            {"id": "memory-1", "text": "Test memory 1"},
            {"id": "memory-2", "text": "Test memory 2"},
        ]

        # Patch the Memory class
        self.memory_patcher = patch(
            "agent_team.mem0_enhanced_agents.Memory",
            return_value=self.memory_mock,
        )
        self.memory_patcher.start()

        # Patch the Crew class
        self.crew_mock = MagicMock()
        self.crew_mock.kickoff.return_value = "Test workflow result"
        self.crew_patcher = patch(
            "agent_team.mem0_enhanced_agents.Crew",
            return_value=self.crew_mock,
        )
        self.crew_patcher.start()

        # Patch the Agent class
        self.agent_mock = MagicMock()
        self.agent_patcher = patch(
            "agent_team.mem0_enhanced_agents.Agent",
            return_value=self.agent_mock,
        )
        self.agent_patcher.start()

        # Patch the Task class
        self.task_mock = MagicMock()
        self.task_patcher = patch(
            "agent_team.mem0_enhanced_agents.Task",
            return_value=self.task_mock,
        )
        self.task_patcher.start()

        # Create a test instance
        self.team = MemoryEnhancedCrewAIAgentTeam(user_id="test-user")

        # Disable logging during tests
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Tear down test fixtures."""
        # Stop all patches
        self.memory_patcher.stop()
        self.crew_patcher.stop()
        self.agent_patcher.stop()
        self.task_patcher.stop()

        # Re-enable logging
        logging.disable(logging.NOTSET)

    def test_initialization(self):
        """Test that the team initializes correctly."""
        # Check that the memory was initialized
        assert self.team.memory == self.memory_mock
        assert self.team.user_id == "test-user"

        # Check that a memory was stored during initialization
        self.memory_mock.add.assert_called_once()
        args, kwargs = self.memory_mock.add.call_args
        assert "test-user" in str(args) or "test-user" in str(kwargs)

    def test_add_agent(self):
        """Test adding an agent to the team."""
        # Add an agent
        agent = self.team.add_agent(
            role="Researcher",
            goal="Find information",
            backstory="Expert researcher",
        )

        # Check that the agent was created
        assert agent == self.agent_mock

        # Check that the agent was added to the team
        assert agent in self.team.agents

        # Check that a memory was stored
        assert self.memory_mock.add.call_count >= 2  # Once for init, once for add_agent
        args, kwargs = self.memory_mock.add.call_args
        assert "Researcher" in str(args) or "Researcher" in str(kwargs)

    def test_add_task(self):
        """Test adding a task to the team."""
        # Add an agent first
        agent = self.team.add_agent(
            role="Researcher",
            goal="Find information",
            backstory="Expert researcher",
        )

        # Add a task
        task = self.team.add_task(
            description="Research AI memory systems",
            agent=agent,
        )

        # Check that the task was created
        assert task == self.task_mock

        # Check that the task was added to the team
        assert task in self.team.tasks

        # Check that a memory was stored
        assert self.memory_mock.add.call_count >= 3  # Init, add_agent, add_task
        args, kwargs = self.memory_mock.add.call_args
        assert "Research AI memory systems" in str(
            args
        ) or "Research AI memory systems" in str(kwargs)

    def test_run(self):
        """Test running the team workflow."""
        # Add an agent and task
        agent = self.team.add_agent(
            role="Researcher",
            goal="Find information",
            backstory="Expert researcher",
        )
        task = self.team.add_task(
            description="Research AI memory systems",
            agent=agent,
        )

        # Run the workflow
        result = self.team.run()

        # Check that the crew was created and run
        assert result == "Test workflow result"
        self.crew_mock.kickoff.assert_called_once()

        # Check that memories were retrieved and stored
        assert self.memory_mock.search.call_count >= 1
        assert self.memory_mock.add.call_count >= 4  # Init, add_agent, add_task, run

    def test_store_memory(self):
        """Test storing a memory."""
        # Store a memory
        self.team._store_memory(
            "Test memory content",
            metadata={"test_key": "test_value"},
        )

        # Check that the memory was stored
        self.memory_mock.add.assert_called_with(
            "Test memory content",
            user_id="test-user",
            metadata={"test_key": "test_value"},
        )

    def test_retrieve_relevant_memories(self):
        """Test retrieving relevant memories."""
        # Retrieve memories
        memories = self.team._retrieve_relevant_memories(
            query="Test query",
            limit=5,
        )

        # Check that memories were retrieved
        self.memory_mock.search.assert_called_with(
            query="Test query",
            user_id="test-user",
            limit=5,
        )
        assert len(memories) == 2
        assert memories[0]["id"] == "memory-1"
        assert memories[1]["id"] == "memory-2"

    def test_enhance_context_with_memories(self):
        """Test enhancing context with memories."""
        # Set up test memories
        memories = [
            {"id": "memory-1", "text": "User prefers dark mode"},
            {"id": "memory-2", "text": "User is allergic to shellfish"},
        ]

        # Mock the _retrieve_relevant_memories method
        self.team._retrieve_relevant_memories = MagicMock(return_value=memories)

        # Test enhancing context
        original_context = "What should I eat for dinner?"
        enhanced_context = self.team._enhance_context_with_memories(original_context)

        # Check that the context was enhanced with memories
        assert "User prefers dark mode" in enhanced_context
        assert "User is allergic to shellfish" in enhanced_context
        assert original_context in enhanced_context

        # Check that memories were retrieved
        self.team._retrieve_relevant_memories.assert_called_once()

    def test_memory_persistence(self):
        """Test that memories persist across team instances."""
        # Create a new team with the same user_id
        new_team = MemoryEnhancedCrewAIAgentTeam(user_id="test-user")

        # Check that the memory was initialized
        assert new_team.memory == self.memory_mock
        assert new_team.user_id == "test-user"

        # Retrieve memories with the new team
        query = "What are my preferences?"
        new_team._retrieve_relevant_memories(query=query)

        # Check that memories were retrieved using the same user_id
        self.memory_mock.search.assert_called_with(
            query=query,
            user_id="test-user",
            limit=5,  # Default limit
        )


if __name__ == "__main__":
    unittest.main()
