"""Exception classes for the adapters package."""


class AdapterError(Exception):
    """Base class for adapter-related errors."""


class ModelContextProtocolError(AdapterError):
    """Raised when there are issues with the Model Context Protocol."""

    MESSAGE = (
        "modelcontextprotocol package is not installed. "
        "This package has been made optional due to heavy dependencies. "
        "To enable MCP functionality, install it separately with: "
        "`pip install modelcontextprotocol` or `uv add modelcontextprotocol`"
    )

    def __init__(self) -> None:
        """Initialize the error with a standard message."""
        super().__init__(self.MESSAGE)
