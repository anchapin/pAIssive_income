"""
Tests for service discovery functionality.

This module contains tests for the service discovery and registration.
"""


from unittest.mock import MagicMock, patch

import pytest

from api.config import APIConfig
from api.service_discovery import ServiceDiscovery, ServiceRegistration


class TestServiceDiscovery

:
    """Tests for service discovery functionality."""

    @patch("consul.Consul")
    def test_service_registration(self, mock_consul):
        """Test service registration with Consul."""
        # Create mock consul client
        mock_client = MagicMock()
        mock_consul.return_value = mock_client

        # Configure mock response for registration
        mock_client.agent.service.register.return_value = True

        # Create service registration
        config = APIConfig(
            service_name="test-service",
            service_host="localhost",
            service_port=8000,
            consul_host="localhost",
            consul_port=8500,
            enable_service_discovery=True,
        )

        service_reg = ServiceRegistration(config)

        # Register service
        result = service_reg.register()

        # Verify registration was called
        assert result is True
        mock_client.agent.service.register.assert_called_once()

        # Verify registration parameters
        call_args = mock_client.agent.service.register.call_args[1]
        assert call_args["name"] == "test-service"
        assert call_args["address"] == "localhost"
        assert call_args["port"] == 8000
        assert "check" in call_args
        assert call_args["check"]["http"] == "http://localhost:8000/health"

    @patch("consul.Consul")
    def test_service_deregistration(self, mock_consul):
        """Test service deregistration with Consul."""
        # Create mock consul client
        mock_client = MagicMock()
        mock_consul.return_value = mock_client

        # Configure mock response for deregistration
        mock_client.agent.service.deregister.return_value = True

        # Create service registration
        config = APIConfig(
            service_name="test-service",
            service_host="localhost",
            service_port=8000,
            consul_host="localhost",
            consul_port=8500,
            enable_service_discovery=True,
        )

        service_reg = ServiceRegistration(config)

        # Deregister service
        result = service_reg.deregister()

        # Verify deregistration was called
        assert result is True
        mock_client.agent.service.deregister.assert_called_once_with("test-service")

    @patch("consul.Consul")
    def test_service_discovery(self, mock_consul):
        """Test discovering services with Consul."""
        # Create mock consul client
        mock_client = MagicMock()
        mock_consul.return_value = mock_client

        # Configure mock response for service discovery
        mock_client.catalog.service.return_value = (
            None,  # Index
            [
                {
                    "ServiceID": "service-1",
                    "ServiceName": "test-service",
                    "ServiceAddress": "10.0.0.1",
                    "ServicePort": 8000,
                    "ServiceTags": ["v1", "production"],
                },
                {
                    "ServiceID": "service-2",
                    "ServiceName": "test-service",
                    "ServiceAddress": "10.0.0.2",
                    "ServicePort": 8000,
                    "ServiceTags": ["v1", "staging"],
                },
            ],
        )

        # Create service discovery
        config = APIConfig(
            consul_host="localhost", consul_port=8500, enable_service_discovery=True
        )

        discovery = ServiceDiscovery(config)

        # Discover services
        services = discovery.get_services("test-service")

        # Verify discovery was called
        mock_client.catalog.service.assert_called_once_with("test-service")

        # Verify discovered services
        assert len(services) == 2
        assert services[0]["address"] == "10.0.0.1"
        assert services[0]["port"] == 8000
        assert services[1]["address"] == "10.0.0.2"
        assert services[1]["port"] == 8000

    @patch("consul.Consul")
    def test_service_discovery_with_tag(self, mock_consul):
        """Test discovering services with specific tags."""
        # Create mock consul client
        mock_client = MagicMock()
        mock_consul.return_value = mock_client

        # Configure mock response for service discovery
        mock_client.catalog.service.return_value = (
            None,  # Index
            [
                {
                    "ServiceID": "service-2",
                    "ServiceName": "test-service",
                    "ServiceAddress": "10.0.0.2",
                    "ServicePort": 8000,
                    "ServiceTags": ["v1", "staging"],
                },
            ],
        )

        # Create service discovery
        config = APIConfig(
            consul_host="localhost", consul_port=8500, enable_service_discovery=True
        )

        discovery = ServiceDiscovery(config)

        # Discover services with tag
        services = discovery.get_services("test-service", tag="staging")

        # Verify discovery was called with tag
        mock_client.catalog.service.assert_called_once_with(
            "test-service", tag="staging"
        )

        # Verify discovered services
        assert len(services) == 1
        assert services[0]["address"] == "10.0.0.2"
        assert services[0]["port"] == 8000
        assert "staging" in services[0]["tags"]

    @patch("consul.Consul")
    def test_health_check(self, mock_consul):
        """Test health check registration and status."""
        # Create mock consul client
        mock_client = MagicMock()
        mock_consul.return_value = mock_client

        # Configure mock response for health checks
        mock_client.agent.checks.return_value = {
            "service:test-service": {
                "Node": "node1",
                "CheckID": "service:test-service",
                "Name": "Service 'test-service' check",
                "Status": "passing",
                "ServiceName": "test-service",
            }
        }

        # Create service registration with health check
        config = APIConfig(
            service_name="test-service",
            service_host="localhost",
            service_port=8000,
            consul_host="localhost",
            consul_port=8500,
            enable_service_discovery=True,
            health_check_interval="10s",
            health_check_timeout="5s",
        )

        service_reg = ServiceRegistration(config)

        # Register service
        service_reg.register()

        # Verify registration parameters for health check
        call_args = mock_client.agent.service.register.call_args[1]
        assert "check" in call_args
        assert call_args["check"]["http"] == "http://localhost:8000/health"
        assert call_args["check"]["interval"] == "10s"
        assert call_args["check"]["timeout"] == "5s"

        # Get health check status
        health_status = service_reg.get_health_status()

        # Verify health check status
        mock_client.agent.checks.assert_called_once()
        assert health_status == "passing"

    @patch("consul.Consul")
    def test_service_discovery_disabled(self, mock_consul):
        """Test behavior when service discovery is disabled."""
        # Create service registration with discovery disabled
        config = APIConfig(
            service_name="test-service",
            service_host="localhost",
            service_port=8000,
            consul_host="localhost",
            consul_port=8500,
            enable_service_discovery=False,
        )

        service_reg = ServiceRegistration(config)

        # Register service
        result = service_reg.register()

        # Verify registration was not called
        assert result is False
        mock_consul.assert_not_called()

        # Create service discovery with discovery disabled
        discovery = ServiceDiscovery(config)

        # Discover services
        services = discovery.get_services("test-service")

        # Verify discovery was not called and empty list returned
        assert services == []
        mock_consul.assert_not_called()


if __name__ == "__main__":
    pytest.main(["-v", "test_service_discovery.py"])