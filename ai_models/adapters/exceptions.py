"""Exception classes for the adapters package."""

class AdapterError(Exception):
    """Base class for adapter-related errors."""


class ModelContextProtocolError(AdapterError):
    """Raised when there are issues with the Model Context Protocol."""
    def __init__(self):
        super().__init__("modelcontextprotocol-python-sdk is not installed. Please install it with `uv pip install modelcontextprotocol-python-sdk`.")
