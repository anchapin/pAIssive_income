"""Tests for the ConsulServiceRegistry class."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from services.service_discovery.discovery_client import ConsulServiceRegistry


class TestConsulServiceRegistry:
    """Test cases for the ConsulServiceRegistry class."""

    def test_init(self):
        """Test initialization of ConsulServiceRegistry."""
        # Test with default parameters
        registry = ConsulServiceRegistry()
        assert registry.host == "localhost"
        assert registry.port == 8500

        # Test with custom parameters
        registry = ConsulServiceRegistry(host="consul.example.com", port=8501)
        assert registry.host == "consul.example.com"
        assert registry.port == 8501

    @patch("services.service_discovery.discovery_client.logging.info")
    def test_register_service(self, mock_logging_info):
        """Test register_service method."""
        registry = ConsulServiceRegistry()

        # Test with minimal parameters
        result = registry.register_service("test-service", 8080)
        assert result is True
        # Check that the first call to logging.info has the expected message
        mock_logging_info.assert_any_call("Registering service test-service on port 8080")

        # Test with all parameters
        result = registry.register_service(
            "test-service",
            8080,
            health_check_path="/custom-health",
            tags=["api", "v1"],
            metadata={"version": "1.0.0"}
        )
        assert result is True
        mock_logging_info.assert_any_call("Registering service test-service on port 8080")

    @patch("services.service_discovery.discovery_client.logging.info")
    def test_deregister_service(self, mock_logging_info):
        """Test deregister_service method."""
        registry = ConsulServiceRegistry()

        result = registry.deregister_service("test-service-id")
        assert result is True
        mock_logging_info.assert_called_with("Deregistering service test-service-id")

    @patch("services.service_discovery.discovery_client.logging.info")
    def test_get_service_instances(self, mock_logging_info):
        """Test get_service_instances method."""
        registry = ConsulServiceRegistry()

        # Test with a service that has instances
        instances = registry.get_service_instances("test-service")
        assert len(instances) == 2
        assert instances[0]["id"] == "test-service-1"
        assert instances[0]["address"] == "localhost"
        assert instances[0]["port"] == 8001
        assert instances[1]["id"] == "test-service-2"
        assert instances[1]["address"] == "localhost"
        assert instances[1]["port"] == 8002
        mock_logging_info.assert_called_with("Looking up instances for service test-service")

        # Test with a service that has no instances
        instances = registry.get_service_instances("unknown-service")
        assert len(instances) == 0
        mock_logging_info.assert_called_with("Looking up instances for service unknown-service")
