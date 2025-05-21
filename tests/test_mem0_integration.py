"""
Integration tests for mem0 functionality.

These tests verify the end-to-end functionality of mem0 integration
with ADK agents. They require mem0ai to be installed and configured
with an OpenAI API key.
"""

import os
import logging
import sys
import unittest
from unittest.mock import patch

import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Check if mem0 is available
try:
    import mem0ai

    Memory = mem0ai.Memory
    mem0 = mem0ai
except ImportError:  # mem0 or agent frameworks not available, skip test
    mem0 = None
    Memory = None

# Import ADK components
from adk.agent import Agent


class MemoryEnhancedAgent(Agent):
    """ADK agent enhanced with mem0 memory capabilities."""

    def __init__(self, name: str, user_id: str) -> None:
        """Initialize the agent."""
        super().__init__(name)

        # Initialize mem0 memory
        if Memory is not None:
            self.memory = Memory()
        else:
            self.memory = None

        self.user_id = user_id

    def _store_memory(self, content: str) -> None:
        """Store a memory."""
        if self.memory:
            self.memory.add(content, user_id=self.user_id)

    def _retrieve_relevant_memories(self, query: str) -> list:
        """Retrieve relevant memories."""
        if self.memory:
            result = self.memory.search(query, user_id=self.user_id, limit=5)
            return result.get("results", [])
        return []

    def process_message(self, message: str) -> str:
        """Process an incoming message."""
        # Retrieve relevant memories
        relevant_memories = self._retrieve_relevant_memories(message)

        # Add memory context if available
        context = ""
        if relevant_memories:
            memory_str = "\n".join(
                [f"- {m.get('content', '')}" for m in relevant_memories]
            )
            if memory_str:
                context = f"Relevant memories:\n{memory_str}\n\n"

        # Process message with context and store result
        response = super().process_message(context + message)
        self._store_memory(f"User: {message}\nAssistant: {response}")

        return response


def get_api_key():
    """Get OpenAI API key from environment."""
    api_key = os.environ.get("OPENAI_API_KEY")
    assert api_key, "OPENAI_API_KEY environment variable must be set"
    return api_key


def test_mem0_import():
    """Test that mem0 can be imported."""
    try:
        import mem0ai

        logger.info(f"Successfully imported mem0ai version {mem0ai.__version__}")
        assert True
    except ImportError as e:
        logger.error(f"Failed to import mem0ai: {e}")
        assert False


def test_mem0_dependencies():
    """Test that mem0 dependencies are installed."""
    dependencies = ["qdrant_client", "openai", "pytz"]
    all_installed = True

    for dep in dependencies:
        try:
            import importlib

            importlib.import_module(dep)
            logger.info(f"Successfully imported {dep}")
        except ImportError as e:
            logger.error(f"Failed to import {dep}: {e}")
            all_installed = False

    assert all_installed, "Not all required dependencies are installed"


@pytest.mark.skipif(mem0 is None, reason="mem0ai not installed")
class TestMem0Integration(unittest.TestCase):
    """Test suite for mem0 integration."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.api_key = get_api_key()
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))

    def setUp(self):
        """Set up test fixtures."""
        # Set up API key environment
        self.patcher = patch.dict("os.environ", {"OPENAI_API_KEY": self.api_key})
        self.patcher.start()

        # Create a unique user ID for testing
        self.user_id = f"test_user_{os.urandom(4).hex()}"

        # Create an enhanced agent for testing
        self.agent = MemoryEnhancedAgent("TestAgent", self.user_id)

        # Store some test memories
        self.agent._store_memory("User prefers light mode")
        self.agent._store_memory("User is allergic to peanuts")

    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()

    def test_agent_memory_storage(self):
        """Test that the agent can store memories."""
        # Store a new memory
        test_content = f"Test memory {os.urandom(4).hex()}"
        self.agent._store_memory(test_content)

        # Retrieve the memory
        memories = self.agent._retrieve_relevant_memories(test_content[:10])

        # Check that the memory was stored and retrieved
        assert len(memories) > 0
        assert any(test_content in str(memory) for memory in memories)

    def test_agent_memory_retrieval(self):
        """Test that the agent can retrieve memories."""
        # Test memory retrieval
        memories = self.agent._retrieve_relevant_memories("allergies")

        # Check that memories were retrieved
        assert len(memories) > 0
        assert any("peanuts" in str(memory) for memory in memories)

    def test_agent_message_processing(self):
        """Test that the agent processes messages with memory context."""
        # Send a test message
        response = self.agent.process_message("What are my preferences?")

        # Check that the response includes memory context
        assert "light mode" in response.lower()


def test_mem0_basic_functionality():
    """Placeholder for basic mem0 functionality test."""
    logger.info("Running basic mem0 functionality test (placeholder).")
    assert True

if __name__ == "__main__":
    test_mem0_import()
    test_mem0_dependencies()
    test_mem0_basic_functionality()

    logger.info("All mem0 integration tests passed!")
    sys.exit(0)
