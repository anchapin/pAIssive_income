"""
Service discovery client for pAIssive income microservices.

This module provides a high-level client for microservices to register
themselves and discover other services in the system.
"""

import logging
import os
import socket
import uuid
from typing import Dict, List, Optional, Any, Tuple

from services.service_discovery.service_registry import (
    ServiceRegistry,
    ServiceInstance,
    ServiceRegistrationError,
    ServiceLookupError
)
from services.service_discovery.consul_registry import ConsulServiceRegistry

# Set up logging
logger = logging.getLogger(__name__)


class ServiceDiscoveryClient:
    """High-level client for service discovery operations."""
    
    def __init__(
        self,
        service_name: str,
        host: Optional[str] = None,
        port: int = 0,
        version: str = "1.0.0",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        health_check_url: str = "/health",
        registry_host: str = "localhost",
        registry_port: int = 8500,
        auto_register: bool = True,
        is_secure: bool = False
    ):
        """
        Initialize the service discovery client.
        
        Args:
            service_name: The name of this service
            host: Host address where this service runs (default: auto-detect)
            port: Port where this service runs
            version: Service version (default: "1.0.0")
            tags: List of tags for this service (optional)
            metadata: Additional metadata for this service (optional)
            health_check_url: URL path for health checks (default: "/health")
            registry_host: Hostname of the service registry (default: "localhost")
            registry_port: Port of the service registry (default: 8500)
            auto_register: Whether to register this service automatically (default: True)
            is_secure: Whether this service uses HTTPS (default: False)
        """
        self.service_name = service_name
        self.port = port
        self.version = version
        self.tags = tags or []
        self.metadata = metadata or {}
        self.health_check_url = health_check_url
        self.is_secure = is_secure
        
        # Generate a unique service ID
        self.service_id = f"{service_name}-{str(uuid.uuid4())[:8]}"
        
        # Auto-detect host if not provided
        if host is None:
            self.host = self._get_local_ip()
        else:
            self.host = host
            
        # Initialize the registry client
        self.registry = ConsulServiceRegistry(
            host=registry_host,
            port=registry_port
        )
        
        # Register this service if auto-register is True
        if auto_register and port > 0:
            self.register_self()
    
    def _get_local_ip(self) -> str:
        """
        Get the local IP address.
        
        Returns:
            str: The local IP address
        """
        try:
            # Create a socket to get the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Connect to Google DNS
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            logger.warning(f"Failed to get local IP: {str(e)}")
            # Fallback to localhost
            return "127.0.0.1"
    
    def register_self(self) -> bool:
        """
        Register this service with the registry.
        
        Returns:
            bool: True if registration was successful, False otherwise
            
        Raises:
            ServiceRegistrationError: If registration fails
        """
        instance = ServiceInstance(
            service_id=self.service_id,
            service_name=self.service_name,
            host=self.host,
            port=self.port,
            health_check_url=self.health_check_url,
            metadata=self.metadata,
            version=self.version,
            is_secure=self.is_secure,
            tags=self.tags
        )
        return self.registry.register(instance)
    
    def deregister_self(self) -> bool:
        """
        Deregister this service from the registry.
        
        Returns:
            bool: True if deregistration was successful, False otherwise
        """
        return self.registry.deregister(self.service_id)
    
    def discover_service(self, service_name: str) -> List[ServiceInstance]:
        """
        Discover instances of a service by name.
        
        Args:
            service_name: The name of the service to discover
            
        Returns:
            List[ServiceInstance]: All instances of the requested service
            
        Raises:
            ServiceLookupError: If lookup fails
        """
        return self.registry.get_service(service_name)
    
    def get_service_url(self, service_name: str, path: str = "/") -> Optional[str]:
        """
        Get the URL for a service, automatically selecting an instance.
        
        Args:
            service_name: The name of the service
            path: The path to append to the URL (default: "/")
            
        Returns:
            Optional[str]: The URL for the service, or None if no instances found
        """
        instances = self.discover_service(service_name)
        
        if not instances:
            logger.warning(f"No instances found for service: {service_name}")
            return None
        
        # Use the first instance (in a production system, you might want to implement load balancing here)
        instance = instances[0]
        
        # Build the URL
        protocol = "https" if instance.is_secure else "http"
        return f"{protocol}://{instance.host}:{instance.port}{path}"
    
    def discover_all_services(self) -> Dict[str, List[ServiceInstance]]:
        """
        Discover all registered services.
        
        Returns:
            Dict[str, List[ServiceInstance]]: A dictionary mapping service names to lists of instances
        """
        return self.registry.get_all_services()
    
    def is_service_healthy(self, service_name: str) -> bool:
        """
        Check if at least one instance of a service is healthy.
        
        Args:
            service_name: The name of the service to check
            
        Returns:
            bool: True if at least one instance is healthy, False otherwise
        """
        instances = self.discover_service(service_name)
        if not instances:
            return False
            
        for instance in instances:
            if self.registry.get_service_health(instance.service_id):
                return True
                
        return False