"""
Load balancing strategies for service discovery.

This module defines various load balancing strategies for distributing
requests across multiple instances of a service.
"""

import abc
import random
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")

class LoadBalancerStrategy(Generic[T], abc.ABC):
    """Base interface for load balancing strategies."""

    @abc.abstractmethod
    def select(self, instances: List[T]) -> Optional[T]:
        """
        Select an instance from the list using the strategy.

        Args:
            instances: List of instances to select from

        Returns:
            Optional[T]: The selected instance, or None if the list is empty
        """
        pass

class RoundRobinStrategy(LoadBalancerStrategy[T]):
    """Round - robin load balancing strategy."""

    def __init__(self):
        self.counter = 0

    def select(self, instances: List[T]) -> Optional[T]:
        """Select an instance using round - robin strategy."""
        if not instances:
            return None

        self.counter = (self.counter + 1) % len(instances)
        return instances[self.counter]

class RandomStrategy(LoadBalancerStrategy[T]):
    """Random selection load balancing strategy."""

    def select(self, instances: List[T]) -> Optional[T]:
        """Select a random instance."""
        if not instances:
            return None

        return random.choice(instances)

class WeightedRandomStrategy(LoadBalancerStrategy[T]):
    """Weighted random selection load balancing strategy."""

    def __init__(self, weight_function):
        """
        Initialize the weighted random strategy.

        Args:
            weight_function: Function that takes an instance and returns its weight
        """
        self.weight_function = weight_function

    def select(self, instances: List[T]) -> Optional[T]:
        """Select an instance using weighted random selection."""
        if not instances:
            return None

        # Get weights for all instances
        weights = [self.weight_function(instance) for instance in instances]

        # Select an instance based on weights
        return random.choices(instances, weights=weights, k=1)[0]

class LeastConnectionsStrategy(LoadBalancerStrategy[T]):
    """Least connections load balancing strategy."""

    def __init__(self, get_connections_function):
        """
        Initialize the least connections strategy.

        Args:
            get_connections_function: Function that takes an instance and \
                returns its connection count
        """
        self.get_connections = get_connections_function

    def select(self, instances: List[T]) -> Optional[T]:
        """Select the instance with the least connections."""
        if not instances:
            return None

        return min(instances, key=self.get_connections)

class LoadBalancer(Generic[T]):
    """Load balancer for selecting service instances."""

    def __init__(self, strategy: LoadBalancerStrategy[T] = None, filter_function=None):
        """
        Initialize the load balancer.

        Args:
            strategy: The load balancing strategy to use (default: RoundRobinStrategy)
            filter_function: Optional function to filter instances before selection
        """
        self.strategy = strategy or RoundRobinStrategy()
        self.filter_function = filter_function

    def select(self, instances: List[T]) -> Optional[T]:
        """
        Select an instance from the list using the configured strategy.

        Args:
            instances: List of instances to select from

        Returns:
            Optional[T]: The selected instance, or None if no suitable instances found
        """
        if not instances:
            return None

        # Apply filter if provided
        if self.filter_function:
            filtered_instances = [i for i in instances if self.filter_function(i)]
            if filtered_instances:
                instances = filtered_instances

        # Use strategy to select an instance
        return self.strategy.select(instances)
