"""
SFM Service - Unified Facade for Social Fabric Matrix Framework

This module provides a simplified, unified interface to the SFM framework's core functionality.
It acts as a facade that abstracts away the complexity of directly working with repositories,
query engines, and data models, providing an intuitive API for common SFM operations.

The service is designed to work as a direct Python library and as a backend service
for various client applications.

Key Features:
- Unified interface for creating, managing, and analyzing SFM graphs
- Built-in repository management with pluggable storage backends
- Integrated query engine for advanced network analysis
- High-level operations for common SFM use cases
- Type-safe operations with runtime validation
- Automatic graph synchronization and consistency management
- Comprehensive error handling and logging

Usage Examples:

Direct Python Usage:
```python
from api.sfm_service import SFMService

service = SFMService()
actor = service.create_actor(name="USDA", sector="government")
policy = service.create_policy(name="Farm Bill 2023")
service.connect(actor.id, policy.id, "IMPLEMENTS")
analysis = service.analyze_centrality()
```

Direct Usage:
```python
from api.sfm_service import SFMService

service = SFMService()

# Create entities
actor = service.create_actor(name="Tech Corp", sector="Technology")
resource = service.create_resource(name="Solar Panel", rtype="PRODUCED")
```
"""

# Standard library imports
import logging
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Type, TypeVar

# Third-party imports
import networkx as nx

# Local imports
from models import (
    Node,
    Actor,
    Institution,
    Resource,
    Process,
    Flow,
    Relationship,
    Policy,
)
from graph import SFMGraph
from models.sfm_enums import ResourceType, RelationshipKind
from graph.sfm_query import SFMQueryEngine, NetworkXSFMQueryEngine
from models.exceptions import (
    SFMError,
    SFMValidationError,
    SFMNotFoundError,
    GraphOperationError,
    NodeCreationError,
    NodeUpdateError,
    NodeDeleteError,
    RelationshipValidationError,
    QueryExecutionError,
    ErrorContext,
    ErrorCode,
    create_not_found_error,
    create_validation_error,
    create_node_creation_error,
)
from config.config_manager import get_config, SFMConfig
from config.secrets_manager import SecretsManagerFactory
from infrastructure.security_validators import (
    validate_and_sanitize_node_data,
    SecurityValidationError,
)
from infrastructure.transaction_manager import TransactionManager
from infrastructure.audit_logger import (
    AuditLogger, audit_operation, OperationType as AuditOperationType,
    AuditLevel, get_audit_logger
)
from infrastructure.performance_metrics import (
    MetricsCollector, get_metrics_collector, timed_operation
)
from infrastructure.lock_manager import get_lock_manager, LockType
from utils.patterns.command import CommandManager, AddNodeCommand, AddRelationshipCommand
from data.repositories import (
    SFMRepositoryFactory,
    ActorRepository,
    InstitutionRepository,
    PolicyRepository,
    ResourceRepository,
    RelationshipRepository,
    ProcessRepository,
    FlowRepository,
)

# Constants
DEFAULT_PAGE_LIMIT = 100
DEFAULT_PAGE_OFFSET = 0
MAX_PAGE_LIMIT = 1000
DEFAULT_GRAPH_SIZE_LIMIT = 10000
DEFAULT_QUERY_TIMEOUT = 30
TOP_NODES_LIMIT = 10
DEFAULT_DISTANCE = 1

# Setup logging
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Node)  # Generic type for Node entities

# Backward compatibility alias
ValidationError = SFMValidationError
SFMServiceError = SFMError

# Public API
__all__ = [
    # DTOs
    'CreateActorRequest',
    'CreateInstitutionRequest', 
    'CreatePolicyRequest',
    'CreateResourceRequest',
    'CreateRelationshipRequest',
    'NodeResponse',
    'RelationshipResponse',
    'GraphStatistics',
    'CentralityAnalysis',
    'PolicyImpactAnalysis',
    'ServiceStatus',
    'ServiceHealth',
    'SFMServiceConfig',
    'SFMError',
    'SFMValidationError',
    'ValidationError',  # Backward compatibility alias
    'SFMServiceError',  # Backward compatibility alias
    'SFMNotFoundError',
    'GraphOperationError',
    'NodeCreationError',
    'NodeUpdateError',
    'NodeDeleteError',
    'RelationshipValidationError',
    'QueryExecutionError',
    'SFMService',
    'DEFAULT_PAGE_LIMIT',
    'DEFAULT_PAGE_OFFSET',
    'MAX_PAGE_LIMIT',
    'DEFAULT_GRAPH_SIZE_LIMIT',
    'quick_analysis',
]


# ═══ DATA TRANSFER OBJECTS (DTOs) ═══

@dataclass
class CreateActorRequest:
    """Request model for creating an actor."""

    name: str
    description: str = ""
    sector: str = ""
    legal_form: str = ""
    meta: Optional[Dict[str, str]] = None


@dataclass
class CreateInstitutionRequest:
    """Request model for creating an institution."""

    name: str
    description: str = ""
    meta: Optional[Dict[str, str]] = None


@dataclass
class CreatePolicyRequest:
    """Request model for creating a policy."""

    name: str
    description: str = ""
    authority: str = ""
    target_sectors: Optional[List[str]] = None
    enforcement: float = 0.0
    meta: Optional[Dict[str, str]] = None


@dataclass
class CreateResourceRequest:
    """Request model for creating a resource."""

    name: str
    description: str = ""
    rtype: str = "NATURAL"  # String representation
    unit: str = ""
    meta: Optional[Dict[str, str]] = None


@dataclass
class CreateRelationshipRequest:
    """Request model for creating a relationship."""

    source_id: str  # String UUID
    target_id: str  # String UUID
    kind: str
    weight: float = 1.0
    meta: Optional[Dict[str, str]] = None


@dataclass
class NodeResponse:
    """Response model for node entities."""

    id: str
    label: str
    description: str
    node_type: str
    meta: Dict[str, Any]
    created_at: Optional[str] = None

@dataclass
class RelationshipResponse:
    """Response model for relationships."""

    id: str
    source_id: str
    target_id: str
    kind: str
    weight: float
    meta: Optional[Dict[str, Any]] = None


@dataclass
class GraphStatistics:
    """Response model for graph statistics."""

    total_nodes: int
    total_relationships: int
    node_types: Dict[str, int]
    relationship_kinds: Dict[str, int]
    timestamp: str


@dataclass
class CentralityAnalysis:
    """Response model for centrality analysis."""

    node_centrality: Dict[str, float]
    most_central_nodes: List[Tuple[str, float]]
    analysis_type: str
    timestamp: str


@dataclass
class PolicyImpactAnalysis:
    """Response model for policy impact analysis."""

    policy_id: str
    total_affected_nodes: int
    affected_actors: List[str]
    affected_institutions: List[str]
    affected_resources: List[str]
    network_metrics: Dict[str, float]
    impact_radius: int


class ServiceStatus(Enum):
    """Service operational status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    ERROR = "error"


@dataclass
class ServiceHealth:
    """Service health check response."""

    status: ServiceStatus
    timestamp: str
    version: str = "1.0.0"
    backend: str = "networkx"
    node_count: int = 0
    relationship_count: int = 0
    last_operation: Optional[str] = None


# ═══ SERVICE CONFIGURATION ═══


@dataclass
@dataclass
class SFMServiceConfig:
    """Configuration for SFM Service."""

    storage_backend: str = "networkx"
    auto_sync: bool = True
    validation_enabled: bool = True
    cache_queries: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"
    max_graph_size: int = DEFAULT_GRAPH_SIZE_LIMIT
    query_timeout: int = DEFAULT_QUERY_TIMEOUT
    
    # New configuration fields that can be overridden
    use_global_config: bool = True
    global_config: Optional[SFMConfig] = None
    
    @classmethod
    def from_global_config(cls, global_config: Optional[SFMConfig] = None) -> 'SFMServiceConfig':
        """Create service config from global configuration.
        
        Args:
            global_config: Global configuration object, or None to load from default
            
        Returns:
            SFMServiceConfig: Service configuration
        """
        if global_config is None:
            global_config = get_config()
        
        return cls(
            storage_backend="networkx",  # Default for now
            auto_sync=True,
            validation_enabled=True,
            cache_queries=global_config.cache.backend != "memory",
            enable_logging=global_config.logging.console_enabled,
            log_level=global_config.logging.level,
            max_graph_size=DEFAULT_GRAPH_SIZE_LIMIT,
            query_timeout=DEFAULT_QUERY_TIMEOUT,
            use_global_config=True,
            global_config=global_config
        )


# ═══ MAIN SERVICE CLASS ═══


class SFMService:
    """
    Unified facade for Social Fabric Matrix framework operations.

    This service provides a simplified interface for creating, managing, and analyzing
    SFM graphs without requiring direct interaction with repositories or query engines.
    It's designed to work as a direct Python library and as a backend for various applications.
    """

    def __init__(self, config: Optional[SFMServiceConfig] = None):
        """
        Initialize the SFM Service.

        Args:
            config: Service configuration options
        """
        # Load configuration - use global config if not provided
        if config is None:
            try:
                global_config = get_config()
                self.config = SFMServiceConfig.from_global_config(global_config)
            except Exception as e:
                logger.warning(f"Failed to load global configuration: {e}")
                self.config = SFMServiceConfig()
        else:
            self.config = config

        # Setup logging
        if self.config.enable_logging:
            logging.basicConfig(level=getattr(logging, self.config.log_level.upper()))

        # Initialize repositories
        self._base_repo = SFMRepositoryFactory.create_repository(
            self.config.storage_backend
        )
        self._actor_repo = ActorRepository(self._base_repo)
        self._institution_repo = InstitutionRepository(self._base_repo)
        self._policy_repo = PolicyRepository(self._base_repo)
        self._resource_repo = ResourceRepository(self._base_repo)
        self._relationship_repo = RelationshipRepository(self._base_repo)
        self._process_repo = ProcessRepository(self._base_repo)
        self._flow_repo = FlowRepository(self._base_repo)

        # Initialize query engine (lazy-loaded)
        self._query_engine: Optional[SFMQueryEngine] = None
        self._graph_cache: Optional[SFMGraph] = None
        self._cache_dirty = True
        self._last_operation: Optional[str] = None

        # Initialize new systems
        self._transaction_manager = TransactionManager()
        self._audit_logger = get_audit_logger()
        self._metrics_collector = get_metrics_collector()
        self._lock_manager = get_lock_manager()
        self._command_manager = CommandManager()  # Add command manager

        logger.info(
            "SFM Service initialized with backend: %s", self.config.storage_backend
        )

    # ═══ PROPERTY ACCESS & INTERNAL METHODS ═══

    @property
    def query_engine(self) -> SFMQueryEngine:
        """Get the query engine, creating it if necessary."""
        if self._query_engine is None or self._cache_dirty:
            graph = self.get_graph()
            self._query_engine = NetworkXSFMQueryEngine(graph)
            self._cache_dirty = False
        return self._query_engine

    def get_graph(self) -> SFMGraph:
        """Get the current SFM graph."""
        if self._graph_cache is None or self._cache_dirty:
            self._graph_cache = self._base_repo.load_graph()
            self._cache_dirty = False
        return self._graph_cache

    def _mark_dirty(self, operation: Optional[str] = None):
        """Mark the cache as dirty after modifications."""
        if self.config.auto_sync:
            self._cache_dirty = True
        self._last_operation = operation or "unknown"
        logger.debug("Cache marked dirty after operation: %s", self._last_operation)

    def _validate_graph_size(self):
        """Validate that the graph hasn't exceeded size limits."""
        if self.config.max_graph_size > 0:
            stats = self.get_statistics()
            if stats.total_nodes > self.config.max_graph_size:
                message = (
                    f"Graph size ({stats.total_nodes}) exceeds maximum "
                    f"({self.config.max_graph_size})"
                )
                raise SFMError(
                    message,
                    ErrorCode.GRAPH_SIZE_EXCEEDED,
                    remediation="Consider pruning the graph or increasing the size limit"
                )

    def _convert_to_resource_type(self, rtype_str: str) -> ResourceType:
        """Convert string to ResourceType enum."""
        try:
            return ResourceType[rtype_str.upper()]
        except KeyError as exc:
            raise SFMValidationError(
                f"Invalid resource type: {rtype_str}", "rtype", rtype_str
            ) from exc

    def _convert_to_relationship_kind(self, kind_str: str) -> RelationshipKind:
        """Convert string to RelationshipKind enum."""
        try:
            return RelationshipKind[kind_str.upper()]
        except KeyError:
            # Default to AFFECTS if not found
            logger.warning("Unknown relationship kind '%s', using AFFECTS", kind_str)
            return RelationshipKind.AFFECTS

    def _node_to_response(self, node: Node) -> NodeResponse:
        """Convert a Node to a NodeResponse."""
        return NodeResponse(
            id=str(node.id),
            label=node.label,
            description=node.description or "",
            node_type=type(node).__name__,
            meta=node.meta or {},
            created_at=datetime.now().isoformat(),
        )

    def _relationship_to_response(self, rel: Relationship) -> RelationshipResponse:
        """Convert a Relationship to a RelationshipResponse."""
        return RelationshipResponse(
            id=str(rel.id),
            source_id=str(rel.source_id),
            target_id=str(rel.target_id),
            kind=rel.kind.name,
            weight=rel.weight or 1.0,
            meta=rel.meta if hasattr(rel, "meta") else {},
        )

    # ═══ HEALTH & STATUS ═══

    @timed_operation("get_health")
    def get_health(self) -> ServiceHealth:
        """Get service health status with enhanced metrics."""
        try:
            stats = self.get_statistics()
            
            # Get performance and audit metrics
            performance_summary = self._metrics_collector.get_summary_stats()
            audit_stats = self._audit_logger.get_audit_stats()
            transaction_stats = self._transaction_manager.get_transaction_stats()
            
            # Enhanced health information
            enhanced_health = ServiceHealth(
                status=ServiceStatus.HEALTHY,
                timestamp=datetime.now().isoformat(),
                backend=self.config.storage_backend,
                node_count=stats.total_nodes,
                relationship_count=stats.total_relationships,
                last_operation=self._last_operation,
            )
            
            # Add enhanced metrics to the health response via metadata
            if hasattr(enhanced_health, 'meta'):
                enhanced_health.meta = {
                    "performance_metrics": {
                        "total_operations": performance_summary.get("total_operations", 0),
                        "operations_per_second": performance_summary.get("operations_per_second", 0.0),
                        "error_rate": performance_summary.get("error_rate", 0.0),
                        "uptime_seconds": performance_summary.get("uptime_seconds", 0.0)
                    },
                    "audit_metrics": {
                        "total_audit_events": audit_stats.get("total_events", 0),
                        "recent_events": audit_stats.get("recent_events", 0)
                    },
                    "transaction_metrics": {
                        "total_transactions": transaction_stats.get("total_transactions", 0),
                        "committed_transactions": transaction_stats.get("committed_transactions", 0),
                        "rolled_back_transactions": transaction_stats.get("rolled_back_transactions", 0),
                        "active_transactions": transaction_stats.get("active_transactions", 0)
                    }
                }
            
            return enhanced_health
            
        except Exception as e:
            logger.error("Health check failed: %s", e)
            return ServiceHealth(
                status=ServiceStatus.ERROR,
                timestamp=datetime.now().isoformat(),
                backend=self.config.storage_backend,
                last_operation=self._last_operation,
            )

    # ═══ ENTITY CREATION ═══

    @audit_operation(AuditOperationType.CREATE, entity_type="Actor")
    @timed_operation("create_actor")
    def create_actor(
        self, request: Union[CreateActorRequest, dict], **kwargs
    ) -> NodeResponse:
        """
        Create a new Actor entity with security validation.

        Args:
            request: CreateActorRequest object or dict with actor data
            **kwargs: Additional arguments for direct Python usage

        Returns:
            NodeResponse with the created actor data
        """
        try:
            # Handle both request objects and direct calls
            if isinstance(request, dict):
                data = request
            elif isinstance(request, CreateActorRequest):
                data = asdict(request)
            else:
                # Direct call with named parameters
                data = {"name": request, **kwargs}

            # Security validation - sanitize and validate input data
            try:
                data = validate_and_sanitize_node_data(data)
            except SecurityValidationError as e:
                logger.warning("Security validation failed for actor creation: %s", e.message)
                raise SFMValidationError(f"Security validation failed: {e.message}",
                                      e.field, e.value) from e

            if self.config.validation_enabled:
                if not data.get("name"):
                    raise SFMValidationError("Actor name is required", "name")

            actor = Actor(
                label=data["name"],
                description=data.get("description", ""),
                sector=data.get("sector", ""),
                legal_form=data.get("legal_form", ""),
                meta=data.get("meta", {}),
            )

            result = self._actor_repo.create(actor)
            
            # Track operation in transaction if active
            if self._transaction_manager.is_in_transaction():
                self._transaction_manager.add_operation(
                    operation_type="create_actor",
                    data={"actor_id": str(result.id), "name": result.label},
                    rollback_data={"actor_id": str(result.id)},
                    rollback_function=lambda data: self._rollback_create_actor(data["actor_id"])
                )
            
            self._mark_dirty("create_actor")
            self._validate_graph_size()

            logger.info("Created actor: %s (%s)", result.label, result.id)
            return self._node_to_response(result)

        except (ValueError, TypeError) as e:
            logger.error("Failed to create actor: %s", e)
            raise SFMValidationError(f"Invalid actor data: {str(e)}") from e
        except SFMError:
            raise
        except Exception as e:
            logger.error("Failed to create actor: %s", e)
            raise SFMError(
                f"Failed to create actor: {str(e)}", ErrorCode.CREATE_ACTOR_FAILED
            ) from e

    @audit_operation(AuditOperationType.CREATE, entity_type="Institution")
    @timed_operation("create_institution")
    def create_institution(
        self, request: Union[CreateInstitutionRequest, dict], **kwargs
    ) -> NodeResponse:
        """Create a new Institution entity with security validation."""
        try:
            if isinstance(request, dict):
                data = request
            elif isinstance(request, CreateInstitutionRequest):
                data = asdict(request)
            else:
                data = {"name": request, **kwargs}

            # Security validation - sanitize and validate input data
            try:
                data = validate_and_sanitize_node_data(data)
            except SecurityValidationError as e:
                logger.warning("Security validation failed for institution creation: %s", e.message)
                raise SFMValidationError(f"Security validation failed: {e.message}",
                                      e.field, e.value) from e

            if self.config.validation_enabled:
                if not data.get("name"):
                    raise SFMValidationError("Institution name is required", "name")

            institution = Institution(
                label=data["name"],
                description=data.get("description", ""),
                meta=data.get("meta", {}),
            )

            result = self._institution_repo.create(institution)
            
            # Track operation in transaction if active
            if self._transaction_manager.is_in_transaction():
                self._transaction_manager.add_operation(
                    operation_type="create_institution",
                    data={"institution_id": str(result.id), "name": result.label},
                    rollback_data={"institution_id": str(result.id)},
                    rollback_function=lambda data: self._rollback_create_institution(data["institution_id"])
                )
            
            self._mark_dirty("create_institution")

            logger.info("Created institution: %s (%s)", result.label, result.id)
            return self._node_to_response(result)

        except (ValueError, TypeError) as e:
            logger.error("Failed to create institution: %s", e)
            raise SFMValidationError(f"Invalid institution data: {str(e)}") from e
        except SFMError:
            raise
        except Exception as e:
            logger.error("Failed to create institution: %s", e)
            raise SFMError(
                f"Failed to create institution: {str(e)}", "CREATE_INSTITUTION_FAILED"
            ) from e

    @audit_operation(AuditOperationType.CREATE, entity_type="Policy")  
    @timed_operation("create_policy")
    def create_policy(
        self, request: Union[CreatePolicyRequest, dict], **kwargs
    ) -> NodeResponse:
        """Create a new Policy entity with security validation."""
        try:
            if isinstance(request, dict):
                data = request
            elif isinstance(request, CreatePolicyRequest):
                data = asdict(request)
            else:
                data = {"name": request, **kwargs}

            # Security validation - sanitize and validate input data
            try:
                data = validate_and_sanitize_node_data(data)
            except SecurityValidationError as e:
                logger.warning("Security validation failed for policy creation: %s", e.message)
                raise SFMValidationError(f"Security validation failed: {e.message}",
                                      e.field, e.value) from e

            if self.config.validation_enabled:
                if not data.get("name"):
                    raise SFMValidationError("Policy name is required", "name")

            policy = Policy(
                label=data["name"],
                description=data.get("description", ""),
                authority=data.get("authority", ""),
                target_sectors=data.get("target_sectors", []),
                enforcement=data.get("enforcement", 0.0),
                meta=data.get("meta", {}),
            )

            result = self._policy_repo.create(policy)
            
            # Track operation in transaction if active
            if self._transaction_manager.is_in_transaction():
                self._transaction_manager.add_operation(
                    operation_type="create_policy",
                    data={"policy_id": str(result.id), "name": result.label},
                    rollback_data={"policy_id": str(result.id)},
                    rollback_function=lambda data: self._rollback_create_policy(data["policy_id"])
                )
            
            self._mark_dirty("create_policy")

            logger.info("Created policy: %s (%s)", result.label, result.id)
            return self._node_to_response(result)

        except (ValueError, TypeError) as e:
            logger.error("Failed to create policy: %s", e)
            raise SFMValidationError(f"Invalid policy data: {str(e)}") from e
        except SFMError:
            raise
        except Exception as e:
            logger.error("Failed to create policy: %s", e)
            raise SFMError(
                f"Failed to create policy: {str(e)}", "CREATE_POLICY_FAILED"
            ) from e

    def create_resource(
        self, request: Union[CreateResourceRequest, dict], **kwargs
    ) -> NodeResponse:
        """Create a new Resource entity with security validation."""
        try:
            if isinstance(request, dict):
                data = request
            elif isinstance(request, CreateResourceRequest):
                data = asdict(request)
            else:
                data = {"name": request, **kwargs}

            # Security validation - sanitize and validate input data
            try:
                data = validate_and_sanitize_node_data(data)
            except SecurityValidationError as e:
                logger.warning("Security validation failed for resource creation: %s", e.message)
                raise SFMValidationError(f"Security validation failed: {e.message}",
                                      e.field, e.value) from e

            if self.config.validation_enabled:
                if not data.get("name"):
                    raise SFMValidationError("Resource name is required", "name")

            rtype = self._convert_to_resource_type(data.get("rtype", "NATURAL"))

            resource = Resource(
                label=data["name"],
                description=data.get("description", ""),
                rtype=rtype,
                unit=data.get("unit", ""),
                meta=data.get("meta", {}),
            )

            result = self._resource_repo.create(resource)
            
            # Track operation in transaction if active
            if self._transaction_manager.is_in_transaction():
                self._transaction_manager.add_operation(
                    operation_type="create_resource",
                    data={"resource_id": str(result.id), "name": result.label},
                    rollback_data={"resource_id": str(result.id)},
                    rollback_function=lambda data: self._rollback_create_resource(data["resource_id"])
                )
            
            self._mark_dirty("create_resource")

            logger.info("Created resource: %s (%s)", result.label, result.id)
            return self._node_to_response(result)

        except (ValueError, TypeError) as e:
            logger.error("Failed to create resource: %s", e)
            raise SFMValidationError(f"Invalid resource data: {str(e)}") from e
        except SFMError:
            raise
        except Exception as e:
            logger.error("Failed to create resource: %s", e)
            raise SFMError(
                f"Failed to create resource: {str(e)}", "CREATE_RESOURCE_FAILED"
            ) from e

    # ═══ RELATIONSHIP MANAGEMENT ═══

    def create_relationship(
        self, request: Union[CreateRelationshipRequest, dict], **kwargs
    ) -> RelationshipResponse:
        """Create a relationship between two entities with referential integrity validation."""
        try:
            if isinstance(request, dict):
                data = request
            elif isinstance(request, CreateRelationshipRequest):
                data = asdict(request)
            else:
                # Direct call with positional args
                data = {
                    "source_id": str(request),
                    "target_id": str(kwargs.get("target_id")),
                    "kind": kwargs.get(
                        "kind", kwargs.get("relationship_kind", "AFFECTS")
                    ),
                    "weight": kwargs.get("weight", 1.0),
                    "meta": kwargs.get("meta", {}),
                }

            if self.config.validation_enabled:
                if not data.get("source_id") or not data.get("target_id"):
                    raise SFMValidationError("Source and target IDs are required")
                if not data.get("kind"):
                    raise SFMValidationError("Relationship kind is required")

            source_id = uuid.UUID(data["source_id"])
            target_id = uuid.UUID(data["target_id"])
            
            # Handle self-referencing relationships to avoid deadlock
            if source_id == target_id:
                # For self-referencing relationships, only acquire one lock
                with self._lock_manager.lock_entity(source_id, LockType.READ) as entity_lock:
                    # Referential integrity validation - ensure entity exists
                    if not self._validate_relationship_integrity(source_id, target_id):
                        raise SFMValidationError(
                            f"Referential integrity violation: entity {source_id} does not exist"
                        )
                    
                    kind = self._convert_to_relationship_kind(data["kind"])

                    relationship = Relationship(
                        source_id=source_id,
                        target_id=target_id,
                        kind=kind,
                        weight=data.get("weight", 1.0),
                        meta=data.get("meta", {})
                    )
                    
                    result = self._relationship_repo.create(relationship)
                    self._mark_dirty("create_relationship")
                    return self._relationship_to_response(result)
            else:
                # For different entities, acquire locks on both to prevent concurrent modification
                with self._lock_manager.lock_entity(source_id, LockType.READ) as source_lock:
                    with self._lock_manager.lock_entity(target_id, LockType.READ) as target_lock:
                        # Referential integrity validation - ensure both endpoints exist
                        if not self._validate_relationship_integrity(source_id, target_id):
                            raise SFMValidationError(
                                f"Referential integrity violation: source {source_id} or target {target_id} does not exist"
                            )
                        
                        kind = self._convert_to_relationship_kind(data["kind"])

                        relationship = Relationship(
                            source_id=source_id,
                            target_id=target_id,
                            kind=kind,
                            weight=data.get("weight", 1.0),
                            meta=data.get("meta", {}),
                        )

                        result = self._relationship_repo.create(relationship)
                        
                        # Track operation in transaction if active
                        if self._transaction_manager.is_in_transaction():
                            self._transaction_manager.add_operation(
                                operation_type="create_relationship",
                                data={"relationship_id": str(result.id), "source_id": str(source_id), "target_id": str(target_id)},
                                rollback_data={"relationship_id": str(result.id)},
                                rollback_function=lambda data: self._rollback_create_relationship(data["relationship_id"])
                            )
                        
                        self._mark_dirty("create_relationship")

                        logger.info(
                            "Created relationship: %s --%s--> %s",
                            source_id, kind.name, target_id
                        )
                        return self._relationship_to_response(result)

        except ValueError as e:
            logger.error("Failed to create relationship: %s", e)
            raise SFMValidationError(f"Invalid UUID format: {e}") from e
        except (TypeError, AttributeError) as e:
            logger.error("Failed to create relationship: %s", e)
            raise SFMValidationError(f"Invalid relationship data: {str(e)}") from e
        except SFMError:
            raise
        except Exception as e:
            logger.error("Failed to create relationship: %s", e)
            raise SFMError(
                f"Failed to create relationship: {str(e)}", "CREATE_RELATIONSHIP_FAILED"
            ) from e

    def connect(
        self,
        source_id: Union[str, uuid.UUID],
        target_id: Union[str, uuid.UUID],
        kind: str,
        weight: float = 1.0,
        **kwargs,
    ) -> RelationshipResponse:
        """Convenience method for creating relationships (backward compatibility)."""
        return self.create_relationship(
            {
                "source_id": str(source_id),
                "target_id": str(target_id),
                "kind": kind,
                "weight": weight,
                "meta": kwargs.get("meta", {}),
            }
        )

    # ═══ ENTITY RETRIEVAL ═══

    def get_entity(self, entity_type: Type[T], entity_id: uuid.UUID) -> Optional[T]:
        """Generic method to retrieve any entity by type and ID."""
        try:
            repo_mapping = {
                Actor: self._actor_repo,
                Policy: self._policy_repo,
                Institution: self._institution_repo,
                Resource: self._resource_repo,
                Process: self._process_repo,
                Flow: self._flow_repo,
                Relationship: self._relationship_repo,
                # Add other entity types as needed
            }

            repo = repo_mapping.get(entity_type)
            if repo is None:
                raise ValueError(f"No repository found for entity type: {entity_type}")

            return repo.read(entity_id)
        except Exception as e:
            logger.error("Failed to retrieve %s %s: %s", entity_type.__name__, entity_id, e)
            return None

    def get_actor(self, actor_id: uuid.UUID) -> Optional[Actor]:
        """Retrieve an actor by ID."""
        return self.get_entity(Actor, actor_id)

    def get_policy(self, policy_id: uuid.UUID) -> Optional[Policy]:
        """Retrieve a policy by ID."""
        return self.get_entity(Policy, policy_id)

    def get_institution(self, institution_id: uuid.UUID) -> Optional[Institution]:
        """Retrieve an institution by ID."""
        return self.get_entity(Institution, institution_id)

    def get_resource(self, resource_id: uuid.UUID) -> Optional[Resource]:
        """Retrieve a resource by ID."""
        return self.get_entity(Resource, resource_id)

    def get_process(self, process_id: uuid.UUID) -> Optional[Process]:
        """Retrieve a process by ID."""
        return self.get_entity(Process, process_id)

    def get_flow(self, flow_id: uuid.UUID) -> Optional[Flow]:
        """Retrieve a flow by ID."""
        return self.get_entity(Flow, flow_id)

    def get_relationship(
        self, rel_id: Union[str, uuid.UUID]
    ) -> Optional[RelationshipResponse]:
        """Get a relationship by ID."""
        try:
            if isinstance(rel_id, str):
                rel_id = uuid.UUID(rel_id)

            rel = self._relationship_repo.read(rel_id)
            if not rel:
                return None

            return self._relationship_to_response(rel)

        except ValueError as exc:
            raise SFMValidationError(f"Invalid UUID format: {rel_id}") from exc
        except Exception as e:
            logger.error("Failed to get relationship %s: %s", rel_id, e)
            raise SFMError(
                f"Failed to retrieve relationship: {str(e)}", "GET_RELATIONSHIP_FAILED"
            ) from e

    def get_node_neighbors(
        self,
        node_id: Union[str, uuid.UUID],
        relationship_kinds: Optional[List[str]] = None,
        distance: int = DEFAULT_DISTANCE,
    ) -> List[str]:
        """
        Get neighboring nodes within specified distance.

        Args:
            node_id: ID of the node to find neighbors for
            relationship_kinds: Optional list of relationship kind names to filter by
            distance: Distance/hops to search (default: 1 for direct neighbors)

        Returns:
            List of node IDs as strings
        """
        try:
            if isinstance(node_id, str):
                node_uuid = uuid.UUID(node_id)
            else:
                node_uuid = node_id

            # Convert string relationship kinds to enum values if provided
            relationship_kind_enums = None
            if relationship_kinds:
                relationship_kind_enums = []
                for kind_str in relationship_kinds:
                    try:
                        kind_enum = self._convert_to_relationship_kind(kind_str)
                        relationship_kind_enums.append(kind_enum)
                    except SFMValidationError:
                        logger.warning("Unknown relationship kind: %s", kind_str)

            # Use the query engine to find neighbors
            engine = self.query_engine
            neighbor_ids = engine.get_node_neighbors(
                node_uuid, relationship_kind_enums, distance
            )

            # Convert UUIDs back to strings for compatibility
            return [str(neighbor_id) for neighbor_id in neighbor_ids]

        except ValueError as exc:
            raise SFMValidationError(f"Invalid UUID format: {node_id}") from exc
        except Exception as e:
            logger.error("Failed to get neighbors for node %s: %s", node_id, e)
            raise SFMError(
                f"Failed to get node neighbors: {str(e)}", "GET_NODE_NEIGHBORS_FAILED"
            ) from e

    # ═══ ENTITY LISTING ═══

    def _get_node_type_mapping(self) -> Dict[str, Type[Node]]:
        """Get mapping of string node types to their corresponding classes."""
        return {
            "Actor": Actor,
            "Institution": Institution,
            "Policy": Policy,
            "Resource": Resource,
            "Flow": Flow,
        }

    def _apply_pagination(
        self, items: List[Any], limit: int, offset: int
    ) -> List[Any]:
        """Apply pagination to a list of items."""
        return items[offset : offset + limit]

    def list_nodes(
        self,
        node_type: Optional[str] = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = DEFAULT_PAGE_OFFSET
    ) -> List[NodeResponse]:
        """List nodes with optional filtering and pagination."""
        try:
            # Get node type mapping and filter type
            type_mapping = self._get_node_type_mapping()
            filter_type = type_mapping.get(node_type) if node_type else None

            # Get nodes from repository
            nodes = self._base_repo.list_nodes(filter_type)

            # Apply pagination
            paginated_nodes = self._apply_pagination(nodes, limit, offset)

            return [self._node_to_response(node) for node in paginated_nodes]

        except (ValueError, TypeError) as e:
            logger.error("Failed to list nodes: %s", e)
            raise SFMValidationError(f"Invalid parameters for listing nodes: {str(e)}") from e
        except Exception as e:
            logger.error("Failed to list nodes: %s", e)
            raise SFMError(
                f"Failed to list nodes: {str(e)}", "LIST_NODES_FAILED"
            ) from e

    def list_relationships(
        self,
        kind: Optional[str] = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = DEFAULT_PAGE_OFFSET
    ) -> List[RelationshipResponse]:
        """List relationships with optional filtering and pagination."""
        try:
            # Apply filtering by kind if specified
            filter_kind = self._convert_to_relationship_kind(kind) if kind else None
            relationships = (
                self._relationship_repo.list_all()
                if not filter_kind
                else self._relationship_repo.find_by_kind(filter_kind)
            )

            # Apply pagination
            paginated_rels = self._apply_pagination(relationships, limit, offset)

            return [self._relationship_to_response(rel) for rel in paginated_rels]

        except (ValueError, TypeError) as e:
            logger.error("Failed to list relationships: %s", e)
            raise SFMValidationError(f"Invalid parameters for listing relationships: {str(e)}") from e
        except Exception as e:
            logger.error("Failed to list relationships: %s", e)
            raise SFMError(
                f"Failed to list relationships: {str(e)}", "LIST_RELATIONSHIPS_FAILED"
            ) from e

    # ═══ ANALYSIS OPERATIONS ═══

    def _count_nodes_by_type(self, graph: SFMGraph) -> Tuple[int, Dict[str, int]]:
        """
        Count nodes by their type in the graph.

        Returns:
            Tuple of (total_nodes, type_counts_dict)
        """
        type_counts: Dict[str, int] = {}
        try:
            # Iterate through nodes and count by type
            # This handles both real graphs and mock objects gracefully
            for node in graph:
                node_type = type(node).__name__
                type_counts[node_type] = type_counts.get(node_type, 0) + 1

            total_nodes = len(graph)
        except (TypeError, AttributeError):
            # If graph is not iterable (e.g., Mock object in tests)
            total_nodes = 0
            type_counts = {}

        return total_nodes, type_counts

    def _count_relationships_by_kind(self, graph: SFMGraph) -> Tuple[int, Dict[str, int]]:
        """
        Count relationships by their kind in the graph.

        Returns:
            Tuple of (total_relationships, kind_counts_dict)
        """
        rel_counts: Dict[str, int] = {}
        try:
            # Access relationships attribute safely
            relationships = getattr(graph, 'relationships', {})
            for rel in relationships.values():
                kind = rel.kind.name
                rel_counts[kind] = rel_counts.get(kind, 0) + 1

            total_relationships = len(relationships)
        except (TypeError, AttributeError):
            # If relationships is not accessible, return defaults
            total_relationships = 0
            rel_counts = {}

        return total_relationships, rel_counts

    @audit_operation(AuditOperationType.READ, "get_statistics", level=AuditLevel.INFO)
    @timed_operation("get_statistics")
    def get_statistics(self) -> GraphStatistics:
        """Get comprehensive statistics about the current graph."""
        try:
            graph = self.get_graph()

            # Count nodes by type using helper method
            total_nodes, type_counts = self._count_nodes_by_type(graph)

            # Count relationships by kind using helper method
            total_relationships, rel_counts = self._count_relationships_by_kind(graph)

            return GraphStatistics(
                total_nodes=total_nodes,
                total_relationships=total_relationships,
                node_types=type_counts,
                relationship_kinds=rel_counts,
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error("Failed to get statistics: %s", e)
            raise SFMError(
                f"Failed to get statistics: {str(e)}", "GET_STATISTICS_FAILED"
            ) from e

    def analyze_centrality(
        self, centrality_type: str = "betweenness", limit: int = TOP_NODES_LIMIT
    ) -> CentralityAnalysis:
        """Perform centrality analysis on the network."""
        try:
            engine = self.query_engine
            graph = self.get_graph()

            # Calculate centrality for all nodes
            centrality_scores = {}
            most_central = []

            if len(graph) > 0:
                for node in graph:
                    score = engine.get_node_centrality(node.id, centrality_type)
                    centrality_scores[str(node.id)] = score

                # Get most central nodes
                central_nodes = engine.get_most_central_nodes(
                    None, centrality_type, limit
                )
                most_central = [
                    (str(node_id), score) for node_id, score in central_nodes
                ]

            return CentralityAnalysis(
                node_centrality=centrality_scores,
                most_central_nodes=most_central,
                analysis_type=centrality_type,
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error("Failed to analyze centrality: %s", e)
            raise SFMError(
                f"Failed to analyze centrality: {str(e)}", "CENTRALITY_ANALYSIS_FAILED"
            ) from e

    def _validate_and_convert_uuid(self, value: Union[str, uuid.UUID]) -> uuid.UUID:
        """Validate and convert a string or UUID to a proper UUID object."""
        if isinstance(value, str):
            try:
                return uuid.UUID(value)
            except ValueError as e:
                raise SFMValidationError(f"Invalid UUID format: {value}") from e
        return value

    def _build_policy_impact_analysis(
        self, policy_id: uuid.UUID, impact_data: Dict[str, Any], impact_radius: int
    ) -> PolicyImpactAnalysis:
        """Build PolicyImpactAnalysis from impact data."""
        return PolicyImpactAnalysis(
            policy_id=str(policy_id),
            total_affected_nodes=impact_data.get("total_affected_nodes", 0),
            affected_actors=[
                str(node_id) for node_id in impact_data.get("affected_actors", [])
            ],
            affected_institutions=[
                str(node_id)
                for node_id in impact_data.get("affected_institutions", [])
            ],
            affected_resources=[
                str(node_id)
                for node_id in impact_data.get("affected_resources", [])
            ],
            network_metrics=impact_data.get("network_metrics", {}),
            impact_radius=impact_radius,
        )

    def analyze_policy_impact(
        self, policy_id: Union[str, uuid.UUID], impact_radius: int = 3
    ) -> PolicyImpactAnalysis:
        """Analyze the potential impact of a policy."""
        try:
            # Validate and convert policy ID
            validated_policy_id = self._validate_and_convert_uuid(policy_id)

            # Get impact analysis from query engine
            engine = self.query_engine
            impact_data = engine.analyze_policy_impact(validated_policy_id, impact_radius)

            # Check for error in impact data
            if "error" in impact_data:
                raise SFMNotFoundError("Policy", str(validated_policy_id))

            # Build and return the analysis result
            return self._build_policy_impact_analysis(
                validated_policy_id, impact_data, impact_radius
            )

        except nx.NodeNotFound as e:
            raise SFMNotFoundError("Policy", str(policy_id)) from e
        except SFMValidationError:
            raise
        except (SFMNotFoundError, SFMError):
            raise
        except Exception as e:
            logger.error("Failed to analyze policy impact: %s", e)
            raise SFMError(
                f"Failed to analyze policy impact: {str(e)}",
                "POLICY_IMPACT_ANALYSIS_FAILED",
            ) from e

    def find_shortest_path(
        self,
        source_id: Union[str, uuid.UUID],
        target_id: Union[str, uuid.UUID],
        relationship_kinds: Optional[List[str]] = None,
    ) -> Optional[List[str]]:
        """
        Find the shortest path between two nodes.

        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            relationship_kinds: Optional list of relationship kind names to filter by

        Returns:
            List of node IDs representing the path (including source and target),
            or None if no path exists
        """
        try:
            if isinstance(source_id, str):
                source_uuid = uuid.UUID(source_id)
            else:
                source_uuid = source_id

            if isinstance(target_id, str):
                target_uuid = uuid.UUID(target_id)
            else:
                target_uuid = target_id

            # Convert string relationship kinds to enum values if provided
            relationship_kind_enums = None
            if relationship_kinds:
                relationship_kind_enums = []
                for kind_str in relationship_kinds:
                    try:
                        kind_enum = self._convert_to_relationship_kind(kind_str)
                        relationship_kind_enums.append(kind_enum)
                    except SFMValidationError:
                        logger.warning("Unknown relationship kind: %s", kind_str)

            # Use the query engine to find the path
            engine = self.query_engine
            path_ids = engine.find_shortest_path(
                source_uuid, target_uuid, relationship_kind_enums
            )

            if path_ids is None:
                return None

            # Convert UUIDs back to strings for compatibility
            return [str(node_id) for node_id in path_ids]

        except ValueError as exc:
            raise SFMValidationError("Invalid UUID format in path finding") from exc
        except Exception as e:
            logger.error(
                "Failed to find path between %s and %s: %s", source_id, target_id, e
            )
            raise SFMError(
                f"Failed to find shortest path: {str(e)}", "FIND_PATH_FAILED"
            ) from e

    def find_shortest_path_legacy(self, source_id: str, target_id: str) -> list:
        """
        Find the shortest path between two nodes by their IDs.
        Returns a list of node IDs representing the path, or empty list if no path exists.
        """
        # Get the networkx graph from the base repository
        graph = getattr(self._base_repo, "graph", None)
        if graph is None:
            return []

        try:
            path = nx.shortest_path(graph, source=source_id, target=target_id)
            return path if isinstance(path, list) else []
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            # No path exists or nodes don't exist
            return []
        except Exception as e:
            logger.error("Failed to find legacy path between %s and %s: %s",
                        source_id, target_id, e)
            return []

    # ═══ SYSTEM MANAGEMENT ═══

    @audit_operation(AuditOperationType.DELETE, "clear_all_data", level=AuditLevel.WARNING)
    @timed_operation("clear_all_data")
    def clear_all_data(self) -> Dict[str, Any]:
        """Clear all data from the repository."""
        try:
            stats_before = self.get_statistics()
            self._base_repo.clear()
            self._graph_cache = None
            self._query_engine = None
            self._cache_dirty = True
            self._mark_dirty("clear_all_data")

            logger.warning("All data cleared from repository")
            return {
                "status": "success",
                "nodes_removed": stats_before.total_nodes,
                "relationships_removed": stats_before.total_relationships,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error("Failed to clear data: %s", e)
            raise SFMError(
                f"Failed to clear data: {str(e)}", "CLEAR_DATA_FAILED"
            ) from e

    # ═══ BULK OPERATIONS ═══

    def bulk_create_actors(
        self, requests: List[CreateActorRequest]
    ) -> List[NodeResponse]:
        """Create multiple actors in batch with transaction support."""
        with self.transaction(metadata={"operation": "bulk_create_actors", "count": len(requests)}) as tx:
            results = []
            try:
                for request in requests:
                    result = self.create_actor(request)
                    results.append(result)
                
                logger.info(f"Successfully created {len(results)} actors in bulk operation")
                return results
                
            except Exception as e:
                logger.error(f"Bulk actor creation failed after {len(results)} successful operations: {e}")
                # Transaction will automatically rollback all created actors
                raise SFMError(
                    f"Bulk actor creation failed: {str(e)}", "BULK_CREATE_ACTORS_FAILED"
                ) from e

    def transaction(self, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager for transactional operations.
        
        This provides proper transaction support with rollback capabilities.
        All operations within the transaction context will be rolled back
        if an exception occurs.
        
        Args:
            metadata: Optional metadata for the transaction
            
        Yields:
            SFMService: The service instance for chaining operations
            
        Example:
            with service.transaction() as tx_service:
                actor = tx_service.create_actor(actor_request)
                policy = tx_service.create_policy(policy_request)
                tx_service.connect(actor.id, policy.id, "IMPLEMENTS")
                # All operations committed on successful exit
                # All operations rolled back on exception
        """
        @contextmanager
        def transaction_wrapper():
            with self._transaction_manager.transaction(metadata):
                yield self
        
        return transaction_wrapper()

    # ═══ TRANSACTION ROLLBACK HELPERS ═══

    def _rollback_create_actor(self, actor_id: str):
        """Rollback actor creation by deleting the actor."""
        try:
            self._actor_repo.delete(uuid.UUID(actor_id))
            logger.debug(f"Rolled back actor creation: {actor_id}")
        except Exception as e:
            logger.error(f"Failed to rollback actor creation {actor_id}: {e}")

    def _rollback_create_policy(self, policy_id: str):
        """Rollback policy creation by deleting the policy."""
        try:
            self._policy_repo.delete(uuid.UUID(policy_id))
            logger.debug(f"Rolled back policy creation: {policy_id}")
        except Exception as e:
            logger.error(f"Failed to rollback policy creation {policy_id}: {e}")

    def _rollback_create_institution(self, institution_id: str):
        """Rollback institution creation by deleting the institution."""
        try:
            self._institution_repo.delete(uuid.UUID(institution_id))
            logger.debug(f"Rolled back institution creation: {institution_id}")
        except Exception as e:
            logger.error(f"Failed to rollback institution creation {institution_id}: {e}")

    def _rollback_create_resource(self, resource_id: str):
        """Rollback resource creation by deleting the resource."""
        try:
            self._resource_repo.delete(uuid.UUID(resource_id))
            logger.debug(f"Rolled back resource creation: {resource_id}")
        except Exception as e:
            logger.error(f"Failed to rollback resource creation {resource_id}: {e}")

    def _rollback_create_relationship(self, relationship_id: str):
        """Rollback relationship creation by deleting the relationship."""
        try:
            self._relationship_repo.delete(uuid.UUID(relationship_id))
            logger.debug(f"Rolled back relationship creation: {relationship_id}")
        except Exception as e:
            logger.error(f"Failed to rollback relationship creation {relationship_id}: {e}")

    def _validate_relationship_integrity(self, source_id: uuid.UUID, target_id: uuid.UUID) -> bool:
        """
        Validate referential integrity for relationship endpoints.
        
        Args:
            source_id: Source entity UUID
            target_id: Target entity UUID
            
        Returns:
            True if both entities exist, False otherwise
        """
        try:
            # Check if source entity exists
            source_exists = False
            for repo in [self._actor_repo, self._institution_repo, self._policy_repo, 
                        self._resource_repo, self._process_repo, self._flow_repo]:
                if repo.read(source_id) is not None:
                    source_exists = True
                    break
            
            if not source_exists:
                logger.warning(f"Source entity {source_id} does not exist")
                return False
            
            # Check if target entity exists
            target_exists = False
            for repo in [self._actor_repo, self._institution_repo, self._policy_repo, 
                        self._resource_repo, self._process_repo, self._flow_repo]:
                if repo.read(target_id) is not None:
                    target_exists = True
                    break
            
            if not target_exists:
                logger.warning(f"Target entity {target_id} does not exist")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating relationship integrity: {e}")
            return False

    # ═══ ENHANCED MONITORING & METRICS ═══

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return self._metrics_collector.get_summary_stats()

    def get_operation_metrics(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for specific operations or all operations."""
        if operation_name:
            return self._metrics_collector.get_operation_metrics(operation_name)
        return self._metrics_collector.get_all_operation_metrics()

    def get_audit_metrics(self) -> Dict[str, Any]:
        """Get audit logging statistics."""
        return self._audit_logger.get_audit_stats()

    def get_transaction_metrics(self) -> Dict[str, Any]:
        """Get transaction management statistics."""
        return self._transaction_manager.get_transaction_stats()

    def get_system_resource_metrics(self, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
        """Get system resource usage metrics."""
        return self._metrics_collector.get_system_metrics(limit)

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive service status including all metrics."""
        health = self.get_health()
        return {
            "health": {
                "status": health.status.value,
                "timestamp": health.timestamp,
                "backend": health.backend,
                "node_count": health.node_count,
                "relationship_count": health.relationship_count,
                "last_operation": health.last_operation
            },
            "performance_metrics": self.get_performance_metrics(),
            "audit_metrics": self.get_audit_metrics(),
            "transaction_metrics": self.get_transaction_metrics(),
            "lock_metrics": self._lock_manager.get_lock_stats(),
            "system_metrics": self.get_system_resource_metrics(5)
        }

    def reset_metrics(self):
        """Reset all collected metrics (for testing/maintenance)."""
        self._metrics_collector.reset_metrics()
        # Note: Audit history is retained for compliance

    # ═══ COMMAND PATTERN SUPPORT ═══

    def undo_last_operation(self) -> bool:
        """Undo the last operation using the command pattern."""
        return self._command_manager.undo()

    def redo_last_operation(self) -> bool:
        """Redo the last undone operation using the command pattern."""
        return self._command_manager.redo()

    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get the command history for undo/redo operations."""
        return [
            {
                "command_id": str(metadata.command_id),
                "command_type": metadata.command_type,
                "description": metadata.description,
                "timestamp": metadata.timestamp.isoformat(),
                "executed": metadata.executed,
                "undone": metadata.undone,
                "execution_time_ms": metadata.execution_time_ms,
                "error_message": metadata.error_message
            }
            for metadata in self._command_manager.get_history()
            if metadata is not None
        ]

    def can_undo(self) -> bool:
        """Check if there are operations that can be undone."""
        return self._command_manager.can_undo()

    def can_redo(self) -> bool:
        """Check if there are operations that can be redone."""
        return self._command_manager.can_redo()

    def get_command_statistics(self) -> Dict[str, Any]:
        """Get statistics about command execution."""
        return self._command_manager.get_statistics()

    # ═══ DATA INTEGRITY VALIDATION ═══
    
    def validate_graph_integrity(self) -> List[Dict[str, Any]]:
        """
        Validate the integrity of the entire graph and return violations.
        
        Returns:
            List of integrity violations found
        """
        violations = []
        
        try:
            # Check for orphaned relationships
            orphaned_relationships = self._find_orphaned_relationships()
            for rel_id, details in orphaned_relationships.items():
                violations.append({
                    "type": "orphaned_relationship",
                    "relationship_id": str(rel_id),
                    "source_id": str(details["source_id"]),
                    "target_id": str(details["target_id"]),
                    "missing_entity": details["missing_entity"],
                    "severity": "high"
                })
            
            # Check for graph consistency
            consistency_violations = self._check_graph_consistency()
            violations.extend(consistency_violations)
            
            logger.info(f"Graph integrity validation completed: {len(violations)} violations found")
            return violations
            
        except Exception as e:
            logger.error(f"Graph integrity validation failed: {e}")
            return [{
                "type": "validation_error",
                "message": f"Integrity validation failed: {str(e)}",
                "severity": "critical"
            }]
    
    def _find_orphaned_relationships(self) -> Dict[uuid.UUID, Dict[str, Any]]:
        """
        Find relationships that reference non-existent entities.
        
        Returns:
            Dictionary of orphaned relationship IDs and their details
        """
        orphaned = {}
        
        try:
            # Get all relationships
            all_relationships = self._relationship_repo.list_all()
            
            for relationship in all_relationships:
                missing_entities = []
                
                # Check if source exists
                if not self._entity_exists(relationship.source_id):
                    missing_entities.append("source")
                
                # Check if target exists
                if not self._entity_exists(relationship.target_id):
                    missing_entities.append("target")
                
                if missing_entities:
                    orphaned[relationship.id] = {
                        "source_id": relationship.source_id,
                        "target_id": relationship.target_id,
                        "missing_entity": missing_entities,
                        "kind": relationship.kind.name
                    }
            
            if orphaned:
                logger.warning(f"Found {len(orphaned)} orphaned relationships")
            
            return orphaned
            
        except Exception as e:
            logger.error(f"Error finding orphaned relationships: {e}")
            raise
    
    def _entity_exists(self, entity_id: uuid.UUID) -> bool:
        """Check if an entity exists in any repository."""
        try:
            for repo in [self._actor_repo, self._institution_repo, self._policy_repo, 
                        self._resource_repo, self._process_repo, self._flow_repo]:
                if repo.read(entity_id) is not None:
                    return True
            return False
        except Exception:
            return False
    
    def _check_graph_consistency(self) -> List[Dict[str, Any]]:
        """Check for graph consistency issues."""
        violations = []
        
        try:
            # Check for duplicate entities (same label/type combination)
            duplicate_violations = self._check_duplicate_entities()
            violations.extend(duplicate_violations)
            
            # Check for circular dependencies in critical paths
            circular_violations = self._check_circular_dependencies()
            violations.extend(circular_violations)
            
            return violations
            
        except Exception as e:
            logger.error(f"Graph consistency check failed: {e}")
            return [{
                "type": "consistency_check_error",
                "message": f"Consistency check failed: {str(e)}",
                "severity": "medium"
            }]
    
    def _check_duplicate_entities(self) -> List[Dict[str, Any]]:
        """Check for potential duplicate entities."""
        violations = []
        
        try:
            # Group entities by type and label
            entity_groups = {}
            
            for repo_name, repo in [
                ("Actor", self._actor_repo),
                ("Institution", self._institution_repo),
                ("Policy", self._policy_repo),
                ("Resource", self._resource_repo)
            ]:
                entities = repo.list_all()
                for entity in entities:
                    key = (repo_name, entity.label.lower().strip())
                    if key not in entity_groups:
                        entity_groups[key] = []
                    entity_groups[key].append(entity)
            
            # Find groups with multiple entities
            for (entity_type, label), entities in entity_groups.items():
                if len(entities) > 1:
                    violations.append({
                        "type": "potential_duplicate",
                        "entity_type": entity_type,
                        "label": label,
                        "entity_ids": [str(e.id) for e in entities],
                        "count": len(entities),
                        "severity": "medium"
                    })
            
            return violations
            
        except Exception as e:
            logger.error(f"Duplicate entity check failed: {e}")
            return []
    
    def _check_circular_dependencies(self) -> List[Dict[str, Any]]:
        """Check for circular dependencies that could cause issues."""
        violations = []
        
        try:
            # Use NetworkX to detect cycles
            graph = self.get_graph()
            
            # Convert to NetworkX format for cycle detection
            nx_graph = nx.DiGraph()
            
            # Add nodes
            for node in graph:
                nx_graph.add_node(str(node.id))
            
            # Add edges (relationships)
            for rel in graph.relationships.values():
                nx_graph.add_edge(str(rel.source_id), str(rel.target_id))
            
            # Find cycles
            try:
                cycles = list(nx.simple_cycles(nx_graph))
                for cycle in cycles:
                    # Only report cycles longer than 2 nodes as potential issues
                    if len(cycle) > 2:
                        violations.append({
                            "type": "circular_dependency",
                            "cycle": cycle,
                            "length": len(cycle),
                            "severity": "low"
                        })
            except nx.NetworkXNoCycle:
                # No cycles found, which is good
                pass
            
            return violations
            
        except Exception as e:
            logger.error(f"Circular dependency check failed: {e}")
            return []
    
    def repair_orphaned_relationships(self, auto_repair: bool = False) -> Dict[str, Any]:
        """
        Repair orphaned relationships by removing them.
        
        Args:
            auto_repair: If True, automatically remove orphaned relationships
            
        Returns:
            Dictionary with repair results
        """
        try:
            orphaned = self._find_orphaned_relationships()
            
            if not orphaned:
                return {
                    "status": "success",
                    "message": "No orphaned relationships found",
                    "removed_count": 0
                }
            
            if not auto_repair:
                return {
                    "status": "found_issues",
                    "message": f"Found {len(orphaned)} orphaned relationships",
                    "orphaned_relationships": [str(rel_id) for rel_id in orphaned.keys()],
                    "action_required": "Set auto_repair=True to remove them"
                }
            
            # Remove orphaned relationships
            removed_count = 0
            with self.transaction(metadata={"operation": "repair_orphaned_relationships"}) as tx:
                for rel_id in orphaned.keys():
                    try:
                        self._relationship_repo.delete(rel_id)
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to remove orphaned relationship {rel_id}: {e}")
            
            logger.info(f"Removed {removed_count} orphaned relationships")
            return {
                "status": "success",
                "message": f"Removed {removed_count} orphaned relationships",
                "removed_count": removed_count
            }
            
        except Exception as e:
            logger.error(f"Failed to repair orphaned relationships: {e}")
            return {
                "status": "error",
                "message": f"Repair failed: {str(e)}",
                "removed_count": 0
            }


# ═══ SERVICE FACTORY & DEPENDENCY INJECTION ═══

_service_instance: Optional[SFMService] = None


def create_sfm_service(config: Optional[SFMServiceConfig] = None) -> SFMService:
    """Factory function to create SFM service instances."""
    return SFMService(config)


def get_sfm_service() -> SFMService:
    """Get singleton SFM service instance (for dependency injection)."""
    global _service_instance
    if _service_instance is None:
        _service_instance = create_sfm_service()
    return _service_instance


def reset_sfm_service():
    """Reset the singleton service instance (useful for testing)."""
    global _service_instance
    _service_instance = None


# ═══ CONVENIENCE FUNCTIONS ═══


def quick_analysis(service: SFMService) -> Dict[str, Any]:
    """
    Perform a quick analysis of an SFM graph.

    Args:
        service: SFM service instance

    Returns:
        Dictionary containing analysis results
    """
    try:
        stats = service.get_statistics()
        centrality = service.analyze_centrality(limit=5)
        health = service.get_health()

        return {
            "health": asdict(health),
            "statistics": asdict(stats),
            "top_central_nodes": centrality.most_central_nodes,
            "analysis_timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error("Quick analysis failed: %s", e, exc_info=True)
        return {"error": "An internal error occurred. Please try again later.",
                "analysis_timestamp": datetime.now().isoformat()}
