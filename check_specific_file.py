#!/usr/bin/env python3
import re

def check_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
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
                
        print(f"No docstrings with colons found in {file_path}")
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

if __name__ == "__main__":
    check_file('fix_all_issues_final.py')
