"""
Redis cache backend for the model cache system.

This module provides a Redis-based cache backend.
"""

import json
import time
import pickle
from typing import Dict, Any, Optional, List, Tuple
import re

from .base import CacheBackend

# Try to import Redis
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisCache(CacheBackend):
    """
    Redis-based cache backend.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "model_cache:",
        serialization: str = "json",
        **kwargs,
    ):
        """
        Initialize the Redis cache.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            prefix: Key prefix for cache items
            serialization: Serialization format (json, pickle)
            **kwargs: Additional parameters for the Redis client
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "Redis not available. Please install it with: pip install redis"
            )

        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.prefix = prefix
        self.serialization = serialization.lower()

        # Create Redis client
        self.redis = redis.Redis(
            host=self.host, port=self.port, db=self.db, password=self.password, **kwargs
        )

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0,
            "clears": 0,
        }
        self._load_stats()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        redis_key = self._get_redis_key(key)
        metadata_key = self._get_metadata_key(key)

        # Check if key exists
        if not self.redis.exists(redis_key):
            self.stats["misses"] += 1
            self._save_stats()
            return None

        # Get value
        value_blob = self.redis.get(redis_key)

        if value_blob is None:
            self.stats["misses"] += 1
            self._save_stats()
            return None

        # Deserialize value
        try:
            value = self._deserialize(value_blob)

            # Update access statistics
            self.redis.hincrby(metadata_key, "access_count", 1)
            self.redis.hset(metadata_key, "last_access_time", time.time())

            self.stats["hits"] += 1
            self._save_stats()
            return value

        except Exception as e:
            self.stats["misses"] += 1
            self._save_stats()
            return None

    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiration)

        Returns:
            True if successful, False otherwise
        """
        redis_key = self._get_redis_key(key)
        metadata_key = self._get_metadata_key(key)

        # Serialize value
        try:
            value_blob = self._serialize(value)

            # Set value
            if ttl is not None:
                self.redis.setex(redis_key, ttl, value_blob)
            else:
                self.redis.set(redis_key, value_blob)

            # Set metadata
            metadata = {
                "key": key,
                "creation_time": time.time(),
                "last_access_time": time.time(),
                "update_time": time.time(),
                "access_count": 0,
            }

            self.redis.hmset(metadata_key, metadata)

            # Set TTL for metadata
            if ttl is not None:
                self.redis.expire(metadata_key, ttl)

            self.stats["sets"] += 1
            self._save_stats()
            return True

        except Exception as e:
            return False

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        redis_key = self._get_redis_key(key)
        metadata_key = self._get_metadata_key(key)

        # Delete value and metadata
        self.redis.delete(redis_key, metadata_key)

        self.stats["deletes"] += 1
        self._save_stats()
        return True

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: Cache key

        Returns:
            True if the key exists, False otherwise
        """
        redis_key = self._get_redis_key(key)
        return bool(self.redis.exists(redis_key))

    def clear(self) -> bool:
        """
        Clear all values from the cache.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all keys with prefix
            pattern = f"{self.prefix}*"
            keys = self.redis.keys(pattern)

            if keys:
                # Delete all keys
                self.redis.delete(*keys)

            self.stats["clears"] += 1
            self._save_stats()
            return True

        except Exception as e:
            return False

    def get_size(self) -> int:
        """
        Get the size of the cache.

        Returns:
            Number of items in the cache
        """
        # Count keys with value prefix
        pattern = f"{self.prefix}value:*"
        return len(self.redis.keys(pattern))

    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all keys in the cache.

        Args:
            pattern: Optional pattern to filter keys

        Returns:
            List of keys
        """
        # Get all keys with value prefix
        redis_pattern = f"{self.prefix}value:*"
        redis_keys = self.redis.keys(redis_pattern)

        # Extract original keys
        keys = []
        prefix_len = len(f"{self.prefix}value:")

        for redis_key in redis_keys:
            key = redis_key.decode("utf-8")[prefix_len:]
            keys.append(key)

        if pattern is None:
            return keys

        # Filter keys by pattern
        regex = re.compile(pattern)
        return [key for key in keys if regex.match(key)]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.

        Returns:
            Dictionary with cache statistics
        """
        stats = self.stats.copy()
        stats["size"] = self.get_size()
        stats["serialization"] = self.serialization
        stats["host"] = self.host
        stats["port"] = self.port
        stats["db"] = self.db
        stats["prefix"] = self.prefix

        # Get Redis info
        try:
            info = self.redis.info()
            stats["redis_version"] = info.get("redis_version")
            stats["redis_memory_used"] = info.get("used_memory")
            stats["redis_memory_peak"] = info.get("used_memory_peak")
        except Exception:
            pass

        return stats

    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get the time to live for a key.

        Args:
            key: Cache key

        Returns:
            Time to live in seconds or None if no expiration
        """
        redis_key = self._get_redis_key(key)

        ttl = self.redis.ttl(redis_key)

        if ttl == -1:  # No expiration
            return None
        elif ttl == -2:  # Key does not exist
            return None
        else:
            return ttl

    def set_ttl(self, key: str, ttl: int) -> bool:
        """
        Set the time to live for a key.

        Args:
            key: Cache key
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        redis_key = self._get_redis_key(key)
        metadata_key = self._get_metadata_key(key)

        # Check if key exists
        if not self.redis.exists(redis_key):
            return False

        # Set TTL
        self.redis.expire(redis_key, ttl)
        self.redis.expire(metadata_key, ttl)

        return True

    def _get_redis_key(self, key: str) -> str:
        """
        Get the Redis key for a cache key.

        Args:
            key: Cache key

        Returns:
            Redis key
        """
        return f"{self.prefix}value:{key}"

    def _get_metadata_key(self, key: str) -> str:
        """
        Get the Redis key for metadata.

        Args:
            key: Cache key

        Returns:
            Redis metadata key
        """
        return f"{self.prefix}metadata:{key}"

    def _get_stats_key(self, name: str) -> str:
        """
        Get the Redis key for a statistic.

        Args:
            name: Statistic name

        Returns:
            Redis stats key
        """
        return f"{self.prefix}stats:{name}"

    def _serialize(self, value: Dict[str, Any]) -> bytes:
        """
        Serialize a value.

        Args:
            value: Value to serialize

        Returns:
            Serialized value
        """
        if self.serialization == "json":
            return json.dumps(value).encode("utf-8")
        elif self.serialization == "pickle":
            return pickle.dumps(value)
        else:
            # Default to JSON
            return json.dumps(value).encode("utf-8")

    def _deserialize(self, value_blob: bytes) -> Dict[str, Any]:
        """
        Deserialize a value.

        Args:
            value_blob: Serialized value

        Returns:
            Deserialized value
        """
        if self.serialization == "json":
            return json.loads(value_blob.decode("utf-8"))
        elif self.serialization == "pickle":
            return pickle.loads(value_blob)
        else:
            # Default to JSON
            return json.loads(value_blob.decode("utf-8"))

    def _load_stats(self) -> None:
        """
        Load statistics from Redis.
        """
        for name in self.stats.keys():
            key = self._get_stats_key(name)
            value = self.redis.get(key)

            if value is not None:
                try:
                    self.stats[name] = int(value)
                except (ValueError, TypeError):
                    pass

    def _save_stats(self) -> None:
        """
        Save statistics to Redis.
        """
        for name, value in self.stats.items():
            key = self._get_stats_key(name)
            self.redis.set(key, value)
