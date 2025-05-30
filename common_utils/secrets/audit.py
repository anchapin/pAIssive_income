"""
audit - Module for common_utils/secrets.audit.

This module provides utilities for auditing code for hardcoded secrets.
"""

# Standard library imports
from __future__ import annotations

import base64
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, cast

# Third-party imports
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Local imports
from common_utils.logging.secure_logging import get_secure_logger, mask_sensitive_data

# Initialize secure logger
logger = get_secure_logger(__name__)

# Constants and configurations
PATTERNS = {
    "credential_type_1": re.compile(
        (
            r'(api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?'
            r'([a-zA-Z0-9_\-\.]{10,})["\']?'
        ),
        re.IGNORECASE,
    ),
    "auth_credential": re.compile(
        (r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']?' r'([^"\'\s]{3,})["\']?'),
        re.IGNORECASE,
    ),
    "access_credential": re.compile(
        (
            r'(token|access_token|refresh_token|jwt)["\']?\s*[:=]\s*["\']?'
            r'([a-zA-Z0-9_\-\.]{10,})["\']?'
        ),
        re.IGNORECASE,
    ),
    "sensitive_credential": re.compile(
        (
            r'(secret|private_key)["\']?\s*[:=]\s*["\']?'
            r'([a-zA-Z0-9_\-\.]{10,})["\']?'
        ),
        re.IGNORECASE,
    ),
}

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

TEXT_FILE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".json",
    ".yml",
    ".yaml",
    ".md",
    ".txt",
    ".html",
    ".css",
    ".scss",
    ".sh",
    ".bat",
    ".ps1",
    ".env",
    ".ini",
    ".cfg",
    ".conf",
    ".xml",
}


def is_text_file(file_path: str) -> bool:
    """
    Check if a file is a text file.

    Args:
    ----
        file_path: Path to the file

    Returns:
    -------
        bool: True if the file is a text file, False otherwise

    """
    path = Path(file_path)
    if path.suffix.lower() in TEXT_FILE_EXTENSIONS:
        return True

    try:
        with Path(file_path).open(encoding="utf-8", errors="ignore") as f:
            sample = f.read(1024)
            return "\x00" not in sample
    except (OSError, UnicodeError) as e:
        logger.debug("Error checking if file is text: %s", e)
        return False


def is_example_code(content: str, line: str) -> bool:
    """
    Check if a line is part of example code.

    Args:
    ----
        content: The full content of the file
        line: The line to check

    Returns:
    -------
        bool: True if the line is part of example code, False otherwise

    """
    example_indicators = [
        "example",
        "sample",
        "demo",
        "test",
        "mock",
        "dummy",
        "placeholder",
        "todo",
        "fixme",
    ]

    line_lower = line.lower()
    for indicator in example_indicators:
        if indicator in line_lower:
            return True

    return ('"""' in content or "'''" in content) and line.startswith("    ")


def should_exclude(file_path: str, exclude_dirs: Optional[set[str]] = None) -> bool:
    """
    Check if a file should be excluded from scanning.

    Args:
    ----
        file_path: Path to the file
        exclude_dirs: Directories to exclude

    Returns:
    -------
        bool: True if the file should be excluded, False otherwise

    """
    if exclude_dirs is None:
        exclude_dirs = DEFAULT_EXCLUDE_DIRS

    path = Path(file_path).resolve()
    path_parts = path.parts

    return any(part in exclude_dirs for part in path_parts)


def _validate_file_access(file_path: str) -> None:
    """
    Validate that a file exists and is readable.

    Args:
        file_path: Path to the file

    Raises:
        MissingFileError: If file not found
        FilePermissionError: If insufficient permissions

    """
    path = Path(file_path)
    if not path.exists():
        from common_utils.exceptions import MissingFileError

        raise MissingFileError(file_path)

    if not os.access(file_path, os.R_OK):
        from common_utils.exceptions import FilePermissionError

        raise FilePermissionError(file_path)


def _read_file_content(file_path: str) -> tuple[str, list[str]]:
    """
    Read file content with appropriate error handling.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (file content, lines)

    Raises:
        UnicodeError: If file cannot be decoded even with replacement

    """
    path = Path(file_path)
    try:
        with path.open(encoding="utf-8", errors="strict") as f:
            content = f.read()
            lines = content.splitlines()
            return content, lines
    except UnicodeError as e:
        logger.exception(
            "UTF-8 decoding error", extra={"file": file_path, "error": str(e)}
        )
        # Try again with replacement characters
        with path.open(encoding="utf-8", errors="replace") as f:
            content = f.read()
            lines = content.splitlines()
            logger.warning(
                "File processed with replacement characters",
                extra={"file": file_path},
            )
            return content, lines


def _process_pattern_matches(
    pattern_name: str, pattern: re.Pattern, line: str, line_number: int, file_path: str
) -> list[tuple[str, int, str, str]]:
    """
    Process matches for a specific pattern in a line.

    Args:
        pattern_name: Name of the pattern
        pattern: Compiled regex pattern
        line: Line to check
        line_number: Line number (1-based)
        file_path: Path to the file

    Returns:
        List of (pattern_name, line_number, line, secret_value) tuples

    """
    results: list[tuple[str, int, str, str]] = []

    try:
        matches = pattern.findall(line)
    except Exception as e:
        logger.exception(
            "Regex pattern error",
            extra={
                "file": file_path,
                "line": line_number,
                "pattern": pattern_name,
                "error": type(e).__name__,
            },
        )
        return results

    if not matches:
        return results

    # Process all matches outside the loop to avoid try-except inside loop
    for match in matches:
        if isinstance(match, tuple) and len(match) > 1:
            secret_value = match[1]
        else:
            secret_value = match
        results.append((pattern_name, line_number, line, secret_value))

    return results


def find_potential_secrets(
    file_path: str,
) -> list[tuple[str, int, str, str]]:
    """
    Find potential secrets in a file.

    Args:
    ----
        file_path: Path to the file

    Returns:
    -------
        list[tuple[str, int, str, str]]: List of pattern name, line number, line, value

    Raises:
    ------
        FileNotFoundError: If file not found
        PermissionError: If insufficient permissions
        UnicodeError: If file cannot be decoded

    """
    # Step 1: Validate file access
    _validate_file_access(file_path)

    # Step 2: Read file content
    content, lines = _read_file_content(file_path)

    # Step 3: Process each line for potential secrets
    results = []

    for i, line in enumerate(lines):
        # Skip example code
        if is_example_code(content, line):
            continue

        # Check each pattern
        for pattern_name, pattern in PATTERNS.items():
            line_results = _process_pattern_matches(
                pattern_name,
                pattern,
                line,
                i + 1,  # Convert to 1-based line number
                file_path,
            )
            results.extend(line_results)

    return results


def process_file(
    file_path: str, exclude_dirs: Optional[set[str]] = None
) -> list[tuple[str, int, str, str]]:
    """
    Process a single file for potential secrets.

    Args:
    ----
        file_path: Path to the file to process
        exclude_dirs: Directories to exclude

    Returns:
    -------
        list[tuple[str, int, str, str]]: List of secrets found

    """
    if should_exclude(file_path, exclude_dirs) or not is_text_file(file_path):
        return []

    return find_potential_secrets(file_path)


def handle_file_error(file_path: str, error: Exception) -> dict[str, str]:
    """
    Handle file processing errors uniformly.

    Args:
    ----
        file_path: Path to the file that caused the error
        error: The exception that occurred

    Returns:
    -------
        dict[str, str]: Error details dictionary

    """
    return {
        "file": file_path,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "error_type": type(error).__name__,
        "error_id": str(uuid.uuid4()),
    }


def scan_directory(
    directory: str, exclude_dirs: Optional[set[str]] = None
) -> dict[str, list[tuple[str, int, str, str]]]:
    """
    Scan a directory recursively for potential secrets.

    Args:
    ----
        directory: Directory to scan
        exclude_dirs: Directories to exclude

    Returns:
    -------
        dict[str,
        list[tuple[str,
        int,
        str,
        str]]]: Mapping of file paths to secrets found

    Raises:
    ------
        FileNotFoundError: If directory not found
        PermissionError: If insufficient permissions

    """
    dir_path = Path(directory)
    if not dir_path.exists():
        from common_utils.exceptions import DirectoryNotFoundError

        raise DirectoryNotFoundError(directory)

    if not os.access(directory, os.R_OK | os.X_OK):
        from common_utils.exceptions import DirectoryPermissionError

        raise DirectoryPermissionError

    exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    results: dict[str, list[tuple[str, int, str, str]]] = {}
    scanned_files = 0
    error_files: list[dict[str, str]] = []

    try:
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                file_path = str(Path(root) / file)

                try:
                    secrets = process_file(file_path, exclude_dirs)
                    if secrets:
                        results[file_path] = secrets

                    scanned_files += 1
                    if scanned_files % 100 == 0:
                        logger.info(
                            "Scan progress",
                            extra={
                                "files_scanned": scanned_files,
                                "files_with_secrets": len(results),
                                "current_directory": root,
                            },
                        )

                except (PermissionError, FileNotFoundError) as e:
                    error_details = handle_file_error(file_path, e)
                    error_files.append(error_details)
                    logger.warning(
                        "File access error",
                        extra={"file": file_path, "error": str(e), **error_details},
                    )
                except Exception as e:
                    error_details = handle_file_error(file_path, e)
                    error_files.append(error_details)
                    logger.exception(
                        "Unexpected error processing file",
                        extra={
                            "file": file_path,
                            "error": str(e),
                            "stack_trace": True,
                            **error_details,
                        },
                    )

        log_scan_completion(scanned_files, error_files, results)

    except (PermissionError, OSError) as e:
        logger.exception(
            "Directory traversal error",
            extra={
                "directory": directory,
                "error": str(e),
                "error_type": type(e).__name__,
                "stack_trace": True,
            },
        )
        raise

    return results


def log_scan_completion(
    scanned_files: int,
    error_files: list[dict[str, str]],
    results: dict[str, list[tuple[str, int, str, str]]],
) -> None:
    """
    Log scan completion status with appropriate metrics.

    Args:
    ----
        scanned_files: Number of files scanned
        error_files: List of files that had errors
        results: Dictionary of files with secrets found

    """
    if error_files:
        logger.warning(
            "Scan completed with errors",
            extra={
                "total_files": scanned_files,
                "error_files": len(error_files),
                "files_with_secrets": len(results),
                "error_types": {e["error_type"] for e in error_files},
            },
        )
    else:
        logger.info(
            "Scan completed successfully",
            extra={
                "total_files": scanned_files,
                "files_with_secrets": len(results),
                "clean_files": scanned_files - len(results),
            },
        )


def generate_json_report(results: dict[str, list[tuple[str, int, str, str]]]) -> str:
    """
    Generate a JSON format report.

    Args:
    ----
        results: Dictionary of file paths to secrets

    Returns:
    -------
        str: JSON formatted report with masked sensitive data

    """
    json_results = {}
    for file_path, secrets in results.items():
        masked_file_path = mask_sensitive_data(file_path)
        json_results[masked_file_path] = [
            {
                "type": pattern_name,
                "line_number": line_number,
                "line": mask_sensitive_data(line),
                "value": "[REDACTED]",
            }
            for pattern_name, line_number, line, _ in secrets
        ]

    masked_json = json.dumps(json_results, indent=2)
    return cast("str", mask_sensitive_data(masked_json))


def generate_text_report(results: dict[str, list[tuple[str, int, str, str]]]) -> str:
    """
    Generate a text format report.

    Args:
    ----
        results: Dictionary of file paths to secrets

    Returns:
    -------
        str: Text formatted report with masked sensitive data

    """
    lines = [
        "Security Scan Report",
        "===================",
        "",
        "Scan completed successfully",
        "",
    ]

    for file_path, secrets in results.items():
        masked_file_path = mask_sensitive_data(file_path)
        lines.append(f"File: {masked_file_path}")
        lines.append("-" * (len(str(masked_file_path)) + 6))

        for pattern_name, line_number, line, _ in secrets:
            masked_line = mask_sensitive_data(line)
            if not isinstance(masked_line, str):
                masked_line = str(masked_line)
            masked_line = mask_sensitive_data(masked_line, visible_chars=2)
            if not isinstance(masked_line, str):
                masked_line = str(masked_line)
            lines.append(f"  Line {line_number}: {pattern_name}")
            lines.append(f"    {masked_line.strip()}")
            lines.append("")
        lines.append("")

    output = mask_sensitive_data("\n".join(lines))
    return cast("str", mask_sensitive_data(output, visible_chars=2))


def encrypt_report_content(content: str) -> tuple[bytes, bytes]:
    """
    Encrypt report content using environment key or system entropy.

    Args:
    ----
        content: Content to encrypt

    Returns:
    -------
        tuple[bytes, bytes]: Salt and encrypted content

    """
    salt = os.urandom(16)
    system_entropy = f"{uuid.getnode()}{Path.home()}{os.getpid()}"

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )

    key_material = os.environ.get("PAISSIVE_REPORT_KEY", "").encode(
        "utf-8"
    ) or system_entropy.encode("utf-8")

    try:
        derived_key = kdf.derive(key_material)
        encoded_key = base64.urlsafe_b64encode(derived_key)
        fernet = Fernet(encoded_key)
        return salt, fernet.encrypt(content.encode())
    finally:
        # Clean up sensitive data
        del key_material
        if "derived_key" in locals():
            del derived_key
        if "encoded_key" in locals():
            del encoded_key


def save_encrypted_report(path: str, salt: bytes, encrypted_content: bytes) -> None:
    """
    Save encrypted report to file.

    Args:
    ----
        path: Output file path
        salt: Salt used for encryption
        encrypted_content: Encrypted report content

    """
    output_path = Path(path)
    if output_path.parent != Path():
        output_path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)

    with output_path.open("wb") as f:
        f.write(salt + encrypted_content)


def generate_report(
    results: dict[str, list[tuple[str, int, str, str]]],
    output_file: Optional[str] = None,
    json_format: bool = False,
) -> None:
    """
    Generate a report of potential secrets.

    Args:
    ----
        results: Dictionary of file paths to secrets
        output_file: Path to the output file
        json_format: Whether to output in JSON format

    """
    if not results:
        logger.info("No potential security findings")
        return

    # Don't log the actual number of secrets as it might reveal sensitive information about the codebase
    logger.info(
        "Completed security scan",
        extra={"scan_completed": True},
    )

    output = (
        generate_json_report(results) if json_format else generate_text_report(results)
    )

    if output_file:
        try:
            # Apply additional security measures
            secure_output = mask_sensitive_data(output, visible_chars=1)
            secure_output = mask_sensitive_data(secure_output, visible_chars=0)

            # Remove any remaining sensitive patterns
            for pattern in PATTERNS.values():
                if isinstance(secure_output, str):
                    secure_output = pattern.sub(r"\1[REDACTED]", secure_output)

            # Encrypt and save the report
            salt, encrypted_content = encrypt_report_content(str(secure_output))
            save_encrypted_report(output_file, salt, encrypted_content)

            logger.info(
                "Report saved successfully",
                extra={"output_file": mask_sensitive_data(output_file)},
            )
        except Exception as e:
            # Mask any potential sensitive data in error message
            masked_error = mask_sensitive_data(str(e))
            logger.exception("Error saving report", extra={"error": masked_error})
    else:
        # Don't log the full report, just that it was generated
        logger.info("Security scan report generated")


class SecretsAuditor:
    """Utility for auditing code for hardcoded secrets."""

    def __init__(
        self, exclude_dirs: Optional[set[str]] = None, patterns: Optional[dict] = None
    ) -> None:
        """
        Initialize the secrets auditor.

        Args:
        ----
            exclude_dirs: Directories to exclude
            patterns: Patterns to use for detecting secrets

        """
        self.exclude_dirs: set[str] = exclude_dirs or DEFAULT_EXCLUDE_DIRS
        self.patterns: dict = patterns or PATTERNS
        logger.info("Secrets auditor initialized")

    def scan(self, directory: str) -> dict[str, list[tuple[str, int, str, str]]]:
        """
        Scan a directory for potential secrets.

        Args:
            directory: Directory to scan

        Returns:
            Dictionary mapping file paths to lists of (pattern_name,
            line_number,
            line_content,
            secret_value)

        """
        return scan_directory(directory, self.exclude_dirs)

    def generate_report(
        self,
        results: dict[str, list[tuple[str, int, str, str]]],
        output_file: Optional[str] = None,
        json_format: bool = False,
    ) -> dict[str, list[tuple[str, int, str, str]]]:
        """
        Audit a directory for potential secrets and generate a report.

        Args:
            results: Dictionary mapping file paths to lists of (pattern_name,
            line_number,
            line_content,
            secret_value)
            output_file: Optional output file path
            json_format: Whether to output in JSON format

        Returns:
            Dictionary mapping file paths to lists of (pattern_name,
            line_number,
            line_content,
            secret_value)

        """
        generate_report(results, output_file, json_format)
        return results

    def audit(
        self,
        directory: str,
        output_file: Optional[str] = None,
        format: str = "text",
        json_format: bool = None,  # For backward compatibility
    ) -> dict[str, list[tuple[str, int, str, str]]]:
        """
        Audit a directory for potential secrets and generate a report.

        Args:
            directory: Directory to scan
            output_file: Path to the output file
            format: Output format ("json" or "text")
            json_format: Deprecated - Whether to output in JSON format

        Returns:
            Dictionary mapping file paths to lists of (pattern_name,
            line_number,
            line_content,
            secret_value)

        """
        results = self.scan(directory)

        # Handle backward compatibility with json_format parameter
        use_json = False
        if json_format is not None:
            use_json = json_format
        elif format.lower() == "json":
            use_json = True

        self.generate_report(results, output_file, use_json)
        return results
