#!/usr/bin/env python3
import ast
import os
import sys

def check_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            ast.parse(content)
            return True
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return False

def main():
    # Get all Python files in the current directory and subdirectories
    python_files = []
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                # Skip files in .venv directory
                if '.venv' not in file_path:
                    python_files.append(file_path)
    
    # Check each file for syntax errors
    all_ok = True
    for file_path in python_files:
        if not check_file(file_path):
            all_ok = False
    
    if all_ok:
        print("All files parsed successfully!")
        return 0
    else:
        print("Some files have syntax errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
