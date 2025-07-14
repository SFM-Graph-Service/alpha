"""
Tests for the  SFM DAO layer.
This module contains unit tests for the SFM DAO layer
"""

import unittest
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import networkx as nx

from core.sfm_models import *
from core.sfm_enums import *
from core.exceptions import (
    NodeCreationError,
    SFMNotFoundError,
    RelationshipValidationError,
    SFMValidationError,
)
from db.sfm_dao import (
    SFMRepository, NetworkXSFMRepository, SFMRepositoryFactory, TypedSFMRepository,
    ActorRepository, InstitutionRepository, PolicyRepository,
    ResourceRepository, ProcessRepository, FlowRepository,
    BeliefSystemRepository, TechnologySystemRepository,
    IndicatorRepository, FeedbackLoopRepository,
    SystemPropertyRepository, AnalyticalContextRepository,
    RelationshipRepository
)

# Import centralized mocks and fixtures
from tests.mocks import (
    MockRepositoryFactory,
    MockStorageBackend,
    create_mock_graph,
    create_sample_nodes,
)


# ==============================================================================
# BASIC REPOSITORY UNIT TESTS 
# ==============================================================================

class TestNetworkXSFMRepositoryUnit(unittest.TestCase):
    """Unit tests for NetworkXSFMRepository using centralized mocks."""

    def setUp(self):
        """Set up test fixtures using centralized mock infrastructure."""
        self.repo = NetworkXSFMRepository()
        
        # Use centralized mock nodes
        nodes = create_sample_nodes()
        actors = [n for n in nodes if isinstance(n, Actor)]
        institutions = [n for n in nodes if isinstance(n, Institution)]
        
        # Assign specific test nodes with fallbacks
        self.actor1 = actors[0] if actors else Actor(label="Test Actor 1", sector="Government")
        self.actor2 = actors[1] if len(actors) > 1 else Actor(label="Test Actor 2", sector="Private")
        self.institution = institutions[0] if institutions else Institution(label="Test Institution")
        
        # Create relationships using centralized pattern
        self.relationship = Relationship(
            source_id=self.actor1.id,
            target_id=self.actor2.id,
            kind=RelationshipKind.GOVERNS,
            weight=0.75
        )

    def test_create_node(self):
        # Test creating a node
        created_node = self.repo.create_node(self.actor1)
        self.assertEqual(created_node, self.actor1)
        self.assertTrue(self.actor1.id in self.repo.graph)
        
        # Test creating a duplicate node
        with self.assertRaises(NodeCreationError):
            self.repo.create_node(self.actor1)

    def test_read_node(self):
        self.repo.create_node(self.actor1)
        
        # Test reading existing node
        read_node = self.repo.read_node(self.actor1.id)
        self.assertEqual(read_node, self.actor1)
        
        # Test reading non-existent node
        nonexistent_id = uuid.uuid4()
        self.assertIsNone(self.repo.read_node(nonexistent_id))

    def test_update_node(self):
        self.repo.create_node(self.actor1)
        
        # Modify the node
        self.actor1.label = "Updated Actor"
        
        # Test updating
        updated_node = self.repo.update_node(self.actor1)
        self.assertEqual(updated_node.label, "Updated Actor")
        
        # Verify the update in storage
        stored_node = self.repo.read_node(self.actor1.id)
        self.assertEqual(stored_node.label, "Updated Actor") #type: ignore[exists-in-supertype]
        
        # Test updating non-existent node
        non_existent = Actor(label="Non-existent")
        with self.assertRaises(SFMNotFoundError):
            self.repo.update_node(non_existent)

    def test_delete_node(self):
        self.repo.create_node(self.actor1)
        
        # Test successful deletion
        self.assertTrue(self.repo.delete_node(self.actor1.id))
        self.assertIsNone(self.repo.read_node(self.actor1.id))
        
        # Test deleting non-existent node
        self.assertFalse(self.repo.delete_node(uuid.uuid4()))

    def test_list_nodes(self):
        self.repo.create_node(self.actor1)
        self.repo.create_node(self.actor2)
        self.repo.create_node(self.institution)
        
        # Test listing all nodes
        all_nodes = self.repo.list_nodes()
        self.assertEqual(len(all_nodes), 3)
        
        # Test filtering by type
        actors = self.repo.list_nodes(Actor)
        self.assertEqual(len(actors), 2)
        institutions = self.repo.list_nodes(Institution)
        self.assertEqual(len(institutions), 1)

    def test_create_relationship(self):
        # Add nodes first
        self.repo.create_node(self.actor1)
        self.repo.create_node(self.actor2)
        
        # Test creating relationship
        created_rel = self.repo.create_relationship(self.relationship)
        self.assertEqual(created_rel, self.relationship)
        
        # Test creating with missing source
        self.repo.delete_node(self.actor1.id)
        with self.assertRaises(SFMNotFoundError):
            self.repo.create_relationship(self.relationship)
            
        # Restore actor1 and test with missing target
        self.repo.create_node(self.actor1)
        self.repo.delete_node(self.actor2.id)
        with self.assertRaises(SFMNotFoundError):
            self.repo.create_relationship(self.relationship)
            
        # Test duplicate
        self.repo.create_node(self.actor2)
        self.repo.create_relationship(self.relationship)
        with self.assertRaises(RelationshipValidationError):
            self.repo.create_relationship(self.relationship)

    def test_read_relationship(self):
        self.repo.create_node(self.actor1)
        self.repo.create_node(self.actor2)
        self.repo.create_relationship(self.relationship)
        
        # Test reading existing relationship
        read_rel = self.repo.read_relationship(self.relationship.id)
        self.assertEqual(read_rel, self.relationship)
        
        # Test reading non-existent relationship
        nonexistent_id = uuid.uuid4()
        self.assertIsNone(self.repo.read_relationship(nonexistent_id))

    def test_update_relationship(self):
        self.repo.create_node(self.actor1)
        self.repo.create_node(self.actor2)
        self.repo.create_relationship(self.relationship)
        
        # Modify the relationship
        self.relationship.weight = 0.9
        
        # Test updating
        updated_rel = self.repo.update_relationship(self.relationship)
        self.assertEqual(updated_rel.weight, 0.9)
        
        # Verify the update in storage
        stored_rel = self.repo.read_relationship(self.relationship.id)
        self.assertEqual(stored_rel.weight, 0.9) #type: ignore[exists-in-supertype]
        
        # Test updating non-existent relationship
        non_existent = Relationship(
            source_id=uuid.uuid4(),
            target_id=uuid.uuid4(),
            kind=RelationshipKind.GOVERNS
        )
        with self.assertRaises(SFMNotFoundError):
            self.repo.update_relationship(non_existent)

    def test_delete_relationship(self):
        self.repo.create_node(self.actor1)
        self.repo.create_node(self.actor2)
        self.repo.create_relationship(self.relationship)
        
        # Test successful deletion
        self.assertTrue(self.repo.delete_relationship(self.relationship.id))
        self.assertIsNone(self.repo.read_relationship(self.relationship.id))
        
        # Test deleting non-existent relationship
        self.assertFalse(self.repo.delete_relationship(uuid.uuid4()))

    def test_list_relationships(self):
        self.repo.create_node(self.actor1)
        self.repo.create_node(self.actor2)
        self.repo.create_node(self.institution)
        
        # Create two relationships with different kinds
        rel1 = Relationship(
            source_id=self.actor1.id,
            target_id=self.actor2.id,
            kind=RelationshipKind.GOVERNS
        )
        rel2 = Relationship(
            source_id=self.actor2.id,
            target_id=self.institution.id,
            kind=RelationshipKind.SERVES
        )
        self.repo.create_relationship(rel1)
        self.repo.create_relationship(rel2)
        
        # Test listing all relationships
        all_rels = self.repo.list_relationships()
        self.assertEqual(len(all_rels), 2)
        
        # Test filtering by kind
        governs_rels = self.repo.list_relationships(RelationshipKind.GOVERNS)
        self.assertEqual(len(governs_rels), 1)
        self.assertEqual(governs_rels[0].kind, RelationshipKind.GOVERNS)

    def test_find_relationships(self):
        # Create test setup
        self.repo.create_node(self.actor1)
        self.repo.create_node(self.actor2)
        self.repo.create_node(self.institution)
        
        rel1 = Relationship(
            source_id=self.actor1.id,
            target_id=self.actor2.id,
            kind=RelationshipKind.GOVERNS
        )
        rel2 = Relationship(
            source_id=self.actor1.id,
            target_id=self.institution.id,
            kind=RelationshipKind.SERVES
        )
        rel3 = Relationship(
            source_id=self.actor2.id,
            target_id=self.institution.id,
            kind=RelationshipKind.SERVES
        )
        
        self.repo.create_relationship(rel1)
        self.repo.create_relationship(rel2)
        self.repo.create_relationship(rel3)
        
        # Test finding by source
        source_rels = self.repo.find_relationships(source_id=self.actor1.id)
        self.assertEqual(len(source_rels), 2)
        
        # Test finding by target
        target_rels = self.repo.find_relationships(target_id=self.institution.id)
        self.assertEqual(len(target_rels), 2)
        
        # Test finding by kind
        kind_rels = self.repo.find_relationships(kind=RelationshipKind.SERVES)
        self.assertEqual(len(kind_rels), 2)
        
        # Test combined filters
        combined_rels = self.repo.find_relationships(
            source_id=self.actor1.id,
            target_id=self.institution.id,
            kind=RelationshipKind.SERVES
        )
        self.assertEqual(len(combined_rels), 1)
        self.assertEqual(combined_rels[0].source_id, self.actor1.id)
        self.assertEqual(combined_rels[0].target_id, self.institution.id)
        self.assertEqual(combined_rels[0].kind, RelationshipKind.SERVES)

    def test_clear(self):
        # Add some data
        self.repo.create_node(self.actor1)
        self.repo.create_node(self.actor2)
        self.repo.create_relationship(self.relationship)
        
        # Verify data exists
        self.assertEqual(len(self.repo.list_nodes()), 2)
        self.assertEqual(len(self.repo.list_relationships()), 1)
        
        # Clear and verify
        self.repo.clear()
        self.assertEqual(len(self.repo.list_nodes()), 0)
        self.assertEqual(len(self.repo.list_relationships()), 0)


class TestTypedSFMRepositoryUnit(unittest.TestCase):
    """Unit tests for TypedSFMRepository."""

    def setUp(self):
        self.base_repo = NetworkXSFMRepository()
        self.actor_repo = TypedSFMRepository(self.base_repo, Actor)
        
        # Create test data
        self.actor = Actor(label="Test Actor", sector="Government")
        self.institution = Institution(label="Test Institution")

    def test_create(self):
        # Test correct type
        created = self.actor_repo.create(self.actor)
        self.assertEqual(created, self.actor)
        
        # Test wrong type
        with self.assertRaises(TypeError):
            self.actor_repo.create(self.institution) #type: ignore[arg-type] this is testing a type error

    def test_read(self):
        # Add nodes
        self.base_repo.create_node(self.actor)
        self.base_repo.create_node(self.institution)
        
        # Should find actors
        actor = self.actor_repo.read(self.actor.id)
        self.assertEqual(actor, self.actor)
        
        # Should not find institutions
        self.assertIsNone(self.actor_repo.read(self.institution.id))
        
        # Should not find non-existent nodes
        self.assertIsNone(self.actor_repo.read(uuid.uuid4()))

    def test_update(self):
        # Add node
        self.actor_repo.create(self.actor)
        
        # Update
        self.actor.label = "Updated Actor"
        updated = self.actor_repo.update(self.actor)
        self.assertEqual(updated.label, "Updated Actor")
        
        # Test wrong type
        with self.assertRaises(TypeError):
            self.actor_repo.update(self.institution) #type: ignore[arg-type] this is testing a type error

    def test_delete(self):
        self.actor_repo.create(self.actor)
        self.assertTrue(self.actor_repo.delete(self.actor.id))
        self.assertIsNone(self.actor_repo.read(self.actor.id))

    def test_list_all(self):
        # Add mixed types to base repo
        self.base_repo.create_node(self.actor)
        self.base_repo.create_node(self.institution)
        
        # Should only list actors
        actors = self.actor_repo.list_all()
        self.assertEqual(len(actors), 1)
        self.assertEqual(actors[0], self.actor)

    def test_query(self):
        # Add test actors with different attributes
        actor1 = Actor(label="Actor 1", sector="Government", legal_form="Federal")
        actor2 = Actor(label="Actor 2", sector="Government", legal_form="State")
        actor3 = Actor(label="Actor 3", sector="Private", legal_form="Corporation")
        
        self.actor_repo.create(actor1)
        self.actor_repo.create(actor2)
        self.actor_repo.create(actor3)
        
        # Query by a single attribute
        govt_actors = self.actor_repo.query({"sector": "Government"})
        self.assertEqual(len(govt_actors), 2)
        
        # Query by multiple attributes
        fed_govt_actors = self.actor_repo.query({
            "sector": "Government",
            "legal_form": "Federal"
        })
        self.assertEqual(len(fed_govt_actors), 1)
        self.assertEqual(fed_govt_actors[0].label, "Actor 1")
        
        # Query with no matches
        no_matches = self.actor_repo.query({"sector": "Nonprofit"})
        self.assertEqual(len(no_matches), 0)
        
        # Query with non-existent attribute
        empty_result = self.actor_repo.query({"non_existent": "value"})
        self.assertEqual(len(empty_result), 0)


class TestSpecializedRepositoriesUnit(unittest.TestCase):
    """Unit tests for specialized repository classes."""

    def setUp(self):
        self.base_repo = NetworkXSFMRepository()
        self.actor_repo = ActorRepository(self.base_repo)
        self.institution_repo = InstitutionRepository(self.base_repo)
        self.policy_repo = PolicyRepository(self.base_repo)
        self.resource_repo = ResourceRepository(self.base_repo)
        self.relationship_repo = RelationshipRepository(self.base_repo)
        
        # Create test data
        self.actor1 = Actor(label="Test Actor 1", sector="Government")
        self.actor2 = Actor(label="Test Actor 2", sector="Private", legal_form="Corporation")
        self.institution = Institution(label="Test Institution")
        self.policy = Policy(
            label="Test Policy", 
            authority="EPA",
            target_sectors=["Energy", "Transportation"]
        )
        self.resource = Resource(
            label="Test Resource",
            rtype=ResourceType.NATURAL
        )
        
        # Create a relationship
        self.relationship = Relationship(
            source_id=self.actor1.id,
            target_id=self.actor2.id,
            kind=RelationshipKind.GOVERNS
        )
        
        # Add data to repositories
        self.actor_repo.create(self.actor1)
        self.actor_repo.create(self.actor2)
        self.institution_repo.create(self.institution)
        self.policy_repo.create(self.policy)
        self.resource_repo.create(self.resource)
        self.relationship_repo.create(self.relationship)

    def test_actor_repository_specialized_methods(self):
        # Test find_by_sector
        govt_actors = self.actor_repo.find_by_sector("Government")
        self.assertEqual(len(govt_actors), 1)
        self.assertEqual(govt_actors[0].label, "Test Actor 1")
        
        # Test find_by_legal_form
        corp_actors = self.actor_repo.find_by_legal_form("Corporation")
        self.assertEqual(len(corp_actors), 1)
        self.assertEqual(corp_actors[0].label, "Test Actor 2")

    def test_policy_repository_specialized_methods(self):
        # Test find_by_authority
        epa_policies = self.policy_repo.find_by_authority("EPA")
        self.assertEqual(len(epa_policies), 1)
        self.assertEqual(epa_policies[0].label, "Test Policy")
        
        # Test find_by_target_sector
        energy_policies = self.policy_repo.find_by_target_sector("Energy")
        self.assertEqual(len(energy_policies), 1)
        self.assertEqual(energy_policies[0].label, "Test Policy")
        
        transportation_policies = self.policy_repo.find_by_target_sector("Transportation")
        self.assertEqual(len(transportation_policies), 1)
        
        agriculture_policies = self.policy_repo.find_by_target_sector("Agriculture")
        self.assertEqual(len(agriculture_policies), 0)

    def test_resource_repository_specialized_methods(self):
        # Test find_by_type
        natural_resources = self.resource_repo.find_by_type(ResourceType.NATURAL)
        self.assertEqual(len(natural_resources), 1)
        self.assertEqual(natural_resources[0].label, "Test Resource")
        
        produced_resources = self.resource_repo.find_by_type(ResourceType.PRODUCED)
        self.assertEqual(len(produced_resources), 0)

    def test_relationship_repository_methods(self):
        # Test find_by_kind
        governs_rels = self.relationship_repo.find_by_kind(RelationshipKind.GOVERNS)
        self.assertEqual(len(governs_rels), 1)
        
        # Test find_by_source
        source_rels = self.relationship_repo.find_by_source(self.actor1.id)
        self.assertEqual(len(source_rels), 1)
        self.assertEqual(source_rels[0].source_id, self.actor1.id)
        
        # Test find_by_target
        target_rels = self.relationship_repo.find_by_target(self.actor2.id)
        self.assertEqual(len(target_rels), 1)
        self.assertEqual(target_rels[0].target_id, self.actor2.id)
        
        # Test find_by_nodes
        node_rels = self.relationship_repo.find_by_nodes(
            self.actor1.id,
            self.actor2.id
        )
        self.assertEqual(len(node_rels), 1)
        self.assertEqual(node_rels[0].source_id, self.actor1.id)
        self.assertEqual(node_rels[0].target_id, self.actor2.id)


class TestSFMRepositoryFactoryUnit(unittest.TestCase):
    """Unit tests for SFMRepositoryFactory."""

    def test_create_repository(self):
        # Test creating with default
        default_repo = SFMRepositoryFactory.create_repository()
        self.assertIsInstance(default_repo, NetworkXSFMRepository)
        
        # Test creating with networkx explicitly
        nx_repo = SFMRepositoryFactory.create_repository("networkx")
        self.assertIsInstance(nx_repo, NetworkXSFMRepository)
        
        # Test unsupported storage type
        with self.assertRaises(SFMValidationError):
            SFMRepositoryFactory.create_repository("unsupported_storage")

    def test_create_specialized_repositories(self):
        # Test creating actor repository
        actor_repo = SFMRepositoryFactory.create_actor_repository()
        self.assertIsInstance(actor_repo, ActorRepository)
        
        # Test creating institution repository
        inst_repo = SFMRepositoryFactory.create_institution_repository()
        self.assertIsInstance(inst_repo, InstitutionRepository)
        
        # Test creating policy repository
        policy_repo = SFMRepositoryFactory.create_policy_repository()
        self.assertIsInstance(policy_repo, PolicyRepository)
        
        # Test creating resource repository
        resource_repo = SFMRepositoryFactory.create_resource_repository()
        self.assertIsInstance(resource_repo, ResourceRepository)
        
        # Test creating relationship repository
        rel_repo = SFMRepositoryFactory.create_relationship_repository()
        self.assertIsInstance(rel_repo, RelationshipRepository)


class TestSFMRepositoryIntegration(unittest.TestCase):
    """Integration tests for SFM repositories."""

    def setUp(self):
        # Create repositories
        self.repo = NetworkXSFMRepository()
        self.actor_repo = ActorRepository(self.repo)
        self.institution_repo = InstitutionRepository(self.repo)
        self.relationship_repo = RelationshipRepository(self.repo)
        
        # Create test data
        self.actor = Actor(label="Government Actor", sector="Government")
        self.institution = Institution(label="Research Institution")

    def test_cross_repo_operations(self):
        # Create nodes in different repositories
        self.actor_repo.create(self.actor)
        self.institution_repo.create(self.institution)
        
        # Create a relationship between them
        relationship = Relationship(
            source_id=self.actor.id,
            target_id=self.institution.id,
            kind=RelationshipKind.FUNDS
        )
        self.relationship_repo.create(relationship)
        
        # Query from relationship repo
        actor_relations = self.relationship_repo.find_by_source(self.actor.id)
        self.assertEqual(len(actor_relations), 1)
        
        # Query from actor repo - should see the relationship through the base repo
        node = self.actor_repo.read(self.actor.id)
        self.assertIsNotNone(node)

    def test_graph_save_load_basic(self):
        # Create complex data structure
        actor1 = Actor(label="Actor 1")
        actor2 = Actor(label="Actor 2")
        institution = Institution(label="Institution")
        
        rel1 = Relationship(
            source_id=actor1.id,
            target_id=actor2.id,
            kind=RelationshipKind.GOVERNS
        )
        rel2 = Relationship(
            source_id=actor1.id,
            target_id=institution.id,
            kind=RelationshipKind.FUNDS
        )
        
        # Create entities
        self.actor_repo.create(actor1)
        self.actor_repo.create(actor2)
        self.institution_repo.create(institution)
        self.relationship_repo.create(rel1)
        self.relationship_repo.create(rel2)
        
        # Load into SFMGraph
        graph = self.repo.load_graph()
        
        # Verify graph contents
        self.assertEqual(len(graph), 3)  # 3 nodes
        self.assertEqual(len(graph.relationships), 2)  # 2 relationships
        
        # Clear repository
        self.repo.clear()
        self.assertEqual(len(self.actor_repo.list_all()), 0)
        
        # Save graph back
        self.repo.save_graph(graph)
        
        # Verify restored contents
        self.assertEqual(len(self.actor_repo.list_all()), 2)
        self.assertEqual(len(self.institution_repo.list_all()), 1)
        self.assertEqual(len(self.relationship_repo.list_all()), 2)

    def test_type_safety_across_system(self):
        # Create node in actor repo
        actor = Actor(label="Test Actor")
        self.actor_repo.create(actor)
        
        # Try to read as institution - should return None
        found_institution = self.institution_repo.read(actor.id)
        self.assertIsNone(found_institution)
        
        # Trying to update an institution as an actor should fail
        inst = Institution(label="Test Institution")
        with self.assertRaises(TypeError):
            self.actor_repo.update(inst) #type: ignore[arg-type] this is testing a type error


class TestMultipleStorageTypes(unittest.TestCase):
    """
    Tests to validate that different repositories can work together 
    even with different storage backends.
    
    Note: Currently this just tests the same NetworkX backend,
    but the test structure is in place for future storage types.
    """
    
    def setUp(self):
        self.base_repo1 = SFMRepositoryFactory.create_repository("networkx")
        self.base_repo2 = SFMRepositoryFactory.create_repository("networkx")
        
        # Create specialized repositories
        self.actor_repo = ActorRepository(self.base_repo1)
        self.institution_repo = InstitutionRepository(self.base_repo2)

    def test_data_isolation(self):
        # Each repo should have separate storage
        actor = Actor(label="Test Actor")
        institution = Institution(label="Test Institution")
        
        # Add to respective repositories
        self.actor_repo.create(actor)
        self.institution_repo.create(institution)
        
        # Base repo 1 should only have actor
        self.assertEqual(len(self.base_repo1.list_nodes()), 1)
        self.assertEqual(len(self.base_repo1.list_nodes(Actor)), 1)
        self.assertEqual(len(self.base_repo1.list_nodes(Institution)), 0)
        
        # Base repo 2 should only have institution
        self.assertEqual(len(self.base_repo2.list_nodes()), 1)
        self.assertEqual(len(self.base_repo2.list_nodes(Actor)), 0)
        self.assertEqual(len(self.base_repo2.list_nodes(Institution)), 1)

class TestNetworkXSFMRepository(unittest.TestCase):
    """Test the  NetworkX repository implementation."""
    
    def setUp(self):
        self.repo = NetworkXSFMRepository()
        
        # Create sample temporal and spatial contexts
        self.time_slice = TimeSlice(label="Q1-2024")
        self.spatial_unit = SpatialUnit(code="US-CA", name="California")
        
        # Create sample nodes
        self.actor = Actor(label="Test Actor", sector="Government")
        self.flow = Flow(
            label="Test Flow",
            time=self.time_slice,
            space=self.spatial_unit
        )
        
        # Add nodes to repo
        self.repo.create_node(self.actor)
        self.repo.create_node(self.flow)
        
        # Create relationship with temporal/spatial context
        self.relationship = Relationship(
            source_id=self.actor.id,
            target_id=self.flow.id,
            kind=RelationshipKind.INFLUENCES,
            time=self.time_slice,
            space=self.spatial_unit
        )
        self.repo.create_relationship(self.relationship)
    
    def test_temporal_node_queries(self):
        """Test finding nodes by time slice."""
        # Should find the flow node
        temporal_nodes = self.repo.find_nodes_by_time(self.time_slice)
        self.assertEqual(len(temporal_nodes), 1)
        self.assertEqual(temporal_nodes[0].id, self.flow.id)
        
        # Should find specific node type
        temporal_flows = self.repo.find_nodes_by_time(self.time_slice, Flow)
        self.assertEqual(len(temporal_flows), 1)
        self.assertIsInstance(temporal_flows[0], Flow)
        
        # Should find no actors with this time slice
        temporal_actors = self.repo.find_nodes_by_time(self.time_slice, Actor)
        self.assertEqual(len(temporal_actors), 0)
    
    def test_spatial_node_queries(self):
        """Test finding nodes by spatial unit."""
        # Should find the flow node
        spatial_nodes = self.repo.find_nodes_by_space(self.spatial_unit)
        self.assertEqual(len(spatial_nodes), 1)
        self.assertEqual(spatial_nodes[0].id, self.flow.id)
        
        # Should find specific node type
        spatial_flows = self.repo.find_nodes_by_space(self.spatial_unit, Flow)
        self.assertEqual(len(spatial_flows), 1)
        self.assertIsInstance(spatial_flows[0], Flow)
    
    def test_temporal_relationship_queries(self):
        """Test finding relationships by time slice."""
        temporal_rels = self.repo.find_relationships_by_time(self.time_slice)
        self.assertEqual(len(temporal_rels), 1)
        self.assertEqual(temporal_rels[0].id, self.relationship.id)
    
    def test_spatial_relationship_queries(self):
        """Test finding relationships by spatial unit."""
        spatial_rels = self.repo.find_relationships_by_space(self.spatial_unit)
        self.assertEqual(len(spatial_rels), 1)
        self.assertEqual(spatial_rels[0].id, self.relationship.id)


class TestTypedRepositories(unittest.TestCase):
    """Test functionality in typed repositories."""
    
    def setUp(self):
        self.repos = SFMRepositoryFactory.create_all_repositories()
        
        # Create test data
        self.actor = Actor(
            label="Test Actor",
            sector="Government",
            legal_form="Federal Agency"
        )
        self.policy = Policy(
            label="Test Policy",
            authority="EPA",
            enforcement=0.85,
            target_sectors=["Energy", "Environment"]
        )
        self.indicator = Indicator(
            label="Test Indicator",
            value_category=ValueCategory.ECONOMIC,
            current_value=100.0,
            target_value=120.0
        )
        
        # Add to repositories
        self.repos['actor'].create(self.actor)
        self.repos['policy'].create(self.policy)
        self.repos['indicator'].create(self.indicator)
    
    def test_policy_repository_enhancements(self):
        """Test policy repository methods."""
        policy_repo = self.repos['policy']
        
        # Test find by authority
        epa_policies = policy_repo.find_by_authority("EPA")
        self.assertEqual(len(epa_policies), 1)
        self.assertEqual(epa_policies[0].label, "Test Policy")
        
        # Test find by target sector
        energy_policies = policy_repo.find_by_target_sector("Energy")
        self.assertEqual(len(energy_policies), 1)
        
        # Test find by enforcement level
        high_enforcement = policy_repo.find_by_enforcement_level(0.8)
        self.assertEqual(len(high_enforcement), 1)
        
        medium_enforcement = policy_repo.find_by_enforcement_level(0.9)
        self.assertEqual(len(medium_enforcement), 0)
    
    def test_indicator_repository_enhancements(self):
        """Test indicator repository methods."""
        indicator_repo = self.repos['indicator']
        
        # Test find by value category
        economic_indicators = indicator_repo.find_by_value_category(ValueCategory.ECONOMIC)
        self.assertEqual(len(economic_indicators), 1)
        
        # Test find by value range
        value_range_indicators = indicator_repo.find_by_current_value_range(90.0, 110.0)
        self.assertEqual(len(value_range_indicators), 1)
        
        # Test target comparisons
        below_target = indicator_repo.find_below_target()
        self.assertEqual(len(below_target), 1)
        
        above_target = indicator_repo.find_above_target()
        self.assertEqual(len(above_target), 0)
    
    def test_relationship_repository_enhancements(self):
        """Test relationship repository methods."""
        rel_repo = self.repos['relationship']
        
        # Create test relationship
        relationship = Relationship(
            source_id=self.actor.id,
            target_id=self.policy.id,
            kind=RelationshipKind.IMPLEMENTS,
            weight=0.8,
            certainty=0.9
        )
        rel_repo.create(relationship)
        
        # Test weight range queries
        weight_range_rels = rel_repo.find_by_weight_range(0.7, 0.9)
        self.assertEqual(len(weight_range_rels), 1)
        
        # Test certainty range queries
        high_certainty_rels = rel_repo.find_by_certainty_range(0.85, 1.0)
        self.assertEqual(len(high_certainty_rels), 1)


class TestCompleteRepositoryCoverage(unittest.TestCase):
    """Test that all node types have corresponding repositories."""
    
    def test_all_repositories_available(self):
        """Test that all repository types can be created."""
        repos = SFMRepositoryFactory.create_all_repositories()
        
        expected_repos = [
            'base', 'actor', 'institution', 'policy', 'resource',
            'process', 'flow', 'belief_system', 'technology_system',
            'indicator', 'feedback_loop', 'system_property',
            'analytical_context', 'relationship'
        ]
        
        for repo_name in expected_repos:
            self.assertIn(repo_name, repos, f"Missing repository: {repo_name}")
            self.assertIsNotNone(repos[repo_name], f"Repository {repo_name} is None")
    
    def test_all_node_types_supported(self):
        """Test that all node types can be created and stored."""
        repos = SFMRepositoryFactory.create_all_repositories()
        base_repo = repos['base']
        
        # Create instances of all node types
        nodes = [
            Actor(label="Test Actor"),
            Institution(label="Test Institution"),
            Policy(label="Test Policy"),
            Resource(label="Test Resource"),
            Process(label="Test Process"),
            Flow(label="Test Flow"),
            BeliefSystem(label="Test Belief System"),
            TechnologySystem(label="Test Technology System"),
            Indicator(label="Test Indicator"),
            FeedbackLoop(label="Test Feedback Loop"),
            SystemProperty(label="Test System Property"),
            AnalyticalContext(label="Test Analytical Context"),
        ]
        
        # Create all nodes
        for node in nodes:
            created_node = base_repo.create_node(node)
            self.assertEqual(created_node.id, node.id)
        
        # Verify all nodes can be retrieved
        for node in nodes:
            retrieved_node = base_repo.read_node(node.id)
            self.assertIsNotNone(retrieved_node)
            self.assertEqual(retrieved_node.label, node.label)
        
        # Verify total count
        all_nodes = base_repo.list_nodes()
        self.assertEqual(len(all_nodes), len(nodes))


class TestFactoryMethods(unittest.TestCase):
    """Test the factory methods."""
    
    def test_individual_repository_creation(self):
        """Test that individual repositories can be created."""
        # Test each repository type
        actor_repo = SFMRepositoryFactory.create_actor_repository()
        self.assertIsInstance(actor_repo, ActorRepository)
        
        policy_repo = SFMRepositoryFactory.create_policy_repository()
        self.assertIsInstance(policy_repo, PolicyRepository)
        
        indicator_repo = SFMRepositoryFactory.create_indicator_repository()
        self.assertIsInstance(indicator_repo, IndicatorRepository)
        
        # Test new repository types
        belief_repo = SFMRepositoryFactory.create_belief_system_repository()
        self.assertIsInstance(belief_repo, BeliefSystemRepository)
        
        tech_repo = SFMRepositoryFactory.create_technology_system_repository()
        self.assertIsInstance(tech_repo, TechnologySystemRepository)
        
        feedback_repo = SFMRepositoryFactory.create_feedback_loop_repository()
        self.assertIsInstance(feedback_repo, FeedbackLoopRepository)
    
    def test_create_all_repositories(self):
        """Test the create_all_repositories method."""
        repos = SFMRepositoryFactory.create_all_repositories()
        
        # Should be a dictionary
        self.assertIsInstance(repos, dict)
        
        # Should have all expected keys
        expected_keys = [
            'base', 'actor', 'institution', 'policy', 'resource',
            'process', 'flow', 'belief_system', 'technology_system',
            'indicator', 'feedback_loop', 'system_property',
            'analytical_context', 'relationship'
        ]
        
        for key in expected_keys:
            self.assertIn(key, repos)
        
        # All repositories should share the same base repository
        base_repo = repos['base']
        for key, repo in repos.items():
            if key != 'base' and hasattr(repo, 'base_repo'):
                self.assertEqual(repo.base_repo, base_repo)


class TestDataConsistency(unittest.TestCase):
    """Test data consistency across different repository types."""
    
    def setUp(self):
        self.repos = SFMRepositoryFactory.create_all_repositories()
    
    def test_cross_repository_consistency(self):
        """Test that data is consistent across different repository interfaces."""
        # Create an actor through actor repository
        actor = Actor(label="Cross-Repo Actor", sector="Test")
        actor_repo = self.repos['actor']
        created_actor = actor_repo.create(actor)
        
        # Should be accessible through base repository
        base_repo = self.repos['base']
        retrieved_actor = base_repo.read_node(actor.id)
        
        self.assertIsNotNone(retrieved_actor)
        self.assertEqual(retrieved_actor.label, "Cross-Repo Actor")
        self.assertIsInstance(retrieved_actor, Actor)
        
        # Should appear in base repository node listings
        all_actors = base_repo.list_nodes(Actor)
        self.assertIn(created_actor, all_actors)
    
    def test_graph_save_load_consistency(self):
        """Test that graph save/load maintains data integrity."""
        base_repo = self.repos['base']
        
        # Create various node types
        actor = Actor(label="Save Test Actor")
        policy = Policy(label="Save Test Policy")
        
        base_repo.create_node(actor)
        base_repo.create_node(policy)
        
        # Create relationship
        relationship = Relationship(
            source_id=actor.id,
            target_id=policy.id,
            kind=RelationshipKind.IMPLEMENTS
        )
        base_repo.create_relationship(relationship)
        
        # Load graph
        graph = base_repo.load_graph()
        
        # Verify integrity
        self.assertEqual(len(graph.actors), 1)
        self.assertEqual(len(graph.policies), 1)
        self.assertEqual(len(graph.relationships), 1)
        
        # Clear and reload
        base_repo.clear()
        self.assertEqual(len(base_repo.list_nodes()), 0)
        
        base_repo.save_graph(graph)
        reloaded_nodes = base_repo.list_nodes()
        self.assertEqual(len(reloaded_nodes), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
