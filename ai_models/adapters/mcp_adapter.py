"""mcp_adapter - Module for ai_models/adapters.mcp_adapter."""

# Third-party imports
try:
    import mcp_use
except ImportError:
    mcp_use = None

# Example MCPAdapter class
class MCPAdapter:
    """
    Adapter for connecting to MCP servers using the mcp-use library.
    """

    def __init__(self, host: str, port: int, **kwargs):
        if mcp_use is None:
            raise ImportError("mcp-use library is not installed. Please install it with `pip install mcp-use`.")
        self.host = host
        self.port = port
        self.client = None
        self.kwargs = kwargs

    def connect(self):
        """
        Connect to the MCP server.
        """
        self.client = mcp_use.MCPClient(self.host, self.port, **self.kwargs)
        self.client.connect()

    def send_message(self, message: str) -> str:
        """
        Send a message to the MCP server and return the response.
        """
        if not self.client:
            self.connect()
        return self.client.send_message(message)

    def close(self):
        """
        Close the connection to the MCP server.
        """
        if self.client:
            self.client.close()
            self.client = None