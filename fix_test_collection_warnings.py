#!/usr/bin/env python
"""
Script to fix common syntax errors that cause test collection failures.
This script automatically fixes:
    1. Missing colons after class definitions
    2. Missing parentheses in function definitions
    3. Incomplete import statements with trailing commas
    4. Basic indentation issues
"""


import argparse
import ast
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Set




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


def find_syntax_error(file_path: str) -> Optional[SyntaxError]:
    """Check Python file for syntax errors and return the exception if found."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            source = file.read()
        ast.parse(source, filename=file_path)
        return None
    except SyntaxError as e:
        return e
    except Exception:
        return None


def fix_missing_colon(content: str, error_line: int) -> str:
    """Fix missing colons after class definitions."""
    lines = content.splitlines()
    if error_line <= 0 or error_line > len(lines):
        return content

    # Check if this is a class definition missing a colon
    line = lines[error_line - 1]
    class_match = re.match(r"^(\s*class\s+\w+(?:\(.*\))?)$", line)
    if class_match:
        lines[error_line - 1] = class_match.group(1) + ":"
        return "\n".join(lines)

    return content


def fix_missing_parentheses(content: str, error_line: int) -> str:
    """Fix missing parentheses in function definitions."""
    lines = content.splitlines()
    if error_line <= 0 or error_line > len(lines):
        return content

    # Check if this is a function definition missing parentheses
    line = lines[error_line - 1]
    func_match = re.match(r"^(\s*def\s+\w+)$", line)
    if func_match:
        lines[error_line - 1] = func_match.group(1) + "():"
        return "\n".join(lines)

    return content


def fix_incomplete_import(content: str, error_line: int) -> str:
    """Fix incomplete import statements."""
    lines = content.splitlines()
    if error_line <= 0 or error_line > len(lines):
        return content

    # Check if this is an incomplete import statement
    line = lines[error_line - 1]
    if line.endswith("import"):
        # If the import statement ends with "import", add a placeholder
        lines[error_line - 1] = line + " # Incomplete import needs specific modules"
        return "\n".join(lines)

    # Check for trailing comma in import
    if "import" in line and line.strip().endswith(","):
        lines[error_line - 1] = line.rstrip(",") + " # Fixed trailing comma"
        return "\n".join(lines)

    return content


def fix_indentation(content: str, error_line: int) -> str:
    """Fix basic indentation issues."""
    lines = content.splitlines()
    if error_line <= 0 or error_line > len(lines):
        return content

    # Check if this has indentation issues
    line = lines[error_line - 1]
    if "IndentationError" in str(find_syntax_error(content)):
        # Try to determine correct indentation from context
        if error_line > 1:
            prev_line = lines[error_line - 2]
            if prev_line.rstrip().endswith(":"):
                # The previous line ends with a colon, so this line should be indented
                current_indent = len(line) - len(line.lstrip())
                if current_indent == 0:
                    # No indent when expected
                    lines[error_line - 1] = "    " + line
                else:
                    # Try removing the indent to see if that helps
                    lines[error_line - 1] = line.lstrip()
            elif "def " in prev_line or "class " in prev_line:
                # Previous line is likely a function or class definition
                lines[error_line - 1] = "    " + line.lstrip()

    return "\n".join(lines)


def fix_syntax_errors(file_path: str) -> bool:
    """Try to automatically fix common syntax errors in a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            original_content = file.read()

        modified_content = original_content
        fixed = False

        while True:
            error = find_syntax_error(file_path)
            if not error:
                break

            # Try various fixes based on the error message
            if "expected ':'" in str(error):
                modified_content = fix_missing_colon(modified_content, error.lineno)
            elif "expected '('" in str(error):
                modified_content = fix_missing_parentheses(
                    modified_content, error.lineno
                )
            elif (
                "invalid syntax" in str(error)
                and "import" in modified_content.splitlines()[error.lineno - 1]
            ):
                modified_content = fix_incomplete_import(modified_content, error.lineno)
            elif "IndentationError" in str(error):
                modified_content = fix_indentation(modified_content, error.lineno)
            else:
                # Add a comment indicating a syntax error we couldn't fix
                lines = modified_content.splitlines()
                if error.lineno <= len(lines):
                    lines[error.lineno - 1] += "  # FIXME: Syntax error"
                modified_content = "\n".join(lines)

            # Write the modified content back to the file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(modified_content)

            # Check if we've made any changes
            if modified_content != original_content:
                fixed = True
                # If we've made changes but still have errors, continue the loop
                continue
            else:
                # If we couldn't make any more changes, break the loop
                print(f"❌ Could not fix all syntax errors in {file_path}")
                print(f"   Remaining error: {error}")
                return False

        if fixed:
            print(f"✅ Fixed syntax errors in {file_path}")
            return True

        return True

    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return False


def process_directory(directory: str, file_patterns: List[str] = None) -> bool:
    """Process all Python files in a directory and its subdirectories."""
    all_passed = True
    ignore_patterns = get_gitignore_patterns()

    if file_patterns:
        # Process specific files/patterns
        for pattern in file_patterns:
            for file_path in Path(directory).glob(pattern):
                if file_path.is_file() and file_path.suffix == ".py":
                    relative_path = str(file_path.relative_to(directory))
                    if not should_ignore(relative_path, ignore_patterns):
                        if not fix_syntax_errors(str(file_path)):
                            all_passed = False
    else:
        # Process all Python files
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    if not should_ignore(relative_path, ignore_patterns):
                        if not fix_syntax_errors(file_path):
                            all_passed = False

    return all_passed


def check_syntax_errors(file_path: str) -> bool:
    """Check if a Python file has syntax errors without fixing them."""
    try:
        error = find_syntax_error(file_path)
        if error:
            print(f"❌ Syntax error in {file_path} at line {error.lineno}: {error}")
            return False
        return True
    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return False


def check_directory(directory: str, file_patterns: List[str] = None) -> bool:
    """Check all Python files in a directory and its subdirectories for syntax errors."""
    all_passed = True
    ignore_patterns = get_gitignore_patterns()

    if file_patterns:
        # Process specific files/patterns
        for pattern in file_patterns:
            for file_path in Path(directory).glob(pattern):
                if file_path.is_file() and file_path.suffix == ".py":
                    relative_path = str(file_path.relative_to(directory))
                    if not should_ignore(relative_path, ignore_patterns):
                        if not check_syntax_errors(str(file_path)):
                            all_passed = False
    else:
        # Process all Python files
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    if not should_ignore(relative_path, ignore_patterns):
                        if not check_syntax_errors(file_path):
                            all_passed = False

    return all_passed


def main():
    """Main function to parse args and run the script."""
    parser = argparse.ArgumentParser(
        description="Fix common syntax errors in Python files that cause test collection failures."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to a file or directory to process (default: current directory)",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Specific file patterns to process (e.g., '*.py' 'src/*.py')",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check for syntax errors without fixing them",
    )

    args = parser.parse_args()

    print("🔍 Scanning for Python files with syntax errors...")

    if args.check:
        # Check mode - only report errors without fixing
        if os.path.isfile(args.path):
            # Check a single file
            success = check_syntax_errors(args.path)
        else:
            # Check a directory
            success = check_directory(args.path, args.files)

        if success:
            print("\n✅ No syntax errors found!")
            return 0
        else:
            print(
                "\n❌ Syntax errors found. Please fix them manually or run without --check."
            )
            return 1
    else:
        # Fix mode - attempt to fix errors
        if os.path.isfile(args.path):
            # Process a single file
            success = fix_syntax_errors(args.path)
        else:
            # Process a directory
            success = process_directory(args.path, args.files)

        if success:
            print("\n✅ All fixable syntax errors have been corrected!")
            return 0
        else:
            print("\n⚠️ Some files still have syntax errors that need manual fixing.")
            return 1


if __name__ == "__main__":
    sys.exit(main())
