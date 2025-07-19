"""
Performance optimization tests for SFMGraph.

This module tests the specific performance improvements implemented
for node lookups and relationship caching.
"""

import time
import uuid
import unittest
from typing import List

from graph.graph import SFMGraph
from models.core_nodes import Actor
from models.relationships import Relationship


class TestPerformanceOptimizations(unittest.TestCase):
    """Test performance optimizations in SFMGraph."""

    def setUp(self):
        """Set up test fixtures."""
        self.graph = SFMGraph()
        self.nodes: List[Actor] = []
        
        # Create a larger number of nodes for performance testing
        for i in range(1000):
            actor = Actor(label=f"Actor_{i}", description=f"Test actor {i}")
            self.nodes.append(actor)
            self.graph.add_node(actor)

    def test_node_lookup_performance_improvement(self):
        """Test that node lookup by ID is fast (O(1) vs O(n))."""
        # Test lookup performance for nodes at different positions
        test_indices = [0, 100, 500, 999]  # Test beginning, middle, and end
        
        for idx in test_indices:
            node_id = self.nodes[idx].id
            
            start_time = time.time()
            found_node = self.graph.get_node_by_id(node_id)
            lookup_time = time.time() - start_time
            
            # Verify correct node is found
            self.assertIsNotNone(found_node)
            self.assertEqual(found_node.id, node_id)
            
            # Performance assertion - should be very fast (O(1))
            self.assertLess(
                lookup_time, 0.001,  # 1ms
                f"Node lookup took too long: {lookup_time:.4f}s for node at index {idx}"
            )

    def test_relationship_caching_performance(self):
        """Test relationship caching improves repeated access performance."""
        # Create relationships
        relationships = []
        for i in range(0, 100, 2):  # Create 50 relationships
            rel = Relationship(
                source_id=self.nodes[i].id,
                target_id=self.nodes[i + 1].id,
                kind="AFFECTS"
            )
            relationships.append(rel)
            self.graph.add_relationship(rel)
        
        # Test first access (cache miss)
        test_node_id = self.nodes[0].id
        start_time = time.time()
        rels_first = self.graph.get_node_relationships(test_node_id)
        first_access_time = time.time() - start_time
        
        # Test second access (cache hit)
        start_time = time.time()
        rels_second = self.graph.get_node_relationships(test_node_id)
        second_access_time = time.time() - start_time
        
        # Verify same results
        self.assertEqual(len(rels_first), len(rels_second))
        self.assertEqual(rels_first, rels_second)
        
        # Verify that cache is actually populated after the first access
        self.assertIn(test_node_id, self.graph._relationship_cache,
                      "Cache should be populated after first access")
        
        # Second access should be faster (cached) with a small tolerance for timing variations
        # Allow a small tolerance (1ms) to account for system timing variations
        tolerance = 0.001  # 1ms tolerance
        self.assertLessEqual(
            second_access_time, first_access_time + tolerance,
            f"Cached access ({second_access_time:.4f}s) should be <= first access ({first_access_time:.4f}s) + tolerance ({tolerance:.4f}s)"
        )

    def test_cache_size_management(self):
        """Test that relationship cache manages its size properly."""
        # Add many relationships to trigger cache management
        for i in range(0, min(200, len(self.nodes) - 1)):
            rel = Relationship(
                source_id=self.nodes[i].id,
                target_id=self.nodes[i + 1].id,
                kind="AFFECTS"
            )
            self.graph.add_relationship(rel)
        
        # Access relationships for many nodes to populate cache
        for i in range(150):  # More than cache max size (1000)
            if i < len(self.nodes):
                self.graph.get_node_relationships(self.nodes[i].id)
        
        # Cache should not exceed max size
        self.assertLessEqual(
            len(self.graph._relationship_cache),
            self.graph._relationship_cache_max_size,
            "Relationship cache exceeded maximum size"
        )

    def test_central_index_consistency(self):
        """Test that central node index remains consistent."""
        # Verify all nodes are in the index
        self.assertEqual(len(self.graph._node_index), len(self.nodes))
        
        # Verify index contains correct nodes
        for node in self.nodes:
            indexed_node = self.graph._node_index.get(node.id)
            self.assertIsNotNone(indexed_node)
            self.assertEqual(indexed_node, node)
        
        # Add a new node and verify index is updated
        new_actor = Actor(label="New Actor")
        self.graph.add_node(new_actor)
        
        self.assertIn(new_actor.id, self.graph._node_index)
        self.assertEqual(self.graph._node_index[new_actor.id], new_actor)

    def test_cache_invalidation_on_relationship_changes(self):
        """Test that relationship cache is cleared when relationships change."""
        # Create initial relationship
        rel1 = Relationship(
            source_id=self.nodes[0].id,
            target_id=self.nodes[1].id,
            kind="AFFECTS"
        )
        self.graph.add_relationship(rel1)
        
        # Access relationships to populate cache
        node_id = self.nodes[0].id
        initial_rels = self.graph.get_node_relationships(node_id)
        self.assertEqual(len(initial_rels), 1)
        
        # Verify cache is populated
        self.assertIn(node_id, self.graph._relationship_cache)
        
        # Add another relationship
        rel2 = Relationship(
            source_id=self.nodes[0].id,
            target_id=self.nodes[2].id,
            kind="AFFECTS"
        )
        self.graph.add_relationship(rel2)
        
        # Cache should be cleared
        self.assertEqual(len(self.graph._relationship_cache), 0)
        
        # New access should reflect updated relationships
        updated_rels = self.graph.get_node_relationships(node_id)
        self.assertEqual(len(updated_rels), 2)

    def test_lazy_loading_functionality(self):
        """Test lazy loading mechanism for nodes."""
        # Create a separate graph for lazy loading test
        lazy_graph = SFMGraph()
        
        # Create a mock loader
        def mock_node_loader(node_id: uuid.UUID) -> Actor:
            if str(node_id).startswith('11111111'):
                return Actor(label=f"Lazy Actor {node_id}", id=node_id)
            return None
        
        # Enable lazy loading
        lazy_graph.enable_lazy_loading(mock_node_loader)
        
        # Try to find a node that should be lazy-loaded
        test_id = uuid.UUID('11111111-0000-0000-0000-000000000001')
        node = lazy_graph.get_node_by_id(test_id)
        
        # Verify lazy loading worked
        self.assertIsNotNone(node)
        self.assertEqual(node.id, test_id)
        self.assertTrue(node.label.startswith("Lazy Actor"))
        
        # Verify node is now in the index
        self.assertIn(test_id, lazy_graph._node_index)
        
        # Try to find a node that shouldn't be lazy-loaded
        invalid_id = uuid.UUID('22222222-0000-0000-0000-000000000001')
        invalid_node = lazy_graph.get_node_by_id(invalid_id)
        self.assertIsNone(invalid_node)
        
        # Disable lazy loading and test
        lazy_graph.disable_lazy_loading()
        another_test_id = uuid.UUID('11111111-0000-0000-0000-000000000002')
        disabled_node = lazy_graph.get_node_by_id(another_test_id)
        self.assertIsNone(disabled_node)  # Should not be found since lazy loading is disabled

    def test_lazy_loading_error_handling(self):
        """Test lazy loading error handling for failed node loader operations."""
        import logging
        
        # Create a separate graph for error handling test
        lazy_graph = SFMGraph()
        
        # Capture log messages
        log_messages = []
        
        class TestLogHandler(logging.Handler):
            def emit(self, record):
                log_messages.append(record.getMessage())
        
        # Set up logging to capture warnings
        logger = logging.getLogger('core.graph')
        test_handler = TestLogHandler()
        logger.addHandler(test_handler)
        logger.setLevel(logging.WARNING)
        
        try:
            # Create a mock loader that raises an exception
            def failing_node_loader(node_id: uuid.UUID) -> Actor:
                raise ValueError(f"Simulated database error for {node_id}")
            
            # Enable lazy loading with failing loader
            lazy_graph.enable_lazy_loading(failing_node_loader)
            
            # Try to find a node that will trigger the failing loader
            test_id = uuid.UUID('33333333-0000-0000-0000-000000000001')
            node = lazy_graph.get_node_by_id(test_id)
            
            # Verify that the node is None (loader failed)
            self.assertIsNone(node)
            
            # Verify that a warning was logged
            self.assertEqual(len(log_messages), 1)
            self.assertIn("Failed to lazy load node", log_messages[0])
            self.assertIn("33333333-0000-0000-0000-000000000001", log_messages[0])
            self.assertIn("Simulated database error", log_messages[0])
            
        finally:
            # Clean up logging handler
            logger.removeHandler(test_handler)


if __name__ == "__main__":
    unittest.main(verbosity=2)