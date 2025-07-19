"""
Mock factories and utilities for DAO/repository testing.

Provides centralized mock implementations for SFM repositories,
storage backends, and data access operations.
"""

import uuid
from unittest.mock import MagicMock
from typing import Dict, List, Any, Optional, Type, TypeVar
from datetime import datetime

from models import (
    Node, Actor, Institution, Policy, Resource, Process, Flow, 
    Relationship,
)
from data.repositories import (
    SFMRepository, TypedSFMRepository,
    ActorRepository, InstitutionRepository, PolicyRepository,
    ResourceRepository, ProcessRepository, FlowRepository,
    RelationshipRepository
)

from models.sfm_enums import RelationshipKind

T = TypeVar("T", bound=Node)
from graph.graph import SFMGraph


class MockStorageBackend:
    """Mock storage backend that simulates persistent storage."""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    def store_node(self, node: Node) -> Node:
        """Store a node in the mock backend."""
        self.nodes[str(node.id)] = node
        self._update_metadata()
        return node
    
    def retrieve_node(self, node_id: str) -> Optional[Node]:
        """Retrieve a node from the mock backend."""
        return self.nodes.get(node_id)
    
    def store_relationship(self, relationship: Relationship) -> Relationship:
        """Store a relationship in the mock backend."""
        self.relationships[str(relationship.id)] = relationship
        self._update_metadata()
        return relationship
    
    def retrieve_relationship(self, rel_id: str) -> Optional[Relationship]:
        """Retrieve a relationship from the mock backend."""
        return self.relationships.get(rel_id)
    
    def list_nodes_by_type(self, node_type: Type[T]) -> List[T]:
        """List all nodes of a specific type."""
        return [node for node in self.nodes.values() if isinstance(node, node_type)]
    
    def clear_all(self):
        """Clear all stored data."""
        self.nodes.clear()
        self.relationships.clear()
        self._update_metadata()
    
    def _update_metadata(self):
        """Update metadata timestamps."""
        self.metadata["last_modified"] = datetime.now().isoformat()


class MockRepositoryFactory:
    """Factory for creating consistently configured mock repositories."""
    
    @classmethod
    def create_mock_sfm_repository(cls, with_storage_backend=True):
        """Create a fully mocked SFM repository."""
        mock_repo = MagicMock(spec=SFMRepository)
        
        # Configure CRUD operations
        mock_repo.create_node.side_effect = cls._mock_create_node
        mock_repo.read_node.side_effect = cls._mock_get_node
        mock_repo.update_node.side_effect = cls._mock_update_node
        mock_repo.delete_node.return_value = True
        mock_repo.list_nodes.return_value = cls._get_sample_nodes()
        
        # Configure relationship operations
        mock_repo.create_relationship.side_effect = cls._mock_create_relationship
        mock_repo.read_relationship.side_effect = cls._mock_get_relationship
        mock_repo.update_relationship.side_effect = cls._mock_update_relationship
        mock_repo.delete_relationship.return_value = True
        mock_repo.list_relationships.return_value = cls._get_sample_relationships()
        
        # Configure query operations
        mock_repo.find_nodes_by_type.side_effect = cls._mock_find_nodes_by_type
        mock_repo.find_relationships_by_kind.side_effect = cls._mock_find_relationships_by_kind
        mock_repo.get_node_relationships.return_value = cls._get_sample_relationships()
        
        # Configure graph operations
        mock_repo.get_graph.return_value = SFMGraph()
        mock_repo.clear_graph.return_value = True
        mock_repo.get_statistics.return_value = {
            "node_count": 10,
            "relationship_count": 15,
            "last_updated": datetime.now().isoformat()
        }
        
        # Add storage backend if requested
        if with_storage_backend:
            mock_repo._storage = MockStorageBackend()
        
        return mock_repo
    
    @classmethod
    def create_mock_typed_repository(cls, node_type: Type[T]):
        """Create a mock typed repository for a specific node type."""
        mock_repo = MagicMock(spec=TypedSFMRepository)
        
        # Configure typed operations
        mock_repo.create.side_effect = lambda **kwargs: cls._create_sample_node(node_type, **kwargs)
        mock_repo.get.side_effect = lambda node_id: cls._create_sample_node(node_type, id=node_id)
        mock_repo.update.side_effect = lambda node: node
        mock_repo.delete.return_value = True
        mock_repo.list_all.return_value = [cls._create_sample_node(node_type) for _ in range(3)]
        
        # Configure search operations
        mock_repo.find_by_label.return_value = [cls._create_sample_node(node_type)]
        mock_repo.find_by_attribute.return_value = [cls._create_sample_node(node_type)]
        mock_repo.count.return_value = 5
        
        return mock_repo
    
    @classmethod
    def create_mock_actor_repository(cls):
        """Create a mock actor repository."""
        return cls.create_mock_typed_repository(Actor)
    
    @classmethod
    def create_mock_institution_repository(cls):
        """Create a mock institution repository."""
        return cls.create_mock_typed_repository(Institution)
    
    @classmethod
    def create_mock_policy_repository(cls):
        """Create a mock policy repository."""
        return cls.create_mock_typed_repository(Policy)
    
    @classmethod
    def create_mock_resource_repository(cls):
        """Create a mock resource repository."""
        return cls.create_mock_typed_repository(Resource)
    
    @classmethod
    def create_mock_relationship_repository(cls):
        """Create a mock relationship repository."""
        mock_repo = MagicMock(spec=RelationshipRepository)
        
        mock_repo.create.side_effect = cls._mock_create_relationship
        mock_repo.get.side_effect = cls._mock_get_relationship
        mock_repo.update.side_effect = lambda rel: rel
        mock_repo.delete.return_value = True
        mock_repo.list_all.return_value = cls._get_sample_relationships()
        mock_repo.find_by_kind.return_value = cls._get_sample_relationships()
        mock_repo.find_by_source.return_value = cls._get_sample_relationships()
        mock_repo.find_by_target.return_value = cls._get_sample_relationships()
        
        return mock_repo
    
    # Helper methods for creating sample data
    
    @staticmethod
    def _mock_create_node(node: Node) -> Node:
        """Mock node creation that returns the node with a generated ID."""
        if not node.id:
            node.id = uuid.uuid4()
        return node
    
    @staticmethod
    def _mock_get_node(node_id: uuid.UUID) -> Optional[Node]:
        """Mock node retrieval."""
        return Actor(id=node_id, label="Mock Actor", sector="Test")
    
    @staticmethod
    def _mock_update_node(node: Node) -> Node:
        """Mock node update that returns the updated node."""
        return node
    
    @staticmethod
    def _mock_create_relationship(relationship: Relationship) -> Relationship:
        """Mock relationship creation."""
        if not relationship.id:
            relationship.id = uuid.uuid4()
        return relationship
    
    @staticmethod
    def _mock_get_relationship(rel_id: uuid.UUID) -> Optional[Relationship]:
        """Mock relationship retrieval."""
        return Relationship(
            id=rel_id,
            source_id=uuid.uuid4(),
            target_id=uuid.uuid4(),
            kind=RelationshipKind.AFFECTS
        )
    
    @staticmethod
    def _mock_update_relationship(relationship: Relationship) -> Relationship:
        """Mock relationship update."""
        return relationship
    
    @staticmethod
    def _mock_find_nodes_by_type(node_type: Type[T]) -> List[Node]:
        """Mock finding nodes by type."""
        return [MockRepositoryFactory._create_sample_node(node_type) for _ in range(2)]
    
    @staticmethod
    def _mock_find_relationships_by_kind(kind: RelationshipKind) -> List[Relationship]:
        """Mock finding relationships by kind."""
        return MockRepositoryFactory._get_sample_relationships()
    
    @staticmethod
    def _create_sample_node(node_type: Type[T], **kwargs) -> Node:
        """Create a sample node of the specified type."""
        node_id = kwargs.get('id', uuid.uuid4())
        
        if node_type == Actor:
            return Actor(id=node_id, label="Sample Actor", sector="Test", **kwargs)
        elif node_type == Institution:
            return Institution(id=node_id, label="Sample Institution", **kwargs)
        elif node_type == Policy:
            return Policy(id=node_id, label="Sample Policy", authority="Test Authority", **kwargs)
        elif node_type == Resource:
            return Resource(id=node_id, label="Sample Resource", **kwargs)
        else:
            # Generic node creation
            return node_type(id=node_id, label="Sample Node", **kwargs)
    
    @staticmethod
    def _get_sample_nodes() -> List[Node]:
        """Get a list of sample nodes for testing."""
        return [
            Actor(label="Sample Actor 1", sector="Government"),
            Institution(label="Sample Institution 1"),
            Policy(label="Sample Policy 1", authority="Federal"),
            Resource(label="Sample Resource 1")
        ]
    
    @staticmethod
    def _get_sample_relationships() -> List[Relationship]:
        """Get a list of sample relationships for testing."""
        return [
            Relationship(
                source_id=uuid.uuid4(),
                target_id=uuid.uuid4(),
                kind=RelationshipKind.GOVERNS,
                weight=0.8
            ),
            Relationship(
                source_id=uuid.uuid4(),
                target_id=uuid.uuid4(),
                kind=RelationshipKind.INFLUENCES,
                weight=0.6
            )
        ]


class MockNetworkXRepository:
    """Mock specifically for NetworkX repository functionality."""
    
    def __init__(self):
        self.graph = MagicMock()
        self.nodes = {}
        self.relationships = {}
    
    def mock_graph_operations(self):
        """Configure mock for common graph operations."""
        self.graph.add_node.side_effect = self._add_node
        self.graph.add_edge.side_effect = self._add_edge
        self.graph.remove_node.side_effect = self._remove_node
        self.graph.remove_edge.side_effect = self._remove_edge
        self.graph.nodes.return_value = list(self.nodes.keys())
        self.graph.edges.return_value = list(self.relationships.keys())
        self.graph.number_of_nodes.return_value = len(self.nodes)
        self.graph.number_of_edges.return_value = len(self.relationships)
    
    def _add_node(self, node_id, **attrs):
        """Mock adding a node to the graph."""
        self.nodes[node_id] = attrs
    
    def _add_edge(self, source, target, **attrs):
        """Mock adding an edge to the graph."""
        edge_key = (source, target)
        self.relationships[edge_key] = attrs
    
    def _remove_node(self, node_id):
        """Mock removing a node from the graph."""
        if node_id in self.nodes:
            del self.nodes[node_id]
    
    def _remove_edge(self, source, target):
        """Mock removing an edge from the graph."""
        edge_key = (source, target)
        if edge_key in self.relationships:
            del self.relationships[edge_key]
