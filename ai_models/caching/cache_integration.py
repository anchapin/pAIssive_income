"""
Cache integration for the AI models module.

This module provides integration between the AI models module and the
centralized caching service from common_utils. This allows the AI models
to use the same caching infrastructure as the rest of the project.
"""

import functools
import inspect
import logging
from typing import Callable, Optional

from common_utils.caching import CacheService, default_cache

# Set up logging
logger = logging.getLogger(__name__)


def get_cache_service() -> CacheService:
    """
    Get the cache service singleton.

    Returns:
        Cache service instance
    """
    return default_cache


def cache_model_result(
    func: Optional[Callable] = None,
    ttl: Optional[int] = None,
    model_id_arg: str = "model_id",
):
    """
    Decorator for caching AI model results.

    This decorator automatically caches the results of model operations
    using the centralized caching service. It extracts the model_id and
    inputs from the function arguments.

    Example:
        @cache_model_result(ttl=3600)
        def generate_text(model_id, prompt, parameters=None):
            # Call the model to generate text
            return model.generate(prompt, parameters)

    Args:
        func: Function to decorate
        ttl: Optional time - to - live in seconds
        model_id_arg: Name of the model ID argument in the function

    Returns:
        Decorated function
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Get the cache service
            cache = get_cache_service()

            # Check if caching is enabled
            if not cache.is_enabled():
                return f(*args, **kwargs)

            # Get function signature to map positional args to names
            sig = inspect.signature(f)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            all_args = bound_args.arguments

            # Extract model_id from args
            if model_id_arg not in all_args:
                logger.warning(
                    f"Cannot cache result: '{model_id_arg}' not found in function" \
                     + "arguments"
                )
                return f(*args, **kwargs)

            model_id = all_args[model_id_arg]

            # Determine the operation type from the function name
            operation = f.__name__

            # Extract inputs from args - typically the first non - model_id argument
            inputs = None
            parameters = {}

            for arg_name, arg_value in all_args.items():
                if arg_name == model_id_arg:
                    continue

                if inputs is None:
                    # The first non - model_id argument is considered the primary input
                    inputs = arg_value
                else:
                    # All other arguments are considered parameters
                    parameters[arg_name] = arg_value

            # Check if result is already cached
            cached_result = cache.get_model_output(model_id, operation, inputs, 
                parameters)

            if cached_result is not None:
                logger.debug(f"Cache hit for {operation} with model {model_id}")
                return cached_result

            # Call the original function
            logger.debug(f"Cache miss for {operation} with model {model_id}")
            result = f(*args, **kwargs)

            # Cache the result
            cache.cache_model_output(model_id, operation, inputs, result, parameters, 
                ttl)

            return result

        return wrapper

    # Handle both @cache_model_result and @cache_model_result()
    if func is not None:
        return decorator(func)
    return decorator


def invalidate_model_cache(model_id: str, operation: Optional[str] = None) -> bool:
    """
    Invalidate cache for a specific model or operation.

    Args:
        model_id: ID of the model
        operation: Optional operation to invalidate. If None, 
            all operations are invalidated.

    Returns:
        True if successful, False otherwise
    """
    # This is a simplified implementation that just clears the entire cache
    # A more sophisticated implementation would selectively clear cache entries
    cache = get_cache_service()
    return cache.clear()
