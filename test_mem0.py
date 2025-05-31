"""
Simple test script to verify mem0 installation and functionality.

This script tests basic mem0 operations to ensure it's working correctly.
"""

from __future__ import annotations

import os
import sys

from logging_config import configure_logging

try:
    from mem0 import Memory
except ImportError:
    sys.exit(1)

def test_mem0_basic_operations() -> bool | None:
    """Test basic mem0 operations."""
    try:
        # Initialize memory
        memory = Memory()

        # Add a test memory
        user_id = "test_user"
        test_memory = "This is a test memory for mem0 verification."

        memory.add(test_memory, user_id=user_id)

        # Search for the memory
        search_results = memory.search("test memory", user_id=user_id, limit=5)

        return bool(search_results)

    except Exception:
        return False

if __name__ == "__main__":
    configure_logging()
    # Check if OpenAI API key is set (required by mem0)
    if "OPENAI_API_KEY" not in os.environ:
        pass

    # Run the test
    success = test_mem0_basic_operations()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)
