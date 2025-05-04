"""
"""
Cache service for the pAIssive Income project.
Cache service for the pAIssive Income project.


This module provides a unified caching interface that builds on top of the
This module provides a unified caching interface that builds on top of the
existing AI models caching infrastructure to make caching available to
existing AI models caching infrastructure to make caching available to
all parts of the project.
all parts of the project.
"""
"""


import functools
import functools
import hashlib
import hashlib
import json
import json
import time
import time
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar


from ai_models.caching import CacheConfig, CacheManager
from ai_models.caching import CacheConfig, CacheManager


config
config
import re
import re


# Import the caching system from AI models module
# Import the caching system from AI models module
# Type variable for the decorator
# Type variable for the decorator
T = TypeVar("T")
T = TypeVar("T")




class CacheService:
    class CacheService:
    """
    """
    Central cache service that provides a unified interface for caching operations.
    Central cache service that provides a unified interface for caching operations.


    This class wraps the AI models CacheManager to provide a consistent interface
    This class wraps the AI models CacheManager to provide a consistent interface
    for caching throughout the project. It adds functionality specific to the
    for caching throughout the project. It adds functionality specific to the
    project's needs while maintaining compatibility with the underlying cache system.
    project's needs while maintaining compatibility with the underlying cache system.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    backend_type: str = "memory",
    backend_type: str = "memory",
    ttl: int = 3600,
    ttl: int = 3600,
    max_size: Optional[int] = None,
    max_size: Optional[int] = None,
    cache_dir: Optional[str] = None,
    cache_dir: Optional[str] = None,
    db_path: Optional[str] = None,
    db_path: Optional[str] = None,
    redis_url: Optional[str] = None,
    redis_url: Optional[str] = None,
    ):
    ):
    """
    """
    Initialize a new cache service.
    Initialize a new cache service.


    Args:
    Args:
    backend_type: Type of cache backend to use ('memory', 'disk', 'sqlite', 'redis')
    backend_type: Type of cache backend to use ('memory', 'disk', 'sqlite', 'redis')
    ttl: Default time-to-live in seconds (default: 1 hour)
    ttl: Default time-to-live in seconds (default: 1 hour)
    max_size: Maximum size of the cache (for memory backend)
    max_size: Maximum size of the cache (for memory backend)
    cache_dir: Directory for disk cache
    cache_dir: Directory for disk cache
    db_path: Path to SQLite database
    db_path: Path to SQLite database
    redis_url: URL for Redis connection
    redis_url: URL for Redis connection
    """
    """
    # Create a cache config
    # Create a cache config
    = CacheConfig(
    = CacheConfig(
    enabled=True,
    enabled=True,
    backend=backend_type,
    backend=backend_type,
    ttl=ttl,
    ttl=ttl,
    max_size=max_size,
    max_size=max_size,
    backend_config={},
    backend_config={},
    )
    )


    # Add backend-specific configuration
    # Add backend-specific configuration
    if backend_type == "disk" and cache_dir:
    if backend_type == "disk" and cache_dir:
    config.backend_config["disk"] = {"cache_dir": cache_dir}
    config.backend_config["disk"] = {"cache_dir": cache_dir}
    elif backend_type == "sqlite" and db_path:
    elif backend_type == "sqlite" and db_path:
    config.backend_config["sqlite"] = {"db_path": db_path}
    config.backend_config["sqlite"] = {"db_path": db_path}
    elif backend_type == "redis" and redis_url:
    elif backend_type == "redis" and redis_url:
    # Parse redis URL
    # Parse redis URL




    match = re.match(
    match = re.match(
    r"redis://(?:([^:@]+)(?::([^@]+))?@)?([^:]+)(?::(\d+))?(?:/(\d+))?",
    r"redis://(?:([^:@]+)(?::([^@]+))?@)?([^:]+)(?::(\d+))?(?:/(\d+))?",
    redis_url,
    redis_url,
    )
    )
    if match:
    if match:
    username, password, host, port, db = match.groups()
    username, password, host, port, db = match.groups()
    config.backend_config["redis"] = {
    config.backend_config["redis"] = {
    "host": host or "localhost",
    "host": host or "localhost",
    "port": int(port) if port else 6379,
    "port": int(port) if port else 6379,
    "db": int(db) if db else 0,
    "db": int(db) if db else 0,
    "password": password,
    "password": password,
    }
    }


    # Create the cache manager with the specified config
    # Create the cache manager with the specified config
    self.cache_manager = CacheManager(config=config)
    self.cache_manager = CacheManager(config=config)


    # Default TTL in seconds
    # Default TTL in seconds
    self.default_ttl = ttl
    self.default_ttl = ttl


    # Optional hook to check if caching is enabled for a namespace
    # Optional hook to check if caching is enabled for a namespace
    self.is_namespace_enabled_hook: Optional[Callable[[str], bool]] = None
    self.is_namespace_enabled_hook: Optional[Callable[[str], bool]] = None


    # Keep stats on cache hits, misses, etc.
    # Keep stats on cache hits, misses, etc.
    self.stats: Dict[str, Dict[str, int]] = {}
    self.stats: Dict[str, Dict[str, int]] = {}


    def set(
    def set(
    self,
    self,
    key: str,
    key: str,
    value: Any,
    value: Any,
    ttl: Optional[int] = None,
    ttl: Optional[int] = None,
    namespace: str = "default",
    namespace: str = "default",
    ) -> bool:
    ) -> bool:
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
    ttl: Time-to-live in seconds (optional, uses default if not specified)
    ttl: Time-to-live in seconds (optional, uses default if not specified)
    namespace: Namespace for the cache key
    namespace: Namespace for the cache key


    Returns:
    Returns:
    True if the value was set successfully, False otherwise
    True if the value was set successfully, False otherwise
    """
    """
    # Check if caching is enabled for this namespace
    # Check if caching is enabled for this namespace
    if self.is_namespace_enabled_hook and not self.is_namespace_enabled_hook(
    if self.is_namespace_enabled_hook and not self.is_namespace_enabled_hook(
    namespace
    namespace
    ):
    ):
    return False
    return False


    # Initialize stats for this namespace if not exists
    # Initialize stats for this namespace if not exists
    if namespace not in self.stats:
    if namespace not in self.stats:
    self.stats[namespace] = {"hits": 0, "misses": 0, "sets": 0, "clears": 0}
    self.stats[namespace] = {"hits": 0, "misses": 0, "sets": 0, "clears": 0}


    # Use the default TTL if not specified
    # Use the default TTL if not specified
    actual_ttl = ttl if ttl is not None else self.default_ttl
    actual_ttl = ttl if ttl is not None else self.default_ttl


    # Cache the value using model_id as namespace
    # Cache the value using model_id as namespace
    success = self.cache_manager.set(
    success = self.cache_manager.set(
    model_id=namespace,
    model_id=namespace,
    operation="set",
    operation="set",
    inputs=key,
    inputs=key,
    value={"value": value},
    value={"value": value},
    ttl=actual_ttl,
    ttl=actual_ttl,
    )
    )


    # Update stats
    # Update stats
    if success:
    if success:
    self.stats[namespace]["sets"] += 1
    self.stats[namespace]["sets"] += 1


    return success
    return success


    def get(self, key: str, namespace: str = "default") -> Any:
    def get(self, key: str, namespace: str = "default") -> Any:
    """
    """
    Get a value from the cache.
    Get a value from the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key
    namespace: Namespace for the cache key
    namespace: Namespace for the cache key


    Returns:
    Returns:
    The cached value, or None if not found
    The cached value, or None if not found
    """
    """
    # Check if caching is enabled for this namespace
    # Check if caching is enabled for this namespace
    if self.is_namespace_enabled_hook and not self.is_namespace_enabled_hook(
    if self.is_namespace_enabled_hook and not self.is_namespace_enabled_hook(
    namespace
    namespace
    ):
    ):
    return None
    return None


    # Initialize stats for this namespace if not exists
    # Initialize stats for this namespace if not exists
    if namespace not in self.stats:
    if namespace not in self.stats:
    self.stats[namespace] = {"hits": 0, "misses": 0, "sets": 0, "clears": 0}
    self.stats[namespace] = {"hits": 0, "misses": 0, "sets": 0, "clears": 0}


    # Get the value from the cache
    # Get the value from the cache
    # Use the same operation ('set') as in the set method to ensure we're looking up the correct key
    # Use the same operation ('set') as in the set method to ensure we're looking up the correct key
    result = self.cache_manager.get(model_id=namespace, operation="set", inputs=key)
    result = self.cache_manager.get(model_id=namespace, operation="set", inputs=key)


    # Extract the value from the result
    # Extract the value from the result
    value = result.get("value") if result else None
    value = result.get("value") if result else None


    # Update stats
    # Update stats
    if value is not None:
    if value is not None:
    self.stats[namespace]["hits"] += 1
    self.stats[namespace]["hits"] += 1
    else:
    else:
    self.stats[namespace]["misses"] += 1
    self.stats[namespace]["misses"] += 1


    return value
    return value


    def delete(self, key: str, namespace: str = "default") -> bool:
    def delete(self, key: str, namespace: str = "default") -> bool:
    """
    """
    Delete a value from the cache.
    Delete a value from the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key
    namespace: Namespace for the cache key
    namespace: Namespace for the cache key


    Returns:
    Returns:
    True if the value was deleted, False otherwise
    True if the value was deleted, False otherwise
    """
    """
    # Use the same operation ('set') as in the set method to ensure we're deleting the correct key
    # Use the same operation ('set') as in the set method to ensure we're deleting the correct key
    return self.cache_manager.delete(
    return self.cache_manager.delete(
    model_id=namespace, operation="set", inputs=key
    model_id=namespace, operation="set", inputs=key
    )
    )


    def clear(self, namespace: str = "default") -> bool:
    def clear(self, namespace: str = "default") -> bool:
    """
    """
    Clear all values for a namespace.
    Clear all values for a namespace.


    Args:
    Args:
    namespace: Namespace to clear
    namespace: Namespace to clear


    Returns:
    Returns:
    True if the namespace was cleared, False otherwise
    True if the namespace was cleared, False otherwise
    """
    """
    # Initialize stats for this namespace if not exists
    # Initialize stats for this namespace if not exists
    if namespace not in self.stats:
    if namespace not in self.stats:
    self.stats[namespace] = {"hits": 0, "misses": 0, "sets": 0, "clears": 0}
    self.stats[namespace] = {"hits": 0, "misses": 0, "sets": 0, "clears": 0}


    # Use the CacheManager's clear_namespace method to clear only keys for this namespace
    # Use the CacheManager's clear_namespace method to clear only keys for this namespace
    # This avoids clearing the entire cache when only one namespace needs to be cleared
    # This avoids clearing the entire cache when only one namespace needs to be cleared
    success = self.cache_manager.clear_namespace(namespace)
    success = self.cache_manager.clear_namespace(namespace)


    # Update stats
    # Update stats
    if success:
    if success:
    self.stats[namespace]["clears"] += 1
    self.stats[namespace]["clears"] += 1


    return success
    return success


    def clear_all(self) -> bool:
    def clear_all(self) -> bool:
    """
    """
    Clear all values in the cache.
    Clear all values in the cache.


    Returns:
    Returns:
    True if the cache was cleared, False otherwise
    True if the cache was cleared, False otherwise
    """
    """
    success = self.cache_manager.clear()
    success = self.cache_manager.clear()


    # Reset stats
    # Reset stats
    if success:
    if success:
    self.stats = {}
    self.stats = {}


    return success
    return success


    def get_stats(self) -> Dict[str, Any]:
    def get_stats(self) -> Dict[str, Any]:
    """
    """
    Get statistics about cache usage.
    Get statistics about cache usage.


    Returns:
    Returns:
    Dictionary containing cache statistics
    Dictionary containing cache statistics
    """
    """
    # Calculate hit rates and add to stats
    # Calculate hit rates and add to stats
    result = {}
    result = {}
    for namespace, ns_stats in self.stats.items():
    for namespace, ns_stats in self.stats.items():
    total_gets = ns_stats["hits"] + ns_stats["misses"]
    total_gets = ns_stats["hits"] + ns_stats["misses"]
    hit_rate = ns_stats["hits"] / total_gets if total_gets > 0 else 0
    hit_rate = ns_stats["hits"] / total_gets if total_gets > 0 else 0


    result[namespace] = {
    result[namespace] = {
    **ns_stats,
    **ns_stats,
    "hit_rate": hit_rate,
    "hit_rate": hit_rate,
    "total_gets": total_gets,
    "total_gets": total_gets,
    }
    }


    return result
    return result


    def register_namespace_hook(self, hook: Callable[[str], bool]) -> None:
    def register_namespace_hook(self, hook: Callable[[str], bool]) -> None:
    """
    """
    Register a hook to check if a namespace is enabled.
    Register a hook to check if a namespace is enabled.


    Args:
    Args:
    hook: Function that takes a namespace string and returns a boolean
    hook: Function that takes a namespace string and returns a boolean
    """
    """
    self.is_namespace_enabled_hook = hook
    self.is_namespace_enabled_hook = hook


    def set_default_ttl(self, ttl: int) -> None:
    def set_default_ttl(self, ttl: int) -> None:
    """
    """
    Set the default TTL for cache entries.
    Set the default TTL for cache entries.


    Args:
    Args:
    ttl: Time-to-live in seconds
    ttl: Time-to-live in seconds
    """
    """
    self.default_ttl = ttl
    self.default_ttl = ttl




    def _generate_cache_key(func: Callable, args: Tuple, kwargs: Dict[str, Any]) -> str:
    def _generate_cache_key(func: Callable, args: Tuple, kwargs: Dict[str, Any]) -> str:
    """
    """
    Generate a cache key for a function call.
    Generate a cache key for a function call.


    Args:
    Args:
    func: The function being called
    func: The function being called
    args: Positional arguments
    args: Positional arguments
    kwargs: Keyword arguments
    kwargs: Keyword arguments


    Returns:
    Returns:
    A unique string key for the function call
    A unique string key for the function call
    """
    """
    # Get the function's module and name
    # Get the function's module and name
    module = func.__module__
    module = func.__module__
    name = func.__qualname__
    name = func.__qualname__


    # Create a representation of the arguments
    # Create a representation of the arguments
    arg_dict = {"args": args, "kwargs": kwargs}
    arg_dict = {"args": args, "kwargs": kwargs}


    # Convert to a string and hash
    # Convert to a string and hash
    arg_str = json.dumps(arg_dict, sort_keys=True, default=str)
    arg_str = json.dumps(arg_dict, sort_keys=True, default=str)
    key = f"{module}.{name}:{hashlib.md5(arg_str.encode()).hexdigest()}"
    key = f"{module}.{name}:{hashlib.md5(arg_str.encode()).hexdigest()}"


    return key
    return key




    def cached(
    def cached(
    ttl: Optional[int] = None,
    ttl: Optional[int] = None,
    namespace: Optional[str] = None,
    namespace: Optional[str] = None,
    key_generator: Optional[Callable[[Callable, Tuple, Dict[str, Any]], str]] = None,
    key_generator: Optional[Callable[[Callable, Tuple, Dict[str, Any]], str]] = None,
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    """
    Decorator to cache function return values.
    Decorator to cache function return values.


    Args:
    Args:
    ttl: Time-to-live in seconds (optional)
    ttl: Time-to-live in seconds (optional)
    namespace: Cache namespace (optional, defaults to function's module)
    namespace: Cache namespace (optional, defaults to function's module)
    key_generator: Custom function to generate cache keys (optional)
    key_generator: Custom function to generate cache keys (optional)


    Returns:
    Returns:
    Decorated function that uses caching
    Decorated function that uses caching
    """
    """


    def decorator(func: Callable[..., T]) -> Callable[..., T]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(func)
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
    def wrapper(*args: Any, **kwargs: Any) -> T:
    # Skip caching if force_refresh is True
    # Skip caching if force_refresh is True
    force_refresh = kwargs.pop("force_refresh", False)
    force_refresh = kwargs.pop("force_refresh", False)


    # Get the cache namespace
    # Get the cache namespace
    cache_ns = namespace
    cache_ns = namespace
    if cache_ns is None:
    if cache_ns is None:
    cache_ns = func.__module__
    cache_ns = func.__module__


    # Generate the cache key
    # Generate the cache key
    if key_generator:
    if key_generator:
    cache_key = key_generator(func, args, kwargs)
    cache_key = key_generator(func, args, kwargs)
    else:
    else:
    cache_key = _generate_cache_key(func, args, kwargs)
    cache_key = _generate_cache_key(func, args, kwargs)


    # Try to get from cache first
    # Try to get from cache first
    if not force_refresh:
    if not force_refresh:
    cached_result = default_cache.get(cache_key, namespace=cache_ns)
    cached_result = default_cache.get(cache_key, namespace=cache_ns)
    if cached_result is not None:
    if cached_result is not None:
    return cached_result
    return cached_result


    # Call the original function
    # Call the original function
    result = func(*args, **kwargs)
    result = func(*args, **kwargs)


    # Cache the result
    # Cache the result
    default_cache.set(cache_key, result, ttl=ttl, namespace=cache_ns)
    default_cache.set(cache_key, result, ttl=ttl, namespace=cache_ns)


    return result
    return result


    return wrapper
    return wrapper


    return decorator
    return decorator




    # Create a default instance for use throughout the application
    # Create a default instance for use throughout the application
    default_cache = CacheService()
    default_cache = CacheService()