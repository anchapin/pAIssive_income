"""
Cache manager for the model cache system.

This module provides the main cache manager for the model cache system.
"""

import os
import re
import logging
import hashlib
from typing import Dict, Any, Optional, List, Union, Type

from .cache_config import CacheConfig
from .cache_key import CacheKey, generate_cache_key, parse_cache_key
from .cache_backends import (
    CacheBackend,
    MemoryCache,
    DiskCache,
    SQLiteCache
)

# Try to import Redis cache if available
try:
    from .cache_backends import RedisCache
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manager for the model cache system.
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        """
        Initialize the cache manager.

        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()
        self.backend = self._create_backend()

    def _make_key(
        self,
        model_id: str,
        operation: str,
        inputs: Union[str, List[str], Dict[str, Any]],
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a consistent cache key string that preserves namespace structure.
        """
        # Generate cache key object
        key = generate_cache_key(model_id, operation, inputs, parameters)
        
        # Return the structured key that maintains namespace information
        # Use colon as separator to maintain compatibility with tests
        return f"{key.model_id}:{key.operation}:{key.input_hash}:{key.parameters_hash}"

    def get(
        self,
        model_id: str,
        operation: str,
        inputs: Union[str, List[str], Dict[str, Any]],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.

        Args:
            model_id: ID of the model
            operation: Operation type (e.g., "generate", "embed", "classify")
            inputs: Input data for the model
            parameters: Optional parameters for the operation

        Returns:
            Cached value or None if not found
        """
        if not self.config.should_cache(model_id, operation):
            return None
        
        # Generate structured cache key
        key = self._make_key(model_id, operation, inputs, parameters)
        
        # Get value from cache
        return self.backend.get(key)

    def set(
        self,
        model_id: str,
        operation: str,
        inputs: Union[str, List[str], Dict[str, Any]],
        value: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set a value in the cache.

        Args:
            model_id: ID of the model
            operation: Operation type (e.g., "generate", "embed", "classify")
            inputs: Input data for the model
            value: Value to cache
            parameters: Optional parameters for the operation
            ttl: Time to live in seconds (None for default TTL)

        Returns:
            True if successful, False otherwise
        """
        if not self.config.should_cache(model_id, operation):
            return False
        
        # Generate structured cache key
        key = self._make_key(model_id, operation, inputs, parameters)
        
        # Use default TTL if not specified
        if ttl is None:
            ttl = self.config.ttl
        
        # Set value in cache
        return self.backend.set(key, value, ttl)

    def delete(
        self,
        model_id: str,
        operation: str,
        inputs: Union[str, List[str], Dict[str, Any]],
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Delete a value from the cache.

        Args:
            model_id: ID of the model
            operation: Operation type (e.g., "generate", "embed", "classify")
            inputs: Input data for the model
            parameters: Optional parameters for the operation

        Returns:
            True if successful, False otherwise
        """
        # Generate structured cache key
        key = self._make_key(model_id, operation, inputs, parameters)
        
        # Delete value from cache
        return self.backend.delete(key)

    def exists(
        self,
        model_id: str,
        operation: str,
        inputs: Union[str, List[str], Dict[str, Any]],
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if a value exists in the cache.

        Args:
            model_id: ID of the model
            operation: Operation type (e.g., "generate", "embed", "classify")
            inputs: Input data for the model
            parameters: Optional parameters for the operation

        Returns:
            True if the value exists, False otherwise
        """
        if not self.config.should_cache(model_id, operation):
            return False
        
        # Generate structured cache key
        key = self._make_key(model_id, operation, inputs, parameters)
        
        # Check if value exists in cache
        return self.backend.exists(key)

    def clear(self) -> bool:
        """
        Clear all values from the cache.

        Returns:
            True if successful, False otherwise
        """
        return self.backend.clear()

    def clear_namespace(self, namespace: str) -> bool:
        """
        Clear all values for a specific namespace.
        
        Args:
            namespace: Namespace to clear (model_id)
            
        Returns:
            True if successful, False otherwise
        """
        # Get all keys that start with the namespace
        # The CacheKey format is "model_id:operation:input_hash:parameters_hash"
        # We need to match keys where the model_id part exactly matches our namespace
        pattern = f"^{re.escape(namespace)}:"
        keys = self.get_keys(pattern)
        
        if not keys:
            # No keys found for this namespace
            return True

        # Delete each key in the namespace
        success = True
        for key in keys:
            if not self.backend.delete(key):
                success = False

        return success

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.

        Returns:
            Dictionary with cache statistics
        """
        stats = self.backend.get_stats()
        stats["enabled"] = self.config.enabled
        stats["backend"] = self.config.backend
        stats["ttl"] = self.config.ttl

        return stats

    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all keys in the cache.

        Args:
            pattern: Optional pattern to filter keys

        Returns:
            List of keys
        """
        return self.backend.get_keys(pattern)

    def get_size(self) -> int:
        """
        Get the size of the cache.

        Returns:
            Number of items in the cache
        """
        return self.backend.get_size()

    def set_config(self, config: CacheConfig) -> None:
        """
        Set a new configuration for the cache.

        Args:
            config: New cache configuration
        """
        self.config = config
        self.backend = self._create_backend()

    def _create_backend(self) -> CacheBackend:
        """
        Create a cache backend based on the configuration.

        Returns:
            Cache backend
        """
        backend_name = self.config.backend.lower()
        backend_config = self.config.get_backend_config()

        if backend_name == "memory":
            return MemoryCache(**backend_config)

        elif backend_name == "disk":
            return DiskCache(**backend_config)

        elif backend_name == "sqlite":
            return SQLiteCache(**backend_config)

        elif backend_name == "redis":
            if not REDIS_AVAILABLE:
                logger.warning("Redis not available. Falling back to memory cache.")
                return MemoryCache(**self.config.get_backend_config("memory"))

            return RedisCache(**backend_config)

        else:
            logger.warning(f"Unknown cache backend: {backend_name}. Falling back to memory cache.")
            return MemoryCache(**self.config.get_backend_config("memory"))
