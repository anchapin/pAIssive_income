"""
Base cache backend for the model cache system.

This module provides the base interface for cache backends.
"""

import abc
from typing import Dict, Any, Optional, List


class CacheBackend(abc.ABC):
    """
    Base class for cache backends.
    """

    @abc.abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: Cache key

        Returns:
            True if the key exists, False otherwise
        """
        pass

    @abc.abstractmethod
    def clear(self) -> bool:
        """
        Clear all values from the cache.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_size(self) -> int:
        """
        Get the size of the cache.

        Returns:
            Number of items in the cache
        """
        pass

    @abc.abstractmethod
    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all keys in the cache.

        Args:
            pattern: Optional pattern to filter keys

        Returns:
            List of keys
        """
        pass

    @abc.abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.

        Returns:
            Dictionary with cache statistics
        """
        pass

    @abc.abstractmethod
    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get the time to live for a key.

        Args:
            key: Cache key

        Returns:
            Time to live in seconds or None if no expiration
        """
        pass

    @abc.abstractmethod
    def set_ttl(self, key: str, ttl: int) -> bool:
        """
        Set the time to live for a key.

        Args:
            key: Cache key
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        pass
