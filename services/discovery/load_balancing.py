"""
Load Balancing Strategies

This module provides various load balancing strategies for service discovery.
"""

import random
import time
from typing import Dict, List, Optional, Any

from .interfaces import LoadBalancingStrategy, ServiceInstance, ServiceStatus


class RandomLoadBalancer(LoadBalancingStrategy):
    """
    Random load balancing strategy.
    
    Selects a service instance randomly from the available healthy instances.
    """
    
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """
        Select an instance randomly from the list of healthy instances.
        
        Args:
            instances: List of available service instances
            
        Returns:
            The selected instance, or None if no instances are available
        """
        healthy_instances = [
            instance for instance in instances
            if instance.status == ServiceStatus.HEALTHY
        ]
        
        if not healthy_instances:
            # If no healthy instances, try any instance that's not unhealthy or stopped
            healthy_instances = [
                instance for instance in instances
                if instance.status not in (ServiceStatus.UNHEALTHY, ServiceStatus.STOPPED)
            ]
        
        if not healthy_instances:
            return None
            
        return random.choice(healthy_instances)


class RoundRobinLoadBalancer(LoadBalancingStrategy):
    """
    Round-robin load balancing strategy.
    
    Selects service instances in a circular order, distributing load evenly.
    """
    
    def __init__(self):
        """Initialize a new RoundRobinLoadBalancer."""
        self._last_index: Dict[str, int] = {}
    
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """
        Select an instance in round-robin fashion from the list of healthy instances.
        
        Args:
            instances: List of available service instances
            
        Returns:
            The selected instance, or None if no instances are available
        """
        if not instances:
            return None
            
        # Filter to only get healthy instances
        healthy_instances = [
            instance for instance in instances
            if instance.status == ServiceStatus.HEALTHY
        ]
        
        if not healthy_instances:
            # If no healthy instances, try any instance that's not unhealthy or stopped
            healthy_instances = [
                instance for instance in instances
                if instance.status not in (ServiceStatus.UNHEALTHY, ServiceStatus.STOPPED)
            ]
            
        if not healthy_instances:
            return None
            
        # Get the service ID from the first instance
        service_id = healthy_instances[0].service_id
        
        # Get the last used index for this service
        last_index = self._last_index.get(service_id, -1)
        
        # Calculate the next index
        next_index = (last_index + 1) % len(healthy_instances)
        
        # Update the last used index
        self._last_index[service_id] = next_index
        
        return healthy_instances[next_index]


class LeastConnectionsLoadBalancer(LoadBalancingStrategy):
    """
    Least connections load balancing strategy.
    
    Selects service instances with the fewest active connections.
    This is a simplified implementation that uses a counter for each instance.
    """
    
    def __init__(self):
        """Initialize a new LeastConnectionsLoadBalancer."""
        self._connections: Dict[str, int] = {}
    
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """
        Select the instance with the fewest active connections.
        
        Args:
            instances: List of available service instances
            
        Returns:
            The selected instance, or None if no instances are available
        """
        if not instances:
            return None
            
        # Filter to only get healthy instances
        healthy_instances = [
            instance for instance in instances
            if instance.status == ServiceStatus.HEALTHY
        ]
        
        if not healthy_instances:
            # If no healthy instances, try any instance that's not unhealthy or stopped
            healthy_instances = [
                instance for instance in instances
                if instance.status not in (ServiceStatus.UNHEALTHY, ServiceStatus.STOPPED)
            ]
            
        if not healthy_instances:
            return None
        
        # Find the instance with the fewest connections
        min_connections = float('inf')
        selected_instance = None
        
        for instance in healthy_instances:
            connections = self._connections.get(instance.instance_id, 0)
            if connections < min_connections:
                min_connections = connections
                selected_instance = instance
        
        # Increment the connection count for the selected instance
        if selected_instance:
            instance_id = selected_instance.instance_id
            self._connections[instance_id] = self._connections.get(instance_id, 0) + 1
            
        return selected_instance
    
    def release_connection(self, instance_id: str) -> None:
        """
        Release a connection to an instance.
        
        Args:
            instance_id: The instance ID to release a connection from
        """
        if instance_id in self._connections and self._connections[instance_id] > 0:
            self._connections[instance_id] -= 1


class WeightedLoadBalancer(LoadBalancingStrategy):
    """
    Weighted load balancing strategy.
    
    Selects service instances based on weights specified in instance metadata.
    """
    
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """
        Select an instance based on weights from the list of healthy instances.
        
        Args:
            instances: List of available service instances
            
        Returns:
            The selected instance, or None if no instances are available
        """
        if not instances:
            return None
            
        # Filter to only get healthy instances
        healthy_instances = [
            instance for instance in instances
            if instance.status == ServiceStatus.HEALTHY
        ]
        
        if not healthy_instances:
            # If no healthy instances, try any instance that's not unhealthy or stopped
            healthy_instances = [
                instance for instance in instances
                if instance.status not in (ServiceStatus.UNHEALTHY, ServiceStatus.STOPPED)
            ]
            
        if not healthy_instances:
            return None
        
        # Get weights for each instance (default to 1 if not specified)
        weights = [
            instance.metadata.get("weight", 1) for instance in healthy_instances
        ]
        
        # Ensure all weights are positive
        weights = [max(1, weight) for weight in weights]
        
        # Select an instance based on weights
        total_weight = sum(weights)
        r = random.uniform(0, total_weight)
        upto = 0
        
        for i, weight in enumerate(weights):
            upto += weight
            if upto >= r:
                return healthy_instances[i]
        
        # Fallback to the last instance if something went wrong
        return healthy_instances[-1]