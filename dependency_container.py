"""Simple dependency injection container for the pAIssive Income project."""

# Standard library imports
import logging
from typing import Any, Optional

# Third-party imports

# Local imports

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SERVICE_ALREADY_REGISTERED_MSG = "Service with name '{name}' is already registered."


class DependencyContainer:
    """A very basic dependency container for registering and retrieving services."""

    def __init__(self) -> None:
        """Initialize an empty container for services."""
        self._services: dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        """Register a service with a given name.

        Args:
            name: Name to register the service under
            service: The service object to register

        Raises:
            ValueError: If a service with the same name is already registered.

        """
        if name in self._services:
            raise ValueError(SERVICE_ALREADY_REGISTERED_MSG.format(name=name))
        self._services[name] = service

    def get(self, name: str) -> Optional[Any]:
        """Retrieve a registered service by name.

        Args:
            name: The name of the service to retrieve

        Returns:
            The registered service or None if not found

        """
        return self._services.get(name)

    def list_services(self) -> list[str]:
        """List all registered service names.

        Returns:
            list[str]: Names of all registered services

        """
        return list(self._services.keys())


def main() -> None:
    """Demo usage of the dependency container."""
    container = DependencyContainer()
    container.register("database", {"url": "sqlite:///:memory:"})
    logging.info(f"Registered services: {container.list_services()}")
    db = container.get("database")
    logging.info(f"Database config: {db}")


if __name__ == "__main__":
    main()
