#!/usr / bin / env python
"""
Script to fix line length issues (E501) in Python files.

This script scans Python files in the project and attempts to fix lines
that exceed the maximum line length (typically 88 or 79 characters).

Usage:
    python fix_line_length.py [directory] [--max - length=88]
"""

import argparse
import os
import re
import sys
from pathlib import Path


def find_python_files(directory):
    """Find all Python files in the given directory and its subdirectories."""
    return list(Path(directory).rglob("*.py"))


def fix_line_length_in_file(file_path, max_length=88):
    """Fix line length issues in a single file."""
    with open(file_path, "r", encoding="utf - 8") as f:
        lines = f.readlines()

    modified = False
    modified_lines = []

    for line in lines:
        # Skip comments and docstrings that exceed max length
        if line.strip().startswith("#") or '"""' in line or "'''" in line:
            modified_lines.append(line)
            continue

        # If line exceeds max length, try to fix it
        if len(line.rstrip()) > max_length:
            # Try to break at logical points
            fixed_line = fix_long_line(line, max_length)
            modified_lines.append(fixed_line)
            if fixed_line != line:
                modified = True
        else:
            modified_lines.append(line)

    # Write changes if needed
    if modified:
        with open(file_path, "w", encoding="utf - 8") as f:
            f.writelines(modified_lines)
        return True

    return False


def fix_long_line(line, max_length):
    """
    Attempt to fix a line that exceeds the maximum length.
    
    This function tries several strategies:
    1. Break at commas in function calls or lists
    2. Break at operators in expressions
    3. Break at open parentheses
    """
    line_stripped = line.rstrip()
    if len(line_stripped) <= max_length:
        return line

    indent = len(line) - len(line.lstrip())
    indent_str = " " * indent
    
    # Strategy 1: Break at commas in function calls or lists
    if "," in line_stripped:
        parts = re.split(r'(,\s*)', line_stripped)
        result = parts[0]
        current_length = len(result)
        
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                comma = parts[i]
                next_part = parts[i + 1]
                
                if current_length + len(comma) + len(next_part) > max_length:
                    result += comma + "\n" + indent_str + "    " + next_part.lstrip()
                    current_length = indent + 4 + len(next_part.lstrip())
                else:
                    result += comma + next_part
                    current_length += len(comma) + len(next_part)
        
        return result + "\n"
    
    # Strategy 2: Break at operators in expressions
    operators = [" + ", " - ", " * ", " / ", " = ", " == ", " != ", " >= ", " <= ", 
        " and ", " or "]
    for op in operators:
        if op in line_stripped:
            parts = line_stripped.split(op, 1)
            if len(parts[0]) > max_length - 5:  # If first part is already too long
                continue
                
            return parts[0] + op + "\\\n" + indent_str + "    " + parts[1] + "\n"
    
    # Strategy 3: Break at open parentheses
    if "(" in line_stripped:
        open_paren_pos = line_stripped.find("(")
        if open_paren_pos < max_length - 5:
            return line_stripped[:open_paren_pos + \
                1] + "\n" + indent_str + "    " + line_stripped[open_paren_pos + 1:] + "\n"
    
    # If we can't fix it automatically, return the original line
    return line


def fix_line_length(directory, max_length=88):
    """Fix line length issues in all Python files in the directory."""
    python_files = find_python_files(directory)
    fixed_files = []
    
    for file_path in python_files:
        try:
            if fix_line_length_in_file(file_path, max_length):
                fixed_files.append(str(file_path))
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return fixed_files


def main():
    """Main function to run the script."""
    parser = \
        argparse.ArgumentParser(description="Fix line length issues in Python files")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan")
    parser.add_argument("--max-length", type=int, default=88, 
        help="Maximum line length")
    
    args = parser.parse_args()
    fixed_files = fix_line_length(args.directory, args.max_length)
    
    if fixed_files:
        print(f"Fixed line length issues in {len(fixed_files)} files:")
        for file in fixed_files:
            print(f"  - {file}")
    else:
        print("No line length issues found or fixed.")


if __name__ == "__main__":
    main()
