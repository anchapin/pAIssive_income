#!/usr/bin/env python3
"""
Setup script to ensure mock modules are properly registered in CI environments.
This script should be run early in CI workflows to prevent import errors.
"""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_mock_modules() -> None:
    """Set up mock modules for CI environment."""
    logger.info("Setting up mock modules for CI environment...")

    # Add current directory to Python path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

    # Import mock modules to register them in sys.modules
    try:
        import mock_crewai
        logger.info(f"✓ mock_crewai loaded (version: {mock_crewai.__version__})")

        # Verify crewai is now available
        import crewai
        logger.info("✓ crewai import now works via mock")

    except ImportError as e:
        logger.exception(f"✗ Failed to load mock_crewai: {e}")

    try:
        import mock_mcp
        logger.info(f"✓ mock_mcp loaded (version: {mock_mcp.__version__})")

        # Verify MCP imports work
        import mcp
        import modelcontextprotocol
        logger.info("✓ MCP imports now work via mock")

    except ImportError as e:
        logger.exception(f"✗ Failed to load mock_mcp: {e}")

    try:
        import mock_mem0
        logger.info(f"✓ mock_mem0 loaded (version: {mock_mem0.__version__})")

        # Verify mem0 imports work
        import mem0
        import mem0ai
        logger.info("✓ mem0 imports now work via mock")

    except ImportError as e:
        logger.exception(f"✗ Failed to load mock_mem0: {e}")

    logger.info("Mock module setup completed")


def verify_mock_functionality() -> bool | None:
    """Verify that mock modules work correctly."""
    logger.info("Verifying mock module functionality...")

    try:
        # Test CrewAI functionality
        import crewai
        agent = crewai.Agent(role="test", goal="test", backstory="test")
        task = crewai.Task(description="test task")
        crew = crewai.Crew(agents=[agent], tasks=[task])
        crew.kickoff()
        logger.info("✓ CrewAI mock functionality verified")

        # Test MCP functionality
        import mcp
        client = mcp.Client()
        client.connect_sync()
        client.list_tools_sync()
        logger.info("✓ MCP mock functionality verified")

        # Test mem0 functionality
        import mem0
        memory = mem0.Memory()
        memory.add("test content")
        memory.search("test")
        logger.info("✓ mem0 mock functionality verified")

        return True

    except Exception as e:
        logger.exception(f"✗ Mock functionality verification failed: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    setup_mock_modules()
    success = verify_mock_functionality()

    if success:
        logger.info("✅ All mock modules set up and verified successfully")
        sys.exit(0)
    else:
        logger.error("❌ Mock module setup or verification failed")
        sys.exit(1)
