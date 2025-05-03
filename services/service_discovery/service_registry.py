"""
Service registry interface for pAIssive income microservices.

This module defines the interface for service registry implementations,
along with common data structures and exceptions used for service discovery.
"""


import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional




@dataclass
class ServiceInstance:
    """Represents an instance of a service."""

    service_id: str
    service_name: str
    host: str
    port: int
    health_check_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    is_secure: bool = False
    tags: List[str] = field(default_factory=list)


class ServiceRegistrationError(Exception):
    """Exception raised when service registration fails."""

    pass


class ServiceDeregistrationError(Exception):
    """Exception raised when service deregistration fails."""

    pass


class ServiceLookupError(Exception):
    """Exception raised when service lookup fails."""

    pass


class ServiceHealthCheckError(Exception):
    """Exception raised when service health check fails."""

    pass


class ServiceRegistry(abc.ABC):
    """Interface for service registry implementations."""

    @abc.abstractmethod
    def register(self, service_instance: ServiceInstance) -> bool:
        """
        Register a service instance with the registry.

        Args:
            service_instance: The service instance to register

        Returns:
            bool: True if registration was successful, False otherwise

        Raises:
            ServiceRegistrationError: If registration fails
        """
        pass

    @abc.abstractmethod
    def deregister(self, service_id: str) -> bool:
        """
        Deregister a service instance from the registry.

        Args:
            service_id: The unique ID of the service to deregister

        Returns:
            bool: True if deregistration was successful, False otherwise

        Raises:
            ServiceDeregistrationError: If deregistration fails
        """
        pass

    @abc.abstractmethod
    def renew(self, service_id: str) -> bool:
        """
        Renew a service registration (for TTL-based checks).

        Args:
            service_id: The unique ID of the service to renew

        Returns:
            bool: True if renewal was successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_service(self, service_name: str) -> List[ServiceInstance]:
        """
        Get all instances of a service by name.

        Args:
            service_name: The name of the service to look up

        Returns:
            List[ServiceInstance]: All instances of the requested service

        Raises:
            ServiceLookupError: If lookup fails
        """
        pass

    @abc.abstractmethod
    def get_all_services(self) -> Dict[str, List[ServiceInstance]]:
        """
        Get all registered services.

        Returns:
            Dict[str, List[ServiceInstance]]: A dictionary mapping service names to lists of instances

        Raises:
            ServiceLookupError: If lookup fails
        """
        pass

    @abc.abstractmethod
    def get_service_health(self, service_id: str) -> bool:
        """
        Get the health status of a service instance.

        Args:
            service_id: The unique ID of the service to check

        Returns:
            bool: True if the service is healthy, False otherwise

        Raises:
            ServiceHealthCheckError: If health check lookup fails
        """
        pass