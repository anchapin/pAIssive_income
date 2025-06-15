"""Base security test module for pAIssive income platform."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import secrets
import stat
import tempfile
from pathlib import Path
from typing import Any, Union

# Configure logging with secure defaults
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message).100s",  # Limit message length
)
logger = logging.getLogger(__name__)

# Constants for secure operations
SECURE_FILE_PERMISSIONS = stat.S_IRUSR | stat.S_IWUSR  # 600 permissions
SECURE_DIR_PERMISSIONS = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR  # 700 permissions
MIN_ENTROPY_BITS = 128  # Minimum entropy for secure random values
DEFAULT_ENCODING = "utf-8"


class BaseSecurityTest:
    """Base class for security tests with common security utilities."""

    @staticmethod
    def secure_temp_dir() -> Path:
        """Create a temporary directory with secure permissions."""
        tmp_dir = Path(tempfile.mkdtemp())
        os.chmod(tmp_dir, SECURE_DIR_PERMISSIONS)
        return tmp_dir

    @staticmethod
    def secure_temp_file(suffix: Union[str, None] = None) -> tuple[Path, Any]:
        """
        Create a temporary file with secure permissions.

        Args:
            suffix: Optional file suffix

        Returns:
            tuple[Path, file]: Path and file handle

        """
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.chmod(path, SECURE_FILE_PERMISSIONS)
        return Path(path), os.fdopen(fd, "w+")

    @staticmethod
    def generate_secure_token(bits: int = MIN_ENTROPY_BITS) -> str:
        """
        Generate a cryptographically secure random token.

        Args:
            bits: Entropy bits (default: 128)

        Returns:
            str: Secure token

        """
        num_bytes = (bits + 7) // 8  # Round up to nearest byte
        return secrets.token_hex(num_bytes)

    @staticmethod
    def secure_hash(data: str | bytes) -> str:
        """
        Create a secure hash of data.

        Args:
            data: Data to hash

        Returns:
            str: Secure hash

        """
        if isinstance(data, str):
            data = data.encode(DEFAULT_ENCODING)
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def write_secure_file(path: Path | str, content: str | bytes) -> None:
        """
        Write content to a file with secure permissions.

        Args:
            path: Path to write to
            content: Content to write

        """
        path = Path(path)
        mode = "wb" if isinstance(content, bytes) else "w"
        # Create with restricted permissions
        with os.fdopen(
            os.open(
                path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, SECURE_FILE_PERMISSIONS
            ),
            mode,
        ) as f:
            f.write(content)

    @staticmethod
    def read_secure_json(path: Union[Path, str]) -> Any:
        """
        Read and parse JSON from a file, verifying permissions.

        Args:
            path: Path to read from

        Returns:
            Any: Parsed JSON data

        """
        path = Path(path)
        if not path.exists():
            msg = f"File not found: {path}"
            raise FileNotFoundError(msg)

        # Check permissions
        stats = path.stat()
        if stats.st_mode & 0o777 != SECURE_FILE_PERMISSIONS:
            msg = f"Insecure file permissions: {stats.st_mode & 0o777:o}"
            raise PermissionError(msg)

        # Read and parse
        with path.open("r", encoding=DEFAULT_ENCODING) as f:
            return json.loads(f.read())

    def cleanup_temp_files(self, *paths: Union[Path, str]) -> None:
        """
        Safely cleanup temporary files.

        Args:
            *paths: Paths to clean up

        """
        for path_str in paths:
            path = Path(path_str)
            if path.exists():
                os.chmod(path, SECURE_FILE_PERMISSIONS)  # Ensure we can delete
                path.unlink()

    def cleanup_temp_dirs(self, *paths: Union[Path, str]) -> None:
        """
        Safely cleanup temporary directories.

        Args:
            *paths: Paths to clean up

        """
        for path_str in paths:
            path = Path(path_str)
            if path.exists() and path.is_dir():
                os.chmod(path, SECURE_DIR_PERMISSIONS)  # Ensure we can delete
                for child in path.glob("**/*"):
                    if child.is_file():
                        os.chmod(child, SECURE_FILE_PERMISSIONS)
                        child.unlink()
                    elif child.is_dir():
                        self.cleanup_temp_dirs(child)
                path.rmdir()
