#!/usr/bin/env python3
"""
Test script for sarif_utils.py.

This script tests the sarif_utils.py script with various input scenarios
to ensure it handles edge cases correctly.
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Add the project root to the Python path for importing scripts package
_PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.utils import sarif_utils  # noqa: E402


@pytest.fixture
def test_dir():
    """Create a temporary directory for test files."""
    test_dir = tempfile.mkdtemp()
    yield test_dir
    # Cleanup
    shutil.rmtree(test_dir)


@pytest.fixture
def output_file(test_dir):
    """Create output file path."""
    return Path(test_dir) / "output.sarif"


class TestSarifUtils:
    """Test cases for sarif_utils.py."""

    def test_empty_input_file(self, test_dir, output_file):
        """Test with an empty input file."""
        # Create an empty input file
        input_file = Path(test_dir) / "empty.json"
        input_file.touch()  # Create empty file

        # Convert the file
        result = sarif_utils.convert_file(
            input_file, output_file, "TestTool", "https://example.com"
        )

        # Check that conversion was successful
        assert result
        # Check that output file exists
        assert output_file.exists()
        # Check that output file is valid SARIF
        with output_file.open() as f:
            sarif_data = json.load(f)
            assert sarif_data["version"] == "2.1.0"
            assert sarif_data["runs"][0]["tool"]["driver"]["name"] == "TestTool"
            assert len(sarif_data["runs"][0]["results"]) == 0

    def test_nonexistent_input_file(self, test_dir, output_file):
        """Test with a nonexistent input file."""
        # Use a file path that doesn't exist
        input_file = Path(test_dir) / "nonexistent.json"

        # Convert the file
        result = sarif_utils.convert_file(
            input_file, output_file, "TestTool", "https://example.com"
        )

        # Check that conversion was successful (creates empty SARIF)
        assert result
        # Check that output file exists
        assert output_file.exists()
        # Check that output file is valid SARIF
        with output_file.open() as f:
            sarif_data = json.load(f)
            assert sarif_data["version"] == "2.1.0"
            assert sarif_data["runs"][0]["tool"]["driver"]["name"] == "TestTool"
            assert len(sarif_data["runs"][0]["results"]) == 0

    def test_invalid_json_input_file(self, test_dir, output_file):
        """Test with an invalid JSON input file."""
        # Create an invalid JSON input file
        input_file = Path(test_dir) / "invalid.json"
        with input_file.open("w") as f:
            f.write("{invalid json")

        # Convert the file
        result = sarif_utils.convert_file(
            input_file, output_file, "TestTool", "https://example.com"
        )

        # Check that conversion was successful (creates empty SARIF)
        assert result
        # Check that output file exists
        assert output_file.exists()
        # Check that output file is valid SARIF
        with output_file.open() as f:
            sarif_data = json.load(f)
            assert sarif_data["version"] == "2.1.0"
            assert sarif_data["runs"][0]["tool"]["driver"]["name"] == "TestTool"
            assert len(sarif_data["runs"][0]["results"]) == 0

    def test_valid_json_input_file(self, test_dir, output_file):
        """Test with a valid JSON input file."""
        # Create a valid JSON input file
        input_file = Path(test_dir) / "valid.json"
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
        with input_file.open("w") as f:
            json.dump(test_data, f)

        # Convert the file
        result = sarif_utils.convert_file(
            input_file, output_file, "TestTool", "https://example.com"
        )

        # Check that conversion was successful
        assert result
        # Check that output file exists
        assert output_file.exists()
        # Check that output file is valid SARIF
        with output_file.open() as f:
            sarif_data = json.load(f)
            assert sarif_data["version"] == "2.1.0"
            assert sarif_data["runs"][0]["tool"]["driver"]["name"] == "TestTool"
            assert len(sarif_data["runs"][0]["results"]) == 1
            assert sarif_data["runs"][0]["results"][0]["ruleId"] == "test-rule"
            assert (
                sarif_data["runs"][0]["results"][0]["message"]["text"] == "Test message"
            )

    def test_list_json_input_file(self, test_dir, output_file):
        """Test with a JSON input file containing a list instead of a dict."""
        # Create a JSON input file with a list
        input_file = Path(test_dir) / "list.json"
        test_data = [
            {
                "id": "test-rule-1",
                "message": "Test message 1",
                "file": "test1.py",
                "line": 42,
                "severity": "high",
                "name": "Test Rule 1",
                "description": "Test rule description 1",
            },
            {
                "id": "test-rule-2",
                "message": "Test message 2",
                "file": "test2.py",
                "line": 84,
                "severity": "medium",
                "name": "Test Rule 2",
                "description": "Test rule description 2",
            },
        ]
        with input_file.open("w") as f:
            json.dump(test_data, f)

        # Convert the file
        result = sarif_utils.convert_file(
            input_file, output_file, "TestTool", "https://example.com"
        )

        # Check that conversion was successful
        assert result
        # Check that output file exists
        assert output_file.exists()
        # Check that output file is valid SARIF
        with output_file.open() as f:
            sarif_data = json.load(f)
            assert sarif_data["version"] == "2.1.0"
            assert sarif_data["runs"][0]["tool"]["driver"]["name"] == "TestTool"
            # Define expected number of results
            expected_results_count = 2
            # Should have two results
            assert len(sarif_data["runs"][0]["results"]) == expected_results_count
            # Check first result
            results = sarif_data["runs"][0]["results"]
            assert results[0]["ruleId"] == "test-rule-1"
            assert results[0]["message"]["text"] == "Test message 1"
            # Check second result
            assert results[1]["ruleId"] == "test-rule-2"
            assert results[1]["message"]["text"] == "Test message 2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
