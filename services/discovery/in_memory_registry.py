"""
In - Memory Service Registry Implementation

This module provides an in - memory implementation of the ServiceRegistry interface,
suitable for development, testing, and small - scale deployments.
"""

import threading
import time
import uuid
from typing import Any, Dict, List, Optional

from .interfaces import ServiceInstance, ServiceRegistry, ServiceStatus


class InMemoryServiceRegistry(ServiceRegistry):
    """
    In - memory implementation of ServiceRegistry.

    This implementation stores all service information in memory and is suitable for
    development, testing, 
        or small - scale deployments where persistence is not required.
    """

    def __init__(self, ttl_seconds: int = 30):
        """
        Initialize a new InMemoryServiceRegistry.

        Args:
            ttl_seconds: Time - \
                to - live in seconds for service registrations before they expire
        """
        self._services: Dict[str, ServiceInstance] = {}
        self._last_renewal: Dict[str, float] = {}
        self._ttl_seconds = ttl_seconds
        self._lock = threading.RLock()

        # Start a background thread to remove expired services
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired_services, 
            daemon=True)
        self._cleanup_thread.start()

    def __del__(self):
        """Clean up resources when the registry is deleted."""
        self._running = False
        if hasattr(self, "_cleanup_thread") and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=1.0)

    def _cleanup_expired_services(self):
        """Background task to remove expired service registrations."""
        while self._running:
            time.sleep(self._ttl_seconds / 2)

            with self._lock:
                current_time = time.time()
                expired_instances = [
                    instance_id
                    for instance_id, last_renewal in self._last_renewal.items()
                    if current_time - last_renewal > self._ttl_seconds
                ]

                for instance_id in expired_instances:
                    self._services.pop(instance_id, None)
                    self._last_renewal.pop(instance_id, None)

    def register(self, service: ServiceInstance) -> bool:
        """
        Register a service instance.

        Args:
            service: The service instance to register

        Returns:
            True if registration was successful, False otherwise
        """
        with self._lock:
            if not service.instance_id:
                service.instance_id = str(uuid.uuid4())

            self._services[service.instance_id] = service
            self._last_renewal[service.instance_id] = time.time()
            return True

    def deregister(self, instance_id: str) -> bool:
        """
        Deregister a service instance.

        Args:
            instance_id: The instance ID to deregister

        Returns:
            True if deregistration was successful, False otherwise
        """
        with self._lock:
            if instance_id in self._services:
                del self._services[instance_id]
                self._last_renewal.pop(instance_id, None)
                return True
            return False

    def renew(self, instance_id: str) -> bool:
        """
        Renew the registration of a service instance.

        Args:
            instance_id: The instance ID to renew

        Returns:
            True if renewal was successful, False otherwise
        """
        with self._lock:
            if instance_id in self._services:
                self._last_renewal[instance_id] = time.time()
                return True
            return False

    def get_instance(self, instance_id: str) -> Optional[ServiceInstance]:
        """
        Get a specific service instance by ID.

        Args:
            instance_id: The instance ID to retrieve

        Returns:
            The service instance, or None if not found
        """
        with self._lock:
            return self._services.get(instance_id)

    def get_instances(self, service_id: str) -> List[ServiceInstance]:
        """
        Get all instances of a specific service.

        Args:
            service_id: The service ID to look up

        Returns:
            List of service instances for the specified service
        """
        with self._lock:
            return [
                service for service in self._services.values(
                    ) if service.service_id == service_id
            ]

    def get_all_instances(self) -> Dict[str, List[ServiceInstance]]:
        """
        Get all registered service instances, grouped by service ID.

        Returns:
            Dictionary mapping service IDs to lists of service instances
        """
        result: Dict[str, List[ServiceInstance]] = {}

        with self._lock:
            for service in self._services.values():
                if service.service_id not in result:
                    result[service.service_id] = []
                result[service.service_id].append(service)

        return result

    def update_status(self, instance_id: str, status: ServiceStatus) -> bool:
        """
        Update the status of a service instance.

        Args:
            instance_id: The instance ID to update
            status: The new status

        Returns:
            True if the update was successful, False otherwise
        """
        with self._lock:
            if instance_id in self._services:
                service = self._services[instance_id]
                service.status = status
                return True
            return False
