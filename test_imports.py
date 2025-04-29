"""
Test script to verify that the circular import issue is fixed.
"""

# Import the modules directly
from ai_models.model_base_types import ModelInfo
from ai_models.model_versioning import VersionedModelManager, ModelVersion
from ai_models.model_manager import ModelManager

# Print success message
print("Import successful!")
