"""Test module for common_utils.logging.secure_logging."""

import logging
import re
from unittest.mock import MagicMock, patch

import pytest

from common_utils.logging.secure_logging import (
    PATTERNS,
    SENSITIVE_FIELDS,
    SecureLogger,
    _mask_if_sensitive,
    _mask_pattern,
    _mask_string,
    get_secure_logger,
    is_sensitive_key,
    mask_sensitive_data,
    prevent_log_injection,
)


class TestSecureLogging:
    """Test suite for secure_logging module."""

    def test_is_sensitive_key_with_sensitive_field(self):
        """Test is_sensitive_key with a key from SENSITIVE_FIELDS."""
        for field in SENSITIVE_FIELDS:
            assert is_sensitive_key(field) is True
            assert is_sensitive_key(f"prefix_{field}") is True
            assert is_sensitive_key(f"{field}_suffix") is True

    def test_is_sensitive_key_with_common_sensitive_terms(self):
        """Test is_sensitive_key with common sensitive terms."""
        sensitive_terms = [
            "password", "token", "secret", "key", "auth",
            "credential", "private", "security", "access", "api", "cert"
        ]
        for term in sensitive_terms:
            assert is_sensitive_key(term) is True
            assert is_sensitive_key(f"prefix_{term}") is True
            assert is_sensitive_key(f"{term}_suffix") is True

    def test_is_sensitive_key_with_non_sensitive_key(self):
        """Test is_sensitive_key with non-sensitive keys."""
        non_sensitive_keys = ["name", "email", "address", "phone", "description"]
        for key in non_sensitive_keys:
            assert is_sensitive_key(key) is False

    def test_is_sensitive_key_with_empty_key(self):
        """Test is_sensitive_key with an empty key."""
        assert is_sensitive_key("") is False
        assert is_sensitive_key(None) is False

    def test_mask_string(self):
        """Test _mask_string function."""
        # Test with default parameters
        result = _mask_string("password123")
        assert result.startswith("pass")
        assert result.endswith("123")
        assert "password123" not in result

        # Test with custom mask character
        result = _mask_string("password123", mask_char="#")
        assert "#" in result
        assert "password123" not in result

        # Test with custom visible characters
        result = _mask_string("password123", visible_chars=2)
        assert result.startswith("pa")
        assert result.endswith("23")
        assert "password123" not in result

        # Test with zero visible characters
        assert _mask_string("password123", visible_chars=0) == "***********"

        # Test with short string
        assert _mask_string("pwd", visible_chars=2) == "***"

        # Test with empty string
        assert _mask_string("") == ""

        # Test with None
        assert _mask_string(None) is None

    def test_mask_pattern(self):
        """Test _mask_pattern function."""
        # Create a test pattern
        test_pattern = re.compile(r'(api_key)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{10,})["\']?', re.IGNORECASE)

        # Test with matching pattern
        text = 'api_key="abcdefghijklmnopqrst"'
        masked = _mask_pattern(text, test_pattern)
        assert masked == 'api_key="abcd************qrst"'

        # Test with non-matching pattern
        text = 'username="john_doe"'
        masked = _mask_pattern(text, test_pattern)
        assert masked == text  # Should remain unchanged

        # Test with custom mask character and visible chars
        text = 'api_key="abcdefghijklmnopqrst"'
        masked = _mask_pattern(text, test_pattern, mask_char="#", visible_chars=2)
        assert masked == 'api_key="ab################st"'

    def test_mask_if_sensitive(self):
        """Test _mask_if_sensitive function."""
        # Test with sensitive key from SENSITIVE_FIELDS
        for field in SENSITIVE_FIELDS:
            masked = _mask_if_sensitive(field, "secret123")
            assert masked != "secret123"
            assert isinstance(masked, str)

        # Test with non-sensitive key
        assert _mask_if_sensitive("username", "john_doe") == "john_doe"

        # Test with non-string value
        data = {"nested": "value"}
        assert _mask_if_sensitive("data", data) == data

    def test_mask_sensitive_data_with_string(self):
        """Test mask_sensitive_data with string input."""
        # Test with string containing sensitive pattern
        text = 'access_credential="abcdefghijklmnopqrst"'
        masked = mask_sensitive_data(text)
        assert "abcdefghijklmnopqrst" not in masked
        assert "access_credential" in masked

        # Test with string not containing sensitive pattern
        text = 'username="john_doe"'
        masked = mask_sensitive_data(text)
        assert masked == text  # Should remain unchanged

    @patch("common_utils.logging.secure_logging._mask_pattern")
    def test_mask_sensitive_data_with_dict(self, mock_mask_pattern):
        """Test mask_sensitive_data with dictionary input."""
        # Setup mock to actually mask the data
        def mask_data(text, pattern, *args, **kwargs):
            if "api_material" in text:
                return text.replace("abcdefghijklmnopqrst", "abcd********qrst")
            return text

        mock_mask_pattern.side_effect = mask_data

        # Test with dictionary containing sensitive keys from SENSITIVE_FIELDS
        data = {
            "username": "john_doe",
            "auth_credential": "secret123",  # This is in SENSITIVE_FIELDS
            "api_material": "abcdefghijklmnopqrst",  # This matches a pattern
            "nested": {
                "access_credential": "1234567890abcdef",  # This is in SENSITIVE_FIELDS
                "public": "public_value"
            }
        }

        masked = mask_sensitive_data(data)

        # Check that sensitive values are masked
        assert masked["username"] == "john_doe"  # Non-sensitive, unchanged
        assert masked["auth_credential"] != "secret123"  # Sensitive, should be masked
        assert masked["nested"]["access_credential"] != "1234567890abcdef"  # Sensitive, should be masked
        assert masked["nested"]["public"] == "public_value"  # Non-sensitive, unchanged

        # Verify that _mask_pattern was called
        assert mock_mask_pattern.call_count > 0

    @patch("common_utils.logging.secure_logging.mask_sensitive_data", wraps=mask_sensitive_data)
    @patch("common_utils.logging.secure_logging._mask_pattern")
    def test_mask_sensitive_data_with_list(self, mock_mask_pattern, wrapped_mask_sensitive_data):
        """Test mask_sensitive_data with list input."""
        # Setup mock to simulate masking
        mock_mask_pattern.side_effect = lambda text, pattern, *args: text.replace("secret123", "MASKED_SECRET").replace("abcdefghijklmnopqrst", "MASKED_KEY")

        # Test with list containing sensitive strings
        data = [
            "username=john_doe",
            'password="secret123"',
            'api_key="abcdefghijklmnopqrst"',
            {"token": "1234567890abcdef"}
        ]

        masked = mask_sensitive_data(data)

        # Check that sensitive values are masked
        assert masked[0] == "username=john_doe"  # Non-sensitive, unchanged
        assert "MASKED_SECRET" in masked[1]  # Sensitive, should be masked
        assert "MASKED_KEY" in masked[2]  # Sensitive, should be masked

        # Verify the recursive call for the dictionary
        assert wrapped_mask_sensitive_data.call_count > 1

    def test_mask_sensitive_data_with_none(self):
        """Test mask_sensitive_data with None input."""
        assert mask_sensitive_data(None) is None

    def test_prevent_log_injection_with_string(self):
        """Test prevent_log_injection with string input."""
        # Test with newlines
        text = "Line 1\nLine 2\rLine 3\r\nLine 4"
        result = prevent_log_injection(text)
        assert "\n" not in result
        assert "\r" not in result
        assert result == "Line 1 [FILTERED] Line 2 [FILTERED] Line 3 [FILTERED] Line 4"

        # Test with control characters
        text = "Hello\x00World\x1FTest"
        result = prevent_log_injection(text)
        assert "\x00" not in result
        assert "\x1F" not in result
        assert result == "Hello [FILTERED] World [FILTERED] Test"

    def test_prevent_log_injection_with_dict(self):
        """Test prevent_log_injection with dictionary input."""
        data = {
            "normal": "value",
            "injection": "Line 1\nLine 2\rLine 3",
            "nested": {
                "normal": "value",
                "injection": "Hello\x00World\x1FTest"
            }
        }
        result = prevent_log_injection(data)

        # Check that the structure is preserved
        assert isinstance(result, dict)
        assert "normal" in result
        assert "injection" in result
        assert "nested" in result
        assert isinstance(result["nested"], dict)

        # Check that injections are sanitized
        assert "\n" not in result["injection"]
        assert "\r" not in result["injection"]
        assert "\x00" not in result["nested"]["injection"]
        assert "\x1F" not in result["nested"]["injection"]

    def test_prevent_log_injection_with_list(self):
        """Test prevent_log_injection with list input."""
        data = [
            "normal value",
            "Line 1\nLine 2\rLine 3",
            ["nested", "Hello\x00World\x1FTest"],
            {"key": "Line 1\nLine 2"}
        ]
        result = prevent_log_injection(data)

        # Check that the structure is preserved
        assert isinstance(result, list)
        assert len(result) == 4
        assert isinstance(result[2], list)
        assert isinstance(result[3], dict)

        # Check that injections are sanitized
        assert "\n" not in result[1]
        assert "\r" not in result[1]
        assert "\x00" not in result[2][1]
        assert "\x1F" not in result[2][1]
        assert "\n" not in result[3]["key"]

    def test_prevent_log_injection_with_none(self):
        """Test prevent_log_injection with None input."""
        assert prevent_log_injection(None) is None

    def test_prevent_log_injection_with_other_types(self):
        """Test prevent_log_injection with other types."""
        # Test with integer
        assert prevent_log_injection(123) == 123

        # Test with boolean
        assert prevent_log_injection(True) is True

        # Test with float
        assert prevent_log_injection(123.45) == 123.45

    def test_get_secure_logger(self):
        """Test get_secure_logger function."""
        logger = get_secure_logger("test_secure_logger")
        assert isinstance(logger, SecureLogger)
        assert logger.logger.name == "test_secure_logger"

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_debug(self, mock_mask_sensitive_data):
        """Test SecureLogger.debug method."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        secure_logger.debug("sensitive message")

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.debug.assert_called_once_with("masked_message")

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_debug_with_secure_context(self, mock_mask_sensitive_data):
        """Test SecureLogger.debug method with secure_context."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method with secure_context=True
        secure_logger.debug("sensitive message", secure_context=True)

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.debug.assert_called_once_with("[SECURE] masked_message", secure_context=True)

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_info(self, mock_mask_sensitive_data):
        """Test SecureLogger.info method."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        secure_logger.info("sensitive message")

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.info.assert_called_once_with("masked_message")

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_info_with_secure_context(self, mock_mask_sensitive_data):
        """Test SecureLogger.info method with secure_context."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method with secure_context=True
        secure_logger.info("sensitive message", secure_context=True)

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.info.assert_called_once_with("[SECURE] masked_message", secure_context=True)

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_warning(self, mock_mask_sensitive_data):
        """Test SecureLogger.warning method."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        secure_logger.warning("sensitive message")

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.warning.assert_called_once_with("masked_message")

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_warning_with_secure_context(self, mock_mask_sensitive_data):
        """Test SecureLogger.warning method with secure_context."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method with secure_context=True
        secure_logger.warning("sensitive message", secure_context=True)

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.warning.assert_called_once_with("[SECURE] masked_message", secure_context=True)

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_error(self, mock_mask_sensitive_data):
        """Test SecureLogger.error method."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        secure_logger.error("sensitive message")

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.error.assert_called_once_with("masked_message")

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_error_with_secure_context(self, mock_mask_sensitive_data):
        """Test SecureLogger.error method with secure_context."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method with secure_context=True
        secure_logger.error("sensitive message", secure_context=True)

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.error.assert_called_once_with("[SECURE] masked_message", secure_context=True)

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_critical(self, mock_mask_sensitive_data):
        """Test SecureLogger.critical method."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        secure_logger.critical("sensitive message")

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.critical.assert_called_once_with("masked_message")

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_critical_with_secure_context(self, mock_mask_sensitive_data):
        """Test SecureLogger.critical method with secure_context."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method with secure_context=True
        secure_logger.critical("sensitive message", secure_context=True)

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.critical.assert_called_once_with("[SECURE] masked_message", secure_context=True)

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_exception(self, mock_mask_sensitive_data):
        """Test SecureLogger.exception method."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        secure_logger.exception("sensitive message")

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.exception.assert_called_once_with("masked_message")

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_exception_with_secure_context(self, mock_mask_sensitive_data):
        """Test SecureLogger.exception method with secure_context."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method with secure_context=True
        secure_logger.exception("sensitive message", secure_context=True)

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.exception.assert_called_once_with("[SECURE] masked_message", secure_context=True)

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_log(self, mock_mask_sensitive_data):
        """Test SecureLogger.log method."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        secure_logger.log(logging.INFO, "sensitive message")

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.log.assert_called_once_with(logging.INFO, "masked_message")

    @patch("common_utils.logging.secure_logging.mask_sensitive_data")
    def test_secure_logger_log_with_secure_context(self, mock_mask_sensitive_data):
        """Test SecureLogger.log method with secure_context."""
        # Setup
        mock_mask_sensitive_data.return_value = "masked_message"
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method with secure_context=True
        secure_logger.log(logging.INFO, "sensitive message", secure_context=True)

        # Assertions
        mock_mask_sensitive_data.assert_called_once_with("sensitive message")
        mock_logger.log.assert_called_once_with(logging.INFO, "[SECURE] masked_message", secure_context=True)

    def test_secure_logger_set_level(self):
        """Test SecureLogger.set_level method."""
        # Setup
        mock_logger = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        secure_logger.set_level(logging.DEBUG)

        # Assertions
        mock_logger.setLevel.assert_called_once_with(logging.DEBUG)

    def test_secure_logger_is_enabled_for(self):
        """Test SecureLogger.is_enabled_for method."""
        # Setup
        mock_logger = MagicMock()
        mock_logger.isEnabledFor.return_value = True
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        result = secure_logger.is_enabled_for(logging.INFO)

        # Assertions
        assert result is True
        mock_logger.isEnabledFor.assert_called_once_with(logging.INFO)

    def test_secure_logger_get_effective_level(self):
        """Test SecureLogger.get_effective_level method."""
        # Setup
        mock_logger = MagicMock()
        mock_logger.getEffectiveLevel.return_value = logging.INFO
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        result = secure_logger.get_effective_level()

        # Assertions
        assert result == logging.INFO
        mock_logger.getEffectiveLevel.assert_called_once()

    def test_secure_logger_get_child(self):
        """Test SecureLogger.get_child method."""
        # Setup
        mock_logger = MagicMock()
        mock_child_logger = MagicMock()
        # Configure the mock to return a string for the name attribute
        mock_child_logger.name = "test_logger.child"
        mock_logger.getChild.return_value = mock_child_logger
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        child_logger = secure_logger.get_child("child")

        # Assertions
        assert isinstance(child_logger, SecureLogger)
        mock_logger.getChild.assert_called_once_with("child")
        assert child_logger.logger is mock_child_logger

    def test_secure_logger_add_handler(self):
        """Test SecureLogger.add_handler method."""
        # Setup
        mock_logger = MagicMock()
        mock_handler = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        secure_logger.add_handler(mock_handler)

        # Assertions
        mock_logger.addHandler.assert_called_once_with(mock_handler)

    def test_secure_logger_remove_handler(self):
        """Test SecureLogger.remove_handler method."""
        # Setup
        mock_logger = MagicMock()
        mock_handler = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        secure_logger.remove_handler(mock_handler)

        # Assertions
        mock_logger.removeHandler.assert_called_once_with(mock_handler)

    def test_secure_logger_has_handlers(self):
        """Test SecureLogger.has_handlers method."""
        # Setup
        mock_logger = MagicMock()
        mock_logger.hasHandlers.return_value = True
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        result = secure_logger.has_handlers()

        # Assertions
        assert result is True
        mock_logger.hasHandlers.assert_called_once()

    def test_secure_logger_call_handlers(self):
        """Test SecureLogger.call_handlers method."""
        # Setup
        mock_logger = MagicMock()
        mock_record = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        secure_logger.call_handlers(mock_record)

        # Assertions
        mock_logger.callHandlers.assert_called_once_with(mock_record)

    def test_secure_logger_handle(self):
        """Test SecureLogger.handle method."""
        # Setup
        mock_logger = MagicMock()
        mock_logger.handle.return_value = True
        mock_record = MagicMock()
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        result = secure_logger.handle(mock_record)

        # Assertions
        assert result is True
        mock_logger.handle.assert_called_once_with(mock_record)

    def test_secure_logger_make_record(self):
        """Test SecureLogger.make_record method."""
        # Setup
        mock_logger = MagicMock()
        mock_record = MagicMock()
        mock_logger.makeRecord.return_value = mock_record
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        result = secure_logger.make_record(
            "name", logging.INFO, "fn", 10, "msg", (), None, "func", {}, "sinfo"
        )

        # Assertions
        assert result is mock_record
        mock_logger.makeRecord.assert_called_once_with(
            "name", logging.INFO, "fn", 10, "msg", (), None, "func", {}, "sinfo"
        )

    def test_secure_logger_find_caller(self):
        """Test SecureLogger.find_caller method."""
        # Setup
        mock_logger = MagicMock()
        mock_logger.findCaller.return_value = ("file", 10, "func", "sinfo")
        secure_logger = SecureLogger("test_logger")
        secure_logger.logger = mock_logger

        # Call the method
        result = secure_logger.find_caller()

        # Assertions
        assert result == ("file", 10, "func", "sinfo")
        mock_logger.findCaller.assert_called_once_with(False, 1)
