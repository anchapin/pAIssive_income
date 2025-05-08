"""Simple dependency injection container for the pAIssive Income project."""

# Standard library imports

# Third-party imports

# Local imports


class DependencyContainer:
    """A very basic dependency container for registering and retrieving services."""

    def __init__(self):
        """Initialize an empty container for services."""
        self._services = {}

    def register(self, name, service):
        """Register a service with a given name.

        Args:
            name: Name to register the service under
            service: The service object to register

        Raises:
            ValueError: If a service with the same name is already registered.

        """
        if name in self._services:
            raise ValueError(f"Service with name '{name}' is already registered.")
        self._services[name] = service

    def get(self, name):
        """Retrieve a registered service by name.

        Args:
            name: The name of the service to retrieve

        Returns:
            The registered service or None if not found

        """
        return self._services.get(name)

    def list_services(self):
        """List all registered service names.

        Returns:
            list: Names of all registered services

        """
        return list(self._services.keys())


def main():
    """Demo usage of the dependency container."""
    container = DependencyContainer()
    container.register("database", {"url": "sqlite:///:memory:"})
    print("Registered services:", container.list_services())
    db = container.get("database")
    print("Database config:", db)


if __name__ == "__main__":
    main()
