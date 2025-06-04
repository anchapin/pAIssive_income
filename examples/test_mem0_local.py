"""
Test script for mem0 local installation.

This script demonstrates basic mem0 functionality using a local installation.
It requires the mem0ai package to be installed:

    pip install mem0ai

Note: This script requires an OpenAI API key to be set as an environment variable:
    export OPENAI_API_KEY='your-api-key'
"""

from __future__ import annotations

import os
import sys
from typing import Any

try:
    from mem0 import Memory
except ImportError:
    sys.exit(1)


def print_json(data: Any) -> None:
    """Print data as formatted JSON."""


def test_basic_memory_operations() -> None:
    """Test basic memory operations: add, search, get_all."""
    # Initialize memory
    memory = Memory()
    user_id = "test_user"

    # Test adding a simple memory
    result = memory.add(
        "I prefer dark mode in my applications and use VSCode as my primary editor.",
        user_id=user_id,
        metadata={"category": "preferences"},
    )
    print_json(result)

    # Test adding conversation messages
    messages = [
        {"role": "user", "content": "I'm allergic to shellfish."},
        {
            "role": "assistant",
            "content": "I'll remember that you have a shellfish allergy.",
        },
    ]
    result = memory.add(messages, user_id=user_id)
    print_json(result)

    # Test searching for memories
    search_result = memory.search("What food allergies do I have?", user_id=user_id)
    print_json(search_result)

    # Test getting all memories
    all_memories = memory.get_all(user_id=user_id)
    print_json(all_memories)

    # Return the memory ID for further testing
    return all_memories.get("results", [{}])[0].get("id")


def test_memory_updates(memory_id: str | None) -> None:
    """Test memory update and history operations."""
    if not memory_id:
        return

    # Initialize memory
    memory = Memory()

    # Test updating a memory
    update_result = memory.update(
        memory_id=memory_id,
        data="I prefer dark mode in all applications and use VSCode and PyCharm as my editors.",
    )
    print_json(update_result)

    # Test getting memory history
    history_result = memory.history(memory_id=memory_id)
    print_json(history_result)


def test_memory_deletion(user_id: str) -> None:
    """Test memory deletion operations."""
    # Initialize memory
    memory = Memory()

    # Add a temporary memory for deletion testing
    result = memory.add(
        "This is a temporary memory that will be deleted.",
        user_id=user_id,
        metadata={"category": "temporary"},
    )
    memory_id = result.get("id")

    if not memory_id:
        return

    # Test deleting a specific memory
    delete_result = memory.delete(memory_id=memory_id)
    print_json(delete_result)

    # Test deleting all memories for a user
    # Commented out to avoid accidentally deleting all memories
    # print(f"\nDeleting all memories for user {user_id}...")
    # delete_all_result = memory.delete_all(user_id=user_id)
    # print("Delete all result:")
    # print_json(delete_all_result)


def main() -> None:
    """Main function to run all tests."""
    # Check if OpenAI API key is set
    if "OPENAI_API_KEY" not in os.environ:
        return

    # Run tests
    user_id = "test_user"
    memory_id = test_basic_memory_operations()
    test_memory_updates(memory_id)
    test_memory_deletion(user_id)


if __name__ == "__main__":
    main()
