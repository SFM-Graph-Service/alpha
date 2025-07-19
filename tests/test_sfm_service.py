#type: ignore    # On the fence about strict type checking and member access for the mocks
#  This module provides comprehensive testing for the SFMService class and related
"""
Unit and Integration Tests for SFM Service

This module provides comprehensive testing for the SFMService class and related components
including data transfer objects, service configuration, error handling, and all CRUD operations.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import uuid
from datetime import datetime
from typing import Dict, List, Any
import json

# Import the classes under test
from api.sfm_service import (
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

# Import dependencies for testing
from models import (
    Actor,
    Institution,
    Policy,
    Resource,
    Relationship,
)
from models.sfm_enums import ResourceType,RelationshipKind
from data.repositories import SFMRepositoryFactory

# Import centralized mock infrastructure
from tests.mocks import (
    MockRepositoryFactory,
    MockStorageBackend,
    create_mock_graph,
    create_sample_nodes
)

# Disable rate limiting globally for all tests
from infrastructure.security_validators import disable_validation_rate_limiting, clear_validation_rate_limit_storage
disable_validation_rate_limiting()
clear_validation_rate_limit_storage()


class TestDataTransferObjects(unittest.TestCase):
    """Test data transfer objects (DTOs) and request/response models."""

    def test_create_actor_request(self):
        """Test CreateActorRequest creation and validation."""
        request = CreateActorRequest(
            name="Test Actor",
            description="Test description",
            sector="government",
            legal_form="agency",
            meta={"key": "value"}
        )
        
        self.assertEqual(request.name, "Test Actor")
        self.assertEqual(request.description, "Test description")
        self.assertEqual(request.sector, "government")
        self.assertEqual(request.legal_form, "agency")
        self.assertEqual(request.meta, {"key": "value"})

    def test_create_institution_request(self):
        """Test CreateInstitutionRequest creation."""
        request = CreateInstitutionRequest(
            name="Test Institution",
            description="Test description",
            meta={"type": "regulatory"}
        )
        
        self.assertEqual(request.name, "Test Institution")
        self.assertEqual(request.description, "Test description")
        self.assertEqual(request.meta, {"type": "regulatory"})

    def test_create_policy_request(self):
        """Test CreatePolicyRequest creation."""
        request = CreatePolicyRequest(
            name="Test Policy",
            description="Test description",
            authority="EPA",
            target_sectors=["agriculture", "energy"],
            enforcement=0.8,
            meta={"priority": "high"}
        )
        
        self.assertEqual(request.name, "Test Policy")
        self.assertEqual(request.authority, "EPA")
        self.assertEqual(request.target_sectors, ["agriculture", "energy"])
        self.assertEqual(request.enforcement, 0.8)

    def test_create_resource_request(self):
        """Test CreateResourceRequest creation."""
        request = CreateResourceRequest(
            name="Test Resource",
            description="Test description",
            rtype="NATURAL",
            unit="tons",
            meta={"renewable": "true"}
        )
        
        self.assertEqual(request.name, "Test Resource")
        self.assertEqual(request.rtype, "NATURAL")
        self.assertEqual(request.unit, "tons")

    def test_create_relationship_request(self):
        """Test CreateRelationshipRequest creation."""
        source_id = str(uuid.uuid4())
        target_id = str(uuid.uuid4())
        
        request = CreateRelationshipRequest(
            source_id=source_id,
            target_id=target_id,
            kind="GOVERNS",
            weight=0.7,
            meta={"strength": "strong"}
        )
        
        self.assertEqual(request.source_id, source_id)
        self.assertEqual(request.target_id, target_id)
        self.assertEqual(request.kind, "GOVERNS")
        self.assertEqual(request.weight, 0.7)

    def test_node_response(self):
        """Test NodeResponse creation."""
        node_id = str(uuid.uuid4())
        response = NodeResponse(
            id=node_id,
            label="Test Node",
            description="Test description",
            node_type="Actor",
            meta={"sector": "public"},
            created_at="2025-06-26T10:00:00"
        )
        
        self.assertEqual(response.id, node_id)
        self.assertEqual(response.label, "Test Node")
        self.assertEqual(response.node_type, "Actor")

    def test_relationship_response(self):
        """Test RelationshipResponse creation."""
        rel_id = str(uuid.uuid4())
        source_id = str(uuid.uuid4())
        target_id = str(uuid.uuid4())
        
        response = RelationshipResponse(
            id=rel_id,
            source_id=source_id,
            target_id=target_id,
            kind="GOVERNS",
            weight=0.8,
            meta={"type": "direct"}
        )
        
        self.assertEqual(response.id, rel_id)
        self.assertEqual(response.source_id, source_id)
        self.assertEqual(response.target_id, target_id)
        self.assertEqual(response.kind, "GOVERNS")

    def test_graph_statistics(self):
        """Test GraphStatistics creation."""
        stats = GraphStatistics(
            total_nodes=100,
            total_relationships=250,
            node_types={"Actor": 30, "Institution": 20, "Policy": 50},
            relationship_kinds={"GOVERNS": 100, "INFLUENCES": 150},
            timestamp="2025-06-26T10:00:00"
        )
        
        self.assertEqual(stats.total_nodes, 100)
        self.assertEqual(stats.total_relationships, 250)
        self.assertIn("Actor", stats.node_types)

    def test_centrality_analysis(self):
        """Test CentralityAnalysis creation."""
        analysis = CentralityAnalysis(
            node_centrality={"node1": 0.8, "node2": 0.6},
            most_central_nodes=[("node1", 0.8), ("node2", 0.6)],
            analysis_type="betweenness",
            timestamp="2025-06-26T10:00:00"
        )
        
        self.assertEqual(analysis.analysis_type, "betweenness")
        self.assertEqual(len(analysis.most_central_nodes), 2)

    def test_policy_impact_analysis(self):
        """Test PolicyImpactAnalysis creation."""
        policy_id = str(uuid.uuid4())
        analysis = PolicyImpactAnalysis(
            policy_id=policy_id,
            total_affected_nodes=15,
            affected_actors=["actor1", "actor2"],
            affected_institutions=["inst1"],
            affected_resources=["res1", "res2"],
            network_metrics={"density": 0.3},
            impact_radius=3
        )
        
        self.assertEqual(analysis.policy_id, policy_id)
        self.assertEqual(analysis.total_affected_nodes, 15)
        self.assertEqual(analysis.impact_radius, 3)


class TestSFMServiceConfig(unittest.TestCase):
    """Test SFM Service configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SFMServiceConfig()
        
        self.assertEqual(config.storage_backend, "networkx")
        self.assertTrue(config.auto_sync)
        self.assertTrue(config.validation_enabled)
        self.assertTrue(config.cache_queries)
        self.assertTrue(config.enable_logging)
        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.max_graph_size, 10000)
        self.assertEqual(config.query_timeout, 30)

    def test_custom_config(self):
        """Test custom configuration values."""
        config = SFMServiceConfig(
            storage_backend="postgres",
            auto_sync=False,
            validation_enabled=False,
            max_graph_size=5000,
            log_level="DEBUG"
        )
        
        self.assertEqual(config.storage_backend, "postgres")
        self.assertFalse(config.auto_sync)
        self.assertFalse(config.validation_enabled)
        self.assertEqual(config.max_graph_size, 5000)
        self.assertEqual(config.log_level, "DEBUG")


class TestSFMServiceErrors(unittest.TestCase):
    """Test custom exception classes."""

    def test_sfm_service_error(self):
        """Test SFMError creation."""
        error = SFMError(
            "Test error message",
            "TEST_ERROR",
            details={"field": "value"}
        )
        
        self.assertEqual(error.message, "Test error message")
        self.assertEqual(error.error_code.value, "SFM_ERROR")
        self.assertEqual(error.details, {"field": "value"})
        self.assertEqual(str(error), "Test error message")

    def test_validation_error(self):
        """Test SFMValidationError creation."""
        error = SFMValidationError("Invalid field", "name", "")
        
        self.assertEqual(error.message, "Invalid field")
        self.assertEqual(error.error_code.value, "VALIDATION_ERROR")
        self.assertEqual(error.details["field"], "name")
        self.assertEqual(error.details["value"], "")

    def test_not_found_error(self):
        """Test SFMNotFoundError creation."""
        entity_id = str(uuid.uuid4())
        error = SFMNotFoundError("Actor", entity_id)
        
        self.assertIn("not found", error.message)
        self.assertEqual(error.error_code.value, "NOT_FOUND_ERROR")
        self.assertEqual(error.details["entity_type"], "Actor")
        self.assertEqual(error.details["entity_id"], entity_id)


class TestServiceHealth(unittest.TestCase):
    """Test service health and status components."""

    def test_service_status_enum(self):
        """Test ServiceStatus enum values."""
        self.assertEqual(ServiceStatus.HEALTHY.value, "healthy")
        self.assertEqual(ServiceStatus.DEGRADED.value, "degraded")
        self.assertEqual(ServiceStatus.ERROR.value, "error")

    def test_service_health_creation(self):
        """Test ServiceHealth creation."""
        health = ServiceHealth(
            status=ServiceStatus.HEALTHY,
            timestamp="2025-06-26T10:00:00",
            version="1.0.0",
            backend="networkx",
            node_count=100,
            relationship_count=200,
            last_operation="create_actor"
        )
        
        self.assertEqual(health.status, ServiceStatus.HEALTHY)
        self.assertEqual(health.version, "1.0.0")
        self.assertEqual(health.backend, "networkx")
        self.assertEqual(health.node_count, 100)
        self.assertEqual(health.relationship_count, 200)


class TestSFMServiceUnit(unittest.TestCase):
    """Unit tests for SFMService class methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = SFMServiceConfig(validation_enabled=True)
        self.service = SFMService(self.config)
        
        # Mock the repositories
        self.service._base_repo = Mock()
        self.service._actor_repo = Mock()
        self.service._institution_repo = Mock()
        self.service._policy_repo = Mock()
        self.service._resource_repo = Mock()
        self.service._relationship_repo = Mock()
        self.service._process_repo = Mock()
        self.service._flow_repo = Mock()

    def test_service_initialization(self):
        """Test service initialization with config."""
        self.assertEqual(self.service.config, self.config)
        self.assertIsNotNone(self.service._actor_repo)
        self.assertIsNotNone(self.service._institution_repo)
        self.assertTrue(self.service._cache_dirty)

    def test_convert_to_resource_type_valid(self):
        """Test valid resource type conversion."""
        result = self.service._convert_to_resource_type("NATURAL")
        self.assertEqual(result, ResourceType.NATURAL)
        
        result = self.service._convert_to_resource_type("natural")
        self.assertEqual(result, ResourceType.NATURAL)

    def test_convert_to_resource_type_invalid(self):
        """Test invalid resource type conversion."""
        with self.assertRaises(SFMValidationError) as context:
            self.service._convert_to_resource_type("INVALID_TYPE")
        
        self.assertIn("Invalid resource type", str(context.exception))

    def test_convert_to_relationship_kind_valid(self):
        """Test valid relationship kind conversion."""
        result = self.service._convert_to_relationship_kind("GOVERNS")
        self.assertEqual(result, RelationshipKind.GOVERNS)

    def test_convert_to_relationship_kind_invalid(self):
        """Test invalid relationship kind conversion falls back to AFFECTS."""
        result = self.service._convert_to_relationship_kind("INVALID_KIND")
        self.assertEqual(result, RelationshipKind.AFFECTS)

    def test_mark_dirty(self):
        """Test cache dirty marking."""
        self.service._cache_dirty = False
        self.service._mark_dirty("test_operation")
        
        self.assertTrue(self.service._cache_dirty)
        self.assertEqual(self.service._last_operation, "test_operation")

    def test_node_to_response_conversion(self):
        """Test node to response conversion."""
        actor = Actor(label="Test Actor", description="Test description")
        actor.meta = {"sector": "public"}
        
        response = self.service._node_to_response(actor)
        
        self.assertEqual(response.label, "Test Actor")
        self.assertEqual(response.description, "Test description")
        self.assertEqual(response.node_type, "Actor")
        self.assertEqual(response.meta, {"sector": "public"})

    def test_relationship_to_response_conversion(self):
        """Test relationship to response conversion."""
        source_id = uuid.uuid4()
        target_id = uuid.uuid4()
        
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            kind=RelationshipKind.GOVERNS,
            weight=0.8
        )
        relationship.meta = {"type": "direct"}
        
        response = self.service._relationship_to_response(relationship)
        
        self.assertEqual(response.source_id, str(source_id))
        self.assertEqual(response.target_id, str(target_id))
        self.assertEqual(response.kind, "GOVERNS")
        self.assertEqual(response.weight, 0.8)

    @patch('api.sfm_service.datetime')
    def test_get_health_success(self, mock_datetime):
        """Test successful health check."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-06-26T10:00:00"
        
        # Mock get_statistics to return valid data
        mock_stats = GraphStatistics(
            total_nodes=10,
            total_relationships=20,
            node_types={},
            relationship_kinds={},
            timestamp="2025-06-26T10:00:00"
        )
        self.service.get_statistics = Mock(return_value=mock_stats)
        
        health = self.service.get_health()
        
        self.assertEqual(health.status, ServiceStatus.HEALTHY)
        self.assertEqual(health.node_count, 10)
        self.assertEqual(health.relationship_count, 20)

    def test_get_health_error(self):
        """Test health check with error."""
        # Mock get_statistics to raise an exception
        self.service.get_statistics = Mock(side_effect=Exception("Test error"))
        
        health = self.service.get_health()
        
        self.assertEqual(health.status, ServiceStatus.ERROR)

    def test_create_actor_with_request_object(self):
        """Test creating actor with request object."""
        request = CreateActorRequest(
            name="Test Actor",
            description="Test description",
            sector="government"
        )
        
        mock_actor = Actor(label="Test Actor", sector="government")
        self.service._actor_repo.create.return_value = mock_actor
        
        response = self.service.create_actor(request)
        
        self.service._actor_repo.create.assert_called_once()
        self.assertEqual(response.label, "Test Actor")
        self.assertEqual(response.node_type, "Actor")

    def test_create_actor_with_dict(self):
        """Test creating actor with dictionary."""
        request_dict = {
            "name": "Test Actor",
            "description": "Test description",
            "sector": "government"
        }
        
        mock_actor = Actor(label="Test Actor", sector="government")
        self.service._actor_repo.create.return_value = mock_actor
        
        response = self.service.create_actor(request_dict)
        
        self.service._actor_repo.create.assert_called_once()
        self.assertEqual(response.label, "Test Actor")

    def test_create_actor_validation_error(self):
        """Test actor creation with validation error."""
        request = CreateActorRequest(name="")  # Empty name should fail validation
        
        with self.assertRaises((SFMValidationError, SFMError)) as context:
            self.service.create_actor(request)
        
        self.assertIn("label", str(context.exception).lower())

    def test_create_actor_repository_error(self):
        """Test actor creation with repository error."""
        request = CreateActorRequest(name="Test Actor")
        self.service._actor_repo.create.side_effect = Exception("Database error")
        
        with self.assertRaises(SFMError) as context:
            self.service.create_actor(request)
        
        self.assertEqual(context.exception.error_code.value, "CREATE_ACTOR_FAILED")

    def test_create_institution_success(self):
        """Test successful institution creation."""
        request = CreateInstitutionRequest(name="Test Institution")
        
        mock_institution = Institution(label="Test Institution")
        self.service._institution_repo.create.return_value = mock_institution
        
        response = self.service.create_institution(request)
        
        self.service._institution_repo.create.assert_called_once()
        self.assertEqual(response.label, "Test Institution")
        self.assertEqual(response.node_type, "Institution")

    def test_create_policy_success(self):
        """Test successful policy creation."""
        request = CreatePolicyRequest(
            name="Test Policy",
            authority="EPA",
            enforcement=0.8
        )
        
        mock_policy = Policy(label="Test Policy", authority="EPA", enforcement=0.8)
        self.service._policy_repo.create.return_value = mock_policy
        
        response = self.service.create_policy(request)
        
        self.service._policy_repo.create.assert_called_once()
        self.assertEqual(response.label, "Test Policy")
        self.assertEqual(response.node_type, "Policy")

    def test_create_resource_success(self):
        """Test successful resource creation."""
        request = CreateResourceRequest(
            name="Test Resource",
            rtype="NATURAL",
            unit="tons"
        )
        
        mock_resource = Resource(
            label="Test Resource",
            rtype=ResourceType.NATURAL,
            unit="tons"
        )
        self.service._resource_repo.create.return_value = mock_resource
        
        response = self.service.create_resource(request)
        
        self.service._resource_repo.create.assert_called_once()
        self.assertEqual(response.label, "Test Resource")
        self.assertEqual(response.node_type, "Resource")

    def test_create_relationship_success(self):
        """Test successful relationship creation."""
        source_id = uuid.uuid4()
        target_id = uuid.uuid4()
        
        request = CreateRelationshipRequest(
            source_id=str(source_id),
            target_id=str(target_id),
            kind="GOVERNS",
            weight=0.8
        )
        
        mock_relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            kind=RelationshipKind.GOVERNS,
            weight=0.8
        )
        self.service._relationship_repo.create.return_value = mock_relationship
        
        response = self.service.create_relationship(request)
        
        self.service._relationship_repo.create.assert_called_once()
        self.assertEqual(response.source_id, str(source_id))
        self.assertEqual(response.target_id, str(target_id))
        self.assertEqual(response.kind, "GOVERNS")

    def test_create_relationship_invalid_uuid(self):
        """Test relationship creation with invalid UUID."""
        request = CreateRelationshipRequest(
            source_id="invalid-uuid",
            target_id="also-invalid",
            kind="GOVERNS"
        )
        
        with self.assertRaises(SFMValidationError) as context:
            self.service.create_relationship(request)
        
        self.assertIn("Invalid UUID format", str(context.exception))

    def test_connect_convenience_method(self):
        """Test the connect convenience method."""
        source_id = uuid.uuid4()
        target_id = uuid.uuid4()
        
        mock_relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            kind=RelationshipKind.GOVERNS,
            weight=0.7
        )
        self.service._relationship_repo.create.return_value = mock_relationship
        
        response = self.service.connect(source_id, target_id, "GOVERNS", 0.7)
        
        self.assertEqual(response.source_id, str(source_id))
        self.assertEqual(response.kind, "GOVERNS")
        self.assertEqual(response.weight, 0.7)

    def test_get_entity_success(self):
        """Test successful entity retrieval."""
        actor_id = uuid.uuid4()
        mock_actor = Actor(label="Test Actor")
        mock_actor.id = actor_id
        
        self.service._actor_repo.read.return_value = mock_actor
        
        result = self.service.get_entity(Actor, actor_id)
        
        self.assertEqual(result, mock_actor)
        self.service._actor_repo.read.assert_called_once_with(actor_id)

    def test_get_entity_not_found(self):
        """Test entity retrieval when not found."""
        actor_id = uuid.uuid4()
        self.service._actor_repo.read.return_value = None
        
        result = self.service.get_entity(Actor, actor_id)
        
        self.assertIsNone(result)

    def test_get_entity_unsupported_type(self):
        """Test entity retrieval with unsupported type."""
        class UnsupportedType:
            pass
        
        result = self.service.get_entity(UnsupportedType, uuid.uuid4())
        
        self.assertIsNone(result)


class TestSFMServiceIntegration(unittest.TestCase):
    """Integration tests for SFMService with real repositories."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.config = SFMServiceConfig(
            storage_backend="networkx",
            validation_enabled=True
        )
        self.service = SFMService(self.config)
        
        # Clear any existing data
        self.service.clear_all_data()

    def tearDown(self):
        """Clean up after each test."""
        try:
            self.service.clear_all_data()
        except:
            pass  # Ignore cleanup errors

    def test_end_to_end_actor_creation_and_retrieval(self):
        """Test complete actor lifecycle."""
        # Create actor
        request = CreateActorRequest(
            name="Integration Test Actor",
            description="Test actor for integration testing",
            sector="government",
            legal_form="agency",
            meta={"test": "true"}
        )
        
        response = self.service.create_actor(request)
        
        # Verify response
        self.assertEqual(response.label, "Integration Test Actor")
        self.assertEqual(response.node_type, "Actor")
        
        # Retrieve actor by ID
        actor_id = uuid.UUID(response.id)
        retrieved_actor = self.service.get_actor(actor_id)
        
        self.assertIsNotNone(retrieved_actor)
        self.assertEqual(retrieved_actor.label, "Integration Test Actor")
        self.assertEqual(retrieved_actor.sector, "government")

    def test_end_to_end_relationship_creation(self):
        """Test complete relationship creation workflow."""
        # Create two actors
        actor1_response = self.service.create_actor(
            CreateActorRequest(name="Actor 1")
        )
        actor2_response = self.service.create_actor(
            CreateActorRequest(name="Actor 2")
        )
        
        # Create relationship
        rel_request = CreateRelationshipRequest(
            source_id=actor1_response.id,
            target_id=actor2_response.id,
            kind="GOVERNS",
            weight=0.8,
            meta={"test_rel": "true"}
        )
        
        rel_response = self.service.create_relationship(rel_request)
        
        # Verify relationship
        self.assertEqual(rel_response.source_id, actor1_response.id)
        self.assertEqual(rel_response.target_id, actor2_response.id)
        self.assertEqual(rel_response.kind, "GOVERNS")
        self.assertEqual(rel_response.weight, 0.8)

    def test_graph_statistics_after_operations(self):
        """Test graph statistics reflect actual operations."""
        initial_stats = self.service.get_statistics()
        self.assertEqual(initial_stats.total_nodes, 0)
        self.assertEqual(initial_stats.total_relationships, 0)
        
        # Create some entities
        actor = self.service.create_actor(CreateActorRequest(name="Test Actor"))
        institution = self.service.create_institution(
            CreateInstitutionRequest(name="Test Institution")
        )
        
        # Create relationship
        self.service.create_relationship(CreateRelationshipRequest(
            source_id=actor.id,
            target_id=institution.id,
            kind="GOVERNS",
            weight=0.5
        ))
        
        # Check updated statistics
        updated_stats = self.service.get_statistics()
        self.assertEqual(updated_stats.total_nodes, 2)
        self.assertEqual(updated_stats.total_relationships, 1)
        self.assertIn("Actor", updated_stats.node_types)
        self.assertIn("Institution", updated_stats.node_types)
        self.assertIn("GOVERNS", updated_stats.relationship_kinds)

    def test_centrality_analysis_integration(self):
        """Test centrality analysis with real data."""
        # Create a small network
        actors = []
        for i in range(3):
            response = self.service.create_actor(
                CreateActorRequest(name=f"Actor {i}")
            )
            actors.append(response)
        
        # Create relationships to form a simple network
        # Actor 0 -> Actor 1 -> Actor 2
        self.service.create_relationship(CreateRelationshipRequest(
            source_id=actors[0].id,
            target_id=actors[1].id,
            kind="GOVERNS"
        ))
        self.service.create_relationship(CreateRelationshipRequest(
            source_id=actors[1].id,
            target_id=actors[2].id,
            kind="INFLUENCES"
        ))
        
        # Perform centrality analysis
        analysis = self.service.analyze_centrality("betweenness", limit=5)
        
        self.assertEqual(analysis.analysis_type, "betweenness")
        self.assertEqual(len(analysis.node_centrality), 3)
        self.assertLessEqual(len(analysis.most_central_nodes), 3)

    def test_policy_impact_analysis_integration(self):
        """Test policy impact analysis with real data."""
        # Create policy and affected entities
        policy = self.service.create_policy(
            CreatePolicyRequest(name="Test Policy", authority="EPA")
        )
        
        actor = self.service.create_actor(
            CreateActorRequest(name="Affected Actor")
        )
        
        # Create relationship from policy to actor
        self.service.create_relationship(CreateRelationshipRequest(
            source_id=policy.id,
            target_id=actor.id,
            kind="AFFECTS"
        ))
        
        # Analyze policy impact
        impact = self.service.analyze_policy_impact(policy.id, impact_radius=2)
        
        self.assertEqual(impact.policy_id, policy.id)
        self.assertGreaterEqual(impact.total_affected_nodes, 0)

    def test_shortest_path_integration(self):
        """Test shortest path finding with real data."""
        # Create a path: Actor A -> Institution -> Actor B
        actor_a = self.service.create_actor(CreateActorRequest(name="Actor A"))
        institution = self.service.create_institution(
            CreateInstitutionRequest(name="Institution")
        )
        actor_b = self.service.create_actor(CreateActorRequest(name="Actor B"))
        
        self.service.create_relationship(CreateRelationshipRequest(
            source_id=actor_a.id,
            target_id=institution.id,
            kind="GOVERNS"
        ))
        self.service.create_relationship(CreateRelationshipRequest(
            source_id=institution.id,
            target_id=actor_b.id,
            kind="REGULATES"
        ))
        
        # Find shortest path
        path = self.service.find_shortest_path(actor_a.id, actor_b.id)
        
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 3)  # A -> Institution -> B
        self.assertEqual(path[0], actor_a.id)
        self.assertEqual(path[2], actor_b.id)

    def test_get_node_neighbors_integration(self):
        """Test getting node neighbors with real data."""
        # Create central node with multiple neighbors
        central = self.service.create_actor(CreateActorRequest(name="Central Actor"))
        neighbors = []
        
        for i in range(3):
            neighbor = self.service.create_actor(
                CreateActorRequest(name=f"Neighbor {i}")
            )
            neighbors.append(neighbor)
            
            # Connect central to neighbor
            self.service.create_relationship(CreateRelationshipRequest(
                source_id=central.id,
                target_id=neighbor.id,
                kind="GOVERNS"
            ))
        
        # Get neighbors
        neighbor_ids = self.service.get_node_neighbors(central.id)
        
        self.assertEqual(len(neighbor_ids), 3)
        for neighbor in neighbors:
            self.assertIn(neighbor.id, neighbor_ids)

    def test_list_nodes_and_relationships_integration(self):
        """Test listing operations with real data."""
        # Create mixed entities
        actor = self.service.create_actor(CreateActorRequest(name="Test Actor"))
        policy = self.service.create_policy(CreatePolicyRequest(name="Test Policy"))
        
        relationship = self.service.create_relationship(CreateRelationshipRequest(
            source_id=actor.id,
            target_id=policy.id,
            kind="IMPLEMENTS"
        ))
        
        # Test listing all nodes
        all_nodes = self.service.list_nodes()
        self.assertEqual(len(all_nodes), 2)
        
        # Test listing specific node type
        actors_only = self.service.list_nodes(node_type="Actor")
        self.assertEqual(len(actors_only), 1)
        self.assertEqual(actors_only[0].node_type, "Actor")
        
        # Test listing relationships
        all_relationships = self.service.list_relationships()
        self.assertEqual(len(all_relationships), 1)
        self.assertEqual(all_relationships[0].kind, "IMPLEMENTS")

    def test_bulk_operations_integration(self):
        """Test bulk operations with real data."""
        requests = [
            CreateActorRequest(name=f"Bulk Actor {i}", sector="test")
            for i in range(5)
        ]
        
        responses = self.service.bulk_create_actors(requests)
        
        self.assertEqual(len(responses), 5)
        for i, response in enumerate(responses):
            self.assertEqual(response.label, f"Bulk Actor {i}")

    def test_service_health_integration(self):
        """Test service health with real operations."""
        # Initial health check
        health = self.service.get_health()
        self.assertEqual(health.status, ServiceStatus.HEALTHY)
        self.assertEqual(health.node_count, 0)
        
        # Add some data and check again
        self.service.create_actor(CreateActorRequest(name="Health Test Actor"))
        
        updated_health = self.service.get_health()
        self.assertEqual(updated_health.status, ServiceStatus.HEALTHY)
        self.assertGreater(updated_health.node_count, 0)

    def test_clear_all_data_integration(self):
        """Test clearing all data."""
        # Add some data
        self.service.create_actor(CreateActorRequest(name="To Be Deleted"))
        self.service.create_institution(CreateInstitutionRequest(name="Also Deleted"))
        
        # Verify data exists
        stats_before = self.service.get_statistics()
        self.assertGreater(stats_before.total_nodes, 0)
        
        # Clear data
        result = self.service.clear_all_data()
        
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["nodes_removed"], 0)
        
        # Verify data is gone
        stats_after = self.service.get_statistics()
        self.assertEqual(stats_after.total_nodes, 0)


class TestSFMServiceFactory(unittest.TestCase):
    """Test service factory and dependency injection functions."""

    def setUp(self):
        """Reset service singleton before each test."""
        reset_sfm_service()

    def tearDown(self):
        """Reset service singleton after each test."""
        reset_sfm_service()

    def test_create_sfm_service(self):
        """Test service factory function."""
        config = SFMServiceConfig(storage_backend="test")
        service = create_sfm_service(config)
        
        self.assertIsInstance(service, SFMService)
        self.assertEqual(service.config.storage_backend, "test")

    def test_create_sfm_service_default_config(self):
        """Test service factory with default config."""
        service = create_sfm_service()
        
        self.assertIsInstance(service, SFMService)
        self.assertEqual(service.config.storage_backend, "networkx")

    def test_get_sfm_service_singleton(self):
        """Test singleton service getter."""
        service1 = get_sfm_service()
        service2 = get_sfm_service()
        
        self.assertIs(service1, service2)

    def test_reset_sfm_service(self):
        """Test service singleton reset."""
        service1 = get_sfm_service()
        reset_sfm_service()
        service2 = get_sfm_service()
        
        self.assertIsNot(service1, service2)

    def test_quick_analysis_function(self):
        """Test quick analysis convenience function."""
        service = create_sfm_service()
        
        # Clear any existing data
        service.clear_all_data()
        
        # Add some test data
        service.create_actor(CreateActorRequest(name="Quick Test Actor"))
        
        result = quick_analysis(service)
        
        self.assertIn("health", result)
        self.assertIn("statistics", result)
        self.assertIn("top_central_nodes", result)
        self.assertIn("analysis_timestamp", result)

    def test_quick_analysis_error_handling(self):
        """Test quick analysis error handling."""
        # Create a service that will fail
        service = create_sfm_service()
        
        # Mock a method to raise an exception
        service.get_statistics = Mock(side_effect=Exception("Test error"))
        
        result = quick_analysis(service)
        
        self.assertIn("error", result)
        self.assertIn("analysis_timestamp", result)


class TestSFMServiceEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = SFMService(SFMServiceConfig(validation_enabled=True))
        self.service.clear_all_data()

    def tearDown(self):
        """Clean up after tests."""
        try:
            self.service.clear_all_data()
        except:
            pass

    def test_create_entity_with_empty_strings(self):
        """Test creating entities with empty string values."""
        # Should fail validation for required name field
        with self.assertRaises((SFMValidationError, SFMError)):
            self.service.create_actor(CreateActorRequest(name=""))
        
        with self.assertRaises((SFMValidationError, SFMError)):
            self.service.create_institution(CreateInstitutionRequest(name=""))

    def test_create_relationship_with_same_source_target(self):
        """Test creating self-referencing relationship."""
        actor = self.service.create_actor(CreateActorRequest(name="Self Actor"))
        
        # Self-referencing relationships should now work with the fixed lock manager
        response = self.service.create_relationship(CreateRelationshipRequest(
            source_id=actor.id,
            target_id=actor.id,
            kind="GOVERNS"
        ))
        
        # Verify the relationship was created successfully
        self.assertEqual(response.source_id, response.target_id)
        self.assertEqual(response.kind, "GOVERNS")
        self.assertEqual(response.source_id, actor.id)

    def test_analysis_on_empty_graph(self):
        """Test analysis operations on empty graph."""
        # Centrality analysis on empty graph
        analysis = self.service.analyze_centrality()
        self.assertEqual(len(analysis.node_centrality), 0)
        self.assertEqual(len(analysis.most_central_nodes), 0)
        
        # Statistics on empty graph
        stats = self.service.get_statistics()
        self.assertEqual(stats.total_nodes, 0)
        self.assertEqual(stats.total_relationships, 0)

    def test_get_nonexistent_entity(self):
        """Test retrieving non-existent entities."""
        fake_id = uuid.uuid4()
        
        actor = self.service.get_actor(fake_id)
        self.assertIsNone(actor)
        
        relationship = self.service.get_relationship(fake_id)
        self.assertIsNone(relationship)

    def test_shortest_path_no_path_exists(self):
        """Test shortest path when no path exists."""
        # Create two unconnected actors
        actor1 = self.service.create_actor(CreateActorRequest(name="Isolated 1"))
        actor2 = self.service.create_actor(CreateActorRequest(name="Isolated 2"))
        
        path = self.service.find_shortest_path(actor1.id, actor2.id)
        self.assertIsNone(path)

    def test_policy_impact_analysis_nonexistent_policy(self):
        """Test policy impact analysis with non-existent policy."""
        fake_policy_id = uuid.uuid4()
        
        with self.assertRaises(SFMNotFoundError):
            self.service.analyze_policy_impact(fake_policy_id)

    def test_large_graph_size_validation(self):
        """Test graph size validation."""
        # Configure service with small max size
        config = SFMServiceConfig(max_graph_size=2, validation_enabled=True)
        service = SFMService(config)
        service.clear_all_data()
        
        # Create entities up to the limit
        service.create_actor(CreateActorRequest(name="Actor 1"))
        service.create_actor(CreateActorRequest(name="Actor 2"))
        
        # This should fail due to size limit
        with self.assertRaises(SFMError) as context:
            service.create_actor(CreateActorRequest(name="Actor 3"))
        
        self.assertEqual(context.exception.error_code.value, "GRAPH_SIZE_EXCEEDED")

    def test_pagination_edge_cases(self):
        """Test pagination with edge case parameters."""
        # Create some test data
        for i in range(5):
            self.service.create_actor(CreateActorRequest(name=f"Actor {i}"))
        
        # Test offset beyond data size
        nodes = self.service.list_nodes(offset=10)
        self.assertEqual(len(nodes), 0)
        
        # Test very large limit
        nodes = self.service.list_nodes(limit=1000)
        self.assertEqual(len(nodes), 5)  # Should return all available

    def test_transaction_context_manager(self):
        """Test transaction context manager."""
        # This is a placeholder test since transactions are not fully implemented
        with self.service.transaction() as tx_service:
            self.assertIs(tx_service, self.service)
        
        # Test transaction with exception
        try:
            with self.service.transaction():
                raise Exception("Test exception")
        except Exception:
            pass  # Should handle gracefully


class TestSFMServiceAdvanced(unittest.TestCase):
    """Advanced test cases for SFM Service functionality."""

    def setUp(self):
        """Set up test fixtures."""
        config = SFMServiceConfig(
            storage_backend="test",
            max_graph_size=1000,
            enable_logging=False
        )
        self.service = SFMService(config)

    def test_temporal_analysis(self):
        """Test temporal analysis capabilities."""
        # Create an actor first
        actor_request = CreateActorRequest(
            name="Temporal Actor",
            description="Actor for temporal testing",
            sector="government"
        )
        actor_response = self.service.create_actor(actor_request)
        
        # Test temporal queries (basic functionality)
        stats = self.service.get_statistics()
        self.assertIsInstance(stats, GraphStatistics)
        self.assertGreaterEqual(stats.total_nodes, 1)

    def test_uncertainty_handling(self):
        """Test uncertainty and confidence handling."""
        # Create resource with uncertainty (using string values for metadata)
        resource_request = CreateResourceRequest(
            name="Uncertain Resource",
            description="Resource with uncertainty data",
            rtype="FINANCIAL",
            unit="USD",
            meta={"uncertainty": "0.2", "confidence": "0.8"}
        )
        response = self.service.create_resource(resource_request)
        self.assertIsNotNone(response.id)
        self.assertEqual(response.meta.get("uncertainty"), "0.2")

    def test_network_metrics_calculation(self):
        """Test network metrics and centrality calculations."""
        # Create multiple actors and relationships
        actor1 = self.service.create_actor(CreateActorRequest(
            name="Central Actor", description="Hub actor", sector="private"
        ))
        actor2 = self.service.create_actor(CreateActorRequest(
            name="Connected Actor 1", description="Connected actor", sector="public"
        ))
        actor3 = self.service.create_actor(CreateActorRequest(
            name="Connected Actor 2", description="Another connected actor", sector="ngo"
        ))
        
        # Create relationships
        rel1 = self.service.create_relationship(CreateRelationshipRequest(
            source_id=actor1.id,
            target_id=actor2.id,
            kind="INFLUENCES",
            weight=0.8
        ))
        rel2 = self.service.create_relationship(CreateRelationshipRequest(
            source_id=actor1.id,
            target_id=actor3.id,
            kind="GOVERNS",
            weight=0.6
        ))
        
        # Test centrality analysis
        centrality = self.service.analyze_centrality("betweenness", limit=5)
        self.assertIsInstance(centrality, CentralityAnalysis)
        self.assertEqual(centrality.analysis_type, "betweenness")
        self.assertGreater(len(centrality.most_central_nodes), 0)

    def test_flow_analysis(self):
        """Test flow analysis capabilities."""
        # Create resources for flow analysis
        source_resource = self.service.create_resource(CreateResourceRequest(
            name="Source Resource", 
            description="Source for flow", 
            rtype="NATURAL", 
            unit="tons"
        ))
        target_resource = self.service.create_resource(CreateResourceRequest(
            name="Target Resource", 
            description="Target for flow", 
            rtype="FINANCIAL", 
            unit="USD"
        ))
        
        # Create relationship representing flow
        flow_rel = self.service.create_relationship(CreateRelationshipRequest(
            source_id=source_resource.id,
            target_id=target_resource.id,
            kind="FLOWS_TO",
            weight=0.7,
            meta={"flow_rate": "100", "flow_unit": "tons/day"}
        ))
        
        self.assertIsNotNone(flow_rel.id)
        if flow_rel.meta:
            self.assertEqual(flow_rel.meta.get("flow_rate"), "100")

    def test_graph_validation(self):
        """Test graph validation and integrity checks."""
        # Test graph size validation
        stats = self.service.get_statistics()
        self.assertIsInstance(stats, GraphStatistics)
        
        # Test health check
        health = self.service.get_health()
        self.assertIsInstance(health, ServiceHealth)
        self.assertEqual(health.status, ServiceStatus.HEALTHY)

    def test_bulk_operations(self):
        """Test bulk creation and operations."""
        # Create multiple entities in bulk
        actors = []
        for i in range(5):
            actor = self.service.create_actor(CreateActorRequest(
                name=f"Bulk Actor {i}",
                description=f"Actor created in bulk operation {i}",
                sector="mixed",
                meta={"bulk_id": str(i)}
            ))
            actors.append(actor)
        
        # Verify all were created
        stats = self.service.get_statistics()
        self.assertGreaterEqual(stats.total_nodes, 5)
        
        # Create relationships between them
        relationships = []
        for i in range(len(actors) - 1):
            rel = self.service.create_relationship(CreateRelationshipRequest(
                source_id=actors[i].id,
                target_id=actors[i + 1].id,
                kind="COLLABORATES",
                weight=0.5,
                meta={"sequence": str(i)}
            ))
            relationships.append(rel)
        
        stats = self.service.get_statistics()
        self.assertGreaterEqual(stats.total_relationships, 4)

    def test_complex_queries(self):
        """Test complex query scenarios."""
        # Set up a complex graph structure
        institution = self.service.create_institution(CreateInstitutionRequest(
            name="Complex Institution",
            description="Institution for complex testing"
        ))
        
        policy = self.service.create_policy(CreatePolicyRequest(
            name="Complex Policy",
            description="Policy for complex testing",
            authority="Test Authority",
            target_sectors=["agriculture", "energy"],
            enforcement=0.9
        ))
        
        # Create governance relationship
        gov_rel = self.service.create_relationship(CreateRelationshipRequest(
            source_id=institution.id,
            target_id=policy.id,
            kind="GOVERNS",
            weight=1.0
        ))
        
        # Test finding shortest path (if exists)
        try:
            path = self.service.find_shortest_path(institution.id, policy.id)
            if path:
                self.assertGreaterEqual(len(path), 2)
        except SFMNotFoundError:
            # Path not found is acceptable for this test
            pass

    def test_error_recovery(self):
        """Test error handling and recovery scenarios."""
        # Test invalid UUID handling
        with self.assertRaises(SFMValidationError):
            fake_id = "invalid-uuid"
            # Test with policy impact analysis that validates UUIDs
            self.service.analyze_policy_impact(fake_id)
        
        # Test nonexistent entity retrieval
        with self.assertRaises(SFMNotFoundError):
            fake_id = str(uuid.uuid4())
            # Test with policy impact analysis for non-existent policy
            self.service.analyze_policy_impact(fake_id)

    def test_metadata_handling(self):
        """Test metadata and versioning capabilities."""
        # Create entity with rich metadata (all string values)
        actor = self.service.create_actor(CreateActorRequest(
            name="Metadata Actor",
            description="Actor with rich metadata",
            sector="research",
            legal_form="university",
            meta={
                "version": "1.0",
                "founded": "1900",
                "employees": "5000",
                "budget": "1000000",
                "email": "info@example.edu",
                "phone": "+1-555-0123"
            }
        ))
        
        # Verify metadata preservation
        self.assertEqual(actor.meta.get("version"), "1.0")
        self.assertEqual(actor.meta.get("employees"), "5000")
        
    def test_health_monitoring(self):
        """Test health monitoring and diagnostics."""
        health = self.service.get_health()
        self.assertIsInstance(health, ServiceHealth)
        self.assertIsNotNone(health.timestamp)
        self.assertEqual(health.status, ServiceStatus.HEALTHY)


class TestSFMServicePerformance(unittest.TestCase):
    """Performance and scalability tests."""

    def setUp(self):
        """Set up performance test fixtures."""
        config = SFMServiceConfig(
            storage_backend="test",
            max_graph_size=10000,  # Higher limit for performance tests
            enable_logging=False
        )
        self.service = SFMService(config)

    def tearDown(self):
        """Clean up after performance tests."""
        pass

    def test_large_graph_performance(self):
        """Test performance with larger graphs."""
        import time
        
        start_time = time.time()
        
        # Create a moderately sized graph for performance testing
        actors = []
        for i in range(50):  # Reasonable size for testing
            actor = self.service.create_actor(CreateActorRequest(
                name=f"Perf Actor {i}",
                description=f"Performance test actor {i}",
                sector="test",
                meta={"index": str(i)}
            ))
            actors.append(actor)
        
        creation_time = time.time() - start_time
        
        # Test statistics calculation performance
        stats_start = time.time()
        stats = self.service.get_statistics()
        stats_time = time.time() - stats_start
        
        # Basic performance assertions
        self.assertLess(creation_time, 30.0)  # Should complete within 30 seconds
        self.assertLess(stats_time, 5.0)     # Stats should be fast
        self.assertEqual(stats.total_nodes, 50)

    def test_concurrent_operations(self):
        """Test thread safety and concurrent operations."""
        import threading
        import time
        
        results = []
        errors = []
        
        def create_actor_worker(worker_id):
            try:
                actor = self.service.create_actor(CreateActorRequest(
                    name=f"Concurrent Actor {worker_id}",
                    description=f"Created by worker {worker_id}",
                    sector="concurrent",
                    meta={"worker_id": str(worker_id)}
                ))
                results.append(actor)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_actor_worker, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Verify results
        self.assertEqual(len(errors), 0, f"Concurrent operations failed: {errors}")
        self.assertEqual(len(results), 10)


if __name__ == "__main__":
    unittest.main()
