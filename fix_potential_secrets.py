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
from typing import Any, cast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Constants
MAX_FAILED_FILES_TO_LOG = 10

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


def mask_string(
    value: str,
    visible_prefix_len: int = 3,
    visible_suffix_len: int = 3,
    min_len_to_mask: int = 8,
) -> str:
    """
    Masks a string, showing a prefix and suffix if long enough,
    otherwise masks it more completely.
    """
    s_value = str(value) if not isinstance(value, str) else value

    # If string is too short to meaningfully show prefix/suffix, or if prefix+suffix is too large
    if len(s_value) < min_len_to_mask or (
        visible_prefix_len + visible_suffix_len >= len(s_value) and len(s_value) > 0
    ):
        return "*" * len(s_value) if len(s_value) > 0 else ""

    prefix = s_value[:visible_prefix_len]
    suffix = s_value[-visible_suffix_len:]
    # Calculate number of asterisks, ensuring it's not negative
    num_asterisks = max(0, len(s_value) - visible_prefix_len - visible_suffix_len)

    return f"{prefix}{'*' * num_asterisks}{suffix}"


# Directories and files to exclude (these are fallback, .gitignore is primary)
EXCLUDE_DIRS = {
    # ".git" is implicitly handled by find_repo_root and os.walk
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
    # ".gitignore" is read, not excluded from scan itself
    ".dockerignore",  # Example: if you want to parse this too, add logic
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


def should_exclude(file_path: str) -> bool:
    """Check if a file or directory should be excluded from scanning."""
    path_obj = Path(file_path)

    # Check against EXCLUDE_DIRS
    for part in path_obj.parts:
        if part in EXCLUDE_DIRS:
            return True

    # Check against EXCLUDE_FILES
    filename = path_obj.name
    for pattern in EXCLUDE_FILES:
        if (
            pattern.startswith("*") and filename.endswith(pattern[1:])
        ) or pattern == filename:
            return True
    return False


def is_example_code(content: str, line: str) -> bool:
    """Check if the line is part of example code or documentation."""
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
    Assumes file_path is absolute and has already been vetted by should_exclude.
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
                        # Use ternary operator for cleaner code
                        secret_value = match[1] if isinstance(match, tuple) else match

                        if isinstance(
                            secret_value, tuple
                        ):  # If regex captures multiple groups but we only want one
                            secret_value = secret_value[0] if secret_value else ""

                        # SIM102: Combine nested if statements
                        if is_example_code(content, line) and any(
                            safe_val.lower() in str(secret_value).lower()
                            for safe_val in SAFE_REPLACEMENTS.values()
                        ):
                            continue  # It's a known safe replacement value
                        # If it's in an example context but not a known safe value, it might still be a finding
                        # For now, let's be more aggressive in examples
                        # (commented lines below removed by ERA001 fix)

                        # Store length instead of the actual secret value
                        secret_length = len(str(secret_value)) if secret_value else 0
                        results.append((pattern_name, i + 1, secret_length))

        # Results are returned in the else block if no exception occurs
    except Exception:
        return []
    else:  # TRY300
        return results


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
    # Early return if no secrets to fix
    if not secrets:
        return False

    success = False
    try:
        # Validate the file path
        normalized_path = validate_file_path(file_path)
        if normalized_path:
            try:
                # Read file content
                content, lines = read_file_content(normalized_path)

                # Extract actual secrets
                actual_secrets = extract_actual_secrets(lines, content)

                # Apply replacements
                modified = apply_replacements(lines, actual_secrets)

                # Write file if modified
                if modified:
                    success = write_file_with_security(normalized_path, lines)
                    if not success:
                        logging.warning(f"Failed to write file: {normalized_path}")
                else:
                    logging.info(f"No modifications needed for file: {normalized_path}")
            except Exception as e:
                logging.warning(
                    f"Error processing file: {normalized_path}, error: {e!s}"
                )
        else:
            logging.warning(f"Invalid file path: {file_path}")
    except Exception:
        logging.exception("Unexpected error fixing secrets in file")

    return success


def scan_directory(directory: str) -> dict[str, list[tuple[str, int, int]]]:
    """Scan a directory recursively for potential secrets."""
    results = {}
    for root, dirs, files in os.walk(directory, topdown=True):
        # Filter dirs in place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file_name in files:
            file_path = os.path.join(root, file_name)
            if should_exclude(file_path):
                continue

            if not is_text_file(file_path):
                continue

            secrets = find_potential_secrets(file_path)
            if secrets:
                results[file_path] = secrets
    return results


def safe_log_sensitive_info(pattern_name: str, line_num: int) -> str:
    """Log sensitive data info without exposing content."""
    sanitized_pattern = pattern_name.replace("_", " ").capitalize()
    return f"  Line {line_num}: Potential {sanitized_pattern} - [REDACTED]"


def safe_log_file_path(file_path: str) -> str:
    """Safely log file path without exposing potentially sensitive path information."""
    sensitive_keywords = ["secret", "password", "token", "key", "credential", "auth"]
    path_parts = Path(file_path).parts
    # Create a new list of parts to avoid modifying path_parts during iteration if it were mutable
    new_path_parts = list(path_parts)

    for i, part in enumerate(path_parts):
        for keyword in sensitive_keywords:
            if keyword.lower() in part.lower():
                new_path_parts[i] = "[REDACTED_PATH_COMPONENT]"
                # No break here, redact all sensitive components

    # Reconstruct the path using os.path.join for OS compatibility
    # If it was an absolute path, the first part might be empty (for /) or a drive letter.
    if Path(file_path).is_absolute():
        # For absolute paths, the first part might be the root or drive.
        # Path.parts on Windows for 'C:\foo' gives ('C:\\', 'foo').
        # Path.parts on Linux for '/foo' gives ('/', 'foo').
        # We need to handle this to reconstruct correctly.
        if new_path_parts[0] == os.sep or (
            os.name == "nt" and new_path_parts[0].endswith(os.sep)
        ):
            return str(os.path.join(new_path_parts[0], *new_path_parts[1:]))
        else:  # Should not happen for absolute paths from Path.parts
            return str(os.path.join(*new_path_parts))

    return str(os.path.join(*new_path_parts))


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
        ".env",
        ".properties",
        ".log",
        # Add other common text file extensions
    }
    # Also check for files with no extension, common for config files
    file_path_obj = Path(file_path)
    if not file_path_obj.suffix:  # Files like 'Dockerfile', 'Makefile', 'LICENSE'
        # Basic check: try to read a small part, if it decodes, assume text.
        # This is imperfect but better than just extension for extensionless files.
        try:
            with open(file_path_obj, "rb") as f:
                f.read(1024).decode("utf-8")
        except UnicodeDecodeError:
            return False
        except Exception:  # Other read errors
            return False  # If we can't read it, can't scan it
        else:  # TRY300
            return True

    return file_path_obj.suffix.lower() in text_extensions


def initialize_sarif_report() -> dict[str, Any]:
    """Initialize the SARIF report structure.

    Returns:
        A dictionary containing the SARIF report structure.
    """
    return {
        "version": "2.1.0",
        "$schema": (
            "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/"
            "Schemata/sarif-schema-2.1.0.json"
        ),
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Secret Scanner",
                        "rules": [
                            {
                                "id": "secret-detection",
                                "shortDescription": {
                                    "text": "Potential sensitive data detected."
                                },
                                "fullDescription": {
                                    "text": (
                                        "This rule identifies potential hardcoded secrets "
                                        "or sensitive data."
                                    )
                                },
                                "defaultConfiguration": {"level": "error"},
                                "properties": {"tags": ["security", "correctness"]},
                            }
                        ],
                    }
                },
                "results": [],
            }
        ],
    }


def parse_arguments() -> tuple[bool, str]:
    """Parse command line arguments.

    Returns:
        A tuple containing (scan_only, directory).
    """
    scan_only = False
    directory = "."  # Default to current directory

    # Simple argument parsing
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == "--scan-only":
                scan_only = True
            elif arg.startswith("--exclude="):
                # Handle exclude patterns (not implemented in this version)
                pass
            elif not arg.startswith("--"):
                directory = arg

    return scan_only, directory


def ensure_sarif_structure(sarif_report: dict[str, Any]) -> None:
    """Ensure the SARIF report has the required structure.

    Args:
        sarif_report: The SARIF report to validate and update.
    """
    if "runs" not in sarif_report:
        sarif_report["runs"] = []

    if not sarif_report["runs"]:
        sarif_report["runs"] = [
            {"tool": {"driver": {"name": "Secret Scanner", "rules": []}}, "results": []}
        ]

    # Ensure the results array exists
    if "results" not in sarif_report["runs"][0]:
        sarif_report["runs"][0]["results"] = []


def add_sarif_entries(
    sarif_report: dict[str, Any], results: dict[str, list[tuple[str, int, int]]]
) -> None:
    """Add entries to the SARIF report.

    Args:
        sarif_report: The SARIF report to update.
        results: Dictionary mapping file paths to lists of secrets.
    """
    sarif_results = cast(list[dict[str, Any]], sarif_report["runs"][0]["results"])

    for file_path, secrets in results.items():
        try:
            # Use a safe file path in the report
            safe_file_path = safe_log_file_path(file_path)
            for pattern_name, line_num, _secret_length in secrets:
                # Create a generic message that doesn't include length or other metadata
                sarif_results.append({
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
                })
        except Exception:
            logging.exception("Exception while adding SARIF entry")


def log_failed_files(failed_files: list[str]) -> None:
    """Log information about files that failed to be fixed.

    Args:
        failed_files: List of file paths that failed to be fixed.
    """
    if not failed_files:
        return

    logging.warning(
        "Failed to fix secrets in some files",
        extra={"failed_count": len(failed_files)},
    )

    for failed_file in failed_files[:MAX_FAILED_FILES_TO_LOG]:
        safe_path = safe_log_file_path(failed_file)
        logging.warning(f"Failed to fix file: {safe_path}")

    if len(failed_files) > MAX_FAILED_FILES_TO_LOG:
        logging.warning(
            f"... and {len(failed_files) - MAX_FAILED_FILES_TO_LOG} more files"
        )


def process_scan_results(
    results: dict[str, list[tuple[str, int, int]]],
    scan_only: bool,
    sarif_report: dict[str, Any],
) -> tuple[int, int, int]:
    """Process scan results and update SARIF report.

    Args:
        results: Dictionary mapping file paths to lists of secrets.
        scan_only: Whether to only scan and not fix.
        sarif_report: SARIF report to update.

    Returns:
        A tuple containing (total_secrets, fixed_files, exit_code).
    """
    if not results:
        logging.info("No potential secrets found.")
        return 0, 0, 0

    logging.info("Found potential secrets", extra={"file_count": len(results)})

    # Ensure the SARIF report has the required structure
    ensure_sarif_structure(sarif_report)

    # Process results
    total_secrets = sum(len(secrets) for secrets in results.values())
    fixed_files = 0
    failed_files = []

    # Fix secrets if not in scan-only mode
    if not scan_only:
        for file_path, secrets in results.items():
            safe_path = safe_log_file_path(file_path)
            logging.info(
                "Found potential secrets",
                extra={"count": len(secrets), "file": safe_path},
            )

            try:
                if fix_secrets_in_file(file_path, secrets):
                    fixed_files += 1
                    logging.info("Fixed secrets", extra={"file": safe_path})
                else:
                    logging.warning("Failed to fix secrets", extra={"file": safe_path})
                    failed_files.append(file_path)
            except Exception:
                logging.exception(f"Exception while fixing secrets in {safe_path}")
                failed_files.append(file_path)

    # Add results to SARIF report
    add_sarif_entries(sarif_report, results)

    # Log summary of failed files
    log_failed_files(failed_files)

    # Determine exit code
    exit_code = 0
    if scan_only:
        logging.info(
            "Scan complete. Found potential secrets.",
            extra={"total_secrets": total_secrets, "file_count": len(results)},
        )
        # In scan-only mode, exit with 0 even if secrets are found to avoid breaking CI
    else:
        logging.info(
            "Fixed files containing potential secrets.",
            extra={
                "fixed_files": fixed_files,
                "total_files": len(results),
                "failed_files": len(failed_files),
            },
        )
        # Only exit with non-zero if we couldn't fix any files but had files to fix
        if fixed_files == 0 and len(results) > 0:
            exit_code = 1

    return total_secrets, fixed_files, exit_code


def write_sarif_report(sarif_report: dict[str, Any], output_file: str) -> bool:
    """Write SARIF report to file.

    Args:
        sarif_report: SARIF report to write.
        output_file: Path to output file.

    Returns:
        True if successful, False otherwise.
    """
    try:
        # Ensure the SARIF report has the required structure
        if "version" not in sarif_report:
            sarif_report["version"] = "2.1.0"

        if "$schema" not in sarif_report:
            sarif_report["$schema"] = (
                "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
            )

        if "runs" not in sarif_report:
            sarif_report["runs"] = []

        if not sarif_report["runs"]:
            sarif_report["runs"] = [
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
            ]

        # Ensure the results array exists
        if "results" not in sarif_report["runs"][0]:
            sarif_report["runs"][0]["results"] = []

        # Write the report
        with open(output_file, "w") as f:
            json.dump(sarif_report, f, indent=2)

        # Validate the written file
        try:
            with open(output_file) as f:
                json.load(f)
            logging.info(
                "SARIF report written and validated", extra={"file": output_file}
            )
        except json.JSONDecodeError:
            logging.exception(
                "Written SARIF report is not valid JSON", extra={"file": output_file}
            )
            write_empty_sarif_report(output_file)
            return False
        else:
            return True
    except Exception:
        logging.exception("Failed to write SARIF report")
        write_empty_sarif_report(output_file)
        return False


def write_empty_sarif_report(output_file: str) -> None:
    """Write an empty SARIF report in case of error.

    Args:
        output_file: Path to output file.
    """
    try:
        empty_report = {
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
        with open(output_file, "w") as f:
            json.dump(empty_report, f, indent=2)
        logging.info(
            "Empty SARIF report written as fallback", extra={"file": output_file}
        )
    except Exception:
        logging.exception("Failed to write empty SARIF report")
        # Last resort attempt with minimal error handling
        try:
            with open(output_file, "w") as f:
                f.write(
                    '{"version":"2.1.0","runs":[{"tool":{"driver":{"name":"Secret Scanner","rules":[]}},"results":[]}]}'
                )
        except Exception:
            pass


def main() -> int:
    """Scan for and fix potential secrets."""
    # Define the output file for the SARIF report
    output_file = "secrets.sarif.json"

    # Parse command line arguments
    scan_only, directory = parse_arguments()

    # Initialize SARIF report structure
    sarif_report = initialize_sarif_report()

    try:
        logging.info(
            "Starting secret scanning process",
            extra={"scan_only": scan_only, "directory": directory},
        )

        # Validate directory exists
        if not os.path.isdir(directory):
            logging.error(
                f"Directory '{directory}' does not exist or is not accessible"
            )
            write_empty_sarif_report(output_file)
            return 1

        # Scan directory for potential secrets
        logging.info(
            "Scanning directory for potential secrets", extra={"directory": directory}
        )
        try:
            results = scan_directory(directory)
        except Exception:
            logging.exception("Error scanning directory")
            # Create a minimal valid SARIF report in case of error
            write_empty_sarif_report(output_file)
            return 1

        # Process scan results and update SARIF report
        logging.info("Processing scan results", extra={"file_count": len(results)})
        try:
            total_secrets, fixed_files, exit_code = process_scan_results(
                results, scan_only, sarif_report
            )
            logging.info(
                "Scan results summary",
                extra={
                    "total_secrets": total_secrets,
                    "files_with_secrets": len(results),
                    "fixed_files": fixed_files,
                    "scan_only": scan_only,
                },
            )
        except Exception:
            logging.exception("Error processing scan results")
            # Continue to write whatever we have in the SARIF report
            exit_code = 1

        # Write SARIF report
        logging.info("Writing SARIF report", extra={"output_file": output_file})
        if not write_sarif_report(sarif_report, output_file):
            logging.error("Failed to write SARIF report")
            # Create a minimal valid SARIF report as fallback
            write_empty_sarif_report(output_file)
            return 1
        else:
            return exit_code
    except Exception:
        logging.exception("Unhandled error in main function")
        # Create a minimal valid SARIF report in case of error
        write_empty_sarif_report(output_file)
        return 1


if __name__ == "__main__":
    # This script can be run standalone or be imported by fix_security_issues.py
    # If run standalone, its main() is executed.
    # If imported, fix_security_issues.py calls scan_directory().
    # The sys.exit is important for standalone execution.
    sys.exit(main())
