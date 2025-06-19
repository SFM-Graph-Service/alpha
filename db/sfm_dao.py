"""
Abstract data access layer for Social Fabric Matrix (SFM) graph data.
Provides CRUD operations with support for different storage backends.
Default implementation uses NetworkX for in-memory graph storage.
"""

from abc import ABC, abstractmethod
import uuid
from typing import Dict, List, Optional, TypeVar, Generic, Type, Any, cast
import networkx as nx

from core.sfm_models import (
    Node, Actor, Institution, Resource, Process, Flow, Relationship,
    BeliefSystem, Policy, TechnologySystem, Indicator, FeedbackLoop,
    AnalyticalContext, SystemProperty, SFMGraph, RelationshipKind
)

from core.enums import ResourceType

T = TypeVar('T', bound=Node)

class SFMRepository(ABC):
    """
    Abstract repository interface for SFM graph data with CRUD operations.
    """
    
    @abstractmethod
    def create_node(self, node: Node) -> Node:
        """Create a new node in the repository."""
        pass
    
    @abstractmethod
    def read_node(self, node_id: uuid.UUID) -> Optional[Node]:
        """Read a node by its ID."""
        pass
    
    @abstractmethod
    def update_node(self, node: Node) -> Node:
        """Update an existing node."""
        pass
    
    @abstractmethod
    def delete_node(self, node_id: uuid.UUID) -> bool:
        """Delete a node by its ID."""
        pass
    
    @abstractmethod
    def list_nodes(self, node_type: Optional[Type[Node]] = None) -> List[Node]:
        """List all nodes, optionally filtered by type."""
        pass
    
    @abstractmethod
    def create_relationship(self, rel: Relationship) -> Relationship:
        """Create a new relationship in the repository."""
        pass
    
    @abstractmethod
    def read_relationship(self, rel_id: uuid.UUID) -> Optional[Relationship]:
        """Read a relationship by its ID."""
        pass
    
    @abstractmethod
    def update_relationship(self, rel: Relationship) -> Relationship:
        """Update an existing relationship."""
        pass
    
    @abstractmethod
    def delete_relationship(self, rel_id: uuid.UUID) -> bool:
        """Delete a relationship by its ID."""
        pass
    
    @abstractmethod
    def list_relationships(self, kind: Optional[RelationshipKind] = None) -> List[Relationship]:
        """List all relationships, optionally filtered by kind."""
        pass
    
    @abstractmethod
    def find_relationships(self, 
                          source_id: Optional[uuid.UUID] = None,
                          target_id: Optional[uuid.UUID] = None,
                          kind: Optional[RelationshipKind] = None) -> List[Relationship]:
        """Find relationships matching the specified criteria."""
        pass
    
    @abstractmethod
    def load_graph(self) -> SFMGraph:
        """Load the complete SFM graph."""
        pass
    
    @abstractmethod
    def save_graph(self, graph: SFMGraph) -> None:
        """Save the complete SFM graph."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all data from the repository."""
        pass


class NetworkXSFMRepository(SFMRepository):
    """
    NetworkX-based implementation of SFMRepository for in-memory storage.
    """
    
    def __init__(self):
        """Initialize the repository with an empty NetworkX graph."""
        self.graph = nx.MultiDiGraph()
    
    def create_node(self, node: Node) -> Node:
        """Create a new node in the repository."""
        if node.id in self.graph:
            raise ValueError(f"Node with ID {node.id} already exists")
        
        # Add node to graph with its full data
        self.graph.add_node(node.id, data=node)
        return node
    
    def read_node(self, node_id: uuid.UUID) -> Optional[Node]:
        """Read a node by its ID."""
        if node_id not in self.graph:
            return None
        
        # Return the node data stored in the graph
        return self.graph.nodes[node_id].get('data')
    
    def update_node(self, node: Node) -> Node:
        """Update an existing node."""
        if node.id not in self.graph:
            raise ValueError(f"Node with ID {node.id} does not exist")
        
        # Update node data in the graph
        self.graph.nodes[node.id]['data'] = node
        return node
    
    def delete_node(self, node_id: uuid.UUID) -> bool:
        """Delete a node by its ID."""
        if node_id not in self.graph:
            return False
        
        # Remove the node from the graph
        self.graph.remove_node(node_id)
        return True
    
    def list_nodes(self, node_type: Optional[Type[Node]] = None) -> List[Node]:
        """List all nodes, optionally filtered by type."""
        result = []
        
        for node_id in self.graph.nodes:
            node = self.graph.nodes[node_id].get('data')
            if node is None:
                continue
                
            if node_type is None or isinstance(node, node_type):
                result.append(node)
        
        return result
    
    def create_relationship(self, rel: Relationship) -> Relationship:
        """Create a new relationship in the repository."""
        # Verify source and target nodes exist
        if rel.source_id not in self.graph:
            raise ValueError(f"Source node with ID {rel.source_id} does not exist")
        if rel.target_id not in self.graph:
            raise ValueError(f"Target node with ID {rel.target_id} does not exist")
        
        # Check if relationship already exists
        for _, _, key, data in self.graph.edges(data=True, keys=True):
            if key == rel.id:
                raise ValueError(f"Relationship with ID {rel.id} already exists")
        
        # Add relationship to graph as an edge with its data
        self.graph.add_edge(rel.source_id, rel.target_id, key=rel.id, data=rel)
        return rel
    
    def read_relationship(self, rel_id: uuid.UUID) -> Optional[Relationship]:
        """Read a relationship by its ID."""
        # Search for the relationship in edges
        for u, v, key, data in self.graph.edges(data=True, keys=True):
            if key == rel_id:
                return data.get('data')
        
        return None
    
    def update_relationship(self, rel: Relationship) -> Relationship:
        """Update an existing relationship."""
        # Find the relationship by ID
        for u, v, key in self.graph.edges(keys=True):
            if key == rel.id:
                # Update the relationship data
                self.graph[u][v][key]['data'] = rel
                return rel
        
        raise ValueError(f"Relationship with ID {rel.id} does not exist")
    
    def delete_relationship(self, rel_id: uuid.UUID) -> bool:
        """Delete a relationship by its ID."""
        # Find the relationship by ID
        for u, v, key in self.graph.edges(keys=True):
            if key == rel_id:
                # Remove the edge
                self.graph.remove_edge(u, v, key=key)
                return True
        
        return False
    
    def list_relationships(self, kind: Optional[RelationshipKind] = None) -> List[Relationship]:
        """List all relationships, optionally filtered by kind."""
        result = []
        
        for u, v, key, data in self.graph.edges(data=True, keys=True):
            rel = data.get('data')
            if rel is None:
                continue
                
            if kind is None or rel.kind == kind:
                result.append(rel)
        
        return result
    
    def find_relationships(self, 
                          source_id: Optional[uuid.UUID] = None,
                          target_id: Optional[uuid.UUID] = None,
                          kind: Optional[RelationshipKind] = None) -> List[Relationship]:
        """Find relationships matching the specified criteria."""
        result = []
        
        for u, v, key, data in self.graph.edges(data=True, keys=True):
            rel = data.get('data')
            if rel is None:
                continue
            
            # Apply filters
            if source_id is not None and rel.source_id != source_id:
                continue
            if target_id is not None and rel.target_id != target_id:
                continue
            if kind is not None and rel.kind != kind:
                continue
            
            result.append(rel)
        
        return result
    
    def load_graph(self) -> SFMGraph:
        """Load the complete SFM graph from the repository."""
        sfm_graph = SFMGraph()
        
        # Load all nodes
        for node in self.list_nodes():
            sfm_graph.add_node(node)
        
        # Load all relationships
        for rel in self.list_relationships():
            sfm_graph.add_relationship(rel)
        
        return sfm_graph
    
    def save_graph(self, graph: SFMGraph) -> None:
        """Save the complete SFM graph to the repository."""
        # Clear existing data
        self.clear()
        
        # Add all nodes
        for node in graph:
            self.create_node(node)
        
        # Add all relationships
        for rel in graph.relationships.values():
            self.create_relationship(rel)
    
    def clear(self) -> None:
        """Clear all data from the repository."""
        self.graph.clear()


# Additional specialized repositories for specific node types

class TypedSFMRepository(Generic[T]):
    """
    Type-safe repository for specific node types, built on top of SFMRepository.
    """
    
    def __init__(self, base_repo: SFMRepository, node_type: Type[T]):
        """
        Initialize with a base repository and the specific node type.
        
        Args:
            base_repo: The underlying SFM repository
            node_type: The specific Node subtype this repository handles
        """
        self.base_repo = base_repo
        self.node_type = node_type
    
    def create(self, node: T) -> T:
        """Create a new node of the specific type."""
        if not isinstance(node, self.node_type):
            raise TypeError(f"Expected {self.node_type.__name__}, got {type(node).__name__}")
        
        result = self.base_repo.create_node(node)
        return cast(T, result)
    
    def read(self, node_id: uuid.UUID) -> Optional[T]:
        """Read a node by its ID."""
        result = self.base_repo.read_node(node_id)
        
        if result is None or not isinstance(result, self.node_type):
            return None
        
        return cast(T, result)
    
    def update(self, node: T) -> T:
        """Update an existing node."""
        if not isinstance(node, self.node_type):
            raise TypeError(f"Expected {self.node_type.__name__}, got {type(node).__name__}")
        
        result = self.base_repo.update_node(node)
        return cast(T, result)
    
    def delete(self, node_id: uuid.UUID) -> bool:
        """Delete a node by its ID."""
        return self.base_repo.delete_node(node_id)
    
    def list_all(self) -> List[T]:
        """List all nodes of the specific type."""
        results = self.base_repo.list_nodes(self.node_type)
        return [cast(T, node) for node in results]
    
    def query(self, filters: Dict[str, Any]) -> List[T]:
        """Query nodes based on attribute filters."""
        # Get all nodes of this type
        nodes = self.list_all()
        
        # Apply filters
        result = []
        for node in nodes:
            matches = True
            for attr, value in filters.items():
                if not hasattr(node, attr) or getattr(node, attr) != value:
                    matches = False
                    break
            
            if matches:
                result.append(node)
        
        return result


class ActorRepository(TypedSFMRepository[Actor]):
    """Repository for Actor entities."""
    
    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, Actor)
    
    def find_by_sector(self, sector: str) -> List[Actor]:
        """Find actors by sector."""
        return [a for a in self.list_all() if a.sector == sector]
    
    def find_by_legal_form(self, legal_form: str) -> List[Actor]:
        """Find actors by legal form."""
        return [a for a in self.list_all() if a.legal_form == legal_form]


class InstitutionRepository(TypedSFMRepository[Institution]):
    """Repository for Institution entities."""
    
    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, Institution)


class PolicyRepository(TypedSFMRepository[Policy]):
    """Repository for Policy entities."""
    
    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, Policy)
    
    def find_by_authority(self, authority: str) -> List[Policy]:
        """Find policies by implementing authority."""
        return [p for p in self.list_all() if p.authority == authority]
    
    def find_by_target_sector(self, sector: str) -> List[Policy]:
        """Find policies targeting a specific sector."""
        return [p for p in self.list_all() 
                if p.target_sectors and sector in p.target_sectors]


class ResourceRepository(TypedSFMRepository[Resource]):
    """Repository for Resource entities."""
    
    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, Resource)
    
    def find_by_type(self, rtype: ResourceType) -> List[Resource]:
        """Find resources by resource type."""
        return [r for r in self.list_all() if r.rtype == rtype]


class RelationshipRepository:
    """Repository for Relationship entities."""
    
    def __init__(self, base_repo: SFMRepository):
        self.base_repo = base_repo
    
    def create(self, relationship: Relationship) -> Relationship:
        """Create a new relationship."""
        return self.base_repo.create_relationship(relationship)
    
    def read(self, rel_id: uuid.UUID) -> Optional[Relationship]:
        """Read a relationship by its ID."""
        return self.base_repo.read_relationship(rel_id)
    
    def update(self, relationship: Relationship) -> Relationship:
        """Update an existing relationship."""
        return self.base_repo.update_relationship(relationship)
    
    def delete(self, rel_id: uuid.UUID) -> bool:
        """Delete a relationship by its ID."""
        return self.base_repo.delete_relationship(rel_id)
    
    def list_all(self) -> List[Relationship]:
        """List all relationships."""
        return self.base_repo.list_relationships()
    
    def find_by_kind(self, kind: RelationshipKind) -> List[Relationship]:
        """Find relationships by kind."""
        return self.base_repo.list_relationships(kind)
    
    def find_by_source(self, source_id: uuid.UUID) -> List[Relationship]:
        """Find relationships by source node ID."""
        return self.base_repo.find_relationships(source_id=source_id)
    
    def find_by_target(self, target_id: uuid.UUID) -> List[Relationship]:
        """Find relationships by target node ID."""
        return self.base_repo.find_relationships(target_id=target_id)
    
    def find_by_nodes(self, source_id: uuid.UUID, target_id: uuid.UUID) -> List[Relationship]:
        """Find relationships between specific source and target nodes."""
        return self.base_repo.find_relationships(source_id=source_id, target_id=target_id)


# Factory for creating repositories
class SFMRepositoryFactory:
    """Factory for creating SFM repositories with different storage backends."""
    
    @staticmethod
    def create_repository(storage_type: str = "networkx") -> SFMRepository:
        """
        Create a new SFM repository.
        
        Args:
            storage_type: The type of storage backend to use.
                          Currently supported: "networkx" (in-memory)
        
        Returns:
            An SFM repository implementation
        
        Raises:
            ValueError: If the storage type is not supported
        """
        if storage_type.lower() == "networkx":
            return NetworkXSFMRepository()
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
    
    @staticmethod
    def create_actor_repository(storage_type: str = "networkx") -> ActorRepository:
        """Create a repository for Actor entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return ActorRepository(base_repo)
    
    @staticmethod
    def create_institution_repository(storage_type: str = "networkx") -> InstitutionRepository:
        """Create a repository for Institution entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return InstitutionRepository(base_repo)
    
    @staticmethod
    def create_policy_repository(storage_type: str = "networkx") -> PolicyRepository:
        """Create a repository for Policy entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return PolicyRepository(base_repo)
    
    @staticmethod
    def create_resource_repository(storage_type: str = "networkx") -> ResourceRepository:
        """Create a repository for Resource entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return ResourceRepository(base_repo)
    
    @staticmethod
    def create_relationship_repository(storage_type: str = "networkx") -> RelationshipRepository:
        """Create a repository for Relationship entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return RelationshipRepository(base_repo)