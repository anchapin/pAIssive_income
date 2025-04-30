"""
Test script to verify that the circular import issue is fixed.
"""

# Import just one module to verify imports work
from ai_models.model_manager import ModelManager

# Create an instance to verify the import works
model_manager = ModelManager()

# Print success message
print("Import successful!")
