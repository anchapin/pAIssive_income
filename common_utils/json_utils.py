"""
JSON utilities for the pAIssive Income project.

This module provides common JSON serialization functions used across the project.
"""

import json
import logging
from typing import Any

# Set up logging
logger = logging.getLogger(__name__)


def to_json(obj: Any, indent: int = 2) -> str:
    """
    Convert an object to a JSON string.

    Args:
        obj: Object to convert
        indent: Number of spaces for indentation (default: 2)

    Returns:
        JSON string representation of the object

    Raises:
        TypeError: If the object is not JSON serializable
    """
    try:
        return json.dumps(obj, indent=indent)
    except (TypeError, ValueError) as e:
        logger.error(f"Error converting object to JSON: {e}")
        raise


def from_json(json_str: str) -> Any:
    """
    Convert a JSON string to an object.

    Args:
        json_str: JSON string to convert

    Returns:
        Object representation of the JSON string

    Raises:
        json.JSONDecodeError: If the string is not valid JSON
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON string: {e}")
        raise


def save_to_json_file(obj: Any, file_path: str, indent: int = 2) -> None:
    """
    Save an object to a JSON file.

    Args:
        obj: Object to save
        file_path: Path to save the file
        indent: Number of spaces for indentation (default: 2)

    Raises:
        TypeError: If the object is not JSON serializable
        IOError: If there's an issue writing to the file
    """
    try:
        with open(file_path, "w", encoding="utf - 8") as f:
            json.dump(obj, f, indent=indent)
        logger.debug(f"Successfully saved object to {file_path}")
    except (TypeError, ValueError) as e:
        logger.error(f"Error serializing object to JSON for file {file_path}: {e}")
        raise
    except (IOError, OSError) as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        raise


def load_from_json_file(file_path: str) -> Any:
    """
    Load an object from a JSON file.

    Args:
        file_path: Path to the file

    Returns:
        Object loaded from the file

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file doesn't contain valid JSON
        IOError: If there's an issue reading the file
    """
    try:
        with open(file_path, "r", encoding="utf - 8") as f:
            obj = json.load(f)
        logger.debug(f"Successfully loaded object from {file_path}")
        return obj
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in file {file_path}: {e}")
        raise
    except (IOError, OSError) as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


class JSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles additional types.
    """

    def default(self, obj: Any) -> Any:
        """
        Convert objects to JSON serializable types.

        Args:
            obj: Object to convert

        Returns:
            JSON serializable representation of the object
        """
        # Handle datetime objects
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        # Handle objects with to_dict method
        elif hasattr(obj, "to_dict"):
            return obj.to_dict()
        # Handle objects with __dict__ attribute
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        # Let the base class handle it (or raise TypeError)
        return super().default(obj)


def json_serialize(obj: Any, indent: int = 2) -> str:
    """
    Serialize an object to a JSON string using the custom encoder.

    Args:
        obj: Object to serialize
        indent: Number of spaces for indentation (default: 2)

    Returns:
        JSON string representation of the object

    Raises:
        TypeError: If the object is not JSON serializable
    """
    try:
        return json.dumps(obj, indent=indent, cls=JSONEncoder)
    except (TypeError, ValueError) as e:
        logger.error(f"Error serializing object to JSON: {e}")
        raise


def json_deserialize(json_str: str) -> Any:
    """
    Deserialize a JSON string to an object.

    This is an alias for from_json for consistency.

    Args:
        json_str: JSON string to deserialize

    Returns:
        Object representation of the JSON string

    Raises:
        json.JSONDecodeError: If the string is not valid JSON
    """
    return from_json(json_str)
