"""
"""
Rate limiting storage backends.
Rate limiting storage backends.


This module provides storage backends for rate limiting.
This module provides storage backends for rate limiting.
"""
"""




import logging
import logging
import time
import time
from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from typing import Any, Dict, Optional


import redis
import redis


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




class RateLimitStorage(ABC):
    class RateLimitStorage(ABC):
    """
    """
    Abstract base class for rate limit storage backends.
    Abstract base class for rate limit storage backends.
    """
    """


    @abstractmethod
    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
    def get(self, key: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get rate limit data for a key.
    Get rate limit data for a key.


    Args:
    Args:
    key: Storage key
    key: Storage key


    Returns:
    Returns:
    Rate limit data or None if not found
    Rate limit data or None if not found
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def set(self, key: str, data: Dict[str, Any], expiry: Optional[int] = None) -> None:
    def set(self, key: str, data: Dict[str, Any], expiry: Optional[int] = None) -> None:
    """
    """
    Set rate limit data for a key.
    Set rate limit data for a key.


    Args:
    Args:
    key: Storage key
    key: Storage key
    data: Rate limit data
    data: Rate limit data
    expiry: Optional expiry time in seconds
    expiry: Optional expiry time in seconds
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def increment(
    def increment(
    self, key: str, amount: float = 1.0, expiry: Optional[int] = None
    self, key: str, amount: float = 1.0, expiry: Optional[int] = None
    ) -> float:
    ) -> float:
    """
    """
    Increment a counter for a key.
    Increment a counter for a key.


    Args:
    Args:
    key: Storage key
    key: Storage key
    amount: Amount to increment by
    amount: Amount to increment by
    expiry: Optional expiry time in seconds
    expiry: Optional expiry time in seconds


    Returns:
    Returns:
    New counter value
    New counter value
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def delete(self, key: str) -> None:
    def delete(self, key: str) -> None:
    """
    """
    Delete rate limit data for a key.
    Delete rate limit data for a key.


    Args:
    Args:
    key: Storage key
    key: Storage key
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def clear(self) -> None:
    def clear(self) -> None:
    """
    """
    Clear all rate limit data.
    Clear all rate limit data.
    """
    """
    pass
    pass




    class InMemoryStorage(RateLimitStorage):
    class InMemoryStorage(RateLimitStorage):
    """
    """
    In-memory storage backend for rate limiting.
    In-memory storage backend for rate limiting.
    """
    """


    def __init__(self):
    def __init__(self):
    """
    """
    Initialize the in-memory storage.
    Initialize the in-memory storage.
    """
    """
    self.data: Dict[str, Dict[str, Any]] = {}
    self.data: Dict[str, Dict[str, Any]] = {}
    self.expiry: Dict[str, float] = {}
    self.expiry: Dict[str, float] = {}


    def get(self, key: str) -> Optional[Dict[str, Any]]:
    def get(self, key: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get rate limit data for a key.
    Get rate limit data for a key.


    Args:
    Args:
    key: Storage key
    key: Storage key


    Returns:
    Returns:
    Rate limit data or None if not found
    Rate limit data or None if not found
    """
    """
    # Check if key exists and is not expired
    # Check if key exists and is not expired
    if key in self.data:
    if key in self.data:
    if key in self.expiry and self.expiry[key] < time.time():
    if key in self.expiry and self.expiry[key] < time.time():
    # Key is expired
    # Key is expired
    del self.data[key]
    del self.data[key]
    del self.expiry[key]
    del self.expiry[key]
    return None
    return None


    return self.data[key]
    return self.data[key]


    return None
    return None


    def set(self, key: str, data: Dict[str, Any], expiry: Optional[int] = None) -> None:
    def set(self, key: str, data: Dict[str, Any], expiry: Optional[int] = None) -> None:
    """
    """
    Set rate limit data for a key.
    Set rate limit data for a key.


    Args:
    Args:
    key: Storage key
    key: Storage key
    data: Rate limit data
    data: Rate limit data
    expiry: Optional expiry time in seconds
    expiry: Optional expiry time in seconds
    """
    """
    self.data[key] = data
    self.data[key] = data


    if expiry is not None:
    if expiry is not None:
    self.expiry[key] = time.time() + expiry
    self.expiry[key] = time.time() + expiry


    def increment(
    def increment(
    self, key: str, amount: float = 1.0, expiry: Optional[int] = None
    self, key: str, amount: float = 1.0, expiry: Optional[int] = None
    ) -> float:
    ) -> float:
    """
    """
    Increment a counter for a key.
    Increment a counter for a key.


    Args:
    Args:
    key: Storage key
    key: Storage key
    amount: Amount to increment by
    amount: Amount to increment by
    expiry: Optional expiry time in seconds
    expiry: Optional expiry time in seconds


    Returns:
    Returns:
    New counter value
    New counter value
    """
    """
    # Initialize counter if needed
    # Initialize counter if needed
    if key not in self.data:
    if key not in self.data:
    self.data[key] = {"count": 0}
    self.data[key] = {"count": 0}


    # Increment counter
    # Increment counter
    if "count" not in self.data[key]:
    if "count" not in self.data[key]:
    self.data[key]["count"] = 0
    self.data[key]["count"] = 0


    self.data[key]["count"] += amount
    self.data[key]["count"] += amount


    # Set expiry if provided
    # Set expiry if provided
    if expiry is not None:
    if expiry is not None:
    self.expiry[key] = time.time() + expiry
    self.expiry[key] = time.time() + expiry


    return self.data[key]["count"]
    return self.data[key]["count"]


    def delete(self, key: str) -> None:
    def delete(self, key: str) -> None:
    """
    """
    Delete rate limit data for a key.
    Delete rate limit data for a key.


    Args:
    Args:
    key: Storage key
    key: Storage key
    """
    """
    if key in self.data:
    if key in self.data:
    del self.data[key]
    del self.data[key]


    if key in self.expiry:
    if key in self.expiry:
    del self.expiry[key]
    del self.expiry[key]


    def clear(self) -> None:
    def clear(self) -> None:
    """
    """
    Clear all rate limit data.
    Clear all rate limit data.
    """
    """
    self.data.clear()
    self.data.clear()
    self.expiry.clear()
    self.expiry.clear()




    class RedisStorage(RateLimitStorage):
    class RedisStorage(RateLimitStorage):
    """
    """
    Redis storage backend for rate limiting.
    Redis storage backend for rate limiting.
    """
    """


    def __init__(self, redis_url: str, prefix: str = "rate_limit:"):
    def __init__(self, redis_url: str, prefix: str = "rate_limit:"):
    """
    """
    Initialize the Redis storage.
    Initialize the Redis storage.


    Args:
    Args:
    redis_url: Redis connection URL
    redis_url: Redis connection URL
    prefix: Key prefix for Redis
    prefix: Key prefix for Redis
    """
    """
    self.prefix = prefix
    self.prefix = prefix
    self.redis = None
    self.redis = None


    try:
    try:




    self.redis = redis.from_url(redis_url)
    self.redis = redis.from_url(redis_url)
    logger.info("Connected to Redis")
    logger.info("Connected to Redis")
except ImportError:
except ImportError:
    logger.warning(
    logger.warning(
    "Redis package not installed, falling back to in-memory storage"
    "Redis package not installed, falling back to in-memory storage"
    )
    )
    self.fallback = InMemoryStorage()
    self.fallback = InMemoryStorage()
except Exception as e:
except Exception as e:
    logger.warning(
    logger.warning(
    f"Failed to connect to Redis: {str(e)}, falling back to in-memory storage"
    f"Failed to connect to Redis: {str(e)}, falling back to in-memory storage"
    )
    )
    self.fallback = InMemoryStorage()
    self.fallback = InMemoryStorage()


    def _get_redis_key(self, key: str) -> str:
    def _get_redis_key(self, key: str) -> str:
    """
    """
    Get the Redis key with prefix.
    Get the Redis key with prefix.


    Args:
    Args:
    key: Storage key
    key: Storage key


    Returns:
    Returns:
    Redis key with prefix
    Redis key with prefix
    """
    """
    return f"{self.prefix}{key}"
    return f"{self.prefix}{key}"


    def get(self, key: str) -> Optional[Dict[str, Any]]:
    def get(self, key: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get rate limit data for a key.
    Get rate limit data for a key.


    Args:
    Args:
    key: Storage key
    key: Storage key


    Returns:
    Returns:
    Rate limit data or None if not found
    Rate limit data or None if not found
    """
    """
    if self.redis is None:
    if self.redis is None:
    return self.fallback.get(key)
    return self.fallback.get(key)


    redis_key = self._get_redis_key(key)
    redis_key = self._get_redis_key(key)
    data = self.redis.hgetall(redis_key)
    data = self.redis.hgetall(redis_key)


    if not data:
    if not data:
    return None
    return None


    # Convert Redis hash to dictionary
    # Convert Redis hash to dictionary
    result = {}
    result = {}
    for k, v in data.items():
    for k, v in data.items():
    k_str = k.decode("utf-8") if isinstance(k, bytes) else k
    k_str = k.decode("utf-8") if isinstance(k, bytes) else k
    try:
    try:
    # Try to convert to number
    # Try to convert to number
    result[k_str] = float(v)
    result[k_str] = float(v)
except (ValueError, TypeError):
except (ValueError, TypeError):
    # If not a number, keep as string
    # If not a number, keep as string
    result[k_str] = v.decode("utf-8") if isinstance(v, bytes) else v
    result[k_str] = v.decode("utf-8") if isinstance(v, bytes) else v


    return result
    return result


    def set(self, key: str, data: Dict[str, Any], expiry: Optional[int] = None) -> None:
    def set(self, key: str, data: Dict[str, Any], expiry: Optional[int] = None) -> None:
    """
    """
    Set rate limit data for a key.
    Set rate limit data for a key.


    Args:
    Args:
    key: Storage key
    key: Storage key
    data: Rate limit data
    data: Rate limit data
    expiry: Optional expiry time in seconds
    expiry: Optional expiry time in seconds
    """
    """
    if self.redis is None:
    if self.redis is None:
    self.fallback.set(key, data, expiry)
    self.fallback.set(key, data, expiry)
    return redis_key = self._get_redis_key(key)
    return redis_key = self._get_redis_key(key)


    # Convert dictionary to Redis hash
    # Convert dictionary to Redis hash
    hash_data = {}
    hash_data = {}
    for k, v in data.items():
    for k, v in data.items():
    hash_data[k] = str(v)
    hash_data[k] = str(v)


    # Set data
    # Set data
    self.redis.hmset(redis_key, hash_data)
    self.redis.hmset(redis_key, hash_data)


    # Set expiry if provided
    # Set expiry if provided
    if expiry is not None:
    if expiry is not None:
    self.redis.expire(redis_key, expiry)
    self.redis.expire(redis_key, expiry)


    def increment(
    def increment(
    self, key: str, amount: float = 1.0, expiry: Optional[int] = None
    self, key: str, amount: float = 1.0, expiry: Optional[int] = None
    ) -> float:
    ) -> float:
    """
    """
    Increment a counter for a key.
    Increment a counter for a key.


    Args:
    Args:
    key: Storage key
    key: Storage key
    amount: Amount to increment by
    amount: Amount to increment by
    expiry: Optional expiry time in seconds
    expiry: Optional expiry time in seconds


    Returns:
    Returns:
    New counter value
    New counter value
    """
    """
    if self.redis is None:
    if self.redis is None:
    return self.fallback.increment(key, amount, expiry)
    return self.fallback.increment(key, amount, expiry)


    redis_key = self._get_redis_key(key)
    redis_key = self._get_redis_key(key)


    # Increment counter
    # Increment counter
    new_value = self.redis.hincrby(redis_key, "count", int(amount))
    new_value = self.redis.hincrby(redis_key, "count", int(amount))


    # Set expiry if provided
    # Set expiry if provided
    if expiry is not None:
    if expiry is not None:
    self.redis.expire(redis_key, expiry)
    self.redis.expire(redis_key, expiry)


    return float(new_value)
    return float(new_value)


    def delete(self, key: str) -> None:
    def delete(self, key: str) -> None:
    """
    """
    Delete rate limit data for a key.
    Delete rate limit data for a key.


    Args:
    Args:
    key: Storage key
    key: Storage key
    """
    """
    if self.redis is None:
    if self.redis is None:
    self.fallback.delete(key)
    self.fallback.delete(key)
    return redis_key = self._get_redis_key(key)
    return redis_key = self._get_redis_key(key)
    self.redis.delete(redis_key)
    self.redis.delete(redis_key)


    def clear(self) -> None:
    def clear(self) -> None:
    """
    """
    Clear all rate limit data.
    Clear all rate limit data.
    """
    """
    if self.redis is None:
    if self.redis is None:
    self.fallback.clear()
    self.fallback.clear()
    return # Find all keys with the prefix
    return # Find all keys with the prefix
    keys = self.redis.keys(f"{self.prefix}*")
    keys = self.redis.keys(f"{self.prefix}*")


    # Delete all keys
    # Delete all keys
    if keys:
    if keys:
    self.redis.delete(*keys)
    self.redis.delete(*keys)




    def create_storage(storage_type: str, **kwargs) -> RateLimitStorage:
    def create_storage(storage_type: str, **kwargs) -> RateLimitStorage:
    """
    """
    Create a storage backend based on the specified type.
    Create a storage backend based on the specified type.


    Args:
    Args:
    storage_type: Storage type ("memory" or "redis")
    storage_type: Storage type ("memory" or "redis")
    **kwargs: Additional arguments for the storage backend
    **kwargs: Additional arguments for the storage backend


    Returns:
    Returns:
    Storage backend instance
    Storage backend instance
    """
    """
    if storage_type == "memory":
    if storage_type == "memory":
    return InMemoryStorage()
    return InMemoryStorage()
    elif storage_type == "redis":
    elif storage_type == "redis":
    redis_url = kwargs.get("redis_url", "redis://localhost:6379/0")
    redis_url = kwargs.get("redis_url", "redis://localhost:6379/0")
    prefix = kwargs.get("prefix", "rate_limit:")
    prefix = kwargs.get("prefix", "rate_limit:")
    return RedisStorage(redis_url, prefix)
    return RedisStorage(redis_url, prefix)
    else:
    else:
    raise ValueError(f"Unknown storage type: {storage_type}")
    raise ValueError(f"Unknown storage type: {storage_type}")