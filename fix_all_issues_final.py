"""fix_all_issues_final - Module for fixing code quality issues.

This script provides a comprehensive solution for fixing various code quality issues,
including syntax errors, formatting issues, and linting problems. It can be run in
check-only mode to identify issues without fixing them, or in fix mode to automatically
fix the issues.
"""

# Standard library imports
import argparse
import os
import subprocess
import sys
from typing import List, Optional, Tuple

# Constants
DEFAULT_LINE_LENGTH = 88


def parse_arguments() -> argparse.Namespace:
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Fix code quality issues in Python files."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific files to fix. If not provided, all Python files will be processed.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for issues without fixing them.",
    )
    parser.add_argument(
        "--syntax-only",
        action="store_true",
        help="Fix only syntax errors.",
    )
    parser.add_argument(
        "--format-only",
        action="store_true",
        help="Fix only formatting issues.",
    )
    parser.add_argument(
        "--no-black",
        action="store_true",
        help="Skip Black formatting.",
    )
    parser.add_argument(
        "--no-isort",
        action="store_true",
        help="Skip isort import sorting.",
    )
    parser.add_argument(
        "--no-ruff",
        action="store_true",
        help="Skip Ruff linting.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    return parser.parse_args()


def find_python_files(specific_files: Optional[List[str]] = None) -> List[str]:
    """Find Python files to process.

    Args:
    ----
        specific_files: List of specific files to process. If None, all Python files will be found.

    Returns:
    -------
        List of Python file paths.

    """
    if specific_files:
        return [f for f in specific_files if f.endswith(".py") and os.path.isfile(f)]

    python_files = []
    ignore_dirs = {".git", ".venv", "venv", "__pycache__", "build", "dist"}

    for root, dirs, files in os.walk("."):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def run_command(command: List[str], check_mode: bool = False) -> Tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr.

    Args:
    ----
        command: Command to run as a list of strings.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
    -------
        Tuple of (exit_code, stdout, stderr).

    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as e:
        return 1, "", str(e)


def fix_line_length_issues(
    file_path: str, line_length: int = DEFAULT_LINE_LENGTH
) -> bool:
    """Fix line length issues in a Python file.

    Args:
    ----
        file_path: Path to the Python file.
        line_length: Maximum line length.

    Returns:
    -------
        True if successful, False otherwise.

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        modified = False
        for i, line in enumerate(lines):
            # Skip comments and docstrings for now
            if line.strip().startswith("#") or '"""' in line:
                continue

            # If line is too long, try to break it
            if len(line.rstrip()) > line_length:
                # Simple approach: if there's a comma, break after it
                if "," in line:
                    parts = line.split(",")
                    new_line = parts[0] + ",\n"
                    indent = len(line) - len(line.lstrip())
                    for part in parts[1:-1]:
                        new_line += " " * indent + part.lstrip() + ",\n"
                    new_line += " " * indent + parts[-1].lstrip()
                    lines[i] = new_line
                    modified = True

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

            return True

        return True  # No changes needed
    except Exception as e:
        print(f"Error fixing line length issues in {file_path}: {e}")
        return False


def fix_syntax_errors(file_path: str) -> bool:
    """Fix common syntax errors in a Python file.

    Args:
    ----
        file_path: Path to the Python file.

    Returns:
    -------
        True if successful, False otherwise.

    """
    try:
        # Try to compile the file to check for syntax errors
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            compile(content, file_path, "exec")
            return True  # No syntax errors
        except SyntaxError:
            # File has syntax errors, attempt to fix
            pass

        # Fix common syntax errors
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        modified = False

        # Remove duplicate lines
        i = 0
        while i < len(lines) - 1:
            if lines[i] == lines[i + 1]:
                lines.pop(i + 1)
                modified = True
            else:
                i += 1

        # Fix missing colons
        for i, line in enumerate(lines):
            # Check for class or function definitions without colons
            if (
                line.strip().startswith("class ") or line.strip().startswith("def ")
            ) and not line.strip().endswith(":"):
                lines[i] = line.rstrip() + ":\n"
                modified = True

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

        # Verify the fix worked
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            compile(content, file_path, "exec")
            return True
        except SyntaxError:
            return False
    except Exception as e:
        print(f"Error fixing syntax errors in {file_path}: {e}")
        return False


def run_black(file_path: str, check_mode: bool = False) -> bool:
    """Run Black formatter on a Python file.

    Args:
    ----
        file_path: Path to the Python file.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
    -------
        True if successful, False otherwise.

    """
    command = ["black"]
    if check_mode:
        command.append("--check")
    command.append(file_path)

    exit_code, stdout, stderr = run_command(command, check_mode)
    return exit_code == 0


def run_isort(file_path: str, check_mode: bool = False) -> bool:
    """Run isort on a Python file.

    Args:
    ----
        file_path: Path to the Python file.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
    -------
        True if successful, False otherwise.

    """
    command = ["isort"]
    if check_mode:
        command.append("--check")
    command.append(file_path)

    exit_code, stdout, stderr = run_command(command, check_mode)
    return exit_code == 0


def run_ruff(file_path: str, check_mode: bool = False) -> bool:
    """Run Ruff linter on a Python file.

    Args:
    ----
        file_path: Path to the Python file.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
    -------
        True if successful, False otherwise.

    """
    command = ["ruff", "check"]
    if not check_mode:
        command.append("--fix")
    command.append(file_path)

    exit_code, stdout, stderr = run_command(command, check_mode)

    # Also run ruff format
    format_command = ["ruff", "format"]
    if check_mode:
        format_command.append("--check")
    format_command.append(file_path)

    format_exit_code, format_stdout, format_stderr = run_command(
        format_command, check_mode
    )

    return exit_code == 0 and format_exit_code == 0


def fix_file(file_path: str, args: argparse.Namespace) -> bool:
    """Fix issues in a Python file.

    Args:
    ----
        file_path: Path to the Python file.
        args: Command-line arguments.

    Returns:
    -------
        True if successful, False otherwise.

    """
    if args.verbose:
        print(f"Processing {file_path}...")

    success = True

    # Fix syntax errors
    if not args.format_only:
        if args.verbose:
            print(f"  Fixing syntax errors in {file_path}...")
        if not fix_syntax_errors(file_path):
            print(f"Failed to fix syntax errors in {file_path}")
            success = False

    # Fix line length issues
    if not args.syntax_only:
        if args.verbose:
            print(f"  Fixing line length issues in {file_path}...")
        if not fix_line_length_issues(file_path):
            print(f"Failed to fix line length issues in {file_path}")
            success = False

    # Run external tools
    if not args.syntax_only:
        # Run Black
        if not args.no_black:
            if args.verbose:
                print(f"  Running Black on {file_path}...")
            if not run_black(file_path, args.check):
                print(f"Black failed on {file_path}")
                success = False

        # Run isort
        if not args.no_isort:
            if args.verbose:
                print(f"  Running isort on {file_path}...")
            if not run_isort(file_path, args.check):
                print(f"isort failed on {file_path}")
                success = False

        # Run Ruff
        if not args.no_ruff:
            if args.verbose:
                print(f"  Running Ruff on {file_path}...")
            if not run_ruff(file_path, args.check):
                print(f"Ruff failed on {file_path}")
                success = False

    return success


def main() -> int:
    """Run the main program to fix code quality issues."""
    args = parse_arguments()

    # Find Python files to process
    python_files = find_python_files(args.files)

    if not python_files:
        print("No Python files found to process.")
        return 0

    print(f"Processing {len(python_files)} Python files...")

    # Process each file
    success_count = 0
    for file_path in python_files:
        if fix_file(file_path, args):
            success_count += 1

    # Print summary
    print(f"Successfully processed {success_count} out of {len(python_files)} files.")

    return 0 if success_count == len(python_files) else 1


if __name__ == "__main__":
    sys.exit(main())
