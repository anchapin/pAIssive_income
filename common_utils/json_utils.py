"""
"""
JSON utilities for the pAIssive Income project.
JSON utilities for the pAIssive Income project.


This module provides common JSON serialization functions used across the project.
This module provides common JSON serialization functions used across the project.
"""
"""


import json
import json
import logging
import logging
from datetime import datetime
from datetime import datetime
from typing import Any
from typing import Any


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




def to_json(obj: Any, indent: int = 2) -> str:
    def to_json(obj: Any, indent: int = 2) -> str:
    """
    """
    Convert an object to a JSON string.
    Convert an object to a JSON string.


    Args:
    Args:
    obj: Object to convert
    obj: Object to convert
    indent: Number of spaces for indentation (default: 2)
    indent: Number of spaces for indentation (default: 2)


    Returns:
    Returns:
    JSON string representation of the object
    JSON string representation of the object


    Raises:
    Raises:
    TypeError: If the object is not JSON serializable
    TypeError: If the object is not JSON serializable
    """
    """
    try:
    try:
    return json.dumps(obj, indent=indent)
    return json.dumps(obj, indent=indent)
except (TypeError, ValueError) as e:
except (TypeError, ValueError) as e:
    logger.error(f"Error converting object to JSON: {e}")
    logger.error(f"Error converting object to JSON: {e}")
    raise
    raise




    def from_json(json_str: str) -> Any:
    def from_json(json_str: str) -> Any:
    """
    """
    Convert a JSON string to an object.
    Convert a JSON string to an object.


    Args:
    Args:
    json_str: JSON string to convert
    json_str: JSON string to convert


    Returns:
    Returns:
    Object representation of the JSON string
    Object representation of the JSON string


    Raises:
    Raises:
    json.JSONDecodeError: If the string is not valid JSON
    json.JSONDecodeError: If the string is not valid JSON
    """
    """
    try:
    try:
    return json.loads(json_str)
    return json.loads(json_str)
except json.JSONDecodeError as e:
except json.JSONDecodeError as e:
    logger.error(f"Error parsing JSON string: {e}")
    logger.error(f"Error parsing JSON string: {e}")
    raise
    raise




    def save_to_json_file(obj: Any, file_path: str, indent: int = 2) -> None:
    def save_to_json_file(obj: Any, file_path: str, indent: int = 2) -> None:
    """
    """
    Save an object to a JSON file.
    Save an object to a JSON file.


    Args:
    Args:
    obj: Object to save
    obj: Object to save
    file_path: Path to save the file
    file_path: Path to save the file
    indent: Number of spaces for indentation (default: 2)
    indent: Number of spaces for indentation (default: 2)


    Raises:
    Raises:
    TypeError: If the object is not JSON serializable
    TypeError: If the object is not JSON serializable
    IOError: If there's an issue writing to the file
    IOError: If there's an issue writing to the file
    """
    """
    try:
    try:
    with open(file_path, "w", encoding="utf-8") as f:
    with open(file_path, "w", encoding="utf-8") as f:
    json.dump(obj, f, indent=indent)
    json.dump(obj, f, indent=indent)
    logger.debug(f"Successfully saved object to {file_path}")
    logger.debug(f"Successfully saved object to {file_path}")
except (TypeError, ValueError) as e:
except (TypeError, ValueError) as e:
    logger.error(f"Error serializing object to JSON for file {file_path}: {e}")
    logger.error(f"Error serializing object to JSON for file {file_path}: {e}")
    raise
    raise
except (IOError, OSError) as e:
except (IOError, OSError) as e:
    logger.error(f"Error writing to file {file_path}: {e}")
    logger.error(f"Error writing to file {file_path}: {e}")
    raise
    raise




    def load_from_json_file(file_path: str) -> Any:
    def load_from_json_file(file_path: str) -> Any:
    """
    """
    Load an object from a JSON file.
    Load an object from a JSON file.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file


    Returns:
    Returns:
    Object loaded from the file
    Object loaded from the file


    Raises:
    Raises:
    FileNotFoundError: If the file doesn't exist
    FileNotFoundError: If the file doesn't exist
    json.JSONDecodeError: If the file doesn't contain valid JSON
    json.JSONDecodeError: If the file doesn't contain valid JSON
    IOError: If there's an issue reading the file
    IOError: If there's an issue reading the file
    """
    """
    try:
    try:
    with open(file_path, "r", encoding="utf-8") as f:
    with open(file_path, "r", encoding="utf-8") as f:
    obj = json.load(f)
    obj = json.load(f)
    logger.debug(f"Successfully loaded object from {file_path}")
    logger.debug(f"Successfully loaded object from {file_path}")
    return obj
    return obj
except FileNotFoundError:
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    logger.error(f"File not found: {file_path}")
    raise
    raise
except json.JSONDecodeError as e:
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON format in file {file_path}: {e}")
    logger.error(f"Invalid JSON format in file {file_path}: {e}")
    raise
    raise
except (IOError, OSError) as e:
except (IOError, OSError) as e:
    logger.error(f"Error reading file {file_path}: {e}")
    logger.error(f"Error reading file {file_path}: {e}")
    raise
    raise




    class JSONEncoder(json.JSONEncoder):
    class JSONEncoder(json.JSONEncoder):
    """
    """
    Custom JSON encoder that handles additional types.
    Custom JSON encoder that handles additional types.
    """
    """


    def default(self, obj: Any) -> Any:
    def default(self, obj: Any) -> Any:
    """
    """
    Convert objects to JSON serializable types.
    Convert objects to JSON serializable types.


    Args:
    Args:
    obj: Object to convert
    obj: Object to convert


    Returns:
    Returns:
    JSON serializable representation of the object
    JSON serializable representation of the object
    """
    """
    # Handle datetime objects
    # Handle datetime objects
    if hasattr(obj, "isoformat"):
    if hasattr(obj, "isoformat"):
    return obj.isoformat()
    return obj.isoformat()
    # Handle objects with to_dict method
    # Handle objects with to_dict method
    elif hasattr(obj, "to_dict"):
    elif hasattr(obj, "to_dict"):
    return obj.to_dict()
    return obj.to_dict()
    # Handle objects with __dict__ attribute
    # Handle objects with __dict__ attribute
    elif hasattr(obj, "__dict__"):
    elif hasattr(obj, "__dict__"):
    return obj.__dict__
    return obj.__dict__
    # Let the base class handle it (or raise TypeError)
    # Let the base class handle it (or raise TypeError)
    return super().default(obj)
    return super().default(obj)




    def json_serialize(obj: Any, indent: int = 2) -> str:
    def json_serialize(obj: Any, indent: int = 2) -> str:
    """
    """
    Serialize an object to a JSON string using the custom encoder.
    Serialize an object to a JSON string using the custom encoder.


    Args:
    Args:
    obj: Object to serialize
    obj: Object to serialize
    indent: Number of spaces for indentation (default: 2)
    indent: Number of spaces for indentation (default: 2)


    Returns:
    Returns:
    JSON string representation of the object
    JSON string representation of the object


    Raises:
    Raises:
    TypeError: If the object is not JSON serializable
    TypeError: If the object is not JSON serializable
    """
    """
    try:
    try:
    return json.dumps(obj, indent=indent, cls=JSONEncoder)
    return json.dumps(obj, indent=indent, cls=JSONEncoder)
except (TypeError, ValueError) as e:
except (TypeError, ValueError) as e:
    logger.error(f"Error serializing object to JSON: {e}")
    logger.error(f"Error serializing object to JSON: {e}")
    raise
    raise




    def json_deserialize(json_str: str) -> Any:
    def json_deserialize(json_str: str) -> Any:
    """
    """
    Deserialize a JSON string to an object.
    Deserialize a JSON string to an object.


    This is an alias for from_json for consistency.
    This is an alias for from_json for consistency.


    Args:
    Args:
    json_str: JSON string to deserialize
    json_str: JSON string to deserialize


    Returns:
    Returns:
    Object representation of the JSON string
    Object representation of the JSON string


    Raises:
    Raises:
    json.JSONDecodeError: If the string is not valid JSON
    json.JSONDecodeError: If the string is not valid JSON
    """
    """
    return from_json(json_str)
    return from_json(json_str)