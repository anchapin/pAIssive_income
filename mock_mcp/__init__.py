"""Mock MCP module for testing."""

from __future__ import annotations


class MockMCPClient:
    """Mock MCP client for testing."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """
        Initialize MockMCPClient.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        """
        # Store args and kwargs to avoid unused argument warnings
        self._args = args
        self._kwargs = kwargs
        self.connected = False

    async def connect(self) -> bool:
        """Mock connect method."""
        self.connected = True
        return True

    async def disconnect(self) -> None:
        """Mock disconnect method."""
        self.connected = False

    async def call_tool(
        self, name: str, arguments: dict[str, object] | None = None
    ) -> dict[str, str]:
        """Mock tool call method."""
        # Store arguments to avoid unused argument warnings
        self._last_arguments = arguments
        return {"result": f"Mock result for {name}"}


class MockMCPServer:
    """Mock MCP server for testing."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """
        Initialize MockMCPServer.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        """
        # Store args and kwargs to avoid unused argument warnings
        self._args = args
        self._kwargs = kwargs
        self.running = False

    async def start(self) -> bool:
        """Mock start method."""
        self.running = True
        return True

    async def stop(self) -> None:
        """Mock stop method."""
        self.running = False


# Mock functions
def create_client(*args: object, **kwargs: object) -> MockMCPClient:
    """Create a mock MCP client."""
    return MockMCPClient(*args, **kwargs)


def create_server(*args: object, **kwargs: object) -> MockMCPServer:
    """Create a mock MCP server."""
    return MockMCPServer(*args, **kwargs)
