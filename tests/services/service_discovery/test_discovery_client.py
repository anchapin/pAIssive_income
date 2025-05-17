"""Tests for the service discovery client."""

import logging
import unittest
from unittest.mock import patch, MagicMock

import pytest

from services.service_discovery.discovery_client import ServiceDiscoveryClient


class TestServiceDiscoveryClient(unittest.TestCase):
    """Test cases for the ServiceDiscoveryClient class."""

    def setUp(self):
        """Set up test environment."""
        # Create a mock registry
        self.mock_registry = MagicMock()

        # Create a client with the mock registry
        with patch("services.service_discovery.discovery_client.ConsulServiceRegistry",
                  return_value=self.mock_registry):
            self.client = ServiceDiscoveryClient(
                service_name="test-service",
                port=8000,
                auto_register=False
            )

    def test_init(self):
        """Test initialization of ServiceDiscoveryClient."""
        # Create a client with auto_register=True
        with patch("services.service_discovery.discovery_client.ConsulServiceRegistry") as mock_registry_class:
            mock_registry = MagicMock()
            mock_registry_class.return_value = mock_registry

            client = ServiceDiscoveryClient(
                service_name="test-service",
                port=8000,
                auto_register=True
            )

            # Verify that register_service was called
            mock_registry.register_service.assert_called_once_with(
                service_name="test-service",
                port=8000,
                health_check_path="/health",
                tags=[],
                metadata={}
            )

    def test_discover_service(self):
        """Test discover_service method."""
        # Mock the registry's get_service_instances method
        mock_instances = [
            {"id": "service1", "address": "localhost", "port": 8001},
            {"id": "service2", "address": "localhost", "port": 8002}
        ]
        self.mock_registry.get_service_instances.return_value = mock_instances

        # Call the method
        instances = self.client.discover_service("target-service")

        # Verify the result
        self.assertEqual(instances, mock_instances)
        self.mock_registry.get_service_instances.assert_called_once_with("target-service")

    def test_discover_service_empty(self):
        """Test discover_service method with no instances."""
        # Mock the registry's get_service_instances method to return empty list
        self.mock_registry.get_service_instances.return_value = []

        # Call the method
        instances = self.client.discover_service("target-service")

        # Verify the result
        self.assertEqual(instances, [])
        self.mock_registry.get_service_instances.assert_called_once_with("target-service")

    def test_get_service_url(self):
        """Test get_service_url method."""
        # Mock the registry's get_service_instances method
        mock_instances = [
            {"id": "service1", "address": "localhost", "port": 8001},
            {"id": "service2", "address": "localhost", "port": 8002}
        ]
        self.mock_registry.get_service_instances.return_value = mock_instances

        # Mock the load balancer's select_instance method
        self.client.load_balancer.select_instance = MagicMock(return_value=mock_instances[0])

        # Call the method
        url = self.client.get_service_url("target-service", "/api/resource")

        # Verify the result
        self.assertEqual(url, "http://localhost:8001/api/resource")
        self.mock_registry.get_service_instances.assert_called_once_with("target-service")
        self.client.load_balancer.select_instance.assert_called_once_with(mock_instances)

    def test_get_service_url_no_instances(self):
        """Test get_service_url method with no instances."""
        # Mock the registry's get_service_instances method to return empty list
        self.mock_registry.get_service_instances.return_value = []

        # Call the method
        url = self.client.get_service_url("target-service", "/api/resource")

        # Verify the result
        self.assertIsNone(url)
        self.mock_registry.get_service_instances.assert_called_once_with("target-service")

    def test_register_service(self):
        """Test register_service method."""
        # Call the method
        self.client.register_service(
            service_name="new-service",
            port=8003,
            health_check_path="/health",
            tags=["api", "v1"],
            metadata={"version": "1.0.0"}
        )

        # Verify that the registry's register_service method was called
        self.mock_registry.register_service.assert_called_once_with(
            service_name="new-service",
            port=8003,
            health_check_path="/health",
            tags=["api", "v1"],
            metadata={"version": "1.0.0"}
        )

    def test_deregister_service(self):
        """Test deregister_service method."""
        # Call the method
        self.client.deregister_service("service-id")

        # Verify that the registry's deregister_service method was called
        self.mock_registry.deregister_service.assert_called_once_with("service-id")


if __name__ == "__main__":
    unittest.main()
