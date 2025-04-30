"""Common caching utilities for the pAIssive Income project."""

from .cache_service import CacheService, cached, default_cache
from .cache_controls import (
    CacheControls,
    CachingPolicy,
    CacheCategory,
    cache_controls,
    register_namespace,
    get_ttl_for_namespace,
)

# Connect cache_controls with default_cache
default_cache.register_namespace_hook(cache_controls.is_caching_enabled)

__all__ = [
    "CacheService",
    "cached",
    "default_cache",
    "CacheControls",
    "CachingPolicy",
    "CacheCategory",
    "cache_controls",
    "register_namespace",
    "get_ttl_for_namespace",
]
