"""
"""
Example usage of the model caching system.
Example usage of the model caching system.


This script demonstrates how to use the caching system to improve performance
This script demonstrates how to use the caching system to improve performance
by caching model responses.
by caching model responses.
"""
"""




import argparse
import argparse
import logging
import logging
import os
import os
import sys
import sys
import time
import time
from typing import Any, Dict
from typing import Any, Dict


from ai_models.caching import RedisCache
from ai_models.caching import RedisCache


REDIS_AVAILABLE
REDIS_AVAILABLE


# Add the parent directory to the path to import the ai_models module
# Add the parent directory to the path to import the ai_models module
sys.path.append(
sys.path.append(
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
)


from ai_models.caching import CacheConfig, CacheManager
from ai_models.caching import CacheConfig, CacheManager


# Try to import Redis cache if available
# Try to import Redis cache if available
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    REDIS_AVAILABLE = False
    REDIS_AVAILABLE = False


    # Set up logging
    # Set up logging
    logging.basicConfig(
    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    )
    logger = logging.getLogger(__name__)
    logger = logging.getLogger(__name__)




    def simulate_model_inference(text: str, delay: float = 1.0) -> Dict[str, Any]:
    def simulate_model_inference(text: str, delay: float = 1.0) -> Dict[str, Any]:
    """
    """
    Simulate a model inference.
    Simulate a model inference.


    Args:
    Args:
    text: Input text
    text: Input text
    delay: Delay in seconds to simulate inference time
    delay: Delay in seconds to simulate inference time


    Returns:
    Returns:
    Model response
    Model response
    """
    """
    logger.info(f"Running inference for: {text}")
    logger.info(f"Running inference for: {text}")
    time.sleep(delay)
    time.sleep(delay)


    return {"text": text, "response": f"Response for: {text}", "timestamp": time.time()}
    return {"text": text, "response": f"Response for: {text}", "timestamp": time.time()}




    def test_memory_cache() -> None:
    def test_memory_cache() -> None:
    """
    """
    Test the memory cache backend.
    Test the memory cache backend.
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print("Testing Memory Cache")
    print("Testing Memory Cache")
    print("=" * 80)
    print("=" * 80)


    # Create cache configuration
    # Create cache configuration
    config = CacheConfig(
    config = CacheConfig(
    enabled=True,
    enabled=True,
    backend="memory",
    backend="memory",
    ttl=60,  # 60 seconds
    ttl=60,  # 60 seconds
    max_size=100,
    max_size=100,
    eviction_policy="lru",
    eviction_policy="lru",
    )
    )


    # Create cache manager
    # Create cache manager
    cache_manager = CacheManager(config)
    cache_manager = CacheManager(config)


    # Test cache
    # Test cache
    _run_cache_test(cache_manager)
    _run_cache_test(cache_manager)




    def test_disk_cache() -> None:
    def test_disk_cache() -> None:
    """
    """
    Test the disk cache backend.
    Test the disk cache backend.
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print("Testing Disk Cache")
    print("Testing Disk Cache")
    print("=" * 80)
    print("=" * 80)


    # Create cache directory
    # Create cache directory
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)


    # Create cache configuration
    # Create cache configuration
    config = CacheConfig(
    config = CacheConfig(
    enabled=True,
    enabled=True,
    backend="disk",
    backend="disk",
    ttl=60,  # 60 seconds
    ttl=60,  # 60 seconds
    max_size=100,
    max_size=100,
    eviction_policy="lru",
    eviction_policy="lru",
    backend_config={"disk": {"cache_dir": cache_dir, "serialization": "json"}},
    backend_config={"disk": {"cache_dir": cache_dir, "serialization": "json"}},
    )
    )


    # Create cache manager
    # Create cache manager
    cache_manager = CacheManager(config)
    cache_manager = CacheManager(config)


    # Test cache
    # Test cache
    _run_cache_test(cache_manager)
    _run_cache_test(cache_manager)




    def test_sqlite_cache() -> None:
    def test_sqlite_cache() -> None:
    """
    """
    Test the SQLite cache backend.
    Test the SQLite cache backend.
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print("Testing SQLite Cache")
    print("Testing SQLite Cache")
    print("=" * 80)
    print("=" * 80)


    # Create cache directory
    # Create cache directory
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)


    # Create cache configuration
    # Create cache configuration
    config = CacheConfig(
    config = CacheConfig(
    enabled=True,
    enabled=True,
    backend="sqlite",
    backend="sqlite",
    ttl=60,  # 60 seconds
    ttl=60,  # 60 seconds
    backend_config={
    backend_config={
    "sqlite": {
    "sqlite": {
    "db_path": os.path.join(cache_dir, "cache.db"),
    "db_path": os.path.join(cache_dir, "cache.db"),
    "serialization": "json",
    "serialization": "json",
    }
    }
    },
    },
    )
    )


    # Create cache manager
    # Create cache manager
    cache_manager = CacheManager(config)
    cache_manager = CacheManager(config)


    # Test cache
    # Test cache
    _run_cache_test(cache_manager)
    _run_cache_test(cache_manager)




    def test_redis_cache() -> None:
    def test_redis_cache() -> None:
    """
    """
    Test the Redis cache backend.
    Test the Redis cache backend.
    """
    """
    if not REDIS_AVAILABLE:
    if not REDIS_AVAILABLE:
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print("Redis Cache Not Available")
    print("Redis Cache Not Available")
    print("=" * 80)
    print("=" * 80)
    print("Redis not available. Please install it with: pip install redis")
    print("Redis not available. Please install it with: pip install redis")
    return print("\n" + "=" * 80)
    return print("\n" + "=" * 80)
    print("Testing Redis Cache")
    print("Testing Redis Cache")
    print("=" * 80)
    print("=" * 80)


    # Create cache configuration
    # Create cache configuration
    config = CacheConfig(
    config = CacheConfig(
    enabled=True,
    enabled=True,
    backend="redis",
    backend="redis",
    ttl=60,  # 60 seconds
    ttl=60,  # 60 seconds
    backend_config={
    backend_config={
    "redis": {
    "redis": {
    "host": "localhost",
    "host": "localhost",
    "port": 6379,
    "port": 6379,
    "db": 0,
    "db": 0,
    "prefix": "model_cache:",
    "prefix": "model_cache:",
    "serialization": "json",
    "serialization": "json",
    }
    }
    },
    },
    )
    )


    # Create cache manager
    # Create cache manager
    try:
    try:
    cache_manager = CacheManager(config)
    cache_manager = CacheManager(config)


    # Test cache
    # Test cache
    _run_cache_test(cache_manager)
    _run_cache_test(cache_manager)


except Exception as e:
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    print(f"Error connecting to Redis: {e}")
    print("Make sure Redis is running on localhost:6379")
    print("Make sure Redis is running on localhost:6379")




    def _run_cache_test(cache_manager: CacheManager) -> None:
    def _run_cache_test(cache_manager: CacheManager) -> None:
    """
    """
    Run a cache test with a given cache manager.
    Run a cache test with a given cache manager.


    Args:
    Args:
    cache_manager: Cache manager to test
    cache_manager: Cache manager to test
    """
    """
    # Define model and operation
    # Define model and operation
    model_id = "test-model"
    model_id = "test-model"
    operation = "generate"
    operation = "generate"


    # Define inputs
    # Define inputs
    inputs = [
    inputs = [
    "Hello, world!",
    "Hello, world!",
    "How are you?",
    "How are you?",
    "What is the meaning of life?",
    "What is the meaning of life?",
    "Hello, world!",  # Repeated input to test cache hit
    "Hello, world!",  # Repeated input to test cache hit
    ]
    ]


    # Define parameters
    # Define parameters
    parameters = {"temperature": 0.7, "max_tokens": 100}
    parameters = {"temperature": 0.7, "max_tokens": 100}


    # Run inference with caching
    # Run inference with caching
    for i, text in enumerate(inputs):
    for i, text in enumerate(inputs):
    start_time = time.time()
    start_time = time.time()


    # Check if response is in cache
    # Check if response is in cache
    cached_response = cache_manager.get(model_id, operation, text, parameters)
    cached_response = cache_manager.get(model_id, operation, text, parameters)


    if cached_response:
    if cached_response:
    print(f"Cache hit for input {i+1}: {text}")
    print(f"Cache hit for input {i+1}: {text}")
    print(f"Cached response: {cached_response}")
    print(f"Cached response: {cached_response}")
    else:
    else:
    print(f"Cache miss for input {i+1}: {text}")
    print(f"Cache miss for input {i+1}: {text}")


    # Run inference
    # Run inference
    response = simulate_model_inference(text)
    response = simulate_model_inference(text)


    # Cache response
    # Cache response
    cache_manager.set(model_id, operation, text, response, parameters)
    cache_manager.set(model_id, operation, text, response, parameters)


    print(f"Response: {response}")
    print(f"Response: {response}")


    elapsed_time = time.time() - start_time
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.4f} seconds")
    print(f"Elapsed time: {elapsed_time:.4f} seconds")
    print()
    print()


    # Get cache statistics
    # Get cache statistics
    stats = cache_manager.get_stats()
    stats = cache_manager.get_stats()
    print("Cache Statistics:")
    print("Cache Statistics:")
    for key, value in stats.items():
    for key, value in stats.items():
    print(f"  {key}: {value}")
    print(f"  {key}: {value}")


    # Get cache keys
    # Get cache keys
    keys = cache_manager.get_keys()
    keys = cache_manager.get_keys()
    print(f"\nCache Keys ({len(keys)}):")
    print(f"\nCache Keys ({len(keys)}):")
    for key in keys:
    for key in keys:
    print(f"  {key}")
    print(f"  {key}")


    # Clear cache
    # Clear cache
    print("\nClearing cache...")
    print("\nClearing cache...")
    cache_manager.clear()
    cache_manager.clear()


    # Verify cache is empty
    # Verify cache is empty
    size = cache_manager.get_size()
    size = cache_manager.get_size()
    print(f"Cache size after clearing: {size}")
    print(f"Cache size after clearing: {size}")




    def main():
    def main():
    """
    """
    Main function to demonstrate the model caching system.
    Main function to demonstrate the model caching system.
    """
    """
    parser = argparse.ArgumentParser(description="Test different cache backends")
    parser = argparse.ArgumentParser(description="Test different cache backends")
    parser.add_argument(
    parser.add_argument(
    "--backend",
    "--backend",
    type=str,
    type=str,
    choices=["memory", "disk", "sqlite", "redis", "all"],
    choices=["memory", "disk", "sqlite", "redis", "all"],
    default="all",
    default="all",
    help="Cache backend to test",
    help="Cache backend to test",
    )
    )


    args = parser.parse_args()
    args = parser.parse_args()


    if args.backend == "memory" or args.backend == "all":
    if args.backend == "memory" or args.backend == "all":
    test_memory_cache()
    test_memory_cache()


    if args.backend == "disk" or args.backend == "all":
    if args.backend == "disk" or args.backend == "all":
    test_disk_cache()
    test_disk_cache()


    if args.backend == "sqlite" or args.backend == "all":
    if args.backend == "sqlite" or args.backend == "all":
    test_sqlite_cache()
    test_sqlite_cache()


    if args.backend == "redis" or args.backend == "all":
    if args.backend == "redis" or args.backend == "all":
    test_redis_cache()
    test_redis_cache()




    if __name__ == "__main__":
    if __name__ == "__main__":
    main()
    main()