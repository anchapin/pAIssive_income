"""
Cache key generation for the model cache system.

This module provides utilities for generating and managing cache keys.
"""


import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union




@dataclass
class CacheKey:
    """
    Cache key for model responses.
    """

    model_id: str
    operation: str
    input_hash: str
    parameters_hash: str

    def __str__(self) -> str:
        """
        Convert the cache key to a string.

        Returns:
            String representation of the cache key
        """
        return (
            f"{self.model_id}:{self.operation}:{self.input_hash}:{self.parameters_hash}"
        )


def generate_cache_key(
    model_id: str,
    operation: str,
    inputs: Union[str, List[str], Dict[str, Any]],
    parameters: Optional[Dict[str, Any]] = None,
) -> CacheKey:
    """
    Generate a cache key for model responses.

    Args:
        model_id: ID of the model
        operation: Operation type (e.g., "generate", "embed", "classify")
        inputs: Input data for the model
        parameters: Optional parameters for the operation

    Returns:
        Cache key object
    """
    # Generate hash for inputs
    if isinstance(inputs, str):
        input_hash = _hash_string(inputs)
    elif isinstance(inputs, list):
        input_hash = _hash_list(inputs)
    elif isinstance(inputs, dict):
        input_hash = _hash_dict(inputs)
    else:
        input_hash = _hash_string(str(inputs))

    # Generate hash for parameters
    if parameters:
        parameters_hash = _hash_dict(parameters)
    else:
        parameters_hash = _hash_dict({})

    return CacheKey(
        model_id=model_id,
        operation=operation,
        input_hash=input_hash,
        parameters_hash=parameters_hash,
    )


def _hash_string(s: str) -> str:
    """
    Generate a hash for a string.

    Args:
        s: String to hash

    Returns:
        Hash of the string
    """
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _hash_list(lst: List[Any]) -> str:
    """
    Generate a hash for a list.

    Args:
        lst: List to hash

    Returns:
        Hash of the list
    """
    return hashlib.md5(json.dumps(lst, sort_keys=True).encode("utf-8")).hexdigest()


def _hash_dict(d: Dict[str, Any]) -> str:
    """
    Generate a hash for a dictionary.

    Args:
        d: Dictionary to hash

    Returns:
        Hash of the dictionary
    """
    return hashlib.md5(json.dumps(d, sort_keys=True).encode("utf-8")).hexdigest()


def parse_cache_key(key_str: str) -> CacheKey:
    """
    Parse a cache key from a string.

    Args:
        key_str: String representation of the cache key

    Returns:
        Cache key object

    Raises:
        ValueError: If the key string is invalid
    """
    parts = key_str.split(":")
    if len(parts) != 4:
        raise ValueError(f"Invalid cache key format: {key_str}")

    return CacheKey(
        model_id=parts[0],
        operation=parts[1],
        input_hash=parts[2],
        parameters_hash=parts[3],
    )