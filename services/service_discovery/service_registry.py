"""
"""
Service registry interface for pAIssive income microservices.
Service registry interface for pAIssive income microservices.


This module defines the interface for service registry implementations,
This module defines the interface for service registry implementations,
along with common data structures and exceptions used for service discovery.
along with common data structures and exceptions used for service discovery.
"""
"""


import abc
import abc
from dataclasses import dataclass, field
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional




@dataclass
@dataclass
class ServiceInstance:
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

    pass


    class ServiceDeregistrationError(Exception):

    pass


    class ServiceLookupError(Exception):

    pass


    class ServiceHealthCheckError(Exception):


    pass
    pass




    class ServiceRegistry(abc.ABC):
    class ServiceRegistry(abc.ABC):


    @abc.abstractmethod
    @abc.abstractmethod
    def register(self, service_instance: ServiceInstance) -> bool:
    def register(self, service_instance: ServiceInstance) -> bool:
    """
    """
    Register a service instance with the registry.
    Register a service instance with the registry.


    Args:
    Args:
    service_instance: The service instance to register
    service_instance: The service instance to register


    Returns:
    Returns:
    bool: True if registration was successful, False otherwise
    bool: True if registration was successful, False otherwise


    Raises:
    Raises:
    ServiceRegistrationError: If registration fails
    ServiceRegistrationError: If registration fails
    """
    """
    pass
    pass


    @abc.abstractmethod
    @abc.abstractmethod
    def deregister(self, service_id: str) -> bool:
    def deregister(self, service_id: str) -> bool:
    """
    """
    Deregister a service instance from the registry.
    Deregister a service instance from the registry.


    Args:
    Args:
    service_id: The unique ID of the service to deregister
    service_id: The unique ID of the service to deregister


    Returns:
    Returns:
    bool: True if deregistration was successful, False otherwise
    bool: True if deregistration was successful, False otherwise


    Raises:
    Raises:
    ServiceDeregistrationError: If deregistration fails
    ServiceDeregistrationError: If deregistration fails
    """
    """
    pass
    pass


    @abc.abstractmethod
    @abc.abstractmethod
    def renew(self, service_id: str) -> bool:
    def renew(self, service_id: str) -> bool:
    """
    """
    Renew a service registration (for TTL-based checks).
    Renew a service registration (for TTL-based checks).


    Args:
    Args:
    service_id: The unique ID of the service to renew
    service_id: The unique ID of the service to renew


    Returns:
    Returns:
    bool: True if renewal was successful, False otherwise
    bool: True if renewal was successful, False otherwise
    """
    """
    pass
    pass


    @abc.abstractmethod
    @abc.abstractmethod
    def get_service(self, service_name: str) -> List[ServiceInstance]:
    def get_service(self, service_name: str) -> List[ServiceInstance]:
    """
    """
    Get all instances of a service by name.
    Get all instances of a service by name.


    Args:
    Args:
    service_name: The name of the service to look up
    service_name: The name of the service to look up


    Returns:
    Returns:
    List[ServiceInstance]: All instances of the requested service
    List[ServiceInstance]: All instances of the requested service


    Raises:
    Raises:
    ServiceLookupError: If lookup fails
    ServiceLookupError: If lookup fails
    """
    """
    pass
    pass


    @abc.abstractmethod
    @abc.abstractmethod
    def get_all_services(self) -> Dict[str, List[ServiceInstance]]:
    def get_all_services(self) -> Dict[str, List[ServiceInstance]]:
    """
    """
    Get all registered services.
    Get all registered services.


    Returns:
    Returns:
    Dict[str, List[ServiceInstance]]: A dictionary mapping service names to lists of instances
    Dict[str, List[ServiceInstance]]: A dictionary mapping service names to lists of instances


    Raises:
    Raises:
    ServiceLookupError: If lookup fails
    ServiceLookupError: If lookup fails
    """
    """
    pass
    pass


    @abc.abstractmethod
    @abc.abstractmethod
    def get_service_health(self, service_id: str) -> bool:
    def get_service_health(self, service_id: str) -> bool:
    """
    """
    Get the health status of a service instance.
    Get the health status of a service instance.


    Args:
    Args:
    service_id: The unique ID of the service to check
    service_id: The unique ID of the service to check


    Returns:
    Returns:
    bool: True if the service is healthy, False otherwise
    bool: True if the service is healthy, False otherwise


    Raises:
    Raises:
    ServiceHealthCheckError: If health check lookup fails
    ServiceHealthCheckError: If health check lookup fails
    """
    """
    pass
    pass

