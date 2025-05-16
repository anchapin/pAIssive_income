"""Secure logging utilities to prevent sensitive information from being logged.

This module provides functions to mask sensitive information in logs, such as access
credentials, authentication materials, and other sensitive data.
"""

import logging
import re

from re import Pattern
from typing import Any
from typing import Optional

# List of sensitive field names to mask in logs
SENSITIVE_FIELDS: list[str] = [
    "auth_credential",
    "access_credential",
    "auth_material",
    "sensitive_data",
    "auth_code",
    "crypto_material",
    "private_material",
    "access_material",
    "refresh_material",
    "auth_signature",
    "verification_data",
    "security_salt",
    "identity_code",
    "personal_id",
    "payment_info",
    "card_info",
    "security_material",
]

# Regex patterns to detect sensitive information
PATTERNS: dict[str, Pattern] = {
    "credential_type_1": re.compile(
        (
            r'(access[_-]?credential|api_material)["\']?\s*[:=]\s*["\']?'
            r'([a-zA-Z0-9_\-\.]{10,})["\']?'
        ),
        re.IGNORECASE,
    ),
    "auth_type_1": re.compile(
        (r'(auth_material|credential)["\']?\s*[:=]\s*["\']?' r'([^"\'\s]{3,})["\']?'),
        re.IGNORECASE,
    ),
    "auth_type_2": re.compile(
        (
            r'(auth_code|material|access_material)["\']?\s*[:=]\s*["\']?'
            r'([a-zA-Z0-9_\-\.]{10,})["\']?'
        ),
        re.IGNORECASE,
    ),
    "sensitive_type_1": re.compile(
        (
            r'(sensitive_material|private_material)["\']?\s*[:=]\s*["\']?'
            r'([a-zA-Z0-9_\-\.]{10,})["\']?'
        ),
        re.IGNORECASE,
    ),
}


def is_sensitive_key(key: str) -> bool:
    """Check if a key name contains sensitive information patterns.

    Args:
    ----
        key: The key name to check

    Returns:
    -------
        bool: True if the key appears to reference sensitive information

    """
    if not key:
        return False

    key_lower = key.lower()
    # Check against our predefined list of sensitive field names
    for sensitive_field in SENSITIVE_FIELDS:
        if sensitive_field in key_lower:
            return True

    # Check for common sensitive patterns
    sensitive_terms: list[str] = [
        "password",
        "token",
        "secret",
        "key",
        "auth",
        "credential",
        "private",
        "security",
        "access",
        "api",
        "cert",
    ]

    return any(term in key_lower for term in sensitive_terms)


def mask_sensitive_data(data: Any, mask_char: str = "*", visible_chars: int = 4) -> Any:
    """Mask sensitive data in logs to prevent logging of sensitive information.

    Applies masking to sensitive information while preserving some visibility
    for debugging purposes.

    Args:
    ----
        data: The data to mask. Can be a string, dict, list, or other types
        mask_char: The character to use for masking. Default is "*"
        visible_chars: Number of characters to show at start and end. Default is 4

    Returns:
    -------
        Any: The masked data with sensitive information hidden.
        Returns the same type as the input data.

    """
    if data is None:
        return None

    if isinstance(data, str):
        # Check if the string matches any of our sensitive patterns
        for _, pattern in PATTERNS.items():
            data = _mask_pattern(data, pattern, mask_char, visible_chars)
        return data

    elif isinstance(data, dict):
        # Recursively mask values in dictionary
        dict_result: dict[str, Any] = {}
        for k, v in data.items():
            dict_result[k] = _mask_if_sensitive(k, v, mask_char, visible_chars)
        return dict_result  # Explicitly return a Dict[str, Any]

    elif isinstance(data, list):
        # Recursively mask values in list
        list_result: list[Any] = [
            mask_sensitive_data(item, mask_char, visible_chars) for item in data
        ]
        return list_result

    # For any other type, return as is
    return data


def _mask_if_sensitive(
    key: str, value: Any, mask_char: str = "*", visible_chars: int = 4
) -> Any:
    """Check if a key is sensitive and mask its value if needed.

    Examines the key for sensitive terms and applies masking if necessary.

    Args:
    ----
        key: The dictionary key to check
        value: The value to potentially mask
        mask_char: The character to use for masking
        visible_chars: Number of characters to leave visible

    Returns:
    -------
        The original value or a masked version if the key is sensitive

    """
    if not isinstance(value, str):
        return mask_sensitive_data(value, mask_char, visible_chars)

    # Check if the key contains any sensitive terms
    for sensitive_field in SENSITIVE_FIELDS:
        if sensitive_field in key.lower():
            return _mask_string(value, mask_char, visible_chars)

    return mask_sensitive_data(value, mask_char, visible_chars)


def _mask_string(value: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask a string, showing only the first and last few characters.

    Args:
    ----
        value: The string to mask
        mask_char: The character to use for masking
        visible_chars: Number of characters to leave visible at beginning and end

    Returns:
    -------
        The masked string

    """
    if not value or len(value) <= (visible_chars * 2):
        return mask_char * len(value) if value else value

    prefix = value[:visible_chars]
    suffix = value[-visible_chars:] if visible_chars > 0 else ""
    masked_length = len(value) - (len(prefix) + len(suffix))

    return f"{prefix}{mask_char * masked_length}{suffix}"


def _mask_pattern(
    text: str, pattern: Pattern, mask_char: str = "*", visible_chars: int = 4
) -> str:
    """Mask text that matches a specific regex pattern.

    Args:
    ----
        text: The text to process
        pattern: The regex pattern to match
        mask_char: The character to use for masking
        visible_chars: Number of characters to leave visible

    Returns:
    -------
        The text with sensitive information masked

    """

    def _replacer(match: re.Match[str]) -> str:
        full_match: str = match.group(0)
        sensitive_value: str = match.group(2)

        if not sensitive_value:
            return full_match

        masked_value: str = _mask_string(sensitive_value, mask_char, visible_chars)
        return full_match.replace(sensitive_value, masked_value)

    result = pattern.sub(_replacer, text)
    return str(result)


class SecureLogger:
    """A wrapper around the standard logger that masks sensitive information."""

    def __init__(self, name: str) -> None:
        """Initialize the secure logger.

        Args:
            name: The name of the logger
        """
        self.logger = logging.getLogger(name)

    def has_handlers(self) -> bool:
        """Check if this logger has any handlers configured.

        Returns:
            bool: True if this logger has handlers configured
        """
        return self.logger.hasHandlers()

    def handle(self, record: logging.LogRecord) -> bool:
        """Call the handlers for the specified record.

        Args:
            record: The log record to handle

        Returns:
            bool: True if the message was handled
        """
        return self.logger.handle(record)

    def make_record(
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: str,
        args: tuple,
        exc_info: Optional[tuple],
        func: Optional[str] = None,
        extra: Optional[dict[str, Any]] = None,
        sinfo: Optional[str] = None,
    ) -> logging.LogRecord:
        """Make a LogRecord.

        Args:
            name: The logger name
            level: The logging level
            fn: The filename
            lno: The line number
            msg: The message
            args: The message arguments
            exc_info: The exception info
            func: The function name
            extra: Extra info
            sinfo: Stack info

        Returns:
            logging.LogRecord: The created log record
        """
        # Apply the sensitive data masking before creating the record
        msg = mask_sensitive_data(str(msg))
        return self.logger.makeRecord(
            name, level, fn, lno, msg, args, exc_info, func, extra, sinfo
        )

    # Standard logging compatibility aliases
    makeRecord = make_record  # noqa: N815

    def find_caller(
        self, stack_info: bool = False, stacklevel: int = 1
    ) -> tuple[str, int, str, Optional[str]]:
        """Find the caller's source file and line number."""
        result: tuple[str, int, str, Optional[str]] = self.logger.findCaller(
            stack_info, stacklevel
        )
        return result

    # Standard logging compatibility aliases
    findCaller = find_caller  # noqa: N815

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message with sensitive information masked.

        Args:
            msg: The message to log
            args: Arguments for message formatting
            kwargs: Keyword arguments for logging configuration
        """
        msg = mask_sensitive_data(msg)
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message with sensitive information masked.

        Args:
            msg: The message to log
            args: Arguments for message formatting
            kwargs: Keyword arguments for logging configuration
        """
        msg = mask_sensitive_data(msg)
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message with sensitive information masked.

        Args:
            msg: The message to log
            args: Arguments for message formatting
            kwargs: Keyword arguments for logging configuration
        """
        msg = mask_sensitive_data(msg)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message with sensitive information masked.

        Args:
            msg: The message to log
            args: Arguments for message formatting
            kwargs: Keyword arguments for logging configuration
        """
        msg = mask_sensitive_data(msg)
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a critical message with sensitive information masked.

        Args:
            msg: The message to log
            args: Arguments for message formatting
            kwargs: Keyword arguments for logging configuration
        """
        msg = mask_sensitive_data(msg)
        self.logger.critical(msg, *args, **kwargs)

    # Standard aliases
    warn = warning
    fatal = critical


def get_secure_logger(name: str) -> SecureLogger:
    """Get a secure logger that masks sensitive information.

    Args:
    ----
        name: The name of the logger

    Returns:
    -------
        A SecureLogger instance

    """
    return SecureLogger(name)
