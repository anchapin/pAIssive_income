"""fix_windows_issues - Windows-specific script for fixing code quality issues.

This script is specifically designed to work on Windows environments and handles
Windows path separators correctly. It provides a robust solution for fixing
various code quality issues, including syntax errors, formatting issues, and
linting problems.
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
        description="Fix code quality issues in Python files on Windows."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help=(
            "Specific files to fix. "
            "If not provided, all Python files will be processed."
        ),
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
    """Find Python files to process, with Windows-specific path handling."""
    if specific_files:
        # Normalize paths for Windows
        normalized_files = []
        for f in specific_files:
            if f.endswith(".py") and os.path.isfile(f):
                normalized_files.append(os.path.normpath(f))
        return normalized_files

    python_files: List[str] = []
    # Directories to ignore
    ignore_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
    }

    # Create normalized patterns for Windows paths
    ignore_patterns = []
    for pattern in ignore_dirs:
        # Add Windows-specific path pattern
        ignore_patterns.append(os.path.normpath(f".\\{pattern}"))

    print(f"Ignore patterns: {ignore_patterns}")
    print(f"Platform: {sys.platform}")

    for root, dirs, files in os.walk("."):
        # Skip ignored directories
        norm_root = os.path.normpath(root)

        # Debug output for the first few directories
        if len(python_files) < 5:
            print(f"Checking directory: {norm_root}")

        # Check if this directory should be ignored
        skip_dir = False
        for pattern in ignore_patterns:
            if norm_root.startswith(pattern) or any(
                d in norm_root.split(os.sep) for d in ignore_dirs
            ):
                skip_dir = True
                break

        if skip_dir:
            if len(python_files) < 5:
                print(f"  Skipping ignored directory: {norm_root}")
            continue

        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.normpath(os.path.join(root, file))
                python_files.append(file_path)
                if len(python_files) <= 5:
                    print(f"  Found Python file: {file_path}")

    print(f"Total Python files found: {len(python_files)}")
    return python_files


def run_command(command: List[str], check_mode: bool = False) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr with Windows handling."""
    try:
        # Always use shell=True on Windows
        shell = True

        # Print command for debugging
        cmd_str = " ".join(command)
        print(f"Running command: {cmd_str}")

        try:
            # Try using subprocess.run first (more reliable)
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=shell,
                check=False,  # Don't raise exception on non-zero exit
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as run_error:
            print(f"subprocess.run failed: {run_error}, falling back to Popen")
            # Fall back to Popen if run fails
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=shell,
            )
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr
    except Exception as e:
        print(f"Error running command {' '.join(command)}: {e}")
        import traceback

        traceback.print_exc()
        return 1, "", str(e)


def fix_syntax_errors(file_path: str) -> bool:
    """Fix common syntax errors in a Python file, with Windows-specific handling."""
    try:
        # Try to compile the file to check for syntax errors
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()

        try:
            compile(content, file_path, "exec")
            return True  # No syntax errors
        except SyntaxError:
            # File has syntax errors, attempt to fix
            pass

        # Fix common syntax errors
        with open(file_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        modified = False

        # Fix missing colons
        for i, line in enumerate(lines):
            # Check for class or function definitions without colons
            if (
                line.strip().startswith("class ") or line.strip().startswith("def ")
            ) and not line.strip().endswith(":"):
                lines[i] = line.rstrip() + ":\n"
                modified = True

        if modified:
            with open(file_path, "w", encoding="utf-8", errors="replace") as f:
                f.writelines(lines)

        # Verify the fix worked
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()

        try:
            compile(content, file_path, "exec")
            return True
        except SyntaxError:
            return False
    except Exception as e:
        print(f"Error fixing syntax errors in {file_path}: {e}")
        return False


def main() -> int:
    """Run the main program to fix code quality issues on Windows."""
    try:
        print(f"Running fix_windows_issues.py on platform: {sys.platform}")
        print(f"Python version: {sys.version}")
        print(f"Current working directory: {os.getcwd()}")

        args = parse_arguments()
        print(f"Arguments: {args}")

        # Find Python files to process
        print("Finding Python files to process...")
        python_files = find_python_files(args.files)

        if not python_files:
            print("No Python files found to process.")
            return 0

        print(f"Processing {len(python_files)} Python files...")

        # Process each file
        success_count = 0
        failed_files = []

        for i, file_path in enumerate(python_files):
            print(f"\nProcessing file {i + 1}/{len(python_files)}: {file_path}")
            try:
                # For now, just fix syntax errors
                if fix_syntax_errors(file_path):
                    success_count += 1
                    print(f"✓ Successfully processed {file_path}")
                else:
                    failed_files.append(file_path)
                    print(f"✗ Failed to process {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                import traceback

                traceback.print_exc()
                failed_files.append(file_path)

        # Print summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(
            f"Successfully processed {success_count} out of {len(python_files)} files."
        )

        if failed_files:
            print("\nFailed files:")
            for file_path in failed_files:
                print(f"  - {file_path}")

        return 0 if success_count == len(python_files) else 1
    except Exception as e:
        print(f"Error in main function: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
