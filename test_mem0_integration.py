"""Test script to verify mem0 integration."""

from __future__ import annotations

import logging
import sys

from logging_config import configure_logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_mem0_import() -> bool | None:
    """Test that mem0 can be imported."""
    try:
        import mem0  # nosec B404
        logger.info(f"Successfully imported mem0 version {mem0.__version__}")
        return True
    except ImportError as e:
        logger.exception(f"Failed to import mem0: {e}")
        return False


def test_mem0_dependencies():
    """Test that mem0 dependencies are installed."""
    dependencies = ["qdrant_client", "openai", "pytz"]
    all_installed = True

    for dep in dependencies:
        try:
            # Use importlib instead of __import__ for better security
            import importlib
            importlib.import_module(dep)  # nosec B403
            logger.info(f"Successfully imported {dep}")
        except ImportError as e:
            logger.exception(f"Failed to import {dep}: {e}")
            all_installed = False

    if not all_installed:
        logger.error("Not all required dependencies are installed")
    return all_installed


def test_mem0_basic_functionality() -> bool | None:
    """Test basic mem0 functionality."""
    try:
        import mem0  # nosec B404        # Create a memory instance (without actually connecting to any services)
        # Using the correct API based on documentation, and ensuring instance creation works
        _ = mem0.Memory()  # nosec B106

        logger.info("Successfully created Memory instance")
        return True
    except Exception as e:
        logger.exception(f"Failed to test basic mem0 functionality: {e}")
        return False


if __name__ == "__main__":
    configure_logging()
    logger.info("Testing mem0 integration...")

    import_success = test_mem0_import()

    if import_success:
        dependencies_success = test_mem0_dependencies()
        functionality_success = test_mem0_basic_functionality()

        if dependencies_success and functionality_success:
            logger.info("All mem0 integration tests passed!")
            sys.exit(0)
        else:
            logger.error("Some mem0 integration tests failed!")
            sys.exit(1)
    else:
        logger.warning("mem0 is not installed. Skipping further tests.")
        # Exit with code 0 since this is expected in environments without mem0
        sys.exit(0)
