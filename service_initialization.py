"""service_initialization.py - Service initialization utilities for the pAIssive Income project."""

class Service:
    """A simple mock service class."""
    def __init__(self, name):
        self.name = name
        self.initialized = False

    def initialize(self):
        self.initialized = True
        print(f"Service '{self.name}' initialized.")


def initialize_services(service_names):
    """Initialize a list of services by name."""
    services = [Service(name) for name in service_names]
    for service in services:
        service.initialize()
    return services


def main():
    """Demo service initialization."""
    service_names = ["auth", "database", "api"]
    initialize_services(service_names)


if __name__ == "__main__":
    main()
