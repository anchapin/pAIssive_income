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

# Local imports
from common_utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

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
        specific_files: List of specific files to process. If None,
        all Python files will be found.

    Returns:
    -------
        List of Python file paths.

    Raises:
    ------
        ValueError: If specific_files contains non-Python files
        FileNotFoundError: If a specific file doesn't exist
        PermissionError: If access to a file or directory is denied

    """
    # Normalize ignore patterns once for better performance
    ignore_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
    }
    ignore_files = {"fix_all_issues_final.py"}  # Avoid self-modification

    if specific_files:
        normalized_files = []
        for file_path in specific_files:
            if not file_path.endswith(".py"):
                raise ValueError(f"Not a Python file: {file_path}")

            norm_path = os.path.normpath(file_path)
            if not os.path.isfile(norm_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            if not os.access(norm_path, os.R_OK):
                raise PermissionError(f"Permission denied: {file_path}")

            normalized_files.append(norm_path)
        return normalized_files

    python_files: List[str] = []
    processed_dirs = 0
    error_files: List[Tuple[str, str]] = []

    for root, dirs, files in os.walk("."):
        try:
            # Skip ignored directories
            norm_root = os.path.normpath(root)

            # Only process directories we have access to
            if not os.access(norm_root, os.R_OK | os.X_OK):
                logger.warning(f"Permission denied for directory: {norm_root}")
                continue

            # Filter ignored directories in-place
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for file in files:
                if file.endswith(".py") and file not in ignore_files:
                    try:
                        file_path = os.path.normpath(os.path.join(root, file))

                        # Verify file access
                        if not os.access(file_path, os.R_OK):
                            error_files.append((file_path, "Permission denied"))
                            continue

                        python_files.append(file_path)

                        if len(python_files) <= 5:
                            logger.debug(f"Found Python file: {file_path}")

                    except OSError as e:
                        error_files.append((file, str(e)))

            processed_dirs += 1
            if processed_dirs % 10 == 0:
                logger.debug(
                    f"Directory scan progress - Processed: {processed_dirs}, "
                    f"Files found: {len(python_files)}"
                )

        except OSError as e:
            logger.error(f"Error accessing directory {root}: {e}")

    if error_files:
        logger.warning(
            f"Found {len(error_files)} files with access issues. "
            "See debug log for details."
        )
        for file_path, error in error_files:
            logger.debug(f"File access error - {file_path}: {error}")

    logger.info(f"Total Python files found: {len(python_files)}")
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
        # Check if the command exists before running it
        if command and command[0] in ["black", "isort", "ruff"]:
            try:
                # Use shell=True on Windows to find commands in PATH
                shell = sys.platform == "win32"

                # For Windows, use where command to check if tool exists
                if shell:
                    check_cmd = ["where", command[0]]
                else:
                    check_cmd = ["which", command[0]]

                result = subprocess.run(
                    check_cmd,
                    capture_output=True,
                    text=True,
                    shell=shell,
                )

                if result.returncode != 0:
                    logger.warning(f"Command not found: {command[0]}")
                    return 0, "", f"Command '{command[0]}' not found. Skipped."

            except (subprocess.SubprocessError, FileNotFoundError) as e:
                logger.warning(f"Command check failed: {command[0]} - {e}")
                return 0, "", f"Command '{command[0]}' not found. Skipped."

        # Use shell=True on Windows to find commands in PATH
        shell = sys.platform == "win32"

        # Log command for debugging
        cmd_str = " ".join(command)
        logger.debug(f"Running command: {cmd_str}")

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
            logger.error(f"subprocess.run failed: {run_error}, falling back to Popen")
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
        logger.error(
            "Error running command",
            extra={"command": " ".join(command), "error": str(e)},
        )
        import traceback

        logger.debug(traceback.format_exc())
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
        logger.error(
            "Error fixing line length issues",
            extra={"file": file_path, "error": str(e)},
        )
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
        logger.error(
            "Error fixing syntax errors",
            extra={"file": file_path, "error": str(e)},
        )
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
    logger.info(f"Processing file: {file_path}")
    success = True

    # Fix syntax errors
    if not args.format_only:
        if args.verbose:
            logger.debug(f"Fixing syntax errors in {file_path}")
        if not fix_syntax_errors(file_path):
            logger.error(f"Failed to fix syntax errors in {file_path}")
            success = False

    # Fix line length issues
    if not args.syntax_only:
        if args.verbose:
            logger.debug(f"Fixing line length issues in {file_path}")
        if not fix_line_length_issues(file_path):
            logger.error(f"Failed to fix line length issues in {file_path}")
            success = False

    # Run external tools
    if not args.syntax_only:
        # Run Black
        if not args.no_black:
            if args.verbose:
                logger.debug(f"Running Black on {file_path}")
            if not run_black(file_path, args.check):
                logger.error(f"Black failed on {file_path}")
                success = False

        # Run isort
        if not args.no_isort:
            if args.verbose:
                logger.debug(f"Running isort on {file_path}")
            if not run_isort(file_path, args.check):
                logger.error(f"isort failed on {file_path}")
                success = False

        # Run Ruff
        if not args.no_ruff:
            if args.verbose:
                logger.debug(f"Running Ruff on {file_path}")
            if not run_ruff(file_path, args.check):
                logger.error(f"Ruff failed on {file_path}")
                success = False

    return success


def main() -> int:
    """Run the main program to fix code quality issues."""
    try:
        logger.info("Running fix_all_issues_final.py")
        logger.debug(f"Platform: {sys.platform}")
        logger.debug(f"Python version: {sys.version}")
        logger.debug(f"Current working directory: {os.getcwd()}")

        args = parse_arguments()
        logger.debug(f"Arguments: {args}")

        # Find Python files to process
        logger.info("Finding Python files to process...")
        python_files = find_python_files(args.files)

        if not python_files:
            logger.info("No Python files found to process.")
            return 0

        logger.info(f"Processing {len(python_files)} Python files...")

        # If specific files were provided, show them
        if args.files:
            logger.debug("Specific files requested:", extra={"files": args.files})
            logger.debug("Actual files found:", extra={"files": python_files})

        # Check if required tools are installed
        tools_to_check = []
        if not args.syntax_only and not args.no_black:
            tools_to_check.append("black")
        if not args.syntax_only and not args.no_isort:
            tools_to_check.append("isort")
        if not args.syntax_only and not args.no_ruff:
            tools_to_check.append("ruff")

        logger.info(f"Checking for required tools: {tools_to_check}")
        missing_tools = []

        for tool in tools_to_check:
            try:
                shell = sys.platform == "win32"
                # For Windows, use where command to check if tool exists
                if shell:
                    check_cmd = ["where", tool]
                else:
                    check_cmd = ["which", tool]

                result = subprocess.run(
                    check_cmd,
                    capture_output=True,
                    text=True,
                    shell=shell,
                )

                if result.returncode == 0:
                    logger.info(f"Tool {tool} found: {result.stdout.strip()}")
                else:
                    logger.warning(f"Tool {tool} not found in PATH")
                    missing_tools.append(tool)
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                logger.error(f"Tool check failed: {tool} - {e}")
                missing_tools.append(tool)

        if missing_tools and not args.syntax_only:
            logger.warning(
                "Missing required tools",
                extra={"tools": missing_tools},
            )
            logger.info("Continuing with available tools only...")

        # Process each file
        success_count = 0
        failed_files = []
        syntax_error_files = []
        format_error_files = []
        tool_error_files = []

        for i, file_path in enumerate(python_files):
            logger.info(
                f"Processing file {i + 1} of {len(python_files)}",
                extra={"file": file_path, "progress": f"{i + 1}/{len(python_files)}"},
            )
            try:
                if fix_file(file_path, args):
                    success_count += 1
                    logger.info(f"Successfully processed: {file_path}")
                else:
                    failed_files.append(file_path)
                    logger.error(f"Failed to process: {file_path}")
            except Exception as e:
                logger.error(
                    "Error processing file",
                    extra={"file": file_path, "error": str(e)},
                )
                import traceback

                logger.debug(traceback.format_exc())
                failed_files.append(file_path)

        # Log summary
        logger.info("=" * 50)
        logger.info("SUMMARY")
        logger.info("=" * 50)
        logger.info(
            "Processing complete",
            extra={
                "success_count": success_count,
                "total_files": len(python_files),
                "failed_files": len(failed_files),
            },
        )

        if failed_files:
            # Try to categorize failures
            for file_path in failed_files:
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                    try:
                        compile(content, file_path, "exec")
                    except SyntaxError:
                        syntax_error_files.append(file_path)
                        continue

                    # If we get here, it's not a syntax error
                    if args.syntax_only:
                        format_error_files.append(file_path)
                    else:
                        tool_error_files.append(file_path)
                except Exception:
                    # If we can't even read the file, count it as a syntax error
                    syntax_error_files.append(file_path)

            if syntax_error_files:
                logger.error(
                    "Files with syntax errors",
                    extra={"files": syntax_error_files},
                )

            if format_error_files:
                logger.error(
                    "Files with formatting errors",
                    extra={"files": format_error_files},
                )

            if tool_error_files:
                logger.error(
                    "Files with tool errors",
                    extra={"files": tool_error_files},
                )

        return 0 if success_count == len(python_files) else 1
    except Exception as e:
        logger.error("Error in main function", extra={"error": str(e)})
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
