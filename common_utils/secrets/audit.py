"""audit - Module for common_utils/secrets.audit.

This module provides utilities for auditing code for hardcoded secrets.
"""

# Standard library imports
import json
import os
import re
from typing import Dict, List, Optional, Set, Tuple

# Third-party imports
# Local imports
from common_utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Patterns to detect potential secrets
PATTERNS = {
    "api_key": re.compile(
        r'(api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{10,})["\']?',
        re.IGNORECASE,
    ),
    "password": re.compile(
        r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^"\'\s]{3,})["\']?',
        re.IGNORECASE,
    ),
    "token": re.compile(
        r'(token|access_token|refresh_token|jwt)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{10,})["\']?',
        re.IGNORECASE,
    ),
    "secret": re.compile(
        r'(secret|private_key)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{10,})["\']?',
        re.IGNORECASE,
    ),
}

# Directories to exclude from scanning
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

# File extensions to scan
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
    # Check file extension
    _, ext = os.path.splitext(file_path.lower())
    if ext in TEXT_FILE_EXTENSIONS:
        return True

    # Try to read the file as text
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            sample = f.read(1024)
            # Check for null bytes, which indicate a binary file
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
    # Check for common example indicators
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

    # Check if the line is in a docstring or comment block
    if '"""' in content or "'''" in content:
        # Simple heuristic: if the line has a lot of indentation,
        # it's probably in a docstring
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

    # Normalize path
    file_path = os.path.normpath(file_path)

    # Check if the file is in an excluded directory
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
        List[Tuple[str, int, str, str]]:
        List of (pattern_name, line_number, line, secret_value)

    """
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.splitlines()

        results = []
        for i, line in enumerate(lines):
            for pattern_name, pattern in PATTERNS.items():
                matches = pattern.findall(line)
                if matches:
                    for match in matches:
                        # Handle different match formats
                        if isinstance(match, tuple):
                            # For patterns that capture the key name and value
                            secret_value = match[1]
                        else:
                            # For patterns that only capture the value
                            secret_value = match

                        # Skip if this is clearly an example
                        if is_example_code(content, line):
                            continue

                        results.append((pattern_name, i + 1, line, secret_value))

        return results
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return []


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
        Dict[str, List[Tuple[str, int, str, str]]]: Dictionary of file paths to secrets

    """
    if exclude_dirs is None:
        exclude_dirs = DEFAULT_EXCLUDE_DIRS

    results = {}

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            file_path = os.path.join(root, file)
            if should_exclude(file_path, exclude_dirs):
                continue

            # Only scan text files
            if not is_text_file(file_path):
                continue

            secrets = find_potential_secrets(file_path)
            if secrets:
                results[file_path] = secrets

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
    logger.info(f"Found {total_secrets} potential secrets in {len(results)} files")

    if json_format:
        # Convert to a format suitable for JSON
        json_results = {}
        for file_path, secrets in results.items():
            json_results[file_path] = [
                {
                    "type": pattern_name,
                    "line_number": line_number,
                    "line": line,
                    # Intentionally not including the actual secret value to
                    # avoid exposing sensitive information
                    "value": "[REDACTED]",
                }
                for pattern_name, line_number, line, _ in secrets
            ]

        output = json.dumps(json_results, indent=2)
    else:
        # Generate a text report
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
            # Intentionally not using secret_value to
            # avoid exposing sensitive information in reports
            for pattern_name, line_number, line, _ in secrets:
                lines.append(f"  Line {line_number}: {pattern_name}")
                lines.append(f"    {line.strip()}")
                lines.append("")
            lines.append("")

        output = "\n".join(lines)

    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output)
            logger.info(f"Report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    else:
        print(output)


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
