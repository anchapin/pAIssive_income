"""
Script to fix Pydantic models to use V2 style.

This script updates Pydantic models to use the new V2 style with field_validator
instead of validator and adds model_config = ConfigDict(protected_namespaces=())
to all models to prevent namespace conflicts.
"""

import os
import re
import sys
from pathlib import Path


def fix_pydantic_model(file_path):
    """Fix Pydantic models in a file to use V2 style."""
    print(f"Processing {file_path}...")
    
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Check if the file contains Pydantic models
    if "from pydantic import" not in content and "import pydantic" not in content:
        print(f"  No Pydantic imports found in {file_path}, skipping")
        return False
    
    # Add ConfigDict import if not already present
    if "ConfigDict" not in content:
        if "from pydantic import " in content:
            content = re.sub(
                r"from pydantic import ([^\n]+)",
                r"from pydantic import \1, ConfigDict",
                content
            )
        else:
            content = re.sub(
                r"import pydantic",
                r"import pydantic\nfrom pydantic import ConfigDict",
                content
            )
    
    # Replace validator with field_validator
    if "validator" in content and "field_validator" not in content:
        content = content.replace("validator", "field_validator")
    
    # Add model_config to BaseModel classes
    model_config_pattern = r"class\s+(\w+)\s*\(\s*BaseModel\s*\):"
    model_config_replacement = r"class \1(BaseModel):\n    model_config = ConfigDict(protected_namespaces=())"
    content = re.sub(model_config_pattern, model_config_replacement, content)
    
    # Fix Field with extra keyword arguments
    field_pattern = r"Field\(([^)]*),\s*description\s*=\s*([^,)]+)([^)]*)\)"
    field_replacement = r"Field(\1, description=\2\3)"
    content = re.sub(field_pattern, field_replacement, content)
    
    # Write the updated content back to the file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    
    print(f"  Updated Pydantic models in {file_path}")
    return True


def process_directory(directory):
    """Process all Python files in a directory and its subdirectories."""
    updated_files = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if fix_pydantic_model(file_path):
                    updated_files += 1
    
    return updated_files


def main():
    """Main function."""
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "."
    
    print(f"Fixing Pydantic models in {directory}...")
    updated_files = process_directory(directory)
    print(f"Updated {updated_files} files")


if __name__ == "__main__":
    main()
