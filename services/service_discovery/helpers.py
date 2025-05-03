"""
Helper functions for service discovery integration.

This module provides utility functions to simplify the integration of service discovery
into microservices in the pAIssive income platform.
"""

import atexit
import logging
import os
import signal
from typing import Any, Callable, Dict, List, Optional

from services.service_discovery.discovery_client import ServiceDiscoveryClient

logger = logging.getLogger(__name__)


def setup_service_discovery(
    service_name: str,
    port: int,
    version: str = "1.0.0",
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    health_check_url: str = " / health",
    registry_host: Optional[str] = None,
    registry_port: Optional[int] = None,
    auto_deregister: bool = True,
    is_secure: bool = False,
) -> ServiceDiscoveryClient:
    """
    Set up service discovery for a microservice.

    This function configures the service discovery client, registers the service,
    and sets up automatic deregistration on service shutdown.

    Args:
        service_name: Name of this service
        port: Port this service is running on
        version: Service version (default: "1.0.0")
        tags: List of tags for this service (optional)
        metadata: Additional metadata for this service (optional)
        health_check_url: URL path for health checks (default: " / health")
        registry_host: Hostname of the registry service (default: from environment variable)
        registry_port: Port of the registry service (default: from environment variable)
        auto_deregister: Whether to automatically deregister on shutdown (default: True)
        is_secure: Whether this service uses HTTPS (default: False)

    Returns:
        ServiceDiscoveryClient: The configured service discovery client
    """
    # Get registry host and port from environment variables if not provided
    if registry_host is None:
        registry_host = os.environ.get("SERVICE_REGISTRY_HOST", "localhost")

    if registry_port is None:
        try:
            registry_port = int(os.environ.get("SERVICE_REGISTRY_PORT", "8500"))
        except ValueError:
            logger.warning("Invalid SERVICE_REGISTRY_PORT, using default 8500")
            registry_port = 8500

    logger.info(
        f"Setting up service discovery for {service_name} at {registry_host}:{registry_port}"
    )

    # Create discovery client
    try:
        client = ServiceDiscoveryClient(
            service_name=service_name,
            port=port,
            version=version,
            tags=tags,
            metadata=metadata,
            health_check_url=health_check_url,
            registry_host=registry_host,
            registry_port=registry_port,
            auto_register=True,
            is_secure=is_secure,
        )

        # Set up automatic deregistration on shutdown
        if auto_deregister:

            def deregister_service():
                logger.info(f"Deregistering service {service_name}")
                try:
                    client.deregister_self()
                except Exception as e:
                    logger.error(f"Error deregistering service: {str(e)}")

            # Register the deregistration function to be called on exit
            atexit.register(deregister_service)

            # Handle termination signals
            def signal_handler(sig, frame):
                logger.info(f"Received signal {sig}")
                deregister_service()
                raise SystemExit(0)

            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)

        return client
    except Exception as e:
        logger.error(f"Failed to set up service discovery: {str(e)}")
        # Return disabled client when service discovery is not available
        return ServiceDiscoveryClient(service_name=service_name, port=port, auto_register=False)


def create_health_check_handler(
    service_name: str, check_functions: Optional[List[Callable[[], bool]]] = None
) -> Callable[[], Dict[str, Any]]:
    """
    Create a health check handler function for use in web frameworks.

    Args:
        service_name: Name of the service
        check_functions: List of functions to call to check service health (optional)

    Returns:
        Callable: A function that returns a health check response
    """

    def health_check() -> Dict[str, Any]:
        """Check if the service is healthy."""
        status = "UP"
        checks = {}

        # Run custom health checks if provided
        if check_functions:
            for i, check_fn in enumerate(check_functions):
                check_name = getattr(check_fn, "__name__", f"check_{i + 1}")
                try:
                    result = check_fn()
                    checks[check_name] = {"status": "UP" if result else "DOWN"}

                    if not result:
                        status = "DOWN"
                except Exception as e:
                    checks[check_name] = {"status": "DOWN", "error": str(e)}
                    status = "DOWN"

        return {
            "status": status,
            "service": service_name,
            "timestamp": import_iso_timestamp(),
            "checks": checks,
        }

    return health_check


def import_iso_timestamp() -> str:
    """
    Get the current timestamp in ISO 8601 format.

    Returns:
        str: Current timestamp in ISO 8601 format
    """
    from datetime import datetime

    return datetime.utcnow().isoformat() + "Z"


def register_health_check_endpoint(app, url_path: str = " / health", **kwargs):
    """
    Register a health check endpoint with a web application.

    This function detects the web framework being used and registers
    a health check endpoint appropriately.

    Args:
        app: The web application instance
        url_path: URL path for the health check endpoint (default: " / health")
        **kwargs: Additional arguments to pass to create_health_check_handler
    """
    health_check = create_health_check_handler(**kwargs)

    # Detect framework type
    if hasattr(app, "route"):  # Flask

        @app.route(url_path, methods=["GET"])
        def flask_health_check():
            return health_check()

    elif hasattr(app, "add_api_route"):  # FastAPI
        from fastapi.responses import JSONResponse

        @app.get(url_path)
        def fastapi_health_check():
            result = health_check()
            status_code = 200 if result["status"] == "UP" else 503
            return JSONResponse(content=result, status_code=status_code)

    else:
        logger.warning(f"Unknown web framework type, health check not registered at {url_path}")


def get_service_url(
    service_name: str, path: str = " / ", client: Optional[ServiceDiscoveryClient] = None
) -> Optional[str]:
    """
    Get the URL for a service by name.

    Args:
        service_name: Name of the service to look up
        path: Path to append to the URL (default: " / ")
        client: ServiceDiscoveryClient to use (optional, creates a temporary one if not provided)

    Returns:
        Optional[str]: The URL for the service, or None if not found
    """
    if client is None:
        # Create a temporary client
        registry_host = os.environ.get("SERVICE_REGISTRY_HOST", "localhost")
        registry_port = int(os.environ.get("SERVICE_REGISTRY_PORT", "8500"))

        client = ServiceDiscoveryClient(
            service_name="temp - client",
            port=0,  # No need for port since we're not registering
            auto_register=False,
            registry_host=registry_host,
            registry_port=registry_port,
        )

    return client.get_service_url(service_name, path)
