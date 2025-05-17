"""Service initialization utilities for the pAIssive Income project."""

# Standard library imports
import logging

# Third-party imports

# Local imports


class Service:
    """A simple mock service class."""

    def __init__(self, name: str) -> None:
        """Initialize a service with the given name.

        Args:
            name: The name of the service

        """
        self.name = name
        self.initialized = False

    def initialize(self) -> None:
        """Initialize the service and log the initialization.

        Sets the initialized flag to True and logs a message.
        """
        self.initialized = True
        logging.info(f"Service '{self.name}' initialized.")


def initialize_services(service_names: list[str]) -> list[Service]:
    """Initialize a list of services by name.

    Args:
        service_names: List of service names to initialize

    Returns:
        list: The initialized service objects

    """
    services = [Service(name) for name in service_names]
    for service in services:
        service.initialize()
    return services


def main() -> None:
    """Demo service initialization."""
    logging.basicConfig(level=logging.INFO)
    service_names = ["auth", "database", "api"]
    initialize_services(service_names)


if __name__ == "__main__":
    main()
