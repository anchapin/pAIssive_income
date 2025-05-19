"""Comprehensive tests for the common_utils.json_utils module."""

import json
import os
import tempfile
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import pytest

from common_utils.json_utils import (
    DateTimeEncoder,
    load_json_file,
    save_json_file,
    json_to_string,
    string_to_json,
    merge_json_objects,
    flatten_json,
    unflatten_json,
)
from common_utils.exceptions import MissingFileError, FilePermissionError


class TestJsonUtilsComprehensive:
    """Comprehensive test suite for JSON utility functions."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

        # Create a test JSON file
        self.test_json_file = os.path.join(self.temp_dir, "test.json")
        self.test_data = {"key": "value", "list": [1, 2, 3], "nested": {"inner": "value"}}
        with open(self.test_json_file, "w") as f:
            json.dump(self.test_data, f)

    def teardown_method(self):
        """Clean up after each test."""
        # Remove the temporary directory and all its contents
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_date_time_encoder_datetime(self):
        """Test DateTimeEncoder with datetime objects."""
        dt = datetime(2023, 1, 15, 12, 30, 45)
        data = {"datetime": dt}
        json_str = json.dumps(data, cls=DateTimeEncoder)
        assert json_str == '{"datetime": "2023-01-15T12:30:45"}'

        # Parse and verify
        parsed = json.loads(json_str)
        assert parsed["datetime"] == "2023-01-15T12:30:45"

    def test_date_time_encoder_date(self):
        """Test DateTimeEncoder with date objects."""
        d = date(2023, 1, 15)
        data = {"date": d}
        json_str = json.dumps(data, cls=DateTimeEncoder)
        assert json_str == '{"date": "2023-01-15"}'

        # Parse and verify
        parsed = json.loads(json_str)
        assert parsed["date"] == "2023-01-15"

    def test_date_time_encoder_mixed(self):
        """Test DateTimeEncoder with mixed data types."""
        dt = datetime(2023, 1, 15, 12, 30, 45)
        d = date(2023, 1, 15)
        data = {
            "datetime": dt,
            "date": d,
            "string": "test",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"key": "value"}
        }

        json_str = json.dumps(data, cls=DateTimeEncoder)
        parsed = json.loads(json_str)

        assert parsed["datetime"] == "2023-01-15T12:30:45"
        assert parsed["date"] == "2023-01-15"
        assert parsed["string"] == "test"
        assert parsed["number"] == 42
        assert parsed["list"] == [1, 2, 3]
        assert parsed["nested"] == {"key": "value"}

    def test_load_json_file_basic(self):
        """Test basic functionality of load_json_file."""
        data = load_json_file(self.test_json_file)
        assert data == self.test_data

    def test_load_json_file_nonexistent(self):
        """Test load_json_file with a non-existent file."""
        with pytest.raises(MissingFileError):
            load_json_file(os.path.join(self.temp_dir, "nonexistent.json"))

    @patch("builtins.open", new_callable=mock_open)
    def test_load_json_file_permission_error(self, mock_file):
        """Test load_json_file with permission error."""
        mock_file.side_effect = PermissionError("Permission denied")

        with pytest.raises(FilePermissionError) as excinfo:
            load_json_file(self.test_json_file)

        assert "Cannot read file" in str(excinfo.value)

    def test_save_json_file_basic(self):
        """Test basic functionality of save_json_file."""
        new_file = os.path.join(self.temp_dir, "new_file.json")
        save_json_file(new_file, self.test_data)

        # Verify the file was created
        assert os.path.isfile(new_file)

        # Load and verify the content
        with open(new_file, "r") as f:
            loaded_data = json.load(f)

        assert loaded_data == self.test_data

    def test_save_json_file_create_dirs(self):
        """Test save_json_file with create_dirs option."""
        new_file = os.path.join(self.temp_dir, "new_dir", "new_file.json")
        save_json_file(new_file, self.test_data, create_dirs=True)

        # Verify the directory and file were created
        assert os.path.isdir(os.path.join(self.temp_dir, "new_dir"))
        assert os.path.isfile(new_file)

        # Load and verify the content
        with open(new_file, "r") as f:
            loaded_data = json.load(f)

        assert loaded_data == self.test_data

    def test_save_json_file_with_datetime(self):
        """Test save_json_file with datetime and date objects."""
        dt = datetime(2023, 1, 15, 12, 30, 45)
        d = date(2023, 1, 15)
        data_with_dates = {"datetime": dt, "date": d}

        new_file = os.path.join(self.temp_dir, "dates.json")
        save_json_file(new_file, data_with_dates)

        # Verify the file was created
        assert os.path.isfile(new_file)

        # Load and verify the content
        with open(new_file, "r") as f:
            loaded_data = json.load(f)

        assert loaded_data["datetime"] == "2023-01-15T12:30:45"
        assert loaded_data["date"] == "2023-01-15"

    @patch("builtins.open", new_callable=mock_open)
    def test_save_json_file_permission_error(self, mock_file):
        """Test save_json_file with permission error."""
        mock_file.side_effect = PermissionError("Permission denied")

        with pytest.raises(FilePermissionError) as excinfo:
            save_json_file(self.test_json_file, self.test_data)

        assert "Cannot write to file" in str(excinfo.value)

    def test_json_to_string_basic(self):
        """Test basic functionality of json_to_string."""
        json_str = json_to_string(self.test_data)
        parsed = json.loads(json_str)
        assert parsed == self.test_data

    def test_json_to_string_with_indent(self):
        """Test json_to_string with indentation."""
        json_str = json_to_string(self.test_data, indent=2)
        assert "{\n  " in json_str  # Check for indentation
        parsed = json.loads(json_str)
        assert parsed == self.test_data

    def test_json_to_string_with_datetime(self):
        """Test json_to_string with datetime and date objects."""
        dt = datetime(2023, 1, 15, 12, 30, 45)
        d = date(2023, 1, 15)
        data_with_dates = {"datetime": dt, "date": d}

        json_str = json_to_string(data_with_dates)
        parsed = json.loads(json_str)

        assert parsed["datetime"] == "2023-01-15T12:30:45"
        assert parsed["date"] == "2023-01-15"

    def test_string_to_json_basic(self):
        """Test basic functionality of string_to_json."""
        json_str = '{"key": "value", "list": [1, 2, 3]}'
        data = string_to_json(json_str)

        assert data["key"] == "value"
        assert data["list"] == [1, 2, 3]

    def test_string_to_json_invalid(self):
        """Test string_to_json with invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            string_to_json('{"key": "value", invalid}')

    def test_merge_json_objects_basic(self):
        """Test basic functionality of merge_json_objects."""
        obj1 = {"a": 1, "b": 2}
        obj2 = {"b": 3, "c": 4}

        merged = merge_json_objects(obj1, obj2)

        assert merged == {"a": 1, "b": 3, "c": 4}
        # Verify original objects are not modified
        assert obj1 == {"a": 1, "b": 2}
        assert obj2 == {"b": 3, "c": 4}

    def test_merge_json_objects_nested(self):
        """Test merge_json_objects with nested objects."""
        obj1 = {"a": 1, "b": {"c": 2, "d": 3}}
        obj2 = {"b": {"c": 4, "e": 5}, "f": 6}

        merged = merge_json_objects(obj1, obj2)

        assert merged == {"a": 1, "b": {"c": 4, "d": 3, "e": 5}, "f": 6}
        # Verify original objects are not modified
        assert obj1 == {"a": 1, "b": {"c": 2, "d": 3}}
        assert obj2 == {"b": {"c": 4, "e": 5}, "f": 6}

    def test_merge_json_objects_empty(self):
        """Test merge_json_objects with empty objects."""
        obj1 = {"a": 1, "b": 2}

        # Empty second object
        merged = merge_json_objects(obj1, {})
        assert merged == obj1

        # Empty first object
        merged = merge_json_objects({}, obj1)
        assert merged == obj1

        # Both empty
        merged = merge_json_objects({}, {})
        assert merged == {}

    def test_merge_json_objects_deep_nesting(self):
        """Test merge_json_objects with deeply nested objects."""
        obj1 = {"a": {"b": {"c": {"d": 1}}}}
        obj2 = {"a": {"b": {"c": {"e": 2}}}}

        merged = merge_json_objects(obj1, obj2)

        assert merged == {"a": {"b": {"c": {"d": 1, "e": 2}}}}

    def test_flatten_json_basic(self):
        """Test basic functionality of flatten_json."""
        obj = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}

        flattened = flatten_json(obj)

        assert flattened == {"a": 1, "b.c": 2, "b.d.e": 3}

    def test_flatten_json_custom_delimiter(self):
        """Test flatten_json with custom delimiter."""
        obj = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}

        flattened = flatten_json(obj, delimiter="_")

        assert flattened == {"a": 1, "b_c": 2, "b_d_e": 3}

    def test_flatten_json_empty(self):
        """Test flatten_json with empty object."""
        flattened = flatten_json({})
        assert flattened == {}

    def test_unflatten_json_basic(self):
        """Test basic functionality of unflatten_json."""
        obj = {"a": 1, "b.c": 2, "b.d.e": 3}

        unflattened = unflatten_json(obj)

        assert unflattened == {"a": 1, "b": {"c": 2, "d": {"e": 3}}}

    def test_unflatten_json_custom_delimiter(self):
        """Test unflatten_json with custom delimiter."""
        obj = {"a": 1, "b_c": 2, "b_d_e": 3}

        unflattened = unflatten_json(obj, delimiter="_")

        assert unflattened == {"a": 1, "b": {"c": 2, "d": {"e": 3}}}

    def test_unflatten_json_empty(self):
        """Test unflatten_json with empty object."""
        unflattened = unflatten_json({})
        assert unflattened == {}

    def test_date_time_encoder_other_types(self):
        """Test DateTimeEncoder with non-date/datetime types."""
        encoder = DateTimeEncoder()
        # Test with a regular object that should use the default implementation
        with pytest.raises(TypeError):
            encoder.default(object())

    def test_load_json_file_with_path_object(self):
        """Test load_json_file with a Path object."""
        path_obj = Path(self.test_json_file)
        data = load_json_file(path_obj)
        assert data == self.test_data

    def test_save_json_file_with_path_object(self):
        """Test save_json_file with a Path object."""
        new_file = Path(self.temp_dir) / "path_obj_file.json"
        save_json_file(new_file, self.test_data)

        # Verify the file was created
        assert new_file.exists()

        # Load and verify the content
        with open(new_file, "r") as f:
            loaded_data = json.load(f)

        assert loaded_data == self.test_data

    def test_save_json_file_without_create_dirs(self):
        """Test save_json_file with create_dirs=False."""
        # Try to save to a non-existent directory with create_dirs=False
        non_existent_dir = os.path.join(self.temp_dir, "non_existent_dir")
        new_file = os.path.join(non_existent_dir, "test.json")

        # This should fail because the directory doesn't exist
        with pytest.raises(FileNotFoundError):
            save_json_file(new_file, self.test_data, create_dirs=False)

    def test_json_to_string_with_ensure_ascii(self):
        """Test json_to_string with ensure_ascii=True."""
        data = {"key": "值"}  # Chinese character

        # With ensure_ascii=False (default)
        json_str_default = json_to_string(data)
        assert "值" in json_str_default

        # With ensure_ascii=True
        json_str_ascii = json_to_string(data, ensure_ascii=True)
        assert "值" not in json_str_ascii
        assert "\\u" in json_str_ascii

    def test_string_to_json_with_complex_data(self):
        """Test string_to_json with complex nested data."""
        complex_json = '''
        {
            "string": "value",
            "number": 42,
            "boolean": true,
            "null": null,
            "array": [1, 2, 3],
            "nested": {
                "a": 1,
                "b": {
                    "c": 2
                }
            }
        }
        '''

        data = string_to_json(complex_json)

        assert data["string"] == "value"
        assert data["number"] == 42
        assert data["boolean"] is True
        assert data["null"] is None
        assert data["array"] == [1, 2, 3]
        assert data["nested"]["a"] == 1
        assert data["nested"]["b"]["c"] == 2

    def test_merge_json_objects_with_arrays(self):
        """Test merge_json_objects with arrays."""
        obj1 = {"array": [1, 2, 3]}
        obj2 = {"array": [4, 5, 6]}

        # Arrays should be replaced, not merged
        merged = merge_json_objects(obj1, obj2)
        assert merged["array"] == [4, 5, 6]

    def test_merge_json_objects_with_mixed_types(self):
        """Test merge_json_objects with mixed types at the same key."""
        obj1 = {"key": {"nested": "value"}}
        obj2 = {"key": "string_value"}

        # The second object's value should replace the first
        merged = merge_json_objects(obj1, obj2)
        assert merged["key"] == "string_value"

    def test_flatten_json_with_arrays(self):
        """Test flatten_json with arrays."""
        obj = {"a": [1, 2, 3], "b": {"c": [4, 5, 6]}}

        flattened = flatten_json(obj)

        assert flattened["a"] == [1, 2, 3]
        assert flattened["b.c"] == [4, 5, 6]

    def test_flatten_json_with_nested_arrays(self):
        """Test flatten_json with nested arrays."""
        obj = {"a": {"b": [{"c": 1}, {"d": 2}]}}

        flattened = flatten_json(obj)

        assert flattened["a.b"] == [{"c": 1}, {"d": 2}]

    def test_unflatten_json_with_numeric_keys(self):
        """Test unflatten_json with numeric keys."""
        obj = {"a.0": 1, "a.1": 2, "a.2": 3}

        # This should create a nested dict, not an array
        unflattened = unflatten_json(obj)

        assert unflattened == {"a": {"0": 1, "1": 2, "2": 3}}

    def test_unflatten_json_with_complex_paths(self):
        """Test unflatten_json with complex paths."""
        obj = {
            "a.b.c": 1,
            "a.b.d": 2,
            "a.e": 3,
            "f": 4
        }

        unflattened = unflatten_json(obj)

        assert unflattened == {
            "a": {
                "b": {
                    "c": 1,
                    "d": 2
                },
                "e": 3
            },
            "f": 4
        }
