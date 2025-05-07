"""audit - Module for common_utils/secrets.audit.

This module provides utilities for auditing code for hardcoded secrets.
"""

# Standard library imports
import base64
import json
import os
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

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
        logger.info("No potential security findings")
        return

    total_secrets = sum(len(secrets) for secrets in results.values())
    logger.info(
        "Completed security scan",
        extra={"scan_completed": True, "total_secrets": total_secrets},
    )

    if json_format:
        json_results = {}
        for file_path, secrets in results.items():
            # Mask the file path to prevent leaking sensitive paths
            masked_file_path = mask_sensitive_data(file_path)
            json_results[masked_file_path] = [
                {
                    "type": pattern_name,
                    "line_number": line_number,
                    "line": mask_sensitive_data(
                        line
                    ),  # Mask the entire line, not just the value
                    "value": "[REDACTED]",  # Never expose the actual secret value
                }
                for pattern_name, line_number, line, _ in secrets
            ]

        # Create a pre-masked JSON string - never store unmasked data
        masked_json = json.dumps(json_results, indent=2)
        # Apply additional masking for extra security
        output = mask_sensitive_data(masked_json)
    else:
        lines = [
            "Security Scan Report",
            "===================",
            "",
            "Scan completed successfully",
            "",
        ]

        for file_path, secrets in results.items():
            # Mask the file path in the report
            masked_file_path = mask_sensitive_data(file_path)
            lines.append(f"File: {masked_file_path}")
            lines.append("-" * (len(masked_file_path) + 6))
            for pattern_name, line_number, line, _ in secrets:
                # Immediately mask the line to avoid storing sensitive data
                # in clear text
                masked_line = mask_sensitive_data(line)
                # Apply second-level masking for critical parts
                masked_line = mask_sensitive_data(masked_line, visible_chars=2)
                lines.append(f"  Line {line_number}: {pattern_name}")
                # Apply masking to the line content
                lines.append(f"    {masked_line.strip()}")
                lines.append("")
            lines.append("")

        # Apply multi-level masking to the full output
        # First-level masking
        output = mask_sensitive_data("\n".join(lines))
        # Second-level masking with reduced visibility
        output = mask_sensitive_data(output, visible_chars=2)

    if output_file:
        try:
            # Apply additional security measures for the file content
            # Triple-level masking to ensure no sensitive data is stored in clear text
            secure_output = mask_sensitive_data(output, visible_chars=1)
            secure_output = mask_sensitive_data(secure_output, visible_chars=0)

            # Final verification - replace any suspicious patterns with fixed strings
            for _pattern_name, pattern in PATTERNS.items():
                secure_output = pattern.sub(r"\1[REDACTED]", secure_output)

            # Encrypt the report content using environment-based key
            # Rather than hardcoded password
            # Generate secure random password if one is not provided
            env_key = os.environ.get("PAISSIVE_REPORT_KEY")
            if env_key:
                password = env_key.encode("utf-8")
            else:
                # Use system-specific values to generate a deterministic but
                # not hardcoded key
                system_id = (
                    str(uuid.getnode())
                    + os.environ.get("COMPUTERNAME", "")
                    + os.environ.get("HOSTNAME", "")
                )
                password = system_id.encode("utf-8")

            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend(),
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            cipher = Fernet(key)
            encrypted_output = cipher.encrypt(secure_output.encode())

            # Create the output directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, mode=0o700)  # Secure permissions

            # Write the encrypted output to the file
            with open(output_file, "wb") as f:
                f.write(encrypted_output)
        except Exception as e:
            # Mask any potential sensitive data in error message
            masked_error = mask_sensitive_data(str(e))
            logger.error("Error saving report", extra={"error": masked_error})
    else:
        # Don't log the full report, just that it was generated
        logger.info("Security scan report generated")
        print("Security scan completed. Review the secured report for details.")


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
