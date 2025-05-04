"""
"""
Cache backends for the model cache system.
Cache backends for the model cache system.


This package provides different cache storage backends for the model cache system.
This package provides different cache storage backends for the model cache system.
"""
"""




from .base import CacheBackend
from .base import CacheBackend
from .disk_cache import DiskCache
from .disk_cache import DiskCache
from .memory_cache import MemoryCache
from .memory_cache import MemoryCache
from .redis_cache import RedisCache
from .redis_cache import RedisCache
from .sqlite_cache import SQLiteCache
from .sqlite_cache import SQLiteCache


REDIS_AVAILABLE
REDIS_AVAILABLE


# Import Redis cache if available
# Import Redis cache if available
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    REDIS_AVAILABLE = False
    REDIS_AVAILABLE = False


    __all__ = [
    __all__ = [
    "CacheBackend",
    "CacheBackend",
    "MemoryCache",
    "MemoryCache",
    "DiskCache",
    "DiskCache",
    "SQLiteCache",
    "SQLiteCache",
    ]
    ]


    # Add Redis cache if available
    # Add Redis cache if available
    if REDIS_AVAILABLE:
    if REDIS_AVAILABLE:
    __all__.append("RedisCache")
    __all__.append("RedisCache")