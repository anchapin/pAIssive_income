#!/usr/bin/env python3
"""Fix potential secrets in files.

This script scans files for potential secrets and replaces them with safe values.
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Regular expressions for detecting potential secrets
PATTERNS = {
    "api_key": re.compile(
        r"(api[_-]?key|apikey)['\"]?\s*(?::|=|:=|\s+)\s*['\"]([a-zA-Z0-9]{16,})['\"]"
    ),
    "password": re.compile(
        r"(password|passwd|pwd)['\"]?\s*(?::|=|:=|\s+)\s*['\"]([^'\"]{8,})['\"]"
    ),
    "secret_key": re.compile(
        r"(secret[_-]?key|secretkey)['\"]?\s*(?::|=|:=|\s+)\s*['\"]([a-zA-Z0-9]{16,})['\"]"
    ),
    "access_key": re.compile(
        r"(access[_-]?key|accesskey)['\"]?\s*(?::|=|:=|\s+)\s*['\"]([a-zA-Z0-9]{16,})['\"]"
    ),
    "auth_token": re.compile(
        r"(auth[_-]?token|authtoken)['\"]?\s*(?::|=|:=|\s+)\s*['\"]([a-zA-Z0-9]{16,})['\"]"
    ),
    "jwt_token": re.compile(
        r"(jwt[_-]?token|jwttoken)['\"]?\s*(?::|=|:=|\s+)\s*['\"]([a-zA-Z0-9._-]{16,})['\"]"
    ),
    "private_key": re.compile(
        r"(private[_-]?key|privatekey)['\"]?\s*(?::|=|:=|\s+)\s*['\"]([a-zA-Z0-9/+._-]{16,})['\"]"
    ),
    "connection_string": re.compile(
        r"(connection[_-]?string|connectionstring)['\"]?\s*(?::|=|:=|\s+)\s*['\"]([^'\"]{16,})['\"]"
    ),
}

# Safe replacements for detected secrets
SAFE_REPLACEMENTS = {
    "api_key": "your-api-key",
    "password": "your-password",
    "secret_key": "your-secret-key",
    "access_key": "your-access-key",
    "auth_token": "your-auth-token",
    "jwt_token": "your-jwt-token",
    "private_key": "your-private-key",
    "connection_string": "your-connection-string",
}

# File extensions to scan
EXTENSIONS_TO_SCAN = {
    ".py",
    ".js",
    ".ts",
    ".json",
    ".yaml",
    ".yml",
    ".env",
    ".ini",
    ".cfg",
    ".conf",
    ".xml",
    ".md",
    ".txt",
    ".sh",
    ".bat",
    ".ps1",
}

# Directories to exclude
DIRS_TO_EXCLUDE = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

# Files to exclude
FILES_TO_EXCLUDE = {
    ".gitignore",
    ".dockerignore",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Pipfile.lock",
}


def mask_string(
    s: str, prefix_len: int = 2, suffix_len: int = 2, mask_len: int = 6
) -> str:
    """Mask a string, showing only the first and last few characters.

    Args:
        s: The string to mask.
        prefix_len: Number of characters to show at the beginning.
        suffix_len: Number of characters to show at the end.
        mask_len: Number of mask characters to use.

    Returns:
        The masked string.
    """
    if len(s) <= prefix_len + suffix_len:
        return "*" * len(s)

    prefix = s[:prefix_len]
    suffix = s[-suffix_len:] if suffix_len > 0 else ""
    mask = "*" * mask_len

    return f"{prefix}{mask}{suffix}"


def is_example_code(content: str, line: str) -> bool:
    """Check if a line is part of example code.

    Args:
        content: The full file content.
        line: The line to check.

    Returns:
        True if the line is part of example code, False otherwise.
    """
    # Check if line is in a code block in markdown
    if "```" in content:
        code_blocks = re.findall(r"```.*?```", content, re.DOTALL)
        if any(line in block for block in code_blocks):
            return True

    # Check if line is in a comment
    if line.strip().startswith(("#", "//", "/*", "*", "<!--")):
        return True

    # Check if line is in a docstring
    if '"""' in content or "'''" in content:
        docstring_patterns = [r'""".*?"""', r"'''.*?'''"]
        for pattern in docstring_patterns:
            docstrings = re.findall(pattern, content, re.DOTALL)
            if any(line in docstring for docstring in docstrings):
                return True

    # Check for common example patterns
    example_patterns = [
        r"example",
        r"sample",
        r"test",
        r"demo",
        r"placeholder",
        r"dummy",
    ]
    return any(re.search(pattern, line, re.IGNORECASE) for pattern in example_patterns)


def extract_actual_secrets(
    lines: list[str], content: str
) -> list[tuple[str, int, str]]:
    """Extract actual secrets from file content.

    Args:
        lines: List of lines from the file.
        content: Full file content.

    Returns:
        List of tuples (pattern_name, line_index, masked_secret_value).
    """
    actual_secrets = []
    for i, line in enumerate(lines):
        for pattern_name, pattern in PATTERNS.items():
            matches = pattern.findall(line)
            if not matches:
                continue

            # Check if line is example code before processing matches
            if is_example_code(content, line):
                continue

            # Don't store the actual secret value, just the pattern name and line number
            # This prevents any possibility of logging sensitive data
            actual_secrets.append((pattern_name, i, ""))

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
    for pattern_name, line_index, _masked_secret in actual_secrets:
        if line_index < len(lines):
            replacement = SAFE_REPLACEMENTS.get(pattern_name, "your-secret-value")
            line = lines[line_index]

            # Find the actual secret in the line using the pattern
            for pattern in [PATTERNS[pattern_name]]:
                matches = pattern.findall(line)
                if matches:
                    for match in matches:
                        # Handle different match formats
                        actual_secret = match[1] if isinstance(match, tuple) else match
                        # Replace the actual secret value
                        lines[line_index] = lines[line_index].replace(
                            actual_secret, replacement
                        )
                        modified = True

    return modified


def fix_secrets_in_file(file_path: str, secrets: list[tuple[str, int, str]]) -> bool:
    """Fix secrets in a file.

    Args:
        file_path: Path to the file.
        secrets: List of secrets to fix.

    Returns:
        True if the file was modified, False otherwise.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        if apply_replacements(lines, secrets):
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True
        else:
            return False
    except Exception:
        # Use a generic message without revealing the full file path
        logging.exception(f"Error processing file: {os.path.basename(file_path)}")
        return False


def scan_file(file_path: str) -> list[tuple[str, int, str]]:
    """Scan a file for potential secrets.

    Args:
        file_path: Path to the file.

    Returns:
        List of tuples (pattern_name, line_index, secret_value).
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines(keepends=True)

        return extract_actual_secrets(lines, content)
    except Exception:
        # Use a generic message without revealing the full file path
        logging.exception(f"Error scanning file: {os.path.basename(file_path)}")
        return []


def should_scan_file(file_path: str) -> bool:
    """Check if a file should be scanned.

    Args:
        file_path: Path to the file.

    Returns:
        True if the file should be scanned, False otherwise.
    """
    # Check if file exists
    if not os.path.isfile(file_path):
        return False

    # Check if file is in an excluded directory
    parts = Path(file_path).parts
    for part in parts:
        if part in DIRS_TO_EXCLUDE:
            return False

    # Check if file is excluded
    if os.path.basename(file_path) in FILES_TO_EXCLUDE:
        return False

    # Check if file has an extension to scan
    _, ext = os.path.splitext(file_path)
    return ext.lower() in EXTENSIONS_TO_SCAN


def safe_log_sensitive_info(pattern_name: str, line_num: int) -> str:
    """Log sensitive data info without exposing content.

    Args:
        pattern_name: The type of sensitive data (e.g., 'api_key', 'password')
        line_num: The line number where the sensitive data was found

    Returns:
        A string with sanitized information about the sensitive data
    """
    sanitized_pattern = pattern_name.replace("_", " ").capitalize()
    return f"  Line {line_num}: Potential {sanitized_pattern} - [REDACTED]"


def log_failed_files(failed_files: list[str]) -> None:
    """Log failed files.

    Args:
        failed_files: List of files that failed to be fixed.
    """
    if not failed_files:
        return

    # Log counts using extra parameter to avoid exposing sensitive data in the message
    logging.warning(
        "Some files could not be processed.", extra={"failed_count": len(failed_files)}
    )

    # Log only the base filename to avoid potential path disclosure
    for file_path in failed_files:
        safe_path = os.path.basename(file_path)
        logging.warning("Failed to process file.", extra={"file": safe_path})


def scan_directory(directory: str) -> dict[str, list[tuple[str, int, str]]]:
    """Scan a directory for potential secrets.

    Args:
        directory: Directory to scan.

    Returns:
        Dictionary mapping file paths to lists of secrets.
    """
    results = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if should_scan_file(file_path):
                secrets = scan_file(file_path)
                if secrets:
                    results[file_path] = secrets
    return results


def generate_sarif_report(
    results: dict[str, list[tuple[str, int, str]]], output_file: str
) -> None:
    """Generate a SARIF report from scan results.

    Args:
        results: Dictionary mapping file paths to lists of secrets.
        output_file: Path to the output file.
    """
    sarif = {
        "version": "2.1.0",
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Secret Scanner",
                        "informationUri": "https://github.com/anchapin/pAIssive_income",
                        "rules": [
                            {
                                "id": pattern_name,
                                "name": pattern_name.replace("_", " ").capitalize(),
                                "shortDescription": {
                                    "text": f"Potential {pattern_name.replace('_', ' ')} detected"
                                },
                                "fullDescription": {
                                    "text": f"Potential {pattern_name.replace('_', ' ')} detected in the code"
                                },
                                "help": {
                                    "text": f"Replace the {pattern_name.replace('_', ' ')} with a safe value or move it to a secure location"
                                },
                                "properties": {"security-severity": "9.0"},
                            }
                            for pattern_name in PATTERNS
                        ],
                    }
                },
                "results": [],
            }
        ],
    }

    # Ensure runs is a list before indexing
    if isinstance(sarif["runs"], list) and len(sarif["runs"]) > 0:
        for file_path, secrets in results.items():
            for pattern_name, line_index, _ in secrets:
                sarif["runs"][0]["results"].append({
                    "ruleId": pattern_name,
                    "level": "error",
                    "message": {
                        "text": f"Potential {pattern_name.replace('_', ' ')} detected"
                    },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": file_path.replace("\\", "/")
                                },
                                "region": {"startLine": line_index + 1},
                            }
                        }
                    ],
                })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sarif, f, indent=2)


def process_scan_results(
    results: dict[str, list[tuple[str, int, str]]], fix: bool = True
) -> list[str]:
    """Process scan results.

    Args:
        results: Dictionary mapping file paths to lists of secrets.
        fix: Whether to fix the secrets.

    Returns:
        List of files that failed to be fixed.
    """
    failed_files: list[str] = []
    fixed_files = 0
    total_secrets = sum(len(secrets) for secrets in results.values())

    if results:
        # Use a generic message that doesn't reveal any sensitive information
        logging.info("Scan complete. Potential sensitive data found.")
        # Log counts using extra parameter to avoid exposing sensitive data in the message
        logging.info(
            "Found potential issues in files.",
            extra={"issue_count": total_secrets, "file_count": len(results)},
        )

        if fix:
            # Log counts using extra parameter to avoid exposing sensitive data in the message
            logging.info(
                "Files processed. Potential sensitive data addressed.",
                extra={
                    "fixed_files": fixed_files,
                    "total_files": len(results),
                    "failed_files": len(failed_files),
                },
            )
        else:
            logging.info("Scan-only mode. No files were modified.")
    else:
        logging.info("Scan complete. No potential sensitive data found.")

    for file_path, secrets in results.items():
        # Use a safe path for logging
        safe_path = os.path.basename(file_path)

        # Log the file and the secrets found - use generic message without revealing details
        # Log file information using extra parameter to avoid exposing sensitive data in the message
        logging.info(
            "Processing file with potential issues.",
            extra={"file": safe_path, "issue_count": len(secrets)},
        )

        for pattern_name, line_index, _ in secrets:
            logging.info(safe_log_sensitive_info(pattern_name, line_index + 1))

        if fix:
            try:
                if fix_secrets_in_file(file_path, secrets):
                    fixed_files += 1
                    logging.info(
                        "File processed successfully.", extra={"file": safe_path}
                    )
                else:
                    logging.warning(
                        "File processing failed.", extra={"file": safe_path}
                    )
                    failed_files.append(file_path)
            except Exception:
                logging.exception(
                    "Exception during file processing.", extra={"file": safe_path}
                )
                failed_files.append(file_path)

    if failed_files:
        log_failed_files(failed_files)

    return failed_files


def main() -> int:
    """Main function.

    Returns:
        Exit code.
    """
    parser = argparse.ArgumentParser(description="Fix potential secrets in files")
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Only scan for secrets, don't fix them",
    )
    parser.add_argument(
        "--sarif",
        action="store_true",
        help="Generate a SARIF report",
    )
    parser.add_argument(
        "--sarif-output",
        default="secrets.sarif.json",
        help="Path to the SARIF report output file (default: secrets.sarif.json)",
    )
    args = parser.parse_args()

    try:
        # Use a generic message without revealing the full directory path
        logging.info(f"Starting scan in directory: {os.path.basename(args.directory)}")
        results = scan_directory(args.directory)
        failed_files = process_scan_results(results, fix=not args.scan_only)

        if args.sarif:
            # Use a generic message without revealing the full file path
            logging.info(
                f"Generating SARIF report: {os.path.basename(args.sarif_output)}"
            )
            generate_sarif_report(results, args.sarif_output)

        if failed_files:
            return 1
        else:
            return 0
    except Exception:
        # Use a generic message that doesn't reveal any sensitive information
        logging.exception("Process failed due to an unexpected error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
