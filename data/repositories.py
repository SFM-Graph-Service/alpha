"""
Enhanced Abstract data access layer for Social Fabric Matrix (SFM) graph data.
Provides comprehensive CRUD operations with support for all data classes and storage backends.
Default implementation uses NetworkX for in-memory graph storage.
"""

from abc import ABC, abstractmethod
import uuid
from typing import Optional, Any, List, Type, TypeVar, Generic, cast, Dict
import networkx as nx
from datetime import datetime, timedelta

from models import (
    Node,
    Actor,
    Institution,
    Resource,
    Process,
    Flow,
    Relationship,
    BeliefSystem,
    Policy,
    TechnologySystem,
    Indicator,
    FeedbackLoop,
    AnalyticalContext,
    SystemProperty,
    TimeSlice,
    SpatialUnit,
)
from graph import SFMGraph

from models.sfm_enums import ResourceType, InstitutionLayer, ValueCategory,RelationshipKind
from models.exceptions import (
    SFMValidationError,
    SFMNotFoundError,
    NodeCreationError,
    RelationshipValidationError,
)

T = TypeVar("T", bound=Node)


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
    def list_relationships(
        self, kind: Optional[RelationshipKind] = None
    ) -> List[Relationship]:
        """List all relationships, optionally filtered by kind."""
        pass

    @abstractmethod
    def find_relationships(
        self,
        source_id: Optional[uuid.UUID] = None,
        target_id: Optional[uuid.UUID] = None,
        kind: Optional[RelationshipKind] = None,
    ) -> List[Relationship]:
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

    # Enhanced methods for temporal and spatial queries
    @abstractmethod
    def find_nodes_by_time(
        self, time_slice: TimeSlice, node_type: Optional[Type[Node]] = None
    ) -> List[Node]:
        """Find nodes associated with a specific time slice."""
        pass

    @abstractmethod
    def find_nodes_by_space(
        self, spatial_unit: SpatialUnit, node_type: Optional[Type[Node]] = None
    ) -> List[Node]:
        """Find nodes associated with a specific spatial unit."""
        pass

    @abstractmethod
    def find_relationships_by_time(self, time_slice: TimeSlice) -> List[Relationship]:
        """Find relationships associated with a specific time slice."""
        pass

    @abstractmethod
    def find_relationships_by_space(
        self, spatial_unit: SpatialUnit
    ) -> List[Relationship]:
        """Find relationships associated with a specific spatial unit."""
        pass


class NetworkXSFMRepository(SFMRepository):
    """
    Enhanced NetworkX-based implementation of SFMRepository for in-memory storage.
    """

    def __init__(self):
        """Initialize the repository with an empty NetworkX graph."""
        self.graph: nx.MultiDiGraph[uuid.UUID] = nx.MultiDiGraph()

    def create_node(self, node: Node) -> Node:
        """Create a new node in the repository."""
        if node.id in self.graph:
            raise NodeCreationError(
                f"Node with ID {node.id} already exists",
                node_type=type(node).__name__,
                node_id=node.id
            )

        # Add node to graph with its full data
        self.graph.add_node(node.id, data=node)
        return node

    def read_node(self, node_id: uuid.UUID) -> Optional[Node]:
        """Read a node by its ID."""
        if node_id not in self.graph:
            return None

        # Return the node data stored in the graph
        return self.graph.nodes[node_id].get("data")

    def update_node(self, node: Node) -> Node:
        """Update an existing node."""
        if node.id not in self.graph:
            raise SFMNotFoundError(
                entity_type=type(node).__name__,
                entity_id=node.id
            )

        # Update node data in the graph
        self.graph.nodes[node.id]["data"] = node
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
        result: List[Node] = []

        for node_id in self.graph.nodes:
            node = self.graph.nodes[node_id].get("data")
            if node is None:
                continue

            if node_type is None or isinstance(node, node_type):
                result.append(node)

        return result

    def create_relationship(self, rel: Relationship) -> Relationship:
        """Create a new relationship in the repository."""
        # Verify source and target nodes exist
        if rel.source_id not in self.graph:
            raise SFMNotFoundError(
                entity_type="Node",
                entity_id=rel.source_id
            )
        if rel.target_id not in self.graph:
            raise SFMNotFoundError(
                entity_type="Node", 
                entity_id=rel.target_id
            )

        # Check if relationship already exists
        for _, _, key, _ in self.graph.edges(data=True, keys=True):
            if key == rel.id:
                raise RelationshipValidationError(
                    f"Relationship with ID {rel.id} already exists",
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    relationship_kind=str(rel.kind.value) if rel.kind else None
                )

        # Add relationship to graph as an edge with its data
        self.graph.add_edge(rel.source_id, rel.target_id, key=rel.id, data=rel)
        return rel

    def read_relationship(self, rel_id: uuid.UUID) -> Optional[Relationship]:
        """Read a relationship by its ID."""
        # Search for the relationship in edges
        for _, _, key, data in self.graph.edges(data=True, keys=True):
            if key == rel_id:
                return data.get("data")

        return None

    def update_relationship(self, rel: Relationship) -> Relationship:
        """Update an existing relationship."""
        # Find the relationship by ID
        for u, v, key in self.graph.edges(keys=True):
            if key == rel.id:
                # Update the relationship data
                self.graph[u][v][key]["data"] = rel
                return rel

        raise SFMNotFoundError(
            entity_type="Relationship",
            entity_id=rel.id
        )

    def delete_relationship(self, rel_id: uuid.UUID) -> bool:
        """Delete a relationship by its ID."""
        # Find the relationship by ID
        for u, v, key in self.graph.edges(keys=True):
            if key == rel_id:
                # Remove the edge
                self.graph.remove_edge(u, v, key=key)
                return True

        return False

    def list_relationships(
        self, kind: Optional[RelationshipKind] = None
    ) -> List[Relationship]:
        """List all relationships, optionally filtered by kind."""
        result = []

        for _, _, _, data in self.graph.edges(data=True, keys=True):
            rel = data.get("data")
            if rel is None:
                continue

            if kind is None or rel.kind == kind:
                result.append(rel)

        return result

    def find_relationships(
        self,
        source_id: Optional[uuid.UUID] = None,
        target_id: Optional[uuid.UUID] = None,
        kind: Optional[RelationshipKind] = None,
    ) -> List[Relationship]:
        """Find relationships matching the specified criteria."""
        result = []

        for _, _, _, data in self.graph.edges(data=True, keys=True):
            rel = data.get("data")
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

    def find_nodes_by_time(
        self, time_slice: TimeSlice, node_type: Optional[Type[Node]] = None
    ) -> List[Node]:
        """Find nodes associated with a specific time slice."""
        result: List[Node] = []

        for node in self.list_nodes(node_type):
            # Check if node is a Flow and has time attribute
            if isinstance(node, Flow) and node.time == time_slice:
                result.append(node)

        return result

    def find_nodes_by_space(
        self, spatial_unit: SpatialUnit, node_type: Optional[Type[Node]] = None
    ) -> List[Node]:
        """Find nodes associated with a specific spatial unit."""
        result: List[Node] = []

        for node in self.list_nodes(node_type):
            # Check if node is a Flow and has space attribute
            if isinstance(node, Flow) and node.space == spatial_unit:
                result.append(node)

        return result

    def find_relationships_by_time(self, time_slice: TimeSlice) -> List[Relationship]:
        """Find relationships associated with a specific time slice."""
        result = []

        for rel in self.list_relationships():
            if rel.time == time_slice:
                result.append(rel)

        return result

    def find_relationships_by_space(
        self, spatial_unit: SpatialUnit
    ) -> List[Relationship]:
        """Find relationships associated with a specific spatial unit."""
        result = []

        for rel in self.list_relationships():
            if rel.space == spatial_unit:
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


# Enhanced typed repositories for all node types


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
            raise TypeError(
                f"Expected {self.node_type.__name__}, got {type(node).__name__}"
            )

        result = self.base_repo.create_node(node)
        return result

    def read(self, node_id: uuid.UUID) -> Optional[T]:
        """Read a node by its ID."""
        result = self.base_repo.read_node(node_id)

        if result is None or not isinstance(result, self.node_type):
            return None

        return result

    def update(self, node: T) -> T:
        """Update an existing node."""
        if not isinstance(node, self.node_type):
            raise TypeError(
                f"Expected {self.node_type.__name__}, got {type(node).__name__}"
            )

        result = self.base_repo.update_node(node)
        return result  # Ensure the return type matches the expected type

    def delete(self, node_id: uuid.UUID) -> bool:
        """Delete a node by its ID."""
        return self.base_repo.delete_node(node_id)

    def list_all(self) -> List[T]:
        """List all nodes of the specific type."""
        results = self.base_repo.list_nodes(self.node_type)
        return [cast(T, node) for node in results]

    def query(self, filters: Dict[str, Any]) -> List[T]:
        """Query nodes based on attribute filters."""
        nodes = self.list_all()

        result: List[T] = []
        for node in nodes:
            matches = True
            for attr, value in filters.items():
                if not hasattr(node, attr) or getattr(node, attr) != value:
                    matches = False
                    break

            if matches:
                result.append(node)

        return result

    def find_by_time(self, time_slice: TimeSlice) -> List[T]:
        """Find nodes of this type associated with a time slice."""
        results = self.base_repo.find_nodes_by_time(time_slice, self.node_type)
        return [cast(T, node) for node in results]

    def find_by_space(self, spatial_unit: SpatialUnit) -> List[T]:
        """Find nodes of this type associated with a spatial unit."""
        results = self.base_repo.find_nodes_by_space(spatial_unit, self.node_type)
        return [cast(T, node) for node in results]


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

    def find_by_layer(self, layer: InstitutionLayer) -> List[Institution]:
        """Find institutions by layer."""
        return [i for i in self.list_all() if i.layer == layer]


class PolicyRepository(TypedSFMRepository[Policy]):
    """Repository for Policy entities."""

    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, Policy)

    def find_by_authority(self, authority: str) -> List[Policy]:
        """Find policies by implementing authority."""
        return [p for p in self.list_all() if p.authority == authority]

    def find_by_target_sector(self, sector: str) -> List[Policy]:
        """Find policies targeting a specific sector."""
        return [
            p
            for p in self.list_all()
            if p.target_sectors and sector in p.target_sectors
        ]

    def find_by_enforcement_level(self, min_enforcement: float) -> List[Policy]:
        """Find policies with enforcement level above threshold."""
        return [
            p
            for p in self.list_all()
            if p.enforcement and p.enforcement >= min_enforcement
        ]


class ResourceRepository(TypedSFMRepository[Resource]):
    """Repository for Resource entities."""

    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, Resource)

    def find_by_type(self, rtype: ResourceType) -> List[Resource]:
        """Find resources by resource type."""
        return [r for r in self.list_all() if r.rtype == rtype]

    def find_by_unit(self, unit: str) -> List[Resource]:
        """Find resources by unit of measurement."""
        return [r for r in self.list_all() if r.unit == unit]


class ProcessRepository(TypedSFMRepository[Process]):
    """Repository for Process entities."""

    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, Process)

    def find_by_technology(self, technology: str) -> List[Process]:
        """Find processes by technology."""
        return [p for p in self.list_all() if p.technology == technology]

    def find_by_responsible_actor(self, actor_id: str) -> List[Process]:
        """Find processes by responsible actor."""
        return [p for p in self.list_all() if p.responsible_actor_id == actor_id]


class FlowRepository(TypedSFMRepository[Flow]):
    """Repository for Flow entities."""

    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, Flow)

    def find_by_nature(self, nature: str) -> List[Flow]:
        """Find flows by nature (input, output, transfer)."""
        return [f for f in self.list_all() if str(f.nature.value) == nature]

    def find_by_quantity_range(self, min_qty: float, max_qty: float) -> List[Flow]:
        """Find flows within quantity range."""
        return [
            f
            for f in self.list_all()
            if f.quantity is not None and min_qty <= f.quantity <= max_qty
        ]


class BeliefSystemRepository(TypedSFMRepository[BeliefSystem]):
    """Repository for BeliefSystem entities."""

    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, BeliefSystem)

    def find_by_domain(self, domain: str) -> List[BeliefSystem]:
        """Find belief systems by domain."""
        return [b for b in self.list_all() if b.domain == domain]

    def find_by_strength_range(
        self, min_strength: float, max_strength: float
    ) -> List[BeliefSystem]:
        """Find belief systems within strength range."""
        return [
            b
            for b in self.list_all()
            if b.strength is not None and min_strength <= b.strength <= max_strength
        ]


class TechnologySystemRepository(TypedSFMRepository[TechnologySystem]):
    """Repository for TechnologySystem entities."""

    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, TechnologySystem)

    def find_by_maturity_range(
        self, min_maturity: int, max_maturity: int
    ) -> List[TechnologySystem]:
        """Find technology systems within maturity range (TRL 1-9)."""
        return [
            t
            for t in self.list_all()
            if t.maturity is not None and min_maturity <= t.maturity.value <= max_maturity
        ]

    def find_compatible_with(
        self, system_name: str, min_compatibility: float = 0.5
    ) -> List[TechnologySystem]:
        """Find technology systems compatible with given system."""
        return [
            t
            for t in self.list_all()
            if (
                t.compatibility
                and system_name in t.compatibility
                and t.compatibility[system_name] >= min_compatibility
            )
        ]


class IndicatorRepository(TypedSFMRepository[Indicator]):
    """Repository for Indicator entities."""

    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, Indicator)

    def find_by_value_category(self, category: ValueCategory) -> List[Indicator]:
        """Find indicators by value category."""
        return [i for i in self.list_all() if i.value_category == category]

    def find_by_current_value_range(
        self, min_value: float, max_value: float
    ) -> List[Indicator]:
        """Find indicators within current value range."""
        return [
            i
            for i in self.list_all()
            if i.current_value is not None and min_value <= i.current_value <= max_value
        ]

    def find_above_target(self) -> List[Indicator]:
        """Find indicators where current value exceeds target."""
        return [
            i
            for i in self.list_all()
            if (
                i.current_value is not None
                and i.target_value is not None
                and i.current_value > i.target_value
            )
        ]

    def find_below_target(self) -> List[Indicator]:
        """Find indicators where current value is below target."""
        return [
            i
            for i in self.list_all()
            if (
                i.current_value is not None
                and i.target_value is not None
                and i.current_value < i.target_value
            )
        ]


class FeedbackLoopRepository(TypedSFMRepository[FeedbackLoop]):
    """Repository for FeedbackLoop entities."""

    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, FeedbackLoop)

    def find_by_polarity(self, polarity: str) -> List[FeedbackLoop]:
        """Find feedback loops by polarity."""
        return [f for f in self.list_all() if f.polarity and f.polarity.value == int(polarity)]

    def find_by_strength_range(
        self, min_strength: float, max_strength: float
    ) -> List[FeedbackLoop]:
        """Find feedback loops within strength range."""
        return [
            f
            for f in self.list_all()
            if f.strength is not None and min_strength <= f.strength <= max_strength
        ]

    def find_containing_relationship(
        self, relationship_id: uuid.UUID
    ) -> List[FeedbackLoop]:
        """Find feedback loops containing a specific relationship."""
        return [f for f in self.list_all() if relationship_id in f.relationships]


class SystemPropertyRepository(TypedSFMRepository[SystemProperty]):
    """Repository for SystemProperty entities."""

    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, SystemProperty)

    def find_by_property_type(self, property_type: str) -> List[SystemProperty]:
        """Find system properties by type."""
        return [s for s in self.list_all() if str(s.property_type) == property_type]

    def find_affecting_node(self, node_id: uuid.UUID) -> List[SystemProperty]:
        """Find system properties affecting a specific node."""
        return [s for s in self.list_all() if node_id in s.affected_nodes]

    def find_by_timestamp_range(
        self, start_time: datetime, end_time: datetime
    ) -> List[SystemProperty]:
        """Find system properties within timestamp range."""
        return [s for s in self.list_all() if start_time <= s.timestamp <= end_time]


class AnalyticalContextRepository(TypedSFMRepository[AnalyticalContext]):
    """Repository for AnalyticalContext entities."""

    def __init__(self, base_repo: SFMRepository):
        super().__init__(base_repo, AnalyticalContext)

    def find_by_method(self, method: str) -> List[AnalyticalContext]:
        """Find analytical contexts using a specific method."""
        return [a for a in self.list_all() if method in a.methods_used]

    def find_by_data_source(self, source_name: str) -> List[AnalyticalContext]:
        """Find analytical contexts using a specific data source."""
        return [a for a in self.list_all() if source_name in a.data_sources]

    def find_recent(self, days: int = 30) -> List[AnalyticalContext]:
        """Find analytical contexts created within the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [a for a in self.list_all() if a.created_at >= cutoff_date]


class RelationshipRepository:
    """Enhanced repository for Relationship entities."""

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

    def find_by_nodes(
        self, source_id: uuid.UUID, target_id: uuid.UUID
    ) -> List[Relationship]:
        """Find relationships between specific source and target nodes."""
        return self.base_repo.find_relationships(
            source_id=source_id, target_id=target_id
        )

    def find_by_weight_range(
        self, min_weight: float, max_weight: float
    ) -> List[Relationship]:
        """Find relationships within weight range."""
        return [
            r
            for r in self.list_all()
            if r.weight is not None and min_weight <= r.weight <= max_weight
        ]

    def find_by_certainty_range(
        self, min_certainty: float, max_certainty: float
    ) -> List[Relationship]:
        """Find relationships within certainty range."""
        return [
            r
            for r in self.list_all()
            if r.certainty is not None and min_certainty <= r.certainty <= max_certainty
        ]

    def find_by_time(self, time_slice: TimeSlice) -> List[Relationship]:
        """Find relationships by time slice."""
        return self.base_repo.find_relationships_by_time(time_slice)

    def find_by_space(self, spatial_unit: SpatialUnit) -> List[Relationship]:
        """Find relationships by spatial unit."""
        return self.base_repo.find_relationships_by_space(spatial_unit)


# Enhanced factory with all repository types
class SFMRepositoryFactory:
    """Enhanced factory for creating SFM repositories with different storage backends."""

    @staticmethod
    def create_repository(storage_type: str = "networkx") -> SFMRepository:
        """
        Create a new SFM repository.

        Args:
            storage_type: The type of storage backend to use.
                          Currently supported: "networkx" (in-memory), "test" (for testing)

        Returns:
            An SFM repository implementation

        Raises:
            ValueError: If the storage type is not supported
        """
        if storage_type.lower() in ("networkx", "test"):
            return NetworkXSFMRepository()
        else:
            raise SFMValidationError(f"Unsupported storage type: {storage_type}", "storage_type", storage_type)

    @staticmethod
    def create_actor_repository(storage_type: str = "networkx") -> ActorRepository:
        """Create a repository for Actor entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return ActorRepository(base_repo)

    @staticmethod
    def create_institution_repository(
        storage_type: str = "networkx",
    ) -> InstitutionRepository:
        """Create a repository for Institution entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return InstitutionRepository(base_repo)

    @staticmethod
    def create_policy_repository(storage_type: str = "networkx") -> PolicyRepository:
        """Create a repository for Policy entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return PolicyRepository(base_repo)

    @staticmethod
    def create_resource_repository(
        storage_type: str = "networkx",
    ) -> ResourceRepository:
        """Create a repository for Resource entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return ResourceRepository(base_repo)

    @staticmethod
    def create_process_repository(storage_type: str = "networkx") -> ProcessRepository:
        """Create a repository for Process entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return ProcessRepository(base_repo)

    @staticmethod
    def create_flow_repository(storage_type: str = "networkx") -> FlowRepository:
        """Create a repository for Flow entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return FlowRepository(base_repo)

    @staticmethod
    def create_belief_system_repository(
        storage_type: str = "networkx",
    ) -> BeliefSystemRepository:
        """Create a repository for BeliefSystem entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return BeliefSystemRepository(base_repo)

    @staticmethod
    def create_technology_system_repository(
        storage_type: str = "networkx",
    ) -> TechnologySystemRepository:
        """Create a repository for TechnologySystem entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return TechnologySystemRepository(base_repo)

    @staticmethod
    def create_indicator_repository(
        storage_type: str = "networkx",
    ) -> IndicatorRepository:
        """Create a repository for Indicator entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return IndicatorRepository(base_repo)

    @staticmethod
    def create_feedback_loop_repository(
        storage_type: str = "networkx",
    ) -> FeedbackLoopRepository:
        """Create a repository for FeedbackLoop entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return FeedbackLoopRepository(base_repo)

    @staticmethod
    def create_system_property_repository(
        storage_type: str = "networkx",
    ) -> SystemPropertyRepository:
        """Create a repository for SystemProperty entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return SystemPropertyRepository(base_repo)

    @staticmethod
    def create_analytical_context_repository(
        storage_type: str = "networkx",
    ) -> AnalyticalContextRepository:
        """Create a repository for AnalyticalContext entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return AnalyticalContextRepository(base_repo)

    @staticmethod
    def create_relationship_repository(
        storage_type: str = "networkx",
    ) -> RelationshipRepository:
        """Create a repository for Relationship entities."""
        base_repo = SFMRepositoryFactory.create_repository(storage_type)
        return RelationshipRepository(base_repo)

    @staticmethod
    def create_all_repositories(storage_type: str = "networkx") -> Dict[str, Any]:
        """Create all repository types and return as a dictionary."""
        # Create a single shared base repository
        base_repo = SFMRepositoryFactory.create_repository(storage_type)

        return {
            "base": base_repo,
            "actor": ActorRepository(base_repo),
            "institution": InstitutionRepository(base_repo),
            "policy": PolicyRepository(base_repo),
            "resource": ResourceRepository(base_repo),
            "process": ProcessRepository(base_repo),
            "flow": FlowRepository(base_repo),
            "belief_system": BeliefSystemRepository(base_repo),
            "technology_system": TechnologySystemRepository(base_repo),
            "indicator": IndicatorRepository(base_repo),
            "feedback_loop": FeedbackLoopRepository(base_repo),
            "system_property": SystemPropertyRepository(base_repo),
            "analytical_context": AnalyticalContextRepository(base_repo),
            "relationship": RelationshipRepository(base_repo),
        }
