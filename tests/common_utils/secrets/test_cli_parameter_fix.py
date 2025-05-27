"""Tests for the parameter name fix in common_utils/secrets/cli.py."""

import logging
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pytest

from common_utils.secrets.audit import SecretsAuditor
from common_utils.secrets.cli import handle_audit


class TestCliParameterFix(unittest.TestCase):
    """Test cases for the parameter name fix in cli.py."""

    @patch("common_utils.secrets.cli.SecretsAuditor")
    @patch("common_utils.secrets.cli._check_auth", return_value=True)
    def test_audit_uses_correct_parameter_name(self, mock_check_auth, mock_auditor_class):
        """Test that handle_audit uses the correct parameter name 'format' instead of 'output_format'."""
        # Create a mock auditor instance
        mock_auditor = MagicMock()
        mock_auditor_class.return_value = mock_auditor

        # Create mock args
        mock_args = MagicMock()
        mock_args.directory = "test_dir"
        mock_args.output = None
        mock_args.json = True
        mock_args.exclude = None
        mock_args.backend = "env"

        # Mock os.path.exists to return True for the directory
        with patch("os.path.exists", return_value=True):
            # Call handle_audit
            handle_audit(mock_args)

        # Verify that audit was called with the correct parameter name 'format'
        mock_auditor.audit.assert_called_once()
        call_kwargs = mock_auditor.audit.call_args[1]

        # Check that 'format' is in the kwargs and 'output_format' is not
        assert "format" in call_kwargs
        assert "output_format" not in call_kwargs

        # Check that the format value is correct
        assert call_kwargs["format"] == "json"

    @patch("common_utils.secrets.cli.SecretsAuditor")
    @patch("common_utils.secrets.cli._check_auth", return_value=True)
    def test_audit_with_text_format(self, mock_check_auth, mock_auditor_class):
        """Test that handle_audit uses 'text' format when json is False."""
        # Create a mock auditor instance
        mock_auditor = MagicMock()
        mock_auditor_class.return_value = mock_auditor

        # Create mock args
        mock_args = MagicMock()
        mock_args.directory = "test_dir"
        mock_args.output = None
        mock_args.json = False
        mock_args.exclude = None
        mock_args.backend = "env"

        # Mock os.path.exists to return True for the directory
        with patch("os.path.exists", return_value=True):
            # Call handle_audit
            handle_audit(mock_args)

        # Verify that audit was called with the correct parameter name 'format'
        mock_auditor.audit.assert_called_once()
        call_kwargs = mock_auditor.audit.call_args[1]

        # Check that 'format' is in the kwargs and has the correct value
        assert "format" in call_kwargs
        assert call_kwargs["format"] == "text"

    @patch("common_utils.secrets.cli.SecretsAuditor")
    @patch("common_utils.secrets.cli._check_auth", return_value=True)
    def test_audit_with_output_file(self, mock_check_auth, mock_auditor_class):
        """Test that handle_audit correctly passes the output_file parameter."""
        # Create a mock auditor instance
        mock_auditor = MagicMock()
        mock_auditor_class.return_value = mock_auditor

        # Use a mock file path instead of a real temporary file to avoid file access issues
        mock_output_path = "/tmp/mock_output_file.txt"

        # Create mock args
        mock_args = MagicMock()
        mock_args.directory = "test_dir"
        mock_args.output = mock_output_path
        mock_args.json = True
        mock_args.exclude = None
        mock_args.backend = "env"

        # Mock os.path.exists to return True for both directory and output directory
        with patch("os.path.exists", return_value=True):
            # Call handle_audit
            handle_audit(mock_args)

        # Verify that audit was called with the correct parameters
        mock_auditor.audit.assert_called_once()
        call_kwargs = mock_auditor.audit.call_args[1]

        # Check that both 'format' and 'output_file' are in the kwargs
        assert "format" in call_kwargs
        assert "output_file" in call_kwargs

        # Check that the values are correct
        assert call_kwargs["format"] == "json"
        assert call_kwargs["output_file"] == mock_output_path

    @patch("common_utils.secrets.cli.SecretsAuditor")
    @patch("common_utils.secrets.cli.logger")
    @patch("common_utils.secrets.cli._check_auth", return_value=True)
    def test_audit_exception_handling(self, mock_check_auth, mock_logger, mock_auditor_class):
        """Test that handle_audit properly handles exceptions."""
        # Create a mock auditor instance that raises an exception
        mock_auditor = MagicMock()
        mock_auditor.audit.side_effect = Exception("Test exception")
        mock_auditor_class.return_value = mock_auditor

        # Create mock args
        mock_args = MagicMock()
        mock_args.directory = "test_dir"
        mock_args.output = None
        mock_args.json = True
        mock_args.exclude = None
        mock_args.backend = "env"

        # Mock os.path.exists to return True for the directory
        with patch("os.path.exists", return_value=True):
            # Call handle_audit and expect it to handle the exception
            with pytest.raises(SystemExit):
                handle_audit(mock_args)

            # Verify that the exception was logged
            mock_logger.exception.assert_called()


if __name__ == "__main__":
    unittest.main()
