"""
Test comprehensive advanced caching implementations.

This module tests the new caching features including Redis backend,
cache warming, enhanced decorators, and monitoring.
"""

import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from core.advanced_caching import (
    MemoryCache, TTLMemoryCache, RedisCache, MultiLevelCache,
    QueryCache, CacheWarmer, CacheMetrics, cached, CacheConfig,
    create_cache_manager, cached_operation
)
from core.cache_config import CacheConfigManager, CACHE_CONFIG
from core.cache_monitoring import CacheMonitor, monitor_cache_performance


class TestRedisCacheBackend(unittest.TestCase):
    """Test Redis cache backend functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock Redis client
        self.mock_redis = Mock()
        self.mock_redis.ping.return_value = True
        
    def test_redis_cache_initialization(self):
        """Test Redis cache initialization."""
        cache = RedisCache("test_cache", redis_client=self.mock_redis)
        
        self.assertEqual(cache.name, "test_cache")
        self.assertEqual(cache.default_ttl, 3600)
        self.mock_redis.ping.assert_called_once()
    
    def test_redis_cache_operations(self):
        """Test Redis cache get/set operations."""
        cache = RedisCache("test_cache", redis_client=self.mock_redis)
        
        # Test set operation
        cache.set("key1", "value1", ttl=300)
        self.mock_redis.setex.assert_called_once()
        
        # Test get operation (cache hit)
        import pickle
        self.mock_redis.get.return_value = pickle.dumps("value1")
        result = cache.get("key1")
        self.assertEqual(result, "value1")
        
        # Test get operation (cache miss)
        self.mock_redis.get.return_value = None
        result = cache.get("missing_key")
        self.assertIsNone(result)
    
    def test_redis_cache_delete(self):
        """Test Redis cache delete operation."""
        cache = RedisCache("test_cache", redis_client=self.mock_redis)
        
        self.mock_redis.delete.return_value = 1
        result = cache.delete("key1")
        self.assertTrue(result)
        
        self.mock_redis.delete.return_value = 0
        result = cache.delete("missing_key")
        self.assertFalse(result)
    
    def test_redis_cache_clear(self):
        """Test Redis cache clear operation."""
        cache = RedisCache("test_cache", redis_client=self.mock_redis)
        
        self.mock_redis.keys.return_value = [b"test_cache:key1", b"test_cache:key2"]
        cache.clear()
        self.mock_redis.delete.assert_called_once()
    
    def test_redis_cache_pattern_deletion(self):
        """Test Redis cache pattern deletion."""
        cache = RedisCache("test_cache", redis_client=self.mock_redis)
        
        self.mock_redis.keys.return_value = [b"test_cache:user:*"]
        self.mock_redis.delete.return_value = 2
        deleted_count = cache.delete_pattern("user:*")
        self.assertEqual(deleted_count, 2)


class TestCacheWarmer(unittest.TestCase):
    """Test cache warming functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.query_cache = QueryCache()
        self.mock_graph = Mock()
        self.warmer = CacheWarmer(self.query_cache, self.mock_graph)
    
    def test_cache_warmer_initialization(self):
        """Test cache warmer initialization."""
        self.assertEqual(self.warmer.cache, self.query_cache)
        self.assertEqual(self.warmer.graph, self.mock_graph)
        self.assertEqual(len(self.warmer._warming_strategies), 0)
    
    def test_register_warming_strategy(self):
        """Test registering warming strategies."""
        def mock_strategy():
            pass
        
        self.warmer.register_warming_strategy("test_strategy", mock_strategy)
        self.assertIn("test_strategy", self.warmer._warming_strategies)
        self.assertEqual(self.warmer._warming_strategies["test_strategy"], mock_strategy)
    
    def test_warm_cache_with_specific_strategy(self):
        """Test warming cache with specific strategy."""
        mock_strategy = Mock()
        self.warmer.register_warming_strategy("test_strategy", mock_strategy)
        
        self.warmer.warm_cache("test_strategy")
        mock_strategy.assert_called_once()
    
    def test_warm_cache_all_strategies(self):
        """Test warming cache with all strategies."""
        mock_strategy1 = Mock()
        mock_strategy2 = Mock()
        self.warmer.register_warming_strategy("strategy1", mock_strategy1)
        self.warmer.register_warming_strategy("strategy2", mock_strategy2)
        
        self.warmer.warm_cache()
        mock_strategy1.assert_called_once()
        mock_strategy2.assert_called_once()
    
    def test_warm_frequently_accessed_nodes(self):
        """Test warming frequently accessed nodes."""
        node_ids = ["node1", "node2", "node3"]
        
        self.warmer.warm_frequently_accessed_nodes(node_ids)
        
        # Verify graph methods were called
        self.assertEqual(self.mock_graph.get_node_relationships.call_count, 3)
        self.assertEqual(self.mock_graph.get_node_by_id.call_count, 3)
    
    def test_warm_common_queries(self):
        """Test warming common queries."""
        self.warmer.warm_common_queries()
        
        # Verify common graph methods were called
        self.mock_graph.get_node_count.assert_called_once()
        self.mock_graph.get_relationship_count.assert_called_once()


class TestCacheMetrics(unittest.TestCase):
    """Test cache metrics functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.metrics = CacheMetrics(enabled=False)  # Disable Prometheus for testing
    
    def test_cache_metrics_initialization(self):
        """Test cache metrics initialization."""
        self.assertFalse(self.metrics.enabled)
    
    def test_cache_metrics_record_operations(self):
        """Test recording cache operations."""
        # These should not raise exceptions even when disabled
        self.metrics.record_hit("test_cache", "memory")
        self.metrics.record_miss("test_cache", "memory")
        self.metrics.record_eviction("test_cache", "memory")
        self.metrics.record_operation("get", "test_cache")
        self.metrics.update_hit_rate("test_cache", "memory", 0.85)
        self.metrics.update_size("test_cache", "memory", 1024)


class TestCacheDecorators(unittest.TestCase):
    """Test cache decorator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.cache = QueryCache()
    
    def test_cached_decorator_basic(self):
        """Test basic cached decorator functionality."""
        call_count = 0
        
        @cached(ttl=300, cache_instance=self.cache)
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute function
        result1 = expensive_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Second call should use cache
        result2 = expensive_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Function not called again
    
    def test_cached_decorator_with_custom_key_function(self):
        """Test cached decorator with custom key function."""
        def custom_key_func(x: int, y: int) -> str:
            return f"custom:{x}:{y}"
        
        @cached(ttl=300, cache_key_func=custom_key_func, cache_instance=self.cache)
        def add_function(x: int, y: int) -> int:
            return x + y
        
        result = add_function(3, 4)
        self.assertEqual(result, 7)
        
        # Check that custom key was used
        cached_result = self.cache.get_cached_result("add_function", "custom:3:4")
        self.assertEqual(cached_result, 7)
    
    def test_cached_operation_decorator(self):
        """Test cached_operation decorator."""
        call_count = 0
        
        @cached_operation(self.cache, "test_operation", ttl=300)
        def test_function(value: str) -> str:
            nonlocal call_count
            call_count += 1
            return value.upper()
        
        # First call
        result1 = test_function("hello")
        self.assertEqual(result1, "HELLO")
        self.assertEqual(call_count, 1)
        
        # Second call should use cache
        result2 = test_function("hello")
        self.assertEqual(result2, "HELLO")
        self.assertEqual(call_count, 1)


class TestCacheConfiguration(unittest.TestCase):
    """Test cache configuration functionality."""

    def test_cache_config_manager_initialization(self):
        """Test cache config manager initialization."""
        config_manager = CacheConfigManager()
        self.assertEqual(config_manager.config, CACHE_CONFIG)
    
    def test_cache_config_manager_get_layer_config(self):
        """Test getting layer configuration."""
        config_manager = CacheConfigManager()
        
        # Test getting existing layer config
        query_config = config_manager.get_layer_config("query_cache")
        self.assertEqual(query_config.backend, "memory")
        self.assertEqual(query_config.ttl, 1800)
        self.assertEqual(query_config.max_size, 5000)
        
        # Test getting default config for non-existent layer
        custom_config = config_manager.get_layer_config("non_existent")
        self.assertEqual(custom_config.backend, "redis")  # Default backend
    
    def test_cache_config_manager_get_redis_config(self):
        """Test getting Redis configuration."""
        config_manager = CacheConfigManager()
        redis_config = config_manager.get_redis_config()
        
        self.assertEqual(redis_config.host, "localhost")
        self.assertEqual(redis_config.port, 6379)
        self.assertEqual(redis_config.db, 0)
        self.assertIsNone(redis_config.password)
    
    def test_cache_config_manager_update_config(self):
        """Test updating configuration."""
        config_manager = CacheConfigManager()
        
        updates = {
            "new_cache": {
                "backend": "memory",
                "ttl": 600,
                "max_size": 2000
            }
        }
        
        config_manager.update_config(updates)
        new_config = config_manager.get_layer_config("new_cache")
        self.assertEqual(new_config.backend, "memory")
        self.assertEqual(new_config.ttl, 600)
        self.assertEqual(new_config.max_size, 2000)


class TestCacheFactory(unittest.TestCase):
    """Test cache factory functionality."""

    def test_create_cache_manager_basic(self):
        """Test creating cache manager with basic config."""
        config = CacheConfig(
            memory_cache_size=2000,
            default_ttl=1800,
            enable_redis=False
        )
        
        cache_manager = create_cache_manager(config)
        self.assertIsInstance(cache_manager, QueryCache)
    
    @patch('core.advanced_caching.REDIS_AVAILABLE', True)
    @patch('core.advanced_caching.RedisCache')
    def test_create_cache_manager_with_redis(self, mock_redis_cache):
        """Test creating cache manager with Redis enabled."""
        config = CacheConfig(
            memory_cache_size=2000,
            default_ttl=1800,
            enable_redis=True,
            redis_host="localhost",
            redis_port=6379
        )
        
        # Mock Redis cache instance
        mock_redis_instance = Mock()
        mock_redis_cache.return_value = mock_redis_instance
        
        cache_manager = create_cache_manager(config)
        self.assertIsInstance(cache_manager, QueryCache)
        
        # Verify Redis cache was created with correct parameters
        mock_redis_cache.assert_called_once_with(
            name="redis_cache",
            host="localhost",
            port=6379,
            db=0,
            password=None,
            max_size=10000,
            default_ttl=1800
        )


class TestCacheMonitoring(unittest.TestCase):
    """Test cache monitoring functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.monitor = CacheMonitor("test_cache", enable_prometheus=False)
    
    def test_cache_monitor_initialization(self):
        """Test cache monitor initialization."""
        self.assertEqual(self.monitor.cache_name, "test_cache")
        self.assertFalse(self.monitor.enable_prometheus)
    
    def test_cache_monitor_record_operations(self):
        """Test recording cache operations."""
        # These should not raise exceptions
        self.monitor.record_hit("memory")
        self.monitor.record_miss("memory")
        self.monitor.record_eviction("memory")
        self.monitor.record_operation("get")
        self.monitor.update_hit_rate(0.85, "memory")
        self.monitor.update_cache_size(1024, "memory")
    
    def test_cache_monitor_time_operation(self):
        """Test timing cache operations."""
        with self.monitor.time_operation("test_op"):
            time.sleep(0.01)  # Simulate some work
        
        metrics = self.monitor.get_performance_metrics()
        self.assertGreater(metrics.average_response_time, 0)
    
    def test_monitor_cache_performance(self):
        """Test monitoring cache performance across multiple caches."""
        # Create mock caches with stats
        mock_cache1 = Mock()
        mock_cache1.get_stats.return_value = Mock(
            hits=80, total_operations=100, size=500, max_size=1000,
            memory_usage_bytes=1024 * 1024
        )
        
        mock_cache2 = Mock()
        mock_cache2.get_stats.return_value = Mock(
            hits=60, total_operations=100, size=800, max_size=1000,
            memory_usage_bytes=2 * 1024 * 1024
        )
        
        caches = {"cache1": mock_cache1, "cache2": mock_cache2}
        
        performance_metrics = monitor_cache_performance(caches)
        
        self.assertEqual(len(performance_metrics), 2)
        self.assertIn("cache1", performance_metrics)
        self.assertIn("cache2", performance_metrics)
        
        # Check calculated metrics
        cache1_metrics = performance_metrics["cache1"]
        self.assertEqual(cache1_metrics.hit_rate, 0.8)
        self.assertEqual(cache1_metrics.size_utilization, 0.5)
        self.assertEqual(cache1_metrics.memory_usage_mb, 1.0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the caching system."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = CacheConfig(
            memory_cache_size=100,
            default_ttl=300,
            enable_redis=False
        )
        self.cache_manager = create_cache_manager(self.config)
        self.warmer = CacheWarmer(self.cache_manager)
    
    def test_end_to_end_caching_workflow(self):
        """Test end-to-end caching workflow."""
        # Test caching a simple operation
        @cached(ttl=300, cache_instance=self.cache_manager)
        def fibonacci(n: int) -> int:
            if n <= 1:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)
        
        # First call - should compute
        result1 = fibonacci(10)
        self.assertEqual(result1, 55)
        
        # Second call - should use cache
        result2 = fibonacci(10)
        self.assertEqual(result2, 55)
        
        # Verify cache statistics
        stats = self.cache_manager.get_stats()
        self.assertGreater(stats["recent_queries"]["hits"], 0)
    
    def test_cache_warming_integration(self):
        """Test cache warming integration."""
        # Register a warming strategy
        def warm_fibonacci():
            @cached(ttl=300, cache_instance=self.cache_manager)
            def fib(n: int) -> int:
                return n * 2  # Simplified for testing
            
            # Pre-warm some values
            for i in range(1, 6):
                fib(i)
        
        self.warmer.register_warming_strategy("fibonacci", warm_fibonacci)
        
        # Warm the cache
        self.warmer.warm_cache("fibonacci")
        
        # Verify cache has been warmed
        stats = self.cache_manager.get_stats()
        self.assertGreater(stats["recent_queries"]["size"], 0)


if __name__ == "__main__":
    unittest.main()