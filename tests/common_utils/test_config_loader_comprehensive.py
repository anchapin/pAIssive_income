"""Comprehensive tests for the common_utils.config_loader module."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from pydantic import ValidationError as PydanticValidationError

from common_utils.config_loader import load_config, ExampleConfigModel
from common_utils.validation.core import ValidationError


class TestConfigLoaderComprehensive:
    """Comprehensive test suite for config_loader module."""

    def setup_method(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up after tests."""
        # Remove the temporary directory and its contents
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_load_config_valid(self):
        """Test loading a valid configuration file."""
        # Create a valid config file
        config_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 50
        }
        config_file = os.path.join(self.temp_dir, "valid_config.json")
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Load the config
        config = load_config(config_file)

        # Verify the config was loaded correctly
        assert isinstance(config, ExampleConfigModel)
        assert config.db_url == config_data["db_url"]
        assert config.debug is True
        assert config.max_connections == 50

    def test_load_config_missing_required_field(self):
        """Test loading a config file with a missing required field."""
        # Create a config file with a missing required field
        config_data = {
            "debug": True,
            "max_connections": 50
            # Missing db_url
        }
        config_file = os.path.join(self.temp_dir, "missing_field_config.json")
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Attempt to load the config
        with pytest.raises(ValidationError) as excinfo:
            load_config(config_file)

        # Verify the error message
        assert "db_url" in str(excinfo.value)
        assert "field required" in str(excinfo.value).lower()

    def test_load_config_invalid_field_type(self):
        """Test loading a config file with an invalid field type."""
        # Create a config file with an invalid field type
        config_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": "not_a_boolean",  # Should be a boolean
            "max_connections": 50
        }
        config_file = os.path.join(self.temp_dir, "invalid_type_config.json")
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Attempt to load the config
        with pytest.raises(ValidationError) as excinfo:
            load_config(config_file)

        # Verify the error message
        assert "debug" in str(excinfo.value)
        assert "bool" in str(excinfo.value).lower()

    def test_load_config_invalid_field_value(self):
        """Test loading a config file with an invalid field value."""
        # Create a config file with an invalid field value
        config_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 0  # Should be >= 1
        }
        config_file = os.path.join(self.temp_dir, "invalid_value_config.json")
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Attempt to load the config
        with pytest.raises(ValidationError) as excinfo:
            load_config(config_file)

        # Verify the error message
        assert "max_connections" in str(excinfo.value)
        assert "greater than or equal to" in str(excinfo.value).lower()

    def test_load_config_file_not_found(self):
        """Test loading a non-existent config file."""
        # Attempt to load a non-existent config file
        with pytest.raises(FileNotFoundError):
            load_config(os.path.join(self.temp_dir, "nonexistent_config.json"))

    def test_load_config_invalid_json(self):
        """Test loading a config file with invalid JSON."""
        # Create a file with invalid JSON
        config_file = os.path.join(self.temp_dir, "invalid_json_config.json")
        with open(config_file, "w") as f:
            f.write("This is not valid JSON")

        # Attempt to load the config
        with pytest.raises(json.JSONDecodeError):
            load_config(config_file)

    def test_load_config_with_default_values(self):
        """Test loading a config file with default values."""
        # Create a config file with only required fields
        config_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "max_connections": 50
            # debug is optional and has a default value of False
        }
        config_file = os.path.join(self.temp_dir, "default_values_config.json")
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Load the config
        config = load_config(config_file)

        # Verify the config was loaded correctly
        assert isinstance(config, ExampleConfigModel)
        assert config.db_url == config_data["db_url"]
        assert config.debug is False  # Default value
        assert config.max_connections == 50

    def test_load_config_with_extra_fields(self):
        """Test loading a config file with extra fields."""
        # Create a config file with extra fields
        config_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 50,
            "extra_field": "This field is not in the model"
        }
        config_file = os.path.join(self.temp_dir, "extra_fields_config.json")
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Load the config
        config = load_config(config_file)

        # Verify the config was loaded correctly
        assert isinstance(config, ExampleConfigModel)
        assert config.db_url == config_data["db_url"]
        assert config.debug is True
        assert config.max_connections == 50
        # Extra field should be ignored
        assert not hasattr(config, "extra_field")

    @patch("common_utils.config_loader.validate_input")
    def test_load_config_validation_error_handling(self, mock_validate_input):
        """Test handling of validation errors."""
        # Create a valid config file
        config_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 50
        }
        config_file = os.path.join(self.temp_dir, "valid_config.json")
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Mock validate_input to raise a ValidationError
        mock_error = ValidationError("Validation failed", {"details": "Error details"})
        mock_validate_input.side_effect = mock_error

        # Attempt to load the config
        with pytest.raises(ValidationError) as excinfo:
            load_config(config_file)

        # Verify the error was propagated
        assert excinfo.value == mock_error

    @patch("common_utils.config_loader.logger")
    def test_load_config_validation_error_logging(self, mock_logger):
        """Test logging of validation errors."""
        # Create a config file with an invalid field value
        config_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 0  # Should be >= 1
        }
        config_file = os.path.join(self.temp_dir, "invalid_value_config.json")
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Attempt to load the config
        with pytest.raises(ValidationError):
            load_config(config_file)

        # Verify that the error was logged
        mock_logger.exception.assert_called_once()
        assert "Config validation failed" in mock_logger.exception.call_args[0][0]

    def test_example_config_model_validation(self):
        """Test validation of ExampleConfigModel directly."""
        # Valid data
        valid_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 50
        }
        config = ExampleConfigModel(**valid_data)
        assert config.db_url == valid_data["db_url"]
        assert config.debug is True
        assert config.max_connections == 50

        # Invalid data - missing required field
        invalid_data = {
            "debug": True,
            "max_connections": 50
            # Missing db_url
        }
        with pytest.raises(PydanticValidationError):
            ExampleConfigModel(**invalid_data)

        # Invalid data - invalid field type
        invalid_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": "not_a_boolean",  # Should be a boolean
            "max_connections": 50
        }
        with pytest.raises(PydanticValidationError):
            ExampleConfigModel(**invalid_data)

        # Invalid data - invalid field value
        invalid_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 0  # Should be >= 1
        }
        with pytest.raises(PydanticValidationError):
            ExampleConfigModel(**invalid_data)

        # Invalid data - db_url too short
        invalid_data = {
            "db_url": "short",  # Should be at least 10 characters
            "debug": True,
            "max_connections": 50
        }
        with pytest.raises(PydanticValidationError):
            ExampleConfigModel(**invalid_data)

        # Invalid data - max_connections too large
        invalid_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 101  # Should be <= 100
        }
        with pytest.raises(PydanticValidationError):
            ExampleConfigModel(**invalid_data)
