"""
Service registration for pAIssive income microservices.

This module provides utilities for registering microservices with the service registry
and managing service lifecycle events.
"""

import atexit
import logging
import os
import signal
import socket
import sys
from typing import Any, Callable, Dict, List, Optional

from services.service_discovery.discovery_client import ServiceDiscoveryClient
from services.service_discovery.helpers import (
    register_health_check_endpoint,
    setup_service_discovery,
)

logger = logging.getLogger(__name__)


class ServiceRegistration:
    """
    Manages service registration with the service registry.

    This class handles service registration, deregistration, and health check setup.
    """

    def __init__(
        self,
        service_name: str,
        port: int,
        version: str = "1.0.0",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        health_check_url: str = " / health",
        registry_host: Optional[str] = None,
        registry_port: Optional[int] = None,
        is_secure: bool = False,
    ):
        """
        Initialize service registration.

        Args:
            service_name: Name of this service
            port: Port this service is running on
            version: Service version
            tags: List of tags for this service
            metadata: Additional metadata for this service
            health_check_url: URL path for health checks
            registry_host: Hostname of the registry service
            registry_port: Port of the registry service
            is_secure: Whether this service uses HTTPS
        """
        self.service_name = service_name
        self.port = port
        self.version = version
        self.tags = tags or []
        self.metadata = metadata or {}
        self.health_check_url = health_check_url
        self.is_secure = is_secure

        # Get registry host and port from environment variables if not provided
        self.registry_host = registry_host or os.environ.get("SERVICE_REGISTRY_HOST", "localhost")

        try:
            self.registry_port = registry_port or int(
                os.environ.get("SERVICE_REGISTRY_PORT", "8500")
            )
        except ValueError:
            logger.warning("Invalid SERVICE_REGISTRY_PORT, using default 8500")
            self.registry_port = 8500

        # Create discovery client
        self.client = None

        # Register service deregistration on application exit
        atexit.register(self._deregister)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def register(self) -> bool:
        """
        Register this service with the registry.

        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            logger.info(
                f"Registering service {self.service_name} at {self.registry_host}:{self.registry_port}"
            )

            self.client = ServiceDiscoveryClient(
                service_name=self.service_name,
                port=self.port,
                version=self.version,
                tags=self.tags,
                metadata=self.metadata,
                health_check_url=self.health_check_url,
                registry_host=self.registry_host,
                registry_port=self.registry_port,
                auto_register=True,
                is_secure=self.is_secure,
            )

            return True
        except Exception as e:
            logger.error(f"Failed to register service {self.service_name}: {str(e)}")
            return False

    def _deregister(self) -> None:
        """Deregister this service from the registry."""
        if self.client:
            try:
                logger.info(f"Deregistering service {self.service_name}")
                self.client.deregister_self()
            except Exception as e:
                logger.error(f"Error deregistering service {self.service_name}: {str(e)}")

    def _signal_handler(self, sig, frame) -> None:
        """Handle termination signals."""
        logger.info(f"Received signal {sig}, shutting down {self.service_name}")
        self._deregister()
        sys.exit(0)

    def setup_health_check(
        self, app, check_functions: Optional[List[Callable[[], bool]]] = None
    ) -> None:
        """
        Set up health check endpoint for this service.

        Args:
            app: The web application instance
            check_functions: List of functions to call to check service health
        """
        register_health_check_endpoint(
            app=app,
            url_path=self.health_check_url,
            service_name=self.service_name,
            check_functions=check_functions,
        )

        logger.info(f"Set up health check endpoint at {self.health_check_url}")


def register_service(
    app,
    service_name: str,
    port: int,
    version: str = "1.0.0",
    health_check_path: str = " / health",
    check_functions: Optional[List[Callable[[], bool]]] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    registry_host: Optional[str] = None,
    registry_port: Optional[int] = None,
    is_secure: bool = False,
) -> ServiceRegistration:
    """
    Register a service with the service registry and set up health checks.

    This is a convenience function that creates a ServiceRegistration instance,
    registers the service, and sets up health check endpoints.

    Args:
        app: The web application instance
        service_name: Name of this service
        port: Port this service is running on
        version: Service version
        health_check_path: URL path for health checks
        check_functions: List of functions to call to check service health
        tags: List of tags for this service
        metadata: Additional metadata for this service
        registry_host: Hostname of the registry service
        registry_port: Port of the registry service
        is_secure: Whether this service uses HTTPS

    Returns:
        ServiceRegistration: The service registration instance
    """
    registration = ServiceRegistration(
        service_name=service_name,
        port=port,
        version=version,
        tags=tags,
        metadata=metadata,
        health_check_url=health_check_path,
        registry_host=registry_host,
        registry_port=registry_port,
        is_secure=is_secure,
    )

    # Register service
    success = registration.register()

    # Set up health check endpoint
    if success:
        registration.setup_health_check(app, check_functions)

    return registration


def get_service_metadata() -> Dict[str, Any]:
    """
    Get metadata about this service for registration.

    Returns:
        Dict[str, Any]: Service metadata
    """
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    pid = os.getpid()

    return {
        "hostname": hostname,
        "host_ip": host_ip,
        "pid": str(pid),
        "platform": sys.platform,
        "python_version": sys.version.split()[0],
    }


def get_default_tags() -> List[str]:
    """
    Get default tags for service registration.

    Returns:
        List[str]: Default tags
    """
    env = os.environ.get("ENVIRONMENT", "development")
    return [f"env:{env}", f"platform:{sys.platform}"]
