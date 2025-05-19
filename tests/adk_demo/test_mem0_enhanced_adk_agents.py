"""
Tests for mem0-enhanced ADK agents.

These tests verify the functionality of the memory-enhanced ADK agent implementations.
They use mocking to avoid actual API calls to mem0 or ADK.
"""

import logging
import unittest
from unittest.mock import MagicMock, patch

import pytest

# Import the memory-enhanced ADK agents
from adk_demo.mem0_enhanced_adk_agents import (
    ADK_AVAILABLE,
    MEM0_AVAILABLE,
    MemoryEnhancedDataGathererAgent,
    MemoryEnhancedSummarizerAgent,
)


# Skip all tests if dependencies are not available
pytestmark = pytest.mark.skipif(
    not ADK_AVAILABLE or not MEM0_AVAILABLE,
    reason="ADK or mem0 not installed",
)


class TestMemoryEnhancedADKAgents(unittest.TestCase):
    """Tests for the memory-enhanced ADK agent implementations."""

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
            "adk_demo.mem0_enhanced_adk_agents.Memory",
            return_value=self.memory_mock,
        )
        self.memory_patcher.start()

        # Patch the SimpleMemory class
        self.simple_memory_mock = MagicMock()
        self.simple_memory_patcher = patch(
            "adk_demo.mem0_enhanced_adk_agents.SimpleMemory",
            return_value=self.simple_memory_mock,
        )
        self.simple_memory_patcher.start()

        # Patch the DataGathererSkill class
        self.data_gatherer_skill_mock = MagicMock()
        self.data_gatherer_skill_mock.run.return_value = "Test data"
        self.data_gatherer_skill_patcher = patch(
            "adk_demo.mem0_enhanced_adk_agents.DataGathererSkill",
            return_value=self.data_gatherer_skill_mock,
        )
        self.data_gatherer_skill_patcher.start()

        # Patch the SummarizerSkill class
        self.summarizer_skill_mock = MagicMock()
        self.summarizer_skill_mock.run.return_value = "Test summary"
        self.summarizer_skill_patcher = patch(
            "adk_demo.mem0_enhanced_adk_agents.SummarizerSkill",
            return_value=self.summarizer_skill_mock,
        )
        self.summarizer_skill_patcher.start()

        # Create a mock Message class
        self.message_mock = MagicMock()
        self.message_mock.type = "gather"
        self.message_mock.payload = {"query": "Test query"}
        self.message_mock.sender = "test-sender"

        # Create a mock response Message
        self.response_mock = MagicMock()
        self.response_mock.type = "gather_result"
        self.response_mock.payload = {"data": "Test data"}

        # Patch the Agent.handle_message method
        self.handle_message_patcher = patch(
            "adk_demo.mem0_enhanced_adk_agents.Agent.handle_message",
            return_value=self.response_mock,
        )
        self.handle_message_mock = self.handle_message_patcher.start()

        # Create test instances
        self.gatherer = MemoryEnhancedDataGathererAgent(
            name="TestGatherer",
            user_id="test-user",
        )
        self.summarizer = MemoryEnhancedSummarizerAgent(
            name="TestSummarizer",
            user_id="test-user",
        )

        # Disable logging during tests
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Tear down test fixtures."""
        # Stop all patches
        self.memory_patcher.stop()
        self.simple_memory_patcher.stop()
        self.data_gatherer_skill_patcher.stop()
        self.summarizer_skill_patcher.stop()
        self.handle_message_patcher.stop()

        # Re-enable logging
        logging.disable(logging.NOTSET)

    def test_initialization(self):
        """Test that the agents initialize correctly."""
        # Check that the memory was initialized
        assert self.gatherer.memory == self.memory_mock
        assert self.gatherer.user_id == "test-user"
        assert self.gatherer.name == "TestGatherer"

        assert self.summarizer.memory == self.memory_mock
        assert self.summarizer.user_id == "test-user"
        assert self.summarizer.name == "TestSummarizer"

        # Check that a memory was stored during initialization
        assert self.memory_mock.add.call_count >= 2  # Once for each agent
        args, kwargs = self.memory_mock.add.call_args_list[0]
        assert "TestGatherer" in str(args) or "TestGatherer" in str(kwargs)

    def test_handle_message(self):
        """Test handling a message with memory enhancement."""
        # Handle a message
        response = self.gatherer.handle_message(self.message_mock)

        # Check that the parent handle_message was called
        self.handle_message_mock.assert_called_once()

        # Check that memories were retrieved
        self.memory_mock.search.assert_called_once()
        args, kwargs = self.memory_mock.search.call_args
        assert "Test query" in str(args) or "Test query" in str(kwargs)

        # Check that the interaction was stored
        assert self.memory_mock.add.call_count >= 3  # Init + interaction
        args, kwargs = self.memory_mock.add.call_args
        assert "user" in str(args) or "user" in str(kwargs)
        assert "assistant" in str(args) or "assistant" in str(kwargs)

        # Check that the response was returned
        assert response == self.response_mock

    def test_extract_query_from_message(self):
        """Test extracting a query from a message."""
        # Extract query from gather message
        query = self.gatherer._extract_query_from_message(self.message_mock)
        assert query == "Test query"

        # Extract query from summarize message
        summarize_message = MagicMock()
        summarize_message.type = "summarize"
        summarize_message.payload = {"data": "Test data"}
        query = self.gatherer._extract_query_from_message(summarize_message)
        assert query == "Test data"

        # Extract query from unknown message type
        unknown_message = MagicMock()
        unknown_message.type = "unknown"
        unknown_message.sender = "test-sender"
        query = self.gatherer._extract_query_from_message(unknown_message)
        assert "unknown" in query
        assert "test-sender" in query

    def test_store_memory(self):
        """Test storing a memory."""
        # Store a memory
        self.gatherer._store_memory(
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
        memories = self.gatherer._retrieve_relevant_memories(
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

    def test_store_interaction(self):
        """Test storing an interaction."""
        # Store an interaction
        self.gatherer._store_interaction(self.message_mock, self.response_mock)

        # Check that the interaction was stored
        self.memory_mock.add.assert_called_once_with(
            [
                {"role": "user", "content": "gather: {'query': 'Test query'}"},
                {"role": "assistant", "content": "gather_result: {'data': 'Test data'}"},
            ],
            user_id="test-user",
            metadata={
                "message_type": "gather",
                "response_type": "gather_result",
                "sender": "test-sender",
            },
        )


if __name__ == "__main__":
    unittest.main()
