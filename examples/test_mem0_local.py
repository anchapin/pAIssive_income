"""
Test script for mem0 local installation.

This script demonstrates basic mem0 functionality using a local installation.
It requires the mem0ai package to be installed:

    pip install mem0ai

Note: This script requires an OpenAI API key to be set as an environment variable:
    export OPENAI_API_KEY='your-api-key'
"""

import json
from __future__ import annotations

import json # Already imported, but good to ensure
import os
import sys
from typing import Any # Keep Any for print_json
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

try:
    from mem0 import Memory
except ImportError:
    logger.error("mem0ai package not installed. Please install it with: pip install mem0ai")
    sys.exit(1)


def print_json(data: Any) -> None:
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))


def test_basic_memory_operations() -> None:
    """Test basic memory operations: add, search, get_all."""
    logger.info("\n=== Testing Basic Memory Operations ===\n")

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
    print_json(result)

    # Test adding conversation messages
    logger.info("\nAdding conversation messages...")
    messages = [
        {"role": "user", "content": "I'm allergic to shellfish."},
        {
            "role": "assistant",
            "content": "I'll remember that you have a shellfish allergy.",
        },
    ]
    result = memory.add(messages, user_id=user_id)
    logger.info("Result:")
    print_json(result)

    # Test searching for memories
    logger.info("\nSearching for memories about allergies...")
    search_result = memory.search("What food allergies do I have?", user_id=user_id)
    logger.info("Search result:")
    print_json(search_result)

    # Test getting all memories
    logger.info("\nGetting all memories...")
    all_memories = memory.get_all(user_id=user_id)
    logger.info("All memories:")
    print_json(all_memories)

    # Return the memory ID for further testing
    return all_memories.get("results", [{}])[0].get("id")


def test_memory_updates(memory_id: str | None) -> None:
    """Test memory update and history operations."""
    if not memory_id:
        logger.warning("No memory ID available for update testing.")
        return

    logger.info("\n=== Testing Memory Updates and History ===\n")

    # Initialize memory
    memory = Memory()

    # Test updating a memory
    logger.info("Updating memory %s...", memory_id)
    update_result = memory.update(
        memory_id=memory_id,
        data="I prefer dark mode in all applications and use VSCode and PyCharm as my editors.",
    )
    logger.info("Update result:")
    print_json(update_result)

    # Test getting memory history
    logger.info("\nGetting memory history...")
    history_result = memory.history(memory_id=memory_id)
    logger.info("History result:")
    print_json(history_result)


def test_memory_deletion(user_id: str) -> None:
    """Test memory deletion operations."""
    logger.info("\n=== Testing Memory Deletion ===\n")

    # Initialize memory
    memory = Memory()

    # Add a temporary memory for deletion testing
    logger.info("Adding a temporary memory for deletion testing...")
    result = memory.add(
        "This is a temporary memory that will be deleted.",
        user_id=user_id,
        metadata={"category": "temporary"},
    )
    memory_id = result.get("id")

    if not memory_id:
        logger.warning("Failed to create temporary memory for deletion testing.")
        return

    # Test deleting a specific memory
    logger.info("\nDeleting memory %s...", memory_id)
    delete_result = memory.delete(memory_id=memory_id)
    logger.info("Delete result:")
    print_json(delete_result)

    # Test deleting all memories for a user
    # Commented out to avoid accidentally deleting all memories
    # logger.info("\nDeleting all memories for user %s...", user_id)
    # delete_all_result = memory.delete_all(user_id=user_id)
    # logger.info("Delete all result:")
    # print_json(delete_all_result)


def main() -> None:
    """Main function to run all tests."""
    # Check if OpenAI API key is set
    if "OPENAI_API_KEY" not in os.environ:
        logger.error("OPENAI_API_KEY environment variable not set.")
        logger.error("mem0 requires an OpenAI API key to function properly.")
        logger.error("Set it with: export OPENAI_API_KEY='your-api-key'")
        return

    # Run tests
    user_id = "test_user"
    memory_id = test_basic_memory_operations()
    test_memory_updates(memory_id)
    test_memory_deletion(user_id)

    logger.info("\n=== All Tests Completed ===\n")


if __name__ == "__main__":
    main()
