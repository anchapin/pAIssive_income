"""
Tests for the dependency container.
"""


from abc import ABC, abstractmethod
from typing import List

import pytest

from dependency_container import DependencyContainer, clear_container, get_container




# Define some test interfaces and implementations
class ITestService(ABC):
    """Test service interface."""

    @abstractmethod
    def get_name(self) -> str:
        """Get the service name."""
        pass


class TestService(ITestService):
    """Test service implementation."""

    def setup_method(self, name: str = "TestService"):
        """Initialize the test service."""
        self.name = name

    def get_name(self) -> str:
        """Get the service name."""
        return self.name


class IListService(ABC):
    """List service interface."""

    @abstractmethod
    def get_items(self) -> List[str]:
        """Get the list items."""
        pass


class ListService(IListService):
    """List service implementation."""

    def __init__(self, items: List[str] = None):
        """Initialize the list service."""
        self.items = items or ["item1", "item2", "item3"]

    def get_items(self) -> List[str]:
        """Get the list items."""
        return self.items


@pytest.fixture
def container():
    """Create a new dependency container for each test."""
    return DependencyContainer()


def test_register_and_resolve(container):
    """Test registering and resolving a dependency."""
    # Register a dependency
    container.register(ITestService, lambda: TestService())

    # Resolve the dependency
    service = container.resolve(ITestService)

    # Verify the result
    assert isinstance(service, TestService)
    assert service.get_name() == "TestService"


def test_register_instance(container):
    """Test registering and resolving an instance."""
    # Create an instance
    instance = TestService("InstanceService")

    # Register the instance
    container.register_instance("test_service", instance)

    # Resolve the instance
    resolved = container.resolve_named("test_service")

    # Verify the result
    assert resolved is instance
    assert resolved.get_name() == "InstanceService"


def test_singleton(container):
    """Test singleton behavior."""
    # Register a singleton
    container.register(ITestService, lambda: TestService(), singleton=True)

    # Resolve the singleton twice
    service1 = container.resolve(ITestService)
    service2 = container.resolve(ITestService)

    # Verify that both references point to the same instance
    assert service1 is service2


def test_non_singleton(container):
    """Test non-singleton behavior."""
    # Register a non-singleton
    container.register(ITestService, lambda: TestService(), singleton=False)

    # Resolve the service twice
    service1 = container.resolve(ITestService)
    service2 = container.resolve(ITestService)

    # Verify that both references point to different instances
    assert service1 is not service2


def test_resolve_unregistered(container):
    """Test resolving an unregistered dependency."""
    # Attempt to resolve an unregistered dependency
    with pytest.raises(KeyError):
        container.resolve(ITestService)


def test_resolve_named_unregistered(container):
    """Test resolving an unregistered named instance."""
    # Attempt to resolve an unregistered named instance
    with pytest.raises(KeyError):
        container.resolve_named("unregistered")


def test_clear(container):
    """Test clearing the container."""
    # Register some dependencies
    container.register(ITestService, lambda: TestService())
    container.register(IListService, lambda: ListService())
    container.register_instance("test_service", TestService())

    # Clear the container
    container.clear()

    # Verify that the container is empty
    with pytest.raises(KeyError):
        container.resolve(ITestService)

    with pytest.raises(KeyError):
        container.resolve(IListService)

    with pytest.raises(KeyError):
        container.resolve_named("test_service")


def test_get_container():
    """Test getting the global container."""
    # Clear the global container
    clear_container()

    # Get the global container
    container1 = get_container()
    container2 = get_container()

    # Verify that both references point to the same instance
    assert container1 is container2

    # Register a dependency
    container1.register(ITestService, lambda: TestService())

    # Verify that the dependency is available in container2
    service = container2.resolve(ITestService)
    assert isinstance(service, TestService)

    # Clear the global container
    clear_container()