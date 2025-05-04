"""
Integration tests for service version compatibility.

This module contains tests for version compatibility between services in the
microservices architecture.
"""


from unittest.mock import MagicMock, patch

import pytest

(
ServiceDiscoveryClient,
ServiceInstance,
ServiceRegistry,
InMemoryServiceRegistry
)
from services.versioning import (SemanticVersion, VersionCompatibilityChecker,
VersionManager, VersionMismatchError)


@pytest.fixture
def in_memory_registry():
    """Create an in-memory service registry with versioned services."""
    registry = InMemoryServiceRegistry()

    # Register test services with different versions
    services = [
    # Auth service versions
    {
    "service_name": "auth-service",
    "host": "localhost",
    "port": 8001,
    "version": "1.0.0",
    "api_version": "v1"
    },
    {
    "service_name": "auth-service",
    "host": "localhost",
    "port": 8002,
    "version": "1.1.0",
    "api_version": "v1"
    },
    {
    "service_name": "auth-service",
    "host": "localhost",
    "port": 8003,
    "version": "2.0.0",
    "api_version": "v2"
    },

    # User service versions
    {
    "service_name": "user-service",
    "host": "localhost",
    "port": 8101,
    "version": "1.0.0",
    "api_version": "v1",
    "dependencies": {
    "auth-service": "^1.0.0"  # Compatible with auth-service 1.x.x
    }
    },
    {
    "service_name": "user-service",
    "host": "localhost",
    "port": 8102,
    "version": "2.0.0",
    "api_version": "v2",
    "dependencies": {
    "auth-service": "^2.0.0"  # Compatible with auth-service 2.x.x
    }
    },

    # Product service versions
    {
    "service_name": "product-service",
    "host": "localhost",
    "port": 8201,
    "version": "1.0.0",
    "api_version": "v1",
    "features": ["basic-catalog"]
    },
    {
    "service_name": "product-service",
    "host": "localhost",
    "port": 8202,
    "version": "1.5.0",
    "api_version": "v1",
    "features": ["basic-catalog", "advanced-search"]
    },

    # API Gateway
    {
    "service_name": "api-gateway",
    "host": "localhost",
    "port": 8000,
    "version": "1.0.0",
    "api_version": "v1",
    "dependencies": {
    "auth-service": "^1.0.0",
    "user-service": "^1.0.0",
    "product-service": "^1.0.0"
    }
    }
    ]

    # Register services
    for service in services:
    dependencies = service.pop("dependencies", {})
    features = service.pop("features", [])

    instance = ServiceInstance(
    service_id=f"{service['service_name']}-{service['version']}",
    metadata={
    "dependencies": dependencies,
    "features": features,
    "api_version": service.pop("api_version")
    },
    **service
    )
    registry.register(instance)

    return registry


    @pytest.fixture
    def discovery_client(in_memory_registry):
    """Create a service discovery client."""
    client = ServiceDiscoveryClient(
    service_name="test-client",
    auto_register=False
    )
    client.registry = in_memory_registry
    return client


    @pytest.fixture
    def version_manager(discovery_client):
    """Create a version manager."""
    return VersionManager(discovery_client=discovery_client)


    @pytest.fixture
    def compatibility_checker(version_manager):
    """Create a version compatibility checker."""
    return VersionCompatibilityChecker(version_manager=version_manager)


    class TestServiceVersionCompatibility:

    def test_version_specific_discovery(self, discovery_client):
    """Test version-specific service discovery."""
    # Discover auth-service v1.0.0
    instances = discovery_client.discover_service("auth-service", version="1.0.0")
    assert len(instances) == 1
    assert instances[0].version == "1.0.0"

    # Discover auth-service v2.0.0
    instances = discovery_client.discover_service("auth-service", version="2.0.0")
    assert len(instances) == 1
    assert instances[0].version == "2.0.0"

    # Discover auth-service latest version
    instances = discovery_client.discover_service("auth-service", latest=True)
    assert len(instances) == 1
    assert instances[0].version == "2.0.0"  # Should be the highest version

    def test_version_prefix_discovery(self, discovery_client):
    """Test version prefix service discovery."""
    # Discover auth-service v1.x.x
    instances = discovery_client.discover_service("auth-service", version_prefix="1.")
    assert len(instances) == 2
    assert all(instance.version.startswith("1.") for instance in instances)

    # Discover auth-service v2.x.x
    instances = discovery_client.discover_service("auth-service", version_prefix="2.")
    assert len(instances) == 1
    assert instances[0].version == "2.0.0"

    def test_semantic_version_comparison(self, version_manager):
    """Test semantic version comparison."""
    # Compare versions
    assert version_manager.compare_versions("1.0.0", "1.1.0") < 0
    assert version_manager.compare_versions("1.1.0", "1.0.0") > 0
    assert version_manager.compare_versions("1.0.0", "1.0.0") == 0
    assert version_manager.compare_versions("1.0.0", "2.0.0") < 0
    assert version_manager.compare_versions("1.1.0", "1.1.0-alpha") > 0

    # Check version compatibility
    assert version_manager.is_compatible("1.0.0", "^1.0.0")
    assert version_manager.is_compatible("1.1.0", "^1.0.0")
    assert not version_manager.is_compatible("2.0.0", "^1.0.0")
    assert version_manager.is_compatible("1.0.0", "~1.0.0")
    assert not version_manager.is_compatible("1.1.0", "~1.0.0")
    assert version_manager.is_compatible("1.0.1", "~1.0.0")

    def test_service_dependency_compatibility(self, compatibility_checker):
    """Test service dependency compatibility."""
    # Check compatibility for API Gateway
    compatibility = compatibility_checker.check_service_compatibility("api-gateway", "1.0.0")
    assert compatibility["compatible"] is True
    assert len(compatibility["compatible_dependencies"]) == 3

    # Check compatibility for user-service v2.0.0 (requires auth-service v2.x.x)
    compatibility = compatibility_checker.check_service_compatibility("user-service", "2.0.0")
    assert compatibility["compatible"] is True
    assert len(compatibility["compatible_dependencies"]) == 1
    assert compatibility["compatible_dependencies"][0]["service_name"] == "auth-service"
    assert compatibility["compatible_dependencies"][0]["version"] == "2.0.0"

    def test_feature_based_version_selection(self, discovery_client):
    """Test feature-based version selection."""
    # Find product-service with advanced-search feature
    instances = discovery_client.discover_service("product-service")
    advanced_search_instances = [
    instance for instance in instances
    if "advanced-search" in instance.metadata.get("features", [])
    ]

    assert len(advanced_search_instances) == 1
    assert advanced_search_instances[0].version == "1.5.0"

    # Find product-service with only basic-catalog feature
    basic_catalog_only_instances = [
    instance for instance in instances
    if "basic-catalog" in instance.metadata.get("features", []) and
    "advanced-search" not in instance.metadata.get("features", [])
    ]

    assert len(basic_catalog_only_instances) == 1
    assert basic_catalog_only_instances[0].version == "1.0.0"

    def test_api_version_compatibility(self, compatibility_checker):
    """Test API version compatibility."""
    # Check API version compatibility
    api_compatibility = compatibility_checker.check_api_compatibility(
    "user-service", "1.0.0",
    "auth-service", "1.0.0"
    )
    assert api_compatibility["compatible"] is True
    assert api_compatibility["user_service_api_version"] == "v1"
    assert api_compatibility["auth_service_api_version"] == "v1"

    # Check API version incompatibility
    api_compatibility = compatibility_checker.check_api_compatibility(
    "user-service", "1.0.0",
    "auth-service", "2.0.0"
    )
    assert api_compatibility["compatible"] is False
    assert api_compatibility["user_service_api_version"] == "v1"
    assert api_compatibility["auth_service_api_version"] == "v2"

    def test_version_upgrade_path(self, version_manager):
    """Test version upgrade path."""
    # Get upgrade path for auth-service from 1.0.0 to 2.0.0
    upgrade_path = version_manager.get_upgrade_path("auth-service", "1.0.0", "2.0.0")
    assert len(upgrade_path) == 3
    assert upgrade_path[0] == "1.0.0"
    assert upgrade_path[1] == "1.1.0"
    assert upgrade_path[2] == "2.0.0"

    # Get upgrade path for product-service from 1.0.0 to 1.5.0
    upgrade_path = version_manager.get_upgrade_path("product-service", "1.0.0", "1.5.0")
    assert len(upgrade_path) == 2
    assert upgrade_path[0] == "1.0.0"
    assert upgrade_path[1] == "1.5.0"


    if __name__ == "__main__":
    pytest.main(["-v", "test_service_version_compatibility.py"])