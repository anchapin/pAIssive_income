#!/usr/bin/env python3
"""
Test script for security scanning workflow.

This script simulates the security scanning workflow locally to verify that
the changes made to the workflow file work as expected.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shlex
import stat
import subprocess  # nosec B404 - subprocess is used with proper security controls
import sys
from pathlib import Path
from shutil import which
from typing import Optional

logger = logging.getLogger(__name__)

# Define constants for improved maintainability and security
SECURE_FILE_PERMISSIONS = stat.S_IRUSR | stat.S_IWUSR  # 600 permissions
ALLOWED_TOOLS = {"safety", "bandit", "python", "uv", "gzip"}
REPORT_FILE_EXTENSIONS = {".json", ".sarif", ".gz"}
REPORTS_DIR = "security-reports"
COMPRESSED_DIR = "security-reports/compressed"


def validate_executable(executable: str) -> str | None:
    """
    Validate that an executable exists, is allowed, and resolve its full path.

    Args:
        executable: Name of the executable to validate

    Returns:
        str | None: Full path to executable if valid and allowed, None otherwise

    """
    if executable not in ALLOWED_TOOLS:
        logger.error("Executable %s is not in the allowed tools list", executable)
        return None

    exe_path = which(executable)
    if not exe_path:
        logger.error("Executable %s not found", executable)
        return None

    return exe_path


def secure_path(path: str) -> bool:
    """
    Check if a path is safe and set secure permissions.

    Args:
        path: Path to secure

    Returns:
        bool: True if path is safe, False otherwise

    """
    # Convert to Path object for easier manipulation
    p = Path(path)

    # Validate path
    suffix = p.suffix.lower()
    if suffix not in REPORT_FILE_EXTENSIONS:
        logger.error("Invalid file extension: %s", suffix)
        return False

    try:
        # Set secure permissions - owner read/write only
        os.chmod(path, SECURE_FILE_PERMISSIONS)
    except OSError:
        logger.exception("Failed to set secure permissions on %s", path)
        return False
    else:
        return True


def run_command(command: str, cwd: Optional[str] = None) -> tuple[str, str, int]:
    """
    Run a shell command and return stdout, stderr, and return code.

    Args:
        command: Command to run, must not contain untrusted input
        cwd: Working directory

    Returns:
        Tuple of (stdout, stderr, return_code)

    """
    try:
        # Split the command into args for safer execution
        args = shlex.split(command)

        if len(args) == 0:
            return "", "Empty command", 1

        # Validate the executable exists and is allowed
        executable = args[0]
        exe_path = validate_executable(executable)
        if not exe_path:
            return "", f"Command {executable} is not allowed or not found", 1

        args[0] = exe_path

        # Create a clean environment
        env = os.environ.copy()
        # Remove potentially dangerous environment variables
        for key in list(env.keys()):
            if key.startswith(("LD_", "PYTHON")):
                del env[key]

        # Use subprocess.run instead of Popen for simpler code
        # nosec B603 - subprocess call is used with shell=False and validated input
        result = subprocess.run(
            args,
            shell=False,  # Avoid shell=True for security
            capture_output=True,
            cwd=cwd,
            text=True,
            check=False,
            env=env,  # Use cleaned environment
        )
        stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
    except (subprocess.SubprocessError, OSError) as e:
        stdout, stderr, returncode = "", str(e), 1

    return stdout, stderr, returncode


def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists with secure permissions.

    Args:
        directory: Directory path

    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    # Set secure directory permissions - owner read/write/execute only
    os.chmod(path, SECURE_FILE_PERMISSIONS | stat.S_IXUSR)


def cleanup_sensitive_files(pattern: str) -> None:
    """
    Safely cleanup temporary sensitive files.

    Args:
        pattern: File pattern to match for cleanup

    """
    try:
        for file in Path(REPORTS_DIR).glob(pattern):
            if file.is_file() and file.suffix in REPORT_FILE_EXTENSIONS:
                file.unlink()
    except (OSError, PermissionError):
        logger.exception("Error cleaning up files matching %s", pattern)


def write_secure_file(path: str, content: str) -> bool:
    """
    Write content to a file with secure permissions.

    Args:
        path: File path to write to
        content: Content to write

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        # Create file with restricted permissions
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        mode = stat.S_IRUSR | stat.S_IWUSR  # 600 permissions
        with os.fdopen(os.open(path, flags, mode), "w") as f:
            f.write(content)

        # Double check permissions are set
        return secure_path(path)
    except OSError:
        logger.exception("Error writing to file %s", path)
        return False


def test_safety_scan() -> bool:
    """
    Test the Safety scan functionality.

    Returns:
        bool: True if successful, False otherwise

    """
    logger.info("\n=== Testing Safety Scan ===")
    ensure_directory(REPORTS_DIR)

    # Clean up any previous results
    cleanup_sensitive_files("safety-*.json*")

    # Create fallback safety results file with secure permissions
    if not write_secure_file(f"{REPORTS_DIR}/safety-results.json", "[]"):
        return False

    # Run safety check
    logger.info("Running safety check...")
    stdout, stderr, return_code = run_command("safety check --json")

    if return_code != 0 and "command not found" in stderr:
        logger.info("Safety not installed. Installing...")
        # Use uv for safe package installation
        install_result = run_command("uv pip install safety")
        if install_result[2] != 0:
            logger.error("Failed to install safety: %s", install_result[1])
            return False
        stdout, stderr, return_code = run_command("safety check --json")

    if stdout:
        tmp_path = f"{REPORTS_DIR}/safety-results.json.tmp"
        final_path = f"{REPORTS_DIR}/safety-results.json"

        # Write output to temporary file with secure permissions
        if not write_secure_file(tmp_path, stdout):
            return False

        # Validate JSON format
        try:
            json.loads(stdout)
            logger.info("Safety output is valid JSON")
            # Move temporary file to final location
            Path(tmp_path).rename(final_path)
            secure_path(final_path)  # Ensure secure permissions after move
        except json.JSONDecodeError:
            logger.warning("Safety output is not valid JSON. Using empty results.")
            logger.exception("Invalid JSON content")
            # Log only first bit of output to avoid sensitive data
            if stdout:
                logger.debug("Output preview: %.100s...", stdout)
            cleanup_sensitive_files("safety-*.json.tmp")
    else:
        logger.warning("Safety check produced no output")
        if stderr:
            logger.error("Safety error log: %s", stderr[:100])  # Limit error output

    # Convert to SARIF format
    logger.info("Converting Safety results to SARIF format...")
    sarif_cmd = (
        f"python sarif_utils.py {REPORTS_DIR}/safety-results.json "
        f"{REPORTS_DIR}/safety-results.sarif Safety "
        "https://pyup.io/safety/"
    )
    stdout, stderr, return_code = run_command(sarif_cmd)

    if return_code != 0:
        logger.error("Error converting Safety results to SARIF: %.100s", stderr)
        return False

    # Set secure permissions on SARIF file
    secure_path(f"{REPORTS_DIR}/safety-results.sarif")
    logger.info("Safety scan test completed")
    return True


def test_bandit_scan() -> bool:
    """
    Test the Bandit scan functionality.

    Returns:
        bool: True if successful, False otherwise

    """
    logger.info("\n=== Testing Bandit Scan ===")
    ensure_directory(REPORTS_DIR)

    # Clean up any previous results
    cleanup_sensitive_files("bandit-*.json*")

    # Create fallback bandit results file with secure permissions
    if not write_secure_file(f"{REPORTS_DIR}/bandit-results.json", "[]"):
        return False

    # Run bandit scan
    logger.info("Running bandit scan...")
    stdout, stderr, return_code = run_command("bandit -r . -f json")

    if return_code != 0 and "command not found" in stderr:
        logger.info("Bandit not installed. Installing...")
        install_result = run_command("uv pip install bandit")
        if install_result[2] != 0:
            logger.error("Failed to install bandit: %s", install_result[1])
            return False
        stdout, stderr, return_code = run_command("bandit -r . -f json")

    if stdout:
        tmp_path = f"{REPORTS_DIR}/bandit-results.json.tmp"
        final_path = f"{REPORTS_DIR}/bandit-results.json"

        # Write output to temporary file with secure permissions
        if not write_secure_file(tmp_path, stdout):
            return False

        # Validate JSON format
        try:
            json.loads(stdout)
            logger.info("Bandit output is valid JSON")
            # Move temporary file to final location
            Path(tmp_path).rename(final_path)
            secure_path(final_path)  # Ensure secure permissions after move
        except json.JSONDecodeError:
            logger.warning("Bandit output is not valid JSON. Using empty results.")
            logger.warning("Invalid JSON content:")
            logger.warning("%.100s", stdout[:100])  # Show first 100 characters
            cleanup_sensitive_files("bandit-*.json.tmp")
    else:
        logger.warning("Bandit scan produced no output")
        if stderr:
            logger.warning(
                "Bandit error log: %.100s", stderr[:100]
            )  # Limit error output

    # Convert to SARIF format
    logger.info("Converting Bandit results to SARIF format...")
    sarif_cmd = (
        f"python sarif_utils.py {REPORTS_DIR}/bandit-results.json "
        f"{REPORTS_DIR}/bandit-results.sarif Bandit "
        "https://bandit.readthedocs.io/"
    )
    stdout, stderr, return_code = run_command(sarif_cmd)

    if return_code != 0:
        logger.error("Error converting Bandit results to SARIF: %.100s", stderr)
        return False

    # Set secure permissions on SARIF file
    secure_path(f"{REPORTS_DIR}/bandit-results.sarif")
    logger.info("Bandit scan test completed")
    return True


def test_sarif_file_handling() -> bool:
    """
    Test SARIF file handling functionality.

    Returns:
        bool: True if successful, False otherwise

    """
    logger.info("\n=== Testing SARIF File Handling ===")
    ensure_directory(REPORTS_DIR)
    ensure_directory(COMPRESSED_DIR)

    # Clean up any previous compressed files
    cleanup_sensitive_files("compressed/*.gz")

    # Check if SARIF files exist
    sarif_files = list(Path(REPORTS_DIR).glob("*.sarif"))
    if not sarif_files:
        logger.info("No SARIF files found. Creating a test SARIF file...")

        # Create a test SARIF file with secure permissions
        test_cmd = (
            f'python sarif_utils.py "[]" {REPORTS_DIR}/test-results.sarif '
            "Test https://example.com"
        )
        stdout, stderr, return_code = run_command(test_cmd)

        if return_code != 0:
            logger.error("Error creating test SARIF file: %.100s", stderr)
            return False

        # Ensure test file has secure permissions
        secure_path(f"{REPORTS_DIR}/test-results.sarif")
        sarif_files = list(Path(REPORTS_DIR).glob("*.sarif"))

    # Process SARIF files
    for sarif_file in sarif_files:
        logger.info(
            "Processing %s...", sarif_file.name
        )  # Log only filename for security

        # Verify file has secure permissions
        if not secure_path(str(sarif_file)):
            logger.error("Insecure file permissions on %s", sarif_file.name)
            continue

        # Check file size
        file_size = sarif_file.stat().st_size
        logger.info("File size: %s bytes", file_size)

        # Validate SARIF format
        try:
            with open(sarif_file, encoding="utf-8") as f:
                json.load(f)
            logger.info("✅ %s is valid JSON", sarif_file.name)
        except json.JSONDecodeError:
            logger.warning("❌ %s is not valid JSON", sarif_file.name)
            logger.info("Creating a valid but empty SARIF file as fallback")

            # Create fallback SARIF file
            cmd = f'python sarif_utils.py "[]" {sarif_file} Test https://example.com'
            stdout, stderr, return_code = run_command(cmd)

            if return_code != 0:
                logger.exception("Error creating fallback SARIF file: %.100s", stderr)
                return False

            # Set secure permissions on new file
            secure_path(str(sarif_file))

        # Create compressed version with secure permissions
        compressed_file = Path(COMPRESSED_DIR) / f"{sarif_file.name}.gz"
        gzip_cmd = f"gzip -c {sarif_file} > {compressed_file}"
        stdout, stderr, return_code = run_command(gzip_cmd)

        if return_code != 0:
            logger.error("Error creating compressed version: %.100s", stderr)
            return False

        # Set secure permissions on compressed file
        secure_path(str(compressed_file))
        logger.info("Created compressed version: %s", compressed_file.name)

    logger.info("SARIF file handling test completed")
    return True


def main() -> int:
    """
    Run security scan tests.

    Returns:
        int: Exit code

    """
    # Set up logging with secure format (no sensitive data)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message).100s",  # Limit message length
    )

    parser = argparse.ArgumentParser(description="Test security scanning workflow")
    parser.add_argument("--safety", action="store_true", help="Test Safety scan")
    parser.add_argument("--bandit", action="store_true", help="Test Bandit scan")
    parser.add_argument("--sarif", action="store_true", help="Test SARIF file handling")
    parser.add_argument("--all", action="store_true", help="Test all components")
    parser.add_argument(
        "--cleanup", action="store_true", help="Clean up test files after running"
    )

    args = parser.parse_args()

    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return 1

    success = True

    try:
        # Run tests
        if args.all or args.safety:
            success = test_safety_scan() and success

        if args.all or args.bandit:
            success = test_bandit_scan() and success

        if args.all or args.sarif:
            success = test_sarif_file_handling() and success

        if success:
            logger.info("\n✅ All tests completed successfully")
        else:
            logger.warning("\n❌ Some tests failed")

    except KeyboardInterrupt:
        logger.info("\nTests interrupted by user")
        success = False

    except Exception as e:
        logger.exception("\nUnexpected error during tests: %s", type(e).__name__)
        success = False

    finally:
        # Clean up if requested
        if args.cleanup:
            logger.info("Cleaning up test files...")
            try:
                cleanup_sensitive_files("*.json*")
                cleanup_sensitive_files("*.sarif*")
                cleanup_sensitive_files("compressed/*.gz")
            except Exception:
                logger.exception("Error during cleanup")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
