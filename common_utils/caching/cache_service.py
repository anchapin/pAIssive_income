"""
Cache service for the pAIssive Income project.

This module provides a unified caching interface that builds on top of the
existing AI models caching infrastructure to make caching available to
all parts of the project.
"""

import functools
import hashlib
import json
from typing import Any, Dict, Optional, Callable, Tuple, TypeVar

# Import the caching system from AI models module
from ai_models.caching import CacheManager

# Type variable for the decorator
T = TypeVar("T")


class CacheService:
    """
    Central cache service that provides a unified interface for caching operations.

    This class wraps the AI models CacheManager to provide a consistent interface
    for caching throughout the project. It adds functionality specific to the
    project's needs while maintaining compatibility with the underlying cache system.
    """

    def __init__(
        self,
        backend_type: str = "memory",
        ttl: int = 3600,
        max_size: Optional[int] = None,
        cache_dir: Optional[str] = None,
        db_path: Optional[str] = None,
        redis_url: Optional[str] = None,
    ):
        """
        Initialize a new cache service.

        Args:
            backend_type: Type of cache backend to use ('memory', 'disk', 'sqlite', 'redis')
            ttl: Default time-to-live in seconds (default: 1 hour)
            max_size: Maximum size of the cache (for memory backend)
            cache_dir: Directory for disk cache
            db_path: Path to SQLite database
            redis_url: URL for Redis connection
        """
        # Create a cache config
        from ai_models.caching import CacheConfig

        config = CacheConfig(
            enabled=True,
            backend=backend_type,
            ttl=ttl,
            max_size=max_size,
            backend_config={},
        )

        # Add backend-specific configuration
        if backend_type == "disk" and cache_dir:
            config.backend_config["disk"] = {"cache_dir": cache_dir}
        elif backend_type == "sqlite" and db_path:
            config.backend_config["sqlite"] = {"db_path": db_path}
        elif backend_type == "redis" and redis_url:
            # Parse redis URL
            import re

            match = re.match(
                r"redis://(?:([^:@]+)(?::([^@]+))?@)?([^:]+)(?::(\d+))?(?:/(\d+))?",
                redis_url,
            )
            if match:
                username, password, host, port, db = match.groups()
                config.backend_config["redis"] = {
                    "host": host or "localhost",
                    "port": int(port) if port else 6379,
                    "db": int(db) if db else 0,
                    "password": password,
                }

        # Create the cache manager with the specified config
        self.cache_manager = CacheManager(config=config)

        # Default TTL in seconds
        self.default_ttl = ttl

        # Optional hook to check if caching is enabled for a namespace
        self.is_namespace_enabled_hook: Optional[Callable[[str], bool]] = None

        # Keep stats on cache hits, misses, etc.
        self.stats: Dict[str, Dict[str, int]] = {}

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "default",
    ) -> bool:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (optional, uses default if not specified)
            namespace: Namespace for the cache key

        Returns:
            True if the value was set successfully, False otherwise
        """
        # Check if caching is enabled for this namespace
        if self.is_namespace_enabled_hook and not self.is_namespace_enabled_hook(
            namespace
        ):
            return False

        # Initialize stats for this namespace if not exists
        if namespace not in self.stats:
            self.stats[namespace] = {"hits": 0, "misses": 0, "sets": 0, "clears": 0}

        # Use the default TTL if not specified
        actual_ttl = ttl if ttl is not None else self.default_ttl

        # Cache the value using model_id as namespace
        success = self.cache_manager.set(
            model_id=namespace,
            operation="set",
            inputs=key,
            value={"value": value},
            ttl=actual_ttl,
        )

        # Update stats
        if success:
            self.stats[namespace]["sets"] += 1

        return success

    def get(self, key: str, namespace: str = "default") -> Any:
        """
        Get a value from the cache.

        Args:
            key: Cache key
            namespace: Namespace for the cache key

        Returns:
            The cached value, or None if not found
        """
        # Check if caching is enabled for this namespace
        if self.is_namespace_enabled_hook and not self.is_namespace_enabled_hook(
            namespace
        ):
            return None

        # Initialize stats for this namespace if not exists
        if namespace not in self.stats:
            self.stats[namespace] = {"hits": 0, "misses": 0, "sets": 0, "clears": 0}

        # Get the value from the cache
        # Use the same operation ('set') as in the set method to ensure we're looking up the correct key
        result = self.cache_manager.get(model_id=namespace, operation="set", inputs=key)

        # Extract the value from the result
        value = result.get("value") if result else None

        # Update stats
        if value is not None:
            self.stats[namespace]["hits"] += 1
        else:
            self.stats[namespace]["misses"] += 1

        return value

    def delete(self, key: str, namespace: str = "default") -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key
            namespace: Namespace for the cache key

        Returns:
            True if the value was deleted, False otherwise
        """
        # Use the same operation ('set') as in the set method to ensure we're deleting the correct key
        return self.cache_manager.delete(
            model_id=namespace, operation="set", inputs=key
        )

    def clear(self, namespace: str = "default") -> bool:
        """
        Clear all values for a namespace.

        Args:
            namespace: Namespace to clear

        Returns:
            True if the namespace was cleared, False otherwise
        """
        # Initialize stats for this namespace if not exists
        if namespace not in self.stats:
            self.stats[namespace] = {"hits": 0, "misses": 0, "sets": 0, "clears": 0}

        # Use the CacheManager's clear_namespace method to clear only keys for this namespace
        # This avoids clearing the entire cache when only one namespace needs to be cleared
        success = self.cache_manager.clear_namespace(namespace)

        # Update stats
        if success:
            self.stats[namespace]["clears"] += 1

        return success

    def clear_all(self) -> bool:
        """
        Clear all values in the cache.

        Returns:
            True if the cache was cleared, False otherwise
        """
        success = self.cache_manager.clear()

        # Reset stats
        if success:
            self.stats = {}

        return success

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about cache usage.

        Returns:
            Dictionary containing cache statistics
        """
        # Calculate hit rates and add to stats
        result = {}
        for namespace, ns_stats in self.stats.items():
            total_gets = ns_stats["hits"] + ns_stats["misses"]
            hit_rate = ns_stats["hits"] / total_gets if total_gets > 0 else 0

            result[namespace] = {
                **ns_stats,
                "hit_rate": hit_rate,
                "total_gets": total_gets,
            }

        return result

    def register_namespace_hook(self, hook: Callable[[str], bool]) -> None:
        """
        Register a hook to check if a namespace is enabled.

        Args:
            hook: Function that takes a namespace string and returns a boolean
        """
        self.is_namespace_enabled_hook = hook

    def set_default_ttl(self, ttl: int) -> None:
        """
        Set the default TTL for cache entries.

        Args:
            ttl: Time-to-live in seconds
        """
        self.default_ttl = ttl


def _generate_cache_key(func: Callable, args: Tuple, kwargs: Dict[str, Any]) -> str:
    """
    Generate a cache key for a function call.

    Args:
        func: The function being called
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        A unique string key for the function call
    """
    # Get the function's module and name
    module = func.__module__
    name = func.__qualname__

    # Create a representation of the arguments
    arg_dict = {"args": args, "kwargs": kwargs}

    # Convert to a string and hash
    arg_str = json.dumps(arg_dict, sort_keys=True, default=str)
    key = f"{module}.{name}:{hashlib.md5(arg_str.encode()).hexdigest()}"

    return key


def cached(
    ttl: Optional[int] = None,
    namespace: Optional[str] = None,
    key_generator: Optional[Callable[[Callable, Tuple, Dict[str, Any]], str]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to cache function return values.

    Args:
        ttl: Time-to-live in seconds (optional)
        namespace: Cache namespace (optional, defaults to function's module)
        key_generator: Custom function to generate cache keys (optional)

    Returns:
        Decorated function that uses caching
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Skip caching if force_refresh is True
            force_refresh = kwargs.pop("force_refresh", False)

            # Get the cache namespace
            cache_ns = namespace
            if cache_ns is None:
                cache_ns = func.__module__

            # Generate the cache key
            if key_generator:
                cache_key = key_generator(func, args, kwargs)
            else:
                cache_key = _generate_cache_key(func, args, kwargs)

            # Try to get from cache first
            if not force_refresh:
                cached_result = default_cache.get(cache_key, namespace=cache_ns)
                if cached_result is not None:
                    return cached_result

            # Call the original function
            result = func(*args, **kwargs)

            # Cache the result
            default_cache.set(cache_key, result, ttl=ttl, namespace=cache_ns)

            return result

        return wrapper

    return decorator


# Create a default instance for use throughout the application
default_cache = CacheService()
