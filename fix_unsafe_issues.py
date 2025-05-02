#!/usr/bin/env python
"""
Script to fix unsafe issues in Python files using ruff.
"""

import os
import subprocess
import sys


def fix_file(file_path):
    """Fix a file using ruff with unsafe fixes."""
    print(f"\nFixing {file_path}...")
    
    # Fix issues with ruff using unsafe fixes
    try:
        subprocess.run(
            ["ruff", "check", "--fix", "--unsafe-fixes", file_path],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"✅ ruff fixes successful for {file_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ruff fixes failed for {file_path}")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        return False


def process_directory(directory, exclude_dirs=None):
    """Process all Python files in a directory and its subdirectories."""
    if exclude_dirs is None:
        exclude_dirs = [".venv", ".git", "__pycache__"]
    
    all_passed = True
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if not fix_file(file_path):
                    all_passed = False
    
    return all_passed


def main():
    """Main function to parse args and run the script."""
    directory = "."
    exclude_dirs = [".venv", ".git", "__pycache__"]
    
    success = process_directory(directory, exclude_dirs)
    
    if success:
        print("\n✅ All files fixed successfully!")
        return 0
    else:
        print("\n❌ Some files could not be fixed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
