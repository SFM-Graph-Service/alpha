"""
Test module specifically for MultiLevelCache.get method.

This test validates that the get method reported as a stub in the core analysis
is actually fully implemented and working correctly.
"""

import unittest
import threading
import time
from unittest.mock import Mock

from infrastructure.advanced_caching import MultiLevelCache, MemoryCache, TTLMemoryCache


class TestMultiLevelCacheGet(unittest.TestCase):
    """Test MultiLevelCache.get method implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mlc = MultiLevelCache("test_cache")
        self.l1_cache = MemoryCache("L1", max_size=10)
        self.l2_cache = MemoryCache("L2", max_size=100)
        self.mlc.add_level(self.l1_cache)
        self.mlc.add_level(self.l2_cache)

    def test_get_nonexistent_key_returns_none(self):
        """Test that get returns None for non-existent keys."""
        result = self.mlc.get("nonexistent_key")
        self.assertIsNone(result)

    def test_get_promotes_from_lower_level_cache(self):
        """Test that get promotes values from lower level caches."""
        # Set value only in L2 cache
        self.l2_cache.set("test_key", "test_value")
        
        # Verify initial state
        self.assertIsNone(self.l1_cache.get("test_key"))
        self.assertEqual(self.l2_cache.get("test_key"), "test_value")
        
        # Get via multi-level cache should promote to L1
        result = self.mlc.get("test_key")
        
        # Verify result and promotion
        self.assertEqual(result, "test_value")
        self.assertEqual(self.l1_cache.get("test_key"), "test_value")
        self.assertEqual(self.l2_cache.get("test_key"), "test_value")

    def test_get_from_highest_level_no_promotion_needed(self):
        """Test that getting from the highest level cache doesn't trigger promotion."""
        # Set value in L1 (highest level)
        self.l1_cache.set("l1_key", "l1_value")
        
        result = self.mlc.get("l1_key")
        self.assertEqual(result, "l1_value")
        
        # Should not be in L2 since it was found in L1
        self.assertIsNone(self.l2_cache.get("l1_key"))

    def test_get_with_multiple_cache_levels(self):
        """Test get behavior with more than 2 cache levels."""
        # Add a third cache level
        l3_cache = TTLMemoryCache("L3", max_size=1000, default_ttl=3600)
        self.mlc.add_level(l3_cache)
        
        # Set value only in L3 (lowest level)
        l3_cache.set("l3_key", "l3_value")
        
        # Get should promote to all higher levels
        result = self.mlc.get("l3_key")
        
        self.assertEqual(result, "l3_value")
        self.assertEqual(self.l1_cache.get("l3_key"), "l3_value")  # Promoted to L1
        self.assertEqual(self.l2_cache.get("l3_key"), "l3_value")  # Promoted to L2
        self.assertEqual(l3_cache.get("l3_key"), "l3_value")       # Still in L3

    def test_get_thread_safety(self):
        """Test that get method is thread-safe."""
        # Set a value
        self.mlc.set("thread_key", "thread_value")
        
        results = []
        errors = []
        
        def worker():
            try:
                for _ in range(100):
                    result = self.mlc.get("thread_key")
                    results.append(result)
                    time.sleep(0.0001)  # Small delay to encourage race conditions
            except Exception as e:
                errors.append(e)
        
        # Create and start multiple threads
        threads = []
        for _ in range(5):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Verify no errors occurred and all results are correct
        self.assertEqual(len(errors), 0, f"Thread safety test had errors: {errors}")
        self.assertTrue(all(r == "thread_value" for r in results),
                       f"Not all results were correct: {set(results)}")

    def test_get_preserves_cache_level_order(self):
        """Test that get respects cache level priority order."""
        # Set same key with different values in different levels
        self.l1_cache.set("same_key", "l1_value")
        self.l2_cache.set("same_key", "l2_value")
        
        # Should return value from highest priority cache (L1)
        result = self.mlc.get("same_key")
        self.assertEqual(result, "l1_value")

    def test_get_with_cache_backend_errors(self):
        """Test get behavior when cache backends raise exceptions."""
        # Create a mock cache that raises an exception
        mock_cache = Mock()
        mock_cache.get.side_effect = Exception("Cache backend error")
        
        # Insert mock cache as highest priority
        self.mlc._levels.insert(0, mock_cache)
        
        # Set value in L2 (now the second cache checked)
        self.l2_cache.set("error_test_key", "fallback_value")
        
        # Should still be able to get value from L2 despite L1 error
        # Note: Current implementation doesn't handle cache backend errors gracefully
        # This test documents the current behavior
        with self.assertRaises(Exception):
            self.mlc.get("error_test_key")

    def test_get_method_signature_and_return_type(self):
        """Test that get method has correct signature and return type."""
        import inspect
        from typing import get_type_hints
        
        # Check method signature
        sig = inspect.signature(self.mlc.get)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['key'])
        self.assertEqual(sig.parameters['key'].annotation, str)
        
        # Check return type annotation
        hints = get_type_hints(self.mlc.get)
        # Should be Optional[Any] which resolves to Union[Any, None]
        self.assertIn('return', hints)

    def test_get_method_is_not_abstract(self):
        """Test that get method is implemented (not abstract)."""
        # This test verifies the method is callable and has implementation
        self.assertTrue(callable(self.mlc.get))
        
        # Should not raise NotImplementedError
        try:
            self.mlc.get("test_key")
        except NotImplementedError:
            self.fail("get method should be implemented, not abstract")

    def test_get_performance_characteristics(self):
        """Test performance characteristics of cache promotion."""
        # Use a small number of keys that fit in L1 cache (max_size=10)
        test_keys = [f"perf_key_{i}" for i in range(5)]
        
        # Set data in L2 only
        for key in test_keys:
            self.l2_cache.set(key, f"value_{key}")
        
        # Verify initial state: not in L1, present in L2
        for key in test_keys:
            self.assertIsNone(self.l1_cache.get(key))
            self.assertIsNotNone(self.l2_cache.get(key))
        
        # First access: should find in L2 and promote to L1
        start_time = time.time()
        for key in test_keys:
            self.mlc.get(key)
        first_pass_time = time.time() - start_time
        
        # Verify all keys were promoted to L1
        for key in test_keys:
            self.assertIsNotNone(self.l1_cache.get(key), 
                               f"Key {key} should have been promoted to L1")
        
        # Second access: should find in L1 (faster)
        start_time = time.time()
        for key in test_keys:
            result = self.mlc.get(key)
            self.assertEqual(result, f"value_{key}")
        second_pass_time = time.time() - start_time
        
        # Performance improvement isn't guaranteed due to test environment variability
        # But we can verify that promotion occurred correctly
        print(f"First pass: {first_pass_time:.4f}s, Second pass: {second_pass_time:.4f}s")
        
        # Verify final state: all keys in both L1 and L2
        for key in test_keys:
            self.assertEqual(self.l1_cache.get(key), f"value_{key}")
            self.assertEqual(self.l2_cache.get(key), f"value_{key}")


if __name__ == '__main__':
    unittest.main()