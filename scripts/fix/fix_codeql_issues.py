#!/usr/bin/env python3


# Configure logging
logger = logging.getLogger(__name__)

"""
Script to fix CodeQL issues in the codebase.

This script addresses common security issues detected by CodeQL:
1. Hardcoded credentials
2. Clear-text logging of sensitive information
3. Clear-text storage of sensitive information
4. Insecure regular expressions
"""

import logging
import re
import sys
from pathlib import Path


# Patterns to detect potential security issues
PATTERNS = {
    # Hardcoded credentials
    "hardcoded_credentials": re.compile(
        r'(password|token|secret|key|credential)["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        re.IGNORECASE,
    ),
    # Clear-text logging
    "clear_text_logging": re.compile(
        r'(log|logger)\.(debug|info|warning|error|critical|exception)\s*\(\s*f?["\'].*?'
        r'(password|token|secret|key|credential).*?["\']',
        re.IGNORECASE,
    ),
    # Clear-text storage
    "clear_text_storage": re.compile(
        r"(save|store|write|dump|json\.dumps)\s*\(\s*.*?"
        r"(password|token|secret|key|credential).*?\)",
        re.IGNORECASE,
    ),
    # Insecure regular expressions (missing anchors)
    "insecure_regex": re.compile(
        r'(re\.(match|search|findall|finditer|sub|subn))\s*\(\s*r?["\'](?!\^)([^"\']+)(?!\$)["\']',
        re.IGNORECASE,
    ),
}

# File extensions to scan
EXTENSIONS_TO_SCAN = {".py", ".js", ".ts", ".jsx", ".tsx"}

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
}


def should_scan_file(file_path: str) -> bool:
    """
    Check if a file should be scanned.

    Args:
        file_path: Path to the file

    Returns:
        bool: True if the file should be scanned, False otherwise

    """
    # Check if the file has an extension we want to scan
    file_path_obj = Path(file_path)
    ext = file_path_obj.suffix
    if ext.lower() not in EXTENSIONS_TO_SCAN:
        return False

    # Check if the file is in a directory we want to exclude
    parts = Path(file_path).parts
    return all(part not in DIRS_TO_EXCLUDE for part in parts)


def fix_hardcoded_credentials(line: str) -> str:
    """
    Fix hardcoded credentials in a line.

    Args:
        line: Line to fix

    Returns:
        str: Fixed line

    """
    # Replace hardcoded credentials with environment variables
    pattern = PATTERNS["hardcoded_credentials"]
    matches = pattern.findall(line)

    if not matches:
        return line

    fixed_line = line
    for match in matches:
        credential_type, credential_value = match

        # Skip test credentials
        if any(
            test_word in credential_value.lower()
            for test_word in ["test", "example", "sample", "dummy", "mock"]
        ):
            continue

        # Replace with environment variable reference
        env_var_name = f"{credential_type.upper()}"
        replacement = f'{credential_type}=os.environ.get("{env_var_name}")'
        fixed_line = fixed_line.replace(
            f'{credential_type}="{credential_value}"', replacement
        )
        fixed_line = fixed_line.replace(
            f"{credential_type}='{credential_value}'", replacement
        )
        fixed_line = fixed_line.replace(
            f'{credential_type}:"{credential_value}"',
            f'{credential_type}:os.environ.get("{env_var_name}")',
        )
        fixed_line = fixed_line.replace(
            f"{credential_type}:'{credential_value}'",
            f"{credential_type}:os.environ.get('{env_var_name}')",
        )

    return fixed_line


def fix_clear_text_logging(line: str) -> str:
    """
    Fix clear-text logging of sensitive information.

    Args:
        line: Line to fix

    Returns:
        str: Fixed line

    """
    # Replace sensitive information in logging with masked values
    pattern = PATTERNS["clear_text_logging"]
    match = pattern.search(line)

    if not match:
        return line

    # Add masking for sensitive information
    fixed_line = line
    for sensitive_word in ["password", "token", "secret", "key", "credential"]:
        if sensitive_word.lower() in line.lower():
            # Replace with masked version in f-strings
            fixed_line = re.sub(
                rf'f["\'].*?({sensitive_word})\s*=\s*([^{{}}"\']+).*?["\']',
                r'f"\1=***MASKED***"',
                fixed_line,
                flags=re.IGNORECASE,
            )

            # Replace with masked version in regular strings
            fixed_line = re.sub(
                rf'["\'].*?({sensitive_word})\s*=\s*.*?["\']',
                r'"\1=***MASKED***"',
                fixed_line,
                flags=re.IGNORECASE,
            )

    return fixed_line


def fix_clear_text_storage(line: str) -> str:
    """
    Fix clear-text storage of sensitive information.

    Args:
        line: Line to fix

    Returns:
        str: Fixed line

    """
    # Replace sensitive information in storage with masked values
    pattern = PATTERNS["clear_text_storage"]
    match = pattern.search(line)

    if not match:
        return line

    # Add masking for sensitive information
    fixed_line = line
    for sensitive_word in ["password", "token", "secret", "key", "credential"]:
        if sensitive_word.lower() in line.lower():
            # Add masking before storage
            fixed_line = re.sub(
                rf"({sensitive_word})\s*=\s*([^;,)]+)",
                r'\1 = "***MASKED***" if \2 else None  # Masked for security',
                fixed_line,
                flags=re.IGNORECASE,
            )

    return fixed_line


def fix_insecure_regex(line: str) -> str:
    """
    Fix insecure regular expressions.

    Args:
        line: Line to fix

    Returns:
        str: Fixed line

    """
    # Add anchors to regular expressions
    pattern = PATTERNS["insecure_regex"]
    match = pattern.search(line)

    if not match:
        return line

    # Add anchors to regex patterns
    fixed_line = line
    # Define variables for match indices
    function_index = 0
    pattern_index = 2
    min_match_length = 3

    matches = pattern.findall(line)
    for match in matches:
        # Ensure match has enough elements and they are strings
        if (
            len(match) >= min_match_length
            and isinstance(match[function_index], str)
            and isinstance(match[pattern_index], str)
        ):
            re_function, regex_pattern = match[function_index], match[pattern_index]
        else:
            continue

        # Skip if it's already using a variable or has anchors
        if not regex_pattern or "^" in regex_pattern or "$" in regex_pattern:
            continue

        # Add anchors to the pattern
        anchored_pattern = f"^{regex_pattern}$"
        fixed_line = fixed_line.replace(
            f'{re_function}(r"{regex_pattern}"', f'{re_function}(r"{anchored_pattern}"'
        )
        fixed_line = fixed_line.replace(
            f"{re_function}(r'{regex_pattern}'", f"{re_function}(r'{anchored_pattern}'"
        )
        fixed_line = fixed_line.replace(
            f'{re_function}("{regex_pattern}"', f'{re_function}("^{regex_pattern}$"'
        )
        fixed_line = fixed_line.replace(
            f"{re_function}('{regex_pattern}'", f"{re_function}('^{regex_pattern}$'"
        )

    return fixed_line


def fix_file(file_path: str) -> bool:
    """
    Fix security issues in a file.

    Args:
        file_path: Path to the file

    Returns:
        bool: True if the file was modified, False otherwise

    """
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            lines = f.readlines()

        modified = False
        fixed_lines = []

        for line in lines:
            fixed_line = line

            # Apply fixes
            fixed_line = fix_hardcoded_credentials(fixed_line)
            fixed_line = fix_clear_text_logging(fixed_line)
            fixed_line = fix_clear_text_storage(fixed_line)
            fixed_line = fix_insecure_regex(fixed_line)

            fixed_lines.append(fixed_line)
            if fixed_line != line:
                modified = True

        if modified:
            with Path(file_path).open("w", encoding="utf-8") as f:
                f.writelines(fixed_lines)
            logger.info("Fixed security issues in %s", file_path)
            return modified
    except Exception:
        logger.exception("Error processing %s", file_path)
        return False

    return modified


def main() -> None:
    """Execute the main function to fix CodeQL issues."""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    # Get the directory to scan
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    logger.info("Scanning directory: %s", root_dir)

    # Track statistics
    stats = {
        "files_scanned": 0,
        "files_modified": 0,
    }

    # Walk through the directory
    import os  # Import os here for os.walk

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in DIRS_TO_EXCLUDE]

        for filename in filenames:
            file_path = Path(dirpath) / filename

            if should_scan_file(str(file_path)):
                stats["files_scanned"] += 1
                if fix_file(str(file_path)):
                    stats["files_modified"] += 1

    # Print statistics
    logger.info("Scanned %d files", stats["files_scanned"])
    logger.info("Modified %d files", stats["files_modified"])


if __name__ == "__main__":
    main()
