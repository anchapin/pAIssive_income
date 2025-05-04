"""
"""
Cache manager for the model cache system.
Cache manager for the model cache system.


This module provides the main cache manager for the model cache system.
This module provides the main cache manager for the model cache system.
"""
"""




import logging
import logging
import re
import re
from typing import Any, Dict, List, Optional, Union
from typing import Any, Dict, List, Optional, Union


from .cache_backends import (CacheBackend, DiskCache, MemoryCache, RedisCache,
from .cache_backends import (CacheBackend, DiskCache, MemoryCache, RedisCache,
SQLiteCache)
SQLiteCache)
from .cache_config import CacheConfig
from .cache_config import CacheConfig
from .cache_key import generate_cache_key
from .cache_key import generate_cache_key


REDIS_AVAILABLE
REDIS_AVAILABLE


# Try to import Redis cache if available
# Try to import Redis cache if available
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    REDIS_AVAILABLE = False
    REDIS_AVAILABLE = False


    # Set up logging
    # Set up logging
    logging.basicConfig(
    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    )
    logger = logging.getLogger(__name__)
    logger = logging.getLogger(__name__)




    class CacheManager:
    class CacheManager:
    """
    """
    Manager for the model cache system.
    Manager for the model cache system.
    """
    """


    def __init__(self, config: Optional[CacheConfig] = None):
    def __init__(self, config: Optional[CacheConfig] = None):
    """
    """
    Initialize the cache manager.
    Initialize the cache manager.


    Args:
    Args:
    config: Cache configuration
    config: Cache configuration
    """
    """
    self.config = config or CacheConfig()
    self.config = config or CacheConfig()
    self.backend = self._create_backend()
    self.backend = self._create_backend()


    def _make_key(
    def _make_key(
    self,
    self,
    model_id: str,
    model_id: str,
    operation: str,
    operation: str,
    inputs: Union[str, List[str], Dict[str, Any]],
    inputs: Union[str, List[str], Dict[str, Any]],
    parameters: Optional[Dict[str, Any]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
    ) -> str:
    """
    """
    Create a consistent cache key string that preserves namespace structure.
    Create a consistent cache key string that preserves namespace structure.
    """
    """
    # Generate cache key object
    # Generate cache key object
    key = generate_cache_key(model_id, operation, inputs, parameters)
    key = generate_cache_key(model_id, operation, inputs, parameters)


    # Create a composite key with strict component separation for uniqueness
    # Create a composite key with strict component separation for uniqueness
    return f"model:{key.model_id}|op:{key.operation}|in:{key.input_hash}|params:{key.parameters_hash}"
    return f"model:{key.model_id}|op:{key.operation}|in:{key.input_hash}|params:{key.parameters_hash}"


    def get(
    def get(
    self,
    self,
    model_id: str,
    model_id: str,
    operation: str,
    operation: str,
    inputs: Union[str, List[str], Dict[str, Any]],
    inputs: Union[str, List[str], Dict[str, Any]],
    parameters: Optional[Dict[str, Any]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
    ) -> Optional[Dict[str, Any]]:
    """
    """
    Get a value from the cache.
    Get a value from the cache.


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
    Cached value or None if not found
    Cached value or None if not found
    """
    """
    if not self.config.should_cache(model_id, operation):
    if not self.config.should_cache(model_id, operation):
    return None
    return None


    # Generate structured cache key
    # Generate structured cache key
    key = self._make_key(model_id, operation, inputs, parameters)
    key = self._make_key(model_id, operation, inputs, parameters)


    # Get value from cache
    # Get value from cache
    return self.backend.get(key)
    return self.backend.get(key)


    def set(
    def set(
    self,
    self,
    model_id: str,
    model_id: str,
    operation: str,
    operation: str,
    inputs: Union[str, List[str], Dict[str, Any]],
    inputs: Union[str, List[str], Dict[str, Any]],
    value: Dict[str, Any],
    value: Dict[str, Any],
    parameters: Optional[Dict[str, Any]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    ttl: Optional[int] = None,
    ttl: Optional[int] = None,
    ) -> bool:
    ) -> bool:
    """
    """
    Set a value in the cache.
    Set a value in the cache.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    operation: Operation type (e.g., "generate", "embed", "classify")
    operation: Operation type (e.g., "generate", "embed", "classify")
    inputs: Input data for the model
    inputs: Input data for the model
    value: Value to cache
    value: Value to cache
    parameters: Optional parameters for the operation
    parameters: Optional parameters for the operation
    ttl: Time to live in seconds (None for default TTL)
    ttl: Time to live in seconds (None for default TTL)


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    if not self.config.should_cache(model_id, operation):
    if not self.config.should_cache(model_id, operation):
    return False
    return False


    # Generate structured cache key
    # Generate structured cache key
    key = self._make_key(model_id, operation, inputs, parameters)
    key = self._make_key(model_id, operation, inputs, parameters)


    # Use default TTL if not specified
    # Use default TTL if not specified
    if ttl is None:
    if ttl is None:
    ttl = self.config.ttl
    ttl = self.config.ttl


    # Set value in cache
    # Set value in cache
    return self.backend.set(key, value, ttl)
    return self.backend.set(key, value, ttl)


    def delete(
    def delete(
    self,
    self,
    model_id: str,
    model_id: str,
    operation: str,
    operation: str,
    inputs: Union[str, List[str], Dict[str, Any]],
    inputs: Union[str, List[str], Dict[str, Any]],
    parameters: Optional[Dict[str, Any]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    ) -> bool:
    ) -> bool:
    """
    """
    Delete a value from the cache.
    Delete a value from the cache.


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
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    # Generate structured cache key
    # Generate structured cache key
    key = self._make_key(model_id, operation, inputs, parameters)
    key = self._make_key(model_id, operation, inputs, parameters)


    # Delete value from cache
    # Delete value from cache
    return self.backend.delete(key)
    return self.backend.delete(key)


    def exists(
    def exists(
    self,
    self,
    model_id: str,
    model_id: str,
    operation: str,
    operation: str,
    inputs: Union[str, List[str], Dict[str, Any]],
    inputs: Union[str, List[str], Dict[str, Any]],
    parameters: Optional[Dict[str, Any]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    ) -> bool:
    ) -> bool:
    """
    """
    Check if a value exists in the cache.
    Check if a value exists in the cache.


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
    True if the value exists, False otherwise
    True if the value exists, False otherwise
    """
    """
    if not self.config.should_cache(model_id, operation):
    if not self.config.should_cache(model_id, operation):
    return False
    return False


    # Generate structured cache key
    # Generate structured cache key
    key = self._make_key(model_id, operation, inputs, parameters)
    key = self._make_key(model_id, operation, inputs, parameters)


    # Check if value exists in cache
    # Check if value exists in cache
    return self.backend.exists(key)
    return self.backend.exists(key)


    def clear(self) -> bool:
    def clear(self) -> bool:
    """
    """
    Clear all values from the cache.
    Clear all values from the cache.


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    return self.backend.clear()
    return self.backend.clear()


    def clear_namespace(self, namespace: str) -> bool:
    def clear_namespace(self, namespace: str) -> bool:
    """
    """
    Clear all values for a specific namespace.
    Clear all values for a specific namespace.


    Args:
    Args:
    namespace: Namespace to clear (model_id)
    namespace: Namespace to clear (model_id)


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    # The key format is "model:model_id|op:operation|in:input_hash|params:parameters_hash"
    # The key format is "model:model_id|op:operation|in:input_hash|params:parameters_hash"
    # Match keys where the model_id part exactly matches our namespace
    # Match keys where the model_id part exactly matches our namespace
    pattern = f"^model:{re.escape(namespace)}\\|"
    pattern = f"^model:{re.escape(namespace)}\\|"
    keys = self.get_keys(pattern)
    keys = self.get_keys(pattern)


    if not keys:
    if not keys:
    # No keys found for this namespace
    # No keys found for this namespace
    return True
    return True


    # Delete each key in the namespace
    # Delete each key in the namespace
    success = True
    success = True
    for key in keys:
    for key in keys:
    if not self.backend.delete(key):
    if not self.backend.delete(key):
    success = False
    success = False


    return success
    return success


    def get_stats(self) -> Dict[str, Any]:
    def get_stats(self) -> Dict[str, Any]:
    """
    """
    Get statistics about the cache.
    Get statistics about the cache.


    Returns:
    Returns:
    Dictionary with cache statistics
    Dictionary with cache statistics
    """
    """
    stats = self.backend.get_stats()
    stats = self.backend.get_stats()
    stats["enabled"] = self.config.enabled
    stats["enabled"] = self.config.enabled
    stats["backend"] = self.config.backend
    stats["backend"] = self.config.backend
    stats["ttl"] = self.config.ttl
    stats["ttl"] = self.config.ttl


    return stats
    return stats


    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
    """
    """
    Get all keys in the cache.
    Get all keys in the cache.


    Args:
    Args:
    pattern: Optional pattern to filter keys
    pattern: Optional pattern to filter keys


    Returns:
    Returns:
    List of keys
    List of keys
    """
    """
    return self.backend.get_keys(pattern)
    return self.backend.get_keys(pattern)


    def get_size(self) -> int:
    def get_size(self) -> int:
    """
    """
    Get the size of the cache.
    Get the size of the cache.


    Returns:
    Returns:
    Number of items in the cache
    Number of items in the cache
    """
    """
    return self.backend.get_size()
    return self.backend.get_size()


    def set_config(self, config: CacheConfig) -> None:
    def set_config(self, config: CacheConfig) -> None:
    """
    """
    Set a new configuration for the cache.
    Set a new configuration for the cache.


    Args:
    Args:
    config: New cache configuration
    config: New cache configuration
    """
    """
    self.config = config
    self.config = config
    self.backend = self._create_backend()
    self.backend = self._create_backend()


    def _create_backend(self) -> CacheBackend:
    def _create_backend(self) -> CacheBackend:
    """
    """
    Create a cache backend based on the configuration.
    Create a cache backend based on the configuration.


    Returns:
    Returns:
    Cache backend
    Cache backend
    """
    """
    backend_name = self.config.backend.lower()
    backend_name = self.config.backend.lower()
    backend_config = self.config.get_backend_config()
    backend_config = self.config.get_backend_config()


    if backend_name == "memory":
    if backend_name == "memory":
    return MemoryCache(**backend_config)
    return MemoryCache(**backend_config)


    elif backend_name == "disk":
    elif backend_name == "disk":
    return DiskCache(**backend_config)
    return DiskCache(**backend_config)


    elif backend_name == "sqlite":
    elif backend_name == "sqlite":
    return SQLiteCache(**backend_config)
    return SQLiteCache(**backend_config)


    elif backend_name == "redis":
    elif backend_name == "redis":
    if not REDIS_AVAILABLE:
    if not REDIS_AVAILABLE:
    logger.warning("Redis not available. Falling back to memory cache.")
    logger.warning("Redis not available. Falling back to memory cache.")
    return MemoryCache(**self.config.get_backend_config("memory"))
    return MemoryCache(**self.config.get_backend_config("memory"))


    return RedisCache(**backend_config)
    return RedisCache(**backend_config)


    else:
    else:
    logger.warning(
    logger.warning(
    f"Unknown cache backend: {backend_name}. Falling back to memory cache."
    f"Unknown cache backend: {backend_name}. Falling back to memory cache."
    )
    )
    return MemoryCache(**self.config.get_backend_config("memory"))
    return MemoryCache(**self.config.get_backend_config("memory"))