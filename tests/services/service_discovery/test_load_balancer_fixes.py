"""Tests for the fixes in services/service_discovery/load_balancer.py."""

import logging
import unittest
from unittest.mock import patch, MagicMock

import pytest

from services.service_discovery.load_balancer import LoadBalancingStrategy


class TestLoadBalancerFixes(unittest.TestCase):
    """Test cases for the fixes in load_balancer.py."""

    def test_protocol_method_raises_not_implemented_error(self):
        """Test that the Protocol method raises NotImplementedError."""
        # Create a class that implements the LoadBalancingStrategy protocol
        class TestStrategy(LoadBalancingStrategy):
            pass
        
        # Create an instance of the test strategy
        strategy = TestStrategy()
        
        # Call select_instance and expect NotImplementedError
        with pytest.raises(NotImplementedError) as excinfo:
            strategy.select_instance([])
        
        # Verify the error message
        assert "This method must be implemented by concrete strategy classes" in str(excinfo.value)

    def test_protocol_method_documentation(self):
        """Test that the Protocol method has proper documentation."""
        # Get the docstring of the select_instance method
        docstring = LoadBalancingStrategy.select_instance.__doc__
        
        # Verify that the docstring exists and contains expected information
        assert docstring is not None
        assert "Select an instance from a list of instances" in docstring
        assert "Args:" in docstring
        assert "instances: List of service instances" in docstring
        assert "Returns:" in docstring
        assert "Selected instance or None if no instances are available" in docstring

    def test_concrete_strategies_implement_select_instance(self):
        """Test that concrete strategies implement the select_instance method."""
        from services.service_discovery.load_balancer import (
            RoundRobinStrategy,
            RandomStrategy,
            WeightedRandomStrategy,
            LeastConnectionsStrategy
        )
        
        # Create instances of each concrete strategy
        round_robin = RoundRobinStrategy()
        random_strategy = RandomStrategy()
        weighted_random = WeightedRandomStrategy(lambda _: 1.0)
        least_connections = LeastConnectionsStrategy()
        
        # Verify that each strategy has a select_instance method that doesn't raise NotImplementedError
        test_instances = [{"id": "test", "address": "localhost", "port": 8080}]
        
        # These should not raise NotImplementedError
        round_robin.select_instance(test_instances)
        random_strategy.select_instance(test_instances)
        weighted_random.select_instance(test_instances)
        least_connections.select_instance(test_instances)

    def test_load_balancer_uses_strategy_select_instance(self):
        """Test that LoadBalancer uses the strategy's select_instance method."""
        from services.service_discovery.load_balancer import LoadBalancer
        
        # Create a mock strategy
        mock_strategy = MagicMock()
        mock_strategy.select_instance.return_value = {"id": "selected"}
        
        # Create a LoadBalancer with the mock strategy
        load_balancer = LoadBalancer()
        load_balancer.strategy = mock_strategy
        
        # Call select_instance
        test_instances = [{"id": "test1"}, {"id": "test2"}]
        result = load_balancer.select_instance(test_instances)
        
        # Verify that the strategy's select_instance method was called
        mock_strategy.select_instance.assert_called_once_with(test_instances)
        
        # Verify that the result is the value returned by the strategy
        assert result == {"id": "selected"}


if __name__ == "__main__":
    unittest.main()
