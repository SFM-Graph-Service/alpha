"""
Graph structure and network metrics for SFM modeling.

This module defines the SFMGraph class that aggregates all SFM entities
and the NetworkMetrics class for network analysis.
"""

from __future__ import annotations

import uuid
import logging
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Iterator, Callable, Set, Type, Tuple, Any
from datetime import datetime

from core.base_nodes import Node
from core.core_nodes import (
    Actor, Institution, Policy, Resource, Process, Flow, ValueFlow, GovernanceStructure
)
from core.specialized_nodes import (
    BeliefSystem, TechnologySystem, Indicator, FeedbackLoop, SystemProperty,
    AnalyticalContext, PolicyInstrument
)
from core.behavioral_nodes import (
    ValueSystem, CeremonialBehavior, InstrumentalBehavior, ChangeProcess,
    CognitiveFramework, BehavioralPattern
)
from core.relationships import Relationship
from core.metadata_models import ModelMetadata, ValidationRule
from core.sfm_enums import EnumValidator
from core.memory_management import MemoryMonitor, MemoryUsageStats, EvictionStrategy, EvictableGraph
from core.advanced_caching import QueryCache
from core.performance_metrics import timed_operation

# Set up logger for lazy loading operations
logger = logging.getLogger(__name__)


class NodeTypeRegistry:
    """Registry pattern for mapping node types to their collections in SFMGraph."""

    def __init__(self):
        """Initialize the registry with ordered type mappings."""
        # Order matters for inheritance - most specific types first
        self._type_handlers: List[Tuple[Type[Node], str]] = [
            # Core nodes with inheritance considerations
            (ValueFlow, 'value_flows'),  # Before Flow
            (GovernanceStructure, 'governance_structures'),
            (Policy, 'policies'),  # Before Institution
            (Institution, 'institutions'),  # After Policy
            (Actor, 'actors'),
            (Resource, 'resources'),
            (Process, 'processes'),
            (Flow, 'flows'),  # After ValueFlow

            # Specialized nodes
            (BeliefSystem, 'belief_systems'),
            (TechnologySystem, 'technology_systems'),
            (Indicator, 'indicators'),
            (FeedbackLoop, 'feedback_loops'),
            (SystemProperty, 'system_properties'),
            (AnalyticalContext, 'analytical_contexts'),
            (PolicyInstrument, 'policy_instruments'),

            # Behavioral nodes
            (ValueSystem, 'value_systems'),
            (CeremonialBehavior, 'ceremonial_behaviors'),
            (InstrumentalBehavior, 'instrumental_behaviors'),
            (ChangeProcess, 'change_processes'),
            (CognitiveFramework, 'cognitive_frameworks'),
            (BehavioralPattern, 'behavioral_patterns'),

            # Graph nodes
            (NetworkMetrics, 'network_metrics'),
        ]

    def get_collection_name(self, node: Node) -> str:
        """Get the collection name for a given node type."""
        for node_type, collection_name in self._type_handlers:
            if isinstance(node, node_type):
                return collection_name
        raise TypeError(f"Unsupported node type: {type(node)}")

    def get_all_collection_names(self) -> List[str]:
        """Get all collection names in the registry."""
        return [collection_name for _, collection_name in self._type_handlers]

    def iter_collections(self, graph: 'SFMGraph') -> Iterator[Dict[uuid.UUID, Node]]:
        """Iterate over all collections in the graph."""
        for collection_name in self.get_all_collection_names():
            collection = getattr(graph, collection_name)
            yield collection


@dataclass
class NetworkMetrics(Node):
    """Captures network analysis metrics for nodes or subgraphs."""

    centrality_measures: Dict[str, float] = field(default_factory=lambda: {})
    clustering_coefficient: Optional[float] = None
    path_lengths: Dict[uuid.UUID, float] = field(default_factory=lambda: {})
    community_assignment: Optional[str] = None


@dataclass
class SFMGraph(EvictableGraph):  # pylint: disable=too-many-instance-attributes
    """A complete Social Fabric Matrix representation with advanced performance optimizations."""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    description: Optional[str] = None

    # Core SFM components
    actors: Dict[uuid.UUID, Actor] = field(default_factory=lambda: {})
    institutions: Dict[uuid.UUID, Institution] = field(default_factory=lambda: {})
    resources: Dict[uuid.UUID, Resource] = field(default_factory=lambda: {})
    processes: Dict[uuid.UUID, Process] = field(default_factory=lambda: {})
    flows: Dict[uuid.UUID, Flow] = field(default_factory=lambda: {})
    relationships: Dict[uuid.UUID, Relationship] = field(default_factory=lambda: {})
    # Optional specialized components
    belief_systems: Dict[uuid.UUID, BeliefSystem] = field(default_factory=lambda: {})
    technology_systems: Dict[uuid.UUID, TechnologySystem] = field(default_factory=lambda: {})
    indicators: Dict[uuid.UUID, Indicator] = field(default_factory=lambda: {})
    policies: Dict[uuid.UUID, Policy] = field(default_factory=lambda: {})
    feedback_loops: Dict[uuid.UUID, FeedbackLoop] = field(default_factory=lambda: {})
    system_properties: Dict[uuid.UUID, SystemProperty] = field(default_factory=lambda: {})
    analytical_contexts: Dict[uuid.UUID, AnalyticalContext] = field(default_factory=lambda: {})
    policy_instruments: Dict[uuid.UUID, PolicyInstrument] = field(default_factory=lambda: {})
    governance_structures: Dict[uuid.UUID, GovernanceStructure] = field(default_factory=lambda: {})

    # Hayden's enhanced SFM components
    value_systems: Dict[uuid.UUID, ValueSystem] = field(default_factory=lambda: {})
    ceremonial_behaviors: Dict[uuid.UUID, CeremonialBehavior] = field(default_factory=lambda: {})
    instrumental_behaviors: Dict[uuid.UUID, InstrumentalBehavior] = field(
        default_factory=lambda: {}
    )
    change_processes: Dict[uuid.UUID, ChangeProcess] = field(default_factory=lambda: {})
    cognitive_frameworks: Dict[uuid.UUID, CognitiveFramework] = field(default_factory=lambda: {})
    behavioral_patterns: Dict[uuid.UUID, BehavioralPattern] = field(default_factory=lambda: {})
    value_flows: Dict[uuid.UUID, ValueFlow] = field(default_factory=lambda: {})
    network_metrics: Dict[uuid.UUID, NetworkMetrics] = field(default_factory=lambda: {})

    # Model metadata
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    data_quality: Optional[str] = None  # Description of data quality
    previous_version_id: Optional[uuid.UUID] = None
    model_metadata: Optional[ModelMetadata] = None
    validation_rules: List[ValidationRule] = field(default_factory=lambda: [])

    # Node type registry for dispatch
    _node_registry: NodeTypeRegistry = field(
        default_factory=NodeTypeRegistry, init=False
    )

    # Performance optimization: Central node index for O(1) lookups
    _node_index: Dict[uuid.UUID, Node] = field(default_factory=lambda: {}, init=False)

    # Performance optimization: Simple relationship cache for frequently accessed relationships
    _relationship_cache: Dict[uuid.UUID, List[Relationship]] = field(
        default_factory=lambda: {}, init=False
    )
    _relationship_cache_max_size: int = field(default=1000, init=False)

    # Performance optimization: Optional lazy loading support
    _lazy_loading_enabled: bool = field(default=False, init=False)
    _node_loader: Optional[Callable[[uuid.UUID], Optional[Node]]] = field(default=None, init=False)

    # Memory management and advanced caching
    _memory_monitor: Optional[MemoryMonitor] = field(default=None, init=False)
    _query_cache: QueryCache = field(default_factory=QueryCache, init=False)
    _memory_limit_mb: float = field(default=1000.0, init=False)
    _enable_memory_management: bool = field(default=True, init=False)
    _enable_advanced_caching: bool = field(default=True, init=False)

    def __post_init__(self):
        """Initialize performance optimizations after dataclass initialization."""
        if self._enable_memory_management:
            self._memory_monitor = MemoryMonitor(
                memory_limit_mb=self._memory_limit_mb,
                warning_threshold=0.8,
                critical_threshold=0.95
            )
        
        if self._enable_advanced_caching:
            self._setup_cache_invalidation_rules()
    
    def __getstate__(self):
        """Custom pickle serialization to handle non-serializable objects."""
        state = self.__dict__.copy()
        # Remove non-serializable objects before pickling
        non_serializable = ['_memory_monitor', '_query_cache']
        for key in non_serializable:
            if key in state:
                del state[key]
        return state
    
    def __setstate__(self, state: Dict[str, Any]) -> None:
        """Custom pickle deserialization to restore non-serializable objects."""
        self.__dict__.update(state)
        # Restore non-serializable objects after unpickling
        if getattr(self, '_enable_memory_management', True):
            self._memory_monitor = MemoryMonitor(
                memory_limit_mb=getattr(self, '_memory_limit_mb', 1000.0),
                warning_threshold=0.8,
                critical_threshold=0.95
            )
        
        if getattr(self, '_enable_advanced_caching', True):
            self._query_cache = QueryCache()
            self._setup_cache_invalidation_rules()
    
    def _setup_cache_invalidation_rules(self):
        """Set up cache invalidation rules for different events."""
        if not hasattr(self, '_query_cache') or not self._query_cache:
            self._query_cache = QueryCache()
            
        # Node-related invalidations
        self._query_cache.register_invalidation_rule(
            'node_added', 
            ['get_node_relationships:{node_id}:*', 'get_nodes_by_type:*', 'count_nodes:*']
        )
        
        self._query_cache.register_invalidation_rule(
            'node_removed',
            ['get_node_relationships:{node_id}:*', 'get_nodes_by_type:*', 'count_nodes:*']
        )
        
        # Relationship-related invalidations
        self._query_cache.register_invalidation_rule(
            'relationship_added',
            ['get_node_relationships:*', 'find_paths:*', 'analyze_network:*']
        )
        
        self._query_cache.register_invalidation_rule(
            'relationship_removed', 
            ['get_node_relationships:*', 'find_paths:*', 'analyze_network:*']
        )

    @timed_operation("add_node")
    def add_node(self, node: Node) -> Node:
        """Add a node to the appropriate collection based on its type."""
        collection_name = self._node_registry.get_collection_name(node)
        collection = getattr(self, collection_name)
        collection[node.id] = node

        # Performance optimization: Maintain central index for O(1) lookups
        self._node_index[node.id] = node

        # Memory management: Record node access and check memory limits
        if self._memory_monitor:
            self._memory_monitor.record_node_access(node.id)
            if self._memory_monitor.should_evict_nodes():
                evicted = self._memory_monitor.evict_nodes(self)
                if evicted > 0:
                    logger.info(f"Evicted {evicted} nodes after adding new node")

        # Cache invalidation
        if self._enable_advanced_caching and hasattr(self, '_query_cache') and self._query_cache:
            self._query_cache.invalidate_on_event('node_added', node_id=self._get_node_id_for_cache(node.id))  # type: ignore[arg-type]

        return node

    @timed_operation("add_relationship")
    def add_relationship(self, relationship: Relationship) -> Relationship:
        """Add a relationship to the SFM graph with validation."""

        # Perform SFM-specific validation if both nodes exist
        source_node = self._find_node_by_id(relationship.source_id)
        target_node = self._find_node_by_id(relationship.target_id)

        if source_node and target_node:
            source_type = source_node.__class__.__name__
            target_type = target_node.__class__.__name__

            # Validate the relationship context
            EnumValidator.validate_relationship_context(
                relationship.kind, source_type, target_type
            )

        # Store the relationship
        self.relationships[relationship.id] = relationship

        # Performance optimization: Clear relationship cache when relationships change
        self._clear_relationship_cache()

        # Cache invalidation
        if self._enable_advanced_caching and hasattr(self, '_query_cache') and self._query_cache:
            self._query_cache.invalidate_on_event('relationship_added', 
                                               source_id=self._get_node_id_for_cache(relationship.source_id),
                                               target_id=self._get_node_id_for_cache(relationship.target_id))

        return relationship

    def _find_node_by_id(self, node_id: uuid.UUID) -> Optional[Node]:
        """Find a node by its ID using central index for O(1) lookup."""
        if self._lazy_loading_enabled:
            return self._find_node_by_id_with_lazy_loading(node_id)
        
        # Record access for memory management
        if self._memory_monitor:
            self._memory_monitor.record_node_access(node_id)
            
        return self._node_index.get(node_id)

    @timed_operation("get_node_by_id")
    def get_node_by_id(self, node_id: uuid.UUID) -> Optional[Node]:
        """Public method to retrieve a node by its ID."""
        return self._find_node_by_id(node_id)

    def __iter__(self) -> Iterator[Node]:
        """Iterate over all nodes in the SFMGraph."""
        for collection in self._node_registry.iter_collections(self):
            yield from collection.values()

    def __len__(self) -> int:
        """Return the total number of nodes in the graph."""
        return sum(
            len(collection) for collection in self._node_registry.iter_collections(self)
        )

    def clear(self) -> None:
        """Clear all nodes and relationships from the graph."""
        for collection in self._node_registry.iter_collections(self):
            collection.clear()
        self.relationships.clear()

        # Performance optimization: Clear index and cache
        self._node_index.clear()
        self._relationship_cache.clear()

    def _clear_relationship_cache(self) -> None:
        """Clear the relationship cache when relationships change."""
        self._relationship_cache.clear()

    def _get_node_id_for_cache(self, node_id: uuid.UUID) -> str:
        """Convert node ID to string format for cache operations."""
        return str(node_id)

    @timed_operation("get_node_relationships")
    def get_node_relationships(self, node_id: uuid.UUID) -> List[Relationship]:
        """Get all relationships for a node with caching for performance."""
        # Try advanced cache first
        if (self._enable_advanced_caching and 
            hasattr(self, '_query_cache') and self._query_cache):
            cached_result = self._query_cache.get_cached_result("get_node_relationships", node_id)
            if cached_result is not None:
                return cached_result

        # Check basic cache
        if node_id in self._relationship_cache:
            relationships = self._relationship_cache[node_id]
            # Cache in advanced cache too
            if (self._enable_advanced_caching and 
                hasattr(self, '_query_cache') and self._query_cache):
                self._query_cache.cache_result("get_node_relationships", relationships, node_id=self._get_node_id_for_cache(node_id))
            return relationships

        # Compute relationships for this node
        relationships: List[Relationship] = []
        for relationship in self.relationships.values():
            if node_id in (relationship.source_id, relationship.target_id):
                relationships.append(relationship)

        # Cache result with simple size management
        if len(self._relationship_cache) >= self._relationship_cache_max_size:
            # Simple eviction: remove one random item to make space
            oldest_key = next(iter(self._relationship_cache))
            del self._relationship_cache[oldest_key]

        self._relationship_cache[node_id] = relationships
        
        # Cache in advanced cache
        if (self._enable_advanced_caching and 
            hasattr(self, '_query_cache') and self._query_cache):
            self._query_cache.cache_result("get_node_relationships", relationships, ttl=1800, node_id=self._get_node_id_for_cache(node_id))
        
        return relationships

    def enable_lazy_loading(self, node_loader: Callable[[uuid.UUID], Optional[Node]]) -> None:
        """Enable lazy loading with a custom node loader function.

        Args:
            node_loader: Function that takes a UUID and returns a Node or None
        """
        self._lazy_loading_enabled = True
        self._node_loader = node_loader

    def disable_lazy_loading(self) -> None:
        """Disable lazy loading."""
        self._lazy_loading_enabled = False
        self._node_loader = None

    def _find_node_by_id_with_lazy_loading(self, node_id: uuid.UUID) -> Optional[Node]:
        """Find a node by ID with optional lazy loading support."""
        # First check the index
        node = self._node_index.get(node_id)

        # If not found and lazy loading is enabled, try to load it
        if node is None and self._lazy_loading_enabled and self._node_loader:
            try:
                node = self._node_loader(node_id)
                if node is not None:
                    # Add the lazy-loaded node to the graph
                    self.add_node(node)
            except Exception as e:
                logger.warning("Failed to lazy load node %s: %s", node_id, e)

        # Record access for memory management
        if node and self._memory_monitor:
            self._memory_monitor.record_node_access(node_id)

        return node

    # EvictableGraph protocol implementation
    def get_all_node_ids(self) -> Set[uuid.UUID]:
        """Get all node IDs in the graph."""
        return set(self._node_index.keys())

    def remove_node_from_memory(self, node_id: uuid.UUID) -> bool:
        """Remove a node from memory (but not from persistent storage)."""
        if node_id not in self._node_index:
            return False

        try:
            # Get the node to determine its collection
            node = self._node_index[node_id]
            collection_name = self._node_registry.get_collection_name(node)
            collection = getattr(self, collection_name)
            
            # Remove from collection and index
            del collection[node_id]
            del self._node_index[node_id]
            
            # Clear related caches
            self._relationship_cache.pop(node_id, None)
            if (self._enable_advanced_caching and 
                hasattr(self, '_query_cache') and self._query_cache):
                self._query_cache.invalidate_on_event('node_removed', node_id=self._get_node_id_for_cache(node_id))  # type: ignore[arg-type]
            
            logger.debug(f"Evicted node {node_id} from memory")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove node {node_id} from memory: {e}")
            return False

    def get_node_size_estimate(self, node_id: uuid.UUID) -> int:
        """Get estimated memory size of a node in bytes."""
        node = self._node_index.get(node_id)
        if not node:
            return 0
        
        try:
            # Basic size estimation
            size = sys.getsizeof(node)
            
            # Add size of string attributes
            if hasattr(node, 'label') and node.label:
                size += sys.getsizeof(node.label)
            if hasattr(node, 'description') and node.description:
                size += sys.getsizeof(node.description)
                
            return size
        except Exception:
            return 128  # Default estimate

    # Memory management methods
    def set_memory_limit(self, limit_mb: float) -> None:
        """Set the memory limit for the graph."""
        self._memory_limit_mb = limit_mb
        if self._memory_monitor:
            self._memory_monitor.memory_limit_mb = limit_mb

    def get_memory_usage(self) -> MemoryUsageStats:
        """Get current memory usage statistics."""
        if self._memory_monitor:
            return self._memory_monitor.check_memory_usage()
        return MemoryUsageStats.capture_current()

    def force_memory_cleanup(self) -> int:
        """Force memory cleanup by evicting nodes."""
        if self._memory_monitor:
            return self._memory_monitor.evict_nodes(self, force=True)
        return 0

    def set_eviction_strategy(self, strategy: EvictionStrategy) -> None:
        """Set the node eviction strategy."""
        if self._memory_monitor:
            self._memory_monitor.current_strategy = strategy

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory management statistics."""
        stats: Dict[str, Any] = {
            "memory_limit_mb": self._memory_limit_mb,
            "total_nodes": len(self._node_index),
            "total_relationships": len(self.relationships),
            "relationship_cache_size": len(self._relationship_cache),
            "memory_management_enabled": self._enable_memory_management
        }
        
        if self._memory_monitor:
            stats.update(self._memory_monitor.get_eviction_stats())  # type: ignore[arg-type]
            
        if self._enable_advanced_caching and hasattr(self, '_query_cache') and self._query_cache:
            stats["query_cache_stats"] = self._query_cache.get_stats()  # type: ignore[assignment]
            
        return stats

    # Advanced caching methods
    def enable_advanced_caching(self, enable: bool = True) -> None:
        """Enable or disable advanced caching."""
        self._enable_advanced_caching = enable
        if not enable and hasattr(self, '_query_cache') and self._query_cache:
            self._query_cache.clear()

    def clear_all_caches(self) -> None:
        """Clear all caches."""
        self._relationship_cache.clear()
        if (self._enable_advanced_caching and 
            hasattr(self, '_query_cache') and self._query_cache):
            self._query_cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = {
            "relationship_cache_size": len(self._relationship_cache),
            "relationship_cache_max_size": self._relationship_cache_max_size,
        }
        
        if (self._enable_advanced_caching and 
            hasattr(self, '_query_cache') and self._query_cache):
            stats["query_cache"] = self._query_cache.get_stats()  # type: ignore[assignment]
            
        return stats
