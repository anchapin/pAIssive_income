"""load_balancer - Module for services/service_discovery.load_balancer."""

# Standard library imports
import logging
import random
from typing import Any, Callable, Dict, List, Optional, Protocol

# Third-party imports

# Local imports

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Protocol):
    """Protocol for load balancing strategies."""

    def select_instance(self, instances: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select an instance from a list of instances.

        Args:
            instances: List of service instances

        Returns:
            Selected instance or None if no instances are available
        """
        ...


class RoundRobinStrategy:
    """Round-robin load balancing strategy."""

    def __init__(self):
        """Initialize the round-robin strategy."""
        self.current_index = 0

    def select_instance(self, instances: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select an instance using round-robin strategy.

        Args:
            instances: List of service instances

        Returns:
            Selected instance or None if no instances are available
        """
        if not instances:
            return None

        selected = instances[self.current_index % len(instances)]
        self.current_index += 1
        return selected


class RandomStrategy:
    """Random load balancing strategy."""

    def select_instance(self, instances: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select an instance randomly.

        Args:
            instances: List of service instances

        Returns:
            Selected instance or None if no instances are available
        """
        if not instances:
            return None

        return random.choice(instances)


class WeightedRandomStrategy:
    """Weighted random load balancing strategy."""

    def __init__(self, weight_function: Callable[[Dict[str, Any]], float]):
        """Initialize the weighted random strategy.

        Args:
            weight_function: Function that returns the weight of an instance
        """
        self.weight_function = weight_function

    def select_instance(self, instances: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select an instance using weighted random strategy.

        Args:
            instances: List of service instances

        Returns:
            Selected instance or None if no instances are available
        """
        if not instances:
            return None

        weights = [self.weight_function(instance) for instance in instances]
        return random.choices(instances, weights=weights, k=1)[0]


class LeastConnectionsStrategy:
    """Least connections load balancing strategy."""

    def select_instance(self, instances: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the instance with the least connections.

        Args:
            instances: List of service instances with 'connections' field

        Returns:
            Selected instance or None if no instances are available
        """
        if not instances:
            return None

        return min(instances, key=lambda instance: instance.get("connections", 0))


class LoadBalancer:
    """Load balancer for service instances."""

    def __init__(self, strategy: str = "round_robin"):
        """Initialize the load balancer.

        Args:
            strategy: Load balancing strategy to use
        """
        self.strategy = self._create_strategy(strategy)

    def _create_strategy(self, strategy_name: str) -> LoadBalancingStrategy:
        """Create a load balancing strategy.

        Args:
            strategy_name: Name of the strategy to create

        Returns:
            Load balancing strategy

        Raises:
            ValueError: If the strategy name is invalid
        """
        if strategy_name == "round_robin":
            return RoundRobinStrategy()
        elif strategy_name == "random":
            return RandomStrategy()
        elif strategy_name == "weighted_random":
            # Default weight function gives all instances equal weight
            return WeightedRandomStrategy(lambda _: 1.0)
        elif strategy_name == "least_connections":
            return LeastConnectionsStrategy()
        else:
            raise ValueError(f"Invalid load balancing strategy: {strategy_name}")

    def select_instance(self, instances: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select an instance using the configured strategy.

        Args:
            instances: List of service instances

        Returns:
            Selected instance or None if no instances are available
        """
        if not instances:
            return None

        return self.strategy.select_instance(instances)
