"""
SFM Graph Persistence Manager

This module provides comprehensive persistence capabilities for Social Fabric Matrix (SFM) graphs,
enabling offline storage, loading, and state management of in-memory graph data.

Key Features:
- Multiple storage formats (JSON, Pickle, NetworkX formats)
- Incremental updates and change tracking
- Version management and rollback capabilities
- Data validation and integrity checking
- Compression and optimization for large graphs
- Backup and recovery mechanisms
- Thread-safe operations for concurrent access
- Automatic serialization of complex data types
"""

# Standard library imports
import gzip
import hashlib
import json
import logging
import pickle
import shutil
import threading
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Sequence, Mapping, Tuple

# Local imports
from models.sfm_enums import FlowNature, RelationshipKind, ResourceType, InstitutionLayer
from models import (
    Actor, AnalyticalContext, BeliefSystem, FeedbackLoop, Flow, Indicator,
    Institution, Node, Policy, Process, Relationship, Resource,
    SystemProperty, TechnologySystem,
)
from graph.graph import SFMGraph

# Setup logging
logger = logging.getLogger(__name__)


class StorageFormat(Enum):
    """Supported storage formats for SFM graphs."""
    JSON = "json"
    PICKLE = "pickle"
    COMPRESSED_JSON = "json.gz"
    COMPRESSED_PICKLE = "pickle.gz"


class VersioningStrategy(Enum):
    """Versioning strategies for graph storage."""
    NONE = "none"
    INCREMENTAL = "incremental"
    ROLLING = "rolling"
    SNAPSHOT = "snapshot"


@dataclass
class GraphMetadata:
    """Metadata associated with stored graphs."""
    graph_id: str
    name: str
    description: str = ""
    version: int = 1
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    author: str = ""
    tags: Optional[List[str]] = None
    size_bytes: int = 0
    node_count: int = 0
    relationship_count: int = 0
    checksum: str = ""
    format: StorageFormat = StorageFormat.JSON
    compression_ratio: Optional[float] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.tags is None:
            self.tags = []


@dataclass
class PersistenceConfig:
    """Configuration for persistence manager."""
    base_path: str = "./sfm_data"
    default_format: StorageFormat = StorageFormat.JSON
    enable_compression: bool = False
    enable_versioning: bool = True
    versioning_strategy: VersioningStrategy = VersioningStrategy.INCREMENTAL
    max_versions: int = 10
    enable_backup: bool = True
    backup_interval_hours: int = 24
    validate_on_load: bool = True
    validate_on_save: bool = True
    thread_safe: bool = True
    auto_create_directories: bool = True


class SFMSerializationError(Exception):
    """Errors related to graph serialization/deserialization."""


class SFMPersistenceError(Exception):
    """General persistence-related errors."""


class NodeSerializer:
    """Handles serialization of individual nodes."""

    @staticmethod
    def node_to_dict(node: Node) -> Dict[str, Any]:
        """Convert a Node to dictionary representation."""
        result: Dict[str, Any] = {
            'type': type(node).__name__,
            'id': str(node.id),
            'label': node.label,
            'description': node.description,
            'meta': node.meta,
            'version': getattr(node, 'version', 1),
            'created_at': getattr(node, 'created_at', datetime.now()).isoformat(),
            'modified_at': NodeSerializer._serialize_datetime(
                getattr(node, 'modified_at', None)
            ),
            'certainty': getattr(node, 'certainty', 1.0)
        }

        # Add type-specific fields using strategy pattern
        NodeSerializer._add_type_specific_fields(node, result)
        return result

    @staticmethod
    def _serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
        """Safely serialize datetime objects."""
        return dt.isoformat() if dt else None

    @staticmethod
    def _add_type_specific_fields(node: Node, result: Dict[str, Any]) -> None:
        """Add type-specific fields to node dictionary."""
        type_handlers: Dict[type, Any] = {
            Actor: NodeSerializer._handle_actor,
            Institution: NodeSerializer._handle_institution,
            Resource: NodeSerializer._handle_resource,
            Policy: NodeSerializer._handle_policy,
            Flow: NodeSerializer._handle_flow,
        }

        handler = type_handlers.get(type(node))
        if handler:
            handler(node, result)

    @staticmethod
    def _handle_actor(actor: Actor, result: Dict[str, Any]) -> None:
        """Handle Actor-specific fields."""
        result.update({
            'legal_form': actor.legal_form,
            'sector': actor.sector,
            'power_resources': getattr(actor, 'power_resources', {}),
            'decision_making_capacity': getattr(actor, 'decision_making_capacity', None)
        })

    @staticmethod
    def _handle_institution(institution: Institution, result: Dict[str, Any]) -> None:
        """Handle Institution-specific fields."""
        result.update({
            'layer': institution.layer.name if institution.layer else None,
            'formal_rules': getattr(institution, 'formal_rules', []),
            'informal_norms': getattr(institution, 'informal_norms', [])
        })

    @staticmethod
    def _handle_resource(resource: Resource, result: Dict[str, Any]) -> None:
        """Handle Resource-specific fields."""
        result.update({
            'rtype': resource.rtype.name if resource.rtype else None,
            'unit': resource.unit
        })

    @staticmethod
    def _handle_policy(policy: Policy, result: Dict[str, Any]) -> None:
        """Handle Policy-specific fields."""
        result.update({
            'authority': policy.authority,
            'enforcement': policy.enforcement,
            'target_sectors': getattr(policy, 'target_sectors', [])
        })

    @staticmethod
    def _handle_flow(flow: Flow, result: Dict[str, Any]) -> None:
        """Handle Flow-specific fields."""
        result.update({
            'nature': flow.nature.name if flow.nature else None,
            'quantity': flow.quantity,
            'unit': flow.unit,
            'flow_type': getattr(flow, 'flow_type', ''),
            'source_process_id': str(flow.source_process_id) if getattr(
                flow, 'source_process_id', None) else None,
            'target_process_id': str(flow.target_process_id) if getattr(
                flow, 'target_process_id', None) else None
        })

    @staticmethod
    def dict_to_node(data: Dict[str, Any], node_class: type) -> Node:
        """Convert dictionary representation back to Node."""
        try:
            # Create basic node with common fields
            node_kwargs: Dict[str, Any] = {
                'id': uuid.UUID(data['id']),
                'label': data['label'],
                'description': data.get('description'),
                'meta': data.get('meta', {}),
            }

            # Add type-specific fields using strategy pattern
            NodeSerializer._add_type_specific_kwargs(data, node_class, node_kwargs)
            return node_class(**node_kwargs)
        except Exception as e:
            logger.error("Failed to deserialize node: %s", str(e))
            raise SFMSerializationError(f"Failed to deserialize node: {str(e)}") from e

    @staticmethod
    def _add_type_specific_kwargs(data: Dict[str, Any], node_class: type,
                                  node_kwargs: Dict[str, Any]) -> None:
        """Add type-specific constructor arguments."""
        type_handlers: Dict[type, Any] = {
            Actor: NodeSerializer._add_actor_kwargs,
            Institution: NodeSerializer._add_institution_kwargs,
            Resource: NodeSerializer._add_resource_kwargs,
            Policy: NodeSerializer._add_policy_kwargs,
            Flow: NodeSerializer._add_flow_kwargs,
        }

        handler = type_handlers.get(node_class)
        if handler:
            handler(data, node_kwargs)

    @staticmethod
    def _add_actor_kwargs(data: Dict[str, Any], node_kwargs: Dict[str, Any]) -> None:
        """Add Actor-specific constructor arguments."""
        node_kwargs.update({
            'legal_form': data.get('legal_form'),
            'sector': data.get('sector')
        })

    @staticmethod
    def _add_institution_kwargs(data: Dict[str, Any], node_kwargs: Dict[str, Any]) -> None:
        """Add Institution-specific constructor arguments."""
        layer_name = data.get('layer')
        node_kwargs['layer'] = InstitutionLayer[layer_name] if layer_name else None

    @staticmethod
    def _add_resource_kwargs(data: Dict[str, Any], node_kwargs: Dict[str, Any]) -> None:
        """Add Resource-specific constructor arguments."""
        rtype_name = data.get('rtype')
        node_kwargs.update({
            'rtype': ResourceType[rtype_name] if rtype_name else ResourceType.NATURAL,
            'unit': data.get('unit')
        })

    @staticmethod
    def _add_policy_kwargs(data: Dict[str, Any], node_kwargs: Dict[str, Any]) -> None:
        """Add Policy-specific constructor arguments."""
        node_kwargs.update({
            'authority': data.get('authority'),
            'enforcement': data.get('enforcement', 0.0),
        })

    @staticmethod
    def _add_flow_kwargs(data: Dict[str, Any], node_kwargs: Dict[str, Any]) -> None:
        """Add Flow-specific constructor arguments."""
        nature_name = data.get('nature')
        node_kwargs.update({
            'nature': FlowNature[nature_name] if nature_name else FlowNature.TRANSFER,
            'quantity': data.get('quantity'),
            'unit': data.get('unit')
        })


class SFMGraphSerializer:
    """Handles serialization and deserialization of SFM graphs."""

    @staticmethod
    def serialize_graph(graph: SFMGraph,
                        format_type: StorageFormat = StorageFormat.JSON) -> bytes:
        """Serialize an SFM graph to bytes."""
        try:
            if format_type in [StorageFormat.JSON, StorageFormat.COMPRESSED_JSON]:
                return SFMGraphSerializer._serialize_json(graph, format_type)
            if format_type in [StorageFormat.PICKLE, StorageFormat.COMPRESSED_PICKLE]:
                return SFMGraphSerializer._serialize_pickle(graph, format_type)

            raise SFMSerializationError(f"Unsupported format: {format_type}")

        except Exception as e:
            raise SFMSerializationError(f"Failed to serialize graph: {str(e)}") from e

    @staticmethod
    def _serialize_json(graph: SFMGraph, format_type: StorageFormat) -> bytes:
        """Serialize graph to JSON format."""
        data = SFMGraphSerializer._graph_to_dict(graph)
        json_str = json.dumps(data, indent=2,
                              default=SFMGraphSerializer.json_serializer)
        json_bytes = json_str.encode('utf-8')

        if format_type == StorageFormat.COMPRESSED_JSON:
            return gzip.compress(json_bytes)
        return json_bytes

    @staticmethod
    def _serialize_pickle(graph: SFMGraph, format_type: StorageFormat) -> bytes:
        """Serialize graph to Pickle format."""
        if format_type == StorageFormat.COMPRESSED_PICKLE:
            return gzip.compress(pickle.dumps(graph, protocol=pickle.HIGHEST_PROTOCOL))
        return pickle.dumps(graph, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def deserialize_graph(data: bytes, format_type: StorageFormat = StorageFormat.JSON) -> SFMGraph:
        """Deserialize bytes to an SFM graph."""
        try:
            logger.debug("Deserializing graph with format '%s'. Data size: %d bytes",
                        format_type, len(data))

            if format_type in [StorageFormat.COMPRESSED_JSON, StorageFormat.COMPRESSED_PICKLE]:
                data = gzip.decompress(data)

            if format_type in [StorageFormat.JSON, StorageFormat.COMPRESSED_JSON]:
                dict_data = json.loads(data.decode('utf-8'))
                logger.debug("Deserialized JSON data: %s", dict_data)
                required_keys = ['id', 'name', 'description', 'relationships']
                missing_keys = [key for key in required_keys if key not in dict_data]
                if missing_keys:
                    logger.error("Missing required keys in graph data: %s", missing_keys)
                    raise ValueError(f"Missing required keys: {missing_keys}")
                return SFMGraphSerializer._dict_to_graph(dict_data)

            if format_type in [StorageFormat.PICKLE, StorageFormat.COMPRESSED_PICKLE]:
                deserialized_data = pickle.loads(data)
                logger.debug("Deserialized PICKLE data: %s", deserialized_data)
                return deserialized_data

            raise SFMSerializationError(f"Unsupported format: {format_type}")

        except Exception as e:
            logger.error("Failed to deserialize graph. Format: '%s', Error: %s",
                        format_type, str(e))
            raise SFMSerializationError(f"Failed to deserialize graph: {str(e)}") from e

    @staticmethod
    def _dict_to_graph(data: Dict[str, Any]) -> SFMGraph:
        """Convert dictionary representation back to SFMGraph."""
        try:
            logger.debug("Deserializing graph from dictionary: %s", data)

            # Validate dictionary keys
            required_keys = ['id', 'name', 'description']
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Missing required key '{key}' in graph data: {data}")

            logger.debug("Dictionary keys: %s", list(data.keys()))
            logger.debug("Dictionary content: %s", data)

            logger.debug("Graph ID: %s, Name: %s, Description: %s",
                        data['id'], data['name'], data.get('description', ''))

            graph = SFMGraph(
                id=uuid.UUID(data['id']),
                name=data['name'],
                description=data.get('description', '')
            )

            logger.debug("Graph initialized: %s", graph)

            # Deserialize node collections
            node_type_mapping: List[Tuple[str, type, Mapping[Any, Node]]] = [
                ('actors', Actor, graph.actors),
                ('institutions', Institution, graph.institutions),
                ('resources', Resource, graph.resources),
                ('processes', Process, graph.processes),
                ('flows', Flow, graph.flows),
                ('policies', Policy, graph.policies),
                ('belief_systems', BeliefSystem, graph.belief_systems),
                ('technology_systems', TechnologySystem, graph.technology_systems),
                ('indicators', Indicator, graph.indicators),
                ('feedback_loops', FeedbackLoop, graph.feedback_loops),
                ('system_properties', SystemProperty, graph.system_properties),
                ('analytical_contexts', AnalyticalContext, graph.analytical_contexts),
            ]

            logger.debug("Node collections during deserialization: %s", node_type_mapping)

            for collection_name, node_class, target_collection in node_type_mapping:
                collection_data = data.get(collection_name, {})
                if not isinstance(collection_data, dict):
                    raise ValueError(f"Invalid data for collection '{collection_name}': "
                                   f"{collection_data}")
                if not collection_data:
                    logger.warning(f"Collection '{collection_name}' is empty.")
                for node_data in collection_data.values():
                    if not isinstance(node_data, dict):
                        raise ValueError(f"Invalid node data in collection '{collection_name}': "
                                       f"{node_data}")
                    node: Node = NodeSerializer.dict_to_node(node_data, node_class)
                    target_collection[node.id] = node  # type: ignore

            logger.debug("Node collections deserialized successfully.")

            # Deserialize relationships
            relationships_data = data.get('relationships', {})
            if not isinstance(relationships_data, dict):
                raise ValueError(f"Invalid data for relationships: {relationships_data}")

            logger.debug("Relationships during deserialization: %s", relationships_data)

            for rel_data in relationships_data.values():
                relationship = SFMGraphSerializer._dict_to_relationship(rel_data)
                graph.relationships[relationship.id] = relationship

            logger.debug("Relationships deserialized successfully.")

            return graph

        except Exception as e:
            logger.error("Failed to deserialize graph: %s", str(e))
            raise SFMSerializationError(f"Failed to deserialize graph: {str(e)}") from e

    @staticmethod
    def _dict_to_relationship(data: Dict[str, Any]) -> Relationship:
        """Convert dictionary representation back to Relationship."""
        try:
            logger.debug("Deserializing relationship data: %s", data)
            return Relationship(
                id=uuid.UUID(data['id']),
                source_id=uuid.UUID(data['source_id']),
                target_id=uuid.UUID(data['target_id']),
                kind=RelationshipKind[data['kind']],
                weight=data.get('weight', 1.0),
                meta=data.get('meta', {}),
                certainty=data.get('certainty', 1.0),
                modified_at=data.get('modified_at', None)  # Handle missing modified_at
            )
        except Exception as e:
            logger.error("Failed to deserialize relationship: %s", str(e))
            raise SFMSerializationError(f"Failed to deserialize relationship: {str(e)}") from e

    @staticmethod
    def json_serializer(obj: Any) -> str:
        """Custom JSON serializer for complex types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    @staticmethod
    def _graph_to_dict(graph: SFMGraph) -> Dict[str, Any]:
        """Convert SFMGraph to dictionary representation."""
        node_collections: List[Tuple[str, Mapping[Any, Node]]] = [
            ('actors', graph.actors),
            ('institutions', graph.institutions),
            ('resources', graph.resources),
            ('processes', graph.processes),
            ('flows', graph.flows),
            ('policies', graph.policies),
            ('belief_systems', graph.belief_systems),
            ('technology_systems', graph.technology_systems),
            ('indicators', graph.indicators),
            ('feedback_loops', graph.feedback_loops),
            ('system_properties', graph.system_properties),
            ('analytical_contexts', graph.analytical_contexts),
        ]

        result: Dict[str, Any] = {
            'id': str(graph.id),
            'name': graph.name,
            'description': graph.description,
            'relationships': {
                str(k): SFMGraphSerializer._relationship_to_dict(v)
                for k, v in graph.relationships.items()
            },
            'metadata': {
                'serialization_timestamp': datetime.now().isoformat(),
                'serialization_version': '1.0'
            }
        }

        # Add node collections
        for collection_name, collection in node_collections:
            result[collection_name] = {
                str(k): NodeSerializer.node_to_dict(v)
                for k, v in collection.items()
            }

        logger.debug("Serialized graph dictionary: %s", result)
        return result

    @staticmethod
    def _relationship_to_dict(rel: Relationship) -> Dict[str, Any]:
        """Convert Relationship to dictionary representation."""
        return {
            'id': str(rel.id),
            'source_id': str(rel.source_id),
            'target_id': str(rel.target_id),
            'kind': rel.kind.name,
            'weight': rel.weight,
            'meta': getattr(rel, 'meta', {}),
            'certainty': getattr(rel, 'certainty', 1.0),
            'created_at': getattr(rel, 'created_at', datetime.now()).isoformat(),
            'modified_at': rel.modified_at.isoformat() if rel.modified_at else None,
        }


class FileManager:
    """Handles file operations for persistence."""

    def __init__(self, config: PersistenceConfig):
        self.config = config
        self.base_path = Path(config.base_path)
        self.graphs_path = self.base_path / "graphs"
        self.metadata_path = self.base_path / "metadata"
        self.backups_path = self.base_path / "backups"
        self.versions_path = self.base_path / "versions"

    def initialize_directories(self):
        """Create necessary directory structure."""
        for path in [self.base_path, self.graphs_path, self.metadata_path,
                     self.backups_path, self.versions_path]:
            path.mkdir(parents=True, exist_ok=True)

    def get_graph_file_path(self, graph_id: str, format_type: StorageFormat) -> Path:
        """Get file path for graph data."""
        extension_mapping = {
            StorageFormat.JSON: ".json",
            StorageFormat.PICKLE: ".pkl",
            StorageFormat.COMPRESSED_JSON: ".json.gz",
            StorageFormat.COMPRESSED_PICKLE: ".pkl.gz"
        }
        extension = extension_mapping[format_type]
        return self.graphs_path / f"{graph_id}{extension}"

    def get_version_file_path(self, graph_id: str, version: int,
                              format_type: StorageFormat) -> Path:
        """Get file path for versioned graph data."""
        extension_mapping = {
            StorageFormat.JSON: ".json",
            StorageFormat.PICKLE: ".pkl",
            StorageFormat.COMPRESSED_JSON: ".json.gz",
            StorageFormat.COMPRESSED_PICKLE: ".pkl.gz"
        }
        extension = extension_mapping[format_type]
        return self.versions_path / graph_id / f"v{version}_data{extension}"

    def get_metadata_file_path(self, graph_id: str) -> Path:
        """Get file path for metadata."""
        return self.metadata_path / f"{graph_id}.json"


class SFMPersistenceManager:
    """
    Comprehensive persistence manager for SFM graphs.

    Provides offline storage, loading, versioning, and state management
    capabilities for in-memory SFM graph data.
    """

    def __init__(self, config: Union[PersistenceConfig, str, None] = None):
        """
        Initialize the persistence manager.

        Args:
            config: Configuration object, path string, or None for defaults
        """
        self.config = self._initialize_config(config)
        self.file_manager = FileManager(self.config)
        self._lock = threading.RLock() if self.config.thread_safe else None
        self._metadata_cache: Dict[str, GraphMetadata] = {}
        self._cache_dirty = True

        if self.config.auto_create_directories:
            self.file_manager.initialize_directories()

        logger.info("SFM Persistence Manager initialized at: %s",
                    self.file_manager.base_path)

    def _initialize_config(self, config: Union[PersistenceConfig, str, None]
                           ) -> PersistenceConfig:
        """Initialize configuration from various input types."""
        if isinstance(config, str):
            return PersistenceConfig(base_path=config)
        if config is None:
            return PersistenceConfig()

        return config

    @contextmanager
    def _thread_safe(self):
        """Context manager for thread-safe operations."""
        if self._lock:
            with self._lock:
                yield
        else:
            yield

    def save_graph(self,
                   graph_id: str,
                   graph: SFMGraph,
                   metadata: Optional[Dict[str, Any]] = None,
                   format_type: Optional[StorageFormat] = None) -> GraphMetadata:
        """
        Save an SFM graph to persistent storage.

        Args:
            graph_id: Unique identifier for the graph
            graph: SFMGraph instance to save
            metadata: Optional metadata dictionary
            format_type: Storage format (defaults to config default)

        Returns:
            GraphMetadata for the saved graph
        """
        with self._thread_safe():
            try:
                format_type = format_type or self.config.default_format

                if self.config.validate_on_save:
                    self._validate_graph(graph)

                current_metadata = self._get_metadata(graph_id)
                version = (current_metadata.version + 1) if current_metadata else 1

                if self.config.enable_versioning and current_metadata:
                    self._archive_version(graph_id, current_metadata)

                serialized_data = SFMGraphSerializer.serialize_graph(graph, format_type)
                checksum = hashlib.sha256(serialized_data).hexdigest()

                new_metadata = self._create_metadata(
                    graph_id, graph, version, current_metadata,
                    metadata, serialized_data, checksum, format_type
                )

                self._save_graph_data(graph_id, serialized_data, format_type)
                self._save_metadata(graph_id, new_metadata)
                self._metadata_cache[graph_id] = new_metadata

                logger.info("Graph '%s' saved successfully (version %d)",
                            graph_id, version)
                return new_metadata

            except Exception as e:
                logger.error("Failed to save graph '%s': %s", graph_id, str(e))
                raise SFMPersistenceError(f"Failed to save graph: {str(e)}") from e

    def _create_metadata(self, graph_id: str, graph: SFMGraph, version: int,
                         current_metadata: Optional[GraphMetadata],
                         metadata: Optional[Dict[str, Any]], serialized_data: bytes,
                         checksum: str, format_type: StorageFormat) -> GraphMetadata:
        """Create metadata object for saved graph."""
        return GraphMetadata(
            graph_id=graph_id,
            name=graph.name or graph_id,
            description=graph.description or "",
            version=version,
            created_at=current_metadata.created_at if current_metadata else datetime.now(),
            modified_at=datetime.now(),
            author=metadata.get('author', '') if metadata else '',
            tags=metadata.get('tags', []) if metadata else [],
            size_bytes=len(serialized_data),
            node_count=self._count_nodes(graph),
            relationship_count=len(graph.relationships),
            checksum=checksum,
            format=format_type
        )

    def _save_graph_data(self, graph_id: str, serialized_data: bytes,
                         format_type: StorageFormat) -> None:
        """Save serialized graph data to file."""
        graph_file = self.file_manager.get_graph_file_path(graph_id, format_type)
        graph_file.write_bytes(serialized_data)

    def load_graph(self,
                   graph_id: str,
                   version: Optional[int] = None) -> Optional[SFMGraph]:
        """
        Load an SFM graph from persistent storage.

        Args:
            graph_id: Unique identifier for the graph
            version: Specific version to load (latest if None)

        Returns:
            SFMGraph instance or None if not found
        """
        with self._thread_safe():
            try:
                latest_metadata = self._get_metadata(graph_id)
                if not latest_metadata:
                    logger.warning("Graph '%s' not found", graph_id)
                    return None

                metadata_to_load: Optional[GraphMetadata]
                graph_file: Path

                if version is None or version == latest_metadata.version:
                    # Loading the latest version
                    metadata_to_load = latest_metadata
                    graph_file = self.file_manager.get_graph_file_path(
                        graph_id, metadata_to_load.format)
                else:
                    # Loading a specific archived version
                    metadata_to_load = self._get_metadata(graph_id, version)
                    if not metadata_to_load:
                        logger.warning("Graph '%s' version %s not found", graph_id, version)
                        return None
                    graph_file = self.file_manager.get_version_file_path(
                        graph_id, version, metadata_to_load.format)

                if not graph_file.exists():
                    logger.error("Graph file not found: %s", graph_file)
                    return None

                serialized_data = graph_file.read_bytes()
                self._verify_checksum(serialized_data, metadata_to_load, graph_id)

                graph = SFMGraphSerializer.deserialize_graph(serialized_data,
                                                             metadata_to_load.format)

                if self.config.validate_on_load:
                    self._validate_graph(graph)

                logger.info("Graph '%s' loaded successfully (version %d)",
                            graph_id, metadata_to_load.version)
                return graph

            except Exception as e:
                logger.error("Failed to load graph '%s': %s", graph_id, str(e))
                raise SFMPersistenceError(f"Failed to load graph: {str(e)}") from e

    def _verify_checksum(self, serialized_data: bytes, metadata: GraphMetadata,
                         graph_id: str) -> None:
        """Verify data integrity using checksum."""
        if metadata.checksum:
            actual_checksum = hashlib.sha256(serialized_data).hexdigest()
            if actual_checksum != metadata.checksum:
                logger.warning("Checksum mismatch for graph '%s'. Data may be corrupted.",
                               graph_id)

    def delete_graph(self, graph_id: str, include_versions: bool = True) -> bool:
        """
        Delete a graph and optionally its versions.

        Args:
            graph_id: Unique identifier for the graph
            include_versions: Whether to delete all versions

        Returns:
            True if successful, False otherwise
        """
        with self._thread_safe():
            try:
                metadata = self._get_metadata(graph_id)
                if not metadata:
                    return False

                # Delete main graph file
                graph_file = self.file_manager.get_graph_file_path(graph_id,
                                                                   metadata.format)
                if graph_file.exists():
                    graph_file.unlink()

                # Delete metadata
                metadata_file = self.file_manager.get_metadata_file_path(graph_id)
                if metadata_file.exists():
                    metadata_file.unlink()

                # Delete versions if requested
                if include_versions:
                    version_dir = self.file_manager.versions_path / graph_id
                    if version_dir.exists():
                        shutil.rmtree(version_dir)

                # Remove from cache
                self._metadata_cache.pop(graph_id, None)

                logger.info("Graph '%s' deleted successfully", graph_id)
                return True

            except Exception as e:
                logger.error("Failed to delete graph '%s': %s", graph_id, str(e))
                return False

    def list_graphs(self, include_metadata: bool = True) -> Sequence[Union[str, GraphMetadata]]:
        """
        List all stored graphs.

        Args:
            include_metadata: Whether to return metadata objects or just IDs

        Returns:
            List of graph IDs or GraphMetadata objects
        """
        with self._thread_safe():
            try:
                if not self.file_manager.metadata_path.exists():
                    return []

                graph_ids = [
                    metadata_file.stem
                    for metadata_file in self.file_manager.metadata_path.glob("*.json")
                ]

                if not include_metadata:
                    return graph_ids

                # Load metadata for each graph
                result = []
                for graph_id in graph_ids:
                    metadata = self._get_metadata(graph_id)
                    if metadata:
                        result.append(metadata)

                return result

            except Exception as e:
                logger.error("Failed to list graphs: %s", str(e))
                return []

    def get_graph_metadata(self, graph_id: str) -> Optional[GraphMetadata]:
        """Get metadata for a specific graph."""
        return self._get_metadata(graph_id)

    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        with self._thread_safe():
            try:
                stats = self._initialize_stats()
                graphs = self.list_graphs(include_metadata=True)
                stats['total_graphs'] = len(graphs)

                self._calculate_graph_stats(
                    [g for g in graphs if isinstance(g, GraphMetadata)], stats
                )
                self._count_backups(stats)

                return stats

            except Exception as e:
                logger.error("Failed to get storage statistics: %s", str(e))
                return {}

    def _initialize_stats(self) -> Dict[str, Any]:
        """Initialize statistics dictionary."""
        return {
            'total_graphs': 0,
            'total_size_bytes': 0,
            'total_versions': 0,
            'total_backups': 0,
            'format_distribution': {},
            'largest_graph': None,
            'oldest_graph': None,
            'newest_graph': None
        }

    def _calculate_graph_stats(self, graphs: List[GraphMetadata],
                               stats: Dict[str, Any]) -> None:
        """Calculate statistics for graphs."""
        largest_size = 0
        oldest_date = None
        newest_date = None

        for metadata in graphs:
            stats['total_size_bytes'] += metadata.size_bytes

            # Format distribution
            format_name = metadata.format.value
            stats['format_distribution'][format_name] = (
                stats['format_distribution'].get(format_name, 0) + 1
            )

            # Largest graph
            if metadata.size_bytes > largest_size:
                largest_size = metadata.size_bytes
                stats['largest_graph'] = metadata.graph_id

                # Date tracking
                if (metadata.created_at is not None and
                        (oldest_date is None or
                         (metadata.created_at < oldest_date))):
                    oldest_date = metadata.created_at
                    stats['oldest_graph'] = metadata.graph_id

                if (metadata.created_at is not None and
                        (newest_date is None or
                         (metadata.created_at > newest_date))):
                    newest_date = metadata.created_at
                    stats['newest_graph'] = metadata.graph_id

                # Count versions
                version_history = self.get_version_history(metadata.graph_id)
                stats['total_versions'] += len(version_history)

    def _count_backups(self, stats: Dict[str, Any]) -> None:
        """Count backup files with size calculation, validation, and age tracking."""
        if not self.file_manager.backups_path.exists():
            stats['total_backups'] = 0
            stats['total_backup_size_bytes'] = 0
            stats['backup_age_stats'] = {'oldest': None, 'newest': None, 'average_age_days': 0}
            stats['valid_backups'] = 0
            return
            
        backup_files = list(self.file_manager.backups_path.glob("*.backup"))
        stats['total_backups'] = len(backup_files)
        
        total_size = 0
        valid_count = 0
        oldest_date = None
        newest_date = None
        
        current_time = datetime.now()
        total_age_days = 0
        
        for backup_file in backup_files:
            try:
                # Calculate size
                file_size = backup_file.stat().st_size
                total_size += file_size
                
                # Basic validation - check if file is readable and not empty
                if file_size > 0:
                    try:
                        # Try to read first few bytes to validate file integrity
                        with backup_file.open('rb') as f:
                            f.read(10)  # Read first 10 bytes to verify readability
                        valid_count += 1
                    except (IOError, OSError):
                        logger.warning("Backup file %s appears corrupted", backup_file)
                        continue
                
                # Age tracking using file modification time
                file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                if oldest_date is None or file_mtime < oldest_date:
                    oldest_date = file_mtime
                if newest_date is None or file_mtime > newest_date:
                    newest_date = file_mtime
                    
                age_days = (current_time - file_mtime).days
                total_age_days += age_days
                
            except (OSError, IOError) as e:
                logger.warning("Failed to process backup file %s: %s", backup_file, e)
                continue
        
        stats['total_backup_size_bytes'] = total_size
        stats['valid_backups'] = valid_count
        
        # Calculate age statistics
        if backup_files:
            stats['backup_age_stats'] = {
                'oldest': oldest_date.isoformat() if oldest_date else None,
                'newest': newest_date.isoformat() if newest_date else None,
                'average_age_days': total_age_days / len(backup_files) if backup_files else 0
            }
        else:
            stats['backup_age_stats'] = {'oldest': None, 'newest': None, 'average_age_days': 0}

    # Additional methods would be implemented here following the same pattern
    # ... (continuing with remaining methods like get_version_history,
    # create_backup, etc.)

    def _get_metadata(self, graph_id: str,
                      version: Optional[int] = None) -> Optional[GraphMetadata]:
        """Load metadata for a graph with enhanced validation and error handling."""
        try:
            # Input validation
            if not graph_id or not isinstance(graph_id, str):
                logger.error("Invalid graph_id provided: %s", graph_id)
                return None
            
            if version is not None and (not isinstance(version, int) or version < 1):
                logger.error("Invalid version provided: %s", version)
                return None

            # Check cache first
            if version is None and graph_id in self._metadata_cache:
                cached_metadata = self._metadata_cache[graph_id]
                # Validate cached metadata is still consistent
                if self._validate_metadata_consistency(cached_metadata):
                    return cached_metadata
                else:
                    # Remove invalid cached metadata
                    del self._metadata_cache[graph_id]
                    logger.warning("Removed inconsistent cached metadata for '%s'", graph_id)

            metadata_data = self._load_metadata_data(graph_id, version)
            if not metadata_data:
                logger.debug("No metadata found for graph '%s', version %s", graph_id, version)
                return None

            # Validate metadata structure
            if not self._validate_metadata_structure(metadata_data):
                logger.error("Invalid metadata structure for graph '%s'", graph_id)
                return None

            metadata = self._parse_metadata(metadata_data)
            
            # Validate parsed metadata
            if not self._validate_parsed_metadata(metadata, graph_id, version):
                logger.error("Parsed metadata validation failed for graph '%s'", graph_id)
                return None

            # Cache current version
            if version is None:
                self._metadata_cache[graph_id] = metadata

            return metadata

        except json.JSONDecodeError as e:
            logger.error("JSON decode error loading metadata for '%s': %s", graph_id, str(e))
            return None
        except Exception as e:
            logger.error("Failed to load metadata for '%s': %s", graph_id, str(e))
            return None

    def _validate_metadata_consistency(self, metadata: GraphMetadata) -> bool:
        """Validate that cached metadata is still consistent with stored files."""
        try:
            # Check if the corresponding graph file exists
            graph_file = self.file_manager.get_graph_file_path(metadata.graph_id, metadata.format)
            if not graph_file.exists():
                return False
            
            # Check if file size matches metadata
            actual_size = graph_file.stat().st_size
            if abs(actual_size - metadata.size_bytes) > 100:  # Allow small variance for compression
                logger.warning("Size mismatch for graph '%s': expected %d, actual %d", 
                             metadata.graph_id, metadata.size_bytes, actual_size)
                return False
                
            # Check if file modification time is consistent
            file_mtime = datetime.fromtimestamp(graph_file.stat().st_mtime)
            if metadata.modified_at and abs((file_mtime - metadata.modified_at).total_seconds()) > 60:
                logger.warning("Modification time mismatch for graph '%s'", metadata.graph_id)
                return False
                
            return True
        except (OSError, IOError) as e:
            logger.warning("Error validating metadata consistency for '%s': %s", metadata.graph_id, e)
            return False

    def _validate_metadata_structure(self, metadata_data: Dict[str, Any]) -> bool:
        """Validate that metadata has required fields and structure."""
        required_fields = ['graph_id', 'name', 'version', 'created_at', 'format']
        
        for field in required_fields:
            if field not in metadata_data:
                logger.error("Missing required metadata field: %s", field)
                return False
        
        # Validate data types
        if not isinstance(metadata_data['graph_id'], str) or not metadata_data['graph_id']:
            logger.error("Invalid graph_id in metadata")
            return False
            
        if not isinstance(metadata_data['version'], int) or metadata_data['version'] < 1:
            logger.error("Invalid version in metadata: %s", metadata_data['version'])
            return False
            
        if not isinstance(metadata_data['size_bytes'], int) or metadata_data['size_bytes'] < 0:
            logger.error("Invalid size_bytes in metadata: %s", metadata_data['size_bytes'])
            return False
            
        return True

    def _validate_parsed_metadata(self, metadata: GraphMetadata, graph_id: str, 
                                 version: Optional[int]) -> bool:
        """Validate parsed metadata object."""
        # Check that graph_id matches
        if metadata.graph_id != graph_id:
            logger.error("Graph ID mismatch: expected '%s', got '%s'", graph_id, metadata.graph_id)
            return False
            
        # Check version if specified
        if version is not None and metadata.version != version:
            logger.error("Version mismatch: expected %d, got %d", version, metadata.version)
            return False
            
        # Validate checksum if present
        if metadata.checksum:
            try:
                graph_file = self.file_manager.get_graph_file_path(metadata.graph_id, metadata.format)
                if graph_file.exists():
                    actual_checksum = hashlib.sha256(graph_file.read_bytes()).hexdigest()
                    if actual_checksum != metadata.checksum:
                        logger.warning("Checksum mismatch for graph '%s': expected %s, got %s", 
                                     metadata.graph_id, metadata.checksum, actual_checksum)
                        # Don't fail validation for checksum mismatch, just warn
            except (OSError, IOError) as e:
                logger.warning("Could not validate checksum for '%s': %s", metadata.graph_id, e)
                
        return True

    def _load_metadata_data(self, graph_id: str,
                            version: Optional[int]) -> Optional[Dict[str, Any]]:
        """Load raw metadata data from file."""
        if version:
            # Load version-specific metadata
            version_file = (self.file_manager.versions_path / graph_id /
                            f"v{version}.json")
            if not version_file.exists():
                return None
            return json.loads(version_file.read_text())

        # Load current metadata
        metadata_file = self.file_manager.get_metadata_file_path(graph_id)
        if not metadata_file.exists():
            return None
        return json.loads(metadata_file.read_text())

    def _parse_metadata(self, metadata_data: Dict[str, Any]) -> GraphMetadata:
        """Parse metadata dictionary into GraphMetadata object."""
        # Convert datetime strings back to datetime objects
        metadata_data['created_at'] = datetime.fromisoformat(metadata_data['created_at'])
        if metadata_data.get('modified_at'):
            metadata_data['modified_at'] = datetime.fromisoformat(
                metadata_data['modified_at']
            )
        metadata_data['format'] = StorageFormat(metadata_data['format'])

        return GraphMetadata(**metadata_data)

    def _save_metadata(self, graph_id: str, metadata: GraphMetadata) -> None:
        """Save metadata for a graph."""
        try:
            metadata_file = self.file_manager.get_metadata_file_path(graph_id)
            metadata_dict = asdict(metadata)
            metadata_dict['format'] = metadata.format.value

            metadata_file.write_text(
                json.dumps(metadata_dict, indent=2,
                           default=SFMGraphSerializer.json_serializer)
            )

        except Exception as e:
            logger.error("Failed to save metadata for '%s': %s", graph_id, str(e))
            raise

    def _archive_version(self, graph_id: str, metadata: GraphMetadata) -> None:
        """Archive current version before updating."""
        try:
            version_dir = self.file_manager.versions_path / graph_id
            version_dir.mkdir(exist_ok=True)

            # Save version metadata
            version_metadata_file = version_dir / f"v{metadata.version}.json"
            metadata_dict = asdict(metadata)
            metadata_dict['format'] = metadata.format.value
            version_metadata_file.write_text(
                json.dumps(metadata_dict, indent=2,
                           default=SFMGraphSerializer.json_serializer)
            )

            # Copy current graph data to versioned file
            current_graph_file = self.file_manager.get_graph_file_path(
                graph_id, metadata.format
            )
            if current_graph_file.exists():
                version_data_file = self.file_manager.get_version_file_path(
                    graph_id, metadata.version, metadata.format)
                # Ensure directory exists
                version_data_file.parent.mkdir(exist_ok=True, parents=True)
                shutil.copy2(current_graph_file, version_data_file)

        except Exception as e:
            logger.error("Failed to archive version for '%s': %s", graph_id, str(e))
            raise

    def _validate_graph(self, graph: SFMGraph) -> None:
        """Validate graph integrity with enhanced corruption detection."""
        if not graph.id:
            raise SFMSerializationError("Graph must have an ID")

        # Validate graph ID format (UUID or string)
        if not (isinstance(graph.id, (str, uuid.UUID)) and str(graph.id).strip()):
            raise SFMSerializationError("Graph ID must be a non-empty string or valid UUID")

        # Validate node collections exist and are dictionaries
        node_collections = [
            ('actors', graph.actors), ('institutions', graph.institutions), 
            ('resources', graph.resources), ('processes', graph.processes), 
            ('flows', graph.flows), ('policies', graph.policies),
            ('belief_systems', graph.belief_systems), ('technology_systems', graph.technology_systems),
            ('indicators', graph.indicators), ('feedback_loops', graph.feedback_loops),
            ('system_properties', graph.system_properties), ('analytical_contexts', graph.analytical_contexts)
        ]

        all_node_ids = set()
        
        # Validate each node collection
        for collection_name, collection in node_collections:
            if not isinstance(collection, dict):
                raise SFMSerializationError(f"Graph {collection_name} must be a dictionary")
            
            for node_id, node in collection.items():
                # Handle both string and UUID node IDs
                if not (isinstance(node_id, (str, uuid.UUID)) and str(node_id).strip()):
                    raise SFMSerializationError(f"Invalid node ID in {collection_name}: {node_id}")
                
                if not hasattr(node, 'id') or str(node.id) != str(node_id):
                    raise SFMSerializationError(
                        f"Node ID mismatch in {collection_name}: key '{node_id}' != node.id '{getattr(node, 'id', 'missing')}'"
                    )
                
                # Check for duplicate node IDs across collections
                node_id_str = str(node_id)
                if node_id_str in all_node_ids:
                    raise SFMSerializationError(f"Duplicate node ID found: {node_id}")
                    
                all_node_ids.add(node_id_str)

        # Validate relationships
        if not isinstance(graph.relationships, dict):
            raise SFMSerializationError("Graph relationships must be a dictionary")
            
        for rel_id, rel in graph.relationships.items():
            # Handle both string and UUID relationship IDs
            if not (isinstance(rel_id, (str, uuid.UUID)) and str(rel_id).strip()):
                raise SFMSerializationError(f"Invalid relationship ID: {rel_id}")
                
            if not hasattr(rel, 'id') or str(rel.id) != str(rel_id):
                raise SFMSerializationError(
                    f"Relationship ID mismatch: key '{rel_id}' != rel.id '{getattr(rel, 'id', 'missing')}'"
                )
            
            # Validate relationship references
            source_id_str = str(getattr(rel, 'source_id', ''))
            target_id_str = str(getattr(rel, 'target_id', ''))
            
            if not hasattr(rel, 'source_id') or source_id_str not in all_node_ids:
                raise SFMSerializationError(
                    f"Relationship {rel_id} references non-existent source node: {getattr(rel, 'source_id', 'missing')}"
                )
            if not hasattr(rel, 'target_id') or target_id_str not in all_node_ids:
                raise SFMSerializationError(
                    f"Relationship {rel_id} references non-existent target node: {getattr(rel, 'target_id', 'missing')}"
                )
                
            # Validate relationship has required attributes
            if not hasattr(rel, 'kind'):
                raise SFMSerializationError(f"Relationship {rel_id} missing 'kind' attribute")

        # Additional integrity checks
        self._check_graph_structure_integrity(graph, all_node_ids)

    def _check_graph_structure_integrity(self, graph: SFMGraph, all_node_ids: set) -> None:
        """Perform additional graph structure integrity checks."""
        # Check for orphaned relationships (relationships with no corresponding nodes)
        total_nodes = len(all_node_ids)
        total_relationships = len(graph.relationships)
        
        # Warn if the ratio seems unusual (could indicate corruption)
        if total_nodes > 0 and total_relationships > total_nodes * 10:
            logger.warning("Graph '%s' has unusually high relationship-to-node ratio: %d relationships for %d nodes", 
                         graph.id, total_relationships, total_nodes)
        
        # Check for cycles in hierarchical relationships if applicable
        if hasattr(graph, 'name') and not isinstance(graph.name, str):
            raise SFMSerializationError("Graph name must be a string")
            
        # Validate metadata fields if present
        if hasattr(graph, 'description') and graph.description is not None and not isinstance(graph.description, str):
            raise SFMSerializationError("Graph description must be a string or None")

    def _count_nodes(self, graph: SFMGraph) -> int:
        """Count total nodes in graph."""
        return (len(graph.actors) + len(graph.institutions) + len(graph.resources) +
                len(graph.processes) + len(graph.flows) + len(graph.policies) +
                len(graph.belief_systems) + len(graph.technology_systems) +
                len(graph.indicators) + len(graph.feedback_loops) +
                len(graph.system_properties) + len(graph.analytical_contexts))

    # Implement remaining methods following the same pattern...
    def get_version_history(self, graph_id: str) -> List[Dict[str, Any]]:
        """Get version history for a graph."""
        version_dir = self.file_manager.versions_path / graph_id
        if not version_dir.exists() or not version_dir.is_dir():
            return []
        history: List[Dict[str, Any]] = []
        # Iterate over version metadata files v{version}.json (but not v{version}_data.json)
        for metadata_file in sorted(version_dir.glob("v[0-9]*.json")):
            # Skip data files which have '_data' in the name
            if '_data' in metadata_file.name:
                continue
            try:
                data = json.loads(metadata_file.read_text())
                history.append(data)
            except Exception as e:
                logger.error("Failed to load version metadata from %s: %s", metadata_file, e)
        return history

    def create_backup(self, graph_id: str, backup_name: Optional[str] = None) -> str:
        """Create a backup of a specific graph."""
        with self._thread_safe():
            try:
                metadata = self._get_metadata(graph_id)
                if not metadata:
                    raise SFMPersistenceError(f"Graph '{graph_id}' not found for backup.")

                graph_file = self.file_manager.get_graph_file_path(graph_id, metadata.format)
                if not graph_file.exists():
                    raise SFMPersistenceError(f"Graph file '{graph_file}' not found for backup.")

                backup_name = backup_name or f"{graph_id}_backup"
                backup_path = self.file_manager.backups_path / f"{backup_name}.backup"

                logger.debug("Creating backup for graph ID '%s'", graph_id)
                logger.debug("Graph file path: %s", graph_file)
                logger.debug("Metadata content: %s", metadata)
                logger.debug("Backup file path: %s", backup_path)

                # Log serialized data for debugging
                serialized_data = graph_file.read_bytes()
                logger.debug("Serialized data in graph file: %s", serialized_data[:100])

                shutil.copy2(graph_file, backup_path)
                logger.info("Backup created for graph '%s' at '%s'", graph_id, backup_path)
                return str(backup_path)

            except Exception as e:
                logger.error("Failed to create backup for graph '%s': %s", graph_id, str(e))
                raise SFMPersistenceError(f"Failed to create backup: {str(e)}") from e

    def restore_from_backup(self, backup_path: str, new_graph_id: Optional[str] = None) -> str:
        """Restore a graph from backup."""
        with self._thread_safe():
            try:
                backup_file = Path(backup_path)
                if not backup_file.exists():
                    raise SFMPersistenceError(f"Backup file '{backup_path}' not found.")

                # Extract original graph ID from backup filename
                original_graph_id = backup_file.stem.rsplit("_backup", 1)[0]
                new_graph_id = new_graph_id or original_graph_id

                # Restore graph data
                graph_file_path = self.file_manager.get_graph_file_path(
                    new_graph_id, self.config.default_format)
                shutil.copy2(backup_file, graph_file_path)

                # Restore metadata
                # This is a simplified restore; a real implementation might store
                # metadata in the backup
                # or reconstruct it. Here, we'll try to load the graph to create basic metadata.
                serialized_data = graph_file_path.read_bytes()
                if not serialized_data:
                    raise SFMPersistenceError("Restored graph file is empty.")

                restored_graph = SFMGraphSerializer.deserialize_graph(
                    serialized_data, self.config.default_format)
                # Ensure the graph was successfully deserialized
                logger.debug("Restored graph deserialized successfully.")

                # Create and save new metadata for the restored graph
                metadata = self._create_metadata(
                    graph_id=new_graph_id,
                    graph=restored_graph,
                    version=1,  # Start with version 1
                    current_metadata=None,
                    metadata={},
                    serialized_data=serialized_data,
                    checksum=hashlib.sha256(serialized_data).hexdigest(),
                    format_type=self.config.default_format
                )
                self._save_metadata(new_graph_id, metadata)
                self._metadata_cache[new_graph_id] = metadata

                logger.info("Graph '%s' restored successfully from backup '%s'",
                           new_graph_id, backup_path)
                return new_graph_id

            except Exception as e:
                logger.error("Failed to restore from backup: %s", str(e))
                raise SFMPersistenceError(f"Failed to restore from backup: {str(e)}") from e

    def check_version_consistency(self, graph_id: str) -> Dict[str, Any]:
        """Check version consistency for a graph across all storage locations."""
        try:
            result = {
                'graph_id': graph_id,
                'is_consistent': True,
                'issues': [],
                'current_version': None,
                'version_files': [],
                'recommendations': []
            }
            
            # Get current metadata
            current_metadata = self._get_metadata(graph_id)
            if not current_metadata:
                result['is_consistent'] = False
                result['issues'].append("No current metadata found")
                return result
                
            result['current_version'] = current_metadata.version
            
            # Check if current graph file exists
            current_graph_file = self.file_manager.get_graph_file_path(graph_id, current_metadata.format)
            if not current_graph_file.exists():
                result['is_consistent'] = False
                result['issues'].append("Current graph file missing")
            
            # Check version history consistency
            version_history = self.get_version_history(graph_id)
            for version_info in version_history:
                version_num = version_info.get('version')
                if version_num:
                    version_file = self.file_manager.get_version_file_path(
                        graph_id, version_num, StorageFormat(version_info.get('format', 'json'))
                    )
                    
                    version_status = {
                        'version': version_num,
                        'metadata_exists': True,
                        'data_file_exists': version_file.exists()
                    }
                    
                    if not version_status['data_file_exists']:
                        result['is_consistent'] = False
                        result['issues'].append(f"Version {version_num} data file missing")
                        
                    result['version_files'].append(version_status)
            
            # Generate recommendations
            if not result['is_consistent']:
                if "Current graph file missing" in result['issues']:
                    result['recommendations'].append("Restore current graph from latest version or backup")
                if any("data file missing" in issue for issue in result['issues']):
                    result['recommendations'].append("Consider cleaning up orphaned version metadata")
                    
            return result
            
        except Exception as e:
            logger.error("Failed to check version consistency for '%s': %s", graph_id, str(e))
            return {
                'graph_id': graph_id,
                'is_consistent': False,
                'issues': [f"Consistency check failed: {str(e)}"],
                'error': str(e)
            }

    def cleanup_old_versions(self, graph_id: str, keep_versions: int = None) -> Dict[str, Any]:
        """Clean up old versions of a graph, keeping the specified number of recent versions."""
        if keep_versions is None:
            keep_versions = self.config.max_versions
            
        try:
            result = {
                'graph_id': graph_id,
                'versions_before': 0,
                'versions_after': 0,
                'cleaned_up': [],
                'space_freed_bytes': 0
            }
            
            version_history = self.get_version_history(graph_id)
            result['versions_before'] = len(version_history)
            
            if len(version_history) <= keep_versions:
                result['versions_after'] = result['versions_before']
                return result
            
            # Sort by version number (descending) to keep the most recent
            version_history.sort(key=lambda x: x.get('version', 0), reverse=True)
            versions_to_remove = version_history[keep_versions:]
            
            for version_info in versions_to_remove:
                version_num = version_info.get('version')
                if not version_num:
                    continue
                    
                try:
                    # Remove version metadata file
                    version_dir = self.file_manager.versions_path / graph_id
                    version_metadata_file = version_dir / f"v{version_num}.json"
                    
                    space_freed = 0
                    if version_metadata_file.exists():
                        space_freed += version_metadata_file.stat().st_size
                        version_metadata_file.unlink()
                    
                    # Remove version data file
                    format_type = StorageFormat(version_info.get('format', 'json'))
                    version_data_file = self.file_manager.get_version_file_path(
                        graph_id, version_num, format_type
                    )
                    if version_data_file.exists():
                        space_freed += version_data_file.stat().st_size
                        version_data_file.unlink()
                    
                    result['cleaned_up'].append(version_num)
                    result['space_freed_bytes'] += space_freed
                    
                except Exception as e:
                    logger.warning("Failed to remove version %d for graph '%s': %s", 
                                 version_num, graph_id, str(e))
            
            result['versions_after'] = result['versions_before'] - len(result['cleaned_up'])
            
            logger.info("Cleaned up %d old versions for graph '%s', freed %d bytes",
                       len(result['cleaned_up']), graph_id, result['space_freed_bytes'])
            
            return result
            
        except Exception as e:
            logger.error("Failed to cleanup old versions for '%s': %s", graph_id, str(e))
            raise SFMPersistenceError(f"Failed to cleanup old versions: {str(e)}") from e

    def cleanup_old_backups(self, max_age_days: int = 30) -> Dict[str, Any]:
        """Clean up old backup files older than specified age."""
        try:
            result = {
                'backups_before': 0,
                'backups_after': 0,
                'cleaned_up': [],
                'space_freed_bytes': 0
            }
            
            if not self.file_manager.backups_path.exists():
                return result
                
            backup_files = list(self.file_manager.backups_path.glob("*.backup"))
            result['backups_before'] = len(backup_files)
            
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(days=max_age_days)
            
            for backup_file in backup_files:
                try:
                    file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_mtime < cutoff_time:
                        space_freed = backup_file.stat().st_size
                        backup_file.unlink()
                        result['cleaned_up'].append(backup_file.name)
                        result['space_freed_bytes'] += space_freed
                        
                except Exception as e:
                    logger.warning("Failed to remove backup file '%s': %s", backup_file, str(e))
            
            result['backups_after'] = result['backups_before'] - len(result['cleaned_up'])
            
            logger.info("Cleaned up %d old backups, freed %d bytes", 
                       len(result['cleaned_up']), result['space_freed_bytes'])
            
            return result
            
        except Exception as e:
            logger.error("Failed to cleanup old backups: %s", str(e))
            raise SFMPersistenceError(f"Failed to cleanup old backups: {str(e)}") from e


# Convenience functions for quick operations

def save_sfm_graph(graph_id: str, graph: SFMGraph,
                   storage_path: str = "./sfm_data") -> GraphMetadata:
    """Quick save function for SFM graphs."""
    manager = SFMPersistenceManager(storage_path)
    return manager.save_graph(graph_id, graph)


def load_sfm_graph(graph_id: str, storage_path: str = "./sfm_data") -> Optional[SFMGraph]:
    """Quick load function for SFM graphs."""
    manager = SFMPersistenceManager(storage_path)
    return manager.load_graph(graph_id)


def list_sfm_graphs(storage_path: str = "./sfm_data") -> List[str]:
    """Quick list function for SFM graphs."""
    manager = SFMPersistenceManager(storage_path)
    # Ensure the result is a list of strings
    return [str(gid) for gid in manager.list_graphs(include_metadata=False)]
