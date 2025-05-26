"""
Simple test script to verify mem0 installation and functionality.

This script tests basic mem0 operations to ensure it's working correctly.
All credentials used are for testing only and are dynamically generated.
"""

from __future__ import annotations

import logging
import os
import sys
import uuid
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_test_memory() -> tuple[str, str]:
    """
    Generate test memory data with a random ID to avoid reuse.

    Returns:
        tuple[str, str]: Tuple of (user_id, test_memory_content)

    """
    unique_id = uuid.uuid4().hex[:8]
    user_id = f"test_user_{unique_id}"
    test_memory = f"Test memory {unique_id} for mem0 verification."
    return user_id, test_memory


def test_mem0_basic_operations() -> bool:
    """
    Test basic mem0 operations.

    Returns:
        bool: True if tests pass, False otherwise

    """
    try:
        # Import mem0 (defined here to keep import error handling close to usage)
        try:
            from mem0 import Memory

            logger.info("mem0 imported successfully!")
        except ImportError:
            logger.exception("Error importing mem0")
            return False

        # Initialize memory
        memory = Memory()
        logger.info("Memory initialized successfully!")

        # Add a test memory with unique ID to prevent credential reuse
        user_id, test_memory = generate_test_memory()

        result = memory.add(test_memory, user_id=user_id)
        logger.info("Memory added successfully: %s", result)

        # Search for the memory
        search_results: Any = memory.search("test memory", user_id=user_id, limit=5)

        if search_results:
            logger.info("Memory search successful! Found results: %s", search_results)
            return True
        logger.warning("Memory search returned no results.")
        return False

    except Exception:
        logger.exception("Error testing mem0")
        return False


if __name__ == "__main__":
    # Check if OpenAI API key is set (required by mem0)
    if "OPENAI_API_KEY" not in os.environ:
        logger.warning(
            "OPENAI_API_KEY environment variable not set. "
            "mem0 requires an OpenAI API key to function properly. "
            "Set it with: export OPENAI_API_KEY='your-api-key'"
        )
        logger.info("Continuing with test anyway...")

    # Run the test
    success = test_mem0_basic_operations()

    if success:
        logger.info("\n✅ mem0 is working correctly!")
        sys.exit(0)
    else:
        logger.error("\n❌ mem0 test failed.")
        sys.exit(1)
