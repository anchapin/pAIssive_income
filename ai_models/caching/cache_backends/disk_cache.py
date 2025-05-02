"""
Disk cache backend for the model cache system.

This module provides a disk-based cache backend.
"""

import hashlib
import json
import os
import pickle
import re
import shutil
import threading
import time
from typing import Any, Dict, List, Optional

from .base import CacheBackend


class DiskCache(CacheBackend):
    """
    Disk-based cache backend.
    """

    def __init__(
        self,
        cache_dir: str,
        max_size: Optional[int] = None,
        eviction_policy: str = "lru",
        serialization: str = "json",
        **kwargs,
    ):
        """
        Initialize the disk cache.

        Args:
            cache_dir: Directory to store cache files
            max_size: Maximum number of items in the cache (None for unlimited)
            eviction_policy: Eviction policy (lru, lfu, fifo)
            serialization: Serialization format (json, pickle)
            **kwargs: Additional parameters for the cache
        """
        self.cache_dir = os.path.abspath(cache_dir)
        self.max_size = max_size
        self.eviction_policy = eviction_policy.lower()
        self.serialization = serialization.lower()

        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)

        # Create metadata directory
        self.metadata_dir = os.path.join(self.cache_dir, "_metadata")
        os.makedirs(self.metadata_dir, exist_ok=True)

        # Lock for thread safety
        self.lock = threading.RLock()

        # Statistics
        self.stats_file = os.path.join(self.metadata_dir, "stats.json")
        self._load_stats()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value from the cache."""
        with self.lock:
            if not self.exists(key):
                self.stats["misses"] += 1
                self._save_stats()
                return None

            try:
                # Load metadata first to check expiration
                metadata = self._load_metadata(key)
                expiration_time = metadata.get("expiration_time")

                if expiration_time is not None and time.time() > expiration_time:
                    # Item has expired
                    self.delete(key)
                    self.stats["misses"] += 1
                    self._save_stats()
                    return None

                # Load value
                value = self._load_value(key)

                # Initialize access_count if not present
                if "access_count" not in metadata:
                    metadata["access_count"] = 0

                # Update access time and count in metadata
                metadata["last_access_time"] = time.time()
                metadata["access_count"] = metadata.get("access_count", 0) + 1
                self._save_metadata(key, metadata)
                self.stats["hits"] += 1
                self._save_stats()
                return value

            except (IOError, json.JSONDecodeError):
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
        with self.lock:
            # Check if we need to evict an item first - BEFORE setting the new item
            if self.max_size is not None and not self.exists(key):
                current_size = self.get_size()
                if current_size >= self.max_size:
                    self._evict_item()

            # Calculate expiration time
            expiration_time = None
            if ttl is not None:
                expiration_time = time.time() + ttl

            # Always start with access_count of 0 for new items
            # Only preserve access count if key exists and we're updating
            access_count = 0
            if self.exists(key):
                try:
                    old_metadata = self._load_metadata(key)
                    if self.eviction_policy == "lfu":
                        # For LFU, preserve the access count
                        access_count = old_metadata.get("access_count", 0)
                    else:
                        # For other policies, reset access count on update
                        access_count = 0
                except (IOError, json.JSONDecodeError):
                    pass

            # Create metadata
            current_time = time.time()
            metadata = {
                "key": key,
                "expiration_time": expiration_time,
                "access_count": access_count,
                "last_access_time": current_time,
                "creation_time": (
                    current_time
                    if not self.exists(key)
                    else self._load_metadata(key).get("creation_time", current_time)
                ),
            }

            # Save value and metadata
            try:
                self._save_value(key, value)
                self._save_metadata(key, metadata)

                self.stats["sets"] += 1
                self._save_stats()
                return True

            except Exception:
                return False

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            file_path = self._get_file_path(key)
            metadata_path = self._get_metadata_path(key)

            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass

            if os.path.exists(metadata_path):
                try:
                    os.remove(metadata_path)
                except Exception:
                    pass

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
        with self.lock:
            file_path = self._get_file_path(key)
            metadata_path = self._get_metadata_path(key)

            if not os.path.exists(file_path) or not os.path.exists(metadata_path):
                return False

            # Load metadata
            metadata = self._load_metadata(key)

            # Check if expired
            if (
                metadata.get("expiration_time") is not None
                and time.time() > metadata["expiration_time"]
            ):
                self.delete(key)
                return False

            return True

    def clear(self) -> bool:
        """
        Clear all values from the cache.

        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            try:
                # Remove all files except metadata directory
                for item in os.listdir(self.cache_dir):
                    item_path = os.path.join(self.cache_dir, item)
                    if item != "_metadata" and os.path.exists(item_path):
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)

                # Clear metadata directory
                for item in os.listdir(self.metadata_dir):
                    if item != "stats.json":
                        item_path = os.path.join(self.metadata_dir, item)
                        if os.path.exists(item_path):
                            os.remove(item_path)

                self.stats["clears"] += 1
                self._save_stats()
                return True

            except Exception:
                return False

    def get_size(self) -> int:
        """
        Get the size of the cache.

        Returns:
            Number of items in the cache
        """
        with self.lock:
            # Remove expired items
            self._remove_expired_items()

            # Count files in cache directory
            count = 0
            for item in os.listdir(self.cache_dir):
                item_path = os.path.join(self.cache_dir, item)
                if item != "_metadata" and os.path.isfile(item_path):
                    count += 1

            return count

    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all keys in the cache.

        Args:
            pattern: Optional pattern to filter keys

        Returns:
            List of keys
        """
        keys = []

        # List all metadata files to get the actual keys
        for filename in os.listdir(self.metadata_dir):
            if not filename.endswith(".json") or filename == "stats.json":
                continue

            try:
                metadata_path = os.path.join(self.metadata_dir, filename)
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                    if "key" in metadata:
                        key = metadata["key"]
                        if pattern is None or re.match(pattern, key):
                            keys.append(key)
            except (IOError, json.JSONDecodeError):
                continue

        return keys

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
            stats["serialization"] = self.serialization
            stats["cache_dir"] = self.cache_dir

            # Calculate disk usage
            disk_usage = 0
            for root, dirs, files in os.walk(self.cache_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    disk_usage += os.path.getsize(file_path)

            stats["disk_usage"] = disk_usage

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
            if not self.exists(key):
                return None

            metadata = self._load_metadata(key)

            if metadata.get("expiration_time") is None:
                return None

            ttl = int(metadata["expiration_time"] - time.time())
            return ttl if ttl > 0 else 0

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
            if not self.exists(key):
                return False

            metadata = self._load_metadata(key)

            expiration_time = time.time() + ttl
            metadata["expiration_time"] = expiration_time

            self._save_metadata(key, metadata)
            return True

    def _get_file_path(self, key: str) -> str:
        """
        Get the file path for a cache key.

        Args:
            key: Cache key

        Returns:
            File path
        """
        # Hash the key to create a valid filename
        hashed_key = hashlib.md5(key.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, hashed_key)

    def _get_metadata_path(self, key: str) -> str:
        """
        Get the metadata file path for a cache key.

        Args:
            key: Cache key

        Returns:
            Metadata file path
        """
        # Hash the key to create a valid filename
        hashed_key = hashlib.md5(key.encode("utf-8")).hexdigest()
        return os.path.join(self.metadata_dir, f"{hashed_key}.json")

    def _save_value(self, key: str, value: Dict[str, Any]) -> None:
        """
        Save a value to disk.

        Args:
            key: Cache key
            value: Value to save
        """
        file_path = self._get_file_path(key)

        if self.serialization == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(value, f)
        elif self.serialization == "pickle":
            with open(file_path, "wb") as f:
                pickle.dump(value, f)
        else:
            # Default to JSON
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(value, f)

    def _load_value(self, key: str) -> Dict[str, Any]:
        """
        Load a value from disk.

        Args:
            key: Cache key

        Returns:
            Loaded value
        """
        file_path = self._get_file_path(key)

        if self.serialization == "json":
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        elif self.serialization == "pickle":
            with open(file_path, "rb") as f:
                return pickle.load(f)
        else:
            # Default to JSON
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _save_metadata(self, key: str, metadata: Dict[str, Any]) -> None:
        """
        Save metadata to disk.

        Args:
            key: Cache key
            metadata: Metadata to save
        """
        metadata_path = self._get_metadata_path(key)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f)

    def _load_metadata(self, key: str) -> Dict[str, Any]:
        """
        Load metadata from disk.

        Args:
            key: Cache key

        Returns:
            Loaded metadata
        """
        metadata_path = self._get_metadata_path(key)

        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_stats(self) -> None:
        """
        Load statistics from disk.
        """
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    self.stats = json.load(f)
            except Exception:
                self.stats = {
                    "hits": 0,
                    "misses": 0,
                    "sets": 0,
                    "deletes": 0,
                    "evictions": 0,
                    "clears": 0,
                }
        else:
            self.stats = {
                "hits": 0,
                "misses": 0,
                "sets": 0,
                "deletes": 0,
                "evictions": 0,
                "clears": 0,
            }

    def _save_stats(self) -> None:
        """
        Save statistics to disk.
        """
        with open(self.stats_file, "w", encoding="utf-8") as f:
            json.dump(self.stats, f)

    def _evict_item(self) -> None:
        """Evict an item from the cache based on the eviction policy."""
        with self.lock:
            keys = self.get_keys()
            if not keys:
                return

            try:
                # Load all metadata up front to avoid multiple disk reads
                metadata_map = {}
                current_time = time.time()
                for key in keys:
                    try:
                        metadata = self._load_metadata(key)
                        # Skip expired items
                        expiration_time = metadata.get("expiration_time")
                        if (
                            expiration_time is not None
                            and current_time > expiration_time
                        ):
                            self.delete(key)
                            continue
                        metadata_map[key] = metadata
                    except (IOError, json.JSONDecodeError):
                        # Skip corrupted metadata
                        continue

                if not metadata_map:
                    return

                if self.eviction_policy == "lru":
                    # Least Recently Used - evict item with oldest last_access_time
                    key_to_evict = min(
                        metadata_map.keys(),
                        key=lambda k: metadata_map[k].get("last_access_time", 0),
                    )
                elif self.eviction_policy == "lfu":
                    # Least Frequently Used - evict item with lowest access count and oldest creation time
                    def get_score(k):
                        metadata = metadata_map[k]
                        count = metadata.get("access_count", 0)
                        # Creation time is used as a tiebreaker - older items are evicted first
                        creation_time = metadata.get("creation_time", float("inf"))
                        # Return tuple of (count, creation_time) for comparison
                        # Python will compare tuples element by element
                        return (
                            count,
                            -creation_time,
                        )  # Negative creation_time so older items are evicted first

                    key_to_evict = min(metadata_map.keys(), key=get_score)
                elif self.eviction_policy == "fifo":
                    # First In First Out - evict oldest item by creation time
                    key_to_evict = min(
                        metadata_map.keys(),
                        key=lambda k: metadata_map[k].get("creation_time", 0),
                    )
                else:
                    # Default to LRU
                    key_to_evict = min(
                        metadata_map.keys(),
                        key=lambda k: metadata_map[k].get("last_access_time", 0),
                    )

                if key_to_evict:
                    self.delete(key_to_evict)
                    self.stats["evictions"] += 1
                    self._save_stats()

            except Exception:
                import logging

                logging.exception(
                    "Error during cache eviction. Falling back to deleting the first key."
                )
                if keys:
                    # If there's any error, just delete the first key
                    self.delete(keys[0])
                    self.stats["evictions"] += 1
                    self._save_stats()

    def _remove_expired_items(self) -> None:
        """
        Remove expired items from the cache.
        """
        with self.lock:
            current_time = time.time()

            # List all metadata files
            for filename in os.listdir(self.metadata_dir):
                if not filename.endswith(".json") or filename == "stats.json":
                    continue

                metadata_path = os.path.join(self.metadata_dir, filename)
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)

                    expiration_time = metadata.get("expiration_time")
                    if expiration_time is not None and current_time > expiration_time:
                        # Get the key and delete both value and metadata
                        key = metadata.get("key")
                        if key:
                            self.delete(key)
                            self.stats["evictions"] += 1
                            self._save_stats()
                except (IOError, json.JSONDecodeError):
                    # Remove corrupted metadata files
                    try:
                        os.remove(metadata_path)
                    except OSError:
                        pass
