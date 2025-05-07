"""Test script to verify security fixes."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from common_utils.secrets.audit import generate_report
from common_utils.secrets.cli import handle_list


class TestSecurityFixes(unittest.TestCase):
    """Test cases for security fixes."""

    def test_generate_report_no_sensitive_data_in_logs(self):
        """Test that generate_report doesn't log sensitive data."""
        # Mock results with sensitive data
        results = {
            "test_file.py": [
                (
                    "api_key",
                    10,
                    'api_key = "supersecretapikey123"',
                    "supersecretapikey123",
                ),
                ("password", 20, 'password = "mypassword"', "mypassword"),
            ]
        }

        # Mock logger
        with patch("common_utils.secrets.audit.logger") as mock_logger:
            # Call generate_report
            generate_report(results)

            # Check that the logger was called with safe messages
            for call_args in mock_logger.info.call_args_list:
                msg = call_args[0][0]
                # Ensure no sensitive data in log messages
                self.assertNotIn("supersecretapikey123", msg)
                self.assertNotIn("mypassword", msg)

    def test_generate_report_file_output_no_sensitive_data(self):
        """Test that generate_report doesn't write sensitive data to file."""
        # Mock results with sensitive data
        results = {
            "test_file.py": [
                (
                    "api_key",
                    10,
                    'api_key = "supersecretapikey123"',
                    "supersecretapikey123",
                ),
                ("password", 20, 'password = "mypassword"', "mypassword"),
            ]
        }

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Call generate_report with file output
            generate_report(results, output_file=temp_path)

            # Read the file content
            with open(temp_path) as f:
                content = f.read()

            # Ensure no sensitive data in file
            self.assertNotIn("supersecretapikey123", content)
            self.assertNotIn("mypassword", content)

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_handle_list_no_sensitive_keys(self):
        """Test that handle_list doesn't print sensitive key names."""
        # Mock secrets with sensitive keys
        secrets = {
            "api_key_production": "secret1",
            "database_password": "secret2",
            "jwt_token": "secret3",
        }

        # Mock args
        args = MagicMock()
        args.backend = "env"

        # Mock list_secrets to return our test data
        with patch("common_utils.secrets.cli.list_secrets", return_value=secrets):
            # Mock print to capture output
            with patch("builtins.print") as mock_print:
                # Call handle_list
                handle_list(args)

                # Check that print was called without sensitive keys
                for call_args in mock_print.call_args_list:
                    msg = call_args[0][0]
                    # Ensure no sensitive key names in output
                    self.assertNotIn("api_key_production", msg)
                    self.assertNotIn("database_password", msg)
                    self.assertNotIn("jwt_token", msg)
                    # Check that we're using the hash format
                    if msg.startswith("  Secret #"):
                        self.assertGreater(
                            len(msg),
                            10,
                            "Secret hash should be longer than 10 characters",
                        )

    @patch("fix_security_issues.IMPORTED_SECRET_SCANNER", False)
    @patch("fix_security_issues.globals")
    @patch("subprocess.run")
    def test_run_security_scan_with_missing_imports(
        self, mock_subprocess_run, mock_globals, _
    ):
        """Test that run_security_scan handles missing imports gracefully."""
        # Configure mock to simulate 'scan_directory_for_secrets' not in globals
        mock_globals.return_value = {}

        # Configure subprocess mock
        mock_subprocess_run.return_value.stdout = (
            '{"test_file.py": [{"type": "api_key", "line_number": 10}]}'
        )
        mock_subprocess_run.return_value.returncode = 0

        # Import the function we want to test
        from fix_security_issues import run_security_scan

        # Run the function with missing imports
        result = run_security_scan("./test_directory", set([".git", "venv"]))

        # Verify we got a result despite the import failing
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
