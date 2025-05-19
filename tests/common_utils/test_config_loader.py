"""test_config_loader - Module for tests/common_utils.test_config_loader."""

# Standard library imports
import logging
import json
import os
import tempfile
from unittest.mock import patch, MagicMock

# Third-party imports
import pytest
from pydantic import ValidationError as PydanticValidationError

# Local imports
from common_utils.config_loader import load_config, ExampleConfigModel
from common_utils.validation.core import ValidationError


class TestConfigLoader:
    """Test suite for the config_loader module."""

    def test_example_config_model(self):
        """Test the ExampleConfigModel validation."""
        # Valid configuration
        valid_config = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 50
        }
        config = ExampleConfigModel(**valid_config)
        assert config.db_url == valid_config["db_url"]
        assert config.debug is True
        assert config.max_connections == 50

        # Test default values
        minimal_config = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "max_connections": 10
        }
        config = ExampleConfigModel(**minimal_config)
        assert config.debug is False  # Default value

        # Test validation errors
        with pytest.raises(PydanticValidationError):
            # db_url too short
            ExampleConfigModel(db_url="short", max_connections=10)

        with pytest.raises(PydanticValidationError):
            # max_connections out of range
            ExampleConfigModel(db_url="postgresql://localhost", max_connections=101)

        with pytest.raises(PydanticValidationError):
            # max_connections out of range (too low)
            ExampleConfigModel(db_url="postgresql://localhost", max_connections=0)

    def test_load_config_success(self):
        """Test loading a valid configuration file."""
        # Create a temporary config file
        valid_config = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 50
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump(valid_config, temp_file)
            temp_path = temp_file.name

        try:
            # Load the config
            config = load_config(temp_path)

            # Verify the config was loaded correctly
            assert isinstance(config, ExampleConfigModel)
            assert config.db_url == valid_config["db_url"]
            assert config.debug is True
            assert config.max_connections == 50
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)

    def test_load_config_invalid_json(self):
        """Test loading an invalid JSON file."""
        # Create a temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("This is not valid JSON")
            temp_path = temp_file.name

        try:
            # Attempt to load the config
            with pytest.raises(json.JSONDecodeError):
                load_config(temp_path)
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)

    def test_load_config_validation_error(self):
        """Test loading a config with validation errors."""
        # Create a temporary config file with invalid data
        invalid_config = {
            "db_url": "short",  # Too short
            "debug": True,
            "max_connections": 50
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump(invalid_config, temp_file)
            temp_path = temp_file.name

        try:
            # Attempt to load the config
            with pytest.raises(ValidationError):
                load_config(temp_path)
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)

    @patch('common_utils.config_loader.validate_input')
    @patch('common_utils.config_loader.logger')
    def test_load_config_logs_validation_error(self, mock_logger, mock_validate_input):
        """Test that validation errors are logged."""
        # Create a mock validation error
        mock_error = ValidationError("Validation failed")
        mock_error.details = {"field": "error message"}

        # Configure the mock to raise the validation error
        mock_validate_input.side_effect = mock_error

        # Create a temporary config file
        valid_config = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 50
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump(valid_config, temp_file)
            temp_path = temp_file.name

        try:
            # Attempt to load the config
            with pytest.raises(ValidationError):
                load_config(temp_path)

            # Verify that the error was logged
            mock_logger.exception.assert_called_once_with(
                "Config validation failed: %s", mock_error.details
            )
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)

    def test_example_config_model_dict_method(self):
        """Test the dict method of ExampleConfigModel."""
        # Create a valid configuration
        valid_config = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 50
        }

        # Create a config model
        config = ExampleConfigModel(**valid_config)

        # Convert to dict and verify
        config_dict = config.dict()
        assert isinstance(config_dict, dict)
        assert config_dict["db_url"] == valid_config["db_url"]
        assert config_dict["debug"] is True
        assert config_dict["max_connections"] == 50

    def test_example_config_model_json_method(self):
        """Test the json method of ExampleConfigModel."""
        # Create a valid configuration
        valid_config = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 50
        }

        # Create a config model
        config = ExampleConfigModel(**valid_config)

        # Convert to JSON and verify
        config_json = config.json()
        assert isinstance(config_json, str)

        # Parse the JSON and verify the contents
        parsed_json = json.loads(config_json)
        assert parsed_json["db_url"] == valid_config["db_url"]
        assert parsed_json["debug"] is True
        assert parsed_json["max_connections"] == 50

    @patch('pathlib.Path.open')
    def test_load_config_file_not_found(self, mock_open):
        """Test loading a configuration file that doesn't exist."""
        # Configure the mock to raise FileNotFoundError
        mock_open.side_effect = FileNotFoundError("File not found")

        # Attempt to load the config
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_file.json")

    def test_example_config_model_schema(self):
        """Test the schema method of ExampleConfigModel."""
        # Get the schema
        schema = ExampleConfigModel.schema()

        # Verify the schema
        assert isinstance(schema, dict)
        assert schema["title"] == "ExampleConfigModel"
        assert "properties" in schema
        assert "db_url" in schema["properties"]
        assert "debug" in schema["properties"]
        assert "max_connections" in schema["properties"]
