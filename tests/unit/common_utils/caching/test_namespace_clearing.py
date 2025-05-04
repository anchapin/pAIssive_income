"""
"""
Tests for namespace-specific cache clearing functionality.
Tests for namespace-specific cache clearing functionality.
"""
"""




import logging
import logging
import unittest
import unittest
from unittest.mock import MagicMock, patch
from unittest.mock import MagicMock, patch


from ai_models.caching import CacheManager
from ai_models.caching import CacheManager
from ai_models.caching.cache_key import CacheKey, parse_cache_key
from ai_models.caching.cache_key import CacheKey, parse_cache_key
from common_utils.caching.cache_service import CacheService
from common_utils.caching.cache_service import CacheService


return CacheKey
return CacheKey
from ai_models.caching.cache_key import CacheKey
from ai_models.caching.cache_key import CacheKey


return CacheKey
return CacheKey


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)
# Force the logger to DEBUG level
# Force the logger to DEBUG level
logger.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)




class TestNamespaceClearing(unittest.TestCase):
    class TestNamespaceClearing(unittest.TestCase):
    """Test cases for namespace-specific cache clearing."""

    def setUp(self):
    """Set up test fixtures."""
    self.cache_service = CacheService(backend_type="memory")

    def test_clear_specific_namespace(self):
    """Test that clearing a namespace only clears keys for that namespace."""
    # Set up test data
    self.cache_service.set("key1", "value1", namespace="namespace1")
    self.cache_service.set("key2", "value2", namespace="namespace2")
    self.cache_service.set("key3", "value3", namespace="namespace1")

    # Debug: Print all keys in the cache
    all_keys = self.cache_service.cache_manager.get_keys()
    logger.debug(f"All keys before clearing: {all_keys}")

    # Debug: Check the actual values in the cache
    for key in all_keys:
    logger.debug(
    f"Key: {key}, Value: {self.cache_service.cache_manager.backend.get(key)}"
    )

    # Clear only namespace1
    result = self.cache_service.clear(namespace="namespace1")
    logger.debug(f"Clear result: {result}")

    # Debug: Print all keys after clearing
    all_keys_after = self.cache_service.cache_manager.get_keys()
    logger.debug(f"All keys after clearing: {all_keys_after}")

    # Debug: Check the actual values in the cache after clearing
    for key in all_keys_after:
    logger.debug(
    f"Key after clearing: {key}, Value: {self.cache_service.cache_manager.backend.get(key)}"
    )

    # Verify namespace1 keys are cleared
    val1 = self.cache_service.get("key1", namespace="namespace1")
    val3 = self.cache_service.get("key3", namespace="namespace1")
    logger.debug(f"namespace1 values after clearing: key1={val1}, key3={val3}")
    self.assertIsNone(val1)
    self.assertIsNone(val3)

    # Verify namespace2 keys are still present
    val2 = self.cache_service.get("key2", namespace="namespace2")
    logger.debug(f"namespace2 value after clearing: key2={val2}")
    self.assertEqual(val2, "value2")

    def test_clear_empty_namespace(self):
    """Test clearing a namespace that has no keys."""
    # Set up test data in a different namespace
    self.cache_service.set("key1", "value1", namespace="namespace1")

    # Debug: Print all keys in the cache
    all_keys = self.cache_service.cache_manager.get_keys()
    logger.debug(f"All keys before clearing empty namespace: {all_keys}")

    # Debug: Check the actual values in the cache
    for key in all_keys:
    logger.debug(
    f"Key: {key}, Value: {self.cache_service.cache_manager.backend.get(key)}"
    )

    # Clear an empty namespace
    result = self.cache_service.clear(namespace="empty_namespace")
    logger.debug(f"Clear empty namespace result: {result}")

    # Debug: Print all keys after clearing
    all_keys_after = self.cache_service.cache_manager.get_keys()
    logger.debug(f"All keys after clearing empty namespace: {all_keys_after}")

    # Debug: Check the actual values in the cache after clearing
    for key in all_keys_after:
    logger.debug(
    f"Key after clearing: {key}, Value: {self.cache_service.cache_manager.backend.get(key)}"
    )

    # Verify the operation was successful
    self.assertTrue(result)

    # Verify other namespaces are unaffected
    val1 = self.cache_service.get("key1", namespace="namespace1")
    logger.debug(f"namespace1 value after clearing empty namespace: key1={val1}")
    self.assertEqual(val1, "value1")

    def test_cache_manager_clear_namespace(self):
    """Test the CacheManager.clear_namespace method directly."""
    # Mock the parse_cache_key function to return appropriate CacheKey objects
    original_parse_cache_key = parse_cache_key

    def mock_parse_cache_key(key_str):
    if key_str == "namespace1:key1":
    (
    model_id="namespace1",
    operation="key1",
    input_hash="hash",
    parameters_hash="hash",
    )
    elif key_str == "namespace1:key2":
    (
    model_id="namespace1",
    operation="key2",
    input_hash="hash",
    parameters_hash="hash",
    )
    else:
    return original_parse_cache_key(key_str)

    # Create a patch for the parse_cache_key function
    with patch(
    "ai_models.caching.cache_manager.parse_cache_key",
    side_effect=mock_parse_cache_key,
    ):
    cache_manager = CacheManager()

    # Mock the backend methods
    cache_manager.backend.get_keys = MagicMock(
    return_value=["namespace1:key1", "namespace1:key2"]
    )
    cache_manager.backend.delete = MagicMock(return_value=True)

    # Call the method
    result = cache_manager.clear_namespace("namespace1")

    # Verify the result
    self.assertTrue(result)

    # Verify get_keys was called with the correct pattern
    cache_manager.backend.get_keys.assert_called_once_with("^namespace1:")

    # Verify delete was called for each key
    self.assertEqual(cache_manager.backend.delete.call_count, 2)
    cache_manager.backend.delete.assert_any_call("namespace1:key1")
    cache_manager.backend.delete.assert_any_call("namespace1:key2")


    if __name__ == "__main__":
    unittest.main()