"""Tests for the load balancer module."""

import logging
import unittest
from unittest.mock import MagicMock, patch

import pytest

from services.service_discovery.load_balancer import (
    LeastConnectionsStrategy,
    LoadBalancer,
    RandomStrategy,
    RoundRobinStrategy,
    WeightedRandomStrategy,
)


class TestLoadBalancer(unittest.TestCase):
    """Test cases for the LoadBalancer class."""

    def setUp(self):
        """Set up test environment."""
        self.instances = [
            {"id": "service1", "address": "localhost", "port": 8001},
            {"id": "service2", "address": "localhost", "port": 8002},
            {"id": "service3", "address": "localhost", "port": 8003},
        ]

    def test_init_with_default_strategy(self):
        """Test initialization with default strategy."""
        load_balancer = LoadBalancer()
        self.assertIsInstance(load_balancer.strategy, RoundRobinStrategy)

    def test_init_with_round_robin_strategy(self):
        """Test initialization with round robin strategy."""
        load_balancer = LoadBalancer(strategy="round_robin")
        self.assertIsInstance(load_balancer.strategy, RoundRobinStrategy)

    def test_init_with_random_strategy(self):
        """Test initialization with random strategy."""
        load_balancer = LoadBalancer(strategy="random")
        self.assertIsInstance(load_balancer.strategy, RandomStrategy)

    def test_init_with_weighted_random_strategy(self):
        """Test initialization with weighted random strategy."""
        load_balancer = LoadBalancer(strategy="weighted_random")
        self.assertIsInstance(load_balancer.strategy, WeightedRandomStrategy)

    def test_init_with_least_connections_strategy(self):
        """Test initialization with least connections strategy."""
        load_balancer = LoadBalancer(strategy="least_connections")
        self.assertIsInstance(load_balancer.strategy, LeastConnectionsStrategy)

    def test_init_with_invalid_strategy(self):
        """Test initialization with invalid strategy."""
        with self.assertRaises(ValueError):
            LoadBalancer(strategy="invalid_strategy")

    def test_select_instance_with_empty_instances(self):
        """Test select_instance with empty instances."""
        load_balancer = LoadBalancer()
        instance = load_balancer.select_instance([])
        self.assertIsNone(instance)

    def test_select_instance_with_round_robin_strategy(self):
        """Test select_instance with round robin strategy."""
        load_balancer = LoadBalancer(strategy="round_robin")

        # First call should return the first instance
        instance = load_balancer.select_instance(self.instances)
        self.assertEqual(instance, self.instances[0])

        # Second call should return the second instance
        instance = load_balancer.select_instance(self.instances)
        self.assertEqual(instance, self.instances[1])

        # Third call should return the third instance
        instance = load_balancer.select_instance(self.instances)
        self.assertEqual(instance, self.instances[2])

        # Fourth call should wrap around to the first instance
        instance = load_balancer.select_instance(self.instances)
        self.assertEqual(instance, self.instances[0])

    def test_select_instance_with_random_strategy(self):
        """Test select_instance with random strategy."""
        load_balancer = LoadBalancer(strategy="random")

        # Mock the random.choice function to return a specific instance
        with patch("random.choice", return_value=self.instances[1]):
            instance = load_balancer.select_instance(self.instances)
            self.assertEqual(instance, self.instances[1])

    def test_select_instance_with_weighted_random_strategy(self):
        """Test select_instance with weighted random strategy."""
        # Define a weight function that gives higher weight to the second instance
        def weight_function(instance):
            if instance["id"] == "service2":
                return 10
            return 1

        # Create a weighted random strategy with the weight function
        strategy = WeightedRandomStrategy(weight_function)
        load_balancer = LoadBalancer()
        load_balancer.strategy = strategy

        # Mock the random.choices function to return a specific instance
        with patch("random.choices", return_value=[self.instances[1]]):
            instance = load_balancer.select_instance(self.instances)
            self.assertEqual(instance, self.instances[1])

    def test_select_instance_with_least_connections_strategy(self):
        """Test select_instance with least connections strategy."""
        # Create instances with connection counts
        instances_with_connections = [
            {"id": "service1", "address": "localhost", "port": 8001, "connections": 5},
            {"id": "service2", "address": "localhost", "port": 8002, "connections": 2},
            {"id": "service3", "address": "localhost", "port": 8003, "connections": 8},
        ]

        load_balancer = LoadBalancer(strategy="least_connections")

        # The instance with the least connections should be selected
        instance = load_balancer.select_instance(instances_with_connections)
        self.assertEqual(instance, instances_with_connections[1])


class TestRoundRobinStrategy(unittest.TestCase):
    """Test cases for the RoundRobinStrategy class."""

    def setUp(self):
        """Set up test environment."""
        self.instances = [
            {"id": "service1", "address": "localhost", "port": 8001},
            {"id": "service2", "address": "localhost", "port": 8002},
            {"id": "service3", "address": "localhost", "port": 8003},
        ]
        self.strategy = RoundRobinStrategy()

    def test_select_instance(self):
        """Test select_instance method."""
        # First call should return the first instance
        instance = self.strategy.select_instance(self.instances)
        self.assertEqual(instance, self.instances[0])

        # Second call should return the second instance
        instance = self.strategy.select_instance(self.instances)
        self.assertEqual(instance, self.instances[1])

        # Third call should return the third instance
        instance = self.strategy.select_instance(self.instances)
        self.assertEqual(instance, self.instances[2])

        # Fourth call should wrap around to the first instance
        instance = self.strategy.select_instance(self.instances)
        self.assertEqual(instance, self.instances[0])


if __name__ == "__main__":
    unittest.main()
