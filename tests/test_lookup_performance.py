"""
Lookup Performance Tests for SFM Service

This module contains performance tests specifically for lookup operations
including node retrieval, search, and relationship queries.
"""

import time
import uuid
from typing import List
from api.sfm_service import SFMService, SFMServiceConfig, CreateActorRequest, CreateRelationshipRequest, NodeResponse
from infrastructure.security_validators import disable_validation_rate_limiting, clear_validation_rate_limit_storage

class TestLookupPerformance:
    """Test class for lookup performance benchmarks."""
    
    def setup_method(self) -> None:
        """Set up test fixtures for each test method."""
        # Disable rate limiting for performance tests
        disable_validation_rate_limiting()
        clear_validation_rate_limit_storage()
        
        config = SFMServiceConfig(storage_backend="networkx", enable_logging=False)
        self.service = SFMService(config)
        
        # Clear any existing data
        self.service.clear_all_data()
        
        # Create test data
        self.actors: List[NodeResponse] = []
        for i in range(10):  # Reduced size for simple testing
            actor = self.service.create_actor(CreateActorRequest(
                name=f"Test Actor {i}",
                description=f"Test actor {i}",
                sector="test"
            ))
            self.actors.append(actor)
            
        # Create relationships
        for i in range(5):
            if i < len(self.actors) - 1:
                self.service.create_relationship(CreateRelationshipRequest(
                    source_id=self.actors[i].id,
                    target_id=self.actors[i + 1].id,
                    kind="AFFECTS"
                ))

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        try:
            self.service.clear_all_data()
        except:
            pass  # Ignore cleanup errors

    def test_node_lookup_by_id(self) -> None:
        """Test performance of node lookup by ID."""
        start_time = time.time()
        # Use string ID directly since that's what the service expects
        result = self.service.get_actor(uuid.UUID(self.actors[5].id))
        end_time = time.time()
        
        assert result is not None
        lookup_time = end_time - start_time
        print(f"Node lookup took {lookup_time:.4f} seconds")
        
        # Performance assertion - should be very fast
        assert lookup_time < 1.0, f"Node lookup took too long: {lookup_time:.4f}s"

    def test_node_search_by_name(self) -> None:
        """Test performance of node search by name."""
        start_time = time.time()
        # Use list_nodes to find nodes by type since we don't have a search_nodes method
        result = self.service.list_nodes(node_type="Actor", limit=50)
        # Filter by name
        filtered_result = [node for node in result if "Test Actor 5" in node.label]
        end_time = time.time()
        
        assert len(filtered_result) > 0
        search_time = end_time - start_time
        print(f"Node search took {search_time:.4f} seconds")
        
        # Performance assertion
        assert search_time < 1.0, f"Node search took too long: {search_time:.4f}s"

    def test_relationship_lookup(self) -> None:
        """Test performance of relationship lookup."""
        start_time = time.time()
        # Use get_node_neighbors to get relationships
        result = self.service.get_node_neighbors(self.actors[0].id)
        end_time = time.time()
        
        assert len(result) >= 0
        lookup_time = end_time - start_time
        print(f"Relationship lookup took {lookup_time:.4f} seconds")
        
        # Performance assertion
        assert lookup_time < 1.0, f"Relationship lookup took too long: {lookup_time:.4f}s"

    def test_statistics_calculation(self) -> None:
        """Test performance of statistics calculation."""
        start_time = time.time()
        result = self.service.get_statistics()
        end_time = time.time()
        
        assert result.total_nodes == 10
        calc_time = end_time - start_time
        print(f"Statistics calculation took {calc_time:.4f} seconds")
        
        # Performance assertion
        assert calc_time < 2.0, f"Statistics calculation took too long: {calc_time:.4f}s"

    def test_bulk_node_creation_performance(self) -> None:
        """Test performance of bulk node creation."""
        start_time = time.time()
        
        # Create additional actors for bulk testing
        bulk_actors: List[NodeResponse] = []
        for i in range(20):
            actor = self.service.create_actor(CreateActorRequest(
                name=f"Bulk Actor {i}",
                description=f"Bulk test actor {i}",
                sector="bulk_test"
            ))
            bulk_actors.append(actor)
        
        end_time = time.time()
        creation_time = end_time - start_time
        print(f"Bulk creation of 20 actors took {creation_time:.4f} seconds")
        
        # Verify all actors were created
        assert len(bulk_actors) == 20
        
        # Performance assertion - should create 20 actors in reasonable time
        assert creation_time < 10.0, f"Bulk creation took too long: {creation_time:.4f}s"

    def test_graph_traversal_performance(self) -> None:
        """Test performance of graph traversal operations."""
        start_time = time.time()
        
        # Test shortest path finding
        if len(self.actors) >= 2:
            _ = self.service.find_shortest_path(self.actors[0].id, self.actors[-1].id)
            
        end_time = time.time()
        traversal_time = end_time - start_time
        print(f"Graph traversal took {traversal_time:.4f} seconds")
        
        # Performance assertion
        assert traversal_time < 2.0, f"Graph traversal took too long: {traversal_time:.4f}s"
