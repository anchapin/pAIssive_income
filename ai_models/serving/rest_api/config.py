"""
"""
Configuration for REST API server.
Configuration for REST API server.


This module provides configuration classes for the REST API server.
This module provides configuration classes for the REST API server.
"""
"""




from dataclasses import dataclass
from dataclasses import dataclass
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional


from ..server import ServerConfig, ServerProtocol
from ..server import ServerConfig, ServerProtocol




@dataclass
@dataclass
class RESTConfig(ServerConfig):
    class RESTConfig(ServerConfig):
    """
    """
    Configuration for REST API server.
    Configuration for REST API server.
    """
    """


    # Override default protocol
    # Override default protocol
    protocol: ServerProtocol = ServerProtocol.REST
    protocol: ServerProtocol = ServerProtocol.REST


    # REST-specific configuration
    # REST-specific configuration
    docs_url: str = "/docs"
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    redoc_url: str = "/redoc"


    # Middleware configuration
    # Middleware configuration
    enable_cors: bool = True
    enable_cors: bool = True
    enable_gzip: bool = True
    enable_gzip: bool = True
    enable_https: bool = False
    enable_https: bool = False


    # HTTPS configuration
    # HTTPS configuration
    ssl_keyfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_certfile: Optional[str] = None


    # Endpoint configuration
    # Endpoint configuration
    enable_text_generation: bool = True
    enable_text_generation: bool = True
    enable_text_classification: bool = False
    enable_text_classification: bool = False
    enable_embedding: bool = False
    enable_embedding: bool = False
    enable_image: bool = False
    enable_image: bool = False
    enable_audio: bool = False
    enable_audio: bool = False


    # Health check configuration
    # Health check configuration
    enable_health_check: bool = True
    enable_health_check: bool = True
    health_check_path: str = "/health"
    health_check_path: str = "/health"


    # Metrics configuration
    # Metrics configuration
    enable_metrics: bool = False
    enable_metrics: bool = False
    metrics_path: str = "/metrics"
    metrics_path: str = "/metrics"


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the configuration to a dictionary.
    Convert the configuration to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the configuration
    Dictionary representation of the configuration
    """
    """
    base_dict = super().to_dict()
    base_dict = super().to_dict()


    rest_dict = {
    rest_dict = {
    "docs_url": self.docs_url,
    "docs_url": self.docs_url,
    "openapi_url": self.openapi_url,
    "openapi_url": self.openapi_url,
    "redoc_url": self.redoc_url,
    "redoc_url": self.redoc_url,
    "enable_cors": self.enable_cors,
    "enable_cors": self.enable_cors,
    "enable_gzip": self.enable_gzip,
    "enable_gzip": self.enable_gzip,
    "enable_https": self.enable_https,
    "enable_https": self.enable_https,
    "ssl_keyfile": self.ssl_keyfile,
    "ssl_keyfile": self.ssl_keyfile,
    "ssl_certfile": self.ssl_certfile,
    "ssl_certfile": self.ssl_certfile,
    "enable_text_generation": self.enable_text_generation,
    "enable_text_generation": self.enable_text_generation,
    "enable_text_classification": self.enable_text_classification,
    "enable_text_classification": self.enable_text_classification,
    "enable_embedding": self.enable_embedding,
    "enable_embedding": self.enable_embedding,
    "enable_image": self.enable_image,
    "enable_image": self.enable_image,
    "enable_audio": self.enable_audio,
    "enable_audio": self.enable_audio,
    "enable_health_check": self.enable_health_check,
    "enable_health_check": self.enable_health_check,
    "health_check_path": self.health_check_path,
    "health_check_path": self.health_check_path,
    "enable_metrics": self.enable_metrics,
    "enable_metrics": self.enable_metrics,
    "metrics_path": self.metrics_path,
    "metrics_path": self.metrics_path,
    }
    }


    return {**base_dict, **rest_dict}
    return {**base_dict, **rest_dict}


    @classmethod
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "RESTConfig":
    def from_dict(cls, config_dict: Dict[str, Any]) -> "RESTConfig":
    """
    """
    Create a configuration from a dictionary.
    Create a configuration from a dictionary.


    Args:
    Args:
    config_dict: Dictionary with configuration parameters
    config_dict: Dictionary with configuration parameters


    Returns:
    Returns:
    REST server configuration
    REST server configuration
    """
    """
    # Set protocol to REST
    # Set protocol to REST
    config_dict["protocol"] = ServerProtocol.REST.value
    config_dict["protocol"] = ServerProtocol.REST.value


    # Create configuration using parent method
    # Create configuration using parent method
    return super().from_dict(config_dict)
    return super().from_dict(config_dict)