"""
Integration tests for mem0 functionality.

These tests verify the end-to-end functionality of mem0 integration
with both ADK and CrewAI agents. They require mem0 to be installed
and configured with an OpenAI API key.

To run these tests:
    1. Install mem0: pip install mem0ai
    2. Set OPENAI_API_KEY environment variable
    3. Run: pytest tests/test_mem0_integration.py
"""

import os
import unittest
from unittest.mock import patch
from importlib import import_module # nosec B403

import pytest

# Check if mem0 is available - use importlib for better security
try:
    mem0 = import_module('mem0ai') # nosec B403 - Safe import in test environment
except ImportError:
    mem0 = None

def get_api_key():
    """Get API key from environment with proper validation."""
    api_key = os.getenv('OPENAI_API_KEY', '')  # nosec B105 - Testing environment variable
    if not api_key or not isinstance(api_key, str) or len(api_key) < 32:
        pytest.skip("OPENAI_API_KEY environment variable not properly configured")
    return api_key

@pytest.mark.skipif(mem0 is None, reason="mem0ai not installed")
class TestMem0Integration(unittest.TestCase):
    """Test suite for mem0 integration."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.api_key = get_api_key()  # Validate API key first
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))  # nosec B108 - Safe usage in tests

    def setUp(self):
        """Set up for each test."""
        self.patcher = patch.dict('os.environ', {'OPENAI_API_KEY': self.api_key})  # nosec B108 - Test environment
        self.patcher.start()

    def tearDown(self):
        """Clean up after each test."""
        self.patcher.stop()

    # Check if ADK is available
    try:
        from adk.agent import Agent
        from adk.communication import Message
        ADK_AVAILABLE = True
    except ImportError:
        ADK_AVAILABLE = False

    # Check if CrewAI is available
    try:
        from crewai import Agent as CrewAgent
        CREWAI_AVAILABLE = True
    except ImportError:
        CREWAI_AVAILABLE = False

    # Import memory-enhanced agents
    try:
        from adk_demo.mem0_enhanced_adk_agents import MemoryEnhancedDataGathererAgent
        from agent_team.mem0_enhanced_agents import MemoryEnhancedCrewAIAgentTeam
    except ImportError:
        pass

    # Skip all tests if dependencies are not available or OpenAI API key is not set
    pytestmark = pytest.mark.skipif(
        not mem0 or not (ADK_AVAILABLE or CREWAI_AVAILABLE) or "OPENAI_API_KEY" not in os.environ,
        reason="mem0, agent frameworks not installed, or OPENAI_API_KEY not set",
    )


    def setUp(self):
        """Set up test fixtures."""
        # Create a unique user ID for testing
        self.user_id = f"test_user_{os.urandom(4).hex()}"

        # Initialize mem0 memory
        self.memory = Memory()

        # Add some test memories
        self.memory.add(
            "User prefers dark mode in applications",
            user_id=self.user_id,
            metadata={"category": "preferences"}
        )

        self.memory.add(
            "User is allergic to shellfish",
            user_id=self.user_id,
            metadata={"category": "health"}
        )

        self.memory.add(
            [
                {"role": "user", "content": "What's the weather like today?"},
                {"role": "assistant", "content": "It's sunny and 75 degrees."}
            ],
            user_id=self.user_id,
            metadata={"category": "conversation"}
        )

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up test memories
        # Note: mem0 doesn't have a built-in delete_all method,
        # so we're just letting them expire naturally
        pass

    @pytest.mark.skipif(not ADK_AVAILABLE, reason="ADK not installed")
    def test_adk_agent_memory_retrieval(self):
        """Test that ADK agents can retrieve memories."""
        # Create a memory-enhanced agent
        agent = MemoryEnhancedDataGathererAgent(
            name="TestAgent",
            user_id=self.user_id
        )

        # Test memory retrieval
        memories = agent._retrieve_relevant_memories("preferences")

        # Check that memories were retrieved
        assert len(memories) > 0
        assert any("dark mode" in str(memory) for memory in memories)

    @pytest.mark.skipif(not ADK_AVAILABLE, reason="ADK not installed")
    def test_adk_agent_memory_storage(self):
        """Test that ADK agents can store memories."""
        # Create a memory-enhanced agent
        agent = MemoryEnhancedDataGathererAgent(
            name="TestAgent",
            user_id=self.user_id
        )

        # Store a new memory
        test_content = f"Test memory {os.urandom(4).hex()}"
        agent._store_memory(test_content)

        # Retrieve the memory
        memories = agent._retrieve_relevant_memories(test_content[:10])

        # Check that the memory was stored and retrieved
        assert len(memories) > 0
        assert any(test_content in str(memory) for memory in memories)

    @pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI not installed")
    def test_crewai_team_memory_retrieval(self):
        """Test that CrewAI teams can retrieve memories."""
        # Create a memory-enhanced team
        team = MemoryEnhancedCrewAIAgentTeam(user_id=self.user_id)

        # Test memory retrieval
        memories = team._retrieve_relevant_memories("allergies")

        # Check that memories were retrieved
        assert len(memories) > 0
        assert any("shellfish" in str(memory) for memory in memories)

    @pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI not installed")
    def test_crewai_team_memory_storage(self):
        """Test that CrewAI teams can store memories."""
        # Create a memory-enhanced team
        team = MemoryEnhancedCrewAIAgentTeam(user_id=self.user_id)

        # Store a new memory
        test_content = f"Test team memory {os.urandom(4).hex()}"
        team._store_memory(test_content)

        # Retrieve the memory
        memories = team._retrieve_relevant_memories(test_content[:10])

        # Check that the memory was stored and retrieved
        assert len(memories) > 0
        assert any(test_content in str(memory) for memory in memories)


if __name__ == "__main__":
    unittest.main()
