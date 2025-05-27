"""JSON utility functions for the pAIssive_income project.

This module provides common JSON processing functions used across the project.
"""

# Standard library imports
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Third-party imports

# Local imports
from common_utils.exceptions import MissingFileError, FilePermissionError


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime and date objects."""

    def default(self, obj: Any) -> Any:
        """
        Convert datetime and date objects to ISO format strings.

        Args:
            obj: The object to convert

        Returns:
            The converted object
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


def load_json_file(file_path: Union[str, Path], encoding: str = "utf-8") -> Any:
    """
    Load JSON data from a file.

    Args:
        file_path: The path to the JSON file
        encoding: The encoding to use (default: "utf-8")

    Returns:
        The parsed JSON data

    Raises:
        MissingFileError: If the file does not exist
        FilePermissionError: If the file cannot be read due to permissions
        json.JSONDecodeError: If the file contains invalid JSON

    Examples:
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        ...     f.write('{"key": "value"}')
        ...     temp_file = f.name
        16
        >>> data = load_json_file(temp_file)
        >>> data
        {'key': 'value'}
        >>> os.unlink(temp_file)  # Clean up
    """
    path = Path(file_path)
    if not path.exists():
        raise MissingFileError(f"File {file_path} does not exist")

    try:
        with open(path, "r", encoding=encoding) as f:
            return json.load(f)
    except PermissionError as e:
        raise FilePermissionError(f"Cannot read file {file_path}: {e}") from e


def save_json_file(
    file_path: Union[str, Path],
    data: Any,
    encoding: str = "utf-8",
    indent: int = 2,
    ensure_ascii: bool = False,
    create_dirs: bool = True,
) -> None:
    """
    Save data to a JSON file.

    Args:
        file_path: The path to the JSON file
        data: The data to save
        encoding: The encoding to use (default: "utf-8")
        indent: The indentation level (default: 2)
        ensure_ascii: Whether to escape non-ASCII characters (default: False)
        create_dirs: Whether to create parent directories if they don't exist (default: True)

    Raises:
        FilePermissionError: If the file cannot be written due to permissions
        TypeError: If the data cannot be serialized to JSON

    Examples:
        >>> import tempfile
        >>> temp_dir = tempfile.gettempdir()
        >>> test_file = os.path.join(temp_dir, "test_save.json")
        >>> data = {"key": "value", "list": [1, 2, 3]}
        >>> save_json_file(test_file, data)
        >>> with open(test_file, "r") as f:
        ...     content = f.read()
        >>> "key" in content and "value" in content
        True
        >>> os.unlink(test_file)  # Clean up
    """
    path = Path(file_path)

    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "w", encoding=encoding) as f:
            json.dump(data, f, cls=DateTimeEncoder, indent=indent, ensure_ascii=ensure_ascii)
    except PermissionError as e:
        raise FilePermissionError(f"Cannot write to file {file_path}: {e}") from e


def json_to_string(
    data: Any,
    indent: Optional[int] = None,
    ensure_ascii: bool = False,
) -> str:
    """
    Convert data to a JSON string.

    Args:
        data: The data to convert
        indent: The indentation level (default: None)
        ensure_ascii: Whether to escape non-ASCII characters (default: False)

    Returns:
        The JSON string

    Raises:
        TypeError: If the data cannot be serialized to JSON

    Examples:
        >>> data = {"key": "value", "list": [1, 2, 3]}
        >>> json_str = json_to_string(data, indent=2)
        >>> "key" in json_str and "value" in json_str
        True
    """
    return json.dumps(data, cls=DateTimeEncoder, indent=indent, ensure_ascii=ensure_ascii)


def string_to_json(json_str: str) -> Any:
    """
    Parse a JSON string into a Python object.

    Args:
        json_str: The JSON string to parse

    Returns:
        The parsed JSON data

    Raises:
        json.JSONDecodeError: If the string contains invalid JSON

    Examples:
        >>> json_str = '{"key": "value", "list": [1, 2, 3]}'
        >>> data = string_to_json(json_str)
        >>> data["key"]
        'value'
        >>> data["list"]
        [1, 2, 3]
    """
    return json.loads(json_str)


def merge_json_objects(obj1: Dict[str, Any], obj2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two JSON objects (dictionaries) recursively.

    Args:
        obj1: The first JSON object
        obj2: The second JSON object (takes precedence for duplicate keys)

    Returns:
        The merged JSON object

    Examples:
        >>> obj1 = {"a": 1, "b": {"c": 2, "d": 3}}
        >>> obj2 = {"b": {"c": 4, "e": 5}, "f": 6}
        >>> merged = merge_json_objects(obj1, obj2)
        >>> merged
        {'a': 1, 'b': {'c': 4, 'd': 3, 'e': 5}, 'f': 6}
    """
    result = obj1.copy()

    for key, value in obj2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_json_objects(result[key], value)
        else:
            result[key] = value

    return result


def flatten_json(obj: Dict[str, Any], delimiter: str = ".") -> Dict[str, Any]:
    """
    Flatten a nested JSON object into a single-level dictionary.

    Args:
        obj: The JSON object to flatten
        delimiter: The delimiter to use for nested keys (default: ".")

    Returns:
        The flattened JSON object

    Examples:
        >>> obj = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        >>> flattened = flatten_json(obj)
        >>> flattened
        {'a': 1, 'b.c': 2, 'b.d.e': 3}
    """
    result: Dict[str, Any] = {}

    def _flatten(x: Dict[str, Any], name: str = "") -> None:
        for key, value in x.items():
            new_key = f"{name}{delimiter}{key}" if name else key

            if isinstance(value, dict):
                _flatten(value, new_key)
            else:
                result[new_key] = value

    _flatten(obj)
    return result


def unflatten_json(obj: Dict[str, Any], delimiter: str = ".") -> Dict[str, Any]:
    """
    Unflatten a single-level dictionary into a nested JSON object.

    Args:
        obj: The flattened JSON object
        delimiter: The delimiter used for nested keys (default: ".")

    Returns:
        The nested JSON object

    Examples:
        >>> obj = {"a": 1, "b.c": 2, "b.d.e": 3}
        >>> unflattened = unflatten_json(obj)
        >>> unflattened
        {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
    """
    result: Dict[str, Any] = {}

    for key, value in obj.items():
        parts = key.split(delimiter)
        current = result

        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                current[part] = value
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]

    return result
