#!/usr/bin/env python3
import os
import re
import sys

def check_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Skip files that are searching for patterns
            if 'find_docstring_colon' in file_path:
                return False

            # Look for docstrings followed by a colon
            pattern = r'""".*?"""\s*:'
            matches = re.findall(pattern, content, re.DOTALL)

            if matches:
                print(f"Found docstring with colon in {file_path}:")
                for match in matches:
                    print(f"  {match}")
                return True

            # Also look for single-quoted docstrings
            pattern = r"'''.*?'''\s*:"
            matches = re.findall(pattern, content, re.DOTALL)

            if matches:
                print(f"Found docstring with colon in {file_path}:")
                for match in matches:
                    print(f"  {match}")
                return True

            # Look for any line ending with a docstring and a colon
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if re.search(r'""".*?"""\s*:', line) or re.search(r"'''.*?'''\s*:", line):
                    print(f"Found docstring with colon in {file_path} at line {i+1}:")
                    print(f"  {line}")
                    return True

            return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def main():
    # Get all Python files in the current directory and subdirectories
    python_files = []
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                # Skip files in .venv directory and scripts that search for patterns
                if '.venv' not in file_path and 'find_' not in file_path:
                    python_files.append(file_path)

    # Check each file for docstrings with colons
    found = False
    for file_path in python_files:
        if check_file(file_path):
            found = True

    if not found:
        print("No docstrings with colons found.")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
