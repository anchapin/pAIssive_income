#!/usr/bin/env python
"""
Script to run MCP adapter tests without loading the main conftest.py.
This script is used by the CI/CD pipeline to run the MCP adapter tests.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def run_mcp_tests():
    """Run MCP adapter tests without loading the main conftest.py."""
    logger.info("Running MCP adapter tests...")

    # Set environment variables to avoid loading the main conftest.py
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(".")

    # Run the tests
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "--no-header",
        "--no-summary",
        "tests/ai_models/adapters/test_mcp_adapter.py",
        "tests/test_mcp_import.py",
        "tests/test_mcp_top_level_import.py",
        "-k",
        "not test_mcp_server",
        "--confcutdir=tests/ai_models/adapters",
        "--noconftest",
    ]

    try:
        result = subprocess.run(
            cmd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        return result.returncode
    except Exception as e:
        logger.exception(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(run_mcp_tests())
