"""
"""
Cache configuration for the model cache system.
Cache configuration for the model cache system.


This module provides configuration classes for the model cache system.
This module provides configuration classes for the model cache system.
"""
"""




from dataclasses import dataclass, field
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional




@dataclass
@dataclass
class CacheConfig:
    class CacheConfig:
    """
    """
    Configuration for the model cache system.
    Configuration for the model cache system.
    """
    """


    enabled: bool = True
    enabled: bool = True
    backend: str = "memory"
    backend: str = "memory"
    ttl: Optional[int] = None  # Time to live in seconds (None for no expiration)
    ttl: Optional[int] = None  # Time to live in seconds (None for no expiration)
    max_size: Optional[int] = None  # Maximum number of items in the cache
    max_size: Optional[int] = None  # Maximum number of items in the cache
    eviction_policy: str = "lru"  # Eviction policy (lru, lfu, fifo)
    eviction_policy: str = "lru"  # Eviction policy (lru, lfu, fifo)
    serialization: str = "json"  # Serialization format (json, pickle)
    serialization: str = "json"  # Serialization format (json, pickle)


    # Backend-specific configuration
    # Backend-specific configuration
    backend_config: Dict[str, Any] = field(default_factory=dict)
    backend_config: Dict[str, Any] = field(default_factory=dict)


    # Cache filters
    # Cache filters
    model_filters: List[str] = field(default_factory=list)  # List of model IDs to cache
    model_filters: List[str] = field(default_factory=list)  # List of model IDs to cache
    operation_filters: List[str] = field(
    operation_filters: List[str] = field(
    default_factory=list
    default_factory=list
    )  # List of operations to cache
    )  # List of operations to cache


    def should_cache(self, model_id: str, operation: str) -> bool:
    def should_cache(self, model_id: str, operation: str) -> bool:
    """
    """
    Check if a model and operation should be cached.
    Check if a model and operation should be cached.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    operation: Operation type
    operation: Operation type


    Returns:
    Returns:
    True if the model and operation should be cached, False otherwise
    True if the model and operation should be cached, False otherwise
    """
    """
    if not self.enabled:
    if not self.enabled:
    return False
    return False


    # Check model filters
    # Check model filters
    if self.model_filters and model_id not in self.model_filters:
    if self.model_filters and model_id not in self.model_filters:
    return False
    return False


    # Check operation filters
    # Check operation filters
    if self.operation_filters and operation not in self.operation_filters:
    if self.operation_filters and operation not in self.operation_filters:
    return False
    return False


    return True
    return True


    def get_backend_config(self, backend: Optional[str] = None) -> Dict[str, Any]:
    def get_backend_config(self, backend: Optional[str] = None) -> Dict[str, Any]:
    """
    """
    Get configuration for a specific backend.
    Get configuration for a specific backend.


    Args:
    Args:
    backend: Backend name (None for the configured backend)
    backend: Backend name (None for the configured backend)


    Returns:
    Returns:
    Backend configuration
    Backend configuration
    """
    """
    backend_name = backend or self.backend
    backend_name = backend or self.backend


    # Common configuration
    # Common configuration
    config = {
    config = {
    "max_size": self.max_size,
    "max_size": self.max_size,
    "eviction_policy": self.eviction_policy,
    "eviction_policy": self.eviction_policy,
    "serialization": self.serialization,
    "serialization": self.serialization,
    }
    }


    # Add backend-specific configuration
    # Add backend-specific configuration
    if backend_name in self.backend_config:
    if backend_name in self.backend_config:
    config.update(self.backend_config[backend_name])
    config.update(self.backend_config[backend_name])


    return config
    return config




    @dataclass
    @dataclass
    class MemoryCacheConfig:
    class MemoryCacheConfig:
    """
    """
    Configuration for the memory cache backend.
    Configuration for the memory cache backend.
    """
    """


    max_size: Optional[int] = None
    max_size: Optional[int] = None
    eviction_policy: str = "lru"
    eviction_policy: str = "lru"




    @dataclass
    @dataclass
    class DiskCacheConfig:
    class DiskCacheConfig:
    """
    """
    Configuration for the disk cache backend.
    Configuration for the disk cache backend.
    """
    """


    cache_dir: str = "cache"
    cache_dir: str = "cache"
    max_size: Optional[int] = None
    max_size: Optional[int] = None
    eviction_policy: str = "lru"
    eviction_policy: str = "lru"
    serialization: str = "json"
    serialization: str = "json"




    @dataclass
    @dataclass
    class SQLiteCacheConfig:
    class SQLiteCacheConfig:
    """
    """
    Configuration for the SQLite cache backend.
    Configuration for the SQLite cache backend.
    """
    """


    db_path: str = "cache/cache.db"
    db_path: str = "cache/cache.db"
    serialization: str = "json"
    serialization: str = "json"




    @dataclass
    @dataclass
    class RedisCacheConfig:
    class RedisCacheConfig:
    """
    """
    Configuration for the Redis cache backend.
    Configuration for the Redis cache backend.
    """
    """


    host: str = "localhost"
    host: str = "localhost"
    port: int = 6379
    port: int = 6379
    db: int = 0
    db: int = 0
    password: Optional[str] = None
    password: Optional[str] = None
    prefix: str = "model_cache:"
    prefix: str = "model_cache:"
    serialization: str = "json"
    serialization: str = "json"