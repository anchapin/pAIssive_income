"""
Cache backends for the model cache system.

This package provides different cache storage backends for the model cache system.
"""


from .base import CacheBackend
from .disk_cache import DiskCache
from .memory_cache import MemoryCache
from .sqlite_cache import SQLiteCache


    from .redis_cache import RedisCache

    REDIS_AVAILABLE 

# Import Redis cache if available
try:
= True
except ImportError:
    REDIS_AVAILABLE = False

__all__ = [
    "CacheBackend",
    "MemoryCache",
    "DiskCache",
    "SQLiteCache",
]

# Add Redis cache if available
if REDIS_AVAILABLE:
    __all__.append("RedisCache")