"""
Secure logging utilities to prevent sensitive information from being logged.

This module provides functions to mask sensitive information in logs, such as access
credentials, authentication materials, and other sensitive data.
"""

from __future__ import annotations

import logging
import re
from re import Pattern
from typing import Any, Optional

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
    # Added patterns to detect log injection attempts
    "log_injection_newlines": re.compile(r'[\r\n]+'),
    "log_injection_control_chars": re.compile(r'[\x00-\x1F\x7F]'),
    "password_pattern": re.compile(r'(password)["\']?\s*[:=]\s*["\']?([^"\'\s]{3,})["\']?', re.IGNORECASE),
    "api_key_pattern": re.compile(r'(api[_-]?key)["\']?\s*[:=]\s*["\']?([^"\'\s]{3,})["\']?', re.IGNORECASE),
    "token_pattern": re.compile(r'(token)["\']?\s*[:=]\s*["\']?([^"\'\s]{3,})["\']?', re.IGNORECASE),
    "secret_pattern": re.compile(r'(secret)["\']?\s*[:=]\s*["\']?([^"\'\s]{3,})["\']?', re.IGNORECASE),
}


def is_sensitive_key(key: str) -> bool:
    """
    Check if a key name contains sensitive information patterns.

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


def prevent_log_injection(data: object) -> object:
    """
    Prevent log injection attacks by sanitizing input data.

    This function removes or escapes characters that could be used for log injection attacks,
    such as newlines, carriage returns, and other control characters.

    Args:
        data: The data to sanitize. Can be a string, dict, list, or other types.

    Returns:
        The sanitized data with potentially dangerous characters removed or escaped.
        Returns the same type as the input data.
    """
    if data is None:
        return None

    if isinstance(data, str):
        # Replace newlines and control characters
        sanitized = PATTERNS["log_injection_newlines"].sub(" [FILTERED] ", data)
        sanitized = PATTERNS["log_injection_control_chars"].sub(" [FILTERED] ", sanitized)
        return sanitized

    if isinstance(data, dict):
        # Recursively sanitize values in dictionary
        return {k: prevent_log_injection(v) for k, v in data.items()}

    if isinstance(data, list):
        # Recursively sanitize values in list
        return [prevent_log_injection(item) for item in data]

    # For any other type, return as is
    return data


def mask_sensitive_data(
    data: object, mask_char: str = "*", visible_chars: int = 4
) -> object:
    """
    Mask sensitive data in logs to prevent logging of sensitive information.

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

    # First prevent log injection
    data = prevent_log_injection(data)

    if isinstance(data, str):
        # Check if the string matches any of our sensitive patterns
        for pattern in PATTERNS.values():
            data = _mask_pattern(data, pattern, mask_char, visible_chars)
        return data

    if isinstance(data, dict):
        # Recursively mask values in dictionary
        dict_result: dict[str, Any] = {}
        for k, v in data.items():
            dict_result[k] = _mask_if_sensitive(k, v, mask_char, visible_chars)
        return dict_result  # Explicitly return a Dict[str, Any]

    if isinstance(data, list):
        # Recursively mask values in list
        list_result: list[Any] = [
            mask_sensitive_data(item, mask_char, visible_chars) for item in data
        ]
        return list_result

    # For any other type, return as is
    return data


def _mask_if_sensitive(
    key: str, value: object, mask_char: str = "*", visible_chars: int = 4
) -> object:
    """
    Check if a key is sensitive and mask its value if needed.

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
    """
    Mask a string, showing only the first and last few characters.

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
    """
    Mask text that matches a specific regex pattern.

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
        """
        Initialize the secure logger.

        Args:
            name: The name of the logger

        """
        self.name = name  # Store the name attribute
        self.logger = logging.getLogger(name)
        self._handlers: list[logging.Handler] = self.logger.handlers

    @property
    def handlers(self) -> list[logging.Handler]:
        """Get the handlers for this logger."""
        return self._handlers

    def set_level(self, level: int) -> None:
        """Set the logging level of this logger."""
        self.logger.setLevel(level)
        self.level: int = self.logger.level

    # Standard logging compatibility aliases
    setLevel = set_level  # noqa: N815

    def is_enabled_for(self, level: int) -> bool:
        """Check if this logger is enabled for the specified level."""
        result: bool = self.logger.isEnabledFor(level)
        return result

    # Standard logging compatibility aliases
    isEnabledFor = is_enabled_for  # noqa: N815

    def get_effective_level(self) -> int:
        """Get the effective level for this logger."""
        result: int = self.logger.getEffectiveLevel()
        return result

    # Standard logging compatibility aliases
    getEffectiveLevel = get_effective_level  # noqa: N815

    def get_child(self, suffix: str) -> SecureLogger:
        """Get a logger which is a descendant to this logger."""
        child_logger = self.logger.getChild(suffix)
        secure_child = SecureLogger(child_logger.name)
        secure_child.logger = child_logger
        return secure_child

    # Standard logging compatibility aliases
    getChild = get_child  # noqa: N815

    def add_handler(self, hdlr: logging.Handler) -> None:
        """Add the specified handler to this logger."""
        self.logger.addHandler(hdlr)
        # Store handlers in a property
        self._handlers = self.logger.handlers

    # Standard logging compatibility aliases
    addHandler = add_handler  # noqa: N815

    def remove_handler(self, hdlr: logging.Handler) -> None:
        """Remove the specified handler from this logger."""
        self.logger.removeHandler(hdlr)
        # Update handlers attribute
        self._handlers = self.logger.handlers

    # Standard logging compatibility aliases
    removeHandler = remove_handler  # noqa: N815

    def has_handlers(self) -> bool:
        """
        Check if this logger has any handlers configured.

        Returns:
            bool: True if this logger has handlers configured

        """
        return self.logger.hasHandlers()

    # Standard logging compatibility aliases
    hasHandlers = has_handlers  # noqa: N815

    def call_handlers(self, record: logging.LogRecord) -> None:
        """Pass a record to all relevant handlers."""
        self.logger.callHandlers(record)  # Standard logging compatibility aliases

    callHandlers = call_handlers  # noqa: N815

    def handle(self, record: logging.LogRecord) -> bool:
        """
        Call the handlers for the specified record.

        Args:
            record: The log record to handle

        Returns:
            bool: True if the record was handled successfully

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
        """
        Make a LogRecord.

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
        masked_msg = mask_sensitive_data(str(msg))
        if not isinstance(masked_msg, str):
            masked_msg = str(masked_msg)
        return self.logger.makeRecord(
            name, level, fn, lno, masked_msg, args, exc_info, func, extra, sinfo
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

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Log a debug message with sensitive information masked.

        Args:
            msg: The message to log
            args: Arguments for message formatting
            kwargs: Keyword arguments for logging configuration

        """
        masked_msg = mask_sensitive_data(msg)
        if not isinstance(masked_msg, str):
            masked_msg = str(masked_msg)

        # Add [SECURE] prefix if secure_context is True
        if kwargs.get('secure_context', False):
            masked_msg = f"[SECURE] {masked_msg}"

        self.logger.debug(masked_msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Log an info message with sensitive information masked.

        Args:
            msg: The message to log
            args: Arguments for message formatting
            kwargs: Keyword arguments for logging configuration

        """
        masked_msg = mask_sensitive_data(msg)
        if not isinstance(masked_msg, str):
            masked_msg = str(masked_msg)

        # Add [SECURE] prefix if secure_context is True
        if kwargs.get('secure_context', False):
            masked_msg = f"[SECURE] {masked_msg}"

        self.logger.info(masked_msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Log a warning message with sensitive information masked.

        Args:
            msg: The message to log
            args: Arguments for message formatting
            kwargs: Keyword arguments for logging configuration

        """
        masked_msg = mask_sensitive_data(msg)
        if not isinstance(masked_msg, str):
            masked_msg = str(masked_msg)

        # Add [SECURE] prefix if secure_context is True
        if kwargs.get('secure_context', False):
            masked_msg = f"[SECURE] {masked_msg}"

        self.logger.warning(masked_msg, *args, **kwargs)

    # Alias for warning
    warn = warning

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Log an error message with sensitive information masked.

        Args:
            msg: The message to log
            args: Arguments for message formatting
            kwargs: Keyword arguments for logging configuration

        """
        masked_msg = mask_sensitive_data(msg)
        if not isinstance(masked_msg, str):
            masked_msg = str(masked_msg)

        # Add [SECURE] prefix if secure_context is True
        if kwargs.get('secure_context', False):
            masked_msg = f"[SECURE] {masked_msg}"

        self.logger.error(masked_msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Log a critical message with sensitive information masked.

        Args:
            msg: The message to log
            args: Arguments for message formatting
            kwargs: Keyword arguments for logging configuration

        """
        masked_msg = mask_sensitive_data(msg)
        if not isinstance(masked_msg, str):
            masked_msg = str(masked_msg)

        # Add [SECURE] prefix if secure_context is True
        if kwargs.get('secure_context', False):
            masked_msg = f"[SECURE] {masked_msg}"

        self.logger.critical(masked_msg, *args, **kwargs)

    # Alias for critical
    fatal = critical

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Log an exception message with sensitive information masked.

        Args:
            msg: The message to log
            args: Arguments for message formatting
            kwargs: Keyword arguments for logging configuration

        """
        masked_msg = mask_sensitive_data(msg)
        if not isinstance(masked_msg, str):
            masked_msg = str(masked_msg)

        # Add [SECURE] prefix if secure_context is True
        if kwargs.get('secure_context', False):
            masked_msg = f"[SECURE] {masked_msg}"

        self.logger.exception(masked_msg, *args, **kwargs)

    def log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """
        Log with specified level.

        Args:
            level: The logging level
            msg: The message to log
            args: Arguments for message formatting
            kwargs: Keyword arguments for logging configuration

        """
        masked_msg = mask_sensitive_data(msg)
        if not isinstance(masked_msg, str):
            masked_msg = str(masked_msg)

        # Add [SECURE] prefix if secure_context is True
        if kwargs.get('secure_context', False):
            masked_msg = f"[SECURE] {masked_msg}"

        self.logger.log(level, masked_msg, *args, **kwargs)


def get_secure_logger(name: str) -> SecureLogger:
    """
    Get a secure logger that masks sensitive information.

    Args:
    ----
        name: The name of the logger

    Returns:
    -------
        A SecureLogger instance

    """
    return SecureLogger(name)
