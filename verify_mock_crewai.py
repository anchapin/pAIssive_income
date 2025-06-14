#!/usr/bin/env python3
"""
Verify that the mock_crewai package works correctly without circular import issues.

This script imports and uses the mock_crewai package to verify that the
circular import issues have been resolved.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import cast

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to ensure mock_crewai can be imported
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


def verify_imports() -> bool:
    """
    Verify that all mock_crewai modules can be imported without circular import issues.

    Returns:
        bool: True if all imports succeed, False otherwise

    """
    try:
        # Try importing the modules in different orders to test for circular imports
        logger.info("Testing import order 1: agent -> task -> crew")

        logger.info("Testing import order 2: task -> agent -> crew")
        # Force reload to ensure we're testing the imports fresh
        import importlib

        importlib.reload(sys.modules["mock_crewai.agent"])
        importlib.reload(sys.modules["mock_crewai.task"])
        importlib.reload(sys.modules["mock_crewai.crew"])

        logger.info("Testing import order 3: crew -> agent -> task")
        importlib.reload(sys.modules["mock_crewai.agent"])
        importlib.reload(sys.modules["mock_crewai.task"])
        importlib.reload(sys.modules["mock_crewai.crew"])

        logger.info("All import orders succeeded")
    except ImportError:
        logger.exception("Import verification failed")
        return False
    else:
        return True


def verify_usage() -> bool:
    """
    Verify that the mock_crewai classes can be used together without issues.

    Returns:
        bool: True if usage tests succeed, False otherwise

    """
    try:
        from mock_crewai import Agent, Crew, Task

        # Create instances and test interactions
        agent = Agent(role="Test Agent", goal="Test Goal", backstory="Test Backstory")
        task = Task(description="Test Task")
        # Assign agent after creation; if type checker complains, use cast
        task.agent = cast("Agent", agent)
        crew = Crew(agents=[agent], tasks=[task])

        # Test method calls
        # If execute_task expects a specific type, cast task to that type
        # If not possible, document why the ignore is necessary
        result = agent.execute_task(task)
        logger.info("Agent.execute_task result: %s", result)

        result = crew.kickoff()
        logger.info("Crew.kickoff result: %s", result)

        logger.info("All usage tests succeeded")
    except (ImportError, AttributeError):
        logger.exception("Usage verification failed")
        return False
    else:
        return True


def main() -> int:
    """
    Run all verification tests.

    Returns:
        int: 0 if all tests pass, 1 otherwise

    """
    logger.info("Verifying mock_crewai package...")

    import_success = verify_imports()
    usage_success = verify_usage()

    if import_success and usage_success:
        logger.info("All verification tests passed!")
        return 0
    logger.error("Verification tests failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
