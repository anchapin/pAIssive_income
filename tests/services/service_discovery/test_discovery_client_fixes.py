"""Tests for the fixes in services/service_discovery/discovery_client.py."""

import unittest
from unittest.mock import patch, MagicMock, call

import pytest

from services.service_discovery.discovery_client import ConsulServiceRegistry


class TestDiscoveryClientFixes(unittest.TestCase):
    """Test cases for the fixes in discovery_client.py."""

    @patch('services.service_discovery.discovery_client.logging')
    def test_register_service_uses_tags_parameter(self, mock_logging):
        """Test that register_service uses the tags parameter."""
        # Create a ConsulServiceRegistry instance
        registry = ConsulServiceRegistry()
        
        # Call register_service with tags
        test_tags = ["tag1", "tag2", "tag3"]
        registry.register_service(
            service_name="test-service",
            port=8080,
            health_check_path="/health",
            tags=test_tags
        )
        
        # Verify that logging.info was called and includes the tags
        mock_logging.info.assert_any_call(f"Service tags: {test_tags}")

    @patch('services.service_discovery.discovery_client.logging')
    def test_register_service_uses_metadata_parameter(self, mock_logging):
        """Test that register_service uses the metadata parameter."""
        # Create a ConsulServiceRegistry instance
        registry = ConsulServiceRegistry()
        
        # Call register_service with metadata
        test_metadata = {"version": "1.0.0", "environment": "test"}
        registry.register_service(
            service_name="test-service",
            port=8080,
            health_check_path="/health",
            metadata=test_metadata
        )
        
        # Verify that logging.info was called and includes the metadata
        mock_logging.info.assert_any_call(f"Service metadata: {test_metadata}")

    @patch('services.service_discovery.discovery_client.logging')
    def test_register_service_with_default_values(self, mock_logging):
        """Test that register_service uses default values for tags and metadata."""
        # Create a ConsulServiceRegistry instance
        registry = ConsulServiceRegistry()
        
        # Call register_service without tags and metadata
        registry.register_service(
            service_name="test-service",
            port=8080,
            health_check_path="/health"
        )
        
        # Verify that logging.info was called with the default values
        mock_logging.info.assert_any_call("Service tags: []")
        mock_logging.info.assert_any_call("Service metadata: {}")

    @patch('services.service_discovery.discovery_client.logging')
    def test_register_service_logs_all_parameters(self, mock_logging):
        """Test that register_service logs all parameters."""
        # Create a ConsulServiceRegistry instance
        registry = ConsulServiceRegistry()
        
        # Call register_service with all parameters
        test_tags = ["tag1", "tag2"]
        test_metadata = {"version": "1.0.0"}
        registry.register_service(
            service_name="test-service",
            port=8080,
            health_check_path="/custom-health",
            tags=test_tags,
            metadata=test_metadata
        )
        
        # Verify that all parameters are logged
        expected_calls = [
            call("Registering service test-service on port 8080"),
            call(f"Service tags: {test_tags}"),
            call(f"Service metadata: {test_metadata}")
        ]
        mock_logging.info.assert_has_calls(expected_calls, any_order=True)

    def test_register_service_returns_true(self):
        """Test that register_service returns True."""
        # Create a ConsulServiceRegistry instance
        registry = ConsulServiceRegistry()
        
        # Call register_service
        result = registry.register_service(
            service_name="test-service",
            port=8080
        )
        
        # Verify that the result is True
        assert result is True


if __name__ == "__main__":
    unittest.main()
