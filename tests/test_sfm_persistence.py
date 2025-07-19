"""
Test suite for SFM Persistence Manager

This module contains comprehensive tests for the SFM persistence functionality,
demonstrating usage patterns and validating storage/retrieval operations.
"""

import unittest
import tempfile
import shutil
import uuid
from pathlib import Path
from datetime import datetime

from graph.sfm_persistence import (
    SFMGraphSerializer, 
    SFMPersistenceManager,
    StorageFormat, 
    PersistenceConfig,
    save_sfm_graph,
    load_sfm_graph,
    list_sfm_graphs
)
from models import ( Actor, Institution, Resource, Process, Flow, 
    Policy, Relationship
)
from models.sfm_enums import ResourceType, RelationshipKind, InstitutionLayer
from graph.graph import SFMGraph


class TestSFMPersistence(unittest.TestCase):
    """Test cases for SFM persistence functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = PersistenceConfig(
            base_path=self.temp_dir,
            enable_versioning=True,
            enable_compression=False,
            validate_on_save=True,
            validate_on_load=True
        )
        self.manager = SFMPersistenceManager(self.config)
        
        # Create a sample graph for testing
        self.sample_graph = self._create_sample_graph()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def _create_sample_graph(self) -> SFMGraph:
        """Create a sample SFM graph for testing."""
        graph = SFMGraph(
            name="Test Graph",
            description="A sample graph for testing persistence"
        )
        
        # Add actors
        farmer = Actor(
            label="Local Farmer",
            description="Small-scale agricultural producer",
            sector="agriculture",
            legal_form="individual"
        )
        usda = Actor(
            label="USDA",
            description="United States Department of Agriculture",
            sector="government",
            legal_form="federal_agency"
        )
        
        graph.actors[farmer.id] = farmer
        graph.actors[usda.id] = usda
        
        # Add institutions
        farm_bill = Institution(
            label="Farm Bill 2023",
            description="Federal agricultural policy legislation",
            layer=InstitutionLayer.FORMAL_RULE
        )
        graph.institutions[farm_bill.id] = farm_bill
        
        # Add resources
        corn = Resource(
            label="Corn",
            description="Maize crop production",
            rtype=ResourceType.NATURAL,
            unit="bushels"
        )
        graph.resources[corn.id] = corn
        
        # Add policies
        subsidy_policy = Policy(
            label="Crop Subsidy Program",
            description="Financial support for crop production",
            authority="USDA",
            enforcement=0.8,
            target_sectors=["agriculture"]
        )
        graph.policies[subsidy_policy.id] = subsidy_policy
        
        # Add relationships
        implements_rel = Relationship(
            source_id=usda.id,
            target_id=subsidy_policy.id,
            kind=RelationshipKind.IMPLEMENTS,
            weight=1.0
        )
        
        benefits_rel = Relationship(
            source_id=farmer.id,
            target_id=subsidy_policy.id,
            kind=RelationshipKind.PARTICIPATES_IN,
            weight=0.8
        )
        
        produces_rel = Relationship(
            source_id=farmer.id,
            target_id=corn.id,
            kind=RelationshipKind.PRODUCES,
            weight=1.0
        )
        
        graph.relationships[implements_rel.id] = implements_rel
        graph.relationships[benefits_rel.id] = benefits_rel
        graph.relationships[produces_rel.id] = produces_rel
        
        return graph
    
    def test_save_and_load_basic(self):
        """Test basic save and load operations."""
        graph_id = "test_basic"
        
        # Save graph
        metadata = self.manager.save_graph(graph_id, self.sample_graph)
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.graph_id, graph_id)
        self.assertEqual(metadata.version, 1)
        
        # Load graph
        loaded_graph = self.manager.load_graph(graph_id)
        self.assertIsNotNone(loaded_graph)
        self.assertEqual(loaded_graph.name, self.sample_graph.name)
        self.assertEqual(len(loaded_graph.actors), len(self.sample_graph.actors))
        self.assertEqual(len(loaded_graph.relationships), len(self.sample_graph.relationships))
    
    def test_versioning(self):
        """Test graph versioning functionality."""
        graph_id = "test_versioning"
        
        # Save initial version
        metadata_v1 = self.manager.save_graph(graph_id, self.sample_graph)
        self.assertEqual(metadata_v1.version, 1)
        
        # Modify graph and save again (use a deep copy to avoid mutating the original)
        import copy
        modified_graph = copy.deepcopy(self.sample_graph)
        new_actor = Actor(label="New Actor", description="Added in version 2")
        modified_graph.actors[new_actor.id] = new_actor
        
        metadata_v2 = self.manager.save_graph(graph_id, modified_graph)
        self.assertEqual(metadata_v2.version, 2)
        
        # Load specific versions
        graph_v1 = self.manager.load_graph(graph_id, version=1)
        graph_v2 = self.manager.load_graph(graph_id, version=2)
        
        self.assertEqual(len(graph_v1.actors), 2)  # Original actors
        self.assertEqual(len(graph_v2.actors), 3)  # Original + new actor
        
        # Check version history
        history = self.manager.get_version_history(graph_id)
        self.assertEqual(len(history), 1)  # One archived version
    
    def test_different_formats(self):
        """Test different storage formats."""
        formats_to_test = [
            StorageFormat.JSON,
            StorageFormat.PICKLE,
            StorageFormat.COMPRESSED_JSON,
            StorageFormat.COMPRESSED_PICKLE
        ]
        
        for format_type in formats_to_test:
            with self.subTest(format=format_type):
                graph_id = f"test_{format_type.value}"
                
                # Save with specific format
                metadata = self.manager.save_graph(graph_id, self.sample_graph, format_type=format_type)
                self.assertEqual(metadata.format, format_type)
                
                # Load and verify
                loaded_graph = self.manager.load_graph(graph_id)
                self.assertIsNotNone(loaded_graph)
                self.assertEqual(loaded_graph.name, self.sample_graph.name)
    
    def test_metadata_handling(self):
        """Test metadata storage and retrieval."""
        graph_id = "test_metadata"
        custom_metadata = {
            "author": "Test Author",
            "tags": ["test", "sample", "agriculture"],
            "project": "SFM Testing"
        }
        
        # Save with custom metadata
        metadata = self.manager.save_graph(
            graph_id, 
            self.sample_graph, 
            metadata=custom_metadata
        )
        
        self.assertEqual(metadata.author, "Test Author")
        self.assertEqual(metadata.tags, ["test", "sample", "agriculture"])
        
        # Retrieve metadata separately
        retrieved_metadata = self.manager.get_graph_metadata(graph_id)
        self.assertIsNotNone(retrieved_metadata)
        self.assertEqual(retrieved_metadata.author, "Test Author")
    
    def test_list_graphs(self):
        """Test graph listing functionality."""
        # Save multiple graphs
        graphs_to_save = ["graph_1", "graph_2", "graph_3"]
        for graph_id in graphs_to_save:
            self.manager.save_graph(graph_id, self.sample_graph)
        
        # List graph IDs only
        graph_ids = self.manager.list_graphs(include_metadata=False)
        self.assertEqual(set(graph_ids), set(graphs_to_save))
        
        # List with metadata
        graph_metadata_list = self.manager.list_graphs(include_metadata=True)
        self.assertEqual(len(graph_metadata_list), 3)
        self.assertTrue(all(hasattr(m, 'graph_id') for m in graph_metadata_list))
    
    def test_delete_graph(self):
        """Test graph deletion."""
        graph_id = "test_delete"
        
        # Save graph
        self.manager.save_graph(graph_id, self.sample_graph)
        
        # Verify it exists
        loaded_graph = self.manager.load_graph(graph_id)
        self.assertIsNotNone(loaded_graph)
        
        # Delete graph
        success = self.manager.delete_graph(graph_id)
        self.assertTrue(success)
        
        # Verify it's gone
        loaded_graph = self.manager.load_graph(graph_id)
        self.assertIsNone(loaded_graph)
    
    def test_backup_and_restore(self):
        """Test backup and restore functionality."""
        graph_id = "test_backup"
        
        # Save original graph
        self.manager.save_graph(graph_id, self.sample_graph)
        
        # Create backup
        backup_path = self.manager.create_backup(graph_id)
        self.assertTrue(Path(backup_path).exists())
        
        # Delete original
        self.manager.delete_graph(graph_id)
        self.assertIsNone(self.manager.load_graph(graph_id))
        
        # Restore from backup
        restored_id = self.manager.restore_from_backup(backup_path)
        self.assertEqual(restored_id, graph_id)
        
        # Verify restoration
        restored_graph = self.manager.load_graph(graph_id)
        self.assertIsNotNone(restored_graph)
        self.assertEqual(restored_graph.name, self.sample_graph.name)
    
    def test_storage_statistics(self):
        """Test storage statistics functionality."""
        # Save some graphs
        for i in range(3):
            self.manager.save_graph(f"stats_test_{i}", self.sample_graph)
        
        stats = self.manager.get_storage_statistics()
        
        self.assertEqual(stats['total_graphs'], 3)
        self.assertGreater(stats['total_size_bytes'], 0)
        self.assertIn('format_distribution', stats)
        self.assertIsNotNone(stats['largest_graph'])
    
    def test_serialization_roundtrip(self):
        """Test direct serialization and deserialization."""
        # Test JSON format
        json_data = SFMGraphSerializer.serialize_graph(self.sample_graph, StorageFormat.JSON)
        recovered_graph = SFMGraphSerializer.deserialize_graph(json_data, StorageFormat.JSON)
        
        self.assertEqual(recovered_graph.name, self.sample_graph.name)
        self.assertEqual(len(recovered_graph.actors), len(self.sample_graph.actors))
        
        # Test pickle format
        pickle_data = SFMGraphSerializer.serialize_graph(self.sample_graph, StorageFormat.PICKLE)
        recovered_graph = SFMGraphSerializer.deserialize_graph(pickle_data, StorageFormat.PICKLE)
        
        self.assertEqual(recovered_graph.name, self.sample_graph.name)
        self.assertEqual(len(recovered_graph.relationships), len(self.sample_graph.relationships))
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        graph_id = "convenience_test"
        
        # Test quick save
        metadata = save_sfm_graph(graph_id, self.sample_graph, self.temp_dir)
        self.assertIsNotNone(metadata)
        
        # Test quick load
        loaded_graph = load_sfm_graph(graph_id, self.temp_dir)
        self.assertIsNotNone(loaded_graph)
        self.assertEqual(loaded_graph.name, self.sample_graph.name)
        
        # Test quick list
        graph_list = list_sfm_graphs(self.temp_dir)
        self.assertIn(graph_id, graph_list)
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        # Test loading non-existent graph
        non_existent = self.manager.load_graph("does_not_exist")
        self.assertIsNone(non_existent)
        
        # Test deleting non-existent graph
        delete_result = self.manager.delete_graph("does_not_exist")
        self.assertFalse(delete_result)


def run_persistence_demo():
    """Demonstrate SFM persistence functionality."""
    print("=== SFM Persistence Manager Demo ===\n")
    
    # Create temporary directory for demo
    demo_dir = tempfile.mkdtemp()
    config = PersistenceConfig(
        base_path=demo_dir,
        enable_versioning=True,
        enable_compression=False
    )
    
    try:
        manager = SFMPersistenceManager(config)
        
        # Create sample graph
        print("1. Creating sample SFM graph...")
        graph = SFMGraph(name="Agricultural Policy Network", 
                        description="Example network for policy analysis")
        
        # Add some sample entities
        farmer = Actor(label="Midwest Farmer", sector="agriculture")
        usda = Actor(label="USDA", sector="government")
        corn = Resource(label="Corn Production", rtype=ResourceType.NATURAL)
        subsidy = Policy(label="Crop Subsidy", authority="USDA")
        
        graph.actors[farmer.id] = farmer
        graph.actors[usda.id] = usda
        graph.resources[corn.id] = corn
        graph.policies[subsidy.id] = subsidy
        
        # Add relationships
        rel1 = Relationship(source_id=usda.id, target_id=subsidy.id, 
                           kind=RelationshipKind.IMPLEMENTS)
        rel2 = Relationship(source_id=farmer.id, target_id=subsidy.id,
                           kind=RelationshipKind.BENEFITS_FROM)
        
        graph.relationships[rel1.id] = rel1
        graph.relationships[rel2.id] = rel2
        
        print(f"   - Created graph with {len(graph.actors)} actors, {len(graph.resources)} resources")
        print(f"   - {len(graph.policies)} policies, {len(graph.relationships)} relationships")
        
        # Save graph
        print("\n2. Saving graph...")
        metadata = manager.save_graph("ag_policy_demo", graph, 
                                    metadata={"author": "Demo User", "tags": ["demo", "agriculture"]})
        print(f"   - Saved as version {metadata.version}")
        print(f"   - Size: {metadata.size_bytes} bytes")
        
        # Modify and save new version
        print("\n3. Creating new version...")
        processor = Actor(label="Food Processor", sector="manufacturing")
        graph.actors[processor.id] = processor
        
        new_rel = Relationship(source_id=farmer.id, target_id=processor.id,
                              kind=RelationshipKind.SUPPLIES)
        graph.relationships[new_rel.id] = new_rel
        
        metadata_v2 = manager.save_graph("ag_policy_demo", graph)
        print(f"   - Saved as version {metadata_v2.version}")
        
        # Demonstrate loading
        print("\n4. Loading different versions...")
        v1_graph = manager.load_graph("ag_policy_demo", version=1)
        v2_graph = manager.load_graph("ag_policy_demo", version=2)
        
        print(f"   - Version 1: {len(v1_graph.actors)} actors")
        print(f"   - Version 2: {len(v2_graph.actors)} actors")
        
        # Show version history
        print("\n5. Version history:")
        history = manager.get_version_history("ag_policy_demo")
        for version_info in history:
            print(f"   - Version {version_info['version']}: {version_info['modified_at']}")
        
        # Create backup
        print("\n6. Creating backup...")
        backup_path = manager.create_backup("ag_policy_demo")
        print(f"   - Backup created: {Path(backup_path).name}")
        
        # Show storage statistics
        print("\n7. Storage statistics:")
        stats = manager.get_storage_statistics()
        print(f"   - Total graphs: {stats['total_graphs']}")
        print(f"   - Total size: {stats['total_size_bytes']} bytes")
        print(f"   - Total versions: {stats['total_versions']}")
        print(f"   - Format distribution: {stats['format_distribution']}")
        
        print("\n=== Demo completed successfully! ===")
        
    finally:
        # Clean up
        shutil.rmtree(demo_dir)
        print(f"Cleaned up demo directory: {demo_dir}")


if __name__ == "__main__":
    # Run demo
    run_persistence_demo()
    
    print("\n" + "="*50)
    print("Running unit tests...")
    print("="*50)
    
    # Run tests
    unittest.main(verbosity=2)
