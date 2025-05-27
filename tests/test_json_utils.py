"""Tests for the common_utils.json_utils module."""

import json
import os
import tempfile
from datetime import date, datetime

import pytest

from common_utils.exceptions import FilePermissionError, MissingFileError
from common_utils.json_utils import (
    DateTimeEncoder,
    flatten_json,
    json_to_string,
    load_json_file,
    merge_json_objects,
    save_json_file,
    string_to_json,
    unflatten_json,
)


class TestJsonUtils:
    """Test suite for JSON utility functions."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

        # Create a test JSON file
        self.test_json_file = os.path.join(self.temp_dir, "test.json")
        self.test_data = {"name": "Test", "values": [1, 2, 3], "nested": {"key": "value"}}
        with open(self.test_json_file, "w") as f:
            json.dump(self.test_data, f)

    def teardown_method(self):
        """Clean up after each test."""
        # Remove the temporary directory and all its contents
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.unlink(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_date_time_encoder(self):
        """Test the DateTimeEncoder class."""
        # Test with datetime
        dt = datetime(2023, 1, 15, 12, 30, 45)
        data = {"datetime": dt}
        json_str = json.dumps(data, cls=DateTimeEncoder)
        assert json_str == '{"datetime": "2023-01-15T12:30:45"}'

        # Test with date
        d = date(2023, 1, 15)
        data = {"date": d}
        json_str = json.dumps(data, cls=DateTimeEncoder)
        assert json_str == '{"date": "2023-01-15"}'

        # Test with mixed data
        data = {"datetime": dt, "date": d, "string": "test", "number": 42}
        json_str = json.dumps(data, cls=DateTimeEncoder)
        parsed = json.loads(json_str)
        assert parsed["datetime"] == "2023-01-15T12:30:45"
        assert parsed["date"] == "2023-01-15"
        assert parsed["string"] == "test"
        assert parsed["number"] == 42

    def test_load_json_file(self):
        """Test the load_json_file function."""
        # Test loading an existing JSON file
        data = load_json_file(self.test_json_file)
        assert data == self.test_data

        # Test with non-existent file
        with pytest.raises(MissingFileError):
            load_json_file(os.path.join(self.temp_dir, "non_existent.json"))

        # Test with invalid JSON
        invalid_json_file = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_json_file, "w") as f:
            f.write("This is not valid JSON")

        with pytest.raises(json.JSONDecodeError):
            load_json_file(invalid_json_file)

    def test_save_json_file(self):
        """Test the save_json_file function."""
        # Test saving to a new file
        new_file = os.path.join(self.temp_dir, "new.json")
        data = {"key": "value", "list": [1, 2, 3]}
        save_json_file(new_file, data)

        # Verify the file was created and contains the correct data
        assert os.path.exists(new_file)
        with open(new_file) as f:
            loaded_data = json.load(f)
        assert loaded_data == data

        # Test overwriting an existing file
        updated_data = {"key": "updated", "list": [4, 5, 6]}
        save_json_file(new_file, updated_data)

        # Verify the file was updated
        with open(new_file) as f:
            loaded_data = json.load(f)
        assert loaded_data == updated_data

        # Test creating directories if they don't exist
        nested_file = os.path.join(self.temp_dir, "nested", "dir", "file.json")
        save_json_file(nested_file, data)

        # Verify the file was created
        assert os.path.exists(nested_file)
        with open(nested_file) as f:
            loaded_data = json.load(f)
        assert loaded_data == data

        # Test with datetime and date objects
        dt = datetime(2023, 1, 15, 12, 30, 45)
        d = date(2023, 1, 15)
        data_with_dates = {"datetime": dt, "date": d}
        date_file = os.path.join(self.temp_dir, "dates.json")
        save_json_file(date_file, data_with_dates)

        # Verify the file was created and contains ISO format strings
        with open(date_file) as f:
            loaded_data = json.load(f)
        assert loaded_data["datetime"] == "2023-01-15T12:30:45"
        assert loaded_data["date"] == "2023-01-15"

    def test_json_to_string(self):
        """Test the json_to_string function."""
        # Test with simple data
        data = {"key": "value", "list": [1, 2, 3]}
        json_str = json_to_string(data)
        assert json_str == '{"key": "value", "list": [1, 2, 3]}'

        # Test with indentation
        json_str = json_to_string(data, indent=2)
        assert "{\n  " in json_str
        assert json.loads(json_str) == data

        # Test with datetime and date objects
        dt = datetime(2023, 1, 15, 12, 30, 45)
        d = date(2023, 1, 15)
        data_with_dates = {"datetime": dt, "date": d}
        json_str = json_to_string(data_with_dates)
        parsed = json.loads(json_str)
        assert parsed["datetime"] == "2023-01-15T12:30:45"
        assert parsed["date"] == "2023-01-15"

    def test_string_to_json(self):
        """Test the string_to_json function."""
        # Test with valid JSON string
        json_str = '{"key": "value", "list": [1, 2, 3]}'
        data = string_to_json(json_str)
        assert data == {"key": "value", "list": [1, 2, 3]}

        # Test with invalid JSON string
        with pytest.raises(json.JSONDecodeError):
            string_to_json("This is not valid JSON")

    def test_merge_json_objects(self):
        """Test the merge_json_objects function."""
        # Test merging two simple objects
        obj1 = {"a": 1, "b": 2}
        obj2 = {"b": 3, "c": 4}
        merged = merge_json_objects(obj1, obj2)
        assert merged == {"a": 1, "b": 3, "c": 4}

        # Test merging with nested objects
        obj1 = {"a": 1, "b": {"c": 2, "d": 3}}
        obj2 = {"b": {"c": 4, "e": 5}, "f": 6}
        merged = merge_json_objects(obj1, obj2)
        assert merged == {"a": 1, "b": {"c": 4, "d": 3, "e": 5}, "f": 6}

        # Test that original objects are not modified
        assert obj1 == {"a": 1, "b": {"c": 2, "d": 3}}
        assert obj2 == {"b": {"c": 4, "e": 5}, "f": 6}

        # Test with empty objects
        assert merge_json_objects({}, {}) == {}
        assert merge_json_objects(obj1, {}) == obj1
        assert merge_json_objects({}, obj2) == obj2

    def test_flatten_json(self):
        """Test the flatten_json function."""
        # Test with simple nested object
        obj = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        flattened = flatten_json(obj)
        assert flattened == {"a": 1, "b.c": 2, "b.d.e": 3}

        # Test with custom delimiter
        flattened = flatten_json(obj, delimiter="_")
        assert flattened == {"a": 1, "b_c": 2, "b_d_e": 3}

        # Test with arrays (arrays are not flattened)
        obj = {"a": 1, "b": [1, 2, 3], "c": {"d": [4, 5, 6]}}
        flattened = flatten_json(obj)
        assert flattened == {"a": 1, "b": [1, 2, 3], "c.d": [4, 5, 6]}

        # Test with empty object
        assert flatten_json({}) == {}

    def test_unflatten_json(self):
        """Test the unflatten_json function."""
        # Test with simple flattened object
        obj = {"a": 1, "b.c": 2, "b.d.e": 3}
        unflattened = unflatten_json(obj)
        assert unflattened == {"a": 1, "b": {"c": 2, "d": {"e": 3}}}

        # Test with custom delimiter
        obj = {"a": 1, "b_c": 2, "b_d_e": 3}
        unflattened = unflatten_json(obj, delimiter="_")
        assert unflattened == {"a": 1, "b": {"c": 2, "d": {"e": 3}}}

        # Test with empty object
        assert unflatten_json({}) == {}

        # Test that flattening and then unflattening returns the original object
        original = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        flattened = flatten_json(original)
        unflattened = unflatten_json(flattened)
        assert unflattened == original
