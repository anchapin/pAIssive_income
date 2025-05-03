"""
Configuration for gRPC server.

This module provides configuration classes for the gRPC server.
"""


from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..server import ServerConfig, ServerProtocol




@dataclass
class GRPCConfig(ServerConfig):
    """
    Configuration for gRPC server.
    """

    # Override default protocol
    protocol: ServerProtocol = ServerProtocol.GRPC

    # gRPC-specific configuration
    max_message_length: int = 100 * 1024 * 1024  # 100 MB
    max_concurrent_rpcs: int = 100
    enable_reflection: bool = True
    enable_health_checking: bool = True

    # TLS configuration
    enable_tls: bool = False
    tls_key_file: Optional[str] = None
    tls_cert_file: Optional[str] = None

    # Service configuration
    enable_text_generation: bool = True
    enable_text_classification: bool = False
    enable_embedding: bool = False
    enable_image: bool = False
    enable_audio: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        base_dict = super().to_dict()

        grpc_dict = {
            "max_message_length": self.max_message_length,
            "max_concurrent_rpcs": self.max_concurrent_rpcs,
            "enable_reflection": self.enable_reflection,
            "enable_health_checking": self.enable_health_checking,
            "enable_tls": self.enable_tls,
            "tls_key_file": self.tls_key_file,
            "tls_cert_file": self.tls_cert_file,
            "enable_text_generation": self.enable_text_generation,
            "enable_text_classification": self.enable_text_classification,
            "enable_embedding": self.enable_embedding,
            "enable_image": self.enable_image,
            "enable_audio": self.enable_audio,
        }

        return {**base_dict, **grpc_dict}

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "GRPCConfig":
        """
        Create a configuration from a dictionary.

        Args:
            config_dict: Dictionary with configuration parameters

        Returns:
            gRPC server configuration
        """
        # Set protocol to gRPC
        config_dict["protocol"] = ServerProtocol.GRPC.value

        # Create configuration using parent method
        return super().from_dict(config_dict)