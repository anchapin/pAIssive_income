#!/usr/bin/env python3
"""Test script for sarif_utils.py.

This script tests the sarif_utils.py script with various input scenarios
to ensure it handles edge cases correctly.
"""

import json
import os
import shutil
import tempfile
import unittest

# Import the module to test
import sarif_utils


class TestSarifUtils(unittest.TestCase):
    """Test cases for sarif_utils.py."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.test_dir, "output.sarif")

    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_empty_input_file(self):
        """Test with an empty input file."""
        # Create an empty input file
        input_file = os.path.join(self.test_dir, "empty.json")
        with open(input_file, "w") as f:
            pass  # Create empty file

        # Convert the file
        result = sarif_utils.convert_file(
            input_file, self.output_file, "TestTool", "https://example.com"
        )

        # Check that conversion was successful
        self.assertTrue(result)
        # Check that output file exists
        self.assertTrue(os.path.exists(self.output_file))
        # Check that output file is valid SARIF
        with open(self.output_file) as f:
            sarif_data = json.load(f)
            self.assertEqual(sarif_data["version"], "2.1.0")
            self.assertEqual(
                sarif_data["runs"][0]["tool"]["driver"]["name"], "TestTool"
            )
            self.assertEqual(len(sarif_data["runs"][0]["results"]), 0)

    def test_nonexistent_input_file(self):
        """Test with a nonexistent input file."""
        # Use a file path that doesn't exist
        input_file = os.path.join(self.test_dir, "nonexistent.json")

        # Convert the file
        result = sarif_utils.convert_file(
            input_file, self.output_file, "TestTool", "https://example.com"
        )

        # Check that conversion was successful (creates empty SARIF)
        self.assertTrue(result)
        # Check that output file exists
        self.assertTrue(os.path.exists(self.output_file))
        # Check that output file is valid SARIF
        with open(self.output_file) as f:
            sarif_data = json.load(f)
            self.assertEqual(sarif_data["version"], "2.1.0")
            self.assertEqual(
                sarif_data["runs"][0]["tool"]["driver"]["name"], "TestTool"
            )
            self.assertEqual(len(sarif_data["runs"][0]["results"]), 0)

    def test_invalid_json_input_file(self):
        """Test with an invalid JSON input file."""
        # Create an invalid JSON input file
        input_file = os.path.join(self.test_dir, "invalid.json")
        with open(input_file, "w") as f:
            f.write("{invalid json")

        # Convert the file
        result = sarif_utils.convert_file(
            input_file, self.output_file, "TestTool", "https://example.com"
        )

        # Check that conversion was successful (creates empty SARIF)
        self.assertTrue(result)
        # Check that output file exists
        self.assertTrue(os.path.exists(self.output_file))
        # Check that output file is valid SARIF
        with open(self.output_file) as f:
            sarif_data = json.load(f)
            self.assertEqual(sarif_data["version"], "2.1.0")
            self.assertEqual(
                sarif_data["runs"][0]["tool"]["driver"]["name"], "TestTool"
            )
            self.assertEqual(len(sarif_data["runs"][0]["results"]), 0)

    def test_valid_json_input_file(self):
        """Test with a valid JSON input file."""
        # Create a valid JSON input file
        input_file = os.path.join(self.test_dir, "valid.json")
        test_data = {
            "results": [
                {
                    "id": "test-rule",
                    "message": "Test message",
                    "file": "test.py",
                    "line": 42,
                    "severity": "high",
                    "name": "Test Rule",
                    "description": "Test rule description",
                }
            ]
        }
        with open(input_file, "w") as f:
            json.dump(test_data, f)

        # Convert the file
        result = sarif_utils.convert_file(
            input_file, self.output_file, "TestTool", "https://example.com"
        )

        # Check that conversion was successful
        self.assertTrue(result)
        # Check that output file exists
        self.assertTrue(os.path.exists(self.output_file))
        # Check that output file is valid SARIF
        with open(self.output_file) as f:
            sarif_data = json.load(f)
            self.assertEqual(sarif_data["version"], "2.1.0")
            self.assertEqual(
                sarif_data["runs"][0]["tool"]["driver"]["name"], "TestTool"
            )
            self.assertEqual(len(sarif_data["runs"][0]["results"]), 1)
            self.assertEqual(sarif_data["runs"][0]["results"][0]["ruleId"], "test-rule")
            self.assertEqual(
                sarif_data["runs"][0]["results"][0]["message"]["text"], "Test message"
            )


if __name__ == "__main__":
    unittest.main()
