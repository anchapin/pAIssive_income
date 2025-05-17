"""conftest - Module for tests.ai_models.adapters.conftest.

This conftest file is specific to the MCP adapter tests and avoids loading the main conftest.py
which has dependencies on Flask and other components not needed for these tests.
"""

import sys
import os
import logging
import pytest
from unittest.mock import MagicMock, patch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Create a mock modelcontextprotocol module if it doesn't exist
try:
    import modelcontextprotocol
    logger.info(f"Found modelcontextprotocol module: {modelcontextprotocol}")
except ImportError:
    logger.info("modelcontextprotocol module not found, creating mock")

    # Create a mock modelcontextprotocol module
    class MockClient:
        def __init__(self, endpoint, **kwargs):
            self.endpoint = endpoint
            self.kwargs = kwargs

        def connect(self):
            logger.info(f"Mock connect to {self.endpoint}")

        def disconnect(self):
            logger.info(f"Mock disconnect from {self.endpoint}")

        def send_message(self, message):
            logger.info(f"Mock send message: {message[:50]}...")
            return f"Mock response to: {message[:20]}..."

    # Create the mock module
    class MockMCP:
        def __init__(self):
            self.Client = MockClient
            self.__version__ = "0.1.0-mock"

    # Add the mock module to sys.modules
    sys.modules["modelcontextprotocol"] = MockMCP()
    logger.info("Added mock modelcontextprotocol module to sys.modules")


@pytest.fixture
def mock_mcp():
    """Mock the modelcontextprotocol module."""
    with patch("ai_models.adapters.mcp_adapter.mcp") as mock_mcp:
        mock_client = MagicMock()
        mock_mcp.Client.return_value = mock_client
        mock_mcp.__version__ = "0.1.0-mock"
        yield mock_mcp


@pytest.fixture
def mock_logger():
    """Mock the logger."""
    with patch("ai_models.adapters.mcp_adapter.logger") as mock_logger:
        yield mock_logger
