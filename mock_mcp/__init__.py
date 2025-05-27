"""Mock MCP module for testing environments."""

# Mock MCP module for CI environments
class MockMCPClient:
    def __init__(self, *args, **kwargs):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

    def list_tools(self):
        return []

    def call_tool(self, name, arguments=None):
        return {"result": "mock"}

# Mock the main MCP classes
Client = MockMCPClient

# Create module-level instance
mcp = MockMCPClient()
