"""Common caching utilities for the pAIssive Income project."""

from .cache_controls import (
    CacheCategory,
    CacheControls,
    CachingPolicy,
    cache_controls,
    get_ttl_for_namespace,
    register_namespace,
)
from .cache_service import CacheService, cached, default_cache

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
