"""Mock MCP module for testing environments."""

class MockClient:
    """Mock MCP client for testing."""
    
    def __init__(self, url):
        self.url = url
        self.connected = False
    
    def connect(self):
        """Mock connect method."""
        self.connected = True
        return True
    
    def disconnect(self):
        """Mock disconnect method."""
        self.connected = False
    
    def send_message(self, message):
        """Mock send_message method."""
        return f"Mock response to: {message}"

# Mock the main mcp module
class MockMCP:
    """Mock MCP module."""
    Client = MockClient

# Create module-level instance
mcp = MockMCP()
