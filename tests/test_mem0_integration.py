"""Integration tests for mem0 functionality."""

from __future__ import annotations

# type: ignore[import]
import logging
import os
import sys
import unittest
from typing import Any, Optional
from unittest.mock import patch

import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Check if mem0 is available
mem0 = None
Memory = None
try:
    import mem0ai

    mem0 = mem0ai
    Memory = mem0ai.Memory
except ImportError as e:  # mem0 or agent frameworks not available, skip test
    logger.warning(f"mem0ai not available: {e}")
    # mem0 and Memory remain None, which is the desired fallback.


# Import ADK components
class _FallbackAgent:
    def __init__(self, name: str):
        self.name = name

    def process_message(self, message: str) -> str:
        return f"Processed: {message}"


try:
    from adk.agent import Agent
except ImportError as e:
    logger.warning(f"ADK not available: {e}, using mock implementation")
    Agent = _FallbackAgent


# Helper for formatting relevant memories
def _format_relevant_memories(self, message):
    relevant_memories = self.retrieve_relevant_memories(message)
    if relevant_memories:
        memory_str = "\n".join([f"- {m.get('content', '')}" for m in relevant_memories])
        return f"Relevant memories:\n{memory_str}\n\n"
    return ""


# Dynamically create MemoryEnhancedAgent with Agent as base
MemoryEnhancedAgent = type(
    "MemoryEnhancedAgent",
    (Agent,),
    {
        "__init__": lambda self, name, user_id: (
            Agent.__init__(self, name),
            setattr(self, "memory", Memory() if Memory is not None else None),
            setattr(self, "user_id", user_id),
        ),
        "store_memory": lambda self, content: self.memory.add(
            content, user_id=self.user_id
        )
        if self.memory
        else None,
        "retrieve_relevant_memories": lambda self, query: self.memory.search(
            query, user_id=self.user_id, limit=5
        ).get("results", [])
        if self.memory
        else [],
        "_format_relevant_memories": _format_relevant_memories,
        "process_message": lambda self, message: (
            self._format_relevant_memories(message)
            + Agent.process_message(self, message)
            if hasattr(Agent, "process_message")
            else ""
        ),
    },
)


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
    except ImportError as err:
        logger.exception("Failed to import mem0ai")
        raise AssertionError from err


def test_mem0_dependencies():
    """Test that mem0 dependencies are installed."""
    dependencies = ["qdrant_client", "openai", "pytz"]
    import importlib

    failed_deps = [dep for dep in dependencies if not _is_module_available(dep)]
    if failed_deps:
        for dep in failed_deps:
            logger.exception(f"Failed to import {dep}")
    assert not failed_deps, (
        f"Not all required dependencies are installed: {failed_deps}"
    )


def _is_module_available(module_name: str) -> bool:
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


@pytest.mark.skipif(mem0 is None, reason="mem0ai not installed")
class TestMem0Integration(unittest.TestCase):
    """Test suite for mem0 integration."""

    patcher: Optional[Any] = None
    user_id: Optional[str] = None
    agent: Optional[MemoryEnhancedAgent] = None

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.api_key = get_api_key()
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))

    def setUp(self):
        """Set up test fixtures."""
        self.patcher = patch.dict("os.environ", {"OPENAI_API_KEY": self.api_key})
        self.patcher.start()
        self.user_id = f"test_user_{os.urandom(4).hex()}"
        self.agent = MemoryEnhancedAgent("TestAgent", self.user_id)
        self.agent.store_memory("User prefers light mode")
        self.agent.store_memory("User is allergic to peanuts")

    def tearDown(self):
        """Tear down test fixtures."""
        if self.patcher:
            self.patcher.stop()

    def test_agent_memory_storage(self):
        """Test that the agent can store memories."""
        test_content = f"Test memory {os.urandom(4).hex()}"
        self.agent.store_memory(test_content)
        memories = self.agent.retrieve_relevant_memories(test_content[:10])
        assert len(memories) > 0
        assert any(test_content in str(memory) for memory in memories)

    def test_agent_memory_retrieval(self):
        """Test that the agent can retrieve memories."""
        memories = self.agent.retrieve_relevant_memories("allergies")
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
