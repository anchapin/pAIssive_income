"""mcp_adapter - Module for ai_models/adapters.mcp_adapter."""

# Third-party imports
try:
    import modelcontextprotocol as mcp
except ImportError:
    mcp = None

# Example MCPAdapter class
class MCPAdapter:
    """
    Adapter for connecting to MCP servers using the official modelcontextprotocol SDK.
    """

    def __init__(self, host: str, port: int, **kwargs):
        if mcp is None:
            raise ImportError("modelcontextprotocol-python-sdk is not installed. Please install it with `pip install modelcontextprotocol-python-sdk`.")
        self.host = host
        self.port = port
        self.client = None
        self.kwargs = kwargs

    def connect(self):
        """
        Connect to the MCP server.
        """
        endpoint = f"http://{self.host}:{self.port}"
        self.client = mcp.Client(endpoint, **self.kwargs)
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
            self.client.disconnect()
            self.client = None
