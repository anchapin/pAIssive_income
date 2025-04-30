"""
Configuration for REST API server.

This module provides configuration classes for the REST API server.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union

from ..server import ServerConfig, ServerProtocol


@dataclass
class RESTConfig(ServerConfig):
    """
    Configuration for REST API server.
    """

    # Override default protocol
    protocol: ServerProtocol = ServerProtocol.REST

    # REST-specific configuration
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"

    # Middleware configuration
    enable_cors: bool = True
    enable_gzip: bool = True
    enable_https: bool = False

    # HTTPS configuration
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None

    # Endpoint configuration
    enable_text_generation: bool = True
    enable_text_classification: bool = False
    enable_embedding: bool = False
    enable_image: bool = False
    enable_audio: bool = False

    # Health check configuration
    enable_health_check: bool = True
    health_check_path: str = "/health"

    # Metrics configuration
    enable_metrics: bool = False
    metrics_path: str = "/metrics"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        base_dict = super().to_dict()

        rest_dict = {
            "docs_url": self.docs_url,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "enable_cors": self.enable_cors,
            "enable_gzip": self.enable_gzip,
            "enable_https": self.enable_https,
            "ssl_keyfile": self.ssl_keyfile,
            "ssl_certfile": self.ssl_certfile,
            "enable_text_generation": self.enable_text_generation,
            "enable_text_classification": self.enable_text_classification,
            "enable_embedding": self.enable_embedding,
            "enable_image": self.enable_image,
            "enable_audio": self.enable_audio,
            "enable_health_check": self.enable_health_check,
            "health_check_path": self.health_check_path,
            "enable_metrics": self.enable_metrics,
            "metrics_path": self.metrics_path,
        }

        return {**base_dict, **rest_dict}

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "RESTConfig":
        """
        Create a configuration from a dictionary.

        Args:
            config_dict: Dictionary with configuration parameters

        Returns:
            REST server configuration
        """
        # Set protocol to REST
        config_dict["protocol"] = ServerProtocol.REST.value

        # Create configuration using parent method
        return super().from_dict(config_dict)
