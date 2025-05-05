#!/usr/bin/env python3
import os
import re
import sys

def check_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
            for i, line in enumerate(content):
                # Look for docstrings followed by a colon
                if '"""' in line and ':' in line and line.rstrip().endswith(':'):
                    print(f"Found potential issue in {file_path} at line {i+1}:")
                    print(f"  {line.strip()}")
                    return True
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def find_python_files(directory="."):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # Skip virtual environment files and this script
                if ".venv" not in file_path and "venv" not in file_path and "find_all_docstring_colons.py" not in file_path:
                    python_files.append(file_path)
    return python_files

def main():
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "."
    
    python_files = find_python_files(directory)
    print(f"Checking {len(python_files)} Python files...")
    
    found_issues = False
    for file_path in python_files:
        if check_file(file_path):
            found_issues = True
    
    if not found_issues:
        print("No issues found.")
    
    return 0 if not found_issues else 1

if __name__ == "__main__":
    sys.exit(main())
