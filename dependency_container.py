"""
"""
Dependency Container for the pAIssive Income project.
Dependency Container for the pAIssive Income project.


This module provides a dependency container for managing dependencies
This module provides a dependency container for managing dependencies
and enabling dependency injection throughout the application.
and enabling dependency injection throughout the application.
"""
"""


import logging
import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar, cast
from typing import Any, Callable, Dict, Optional, Type, TypeVar, cast


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


T = TypeVar("T")
T = TypeVar("T")




class DependencyContainer:
    class DependencyContainer:
    """
    """
    Container for managing dependencies.
    Container for managing dependencies.


    This class provides a simple dependency injection container that allows
    This class provides a simple dependency injection container that allows
    registering and resolving dependencies.
    registering and resolving dependencies.
    """
    """


    def __init__(self):
    def __init__(self):
    """Initialize the dependency container."""
    self._dependencies: Dict[str, Any] = {}
    self._factories: Dict[str, Any] = {}
    self._singletons: Dict[str, Any] = {}

    def register(
    self, interface_type: Type[T], factory: Callable[[], T], singleton: bool = True
    ) -> None:
    """
    """
    Register a dependency.
    Register a dependency.


    Args:
    Args:
    interface_type: Interface type
    interface_type: Interface type
    factory: Factory function that creates the implementation
    factory: Factory function that creates the implementation
    singleton: Whether to create a singleton instance
    singleton: Whether to create a singleton instance
    """
    """
    interface_name = interface_type.__name__
    interface_name = interface_type.__name__
    self._factories[interface_name] = factory
    self._factories[interface_name] = factory
    if singleton:
    if singleton:
    self._singletons[interface_name] = None
    self._singletons[interface_name] = None
    logger.debug(f"Registered service: {interface_name}, singleton={singleton}")
    logger.debug(f"Registered service: {interface_name}, singleton={singleton}")


    def register_instance(self, name: str, instance: Any) -> None:
    def register_instance(self, name: str, instance: Any) -> None:
    """
    """
    Register a named instance.
    Register a named instance.


    Args:
    Args:
    name: Name of the instance
    name: Name of the instance
    instance: Instance to register
    instance: Instance to register
    """
    """
    self._singletons[name] = instance
    self._singletons[name] = instance
    logger.debug(f"Registered named instance: {name}")
    logger.debug(f"Registered named instance: {name}")


    def register_factory(self, interface_type: Type[T], factory: callable) -> None:
    def register_factory(self, interface_type: Type[T], factory: callable) -> None:
    """
    """
    Register a factory function for creating dependencies.
    Register a factory function for creating dependencies.


    Args:
    Args:
    interface_type: Interface type
    interface_type: Interface type
    factory: Factory function
    factory: Factory function
    """
    """
    interface_name = interface_type.__name__
    interface_name = interface_type.__name__
    self._factories[interface_name] = factory
    self._factories[interface_name] = factory


    def resolve(self, interface_type: Type[T]) -> T:
    def resolve(self, interface_type: Type[T]) -> T:
    """
    """
    Resolve a dependency.
    Resolve a dependency.


    Args:
    Args:
    interface_type: Interface type
    interface_type: Interface type


    Returns:
    Returns:
    Instance of the dependency
    Instance of the dependency


    Raises:
    Raises:
    KeyError: If the dependency is not registered
    KeyError: If the dependency is not registered
    """
    """
    interface_name = interface_type.__name__
    interface_name = interface_type.__name__


    # Check if we have a singleton instance
    # Check if we have a singleton instance
    if (
    if (
    interface_name in self._singletons
    interface_name in self._singletons
    and self._singletons[interface_name] is not None
    and self._singletons[interface_name] is not None
    ):
    ):
    return cast(T, self._singletons[interface_name])
    return cast(T, self._singletons[interface_name])


    # Check if we have a factory
    # Check if we have a factory
    if interface_name in self._factories:
    if interface_name in self._factories:
    instance = self._factories[interface_name]()
    instance = self._factories[interface_name]()
    if interface_name in self._singletons:
    if interface_name in self._singletons:
    self._singletons[interface_name] = instance
    self._singletons[interface_name] = instance
    logger.debug(f"Resolved service: {interface_name}")
    logger.debug(f"Resolved service: {interface_name}")
    return cast(T, instance)
    return cast(T, instance)


    # Check if we have a registered implementation
    # Check if we have a registered implementation
    if interface_name in self._dependencies:
    if interface_name in self._dependencies:
    implementation = self._dependencies[interface_name]
    implementation = self._dependencies[interface_name]
    instance = implementation()
    instance = implementation()
    if interface_name in self._singletons:
    if interface_name in self._singletons:
    self._singletons[interface_name] = instance
    self._singletons[interface_name] = instance
    logger.debug(f"Resolved service: {interface_name}")
    logger.debug(f"Resolved service: {interface_name}")
    return cast(T, instance)
    return cast(T, instance)


    raise KeyError(f"No dependency registered for {interface_name}")
    raise KeyError(f"No dependency registered for {interface_name}")


    def resolve_named(self, name: str) -> Any:
    def resolve_named(self, name: str) -> Any:
    """
    """
    Resolve a named instance.
    Resolve a named instance.


    Args:
    Args:
    name: Name of the instance to resolve
    name: Name of the instance to resolve


    Returns:
    Returns:
    The named instance
    The named instance


    Raises:
    Raises:
    KeyError: If the named instance is not registered
    KeyError: If the named instance is not registered
    """
    """
    if name not in self._singletons:
    if name not in self._singletons:
    raise KeyError(f"Named instance not registered: {name}")
    raise KeyError(f"Named instance not registered: {name}")


    logger.debug(f"Resolved named instance: {name}")
    logger.debug(f"Resolved named instance: {name}")
    return self._singletons[name]
    return self._singletons[name]


    def clear(self) -> None:
    def clear(self) -> None:
    """Clear all registered dependencies."""
    self._dependencies.clear()
    self._factories.clear()
    self._singletons.clear()
    logger.debug("Dependency container cleared")


    # Global container instance
    _container: Optional[DependencyContainer] = None


    def get_container() -> DependencyContainer:
    """
    """
    Get the global dependency container.
    Get the global dependency container.


    Returns:
    Returns:
    Global dependency container instance
    Global dependency container instance
    """
    """
    global _container
    global _container
    if _container is None:
    if _container is None:
    _container = DependencyContainer()
    _container = DependencyContainer()
    return _container
    return _container




    def clear_container() -> None:
    def clear_container() -> None:
    """Clear the global dependency container."""
    global _container
    if _container is not None:
    _container.clear()
    _container = None
    logger.debug("Global dependency container cleared")
