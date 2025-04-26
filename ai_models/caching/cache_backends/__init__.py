"""
Cache backends for the model cache system.

This package provides different cache storage backends for the model cache system.
"""

from .base import CacheBackend
from .memory_cache import MemoryCache
from .disk_cache import DiskCache
from .sqlite_cache import SQLiteCache

# Import Redis cache if available
try:
    from .redis_cache import RedisCache
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

__all__ = [
    'CacheBackend',
    'MemoryCache',
    'DiskCache',
    'SQLiteCache',
]

# Add Redis cache if available
if REDIS_AVAILABLE:
    __all__.append('RedisCache')
