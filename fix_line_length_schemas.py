#!/usr/bin/env python
"""
Script to fix line length issues (E501) in schema and interface files.

This script specifically handles patterns common in schemas and interfaces:
- Long type hints and annotations
- Complex class inheritance chains
- Long default value assignments
- Long validator and field definitions

Usage:
    python fix_line_length_schemas.py [directory] [max_length]
"""

import os
import re
import sys
import ast
import tokenize
import subprocess
from textwrap import wrap
from io import StringIO

def is_schema_file(file_path):
    """Check if a file is a schema or interface file."""
    basename = os.path.basename(file_path).lower()
    path_parts = file_path.lower().split(os.sep)
    return (
        basename.endswith('.py') and
        any(x in basename for x in ['schema', 'interface', 'model', 'type']) or
        any(x in path_parts for x in ['schemas', 'interfaces', 'models', 'types'])
    )

def fix_type_hint(line, max_length):
    """Fix a long type hint by breaking it into multiple lines."""
    if ':' not in line or '=' not in line:
        return line
        
    try:
        # Split into name, type hint, and value parts
        name_type, value = line.split('=', 1)
        name, type_hint = name_type.split(':', 1)
        
        indent = len(line) - len(line.lstrip())
        name = name.strip()
        type_hint = type_hint.strip()
        value = value.strip()
        
        # If the line with proper spacing is still under max_length, keep it
        formatted = f"{' ' * indent}{name}: {type_hint} = {value}"
        if len(formatted) <= max_length:
            return formatted
            
        # Break into multiple lines with proper indentation
        result = f"{' ' * indent}{name}:\n"
        result += f"{' ' * (indent + 4)}{type_hint} =\n"
        result += f"{' ' * (indent + 4)}{value}"
        return result
    except Exception:
        return line

def fix_class_definition(line, max_length):
    """Fix a long class definition with multiple base classes."""
    if not line.strip().startswith('class ') or '(' not in line:
        return line
        
    try:
        # Split into class name and bases
        prefix = line[:line.find('(')]
        bases = line[line.find('(')+1:line.rfind(')')]
        suffix = line[line.rfind(')'):]
        
        indent = len(line) - len(line.lstrip())
        base_classes = [b.strip() for b in bases.split(',')]
        
        # If only one base class, try to keep it on one line
        if len(base_classes) == 1:
            formatted = f"{prefix}({base_classes[0]}){suffix}"
            if len(formatted) <= max_length:
                return formatted
        
        # Break into multiple lines
        result = prefix + '(\n'
        for base in base_classes[:-1]:
            result += ' ' * (indent + 4) + base + ',\n'
        if base_classes:
            result += ' ' * (indent + 4) + base_classes[-1] + '\n'
        result += ' ' * indent + ')' + suffix
        return result
    except Exception:
        return line

def fix_field_definition(line, max_length):
    """Fix a long field definition in a schema class."""
    if not any(x in line for x in ['Field(', 'Column(', 'field.']):
        return line
        
    try:
        # Split into field name and parameters
        prefix = line[:line.find('(')]
        params = line[line.find('(')+1:line.rfind(')')]
        suffix = line[line.rfind(')'):]
        
        indent = len(line) - len(line.lstrip())
        param_list = []
        current = []
        depth = 0
        
        # Parse parameters respecting nested structures
        for char in params:
            if char == ',' and depth == 0:
                param_list.append(''.join(current))
                current = []
            else:
                current.append(char)
                if char in '([{':
                    depth += 1
                elif char in ')]}':
                    depth -= 1
        if current:
            param_list.append(''.join(current))
            
        param_list = [p.strip() for p in param_list if p.strip()]
        
        # If it can fit on one line, keep it
        formatted = f"{prefix}({', '.join(param_list)}){suffix}"
        if len(formatted) <= max_length:
            return formatted
            
        # Break into multiple lines
        result = prefix + '(\n'
        for param in param_list[:-1]:
            result += ' ' * (indent + 4) + param + ',\n'
        if param_list:
            result += ' ' * (indent + 4) + param_list[-1] + '\n'
        result += ' ' * indent + ')' + suffix
        return result
    except Exception:
        return line

def fix_validator_definition(line, max_length):
    """Fix a long validator method definition."""
    if '@validator' not in line and 'def validate_' not in line:
        return line
        
    try:
        if '@validator' in line:
            # Handle validator decorator
            prefix = line[:line.find('(')]
            params = line[line.find('(')+1:line.rfind(')')]
            suffix = line[line.rfind(')'):]
            
            indent = len(line) - len(line.lstrip())
            param_list = [p.strip() for p in params.split(',') if p.strip()]
            
            # If it can fit on one line, keep it
            formatted = f"{prefix}({', '.join(param_list)}){suffix}"
            if len(formatted) <= max_length:
                return formatted
                
            # Break into multiple lines
            result = prefix + '(\n'
            for param in param_list[:-1]:
                result += ' ' * (indent + 4) + param + ',\n'
            if param_list:
                result += ' ' * (indent + 4) + param_list[-1] + '\n'
            result += ' ' * indent + ')' + suffix
            return result
            
        return line
    except Exception:
        return line

def fix_schema_line(line, max_length):
    """Fix a long line in a schema file."""
    if len(line) <= max_length:
        return line
        
    original_line = line
    
    # Try different schema-specific fixing strategies
    if ':' in line and '=' in line:
        line = fix_type_hint(line, max_length)
    
    if len(line.splitlines()[0]) > max_length and line.strip().startswith('class '):
        line = fix_class_definition(line, max_length)
    
    if len(
        line.splitlines()[0]) > max_length and any(x in line for x in ['Field(', 'Column(', 'field.']
    )):
        line = fix_field_definition(line, max_length)
    
    if len(
        line.splitlines()[0]) > max_length and ('@validator' in line or 'def validate_' in line
    )):
        line = fix_validator_definition(line, max_length)
    
    return line if line != original_line else original_line

def fix_schema_file(file_path, line_numbers, max_length=88):
    """Fix line length issues in a schema file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        modified = False
        for line_num in line_numbers:
            if 0 < line_num <= len(lines):
                original_line = lines[line_num - 1]
                if len(original_line.rstrip('\n')) > max_length:
                    modified_line = fix_schema_line(original_line.rstrip('\n'), max_length)
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

    # Get all schema files with line length issues
    result = subprocess.run(
        ["flake8", directory, "--select=E501"],
        capture_output=True,
        text=True,
        check=False
    )
    
    schema_files = {}
    for line in result.stdout.splitlines():
        match = re.match(r'(.+?):(\d+):\d+: E501', line)
        if match:
            file_path, line_num = match.groups()
            if is_schema_file(file_path):
                schema_files.setdefault(file_path, set()).add(int(line_num))
    
    if not schema_files:
        print("No schema files with line length issues found.")
        return

    # Fix each schema file
    fixed_files = []
    for file_path, line_numbers in schema_files.items():
        if fix_schema_file(file_path, sorted(line_numbers), max_length):
            fixed_files.append(file_path)

    if fixed_files:
        print(f"Fixed line length issues in {len(fixed_files)} schema files:")
        for file in sorted(fixed_files):
            print(f"  - {file}")
    else:
        print("No schema files were modified.")

if __name__ == "__main__":
    main()
