"""
Service Discovery Interfaces

This module defines the core interfaces for the service discovery system.
"""

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class ServiceStatus(enum.Enum):
    """Enum representing the status of a service instance."""

    UNKNOWN = "unknown"
    STARTING = "starting"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STOPPED = "stopped"


@dataclass
class ServiceInstance:
    """
    Data class representing a service instance in the registry.
    """

    service_id: str
    host: str
    port: int
    instance_id: Optional[str] = None
    status: ServiceStatus = ServiceStatus.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)


class ServiceRegistry(ABC):
    """
    Interface for service registry implementations.

    A service registry manages the registration, deregistration, and discovery
    of service instances.
    """

    @abstractmethod
    def register(self, service: ServiceInstance) -> bool:
        """
        Register a service instance.

        Args:
            service: The service instance to register

        Returns:
            True if registration was successful, False otherwise
        """
        pass

    @abstractmethod
    def deregister(self, instance_id: str) -> bool:
        """
        Deregister a service instance.

        Args:
            instance_id: The instance ID to deregister

        Returns:
            True if deregistration was successful, False otherwise
        """
        pass

    @abstractmethod
    def renew(self, instance_id: str) -> bool:
        """
        Renew the registration of a service instance.

        Args:
            instance_id: The instance ID to renew

        Returns:
            True if renewal was successful, False otherwise
        """
        pass

    @abstractmethod
    def get_instance(self, instance_id: str) -> Optional[ServiceInstance]:
        """
        Get a specific service instance by ID.

        Args:
            instance_id: The instance ID to retrieve

        Returns:
            The service instance, or None if not found
        """
        pass

    @abstractmethod
    def get_instances(self, service_id: str) -> List[ServiceInstance]:
        """
        Get all instances of a specific service.

        Args:
            service_id: The service ID to look up

        Returns:
            List of service instances for the specified service
        """
        pass

    @abstractmethod
    def get_all_instances(self) -> Dict[str, List[ServiceInstance]]:
        """
        Get all registered service instances, grouped by service ID.

        Returns:
            Dictionary mapping service IDs to lists of service instances
        """
        pass

    @abstractmethod
    def update_status(self, instance_id: str, status: ServiceStatus) -> bool:
        """
        Update the status of a service instance.

        Args:
            instance_id: The instance ID to update
            status: The new status

        Returns:
            True if the update was successful, False otherwise
        """
        pass


class LoadBalancingStrategy(ABC):
    """
    Interface for load balancing strategies.

    A load balancing strategy selects a service instance from a list of available
    instances based on a specific algorithm.
    """

    @abstractmethod
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """
        Select an instance from the list of available instances.

        Args:
            instances: List of available service instances

        Returns:
            The selected instance, or None if no instances are available
        """
        pass


class ServiceDiscovery(ABC):
    """
    Interface for service discovery.

    Service discovery provides high-level methods for discovering and selecting
    service instances.
    """

    @abstractmethod
    def get_service(self, service_id: str) -> Optional[ServiceInstance]:
        """
        Get an instance of a service based on the configured load balancing strategy.

        Args:
            service_id: The service ID to look up

        Returns:
            A service instance, or None if no instances are available
        """
        pass

    @abstractmethod
    def get_all_services(self) -> List[str]:
        """
        Get a list of all known service IDs.

        Returns:
            List of service IDs
        """
        pass
