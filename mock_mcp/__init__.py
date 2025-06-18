"""Mock MCP module for testing."""


class MockMCPClient:
    """Mock MCP client for testing."""

    def __init__(self, *args, **kwargs):
        self.connected = False

    async def connect(self):
        """Mock connect method."""
        self.connected = True
        return True

    async def disconnect(self):
        """Mock disconnect method."""
        self.connected = False

    async def call_tool(self, name, arguments=None):
        """Mock tool call method."""
        return {"result": f"Mock result for {name}"}


class MockMCPServer:
    """Mock MCP server for testing."""

    def __init__(self, *args, **kwargs):
        self.running = False

    async def start(self):
        """Mock start method."""
        self.running = True
        return True

    async def stop(self):
        """Mock stop method."""
        self.running = False


# Mock functions
def create_client(*args, **kwargs):
    """Create a mock MCP client."""
    return MockMCPClient(*args, **kwargs)


def create_server(*args, **kwargs):
    """Create a mock MCP server."""
    return MockMCPServer(*args, **kwargs)
