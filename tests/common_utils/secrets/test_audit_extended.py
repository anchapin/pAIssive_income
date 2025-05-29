"""Extended tests for the audit module."""

import json
import logging
import os
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

import pytest

from common_utils.secrets.audit import (
    SecretsAuditor,
    encrypt_report_content,
    generate_json_report,
    generate_report,
    generate_text_report,
    log_scan_completion,
    save_encrypted_report,
)


class TestAuditExtended(unittest.TestCase):
    """Extended test cases for the audit module."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    @patch("common_utils.secrets.audit.mask_sensitive_data")
    def test_generate_json_report(self, mock_mask_sensitive_data):
        """Test generate_json_report function."""
        # Setup mock to mask sensitive data
        mock_mask_sensitive_data.side_effect = lambda data, *args: data.replace("abcdefghijklmnopqrstuvwxyz123456", "[MASKED_KEY]").replace("secret123", "[MASKED_PASSWORD]").replace("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "[MASKED_TOKEN]") if isinstance(data, str) else data

        # Create test data
        results = {
            "file1.py": [
                ("credential_type_1", 10, 'api_key = "abcdefghijklmnopqrstuvwxyz123456"', "abcdefghijklmnopqrstuvwxyz123456"),
                ("auth_credential", 20, 'password = "secret123"', "secret123"),
            ],
            "file2.py": [
                ("access_credential", 5, 'token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"),
            ],
        }

        # Generate report
        report = generate_json_report(results)

        # Verify report
        self.assertIsInstance(report, str)
        json_report = json.loads(report)
        self.assertEqual(len(json_report), 2)
        self.assertIn("file1.py", json_report)
        self.assertIn("file2.py", json_report)
        self.assertEqual(len(json_report["file1.py"]), 2)
        self.assertEqual(len(json_report["file2.py"]), 1)

        # Check that value is redacted
        for file_data in json_report.values():
            for item in file_data:
                self.assertEqual(item["value"], "[REDACTED]")

    @patch("common_utils.secrets.audit.mask_sensitive_data")
    def test_generate_text_report(self, mock_mask_sensitive_data):
        """Test generate_text_report function."""
        # Setup mock to actually mask the data
        def mask_data(data, **kwargs):
            if isinstance(data, str):
                return data.replace("abcdefghijklmnopqrstuvwxyz123456", "[MASKED]").replace("secret123", "[MASKED]").replace("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "[MASKED]")
            return data

        mock_mask_sensitive_data.side_effect = mask_data

        # Create test data
        results = {
            "file1.py": [
                ("credential_type_1", 10, 'api_key = "abcdefghijklmnopqrstuvwxyz123456"', "abcdefghijklmnopqrstuvwxyz123456"),
                ("auth_credential", 20, 'password = "secret123"', "secret123"),
            ],
            "file2.py": [
                ("access_credential", 5, 'token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"),
            ],
        }

        # Generate report
        report = generate_text_report(results)

        # Verify report
        self.assertIsInstance(report, str)
        self.assertIn("Security Scan Report", report)
        self.assertIn("file1.py", report)
        self.assertIn("file2.py", report)
        self.assertIn("Line 10", report)
        self.assertIn("Line 20", report)
        self.assertIn("Line 5", report)

        # Verify that mask_sensitive_data was called
        self.assertGreater(mock_mask_sensitive_data.call_count, 0)

    def test_encrypt_report_content(self):
        """Test encrypt_report_content function."""
        # Create test content
        content = "This is a test report with sensitive data: api_key = 'abcdefghijklmnopqrstuvwxyz123456'"

        # Encrypt content
        salt, encrypted_content = encrypt_report_content(content)

        # Verify results
        self.assertIsInstance(salt, bytes)
        self.assertEqual(len(salt), 16)
        self.assertIsInstance(encrypted_content, bytes)
        self.assertGreater(len(encrypted_content), 0)

        # Ensure the original content is not in the encrypted content
        self.assertNotIn(b"abcdefghijklmnopqrstuvwxyz123456", encrypted_content)

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.open", new_callable=mock_open)
    def test_save_encrypted_report(self, mock_path_open, mock_mkdir):
        """Test save_encrypted_report function."""
        # Create test data
        path = os.path.join(self.test_dir, "reports", "report.enc")
        salt = b"0123456789abcdef"
        encrypted_content = b"encrypted_content_bytes"

        # Save encrypted report
        save_encrypted_report(path, salt, encrypted_content)

        # Verify results
        mock_mkdir.assert_called_once_with(parents=True, mode=0o700, exist_ok=True)
        mock_path_open.assert_called_once_with("wb")
        mock_path_open().write.assert_called_once_with(salt + encrypted_content)

    @patch("common_utils.secrets.audit.logger")
    def test_log_scan_completion_with_errors(self, mock_logger):
        """Test log_scan_completion function with errors."""
        # Create test data
        scanned_files = 100
        error_files = [
            {"file": "file1.py", "error_type": "PermissionError"},
            {"file": "file2.py", "error_type": "UnicodeDecodeError"},
        ]
        results = {
            "file3.py": [("credential_type_1", 10, "line content", "secret")],
            "file4.py": [("auth_credential", 20, "line content", "secret")],
        }

        # Call function
        log_scan_completion(scanned_files, error_files, results)

        # Verify results
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[1]
        self.assertEqual(call_args["extra"]["total_files"], 100)
        self.assertEqual(call_args["extra"]["error_files"], 2)
        self.assertEqual(call_args["extra"]["files_with_secrets"], 2)
        self.assertEqual(call_args["extra"]["error_types"], {"PermissionError", "UnicodeDecodeError"})

    @patch("common_utils.secrets.audit.logger")
    def test_log_scan_completion_without_errors(self, mock_logger):
        """Test log_scan_completion function without errors."""
        # Create test data
        scanned_files = 100
        error_files = []
        results = {
            "file1.py": [("credential_type_1", 10, "line content", "secret")],
            "file2.py": [("auth_credential", 20, "line content", "secret")],
        }

        # Call function
        log_scan_completion(scanned_files, error_files, results)

        # Verify results
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[1]
        self.assertEqual(call_args["extra"]["total_files"], 100)
        self.assertEqual(call_args["extra"]["files_with_secrets"], 2)
        self.assertEqual(call_args["extra"]["clean_files"], 98)

    @patch("common_utils.secrets.audit.generate_report")
    @patch("common_utils.secrets.audit.scan_directory")
    def test_secrets_auditor_audit(self, mock_scan_directory, mock_generate_report):
        """Test SecretsAuditor.audit method."""
        # Create test data
        directory = self.test_dir
        results = {
            "file1.py": [("credential_type_1", 10, "line content", "secret")],
        }
        mock_scan_directory.return_value = results

        # Create auditor and call audit
        auditor = SecretsAuditor()
        audit_results = auditor.audit(directory, output_file="report.txt", json_format=True)

        # Verify results
        mock_scan_directory.assert_called_once_with(directory, auditor.exclude_dirs)
        mock_generate_report.assert_called_once_with(results, "report.txt", True)
        self.assertEqual(audit_results, results)

    @patch("common_utils.secrets.audit.logger")
    @patch("common_utils.secrets.audit.generate_json_report")
    def test_generate_report_with_json_format(self, mock_generate_json_report, mock_logger):
        """Test generate_report function with JSON format."""
        # Create test data
        results = {
            "file1.py": [("credential_type_1", 10, "line content", "secret")],
        }
        mock_generate_json_report.return_value = '{"file1.py": [{"type": "credential_type_1"}]}'

        # Call function
        generate_report(results, output_file=None, json_format=True)

        # Verify results
        mock_generate_json_report.assert_called_once_with(results)
        mock_logger.info.assert_called()

    @patch("common_utils.secrets.audit.logger")
    def test_generate_report_with_no_results(self, mock_logger):
        """Test generate_report function with no results."""
        # Call function
        generate_report({})

        # Verify results
        mock_logger.info.assert_called_once_with("No potential security findings")

    @patch("common_utils.secrets.audit.encrypt_report_content")
    @patch("common_utils.secrets.audit.save_encrypted_report")
    @patch("common_utils.secrets.audit.mask_sensitive_data")
    @patch("common_utils.secrets.audit.logger")
    @patch("common_utils.secrets.audit.generate_text_report")
    def test_generate_report_with_output_file(self, mock_generate_text_report, mock_logger,
                                             mock_mask_sensitive_data, mock_save_encrypted_report,
                                             mock_encrypt_report_content):
        """Test generate_report function with output file."""
        # Create test data
        results = {
            "file1.py": [("credential_type_1", 10, "line content", "secret")],
        }
        mock_generate_text_report.return_value = "text report content"
        mock_mask_sensitive_data.return_value = "masked_output"
        mock_encrypt_report_content.return_value = (b"salt", b"encrypted_content")

        # Call function
        generate_report(results, output_file="report.txt")

        # Verify results
        mock_generate_text_report.assert_called_once_with(results)
        mock_mask_sensitive_data.assert_called()
        mock_encrypt_report_content.assert_called_once()
        mock_save_encrypted_report.assert_called_once_with("report.txt", b"salt", b"encrypted_content")
        mock_logger.info.assert_called()

    @patch("common_utils.secrets.audit.encrypt_report_content")
    @patch("common_utils.secrets.audit.logger")
    def test_generate_report_with_exception(self, mock_logger, mock_encrypt_report_content):
        """Test generate_report function with exception."""
        # Create test data
        results = {
            "file1.py": [("credential_type_1", 10, "line content", "secret")],
        }
        mock_encrypt_report_content.side_effect = Exception("Test error")

        # Call function
        generate_report(results, output_file="report.txt")

        # Verify results
        mock_logger.exception.assert_called_once()


if __name__ == "__main__":
    unittest.main()
