"""
Integration tests for service dependency resolution.

This module contains tests for service dependency resolution in the
microservices architecture.
"""


import pytest
from unittest.mock import patch, MagicMock

from services.discovery import 

(
    ServiceDiscoveryClient,
    ServiceInstance,
    ServiceRegistry,
    InMemoryServiceRegistry
)
from services.dependency import (
    DependencyResolver,
    DependencyGraph,
    CircularDependencyError
)


@pytest.fixture
def in_memory_registry():
    """Create an in-memory service registry."""
    registry = InMemoryServiceRegistry()
    
    # Register test services
    services = {
        "auth-service": {
            "host": "localhost",
            "port": 8001,
            "version": "1.0.0",
            "dependencies": []
        },
        "user-service": {
            "host": "localhost",
            "port": 8002,
            "version": "1.0.0",
            "dependencies": ["auth-service"]
        },
        "product-service": {
            "host": "localhost",
            "port": 8003,
            "version": "1.0.0",
            "dependencies": []
        },
        "order-service": {
            "host": "localhost",
            "port": 8004,
            "version": "1.0.0",
            "dependencies": ["user-service", "product-service"]
        },
        "api-gateway": {
            "host": "localhost",
            "port": 8000,
            "version": "1.0.0",
            "dependencies": ["auth-service", "user-service", "product-service", "order-service"]
        }
    }
    
    # Register test services
    service_instances = {}
    for name, info in services.items():
        instance = ServiceInstance(
            service_id=f"{name}-instance-1",
            service_name=name,
            host=info["host"],
            port=info["port"],
            version=info["version"],
            metadata={"dependencies": info["dependencies"]}
        )
        registry.register(instance)
        service_instances[name] = instance
    
    return registry


@pytest.fixture
def dependency_resolver(in_memory_registry):
    """Create a dependency resolver."""
    resolver = DependencyResolver(registry=in_memory_registry)
    return resolver


class TestServiceDependencyResolution:
    """Test service dependency resolution."""

    def test_dependency_resolution(self, dependency_resolver):
        """Test dependency resolution."""
        # Resolve dependencies for api-gateway
        dependencies = dependency_resolver.resolve_dependencies("api-gateway")
        
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

    def test_circular_dependency_detection(self, in_memory_registry):
        """Test circular dependency detection."""
        # Create circular dependency
        circular_services = {
            "service-a": {
                "host": "localhost",
                "port": 9001,
                "version": "1.0.0",
                "dependencies": ["service-b"]
            },
            "service-b": {
                "host": "localhost",
                "port": 9002,
                "version": "1.0.0",
                "dependencies": ["service-c"]
            },
            "service-c": {
                "host": "localhost",
                "port": 9003,
                "version": "1.0.0",
                "dependencies": ["service-a"]
            }
        }
        
        # Register circular services
        for name, info in circular_services.items():
            instance = ServiceInstance(
                service_id=f"{name}-instance-1",
                service_name=name,
                host=info["host"],
                port=info["port"],
                version=info["version"],
                metadata={"dependencies": info["dependencies"]}
            )
            in_memory_registry.register(instance)
        
        # Create resolver with circular dependencies
        resolver = DependencyResolver(registry=in_memory_registry)
        
        # Attempt to resolve circular dependencies
        with pytest.raises(CircularDependencyError):
            resolver.resolve_dependencies("service-a")

    def test_missing_dependency_handling(self, dependency_resolver, in_memory_registry):
        """Test handling of missing dependencies."""
        # Register a service with a missing dependency
        instance = ServiceInstance(
            service_id="missing-dep-service-instance-1",
            service_name="missing-dep-service",
            host="localhost",
            port=9004,
            version="1.0.0",
            metadata={"dependencies": ["non-existent-service"]}
        )
        in_memory_registry.register(instance)
        
        # Attempt to resolve dependencies
        with pytest.raises(Exception):
            dependency_resolver.resolve_dependencies("missing-dep-service")

    def test_dependency_graph_visualization(self, dependency_resolver):
        """Test dependency graph visualization."""
        # Create dependency graph
        graph = dependency_resolver.create_dependency_graph()
        
        # Check that the graph contains all services
        assert "auth-service" in graph.nodes
        assert "user-service" in graph.nodes
        assert "product-service" in graph.nodes
        assert "order-service" in graph.nodes
        assert "api-gateway" in graph.nodes
        
        # Check that the graph contains all dependencies
        assert "auth-service" in graph.get_dependencies("user-service")
        assert "user-service" in graph.get_dependencies("order-service")
        assert "product-service" in graph.get_dependencies("order-service")
        
        # Check that the graph contains all dependents
        assert "user-service" in graph.get_dependents("auth-service")
        assert "order-service" in graph.get_dependents("user-service")
        assert "order-service" in graph.get_dependents("product-service")

    def test_partial_dependency_resolution(self, dependency_resolver):
        """Test partial dependency resolution."""
        # Resolve dependencies for order-service
        dependencies = dependency_resolver.resolve_dependencies("order-service")
        
        # Verify dependency resolution order
        assert "auth-service" in dependencies
        assert "user-service" in dependencies
        assert "product-service" in dependencies
        assert "order-service" in dependencies
        
        # Check that api-gateway is not included
        assert "api-gateway" not in dependencies
        
        # Check that auth-service comes before user-service
        assert dependencies.index("auth-service") < dependencies.index("user-service")
        
        # Check that user-service and product-service come before order-service
        assert dependencies.index("user-service") < dependencies.index("order-service")
        assert dependencies.index("product-service") < dependencies.index("order-service")


if __name__ == "__main__":
    pytest.main(["-v", "test_service_dependency_resolution.py"])