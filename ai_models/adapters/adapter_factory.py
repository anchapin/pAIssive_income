"""adapter_factory - Module for ai_models/adapters.adapter_factory."""

# Standard library imports
import logging
from typing import Optional, Type, Any

# Third-party imports

# Local imports
from .exceptions import AdapterError

# Configure logging
logger = logging.getLogger(__name__)


class UnsupportedServerTypeError(AdapterError):
    """Raised when an unsupported server type is provided."""

    MESSAGE_TEMPLATE = "Unsupported server type: {server_type}"

    def __init__(self, server_type: str):
        message = self.MESSAGE_TEMPLATE.format(server_type=server_type)
        super().__init__(message)


class MCPAdapterNotAvailableError(AdapterError):
    """Raised when MCP adapter is not available."""

    MESSAGE = "MCPAdapter missing. Install mcp-use and ensure the file exists."

    def __init__(self):
        super().__init__(self.MESSAGE)


# Try to import adapters
# These will be properly imported from their respective modules
# If imports fail, they will be None
try:
    from .base_adapter import BaseModelAdapter
except ImportError:
    BaseModelAdapter = None

try:
    from .ollama_adapter import OllamaAdapter
except ImportError:
    OllamaAdapter = None

try:
    from .lmstudio_adapter import LMStudioAdapter
except ImportError:
    LMStudioAdapter = None

try:
    from .openai_compatible_adapter import OpenAICompatibleAdapter
except ImportError:
    OpenAICompatibleAdapter = None

try:
    from .tensorrt_adapter import TensorRTAdapter
except ImportError:
    TensorRTAdapter = None

try:
    from .mcp_adapter import MCPAdapter
except ImportError:
    MCPAdapter = None


class AdapterFactory:
    """Factory class for creating model adapters."""

    # Registry of adapter types
    _adapter_registry = {}

    @classmethod
    def _initialize_registry(cls):
        """Initialize the adapter registry with available adapters."""
        registry = {}

        if OllamaAdapter is not None:
            registry["ollama"] = OllamaAdapter

        if LMStudioAdapter is not None:
            registry["lmstudio"] = LMStudioAdapter

        if OpenAICompatibleAdapter is not None:
            registry["openai"] = OpenAICompatibleAdapter

        if TensorRTAdapter is not None:
            registry["tensorrt"] = TensorRTAdapter

        if MCPAdapter is not None:
            registry["mcp"] = MCPAdapter

        cls._adapter_registry = registry

    @classmethod
    def register_adapter(cls, name: str, adapter_class: Any) -> None:
        """Register a new adapter type.

        Args:
            name: The name of the adapter type
            adapter_class: The adapter class to register
        """
        if not cls._adapter_registry:
            cls._initialize_registry()

        cls._adapter_registry[name] = adapter_class
        logger.info(f"Registered adapter type: {name}")

    @classmethod
    def create_adapter(cls, adapter_type: str, **kwargs) -> Any:
        """Create an adapter of the specified type.

        Args:
            adapter_type: The type of adapter to create
            **kwargs: Additional parameters to pass to the adapter constructor

        Returns:
            An instance of the specified adapter type

        Raises:
            MCPAdapterNotAvailableError: If MCP adapter is requested but not available
            UnsupportedServerTypeError: If server type is not supported
        """
        if not cls._adapter_registry:
            cls._initialize_registry()

        adapter_type = adapter_type.lower()
        adapter_class = cls._adapter_registry.get(adapter_type)

        if adapter_class is None:
            if adapter_type == "mcp" and MCPAdapter is None:
                raise MCPAdapterNotAvailableError()
            else:
                raise UnsupportedServerTypeError(adapter_type)

        try:
            adapter = adapter_class(**kwargs)
            logger.info(f"Created adapter of type: {adapter_type}")
            return adapter
        except Exception as e:
            logger.exception(f"Error creating adapter of type {adapter_type}: {e}")
            raise

    @classmethod
    def get_available_adapter_types(cls) -> list[str]:
        """Get a list of available adapter types.

        Returns:
            A list of registered adapter type names
        """
        if not cls._adapter_registry:
            cls._initialize_registry()

        return list(cls._adapter_registry.keys())
