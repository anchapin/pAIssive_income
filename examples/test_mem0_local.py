"""
Test script for mem0 local installation.

This script demonstrates basic mem0 functionality using a local installation.
It requires the mem0ai package to be installed:

    pip install mem0ai

Note: This script requires an OpenAI API key to be set as an environment variable:
    export OPENAI_API_KEY='your-api-key'
"""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

try:
    from mem0 import Memory
except ImportError:
    logger.exception(
        "mem0ai package not installed. Please install it with: pip install mem0ai"
    )
    sys.exit(1)


def log_json(data: Any) -> None:
    """Logs data as formatted JSON."""
    logger.info(json.dumps(data, indent=2))


def test_basic_memory_operations() -> Optional[str]:
    """
    Tests basic memory operations: add, search, get_all.

    Returns:
        Optional[str]: Memory ID for further testing, or None if not available
    """
    logger.info("=== Testing Basic Memory Operations ===")

    # Initialize memory
    memory = Memory()
    user_id = "test_user"

    # Test adding a simple memory
    logger.info("Adding a simple memory...")
    result = memory.add(
        "I prefer dark mode in my applications and use VSCode as my primary editor.",
        user_id=user_id,
        metadata={"category": "preferences"},
    )
    logger.info("Result:")
    log_json(result)

    # Test adding conversation messages
    logger.info("Adding conversation messages...")
    messages = [
        {"role": "user", "content": "I'm allergic to shellfish."},
        {
            "role": "assistant",
            "content": "I'll remember that you have a shellfish allergy.",
        },
    ]
    result = memory.add(messages, user_id=user_id)
    logger.info("Result:")
    log_json(result)

    # Test searching for memories
    logger.info("Searching for memories about allergies...")
    search_result = memory.search("What food allergies do I have?", user_id=user_id)
    logger.info("Search result:")
    log_json(search_result)

    # Test getting all memories
    logger.info("Getting all memories...")
    all_memories = memory.get_all(user_id=user_id)
    logger.info("All memories:")
    log_json(all_memories)

    # Return the memory ID for further testing
    if (
        isinstance(all_memories, dict)
        and "results" in all_memories
        and all_memories["results"]
    ):
        first_result = all_memories["results"][0]
        if isinstance(first_result, dict):
            return first_result.get("id")

    logger.warning("No memory ID found for further testing")
    return None


def test_memory_updates(memory_id: Optional[str]) -> None:
    """Tests memory update and history operations."""
    if not memory_id:
        logger.warning("No memory ID available for update testing.")
        return

    logger.info("=== Testing Memory Updates and History ===")

    # Initialize memory
    memory = Memory()

    # Test updating a memory
    logger.info("Updating memory %s...", memory_id)
    update_result = memory.update(
        memory_id=memory_id,
        data="I prefer dark mode in all applications and use VSCode and PyCharm as my editors.",
    )
    logger.info("Update result:")
    log_json(update_result)

    # Test getting memory history
    logger.info("Getting memory history...")
    history_result = memory.history(memory_id=memory_id)
    logger.info("History result:")
    log_json(history_result)


def test_memory_deletion(user_id: str) -> None:
    """Tests memory deletion operations."""
    logger.info("=== Testing Memory Deletion ===")

    # Initialize memory
    memory = Memory()

    # Add a temporary memory for deletion testing
    logger.info("Adding a temporary memory for deletion testing...")
    result = memory.add(
        "This is a temporary memory that will be deleted.",
        user_id=user_id,
        metadata={"category": "temporary"},
    )

    memory_id = None
    if isinstance(result, dict):
        memory_id = result.get("id")

    if not memory_id:
        logger.warning("Failed to create temporary memory for deletion testing.")
        return

    # Test deleting a specific memory
    logger.info("Deleting memory %s...", memory_id)
    delete_result = memory.delete(memory_id=memory_id)
    logger.info("Delete result:")
    log_json(delete_result)

    # Note: Deleting all memories is not tested here to avoid accidental data loss


def main() -> None:
    """Runs all memory tests."""
    # Check if OpenAI API key is set
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        logger.exception("OPENAI_API_KEY environment variable not set.")
        logger.exception("mem0 requires an OpenAI API key to function properly.")
        logger.exception("Set it with: export OPENAI_API_KEY='your-api-key'")
        return

    # Run tests
    user_id = "test_user"
    memory_id = test_basic_memory_operations()
    test_memory_updates(memory_id)
    test_memory_deletion(user_id)

    logger.info("=== All Tests Completed ===")


if __name__ == "__main__":
    main()
