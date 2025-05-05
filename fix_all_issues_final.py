#!/usr/bin/env python3
"""
Comprehensive script to fix syntax errors, formatting issues, and linting problems.
This script combines functionality from multiple existing scripts to provide a one-stop
solution for fixing common code quality issues.
"""

import argparse
import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path


def should_ignore(file_path, ignore_patterns=None):
    """Check if a file should be ignored based on patterns."""
    if ignore_patterns is None:
        # Define patterns that work across platforms
        ignore_patterns = [
            # Virtual environments
            ".venv*",
            "*/.venv*",
            "*\\.venv*",
            "venv*",
            "*/venv*",
            "*\\venv*",
            # Git directories
            ".git*",
            "*/.git*",
            "*\\.git*",
            # Python cache
            "__pycache__*",
            "*/__pycache__*",
            "*\\__pycache__*",
            # Python compiled files
            "*.pyc",
            "*.pyo",
            "*.pyd",
            # Build directories
            "build*",
            "*/build*",
            "*\\build*",
            # Distribution directories
            "dist*",
            "*/dist*",
            "*\\dist*",
            # Egg info
            "*.egg-info*",
            "*/*.egg-info*",
            "*\\*.egg-info*",
        ]

    # Normalize path for consistent matching across platforms
    file_path_str = os.path.normpath(str(file_path))
    
    # Also check the path with forward slashes for cross-platform compatibility
    file_path_fwd = file_path_str.replace(os.path.sep, '/')
    
    # Check if file matches any ignore pattern
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(file_path_str, pattern) or fnmatch.fnmatch(file_path_fwd, pattern):
            return True
            
    # Additional checks for common virtual environment paths
    common_venv_dirs = ['.venv', 'venv', '.env', 'env']
    for venv_dir in common_venv_dirs:
        if venv_dir in file_path_str.split(os.path.sep):
            return True

    return False


def find_python_files(path):
    """Find all Python files in the given path."""
    python_files = []

    if os.path.isfile(path) and path.endswith(".py"):
        return [path]

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if not should_ignore(file_path):
                    python_files.append(file_path)

    return python_files


def fix_missing_colons(content):
    """Fix missing colons after class/function definitions and control statements."""
    # Fix missing colons after class definitions
    content = re.sub(r"(class\s+\w+(?:\([^)]*\))?)(\s*\n)", r"\1:\2", content)

    # Fix missing colons after function definitions
    content = re.sub(r"(def\s+\w+\([^)]*\))(\s*\n)", r"\1:\2", content)

    # Fix missing colons after control statements
    for keyword in [
        "if",
        "else",
        "elif",
        "for",
        "while",
        "try",
        "except",
        "finally",
        "with",
    ]:
        pattern = rf"({keyword}\s+[^:\n]+)(\s*\n)"
        content = re.sub(pattern, r"\1:\2", content)

    return content


def fix_class_definitions(content):
    """Fix class definitions that are split across multiple lines."""
    lines = content.split("\n")
    fixed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if line starts a class definition but doesn't end with a colon
        if re.match(r"^\s*class\s+\w+(?:\([^)]*)?$", line.strip()):
            # Collect lines until we find a line with a colon or closing parenthesis
            class_def = line
            j = i + 1

            while j < len(lines) and not re.search(r"[:,]", lines[j]):
                class_def += " " + lines[j].strip()
                j += 1

            # If we found a line with a colon or comma, add it
            if j < len(lines):
                class_def += " " + lines[j].strip()
                j += 1

            # Add the fixed class definition
            if not class_def.strip().endswith(":"):
                class_def += ":"

            fixed_lines.append(class_def)
            i = j
        else:
            fixed_lines.append(line)
            i += 1

    return "\n".join(fixed_lines)


def fix_test_class_init(content):
    """Fix test classes with __init__ methods."""
    # Find test classes with __init__ methods
    pattern = r"(class\s+Test\w+\([^)]*\):\s*\n(?:\s+[^\n]*\n)*?\s+def\s+__init__\s*\([^)]*\):\s*\n)"
    
    # Replace __init__ with setup_method
    content = re.sub(
        pattern,
        lambda m: m.group(0).replace("__init__", "setup_method"),
        content
    )
    
    return content


def fix_syntax(file_path, check_only=False):
    """Fix common syntax issues in a file."""
    try:
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Apply fixes
        original_content = content

        # Fix missing colons
        content = fix_missing_colons(content)

        # Fix class definitions
        content = fix_class_definitions(content)

        # Fix test classes with __init__ methods
        content = fix_test_class_init(content)

        # Check if the content was modified
        if content != original_content:
            if check_only:
                print(f"Syntax issues found in: {file_path}")
                return False
            else:
                # Write the fixed content back to the file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"Fixed syntax in: {file_path}")
                return True

        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def format_file(file_path, check_only=False):
    """Format a Python file to improve code style."""
    try:
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Apply some basic formatting rules
        original_content = content

        # 1. Fix trailing whitespace
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

        # 2. Ensure consistent line endings
        content = content.replace('\r\n', '\n')

        # 3. Fix function calls with multiple arguments
        content = re.sub(
            r'(\s+)([a-zA-Z0-9_]+)\(\s*\n\s*([^,\n]+),\s*\n\s*([^,\n]+),\s*\n\s*\)',
            r'\1\2(\n\1    \3, \4\n\1)',
            content
        )

        # 4. Fix function calls with two arguments on separate lines
        content = re.sub(
            r'(\s+)([a-zA-Z0-9_]+)\(\s*\n\s*([^,\n]+),\s*\n\s*([^,\n]+)\s*\n\s*\)',
            r'\1\2(\n\1    \3, \4\n\1)',
            content
        )

        # 5. Fix function calls with a single argument on a separate line
        content = re.sub(
            r'(\s+)([a-zA-Z0-9_]+)\(\s*\n\s*([^,\n]+)\s*\n\s*\)',
            r'\1\2(\1    \3\1)',
            content
        )

        # Check if the content was modified
        if content != original_content:
            if check_only:
                print(f"Formatting issues found in: {file_path}")
                return False
            else:
                # Write the formatted content back to the file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"Formatted: {file_path}")
                return True

        return True

    except Exception as e:
        print(f"Error formatting {file_path}: {e}")
        return False


def run_external_tool(command, file_path, check_only=False):
    """Run an external tool on a file."""
    try:
        cmd = command + [file_path]
        if check_only:
            # Add check flag if available
            if "--check" in command or "--diff" in command:
                pass  # Command already has check flag
            else:
                cmd = command + ["--check", file_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            if check_only:
                print(f"Issues found in {file_path} by {command[0]}:")
                print(result.stdout)
                print(result.stderr)
                return False
            else:
                print(f"Fixed {file_path} with {command[0]}")
                return True
        
        return True
    
    except Exception as e:
        print(f"Error running {command[0]} on {file_path}: {e}")
        return False


def fix_file(file_path, check_only=False, fix_syntax_only=False, fix_format_only=False, 
             run_black=True, run_isort=True, run_ruff=True):
    """Fix all issues in a file."""
    success = True
    
    # Fix syntax errors
    if not fix_format_only:
        if not fix_syntax(file_path, check_only):
            success = False
    
    # Skip formatting if only fixing syntax
    if fix_syntax_only:
        return success
    
    # Format the file
    if not format_file(file_path, check_only):
        success = False
    
    # Run external tools if they're installed and enabled
    try:
        # Check if black is installed and enabled
        if run_black:
            black_cmd = ["black"]
            if not check_only:
                black_success = run_external_tool(black_cmd, file_path, check_only)
                if not black_success:
                    success = False
        
        # Check if isort is installed and enabled
        if run_isort:
            isort_cmd = ["isort"]
            if not check_only:
                isort_success = run_external_tool(isort_cmd, file_path, check_only)
                if not isort_success:
                    success = False
        
        # Check if ruff is installed and enabled
        if run_ruff:
            ruff_cmd = ["ruff", "check", "--fix"]
            if not check_only:
                ruff_success = run_external_tool(ruff_cmd, file_path, check_only)
                if not ruff_success:
                    success = False
    
    except Exception as e:
        print(f"Error running external tools on {file_path}: {e}")
        success = False
    
    return success


def main():
    """Main function to parse arguments and fix issues."""
    parser = argparse.ArgumentParser(
        description="Fix syntax errors, formatting issues, and linting problems in Python files"
    )

    parser.add_argument(
        "path", nargs="?", default=".", help="Path to file or directory to check/fix"
    )
    parser.add_argument(
        "--check", action="store_true", help="Check for issues without fixing"
    )
    parser.add_argument(
        "--syntax-only", action="store_true", help="Fix only syntax errors"
    )
    parser.add_argument(
        "--format-only", action="store_true", help="Fix only formatting issues"
    )
    parser.add_argument(
        "--no-black", action="store_true", help="Don't run black formatter"
    )
    parser.add_argument(
        "--no-isort", action="store_true", help="Don't run isort"
    )
    parser.add_argument(
        "--no-ruff", action="store_true", help="Don't run ruff linter"
    )

    args = parser.parse_args()

    # Find Python files to check/fix
    python_files = find_python_files(args.path)

    if not python_files:
        print("No Python files found to check.")
        return 0

    print(f"Checking {len(python_files)} Python files...")

    # Check/fix the files
    issues_found = False
    for file_path in python_files:
        if not fix_file(
            file_path, 
            check_only=args.check,
            fix_syntax_only=args.syntax_only,
            fix_format_only=args.format_only,
            run_black=not args.no_black,
            run_isort=not args.no_isort,
            run_ruff=not args.no_ruff
        ):
            issues_found = True

    if args.check and issues_found:
        print("Issues found. Run without --check to fix.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
