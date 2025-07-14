"""
FastAPI REST API for SFM (Social Fabric Matrix) Service

This module provides a REST API interface for the SFM framework,
exposing functionality through HTTP endpoints. 

Features:
- Full CRUD operations for all entity types
- Advanced graph analysis endpoints
- Health monitoring and diagnostics
- Comprehensive error handling
- OpenAPI/Swagger documentation
- Request/response validation
- Async support for better performance

Usage:
    uvicorn api.sfm_api:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any, Union, DefaultDict, Deque
import uuid
from datetime import datetime, timedelta
import logging
import time
from collections import defaultdict, deque

# Import SFM Service and related classes
from core.sfm_service import (
    SFMService,
    SFMServiceConfig,
    SFMError,
    SFMValidationError,
    SFMNotFoundError,
    ServiceStatus,
    ServiceHealth,
    CreateActorRequest,
    CreateInstitutionRequest,
    CreatePolicyRequest,
    CreateResourceRequest,
    CreateRelationshipRequest,
    NodeResponse,
    RelationshipResponse,
    GraphStatistics,
    CentralityAnalysis,
    PolicyImpactAnalysis,
    create_sfm_service,
    get_sfm_service,
    reset_sfm_service,
    quick_analysis,
)

# Import configuration management
from config.config_manager import get_config, SFMConfig
from config.monitoring import load_monitoring_config_from_env
from core.logging_config import configure_logging, get_logger
from core.metrics import configure_metrics, MetricConfig
from core.health_checker import get_health_checker, DatabaseHealthCheck, ServiceReadinessCheck
from core.monitoring_middleware import create_monitoring_middleware
from api.health import create_health_and_metrics_router
from core.exceptions import (
    APIError,
    APIRequestError,
    APIRateLimitError,
    SecurityValidationError,
    ErrorContext,
)

# Setup monitoring configuration first
monitoring_config = load_monitoring_config_from_env()

# Configure logging first
configure_logging(monitoring_config.logging.to_dict())

# Setup logging with monitoring
logger = get_logger(__name__)

# Setup configuration
try:
    sfm_config = get_config()
    logger.info(f"Loaded SFM configuration for environment: {sfm_config.environment}")
except Exception as e:
    logger.error(f"Failed to load SFM configuration: {e}")
    sfm_config = None

# Configure metrics
configure_metrics(MetricConfig(
    enabled=monitoring_config.metrics.enabled,
    export_port=monitoring_config.metrics.export_port,
    collection_interval=monitoring_config.metrics.collection_interval,
    prometheus_enabled=monitoring_config.metrics.prometheus_enabled
))

# Use configuration values for rate limiting
if sfm_config and sfm_config.api.rate_limit:
    # Parse rate limit string (e.g., "100/hour")
    rate_parts = sfm_config.api.rate_limit.split('/')
    if len(rate_parts) == 2:
        try:
            rate_number = int(rate_parts[0])
            rate_period = rate_parts[1]
            
            # Convert to requests per minute
            if rate_period == 'hour':
                RATE_LIMIT_REQUESTS = rate_number
                RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
            elif rate_period == 'minute':
                RATE_LIMIT_REQUESTS = rate_number
                RATE_LIMIT_WINDOW = 60
            else:
                RATE_LIMIT_REQUESTS = rate_number
                RATE_LIMIT_WINDOW = 60
        except ValueError:
            logger.warning(f"Invalid rate limit format: {sfm_config.api.rate_limit}")
            RATE_LIMIT_REQUESTS = 100
            RATE_LIMIT_WINDOW = 60
else:
    # Default rate limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60
rate_limit_storage: DefaultDict[str, Deque[float]] = defaultdict(deque)

def check_rate_limit(request: Request) -> bool:
    """
    Check if request is within rate limits.
    
    Args:
        request: FastAPI request object
        
    Returns:
        True if request is within limits
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old entries
    client_requests = rate_limit_storage[client_ip]
    while client_requests and current_time - client_requests[0] > RATE_LIMIT_WINDOW:
        client_requests.popleft()
    
    # Check if limit exceeded
    if len(client_requests) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per minute allowed.",
            headers={"Retry-After": "60"}
        )
    
    # Add current request
    client_requests.append(current_time)
    return True

def rate_limit_dependency(request: Request) -> bool:
    """FastAPI dependency for rate limiting."""
    return check_rate_limit(request)

# FastAPI app configuration
app = FastAPI(
    title="SFM (Social Fabric Matrix) API",
    description="REST API for Social Fabric Matrix framework - analyze complex social, economic, and environmental networks",
    version=sfm_config.version if sfm_config else "1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=sfm_config.debug if sfm_config else False
)

# CORS middleware configuration from config
cors_origins = ["*"]  # Default
if sfm_config and sfm_config.api.cors_origins:
    cors_origins = sfm_config.api.cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add monitoring middleware using FastAPI's middleware approach
from core.monitoring_middleware import MonitoringMiddleware
app.add_middleware(MonitoringMiddleware, config=monitoring_config.middleware.to_dict())

# Add health and metrics routes
health_metrics_router = create_health_and_metrics_router()
app.include_router(health_metrics_router)

# ═══ DEPENDENCY INJECTION ═══

def get_sfm_service_dependency() -> SFMService:
    """Dependency injection for SFM service."""
    return get_sfm_service()

# ═══ ERROR HANDLERS ═══

@app.exception_handler(SFMValidationError)
async def validation_error_handler(request, exc: SFMValidationError):
    """Handle validation errors with enhanced context."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "message": exc.message,
            "error_code": exc.error_code.value,
            "details": exc.details,
            "context": exc.context.to_dict(),
            "remediation": exc.remediation,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(SecurityValidationError)
async def security_validation_error_handler(request, exc: SecurityValidationError):
    """Handle security validation errors with enhanced context."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Security Validation Error",
            "message": exc.message,
            "error_code": exc.error_code.value,
            "details": exc.details,
            "context": exc.context.to_dict(),
            "remediation": exc.remediation,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(SFMNotFoundError)
async def not_found_error_handler(request, exc: SFMNotFoundError):
    """Handle not found errors with enhanced context."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": exc.message,
            "error_code": exc.error_code.value,
            "details": exc.details,
            "context": exc.context.to_dict(),
            "remediation": exc.remediation,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(SFMError)
async def sfm_service_error_handler(request, exc: SFMError):
    """Handle general SFM service errors with enhanced context."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Service Error",
            "message": exc.message,
            "error_code": exc.error_code.value,
            "details": exc.details,
            "context": exc.context.to_dict(),
            "remediation": exc.remediation,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(APIRateLimitError)
async def rate_limit_error_handler(request, exc: APIRateLimitError):
    """Handle rate limit errors."""
    return JSONResponse(
        status_code=exc.http_status_code,
        content={
            "error": "Rate Limit Exceeded",
            "message": exc.message,
            "error_code": exc.error_code.value,
            "details": exc.details,
            "context": exc.context.to_dict(),
            "remediation": exc.remediation,
            "timestamp": datetime.now().isoformat()
        },
        headers={"Retry-After": "60"}
    )

@app.exception_handler(APIRequestError)
async def api_request_error_handler(request, exc: APIRequestError):
    """Handle API request errors."""
    return JSONResponse(
        status_code=exc.http_status_code,
        content={
            "error": "Request Error",
            "message": exc.message,
            "error_code": exc.error_code.value,
            "details": exc.details,
            "context": exc.context.to_dict(),
            "remediation": exc.remediation,
            "timestamp": datetime.now().isoformat()
        }
    )

# ═══ HEALTH & STATUS ENDPOINTS ═══

@app.get("/health", response_model=ServiceHealth, tags=["Health"])
async def get_health(service: SFMService = Depends(get_sfm_service_dependency)):
    """
    Get service health status.
    
    Returns comprehensive health information including:
    - Service status (healthy/degraded/error)
    - Node and relationship counts
    - Backend information
    - Last operation performed
    """
    return service.get_health()

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "SFM (Social Fabric Matrix) API",
        "version": "1.0.0",
        "description": "REST API for analyzing complex social, economic, and environmental networks",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.now().isoformat()
    }

# ═══ STATISTICS & ANALYTICS ═══

@app.get("/statistics", response_model=GraphStatistics, tags=["Analytics"])
async def get_statistics(service: SFMService = Depends(get_sfm_service_dependency)):
    """
    Get comprehensive graph statistics.
    
    Returns:
    - Total node and relationship counts
    - Breakdown by entity types
    - Relationship distribution by kind
    """
    return service.get_statistics()

@app.get("/analytics/quick", tags=["Analytics"])
async def get_quick_analysis(service: SFMService = Depends(get_sfm_service_dependency)) -> Dict[str, Any]:
    """
    Perform a quick analysis of the entire graph.
    
    Returns summary statistics, health status, and top central nodes.
    """
    result = quick_analysis(service)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.get("/analytics/centrality", response_model=CentralityAnalysis, tags=["Analytics"])
async def analyze_centrality(
    centrality_type: str = Query("betweenness", description="Type of centrality analysis"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of nodes to return"),
    service: SFMService = Depends(get_sfm_service_dependency)
):
    """
    Perform centrality analysis on the network.
    
    Supported centrality types:
    - betweenness: Identifies nodes that act as bridges
    - closeness: Identifies nodes with shortest paths to all others
    - degree: Identifies nodes with most connections
    - eigenvector: Identifies nodes connected to important nodes
    """
    return service.analyze_centrality(centrality_type, limit)

@app.get("/analytics/policy-impact/{policy_id}", response_model=PolicyImpactAnalysis, tags=["Analytics"])
async def analyze_policy_impact(
    policy_id: str = Path(..., description="UUID of the policy to analyze"),
    impact_radius: int = Query(3, ge=1, le=10, description="Radius of impact analysis"),
    service: SFMService = Depends(get_sfm_service_dependency)
):
    """
    Analyze the potential impact of a policy intervention.
    
    Returns:
    - Total affected nodes within the impact radius
    - Breakdown of affected entities by type
    - Network metrics for the impact area
    """
    return service.analyze_policy_impact(policy_id, impact_radius)

@app.get("/analytics/shortest-path", tags=["Analytics"])
async def find_shortest_path(
    source_id: str = Query(..., description="UUID of the source node"),
    target_id: str = Query(..., description="UUID of the target node"),
    relationship_kinds: Optional[List[str]] = Query(None, description="Filter by relationship kinds"),
    service: SFMService = Depends(get_sfm_service_dependency)
) -> Dict[str, Any]:
    """
    Find the shortest path between two nodes.
    
    Returns the path as a list of node IDs, or null if no path exists.
    """
    path = service.find_shortest_path(source_id, target_id, relationship_kinds)
    return {
        "source_id": source_id,
        "target_id": target_id,
        "path": path,
        "path_length": len(path) if path else 0,
        "timestamp": datetime.now().isoformat()
    }

# ═══ ACTOR ENDPOINTS ═══

@app.post("/actors", response_model=NodeResponse, status_code=status.HTTP_201_CREATED, tags=["Actors"])
async def create_actor(
    request: CreateActorRequest,
    service: SFMService = Depends(get_sfm_service_dependency),
    _: bool = Depends(rate_limit_dependency)
):
    """
    Create a new actor entity with input validation and rate limiting.
    
    Actors represent organizations, individuals, or groups that can take actions
    within the social fabric matrix.
    """
    return service.create_actor(request)

@app.get("/actors/{actor_id}", response_model=NodeResponse, tags=["Actors"])
async def get_actor(
    actor_id: str = Path(..., description="UUID of the actor"),
    service: SFMService = Depends(get_sfm_service_dependency)
):
    """Get a specific actor by ID."""
    try:
        actor_uuid = uuid.UUID(actor_id)
        actor = service.get_actor(actor_uuid)
        if not actor:
            raise HTTPException(status_code=404, detail=f"Actor {actor_id} not found")
        return service._node_to_response(actor)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

@app.get("/actors/{actor_id}/neighbors", tags=["Actors"])
async def get_actor_neighbors(
    actor_id: str = Path(..., description="UUID of the actor"),
    relationship_kinds: Optional[List[str]] = Query(None, description="Filter by relationship kinds"),
    distance: int = Query(1, ge=1, le=5, description="Distance/hops to search"),
    service: SFMService = Depends(get_sfm_service_dependency)
) -> Dict[str, Any]:
    """Get neighboring nodes for a specific actor."""
    neighbors = service.get_node_neighbors(actor_id, relationship_kinds, distance)
    return {
        "actor_id": actor_id,
        "neighbors": neighbors,
        "neighbor_count": len(neighbors),
        "distance": distance,
        "relationship_kinds": relationship_kinds
    }

# ═══ INSTITUTION ENDPOINTS ═══

@app.post("/institutions", response_model=NodeResponse, status_code=status.HTTP_201_CREATED, tags=["Institutions"])
async def create_institution(
    request: CreateInstitutionRequest,
    service: SFMService = Depends(get_sfm_service_dependency),
    _: bool = Depends(rate_limit_dependency)
):
    """
    Create a new institution entity with input validation and rate limiting.
    
    Institutions represent formal structures, rules, and norms that govern
    behavior within the social fabric matrix.
    """
    return service.create_institution(request)

@app.get("/institutions/{institution_id}", response_model=NodeResponse, tags=["Institutions"])
async def get_institution(
    institution_id: str = Path(..., description="UUID of the institution"),
    service: SFMService = Depends(get_sfm_service_dependency)
):
    """Get a specific institution by ID."""
    try:
        institution_uuid = uuid.UUID(institution_id)
        institution = service.get_institution(institution_uuid)
        if not institution:
            raise HTTPException(status_code=404, detail=f"Institution {institution_id} not found")
        return service._node_to_response(institution)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

# ═══ POLICY ENDPOINTS ═══

@app.post("/policies", response_model=NodeResponse, status_code=status.HTTP_201_CREATED, tags=["Policies"])
async def create_policy(
    request: CreatePolicyRequest,
    service: SFMService = Depends(get_sfm_service_dependency)
):
    """
    Create a new policy entity.
    
    Policies represent rules, regulations, and interventions that can
    influence the behavior of other entities in the network.
    """
    return service.create_policy(request)

@app.get("/policies/{policy_id}", response_model=NodeResponse, tags=["Policies"])
async def get_policy(
    policy_id: str = Path(..., description="UUID of the policy"),
    service: SFMService = Depends(get_sfm_service_dependency)
):
    """Get a specific policy by ID."""
    try:
        policy_uuid = uuid.UUID(policy_id)
        policy = service.get_policy(policy_uuid)
        if not policy:
            raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
        return service._node_to_response(policy)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

# ═══ RESOURCE ENDPOINTS ═══

@app.post("/resources", response_model=NodeResponse, status_code=status.HTTP_201_CREATED, tags=["Resources"])
async def create_resource(
    request: CreateResourceRequest,
    service: SFMService = Depends(get_sfm_service_dependency)
):
    """
    Create a new resource entity.
    
    Resources represent natural, human, financial, or information assets
    that flow through the social fabric matrix.
    """
    return service.create_resource(request)

@app.get("/resources/{resource_id}", response_model=NodeResponse, tags=["Resources"])
async def get_resource(
    resource_id: str = Path(..., description="UUID of the resource"),
    service: SFMService = Depends(get_sfm_service_dependency)
):
    """Get a specific resource by ID."""
    try:
        resource_uuid = uuid.UUID(resource_id)
        resource = service.get_resource(resource_uuid)
        if not resource:
            raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")
        return service._node_to_response(resource)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

# ═══ RELATIONSHIP ENDPOINTS ═══

@app.post("/relationships", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED, tags=["Relationships"])
async def create_relationship(
    request: CreateRelationshipRequest,
    service: SFMService = Depends(get_sfm_service_dependency)
):
    """
    Create a new relationship between two entities.
    
    Relationships define how entities interact, influence, or connect
    with each other in the social fabric matrix.
    """
    return service.create_relationship(request)

@app.get("/relationships/{relationship_id}", response_model=RelationshipResponse, tags=["Relationships"])
async def get_relationship(
    relationship_id: str = Path(..., description="UUID of the relationship"),
    service: SFMService = Depends(get_sfm_service_dependency)
) -> RelationshipResponse:
    """Get a specific relationship by ID."""
    relationship = service.get_relationship(relationship_id)
    if not relationship:
        raise HTTPException(status_code=404, detail=f"Relationship {relationship_id} not found")
    return relationship

@app.post("/relationships/connect", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED, tags=["Relationships"])
async def connect_entities(
    source_id: str = Body(..., description="UUID of the source entity"),
    target_id: str = Body(..., description="UUID of the target entity"),
    kind: str = Body(..., description="Type of relationship"),
    weight: float = Body(1.0, description="Strength of the relationship"),
    meta: Optional[Dict[str, str]] = Body(None, description="Additional metadata"),
    service: SFMService = Depends(get_sfm_service_dependency)
) -> RelationshipResponse:
    """
    Convenience endpoint to connect two entities.
    
    Alternative to the full relationship creation endpoint with simpler parameters.
    """
    return service.connect(source_id, target_id, kind, weight, meta=meta or {})

# ═══ LISTING ENDPOINTS ═══

@app.get("/nodes", response_model=List[NodeResponse], tags=["Listing"])
async def list_nodes(
    node_type: Optional[str] = Query(None, description="Filter by node type (Actor, Institution, Policy, Resource)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of nodes to return"),
    offset: int = Query(0, ge=0, description="Number of nodes to skip"),
    service: SFMService = Depends(get_sfm_service_dependency)
) -> List[NodeResponse]:
    """
    List all nodes with optional filtering and pagination.
    
    Supports filtering by node type and pagination for large graphs.
    """
    return service.list_nodes(node_type, limit, offset)

@app.get("/relationships", response_model=List[RelationshipResponse], tags=["Listing"])
async def list_relationships(
    kind: Optional[str] = Query(None, description="Filter by relationship kind"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of relationships to return"),
    offset: int = Query(0, ge=0, description="Number of relationships to skip"),
    service: SFMService = Depends(get_sfm_service_dependency)
) -> List[RelationshipResponse]:
    """
    List all relationships with optional filtering and pagination.
    
    Supports filtering by relationship kind and pagination for large graphs.
    """
    return service.list_relationships(kind, limit, offset)

# ═══ BULK OPERATIONS ═══

@app.post("/actors/bulk", response_model=List[NodeResponse], tags=["Bulk Operations"])
async def bulk_create_actors(
    requests: List[CreateActorRequest],
    service: SFMService = Depends(get_sfm_service_dependency)
) -> List[NodeResponse]:
    """
    Create multiple actors in a single batch operation.
    
    More efficient than individual requests for creating many entities.
    """
    return service.bulk_create_actors(requests)

# ═══ SYSTEM MANAGEMENT ═══

@app.delete("/system/clear", tags=["System Management"])
async def clear_all_data(
    confirm: bool = Query(..., description="Confirmation flag - must be true"),
    service: SFMService = Depends(get_sfm_service_dependency)
) -> Dict[str, Any]:
    """
    Clear all data from the system.
    
    ⚠️ WARNING: This operation is irreversible and will delete all entities and relationships.
    Requires explicit confirmation.
    """
    if not confirm:
        raise HTTPException(
            status_code=400, 
            detail="Must provide confirm=true to clear all data"
        )
    
    return service.clear_all_data()

@app.post("/system/reset", tags=["System Management"])
async def reset_service() -> Dict[str, str]:
    """
    Reset the service singleton instance.
    
    Useful for testing or reinitializing the service with different configuration.
    """
    reset_sfm_service()
    return {
        "status": "success",
        "message": "Service instance reset",
        "timestamp": datetime.now().isoformat()
    }

# ═══ CONFIGURATION ═══

@app.get("/config", tags=["Configuration"])
async def get_configuration(service: SFMService = Depends(get_sfm_service_dependency)) -> Dict[str, Any]:
    """Get current service configuration."""
    config = service.config
    return {
        "storage_backend": config.storage_backend,
        "auto_sync": config.auto_sync,
        "validation_enabled": config.validation_enabled,
        "cache_queries": config.cache_queries,
        "enable_logging": config.enable_logging,
        "log_level": config.log_level,
        "max_graph_size": config.max_graph_size,
        "query_timeout": config.query_timeout
    }

# ═══ METADATA & DOCUMENTATION ═══

@app.get("/metadata/entity-types", tags=["Metadata"])
async def get_entity_types() -> Dict[str, Any]:
    """Get information about available entity types and their properties."""
    return {
        "entity_types": {
            "Actor": {
                "description": "Organizations, individuals, or groups that can take actions",
                "properties": ["name", "description", "sector", "legal_form", "meta"]
            },
            "Institution": {
                "description": "Formal structures, rules, and norms that govern behavior",
                "properties": ["name", "description", "meta"]
            },
            "Policy": {
                "description": "Rules, regulations, and interventions",
                "properties": ["name", "description", "authority", "target_sectors", "enforcement", "meta"]
            },
            "Resource": {
                "description": "Natural, human, financial, or information assets",
                "properties": ["name", "description", "rtype", "unit", "meta"]
            }
        },
        "relationship_kinds": [
            "GOVERNS", "INFLUENCES", "AFFECTS", "REGULATES", "COLLABORATES", 
            "COMPETES", "DEPENDS_ON", "FLOWS_TO", "IMPLEMENTS", "SUPPORTS"
        ],
        "resource_types": [
            "NATURAL", "HUMAN", "FINANCIAL", "INFORMATION", "INFRASTRUCTURE",
            "SOCIAL", "POLITICAL", "TECHNOLOGICAL"
        ]
    }

@app.get("/metadata/api-info", tags=["Metadata"])
async def get_api_info() -> Dict[str, Any]:
    """Get comprehensive API information and usage guidelines."""
    return {
        "api_version": "1.0.0",
        "framework": "FastAPI",
        "description": "REST API for Social Fabric Matrix framework",
        "features": [
            "Full CRUD operations for all entity types",
            "Advanced graph analysis and centrality calculations",
            "Policy impact analysis",
            "Shortest path finding",
            "Bulk operations",
            "Health monitoring",
            "Comprehensive error handling"
        ],
        "endpoints": {
            "health": "/health",
            "documentation": "/docs",
            "openapi_spec": "/openapi.json",
            "entities": ["/actors", "/institutions", "/policies", "/resources"],
            "relationships": "/relationships",
            "analytics": ["/analytics/centrality", "/analytics/policy-impact", "/analytics/shortest-path"],
            "bulk_operations": ["/actors/bulk"],
            "system": ["/system/clear", "/system/reset"]
        },
        "authentication": "None (configure as needed for production)",
        "rate_limiting": "None (configure as needed for production)",
        "timestamp": datetime.now().isoformat()
    }

# ═══ STARTUP EVENT ═══

# ═══ CONFIGURATION ENDPOINTS ═══

@app.get("/config/status", response_model=Dict[str, Any])
async def get_config_status():
    """Get configuration status and overview."""
    try:
        if sfm_config:
            # Create a safe view of configuration (no secrets)
            config_status = {
                "environment": sfm_config.environment,
                "debug": sfm_config.debug,
                "version": sfm_config.version,
                "database": {
                    "host": sfm_config.database.host,
                    "port": sfm_config.database.port,
                    "name": sfm_config.database.name,
                    "pool_size": sfm_config.database.pool_size,
                    "ssl_mode": sfm_config.database.ssl_mode
                },
                "cache": {
                    "backend": sfm_config.cache.backend,
                    "host": sfm_config.cache.host,
                    "port": sfm_config.cache.port,
                    "ttl": sfm_config.cache.ttl
                },
                "api": {
                    "host": sfm_config.api.host,
                    "port": sfm_config.api.port,
                    "debug": sfm_config.api.debug,
                    "rate_limit": sfm_config.api.rate_limit,
                    "cors_origins": sfm_config.api.cors_origins[:5] if len(sfm_config.api.cors_origins) > 5 else sfm_config.api.cors_origins  # Limit for security
                },
                "logging": {
                    "level": sfm_config.logging.level,
                    "format": sfm_config.logging.format,
                    "console_enabled": sfm_config.logging.console_enabled,
                    "file_enabled": sfm_config.logging.file_enabled
                },
                "security": {
                    "encryption_enabled": sfm_config.security.encryption_enabled,
                    "audit_enabled": sfm_config.security.audit_enabled,
                    "session_timeout": sfm_config.security.session_timeout
                }
            }
            return {
                "status": "loaded",
                "config": config_status,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "not_loaded",
                "message": "Configuration not loaded - using defaults",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error getting configuration status: {e}")
        return {
            "status": "error",
            "message": "An internal error occurred while fetching the configuration status.",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/config/reload")
async def reload_config():
    """Reload configuration from sources."""
    try:
        from config.config_manager import reload_config
        
        # Reload configuration
        new_config = reload_config()
        
        # Update global reference
        global sfm_config
        sfm_config = new_config
        
        logger.info("Configuration reloaded successfully")
        return {
            "status": "success",
            "message": "Configuration reloaded successfully",
            "environment": new_config.environment,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error reloading configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while reloading the configuration."
        )

# ═══ STARTUP/SHUTDOWN EVENTS ═══

@app.on_event("startup")
async def startup_event() -> None:
    """Initialize the service on startup."""
    logger.info("SFM API starting up...")
    
    # Log configuration status
    if sfm_config:
        logger.info(f"Configuration loaded - Environment: {sfm_config.environment}")
        logger.info(f"API will run on {sfm_config.api.host}:{sfm_config.api.port}")
        logger.info(f"Database: {sfm_config.database.host}:{sfm_config.database.port}")
        logger.info(f"Cache: {sfm_config.cache.backend}")
    else:
        logger.warning("No configuration loaded - using defaults")
    
    # Initialize the service
    service = get_sfm_service()
    health = service.get_health()
    
    # Initialize health checks
    health_checker = get_health_checker()
    
    # Add service-specific health checks
    health_checker.add_check(
        ServiceReadinessCheck(lambda: service),
        include_in_startup=True,
        include_in_liveness=True,
        include_in_readiness=True
    )
    
    logger.info(f"SFM API ready - Backend: {health.backend}, Status: {health.status.value}")
    logger.info("Monitoring and health checks initialized")

@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    logger.info("SFM API shutting down...")
    # Add any cleanup logic here

if __name__ == "__main__":
    import uvicorn
    
    # Use configuration values if available
    if sfm_config:
        host = sfm_config.api.host
        port = sfm_config.api.port
        debug = sfm_config.api.debug
        
        logger.info(f"Starting SFM API server on {host}:{port} (debug={debug})")
        uvicorn.run(
            app, 
            host=host, 
            port=port, 
            reload=debug,
            log_level="info" if sfm_config.logging.level == "INFO" else "debug"
        )
    else:
        logger.info("Starting SFM API server with defaults")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
