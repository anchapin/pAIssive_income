"""Tests for the common_utils/config_loader.py module."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from common_utils.config_loader import ExampleConfigModel, load_config
from common_utils.validation.core import ValidationError


class TestConfigLoader(unittest.TestCase):
    """Test cases for the common_utils/config_loader.py module."""

    def test_example_config_model_valid(self):
        """Test ExampleConfigModel with valid data."""
        config = ExampleConfigModel(
            db_url="postgresql://user:pass@localhost:5432/db",
            debug=True,
            max_connections=50
        )
        assert config.db_url == "postgresql://user:pass@localhost:5432/db"
        assert config.debug
        assert config.max_connections == 50

    def test_example_config_model_defaults(self):
        """Test ExampleConfigModel with default values."""
        config = ExampleConfigModel(
            db_url="postgresql://user:pass@localhost:5432/db",
            max_connections=50
        )
        assert config.db_url == "postgresql://user:pass@localhost:5432/db"
        assert not config.debug  # Default value
        assert config.max_connections == 50

    @patch("common_utils.config_loader.validate_input")
    def test_load_config_success(self, mock_validate_input):
        """Test load_config with valid configuration."""
        # Create a temporary config file
        config_data = {
            "db_url": "postgresql://user:pass@localhost:5432/db",
            "debug": True,
            "max_connections": 50
        }

        # Mock the validate_input function to return a valid config
        mock_config = ExampleConfigModel(**config_data)
        mock_validate_input.return_value = mock_config

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            json.dump(config_data, temp_file)
            temp_file_path = temp_file.name

        try:
            # Test loading the config
            config = load_config(temp_file_path)

            # Verify the config was loaded correctly
            assert config.db_url == "postgresql://user:pass@localhost:5432/db"
            assert config.debug
            assert config.max_connections == 50

            # Verify validate_input was called
            mock_validate_input.assert_called_once()
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    @patch("common_utils.config_loader.validate_input")
    def test_load_config_validation_error(self, mock_validate_input):
        """Test load_config with invalid configuration."""
        # Create a temporary config file
        config_data = {
            "db_url": "postgresql://user:pass@localhost:5432/db",
            "debug": True,
            "max_connections": 50
        }

        # Mock validate_input to raise a ValidationError
        validation_error = ValidationError("Validation failed", {"details": "Invalid config"})
        mock_validate_input.side_effect = validation_error

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            json.dump(config_data, temp_file)
            temp_file_path = temp_file.name

        try:
            # Test loading the config should raise ValidationError
            with pytest.raises(ValidationError):
                load_config(temp_file_path)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)


if __name__ == "__main__":
    unittest.main()
