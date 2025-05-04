"""
Memory cache backend for the model cache system.

This module provides an in-memory cache backend.
"""

import re
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from .base import CacheBackend


class MemoryCache(CacheBackend):
    """
    In-memory cache backend.
    """

    def __init__(
    self, max_size: Optional[int] = None, eviction_policy: str = "lru", **kwargs
    ):
    """
    Initialize the memory cache.
    """
    self.max_size = max_size
    self.eviction_policy = eviction_policy.lower()
    self.cache: Dict[str, Tuple[Dict[str, Any], Optional[float], int, float]] = {}
    self.lock = threading.RLock()
    self.stats = {
    "hits": 0,
    "misses": 0,
    "sets": 0,
    "deletes": 0,
    "evictions": 0,
    "clears": 0,
    }

    def get(self, key: str) -> Optional[Dict[str, Any]]:
    """Get a value from the cache."""
    with self.lock:
    if key not in self.cache:
    self.stats["misses"] += 1
    return None

    value, expiration_time, access_count, last_access_time = self.cache[key]

    # Check if expired
    current_time = time.time()
    if expiration_time is not None and current_time > expiration_time:
    self.delete(key)
    self.stats["misses"] += 1
    return None

    # Update access metadata
    self.cache[key] = (value, expiration_time, access_count + 1, current_time)
    self.stats["hits"] += 1
    return value

    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
    """Set a value in the cache."""
    with self.lock:
    current_time = time.time()
    expiration_time = current_time + ttl if ttl is not None else None

    # Check capacity before adding
    if (
    self.max_size is not None
    and len(self.cache) >= self.max_size
    and key not in self.cache
    ):
    self._evict_item()

    # Set new value with fresh metadata
    self.cache[key] = (value, expiration_time, 0, current_time)
    self.stats["sets"] += 1
    return True

    def delete(self, key: str) -> bool:
    """Delete a value from the cache."""
    with self.lock:
    if key in self.cache:
    del self.cache[key]
    self.stats["deletes"] += 1
    return True
    return False

    def exists(self, key: str) -> bool:
    """Check if a key exists in the cache."""
    with self.lock:
    if key not in self.cache:
    return False

    # Check if expired
    _, expiration_time, _, _ = self.cache[key]
    current_time = time.time()
    if expiration_time is not None and current_time > expiration_time:
    self.delete(key)
    return False

    return True

    def clear(self) -> bool:
    """Clear all values from the cache."""
    with self.lock:
    self.cache.clear()
    self.stats["clears"] += 1
    return True

    def get_size(self) -> int:
    """Get the current size of the cache."""
    with self.lock:
    self._remove_expired_items()
    return len(self.cache)

    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
    """Get all keys matching a pattern."""
    with self.lock:
    self._remove_expired_items()
    if pattern is None:
    return list(self.cache.keys())

    try:
    regex = re.compile(pattern)
    return [key for key in self.cache.keys() if regex.match(key)]
except re.error:
    return [
    key
    for key in self.cache.keys()
    if key.startswith(pattern.rstrip("^$"))
    ]

    def get_stats(self) -> Dict[str, Any]:
    """Get statistics about the cache."""
    with self.lock:
    return self.stats.copy()

    def get_ttl(self, key: str) -> Optional[int]:
    """Get the time to live for a key."""
    with self.lock:
    if key not in self.cache:
    return None

    _, expiration_time, _, _ = self.cache[key]
    if expiration_time is None:
    return None

    current_time = time.time()
    remaining = expiration_time - current_time

    # If expired, delete and return None
    if remaining <= 0:
    self.delete(key)
    return None

    return int(remaining)

    def set_ttl(self, key: str, ttl: int) -> bool:
    """Set the time to live for a key."""
    with self.lock:
    if key not in self.cache:
    return False

    value, _, access_count, last_access_time = self.cache[key]
    current_time = time.time()
    expiration_time = current_time + ttl if ttl is not None else None

    self.cache[key] = (value, expiration_time, access_count, last_access_time)
    return True

    def _evict_item(self) -> None:
    """Evict an item based on the eviction policy."""
    with self.lock:
    if not self.cache:
    return

    current_time = time.time()

    # Filter out expired items first
    valid_items = {
    k: v
    for k, v in self.cache.items()
    if v[1] is None or v[1] > current_time
    }

    if not valid_items:
    return

    if self.eviction_policy == "lru":
    # Get least recently accessed key
    key_to_evict = min(valid_items.items(), key=lambda x: x[1][3])[0]
    elif self.eviction_policy == "lfu":
    # Get least frequently used key
    key_to_evict = min(
    valid_items.items(), key=lambda x: (x[1][2], x[1][3])
    )[0]
    else:  # FIFO or default
    # Get oldest item by creation time (approximated by order in the dict)
    key_to_evict = next(iter(valid_items))

    if key_to_evict in self.cache:
    del self.cache[key_to_evict]
    self.stats["evictions"] += 1
    self.stats["deletes"] += 1

    def _remove_expired_items(self) -> None:
    """Remove all expired items."""
    with self.lock:
    current_time = time.time()
    expired_keys = [
    key
    for key, (_, exp, _, _) in self.cache.items()
    if exp is not None and current_time > exp
    ]
    for key in expired_keys:
    self.delete(key)
