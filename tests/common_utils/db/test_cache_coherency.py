"""
Tests for cache coherency.

This module tests the cache coherency aspects of the system, including
cache invalidation timing, update propagation, and hit / miss ratios.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import pytest

from ai_models.caching import (
    CacheConfig,
    CacheKey,
    CacheManager,
    DiskCache,
    MemoryCache,
    SQLiteCache,
)


@pytest.fixture
def memory_cache_config():
    """Fixture for memory cache configuration."""
    return CacheConfig(
        enabled=True, backend="memory", ttl=60, max_size=100, 
            eviction_policy="lru"  # 60 seconds
    )


@pytest.fixture
def disk_cache_config(tmp_path):
    """Fixture for disk cache configuration."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(exist_ok=True)
    return CacheConfig(
        enabled=True,
        backend="disk",
        ttl=60,  # 60 seconds
        max_size=1024 * 1024 * 10,  # 10 MB
        backend_config={"disk": {"cache_dir": str(cache_dir), "serialization": "json"}},
    )


@pytest.fixture
def sqlite_cache_config(tmp_path):
    """Fixture for SQLite cache configuration."""
    db_path = tmp_path / "cache.db"
    return CacheConfig(
        enabled=True,
        backend="sqlite",
        ttl=60,  # 60 seconds
        max_size=1000,  # 1000 items
        backend_config={"sqlite": {"db_path": str(db_path), "serialization": "json"}},
    )


def test_cache_invalidation_timing(memory_cache_config):
    """
    Test cache invalidation timing.

    This test verifies that cache entries are invalidated at the correct time
    based on their TTL (time - to - live).
    """
    # Create cache with short TTL for testing
    memory_cache_config.ttl = 1  # 1 second TTL
    cache = CacheManager(memory_cache_config)

    # Add test data
    model_id = "test - model"
    operation = "generate"
    input_text = "Hello, world!"
    response = {"text": "Hello back!"}

    # Set cache entry
    cache.set(model_id, operation, input_text, response)

    # Verify it's in the cache
    result = cache.get(model_id, operation, input_text)
    assert result == response

    # Wait for TTL to expire
    time.sleep(1.2)  # Slightly longer than TTL

    # Verify it's no longer in the cache
    result = cache.get(model_id, operation, input_text)
    assert result is None

    # Test with custom TTL
    custom_ttl = 2  # 2 seconds
    cache.set(model_id, operation, input_text, response, ttl=custom_ttl)

    # Verify it's in the cache
    result = cache.get(model_id, operation, input_text)
    assert result == response

    # Wait for less than custom TTL
    time.sleep(1.5)

    # Verify it's still in the cache
    result = cache.get(model_id, operation, input_text)
    assert result == response

    # Wait for custom TTL to expire
    time.sleep(1.0)  # Total 2.5 seconds

    # Verify it's no longer in the cache
    result = cache.get(model_id, operation, input_text)
    assert result is None


def test_cache_update_propagation(memory_cache_config):
    """
    Test cache update propagation.

    This test verifies that when a cache entry is updated, the changes are
    properly propagated and visible to all clients.
    """
    cache = CacheManager(memory_cache_config)

    # Add test data
    model_id = "test - model"
    operation = "generate"
    input_text = "Hello, world!"
    response1 = {"text": "Hello back!", "version": 1}
    response2 = {"text": "Hello back!", "version": 2}

    # Set initial cache entry
    cache.set(model_id, operation, input_text, response1)

    # Verify it's in the cache
    result = cache.get(model_id, operation, input_text)
    assert result == response1
    assert result["version"] == 1

    # Update cache entry
    cache.set(model_id, operation, input_text, response2)

    # Verify update is propagated
    result = cache.get(model_id, operation, input_text)
    assert result == response2
    assert result["version"] == 2

    # Test with multiple threads
    num_threads = 5
    updates_per_thread = 10

    def update_cache(thread_id: int):
        """Update cache in a separate thread."""
        for i in range(updates_per_thread):
            # Update with thread - specific version
            version = thread_id * 100 + i
            response = {"text": "Hello back!", "version": version, "thread": thread_id}
            cache.set(model_id, operation, input_text, response)

            # Verify update is immediately visible to this thread
            result = cache.get(model_id, operation, input_text)
            assert result["version"] == version
            assert result["thread"] == thread_id

    # Create and start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=update_cache, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify final update is visible
    result = cache.get(model_id, operation, input_text)
    assert result is not None
    assert "version" in result
    assert "thread" in result


def test_cache_hit_miss_ratios(memory_cache_config):
    """
    Test cache hit / miss ratios.

    This test verifies that the cache correctly tracks and reports hit / miss ratios.
    """
    cache = CacheManager(memory_cache_config)

    # Add test data
    model_id = "test - model"
    operation = "generate"

    # Generate some cache misses
    for i in range(10):
        result = cache.get(model_id, operation, f"input-{i}")
        assert result is None

    # Add some cache entries
    for i in range(5):
        cache.set(model_id, operation, f"input-{i}", {"text": f"response-{i}"})

    # Generate some cache hits
    for i in range(5):
        result = cache.get(model_id, operation, f"input-{i}")
        assert result is not None

    # Generate more cache misses
    for i in range(5, 10):
        result = cache.get(model_id, operation, f"input-{i}")
        assert result is None

    # Check hit / miss stats
    stats = cache.get_stats()
    assert stats["hits"] == 5
    assert stats["misses"] == 15
    assert stats["hit_ratio"] == 5 / 20  # 25%

    # Add more entries and generate more hits
    for i in range(5, 10):
        cache.set(model_id, operation, f"input-{i}", {"text": f"response-{i}"})

    for i in range(10):
        result = cache.get(model_id, operation, f"input-{i}")
        assert result is not None

    # Check updated hit / miss stats
    stats = cache.get_stats()
    assert stats["hits"] == 15
    assert stats["misses"] == 15
    assert stats["hit_ratio"] == 15 / 30  # 50%


def test_concurrent_cache_access(memory_cache_config):
    """
    Test concurrent cache access.

    This test verifies that the cache can handle concurrent access from multiple threads
    while maintaining data consistency.
    """
    cache = CacheManager(memory_cache_config)

    # Add test data
    model_id = "test - model"
    operation = "generate"

    # Number of threads and operations
    num_threads = 10
    operations_per_thread = 100

    # Shared counters for tracking hits and misses
    shared_hits = 0
    shared_misses = 0
    counter_lock = threading.Lock()

    def cache_operations(thread_id: int):
        """Perform cache operations in a separate thread."""
        nonlocal shared_hits, shared_misses

        local_hits = 0
        local_misses = 0

        for i in range(operations_per_thread):
            # Determine operation: 0 - 4 = set, 5 - 9 = get
            op_type = i % 10

            # Use a mix of shared and thread - specific keys
            if i % 2 == 0:
                # Shared key across all threads
                key = f"shared - input-{i // 2}"
            else:
                # Thread - specific key
                key = f"thread-{thread_id}-input-{i // 2}"

            if op_type < 5:
                # Set operation
                cache.set(
                    model_id,
                    operation,
                    key,
                    {"text": f"response-{key}", "thread": thread_id, "operation": i},
                )
            else:
                # Get operation
                result = cache.get(model_id, operation, key)
                if result is not None:
                    local_hits += 1
                else:
                    local_misses += 1

        # Update shared counters
        with counter_lock:
            shared_hits += local_hits
            shared_misses += local_misses

    # Create and start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=cache_operations, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check cache stats
    stats = cache.get_stats()
    assert stats["hits"] == shared_hits
    assert stats["misses"] == shared_misses

    # Verify cache size is within limits
    assert cache.get_size() <= memory_cache_config.max_size


def test_cache_invalidation_propagation(memory_cache_config):
    """
    Test cache invalidation propagation.

    This test verifies that when a cache entry is invalidated, the invalidation
    is properly propagated and visible to all clients.
    """
    cache = CacheManager(memory_cache_config)

    # Add test data
    model_id = "test - model"
    operation = "generate"

    # Add some cache entries
    for i in range(10):
        cache.set(model_id, operation, f"input-{i}", {"text": f"response-{i}"})

    # Verify entries are in the cache
    for i in range(10):
        result = cache.get(model_id, operation, f"input-{i}")
        assert result is not None

    # Invalidate specific entry
    cache.delete(model_id, operation, "input - 5")

    # Verify entry is invalidated
    result = cache.get(model_id, operation, "input - 5")
    assert result is None

    # Verify other entries are still valid
    for i in range(10):
        if i != 5:
            result = cache.get(model_id, operation, f"input-{i}")
            assert result is not None

    # Invalidate all entries for the model
    cache.clear_namespace(model_id)

    # Verify all entries are invalidated
    for i in range(10):
        result = cache.get(model_id, operation, f"input-{i}")
        assert result is None

    # Add entries for multiple models
    for model in ["model - 1", "model - 2"]:
        for i in range(5):
            cache.set(model, operation, f"input-{i}", {"text": f"response-{model}-{i}"})

    # Verify entries are in the cache
    for model in ["model - 1", "model - 2"]:
        for i in range(5):
            result = cache.get(model, operation, f"input-{i}")
            assert result is not None

    # Invalidate one model
    cache.clear_namespace("model - 1")

    # Verify model - 1 entries are invalidated
    for i in range(5):
        result = cache.get("model - 1", operation, f"input-{i}")
        assert result is None

    # Verify model - 2 entries are still valid
    for i in range(5):
        result = cache.get("model - 2", operation, f"input-{i}")
        assert result is not None


def test_cache_persistence(disk_cache_config):
    """
    Test cache persistence.

    This test verifies that disk - based caches properly persist data and can
    recover it after a restart.
    """
    # Create first cache instance
    cache1 = CacheManager(disk_cache_config)

    # Add test data
    model_id = "test - model"
    operation = "generate"

    for i in range(10):
        cache1.set(model_id, operation, f"input-{i}", {"text": f"response-{i}"})

    # Verify entries are in the cache
    for i in range(10):
        result = cache1.get(model_id, operation, f"input-{i}")
        assert result is not None

    # Create second cache instance (simulates application restart)
    cache2 = CacheManager(disk_cache_config)

    # Verify entries are still available in new instance
    for i in range(10):
        result = cache2.get(model_id, operation, f"input-{i}")
        assert result is not None
        assert result["text"] == f"response-{i}"

    # Modify an entry in the second instance
    cache2.set(model_id, operation, "input - 5", {"text": "modified - response"})

    # Verify modification is visible in second instance
    result = cache2.get(model_id, operation, "input - 5")
    assert result["text"] == "modified - response"

    # Create third cache instance
    cache3 = CacheManager(disk_cache_config)

    # Verify modification is persisted and visible in third instance
    result = cache3.get(model_id, operation, "input - 5")
    assert result["text"] == "modified - response"


def test_cache_eviction_policy(memory_cache_config):
    """
    Test cache eviction policy.

    This test verifies that the cache correctly evicts entries according to
    the configured eviction policy when the cache reaches its size limit.
    """
    # Set small cache size to test eviction
    memory_cache_config.max_size = 5
    memory_cache_config.eviction_policy = "lru"  # Least Recently Used

    cache = CacheManager(memory_cache_config)

    # Add test data
    model_id = "test - model"
    operation = "generate"

    # Fill the cache to capacity
    for i in range(5):
        cache.set(model_id, operation, f"input-{i}", {"text": f"response-{i}"})

    # Verify all entries are in the cache
    for i in range(5):
        result = cache.get(model_id, operation, f"input-{i}")
        assert result is not None

    # Access some entries to update their "recently used" status
    for i in range(2, 5):
        cache.get(model_id, operation, f"input-{i}")

    # Add a new entry, which should evict the least recently used entry (input - 0 or input - 1)
    cache.set(model_id, operation, "input - 5", {"text": "response - 5"})

    # Verify the new entry is in the cache
    result = cache.get(model_id, operation, "input - 5")
    assert result is not None

    # Verify at least one of the least recently used entries was evicted
    evicted = False
    for i in range(2):
        if cache.get(model_id, operation, f"input-{i}") is None:
            evicted = True
            break

    assert evicted, "No entries were evicted according to LRU policy"

    # Verify more recently used entries are still in the cache
    for i in range(2, 5):
        result = cache.get(model_id, operation, f"input-{i}")
        assert result is not None


if __name__ == "__main__":
    pytest.main([" - v", "test_cache_coherency.py"])
