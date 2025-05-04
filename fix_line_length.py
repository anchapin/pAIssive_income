#!/usr/bin/env python
"""
Script to fix line length issues (E501) in Python files.

This script scans Python files in the project and attempts to fix lines
that exceed the maximum line length (usually 79 or 88 characters) using
various strategies like:
- Breaking long function calls into multiple lines
- Breaking long string literals into multiple lines
- Breaking long lists/dicts into multiple lines
- Reformatting long import statements
- Special handling for test assertions and __init__.py files

Usage:
    python fix_line_length.py [directory] [max_length]
"""

import os
import re
import sys
import ast
import tokenize
import subprocess
from textwrap import wrap
from io import StringIO

def run_flake8(directory):
    """Run flake8 to find line length issues and parse the output."""
    try:
        result = subprocess.run(
            ["flake8", directory, "--select=E501"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error running flake8: {e}")
        return []

def parse_flake8_output(output_lines):
    """Parse flake8 output to extract file paths and line numbers."""
    issues = {}
    for line in output_lines:
        # Example line: path/to/file.py:1:1: E501 line too long
        match = re.match(r'(.+?):(\d+):\d+: E501', line)
        if match:
            file_path, line_num = match.groups()
            file_path = file_path.strip()
            line_num = int(line_num)
            issues.setdefault(file_path, set()).add(line_num)
    return {k: sorted(v) for k, v in issues.items()}

def fix_docstring(line, max_length):
    """Fix a long docstring by breaking it into multiple lines."""
    # Check if this is a docstring (triple quotes)
    matches = list(re.finditer(r'([\']{3}|[\"]{3})(.*?)(\1)', line))
    if matches:
        match = matches[0]
        prefix = line[:match.start()].rstrip()
        content = match.group(2)
        suffix = line[match.end():].lstrip()
        quote = match.group(1)
        
        # For multi-line docstrings, format with proper indentation
        if '\n' in content or len(line) > max_length:
            indent = ' ' * len(prefix)
            wrapped = wrap(content, width=max_length-len(indent)-3)
            if wrapped:
                result = prefix + quote + '\n'
                for part in wrapped:
                    result += indent + part + '\n'
                result += indent + quote + suffix
                return result
    return line

def fix_all_list(line, max_length):
    """Fix __all__ list with special formatting for init files."""
    if '__all__' in line and '[' in line and ']' in line:
        try:
            # Extract list content
            prefix = line[:line.find('[')].rstrip()
            content = line[line.find('[')+1:line.rfind(']')]
            suffix = line[line.rfind(']'):]
            
            # Parse items and comments
            items = []
            current_group = []
            current_comment = None
            
            for item in content.split(','):
                item = item.strip()
                if not item:
                    continue
                    
                # Check if this is a comment
                if item.startswith('#'):
                    if current_group:
                        items.append((current_comment, current_group))
                        current_group = []
                    current_comment = item
                else:
                    current_group.append(item)
            
            # Add remaining items
            if current_group:
                items.append((current_comment, current_group))
            
            # Format with proper indentation
            result = prefix + '[\n'
            for comment, group in items:
                if comment:
                    result += ' ' * 4 + comment + '\n'
                for item in group:
                    result += ' ' * 4 + item + ',\n'
            result = result.rstrip(',\n') + '\n]' + suffix
            
            return result
        except Exception:
            return line
    return line

def fix_import_line(line, max_length):
    """Fix a long import statement by breaking it into multiple lines."""
    if 'import' in line:
        # Handle 'from module import items' statements
        if 'from' in line:
            match = re.match(r'(\s*from\s+[\w.]+\s+import\s+)(.+)', line)
            if match:
                prefix = match.group(1)
                items_str = match.group(2)
                
                # Skip if already parenthesized
                if '(' in items_str:
                    return line
                
                items = [item.strip() for item in items_str.split(',')]
                
                # For single long imports, wrap in parentheses
                if len(items) == 1 and len(line) > max_length:
                    return f"{prefix}(\n    {items[0]}\n)"

                # For multiple imports, put each on its own line
                result = prefix + '(\n'
                for item in items[:-1]:
                    result += ' ' * 4 + item + ',\n'
                result += ' ' * 4 + items[-1] + '\n)'
                return result
        else:
            # Handle regular import statements
            parts = line.split('import')
            if len(parts) == 2:
                prefix = parts[0] + 'import '
                modules = [m.strip() for m in parts[1].split(',')]
                if len(modules) > 1:
                    result = prefix + '(\n'
                    for module in modules[:-1]:
                        result += ' ' * 4 + module + ',\n'
                    result += ' ' * 4 + modules[-1] + '\n)'
                    return result
    return line

def fix_function_call(line, max_length):
    """Fix a long function call by breaking arguments into multiple lines."""
    if '(' not in line or ')' not in line or line.strip().startswith(('class ', 'def ')):
        return line

    try:
        # Find the function call part
        prefix = line[:line.find('(')].rstrip()
        content = line[line.find('(')+1:line.rfind(')')]
        suffix = line[line.rfind(')'):]
        
        # Skip if this appears to be a nested structure
        if not content or '(' in prefix:
            return line
        
        # Parse the arguments while respecting nested structures
        args = []
        current = []
        depth = 0
        tokens = list(tokenize.generate_tokens(StringIO(content).readline))
        
        for token in tokens:
            if token.string in '([{':
                depth += 1
            elif token.string in ')]}':
                depth -= 1
            elif token.string == ',' and depth == 0:
                args.append(''.join(current))
                current = []
                continue
            current.append(token.string)
        if current:
            args.append(''.join(current))
        
        args = [arg.strip() for arg in args if arg.strip()]
        
        # For single long arguments, try to break at operators
        if len(args) == 1 and len(line) > max_length:
            arg = args[0]
            if any(op in arg for op in [' + ', ' - ', ' * ', ' / ', ' and ', ' or ']):
                operators = [' + ', ' - ', ' * ', ' / ', ' and ', ' or ']
                for op in operators:
                    if op in arg:
                        parts = arg.split(op)
                        result = prefix + '(\n'
                        result += ' ' * 4 + parts[0]
                        for part in parts[1:]:
                            result += ' ' + op.strip() + '\n' + ' ' * 4 + part.strip()
                        result += '\n)' + suffix
                        return result
            return line

        # Format multiple arguments on separate lines
        if len(args) > 1:
            result = prefix + '(\n'
            for arg in args[:-1]:
                result += ' ' * 4 + arg + ',\n'
            result += ' ' * 4 + args[-1] + '\n'
            result += ')' + suffix
            return result

    except Exception:
        return line
    return line

def fix_list_or_dict(line, max_length):
    """Fix long list or dictionary literals by breaking them into multiple lines."""
    if ('[' not in line and '{' not in line) or len(line) <= max_length:
        return line

    try:
        # Handle __all__ lists specially
        if '__all__' in line:
            return fix_all_list(line, max_length)
            
        # Find the opening bracket/brace
        opening = '[' if '[' in line else '{'
        closing = ']' if opening == '[' else '}'
        prefix = line[:line.find(opening)].rstrip()
        content = line[line.find(opening)+1:line.rfind(closing)]
        suffix = line[line.rfind(closing):]
        
        # Parse the items
        items = []
        current = []
        depth = 0
        tokens = list(tokenize.generate_tokens(StringIO(content).readline))
        
        for token in tokens:
            if token.string in '([{':
                depth += 1
            elif token.string in ')]}':
                depth -= 1
            elif token.string == ',' and depth == 0:
                items.append(''.join(current))
                current = []
                continue
            current.append(token.string)
        if current:
            items.append(''.join(current))
        
        items = [item.strip() for item in items if item.strip()]
        
        # Format items on separate lines
        if len(items) > 1 or len(line) > max_length:
            result = prefix + opening + '\n'
            for item in items[:-1]:
                result += ' ' * 4 + item + ',\n'
            if items:
                result += ' ' * 4 + items[-1] + '\n'
            result += closing + suffix
            return result
    except Exception:
        return line
    return line

def fix_long_line(line, max_length):
    """Attempt to fix a line that exceeds max_length."""
    if len(line) <= max_length:
        return line

    original_line = line
    
    # Try different fixing strategies in order
    if '"""' in line or "'''" in line:
        line = fix_docstring(line, max_length)
    
    if len(line.splitlines()[0]) > max_length and '__all__' in line:
        line = fix_all_list(line, max_length)
    
    if len(line.splitlines()[0]) > max_length and 'import' in line:
        line = fix_import_line(line, max_length)
    
    if len(line.splitlines()[
    0
]]) > max_length and ('(' in line or '[' in line or '{' in line):
        if '(' in line and ')' in line:
            line = fix_function_call(line, max_length)
        if len(line.splitlines()[0]) > max_length and ('[' in line or '{' in line):
            line = fix_list_or_dict(line, max_length)
    
    return line if line != original_line else original_line

def is_init_file(file_path):
    """Check if the file is an __init__.py file."""
    return os.path.basename(file_path) == '__init__.py'

def fix_file(file_path, line_numbers, max_length=88):
    """Fix line length issues in a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        modified = False
        for line_num in line_numbers:
            if 0 < line_num <= len(lines):
                original_line = lines[line_num - 1]
                if len(original_line.rstrip('\n')) > max_length:
                    # Use special handling for __init__.py files
                    if is_init_file(file_path):
                        max_length = max(
    max_length,
    100
))  # Allow slightly longer lines in __init__.py
                    
                    modified_line = fix_long_line(
    original_line.rstrip('\n'),
    max_length
))
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

    # Run flake8 to find line length issues
    flake8_output = run_flake8(directory)
    if not flake8_output:
        print("No line length issues found.")
        return

    # Parse flake8 output
    issues = parse_flake8_output(flake8_output)
    
    # Fix each file
    fixed_files = []
    for file_path, line_numbers in issues.items():
        if fix_file(file_path, line_numbers, max_length):
            fixed_files.append(file_path)

    if fixed_files:
        print(f"Fixed line length issues in {len(fixed_files)} files:")
        for file in sorted(fixed_files):
            print(f"  - {file}")
    else:
        print("No files were modified.")

    # Print remaining issues
    remaining_files = {k for k, v in issues.items() if k not in fixed_files}
    if remaining_files:
        print("\nThe following files still have line length issues:")
        for file in sorted(remaining_files):
            print(f"  - {file}")

if __name__ == "__main__":
    main()
