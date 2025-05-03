"""
Integration tests for microservices architecture components.

This module contains integration tests for the microservices architecture
components including service discovery, message queue, API gateway, and
circuit breaker.
"""

import json
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
import requests

# Import in-memory implementations for testing
from services.discovery.memory_registry import InMemoryServiceRegistry
from services.service_discovery.discovery_client import ServiceDiscoveryClient
from services.service_discovery.load_balancer import (
    LoadBalancer,
    RandomStrategy,
    RoundRobinStrategy,
    WeightedRandomStrategy,
)
from services.service_discovery.service_registry import ServiceInstance


class TestMicroservicesIntegration:
    """Integration tests for microservices architecture components."""

    def setup_method(self):
        """Set up test fixtures."""
        # Use in-memory registry for testing
        self.registry = InMemoryServiceRegistry()

        # Create test services
        self.services = {
            "auth-service": {
                "host": "localhost",
                "port": 8001,
                "version": "1.0.0",
                "dependencies": [],
            },
            "user-service": {
                "host": "localhost",
                "port": 8002,
                "version": "1.0.0",
                "dependencies": ["auth-service"],
            },
            "product-service": {
                "host": "localhost",
                "port": 8003,
                "version": "1.0.0",
                "dependencies": [],
            },
            "order-service": {
                "host": "localhost",
                "port": 8004,
                "version": "1.0.0",
                "dependencies": ["user-service", "product-service"],
            },
            "api-gateway": {
                "host": "localhost",
                "port": 8000,
                "version": "1.0.0",
                "dependencies": [
                    "auth-service",
                    "user-service",
                    "product-service",
                    "order-service",
                ],
            },
        }

        # Register test services
        self.service_instances = {}
        for name, info in self.services.items():
            instance = ServiceInstance(
                service_id=f"{name}-instance-1",
                service_name=name,
                host=info["host"],
                port=info["port"],
                version=info["version"],
                metadata={"dependencies": info["dependencies"]},
            )
            self.registry.register(instance)
            self.service_instances[name] = instance

    def test_service_discovery_integration(self):
        """Test service discovery integration with other components."""
        # Create discovery client with mock registry
        client = ServiceDiscoveryClient(service_name="test-client", auto_register=False)
        client.registry = self.registry

        # Test service discovery
        auth_instances = client.discover_service("auth-service")
        assert len(auth_instances) == 1
        assert auth_instances[0].service_name == "auth-service"

        # Test load balancing with round-robin strategy
        client.load_balancer = LoadBalancer(strategy=RoundRobinStrategy())

        # Add more instances for auth-service
        for i in range(2, 4):
            instance = ServiceInstance(
                service_id=f"auth-service-instance-{i}",
                service_name="auth-service",
                host="localhost",
                port=8001 + i,
                version="1.0.0",
            )
            self.registry.register(instance)

        # Test round-robin load balancing
        selected_instances = []
        for _ in range(6):  # Should cycle through all instances twice
            instance = client.get_service_instance("auth-service")
            selected_instances.append(instance.service_id)

        # Verify all instances were used
        assert len(set(selected_instances)) == 3

        # Test dependency resolution
        dependencies = []

        def resolve_dependencies(service_name, visited=None):
            """Recursively resolve dependencies for a service."""
            if visited is None:
                visited = set()

            if service_name in visited:
                return

            visited.add(service_name)
            service = client.get_service_instance(service_name)

            if not service:
                return

            service_deps = service.metadata.get("dependencies", [])
            for dep in service_deps:
                resolve_dependencies(dep, visited)

            dependencies.append(service_name)

        # Resolve dependencies for api-gateway
        resolve_dependencies("api-gateway")

        # Verify dependency resolution order
        # Dependencies should come before the services that depend on them
        assert "auth-service" in dependencies
        assert "user-service" in dependencies
        assert "product-service" in dependencies
        assert "order-service" in dependencies
        assert "api-gateway" in dependencies

        # Check that auth-service comes before user-service
        assert dependencies.index("auth-service") < dependencies.index("user-service")

        # Check that user-service and product-service come before order-service
        assert dependencies.index("user-service") < dependencies.index("order-service")
        assert dependencies.index("product-service") < dependencies.index("order-service")

        # Check that all dependencies come before api-gateway
        for dep in ["auth-service", "user-service", "product-service", "order-service"]:
            assert dependencies.index(dep) < dependencies.index("api-gateway")

    def test_service_health_monitoring(self):
        """Test service health monitoring integration."""
        # Create a service with health check
        health_service = ServiceInstance(
            service_id="health-test-service",
            service_name="health-service",
            host="localhost",
            port=8010,
            health_check_url="/health",
        )
        self.registry.register(health_service)

        # Mock health check responses
        health_checks = {"health-test-service": True}  # Initially healthy

        def mock_health_check(service_id):
            """Mock health check function."""
            return health_checks.get(service_id, False)

        # Patch the health check method
        with patch.object(self.registry, "check_health", side_effect=mock_health_check):
            # Verify service is initially healthy
            assert self.registry.get_service_health("health-test-service")

            # Make service unhealthy
            health_checks["health-test-service"] = False

            # Verify service is now unhealthy
            assert not self.registry.get_service_health("health-test-service")

            # Create discovery client with health-aware load balancing
            client = ServiceDiscoveryClient(service_name="test-client", auto_register=False)
            client.registry = self.registry

            # Add a healthy instance
            healthy_instance = ServiceInstance(
                service_id="health-service-healthy",
                service_name="health-service",
                host="localhost",
                port=8011,
                health_check_url="/health",
            )
            self.registry.register(healthy_instance)
            health_checks["health-service-healthy"] = True

            # Test health-aware load balancing
            # Should only select the healthy instance
            for _ in range(5):
                instance = client.get_service_instance("health-service")
                assert instance.service_id == "health-service-healthy"

    def test_service_versioning(self):
        """Test service versioning and compatibility."""
        # Create multiple versions of a service
        versions = ["1.0.0", "1.1.0", "2.0.0"]
        for i, version in enumerate(versions):
            instance = ServiceInstance(
                service_id=f"version-service-{i}",
                service_name="version-service",
                host="localhost",
                port=8020 + i,
                version=version,
                metadata={"features": [f"feature-{j}" for j in range(i + 1)]},
            )
            self.registry.register(instance)

        # Create discovery client
        client = ServiceDiscoveryClient(service_name="test-client", auto_register=False)
        client.registry = self.registry

        # Test version-specific discovery
        v1_instances = client.discover_service("version-service", version="1.0.0")
        assert len(v1_instances) == 1
        assert v1_instances[0].version == "1.0.0"

        # Test version compatibility (all 1.x versions)
        v1x_instances = client.discover_service("version-service", version_prefix="1.")
        assert len(v1x_instances) == 2
        assert all(i.version.startswith("1.") for i in v1x_instances)

        # Test feature-based selection
        def has_feature(instance, feature):
            """Check if an instance has a specific feature."""
            return feature in instance.metadata.get("features", [])

        # Find instances with feature-1
        feature_instances = [
            i for i in client.discover_service("version-service") if has_feature(i, "feature-1")
        ]
        assert len(feature_instances) == 2
        assert all(i.version in ["1.1.0", "2.0.0"] for i in feature_instances)

        # Test weighted load balancing based on version
        def version_weight(instance):
            """Calculate weight based on version."""
            if instance.version == "2.0.0":
                return 10
            elif instance.version == "1.1.0":
                return 5
            return 1

        # Create weighted strategy
        weighted_strategy = WeightedRandomStrategy(version_weight)
        client.load_balancer = LoadBalancer(strategy=weighted_strategy)

        # Select instances multiple times
        selected_versions = {v: 0 for v in versions}
        for _ in range(100):
            instance = client.get_service_instance("version-service")
            selected_versions[instance.version] += 1

        # Verify distribution favors higher versions
        assert selected_versions["2.0.0"] > selected_versions["1.1.0"]
        assert selected_versions["1.1.0"] > selected_versions["1.0.0"]


if __name__ == "__main__":
    pytest.main(["-v", "test_microservices_integration.py"])
