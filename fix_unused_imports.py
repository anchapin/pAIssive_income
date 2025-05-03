#!/usr/bin/env python
"""
Script to fix unused imports (F401) in Python files.

This script scans Python files in the project and removes unused imports
that are flagged by linters like flake8 or ruff with the F401 error code.

Usage:
    python fix_unused_imports.py [directory]
"""

import os
import re
import sys
from pathlib import Path


def find_python_files(directory):
    """Find all Python files in the given directory and its subdirectories."""
    return list(Path(directory).rglob("*.py"))


def fix_unused_imports_in_file(file_path):
    """Fix unused imports in a single file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Look for common patterns of unused imports
    # Pattern 1: from module import Class, UnusedClass
    pattern1 = r'from\s+[\w.]+\s+import\s+(?:[^,\s]+,\s*)*([^,\s]+)(?:\s*,\s*[^,\s]+)*\s*#\s*noqa:\s*F401'

    pattern2 = r'import\s+[\w.]+\s*#\s*noqa:\s*F401'


    

        matches.extend(re.finditer(pattern, content))
    
    # Sort matches in reverse order to avoid index issues when replacing
    matches = sorted(matches, key=lambda m: m.start(), reverse=True)
    
    # Replace or remove the unused imports
    modified_content = content
    for match in matches:
        line = match.group(0)
        # Remove the entire line if it's a standalone import
        if "#" in line and "F401" in line:
            start, end = match.span()
            # Find the start of the line
            line_start = modified_content.rfind("\n", 0, start) + 1
            if line_start == 0:  # If it's the first line
                line_start = 0
            # Find the end of the line
            line_end = modified_content.find("\n", end)
            if line_end == -1:  # If it's the last line
                line_end = len(modified_content)
            
            # Remove the line
            modified_content = modified_content[:line_start] + modified_content[line_end:]
    
    # Check if we need to write changes
    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return True
    
    return False


def fix_unused_imports(directory):
    """Fix unused imports in all Python files in the directory."""
    python_files = find_python_files(directory)
    fixed_files = []
    
    for file_path in python_files:
        try:
            if fix_unused_imports_in_file(file_path):
                fixed_files.append(str(file_path))
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return fixed_files


def main():
    """Main function to run the script."""
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    fixed_files = fix_unused_imports(directory)
    
    if fixed_files:
        print(f"Fixed unused imports in {len(fixed_files)} files:")
        for file in fixed_files:
            print(f"  - {file}")
    else:
        print("No unused imports found or fixed.")


if __name__ == "__main__":
    main()
