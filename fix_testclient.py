#!/usr/bin/env python3
"""Script to fix TestClient initialization issues in test files."""

import os
import re

def fix_test_file(filepath):
    """Fix TestClient initialization in a test file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Remove module-level client initialization
    content = re.sub(
        r'client = TestClient\(app\) if app else None\n',
        '',
        content
    )
    
    # Add client = TestClient(app) at the beginning of each test method
    # Find all test methods that use client
    test_methods = re.findall(r'(def test_[^(]+\([^)]*\):.*?)(?=def|\Z)', content, re.DOTALL)
    
    for method in test_methods:
        if 'client.' in method and 'client = TestClient(app)' not in method:
            # Add client initialization after the method definition
            lines = method.split('\n')
            if len(lines) > 1:
                # Find the first non-comment, non-docstring line
                insert_index = 1
                for i, line in enumerate(lines[1:], 1):
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                        insert_index = i
                        break
                
                # Insert client initialization
                indent = len(lines[insert_index]) - len(lines[insert_index].lstrip())
                client_line = ' ' * indent + 'client = TestClient(app)'
                lines.insert(insert_index, client_line)
                
                new_method = '\n'.join(lines)
                content = content.replace(method, new_method)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"Fixed {filepath}")

def main():
    """Fix all test files with TestClient issues."""
    test_files = [
        'tests/api/test_token_management_api.py',
        'tests/api/test_tool_router.py', 
        'tests/api/test_user_api.py'
    ]
    
    for filepath in test_files:
        if os.path.exists(filepath):
            fix_test_file(filepath)
        else:
            print(f"File not found: {filepath}")

if __name__ == '__main__':
    main()
