#!/usr/bin/env python
"""
Wrapper script to run MCP adapter tests.

This script is a wrapper around scripts/run/run_mcp_tests.py to maintain backward compatibility
with existing workflows that expect run_mcp_tests.py to be in the root directory.
"""

import os
import sys
from pathlib import Path

def main() -> int:
    """
    Run the MCP adapter tests by calling the script in its new location.
    
    Returns:
        int: The return code from the test run (0 for success, non-zero for failure)
    """
    # Get the path to the actual script
    script_path = Path(__file__).parent / "scripts" / "run" / "run_mcp_tests.py"
    
    # Check if the script exists
    if not script_path.exists():
        print(f"Error: Script not found at {script_path}")
        return 1
    
    # Execute the script with the same arguments
    # We use execv to replace the current process with the new one
    # This ensures that the return code is properly propagated
    os.execv(sys.executable, [sys.executable, str(script_path)] + sys.argv[1:])
    
    # This line will never be reached due to execv, but it's here for completeness
    return 0

if __name__ == "__main__":
    sys.exit(main())
