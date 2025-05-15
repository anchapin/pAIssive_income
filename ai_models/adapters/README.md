# AI Model Adapters

This directory contains adapter implementations for various AI model servers.

## Available Adapters

- **OllamaAdapter**: For connecting to Ollama servers
- **OpenAICompatibleAdapter**: For connecting to servers with OpenAI-compatible APIs
- **LMStudioAdapter**: For connecting to LM Studio servers
- **TensorRTAdapter**: For connecting to TensorRT servers
- **MCPAdapter**: For connecting to Model Context Protocol (MCP) servers

## MCP Adapter

The MCP adapter allows connecting to servers that implement the Model Context Protocol. This adapter requires the `modelcontextprotocol` Python SDK to be installed.

### Installation

The MCP SDK can be installed using pip:

```bash
pip install modelcontextprotocol-python-sdk
```

Or directly from GitHub:

```bash
git clone https://github.com/modelcontextprotocol/python-sdk.git
cd python-sdk
pip install -e .
```

### Usage

```python
from ai_models.adapters.adapter_factory import get_adapter

# Create an MCP adapter
adapter = get_adapter("mcp", host="localhost", port=9000)

# Connect to the server
adapter.connect()

# Send a message
response = adapter.send_message("Hello, world!")
print(response)

# Close the connection
adapter.close()
```

### Error Handling

The MCP adapter provides several exception classes for handling errors:

- `ModelContextProtocolError`: Raised when the MCP SDK is not installed
- `HostFormatError`: Raised when the host format is invalid
- `PortRangeError`: Raised when the port is outside the valid range
- `MCPConnectionError`: Raised when connection to the MCP server fails
- `MCPCommunicationError`: Raised when communication with the MCP server fails

### Testing

To run the MCP adapter tests:

```bash
pytest -v tests/ai_models/adapters/test_mcp_adapter.py
```

## Adapter Factory

The `adapter_factory.py` module provides a factory function for creating adapters:

```python
from ai_models.adapters.adapter_factory import get_adapter

# Create an adapter for a specific server type
adapter = get_adapter(server_type, host, port, **kwargs)
```

The `server_type` parameter can be one of:
- `"ollama"`: For Ollama servers
- `"openai"`: For OpenAI-compatible servers
- `"lmstudio"`: For LM Studio servers
- `"tensorrt"`: For TensorRT servers
- `"mcp"`: For MCP servers
