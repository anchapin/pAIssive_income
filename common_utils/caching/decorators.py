"""
Cache decorator module for the pAIssive Income project.

This module provides decorators for easy cache integration into functions and methods.
"""

import functools
import logging
import time
from typing import Any, Callable, Optional

from .cache_service import CacheService, get_default_cache_service
from .cache_versioning import generate_versioned_key

# Set up logging
logger = logging.getLogger(__name__)


def cached(
    namespace: str = None,
    ttl: Optional[int] = None,
    condition: Optional[Callable] = None,
    key_generator: Optional[Callable] = None,
    version_with_code: bool = True,
    cache_service: Optional[CacheService] = None,
) -> Callable:
    """
    Decorator to cache function results with intelligent versioning.

    Args:
        namespace: Cache namespace (defaults to function module and name)
        ttl: Time-to-live in seconds (None for infinite)
        condition: Function that determines if result should be cached
        key_generator: Custom function to generate cache keys
        version_with_code: Whether to include function code in version
        cache_service: Cache service to use (uses default if not provided)

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        # Generate default namespace from function if not provided
        nonlocal namespace
        if namespace is None:
            namespace = f"{func.__module__}.{func.__qualname__}"

        # Get cache service
        nonlocal cache_service
        if cache_service is None:
            cache_service = get_default_cache_service()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Check if we should use cache based on condition
            if condition is not None and not condition(*args, **kwargs):
                return func(*args, **kwargs)

            # Generate cache key
            if key_generator is not None:
                base_key = key_generator(func, args, kwargs)
                cache_key = generate_versioned_key(
                    func,
                    args,
                    kwargs,
                    namespace,
                    include_func_version=version_with_code,
                    base_key=base_key,
                )
            else:
                cache_key = generate_versioned_key(
                    func,
                    args,
                    kwargs,
                    namespace,
                    include_func_version=version_with_code,
                )

            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__qualname__}")
                return cached_result

            # Cache miss - execute function
            logger.debug(f"Cache miss for {func.__qualname__}")
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Store in cache
            cache_service.set(cache_key, result, ttl=ttl)

            # Log caching metrics
            logger.debug(
                f"Cached result for {func.__qualname__} " f"(execution time: {execution_time:.3f}s)"
            )

            return result

        # Add cache control methods to the wrapped function
        wrapper.clear_cache = lambda: cache_service.clear_namespace(namespace)
        wrapper.get_namespace = lambda: namespace
        wrapper.invalidate_cache = lambda *a, **kw: cache_service.delete(
            generate_versioned_key(func, a, kw, namespace, version_with_code)
        )

        return wrapper

    return decorator


def method_cached(
    namespace: Optional[str] = None,
    ttl: Optional[int] = None,
    condition: Optional[Callable] = None,
    key_generator: Optional[Callable] = None,
    version_with_code: bool = True,
    instance_aware: bool = True,
    cache_service: Optional[CacheService] = None,
) -> Callable:
    """
    Decorator specifically for caching class methods.

    This variant is aware of 'self' and can optionally incorporate
    the instance identity into the cache key.

    Args:
        namespace: Cache namespace
        ttl: Time-to-live in seconds (None for infinite)
        condition: Function that determines if result should be cached
        key_generator: Custom function to generate cache keys
        version_with_code: Whether to include method code in version
        instance_aware: Whether to include instance identity in cache key
        cache_service: Cache service to use (uses default if not provided)

    Returns:
        Decorated method
    """

    def decorator(method: Callable) -> Callable:
        # Generate default namespace from method if not provided
        nonlocal namespace
        if namespace is None:
            namespace = f"{method.__module__}.{method.__qualname__}"

        # Get cache service
        nonlocal cache_service
        if cache_service is None:
            cache_service = get_default_cache_service()

        @functools.wraps(method)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            # Check if we should use cache based on condition
            if condition is not None and not condition(self, *args, **kwargs):
                return method(self, *args, **kwargs)

            # Add instance info to namespace if instance_aware
            effective_namespace = namespace
            if instance_aware:
                # Use object id or custom identifier if available
                instance_id = getattr(self, "cache_id", id(self))
                effective_namespace = f"{namespace}.instance_{instance_id}"

            # Generate cache key
            if key_generator is not None:
                base_key = key_generator(method, (self,) + args, kwargs)
                cache_key = generate_versioned_key(
                    method,
                    args,
                    kwargs,
                    effective_namespace,
                    include_func_version=version_with_code,
                    base_key=base_key,
                )
            else:
                cache_key = generate_versioned_key(
                    method,
                    args,
                    kwargs,
                    effective_namespace,
                    include_func_version=version_with_code,
                )

            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {method.__qualname__}")
                return cached_result

            # Cache miss - execute method
            logger.debug(f"Cache miss for {method.__qualname__}")
            start_time = time.time()
            result = method(self, *args, **kwargs)
            execution_time = time.time() - start_time

            # Store in cache
            cache_service.set(cache_key, result, ttl=ttl)

            # Log caching metrics
            logger.debug(
                f"Cached result for {method.__qualname__} "
                f"(execution time: {execution_time:.3f}s)"
            )

            return result

        # Add cache control methods to the wrapped function
        wrapper.clear_cache = lambda slf=None: cache_service.clear_namespace(
            f"{namespace}.instance_{id(slf)}" if slf and instance_aware else namespace
        )
        wrapper.get_namespace = lambda slf=None: (
            f"{namespace}.instance_{id(slf)}" if slf and instance_aware else namespace
        )
        wrapper.invalidate_cache = lambda slf=None, *a, **kw: cache_service.delete(
            generate_versioned_key(
                method,
                a,
                kw,
                (f"{namespace}.instance_{id(slf)}" if slf and instance_aware else namespace),
                version_with_code,
            )
        )

        return wrapper

    return decorator


def cache_result(func: Optional[Callable] = None, **kwargs: Any) -> Callable:
    """
    Simple cached decorator that can be used with or without arguments.

    This is a convenience wrapper around the main cached decorator.

    Examples:
        @cache_result
        def my_func(x):
            return x * 2

        @cache_result(ttl=300)
        def another_func(x):
            return x + 1

    Args:
        func: Function to decorate when used without arguments
        **kwargs: Arguments to pass to the cached decorator

    Returns:
        Decorated function or decorator function
    """
    if func is None:
        # Called with arguments: @cache_result(...)
        return cached(**kwargs)
    else:
        # Called without arguments: @cache_result
        return cached()(func)
