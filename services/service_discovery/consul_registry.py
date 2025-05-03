"""
Consul-based service registry implementation for pAIssive income microservices.

This module provides a Consul client implementation of the ServiceRegistry interface,
allowing microservices to register with Consul and discover other services.
"""


import logging
from typing import Dict, List, Optional

import consul

from services.service_discovery.service_registry import 

(
    ServiceDeregistrationError,
    ServiceHealthCheckError,
    ServiceInstance,
    ServiceLookupError,
    ServiceRegistrationError,
    ServiceRegistry,
)

# Set up logging
logger = logging.getLogger(__name__)


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
        Initialize the Consul service registry client.

        Args:
            host: Consul server hostname (default: localhost)
            port: Consul server port (default: 8500)
            token: ACL token (optional)
            scheme: http or https (default: http)
            consistency: Consul consistency mode (default, consistent, stale)
            dc: Datacenter to use (optional)
            verify: Verify SSL certificates (default: True)
        """
        self.host = host
        self.port = port

        try:
            self.consul = consul.Consul(
                host=host,
                port=port,
                token=token,
                scheme=scheme,
                consistency=consistency,
                dc=dc,
                verify=verify,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Consul client: {str(e)}")
            raise ServiceRegistrationError(f"Failed to connect to Consul: {str(e)}")

    def register(self, service_instance: ServiceInstance) -> bool:
        """
        Register a service instance with Consul.

        Args:
            service_instance: The service instance to register

        Returns:
            bool: True if registration was successful, False otherwise

        Raises:
            ServiceRegistrationError: If registration fails
        """
        try:
            # Create service definition
            service_def = {
                "Name": service_instance.service_name,
                "ID": service_instance.service_id,
                "Address": service_instance.host,
                "Port": service_instance.port,
                "Meta": service_instance.metadata,
                "Tags": service_instance.tags or [],
            }

            # Add version tag
            service_def["Tags"].append(f"version={service_instance.version}")

            # Add health check if provided
            if service_instance.health_check_url:
                http_protocol = "https" if service_instance.is_secure else "http"
                service_def["Check"] = {
                    "HTTP": f"{http_protocol}://{service_instance.host}:{service_instance.port}{service_instance.health_check_url}",
                    "Interval": "10s",
                    "Timeout": "5s",
                    "DeregisterCriticalServiceAfter": "30s",
                }

            # Register service with Consul
            result = self.consul.agent.service.register(**service_def)

            if result:
                logger.info(
                    f"Service {service_instance.service_name} registered successfully with ID {service_instance.service_id}"
                )
                        return True
            else:
                logger.error(
                    f"Failed to register service {service_instance.service_name}"
                )
                        return False

        except Exception as e:
            logger.error(
                f"Error registering service {service_instance.service_name}: {str(e)}"
            )
            raise ServiceRegistrationError(f"Failed to register service: {str(e)}")

    def deregister(self, service_id: str) -> bool:
        """
        Deregister a service instance from Consul.

        Args:
            service_id: The unique ID of the service to deregister

        Returns:
            bool: True if deregistration was successful, False otherwise

        Raises:
            ServiceDeregistrationError: If deregistration fails
        """
        try:
            result = self.consul.agent.service.deregister(service_id)
            if result:
                logger.info(f"Service {service_id} deregistered successfully")
                        return True
            else:
                logger.error(f"Failed to deregister service {service_id}")
                        return False
        except Exception as e:
            logger.error(f"Error deregistering service {service_id}: {str(e)}")
            raise ServiceDeregistrationError(f"Failed to deregister service: {str(e)}")

    def renew(self, service_id: str) -> bool:
        """
        Renew a service registration (for TTL-based checks).

        Args:
            service_id: The unique ID of the service to renew

        Returns:
            bool: True if renewal was successful, False otherwise
        """
        try:
            # Note: For HTTP health checks, renewal is handled automatically
            # This would be used for TTL checks, which we're not using in this implementation
            # But we keep the method for compatibility with the interface
            logger.debug(
                f"TTL renewal not necessary for service {service_id} as we use HTTP checks"
            )
                    return True
        except Exception as e:
            logger.error(f"Error renewing service {service_id}: {str(e)}")
                    return False

    def get_service(self, service_name: str) -> List[ServiceInstance]:
        """
        Get all instances of a service by name from Consul.

        Args:
            service_name: The name of the service to look up

        Returns:
            List[ServiceInstance]: All instances of the requested service

        Raises:
            ServiceLookupError: If lookup fails
        """
        try:
            # Query Consul catalog for service instances
            index, service_nodes = self.consul.catalog.service(service_name)

            if not service_nodes:
                logger.warning(f"No instances found for service: {service_name}")
                        return []

            # Convert to ServiceInstance objects
            instances = []
            for node in service_nodes:
                # Extract metadata
                metadata = {}
                if "ServiceMeta" in node:
                    metadata = node["ServiceMeta"]

                # Extract version from tags
                version = "unknown"
                tags = []
                if "ServiceTags" in node:
                    tags = node["ServiceTags"]
                    for tag in tags:
                        if tag.startswith("version="):
                            version = tag.split("=")[1]

                # Check if service is secure
                is_secure = "secure" in tags

                # Create service instance
                instance = ServiceInstance(
                    service_id=node.get("ServiceID", ""),
                    service_name=node.get("ServiceName", ""),
                    host=node.get("ServiceAddress", "") or node.get("Address", ""),
                    port=node.get("ServicePort", 0),
                    health_check_url="/health",  # Default health check path
                    metadata=metadata,
                    version=version,
                    is_secure=is_secure,
                    tags=tags,
                )
                instances.append(instance)

                    return instances
        except Exception as e:
            logger.error(f"Error looking up service {service_name}: {str(e)}")
            raise ServiceLookupError(f"Failed to look up service: {str(e)}")

    def get_all_services(self) -> Dict[str, List[ServiceInstance]]:
        """
        Get all registered services from Consul.

        Returns:
            Dict[str, List[ServiceInstance]]: A dictionary mapping service names to lists of instances

        Raises:
            ServiceLookupError: If lookup fails
        """
        try:
            # Get list of services
            index, services = self.consul.catalog.services()

            # Get instances for each service
            result = {}
            for service_name in services.keys():
                if service_name == "consul":  # Skip the consul service itself
                    continue
                result[service_name] = self.get_service(service_name)

                    return result
        except Exception as e:
            logger.error(f"Error getting all services: {str(e)}")
            raise ServiceLookupError(f"Failed to get all services: {str(e)}")

    def get_service_health(self, service_id: str) -> bool:
        """
        Get the health status of a service instance from Consul.

        Args:
            service_id: The unique ID of the service to check

        Returns:
            bool: True if the service is healthy, False otherwise

        Raises:
            ServiceHealthCheckError: If health check lookup fails
        """
        try:
            # Get health checks for the service
            index, checks = self.consul.health.checks(service_id)

            # Service is healthy if all checks are passing
            for check in checks:
                if check["Status"] != "passing":
                    logger.warning(
                        f"Service {service_id} has non-passing check: {check['Name']} - {check['Status']}"
                    )
                            return False

            # If we got here, all checks are passing (or there are no checks)
                    return True
        except Exception as e:
            logger.error(f"Error checking service health for {service_id}: {str(e)}")
            raise ServiceHealthCheckError(f"Failed to check service health: {str(e)}")