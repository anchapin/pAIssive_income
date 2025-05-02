"""
Consul-based implementation of the service registry interface.

This module provides a Consul implementation of the ServiceRegistry interface
for service discovery in the pAIssive income microservices architecture.
"""

import logging
from typing import Dict, List

import consul

from services.service_discovery.service_registry import (
    ServiceDeregistrationError,
    ServiceHealthCheckError,
    ServiceInstance,
    ServiceLookupError,
    ServiceRegistrationError,
    ServiceRegistry,
)

logger = logging.getLogger(__name__)


class ConsulServiceRegistry(ServiceRegistry):
    """Consul-based implementation of the service registry."""

    def __init__(self, host: str = "localhost", port: int = 8500):
        """
        Initialize the Consul service registry client.

        Args:
            host: Consul server host
            port: Consul server port
        """
        self.consul_client = consul.Consul(host=host, port=port)
        logger.info(f"Initialized Consul service registry client at {host}:{port}")

    def register(self, service_instance: ServiceInstance) -> bool:
        """Register a service instance with Consul."""
        try:
            # Prepare check definition if health check URL is provided
            check = None
            if service_instance.health_check_url:
                protocol = "https" if service_instance.is_secure else "http"
                check = {
                    "http": f"{protocol}://{service_instance.host}:{service_instance.port}{service_instance.health_check_url}",
                    "interval": "10s",
                    "timeout": "5s",
                }

            # Register the service with Consul
            result = self.consul_client.agent.service.register(
                name=service_instance.service_name,
                service_id=service_instance.service_id,
                address=service_instance.host,
                port=service_instance.port,
                tags=service_instance.tags + [f"version={service_instance.version}"],
                check=check,
                meta=service_instance.metadata,
            )

            logger.info(
                f"Registered service {service_instance.service_name} with ID {service_instance.service_id}"
            )
            return result

        except Exception as e:
            error_msg = (
                f"Failed to register service {service_instance.service_name}: {str(e)}"
            )
            logger.error(error_msg)
            raise ServiceRegistrationError(error_msg) from e

    def deregister(self, service_id: str) -> bool:
        """Deregister a service instance from Consul."""
        try:
            result = self.consul_client.agent.service.deregister(service_id)
            logger.info(f"Deregistered service with ID {service_id}")
            return result
        except Exception as e:
            error_msg = f"Failed to deregister service {service_id}: {str(e)}"
            logger.error(error_msg)
            raise ServiceDeregistrationError(error_msg) from e

    def renew(self, service_id: str) -> bool:
        """
        Renew a service registration (for TTL-based checks).

        Note: This is primarily used for custom TTL checks. With HTTP checks,
        Consul handles the checking automatically based on the interval.
        """
        try:
            # For TTL-based checks, we would use check.check_pass
            # This is a simplified version assuming the check is named after the service ID
            self.consul_client.agent.check.ttl_pass(f"service:{service_id}")
            logger.debug(f"Renewed TTL for service {service_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to renew TTL for service {service_id}: {str(e)}")
            return False

    def get_service(self, service_name: str) -> List[ServiceInstance]:
        """Get all instances of a service by name from Consul."""
        try:
            # Get service instances from Consul
            index, services = self.consul_client.catalog.service(service_name)

            # Convert Consul service data to ServiceInstance objects
            instances = []
            for service in services:
                # Extract metadata from tags
                tags = service.get("ServiceTags", [])
                version = "1.0.0"  # Default version

                # Extract version from tags if present
                for tag in tags:
                    if tag.startswith("version="):
                        version = tag.split("=", 1)[1]

                # Create ServiceInstance object
                instance = ServiceInstance(
                    service_id=service.get("ServiceID"),
                    service_name=service.get("ServiceName"),
                    host=service.get("ServiceAddress") or service.get("Address"),
                    port=service.get("ServicePort"),
                    version=version,
                    tags=tags,
                    metadata=service.get("ServiceMeta", {}),
                )
                instances.append(instance)

            return instances

        except Exception as e:
            error_msg = f"Failed to look up service {service_name}: {str(e)}"
            logger.error(error_msg)
            raise ServiceLookupError(error_msg) from e

    def get_all_services(self) -> Dict[str, List[ServiceInstance]]:
        """Get all registered services from Consul."""
        try:
            # Get list of all services
            index, service_names = self.consul_client.catalog.services()

            # Build result dictionary
            result = {}
            for service_name in service_names:
                # Skip consul's own service
                if service_name == "consul":
                    continue

                # Get instances for this service
                instances = self.get_service(service_name)
                result[service_name] = instances

            return result

        except Exception as e:
            error_msg = f"Failed to retrieve all services: {str(e)}"
            logger.error(error_msg)
            raise ServiceLookupError(error_msg) from e

    def get_service_health(self, service_id: str) -> bool:
        """Get the health status of a service instance from Consul."""
        try:
            # Get health checks for the service
            index, checks = self.consul_client.health.checks(service_id)

            # Service is healthy if all checks are passing
            is_healthy = all(check.get("Status") == "passing" for check in checks)
            return is_healthy

        except Exception as e:
            error_msg = f"Failed to check health for service {service_id}: {str(e)}"
            logger.error(error_msg)
            raise ServiceHealthCheckError(error_msg) from e
