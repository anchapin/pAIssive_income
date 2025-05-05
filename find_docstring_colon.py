#!/usr/bin/env python3
import os
import re

def check_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for docstrings ending with a colon
            pattern = r'""".*?"""\s*:'
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                print(f"Found docstring with colon in {file_path}:")
                for match in matches:
                    print(f"  {match}")
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
                # Skip files in .venv directory
                if '.venv' not in file_path:
                    python_files.append(file_path)
    
    # Check each file for docstrings with colons
    found = False
    for file_path in python_files:
        if check_file(file_path):
            found = True
    
    if not found:
        print("No docstrings with colons found.")

if __name__ == "__main__":
    main()
