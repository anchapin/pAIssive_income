"""
Script to update Pydantic models from class-based Config to model_config.
"""

import re
import sys


def update_pydantic_models(file_path):
    """
    Update Pydantic models in a file from class-based Config to model_config.
    
    Args:
        file_path: Path to the file to update
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add ConfigDict import if not already present
    if 'from pydantic import BaseModel' in content and 'ConfigDict' not in content:
        content = re.sub(
            r'from pydantic import (.*?)BaseModel(.*?)',
            r'from pydantic import \1BaseModel, ConfigDict\2',
            content
        )
    
    # Replace class Config with model_config
    pattern = (
        r'class Config:\s+"""Configuration for the model."""\s+'
        r'extra = "allow"  # Allow extra fields'
    )
    replacement = r'model_config = ConfigDict(extra="allow")  # Allow extra fields'
    content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated Pydantic models in {file_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_pydantic_models.py <file_path>")
        sys.exit(1)
    
    update_pydantic_models(sys.argv[1])
