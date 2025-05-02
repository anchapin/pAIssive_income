"""
Service discovery client for pAIssive income microservices.

This module provides a high-level client for microservices to register
themselves and discover other services in the system.
"""

import logging
import os
import socket
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple, Callable

from services.service_discovery.service_registry import (
    ServiceRegistry,
    ServiceInstance,
    ServiceRegistrationError,
    ServiceLookupError
)
from services.service_discovery.consul_registry import ConsulServiceRegistry
from services.service_discovery.load_balancer import (
    LoadBalancer, 
    RoundRobinStrategy,
    RandomStrategy
)

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
        is_secure: bool = False,
        load_balancer_strategy: str = "round_robin"
    ):
        """Initialize the service discovery client."""
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
        
        # Set up the load balancer
        self._setup_load_balancer(load_balancer_strategy)
        
        # Initialize service instance cache
        self._service_cache: Dict[str, Tuple[float, List[ServiceInstance]]] = {}
        self._cache_ttl = 10.0  # Cache TTL in seconds
        
        # Register this service if auto-register is True
        if auto_register and port > 0:
            self.register_self()
    
    def _setup_load_balancer(self, strategy_name: str) -> None:
        """Set up the load balancer with the specified strategy."""
        if strategy_name == "random":
            self.load_balancer = LoadBalancer(strategy=RandomStrategy())
        else:  # Default to round_robin
            self.load_balancer = LoadBalancer(strategy=RoundRobinStrategy())
        
        # Add a filter function that only selects healthy instances
        self.load_balancer.filter_function = lambda instance: self.registry.get_service_health(instance.service_id)
    
    def _get_local_ip(self) -> str:
        """Get the local IP address."""
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
        """Register this service with the registry."""
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
        """Deregister this service from the registry."""
        return self.registry.deregister(self.service_id)
    
    def discover_service(self, service_name: str) -> List[ServiceInstance]:
        """Discover instances of a service by name."""
        # Check if we have a recent cache entry
        now = time.time()
        if service_name in self._service_cache:
            timestamp, instances = self._service_cache[service_name]
            if now - timestamp < self._cache_ttl:
                return instances
        
        # Not in cache or cache expired, get from registry
        try:
            instances = self.registry.get_service(service_name)
            # Update cache
            self._service_cache[service_name] = (now, instances)
            return instances
        except ServiceLookupError as e:
            # If lookup fails but we have a cached version, use it
            if service_name in self._service_cache:
                logger.warning(
                    f"Service lookup failed for {service_name}, using cached data: {str(e)}"
                )
                return self._service_cache[service_name][1]
            raise
    
    def get_service_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Get a service instance, using load balancing to select one."""
        instances = self.discover_service(service_name)
        if not instances:
            logger.warning(f"No instances found for service: {service_name}")
            return None
        
        # Use load balancer to select an instance
        return self.load_balancer.select(instances)
    
    def get_service_url(self, service_name: str, path: str = "/") -> Optional[str]:
        """Get the URL for a service, automatically selecting an instance."""
        instance = self.get_service_instance(service_name)
        if not instance:
            return None
        
        # Build the URL
        protocol = "https" if instance.is_secure else "http"
        return f"{protocol}://{instance.host}:{instance.port}{path}"
    
    def discover_all_services(self) -> Dict[str, List[ServiceInstance]]:
        """Discover all registered services."""
        return self.registry.get_all_services()
    
    def is_service_healthy(self, service_name: str) -> bool:
        """Check if at least one instance of a service is healthy."""
        instances = self.discover_service(service_name)
        if not instances:
            return False
            
        for instance in instances:
            if self.registry.get_service_health(instance.service_id):
                return True
                
        return False
    
    def set_cache_ttl(self, ttl_seconds: float) -> None:
        """Set the time-to-live for the service instance cache."""
        self._cache_ttl = max(0.0, ttl_seconds)
    
    def clear_cache(self) -> None:
        """Clear the service instance cache."""
        self._service_cache.clear()
    
    def with_service(
        self, 
        service_name: str, 
        fallback_url: Optional[str] = None
    ) -> Callable[[str], Optional[str]]:
        """Return a function that builds URLs for the specified service."""
        def url_builder(path: str = "/") -> Optional[str]:
            url = self.get_service_url(service_name, path)
            if url is None and fallback_url:
                return f"{fallback_url.rstrip('/')}{path}"
            return url
        
        return url_builder