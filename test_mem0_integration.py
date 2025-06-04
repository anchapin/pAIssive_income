"""Test script to verify mem0 integration."""

from __future__ import annotations

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_mem0_import() -> bool | None:
    """Test that mem0 can be imported."""
    try:
        import mem0  # nosec B404  # Safe: test-only import, not user-supplied

        logger.info("Successfully imported mem0 version %s", mem0.__version__)
    except ImportError:
        logger.exception("Failed to import mem0")
        return False
    else:
        return True


def test_mem0_dependencies() -> bool:
    """Test that mem0 dependencies are installed."""
    dependencies = ["qdrant_client", "openai", "pytz"]
    import importlib

    def is_importable(dep: str) -> bool:
        try:
            importlib.import_module(dep)  # nosec B403
            logger.info("Successfully imported %s", dep)
        except ImportError:
            return False
        else:
            return True

    failed_deps = [dep for dep in dependencies if not is_importable(dep)]
    all_installed = not failed_deps
    for dep in failed_deps:
        logger.exception("Failed to import %s", dep)
    if not all_installed:
        logger.error("Not all required dependencies are installed")
    return all_installed


def test_mem0_basic_functionality() -> bool | None:
    """Test basic mem0 functionality."""
    try:
        import mem0  # nosec B404  # Safe: test-only import, not user-supplied

        mem0.Memory()  # nosec B106  # Safe: test-only instantiation
        logger.info("Successfully created Memory instance")
    except Exception:
        logger.exception("Failed to test basic mem0 functionality")
        return False
    else:
        return True


if __name__ == "__main__":
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
