"""
Tests for the model versioning system.

These tests cover version compatibility checks, version upgrade / downgrade logic,
and conflict resolution in the model versioning system.
"""

import pytest

from ai_models.model_base_types import ModelInfo
    ModelMigrationTool,
    ModelVersion,
    ModelVersionRegistry,
    VersionedModelManager,
)

@pytest.fixture
def model_info():
    """Fixture providing a basic ModelInfo instance."""
    return ModelInfo(
        id="test - model",
        name="Test Model",
        description="A test model",
        type="huggingface",
        path=" / path / to / model",
        capabilities=["text - generation"],
    )

@pytest.fixture
def version_registry(tmp_path):
    """Fixture providing a ModelVersionRegistry instance."""
    registry_path = tmp_path / "version_registry.json"
    return ModelVersionRegistry(str(registry_path))

@pytest.fixture
def migration_tool(version_registry):
    """Fixture providing a ModelMigrationTool instance."""
    return ModelMigrationTool(version_registry)

def test_version_compatibility_same_major():
    """Test compatibility between versions with the same major version."""
    v1 = ModelVersion(version="1.0.0", model_id="test - model")
    v2 = ModelVersion(version="1.1.0", model_id="test - model")

    # Versions with same major version should be compatible
    assert v1.is_compatible_with_version(v2)
    assert v2.is_compatible_with_version(v1)

def test_version_compatibility_different_major():
    """Test compatibility between versions with different major versions."""
    v1 = ModelVersion(version="1.0.0", model_id="test - model")
    v2 = ModelVersion(version="2.0.0", model_id="test - model")

    # Versions with different major versions should not be compatible
    assert not v1.is_compatible_with_version(v2)
    assert not v2.is_compatible_with_version(v1)

def test_version_compatibility_explicit():
    """Test explicit version compatibility declarations."""
    v1 = ModelVersion(version="1.0.0", model_id="test - model", 
        is_compatible_with=["2.0.0"])
    v2 = ModelVersion(version="2.0.0", model_id="test - model")

    # v1 should be compatible with v2 due to explicit declaration
    assert v1.is_compatible_with_version(v2)
    # v2 has no explicit compatibility, so should follow semver rules
    assert not v2.is_compatible_with_version(v1)

def test_registry_compatibility_check(version_registry, model_info):
    """Test compatibility checking through the registry."""
    # Create and register two versions
    v1 = ModelVersion(version="1.0.0", model_id=model_info.id, 
        is_compatible_with=["2.0.0"])
    v2 = ModelVersion(version="2.0.0", model_id=model_info.id)

    version_registry.register_version(v1)
    version_registry.register_version(v2)

    # Check compatibility through registry
    assert version_registry.check_compatibility(
        source_model_id=model_info.id,
        source_version="1.0.0",
        target_model_id=model_info.id,
        target_version="2.0.0",
    )

def test_cross_model_compatibility(version_registry):
    """Test compatibility between different models."""
    # Create versions for two different models
    v1 = ModelVersion(
        version="1.0.0",
        model_id="model1",
        is_compatible_with=["model2:1.0.0"],  # Explicit cross - model compatibility
    )
    v2 = ModelVersion(version="1.0.0", model_id="model2")

    version_registry.register_version(v1)
    version_registry.register_version(v2)

    # Check cross - model compatibility
    # By default, different models are not compatible unless explicitly specified
    assert not version_registry.check_compatibility(
        source_model_id="model1",
        source_version="1.0.0",
        target_model_id="model2",
        target_version="1.0.0",
    )

def test_invalid_version_string():
    """Test handling of invalid version strings."""
    with pytest.raises(ValueError, match="Invalid version string"):
        ModelVersion(version="invalid", model_id="test - model")

def test_version_upgrade_path(migration_tool, model_info):
    """Test finding an upgrade path between versions."""
    # Register migration functions for upgrade path
    migration_tool.register_migration_function(
        model_id=model_info.id,
        source_version="1.0.0",
        target_version="1.1.0",
        migration_fn=lambda model, **kwargs: model,
    )
    migration_tool.register_migration_function(
        model_id=model_info.id,
        source_version="1.1.0",
        target_version="2.0.0",
        migration_fn=lambda model, **kwargs: model,
    )

    # Check if migration is possible
    assert migration_tool.can_migrate(model_info.id, "1.0.0", "2.0.0")

def test_version_downgrade_path(migration_tool, model_info):
    """Test finding a downgrade path between versions."""
    # Register migration functions for downgrade path
    migration_tool.register_migration_function(
        model_id=model_info.id,
        source_version="2.0.0",
        target_version="1.1.0",
        migration_fn=lambda model, **kwargs: model,
    )
    migration_tool.register_migration_function(
        model_id=model_info.id,
        source_version="1.1.0",
        target_version="1.0.0",
        migration_fn=lambda model, **kwargs: model,
    )

    # Check if migration is possible
    assert migration_tool.can_migrate(model_info.id, "2.0.0", "1.0.0")

def test_version_migration_execution(migration_tool, model_info):
    """Test actual execution of version migration."""

    def upgrade_to_v11(model, **kwargs):
        model.capabilities.append("embedding")
        return model

    def upgrade_to_v20(model, **kwargs):
        model.capabilities.append("classification")
        return model

    # Register migration functions
    migration_tool.register_migration_function(
        model_id=model_info.id,
        source_version="1.0.0",
        target_version="1.1.0",
        migration_fn=upgrade_to_v11,
    )
    migration_tool.register_migration_function(
        model_id=model_info.id,
        source_version="1.1.0",
        target_version="2.0.0",
        migration_fn=upgrade_to_v20,
    )

    # Perform migration
    migrated_model = migration_tool.migrate(model_info, "1.0.0", "2.0.0")

    # Check that capabilities were added in order
    assert "embedding" in migrated_model.capabilities
    assert "classification" in migrated_model.capabilities
    assert len(migrated_model.capabilities) == 3  # original + 2 new

def test_invalid_migration_path(migration_tool, model_info):
    """Test handling of invalid migration paths."""
    # No migration functions registered
    with pytest.raises(ValueError, match="No migration path found"):
        migration_tool.migrate(model_info, "1.0.0", "2.0.0")

def test_direct_vs_indirect_migration(migration_tool, model_info):
    """Test direct migration vs indirect migration through intermediate versions."""

    def direct_migration(model, **kwargs):
        model.capabilities.append("direct")
        return model

    def indirect_step1(model, **kwargs):
        model.capabilities.append("step1")
        return model

    def indirect_step2(model, **kwargs):
        model.capabilities.append("step2")
        return model

    # Register both direct and indirect paths
    migration_tool.register_migration_function(
        model_id=model_info.id,
        source_version="1.0.0",
        target_version="2.0.0",
        migration_fn=direct_migration,
    )
    migration_tool.register_migration_function(
        model_id=model_info.id,
        source_version="1.0.0",
        target_version="1.5.0",
        migration_fn=indirect_step1,
    )
    migration_tool.register_migration_function(
        model_id=model_info.id,
        source_version="1.5.0",
        target_version="2.0.0",
        migration_fn=indirect_step2,
    )

    # Direct migration should be preferred
    migrated_model = migration_tool.migrate(model_info, "1.0.0", "2.0.0")
    assert "direct" in migrated_model.capabilities
    assert "step1" not in migrated_model.capabilities
    assert "step2" not in migrated_model.capabilities

def test_version_conflict_resolution(version_registry, model_info):
    """Test handling of conflicting version changes."""
    # Create conflicting versions with different hashes
    v1 = ModelVersion(
        version="1.0.0", model_id=model_info.id, hash_value="abc123", 
            features=["text - generation"]
    )
    v2 = ModelVersion(
        version="1.0.0",
        model_id=model_info.id,
        hash_value="def456",
        features=["text - generation", "embedding"],
    )

    # First registration should succeed
    version_registry.register_version(v1)

    # Second registration of same version should raise error
    with pytest.raises(ValueError, match="Version 1.0.0 already exists"):
        version_registry.register_version(v2)

def test_version_hash_verification(version_registry, tmp_path):
    """Test verification of version hashes."""
    # Create a test file with known content
    model_path = tmp_path / "model.bin"
    model_path.write_text("test model content")

    # Create ModelInfo with the test file path
    model_info = ModelInfo(
        id="test - model",
        name="Test Model",
        description="A test model",
        type="huggingface",
        path=str(model_path),
        capabilities=["text - generation"],
    )

    # Create version with hash
    version = version_registry.create_version_from_model(model_info=model_info, 
        version_str="1.0.0")

    # Verify the hash was calculated and stored
    assert version.hash_value != ""

    # Modify the file
    model_path.write_text("modified model content")

    # Calculate new hash
    new_hash = version_registry._calculate_file_hash(str(model_path))

    # Verify hash has changed
    assert new_hash != version.hash_value

def test_concurrent_version_updates(version_registry, model_info):
    """Test handling of concurrent version updates."""
    base_version = ModelVersion(version="1.0.0", model_id=model_info.id, 
        features=["base - feature"])
    version_registry.register_version(base_version)

    # Simulate two concurrent updates
    update1 = ModelVersion(
        version="1.1.0", model_id=model_info.id, features=["base - feature", 
            "feature - a"]
    )
    update2 = ModelVersion(
        version="1.1.0", model_id=model_info.id, features=["base - feature", 
            "feature - b"]
    )

    # First update should succeed
    version_registry.register_version(update1)

    # Second update should fail
    with pytest.raises(ValueError):
        version_registry.register_version(update2)

    # Verify the first update was preserved
    registered = version_registry.get_version(model_info.id, "1.1.0")
    assert "feature - a" in registered.features
    assert "feature - b" not in registered.features

def test_version_metadata_conflict(version_registry, model_info):
    """Test handling of conflicts in version metadata."""
    version1 = ModelVersion(
        version="1.0.0", model_id=model_info.id, 
            metadata={"performance": {"accuracy": 0.95}}
    )
    version2 = ModelVersion(
        version="1.0.0", model_id=model_info.id, 
            metadata={"performance": {"accuracy": 0.90}}
    )

    # Register first version
    version_registry.register_version(version1)

    # Attempt to register conflicting version
    with pytest.raises(ValueError):
        version_registry.register_version(version2)

    # Verify original metadata is preserved
    stored = version_registry.get_version(model_info.id, "1.0.0")
    assert stored.metadata["performance"]["accuracy"] == 0.95
