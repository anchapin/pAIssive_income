"""
mock_aiohttp - Module for ai_models.mock_aiohttp.

This module provides mock implementations of aiohttp classes for testing
when the actual aiohttp package is not available.
"""

# Standard library imports
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)


# Configure logging

# Third-party imports

# Local imports

__version__ = "3.9.0-mock"

class ClientResponse:
    """Mock implementation of aiohttp.ClientResponse."""

    def __init__(self, status: int = 200, content: str = "", json_data: Optional[Dict[str, Any]] = None):
        """
        Initialize the mock client response.
        
        Args:
            status: HTTP status code
            content: Response content as string
            json_data: Response data as JSON-serializable dict

        """
        self.status = status
        self._content = content
        self._json_data = json_data or {}
        self.closed = False

    async def text(self) -> str:
        """
        Get the response content as text.
        
        Returns:
            Response content as string

        """
        return self._content

    async def json(self) -> Dict[str, Any]:
        """
        Get the response content as JSON.
        
        Returns:
            Response data as dict

        """
        return self._json_data

    async def __aenter__(self):
        """Enter the async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager."""
        self.closed = True

class ClientSession:
    """Mock implementation of aiohttp.ClientSession."""

    def __init__(self, timeout: Optional[Any] = None):
        """
        Initialize the mock client session.
        
        Args:
            timeout: Request timeout (ignored in mock)

        """
        self.closed = False
        self.timeout = timeout
        logger.info("Initialized mock ClientSession")

    @asynccontextmanager
    async def get(self, url: str, **kwargs) -> AsyncIterator[ClientResponse]:
        """
        Make a GET request.
        
        Args:
            url: Request URL
            **kwargs: Additional request parameters
            
        Yields:
            Mock client response

        """
        logger.info(f"Mock GET request to {url}")
        yield ClientResponse(
            status=200,
            json_data={"models": [{"name": "mock-model-1"}, {"name": "mock-model-2"}]}
        )

    @asynccontextmanager
    async def post(self, url: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> AsyncIterator[ClientResponse]:
        """
        Make a POST request.
        
        Args:
            url: Request URL
            json: Request JSON data
            **kwargs: Additional request parameters
            
        Yields:
            Mock client response

        """
        logger.info(f"Mock POST request to {url}")
        if "generate" in url:
            yield ClientResponse(
                status=200,
                json_data={"model": json.get("model", "unknown"), "response": "Mock response", "done": True}
            )
        elif "chat" in url:
            yield ClientResponse(
                status=200,
                json_data={
                    "model": json.get("model", "unknown"),
                    "message": {"role": "assistant", "content": "Mock chat response"}
                }
            )
        else:
            yield ClientResponse(status=200, json_data={"status": "success"})

    async def close(self):
        """Close the session."""
        logger.info("Closing mock ClientSession")
        self.closed = True

class ClientTimeout:
    """Mock implementation of aiohttp.ClientTimeout."""

    def __init__(self, total: Optional[float] = None):
        """
        Initialize the mock client timeout.
        
        Args:
            total: Total timeout in seconds

        """
        self.total = total
