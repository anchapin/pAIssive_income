"""
"""
In-Memory Service Registry
In-Memory Service Registry


This module provides an in-memory implementation of the ServiceRegistry interface.
This module provides an in-memory implementation of the ServiceRegistry interface.
"""
"""




import time
import time
import uuid
import uuid
from typing import Dict, List, Optional
from typing import Dict, List, Optional


from .interfaces import ServiceInstance, ServiceRegistry, ServiceStatus
from .interfaces import ServiceInstance, ServiceRegistry, ServiceStatus




class InMemoryServiceRegistry:
    class InMemoryServiceRegistry:


    pass  # Added missing block
    pass  # Added missing block
    """
    """
    An in-memory implementation of ServiceRegistry.
    An in-memory implementation of ServiceRegistry.


    This implementation stores service instances in memory and is suitable
    This implementation stores service instances in memory and is suitable
    for development, testing, or single-node deployments.
    for development, testing, or single-node deployments.
    """
    """


    def __init__(self, heartbeat_timeout_seconds: int = 30):
    def __init__(self, heartbeat_timeout_seconds: int = 30):
    """
    """
    Initialize the in-memory service registry.
    Initialize the in-memory service registry.


    Args:
    Args:
    heartbeat_timeout_seconds: Number of seconds after which a service
    heartbeat_timeout_seconds: Number of seconds after which a service
    instance is considered unhealthy if not renewed
    instance is considered unhealthy if not renewed
    """
    """
    self._services: Dict[str, ServiceInstance] = {}
    self._services: Dict[str, ServiceInstance] = {}
    self._last_heartbeat: Dict[str, float] = {}
    self._last_heartbeat: Dict[str, float] = {}
    self._heartbeat_timeout = heartbeat_timeout_seconds
    self._heartbeat_timeout = heartbeat_timeout_seconds


    def register(self, service: ServiceInstance) -> bool:
    def register(self, service: ServiceInstance) -> bool:
    """
    """
    Register a service instance.
    Register a service instance.


    If the service doesn't have an instance_id, one will be generated.
    If the service doesn't have an instance_id, one will be generated.


    Args:
    Args:
    service: The service instance to register
    service: The service instance to register


    Returns:
    Returns:
    True if registration was successful
    True if registration was successful
    """
    """
    # Generate instance ID if not provided
    # Generate instance ID if not provided
    if not service.instance_id:
    if not service.instance_id:
    service.instance_id = f"{service.service_id}-{uuid.uuid4()}"
    service.instance_id = f"{service.service_id}-{uuid.uuid4()}"


    # Register the service
    # Register the service
    self._services[service.instance_id] = service
    self._services[service.instance_id] = service
    self._last_heartbeat[service.instance_id] = time.time()
    self._last_heartbeat[service.instance_id] = time.time()
    return True
    return True


    def deregister(self, instance_id: str) -> bool:
    def deregister(self, instance_id: str) -> bool:
    """
    """
    Deregister a service instance.
    Deregister a service instance.


    Args:
    Args:
    instance_id: The instance ID to deregister
    instance_id: The instance ID to deregister


    Returns:
    Returns:
    True if deregistration was successful, False if instance not found
    True if deregistration was successful, False if instance not found
    """
    """
    if instance_id in self._services:
    if instance_id in self._services:
    del self._services[instance_id]
    del self._services[instance_id]
    if instance_id in self._last_heartbeat:
    if instance_id in self._last_heartbeat:
    del self._last_heartbeat[instance_id]
    del self._last_heartbeat[instance_id]
    return True
    return True
    return False
    return False


    def renew(self, instance_id: str) -> bool:
    def renew(self, instance_id: str) -> bool:
    """
    """
    Renew the registration of a service instance.
    Renew the registration of a service instance.


    Args:
    Args:
    instance_id: The instance ID to renew
    instance_id: The instance ID to renew


    Returns:
    Returns:
    True if renewal was successful, False if instance not found
    True if renewal was successful, False if instance not found
    """
    """
    if instance_id in self._services:
    if instance_id in self._services:
    self._last_heartbeat[instance_id] = time.time()
    self._last_heartbeat[instance_id] = time.time()


    # Update status to healthy if it was unhealthy due to timeout
    # Update status to healthy if it was unhealthy due to timeout
    service = self._services[instance_id]
    service = self._services[instance_id]
    if service.status == ServiceStatus.UNHEALTHY:
    if service.status == ServiceStatus.UNHEALTHY:
    service.status = ServiceStatus.HEALTHY
    service.status = ServiceStatus.HEALTHY


    return True
    return True
    return False
    return False


    def get_instance(self, instance_id: str) -> Optional[ServiceInstance]:
    def get_instance(self, instance_id: str) -> Optional[ServiceInstance]:
    """
    """
    Get a specific service instance by ID.
    Get a specific service instance by ID.


    Args:
    Args:
    instance_id: The instance ID to retrieve
    instance_id: The instance ID to retrieve


    Returns:
    Returns:
    The service instance, or None if not found
    The service instance, or None if not found
    """
    """
    self._check_instance_health(instance_id)
    self._check_instance_health(instance_id)
    return self._services.get(instance_id)
    return self._services.get(instance_id)


    def get_instances(self, service_id: str) -> List[ServiceInstance]:
    def get_instances(self, service_id: str) -> List[ServiceInstance]:
    """
    """
    Get all instances of a specific service.
    Get all instances of a specific service.


    Args:
    Args:
    service_id: The service ID to look up
    service_id: The service ID to look up


    Returns:
    Returns:
    List of service instances for the specified service
    List of service instances for the specified service
    """
    """
    self._check_all_health()
    self._check_all_health()
    return [
    return [
    instance
    instance
    for instance in self._services.values()
    for instance in self._services.values()
    if instance.service_id == service_id
    if instance.service_id == service_id
    and instance.status == ServiceStatus.HEALTHY
    and instance.status == ServiceStatus.HEALTHY
    ]
    ]


    def get_all_instances(self) -> Dict[str, List[ServiceInstance]]:
    def get_all_instances(self) -> Dict[str, List[ServiceInstance]]:
    """
    """
    Get all registered service instances, grouped by service ID.
    Get all registered service instances, grouped by service ID.


    Returns:
    Returns:
    Dictionary mapping service IDs to lists of service instances
    Dictionary mapping service IDs to lists of service instances
    """
    """
    self._check_all_health()
    self._check_all_health()
    result: Dict[str, List[ServiceInstance]] = {}
    result: Dict[str, List[ServiceInstance]] = {}


    for instance in self._services.values():
    for instance in self._services.values():
    if instance.service_id not in result:
    if instance.service_id not in result:
    result[instance.service_id] = []
    result[instance.service_id] = []
    result[instance.service_id].append(instance)
    result[instance.service_id].append(instance)


    return result
    return result


    def update_status(self, instance_id: str, status: ServiceStatus) -> bool:
    def update_status(self, instance_id: str, status: ServiceStatus) -> bool:
    """
    """
    Update the status of a service instance.
    Update the status of a service instance.


    Args:
    Args:
    instance_id: The instance ID to update
    instance_id: The instance ID to update
    status: The new status
    status: The new status


    Returns:
    Returns:
    True if the update was successful, False otherwise
    True if the update was successful, False otherwise
    """
    """
    if instance_id in self._services:
    if instance_id in self._services:
    self._services[instance_id].status = status
    self._services[instance_id].status = status
    return True
    return True
    return False
    return False


    def _check_instance_health(self, instance_id: str) -> None:
    def _check_instance_health(self, instance_id: str) -> None:
    """
    """
    Check if a service instance is still healthy based on its last heartbeat.
    Check if a service instance is still healthy based on its last heartbeat.


    Args:
    Args:
    instance_id: The instance ID to check
    instance_id: The instance ID to check
    """
    """
    if instance_id in self._services and instance_id in self._last_heartbeat:
    if instance_id in self._services and instance_id in self._last_heartbeat:
    instance = self._services[instance_id]
    instance = self._services[instance_id]
    last_heartbeat = self._last_heartbeat[instance_id]
    last_heartbeat = self._last_heartbeat[instance_id]


    if instance.status == ServiceStatus.HEALTHY:
    if instance.status == ServiceStatus.HEALTHY:
    # Mark as unhealthy if heartbeat timeout exceeded
    # Mark as unhealthy if heartbeat timeout exceeded
    if time.time() - last_heartbeat > self._heartbeat_timeout:
    if time.time() - last_heartbeat > self._heartbeat_timeout:
    instance.status = ServiceStatus.UNHEALTHY
    instance.status = ServiceStatus.UNHEALTHY


    def _check_all_health(self) -> None:
    def _check_all_health(self) -> None:
    """Check the health status of all registered instances."""
    for instance_id in list(self._services.keys()):
    self._check_instance_health(instance_id)