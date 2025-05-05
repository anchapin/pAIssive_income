#!/usr/bin/env python3
import re
import sys

def check_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for docstrings with trailing colons
        docstring_pattern = r'""".*?""":'
        matches = re.findall(docstring_pattern, content, re.DOTALL)
        
        if matches:
            print(f"Found docstrings with trailing colons in {file_path}:")
            for match in matches:
                print(f"  {match}")
            
            # Find the line numbers
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '"""' in line and line.rstrip().endswith(':'):
                    print(f"Line {i+1}: {line}")
            
            return False
        
        print(f"No docstrings with trailing colons found in {file_path}")
        return True
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        check_file(file_path)
    else:
        check_file('fix_all_issues_final.py')
