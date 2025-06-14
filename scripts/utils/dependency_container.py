"""Simple dependency injection container for the pAIssive Income project."""

from __future__ import annotations

# Standard library imports
from typing import Optional, TypedDict, TypeVar, cast

# Third-party imports
# Local imports
from common_utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

SERVICE_ALREADY_REGISTERED_MSG: str = (
    "Service with name '{name}' is already registered."
)

T = TypeVar(
    "T", bound=object
)  # Type variable for generic service types with object bound


class DatabaseConfig(TypedDict):
    """Type definition for database configuration."""

    url: str


class DependencyContainer:
    """A very basic dependency container for registering and retrieving services."""

    def __init__(self) -> None:
        """Initialize an empty container for services."""
        self._services: dict[str, object] = {}

    def register(self, name: str, service: object) -> None:
        """
        Register a service with a given name.

        Args:
            name: Name to register the service under
            service: The service object to register

        Raises:
            ValueError: If a service with the same name is already registered

        """
        if name in self._services:
            raise ValueError(SERVICE_ALREADY_REGISTERED_MSG.format(name=name))
        self._services[name] = service

    def get(self, name: str, service_type: Optional[type[T]] = None) -> Optional[T]:
        """
        Retrieve a registered service by name.

        Args:
            name: The name of the service to retrieve
            service_type: Optional type to cast the service to

        Returns:
            The registered service cast to service_type if provided,
            or the raw service if no type provided, or None if not found

        """
        service = self._services.get(name)
        if service is not None and service_type is not None:
            return cast("service_type", service)
        return cast("T", service) if service is not None else None

    def list_services(self) -> list[str]:
        """
        List all registered service names.

        Returns:
            Names of all registered services

        """
        return list(self._services.keys())


def main() -> None:
    """Demo usage of the dependency container."""
    container = DependencyContainer()
    db_config: DatabaseConfig = {"url": "sqlite:///:memory:"}
    container.register("database", db_config)
    logger.info("Registered services: %s", container.list_services())
    db = container.get("database", DatabaseConfig)
    logger.info("Database config: %s", db)


if __name__ == "__main__":
    main()
