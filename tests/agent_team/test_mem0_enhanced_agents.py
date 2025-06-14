"""
Tests for mem0-enhanced agents.

This module contains tests for memory-enhanced agent implementations.
The tests verify the functionality while using mocking to avoid actual API calls.

Classes:
    TestMemoryEnhancedCrewAIAgentTeam: Tests for the MemoryEnhancedCrewAIAgentTeam class.
"""

from __future__ import annotations

import logging
import unittest
from typing import Any, Final, cast
from unittest.mock import MagicMock, patch

import pytest
from typing_extensions import Protocol

# Import the memory-enhanced agent team
from agent_team.mem0_enhanced_agents import (
    CREWAI_AVAILABLE,
    MEM0_AVAILABLE,
    MemoryEnhancedCrewAIAgentTeam,
)

# Skip all tests if dependencies are not available
pytestmark = pytest.mark.skipif(
    not CREWAI_AVAILABLE or not MEM0_AVAILABLE,
    reason="CrewAI or mem0 not installed",
)


class MemoryProtocol(Protocol):
    """Protocol for Memory class mocking."""

    def add(self, text: str, metadata: dict[str, Any] | None = None) -> dict[str, str]:
        """Add a memory."""
        ...

    def search(self, query: str, limit: int | None = None) -> list[dict[str, str]]:
        """Search memories."""
        ...


class TestMemoryEnhancedCrewAIAgentTeam(unittest.TestCase):
    """
    Tests for the MemoryEnhancedCrewAIAgentTeam class.

    This test suite verifies the functionality of memory-enhanced CrewAI agent teams,
    including initialization, agent management, task execution, and memory operations.
    """

    memory_mock: MagicMock
    crew_mock: MagicMock
    agent_mock: MagicMock
    task_mock: MagicMock
    team: MemoryEnhancedCrewAIAgentTeam
    memory_patcher: Any
    crew_patcher: Any
    agent_patcher: Any
    task_patcher: Any

    def setUp(self) -> None:
        """
        Set up test fixtures.

        Creates mock objects for Memory, Crew, Agent and Task classes.
        Initializes a test instance of MemoryEnhancedCrewAIAgentTeam.
        Disables logging during tests.
        """
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
            return_value=cast("MemoryProtocol", self.memory_mock),
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

    def tearDown(self) -> None:
        """
        Tear down test fixtures.

        Stops all mock patches and re-enables logging.
        """
        # Stop all patches
        self.memory_patcher.stop()
        self.crew_patcher.stop()
        self.agent_patcher.stop()
        self.task_patcher.stop()

        # Re-enable logging
        logging.disable(logging.NOTSET)

    def test_initialization(self) -> None:
        """
        Test that the team initializes correctly.

        Verifies:
        - Memory initialization
        - User ID assignment
        - Initial memory storage
        """
        # Check that the memory was initialized
        assert self.team.memory == self.memory_mock
        assert self.team.user_id == "test-user"

        # Check that a memory was stored during initialization
        self.memory_mock.add.assert_called_once()
        args, kwargs = self.memory_mock.add.call_args
        text = str(args) if args else str(kwargs)
        assert "test-user" in text, "Initialization memory should include user_id"

    @patch("agent_team.mem0_enhanced_agents.logging")
    def test_memory_error_handling(self, mock_logging: MagicMock) -> None:
        """
        Test error handling during memory initialization.

        Args:
            mock_logging: Mock logging object

        """
        # Simulate memory initialization failure
        self.memory_mock.add.side_effect = Exception("Memory error")

        # Try to store a memory
        result = self.team._store_memory("Test memory")
        assert not result

        # Verify error was logged
        mock_logging.error.assert_called_once()

    def test_add_agent(self) -> None:
        """Test adding an agent to the team."""
        agent_config: dict[str, Any] = {
            "name": "Test Agent",
            "role": "Test Role",
            "goal": "Test Goal",
            "backstory": "Test Backstory",
        }

        # Add an agent
        self.team.add_agent(**agent_config)

        # Verify agent was created with correct parameters
        self.agent_mock.assert_called_once_with(
            name=agent_config["name"],
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
        )

        assert len(self.team.agents) == 1

    def test_create_task(self) -> None:
        """Test creating a task."""
        task_config: dict[str, Any] = {
            "description": "Test Task",
            "agent": self.agent_mock,
            "context": "Test Context",
        }

        # Create a task
        self.team.add_task(**task_config)

        # Verify task was created with correct parameters
        self.task_mock.assert_called_once_with(
            description=task_config["description"],
            agent=task_config["agent"],
            context=task_config["context"],
        )

        assert len(self.team.tasks) == 1

    def test_execute_workflow(self) -> None:
        """Test executing the workflow."""
        # Add an agent and task
        self.team.add_agent(
            name="Test Agent",
            role="Test Role",
            goal="Test Goal",
            backstory="Test Backstory",
        )
        self.team.add_task(
            description="Test Task",
            agent=self.agent_mock,
        )

        # Execute the workflow
        result = self.team.run()

        # Verify the crew was created and executed
        assert result == "Test workflow result"
        self.crew_mock.kickoff.assert_called_once()

    def test_memory_integration(self) -> None:
        """Test memory integration during workflow execution."""
        # Add an agent and task
        self.team.add_agent(
            name="Test Agent",
            role="Test Role",
            goal="Test Goal",
            backstory="Test Backstory",
        )
        self.team.add_task(
            description="Test Task",
            agent=self.agent_mock,
        )

        # Execute the workflow
        self.team.run()

        # Verify memories were stored and retrieved
        assert self.memory_mock.add.call_count >= 3  # Init, agent, task
        assert self.memory_mock.search.call_count >= 1

    def test_memory_enhancement(self) -> None:
        """Test memory enhancement of task context."""
        # Store some test memories
        self.team._store_memory("Previous task result")
        self.team._store_memory("Important context")

        # Enhance context with memories
        enhanced_context = self.team._enhance_context_with_memories(
            context="Original context",
            query="test query",
        )

        # Verify memories were retrieved and context was enhanced
        self.memory_mock.search.assert_called()
        assert "Original context" in enhanced_context
        assert "Test memory 1" in enhanced_context
        assert "Test memory 2" in enhanced_context

    def test_store_memory(self) -> None:
        """Test storing a memory."""
        # Store a memory
        result = self.team._store_memory(
            "Test memory content",
            metadata={"test_key": "test_value"},
        )

        # Verify memory was stored
        assert result is True
        self.memory_mock.add.assert_called_with(
            "Test memory content",
            user_id="test-user",
            metadata={"test_key": "test_value"},
        )

    def test_retrieve_relevant_memories(self) -> None:
        """Test retrieving relevant memories."""
        # Retrieve memories
        memories = self.team._retrieve_relevant_memories(
            query="Test query",
            limit=5,
        )

        # Verify memories were retrieved
        self.memory_mock.search.assert_called_with(
            query="Test query",
            user_id="test-user",
            limit=5,
        )

        # Verify correct memories were returned
        assert memories == [
            {"id": "memory-1", "text": "Test memory 1"},
            {"id": "memory-2", "text": "Test memory 2"},
        ]

    def test_enhance_context_with_memories(self) -> None:
        """Test enhancing context with relevant memories."""
        # Enhance context
        enhanced_context = self.team._enhance_context_with_memories(
            context="Original context",
            query="Test query",
        )

        # Verify memories were retrieved
        self.memory_mock.search.assert_called_once()

        # Verify context was enhanced
        assert "Original context" in enhanced_context
        assert "Test memory 1" in enhanced_context
        assert "Test memory 2" in enhanced_context

    def test_memory_persistence(self) -> None:
        """Test that memories persist across operations."""
        # Store multiple memories
        self.team._store_memory("Memory 1")
        self.team._store_memory("Memory 2")
        self.team._store_memory("Memory 3")

        # Verify all memories were stored
        assert self.memory_mock.add.call_count >= 4  # Init + 3 memories

        # Retrieve memories
        memories = self.team._retrieve_relevant_memories("test query")

        # Verify memories can be retrieved
        assert len(memories) == 2  # Based on our mock return value


if __name__ == "__main__":
    unittest.main()
