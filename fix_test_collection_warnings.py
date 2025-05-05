"""fix_test_collection_warnings.py.

Script to fix test collection warnings for the pAIssive Income project.
"""

import os
import re


def find_test_files(root_dir="."):
    """Find all Python test files in the project."""
    test_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(os.path.join(root, file))
    return test_files


def fix_test_collection_warnings(file_path):
    """Fix common test collection warnings in the given file."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix 1: Add missing import pytest if needed
    if "import pytest" not in content and "from pytest" not in content:
        content = "import pytest\n" + content

    # Fix 2: Ensure test classes start with 'Test'
    class_pattern = re.compile(r"class\s+(?!Test)([A-Z][a-zA-Z0-9_]*)\s*\(.*\):")
    content = class_pattern.sub(r"class Test\1(\2):", content)

    # Fix 3: Ensure test functions start with 'test_'
    func_pattern = re.compile(
        r'def\s+(?!test_|_)([a-z][a-zA-Z0-9_]*)\s*\(.*\):\s*(?:"""|\'\'\').*(?:"""|\'\'\')?\s*assert'
    )
    content = func_pattern.sub(r"def test_\1(\2):", content)

    # Write the fixed content back
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return True


def main():
    """Find and fix test collection warnings in all test files."""
    print("Checking for test collection warnings...")

    test_files = find_test_files()
    if not test_files:
        print("No test files found.")
        return

    fixed_count = 0
    for file_path in test_files:
        try:
            if fix_test_collection_warnings(file_path):
                fixed_count += 1
                print(f"Fixed: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"Completed. Fixed {fixed_count} files with test collection warnings.")


if __name__ == "__main__":
    # Call main() directly to execute the script
    print("Checking for test collection warnings...")
    main()
