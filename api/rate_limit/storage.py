"""
Rate limiting storage backends.

This module provides storage backends for rate limiting.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RateLimitStorage(ABC):
    """
    Abstract base class for rate limit storage backends.
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get rate limit data for a key.

        Args:
            key: Storage key

        Returns:
            Rate limit data or None if not found
        """
        pass

    @abstractmethod
    def set(self, key: str, data: Dict[str, Any], expiry: Optional[int] = None) -> None:
        """
        Set rate limit data for a key.

        Args:
            key: Storage key
            data: Rate limit data
            expiry: Optional expiry time in seconds
        """
        pass

    @abstractmethod
    def increment(self, key: str, amount: float = 1.0, expiry: Optional[int] = None) -> float:
        """
        Increment a counter for a key.

        Args:
            key: Storage key
            amount: Amount to increment by
            expiry: Optional expiry time in seconds

        Returns:
            New counter value
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete rate limit data for a key.

        Args:
            key: Storage key
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear all rate limit data.
        """
        pass


class InMemoryStorage(RateLimitStorage):
    """
    In-memory storage backend for rate limiting.
    """

    def __init__(self):
        """
        Initialize the in-memory storage.
        """
        self.data: Dict[str, Dict[str, Any]] = {}
        self.expiry: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get rate limit data for a key.

        Args:
            key: Storage key

        Returns:
            Rate limit data or None if not found
        """
        # Check if key exists and is not expired
        if key in self.data:
            if key in self.expiry and self.expiry[key] < time.time():
                # Key is expired
                del self.data[key]
                del self.expiry[key]
                return None

            return self.data[key]

        return None

    def set(self, key: str, data: Dict[str, Any], expiry: Optional[int] = None) -> None:
        """
        Set rate limit data for a key.

        Args:
            key: Storage key
            data: Rate limit data
            expiry: Optional expiry time in seconds
        """
        self.data[key] = data

        if expiry is not None:
            self.expiry[key] = time.time() + expiry

    def increment(self, key: str, amount: float = 1.0, expiry: Optional[int] = None) -> float:
        """
        Increment a counter for a key.

        Args:
            key: Storage key
            amount: Amount to increment by
            expiry: Optional expiry time in seconds

        Returns:
            New counter value
        """
        # Initialize counter if needed
        if key not in self.data:
            self.data[key] = {"count": 0}

        # Increment counter
        if "count" not in self.data[key]:
            self.data[key]["count"] = 0

        self.data[key]["count"] += amount

        # Set expiry if provided
        if expiry is not None:
            self.expiry[key] = time.time() + expiry

        return self.data[key]["count"]

    def delete(self, key: str) -> None:
        """
        Delete rate limit data for a key.

        Args:
            key: Storage key
        """
        if key in self.data:
            del self.data[key]

        if key in self.expiry:
            del self.expiry[key]

    def clear(self) -> None:
        """
        Clear all rate limit data.
        """
        self.data.clear()
        self.expiry.clear()


class RedisStorage(RateLimitStorage):
    """
    Redis storage backend for rate limiting.
    """

    def __init__(self, redis_url: str, prefix: str = "rate_limit:"):
        """
        Initialize the Redis storage.

        Args:
            redis_url: Redis connection URL
            prefix: Key prefix for Redis
        """
        self.prefix = prefix
        self.redis = None

        try:
            import redis

            self.redis = redis.from_url(redis_url)
            logger.info("Connected to Redis")
        except ImportError:
            logger.warning("Redis package not installed, falling back to in-memory storage")
            self.fallback = InMemoryStorage()
        except Exception as e:
            logger.warning(
                f"Failed to connect to Redis: {str(e)}, falling back to in-memory storage"
            )
            self.fallback = InMemoryStorage()

    def _get_redis_key(self, key: str) -> str:
        """
        Get the Redis key with prefix.

        Args:
            key: Storage key

        Returns:
            Redis key with prefix
        """
        return f"{self.prefix}{key}"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get rate limit data for a key.

        Args:
            key: Storage key

        Returns:
            Rate limit data or None if not found
        """
        if self.redis is None:
            return self.fallback.get(key)

        redis_key = self._get_redis_key(key)
        data = self.redis.hgetall(redis_key)

        if not data:
            return None

        # Convert Redis hash to dictionary
        result = {}
        for k, v in data.items():
            k_str = k.decode("utf-8") if isinstance(k, bytes) else k
            try:
                # Try to convert to number
                result[k_str] = float(v)
            except (ValueError, TypeError):
                # If not a number, keep as string
                result[k_str] = v.decode("utf-8") if isinstance(v, bytes) else v

        return result

    def set(self, key: str, data: Dict[str, Any], expiry: Optional[int] = None) -> None:
        """
        Set rate limit data for a key.

        Args:
            key: Storage key
            data: Rate limit data
            expiry: Optional expiry time in seconds
        """
        if self.redis is None:
            self.fallback.set(key, data, expiry)
            return

        redis_key = self._get_redis_key(key)

        # Convert dictionary to Redis hash
        hash_data = {}
        for k, v in data.items():
            hash_data[k] = str(v)

        # Set data
        self.redis.hmset(redis_key, hash_data)

        # Set expiry if provided
        if expiry is not None:
            self.redis.expire(redis_key, expiry)

    def increment(self, key: str, amount: float = 1.0, expiry: Optional[int] = None) -> float:
        """
        Increment a counter for a key.

        Args:
            key: Storage key
            amount: Amount to increment by
            expiry: Optional expiry time in seconds

        Returns:
            New counter value
        """
        if self.redis is None:
            return self.fallback.increment(key, amount, expiry)

        redis_key = self._get_redis_key(key)

        # Increment counter
        new_value = self.redis.hincrby(redis_key, "count", int(amount))

        # Set expiry if provided
        if expiry is not None:
            self.redis.expire(redis_key, expiry)

        return float(new_value)

    def delete(self, key: str) -> None:
        """
        Delete rate limit data for a key.

        Args:
            key: Storage key
        """
        if self.redis is None:
            self.fallback.delete(key)
            return

        redis_key = self._get_redis_key(key)
        self.redis.delete(redis_key)

    def clear(self) -> None:
        """
        Clear all rate limit data.
        """
        if self.redis is None:
            self.fallback.clear()
            return

        # Find all keys with the prefix
        keys = self.redis.keys(f"{self.prefix}*")

        # Delete all keys
        if keys:
            self.redis.delete(*keys)


def create_storage(storage_type: str, **kwargs) -> RateLimitStorage:
    """
    Create a storage backend based on the specified type.

    Args:
        storage_type: Storage type ("memory" or "redis")
        **kwargs: Additional arguments for the storage backend

    Returns:
        Storage backend instance
    """
    if storage_type == "memory":
        return InMemoryStorage()
    elif storage_type == "redis":
        redis_url = kwargs.get("redis_url", "redis://localhost:6379/0")
        prefix = kwargs.get("prefix", "rate_limit:")
        return RedisStorage(redis_url, prefix)
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")
