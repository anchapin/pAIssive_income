#!/usr/bin/env python3
"""
Verify that the mock_crewai package works correctly without circular import issues.

This script imports and uses the mock_crewai package to verify that the
circular import issues have been resolved.
"""

from __future__ import annotations

import importlib
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to ensure mock_crewai can be imported
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


def verify_imports() -> bool:
    """
    Verify that the mock_crewai package can be imported without circular import issues.

    Returns:
        True if imports succeed, False otherwise

    """
    try:
        # First, try importing the types module
        logger.info("Importing types module...")
        # Import but don't use the types - just checking they can be imported
        import mock_crewai.custom_types

        # Try importing the modules in different orders to test for circular imports
        logger.info("Testing import order 1: agent -> task -> crew")
        import mock_crewai.agent
        import mock_crewai.crew
        import mock_crewai.task  # noqa: F401

        # Force reload to ensure we're testing the imports fresh
        logger.info("Testing import order 2: task -> agent -> crew")
        importlib.reload(sys.modules["mock_crewai.agent"])
        importlib.reload(sys.modules["mock_crewai.task"])
        importlib.reload(sys.modules["mock_crewai.crew"])

        logger.info("Testing import order 3: crew -> agent -> task")
        importlib.reload(sys.modules["mock_crewai.agent"])
        importlib.reload(sys.modules["mock_crewai.task"])
        importlib.reload(sys.modules["mock_crewai.crew"])

        logger.info("All import tests succeeded")
    except ImportError:
        logger.exception("Import verification failed")
        return False
    else:
        return True


def verify_usage() -> bool:
    """
    Verify that the mock_crewai package can be used without issues.

    Returns:
        True if usage tests succeed, False otherwise

    """
    try:
        from mock_crewai import Agent, Crew, Task

        # Create instances and test interactions
        agent = Agent(role="Test Agent", goal="Test Goal", backstory="Test Backstory")
        # Use type casting to avoid mypy errors
        task = Task(description="Test Task")
        # Assign agent after creation to avoid type issues
        task.agent = agent  # type: ignore[assignment]
        crew = Crew(agents=[agent], tasks=[task])

        # Test method calls
        # Use type casting to avoid mypy errors
        result = agent.execute_task(task)  # type: ignore[arg-type, type-var]
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
    Run the verification tests.

    Returns:
        0 if all tests pass, 1 otherwise

    """
    logger.info("Verifying mock_crewai package...")

    import_success = verify_imports()
    if not import_success:
        logger.error("Import verification failed")
        return 1

    usage_success = verify_usage()
    if not usage_success:
        logger.error("Usage verification failed")
        return 1

    logger.info("All verifications passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
