#!/usr/bin/env python3
import os
import sys
import py_compile

def check_file(file_path):
    try:
        py_compile.compile(file_path, doraise=True)
        return True
    except py_compile.PyCompileError as e:
        print(f"Syntax error in {file_path}:")
        print(f"  {e}")
        return False
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return False

def find_python_files(directory="."):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # Skip virtual environment files
                if ".venv" not in file_path and "venv" not in file_path:
                    python_files.append(file_path)
    return python_files

def main():
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "."
    
    python_files = find_python_files(directory)
    print(f"Checking {len(python_files)} Python files for syntax errors...")
    
    found_issues = False
    for file_path in python_files:
        if not check_file(file_path):
            found_issues = True
    
    if not found_issues:
        print("No syntax errors found.")
    
    return 0 if not found_issues else 1

if __name__ == "__main__":
    sys.exit(main())
