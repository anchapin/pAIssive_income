#!/usr/bin/env python3
"""Scan for and fix potential secrets in the codebase.

This script identifies and replaces hardcoded example
API keys, tokens, and other sensitive information.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

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
        if pattern.startswith("*") and filename.endswith(pattern[1:]):
            return True
        elif pattern == filename:
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
    for marker in code_block_markers:
        if marker in content:
            return True

    # Check for common example indicators
    example_indicators = ["example", "sample", "demo", "test", "your-", "placeholder"]
    for indicator in example_indicators:
        if indicator.lower() in line.lower():
            return True

    return False


def find_potential_secrets(file_path: str) -> List[Tuple[str, int, str, str]]:
    """Find potential secrets in a file.

    Returns a list of tuples: (pattern_name, line_number, line_content, secret_value)
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
        print(f"Error processing {file_path}: {e}")
        return []


def fix_secrets_in_file(
    file_path: str, secrets: List[Tuple[str, int, str, str]]
) -> bool:
    """Fix secrets in a file by replacing them with safe values."""
    if not secrets:
        return False

    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        modified = False
        for pattern_name, line_num, _, secret_value in secrets:
            line_index = line_num - 1
            if line_index < len(lines):
                replacement = SAFE_REPLACEMENTS.get(pattern_name, "your-secret-value")
                lines[line_index] = lines[line_index].replace(secret_value, replacement)
                modified = True

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True

        return False
    except Exception as e:
        print(f"Error fixing secrets in {file_path}: {e}")
        return False


def scan_directory(directory: str) -> Dict[str, List[Tuple[str, int, str, str]]]:
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


def safe_log_sensitive_info(
    pattern_name: str, line_num: int, secret_length: int
) -> str:
    """Log sensitive data info without exposing content."""
    return f"  Line {line_num}: {pattern_name} - [REDACTED - {secret_length} chars]"


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


def main():
    """Scan for and fix potential secrets."""
    directory = "."
    if len(sys.argv) > 1:
        directory = sys.argv[1]

    print(f"Scanning directory: {directory}")
    results = scan_directory(directory)

    if not results:
        print("No potential secrets found.")
        return 0

    print(f"Security scan identified sensitive information in {len(results)} files:")
    total_secrets = 0
    fixed_files = 0

    for file_path, secrets in results.items():
        total_secrets += len(secrets)
        safe_path = safe_log_file_path(file_path)
        print(f"\n{safe_path}:")
        for pattern_name, line_num, _, secret in secrets:
            # Use safe logging function to avoid exposing sensitive data
            # Don't pass the actual secret, just its length
            secret_length = len(secret) if secret else 0
            log_message = safe_log_sensitive_info(pattern_name, line_num, secret_length)
            print(log_message)

        # Fix secrets in the file
        if fix_secrets_in_file(file_path, secrets):
            fixed_files += 1
            safe_path = safe_log_file_path(file_path)
            print(f"  ✅ Applied security fixes to {safe_path}")

    print(f"\nSummary: Identified sensitive information in {len(results)} files.")
    print(f"Applied security fixes to {fixed_files} files.")

    return 0 if fixed_files == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
