"""Secure logging utilities to prevent sensitive information from being logged.

This module provides functions to mask sensitive information in logs, such as API keys,
passwords, and other credentials.
"""

import logging
import re
from typing import Any, Pattern

# List of sensitive field names to mask in logs
SENSITIVE_FIELDS = [
    "password",
    "api_key",
    "token",
    "secret",
    "credential",
    "auth",
    "key",
    "private",
    "access_token",
    "refresh_token",
    "jwt",
    "session",
    "cookie",
    "signature",
    "hash",
    "salt",
    "pin",
    "cvv",
    "ssn",
    "credit_card",
    "card_number",
    "security_code",
]

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
        r'(token|access_token|refresh_token|jwt)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{10,})["\']?',
        re.IGNORECASE,
    ),
    "secret": re.compile(
        r'(secret|private_key)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{10,})["\']?',
        re.IGNORECASE,
    ),
}


def mask_sensitive_data(data: Any, mask_char: str = "*", visible_chars: int = 4) -> Any:
    """Mask sensitive data in logs to prevent logging of sensitive information.

    Args:
    ----
        data: The data to mask. Can be a string, dict, list, or other types.
        mask_char: The character to use for masking. Default is "*".
        visible_chars: Number of characters to show at start and end. Default is 4.

    Returns:
    -------
        The masked data with sensitive information hidden.

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
        return {
            k: _mask_if_sensitive(k, v, mask_char, visible_chars)
            for k, v in data.items()
        }

    elif isinstance(data, list):
        # Recursively mask values in list
        return [mask_sensitive_data(item, mask_char, visible_chars) for item in data]

    return data


def _mask_if_sensitive(
    key: str, value: Any, mask_char: str = "*", visible_chars: int = 4
) -> Any:
    """Check if a key is sensitive and mask its value if needed.

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

    def _replacer(match) -> str:
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

    def __init__(self, logger_name: str):
        """Initialize a secure logger.

        Args:
        ----
            logger_name: The name of the logger to wrap

        """
        self.logger = logging.getLogger(logger_name)

    def set_level(self, level):
        """Set the logging level of this logger."""
        self.logger.setLevel(level)
        self.level = self.logger.level

    # Alias for compatibility with standard logging
    # noqa: N815 - This needs to match the standard logging method name
    setLevel = set_level  # noqa: N815

    def is_enabled_for(self, level):
        """Check if this logger is enabled for the specified level."""
        return self.logger.isEnabledFor(level)

    # Alias for compatibility with standard logging
    # noqa: N815 - This needs to match the standard logging method name
    isEnabledFor = is_enabled_for  # noqa: N815

    def get_effective_level(self):
        """Get the effective level for this logger."""
        return self.logger.getEffectiveLevel()

    # Alias for compatibility with standard logging
    # noqa: N815 - This needs to match the standard logging method name
    getEffectiveLevel = get_effective_level  # noqa: N815

    def get_child(self, suffix):
        """Get a logger which is a descendant to this logger."""
        child_logger = self.logger.getChild(suffix)
        secure_child = SecureLogger(child_logger.name)
        secure_child.logger = child_logger
        return secure_child

    # Alias for compatibility with standard logging
    # noqa: N815 - This needs to match the standard logging method name
    getChild = get_child  # noqa: N815

    def debug(self, msg: str, *args, **kwargs):
        """Log a debug message with sensitive information masked."""
        self.logger.debug(mask_sensitive_data(msg), *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log an info message with sensitive information masked."""
        self.logger.info(mask_sensitive_data(msg), *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log a warning message with sensitive information masked."""
        self.logger.warning(mask_sensitive_data(msg), *args, **kwargs)

    # Alias for warning
    warn = warning

    def error(self, msg: str, *args, **kwargs):
        """Log an error message with sensitive information masked."""
        self.logger.error(mask_sensitive_data(msg), *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log a critical message with sensitive information masked."""
        self.logger.critical(mask_sensitive_data(msg), *args, **kwargs)

    # Alias for critical
    fatal = critical

    def exception(self, msg: str, *args, **kwargs):
        """Log an exception message with sensitive information masked."""
        self.logger.exception(mask_sensitive_data(msg), *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        """Log with specified level."""
        self.logger.log(level, mask_sensitive_data(msg), *args, **kwargs)

    def add_handler(self, hdlr):
        """Add the specified handler to this logger."""
        self.logger.addHandler(hdlr)
        self.handlers = self.logger.handlers

    # Alias for compatibility with standard logging
    # noqa: N815 - This needs to match the standard logging method name
    addHandler = add_handler  # noqa: N815

    def remove_handler(self, hdlr):
        """Remove the specified handler from this logger."""
        self.logger.removeHandler(hdlr)
        self.handlers = self.logger.handlers

    # Alias for compatibility with standard logging
    # noqa: N815 - This needs to match the standard logging method name
    removeHandler = remove_handler  # noqa: N815

    def has_handlers(self):
        """Check if this logger has any handlers configured."""
        return self.logger.hasHandlers()

    # Alias for compatibility with standard logging
    # noqa: N815 - This needs to match the standard logging method name
    hasHandlers = has_handlers  # noqa: N815

    def call_handlers(self, record):
        """Pass a record to all relevant handlers."""
        self.logger.callHandlers(record)

    # Alias for compatibility with standard logging
    # noqa: N815 - This needs to match the standard logging method name
    callHandlers = call_handlers  # noqa: N815

    def handle(self, record):
        """Call the handlers for the specified record."""
        return self.logger.handle(record)

    def make_record(
        self,
        name,
        level,
        fn,
        lno,
        msg,
        args,
        exc_info,
        func=None,
        extra=None,
        sinfo=None,
    ):
        """Make a LogRecord."""
        return self.logger.makeRecord(
            name, level, fn, lno, msg, args, exc_info, func, extra, sinfo
        )

    # Alias for compatibility with standard logging
    # noqa: N815 - This needs to match the standard logging method name
    makeRecord = make_record  # noqa: N815

    def find_caller(self, stack_info=False, stacklevel=1):
        """Find the caller's source file and line number."""
        return self.logger.findCaller(stack_info, stacklevel)

    # Alias for compatibility with standard logging
    # noqa: N815 - This needs to match the standard logging method name
    findCaller = find_caller  # noqa: N815


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
