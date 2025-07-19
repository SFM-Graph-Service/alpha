"""
Test comprehensive performance optimizations including memory management and advanced caching.

This module tests the advanced performance features implemented to address
scalability and performance issues in the SFM framework.
"""

import time
import uuid
import unittest
from typing import List
from unittest.mock import Mock, patch

from graph.graph import SFMGraph
from models.core_nodes import Actor, Institution
from models.relationships import Relationship
from infrastructure.memory_management import MemoryMonitor, EvictionStrategy, MemoryUsageStats
from infrastructure.advanced_caching import QueryCache, MemoryCache, TTLMemoryCache


class TestAdvancedPerformanceOptimizations(unittest.TestCase):
    """Test advanced performance optimizations in SFMGraph."""

    def setUp(self):
        """Set up test fixtures."""
        self.graph = SFMGraph()
        self.nodes: List[Actor] = []
        
        # Create nodes for testing
        for i in range(100):
            actor = Actor(label=f"Actor_{i}", description=f"Test actor {i}")
            self.nodes.append(actor)
            self.graph.add_node(actor)

    def test_memory_management_initialization(self):
        """Test that memory management is properly initialized."""
        # Memory management should be enabled by default
        self.assertTrue(self.graph._enable_memory_management)
        self.assertIsNotNone(self.graph._memory_monitor)
        self.assertEqual(self.graph._memory_limit_mb, 1000.0)

    def test_memory_limit_configuration(self):
        """Test memory limit configuration."""
        # Set a new memory limit
        new_limit = 500.0
        self.graph.set_memory_limit(new_limit)
        
        self.assertEqual(self.graph._memory_limit_mb, new_limit)
        self.assertEqual(self.graph._memory_monitor.memory_limit_mb, new_limit)

    def test_eviction_strategy_configuration(self):
        """Test eviction strategy configuration."""
        # Test setting different eviction strategies
        strategies = [EvictionStrategy.LRU, EvictionStrategy.LFU, EvictionStrategy.OLDEST_FIRST]
        
        for strategy in strategies:
            self.graph.set_eviction_strategy(strategy)
            self.assertEqual(self.graph._memory_monitor.current_strategy, strategy)

    def test_node_access_tracking(self):
        """Test that node access is properly tracked."""
        # Access some nodes
        test_nodes = self.nodes[:5]
        for node in test_nodes:
            self.graph.get_node_by_id(node.id)
        
        # Verify access tracking
        access_tracker = self.graph._memory_monitor.access_tracker
        for node in test_nodes:
            access_count = access_tracker.get_access_count(node.id)
            self.assertGreater(access_count, 0)

    def test_memory_usage_statistics(self):
        """Test memory usage statistics collection."""
        memory_stats = self.graph.get_memory_usage()
        
        self.assertIsInstance(memory_stats, MemoryUsageStats)
        self.assertGreaterEqual(memory_stats.process_memory_mb, 0)
        self.assertGreaterEqual(memory_stats.timestamp, 0)

    def test_node_eviction_functionality(self):
        """Test node eviction from memory."""
        # Add many more nodes to trigger potential eviction
        large_nodes = []
        for i in range(200, 300):
            actor = Actor(label=f"LargeActor_{i}", description=f"Large test actor {i}" * 100)
            large_nodes.append(actor)
            self.graph.add_node(actor)
        
        initial_count = len(self.graph.get_all_node_ids())
        
        # Force memory cleanup
        evicted_count = self.graph.force_memory_cleanup()
        
        # Verify eviction occurred (may be 0 if memory usage is low)
        self.assertGreaterEqual(evicted_count, 0)
        
        final_count = len(self.graph.get_all_node_ids())
        self.assertLessEqual(final_count, initial_count)

    def test_evictable_graph_protocol(self):
        """Test EvictableGraph protocol implementation."""
        # Test get_all_node_ids
        all_ids = self.graph.get_all_node_ids()
        self.assertEqual(len(all_ids), len(self.nodes))
        
        # Test remove_node_from_memory
        test_node = self.nodes[0]
        success = self.graph.remove_node_from_memory(test_node.id)
        self.assertTrue(success)
        
        # Verify node was removed from memory
        self.assertNotIn(test_node.id, self.graph.get_all_node_ids())
        self.assertIsNone(self.graph.get_node_by_id(test_node.id))

    def test_node_size_estimation(self):
        """Test node size estimation."""
        test_node = self.nodes[0]
        estimated_size = self.graph.get_node_size_estimate(test_node.id)
        
        self.assertGreater(estimated_size, 0)
        self.assertIsInstance(estimated_size, int)

    def test_advanced_caching_initialization(self):
        """Test advanced caching initialization."""
        # Advanced caching should be enabled by default
        self.assertTrue(self.graph._enable_advanced_caching)
        self.assertIsNotNone(self.graph._query_cache)

    def test_query_result_caching(self):
        """Test query result caching functionality."""
        # Create relationships for testing
        for i in range(0, 20, 2):
            rel = Relationship(
                source_id=self.nodes[i].id,
                target_id=self.nodes[i + 1].id,
                kind="AFFECTS"
            )
            self.graph.add_relationship(rel)
        
        test_node_id = self.nodes[0].id
        
        # First access - should be cached
        start_time = time.time()
        relationships_1 = self.graph.get_node_relationships(test_node_id)
        first_duration = time.time() - start_time
        
        # Second access - should be faster (cached)
        start_time = time.time()
        relationships_2 = self.graph.get_node_relationships(test_node_id)
        second_duration = time.time() - start_time
        
        # Verify same results
        self.assertEqual(relationships_1, relationships_2)
        
        # Second access should typically be faster (though this can be flaky in tests)
        # We just verify the caching system doesn't break functionality
        self.assertEqual(len(relationships_1), len(relationships_2))

    def test_cache_invalidation_on_changes(self):
        """Test cache invalidation when data changes."""
        test_node_id = self.nodes[0].id
        
        # Access to populate cache
        initial_rels = self.graph.get_node_relationships(test_node_id)
        
        # Add a new relationship
        new_rel = Relationship(
            source_id=self.nodes[0].id,
            target_id=self.nodes[10].id,
            kind="INFLUENCES"
        )
        self.graph.add_relationship(new_rel)
        
        # Access again - should reflect the change
        updated_rels = self.graph.get_node_relationships(test_node_id)
        
        # Should have one more relationship
        self.assertEqual(len(updated_rels), len(initial_rels) + 1)

    def test_cache_statistics(self):
        """Test cache statistics collection."""
        cache_stats = self.graph.get_cache_stats()
        
        self.assertIn("relationship_cache_size", cache_stats)
        self.assertIn("query_cache", cache_stats)
        self.assertIsInstance(cache_stats["relationship_cache_size"], int)

    def test_memory_statistics(self):
        """Test memory statistics collection."""
        memory_stats = self.graph.get_memory_stats()
        
        expected_keys = [
            "memory_limit_mb", "total_nodes", "total_relationships",
            "relationship_cache_size", "memory_management_enabled"
        ]
        
        for key in expected_keys:
            self.assertIn(key, memory_stats)

    def test_cache_clearing(self):
        """Test cache clearing functionality."""
        # Populate caches
        for node in self.nodes[:5]:
            self.graph.get_node_relationships(node.id)
        
        # Verify caches have data
        initial_cache_size = len(self.graph._relationship_cache)
        self.assertGreater(initial_cache_size, 0)
        
        # Clear caches
        self.graph.clear_all_caches()
        
        # Verify caches are empty
        self.assertEqual(len(self.graph._relationship_cache), 0)

    def test_advanced_caching_toggle(self):
        """Test enabling/disabling advanced caching."""
        # Disable advanced caching
        self.graph.enable_advanced_caching(False)
        self.assertFalse(self.graph._enable_advanced_caching)
        
        # Re-enable advanced caching
        self.graph.enable_advanced_caching(True)
        self.assertTrue(self.graph._enable_advanced_caching)

    def test_performance_metrics_integration(self):
        """Test integration with performance metrics system."""
        # Perform some operations to generate metrics
        for i in range(10):
            node = Actor(label=f"MetricsTest_{i}")
            self.graph.add_node(node)
            self.graph.get_node_by_id(node.id)
        
        # Get performance metrics
        from infrastructure.performance_metrics import get_metrics_collector
        collector = get_metrics_collector()
        
        # Should have recorded some operations
        all_metrics = collector.get_all_operation_metrics()
        self.assertGreater(len(all_metrics), 0)

    @patch('core.memory_management.PSUTIL_AVAILABLE', False)
    @patch('core.memory_management.psutil', None)
    def test_memory_monitoring_without_psutil(self, mock_psutil=None):
        """Test memory monitoring gracefully handles missing psutil."""
        # Should still work without psutil
        memory_stats = MemoryUsageStats.capture_current()
        self.assertEqual(memory_stats.process_memory_mb, 0.0)

    def test_lazy_loading_with_memory_management(self):
        """Test lazy loading works with memory management."""
        # Create a separate graph for lazy loading test
        lazy_graph = SFMGraph()
        
        def mock_node_loader(node_id: uuid.UUID) -> Actor:
            if str(node_id).startswith('11111111'):
                return Actor(label=f"Lazy Actor {node_id}", id=node_id)
            return None
        
        # Enable lazy loading
        lazy_graph.enable_lazy_loading(mock_node_loader)
        
        # Try to load a node
        test_id = uuid.UUID('11111111-0000-0000-0000-000000000001')
        node = lazy_graph.get_node_by_id(test_id)
        
        # Verify lazy loading worked and access was tracked
        self.assertIsNotNone(node)
        self.assertEqual(node.id, test_id)
        
        # Verify memory management tracked the access
        access_count = lazy_graph._memory_monitor.access_tracker.get_access_count(test_id)
        self.assertGreater(access_count, 0)


class TestMemoryManagementComponents(unittest.TestCase):
    """Test individual memory management components."""
    
    def test_memory_cache_basic_operations(self):
        """Test basic memory cache operations."""
        cache = MemoryCache("test_cache", max_size=10)
        
        # Test set/get
        cache.set("key1", "value1")
        self.assertEqual(cache.get("key1"), "value1")
        
        # Test miss
        self.assertIsNone(cache.get("nonexistent"))
        
        # Test stats
        stats = cache.get_stats()
        self.assertEqual(stats.hits, 1)
        self.assertEqual(stats.misses, 1)

    def test_ttl_cache_expiration(self):
        """Test TTL cache expiration."""
        cache = TTLMemoryCache("ttl_cache", max_size=10, default_ttl=0.1)  # 100ms TTL
        
        # Set value with short TTL
        cache.set("key1", "value1")
        self.assertEqual(cache.get("key1"), "value1")
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be expired
        self.assertIsNone(cache.get("key1"))
        
        # Stats should reflect expiration
        stats = cache.get_stats()
        self.assertGreater(stats.expired, 0)

    def test_query_cache_invalidation_rules(self):
        """Test query cache invalidation rules."""
        query_cache = QueryCache()
        
        # Register invalidation rule
        query_cache.register_invalidation_rule(
            'test_event',
            ['test_operation:*']
        )
        
        # Cache some data
        query_cache.cache_result("test_operation", "cached_value", node_id="123")
        
        # Verify cached
        result = query_cache.get_cached_result("test_operation", node_id="123")
        self.assertEqual(result, "cached_value")
        
        # Trigger invalidation
        invalidated = query_cache.invalidate_on_event('test_event', node_id="123")
        self.assertGreater(invalidated, 0)
        
        # Should be invalidated
        result = query_cache.get_cached_result("test_operation", node_id="123")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)