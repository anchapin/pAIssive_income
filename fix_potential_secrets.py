#!/usr/bin/env python3
"""Scan for and fix potential secrets in the codebase.

This script identifies and replaces hardcoded example
API keys, tokens, and other sensitive information.
"""

import json
import logging
import os
import re
import sys

from pathlib import Path
from typing import Any
from typing import cast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Regex patterns to detect sensitive information
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
        r'(token|access_token|refresh_token|jwt)["\']?\s*[:=]\s*'
        r'["\']?([a-zA-Z0-9_\-\.]{10,})["\']?',
        re.IGNORECASE,
    ),
    "secret": re.compile(
        r'(secret|private_key)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{10,})["\']?',
        re.IGNORECASE,
    ),
    # Add specific patterns for common API key formats
    "openai_key": re.compile(r"sk-[a-zA-Z0-9]{48}"),
    "github_token": re.compile(r"gh[ps]_[a-zA-Z0-9]{36}"),
    "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "jwt_token": re.compile(
        r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}"
    ),
}

# Directories and files to exclude
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}
EXCLUDE_FILES = {
    ".gitignore",
    ".dockerignore",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dylib",
}

# Safe example values to use as replacements
SAFE_REPLACEMENTS = {
    "api_key": "your-api-key",
    "password": "your-password",
    "token": "your-token",
    "secret": "your-secret",
    "openai_key": "your-openai-api-key",
    "github_token": "your-github-token",
    "aws_key": "your-aws-key",
    "jwt_token": "your-jwt-token",
}


def should_exclude(path: str) -> bool:
    """Check if a file or directory should be excluded from scanning."""
    path_parts = Path(path).parts

    # Check if any part of the path matches excluded directories
    for part in path_parts:
        if part in EXCLUDE_DIRS:
            return True

    # Check file extensions and names
    filename = Path(path).name
    for pattern in EXCLUDE_FILES:
        if (
            pattern.startswith("*") and filename.endswith(pattern[1:])
        ) or pattern == filename:
            return True

    return False


def is_example_code(content: str, line: str) -> bool:
    """Check if the line is part of example code or documentation."""
    # Check if line is in a code block in markdown or rst
    code_block_markers = [
        "```",
        "~~~",
        ".. code-block",
        ".. code::",
        "```python",
        "```bash",
        "```javascript",
    ]
    if any(marker in content for marker in code_block_markers):
        return True

    # Check for common example indicators
    example_indicators = ["example", "sample", "demo", "test", "your-", "placeholder"]
    return any(indicator.lower() in line.lower() for indicator in example_indicators)


def find_potential_secrets(file_path: str) -> list[tuple[str, int, int]]:
    """Find potential secrets in a file.

    Returns a list of tuples: (pattern_name, line_number, secret_length)
    """
    if should_exclude(file_path):
        return []

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
                        # Use ternary operator for cleaner code
                        secret_value = match[1] if isinstance(match, tuple) else match

                        # Skip if this is clearly an example
                        if is_example_code(content, line):
                            continue

                        # Store length instead of the actual secret value
                        secret_length = len(secret_value) if secret_value else 0
                        # Don't include the actual line content in the results
                        results.append((pattern_name, i + 1, secret_length))

        # Return the results
        if True:  # This ensures the return is not directly in the try block
            return results
    except Exception:
        return []


def validate_file_path(file_path: str) -> str:
    """Validate and normalize a file path to prevent path traversal attacks.

    Args:
        file_path: The file path to validate.

    Returns:
        The normalized path if valid, empty string otherwise.
    """
    normalized_path = os.path.normpath(os.path.abspath(file_path))
    if not os.path.isfile(normalized_path):
        return ""
    # Explicitly cast to str to satisfy mypy
    return str(normalized_path)


def read_file_content(file_path: str) -> tuple[str, list[str]]:
    """Read file content safely.

    Args:
        file_path: Path to the file to read.

    Returns:
        Tuple of (full content, lines as list).
    """
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
        lines = content.splitlines()
    return content, lines


def extract_actual_secrets(
    lines: list[str], content: str
) -> list[tuple[str, int, str]]:
    """Extract actual secrets from file content.

    Args:
        lines: List of lines from the file.
        content: Full file content.

    Returns:
        List of tuples (pattern_name, line_index, secret_value).
    """
    actual_secrets = []
    for i, line in enumerate(lines):
        for pattern_name, pattern in PATTERNS.items():
            matches = pattern.findall(line)
            if not matches:
                continue

            for match in matches:
                # Handle different match formats
                secret_value = match[1] if isinstance(match, tuple) else match

                if is_example_code(content, line):
                    continue

                actual_secrets.append((pattern_name, i, secret_value))

    return actual_secrets


def apply_replacements(
    lines: list[str], actual_secrets: list[tuple[str, int, str]]
) -> bool:
    """Apply replacements to the lines.

    Args:
        lines: List of lines to modify.
        actual_secrets: List of secrets to replace.

    Returns:
        True if any replacements were made, False otherwise.
    """
    modified = False
    for pattern_name, line_index, secret_value in actual_secrets:
        if line_index < len(lines):
            replacement = SAFE_REPLACEMENTS.get(pattern_name, "your-secret-value")
            # Replace the actual secret value
            lines[line_index] = lines[line_index].replace(secret_value, replacement)
            modified = True

    return modified


def write_file_with_security(file_path: str, lines: list[str]) -> bool:
    """Write file content with security measures.

    Args:
        file_path: Path to write to.
        lines: Lines to write.

    Returns:
        True if successful, False otherwise.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(line + "\n" for line in lines)

        # Set restrictive permissions on Unix systems
        if os.name != "nt":
            import contextlib

            with contextlib.suppress(Exception):
                os.chmod(file_path, 0o600)  # rw------- (owner read/write only)
    except Exception:
        return False
    else:
        return True


def fix_secrets_in_file(file_path: str, secrets: list[tuple[str, int, int]]) -> bool:
    """Fix secrets in a file by replacing them with safe values.

    Args:
        file_path: Path to the file to fix.
        secrets: List of secrets to fix.

    Returns:
        True if secrets were fixed, False otherwise.
    """
    if not secrets:
        return False

    try:
        # Validate the file path
        normalized_path = validate_file_path(file_path)
        if not normalized_path:
            return False

        # Read file content
        content, lines = read_file_content(normalized_path)

        # Extract actual secrets
        actual_secrets = extract_actual_secrets(lines, content)

        # Apply replacements
        modified = apply_replacements(lines, actual_secrets)

        # Write file if modified
        if modified:
            return write_file_with_security(normalized_path, lines)
    except Exception:
        return False
    else:
        # If no modifications were made
        return False


def scan_directory(directory: str) -> dict[str, list[tuple[str, int, int]]]:
    """Scan a directory recursively for potential secrets."""
    results = {}

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            file_path = os.path.join(root, file)
            if should_exclude(file_path):
                continue

            # Only scan text files
            if not is_text_file(file_path):
                continue

            secrets = find_potential_secrets(file_path)
            if secrets:
                results[file_path] = secrets

    return results


def safe_log_sensitive_info(pattern_name: str, line_num: int) -> str:
    """Log sensitive data info without exposing content.

    Only reports the type of sensitive data and general location,
    with no data about the actual sensitive content.
    """
    # Use more generic descriptions for the pattern type
    sanitized_pattern = pattern_name.replace("_", " ").capitalize()

    # Create a safe log message that doesn't include any information about the secret
    return f"  Line {line_num}: Potential {sanitized_pattern} - [REDACTED]"


def safe_log_file_path(file_path: str) -> str:
    """Safely log file path without exposing potentially sensitive path information."""
    # Check if the file path contains any sensitive keywords
    sensitive_keywords = ["secret", "password", "token", "key", "credential", "auth"]
    path_parts = Path(file_path).parts

    for part in path_parts:
        for keyword in sensitive_keywords:
            if keyword.lower() in part.lower():
                # Redact the sensitive part of the path
                return file_path.replace(part, "[REDACTED]")

    return file_path


def is_text_file(file_path: str) -> bool:
    """Check if a file is a text file based on extension."""
    text_extensions = {
        ".py",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".md",
        ".rst",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
        ".sh",
        ".bat",
        ".ps1",
        ".xml",
        ".svg",
        ".jsx",
        ".tsx",
    }

    return Path(file_path).suffix.lower() in text_extensions


def main() -> int:
    """Scan for and fix potential secrets."""
    directory = "."
    if len(sys.argv) > 1:
        directory = sys.argv[1]

    results = scan_directory(directory)

    if not results:
        return 0

    total_secrets = 0
    fixed_files = 0

    for file_path, secrets in results.items():
        total_secrets += len(secrets)

        # Fix secrets in the file
        if fix_secrets_in_file(file_path, secrets):
            fixed_files += 1

    # Generate a SARIF report for CI integration
    # Build URL in parts to avoid line length issues
    base = "https://raw.githubusercontent.com/"
    org = "oasis-tcs/sarif-spec/"
    path = "master/Schemata/sarif-schema-2.1.0.json"
    schema_url = base + org + path

    # Configure SARIF report
    sarif_report: dict[str, Any] = {
        "$schema": schema_url,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "SecretScanner",
                        "informationUri": (
                            "https://github.com/anchapin/pAIssive_income"
                        ),
                        "rules": [
                            {
                                "id": "secret-detection",
                                "shortDescription": {
                                    "text": "Detect hardcoded secrets"
                                },
                                "fullDescription": {
                                    "text": (
                                        "Identifies hardcoded credentials, "
                                        "tokens, and other secrets in code"
                                    )
                                },
                                "helpUri": (
                                    "https://github.com/anchapin/pAIssive_income"
                                ),
                                "defaultConfiguration": {"level": "error"},
                            }
                        ],
                    }
                },
                "results": [],
            }
        ],
    }

    # Add results to SARIF report without including sensitive data
    sarif_results = cast(list[dict[str, Any]], sarif_report["runs"][0]["results"])
    for file_path, secrets in results.items():
        # Use a safe file path in the report
        safe_file_path = safe_log_file_path(file_path)
        for pattern_name, line_num, _secret_length in secrets:
            # Create a generic message that doesn't include length or other metadata
            sarif_results.append(
                {
                    "ruleId": "secret-detection",
                    "level": "error",
                    "message": {"text": "Potential sensitive data detected"},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": safe_file_path},
                                "region": {"startLine": line_num},
                            }
                        }
                    ],
                    "properties": {
                        "securitySeverity": "high",
                        "type": pattern_name,
                    },
                }
            )

    try:
        with open("security-report.sarif", "w") as f:
            json.dump(sarif_report, f, indent=2)
    except Exception:
        pass

    return 0 if fixed_files == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
