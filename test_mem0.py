"""
Simple test script to verify mem0 installation and functionality.

This script tests basic mem0 operations to ensure it's working correctly.
"""

import os
import sys

try:
    from mem0 import Memory
    print("mem0 imported successfully!")
except ImportError as e:
    print(f"Error importing mem0: {e}")
    sys.exit(1)

def test_mem0_basic_operations():
    """Test basic mem0 operations."""
    try:
        # Initialize memory
        memory = Memory()
        print("Memory initialized successfully!")

        # Add a test memory
        user_id = "test_user"
        test_memory = "This is a test memory for mem0 verification."

        result = memory.add(test_memory, user_id=user_id)
        print(f"Memory added successfully: {result}")

        # Search for the memory
        search_results = memory.search("test memory", user_id=user_id, limit=5)

        if search_results:
            print(f"Memory search successful! Found results: {search_results}")
            return True
        else:
            print("Memory search returned no results.")
            return False

    except Exception as e:
        print(f"Error testing mem0: {e}")
        return False

if __name__ == "__main__":
    # Check if OpenAI API key is set (required by mem0)
    if "OPENAI_API_KEY" not in os.environ:
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("mem0 requires an OpenAI API key to function properly.")
        print("Set it with: export OPENAI_API_KEY='your-api-key'")
        print("Continuing with test anyway...")

    # Run the test
    success = test_mem0_basic_operations()

    if success:
        print("\n✅ mem0 is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ mem0 test failed.")
        sys.exit(1)
