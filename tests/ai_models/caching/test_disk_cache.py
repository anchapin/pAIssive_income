"""
Tests for the DiskCache backend.
"""

import os
import time
import pytest
import tempfile
import shutil

from ai_models.caching.cache_backends.disk_cache import DiskCache


@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for cache files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def disk_cache(temp_cache_dir):
    """Create a DiskCache instance for testing."""
    cache = DiskCache(
        cache_dir=temp_cache_dir,
        max_size=3,  # Small size to test eviction
        eviction_policy="lru",
    )
    return cache


def test_cache_hit_miss(disk_cache):
    """Test cache hit and miss scenarios."""
    # Test cache miss
    key = "test_key"
    assert disk_cache.get(key) is None

    # Verify miss was recorded
    assert disk_cache.get_stats()["misses"] == 1

    # Test cache hit
    value = {"data": "test_value"}
    disk_cache.set(key, value)
    cached_value = disk_cache.get(key)
    assert cached_value == value

    # Verify hit was recorded
    assert disk_cache.get_stats()["hits"] == 1


def test_cache_invalidation(disk_cache):
    """Test cache invalidation with TTL."""
    key = "test_key"
    value = {"data": "test_value"}

    # Set with 1 second TTL
    disk_cache.set(key, value, ttl=1)

    # Verify value exists
    assert disk_cache.get(key) == value

    # Wait for TTL to expire
    time.sleep(1.1)

    # Verify value is invalidated
    assert disk_cache.get(key) is None
    assert not disk_cache.exists(key)


def test_size_limit_and_eviction(disk_cache):
    """Test cache size limits and eviction policies."""
    # Add items up to max size
    for i in range(3):
        key = f"key{i}"
        value = {"data": f"value{i}"}
        disk_cache.set(key, value)

    # Verify all items exist
    assert disk_cache.get_size() == 3
    for i in range(3):
        assert disk_cache.exists(f"key{i}")

    # Access key1 to make it most recently used
    disk_cache.get("key1")

    # Add new item to trigger eviction
    disk_cache.set("new_key", {"data": "new_value"})

    # Verify size is still at max
    assert disk_cache.get_size() == 3

    # Verify least recently used item was evicted (key0)
    assert not disk_cache.exists("key0")
    assert disk_cache.exists("key1")  # Most recently accessed
    assert disk_cache.exists("key2")
    assert disk_cache.exists("new_key")

    # Verify eviction was recorded
    assert disk_cache.get_stats()["evictions"] == 1


def test_clear_cache(disk_cache):
    """Test clearing the cache."""
    # Add some items
    for i in range(3):
        disk_cache.set(f"key{i}", {"data": f"value{i}"})

    # Verify items exist
    assert disk_cache.get_size() == 3

    # Clear cache
    assert disk_cache.clear()

    # Verify cache is empty
    assert disk_cache.get_size() == 0
    assert disk_cache.get_stats()["clears"] == 1


def test_serialization_formats(temp_cache_dir):
    """Test different serialization formats."""
    # Test JSON serialization
    json_cache = DiskCache(
        cache_dir=os.path.join(temp_cache_dir, "json"), serialization="json"
    )

    # Test pickle serialization
    pickle_cache = DiskCache(
        cache_dir=os.path.join(temp_cache_dir, "pickle"), serialization="pickle"
    )

    value = {"data": "test_value", "number": 42}

    # Test with both serialization formats
    for cache in [json_cache, pickle_cache]:
        cache.set("test_key", value)
        assert cache.get("test_key") == value


def test_metadata_persistence(disk_cache):
    """Test that metadata (access counts, times) persists."""
    key = "test_key"
    value = {"data": "test_value"}

    # Set value and access it multiple times
    disk_cache.set(key, value)
    for _ in range(3):
        disk_cache.get(key)

    # Create new cache instance with same directory
    new_cache = DiskCache(cache_dir=disk_cache.cache_dir)

    # Get metadata
    metadata = new_cache._load_metadata(key)

    # Verify access count was persisted
    assert metadata["access_count"] == 3


def test_eviction_policies(temp_cache_dir):
    """Test different eviction policies."""
    test_cases = [
        ("lru", lambda cache: cache.get("key1")),  # Make key1 most recently used
        (
            "lfu",
            lambda cache: [cache.get("key1") for _ in range(3)],
        ),  # Make key1 most frequently used
        ("fifo", lambda cache: None),  # First in first out, no access needed
    ]

    for policy, access_pattern in test_cases:
        # Create cache with specific eviction policy
        cache = DiskCache(
            cache_dir=os.path.join(temp_cache_dir, policy),
            max_size=3,
            eviction_policy=policy,
        )

        # Add items
        for i in range(3):
            cache.set(f"key{i}", {"data": f"value{i}"})

        # Apply access pattern
        access_pattern(cache)

        # Add new item to trigger eviction
        cache.set("new_key", {"data": "new_value"})

        if policy == "lru":
            # Least recently used (key0) should be evicted
            assert not cache.exists("key0")
            assert cache.exists("key1")  # Most recently used
        elif policy == "lfu":
            # Least frequently used (key2) should be evicted
            assert not cache.exists("key2")
            assert cache.exists("key1")  # Most frequently used
        elif policy == "fifo":
            # First item (key0) should be evicted
            assert not cache.exists("key0")
            assert cache.exists("key1")


def test_concurrent_access(disk_cache):
    """Test thread safety of cache operations."""
    from concurrent.futures import ThreadPoolExecutor
    import random

    def cache_operation(i: int):
        # Randomly choose between get and set operations
        if random.random() < 0.5:
            disk_cache.set(f"key{i}", {"data": f"value{i}"})
        else:
            disk_cache.get(f"key{i}")

    # Run multiple cache operations concurrently
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(cache_operation, range(10)))

    # Verify cache is in a consistent state
    assert disk_cache.get_size() <= disk_cache.max_size

    # Verify metadata files exist for all cache entries
    for key in disk_cache.get_keys():
        assert os.path.exists(disk_cache._get_metadata_path(key))


def test_error_handling(disk_cache):
    """Test error handling scenarios."""
    # Test with invalid serialization format
    cache = DiskCache(cache_dir=disk_cache.cache_dir, serialization="invalid")
    # Should fall back to JSON
    value = {"data": "test"}
    assert cache.set("test_key", value)
    assert cache.get("test_key") == value

    # Test with unserializable value
    import threading

    unserializable = {"lock": threading.Lock()}
    assert not disk_cache.set("bad_key", unserializable)

    # Test with corrupted cache file
    key = "corrupt_key"
    disk_cache.set(key, {"data": "test"})
    file_path = disk_cache._get_file_path(key)

    # Corrupt the file
    with open(file_path, "w") as f:
        f.write("invalid json")

    # Should handle gracefully
    assert disk_cache.get(key) is None


def test_get_ttl(disk_cache):
    """Test TTL retrieval."""
    key = "test_key"
    value = {"data": "test"}

    # Set with TTL
    disk_cache.set(key, value, ttl=10)

    # Check TTL
    ttl = disk_cache.get_ttl(key)
    assert ttl is not None
    assert 0 < ttl <= 10

    # Set without TTL
    disk_cache.set("no_ttl_key", value)
    assert disk_cache.get_ttl("no_ttl_key") is None
