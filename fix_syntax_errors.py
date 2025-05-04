#!/usr/bin/env python
"""
Script to fix common syntax errors in Python files.

This script helps fix syntax errors that are causing GitHub Actions to fail.
It focuses on fixing:
1. Removing duplicate lines
2. Fixing indentation issues
3. Fixing misplaced try-except blocks
4. Ensuring proper code structure
"""

import os
import re
import sys
import ast
import argparse
from pathlib import Path
from typing import List, Set, Tuple, Optional


def get_gitignore_patterns() -> Set[str]:
    """Read .gitignore patterns and return them as a set."""
    patterns = set()
    try:
        with open(".gitignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.add(line)
    except FileNotFoundError:
        pass
    return patterns


def should_ignore(file_path: str, ignore_patterns: Set[str]) -> bool:
    """Check if a file should be ignored based on gitignore patterns."""
    # Convert Windows paths to forward slashes for consistency
    file_path = file_path.replace("\\", "/")

    for pattern in ignore_patterns:
        # Basic gitignore pattern matching
        if pattern.endswith("/"):
            # Directory pattern
            if pattern[:-1] in file_path.split("/"):
                return True
        elif pattern.startswith("**/"):
            # Match anywhere in path
            if file_path.endswith(pattern[3:]):
                return True
        elif pattern.startswith("/"):
            # Match from root
            if file_path.startswith(pattern[1:]):
                return True
        else:
            # Simple pattern
            if pattern in file_path:
                return True
    return False


def is_valid_python(content: str) -> bool:
    """Check if the content is valid Python code."""
    try:
        ast.parse(content)
        return True
    except SyntaxError:
        return False
    except Exception:
        return False


def remove_duplicate_lines(content: str) -> str:
    """Remove duplicate consecutive lines from the content."""
    lines = content.splitlines()
    result_lines = []

    i = 0
    while i < len(lines):
        result_lines.append(lines[i])
        # Skip duplicate consecutive lines
        j = i + 1
        while j < len(lines) and lines[j] == lines[i]:
            j += 1
        i = j

    return '\n'.join(result_lines)


def fix_missing_colons(content: str) -> str:
    """Fix missing colons after class and function definitions."""
    # Fix missing colons after class definitions
    content = re.sub(r'(class\s+\w+\([^)]*\))\s*\n', r'\1:\n', content)

    # Fix missing colons after function definitions
    content = re.sub(r'(def\s+\w+\([^)]*\))\s*\n', r'\1:\n', content)

    # Fix missing parentheses after function definitions
    content = re.sub(r'(def\s+\w+)\s*\n', r'\1():\n', content)

    return content


def fix_indentation(content: str) -> str:
    """Fix common indentation issues."""
    lines = content.splitlines()
    fixed_lines = []
    prev_line_empty = False

    for line in lines:
        # Skip empty lines
        if line.strip() == '':
            fixed_lines.append(line)
            prev_line_empty = True
            continue

        # Check for unexpected indentation at the beginning of a block
        if prev_line_empty and line.startswith('    '):
            fixed_lines.append(line.lstrip())
        else:
            fixed_lines.append(line)

        prev_line_empty = False

    return '\n'.join(fixed_lines)


def fix_unmatched_parentheses(content: str) -> str:
    """Fix unmatched parentheses."""
    # Count opening and closing parentheses
    open_count = content.count('(')
    close_count = content.count(')')

    # If there are more opening than closing parentheses, add closing ones
    if open_count > close_count:
        content += ')' * (open_count - close_count)

    # If there are more closing than opening parentheses, remove extra closing ones
    elif close_count > open_count:
        for _ in range(close_count - open_count):
            last_close = content.rindex(')')
            content = content[:last_close] + content[last_close+1:]

    return content


def fix_try_except_blocks(content: str) -> str:
    """Fix misplaced try-except blocks."""
    # Fix missing except blocks
    if 'try:' in content and 'except' not in content and 'finally' not in content:
        content += '\nexcept Exception as e:\n    pass\n'

    # Fix misplaced except blocks
    pattern = re.compile(r'(\s*)try\s*:\s*\n(.*?)\n\s*except\s+([^\n:]+):\s*\n(.*?)(\n\s*else\s*:\s*\n)',
                        re.DOTALL)

    def fix_block(match):
        indent = match.group(1)
        try_block = match.group(2)
        except_type = match.group(3)
        except_block = match.group(4)

        # Remove the redundant else block
        return f"{indent}try:\n{try_block}\n{indent}except {except_type}:\n{except_block}"

    return pattern.sub(fix_block, content)


def fix_invalid_syntax(content: str) -> str:
    """Fix various invalid syntax issues."""
    # Fix assignment in class/function definition
    content = re.sub(r'(class|def)\s+\w+\s*=', r'\1 ', content)

    # Fix missing quotes in print statements
    content = re.sub(r'print\(f"([^"]*)"([^)]*)\)', r'print(f"\1"\2)', content)

    # Fix missing closing parentheses in function calls
    content = re.sub(r'(\w+)\(([^)]*)\s*$', r'\1(\2)', content)

    return content


def fix_file(file_path: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Apply fixes to a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if the file already has valid syntax
        if is_valid_python(content):
            return True, "File already has valid syntax."

        # Apply fixes
        original_content = content

        # Step 1: Remove duplicate lines
        content = remove_duplicate_lines(content)

        # Step 2: Fix missing colons
        content = fix_missing_colons(content)

        # Step 3: Fix indentation issues
        content = fix_indentation(content)

        # Step 4: Fix unmatched parentheses
        content = fix_unmatched_parentheses(content)

        # Step 5: Fix try-except blocks
        content = fix_try_except_blocks(content)

        # Step 6: Fix other invalid syntax
        content = fix_invalid_syntax(content)

        # Check if our fixes resolved the syntax issues
        if not is_valid_python(content):
            return False, "Could not fix syntax errors automatically."

        # Check if we made any changes
        if content == original_content:
            return True, "No changes needed."

        # Write the fixed content back to the file
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Fixed syntax errors."
        else:
            return True, "Would fix syntax errors (dry run)."

    except Exception as e:
        return False, f"Error processing file: {str(e)}"


def process_directory(directory: str, file_patterns: Optional[List[str]] = None,
                     dry_run: bool = False) -> bool:
    """Process all Python files in a directory and its subdirectories."""
    all_passed = True
    ignore_patterns = get_gitignore_patterns()
    fixed_files = []
    failed_files = []

    if file_patterns:
        # Process specific files/patterns
        for pattern in file_patterns:
            for file_path in Path(directory).glob(pattern):
                if file_path.is_file() and file_path.suffix == ".py":
                    relative_path = str(file_path.relative_to(directory))
                    if not should_ignore(relative_path, ignore_patterns):
                        success, message = fix_file(str(file_path), dry_run)
                        print(f"{file_path}: {message}")
                        if success and message != "No changes needed." and message != "File already has valid syntax.":
                            fixed_files.append(str(file_path))
                        elif not success:
                            failed_files.append(str(file_path))
                            all_passed = False
    else:
        # Process all Python files
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    if not should_ignore(relative_path, ignore_patterns):
                        success, message = fix_file(file_path, dry_run)
                        print(f"{file_path}: {message}")
                        if success and message != "No changes needed." and message != "File already has valid syntax.":
                            fixed_files.append(file_path)
                        elif not success:
                            failed_files.append(file_path)
                            all_passed = False

    # Print summary
    print("\n--- Summary ---")
    print(f"Fixed files: {len(fixed_files)}")
    if fixed_files:
        print("  " + "\n  ".join(fixed_files))

    print(f"Failed files: {len(failed_files)}")
    if failed_files:
        print("  " + "\n  ".join(failed_files))

    return all_passed


def main():
    """Main function to parse args and run the script."""
    parser = argparse.ArgumentParser(description="Fix common syntax errors in Python files.")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to a file or directory to fix (default: current directory)",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Specific file patterns to fix (e.g., '*.py' 'src/*.py')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't modify files, just show what would be fixed",
    )

    args = parser.parse_args()

    if os.path.isfile(args.path):
        # Fix a single file
        success, message = fix_file(args.path, args.dry_run)
        print(f"{args.path}: {message}")
        return 0 if success else 1
    else:
        # Fix a directory
        success = process_directory(args.path, args.files, args.dry_run)

        if args.dry_run:
            print("\nThis was a dry run. No files were modified.")

        if success:
            print("\n✅ All files processed successfully!")
            return 0
        else:
            print("\n❌ Some files could not be fixed automatically.")
            print("   You may need to fix these files manually.")
            return 1


if __name__ == "__main__":
    sys.exit(main())