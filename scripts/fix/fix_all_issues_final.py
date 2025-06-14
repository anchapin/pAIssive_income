"""
fix_all_issues_final - Module for fixing code quality issues.

This script provides a comprehensive solution for fixing various code quality issues,
including syntax errors, formatting issues, and linting problems. It can be run in
check-only mode to identify issues without fixing them, or in fix mode to automatically
fix the issues.
"""

# Standard library imports
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import Callable, Optional

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
        "--no-ruff-format",
        action="store_true",
        help="Skip Ruff formatting.",
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


def _should_ignore_path(
    path: str, ignore_dirs: set[str], ignore_files: set[str]
) -> bool:
    """Check if a path should be ignored based on the ignore sets."""
    # Convert path to use forward slashes for consistency
    path = path.replace("\\", "/")

    # Check if the path is an ignored directory
    if os.path.isdir(path):
        dir_name = os.path.basename(path)
        if dir_name in ignore_dirs:
            return True

    # Check if the path is an ignored file
    if os.path.isfile(path):
        file_name = os.path.basename(path)
        if file_name in ignore_files:
            return True

    # Check if the path is within an ignored directory
    path_parts = path.split("/")
    return any(part in ignore_dirs for part in path_parts)


def _process_directory(
    root: str,
    dirs: list[str],
    files: list[str],
    ignore_dirs: set[str],
    ignore_files: set[str],
    error_files: list[tuple[str, str]],
) -> list[str]:
    """Process a single directory during the os.walk."""
    python_files_in_dir = []

    # Only process directories we have access to
    norm_root = os.path.normpath(root)
    if not os.access(norm_root, os.R_OK | os.X_OK):
        logger.warning(f"Permission denied for directory: {norm_root}")
        return []

    # Filter out ignored directories in-place
    dirs[:] = [
        d
        for d in dirs
        if not _should_ignore_path(os.path.join(root, d), ignore_dirs, ignore_files)
    ]

    for file in files:
        file_path = os.path.normpath(os.path.join(root, file))
        # Check if the file should be ignored
        if not _should_ignore_path(file_path, ignore_dirs, ignore_files):
            try:
                # Verify file access
                if not os.access(file_path, os.R_OK):
                    error_files.append((file_path, "Permission denied"))
                    continue

                python_files_in_dir.append(file_path)

                # Define a constant for the early logging threshold
                max_early_log_files = 5
                if (
                    len(python_files_in_dir) <= max_early_log_files
                ):  # Keep this check for early logging
                    logger.debug(f"Found Python file: {file_path}")

            except OSError as e:
                error_files.append((file, str(e)))

    return python_files_in_dir


def _validate_specific_files(specific_files: list[str]) -> list[str]:
    """
    Validate and normalize specific files provided by the user.

    Args:
        specific_files: List of specific files to process

    Returns:
        List of normalized file paths

    Raises:
        FileNotPythonError: If a file is not a Python file
        MissingFileError: If a file doesn't exist
        FilePermissionError: If access to a file is denied

    """
    normalized_files = []
    for file_path in specific_files:
        if not file_path.endswith(".py"):
            from common_utils.exceptions import FileNotPythonError

            raise FileNotPythonError(file_path)

        norm_path = os.path.normpath(file_path)
        if not os.path.isfile(norm_path):
            from common_utils.exceptions import MissingFileError

            raise MissingFileError(file_path)

        if not os.access(norm_path, os.R_OK):
            from common_utils.exceptions import FilePermissionError

            raise FilePermissionError(file_path)

        normalized_files.append(norm_path)
    return normalized_files


def _scan_directories_for_python_files() -> list[str]:
    """
    Scan directories recursively to find Python files.

    Returns:
        List of Python file paths

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

    python_files: list[str] = []
    processed_dirs = 0
    error_files: list[tuple[str, str]] = []

    for root, dirs, files in os.walk("."):
        try:
            python_files_in_dir = _process_directory(
                root, dirs, files, ignore_dirs, ignore_files, error_files
            )
            python_files.extend(python_files_in_dir)

            processed_dirs += 1
            if processed_dirs % 10 == 0:
                logger.debug(
                    f"Directory scan progress - Processed: {processed_dirs}, "
                    f"Files found: {len(python_files)}"
                )

        except OSError:
            logger.exception("Error accessing directory %s", root)

    _log_file_errors(error_files)

    logger.info("Total Python files found: %d", len(python_files))
    return python_files


def _log_file_errors(error_files: list[tuple[str, str]]) -> None:
    """
    Log file access errors.

    Args:
        error_files: List of tuples containing file path and error message

    """
    if error_files:
        logger.warning(
            f"Found {len(error_files)} files with access issues. "
            "See debug log for details."
        )
        for file_path, error in error_files:
            logger.debug(f"File access error - {file_path}: {error}")


def find_python_files(specific_files: Optional[list[str]] = None) -> list[str]:
    """
    Find Python files to process.

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
    if specific_files:
        return _validate_specific_files(specific_files)

    return _scan_directories_for_python_files()


def run_command(command: list[str]) -> tuple[int, str, str]:
    """
    Run a command and return the exit code, stdout, and stderr.

    Args:
    ----
        command: Command to run as a list of strings.

    Returns:
    -------
        Tuple of (exit_code, stdout, stderr).

    """
    try:
        # Check if the command exists before running it
        if command and command[0] in ["ruff"]:  # Removed "black" and "isort"
            try:
                # Use shutil.which to find commands in PATH safely
                import shutil

                cmd_path = shutil.which(command[0])
                if cmd_path is None:
                    logger.warning(f"Command not found: {command[0]}")
                    return 0, "", f"Command '{command[0]}' not found. Skipped."

            except (subprocess.SubprocessError, FileNotFoundError):
                logger.exception("Tool check failed: %s", command[0])
                return 0, "", f"Command '{command[0]}' not found. Skipped."

        # Always use shell=False for security

        # Log command for debugging
        cmd_str = " ".join(command)
        logger.debug(f"Running command: {cmd_str}")

        try:
            # Try using subprocess.run first (more reliable)
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=False,  # Always use shell=False for security
                check=False,  # Don't raise exception on non-zero exit
            )
        except Exception:
            logger.exception("subprocess.run failed, falling back to Popen")
            # Fall back to Popen if run fails
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,  # Always use shell=False for security
            )
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr
        else:
            return result.returncode, result.stdout, result.stderr
    except Exception as e:
        logger.exception(
            "Error running command",
            extra={"command": " ".join(command), "error": str(e)},
        )
        import traceback

        logger.debug(traceback.format_exc())
        return 1, "", str(e)


def fix_line_length_issues(
    file_path: str, line_length: int = DEFAULT_LINE_LENGTH
) -> bool:
    """
    Fix line length issues in a Python file.

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

            # If line is too long and has a comma, try to break it
            if len(line.rstrip()) > line_length and "," in line:
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
        logger.exception(
            "Error fixing line length issues",
            extra={"file": file_path, "error": str(e)},
        )
        return False


def _check_for_syntax_errors(file_path: str) -> bool:
    """
    Check if a file has syntax errors.

    Args:
        file_path: Path to the Python file

    Returns:
        True if the file has no syntax errors, False otherwise

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        try:
            compile(content, file_path, "exec")
        except SyntaxError:
            return False
        else:
            return True
    except Exception as e:
        logger.exception(
            "Error checking for syntax errors",
            extra={"file": file_path, "error": str(e)},
        )
        return False


def _remove_duplicate_lines(lines: list[str]) -> tuple[list[str], bool]:
    """
    Remove duplicate adjacent lines.

    Args:
        lines: List of lines from the file

    Returns:
        Tuple of (modified lines, whether modifications were made)

    """
    modified = False
    result_lines = lines.copy()

    i = 0
    while i < len(result_lines) - 1:
        if result_lines[i] == result_lines[i + 1]:
            result_lines.pop(i + 1)
            modified = True
        else:
            i += 1

    return result_lines, modified


def _fix_missing_colons(lines: list[str]) -> tuple[list[str], bool]:
    """
    Fix missing colons in class and function definitions.

    Args:
        lines: List of lines from the file

    Returns:
        Tuple of (modified lines, whether modifications were made)

    """
    modified = False
    result_lines = lines.copy()

    for i, line in enumerate(result_lines):
        # Check for class or function definitions without colons
        if (
            line.strip().startswith("class ") or line.strip().startswith("def ")
        ) and not line.strip().endswith(":"):
            result_lines[i] = line.rstrip() + ":\n"
            modified = True

    return result_lines, modified


def _write_modified_file(file_path: str, lines: list[str]) -> bool:
    """
    Write modified lines back to the file.

    Args:
        file_path: Path to the Python file
        lines: List of lines to write

    Returns:
        True if successful, False otherwise

    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
            return True
    except Exception as e:
        logger.exception(
            "Error writing modified file",
            extra={"file": file_path, "error": str(e)},
        )
        return False


def fix_syntax_errors(file_path: str) -> bool:
    """
    Fix common syntax errors in a Python file.

    Args:
    ----
        file_path: Path to the Python file.

    Returns:
    -------
        True if successful, False otherwise.

    """
    try:
        # Check if the file already has correct syntax
        if _check_for_syntax_errors(file_path):
            return True  # No syntax errors

        # Read the file
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            logger.exception(
                "Error reading file",
                extra={"file": file_path, "error": str(e)},
            )
            return False

        # Apply fixes
        modified = False

        # Remove duplicate lines
        lines, dup_modified = _remove_duplicate_lines(lines)
        modified = modified or dup_modified

        # Fix missing colons
        lines, colon_modified = _fix_missing_colons(lines)
        modified = modified or colon_modified

        # Write changes if needed
        if modified and not _write_modified_file(file_path, lines):
            return False

        # Verify the fix worked
        return _check_for_syntax_errors(file_path)

    except Exception as e:
        logger.exception(
            "Error fixing syntax errors",
            extra={"file": file_path, "error": str(e)},
        )
        return False


def run_ruff_format(file_path: str, check_mode: bool = False) -> bool:
    """
    Run Ruff formatter on a Python file.

    Args:
    ----
        file_path: Path to the Python file.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
    -------
        True if successful, False otherwise.

    """
    command = ["ruff", "format"]
    if check_mode:
        command.append("--check")
    command.append(file_path)

    exit_code, stdout, stderr = run_command(command)
    return exit_code == 0


def run_ruff(file_path: str, check_mode: bool = False) -> bool:
    """
    Run Ruff linter on a Python file.

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

    exit_code, stdout, stderr = run_command(command)

    # Also run ruff format
    format_command = ["ruff", "format"]
    if check_mode:
        format_command.append("--check")
    format_command.append(file_path)

    format_exit_code, format_stdout, format_stderr = run_command(format_command)

    return exit_code == 0 and format_exit_code == 0


def _fix_syntax_issues(file_path: str, args: argparse.Namespace) -> bool:
    """
    Fix syntax issues in a Python file.

    Args:
        file_path: Path to the Python file
        args: Command-line arguments

    Returns:
        True if successful, False otherwise

    """
    if args.format_only:
        return True

    if args.verbose:
        logger.debug(f"Fixing syntax errors in {file_path}")

    if not fix_syntax_errors(file_path):
        logger.error(f"Failed to fix syntax errors in {file_path}")
        return False

    return True


def _fix_formatting_issues(file_path: str, args: argparse.Namespace) -> bool:
    """
    Fix formatting issues in a Python file.

    Args:
        file_path: Path to the Python file
        args: Command-line arguments

    Returns:
        True if successful, False otherwise

    """
    if args.syntax_only:
        return True

    if args.verbose:
        logger.debug(f"Fixing line length issues in {file_path}")

    if not fix_line_length_issues(file_path):
        logger.error(f"Failed to fix line length issues in {file_path}")
        return False

    return True


def _run_single_formatter(
    file_path: str,
    formatter_name: str,
    formatter_func: Callable[[str, bool], bool],
    check_mode: bool,
    verbose: bool,
) -> bool:
    """
    Run a single formatter on a Python file.

    Args:
        file_path: Path to the Python file
        formatter_name: Name of the formatter
        formatter_func: Function to run the formatter
        check_mode: Whether to run in check mode
        verbose: Whether to log verbose output

    Returns:
        True if successful, False otherwise

    """
    if verbose:
        logger.debug(f"Running {formatter_name} on {file_path}")

    if not formatter_func(file_path, check_mode):
        logger.error(f"{formatter_name} failed on {file_path}")
        return False

    return True


def _run_external_formatters(file_path: str, args: argparse.Namespace) -> bool:
    """
    Run external formatting tools on a Python file.

    Args:
        file_path: Path to the Python file
        args: Command-line arguments

    Returns:
        True if successful, False otherwise

    """
    if args.syntax_only:
        return True

    formatters = []

    # Define which formatters to run
    if not args.no_ruff_format:  # Changed from no_black
        formatters.append(("Ruff Format", run_ruff_format))  # Changed from Black

    if not args.no_ruff:
        formatters.append(("Ruff", run_ruff))

    # Run all formatters
    success = True
    for formatter_name, formatter_func in formatters:
        if not _run_single_formatter(
            file_path, formatter_name, formatter_func, args.check, args.verbose
        ):
            success = False

    return success


def fix_file(file_path: str, args: argparse.Namespace) -> bool:
    """
    Fix issues in a Python file.

    Args:
    ----
        file_path: Path to the Python file.
        args: Command-line arguments.

    Returns:
    -------
        True if successful, False otherwise.

    """
    logger.info("Processing file: %s", file_path)

    # Step 1: Fix syntax issues
    syntax_success = _fix_syntax_issues(file_path, args)

    # Step 2: Fix formatting issues
    formatting_success = _fix_formatting_issues(file_path, args)

    # Step 3: Run external formatters
    external_success = _run_external_formatters(file_path, args)

    # Return overall success
    return syntax_success and formatting_success and external_success


def _log_environment_info() -> None:
    """Log information about the environment."""
    logger.info("Running fix_all_issues_final.py")
    logger.debug(f"Platform: {sys.platform}")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Current working directory: {os.getcwd()}")


def _get_required_tools(args: argparse.Namespace) -> list[str]:
    """
    Get the list of required external tools based on arguments.

    Args:
        args: Command-line arguments

    Returns:
        List of required tool names

    """
    tools_to_check = []
    if not args.syntax_only:
        if not args.no_ruff_format:  # Changed from no_black
            tools_to_check.append("ruff")  # Ruff handles formatting
        if not args.no_ruff:
            tools_to_check.append("ruff")
    return tools_to_check


def _check_tool_availability(tool: str) -> bool:
    """
    Check if a tool is available in the PATH.

    Args:
        tool: Name of the tool to check

    Returns:
        True if the tool is available, False otherwise

    """
    try:
        shell = sys.platform == "win32"
        # For Windows, use where command to check if tool exists
        check_cmd = ["where", tool] if shell else ["which", tool]

        result = subprocess.run(
            check_cmd,
            capture_output=True,
            text=True,
            shell=shell,
            check=False,
        )

        if result.returncode == 0:
            logger.info("Tool %s found: %s", tool, result.stdout.strip())
            return True
        logger.warning(f"Tool {tool} not found in PATH")
        return False
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.exception("Tool check failed: %s", tool)
        return False


def _verify_tool_availability(args: argparse.Namespace) -> list[str]:
    """
    Verify that required tools are available.

    Args:
        args: Command-line arguments

    Returns:
        List of missing tools

    """
    tools_to_check = _get_required_tools(args)

    if not tools_to_check:
        return []

    logger.info("Checking for required tools: %s", tools_to_check)
    missing_tools = []

    for tool in tools_to_check:
        if not _check_tool_availability(tool):
            missing_tools.append(tool)

    if missing_tools and not args.syntax_only:
        logger.warning(
            "Missing required tools",
            extra={"tools": missing_tools},
        )
        logger.info("Continuing with available tools only...")

    return missing_tools


def _process_files(
    python_files: list[str], args: argparse.Namespace
) -> tuple[int, list[str]]:
    """
    Process Python files to fix issues.

    Args:
        python_files: List of Python files to process
        args: Command-line arguments

    Returns:
        Tuple of (success count, list of failed files)

    """
    success_count = 0
    failed_files = []

    for i, file_path in enumerate(python_files):
        logger.info(
            f"Processing file {i + 1} of {len(python_files)}",
            extra={"file": file_path, "progress": f"{i + 1}/{len(python_files)}"},
        )
        try:
            if fix_file(file_path, args):
                success_count += 1
                logger.info("Successfully processed: %s", file_path)
            else:
                failed_files.append(file_path)
                logger.error(f"Failed to process: {file_path}")
        except Exception:
            logger.exception(
                "Error processing file",
                extra={"file": file_path},
            )
            import traceback

            logger.debug(traceback.format_exc())
            failed_files.append(file_path)

    return success_count, failed_files


def _categorize_failures(
    failed_files: list[str], args: argparse.Namespace
) -> tuple[list[str], list[str], list[str]]:
    """
    Categorize failed files by error type.

    Args:
        failed_files: List of files that failed processing
        args: Command-line arguments

    Returns:
        Tuple of (syntax error files, format error files, tool error files)

    """
    syntax_error_files = []
    format_error_files = []
    tool_error_files = []

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
        except (OSError, UnicodeDecodeError):
            # If we can't even read the file, count it as a syntax error
            syntax_error_files.append(file_path)

    return syntax_error_files, format_error_files, tool_error_files


def _log_summary(
    success_count: int,
    total_files: int,
    syntax_error_files: list[str],
    format_error_files: list[str],
    tool_error_files: list[str],
) -> None:
    """
    Log a summary of the processing results.

    Args:
        success_count: Number of successfully processed files
        total_files: Total number of files processed
        syntax_error_files: List of files with syntax errors
        format_error_files: List of files with formatting errors
        tool_error_files: List of files with tool errors

    """
    logger.info("=" * 50)
    logger.info("SUMMARY")
    logger.info("=" * 50)
    logger.info(
        "Processing complete",
        extra={
            "success_count": success_count,
            "total_files": total_files,
            "failed_files": total_files - success_count,
        },
    )

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


def main() -> int:
    """Run the main program to fix code quality issues."""
    try:
        # Step 1: Log environment information
        _log_environment_info()

        # Step 2: Parse arguments
        args = parse_arguments()
        logger.debug("Arguments: %s", args)

        # Step 3: Find Python files to process
        logger.info("Finding Python files to process...")
        python_files = find_python_files(args.files)

        if not python_files:
            logger.info("No Python files found to process.")
            return 0

        logger.info("Processing %d Python files...", len(python_files))

        # If specific files were provided, show them
        if args.files:
            logger.debug("Specific files requested:", extra={"files": args.files})
            logger.debug("Actual files found:", extra={"files": python_files})

        # Step 4: Verify tool availability
        _verify_tool_availability(args)

        # Step 5: Process files
        success_count, failed_files = _process_files(python_files, args)

        # Step 6: Categorize failures
        syntax_error_files, format_error_files, tool_error_files = _categorize_failures(
            failed_files, args
        )

        # Step 7: Log summary
        _log_summary(
            success_count,
            len(python_files),
            syntax_error_files,
            format_error_files,
            tool_error_files,
        )

        return 0 if success_count == len(python_files) else 1

    except Exception:
        logger.exception("Error in main function")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
