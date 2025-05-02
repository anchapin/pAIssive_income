#!/usr/bin/env python
"""
Script to fix test collection warnings for classes with __init__ constructors.
This script addresses the pytest collection warnings for test classes.
"""

import argparse
import ast
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple


def get_test_files(directory: str, exclude_patterns: Optional[List[str]] = None) -> List[Path]:
    """Get all test files in a directory and its subdirectories."""
    if exclude_patterns is None:
        exclude_patterns = []
    
    test_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                file_path = Path(os.path.join(root, file))
                
                # Check if file should be excluded
                if any(re.search(pattern, str(file_path)) for pattern in exclude_patterns):
                    continue
                
                test_files.append(file_path)
    
    return test_files


def has_test_class_with_init(file_content: str) -> bool:
    """Check if a file contains test classes with __init__ methods."""
    # Look for class definitions that start with "Test" and have an __init__ method
    pattern = r"class\s+Test\w*\s*\([^)]*\):\s*(?:.*\n)+?\s+def\s+__init__\s*\("
    return bool(re.search(pattern, file_content))


def fix_test_class_init(file_path: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """Fix test classes with __init__ methods to use setup_method instead."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if not has_test_class_with_init(content):
        return False, "No test classes with __init__ methods found"
    
    # Parse the Python file
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    
    # Track changes
    changes_made = False
    updated_content = content
    
    # Find all class definitions
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            # Look for __init__ method within the class
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    # Found an __init__ method, need to replace it with setup_method
                    init_start = item.lineno
                    init_end = item.end_lineno if hasattr(item, "end_lineno") else item.lineno
                    
                    # Extract the content of the __init__ method
                    init_lines = content.splitlines()[init_start-1:init_end]
                    init_content = "\n".join(init_lines)
                    
                    # Create the setup_method function
                    setup_method_content = init_content.replace("def __init__(self", "def setup_method(self")
                    
                    # Replace the __init__ method with setup_method
                    updated_content = updated_content.replace(init_content, setup_method_content)
                    changes_made = True
    
    if changes_made and not dry_run:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
    
    return changes_made, "Replaced __init__ methods with setup_method in test classes"


def main():
    """Main function to parse args and run the script."""
    parser = argparse.ArgumentParser(description="Fix test collection warnings for classes with __init__ constructors.")
    parser.add_argument(
        "path",
        nargs="?",
        default="tests",
        help="Path to a file or directory to process (default: tests directory)",
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=[],
        help="Patterns to exclude from processing",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually modify files, just show what would be changed",
    )

    args = parser.parse_args()

    path = Path(args.path)
    if path.is_file():
        # Process a single file
        changed, message = fix_test_class_init(path, args.dry_run)
        if changed:
            print(f"✅ Updated {path}: {message}")
        else:
            print(f"ℹ️ Skipped {path}: {message}")
    else:
        # Process a directory
        files = get_test_files(args.path, args.exclude)
        updated_count = 0
        
        for file_path in files:
            changed, message = fix_test_class_init(file_path, args.dry_run)
            if changed:
                print(f"✅ Updated {file_path}: {message}")
                updated_count += 1
            else:
                print(f"ℹ️ Skipped {file_path}: {message}")
        
        print(f"\nProcessed {len(files)} files, updated {updated_count} files.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
