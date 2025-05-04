"""
"""
Cache key generation for the model cache system.
Cache key generation for the model cache system.


This module provides utilities for generating and managing cache keys.
This module provides utilities for generating and managing cache keys.
"""
"""




import hashlib
import hashlib
import json
import json
from dataclasses import dataclass
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from typing import Any, Dict, List, Optional, Union




@dataclass
@dataclass
class CacheKey:
    class CacheKey:
    """
    """
    Cache key for model responses.
    Cache key for model responses.
    """
    """


    model_id: str
    model_id: str
    operation: str
    operation: str
    input_hash: str
    input_hash: str
    parameters_hash: str
    parameters_hash: str


    def __str__(self) -> str:
    def __str__(self) -> str:
    """
    """
    Convert the cache key to a string.
    Convert the cache key to a string.


    Returns:
    Returns:
    String representation of the cache key
    String representation of the cache key
    """
    """
    return (
    return (
    f"{self.model_id}:{self.operation}:{self.input_hash}:{self.parameters_hash}"
    f"{self.model_id}:{self.operation}:{self.input_hash}:{self.parameters_hash}"
    )
    )




    def generate_cache_key(
    def generate_cache_key(
    model_id: str,
    model_id: str,
    operation: str,
    operation: str,
    inputs: Union[str, List[str], Dict[str, Any]],
    inputs: Union[str, List[str], Dict[str, Any]],
    parameters: Optional[Dict[str, Any]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    ) -> CacheKey:
    ) -> CacheKey:
    """
    """
    Generate a cache key for model responses.
    Generate a cache key for model responses.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    operation: Operation type (e.g., "generate", "embed", "classify")
    operation: Operation type (e.g., "generate", "embed", "classify")
    inputs: Input data for the model
    inputs: Input data for the model
    parameters: Optional parameters for the operation
    parameters: Optional parameters for the operation


    Returns:
    Returns:
    Cache key object
    Cache key object
    """
    """
    # Generate hash for inputs
    # Generate hash for inputs
    if isinstance(inputs, str):
    if isinstance(inputs, str):
    input_hash = _hash_string(inputs)
    input_hash = _hash_string(inputs)
    elif isinstance(inputs, list):
    elif isinstance(inputs, list):
    input_hash = _hash_list(inputs)
    input_hash = _hash_list(inputs)
    elif isinstance(inputs, dict):
    elif isinstance(inputs, dict):
    input_hash = _hash_dict(inputs)
    input_hash = _hash_dict(inputs)
    else:
    else:
    input_hash = _hash_string(str(inputs))
    input_hash = _hash_string(str(inputs))


    # Generate hash for parameters
    # Generate hash for parameters
    if parameters:
    if parameters:
    parameters_hash = _hash_dict(parameters)
    parameters_hash = _hash_dict(parameters)
    else:
    else:
    parameters_hash = _hash_dict({})
    parameters_hash = _hash_dict({})


    return CacheKey(
    return CacheKey(
    model_id=model_id,
    model_id=model_id,
    operation=operation,
    operation=operation,
    input_hash=input_hash,
    input_hash=input_hash,
    parameters_hash=parameters_hash,
    parameters_hash=parameters_hash,
    )
    )




    def _hash_string(s: str) -> str:
    def _hash_string(s: str) -> str:
    """
    """
    Generate a hash for a string.
    Generate a hash for a string.


    Args:
    Args:
    s: String to hash
    s: String to hash


    Returns:
    Returns:
    Hash of the string
    Hash of the string
    """
    """
    return hashlib.md5(s.encode("utf-8")).hexdigest()
    return hashlib.md5(s.encode("utf-8")).hexdigest()




    def _hash_list(lst: List[Any]) -> str:
    def _hash_list(lst: List[Any]) -> str:
    """
    """
    Generate a hash for a list.
    Generate a hash for a list.


    Args:
    Args:
    lst: List to hash
    lst: List to hash


    Returns:
    Returns:
    Hash of the list
    Hash of the list
    """
    """
    return hashlib.md5(json.dumps(lst, sort_keys=True).encode("utf-8")).hexdigest()
    return hashlib.md5(json.dumps(lst, sort_keys=True).encode("utf-8")).hexdigest()




    def _hash_dict(d: Dict[str, Any]) -> str:
    def _hash_dict(d: Dict[str, Any]) -> str:
    """
    """
    Generate a hash for a dictionary.
    Generate a hash for a dictionary.


    Args:
    Args:
    d: Dictionary to hash
    d: Dictionary to hash


    Returns:
    Returns:
    Hash of the dictionary
    Hash of the dictionary
    """
    """
    return hashlib.md5(json.dumps(d, sort_keys=True).encode("utf-8")).hexdigest()
    return hashlib.md5(json.dumps(d, sort_keys=True).encode("utf-8")).hexdigest()




    def parse_cache_key(key_str: str) -> CacheKey:
    def parse_cache_key(key_str: str) -> CacheKey:
    """
    """
    Parse a cache key from a string.
    Parse a cache key from a string.


    Args:
    Args:
    key_str: String representation of the cache key
    key_str: String representation of the cache key


    Returns:
    Returns:
    Cache key object
    Cache key object


    Raises:
    Raises:
    ValueError: If the key string is invalid
    ValueError: If the key string is invalid
    """
    """
    parts = key_str.split(":")
    parts = key_str.split(":")
    if len(parts) != 4:
    if len(parts) != 4:
    raise ValueError(f"Invalid cache key format: {key_str}")
    raise ValueError(f"Invalid cache key format: {key_str}")


    return CacheKey(
    return CacheKey(
    model_id=parts[0],
    model_id=parts[0],
    operation=parts[1],
    operation=parts[1],
    input_hash=parts[2],
    input_hash=parts[2],
    parameters_hash=parts[3],
    parameters_hash=parts[3],
    )
    )