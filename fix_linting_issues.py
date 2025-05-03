#!/usr / bin / env python3
"""
Script to automatically fix common linting issues.

This script helps fix:
1. Unused imports (F401)
2. Line length issues (E501)
3. Missing whitespace around operators (E226)
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Fix common linting issues")
    parser.add_argument("--fix - imports", action="store_true", 
        help="Fix unused imports")
    parser.add_argument("--fix - line - length", action="store_true", 
        help="Fix line length issues")
    parser.add_argument("--fix - whitespace", action="store_true", 
        help="Fix missing whitespace around operators")
    parser.add_argument("--all", action="store_true", help="Fix all issues")
    parser.add_argument("--file", help="Fix issues in a specific file")
    parser.add_argument("--dry - run", action="store_true", help="Don't modify files, 
        just show what would be done")
    return parser.parse_args()

def get_unused_imports(file_path: str) -> List[Tuple[int, str]]:
    """Get unused imports from a file using flake8."""
    import subprocess
    result = subprocess.run(
        ["flake8", file_path, "--select=F401"], 
        capture_output=True, 
        text=True
    )
    
    unused_imports = []
    for line in result.stdout.splitlines():
        parts = line.split(":")
        if len(parts) >= 4:
            line_num = int(parts[1])
            message = parts[3].strip()
            import_name = re.search(r"'(.+)'", message)
            if import_name:
                unused_imports.append((line_num, import_name.group(1)))
    
    return unused_imports

def fix_unused_imports(file_path: str, dry_run: bool = False) -> int:
    """Fix unused imports in a file."""
    print(f"Fixing unused imports in {file_path}")
    
    unused_imports = get_unused_imports(file_path)
    if not unused_imports:
        print(f"  No unused imports found in {file_path}")
        return 0
    
    with open(file_path, 'r', encoding='utf - 8') as f:
        lines = f.readlines()
    
    fixed_count = 0
    for line_num, import_name in sorted(unused_imports, reverse=True):
        line_idx = line_num - 1
        if line_idx < 0 or line_idx >= len(lines):
            continue
        
        line = lines[line_idx]
        
        # Handle different import formats
        if f"import {import_name}" in line:
            # Simple import
            print(f"  Removing: {line.strip()}")
            if not dry_run:
                lines.pop(line_idx)
            fixed_count += 1
        elif f"from " in line and f" import " in line:
            # From import
            parts = line.split("import")
            if len(parts) == 2:
                imports = [imp.strip() for imp in parts[1].split(",")]
                import_to_remove = None
                for imp in imports:
                    if imp == import_name or imp.startswith(f"{import_name} "):
                        import_to_remove = imp
                        break
                
                if import_to_remove:
                    imports.remove(import_to_remove)
                    if imports:
                        # Still have other imports, update the line
                        new_line = f"{parts[0]}import {', '.join(imports)}\n"
                        print(f"  Updating: {line.strip()} -> {new_line.strip()}")
                        if not dry_run:
                            lines[line_idx] = new_line
                    else:
                        # No more imports, remove the line
                        print(f"  Removing: {line.strip()}")
                        if not dry_run:
                            lines.pop(line_idx)
                    fixed_count += 1
    
    if fixed_count > 0 and not dry_run:
        with open(file_path, 'w', encoding='utf - 8') as f:
            f.writelines(lines)
    
    print(f"  Fixed {fixed_count} unused imports in {file_path}")
    return fixed_count

def fix_line_length(file_path: str, dry_run: bool = False) -> int:
    """Fix line length issues in a file."""
    print(f"Fixing line length issues in {file_path}")
    
    import subprocess
    result = subprocess.run(
        ["flake8", file_path, "--select=E501"], 
        capture_output=True, 
        text=True
    )
    
    long_lines = []
    for line in result.stdout.splitlines():
        parts = line.split(":")
        if len(parts) >= 4:
            line_num = int(parts[1])
            long_lines.append(line_num)
    
    if not long_lines:
        print(f"  No line length issues found in {file_path}")
        return 0
    
    with open(file_path, 'r', encoding='utf - 8') as f:
        lines = f.readlines()
    
    fixed_count = 0
    for line_num in sorted(long_lines, reverse=True):
        line_idx = line_num - 1
        if line_idx < 0 or line_idx >= len(lines):
            continue
        
        line = lines[line_idx]
        
        # Try to fix line length by breaking at logical points
        if len(line) > 100:
            # Try to break at commas, parentheses, or operators
            new_lines = break_long_line(line)
            if new_lines != [line]:
                print(f"  Breaking line {line_num}: {line.strip()}")
                if not dry_run:
                    lines[line_idx:line_idx + 1] = new_lines
                fixed_count += 1
    
    if fixed_count > 0 and not dry_run:
        with open(file_path, 'w', encoding='utf - 8') as f:
            f.writelines(lines)
    
    print(f"  Fixed {fixed_count} line length issues in {file_path}")
    return fixed_count

def break_long_line(line: str) -> List[str]:
    """Break a long line into multiple shorter lines."""
    # If it's an import statement, handle it specially
    if line.strip().startswith("from ") and " import " in line:
        return break_import_line(line)
    
    # If it's a function call or definition with many parameters
    if "(" in line and ")" in line:
        return break_function_line(line)
    
    # If it's a string assignment
    if "=" in line and ('"' in line or "'" in line):
        return break_string_assignment(line)
    
    # If it's a list or dictionary
    if "[" in line and "]" in line:
        return break_list_or_dict(line, "[", "]")
    if "{" in line and "}" in line:
        return break_list_or_dict(line, "{", "}")
    
    # Default: just return the original line
    return [line]

def break_import_line(line: str) -> List[str]:
    """Break a long import line into multiple lines."""
    parts = line.split(" import ")
    if len(parts) != 2:
        return [line]
    
    from_part = parts[0]
    imports = [imp.strip() for imp in parts[1].split(",")]
    
    if len(imports) <= 1:
        return [line]
    
    # Create a multi - line import
    result = [f"{from_part} import (\n"]
    for imp in imports:
        result.append(f"    {imp},\n")
    result.append(")\n")
    
    return result

def break_function_line(line: str) -> List[str]:
    """Break a long function call or definition into multiple lines."""
    # Find the opening parenthesis
    open_idx = line.find("(")
    if open_idx == -1:
        return [line]
    
    # Get the indentation and function name
    indent = line[:open_idx].rstrip("(")
    
    # Split the parameters
    params_str = line[open_idx + 1:].rstrip()
    if not params_str.endswith(")"):
        return [line]
    
    params_str = params_str[:-1]  # Remove the closing parenthesis
    
    # Split by commas, but respect nested structures
    params = []
    current_param = ""
    nesting_level = 0
    
    for char in params_str:
        if char == "," and nesting_level == 0:
            params.append(current_param.strip())
            current_param = ""
        else:
            current_param += char
            if char in "([{":
                nesting_level += 1
            elif char in ")]}":
                nesting_level -= 1
    
    if current_param:
        params.append(current_param.strip())
    
    if len(params) <= 1:
        return [line]
    
    # Create a multi - line function call
    result = [f"{indent}(\n"]
    for param in params:
        result.append(f"    {indent}{param},\n")
    result.append(f"{indent})\n")
    
    return result

def break_string_assignment(line: str) -> List[str]:
    """Break a long string assignment into multiple lines."""
    parts = line.split("=", 1)
    if len(parts) != 2:
        return [line]
    
    var_name = parts[0].rstrip()
    value = parts[1].lstrip()
    
    # Check if it's a string
    if not (value.startswith('"') and \
        value.endswith('"')) and not (value.startswith("'") and value.endswith("'")):
        return [line]
    
    # Break into multiple lines using string concatenation
    if len(value) > 80:
        # Find a good breaking point
        break_point = 70
        while break_point > 0:
            if value[break_point] in " ,.;:":
                break
            break_point -= 1
        
        if break_point > 0:
            first_part = value[:break_point + 1]
            second_part = value[break_point + 1:]
            
            # Ensure proper string formatting
            if first_part.startswith('"'):
                first_part = first_part.rstrip() + '"'
                if not second_part.startswith('"'):
                    second_part = '"' + second_part
            elif first_part.startswith("'"):
                first_part = first_part.rstrip() + "'"
                if not second_part.startswith("'"):
                    second_part = "'" + second_part
            
            return [
                f"{var_name} = {first_part} \\\n",
                f"    {second_part}\n"
            ]
    
    return [line]

def break_list_or_dict(line: str, open_char: str, close_char: str) -> List[str]:
    """Break a long list or dictionary into multiple lines."""
    open_idx = line.find(open_char)
    close_idx = line.rfind(close_char)
    
    if open_idx == -1 or close_idx == -1 or close_idx <= open_idx:
        return [line]
    
    prefix = line[:open_idx]
    content = line[open_idx + 1:close_idx]
    suffix = line[close_idx + 1:]
    
    # Split by commas, but respect nested structures
    items = []
    current_item = ""
    nesting_level = 0
    
    for char in content:
        if char == "," and nesting_level == 0:
            items.append(current_item.strip())
            current_item = ""
        else:
            current_item += char
            if char in "([{":
                nesting_level += 1
            elif char in ")]}":
                nesting_level -= 1
    
    if current_item:
        items.append(current_item.strip())
    
    if len(items) <= 1:
        return [line]
    
    # Create a multi - line list or dict
    indent = " " * len(prefix)
    result = [f"{prefix}{open_char}\n"]
    for item in items:
        result.append(f"    {indent}{item},\n")
    result.append(f"{indent}{close_char}{suffix}")
    
    return result

def fix_whitespace(file_path: str, dry_run: bool = False) -> int:
    """Fix missing whitespace around operators in a file."""
    print(f"Fixing whitespace issues in {file_path}")
    
    import subprocess
    result = subprocess.run(
        ["flake8", file_path, "--select=E226"], 
        capture_output=True, 
        text=True
    )
    
    whitespace_issues = []
    for line in result.stdout.splitlines():
        parts = line.split(":")
        if len(parts) >= 4:
            line_num = int(parts[1])
            col_num = int(parts[2])
            whitespace_issues.append((line_num, col_num))
    
    if not whitespace_issues:
        print(f"  No whitespace issues found in {file_path}")
        return 0
    
    with open(file_path, 'r', encoding='utf - 8') as f:
        lines = f.readlines()
    
    fixed_count = 0
    for line_num, col_num in sorted(whitespace_issues, reverse=True):
        line_idx = line_num - 1
        if line_idx < 0 or line_idx >= len(lines):
            continue
        
        line = lines[line_idx]
        if col_num >= len(line):
            continue
        
        # Find the operator at the column
        operators = [' + ', ' - ', ' * ', ' / ', ' % ', '** ', ' // ', '=', '+=', '-=', 
            '*=', '/=', '%=', '**=', '//=']
        found_operator = None
        for op in sorted(operators, key=len, reverse=True):
            if col_num < len(line) and line[col_num - 1:col_num - 1 + len(op)] == op:
                found_operator = op
                break
        
        if found_operator:
            # Fix the whitespace around the operator
            before = line[:col_num - 1].rstrip()
            after = line[col_num - 1 + len(found_operator):].lstrip()
            new_line = f"{before} {found_operator} {after}"
            
            print(f"  Fixing line {line_num}: {line.strip()} -> {new_line.strip()}")
            if not dry_run:
                lines[line_idx] = new_line
            fixed_count += 1
    
    if fixed_count > 0 and not dry_run:
        with open(file_path, 'w', encoding='utf - 8') as f:
            f.writelines(lines)
    
    print(f"  Fixed {fixed_count} whitespace issues in {file_path}")
    return fixed_count

def find_python_files(directory: str = ".") -> List[str]:
    """Find all Python files in the directory and its subdirectories."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def main():
    """Main function."""
    args = parse_args()
    
    if args.file:
        files = [args.file]
    else:
        files = find_python_files()
    
    total_fixed = 0
    
    for file_path in files:
        if args.fix_imports or args.all:
            total_fixed += fix_unused_imports(file_path, args.dry_run)
        
        if args.fix_line_length or args.all:
            total_fixed += fix_line_length(file_path, args.dry_run)
        
        if args.fix_whitespace or args.all:
            total_fixed += fix_whitespace(file_path, args.dry_run)
    
    print(f"\nTotal issues fixed: {total_fixed}")
    if args.dry_run:
        print("Note: This was a dry run. No files were modified.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
