"""
Integration tests for service discovery functionality.
"""


import time
from unittest.mock import patch

import pytest

from services.discovery import 

(
    DiscoveryConfig,
    LoadBalancer,
    ServiceDiscoveryClient,
    ServiceRegistry,
)
from services.errors import (
    LoadBalancingError,
    ServiceNotFoundError,
    ServiceRegistrationError,
)


class TestServiceDiscovery:
    """Integration tests for service discovery functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = DiscoveryConfig(
            registry_host="localhost",
            registry_port=8500,
            service_ttl=30,
            check_interval=5,
        )
        self.registry = ServiceRegistry(self.config)
        self.client = ServiceDiscoveryClient(self.config)
        self.load_balancer = LoadBalancer(self.config)

    def test_service_registration(self):
        """Test service registration workflow."""
        # Service details
        service_info = {
            "name": "ai-model-service",
            "host": "localhost",
            "port": 5000,
            "tags": ["v1", "production"],
            "metadata": {"model_type": "gpt-4", "max_tokens": 4096},
        }

        # Register service
        registration = self.registry.register_service(**service_info)

        # Validate registration
        assert registration["success"] is True
        assert "service_id" in registration
        assert registration["service_status"] == "healthy"

        # Verify service is discoverable
        discovered = self.client.get_service("ai-model-service")
        assert discovered["name"] == service_info["name"]
        assert discovered["host"] == service_info["host"]
        assert discovered["port"] == service_info["port"]
        assert all(tag in discovered["tags"] for tag in service_info["tags"])

        # Clean up
        self.registry.deregister_service(registration["service_id"])

    def test_service_health_checks(self):
        """Test service health checking mechanisms."""
        # Register service with health check
        service_id = self.registry.register_service(
            name="health-check-service",
            host="localhost",
            port=5001,
            health_check_endpoint="/health",
        )["service_id"]

        try:
            # Wait for health check
            time.sleep(self.config.check_interval + 1)

            # Get service health
            health = self.registry.get_service_health(service_id)

            # Validate health check
            assert "status" in health
            assert health["last_check_time"] is not None
            assert "check_output" in health

            # Simulate failing health check
            with patch(
                "services.discovery.ServiceRegistry._check_health"
            ) as mock_check:
                mock_check.return_value = False
                time.sleep(self.config.check_interval + 1)
                health = self.registry.get_service_health(service_id)
                assert health["status"] == "critical"

        finally:
            # Clean up
            self.registry.deregister_service(service_id)

    def test_load_balancing(self):
        """Test load balancing functionality."""
        # Register multiple instances
        service_instances = [
            {"name": "api-service", "host": "localhost", "port": port, "weight": 1}
            for port in range(5010, 5013)
        ]

        service_ids = []
        try:
            # Register services
            for instance in service_instances:
                reg = self.registry.register_service(**instance)
                service_ids.append(reg["service_id"])

            # Test round-robin load balancing
            selected_ports = []
            for _ in range(6):  # Should cycle through all instances twice
                instance = self.load_balancer.get_instance("api-service")
                selected_ports.append(instance["port"])

            # Verify round-robin distribution
            assert len(set(selected_ports)) == 3  # All instances used
            assert selected_ports[:3] != selected_ports[3:]  # Different order in cycles

            # Test weighted load balancing
            self.registry.update_service_metadata(
                service_ids[0], {"weight": 2}  # Double weight for first instance
            )

            # Collect weighted distribution
            port_counts = {5010: 0, 5011: 0, 5012: 0}
            for _ in range(100):
                instance = self.load_balancer.get_instance(
                    "api-service", algorithm="weighted"
                )
                port_counts[instance["port"]] += 1

            # Verify weighted distribution
            assert (
                port_counts[5010] > port_counts[5011]
            )  # Higher weight instance used more
            assert (
                port_counts[5011] == port_counts[5012]
            )  # Equal weight instances used equally

        finally:
            # Clean up
            for service_id in service_ids:
                self.registry.deregister_service(service_id)

    def test_service_discovery_error_handling(self):
        """Test error handling in service discovery."""
        # Test registration with invalid data
        with pytest.raises(ServiceRegistrationError):
            self.registry.register_service(
                name="invalid-service", host="invalid-host", port=-1  # Invalid port
            )

        # Test discovering non-existent service
        with pytest.raises(ServiceNotFoundError):
            self.client.get_service("non-existent-service")

        # Test load balancing with no instances
        with pytest.raises(LoadBalancingError):
            self.load_balancer.get_instance("no-instances-service")

    def test_service_updates_and_deregistration(self):
        """Test service updates and deregistration."""
        # Register service
        service_id = self.registry.register_service(
            name="update-test-service",
            host="localhost",
            port=5020,
            metadata={"version": "1.0"},
        )["service_id"]

        try:
            # Update service metadata
            self.registry.update_service_metadata(
                service_id, {"version": "1.1", "feature_flags": ["beta"]}
            )

            # Verify update
            service = self.client.get_service("update-test-service")
            assert service["metadata"]["version"] == "1.1"
            assert "beta" in service["metadata"]["feature_flags"]

            # Deregister service
            assert self.registry.deregister_service(service_id)["success"]

            # Verify service is no longer discoverable
            with pytest.raises(ServiceNotFoundError):
                self.client.get_service("update-test-service")

        finally:
            # Cleanup attempt (ignore errors)
            try:
                self.registry.deregister_service(service_id)
            except Exception:
                pass

    def test_bulk_operations(self):
        """Test bulk service operations."""
        # Bulk registration
        services = [
            {
                "name": "bulk-service",
                "host": "localhost",
                "port": port,
                "tags": [f"instance-{i}"],
            }
            for i, port in enumerate(range(5030, 5033))
        ]

        service_ids = []
        try:
            # Register multiple services
            results = self.registry.register_services(services)
            service_ids = [r["service_id"] for r in results if r["success"]]

            # Verify all services registered
            assert len(service_ids) == len(services)

            # Test bulk service discovery
            discovered = self.client.get_services(
                service_names=["bulk-service"], tag="instance-1"
            )
            assert len(discovered) == 1
            assert discovered[0]["port"] == 5031

            # Test bulk health check
            health_status = self.registry.get_services_health(service_ids)
            assert len(health_status) == len(service_ids)
            assert all(h["status"] in ["passing", "critical"] for h in health_status)

        finally:
            # Bulk deregistration
            for service_id in service_ids:
                self.registry.deregister_service(service_id)

    def test_service_dependency_resolution(self):
        """Test service dependency resolution."""
        dependencies = {
            "auth-service": {"host": "localhost", "port": 5040, "dependencies": []},
            "user-service": {
                "host": "localhost",
                "port": 5041,
                "dependencies": ["auth-service"],
            },
            "api-gateway": {
                "host": "localhost",
                "port": 5042,
                "dependencies": ["auth-service", "user-service"],
            },
        }

        service_ids = {}
        try:
            # Register services in dependency order
            for service_name, service_info in dependencies.items():
                reg = self.registry.register_service(
                    name=service_name,
                    host=service_info["host"],
                    port=service_info["port"],
                    metadata={"dependencies": service_info["dependencies"]},
                )
                service_ids[service_name] = reg["service_id"]

            # Resolve dependencies for api-gateway
            resolved = self.client.resolve_service_dependencies("api-gateway")

            # Verify dependency resolution
            assert len(resolved) == 3
            assert (
                resolved[0]["name"] == "auth-service"
            )  # Should be first (no dependencies)
            assert resolved[1]["name"] == "user-service"
            assert resolved[2]["name"] == "api-gateway"

            # Test dependency validation
            assert self.client.validate_service_dependencies("api-gateway")["valid"]

        finally:
            # Clean up
            for service_id in service_ids.values():
                self.registry.deregister_service(service_id)


if __name__ == "__main__":
    pytest.main(["-v", "test_service_discovery.py"])