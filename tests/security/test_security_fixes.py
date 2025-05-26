"""Test script to verify security fixes."""

from __future__ import annotations

import os
import secrets  # For secure random data generation
import stat
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, patch

import pytest
from fix_security_issues import run_security_scan

from common_utils.secrets.audit import generate_report
from common_utils.secrets.cli import handle_list

# Constants for file and directory exclusions
EXCLUDE_DIRS = {
    # Environment directories
    ".venv",
    "venv",
    "env",
    ".env",
    "*venv*",
    "*env*",
    # Cache directories
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".cache",
    # Build directories
    "build",
    "dist",
    "*.egg-info",
    "wheels",
    # Node.js
    "node_modules",
    # IDE specific
    ".idea",
    ".vscode",
    # Source control
    ".git",
    ".github",
    # Documentation
    "docs",
    "docs_source",
    "junit",
    "bin",
    "dev_tools",
    "scripts",
    "tool_templates",
}

EXCLUDE_FILES = {
    # Git files
    ".gitignore",
    ".gitleaks.toml",
    # Config files
    "secrets.sarif.json",
    "pyproject.toml",
    "setup.cfg",
    "tox.ini",
    # Documentation
    "*.md",
    "*.rst",
    "LICENSE",
    "README*",
    # Build artifacts
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.egg",
    # Database
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    # Binary/media files
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.svg",
    "*.ico",
    "*.woff",
    "*.woff2",
    "*.ttf",
    "*.eot",
    "*.mp3",
    "*.mp4",
    "*.mov",
    "*.avi",
    "*.pdf",
    # Archives
    "*.zip",
    "*.tar",
    "*.gz",
    "*.rar",
    # IDE
    "*.swp",
    "*.swo",
}

# Constants for secure file operations
SECURE_FILE_PERMISSIONS = stat.S_IRUSR | stat.S_IWUSR  # 600 permissions
MIN_HASH_LENGTH = 32  # Minimum length for secure hashes


def secure_temp_file() -> tuple[str, tempfile.NamedTemporaryFile]:
    """
    Create a temporary file with secure permissions.

    Returns:
        Tuple[str, NamedTemporaryFile]: Path and file handle

    """
    # Create temp file with secure permissions
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        os.chmod(tmp.name, SECURE_FILE_PERMISSIONS)
        return tmp.name, tmp


def generate_secure_placeholder() -> str:
    """
    Generate a secure placeholder value that's clearly not a real secret.

    Returns:
        str: A secure placeholder value

    """
    return f"[TEST_PLACEHOLDER_{secrets.token_hex(8)}]"


@pytest.fixture
def test_data() -> tuple[str, str, dict[str, list[tuple[str, int, str, str]]]]:
    """
    Create test data fixture.

    Returns:
        Tuple containing:
            - placeholder value (str)
            - file name (str)
            - test data dictionary (Dict[str, List[Tuple[str, int, str, str]]])

    """
    placeholder = generate_secure_placeholder()
    file_name = f"test_file_{secrets.token_hex(8)}.py"
    data = {
        file_name: [
            (
                f"test_credential_{secrets.token_hex(8)}",
                secrets.randbelow(1000) + 1,  # Random line number
                f'auth_item = "{placeholder}"',
                placeholder,
            ),
            (
                f"test_material_{secrets.token_hex(8)}",
                secrets.randbelow(1000) + 1,  # Random line number
                f'auth_data = "{placeholder}"',
                placeholder,
            ),
        ]
    }
    return placeholder, file_name, data


def test_generate_report_no_sensitive_data_in_logs(
    test_data: tuple[str, str, dict[str, Any]],
) -> None:
    """Test that generate_report doesn't log sensitive data."""
    placeholder, file_name, data = test_data

    # Mock logger
    with patch("common_utils.secrets.audit.logger") as mock_logger:
        # Call generate_report
        generate_report(data)

        # Check that the logger was called with safe messages
        for call_args in mock_logger.info.call_args_list:
            msg = call_args[0][0] if call_args[0] else ""

            # Ensure no sensitive data in log messages
            assert placeholder not in msg
            for entry in data[file_name]:
                assert entry[0] not in msg  # credential name
                assert entry[2] not in msg  # auth item line
                assert entry[3] not in msg  # secret value

            # Verify we're using safe logging patterns
            if msg.lower().startswith("found"):
                assert "issues" in msg.lower()
                assert all(c.isascii() and c.isprintable() for c in msg), (
                    "Log message contains non-printable or non-ASCII characters"
                )


def test_generate_report_file_output_no_sensitive_data(
    test_data: tuple[str, str, dict[str, Any]],
) -> None:
    """Test that generate_report doesn't write sensitive data to file."""
    placeholder, file_name, data = test_data
    temp_path = None
    try:
        # Create temporary file with secure permissions
        temp_path, temp_file = secure_temp_file()
        temp_file.close()

        # Call generate_report with file output
        generate_report(data, output_file=temp_path)

        # Read and validate file permissions
        temp_path_obj = Path(temp_path)
        stats = temp_path_obj.stat()
        assert stats.st_mode & 0o777 == SECURE_FILE_PERMISSIONS, (
            "Output file has incorrect permissions"
        )

        # Read and validate file content
        with temp_path_obj.open("r") as f:
            content = f.read()

        # Ensure no sensitive data in file
        assert placeholder not in content
        for entry in data[file_name]:
            assert entry[0] not in content  # credential name
            assert entry[2] not in content  # auth item line
            assert entry[3] not in content  # secret value

        # Check for appropriate masked content
        assert "potential" in content.lower()
        assert all(c.isascii() and c.isprintable() for c in content), (
            "File contains non-printable or non-ASCII characters"
        )

    finally:
        # Secure cleanup
        if temp_path and Path(temp_path).exists():
            os.chmod(temp_path, SECURE_FILE_PERMISSIONS)  # Ensure we can delete it
            Path(temp_path).unlink()


def test_handle_list_no_sensitive_keys() -> None:
    """Test that handle_list doesn't print sensitive key names."""
    # Generate secure test credentials
    credentials = {}
    for _ in range(3):
        key = f"test_access_{secrets.token_hex(8)}"
        credentials[key] = generate_secure_placeholder()

    # Mock args with safe backend
    args = MagicMock()
    args.backend = "env"  # Use environment backend for safer testing

    # Use a single with statement with multiple contexts
    with (
        patch("common_utils.secrets.cli.list_secrets", return_value=credentials),
        patch("builtins.print") as mock_print,
    ):
        # Call handle_list
        handle_list(args)

        # Check that print was called without exposing sensitive data
        for call_args in mock_print.call_args_list:
            msg = call_args[0][0] if call_args[0] else ""

            # Ensure no key names in output
            for key, value in credentials.items():
                assert key not in msg
                assert value not in msg

            # Verify secure hash format
            if msg.startswith("  Secret #"):
                # Hash should be sufficiently long
                assert len(msg) >= MIN_HASH_LENGTH, (
                    f"Secret hash too short: {len(msg)} chars"
                )
                # Hash should be printable ASCII
                assert all(c.isascii() and c.isprintable() for c in msg), (
                    "Hash contains non-printable or non-ASCII characters"
                )


@patch("fix_security_issues.IMPORTED_SECRET_SCANNER", False)
@patch("fix_security_issues.globals")
@patch("subprocess.run")
@pytest.mark.usefixtures("_")
def test_run_security_scan_with_missing_imports(
    mock_subprocess_run: MagicMock, mock_globals: MagicMock
) -> None:
    """Test that run_security_scan handles missing imports gracefully."""
    # Configure mock to simulate missing import
    mock_globals.return_value = {}

    # Configure subprocess mock with safe test data
    mock_subprocess_run.return_value.stdout = (
        '{"test_file.py": [{"type": "test_credential_'
        + secrets.token_hex(8)
        + '", "line_number": '
        + str(secrets.randbelow(1000) + 1)
        + "}]}"
    )

    # Run the security scan
    results = run_security_scan()

    # Verify mock was called and results are returned
    mock_subprocess_run.assert_called_once()
    assert isinstance(results, dict)


def should_exclude_path(path: str) -> bool:
    """
    Check if a path should be excluded based on exclusion rules.

    Args:
        path (str): The path to check

    Returns:
        bool: True if path should be excluded, False otherwise

    """
    # Convert path to use forward slashes for consistency
    normalized_path = path.replace("\\", "/")
    path_parts = normalized_path.split("/")
    file_name = path_parts[-1]

    # Check excluded directories
    if _check_excluded_directories(path_parts):
        return True

    # Check excluded files
    return _check_excluded_files(file_name)


def _check_excluded_directories(path_parts: list[str]) -> bool:
    """Check if any path part matches excluded directories."""
    return any(
        _matches_pattern(exclude, part)
        for part in path_parts
        for exclude in EXCLUDE_DIRS
    )


def _check_excluded_files(file_name: str) -> bool:
    """Check if file name matches excluded files."""
    return any(_matches_pattern(exclude, file_name) for exclude in EXCLUDE_FILES)


def _matches_pattern(pattern: str, text: str) -> bool:
    """Check if text matches the given pattern."""
    if pattern.startswith("*") and pattern.endswith("*"):
        return pattern[1:-1] in text
    if pattern.startswith("*"):
        return text.endswith(pattern[1:])
    if pattern.endswith("*"):
        return text.startswith(pattern[:-1])
    return pattern == text
