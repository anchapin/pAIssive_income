"""
"""
Consul-based service registry implementation for pAIssive income microservices.
Consul-based service registry implementation for pAIssive income microservices.


This module provides a Consul client implementation of the ServiceRegistry interface,
This module provides a Consul client implementation of the ServiceRegistry interface,
allowing microservices to register with Consul and discover other services.
allowing microservices to register with Consul and discover other services.
"""
"""




import logging
import logging
from typing import Dict, List, Optional
from typing import Dict, List, Optional


import consul
import consul


(
(
ServiceDeregistrationError,
ServiceDeregistrationError,
ServiceHealthCheckError,
ServiceHealthCheckError,
ServiceInstance,
ServiceInstance,
ServiceLookupError,
ServiceLookupError,
ServiceRegistrationError,
ServiceRegistrationError,
ServiceRegistry,
ServiceRegistry,
)
)


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class ConsulServiceRegistry(ServiceRegistry):
    class ConsulServiceRegistry(ServiceRegistry):
    """Consul implementation of the ServiceRegistry interface."""

    def __init__(
    self,
    host: str = "localhost",
    port: int = 8500,
    token: Optional[str] = None,
    scheme: str = "http",
    consistency: str = "default",
    dc: Optional[str] = None,
    verify: bool = True,
    ):
    """
    """
    Initialize the Consul service registry client.
    Initialize the Consul service registry client.


    Args:
    Args:
    host: Consul server hostname (default: localhost)
    host: Consul server hostname (default: localhost)
    port: Consul server port (default: 8500)
    port: Consul server port (default: 8500)
    token: ACL token (optional)
    token: ACL token (optional)
    scheme: http or https (default: http)
    scheme: http or https (default: http)
    consistency: Consul consistency mode (default, consistent, stale)
    consistency: Consul consistency mode (default, consistent, stale)
    dc: Datacenter to use (optional)
    dc: Datacenter to use (optional)
    verify: Verify SSL certificates (default: True)
    verify: Verify SSL certificates (default: True)
    """
    """
    self.host = host
    self.host = host
    self.port = port
    self.port = port


    try:
    try:
    self.consul = consul.Consul(
    self.consul = consul.Consul(
    host=host,
    host=host,
    port=port,
    port=port,
    token=token,
    token=token,
    scheme=scheme,
    scheme=scheme,
    consistency=consistency,
    consistency=consistency,
    dc=dc,
    dc=dc,
    verify=verify,
    verify=verify,
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Failed to initialize Consul client: {str(e)}")
    logger.error(f"Failed to initialize Consul client: {str(e)}")
    raise ServiceRegistrationError(f"Failed to connect to Consul: {str(e)}")
    raise ServiceRegistrationError(f"Failed to connect to Consul: {str(e)}")


    def register(self, service_instance: ServiceInstance) -> bool:
    def register(self, service_instance: ServiceInstance) -> bool:
    """
    """
    Register a service instance with Consul.
    Register a service instance with Consul.


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
    try:
    try:
    # Create service definition
    # Create service definition
    service_def = {
    service_def = {
    "Name": service_instance.service_name,
    "Name": service_instance.service_name,
    "ID": service_instance.service_id,
    "ID": service_instance.service_id,
    "Address": service_instance.host,
    "Address": service_instance.host,
    "Port": service_instance.port,
    "Port": service_instance.port,
    "Meta": service_instance.metadata,
    "Meta": service_instance.metadata,
    "Tags": service_instance.tags or [],
    "Tags": service_instance.tags or [],
    }
    }


    # Add version tag
    # Add version tag
    service_def["Tags"].append(f"version={service_instance.version}")
    service_def["Tags"].append(f"version={service_instance.version}")


    # Add health check if provided
    # Add health check if provided
    if service_instance.health_check_url:
    if service_instance.health_check_url:
    http_protocol = "https" if service_instance.is_secure else "http"
    http_protocol = "https" if service_instance.is_secure else "http"
    service_def["Check"] = {
    service_def["Check"] = {
    "HTTP": f"{http_protocol}://{service_instance.host}:{service_instance.port}{service_instance.health_check_url}",
    "HTTP": f"{http_protocol}://{service_instance.host}:{service_instance.port}{service_instance.health_check_url}",
    "Interval": "10s",
    "Interval": "10s",
    "Timeout": "5s",
    "Timeout": "5s",
    "DeregisterCriticalServiceAfter": "30s",
    "DeregisterCriticalServiceAfter": "30s",
    }
    }


    # Register service with Consul
    # Register service with Consul
    result = self.consul.agent.service.register(**service_def)
    result = self.consul.agent.service.register(**service_def)


    if result:
    if result:
    logger.info(
    logger.info(
    f"Service {service_instance.service_name} registered successfully with ID {service_instance.service_id}"
    f"Service {service_instance.service_name} registered successfully with ID {service_instance.service_id}"
    )
    )
    return True
    return True
    else:
    else:
    logger.error(
    logger.error(
    f"Failed to register service {service_instance.service_name}"
    f"Failed to register service {service_instance.service_name}"
    )
    )
    return False
    return False


except Exception as e:
except Exception as e:
    logger.error(
    logger.error(
    f"Error registering service {service_instance.service_name}: {str(e)}"
    f"Error registering service {service_instance.service_name}: {str(e)}"
    )
    )
    raise ServiceRegistrationError(f"Failed to register service: {str(e)}")
    raise ServiceRegistrationError(f"Failed to register service: {str(e)}")


    def deregister(self, service_id: str) -> bool:
    def deregister(self, service_id: str) -> bool:
    """
    """
    Deregister a service instance from Consul.
    Deregister a service instance from Consul.


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
    try:
    try:
    result = self.consul.agent.service.deregister(service_id)
    result = self.consul.agent.service.deregister(service_id)
    if result:
    if result:
    logger.info(f"Service {service_id} deregistered successfully")
    logger.info(f"Service {service_id} deregistered successfully")
    return True
    return True
    else:
    else:
    logger.error(f"Failed to deregister service {service_id}")
    logger.error(f"Failed to deregister service {service_id}")
    return False
    return False
except Exception as e:
except Exception as e:
    logger.error(f"Error deregistering service {service_id}: {str(e)}")
    logger.error(f"Error deregistering service {service_id}: {str(e)}")
    raise ServiceDeregistrationError(f"Failed to deregister service: {str(e)}")
    raise ServiceDeregistrationError(f"Failed to deregister service: {str(e)}")


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
    try:
    try:
    # Note: For HTTP health checks, renewal is handled automatically
    # Note: For HTTP health checks, renewal is handled automatically
    # This would be used for TTL checks, which we're not using in this implementation
    # This would be used for TTL checks, which we're not using in this implementation
    # But we keep the method for compatibility with the interface
    # But we keep the method for compatibility with the interface
    logger.debug(
    logger.debug(
    f"TTL renewal not necessary for service {service_id} as we use HTTP checks"
    f"TTL renewal not necessary for service {service_id} as we use HTTP checks"
    )
    )
    return True
    return True
except Exception as e:
except Exception as e:
    logger.error(f"Error renewing service {service_id}: {str(e)}")
    logger.error(f"Error renewing service {service_id}: {str(e)}")
    return False
    return False


    def get_service(self, service_name: str) -> List[ServiceInstance]:
    def get_service(self, service_name: str) -> List[ServiceInstance]:
    """
    """
    Get all instances of a service by name from Consul.
    Get all instances of a service by name from Consul.


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
    try:
    try:
    # Query Consul catalog for service instances
    # Query Consul catalog for service instances
    index, service_nodes = self.consul.catalog.service(service_name)
    index, service_nodes = self.consul.catalog.service(service_name)


    if not service_nodes:
    if not service_nodes:
    logger.warning(f"No instances found for service: {service_name}")
    logger.warning(f"No instances found for service: {service_name}")
    return []
    return []


    # Convert to ServiceInstance objects
    # Convert to ServiceInstance objects
    instances = []
    instances = []
    for node in service_nodes:
    for node in service_nodes:
    # Extract metadata
    # Extract metadata
    metadata = {}
    metadata = {}
    if "ServiceMeta" in node:
    if "ServiceMeta" in node:
    metadata = node["ServiceMeta"]
    metadata = node["ServiceMeta"]


    # Extract version from tags
    # Extract version from tags
    version = "unknown"
    version = "unknown"
    tags = []
    tags = []
    if "ServiceTags" in node:
    if "ServiceTags" in node:
    tags = node["ServiceTags"]
    tags = node["ServiceTags"]
    for tag in tags:
    for tag in tags:
    if tag.startswith("version="):
    if tag.startswith("version="):
    version = tag.split("=")[1]
    version = tag.split("=")[1]


    # Check if service is secure
    # Check if service is secure
    is_secure = "secure" in tags
    is_secure = "secure" in tags


    # Create service instance
    # Create service instance
    instance = ServiceInstance(
    instance = ServiceInstance(
    service_id=node.get("ServiceID", ""),
    service_id=node.get("ServiceID", ""),
    service_name=node.get("ServiceName", ""),
    service_name=node.get("ServiceName", ""),
    host=node.get("ServiceAddress", "") or node.get("Address", ""),
    host=node.get("ServiceAddress", "") or node.get("Address", ""),
    port=node.get("ServicePort", 0),
    port=node.get("ServicePort", 0),
    health_check_url="/health",  # Default health check path
    health_check_url="/health",  # Default health check path
    metadata=metadata,
    metadata=metadata,
    version=version,
    version=version,
    is_secure=is_secure,
    is_secure=is_secure,
    tags=tags,
    tags=tags,
    )
    )
    instances.append(instance)
    instances.append(instance)


    return instances
    return instances
except Exception as e:
except Exception as e:
    logger.error(f"Error looking up service {service_name}: {str(e)}")
    logger.error(f"Error looking up service {service_name}: {str(e)}")
    raise ServiceLookupError(f"Failed to look up service: {str(e)}")
    raise ServiceLookupError(f"Failed to look up service: {str(e)}")


    def get_all_services(self) -> Dict[str, List[ServiceInstance]]:
    def get_all_services(self) -> Dict[str, List[ServiceInstance]]:
    """
    """
    Get all registered services from Consul.
    Get all registered services from Consul.


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
    try:
    try:
    # Get list of services
    # Get list of services
    index, services = self.consul.catalog.services()
    index, services = self.consul.catalog.services()


    # Get instances for each service
    # Get instances for each service
    result = {}
    result = {}
    for service_name in services.keys():
    for service_name in services.keys():
    if service_name == "consul":  # Skip the consul service itself
    if service_name == "consul":  # Skip the consul service itself
    continue
    continue
    result[service_name] = self.get_service(service_name)
    result[service_name] = self.get_service(service_name)


    return result
    return result
except Exception as e:
except Exception as e:
    logger.error(f"Error getting all services: {str(e)}")
    logger.error(f"Error getting all services: {str(e)}")
    raise ServiceLookupError(f"Failed to get all services: {str(e)}")
    raise ServiceLookupError(f"Failed to get all services: {str(e)}")


    def get_service_health(self, service_id: str) -> bool:
    def get_service_health(self, service_id: str) -> bool:
    """
    """
    Get the health status of a service instance from Consul.
    Get the health status of a service instance from Consul.


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
    try:
    try:
    # Get health checks for the service
    # Get health checks for the service
    index, checks = self.consul.health.checks(service_id)
    index, checks = self.consul.health.checks(service_id)


    # Service is healthy if all checks are passing
    # Service is healthy if all checks are passing
    for check in checks:
    for check in checks:
    if check["Status"] != "passing":
    if check["Status"] != "passing":
    logger.warning(
    logger.warning(
    f"Service {service_id} has non-passing check: {check['Name']} - {check['Status']}"
    f"Service {service_id} has non-passing check: {check['Name']} - {check['Status']}"
    )
    )
    return False
    return False


    # If we got here, all checks are passing (or there are no checks)
    # If we got here, all checks are passing (or there are no checks)
    return True
    return True
except Exception as e:
except Exception as e:
    logger.error(f"Error checking service health for {service_id}: {str(e)}")
    logger.error(f"Error checking service health for {service_id}: {str(e)}")
    raise ServiceHealthCheckError(f"Failed to check service health: {str(e)}")
    raise ServiceHealthCheckError(f"Failed to check service health: {str(e)}")