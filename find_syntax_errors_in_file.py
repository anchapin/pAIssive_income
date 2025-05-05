#!/usr/bin/env python3
import ast
import os
import sys

def check_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Try to parse the file with ast
        try:
            ast.parse(content)
            return True
        except SyntaxError as e:
            print(f"Syntax error in {file_path} at line {e.lineno}, column {e.offset}: {e.msg}")
            
            # Print the line with the error
            lines = content.split('\n')
            if e.lineno <= len(lines):
                print(f"Line {e.lineno}: {lines[e.lineno - 1]}")
                if e.offset:
                    print(f"{' ' * (e.offset + 7)}^")
            
            return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python find_syntax_errors_in_file.py <file_path>")
        return 1
        
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return 1
        
    if not file_path.endswith('.py'):
        print(f"Not a Python file: {file_path}")
        return 1
        
    if check_file(file_path):
        print(f"No syntax errors found in {file_path}")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
