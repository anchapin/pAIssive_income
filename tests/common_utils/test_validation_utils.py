"""
Tests for the validation utilities.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from pydantic import BaseModel, Field

from common_utils.validation_utils import (
    is_valid_date,
    is_valid_directory,
    is_valid_email,
    is_valid_file,
    is_valid_file_path,
    is_valid_json,
    is_valid_password,
    is_valid_phone,
    is_valid_slug,
    is_valid_url,
    is_valid_username,
    is_valid_uuid,
    sanitize_filename,
    sanitize_html,
    sanitize_path,
    sanitize_string,
    validate_and_sanitize_input,
    validate_config_file,
)


class TestValidationUtils(unittest.TestCase):
    """Test case for validation utilities."""

    def test_is_valid_email(self):
        """Test is_valid_email function."""
        # Valid emails
        self.assertTrue(is_valid_email("user@example.com"))
        self.assertTrue(is_valid_email("user.name@example.co.uk"))
        self.assertTrue(is_valid_email("user+tag@example.com"))
        self.assertTrue(is_valid_email("user123@example.com"))

        # Invalid emails
        self.assertFalse(is_valid_email(""))
        self.assertFalse(is_valid_email("user"))
        self.assertFalse(is_valid_email("user@"))
        self.assertFalse(is_valid_email("@example.com"))
        self.assertFalse(is_valid_email("user@example"))
        self.assertFalse(is_valid_email("user@.com"))
        self.assertFalse(is_valid_email("user@example..com"))

    def test_is_valid_url(self):
        """Test is_valid_url function."""
        # Valid URLs
        self.assertTrue(is_valid_url("http://example.com"))
        self.assertTrue(is_valid_url("https://example.com"))
        self.assertTrue(is_valid_url("http://example.com/path"))
        self.assertTrue(is_valid_url("http://example.com/path?query=value"))
        self.assertTrue(is_valid_url("http://example.com/path#fragment"))

        # Invalid URLs
        self.assertFalse(is_valid_url(""))
        self.assertFalse(is_valid_url("example.com"))
        self.assertFalse(is_valid_url("http://"))
        self.assertFalse(is_valid_url("http:/example.com"))
        self.assertFalse(is_valid_url("ftp://example.com"))

    def test_is_valid_uuid(self):
        """Test is_valid_uuid function."""
        # Valid UUIDs
        self.assertTrue(is_valid_uuid("123e4567-e89b-12d3-a456-426614174000"))
        self.assertTrue(is_valid_uuid("00000000-0000-0000-0000-000000000000"))

        # Invalid UUIDs
        self.assertFalse(is_valid_uuid(""))
        self.assertFalse(is_valid_uuid("123e4567"))
        self.assertFalse(is_valid_uuid("123e4567-e89b-12d3-a456"))
        self.assertFalse(is_valid_uuid("123e4567-e89b-12d3-a456-42661417400g"))

    def test_is_valid_phone(self):
        """Test is_valid_phone function."""
        # Valid phone numbers
        self.assertTrue(is_valid_phone("1234567890"))
        self.assertTrue(is_valid_phone("+1 (123) 456-7890"))
        self.assertTrue(is_valid_phone("123-456-7890"))
        self.assertTrue(is_valid_phone("123.456.7890"))

        # Invalid phone numbers
        self.assertFalse(is_valid_phone(""))
        self.assertFalse(is_valid_phone("123"))
        self.assertFalse(is_valid_phone("abcdefghij"))
        self.assertFalse(is_valid_phone("123-456-789a"))

    def test_is_valid_username(self):
        """Test is_valid_username function."""
        # Valid usernames
        self.assertTrue(is_valid_username("user"))
        self.assertTrue(is_valid_username("user123"))
        self.assertTrue(is_valid_username("user_name"))
        self.assertTrue(is_valid_username("user-name"))

        # Invalid usernames
        self.assertFalse(is_valid_username(""))
        self.assertFalse(is_valid_username("us"))
        self.assertFalse(is_valid_username("user name"))
        self.assertFalse(is_valid_username("user@name"))
        self.assertFalse(is_valid_username("user_name_that_is_too_long"))

    def test_is_valid_password(self):
        """Test is_valid_password function."""
        # Valid passwords
        self.assertTrue(is_valid_password("Password1!"))
        self.assertTrue(is_valid_password("p@ssw0rd"))
        self.assertTrue(is_valid_password("SecureP@ss123"))

        # Invalid passwords
        self.assertFalse(is_valid_password(""))
        self.assertFalse(is_valid_password("password"))
        self.assertFalse(is_valid_password("PASSWORD"))
        self.assertFalse(is_valid_password("12345678"))
        self.assertFalse(is_valid_password("pass1"))
        self.assertFalse(is_valid_password("password1"))
        self.assertFalse(is_valid_password("Password1"))

    def test_is_valid_slug(self):
        """Test is_valid_slug function."""
        # Valid slugs
        self.assertTrue(is_valid_slug("slug"))
        self.assertTrue(is_valid_slug("slug-name"))
        self.assertTrue(is_valid_slug("slug-123"))

        # Invalid slugs
        self.assertFalse(is_valid_slug(""))
        self.assertFalse(is_valid_slug("slug name"))
        self.assertFalse(is_valid_slug("slug_name"))
        self.assertFalse(is_valid_slug("Slug-Name"))
        self.assertFalse(is_valid_slug("-slug"))
        self.assertFalse(is_valid_slug("slug-"))

    def test_is_valid_json(self):
        """Test is_valid_json function."""
        # Valid JSON
        self.assertTrue(is_valid_json('{"key": "value"}'))
        self.assertTrue(is_valid_json('{"key": 123}'))
        self.assertTrue(is_valid_json('{"key": true}'))
        self.assertTrue(is_valid_json('{"key": null}'))
        self.assertTrue(is_valid_json('{"key": ["value1", "value2"]}'))
        self.assertTrue(is_valid_json('{"key": {"nested": "value"}}'))

        # Invalid JSON
        self.assertFalse(is_valid_json(""))
        self.assertFalse(is_valid_json("{key: value}"))
        self.assertFalse(is_valid_json("{'key': 'value'}"))
        self.assertFalse(is_valid_json('{"key": value}'))
        self.assertFalse(is_valid_json('{"key": "value"'))

    def test_is_valid_date(self):
        """Test is_valid_date function."""
        # Valid dates
        self.assertTrue(is_valid_date("2023-01-01"))
        self.assertTrue(is_valid_date("2023-12-31"))
        self.assertTrue(is_valid_date("01/01/2023", "%m/%d/%Y"))
        self.assertTrue(is_valid_date("31/12/2023", "%d/%m/%Y"))

        # Invalid dates
        self.assertFalse(is_valid_date(""))
        self.assertFalse(is_valid_date("2023-13-01"))
        self.assertFalse(is_valid_date("2023-01-32"))
        self.assertFalse(is_valid_date("01/01/2023", "%Y-%m-%d"))
        self.assertFalse(is_valid_date("2023-01-01", "%m/%d/%Y"))

    def test_is_valid_file_path(self):
        """Test is_valid_file_path function."""
        # Valid file paths
        self.assertTrue(is_valid_file_path("file.txt"))
        self.assertTrue(is_valid_file_path("path/to/file.txt"))
        self.assertTrue(is_valid_file_path("/absolute/path/to/file.txt"))
        self.assertTrue(is_valid_file_path("C:\\Windows\\file.txt"))

        # Invalid file paths
        self.assertFalse(is_valid_file_path(""))
        # Most strings can be interpreted as file paths, so it's hard to find invalid examples

    def test_is_valid_file(self):
        """Test is_valid_file function."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            # Valid file
            self.assertTrue(is_valid_file(temp_file_path))
            self.assertTrue(is_valid_file(temp_file_path, must_exist=True))

            # Non-existent file
            non_existent_file = temp_file_path + ".non_existent"
            self.assertFalse(is_valid_file(non_existent_file))
            self.assertTrue(is_valid_file(non_existent_file, must_exist=False))

            # Invalid file path
            self.assertFalse(is_valid_file(""))
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_is_valid_directory(self):
        """Test is_valid_directory function."""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            # Valid directory
            self.assertTrue(is_valid_directory(temp_dir))
            self.assertTrue(is_valid_directory(temp_dir, must_exist=True))

            # Non-existent directory
            non_existent_dir = temp_dir + "_non_existent"
            self.assertFalse(is_valid_directory(non_existent_dir))
            self.assertTrue(is_valid_directory(non_existent_dir, must_exist=False))

            # Invalid directory path
            self.assertFalse(is_valid_directory(""))
        finally:
            # Clean up
            os.rmdir(temp_dir)

    def test_sanitize_string(self):
        """Test sanitize_string function."""
        # Test sanitization
        self.assertEqual(
            sanitize_string("<script>alert('XSS')</script>"),
            "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;",
        )
        self.assertEqual(
            sanitize_string('"><script>alert("XSS")</script>'),
            "&quot;&gt;&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;",
        )
        self.assertEqual(sanitize_string("Normal string"), "Normal string")
        self.assertEqual(sanitize_string(""), "")
        self.assertEqual(sanitize_string(None), "")

    def test_sanitize_html(self):
        """Test sanitize_html function."""
        # Test sanitization
        self.assertEqual(
            sanitize_html("<script>alert('XSS')</script>"),
            "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;",
        )
        self.assertEqual(sanitize_html("<b>Bold text</b>"), "&lt;b&gt;Bold text&lt;/b&gt;")
        self.assertEqual(sanitize_html("Normal string"), "Normal string")
        self.assertEqual(sanitize_html(""), "")
        self.assertEqual(sanitize_html(None), "")

    def test_sanitize_filename(self):
        """Test sanitize_filename function."""
        # Test sanitization
        self.assertEqual(sanitize_filename("file.txt"), "file.txt")
        self.assertEqual(sanitize_filename("../file.txt"), "file.txt")
        self.assertEqual(sanitize_filename("file/name.txt"), "name.txt")
        self.assertEqual(sanitize_filename("file\\name.txt"), "name.txt")
        self.assertEqual(sanitize_filename("file:name.txt"), "name.txt")
        self.assertEqual(sanitize_filename("file*name.txt"), "filename.txt")
        self.assertEqual(sanitize_filename("file?name.txt"), "filename.txt")
        self.assertEqual(sanitize_filename('file"name.txt'), "filename.txt")
        self.assertEqual(sanitize_filename("file<name.txt"), "filename.txt")
        self.assertEqual(sanitize_filename("file>name.txt"), "filename.txt")
        self.assertEqual(sanitize_filename("file|name.txt"), "filename.txt")
        self.assertEqual(sanitize_filename(""), "")
        self.assertEqual(sanitize_filename(None), "")

    def test_sanitize_path(self):
        """Test sanitize_path function."""
        # Test sanitization
        current_dir = os.getcwd()
        self.assertEqual(sanitize_path("."), current_dir)
        self.assertEqual(sanitize_path("./file.txt"), os.path.join(current_dir, "file.txt"))
        self.assertEqual(
            sanitize_path("../file.txt"),
            os.path.normpath(os.path.join(current_dir, "..", "file.txt")),
        )
        self.assertEqual(sanitize_path(""), "")
        self.assertEqual(sanitize_path(None), "")

    def test_validate_and_sanitize_input(self):
        """Test validate_and_sanitize_input function."""
        # Test validation and sanitization
        # Valid input
        self.assertEqual(
            validate_and_sanitize_input("user@example.com", is_valid_email, sanitize_string),
            "user@example.com",
        )

        # Invalid input
        with self.assertRaises(ValueError):
            validate_and_sanitize_input("invalid-email", is_valid_email, sanitize_string)

        # Custom error message
        with self.assertRaises(ValueError) as cm:
            validate_and_sanitize_input(
                "invalid-email", is_valid_email, sanitize_string, "Custom error message"
            )
        self.assertEqual(str(cm.exception), "Custom error message")

    def test_validate_config_file(self):
        """Test validate_config_file function."""

        # Define a Pydantic model for testing
        class TestConfig(BaseModel):
            name: str = Field(..., min_length=1)
            value: int = Field(..., ge=0)

        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp_file:
            # Valid config
            json.dump({"name": "test", "value": 42}, temp_file)
            temp_file_path = temp_file.name

        try:
            # Test validation with valid config
            config = validate_config_file(temp_file_path, TestConfig)
            self.assertEqual(config.name, "test")
            self.assertEqual(config.value, 42)

            # Test validation with invalid config
            with open(temp_file_path, "w") as f:
                json.dump({"name": "", "value": -1}, f)

            with self.assertRaises(ValueError):
                validate_config_file(temp_file_path, TestConfig)

            # Test validation with invalid JSON
            with open(temp_file_path, "w") as f:
                f.write("invalid json")

            with self.assertRaises(ValueError):
                validate_config_file(temp_file_path, TestConfig)

            # Test validation with non-existent file
            non_existent_file = temp_file_path + ".non_existent"
            with self.assertRaises(ValueError):
                validate_config_file(non_existent_file, TestConfig)
        finally:
            # Clean up
            os.unlink(temp_file_path)


if __name__ == "__main__":
    unittest.main()
