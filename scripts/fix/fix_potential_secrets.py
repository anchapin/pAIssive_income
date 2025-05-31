#!/usr/bin/env python3

# Configure logging
logger = logging.getLogger(__name__)


"""
Script to detect and report potential secrets in the codebase.

This script scans the codebase for potential secrets like API keys, passwords,
and other sensitive information. It can be run in scan-only mode to detect
but not fix secrets, and it generates a SARIF file for GitHub Advanced Security.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
from pathlib import Path
from re import Pattern
from typing import Any

# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Define patterns for potential secrets
SECRET_PATTERNS = {
    "password": re.compile(r"(?i)(?:password|passwd|pwd)[\s]*[=:'\"][\s]*([^'\"]{8,})"),
    "api_key": re.compile(r"(?i)(?:api[_-]?key|apikey)[\s]*[=:'\"][\s]*([^'\"]{16,})"),
    "access_key": re.compile(r"(?i)(?:access[_-]?key)[\s]*[=:'\"][\s]*([^'\"]{16,})"),
    "secret_key": re.compile(r"(?i)(?:secret[_-]?key)[\s]*[=:'\"][\s]*([^'\"]{16,})"),
    "private_key": re.compile(r"(?i)(?:private[_-]?key)[\s]*[=:'\"][\s]*([^'\"]{16,})"),
    "connection_string": re.compile(
        r"(?i)(?:connection[_-]?string)[\s]*[=:'\"][\s]*([^'\"]{16,})"
    ),
    "token": re.compile(r"(?i)(?:token|auth[_-]?token)[\s]*[=:'\"][\s]*([^'\"]{16,})"),
}

# Define directories and files to exclude
EXCLUDE_DIRS = [
    ".git",
    ".github",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
]

EXCLUDE_FILES = [
    ".gitignore",
    ".gitleaks.toml",
    "secrets.sarif.json",
]

EXCLUDE_EXTENSIONS = [
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp3",
    ".mp4",
    ".mov",
    ".avi",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".rar",
]


def safe_log_sensitive_info(
    pattern_name: str, line_num: int, secret_length: int
) -> str:
    """
    Create a safe log message that doesn't expose the actual secret.

    Args:
        pattern_name: The name of the pattern that matched
        line_num: The line number where the match was found
        secret_length: The length of the secret

    Returns:
        A safe log message

    """
    return (
        f"Found potential {pattern_name} at line {line_num} (length: {secret_length})"
    )


def scan_file(
    file_path: str, patterns: dict[str, Pattern[str]]
) -> list[tuple[str, int, str]]:
    """
    Scan a file for potential secrets.

    Args:
        file_path: Path to the file to scan
        patterns: Dictionary of patterns to search for

    Returns:
        List of tuples containing (pattern_name, line_number, secret)

    """
    results: list[tuple[str, int, str]] = []

    try:
        with Path(file_path).open(encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                for pattern_name, pattern in patterns.items():
                    matches = pattern.findall(line)
                    # Filter and transform matches in one step
                    results.extend(
                        (pattern_name, i, match)
                        for match in matches
                        if not is_placeholder_or_example(match)
                    )
    except (UnicodeDecodeError, PermissionError, FileNotFoundError) as e:
        logger.warning("Error scanning %s: %s", file_path, e)

    return results


def is_placeholder_or_example(text: str) -> bool:
    """
    Check if the text is a placeholder or example.

    Args:
        text: The text to check

    Returns:
        True if the text is a placeholder or example, False otherwise

    """
    placeholders = [
        "your_password_here",
        "your_api_key_here",
        "your_access_key_here",
        "your_secret_key_here",
        "your_private_key_here",
        "your_connection_string_here",
        "your_token_here",
        "example",
        "placeholder",
        "dummy",
        "test",
        "sample",
    ]

    text_lower = text.lower()
    return any(placeholder in text_lower for placeholder in placeholders)


def scan_directory(
    directory: str, patterns: dict[str, Pattern[str]]
) -> dict[str, list[tuple[str, int, str]]]:
    """
    Scan a directory for potential secrets.

    Args:
        directory: Path to the directory to scan
        patterns: Dictionary of patterns to search for

    Returns:
        Dictionary mapping file paths to lists of (pattern_name, line_number, secret)

    """
    results: dict[str, list[tuple[str, int, str]]] = {}

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            # Skip excluded files and extensions
            if file in EXCLUDE_FILES or any(
                file.endswith(ext) for ext in EXCLUDE_EXTENSIONS
            ):
                continue

            file_path = str(Path(root) / file)
            file_results = scan_file(file_path, patterns)
            if file_results:
                results[file_path] = file_results

    return results


def generate_sarif(results: dict[str, list[tuple[str, int, str]]]) -> dict[str, Any]:
    """
    Generate a SARIF report from scan results.

    Args:
        results: Dictionary mapping file paths to lists of (pattern_name, line_number, secret)

    Returns:
        SARIF report as a dictionary

    """
    sarif: dict[str, Any] = {
        "version": "2.1.0",
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Secret Scanner",
                        "informationUri": "https://github.com/anchapin/pAIssive_income",
                        "rules": [],
                    }
                },
                "results": [],
            }
        ],
    }

    # Add rules for each pattern
    rules = []
    for pattern_name in SECRET_PATTERNS:
        rule = {
            "id": pattern_name,
            "name": pattern_name,
            "shortDescription": {"text": f"Potential {pattern_name} detected"},
            "fullDescription": {
                "text": f"Potential {pattern_name} detected in the codebase"
            },
            "help": {
                "text": f"Review the potential {pattern_name} to ensure it is not a real secret"
            },
            "properties": {"security-severity": "9.0"},
        }
        rules.append(rule)

    sarif["runs"][0]["tool"]["driver"]["rules"] = rules

    # Add results
    sarif_results = []
    for file_path, file_results in results.items():
        for pattern_name, line_num, _ in file_results:
            result = {
                "ruleId": pattern_name,
                "level": "error",
                "message": {"text": f"Potential {pattern_name} detected"},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": f"./{os.path.normpath(file_path)}"
                            },
                            "region": {"startLine": line_num},
                        }
                    }
                ],
            }
            sarif_results.append(result)

    sarif["runs"][0]["results"] = sarif_results
    return sarif


def main() -> None:
    """Run the script."""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(
        description="Scan for potential secrets in the codebase"
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Only scan for secrets, don't fix them",
    )
    parser.add_argument(
        "--directory",
        type=str,
        default=".",
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="secrets.sarif.json",
        help="Output file for SARIF report (default: secrets.sarif.json)",
    )
    args = parser.parse_args()

    logger.info("Scanning directory: %s", args.directory)
    results = scan_directory(args.directory, SECRET_PATTERNS)

    total_secrets = sum(len(file_results) for file_results in results.values())
    # Don't log the actual number of secrets as it might reveal sensitive information about the codebase
    logger.info("Scan completed", extra={"files_scanned": len(results)})

    # Generate SARIF report
    sarif = generate_sarif(results)
    with Path(args.output).open("w", encoding="utf-8") as f:
        json.dump(sarif, f, indent=2)
    # Don't log the actual file path as it might contain sensitive information
    logger.info("SARIF report saved successfully")

    # Print summary
    if total_secrets > 0:
        logger.warning("Potential secrets found. Review the SARIF report for details.")
        if not args.scan_only:
            logger.info(
                "To fix secrets, review and update the affected files manually."
            )
    else:
        logger.info("No potential secrets found.")


if __name__ == "__main__":
    main()
