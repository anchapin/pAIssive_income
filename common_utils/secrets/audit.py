"""audit - Module for common_utils/secrets.audit.

This module provides utilities for auditing code for hardcoded secrets.
"""

# Standard library imports
import json
import os
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

# Third-party imports
# Local imports
from common_utils.logging.secure_logging import get_secure_logger, mask_sensitive_data

# Initialize secure logger
logger = get_secure_logger(__name__)

# Constants and configurations
PATTERNS = {
    "api_key": re.compile(
        (
            r'(api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?'
            r'([a-zA-Z0-9_\-\.]{10,})["\']?'
        ),
        re.IGNORECASE,
    ),
    "password": re.compile(
        (r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']?' r'([^"\'\s]{3,})["\']?'),
        re.IGNORECASE,
    ),
    "token": re.compile(
        (
            r'(token|access_token|refresh_token|jwt)["\']?\s*[:=]\s*["\']?'
            r'([a-zA-Z0-9_\-\.]{10,})["\']?'
        ),
        re.IGNORECASE,
    ),
    "secret": re.compile(
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
    """Check if a file is a text file.

    Args:
    ----
        file_path: Path to the file

    Returns:
    -------
        bool: True if the file is a text file, False otherwise

    """
    _, ext = os.path.splitext(file_path.lower())
    if ext in TEXT_FILE_EXTENSIONS:
        return True

    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            sample = f.read(1024)
            if "\0" in sample:
                return False
            return True
    except Exception:
        return False


def is_example_code(content: str, line: str) -> bool:
    """Check if a line is part of example code.

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

    if '"""' in content or "'''" in content:
        if line.startswith("    "):
            return True

    return False


def should_exclude(file_path: str, exclude_dirs: Optional[Set[str]] = None) -> bool:
    """Check if a file should be excluded from scanning.

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

    file_path = os.path.normpath(file_path)
    path_parts = file_path.split(os.sep)

    for part in path_parts:
        if part in exclude_dirs:
            return True

    return False


def find_potential_secrets(
    file_path: str,
) -> List[Tuple[str, int, str, str]]:
    """Find potential secrets in a file.

    Args:
    ----
        file_path: Path to the file

    Returns:
    -------
        List[Tuple[str, int, str, str]]: List of pattern name, line number, line, value

    Raises:
    ------
        FileNotFoundError: If file not found
        PermissionError: If insufficient permissions
        UnicodeError: If file cannot be decoded

    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Insufficient permissions to read file: {file_path}")

    results = []
    try:
        with open(file_path, encoding="utf-8", errors="strict") as f:
            content = f.read()
            lines = content.splitlines()
    except UnicodeError as e:
        logger.error("UTF-8 decoding error", extra={"file": file_path, "error": str(e)})
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
            lines = content.splitlines()
            logger.warning(
                "File processed with replacement characters",
                extra={"file": file_path},
            )

    for i, line in enumerate(lines):
        if is_example_code(content, line):
            continue

        for pattern_name, pattern in PATTERNS.items():
            try:
                matches = pattern.findall(line)
            except (re.error, Exception) as e:
                logger.error(
                    "Regex pattern error",
                    extra={
                        "file": file_path,
                        "line": i + 1,
                        "pattern": pattern_name,
                        "error": type(e).__name__,
                    },
                )
                continue

            if matches:
                for match in matches:
                    try:
                        if isinstance(match, tuple):
                            secret_value = match[1]
                        else:
                            secret_value = match
                        results.append((pattern_name, i + 1, line, secret_value))
                    except (IndexError, AttributeError) as e:
                        logger.error(
                            "Match processing error",
                            extra={
                                "file": file_path,
                                "line": i + 1,
                                "pattern": pattern_name,
                                "error": str(e),
                            },
                        )

    return results


def scan_directory(
    directory: str, exclude_dirs: Optional[Set[str]] = None
) -> Dict[str, List[Tuple[str, int, str, str]]]:
    """Scan a directory recursively for potential secrets.

    Args:
    ----
        directory: Directory to scan
        exclude_dirs: Directories to exclude

    Returns:
    -------
        Dict[str, List[Tuple[str, int, str, str]]]: File paths to secrets mapping

    Raises:
    ------
        FileNotFoundError: If directory not found
        PermissionError: If insufficient permissions

    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not os.access(directory, os.R_OK | os.X_OK):
        msg = f"Insufficient permissions to read directory: {directory}"
        raise PermissionError(msg)

    exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    results: Dict[str, List[Tuple[str, int, str, str]]] = {}
    scanned_files = 0
    error_files = []

    try:
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                file_path = os.path.join(root, file)

                try:
                    if should_exclude(file_path, exclude_dirs) or not is_text_file(
                        file_path
                    ):
                        continue

                    secrets = find_potential_secrets(file_path)
                    if secrets:
                        results[file_path] = secrets

                    scanned_files += 1
                    if scanned_files % 100 == 0:
                        logger.info(
                            "Scan progress",
                            extra={
                                "files_scanned": scanned_files,
                                "files_with_secrets": len(results),
                            },
                        )

                except (PermissionError, FileNotFoundError) as e:
                    error_files.append(
                        {
                            "file": file_path,
                            "timestamp": datetime.now().isoformat(),
                            "error_type": type(e).__name__,
                            "error_id": str(uuid.uuid4()),
                        }
                    )
                    logger.warning(
                        "File access error",
                        extra={"file": file_path, "error": str(e)},
                    )
                except Exception as e:
                    error_files.append(
                        {
                            "file": file_path,
                            "timestamp": datetime.now().isoformat(),
                            "error_type": type(e).__name__,
                            "error_id": str(uuid.uuid4()),
                        }
                    )
                    logger.error(
                        "Unexpected error processing file",
                        extra={
                            "file": file_path,
                            "error_type": type(e).__name__,
                            "error_id": str(uuid.uuid4()),
                        },
                    )

        if error_files:
            logger.warning(
                "Scan completed with errors",
                extra={
                    "total_files": scanned_files,
                    "error_files": len(error_files),
                    "files_with_secrets": len(results),
                },
            )
        else:
            logger.info(
                "Scan completed successfully",
                extra={
                    "total_files": scanned_files,
                    "files_with_secrets": len(results),
                },
            )

    except (PermissionError, OSError) as e:
        logger.error(
            "Directory traversal error",
            extra={"directory": directory, "error": str(e)},
        )
        raise

    return results


def generate_report(
    results: Dict[str, List[Tuple[str, int, str, str]]],
    output_file: Optional[str] = None,
    json_format: bool = False,
) -> None:
    """Generate a report of potential secrets.

    Args:
    ----
        results: Dictionary of file paths to secrets
        output_file: Path to the output file
        json_format: Whether to output in JSON format

    """
    if not results:
        logger.info("No potential secrets found")
        return

    total_secrets = sum(len(secrets) for secrets in results.values())
    logger.info(
        "Found potential secrets in files",
        extra={"count": total_secrets, "file_count": len(results)},
    )

    if json_format:
        json_results = {}
        for file_path, secrets in results.items():
            json_results[file_path] = [
                {
                    "type": pattern_name,
                    "line_number": line_number,
                    "line": line,
                    "value": "[REDACTED]",
                }
                for pattern_name, line_number, line, _ in secrets
            ]

        output = json.dumps(json_results, indent=2)
    else:
        lines = [
            "Secrets Audit Report",
            "===================",
            "",
            f"Found {total_secrets} potential secrets in {len(results)} files",
            "",
        ]

        for file_path, secrets in results.items():
            lines.append(f"File: {file_path}")
            lines.append("-" * (len(file_path) + 6))
            for pattern_name, line_number, line, _ in secrets:
                lines.append(f"  Line {line_number}: {pattern_name}")
                lines.append(f"    {line.strip()}")
                lines.append("")
            lines.append("")

        output = "\n".join(lines)

    if output_file:
        try:
            # Apply masking to protect sensitive data
            masked = mask_sensitive_data(output)
            # Double-mask for extra security
            double_masked = mask_sensitive_data(masked)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(double_masked)
            logger.info(
                "Report saved",
                extra={"file": os.path.basename(output_file)},
            )
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    else:
        logger.info("Audit report generated")
        summary = (
            f"Audit report generated: Found {total_secrets} potential secrets "
            f"in {len(results)} files"
        )
        print(summary)


class SecretsAuditor:
    """Utility for auditing code for hardcoded secrets."""

    def __init__(
        self, exclude_dirs: Optional[Set[str]] = None, patterns: Optional[Dict] = None
    ):
        """Initialize the secrets auditor.

        Args:
        ----
            exclude_dirs: Directories to exclude
            patterns: Patterns to use for detecting secrets

        """
        self.exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
        self.patterns = patterns or PATTERNS
        logger.info("Secrets auditor initialized")

    def scan(self, directory: str) -> Dict[str, List[Tuple[str, int, str, str]]]:
        """Scan a directory for potential secrets.

        Args:
        ----
            directory: Directory to scan

        Returns:
        -------
            Dict[str, List[Tuple[str, int, str, str]]]:
            Dictionary of file paths to secrets

        """
        return scan_directory(directory, self.exclude_dirs)

    def generate_report(
        self,
        results: Dict[str, List[Tuple[str, int, str, str]]],
        output_file: Optional[str] = None,
        json_format: bool = False,
    ) -> None:
        """Generate a report of potential secrets.

        Args:
        ----
            results: Dictionary of file paths to secrets
            output_file: Path to the output file
            json_format: Whether to output in JSON format

        """
        generate_report(results, output_file, json_format)

    def audit(
        self,
        directory: str,
        output_file: Optional[str] = None,
        json_format: bool = False,
    ) -> Dict[str, List[Tuple[str, int, str, str]]]:
        """Audit a directory for potential secrets and generate a report.

        Args:
        ----
            directory: Directory to scan
            output_file: Path to the output file
            json_format: Whether to output in JSON format

        Returns:
        -------
            Dict[str, List[Tuple[str, int, str, str]]]:
            Dictionary of file paths to secrets

        """
        results = self.scan(directory)
        self.generate_report(results, output_file, json_format)
        return results
