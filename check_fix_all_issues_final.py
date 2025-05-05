#!/usr/bin/env python3
import sys

def check_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for syntax errors by compiling the file
            try:
                compile(content, file_path, 'exec')
                print(f"No syntax errors found in {file_path}")
            except SyntaxError as e:
                print(f"Syntax error in {file_path} at line {e.lineno}, column {e.offset}:")
                print(f"  {e.text.strip()}")
                print(f"  {' ' * (e.offset - 1)}^")
                print(f"  {e.msg}")
                return False
            
            return True
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "fix_all_issues_final.py"
    
    check_file(file_path)
