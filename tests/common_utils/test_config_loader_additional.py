"""Additional tests for the common_utils.config_loader module to improve coverage."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from pydantic import ValidationError as PydanticValidationError

from common_utils.config_loader import load_config, ExampleConfigModel
from common_utils.validation.core import ValidationError


class TestConfigLoaderAdditional:
    """Additional test suite for config_loader module to improve coverage."""

    def test_example_config_model_validation(self):
        """Test validation in ExampleConfigModel."""
        # Test with valid data
        valid_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 50
        }
        config = ExampleConfigModel(**valid_data)
        assert config.db_url == valid_data["db_url"]
        assert config.debug is True
        assert config.max_connections == 50

        # Test with invalid db_url (too short)
        invalid_data = {
            "db_url": "short",
            "debug": True,
            "max_connections": 50
        }
        with pytest.raises(PydanticValidationError):
            ExampleConfigModel(**invalid_data)

        # Test with invalid max_connections (too large)
        invalid_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 101
        }
        with pytest.raises(PydanticValidationError):
            ExampleConfigModel(**invalid_data)

        # Test with invalid max_connections (too small)
        invalid_data = {
            "db_url": "postgresql://user:password@localhost:5432/db",
            "debug": True,
            "max_connections": 0
        }
        with pytest.raises(PydanticValidationError):
            ExampleConfigModel(**invalid_data)

    def test_example_config_model_default_values(self):
        """Test default values in ExampleConfigModel."""
        # Test with only required fields
        config = ExampleConfigModel(
            db_url="postgresql://user:password@localhost:5432/db",
            max_connections=50
        )
        assert config.db_url == "postgresql://user:password@localhost:5432/db"
        assert config.debug is False  # Default value
        assert config.max_connections == 50

    def test_example_config_model_dict_method(self):
        """Test the dict method of ExampleConfigModel."""
        config = ExampleConfigModel(
            db_url="postgresql://user:password@localhost:5432/db",
            debug=True,
            max_connections=50
        )
        config_dict = config.dict()
        assert isinstance(config_dict, dict)
        assert config_dict["db_url"] == "postgresql://user:password@localhost:5432/db"
        assert config_dict["debug"] is True
        assert config_dict["max_connections"] == 50

    def test_example_config_model_json_method(self):
        """Test the json method of ExampleConfigModel."""
        config = ExampleConfigModel(
            db_url="postgresql://user:password@localhost:5432/db",
            debug=True,
            max_connections=50
        )
        config_json = config.json()
        assert isinstance(config_json, str)

        # Parse the JSON string back to a dict
        config_dict = json.loads(config_json)
        assert config_dict["db_url"] == "postgresql://user:password@localhost:5432/db"
        assert config_dict["debug"] is True
        assert config_dict["max_connections"] == 50

    def test_load_config_with_path_object(self):
        """Test load_config with a Path object."""
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
            # Convert to Path object
            path_obj = Path(temp_path)

            # Load the config
            config = load_config(path_obj)

            # Verify the config was loaded correctly
            assert isinstance(config, ExampleConfigModel)
            assert config.db_url == valid_config["db_url"]
            assert config.debug is True
            assert config.max_connections == 50
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)

    def test_load_config_with_invalid_json(self):
        """Test load_config with invalid JSON."""
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

    def test_load_config_with_validation_error(self):
        """Test load_config with validation error."""
        # Create a temporary config file with invalid data
        invalid_config = {
            "db_url": "short",  # Too short to pass validation
            "debug": True,
            "max_connections": 50
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump(invalid_config, temp_file)
            temp_path = temp_file.name

        try:
            # Attempt to load the config - this should raise ValidationError
            # because the db_url is too short (min_length=10)
            with pytest.raises(ValidationError):
                load_config(temp_path)
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)

    @patch('common_utils.config_loader.logger')
    def test_load_config_logs_validation_error(self, mock_logger):
        """Test that load_config logs validation errors."""
        # Create a temporary config file with invalid data
        invalid_config = {
            "db_url": "short",  # Too short to pass validation
            "debug": True,
            "max_connections": 50
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump(invalid_config, temp_file)
            temp_path = temp_file.name

        try:
            # Attempt to load the config - this should raise ValidationError
            # because the db_url is too short (min_length=10)
            with pytest.raises(ValidationError):
                load_config(temp_path)

            # Verify that the error was logged
            # The exact details will vary, but we can check that logger.exception was called
            mock_logger.exception.assert_called_once()
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
