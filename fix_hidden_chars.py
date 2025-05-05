#!/usr/bin/env python3
import sys

def fix_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        # Replace the colon and carriage return with just a carriage return
        content = content.replace(b'""":\r', b'"""\r')
        content = content.replace(b'print(f"Fixed {file_path} with {command[0]}"):', b'print(f"Fixed {file_path} with {command[0]}")')
        content = content.replace(b'--check", action="store_true", help="Check for issues without fixing":', b'--check", action="store_true", help="Check for issues without fixing"')
        content = content.replace(b'if not fix_file(:', b'if not fix_file(')

        with open(file_path, 'wb') as f:
            f.write(content)

        print(f"Fixed hidden characters in {file_path}")
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
