#!/usr/bin/env python3
import sys

def fix_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace the specific docstrings with colons
        content = content.replace('"""Check if a file should be ignored based on patterns.""":', '"""Check if a file should be ignored based on patterns."""')
        content = content.replace('"""Fix test classes with __init__ methods.""":', '"""Fix test classes with __init__ methods."""')
        content = content.replace('print(f"Fixed {file_path} with {command[0]}"):', 'print(f"Fixed {file_path} with {command[0]}")')
        content = content.replace('--check", action="store_true", help="Check for issues without fixing":', '--check", action="store_true", help="Check for issues without fixing"')
        content = content.replace('if not fix_file(:', 'if not fix_file(')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Fixed docstring colon in {file_path}")
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        fix_file(file_path)
    else:
        fix_file('fix_all_issues_final.py')
