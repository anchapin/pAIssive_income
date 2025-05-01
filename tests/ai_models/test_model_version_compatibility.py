"""
Tests for AI model version compatibility.

These tests verify that the system can handle different model versions
and properly manage version compatibility.
"""

import unittest
from unittest.mock import MagicMock, patch
import json
import tempfile
import os

from ai_models.model_versioning import (
    ModelVersion, ModelVersionRegistry, VersionedModelManager, ModelMigrationTool
)
from ai_models.model_base_types import ModelInfo


class TestModelVersionCompatibility(unittest.TestCase):
    """Test suite for model version compatibility."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary file for the version registry
        self.temp_dir = tempfile.TemporaryDirectory()
        self.registry_path = os.path.join(self.temp_dir.name, "version_registry.json")

        # Create version registry
        self.version_registry = ModelVersionRegistry(self.registry_path)

        # Create migration tool
        self.migration_tool = ModelMigrationTool(self.version_registry)

        # Create versioned model manager
        self.model_manager = MagicMock()
        # Mock the models_dir parameter
        models_dir = self.temp_dir.name

        # Patch the VersionedModelManager to use our test registry and migration tool
        with patch('ai_models.model_versioning.ModelVersionRegistry') as mock_registry_class:
            with patch('ai_models.model_versioning.ModelMigrationTool') as mock_migration_tool_class:
                mock_registry_class.return_value = self.version_registry
                mock_migration_tool_class.return_value = self.migration_tool
                self.versioned_manager = VersionedModelManager(
                    model_manager=self.model_manager,
                    models_dir=models_dir
                )

        # Register test model versions
        self.v1_0_0 = ModelVersion(
            version="1.0.0",
            model_id="test-model",
            timestamp="2023-01-01T00:00:00",
            metadata={
                "description": "Initial release",
                "api_schema": {"input": {"text": "string"}, "output": {"text": "string"}}
            }
        )

        self.v1_1_0 = ModelVersion(
            version="1.1.0",
            model_id="test-model",
            timestamp="2023-02-01T00:00:00",
            metadata={
                "description": "Minor update",
                "api_schema": {"input": {"text": "string"}, "output": {"text": "string", "confidence": "float"}}
            }
        )

        self.v2_0_0 = ModelVersion(
            version="2.0.0",
            model_id="test-model",
            timestamp="2023-03-01T00:00:00",
            metadata={
                "description": "Major update",
                "api_schema": {"input": {"prompt": "string"}, "output": {"generated_text": "string", "confidence": "float"}}
            }
        )

        # Register versions
        self.version_registry.register_version(self.v1_0_0)
        self.version_registry.register_version(self.v1_1_0)
        self.version_registry.register_version(self.v2_0_0)

        # Create test model info
        self.model_info = ModelInfo(
            id="test-model",
            name="Test Model",
            description="A test model",
            type="huggingface",
            path="/path/to/model",
            capabilities=["text-generation"]
        )

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_backward_compatibility_with_older_versions(self):
        """Test backward compatibility with older model versions."""
        # Test compatibility between 1.1.0 and 1.0.0 (should be compatible)
        self.assertTrue(self.version_registry.check_compatibility(
            source_model_id="test-model",
            source_version="1.1.0",
            target_model_id="test-model",
            target_version="1.0.0"
        ))

        # Test compatibility between 2.0.0 and 1.0.0 (should not be compatible)
        self.assertFalse(self.version_registry.check_compatibility(
            source_model_id="test-model",
            source_version="2.0.0",
            target_model_id="test-model",
            target_version="1.0.0"
        ))

        # Get the existing version and modify it to add compatibility
        v2 = self.version_registry.get_version("test-model", "2.0.0")
        v2.is_compatible_with = ["1.0.0"]

        # Force update the registry
        self.version_registry.versions["test-model"]["2.0.0"] = v2
        self.version_registry._save_registry()

        # Now they should be compatible
        self.assertTrue(self.version_registry.check_compatibility(
            source_model_id="test-model",
            source_version="2.0.0",
            target_model_id="test-model",
            target_version="1.0.0"
        ))

    def test_handling_of_model_api_schema_changes(self):
        """Test handling of model API schema changes."""
        # Define migration functions for API schema changes
        def migrate_1_0_0_to_1_1_0(model_info, **kwargs):
            """Migrate from 1.0.0 to 1.1.0 by adding confidence field."""
            # In a real implementation, this would modify the model's behavior
            # For testing, we'll just return a modified copy
            new_info = ModelInfo(
                id=model_info.id,
                name=model_info.name,
                description=model_info.description + " (migrated to 1.1.0)",
                type=model_info.type,
                path=model_info.path,
                capabilities=model_info.capabilities
            )
            return new_info

        def migrate_1_1_0_to_2_0_0(model_info, **kwargs):
            """Migrate from 1.1.0 to 2.0.0 by changing input/output fields."""
            # In a real implementation, this would modify the model's behavior
            # For testing, we'll just return a modified copy
            new_info = ModelInfo(
                id=model_info.id,
                name=model_info.name,
                description=model_info.description + " (migrated to 2.0.0)",
                type=model_info.type,
                path=model_info.path,
                capabilities=model_info.capabilities
            )
            return new_info

        # Register migration functions
        self.migration_tool.register_migration_function(
            model_id="test-model",
            source_version="1.0.0",
            target_version="1.1.0",
            migration_fn=migrate_1_0_0_to_1_1_0
        )

        self.migration_tool.register_migration_function(
            model_id="test-model",
            source_version="1.1.0",
            target_version="2.0.0",
            migration_fn=migrate_1_1_0_to_2_0_0
        )

        # Test migration from 1.0.0 to 1.1.0
        migrated_info = self.migration_tool.migrate(
            model_info=self.model_info,
            source_version="1.0.0",
            target_version="1.1.0"
        )

        self.assertIn("(migrated to 1.1.0)", migrated_info.description)

        # Test migration from 1.0.0 to 2.0.0 (should use both migration functions)
        migrated_info = self.migration_tool.migrate(
            model_info=self.model_info,
            source_version="1.0.0",
            target_version="2.0.0"
        )

        self.assertIn("(migrated to 2.0.0)", migrated_info.description)

    def test_version_specific_feature_availability(self):
        """Test version-specific feature availability."""
        # Create versions with different feature sets
        v1_basic = ModelVersion(
            version="1.0.0",
            model_id="feature-model",
            features=["text-generation"]
        )

        v1_enhanced = ModelVersion(
            version="1.1.0",
            model_id="feature-model",
            features=["text-generation", "summarization"]
        )

        v2_advanced = ModelVersion(
            version="2.0.0",
            model_id="feature-model",
            features=["text-generation", "summarization", "translation"]
        )

        # Register versions
        self.version_registry.register_version(v1_basic)
        self.version_registry.register_version(v1_enhanced)
        self.version_registry.register_version(v2_advanced)

        # Mock the model manager to return different features based on version
        def get_model_with_version(model_id, version):
            if model_id == "feature-model":
                if version == "1.0.0":
                    return MagicMock(features=["text-generation"])
                elif version == "1.1.0":
                    return MagicMock(features=["text-generation", "summarization"])
                elif version == "2.0.0":
                    return MagicMock(features=["text-generation", "summarization", "translation"])
            return None

        self.model_manager.get_model_with_version.side_effect = get_model_with_version

        # Test feature availability in different versions
        model_v1_0 = self.model_manager.get_model_with_version("feature-model", "1.0.0")
        model_v1_1 = self.model_manager.get_model_with_version("feature-model", "1.1.0")
        model_v2_0 = self.model_manager.get_model_with_version("feature-model", "2.0.0")

        # Check features
        self.assertIn("text-generation", model_v1_0.features)
        self.assertNotIn("summarization", model_v1_0.features)

        self.assertIn("text-generation", model_v1_1.features)
        self.assertIn("summarization", model_v1_1.features)
        self.assertNotIn("translation", model_v1_1.features)

        self.assertIn("text-generation", model_v2_0.features)
        self.assertIn("summarization", model_v2_0.features)
        self.assertIn("translation", model_v2_0.features)


if __name__ == "__main__":
    unittest.main()
