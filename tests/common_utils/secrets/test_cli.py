"""Tests for the cli module."""

import logging
import os
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

import pytest

from common_utils.secrets.cli import (
    ADMIN_TOKEN_DIR,
    ADMIN_TOKEN_FILE,
    LOCKOUT_DURATION,
    MAX_FAILED_ATTEMPTS,
    _check_auth,
    _check_rate_limit,
    _validate_secret_value,
    get_secret_value,
    handle_delete,
    handle_get,
    handle_list,
    handle_set,
    parse_args,
    require_auth,
)


class TestCli(unittest.TestCase):
    """Test cases for the cli module."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name

        # Save original values
        self.original_admin_token_dir = ADMIN_TOKEN_DIR
        self.original_admin_token_file = ADMIN_TOKEN_FILE

        # Patch environment variables
        self.env_patcher = patch.dict(os.environ, {})
        self.mock_env = self.env_patcher.start()

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
        self.env_patcher.stop()

    def test_require_auth_decorator(self):
        """Test require_auth decorator."""
        @require_auth
        def test_function():
            return "Success"

        # Test with failed authentication
        with patch("common_utils.secrets.cli._check_auth", return_value=False):
            with self.assertRaises(PermissionError):
                test_function()

        # Test with successful authentication
        with patch("common_utils.secrets.cli._check_auth", return_value=True):
            self.assertEqual(test_function(), "Success")

    def test_check_auth_no_token_file(self):
        """Test _check_auth with no token file."""
        with patch("os.path.exists", return_value=False):
            self.assertFalse(_check_auth())

    def test_check_auth_with_token(self):
        """Test _check_auth with token."""
        # Mock token file and environment variable
        with patch("os.path.exists", return_value=True), \
             patch("os.stat", return_value=MagicMock(st_mode=0o600)), \
             patch("builtins.open", mock_open(read_data="hash_value")), \
             patch.dict(os.environ, {"SECRETS_ADMIN_TOKEN": "token"}), \
             patch("hashlib.sha256", return_value=MagicMock(hexdigest=lambda: "hash_value")):
            self.assertTrue(_check_auth())

    def test_check_auth_with_wrong_token(self):
        """Test _check_auth with wrong token."""
        # Mock token file and environment variable
        with patch("os.path.exists", return_value=True), \
             patch("os.stat", return_value=MagicMock(st_mode=0o600)), \
             patch("builtins.open", mock_open(read_data="hash_value")), \
             patch.dict(os.environ, {"SECRETS_ADMIN_TOKEN": "wrong_token"}), \
             patch("hashlib.sha256", return_value=MagicMock(hexdigest=lambda: "wrong_hash")):
            self.assertFalse(_check_auth())

    def test_check_rate_limit_no_lockout(self):
        """Test _check_rate_limit with no lockout."""
        # Reset failed attempts and lockout times
        with patch("common_utils.secrets.cli.failed_attempts", {}), \
             patch("common_utils.secrets.cli.lockout_times", {}):
            # Should not raise an exception
            _check_rate_limit("test_operation")

    def test_check_rate_limit_with_lockout(self):
        """Test _check_rate_limit with lockout."""
        import time

        # Set up lockout
        with patch("common_utils.secrets.cli.lockout_times", {"test_operation": time.time()}), \
             patch("time.time", return_value=time.time()):
            with self.assertRaises(PermissionError):
                _check_rate_limit("test_operation")

    def test_check_rate_limit_too_many_attempts(self):
        """Test _check_rate_limit with too many attempts."""
        # Set up too many failed attempts
        with patch("common_utils.secrets.cli.failed_attempts", {"test_operation": MAX_FAILED_ATTEMPTS}):
            with self.assertRaises(PermissionError):
                _check_rate_limit("test_operation")

    def test_validate_secret_value_valid(self):
        """Test _validate_secret_value with valid secret."""
        # Valid secret with uppercase, lowercase, digit, and special character
        self.assertTrue(_validate_secret_value("ValidSecret123!"))

    def test_validate_secret_value_invalid(self):
        """Test _validate_secret_value with invalid secrets."""
        # Too short
        self.assertFalse(_validate_secret_value("Short1!"))

        # Missing uppercase
        self.assertFalse(_validate_secret_value("validsecret123!"))

        # Missing lowercase
        self.assertFalse(_validate_secret_value("VALIDSECRET123!"))

        # Missing digit
        self.assertFalse(_validate_secret_value("ValidSecret!"))

        # Missing special character
        self.assertFalse(_validate_secret_value("ValidSecret123"))

    def test_parse_args(self):
        """Test parse_args function."""
        # Test with get command
        with patch("sys.argv", ["secrets_cli.py", "get", "test_key"]):
            args = parse_args()
            self.assertEqual(args.command, "get")
            self.assertEqual(args.key, "test_key")

        # Test with set command
        with patch("sys.argv", ["secrets_cli.py", "set", "test_key"]):
            args = parse_args()
            self.assertEqual(args.command, "set")
            self.assertEqual(args.key, "test_key")

    def test_get_secret_value(self):
        """Test get_secret_value function."""
        # Test with valid secret
        with patch("getpass.getpass", return_value="ValidSecret123!"):
            self.assertEqual(get_secret_value("test_key"), "ValidSecret123!")

        # Test with invalid secret
        with patch("getpass.getpass", return_value="invalid"):
            self.assertIsNone(get_secret_value("test_key"))

    @patch("common_utils.secrets.cli._check_auth", return_value=True)
    @patch("common_utils.secrets.cli.get_secret")
    def test_handle_get(self, mock_get_secret, mock_check_auth):
        """Test handle_get function."""
        # Mock arguments
        args = MagicMock()
        args.key = "test_key"
        args.backend = "env"

        # Test with existing secret
        mock_get_secret.return_value = "secret_value"
        with patch("sys.exit") as mock_exit, \
             patch("common_utils.secrets.cli.logger") as mock_logger, \
             patch.dict(os.environ, {"SECRETS_CLI_MODE": "non-interactive"}):
            handle_get(args)
            mock_exit.assert_not_called()
            mock_logger.info.assert_called()

    @patch("common_utils.secrets.cli._check_auth", return_value=True)
    @patch("common_utils.secrets.cli.get_secret_value")
    @patch("common_utils.secrets.cli.set_secret")
    def test_handle_set(self, mock_set_secret, mock_get_secret_value, mock_check_auth):
        """Test handle_set function."""
        # Mock arguments
        args = MagicMock()
        args.key = "test_key"
        args.backend = "env"

        # Test with valid secret
        mock_get_secret_value.return_value = "ValidSecret123!"
        mock_set_secret.return_value = True
        with patch("sys.exit") as mock_exit, \
             patch("common_utils.secrets.cli.logger") as mock_logger:
            handle_set(args)
            mock_exit.assert_not_called()
            mock_logger.info.assert_called()

    @patch("common_utils.secrets.cli._check_auth", return_value=True)
    @patch("common_utils.secrets.cli.delete_secret")
    @patch("builtins.input", return_value="yes")
    def test_handle_delete(self, mock_input, mock_delete_secret, mock_check_auth):
        """Test handle_delete function."""
        # Mock arguments
        args = MagicMock()
        args.key = "test_key"
        args.backend = "env"

        # Test with successful deletion
        mock_delete_secret.return_value = True
        with patch("sys.exit") as mock_exit, \
             patch("common_utils.secrets.cli.logger") as mock_logger:
            handle_delete(args)
            mock_exit.assert_not_called()
            mock_logger.info.assert_called()

    def test_main_unknown_command(self, monkeypatch):
        from common_utils.secrets import cli
        args = type("Args", (), {"command": "unknown"})()
        monkeypatch.setattr(cli, "parse_args", lambda: args)
        with patch.object(cli, "logger") as mock_logger, patch("sys.exit") as mock_exit:
            cli.main()
            mock_logger.error.assert_called()
            mock_exit.assert_called_once()

    def test_main_missing_command(self, monkeypatch):
        from common_utils.secrets import cli
        args = type("Args", (), {"command": None})()
        monkeypatch.setattr(cli, "parse_args", lambda: args)
        with patch.object(cli, "logger") as mock_logger, patch("sys.exit") as mock_exit:
            cli.main()
            mock_logger.error.assert_called()
            mock_exit.assert_called_once()

    def test_handle_rotation_missing_rotation_command(self, monkeypatch):
        from common_utils.secrets import cli
        args = type("Args", (), {"rotation_command": None, "backend": "env"})()
        with patch.object(cli, "logger") as mock_logger, patch("sys.exit") as mock_exit:
            cli.handle_rotation(args)
            mock_logger.error.assert_called()
            mock_exit.assert_called()

    def test_handle_rotation_unknown_rotation_command(self, monkeypatch):
        from common_utils.secrets import cli
        args = type("Args", (), {"rotation_command": "notarealcommand", "backend": "env", "key": "k"})()
        with patch.object(cli, "logger") as mock_logger, patch("sys.exit") as mock_exit:
            cli.handle_rotation(args)
            mock_logger.error.assert_called()
            mock_exit.assert_called()


if __name__ == "__main__":
    unittest.main()
