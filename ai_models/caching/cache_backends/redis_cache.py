"""
"""
Redis cache backend for the model cache system.
Redis cache backend for the model cache system.


This module provides a Redis-based cache backend.
This module provides a Redis-based cache backend.
"""
"""




import json
import json
import pickle
import pickle
import re
import re
import time
import time
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


import redis
import redis


from .base import CacheBackend
from .base import CacheBackend


# Try to import Redis
# Try to import Redis
try:
    try:




    REDIS_AVAILABLE = True
    REDIS_AVAILABLE = True
except ImportError:
except ImportError:
    REDIS_AVAILABLE = False
    REDIS_AVAILABLE = False




    class RedisCache(CacheBackend):
    class RedisCache(CacheBackend):
    """
    """
    Redis-based cache backend.
    Redis-based cache backend.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    host: str = "localhost",
    host: str = "localhost",
    port: int = 6379,
    port: int = 6379,
    db: int = 0,
    db: int = 0,
    password: Optional[str] = None,
    password: Optional[str] = None,
    prefix: str = "model_cache:",
    prefix: str = "model_cache:",
    serialization: str = "json",
    serialization: str = "json",
    **kwargs,
    **kwargs,
    ):
    ):
    """
    """
    Initialize the Redis cache.
    Initialize the Redis cache.


    Args:
    Args:
    host: Redis host
    host: Redis host
    port: Redis port
    port: Redis port
    db: Redis database number
    db: Redis database number
    password: Redis password
    password: Redis password
    prefix: Key prefix for cache items
    prefix: Key prefix for cache items
    serialization: Serialization format (json, pickle)
    serialization: Serialization format (json, pickle)
    **kwargs: Additional parameters for the Redis client
    **kwargs: Additional parameters for the Redis client
    """
    """
    if not REDIS_AVAILABLE:
    if not REDIS_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "Redis not available. Please install it with: pip install redis"
    "Redis not available. Please install it with: pip install redis"
    )
    )


    self.host = host
    self.host = host
    self.port = port
    self.port = port
    self.db = db
    self.db = db
    self.password = password
    self.password = password
    self.prefix = prefix
    self.prefix = prefix
    self.serialization = serialization.lower()
    self.serialization = serialization.lower()


    # Create Redis client
    # Create Redis client
    self.redis = redis.Redis(
    self.redis = redis.Redis(
    host=self.host, port=self.port, db=self.db, password=self.password, **kwargs
    host=self.host, port=self.port, db=self.db, password=self.password, **kwargs
    )
    )


    # Statistics
    # Statistics
    self.stats = {
    self.stats = {
    "hits": 0,
    "hits": 0,
    "misses": 0,
    "misses": 0,
    "sets": 0,
    "sets": 0,
    "deletes": 0,
    "deletes": 0,
    "evictions": 0,
    "evictions": 0,
    "clears": 0,
    "clears": 0,
    }
    }
    self._load_stats()
    self._load_stats()


    def get(self, key: str) -> Optional[Dict[str, Any]]:
    def get(self, key: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get a value from the cache.
    Get a value from the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    Cached value or None if not found
    Cached value or None if not found
    """
    """
    redis_key = self._get_redis_key(key)
    redis_key = self._get_redis_key(key)
    metadata_key = self._get_metadata_key(key)
    metadata_key = self._get_metadata_key(key)


    # Check if key exists
    # Check if key exists
    if not self.redis.exists(redis_key):
    if not self.redis.exists(redis_key):
    self.stats["misses"] += 1
    self.stats["misses"] += 1
    self._save_stats()
    self._save_stats()
    return None
    return None


    # Get value
    # Get value
    value_blob = self.redis.get(redis_key)
    value_blob = self.redis.get(redis_key)


    if value_blob is None:
    if value_blob is None:
    self.stats["misses"] += 1
    self.stats["misses"] += 1
    self._save_stats()
    self._save_stats()
    return None
    return None


    # Deserialize value
    # Deserialize value
    try:
    try:
    value = self._deserialize(value_blob)
    value = self._deserialize(value_blob)


    # Update access statistics
    # Update access statistics
    self.redis.hincrby(metadata_key, "access_count", 1)
    self.redis.hincrby(metadata_key, "access_count", 1)
    self.redis.hset(metadata_key, "last_access_time", time.time())
    self.redis.hset(metadata_key, "last_access_time", time.time())


    self.stats["hits"] += 1
    self.stats["hits"] += 1
    self._save_stats()
    self._save_stats()
    return value
    return value


except Exception:
except Exception:
    self.stats["misses"] += 1
    self.stats["misses"] += 1
    self._save_stats()
    self._save_stats()
    return None
    return None


    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
    """
    """
    Set a value in the cache.
    Set a value in the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key
    value: Value to cache
    value: Value to cache
    ttl: Time to live in seconds (None for no expiration)
    ttl: Time to live in seconds (None for no expiration)


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    redis_key = self._get_redis_key(key)
    redis_key = self._get_redis_key(key)
    metadata_key = self._get_metadata_key(key)
    metadata_key = self._get_metadata_key(key)


    # Serialize value
    # Serialize value
    try:
    try:
    value_blob = self._serialize(value)
    value_blob = self._serialize(value)


    # Set value
    # Set value
    if ttl is not None:
    if ttl is not None:
    self.redis.setex(redis_key, ttl, value_blob)
    self.redis.setex(redis_key, ttl, value_blob)
    else:
    else:
    self.redis.set(redis_key, value_blob)
    self.redis.set(redis_key, value_blob)


    # Set metadata
    # Set metadata
    metadata = {
    metadata = {
    "key": key,
    "key": key,
    "creation_time": time.time(),
    "creation_time": time.time(),
    "last_access_time": time.time(),
    "last_access_time": time.time(),
    "update_time": time.time(),
    "update_time": time.time(),
    "access_count": 0,
    "access_count": 0,
    }
    }


    self.redis.hmset(metadata_key, metadata)
    self.redis.hmset(metadata_key, metadata)


    # Set TTL for metadata
    # Set TTL for metadata
    if ttl is not None:
    if ttl is not None:
    self.redis.expire(metadata_key, ttl)
    self.redis.expire(metadata_key, ttl)


    self.stats["sets"] += 1
    self.stats["sets"] += 1
    self._save_stats()
    self._save_stats()
    return True
    return True


except Exception:
except Exception:
    return False
    return False


    def delete(self, key: str) -> bool:
    def delete(self, key: str) -> bool:
    """
    """
    Delete a value from the cache.
    Delete a value from the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    redis_key = self._get_redis_key(key)
    redis_key = self._get_redis_key(key)
    metadata_key = self._get_metadata_key(key)
    metadata_key = self._get_metadata_key(key)


    # Delete value and metadata
    # Delete value and metadata
    self.redis.delete(redis_key, metadata_key)
    self.redis.delete(redis_key, metadata_key)


    self.stats["deletes"] += 1
    self.stats["deletes"] += 1
    self._save_stats()
    self._save_stats()
    return True
    return True


    def exists(self, key: str) -> bool:
    def exists(self, key: str) -> bool:
    """
    """
    Check if a key exists in the cache.
    Check if a key exists in the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    True if the key exists, False otherwise
    True if the key exists, False otherwise
    """
    """
    redis_key = self._get_redis_key(key)
    redis_key = self._get_redis_key(key)
    return bool(self.redis.exists(redis_key))
    return bool(self.redis.exists(redis_key))


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
    try:
    try:
    # Get all keys with prefix
    # Get all keys with prefix
    pattern = f"{self.prefix}*"
    pattern = f"{self.prefix}*"
    keys = self.redis.keys(pattern)
    keys = self.redis.keys(pattern)


    if keys:
    if keys:
    # Delete all keys
    # Delete all keys
    self.redis.delete(*keys)
    self.redis.delete(*keys)


    self.stats["clears"] += 1
    self.stats["clears"] += 1
    self._save_stats()
    self._save_stats()
    return True
    return True


except Exception:
except Exception:
    return False
    return False


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
    # Count keys with value prefix
    # Count keys with value prefix
    pattern = f"{self.prefix}value:*"
    pattern = f"{self.prefix}value:*"
    return len(self.redis.keys(pattern))
    return len(self.redis.keys(pattern))


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
    # Get all keys with value prefix
    # Get all keys with value prefix
    redis_pattern = f"{self.prefix}value:*"
    redis_pattern = f"{self.prefix}value:*"
    redis_keys = self.redis.keys(redis_pattern)
    redis_keys = self.redis.keys(redis_pattern)


    # Extract original keys
    # Extract original keys
    keys = []
    keys = []
    prefix_len = len(f"{self.prefix}value:")
    prefix_len = len(f"{self.prefix}value:")


    for redis_key in redis_keys:
    for redis_key in redis_keys:
    key = redis_key.decode("utf-8")[prefix_len:]
    key = redis_key.decode("utf-8")[prefix_len:]
    keys.append(key)
    keys.append(key)


    if pattern is None:
    if pattern is None:
    return keys
    return keys


    # Filter keys by pattern
    # Filter keys by pattern
    regex = re.compile(pattern)
    regex = re.compile(pattern)
    return [key for key in keys if regex.match(key)]
    return [key for key in keys if regex.match(key)]


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
    stats = self.stats.copy()
    stats = self.stats.copy()
    stats["size"] = self.get_size()
    stats["size"] = self.get_size()
    stats["serialization"] = self.serialization
    stats["serialization"] = self.serialization
    stats["host"] = self.host
    stats["host"] = self.host
    stats["port"] = self.port
    stats["port"] = self.port
    stats["db"] = self.db
    stats["db"] = self.db
    stats["prefix"] = self.prefix
    stats["prefix"] = self.prefix


    # Get Redis info
    # Get Redis info
    try:
    try:
    info = self.redis.info()
    info = self.redis.info()
    stats["redis_version"] = info.get("redis_version")
    stats["redis_version"] = info.get("redis_version")
    stats["redis_memory_used"] = info.get("used_memory")
    stats["redis_memory_used"] = info.get("used_memory")
    stats["redis_memory_peak"] = info.get("used_memory_peak")
    stats["redis_memory_peak"] = info.get("used_memory_peak")
except Exception:
except Exception:
    pass
    pass


    return stats
    return stats


    def get_ttl(self, key: str) -> Optional[int]:
    def get_ttl(self, key: str) -> Optional[int]:
    """
    """
    Get the time to live for a key.
    Get the time to live for a key.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    Time to live in seconds or None if no expiration
    Time to live in seconds or None if no expiration
    """
    """
    redis_key = self._get_redis_key(key)
    redis_key = self._get_redis_key(key)


    ttl = self.redis.ttl(redis_key)
    ttl = self.redis.ttl(redis_key)


    if ttl == -1:  # No expiration
    if ttl == -1:  # No expiration
    return None
    return None
    elif ttl == -2:  # Key does not exist
    elif ttl == -2:  # Key does not exist
    return None
    return None
    else:
    else:
    return ttl
    return ttl


    def set_ttl(self, key: str, ttl: int) -> bool:
    def set_ttl(self, key: str, ttl: int) -> bool:
    """
    """
    Set the time to live for a key.
    Set the time to live for a key.


    Args:
    Args:
    key: Cache key
    key: Cache key
    ttl: Time to live in seconds
    ttl: Time to live in seconds


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    redis_key = self._get_redis_key(key)
    redis_key = self._get_redis_key(key)
    metadata_key = self._get_metadata_key(key)
    metadata_key = self._get_metadata_key(key)


    # Check if key exists
    # Check if key exists
    if not self.redis.exists(redis_key):
    if not self.redis.exists(redis_key):
    return False
    return False


    # Set TTL
    # Set TTL
    self.redis.expire(redis_key, ttl)
    self.redis.expire(redis_key, ttl)
    self.redis.expire(metadata_key, ttl)
    self.redis.expire(metadata_key, ttl)


    return True
    return True


    def _get_redis_key(self, key: str) -> str:
    def _get_redis_key(self, key: str) -> str:
    """
    """
    Get the Redis key for a cache key.
    Get the Redis key for a cache key.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    Redis key
    Redis key
    """
    """
    return f"{self.prefix}value:{key}"
    return f"{self.prefix}value:{key}"


    def _get_metadata_key(self, key: str) -> str:
    def _get_metadata_key(self, key: str) -> str:
    """
    """
    Get the Redis key for metadata.
    Get the Redis key for metadata.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    Redis metadata key
    Redis metadata key
    """
    """
    return f"{self.prefix}metadata:{key}"
    return f"{self.prefix}metadata:{key}"


    def _get_stats_key(self, name: str) -> str:
    def _get_stats_key(self, name: str) -> str:
    """
    """
    Get the Redis key for a statistic.
    Get the Redis key for a statistic.


    Args:
    Args:
    name: Statistic name
    name: Statistic name


    Returns:
    Returns:
    Redis stats key
    Redis stats key
    """
    """
    return f"{self.prefix}stats:{name}"
    return f"{self.prefix}stats:{name}"


    def _serialize(self, value: Dict[str, Any]) -> bytes:
    def _serialize(self, value: Dict[str, Any]) -> bytes:
    """
    """
    Serialize a value.
    Serialize a value.


    Args:
    Args:
    value: Value to serialize
    value: Value to serialize


    Returns:
    Returns:
    Serialized value
    Serialized value
    """
    """
    if self.serialization == "json":
    if self.serialization == "json":
    return json.dumps(value).encode("utf-8")
    return json.dumps(value).encode("utf-8")
    elif self.serialization == "pickle":
    elif self.serialization == "pickle":
    return pickle.dumps(value)
    return pickle.dumps(value)
    else:
    else:
    # Default to JSON
    # Default to JSON
    return json.dumps(value).encode("utf-8")
    return json.dumps(value).encode("utf-8")


    def _deserialize(self, value_blob: bytes) -> Dict[str, Any]:
    def _deserialize(self, value_blob: bytes) -> Dict[str, Any]:
    """
    """
    Deserialize a value.
    Deserialize a value.


    Args:
    Args:
    value_blob: Serialized value
    value_blob: Serialized value


    Returns:
    Returns:
    Deserialized value
    Deserialized value
    """
    """
    if self.serialization == "json":
    if self.serialization == "json":
    return json.loads(value_blob.decode("utf-8"))
    return json.loads(value_blob.decode("utf-8"))
    elif self.serialization == "pickle":
    elif self.serialization == "pickle":
    return pickle.loads(value_blob)
    return pickle.loads(value_blob)
    else:
    else:
    # Default to JSON
    # Default to JSON
    return json.loads(value_blob.decode("utf-8"))
    return json.loads(value_blob.decode("utf-8"))


    def _load_stats(self) -> None:
    def _load_stats(self) -> None:
    """
    """
    Load statistics from Redis.
    Load statistics from Redis.
    """
    """
    for name in self.stats.keys():
    for name in self.stats.keys():
    key = self._get_stats_key(name)
    key = self._get_stats_key(name)
    value = self.redis.get(key)
    value = self.redis.get(key)


    if value is not None:
    if value is not None:
    try:
    try:
    self.stats[name] = int(value)
    self.stats[name] = int(value)
except (ValueError, TypeError):
except (ValueError, TypeError):
    pass
    pass


    def _save_stats(self) -> None:
    def _save_stats(self) -> None:
    """
    """
    Save statistics to Redis.
    Save statistics to Redis.
    """
    """
    for name, value in self.stats.items():
    for name, value in self.stats.items():
    key = self._get_stats_key(name)
    key = self._get_stats_key(name)
    self.redis.set(key, value)
    self.redis.set(key, value)