"""dependency_container.py - Simple dependency injection container for the pAIssive Income project."""

class DependencyContainer:
    """
    A very basic dependency container for registering and retrieving services.
    """
    def __init__(self):
        self._services = {}

    def register(self, name, service):
        """Register a service with a given name. Raises ValueError if already registered."""
        if name in self._services:
            raise ValueError(f"Service with name '{name}' is already registered.")
        self._services[name] = service

    def get(self, name):
        """Retrieve a registered service by name."""
        return self._services.get(name)

    def list_services(self):
        """List all registered service names."""
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
