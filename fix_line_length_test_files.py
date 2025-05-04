#!/usr/bin/env python
"""
Script to fix line length issues (E501) in test files.

This script specifically handles test files patterns including:
- Long assertions and test method docstrings
- Complex test method calls
- Test class and method organization
- Assertion chaining

Usage:
    python fix_line_length_test_files.py [directory] [max_length]
"""

import os
import re
import sys
import ast
import tokenize
import subprocess
from textwrap import wrap
from io import StringIO

def is_test_file(file_path):
    """Check if a file is a test file."""
    return (
        'test' in os.path.basename(file_path).lower() and
        file_path.endswith('.py')
    )

def fix_test_assertion(line, max_length):
    """Fix a long test assertion by breaking it into multiple lines."""
    if 'assert' not in line:
        return line
        
    try:
        # Handle assert statements with comparison operators
        operators = [' == ', ' != ', ' is ', ' is not ', ' in ', ' not in ', ' > ', ' < ', ' >= ', ' <= ']
        for op in operators:
            if op in line:
                parts = line.split(op)
                if len(parts) == 2:
                    indent = len(line) - len(line.lstrip())
                    result = ' ' * indent + 'assert ' + parts[0].strip() + '\\\n'
                    result += ' ' * (indent + 8) + op.strip() + ' ' + parts[1].strip()
                    return result
                    
        # Handle assert statements with function calls
        if '(' in line and ')' in line:
            prefix = line[:line.find('(')].rstrip()
            args_str = line[line.find('(')+1:line.rfind(')')]
            suffix = line[line.rfind(')'):]
            
            args = []
            current = []
            depth = 0
            
            # Parse arguments respecting nested structures
            for char in args_str:
                if char == ',' and depth == 0:
                    args.append(''.join(current))
                    current = []
                else:
                    current.append(char)
                    if char in '([{':
                        depth += 1
                    elif char in ')]}':
                        depth -= 1
            if current:
                args.append(''.join(current))
                
            indent = len(line) - len(line.lstrip())
            result = ' ' * indent + prefix + '(\n'
            for arg in args[:-1]:
                result += ' ' * (indent + 4) + arg.strip() + ',\n'
            if args:
                result += ' ' * (indent + 4) + args[-1].strip() + '\n'
            result += ' ' * indent + suffix
            return result
            
    except Exception:
        return line
    return line

def fix_test_method_docstring(line, max_length):
    """Fix a long test method docstring."""
    if '"""' not in line or not line.strip().startswith('"""'):
        return line
        
    indent = len(line) - len(line.lstrip())
    content = line.strip()[3:-3]  # Remove quotes
    
    # For simple one-line docstrings, try to keep them on one line
    if len(content) <= max_length - indent - 6:  # 6 for the quotes
        return line
        
    # For longer docstrings, wrap them
    result = ' ' * indent + '"""\n'
    wrapped = wrap(content, width=max_length-indent-4)
    for part in wrapped:
        result += ' ' * (indent + 4) + part + '\n'
    result += ' ' * indent + '"""'
    return result

def fix_test_method_call(line, max_length):
    """Fix a long test method call."""
    if '(' not in line or ')' not in line or 'assert' in line:
        return line
        
    try:
        prefix = line[:line.find('(')].rstrip()
        args_str = line[line.find('(')+1:line.rfind(')')]
        suffix = line[line.rfind(')'):]
        
        # For test method calls with parameters
        args = []
        current = []
        depth = 0
        
        for char in args_str:
            if char == ',' and depth == 0:
                args.append(''.join(current))
                current = []
            else:
                current.append(char)
                if char in '([{':
                    depth += 1
                elif char in ')]}':
                    depth -= 1
        if current:
            args.append(''.join(current))
            
        indent = len(line) - len(line.lstrip())
        if len(args) > 1 or len(line) > max_length:
            result = ' ' * indent + prefix + '(\n'
            for arg in args[:-1]:
                result += ' ' * (indent + 4) + arg.strip() + ',\n'
            if args:
                result += ' ' * (indent + 4) + args[-1].strip() + '\n'
            result += ' ' * indent + suffix
            return result
            
    except Exception:
        return line
    return line

def fix_assertion_chain(line, max_length):
    """Fix a long assertion chain."""
    if 'assert' not in line or '.' not in line:
        return line
        
    try:
        # Handle method chaining in assertions
        parts = line.split('.')
        if len(parts) > 1:
            indent = len(line) - len(line.lstrip())
            result = ' ' * indent + parts[0] + '\\\n'
            for part in parts[1:-1]:
                result += ' ' * (indent + 4) + '.' + part.strip() + '\\\n'
            result += ' ' * (indent + 4) + '.' + parts[-1].strip()
            return result
    except Exception:
        return line
    return line

def fix_test_line(line, max_length):
    """Fix a long line in a test file."""
    if len(line) <= max_length:
        return line
        
    original_line = line
    
    # Try different test-specific fixing strategies
    if 'assert' in line:
        line = fix_test_assertion(line, max_length)
    
    if len(line.splitlines()[0]) > max_length and '"""' in line:
        line = fix_test_method_docstring(line, max_length)
    
    if len(line.splitlines()[0]) > max_length and '(' in line:
        line = fix_test_method_call(line, max_length)
    
    if len(line.splitlines()[0]) > max_length and '.' in line:
        line = fix_assertion_chain(line, max_length)
    
    return line if line != original_line else original_line

def fix_test_file(file_path, line_numbers, max_length=88):
    """Fix line length issues in a test file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        modified = False
        for line_num in line_numbers:
            if 0 < line_num <= len(lines):
                original_line = lines[line_num - 1]
                if len(original_line.rstrip('\n')) > max_length:
                                        modified_line = fix_test_line(
                        original_line.rstrip('\n'),
                        max_length
                    )
                    if modified_line != original_line:
                        lines[line_num - 1] = modified_line + '\n'
                        modified = True

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    """Main function to run the script."""
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    max_length = int(sys.argv[2]) if len(sys.argv) > 2 else 88

    # Get all test files with line length issues
    result = subprocess.run(
        ["flake8", directory, "--select=E501"],
        capture_output=True,
        text=True,
        check=False
    )
    
    test_files = {}
    for line in result.stdout.splitlines():
        match = re.match(r'(.+?):(\d+):\d+: E501', line)
        if match:
            file_path, line_num = match.groups()
            if is_test_file(file_path):
                test_files.setdefault(file_path, set()).add(int(line_num))
    
    if not test_files:
        print("No test files with line length issues found.")
        return

    # Fix each test file
    fixed_files = []
    for file_path, line_numbers in test_files.items():
        if fix_test_file(file_path, sorted(line_numbers), max_length):
            fixed_files.append(file_path)

    if fixed_files:
        print(f"Fixed line length issues in {len(fixed_files)} test files:")
        for file in sorted(fixed_files):
            print(f"  - {file}")
    else:
        print("No test files were modified.")

if __name__ == "__main__":
    main()
