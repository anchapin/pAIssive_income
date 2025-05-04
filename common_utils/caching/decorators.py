"""
"""
Cache decorator module for the pAIssive Income project.
Cache decorator module for the pAIssive Income project.


This module provides decorators for easy cache integration into functions and methods.
This module provides decorators for easy cache integration into functions and methods.
"""
"""




import functools
import functools
import logging
import logging
import time
import time
from typing import Any, Callable, Optional
from typing import Any, Callable, Optional


from .cache_service import CacheService, get_default_cache_service
from .cache_service import CacheService, get_default_cache_service
from .cache_versioning import generate_versioned_key
from .cache_versioning import generate_versioned_key


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




def cached(
def cached(
namespace: str = None,
namespace: str = None,
ttl: Optional[int] = None,
ttl: Optional[int] = None,
condition: Optional[Callable] = None,
condition: Optional[Callable] = None,
key_generator: Optional[Callable] = None,
key_generator: Optional[Callable] = None,
version_with_code: bool = True,
version_with_code: bool = True,
cache_service: Optional[CacheService] = None,
cache_service: Optional[CacheService] = None,
) -> Callable:
    ) -> Callable:
    """
    """
    Decorator to cache function results with intelligent versioning.
    Decorator to cache function results with intelligent versioning.


    Args:
    Args:
    namespace: Cache namespace (defaults to function module and name)
    namespace: Cache namespace (defaults to function module and name)
    ttl: Time-to-live in seconds (None for infinite)
    ttl: Time-to-live in seconds (None for infinite)
    condition: Function that determines if result should be cached
    condition: Function that determines if result should be cached
    key_generator: Custom function to generate cache keys
    key_generator: Custom function to generate cache keys
    version_with_code: Whether to include function code in version
    version_with_code: Whether to include function code in version
    cache_service: Cache service to use (uses default if not provided)
    cache_service: Cache service to use (uses default if not provided)


    Returns:
    Returns:
    Decorated function
    Decorated function
    """
    """


    def decorator(func: Callable) -> Callable:
    def decorator(func: Callable) -> Callable:
    # Generate default namespace from function if not provided
    # Generate default namespace from function if not provided
    nonlocal namespace
    nonlocal namespace
    if namespace is None:
    if namespace is None:
    namespace = f"{func.__module__}.{func.__qualname__}"
    namespace = f"{func.__module__}.{func.__qualname__}"


    # Get cache service
    # Get cache service
    nonlocal cache_service
    nonlocal cache_service
    if cache_service is None:
    if cache_service is None:
    cache_service = get_default_cache_service()
    cache_service = get_default_cache_service()


    @functools.wraps(func)
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
    # Check if we should use cache based on condition
    # Check if we should use cache based on condition
    if condition is not None and not condition(*args, **kwargs):
    if condition is not None and not condition(*args, **kwargs):
    return func(*args, **kwargs)
    return func(*args, **kwargs)


    # Generate cache key
    # Generate cache key
    if key_generator is not None:
    if key_generator is not None:
    base_key = key_generator(func, args, kwargs)
    base_key = key_generator(func, args, kwargs)
    cache_key = generate_versioned_key(
    cache_key = generate_versioned_key(
    func,
    func,
    args,
    args,
    kwargs,
    kwargs,
    namespace,
    namespace,
    include_func_version=version_with_code,
    include_func_version=version_with_code,
    base_key=base_key,
    base_key=base_key,
    )
    )
    else:
    else:
    cache_key = generate_versioned_key(
    cache_key = generate_versioned_key(
    func,
    func,
    args,
    args,
    kwargs,
    kwargs,
    namespace,
    namespace,
    include_func_version=version_with_code,
    include_func_version=version_with_code,
    )
    )


    # Try to get from cache
    # Try to get from cache
    cached_result = cache_service.get(cache_key)
    cached_result = cache_service.get(cache_key)
    if cached_result is not None:
    if cached_result is not None:
    logger.debug(f"Cache hit for {func.__qualname__}")
    logger.debug(f"Cache hit for {func.__qualname__}")
    return cached_result
    return cached_result


    # Cache miss - execute function
    # Cache miss - execute function
    logger.debug(f"Cache miss for {func.__qualname__}")
    logger.debug(f"Cache miss for {func.__qualname__}")
    start_time = time.time()
    start_time = time.time()
    result = func(*args, **kwargs)
    result = func(*args, **kwargs)
    execution_time = time.time() - start_time
    execution_time = time.time() - start_time


    # Store in cache
    # Store in cache
    cache_service.set(cache_key, result, ttl=ttl)
    cache_service.set(cache_key, result, ttl=ttl)


    # Log caching metrics
    # Log caching metrics
    logger.debug(
    logger.debug(
    f"Cached result for {func.__qualname__} "
    f"Cached result for {func.__qualname__} "
    f"(execution time: {execution_time:.3f}s)"
    f"(execution time: {execution_time:.3f}s)"
    )
    )


    return result
    return result


    # Add cache control methods to the wrapped function
    # Add cache control methods to the wrapped function
    wrapper.clear_cache = lambda: cache_service.clear_namespace(namespace)
    wrapper.clear_cache = lambda: cache_service.clear_namespace(namespace)
    wrapper.get_namespace = lambda: namespace
    wrapper.get_namespace = lambda: namespace
    wrapper.invalidate_cache = lambda *a, **kw: cache_service.delete(
    wrapper.invalidate_cache = lambda *a, **kw: cache_service.delete(
    generate_versioned_key(func, a, kw, namespace, version_with_code)
    generate_versioned_key(func, a, kw, namespace, version_with_code)
    )
    )


    return wrapper
    return wrapper


    return decorator
    return decorator




    def method_cached(
    def method_cached(
    namespace: Optional[str] = None,
    namespace: Optional[str] = None,
    ttl: Optional[int] = None,
    ttl: Optional[int] = None,
    condition: Optional[Callable] = None,
    condition: Optional[Callable] = None,
    key_generator: Optional[Callable] = None,
    key_generator: Optional[Callable] = None,
    version_with_code: bool = True,
    version_with_code: bool = True,
    instance_aware: bool = True,
    instance_aware: bool = True,
    cache_service: Optional[CacheService] = None,
    cache_service: Optional[CacheService] = None,
    ) -> Callable:
    ) -> Callable:
    """
    """
    Decorator specifically for caching class methods.
    Decorator specifically for caching class methods.


    This variant is aware of 'self' and can optionally incorporate
    This variant is aware of 'self' and can optionally incorporate
    the instance identity into the cache key.
    the instance identity into the cache key.


    Args:
    Args:
    namespace: Cache namespace
    namespace: Cache namespace
    ttl: Time-to-live in seconds (None for infinite)
    ttl: Time-to-live in seconds (None for infinite)
    condition: Function that determines if result should be cached
    condition: Function that determines if result should be cached
    key_generator: Custom function to generate cache keys
    key_generator: Custom function to generate cache keys
    version_with_code: Whether to include method code in version
    version_with_code: Whether to include method code in version
    instance_aware: Whether to include instance identity in cache key
    instance_aware: Whether to include instance identity in cache key
    cache_service: Cache service to use (uses default if not provided)
    cache_service: Cache service to use (uses default if not provided)


    Returns:
    Returns:
    Decorated method
    Decorated method
    """
    """


    def decorator(method: Callable) -> Callable:
    def decorator(method: Callable) -> Callable:
    # Generate default namespace from method if not provided
    # Generate default namespace from method if not provided
    nonlocal namespace
    nonlocal namespace
    if namespace is None:
    if namespace is None:
    namespace = f"{method.__module__}.{method.__qualname__}"
    namespace = f"{method.__module__}.{method.__qualname__}"


    # Get cache service
    # Get cache service
    nonlocal cache_service
    nonlocal cache_service
    if cache_service is None:
    if cache_service is None:
    cache_service = get_default_cache_service()
    cache_service = get_default_cache_service()


    @functools.wraps(method)
    @functools.wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
    # Check if we should use cache based on condition
    # Check if we should use cache based on condition
    if condition is not None and not condition(self, *args, **kwargs):
    if condition is not None and not condition(self, *args, **kwargs):
    return method(self, *args, **kwargs)
    return method(self, *args, **kwargs)


    # Add instance info to namespace if instance_aware
    # Add instance info to namespace if instance_aware
    effective_namespace = namespace
    effective_namespace = namespace
    if instance_aware:
    if instance_aware:
    # Use object id or custom identifier if available
    # Use object id or custom identifier if available
    instance_id = getattr(self, "cache_id", id(self))
    instance_id = getattr(self, "cache_id", id(self))
    effective_namespace = f"{namespace}.instance_{instance_id}"
    effective_namespace = f"{namespace}.instance_{instance_id}"


    # Generate cache key
    # Generate cache key
    if key_generator is not None:
    if key_generator is not None:
    base_key = key_generator(method, (self,) + args, kwargs)
    base_key = key_generator(method, (self,) + args, kwargs)
    cache_key = generate_versioned_key(
    cache_key = generate_versioned_key(
    method,
    method,
    args,
    args,
    kwargs,
    kwargs,
    effective_namespace,
    effective_namespace,
    include_func_version=version_with_code,
    include_func_version=version_with_code,
    base_key=base_key,
    base_key=base_key,
    )
    )
    else:
    else:
    cache_key = generate_versioned_key(
    cache_key = generate_versioned_key(
    method,
    method,
    args,
    args,
    kwargs,
    kwargs,
    effective_namespace,
    effective_namespace,
    include_func_version=version_with_code,
    include_func_version=version_with_code,
    )
    )


    # Try to get from cache
    # Try to get from cache
    cached_result = cache_service.get(cache_key)
    cached_result = cache_service.get(cache_key)
    if cached_result is not None:
    if cached_result is not None:
    logger.debug(f"Cache hit for {method.__qualname__}")
    logger.debug(f"Cache hit for {method.__qualname__}")
    return cached_result
    return cached_result


    # Cache miss - execute method
    # Cache miss - execute method
    logger.debug(f"Cache miss for {method.__qualname__}")
    logger.debug(f"Cache miss for {method.__qualname__}")
    start_time = time.time()
    start_time = time.time()
    result = method(self, *args, **kwargs)
    result = method(self, *args, **kwargs)
    execution_time = time.time() - start_time
    execution_time = time.time() - start_time


    # Store in cache
    # Store in cache
    cache_service.set(cache_key, result, ttl=ttl)
    cache_service.set(cache_key, result, ttl=ttl)


    # Log caching metrics
    # Log caching metrics
    logger.debug(
    logger.debug(
    f"Cached result for {method.__qualname__} "
    f"Cached result for {method.__qualname__} "
    f"(execution time: {execution_time:.3f}s)"
    f"(execution time: {execution_time:.3f}s)"
    )
    )


    return result
    return result


    # Add cache control methods to the wrapped function
    # Add cache control methods to the wrapped function
    wrapper.clear_cache = lambda slf=None: cache_service.clear_namespace(
    wrapper.clear_cache = lambda slf=None: cache_service.clear_namespace(
    f"{namespace}.instance_{id(slf)}" if slf and instance_aware else namespace
    f"{namespace}.instance_{id(slf)}" if slf and instance_aware else namespace
    )
    )
    wrapper.get_namespace = lambda slf=None: (
    wrapper.get_namespace = lambda slf=None: (
    f"{namespace}.instance_{id(slf)}" if slf and instance_aware else namespace
    f"{namespace}.instance_{id(slf)}" if slf and instance_aware else namespace
    )
    )
    wrapper.invalidate_cache = lambda slf=None, *a, **kw: cache_service.delete(
    wrapper.invalidate_cache = lambda slf=None, *a, **kw: cache_service.delete(
    generate_versioned_key(
    generate_versioned_key(
    method,
    method,
    a,
    a,
    kw,
    kw,
    (
    (
    f"{namespace}.instance_{id(slf)}"
    f"{namespace}.instance_{id(slf)}"
    if slf and instance_aware
    if slf and instance_aware
    else namespace
    else namespace
    ),
    ),
    version_with_code,
    version_with_code,
    )
    )
    )
    )


    return wrapper
    return wrapper


    return decorator
    return decorator




    def cache_result(func: Optional[Callable] = None, **kwargs: Any) -> Callable:
    def cache_result(func: Optional[Callable] = None, **kwargs: Any) -> Callable:
    """
    """
    Simple cached decorator that can be used with or without arguments.
    Simple cached decorator that can be used with or without arguments.


    This is a convenience wrapper around the main cached decorator.
    This is a convenience wrapper around the main cached decorator.


    Examples:
    Examples:
    @cache_result
    @cache_result
    def my_func(x):
    def my_func(x):
    return x * 2
    return x * 2


    @cache_result(ttl=300)
    @cache_result(ttl=300)
    def another_func(x):
    def another_func(x):
    return x + 1
    return x + 1


    Args:
    Args:
    func: Function to decorate when used without arguments
    func: Function to decorate when used without arguments
    **kwargs: Arguments to pass to the cached decorator
    **kwargs: Arguments to pass to the cached decorator


    Returns:
    Returns:
    Decorated function or decorator function
    Decorated function or decorator function
    """
    """
    if func is None:
    if func is None:
    # Called with arguments: @cache_result(...)
    # Called with arguments: @cache_result(...)
    return cached(**kwargs)
    return cached(**kwargs)
    else:
    else:
    # Called without arguments: @cache_result
    # Called without arguments: @cache_result
    return cached()(func)
    return cached()(func)