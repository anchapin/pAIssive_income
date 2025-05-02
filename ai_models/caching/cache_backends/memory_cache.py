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

    def __init__(self, max_size: Optional[int] = None, eviction_policy: str = "lru", **kwargs):
        """
        Initialize the memory cache.

        Args:
            max_size: Maximum number of items in the cache (None for unlimited)
            eviction_policy: Eviction policy (lru, lfu, fifo)
            **kwargs: Additional parameters for the cache
        """
        self.max_size = max_size
        self.eviction_policy = eviction_policy.lower()

        # Cache storage: key -> (value, expiration_time, access_count, last_access_time)
        self.cache: Dict[str, Tuple[Dict[str, Any], Optional[float], int, float]] = {}

        # Lock for thread safety
        self.lock = threading.RLock()

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0,
            "clears": 0,
        }

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        with self.lock:
            if key in self.cache:
                value, expiration_time, access_count, _ = self.cache[key]
                
                # Check if expired
                current_time = time.time()
                if expiration_time is not None and current_time > expiration_time:
                    self.delete(key)
                    self.stats["misses"] += 1
                    return None
                
                # Update access count and last access time BEFORE returning
                self.cache[key] = (value, expiration_time, access_count + 1, current_time)
                
                self.stats["hits"] += 1
                return value

            self.stats["misses"] += 1
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
        with self.lock:
            current_time = time.time()
            
            # Calculate expiration time
            expiration_time = None
            if ttl is not None:
                expiration_time = current_time + ttl
            
            # For new items, start with access_count of 0
            # For existing items, preserve their access count if using LFU
            existing_data = self.cache.get(key)
            if existing_data:
                _, _, access_count, _ = existing_data
                if self.eviction_policy != "lfu":
                    access_count = 0  # Reset for non-LFU policies
            else:
                access_count = 0
                # Check if we need to evict an item before adding a new one
                # Only evict if this is a new key and we're at capacity
                if self.max_size is not None and len(self.cache) >= self.max_size:
                    self._evict_item()
            
            # Store with current timestamp for proper LRU ordering
            self.cache[key] = (value, expiration_time, access_count, current_time)
            
            self.stats["sets"] += 1
            return True

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.stats["deletes"] += 1
                return True

            return False

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: Cache key

        Returns:
            True if the key exists, False otherwise
        """
        with self.lock:
            if key in self.cache:
                _, expiration_time, _, _ = self.cache[key]

                # Check if expired
                if expiration_time is not None and time.time() > expiration_time:
                    self.delete(key)
                    return False

                return True

            return False

    def clear(self) -> bool:
        """
        Clear all values from the cache.

        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            self.cache.clear()
            self.stats["clears"] += 1
            return True

    def get_size(self) -> int:
        """
        Get the size of the cache.

        Returns:
            Number of items in the cache
        """
        with self.lock:
            # Remove expired items
            self._remove_expired_items()

            return len(self.cache)

    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all keys in the cache.

        Args:
            pattern: Optional pattern to filter keys

        Returns:
            List of keys
        """
        with self.lock:
            # Remove expired items
            self._remove_expired_items()

            if pattern is None:
                return list(self.cache.keys())

            # Filter keys by pattern with safe regex handling
            try:
                regex = re.compile(pattern)
                return [key for key in self.cache.keys() if regex.match(key)]
            except re.error:  # If pattern is invalid, treat as literal prefix
                return [key for key in self.cache.keys() if key.startswith(pattern.rstrip('^$'))]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.

        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            stats = self.stats.copy()
            stats["size"] = self.get_size()
            stats["max_size"] = self.max_size
            stats["eviction_policy"] = self.eviction_policy

            return stats

    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get the time to live for a key.

        Args:
            key: Cache key

        Returns:
            Time to live in seconds or None if no expiration
        """
        with self.lock:
            if key in self.cache:
                _, expiration_time, _, _ = self.cache[key]

                if expiration_time is None:
                    return None

                ttl = int(expiration_time - time.time())
                return ttl if ttl > 0 else 0

            return None

    def set_ttl(self, key: str, ttl: int) -> bool:
        """
        Set the time to live for a key.

        Args:
            key: Cache key
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if key in self.cache:
                value, _, access_count, last_access_time = self.cache[key]

                expiration_time = time.time() + ttl
                self.cache[key] = (
                    value,
                    expiration_time,
                    access_count,
                    last_access_time,
                )

                return True

            return False

    def _evict_item(self) -> None:
        """
        Evict an item from the cache based on the eviction policy.
        """
        if not self.cache:
            return
        
        current_time = time.time()
        
        # Filter out expired items first
        valid_items = [
            (k, v) for k, v in self.cache.items()
            if v[1] is None or v[1] > current_time
        ]
        
        if not valid_items:
            return
        
        try:
            if self.eviction_policy == "lru":
                # Find the least recently used item among non-expired items
                key_to_evict = min(
                    valid_items,
                    key=lambda x: x[1][3]  # x[1][3] is last_access_time
                )[0]
            elif self.eviction_policy == "lfu":
                # Find least frequently used item, using access time as tiebreaker
                key_to_evict = min(
                    valid_items,
                    key=lambda x: (x[1][2], -x[1][3])  # (access_count, -last_access_time)
                )[0]
            elif self.eviction_policy == "fifo":
                # First in first out - take the first non-expired item
                key_to_evict = valid_items[0][0]
            else:
                # Default to LRU
                key_to_evict = min(
                    valid_items,
                    key=lambda x: x[1][3]  # x[1][3] is last_access_time
                )[0]
            
            # Delete the chosen item
            if key_to_evict in self.cache:
                self.delete(key_to_evict)
                self.stats["evictions"] += 1
                
        except Exception:
            # If there's any error in the eviction logic, fall back to removing the first valid item
            if valid_items:
                self.delete(valid_items[0][0])
                self.stats["evictions"] += 1
    
    def _remove_expired_items(self) -> None:
        """
        Remove expired items from the cache.
        """
        current_time = time.time()
        keys_to_delete = [
            key for key, (_, expiration_time, _, _) in self.cache.items()
            if expiration_time is not None and current_time > expiration_time
        ]
        
        for key in keys_to_delete:
            self.delete(key)
