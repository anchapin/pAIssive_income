"""
Simple test script to verify mem0 installation and functionality.

This script tests basic mem0 operations to ensure it's working correctly.
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from mem0 import Memory

    logger.info("mem0 imported successfully!")
except ImportError:
    logger.exception("Error importing mem0")
    sys.exit(1)


def test_mem0_basic_operations() -> bool:
    """Test basic mem0 operations."""
    try:
        # Initialize memory
        memory = Memory()
        logger.info("Memory initialized successfully!")

        # Add a test memory
        user_id = "test_user"
        test_memory = "This is a test memory for mem0 verification."

        result = memory.add(test_memory, user_id=user_id)
        logger.info("Memory added successfully: %s", result)

        # Search for the memory
        search_results = memory.search("test memory", user_id=user_id, limit=5)

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
        logger.warning("OPENAI_API_KEY environment variable not set.")
        logger.warning("mem0 requires an OpenAI API key to function properly.")
        logger.warning("Set it with: export OPENAI_API_KEY='your-api-key'")
        logger.warning("Continuing with test anyway...")

    # Run the test
    success = test_mem0_basic_operations()

    if success:
        logger.info("✅ mem0 is working correctly!")
        sys.exit(0)
    else:
        logger.error("❌ mem0 test failed.")
        sys.exit(1)
