"""
fix_test_collection_warnings.py - Script to fix common issues that prevent test collection.

This script identifies and fixes common syntax errors that prevent pytest from collecting
tests, such as missing colons, incorrect indentation, and improper class definitions.
"""

import argparse
import fnmatch
import os
import re
import sys
from pathlib import Path


def should_ignore(file_path, ignore_patterns=None):
    """Check if a file should be ignored based on patterns."""
    if ignore_patterns is None:
        ignore_patterns = [
            ".venv/**",
            "venv/**",
            ".git/**",
            "__pycache__/**",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "build/**",
            "dist/**",
            "*.egg-info/**"
        ]

    # Convert to string for pattern matching
    file_path_str = str(file_path)

    # Check if file matches any ignore pattern
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(file_path_str, pattern):
            return True

    return False


def find_python_files(directory='.', specific_file=None, ignore_patterns=None):
    """Find Python files to check."""
    if specific_file:
        # If a specific file is provided, only check that file
        file_path = Path(specific_file)
        if file_path.exists() and file_path.suffix == '.py' and not should_ignore(file_path, ignore_patterns):
            return [file_path]
        else:
            print(f"File not found or not a Python file: {specific_file}")
            return []

    # Find all Python files in the directory
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                if not should_ignore(file_path, ignore_patterns):
                    python_files.append(file_path)

    return python_files


def fix_missing_colons(content):
    """Fix missing colons after class/function definitions and control statements."""
    # Fix missing colons after class definitions
    content = re.sub(r'(class\s+\w+(?:\([^)]*\))?)(\s*\n)', r'\1:\2', content)

    # Fix missing colons after function definitions
    content = re.sub(r'(def\s+\w+\([^)]*\))(\s*\n)', r'\1:\2', content)

    # Fix missing colons after control statements
    for keyword in ['if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with']:
        pattern = rf'({keyword}\s+[^:\n]+)(\s*\n)'
        content = re.sub(pattern, r'\1:\2', content)

    return content


def fix_class_definitions(content):
    """Fix common issues with class definitions."""
    # Fix class definitions split across multiple lines
    lines = content.split('\n')
    fixed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if line starts a class definition but doesn't end with a colon
        if re.match(r'^\s*class\s+\w+(?:\([^)]*)?$', line.strip()):
            # Collect lines until we find a line with a colon or closing parenthesis
            class_def = line
            j = i + 1

            while j < len(lines) and not re.search(r'[:,]', lines[j]):
                class_def += ' ' + lines[j].strip()
                j += 1

            # If we found a line with a colon or comma, add it
            if j < len(lines):
                class_def += ' ' + lines[j].strip()
                j += 1

            # Add the fixed class definition
            if not class_def.strip().endswith(':'):
                class_def += ':'

            fixed_lines.append(class_def)
            i = j
        else:
            fixed_lines.append(line)
            i += 1

    return '\n'.join(fixed_lines)


def fix_test_class_init(content):
    """Fix test classes with __init__ methods that prevent collection."""
    # Find test classes with __init__ methods
    test_class_pattern = r'(class\s+Test\w+\(?.*\)?:.*?)(?=\n\s*class|\n\s*def|\Z)'
    init_method_pattern = r'(\s+def\s+__init__\s*\([^)]*\):.*?)(?=\n\s+def|\n\s*class|\Z)'

    # Function to process each test class match
    def process_test_class(match):
        test_class = match.group(1)

        # Check if the class has an __init__ method
        init_match = re.search(init_method_pattern, test_class, re.DOTALL)
        if init_match:
            # Replace __init__ with setup_method
            init_method = init_match.group(1)
            setup_method = init_method.replace('__init__', 'setup_method')

            # Replace self parameter with self, method=None if not already present
            if 'method' not in setup_method:
                setup_method = re.sub(r'(\s+def\s+setup_method\s*\()([^)]*?)(\):)',
                                     lambda m: m.group(1) + m.group(2) + ', method=None' + m.group(3),
                                     setup_method)

            # Replace the __init__ method with setup_method
            test_class = test_class.replace(init_method, setup_method)

        return test_class

    # Replace test classes with fixed versions
    content = re.sub(test_class_pattern, process_test_class, content, flags=re.DOTALL)

    return content


def fix_file(file_path, check_only=False):
    """Fix common issues in a file that prevent test collection."""
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Apply fixes
        original_content = content

        # Fix missing colons
        content = fix_missing_colons(content)

        # Fix class definitions
        content = fix_class_definitions(content)

        # Fix test classes with __init__ methods
        content = fix_test_class_init(content)

        # Check if the content was modified
        if content != original_content:
            if check_only:
                print(f"Syntax issues found in: {file_path}")
                return False
            else:
                # Write the fixed content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"Fixed: {file_path}")
                return True

        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to parse arguments and fix test collection warnings."""
    parser = argparse.ArgumentParser(
        description="Fix common issues that prevent pytest from collecting tests"
    )

    parser.add_argument("path", nargs="?", default=".",
                       help="Path to file or directory to check/fix")
    parser.add_argument("--check", action="store_true",
                       help="Check for issues without fixing")

    args = parser.parse_args()

    # Find Python files to check/fix
    python_files = find_python_files(args.path)

    if not python_files:
        print("No Python files found to check.")
        return 0

    print(f"Checking {len(python_files)} Python files...")

    # Check/fix the files
    issues_found = False
    for file_path in python_files:
        if not fix_file(file_path, check_only=args.check):
            issues_found = True

    if args.check and issues_found:
        print("Syntax issues found. Run without --check to fix.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
