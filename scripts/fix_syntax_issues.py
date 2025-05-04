#!/usr/bin/env python
"""
Script to automatically fix common syntax issues in Python files.

This script:
1. Finds all Python files in the project
2. Excludes files and directories specified in .gitignore
3. Fixes common syntax issues like duplicate lines, indentation problems, and duplicate exception blocks
"""

import os
import re
import sys
import fnmatch
from pathlib import Path
import ast
import tokenize
import io

def parse_gitignore(gitignore_path):
    """Parse .gitignore file and return patterns to exclude."""
    if not os.path.exists(gitignore_path):
        return []
    
    with open(gitignore_path, 'r') as f:
        lines = f.readlines()
    
    patterns = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Convert .gitignore pattern to fnmatch pattern
            if line.startswith('/'):
                line = line[1:]  # Remove leading slash
            if line.endswith('/'):
                line = f"{line}*"  # Add wildcard for directories
            patterns.append(line)
    
    return patterns

def is_excluded(file_path, exclude_patterns):
    """Check if a file should be excluded based on .gitignore patterns."""
    # Convert to relative path from project root
    rel_path = os.path.relpath(file_path)
    
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(rel_path, pattern) or any(fnmatch.fnmatch(part, pattern) for part in rel_path.split(os.sep)):
            return True
    
    return False

def find_python_files(root_dir, exclude_patterns):
    """Find all Python files in the project, excluding those matching .gitignore patterns."""
    python_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not is_excluded(os.path.join(root, d), exclude_patterns)]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if not is_excluded(file_path, exclude_patterns):
                    python_files.append(file_path)
    
    return python_files

def remove_duplicate_lines(content):
    """Remove consecutive duplicate lines."""
    lines = content.split('\n')
    result_lines = []
    
    i = 0
    while i < len(lines):
        result_lines.append(lines[i])
        
        # Skip consecutive duplicate lines
        j = i + 1
        while j < len(lines) and lines[j] == lines[i]:
            j += 1
        
        i = j
    
    return '\n'.join(result_lines)

def fix_duplicate_except_blocks(content):
    """Fix duplicate except blocks."""
    # This is a simplified approach - for complex cases, we'd need a proper parser
    pattern = r'except\s+([A-Za-z0-9_]+)(\s+as\s+[A-Za-z0-9_]+)?:\s*\n\s*except\s+'
    return re.sub(pattern, r'except ', content)

def fix_indentation(content):
    """Fix indentation issues."""
    lines = content.split('\n')
    result_lines = []
    
    # Track indentation level
    indent_level = 0
    for line in lines:
        stripped = line.lstrip()
        
        # Skip empty lines
        if not stripped:
            result_lines.append('')
            continue
        
        # Adjust indentation for control structures
        if stripped.startswith(('def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except ', 'finally:')):
            # Ensure proper indentation for these blocks
            spaces = ' ' * (4 * indent_level)
            result_lines.append(f"{spaces}{stripped}")
            
            # Increase indent level for blocks that start a new scope
            if not stripped.startswith(('elif ', 'else:')):
                indent_level += 1
        elif stripped.startswith(('return ', 'break', 'continue', 'pass', 'raise')):
            # These should be indented at the current level
            spaces = ' ' * (4 * indent_level)
            result_lines.append(f"{spaces}{stripped}")
        else:
            # Regular lines
            spaces = ' ' * (4 * indent_level)
            result_lines.append(f"{spaces}{stripped}")
    
    return '\n'.join(result_lines)

def is_valid_python(content):
    """Check if the content is valid Python code."""
    try:
        ast.parse(content)
        return True
    except SyntaxError:
        return False

def fix_file(file_path):
    """Apply fixes to a Python file."""
    print(f"Processing {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply fixes
        original_content = content
        
        # Step 1: Remove duplicate lines
        content = remove_duplicate_lines(content)
        
        # Step 2: Fix duplicate except blocks
        content = fix_duplicate_except_blocks(content)
        
        # Step 3: Fix indentation (simplified approach)
        # Note: This is a basic approach and might not work for all cases
        # content = fix_indentation(content)
        
        # Only save if changes were made and the result is valid Python
        if content != original_content:
            # Verify the fixed content is valid Python
            if is_valid_python(content):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  Fixed issues in {file_path}")
                return True
            else:
                print(f"  Warning: Fixes would create invalid Python in {file_path}, skipping")
        else:
            print(f"  No issues found in {file_path}")
        
        return False
    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return False

def main():
    """Main function to find and fix Python files."""
    # Get project root directory
    root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    if not os.path.isdir(root_dir):
        root_dir = os.getcwd()
    
    # Parse .gitignore
    gitignore_path = os.path.join(root_dir, '.gitignore')
    exclude_patterns = parse_gitignore(gitignore_path)
    
    # Add common patterns to exclude
    exclude_patterns.extend(['*.pyc', '__pycache__/*', '.git/*', '.venv/*', 'venv/*'])
    
    # Find Python files
    python_files = find_python_files(root_dir, exclude_patterns)
    print(f"Found {len(python_files)} Python files to process")
    
    # Fix files
    fixed_count = 0
    for file_path in python_files:
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"\nFixed issues in {fixed_count} files")

if __name__ == "__main__":
    main()
