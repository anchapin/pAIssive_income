#!/usr/bin/env python
"""
Wrapper script to run MCP adapter tests.

This script is a wrapper around scripts/run/run_mcp_tests.py to maintain backward compatibility
with existing workflows that expect run_mcp_tests.py to be in the root directory.
"""

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
        import logging

        # Create a named logger instead of using the root logger
        logger = logging.getLogger("run_mcp_tests")

        # Use string formatting instead of f-string
        logger.error("Script not found at %s", script_path)
        return 1

    # Execute the script with the same arguments
    # We use subprocess.run instead of os.execv for better security
    # This still ensures that the return code is properly propagated
    import subprocess

    # Validate script_path to ensure it's not from untrusted input
    # Convert to absolute path and ensure it's within the expected directory
    abs_script_path = script_path.resolve()
    expected_dir = (Path(__file__).parent / "scripts" / "run").resolve()

    if not abs_script_path.startswith(expected_dir):
        import logging

        logger = logging.getLogger("run_mcp_tests")
        logger.error("Invalid script path: not in expected directory")
        return 1

    # Use a list of arguments to avoid shell injection
    cmd = [sys.executable, str(script_path)] + sys.argv[1:]

    # We've validated script_path is within our expected directory
    # and we're using a list of arguments to avoid shell injection
    # ruff: noqa: S603
    result = subprocess.run(  # nosec B603
        cmd,
        check=False,
        shell=False,  # Explicitly set shell=False for security
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
