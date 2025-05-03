"""
Example usage of the model caching system.

This script demonstrates how to use the caching system to improve performance
by caching model responses.
"""

import argparse
import logging
import os
import sys
import time
from typing import Any, Dict

# Add the parent directory to the path to import the ai_models module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_models.caching import (
    CacheConfig,
    CacheManager,
)

# Try to import Redis cache if available
try:
    pass

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def simulate_model_inference(text: str, delay: float = 1.0) -> Dict[str, Any]:
    """
    Simulate a model inference.

    Args:
        text: Input text
        delay: Delay in seconds to simulate inference time

    Returns:
        Model response
    """
    logger.info(f"Running inference for: {text}")
    time.sleep(delay)

    return {"text": text, "response": f"Response for: {text}", "timestamp": time.time()}


def test_memory_cache() -> None:
    """
    Test the memory cache backend.
    """
    print("\n" + "=" * 80)
    print("Testing Memory Cache")
    print("=" * 80)

    # Create cache configuration
    config = CacheConfig(
        enabled=True,
        backend="memory",
        ttl=60,  # 60 seconds
        max_size=100,
        eviction_policy="lru",
    )

    # Create cache manager
    cache_manager = CacheManager(config)

    # Test cache
    _run_cache_test(cache_manager)


def test_disk_cache() -> None:
    """
    Test the disk cache backend.
    """
    print("\n" + "=" * 80)
    print("Testing Disk Cache")
    print("=" * 80)

    # Create cache directory
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    os.makedirs(cache_dir, exist_ok=True)

    # Create cache configuration
    config = CacheConfig(
        enabled=True,
        backend="disk",
        ttl=60,  # 60 seconds
        max_size=100,
        eviction_policy="lru",
        backend_config={"disk": {"cache_dir": cache_dir, "serialization": "json"}},
    )

    # Create cache manager
    cache_manager = CacheManager(config)

    # Test cache
    _run_cache_test(cache_manager)


def test_sqlite_cache() -> None:
    """
    Test the SQLite cache backend.
    """
    print("\n" + "=" * 80)
    print("Testing SQLite Cache")
    print("=" * 80)

    # Create cache directory
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    os.makedirs(cache_dir, exist_ok=True)

    # Create cache configuration
    config = CacheConfig(
        enabled=True,
        backend="sqlite",
        ttl=60,  # 60 seconds
        backend_config={
            "sqlite": {
                "db_path": os.path.join(cache_dir, "cache.db"),
                "serialization": "json",
            }
        },
    )

    # Create cache manager
    cache_manager = CacheManager(config)

    # Test cache
    _run_cache_test(cache_manager)


def test_redis_cache() -> None:
    """
    Test the Redis cache backend.
    """
    if not REDIS_AVAILABLE:
        print("\n" + "=" * 80)
        print("Redis Cache Not Available")
        print("=" * 80)
        print("Redis not available. Please install it with: pip install redis")
        return

    print("\n" + "=" * 80)
    print("Testing Redis Cache")
    print("=" * 80)

    # Create cache configuration
    config = CacheConfig(
        enabled=True,
        backend="redis",
        ttl=60,  # 60 seconds
        backend_config={
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "prefix": "model_cache:",
                "serialization": "json",
            }
        },
    )

    # Create cache manager
    try:
        cache_manager = CacheManager(config)

        # Test cache
        _run_cache_test(cache_manager)

    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        print("Make sure Redis is running on localhost:6379")


def _run_cache_test(cache_manager: CacheManager) -> None:
    """
    Run a cache test with a given cache manager.

    Args:
        cache_manager: Cache manager to test
    """
    # Define model and operation
    model_id = "test - model"
    operation = "generate"

    # Define inputs
    inputs = [
        "Hello, world!",
        "How are you?",
        "What is the meaning of life?",
        "Hello, world!",  # Repeated input to test cache hit
    ]

    # Define parameters
    parameters = {"temperature": 0.7, "max_tokens": 100}

    # Run inference with caching
    for i, text in enumerate(inputs):
        start_time = time.time()

        # Check if response is in cache
        cached_response = cache_manager.get(model_id, operation, text, parameters)

        if cached_response:
            print(f"Cache hit for input {i + 1}: {text}")
            print(f"Cached response: {cached_response}")
        else:
            print(f"Cache miss for input {i + 1}: {text}")

            # Run inference
            response = simulate_model_inference(text)

            # Cache response
            cache_manager.set(model_id, operation, text, response, parameters)

            print(f"Response: {response}")

        elapsed_time = time.time() - start_time
        print(f"Elapsed time: {elapsed_time:.4f} seconds")
        print()

    # Get cache statistics
    stats = cache_manager.get_stats()
    print("Cache Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Get cache keys
    keys = cache_manager.get_keys()
    print(f"\nCache Keys ({len(keys)}):")
    for key in keys:
        print(f"  {key}")

    # Clear cache
    print("\nClearing cache...")
    cache_manager.clear()

    # Verify cache is empty
    size = cache_manager.get_size()
    print(f"Cache size after clearing: {size}")


def main():
    """
    Main function to demonstrate the model caching system.
    """
    parser = argparse.ArgumentParser(description="Test different cache backends")
    parser.add_argument(
        "--backend",
        type=str,
        choices=["memory", "disk", "sqlite", "redis", "all"],
        default="all",
        help="Cache backend to test",
    )

    args = parser.parse_args()

    if args.backend == "memory" or args.backend == "all":
        test_memory_cache()

    if args.backend == "disk" or args.backend == "all":
        test_disk_cache()

    if args.backend == "sqlite" or args.backend == "all":
        test_sqlite_cache()

    if args.backend == "redis" or args.backend == "all":
        test_redis_cache()


if __name__ == "__main__":
    main()
