"""
Cache configuration for the model cache system.

This module provides configuration classes for the model cache system.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CacheConfig:
    """
    Configuration for the model cache system.
    """

    enabled: bool = True
    backend: str = "memory"
    ttl: Optional[int] = None  # Time to live in seconds (None for no expiration)
    max_size: Optional[int] = None  # Maximum number of items in the cache
    eviction_policy: str = "lru"  # Eviction policy (lru, lfu, fifo)
    serialization: str = "json"  # Serialization format (json, pickle)

    # Backend-specific configuration
    backend_config: Dict[str, Any] = field(default_factory=dict)

    # Cache filters
    model_filters: List[str] = field(default_factory=list)  # List of model IDs to cache
    operation_filters: List[str] = field(default_factory=list)  # List of operations to cache

    def should_cache(self, model_id: str, operation: str) -> bool:
        """
        Check if a model and operation should be cached.

        Args:
            model_id: ID of the model
            operation: Operation type

        Returns:
            True if the model and operation should be cached, False otherwise
        """
        if not self.enabled:
            return False

        # Check model filters
        if self.model_filters and model_id not in self.model_filters:
            return False

        # Check operation filters
        if self.operation_filters and operation not in self.operation_filters:
            return False

        return True

    def get_backend_config(self, backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration for a specific backend.

        Args:
            backend: Backend name (None for the configured backend)

        Returns:
            Backend configuration
        """
        backend_name = backend or self.backend

        # Common configuration
        config = {
            "max_size": self.max_size,
            "eviction_policy": self.eviction_policy,
            "serialization": self.serialization,
        }

        # Add backend-specific configuration
        if backend_name in self.backend_config:
            config.update(self.backend_config[backend_name])

        return config


@dataclass
class MemoryCacheConfig:
    """
    Configuration for the memory cache backend.
    """

    max_size: Optional[int] = None
    eviction_policy: str = "lru"


@dataclass
class DiskCacheConfig:
    """
    Configuration for the disk cache backend.
    """

    cache_dir: str = "cache"
    max_size: Optional[int] = None
    eviction_policy: str = "lru"
    serialization: str = "json"


@dataclass
class SQLiteCacheConfig:
    """
    Configuration for the SQLite cache backend.
    """

    db_path: str = "cache/cache.db"
    serialization: str = "json"


@dataclass
class RedisCacheConfig:
    """
    Configuration for the Redis cache backend.
    """

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    prefix: str = "model_cache:"
    serialization: str = "json"
