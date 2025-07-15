"""
Unit and Integration Tests for SFM API

This module provides comprehensive testing for the FastAPI SFM API endpoints,
including CRUD operations, analytics, error handling, and response validation.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any

from fastapi.testclient import TestClient
from fastapi import status

# Import the API and related components
from api.sfm_api import app, get_sfm_service_dependency
from core.security import (
    get_current_user, 
    require_permission, 
    require_role,
    auth_manager,
    User,
    Role,
    Permission
)
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
)
from core.sfm_models import Actor, Institution, Policy, Resource, Relationship
from core.sfm_enums import ResourceType

from tests.mocks import (
    create_mock_graph,
    create_sample_nodes
)


# Authentication test utilities
class AuthTestUtils:
    """Utility class for authentication testing."""
    
    @staticmethod
    def create_test_user(username: str = "testuser", role: Role = Role.USER) -> User:
        """Create a test user for authentication testing."""
        return User(
            username=username,
            email=f"{username}@example.com",
            role=role,
            created_at=datetime.now()
        )
    
    @staticmethod
    def create_test_token(user: User) -> str:
        """Create a test JWT token for a user."""
        # Add user to auth manager if not already there
        if user.username not in auth_manager.users:
            auth_manager.users[user.username] = user
        return auth_manager.create_access_token({"sub": user.username})
    
    @staticmethod
    def get_auth_headers(user: User) -> Dict[str, str]:
        """Get authentication headers for a test user."""
        token = AuthTestUtils.create_test_token(user)
        return {"Authorization": f"Bearer {token}"}
    
    @staticmethod
    def mock_current_user(user: User):
        """Mock the current user dependency."""
        def mock_dependency():
            return user
        return mock_dependency
    
    @staticmethod
    def mock_require_permission(permission: Permission):
        """Mock the require_permission dependency."""
        def mock_dependency():
            def permission_checker():
                # Create a test user with the required permission
                if permission == Permission.READ:
                    return AuthTestUtils.create_test_user(role=Role.USER)
                elif permission == Permission.WRITE:
                    return AuthTestUtils.create_test_user(role=Role.USER)
                elif permission == Permission.ANALYTICS:
                    return AuthTestUtils.create_test_user(role=Role.ANALYST)
                elif permission == Permission.ADMIN:
                    return AuthTestUtils.create_test_user(role=Role.ADMIN)
                else:
                    return AuthTestUtils.create_test_user(role=Role.USER)
            return permission_checker
        return mock_dependency
    
    @staticmethod
    def setup_auth_mocks(app):
        """Set up authentication mocks for testing."""
        # Create a test user with admin permissions (has access to everything)
        test_user = AuthTestUtils.create_test_user(role=Role.ADMIN)
        
        # Clear any existing overrides
        app.dependency_overrides.clear()
        
        # Mock all authentication-related dependencies
        def mock_auth_dependency():
            return test_user
        
        def mock_validate_input(request=None):
            return True
        
        # Override the core authentication functions
        from core.security import get_current_user, validate_input
        app.dependency_overrides[get_current_user] = mock_auth_dependency
        app.dependency_overrides[validate_input] = mock_validate_input
        
        # Mock the auth manager's methods
        import unittest.mock
        unittest.mock.patch.object(auth_manager, 'get_current_user', return_value=test_user).start()
        
        # Mock require_permission to always return a function that returns test_user
        def mock_require_permission_method(permission):
            return lambda: test_user
        
        unittest.mock.patch.object(auth_manager, 'require_permission', side_effect=mock_require_permission_method).start()
        
        # Mock require_role to always return a function that returns test_user
        def mock_require_role_method(role):
            return lambda: test_user
        
        unittest.mock.patch.object(auth_manager, 'require_role', side_effect=mock_require_role_method).start()
        
        # Mock the module-level functions
        unittest.mock.patch('core.security.require_permission', side_effect=mock_require_permission_method).start()
        unittest.mock.patch('core.security.require_role', side_effect=mock_require_role_method).start()
        unittest.mock.patch('api.sfm_api.require_permission', side_effect=mock_require_permission_method).start()
        unittest.mock.patch('api.sfm_api.require_role', side_effect=mock_require_role_method).start()
        
        # Mock HTTPBearer to not require authorization headers
        from fastapi.security.http import HTTPAuthorizationCredentials
        
        def mock_http_bearer():
            return HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")
        
        unittest.mock.patch('fastapi.security.HTTPBearer.__call__', return_value=mock_http_bearer()).start()
        
        return test_user

    @staticmethod
    def setup_service_mocks(app, mock_service):
        """Set up service mocks for testing."""
        # Reset service singleton before each test
        from core.sfm_service import reset_sfm_service
        reset_sfm_service()
        
        # Mock service dependency
        app.dependency_overrides[get_sfm_service_dependency] = lambda: mock_service
        
        # Also patch the get_sfm_service function to prevent startup event from creating real service
        import unittest.mock
        get_sfm_service_patcher = unittest.mock.patch('core.sfm_service.get_sfm_service', return_value=mock_service)
        get_sfm_service_patcher.start()
        
        # Also patch it in the API module
        api_get_sfm_service_patcher = unittest.mock.patch('api.sfm_api.get_sfm_service', return_value=mock_service)
        api_get_sfm_service_patcher.start()
        
        return get_sfm_service_patcher, api_get_sfm_service_patcher
        
        # Mock HTTPBearer to not require actual HTTP headers
        from fastapi.security import HTTPBearer
        from fastapi.security.http import HTTPAuthorizationCredentials
        
        def mock_http_bearer():
            return HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")
        
        # Use unittest.mock to patch authentication components
        import unittest.mock
        
        # Mock the auth manager's methods
        unittest.mock.patch.object(auth_manager, 'get_current_user', return_value=test_user).start()
        
        # Mock require_permission to always return a function that returns test_user
        def mock_require_permission_method(permission):
            return lambda: test_user
        
        unittest.mock.patch.object(auth_manager, 'require_permission', side_effect=mock_require_permission_method).start()
        
        # Mock require_role to always return a function that returns test_user
        def mock_require_role_method(role):
            return lambda: test_user
        
        unittest.mock.patch.object(auth_manager, 'require_role', side_effect=mock_require_role_method).start()
        
        # Mock the module-level functions
        unittest.mock.patch('core.security.require_permission', side_effect=mock_require_permission_method).start()
        unittest.mock.patch('core.security.require_role', side_effect=mock_require_role_method).start()
        unittest.mock.patch('api.sfm_api.require_permission', side_effect=mock_require_permission_method).start()
        unittest.mock.patch('api.sfm_api.require_role', side_effect=mock_require_role_method).start()
        
        # Mock HTTPBearer to not require authorization headers
        unittest.mock.patch('fastapi.security.HTTPBearer.__call__', return_value=mock_http_bearer()).start()
        
        return test_user


class TestSFMAPIHealth(unittest.TestCase):
    """Test suite for health and status endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_service = Mock(spec=SFMService)
        
        # Set up service mocks BEFORE creating TestClient
        self.get_sfm_service_patcher, self.api_get_sfm_service_patcher = AuthTestUtils.setup_service_mocks(app, self.mock_service)
        
        # Set up authentication mocks
        AuthTestUtils.setup_auth_mocks(app)
        
        # Create TestClient AFTER setting up mocks
        self.client = TestClient(app)

    def tearDown(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()
        # Stop the service patches
        self.get_sfm_service_patcher.stop()
        self.api_get_sfm_service_patcher.stop()
        # Reset service singleton after each test
        from core.sfm_service import reset_sfm_service
        reset_sfm_service()
        # Stop all patches
        import unittest.mock
        unittest.mock.patch.stopall()

    def test_root_endpoint(self):
        """Test the root endpoint returns API information."""
        response = self.client.get("/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn("name", data)
        self.assertIn("version", data)
        self.assertIn("description", data)
        self.assertIn("docs", data)
        self.assertIn("health", data)
        self.assertIn("timestamp", data)
        
        self.assertEqual(data["name"], "SFM (Social Fabric Matrix) API")
        self.assertEqual(data["version"], "1.0.0")

    def test_health_endpoint(self):
        """Test the health endpoint returns service health."""
        # Mock health response
        mock_health = ServiceHealth(
            status=ServiceStatus.HEALTHY,
            backend="networkx",
            node_count=10,
            relationship_count=15,
            last_operation="test",
            timestamp=datetime.now().isoformat()
        )
        self.mock_service.get_health.return_value = mock_health
        
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["backend"], "networkx")
        self.assertEqual(data["node_count"], 10)
        self.assertEqual(data["relationship_count"], 15)
        self.assertIn("timestamp", data)
        
        self.mock_service.get_health.assert_called_once()


class TestSFMAPIStatistics(unittest.TestCase):
    """Test suite for statistics and analytics endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_service = Mock(spec=SFMService)
        
        # Set up service mocks BEFORE creating TestClient
        self.get_sfm_service_patcher, self.api_get_sfm_service_patcher = AuthTestUtils.setup_service_mocks(app, self.mock_service)
        
        # Set up authentication mocks
        AuthTestUtils.setup_auth_mocks(app)
        
        # Create TestClient AFTER setting up mocks
        self.client = TestClient(app)

    def tearDown(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()
        # Stop the service patches
        self.get_sfm_service_patcher.stop()
        self.api_get_sfm_service_patcher.stop()
        # Reset service singleton after each test
        from core.sfm_service import reset_sfm_service
        reset_sfm_service()
        # Stop all patches
        import unittest.mock
        unittest.mock.patch.stopall()

    def test_get_statistics(self):
        """Test getting graph statistics."""
        # Mock statistics response
        mock_stats = GraphStatistics(
            total_nodes=25,
            total_relationships=40,
            node_types={"Actor": 10, "Institution": 5, "Policy": 5, "Resource": 5},
            relationship_kinds={"GOVERNS": 10, "INFLUENCES": 15, "AFFECTS": 15},
            timestamp=datetime.now().isoformat()
        )
        self.mock_service.get_statistics.return_value = mock_stats
        
        response = self.client.get("/statistics")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data["total_nodes"], 25)
        self.assertEqual(data["total_relationships"], 40)
        self.assertIn("node_types", data)
        self.assertIn("relationship_kinds", data)
        self.assertIn("timestamp", data)
        
        self.mock_service.get_statistics.assert_called_once()

    def test_analyze_centrality(self):
        """Test centrality analysis endpoint."""
        # Mock centrality response
        mock_centrality = CentralityAnalysis(
            node_centrality={"node1": 0.85, "node2": 0.72},
            most_central_nodes=[("node1", 0.85), ("node2", 0.72)],
            analysis_type="betweenness",
            timestamp=datetime.now().isoformat()
        )
        self.mock_service.analyze_centrality.return_value = mock_centrality
        
        response = self.client.get("/analytics/centrality?centrality_type=betweenness&limit=10")
        
        # Debug response on failure
        if response.status_code != status.HTTP_200_OK:
            print(f"DEBUG: Status code: {response.status_code}")
            print(f"DEBUG: Response: {response.text}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data["analysis_type"], "betweenness")
        self.assertIn("node_centrality", data)
        self.assertIn("most_central_nodes", data)
        self.assertEqual(len(data["most_central_nodes"]), 2)
        
        self.mock_service.analyze_centrality.assert_called_once_with("betweenness", 10)

    def test_analyze_policy_impact(self):
        """Test policy impact analysis endpoint."""
        policy_id = str(uuid.uuid4())
        
        # Mock policy impact response
        mock_impact = PolicyImpactAnalysis(
            policy_id=policy_id,
            total_affected_nodes=12,
            affected_actors=["actor1", "actor2", "actor3", "actor4", "actor5"],
            affected_institutions=["inst1", "inst2", "inst3"],
            affected_resources=["res1", "res2", "res3", "res4"],
            network_metrics={"density": 0.35, "clustering": 0.62},
            impact_radius=3
        )
        self.mock_service.analyze_policy_impact.return_value = mock_impact
        
        response = self.client.get(f"/analytics/policy-impact/{policy_id}?impact_radius=3")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data["policy_id"], policy_id)
        self.assertEqual(data["total_affected_nodes"], 12)
        self.assertEqual(data["impact_radius"], 3)
        self.assertIn("affected_actors", data)
        self.assertIn("affected_institutions", data)
        self.assertIn("affected_resources", data)
        self.assertIn("network_metrics", data)
        
        self.mock_service.analyze_policy_impact.assert_called_once_with(policy_id, 3)

    def test_find_shortest_path(self):
        """Test shortest path finding endpoint."""
        source_id = str(uuid.uuid4())
        target_id = str(uuid.uuid4())
        
        # Mock shortest path response
        mock_path = [source_id, str(uuid.uuid4()), target_id]
        self.mock_service.find_shortest_path.return_value = mock_path
        
        response = self.client.get(f"/analytics/shortest-path?source_id={source_id}&target_id={target_id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data["source_id"], source_id)
        self.assertEqual(data["target_id"], target_id)
        self.assertEqual(data["path"], mock_path)
        self.assertEqual(data["path_length"], 3)
        self.assertIn("timestamp", data)
        
        self.mock_service.find_shortest_path.assert_called_once_with(source_id, target_id, None)


class TestSFMAPIActors(unittest.TestCase):
    """Test suite for actor CRUD endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_service = Mock(spec=SFMService)
        
        # Set up service mocks BEFORE creating TestClient
        self.get_sfm_service_patcher, self.api_get_sfm_service_patcher = AuthTestUtils.setup_service_mocks(app, self.mock_service)
        
        # Set up authentication mocks
        AuthTestUtils.setup_auth_mocks(app)
        
        # Create TestClient AFTER setting up mocks
        self.client = TestClient(app)

    def tearDown(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()
        # Stop the service patches
        self.get_sfm_service_patcher.stop()
        self.api_get_sfm_service_patcher.stop()
        # Reset service singleton after each test
        from core.sfm_service import reset_sfm_service
        reset_sfm_service()
        # Stop all patches
        import unittest.mock
        unittest.mock.patch.stopall()

    def test_create_actor_success(self):
        """Test successful actor creation."""
        # Create a test user and get auth headers
        test_user = AuthTestUtils.create_test_user()
        headers = AuthTestUtils.get_auth_headers(test_user)
        
        # Mock response
        actor_id = str(uuid.uuid4())
        mock_response = NodeResponse(
            id=actor_id,
            label="Test Actor",
            description="Test description",
            node_type="Actor",
            meta={"sector": "government", "legal_form": "agency", "test": "true"},
            created_at=datetime.now().isoformat()
        )
        self.mock_service.create_actor.return_value = mock_response
        
        # Test data
        request_data = {
            "name": "Test Actor",
            "description": "Test description",
            "sector": "government",
            "legal_form": "agency",
            "meta": {"test": "true"}
        }
        
        response = self.client.post("/actors", json=request_data, headers=headers)
        
        # Debug response on failure
        if response.status_code != status.HTTP_201_CREATED:
            print(f"DEBUG: Status code: {response.status_code}")
            print(f"DEBUG: Response: {response.text}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        self.assertEqual(data["id"], actor_id)
        self.assertEqual(data["label"], "Test Actor")
        self.assertEqual(data["node_type"], "Actor")
        self.assertIn("meta", data)
        self.assertIn("created_at", data)
        
        # Verify service was called with correct request
        self.mock_service.create_actor.assert_called_once()
        call_args = self.mock_service.create_actor.call_args[0][0]
        self.assertIsInstance(call_args, CreateActorRequest)
        self.assertEqual(call_args.name, "Test Actor")

    def test_get_actor_success(self):
        """Test successful actor retrieval."""
        actor_id = str(uuid.uuid4())
        
        # Mock actor and response
        mock_actor = Actor(
            label="Test Actor",
            description="Test description",
            sector="government"
        )
        mock_actor.id = uuid.UUID(actor_id)
        
        mock_response = NodeResponse(
            id=actor_id,
            label="Test Actor",
            description="Test description",
            node_type="Actor",
            meta={"sector": "government"},
            created_at=datetime.now().isoformat()
        )
        
        self.mock_service.get_actor.return_value = mock_actor
        self.mock_service._node_to_response.return_value = mock_response
        
        response = self.client.get(f"/actors/{actor_id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data["id"], actor_id)
        self.assertEqual(data["label"], "Test Actor")
        self.assertEqual(data["node_type"], "Actor")
        
        self.mock_service.get_actor.assert_called_once_with(uuid.UUID(actor_id))

    def test_get_actor_not_found(self):
        """Test actor retrieval when actor doesn't exist."""
        actor_id = str(uuid.uuid4())
        
        # Mock service to return None
        self.mock_service.get_actor.return_value = None
        
        response = self.client.get(f"/actors/{actor_id}")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertIn("detail", data)

    def test_get_actor_invalid_uuid(self):
        """Test actor retrieval with invalid UUID."""
        invalid_id = "not-a-uuid"
        
        response = self.client.get(f"/actors/{invalid_id}")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("Invalid UUID", data["detail"])

    def test_get_actor_neighbors(self):
        """Test getting actor neighbors."""
        actor_id = str(uuid.uuid4())
        neighbor_ids = [str(uuid.uuid4()) for _ in range(3)]
        
        # Mock neighbors response
        self.mock_service.get_node_neighbors.return_value = neighbor_ids
        
        response = self.client.get(f"/actors/{actor_id}/neighbors?distance=2")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data["actor_id"], actor_id)
        self.assertEqual(data["neighbors"], neighbor_ids)
        self.assertEqual(data["neighbor_count"], 3)
        self.assertEqual(data["distance"], 2)
        
        self.mock_service.get_node_neighbors.assert_called_once_with(actor_id, None, 2)


class TestSFMAPIInstitutions(unittest.TestCase):
    """Test suite for institution CRUD endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_service = Mock(spec=SFMService)
        
        # Mock service dependency
        app.dependency_overrides[get_sfm_service_dependency] = lambda: self.mock_service
        
        # Set up authentication mocks
        AuthTestUtils.setup_auth_mocks(app)

    def tearDown(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_create_institution_success(self):
        """Test successful institution creation."""
        # Mock response
        institution_id = str(uuid.uuid4())
        mock_response = NodeResponse(
            id=institution_id,
            label="Test Institution",
            description="Test description",
            node_type="Institution",
            meta={"type": "regulatory"},
            created_at=datetime.now().isoformat()
        )
        self.mock_service.create_institution.return_value = mock_response
        
        # Test data
        request_data = {
            "name": "Test Institution",
            "description": "Test description",
            "meta": {"type": "regulatory"}
        }
        
        response = self.client.post("/institutions", json=request_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        self.assertEqual(data["id"], institution_id)
        self.assertEqual(data["label"], "Test Institution")
        self.assertEqual(data["node_type"], "Institution")
        
        # Verify service was called with correct request
        self.mock_service.create_institution.assert_called_once()
        call_args = self.mock_service.create_institution.call_args[0][0]
        self.assertIsInstance(call_args, CreateInstitutionRequest)
        self.assertEqual(call_args.name, "Test Institution")

    def test_get_institution_success(self):
        """Test successful institution retrieval."""
        institution_id = str(uuid.uuid4())
        
        # Mock institution and response
        mock_institution = Institution(
            label="Test Institution",
            description="Test description"
        )
        mock_institution.id = uuid.UUID(institution_id)
        
        mock_response = NodeResponse(
            id=institution_id,
            label="Test Institution",
            description="Test description",
            node_type="Institution",
            meta={},
            created_at=datetime.now().isoformat()
        )
        
        self.mock_service.get_institution.return_value = mock_institution
        self.mock_service._node_to_response.return_value = mock_response
        
        response = self.client.get(f"/institutions/{institution_id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data["id"], institution_id)
        self.assertEqual(data["label"], "Test Institution")
        self.assertEqual(data["node_type"], "Institution")


class TestSFMAPIErrorHandling(unittest.TestCase):
    """Test suite for API error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_service = Mock(spec=SFMService)
        
        # Mock service dependency
        app.dependency_overrides[get_sfm_service_dependency] = lambda: self.mock_service
        
        # Set up authentication mocks
        AuthTestUtils.setup_auth_mocks(app)

    def tearDown(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_validation_error_handling(self):
        """Test handling of validation errors."""
        # Mock service to raise SFMValidationError
        validation_error = SFMValidationError(
            message="Invalid data provided",
            field="name",
            value=""
        )
        self.mock_service.create_actor.side_effect = validation_error
        
        request_data = {
            "name": "",  # Invalid empty name
            "description": "Test description"
        }
        
        response = self.client.post("/actors", json=request_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        
        self.assertEqual(data["error"], "Validation Error")
        self.assertEqual(data["message"], "Invalid data provided")
        self.assertEqual(data["error_code"], "VALIDATION_ERROR")
        self.assertIn("details", data)
        self.assertIn("timestamp", data)

    def test_not_found_error_handling(self):
        """Test handling of not found errors."""
        # Mock service to raise SFMNotFoundError
        not_found_error = SFMNotFoundError(
            entity_type="Actor",
            entity_id="123"
        )
        self.mock_service.get_actor.side_effect = not_found_error
        
        actor_id = str(uuid.uuid4())
        response = self.client.get(f"/actors/{actor_id}")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        
        self.assertEqual(data["error"], "Not Found")
        self.assertEqual(data["message"], "Actor with ID 123 not found")
        self.assertEqual(data["error_code"], "NOT_FOUND_ERROR")
        self.assertIn("details", data)
        self.assertIn("timestamp", data)

    def test_service_error_handling(self):
        """Test handling of general service errors."""
        # Mock service to raise SFMError
        service_error = SFMError(
            message="Internal service error",
            error_code="SERVICE_ERROR",
            details={"operation": "create_actor"}
        )
        self.mock_service.create_actor.side_effect = service_error
        
        request_data = {
            "name": "Test Actor",
            "description": "Test description"
        }
        
        response = self.client.post("/actors", json=request_data)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = response.json()
        
        self.assertEqual(data["error"], "Service Error")
        self.assertEqual(data["message"], "Internal service error")
        self.assertEqual(data["error_code"], "SFM_ERROR")
        self.assertIn("details", data)
        self.assertIn("timestamp", data)


class TestSFMAPIMetadata(unittest.TestCase):
    """Test suite for metadata endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_get_entity_types(self):
        """Test getting entity types metadata."""
        response = self.client.get("/metadata/entity-types")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn("entity_types", data)
        self.assertIn("relationship_kinds", data)
        self.assertIn("resource_types", data)
        
        # Check entity types structure
        entity_types = data["entity_types"]
        self.assertIn("Actor", entity_types)
        self.assertIn("Institution", entity_types)
        self.assertIn("Policy", entity_types)
        self.assertIn("Resource", entity_types)
        
        # Check Actor entity type details
        actor_info = entity_types["Actor"]
        self.assertIn("description", actor_info)
        self.assertIn("properties", actor_info)
        self.assertIsInstance(actor_info["properties"], list)

    def test_get_api_info(self):
        """Test getting API information."""
        response = self.client.get("/metadata/api-info")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn("api_version", data)
        self.assertIn("framework", data)
        self.assertIn("description", data)
        self.assertIn("features", data)
        self.assertIn("endpoints", data)
        self.assertIn("timestamp", data)
        
        self.assertEqual(data["api_version"], "1.0.0")
        self.assertEqual(data["framework"], "FastAPI")
        
        # Check endpoints structure
        endpoints = data["endpoints"]
        self.assertIn("health", endpoints)
        self.assertIn("documentation", endpoints)
        self.assertIn("entities", endpoints)
        self.assertIn("analytics", endpoints)


class TestSFMAPIIntegration(unittest.TestCase):
    """Integration tests with real service (no mocks)."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.client = TestClient(app)
        # Use real service for integration tests
        # Clear any existing dependency overrides
        app.dependency_overrides.clear()
        
        # Set up authentication mocks even for integration tests
        AuthTestUtils.setup_auth_mocks(app)

    def tearDown(self):
        """Clean up after integration tests."""
        # Clear the service state after each test
        try:
            service = get_sfm_service_dependency()
            service.clear_all_data()
        except:
            pass  # Ignore cleanup errors
        
        app.dependency_overrides.clear()

    def test_end_to_end_actor_lifecycle(self):
        """Test complete actor lifecycle through API."""
        # Create actor
        create_data = {
            "name": "Integration Test Actor",
            "description": "Test actor for integration testing",
            "sector": "government",
            "legal_form": "agency",
            "meta": {"test": "integration"}
        }
        
        create_response = self.client.post("/actors", json=create_data)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        actor_data = create_response.json()
        actor_id = actor_data["id"]
        
        # Retrieve actor
        get_response = self.client.get(f"/actors/{actor_id}")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        
        retrieved_data = get_response.json()
        self.assertEqual(retrieved_data["id"], actor_id)
        self.assertEqual(retrieved_data["label"], "Integration Test Actor")

    def test_health_check_with_real_service(self):
        """Test health check with real service."""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should have valid health status
        self.assertIn("status", data)
        self.assertIn("backend", data)
        self.assertIn("node_count", data)
        self.assertIn("relationship_count", data)
        
        # Status should be a valid enum value
        valid_statuses = ["healthy", "degraded", "error"]
        self.assertIn(data["status"], valid_statuses)


class TestSFMAPIAuthentication(unittest.TestCase):
    """Test suite for authentication functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_service = Mock(spec=SFMService)
        
        # Mock service dependency
        app.dependency_overrides[get_sfm_service_dependency] = lambda: self.mock_service
        
        # Don't set up auth mocks for authentication tests

    def tearDown(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_register_user_success(self):
        """Test successful user registration."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "role": "user"
        }
        
        response = self.client.post("/auth/register", json=user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["role"], "user")
        self.assertTrue(data["is_active"])

    def test_register_user_duplicate_username(self):
        """Test registration with duplicate username."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "role": "user"
        }
        
        # First registration should succeed
        response1 = self.client.post("/auth/register", json=user_data)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second registration with same username should fail
        response2 = self.client.post("/auth/register", json=user_data)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Test successful login."""
        # First register a user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "role": "user"
        }
        self.client.post("/auth/register", json=user_data)
        
        # Then login
        login_data = {
            "username": "testuser",
            "password": "TestPass123!"
        }
        
        response = self.client.post("/auth/login", json=login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertIn("expires_in", data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = self.client.post("/auth/login", json=login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without authentication."""
        request_data = {
            "name": "Test Actor",
            "description": "Test description"
        }
        
        response = self.client.post("/actors", json=request_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_protected_endpoint_with_auth(self):
        """Test accessing protected endpoint with authentication."""
        # Register and login to get token
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "role": "user"
        }
        self.client.post("/auth/register", json=user_data)
        
        login_data = {
            "username": "testuser",
            "password": "TestPass123!"
        }
        login_response = self.client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Mock successful actor creation
        mock_response = NodeResponse(
            id=str(uuid.uuid4()),
            label="Test Actor",
            description="Test description",
            node_type="Actor",
            meta={},
            created_at=datetime.now().isoformat()
        )
        self.mock_service.create_actor.return_value = mock_response
        
        # Test protected endpoint with token
        headers = {"Authorization": f"Bearer {token}"}
        request_data = {
            "name": "Test Actor",
            "description": "Test description"
        }
        
        response = self.client.post("/actors", json=request_data, headers=headers)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_current_user_info(self):
        """Test getting current user information."""
        # Register and login
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "role": "user"
        }
        self.client.post("/auth/register", json=user_data)
        
        login_data = {
            "username": "testuser",
            "password": "TestPass123!"
        }
        login_response = self.client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Test current user endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/auth/me", headers=headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["role"], "user")

    def test_get_user_permissions(self):
        """Test getting user permissions."""
        # Register and login
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "role": "user"
        }
        self.client.post("/auth/register", json=user_data)
        
        login_data = {
            "username": "testuser",
            "password": "TestPass123!"
        }
        login_response = self.client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Test permissions endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/auth/permissions", headers=headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data["user"], "testuser")
        self.assertEqual(data["role"], "user")
        self.assertIn("permissions", data)
        self.assertIn("read", data["permissions"])
        self.assertIn("write", data["permissions"])

    def test_role_based_access_control(self):
        """Test role-based access control."""
        # Register analyst user
        analyst_data = {
            "username": "analyst",
            "email": "analyst@example.com",
            "password": "AnalystPass123!",
            "role": "analyst"
        }
        self.client.post("/auth/register", json=analyst_data)
        
        # Login as analyst
        login_data = {
            "username": "analyst",
            "password": "AnalystPass123!"
        }
        login_response = self.client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock analytics response
        mock_analytics = CentralityAnalysis(
            node_centrality={"node1": 0.5},
            most_central_nodes=[("node1", 0.5)],
            analysis_type="betweenness",
            timestamp=datetime.now().isoformat()
        )
        self.mock_service.analyze_centrality.return_value = mock_analytics
        
        # Test analytics endpoint (should work for analyst)
        response = self.client.get("/analytics/centrality", headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test write endpoint (should fail for analyst - read-only role)
        request_data = {
            "name": "Test Actor",
            "description": "Test description"
        }
        response = self.client.post("/actors", json=request_data, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_token(self):
        """Test access with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/auth/me", headers=headers)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_token(self):
        """Test access without token."""
        response = self.client.get("/auth/me")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestSFMAPISecurityIntegration(unittest.TestCase):
    """Test suite for security integration with existing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_service = Mock(spec=SFMService)
        
        # Mock service dependency
        app.dependency_overrides[get_sfm_service_dependency] = lambda: self.mock_service

    def tearDown(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_auth_and_functionality_integration(self):
        """Test that authentication works together with existing functionality."""
        # Register and login
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "role": "user"
        }
        self.client.post("/auth/register", json=user_data)
        
        login_data = {
            "username": "testuser",
            "password": "TestPass123!"
        }
        login_response = self.client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test that authenticated user can access protected endpoints
        mock_response = NodeResponse(
            id=str(uuid.uuid4()),
            label="Test Actor",
            description="Test description",
            node_type="Actor",
            meta={},
            created_at=datetime.now().isoformat()
        )
        self.mock_service.create_actor.return_value = mock_response
        
        request_data = {
            "name": "Test Actor",
            "description": "Test description"
        }
        
        response = self.client.post("/actors", json=request_data, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_public_endpoints_still_work(self):
        """Test that public endpoints still work without authentication."""
        # Health endpoint should work without auth
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Root endpoint should work without auth
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Statistics endpoint should work without auth
        mock_stats = GraphStatistics(
            total_nodes=10,
            total_relationships=15,
            node_types={"Actor": 5, "Institution": 5},
            relationship_kinds={"GOVERNS": 10, "INFLUENCES": 5},
            timestamp=datetime.now().isoformat()
        )
        self.mock_service.get_statistics.return_value = mock_stats
        
        response = self.client.get("/statistics")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


if __name__ == "__main__":
    unittest.main(verbosity=2)
