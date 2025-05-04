#!/usr/bin/env python
"""
Script to fix unused imports (F401) in Python files.

This script scans Python files in the project and removes unused imports
that are flagged by linters like flake8 or ruff with the F401 error code.

Usage:
    python fix_unused_imports.py [directory]
"""

import re
import sys
import subprocess

def run_flake8(directory):
    """Run flake8 to find unused imports and parse the output."""
    try:
        result = subprocess.run(
            ["flake8", directory, "--select=F401"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error running flake8: {e}")
        return []

def parse_flake8_output(output_lines):
    """Parse flake8 output to extract file paths and unused imports."""
    unused_imports = {}
    for line in output_lines:
        # Example line: path/to/file.py:1:1: F401 'module' imported but unused
        match = re.match(
                         r'(.+?):(\d+):\d+: F401 [\'"](.*?)[\'"] imported but unused',
                         line
                        )
        if match:
            file_path, line_num, import_name = match.groups()
            file_path = file_path.strip()
            line_num = int(line_num)
            unused_imports.setdefault(file_path, []).append((line_num, import_name))
    return unused_imports

def find_import_span(lines, line_num, import_name):
    """Find the start and end indices of an import statement."""
    line = lines[line_num - 1]
    indentation = len(line) - len(line.lstrip())
    # For multi-line imports, find the full import statement
    if '(' in line and ')' not in line:
        start = line_num - 1
        end = start
        while end < len(lines) and ')' not in lines[end]:
            end += 1
        if end < len(lines):  # Include the line with closing parenthesis
            end += 1
        return start, end
    return line_num - 1, line_num

def remove_unused_imports(file_path, unused_imports):
    """Remove unused imports from a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Sort unused imports by line number in reverse order to avoid index issues
    unused_imports.sort(reverse=True)
    modified = False
    for line_num, import_name in unused_imports:
        if line_num <= len(lines):
            start_idx, end_idx = find_import_span(lines, line_num, import_name)
            line = lines[line_num - 1]
            # Handle import with 'as' alias
            import_parts = import_name.split(" as ")
            if len(import_parts) > 1:
                import_name = import_parts[0]
            if "," in line:
                # Handle multiple imports on one line
                if "from" in line:
                    # Handle 'from module import x, y, z'
                    pattern = fr"(from\s+[.\w]+\s+import\s+)([^#\n]+)"
                    match = re.match(pattern, line.strip())
                    if match:
                        prefix = match.group(1)
                        imports = [i.strip() for i in match.group(2).split(",")]
                        # For 'from' imports, handle both full path and last component
                        import_parts = import_name.split(".")
                        imports =[
    iforiinimportsifi!=import_nameandi!=import_parts[-1]
]]
                        if imports:
                            indent = " " * (len(line) - len(line.lstrip()))
                            lines[
    line_num-1
]] = f"{indent}{prefix}{', '.join(imports)}\n"
                        else:
                            lines[line_num - 1] = ""
                        modified = True
                else:
                    # Handle 'import x, y, z'
                    imports = [i.strip() for i in line.split("import")[1].split(",")]
                    imports = [i for i in imports if i.strip() != import_name]
                    if imports:
                        indent = " " * (len(line) - len(line.lstrip()))
                        lines[line_num - 1] = f"{indent}import {', '.join(imports)}\n"
                    else:
                        lines[line_num - 1] = ""
                    modified = True
            else:
                # Handle single import (both regular and 'from' imports)
                # Clear the entire span for multi-line imports
                for i in range(start_idx, end_idx):
                    lines[i] = ""
                modified = True

    # Remove empty lines that were created
    lines = [line for line in lines if line.strip() or line == "\n"]
    # Remove consecutive blank lines
    final_lines = []
    prev_empty = False
    for line in lines:
        if line.strip():
            final_lines.append(line)
            prev_empty = False
        elif not prev_empty:
            final_lines.append(line)
            prev_empty = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(final_lines)
        return True

    return False

def main():
    """Main function to run the script."""
    directory = sys.argv[1] if len(sys.argv) > 1 else "."

    # Run flake8 to find unused imports
    flake8_output = run_flake8(directory)
    if not flake8_output:
        print("No unused imports found.")
        return

    # Parse flake8 output
    unused_imports = parse_flake8_output(flake8_output)
    # Fix each file
    fixed_files = []
    for file_path, imports in unused_imports.items():
        try:
            if remove_unused_imports(file_path, imports):
                fixed_files.append(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    if fixed_files:
        print(f"Fixed unused imports in {len(fixed_files)} files:")
        for file in fixed_files:
            print(f"  - {file}")
    else:
        print("No files were modified.")

if __name__ == "__main__":
    main()
