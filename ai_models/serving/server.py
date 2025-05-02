"""
Base server interface for AI models.

This module provides the base interface for model servers.
"""

import abc
import enum
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ServerProtocol(enum.Enum):
    """
    Enumeration of server protocols.
    """

    REST = "rest"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    CUSTOM = "custom"


@dataclass
class ServerConfig:
    """
    Configuration for model servers.
    """

    # Basic configuration
    protocol: ServerProtocol = ServerProtocol.REST
    host: str = "0.0.0.0"
    port: int = 8000

    # Model configuration
    model_path: str = ""
    model_type: str = "text-generation"
    model_id: str = ""

    # Server configuration
    workers: int = 1
    timeout: int = 60
    max_batch_size: int = 4
    max_request_size: int = 1024 * 1024  # 1 MB

    # Security configuration
    enable_auth: bool = False
    api_keys: List[str] = field(default_factory=list)
    cors_origins: List[str] = field(default_factory=lambda: ["*"])

    # Rate limiting
    enable_rate_limit: bool = False
    rate_limit: int = 60  # requests per minute

    # Logging configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Additional parameters
    additional_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "protocol": self.protocol.value,
            "host": self.host,
            "port": self.port,
            "model_path": self.model_path,
            "model_type": self.model_type,
            "model_id": self.model_id,
            "workers": self.workers,
            "timeout": self.timeout,
            "max_batch_size": self.max_batch_size,
            "max_request_size": self.max_request_size,
            "enable_auth": self.enable_auth,
            "api_keys": self.api_keys,
            "cors_origins": self.cors_origins,
            "enable_rate_limit": self.enable_rate_limit,
            "rate_limit": self.rate_limit,
            "log_level": self.log_level,
            "log_file": self.log_file,
            **self.additional_params,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "ServerConfig":
        """
        Create a configuration from a dictionary.

        Args:
            config_dict: Dictionary with configuration parameters

        Returns:
            Server configuration
        """
        # Extract protocol
        protocol_str = config_dict.pop("protocol", "rest")
        try:
            protocol = ServerProtocol(protocol_str)
        except ValueError:
            protocol = ServerProtocol.REST

        # Extract additional parameters
        additional_params = {}
        for key, value in list(config_dict.items()):
            if key not in cls.__annotations__:
                additional_params[key] = config_dict.pop(key)

        # Create configuration
        config = cls(protocol=protocol, **config_dict)

        config.additional_params = additional_params
        return config


class ModelServer(abc.ABC):
    """
    Base class for model servers.
    """

    def __init__(self, config: ServerConfig):
        """
        Initialize the model server.

        Args:
            config: Server configuration
        """
        self.config = config
        self.model = None
        self.tokenizer = None

        # Set up logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """
        Set up logging for the server.
        """
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)

        # Add file handler if log file is specified
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(log_level)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    @abc.abstractmethod
    def load_model(self) -> None:
        """
        Load the model for serving.
        """
        pass

    @abc.abstractmethod
    def start(self) -> None:
        """
        Start the server.
        """
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        """
        Stop the server.
        """
        pass

    @abc.abstractmethod
    def is_running(self) -> bool:
        """
        Check if the server is running.

        Returns:
            True if the server is running, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the server.

        Returns:
            Dictionary with server information
        """
        pass
