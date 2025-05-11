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
from typing import Optional
from typing import cast

import pathspec  # New import

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

# Global variables for gitignore processing
REPO_ROOT: Optional[str] = None
GITIGNORE_SPEC: Optional[pathspec.PathSpec] = None


def find_repo_root(start_path: str) -> str:
    """Finds the repository root by looking for .git directory."""
    current_path = Path(start_path).resolve()
    original_resolved_start = current_path
    # Loop upwards until .git is found or filesystem root is reached
    while True:
        if (current_path / ".git").is_dir():
            return str(current_path)
        parent = current_path.parent
        if parent == current_path:  # Reached filesystem root
            break
        current_path = parent
    logging.warning(
        f"Could not find .git directory root starting from {start_path}. "
        f"Using {original_resolved_start!s} as effective root for .gitignore."
    )
    return str(original_resolved_start)


def load_gitignore_patterns(repo_root_dir: str) -> Optional[pathspec.PathSpec]:
    """Loads and parses .gitignore patterns from the repository root."""
    gitignore_file = Path(repo_root_dir) / ".gitignore"
    if gitignore_file.is_file():
        try:
            with open(gitignore_file, encoding="utf-8", errors="ignore") as f:
                gitignore_lines = f.readlines()
            # Filter out empty lines and comments for pathspec
            gitignore_lines = [
                line
                for line in gitignore_lines
                if line.strip() and not line.strip().startswith("#")
            ]
            if gitignore_lines:
                return pathspec.PathSpec.from_lines(
                    pathspec.patterns.GitWildMatchPattern, gitignore_lines
                )
            else:
                logging.info(
                    f".gitignore at {gitignore_file} is empty or only comments."
                )
        except Exception:
            logging.exception(
                f"Error loading or parsing .gitignore at {gitignore_file}"
            )
    else:
        logging.info(
            f".gitignore not found at {gitignore_file}. No gitignore patterns will be applied from it."
        )
    return None


def should_exclude(
    file_path_abs_str: str, path_relative_to_repo_root: Optional[str]
) -> bool:
    """Check if a file or directory should be excluded from scanning."""
    path_obj_abs = Path(file_path_abs_str)

    # 1. Check against EXCLUDE_DIRS (components of absolute path)
    for part in path_obj_abs.parts:
        if part in EXCLUDE_DIRS:
            logging.debug(
                f"Excluding '{file_path_abs_str}' due to EXCLUDE_DIRS: '{part}'"
            )
            return True

    # 2. Check against EXCLUDE_FILES (filename from absolute path)
    filename = path_obj_abs.name
    for pattern in EXCLUDE_FILES:
        if (
            pattern.startswith("*") and filename.endswith(pattern[1:])
        ) or pattern == filename:
            logging.debug(
                f"Excluding '{file_path_abs_str}' due to EXCLUDE_FILES: '{pattern}'"
            )
            return True

    # 3. New .gitignore check (using path_relative_to_repo_root)
    if GITIGNORE_SPEC and path_relative_to_repo_root:
        # pathspec expects paths to be relative to the .gitignore file's location (repo root)
        # Ensure path_relative_to_repo_root uses '/' for pathspec
        normalized_relative_path = path_relative_to_repo_root.replace(os.sep, "/")
        if GITIGNORE_SPEC.match_file(normalized_relative_path):
            logging.debug(
                f"Excluding '{file_path_abs_str}' due to .gitignore pattern matching '{normalized_relative_path}'"
            )
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
        # Further check if the specific line is within a detected code block
        # This is a simplified check; more robust parsing might be needed for accuracy
        # For now, if any marker exists in content, assume it could be an example.
        # A more precise check would involve finding start/end of blocks.
        return True

    example_indicators = [
        "example",
        "sample",
        "demo",
        "test",
        "your-",
        "placeholder",
        "dummy",
        "mock",
    ]
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
                        secret_value = (
                            match[1]
                            if isinstance(match, tuple) and len(match) > 1
                            else match
                        )

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
                        # For now, let's be more aggressive in examples (commented lines below removed by ERA001 fix)

                        # Store length instead of the actual secret value
                        secret_length = len(str(secret_value)) if secret_value else 0
                        results.append((pattern_name, i + 1, secret_length))
    except Exception:
        logging.exception(f"Error processing file {file_path}")
        return []
    else:  # TRY300
        return results


def validate_file_path(file_path: str) -> str:
    """Validate and normalize a file path to prevent path traversal attacks."""
    try:
        # Resolve symlinks and normalize the path
        normalized_path = str(Path(file_path).resolve())
        # Check if it's a file and exists
        if not Path(normalized_path).is_file():
            logging.warning(f"Path is not a file or does not exist: {normalized_path}")
            return ""
    except Exception:
        logging.exception(f"Error validating file path {file_path}")
        return ""
    else:  # TRY300
        return normalized_path


def read_file_content(file_path: str) -> Optional[tuple[str, list[str]]]:
    """Read file content safely."""
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.splitlines()
    except Exception:
        logging.exception(f"Could not read file {file_path}")
        return None
    else:  # TRY300
        return content, lines


def extract_actual_secrets(  # ARG001: file_path_for_logging removed
    lines: list[str], content: str
) -> list[tuple[str, int, str]]:
    """Extract actual secrets from file content."""
    actual_secrets = []
    for i, line in enumerate(lines):
        for pattern_name, pattern in PATTERNS.items():
            matches = pattern.findall(line)
            if not matches:
                continue

            for match in matches:
                secret_value = (
                    match[1] if isinstance(match, tuple) and len(match) > 1 else match
                )
                if isinstance(secret_value, tuple):
                    secret_value = secret_value[0] if secret_value else ""

                if is_example_code(content, line):
                    # Commented line removed by ERA001 fix
                    continue

                actual_secrets.append((pattern_name, i, str(secret_value)))
    return actual_secrets


def apply_replacements(
    lines: list[str], actual_secrets: list[tuple[str, int, str]]
) -> bool:
    """Apply replacements to the lines."""
    modified = False
    for pattern_name, line_index, secret_value in actual_secrets:
        if line_index < len(lines):
            replacement = SAFE_REPLACEMENTS.get(pattern_name, "your-secret-value")
            # Ensure we replace the specific secret_value found
            if secret_value in lines[line_index]:
                lines[line_index] = lines[line_index].replace(secret_value, replacement)
                modified = True
            else:
                logging.warning(
                    f"Secret '{secret_value}' not found in line {line_index} for replacement. Line content: {lines[line_index]}"
                )
    return modified


def write_file_with_security(file_path: str, lines: list[str]) -> bool:
    """Write file content with security measures."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            # Write lines, ensuring they end with a newline
            for i, line_content in enumerate(lines):
                f.write(line_content)
                if (
                    i < len(lines) - 1
                ):  # Avoid adding extra newline at EOF if last line was empty
                    f.write("\n")
            if lines and lines[-1]:  # Add newline if last line had content
                f.write("\n")

        if os.name != "nt":  # Unix-like systems
            try:
                os.chmod(file_path, 0o600)
            except Exception as e_chmod:
                logging.warning(
                    f"Could not set secure permissions on {file_path}: {e_chmod}"
                )
    except Exception:
        logging.exception(f"Error writing file {file_path}")
        return False
    else:  # TRY300
        return True


def fix_secrets_in_file(
    file_path: str, secrets_metadata: list[tuple[str, int, int]]
) -> bool:
    """Fix secrets in a file by replacing them with safe values."""
    if (
        not secrets_metadata
    ):  # secrets_metadata contains (pattern_name, line_num, secret_length)
        return False

    # Commented lines removed by ERA001 fix

    # Read file content
    read_result = read_file_content(file_path)  # file_path is absolute
    if read_result is None:
        return False
    content, lines = read_result

    # Extract actual secrets to be replaced
    actual_secrets_to_replace = extract_actual_secrets(
        lines, content
    )  # ARG001: file_path_for_logging removed
    if not actual_secrets_to_replace:
        logging.info(
            f"No actionable secrets found for replacement in {file_path} after example checks."
        )
        return False

    # Apply replacements
    modified = apply_replacements(lines, actual_secrets_to_replace)

    if modified:
        logging.info(f"Fixing secrets in {file_path}")
        if write_file_with_security(file_path, lines):
            logging.info(f"Successfully fixed secrets in {file_path}")
            return True
        else:
            logging.error(f"Failed to write fixes to {file_path}")
            return False
    return False


def scan_directory(directory: str) -> dict[str, list[tuple[str, int, int]]]:  # noqa: C901
    """Scan a directory recursively for potential secrets."""
    results = {}
    global REPO_ROOT, GITIGNORE_SPEC  # noqa: PLW0603

    current_scan_path_abs = str(Path(directory).resolve())

    if REPO_ROOT is None:
        REPO_ROOT = find_repo_root(current_scan_path_abs)
        logging.info(f"Determined repository root: {REPO_ROOT}")
    if GITIGNORE_SPEC is None:
        GITIGNORE_SPEC = load_gitignore_patterns(REPO_ROOT)

    for root, dirs, files in os.walk(current_scan_path_abs, topdown=True):
        # Filter dirs in place using EXCLUDE_DIRS. .gitignore will handle more specific nested ignores.
        # This broad exclusion is for os.walk performance.
        dirs[:] = [
            d
            for d in dirs
            if d not in EXCLUDE_DIRS and not (Path(root) / d / ".git").is_dir()
        ]

        for file_name in files:
            file_path_abs_str = str(Path(root) / file_name)
            path_relative_to_repo_root_str = None

            if REPO_ROOT:  # Only try to make relative if REPO_ROOT was found
                try:
                    path_relative_to_repo_root_str = str(
                        Path(file_path_abs_str).relative_to(REPO_ROOT)
                    )
                except ValueError:
                    logging.debug(
                        f"File {file_path_abs_str} is outside the determined repo root {REPO_ROOT}. "
                        ".gitignore from repo root may not apply."
                    )

            if should_exclude(file_path_abs_str, path_relative_to_repo_root_str):
                continue

            if not is_text_file(file_path_abs_str):
                continue

            # Validate file path before finding secrets
            validated_path = validate_file_path(file_path_abs_str)
            if not validated_path:
                logging.warning(
                    f"Skipping invalid or non-existent file: {file_path_abs_str}"
                )
                continue

            secrets = find_potential_secrets(
                validated_path
            )  # Pass absolute, validated path
            if secrets:
                results[validated_path] = secrets  # Store with absolute, validated path
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


def main() -> int:  # noqa: C901, PLR0912
    """Scan for and fix potential secrets."""
    directory_to_scan = "."
    scan_only_mode = "--scan-only" in sys.argv  # Check if --scan-only is passed

    # Basic argument parsing for directory if provided
    # More robust parsing is in fix_security_issues.py
    args_iter = iter(sys.argv[1:])
    for arg in args_iter:
        if arg == "--scan-only":
            continue  # Already handled
        elif arg == "--exclude":
            try:
                # This script doesn't directly use --exclude from its own args,
                # it's passed by fix_security_issues.py to its own run_security_scan
                # For standalone run, EXCLUDE_DIRS is used.
                next(args_iter)  # Consume the value for exclude
            except StopIteration:
                logging.exception("--exclude requires a value")
                return 1
        elif not arg.startswith("--"):
            directory_to_scan = arg
            break  # Assume first non-option arg is directory

    logging.info(f"Starting secret scan in directory: {directory_to_scan}")
    if scan_only_mode:
        logging.info("Running in scan-only mode. No files will be modified.")

    results = scan_directory(directory_to_scan)

    if not results:
        logging.info("No potential secrets found.")
        # Output an empty SARIF if in scan_only mode and fix_security_issues.py expects it
        if scan_only_mode and "fix_security_issues.py" in sys.argv[0]:  # Heuristic
            generate_empty_sarif("security-report.sarif")
        return 0

    total_secrets_found = sum(len(s) for s in results.values())
    logging.info(
        f"Found {total_secrets_found} total potential secrets in {len(results)} files."
    )

    fixed_files_count = 0
    successfully_processed_files = 0

    if not scan_only_mode:
        for file_path, secrets_in_file in results.items():
            if fix_secrets_in_file(file_path, secrets_in_file):  # file_path is absolute
                fixed_files_count += 1
            successfully_processed_files += (
                1  # Count even if no fix was made but processed
            )
        logging.info(
            f"Attempted to fix secrets. {fixed_files_count} files were modified."
        )
    else:
        # In scan-only mode, just report what was found
        for file_path, secrets_in_file in results.items():
            logging.info(f"File: {safe_log_file_path(file_path)}")
            for pattern_name, line_num, _ in secrets_in_file:
                logging.info(safe_log_sensitive_info(pattern_name, line_num))

    # SARIF report generation (typically handled by fix_security_issues.py)
    # If this script is run directly and scan_only, it might output its own SARIF.
    # The main() in fix_security_issues.py calls its own generate_sarif_report.
    # This script's main() also has SARIF generation logic. We should ensure only one is active
    # or they output to different files if both are needed.
    # For now, let's assume fix_security_issues.py handles the final SARIF.
    # However, if this script is run standalone, its SARIF generation is useful.

    # If this script is called by fix_security_issues.py, it might output JSON for it to consume.
    # The subprocess call in fix_security_issues.py expects JSON if import fails.
    if (
        not scan_only_mode and "fix_security_issues.py" not in sys.argv[0]
    ):  # If run standalone and not scan_only
        logging.info("Standalone run (not scan-only): Fixes applied.")

    # If called by fix_security_issues.py via subprocess, it should output JSON
    # This part is tricky because the script has dual use.
    # Let's assume if not imported (IMPORTER_SECRET_SCANNER is False in fix_security_issues.py),
    # then this script's stdout is captured.
    # The current main() in this script doesn't print JSON to stdout.
    # It generates a SARIF file directly.

    # Let's refine the return logic.
    # If fixes were attempted, success means all found items in all files were addressed.
    # This is hard to measure perfectly without knowing if every single secret instance was replaceable.
    # A simpler metric: if any file was modified, it implies fixes happened.
    if not scan_only_mode:
        return 0 if fixed_files_count > 0 or total_secrets_found == 0 else 1
    else:  # scan_only_mode
        # For scan_only, return 0 if no secrets, or if it's just reporting.
        # The GitHub action might use the SARIF for pass/fail.
        # If fix_security_issues.py uses this script's SARIF, then its content matters.
        # The SARIF generation in this script's main:
        try:
            # This SARIF generation was outside scan_only_mode check.
            # It should probably only run if this script is the main one generating the report.
            # Let's assume fix_security_issues.py handles the SARIF if it calls this.
            # If run standalone:
            if (
                "fix_security_issues.py" not in sys.argv[0]
            ):  # A bit of a hack to check caller
                generate_sarif_from_results(
                    results, "fix_potential_secrets_report.sarif"
                )
                logging.info(
                    "Standalone SARIF report generated: fix_potential_secrets_report.sarif"
                )

        except Exception:
            logging.exception("Error generating standalone SARIF report")  # TRY401
            return 1  # Error in reporting

    return 0  # Default to success for scan_only if it reaches here.


def generate_empty_sarif(output_file: str) -> None:
    """Generates an empty SARIF report."""
    base = "https://raw.githubusercontent.com/"
    org = "oasis-tcs/sarif-spec/"
    path = "master/Schemata/sarif-schema-2.1.0.json"
    schema_url = base + org + path
    sarif_report: dict[str, Any] = {
        "$schema": schema_url,
        "version": "2.1.0",
        "runs": [{"tool": {"driver": {"name": "SecretScanner"}}, "results": []}],
    }
    try:
        with open(output_file, "w") as f:
            json.dump(sarif_report, f, indent=2)
        logging.info(f"Empty SARIF report saved to {output_file}")
    except Exception:
        logging.exception("Error writing empty SARIF report")  # TRY401


def generate_sarif_from_results(
    results: dict[str, list[tuple[str, int, int]]], output_file: str
) -> None:
    """Generates SARIF report from results."""
    base = "https://raw.githubusercontent.com/"
    org = "oasis-tcs/sarif-spec/"
    path = "master/Schemata/sarif-schema-2.1.0.json"
    schema_url = base + org + path
    sarif_report: dict[str, Any] = {
        "$schema": schema_url,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "SecretScanner (fix_potential_secrets.py)",
                        "informationUri": "https://github.com/anchapin/pAIssive_income",  # Placeholder
                        "rules": [
                            {
                                "id": "custom-secret-detection",
                                "shortDescription": {
                                    "text": "Detects hardcoded secrets using custom patterns."
                                },
                                "defaultConfiguration": {"level": "error"},
                            }
                        ],
                    }
                },
                "results": [],
            }
        ],
    }
    sarif_results_list = cast(list[dict[str, Any]], sarif_report["runs"][0]["results"])
    for file_path, secrets_in_file in results.items():
        safe_file_uri = Path(file_path).as_uri()  # SARIF expects URI
        for pattern_name, line_num, _secret_length in secrets_in_file:
            sarif_results_list.append({
                "ruleId": "custom-secret-detection",  # Could be pattern_name for more specific rule IDs
                "level": "error",  # Or "warning" depending on confidence
                "message": {
                    "text": f"Potential hardcoded secret: '{pattern_name}' detected."
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": safe_file_uri},
                            "region": {"startLine": line_num},
                        }
                    }
                ],
                "properties": {
                    "securitySeverity": "high",
                    "pattern_type": pattern_name,
                },
            })
    try:
        with open(output_file, "w") as f:
            json.dump(sarif_report, f, indent=2)
    except Exception:
        logging.exception(f"Error writing SARIF report to {output_file}")  # TRY401


if __name__ == "__main__":
    # This script can be run standalone or be imported by fix_security_issues.py
    # If run standalone, its main() is executed.
    # If imported, fix_security_issues.py calls scan_directory().
    # The sys.exit is important for standalone execution.
    sys.exit(main())
