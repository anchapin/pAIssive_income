"""
Secure logging utilities to prevent sensitive information from being logged.

This module provides functions to mask sensitive information in logs, such as access
credentials, authentication materials, and other sensitive data.
"""

from __future__ import annotations

import logging
import re
from logging import LogRecord
from re import Pattern
from typing import Any, Callable, TypeVar, cast

# Type variables for generic functions
T = TypeVar("T")
LogFilter = Callable[[LogRecord], bool]
LogFormatter = Callable[[LogRecord], str]

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
PATTERNS: dict[str, Pattern[str]] = {
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
    """
    Check if a key name contains sensitive information patterns.

    Args:
        key: The key name to check

    Returns:
        True if the key appears to reference sensitive information

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


def _mask_string(
    value: str | None, mask_char: str = "*", visible_chars: int = 4
) -> str | None:
    """
    Mask a string value, showing only the first and last n characters.

    Args:
        value: The string to mask
        mask_char: The character to use for masking
        visible_chars: Number of characters to leave visible at start/end

    Returns:
        The masked string, or None if input was None

    """
    if not value or len(value) <= (visible_chars * 2):
        return mask_char * len(value) if value else value

    prefix = value[:visible_chars]
    suffix = value[-visible_chars:] if visible_chars > 0 else ""
    masked_length = len(value) - (len(prefix) + len(suffix))

    return f"{prefix}{mask_char * masked_length}{suffix}"


def _mask_pattern(
    text: str, pattern: Pattern[str], mask_char: str = "*", visible_chars: int = 4
) -> str:
    """
    Mask text that matches a specific regex pattern.

    Args:
        text: The text to process
        pattern: The regex pattern to match
        mask_char: The character to use for masking
        visible_chars: Number of characters to leave visible

    Returns:
        The text with sensitive information masked

    """

    def _replacer(match: re.Match[str]) -> str:
        full_match: str = match.group(0)
        sensitive_value: str | None = match.group(2)

        if not sensitive_value:
            return full_match

        masked_value: str | None = _mask_string(
            sensitive_value, mask_char, visible_chars
        )
        return full_match.replace(sensitive_value, str(masked_value))

    result = pattern.sub(_replacer, text)
    return str(result)


class SecureLogger:
    """A secure logger that masks sensitive information."""

    def __init__(self, name: str) -> None:
        """
        Initialize the secure logger.

        Args:
            name: The name of the logger

        """
        self.logger: logging.Logger = logging.getLogger(name)
        self.name: str = name
        self.level: int = self.logger.level
        self._handlers: list[logging.Handler] = []

    @property
    def handlers(self) -> list[logging.Handler]:
        """
        Get the handlers for this logger.

        Returns:
            List of logging handlers attached to this logger

        """
        return self._handlers

    def set_level(self, level: int) -> None:
        """
        Set the logging level of this logger.

        Args:
            level: The logging level to set (e.g. logging.INFO)

        """
        self.logger.setLevel(level)
        self.level = self.logger.level

    # Standard logging compatibility aliases
    setLevel = set_level  # noqa: N815

    def is_enabled_for(self, level: int) -> bool:
        """
        Check if this logger is enabled for the specified level.

        Args:
            level: The logging level to check

        Returns:
            True if the logger is enabled for the specified level

        """
        return self.logger.isEnabledFor(level)

    # Standard logging compatibility aliases
    isEnabledFor = is_enabled_for  # noqa: N815

    def get_effective_level(self) -> int:
        """
        Get the effective level for this logger.

        Returns:
            The effective logging level for this logger

        """
        return self.logger.getEffectiveLevel()

    # Standard logging compatibility aliases
    getEffectiveLevel = get_effective_level  # noqa: N815

    def get_child(self, suffix: str) -> SecureLogger:
        """
        Get a logger which is a descendant to this logger.

        Args:
            suffix: The suffix to append to the logger name

        Returns:
            A new SecureLogger that is a child of this logger

        """
        child_logger = self.logger.getChild(suffix)
        secure_child = SecureLogger(child_logger.name)
        secure_child.logger = child_logger
        return secure_child

    # Standard logging compatibility aliases
    getChild = get_child  # noqa: N815

    def add_handler(self, hdlr: logging.Handler) -> None:
        """
        Add the specified handler to this logger.

        Args:
            hdlr: The handler to add to this logger

        """
        self.logger.addHandler(hdlr)
        self._handlers = self.logger.handlers

    # Standard logging compatibility aliases
    addHandler = add_handler  # noqa: N815

    def remove_handler(self, hdlr: logging.Handler) -> None:
        """
        Remove the specified handler from this logger.

        Args:
            hdlr: The handler to remove from this logger

        """
        self.logger.removeHandler(hdlr)
        self._handlers = self.logger.handlers

    # Standard logging compatibility aliases
    removeHandler = remove_handler  # noqa: N815

    def has_handlers(self) -> bool:
        """
        Check if this logger has any handlers configured.

        Returns:
            True if this logger has handlers configured

        """
        return bool(self._handlers)

    # Standard logging compatibility aliases
    hasHandlers = has_handlers  # noqa: N815

    def call_handlers(self, record: LogRecord) -> None:
        """
        Pass a record to all relevant handlers.

        Args:
            record: The log record to pass to handlers

        """
        if self._handlers and not getattr(record, "handled", False):
            record.handled = True
            for handler in self._handlers:
                if record.levelno >= handler.level:
                    handler.handle(cast("LogRecord", record))

    # Standard logging compatibility aliases
    callHandlers = call_handlers  # noqa: N815

    def handle(self, record: LogRecord) -> None:
        """
        Handle a record by passing it to handlers.

        Args:
            record: The log record to handle

        """
        if not getattr(record, "handled", False):
            record.handled = True
            self.call_handlers(record)

    def make_record(
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: str,
        args: tuple[Any, ...],
        exc_info: tuple[type[BaseException], BaseException, Any] | None,
        func: str | None = None,
        extra: dict[str, Any] | None = None,
        sinfo: str | None = None,
    ) -> LogRecord:
        """
        Create a LogRecord.

        Args:
            name: The logger name
            level: The logging level
            fn: The filename
            lno: The line number
            msg: The log message
            args: Message arguments
            exc_info: Exception info tuple
            func: Function name
            extra: Extra attributes for record
            sinfo: Stack info

        Returns:
            LogRecord: A LogRecord instance

        """
        return self.logger.makeRecord(
            name,
            level,
            fn,
            lno,
            msg,
            args,
            exc_info,
            func=func,
            extra=extra,
            sinfo=sinfo,
        )

    # Standard logging compatibility aliases
    makeRecord = make_record  # noqa: N815

    def find_caller(
        self, stack_info: bool = False, stacklevel: int = 1
    ) -> tuple[str, int, str, str | None]:
        """
        Find the caller's source file and line number.

        Args:
            stack_info: Whether to capture the full stack trace
            stacklevel: How many frames up the stack to skip

        Returns:
            A tuple of (filename, line number, function name, sinfo)

        """
        return self.logger.findCaller(stack_info, stacklevel)

    # Standard logging compatibility aliases
    findCaller = find_caller  # noqa: N815

    def debug(
        self, msg: str | object, *args: object, **kwargs: dict[str, object]
    ) -> None:
        """
        Log a message with severity 'DEBUG'.

        Args:
            msg: The message to log
            *args: Message format arguments
            **kwargs: Additional logging options

        """
        self.logger.debug(msg, *args, **kwargs)

    def info(
        self, msg: str | object, *args: object, **kwargs: dict[str, object]
    ) -> None:
        """
        Log a message with severity 'INFO'.

        Args:
            msg: The message to log
            *args: Message format arguments
            **kwargs: Additional logging options

        """
        self.logger.info(msg, *args, **kwargs)

    def warning(
        self, msg: str | object, *args: object, **kwargs: dict[str, object]
    ) -> None:
        """
        Log a message with severity 'WARNING'.

        Args:
            msg: The message to log
            *args: Message format arguments
            **kwargs: Additional logging options

        """
        self.logger.warning(msg, *args, **kwargs)

    # Alias for warning
    warn = warning

    def error(
        self, msg: str | object, *args: object, **kwargs: dict[str, object]
    ) -> None:
        """
        Log a message with severity 'ERROR'.

        Args:
            msg: The message to log
            *args: Message format arguments
            **kwargs: Additional logging options

        """
        self.logger.error(msg, *args, **kwargs)

    def critical(
        self, msg: str | object, *args: object, **kwargs: dict[str, object]
    ) -> None:
        """
        Log a message with severity 'CRITICAL'.

        Args:
            msg: The message to log
            *args: Message format arguments
            **kwargs: Additional logging options

        """
        self.logger.critical(msg, *args, **kwargs)

    def exception(
        self, msg: str | object, *args: object, **kwargs: dict[str, object]
    ) -> None:
        """
        Log a message with severity 'ERROR' and include exception information.

        Args:
            msg: The message to log
            *args: Message format arguments
            **kwargs: Additional logging options

        """
        kwargs.setdefault("exc_info", True)
        self.error(msg, *args, **kwargs)

    def log(
        self, level: int, msg: str | object, *args: object, **kwargs: dict[str, object]
    ) -> None:
        """
        Log a message with specified severity level.

        Args:
            level: The logging level
            msg: The message to log
            *args: Message format arguments
            **kwargs: Additional logging options

        """
        self.logger.log(level, msg, *args, **kwargs)


def get_secure_logger(name: str) -> SecureLogger:
    """
    Get a secure logger that masks sensitive information.

    Args:
        name: The name of the logger

    Returns:
        A SecureLogger instance configured with the given name

    """
    return SecureLogger(name)
