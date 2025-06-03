# Mock mock_mcp module for CI
__version__ = "0.1.0"

<<<<<<< HEAD
class MockMCPClient: pass
class Client: pass
class Server: pass
def connect(*args, **kwargs) -> None: pass
def disconnect(*args, **kwargs) -> None: pass
=======
__version__ = "1.0.0"

import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class MockMCPClient:
    """Mock implementation of MCP Client."""

    def __init__(self, host: str = "localhost", port: int = 8080, **kwargs):
        """Initialize mock MCP client."""
        self.host = host
        self.port = port
        self.connected = False
        self.tools = []
        self.kwargs = kwargs
        logger.info(f"Initialized mock MCP client for {host}:{port}")

    async def connect(self) -> bool:
        """Mock connect method."""
        self.connected = True
        logger.info("Mock MCP client connected")
        return True

    def connect_sync(self) -> bool:
        """Synchronous connect method."""
        self.connected = True
        logger.info("Mock MCP client connected (sync)")
        return True

    async def disconnect(self) -> None:
        """Mock disconnect method."""
        self.connected = False
        logger.info("Mock MCP client disconnected")

    def disconnect_sync(self) -> None:
        """Synchronous disconnect method."""
        self.connected = False
        logger.info("Mock MCP client disconnected (sync)")

    async def list_tools(self) -> list[dict[str, Any]]:
        """Mock list_tools method."""
        logger.info("Mock MCP list_tools called")
        return [
            {
                "name": "mock_tool_1",
                "description": "Mock tool for testing",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "mock_tool_2",
                "description": "Another mock tool",
                "parameters": {"type": "object", "properties": {}}
            }
        ]

    def list_tools_sync(self) -> list[dict[str, Any]]:
        """Synchronous list_tools method."""
        logger.info("Mock MCP list_tools called (sync)")
        return [
            {
                "name": "mock_tool_1",
                "description": "Mock tool for testing",
                "parameters": {"type": "object", "properties": {}}
            }
        ]

    async def call_tool(self, name: str, arguments: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Mock call_tool method."""
        logger.info(f"Mock MCP call_tool: {name} with args: {arguments}")
        return {
            "result": f"Mock result for tool {name}",
            "success": True,
            "tool_name": name,
            "arguments": arguments or {}
        }

    def call_tool_sync(self, name: str, arguments: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Synchronous call_tool method."""
        logger.info(f"Mock MCP call_tool: {name} with args: {arguments} (sync)")
        return {
            "result": f"Mock result for tool {name}",
            "success": True,
            "tool_name": name,
            "arguments": arguments or {}
        }

    async def send_message(self, message: Union[str, dict[str, Any]]) -> dict[str, Any]:
        """Mock send_message method."""
        logger.info(f"Mock MCP send_message: {message}")
        return {
            "response": f"Mock response to: {message}",
            "success": True
        }

    def send_message_sync(self, message: Union[str, dict[str, Any]]) -> dict[str, Any]:
        """Synchronous send_message method."""
        logger.info(f"Mock MCP send_message: {message} (sync)")
        return {
            "response": f"Mock response to: {message}",
            "success": True
        }

    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self.connected

    def __enter__(self):
        """Context manager entry."""
        self.connect_sync()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect_sync()


class MockMCPServer:
    """Mock implementation of MCP Server."""

    def __init__(self, name: str = "mock_server", **kwargs):
        """Initialize mock MCP server."""
        self.name = name
        self.running = False
        self.tools = {}
        self.kwargs = kwargs
        logger.info(f"Initialized mock MCP server: {name}")

    async def start(self) -> None:
        """Start the mock server."""
        self.running = True
        logger.info(f"Mock MCP server {self.name} started")

    async def stop(self) -> None:
        """Stop the mock server."""
        self.running = False
        logger.info(f"Mock MCP server {self.name} stopped")

    def register_tool(self, name: str, func: callable, description: str = "") -> None:
        """Register a tool with the server."""
        self.tools[name] = {
            "function": func,
            "description": description
        }
        logger.info(f"Registered tool {name} with mock MCP server")

    def is_running(self) -> bool:
        """Check if server is running."""
        return self.running


# Mock the main MCP classes
Client = MockMCPClient
Server = MockMCPServer

# Create module-level instance for backward compatibility
mcp = MockMCPClient()

# Export all mock classes
__all__ = [
    "Client",
    "MockMCPClient",
    "MockMCPServer",
    "Server",
    "__version__",
    "mcp"
]

logger.info("Mock MCP module loaded successfully")
>>>>>>> b36cd36ce22c7f6f5b640c325729079e36e4e609
