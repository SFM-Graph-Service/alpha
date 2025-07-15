"""
Test file to demonstrate the new comprehensive error handling system.
This test focuses on the new exception hierarchy and error context features.
"""

import unittest
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from core.exceptions import (
    SFMError,
    SFMValidationError,
    SFMNotFoundError,
    SFMIntegrityError,
    NodeCreationError,
    NodeUpdateError,
    NodeDeleteError,
    RelationshipValidationError,
    QueryExecutionError,
    QueryTimeoutError,
    DatabaseConnectionError,
    DatabaseTransactionError,
    SecurityValidationError,
    PermissionDeniedError,
    ErrorContext,
    ErrorCode,
    create_not_found_error,
    create_validation_error,
    create_node_creation_error,
    create_query_error,
    create_database_error,
)
from core.sfm_service import SFMService
from db.sfm_dao import NetworkXSFMRepository
from core.sfm_models import Actor


class TestErrorHandlingSystem(unittest.TestCase):
    """Test the new comprehensive error handling system."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = SFMService()
        self.repo = NetworkXSFMRepository()
        self.test_actor = Actor(label="Test Actor")

    def test_error_context_creation(self):
        """Test error context creation with rich information."""
        context = ErrorContext(
            operation="create_actor",
            entity_id=str(uuid.uuid4()),
            entity_type="Actor",
            user_id="test_user",
            session_id="test_session",
            additional_data={"field": "name", "value": "Test Actor"}
        )
        
        self.assertEqual(context.operation, "create_actor")
        self.assertEqual(context.entity_type, "Actor")
        self.assertEqual(context.user_id, "test_user")
        self.assertEqual(context.session_id, "test_session")
        self.assertIsInstance(context.timestamp, datetime)
        self.assertEqual(context.additional_data["field"], "name")
        
        # Test serialization
        context_dict = context.to_dict()
        self.assertIn("operation", context_dict)
        self.assertIn("timestamp", context_dict)
        self.assertIn("additional_data", context_dict)

    def test_sfm_error_hierarchy(self):
        """Test the SFM error hierarchy and inheritance."""
        # Base error
        base_error = SFMError("Base error", ErrorCode.SFM_ERROR)
        self.assertEqual(base_error.error_code, ErrorCode.SFM_ERROR)
        self.assertIsInstance(base_error.context, ErrorContext)
        
        # Validation error
        validation_error = SFMValidationError("Invalid field", field="name", value="")
        self.assertEqual(validation_error.error_code, ErrorCode.VALIDATION_ERROR)
        self.assertEqual(validation_error.details["field"], "name")
        self.assertEqual(validation_error.details["value"], "")
        
        # Not found error
        not_found_error = SFMNotFoundError("Actor", str(uuid.uuid4()))
        self.assertEqual(not_found_error.error_code, ErrorCode.NOT_FOUND_ERROR)
        self.assertIn("not found", not_found_error.message)
        
        # Check inheritance
        self.assertIsInstance(validation_error, SFMError)
        self.assertIsInstance(not_found_error, SFMError)

    def test_node_operation_errors(self):
        """Test node operation specific errors."""
        node_id = uuid.uuid4()
        
        # Node creation error
        creation_error = NodeCreationError(
            "Failed to create node",
            node_type="Actor",
            node_id=node_id
        )
        self.assertEqual(creation_error.error_code, ErrorCode.GRAPH_OPERATION_ERROR)
        self.assertEqual(creation_error.context.entity_type, "Actor")
        self.assertEqual(creation_error.context.entity_id, str(node_id))
        self.assertEqual(creation_error.context.operation, "create_node")
        
        # Node update error
        update_error = NodeUpdateError(
            "Failed to update node",
            node_id=node_id,
            node_type="Actor"
        )
        self.assertEqual(update_error.context.operation, "update_node")
        
        # Node delete error
        delete_error = NodeDeleteError(
            "Failed to delete node",
            node_id=node_id,
            node_type="Actor"
        )
        self.assertEqual(delete_error.context.operation, "delete_node")

    def test_relationship_validation_error(self):
        """Test relationship validation error with context."""
        source_id = uuid.uuid4()
        target_id = uuid.uuid4()
        
        rel_error = RelationshipValidationError(
            "Invalid relationship",
            source_id=source_id,
            target_id=target_id,
            relationship_kind="GOVERNS"
        )
        
        self.assertEqual(rel_error.error_code, ErrorCode.VALIDATION_ERROR)
        self.assertEqual(rel_error.context.operation, "validate_relationship")
        self.assertEqual(rel_error.details["source_id"], str(source_id))
        self.assertEqual(rel_error.details["target_id"], str(target_id))
        self.assertEqual(rel_error.details["relationship_kind"], "GOVERNS")

    def test_query_errors(self):
        """Test query execution errors."""
        query = "SELECT * FROM nodes"
        
        # Query execution error
        query_error = QueryExecutionError(
            "Query failed",
            query=query
        )
        self.assertEqual(query_error.error_code, ErrorCode.QUERY_EXECUTION_ERROR)
        self.assertEqual(query_error.details["query"], query)
        self.assertEqual(query_error.context.operation, "execute_query")
        
        # Query timeout error
        timeout_error = QueryTimeoutError(
            "Query timed out",
            timeout_seconds=30,
            query=query
        )
        self.assertEqual(timeout_error.error_code, ErrorCode.QUERY_TIMEOUT_ERROR)
        self.assertEqual(timeout_error.details["timeout_seconds"], 30)
        self.assertIn("timeout", timeout_error.remediation.lower())

    def test_database_errors(self):
        """Test database specific errors."""
        # Database connection error
        conn_error = DatabaseConnectionError(
            "Failed to connect",
            database_type="networkx"
        )
        self.assertEqual(conn_error.error_code, ErrorCode.DATABASE_CONNECTION_ERROR)
        self.assertEqual(conn_error.details["database_type"], "networkx")
        self.assertIn("database", conn_error.remediation.lower())
        
        # Database transaction error
        trans_error = DatabaseTransactionError(
            "Transaction failed",
            transaction_id="tx_123"
        )
        self.assertEqual(trans_error.error_code, ErrorCode.DATABASE_TRANSACTION_ERROR)
        self.assertEqual(trans_error.details["transaction_id"], "tx_123")
        self.assertIn("transaction", trans_error.remediation.lower())

    
    def test_security_errors(self):
        """Test security related errors."""
        # Security validation error
        security_error = SecurityValidationError(
            "Invalid input",
            validation_type="sanitization",
            field="description"
        )
        self.assertEqual(security_error.error_code, ErrorCode.SECURITY_VALIDATION_ERROR)
        self.assertEqual(security_error.details["validation_type"], "sanitization")
        self.assertEqual(security_error.details["field"], "description")
        
        # Permission denied error
        permission_error = PermissionDeniedError(
            "Access denied",
            resource="actor",
            action="delete"
        )
        self.assertEqual(permission_error.error_code, ErrorCode.PERMISSION_DENIED_ERROR)
        self.assertEqual(permission_error.details["resource"], "actor")
        self.assertEqual(permission_error.details["action"], "delete")

    def test_error_serialization(self):
        """Test error serialization for API responses."""
        error = SFMNotFoundError(
            "Actor", 
            str(uuid.uuid4()),
            remediation="Check the actor ID and try again"
        )
        
        error_dict = error.to_dict()
        self.assertIn("error", error_dict)
        self.assertIn("message", error_dict["error"])
        self.assertIn("error_code", error_dict["error"])
        self.assertIn("context", error_dict["error"])
        self.assertIn("remediation", error_dict["error"])
        self.assertIn("details", error_dict["error"])
        
        # Check that error code is serialized as string
        self.assertEqual(error_dict["error"]["error_code"], "NOT_FOUND_ERROR")

    def test_convenience_functions(self):
        """Test convenience functions for creating common errors."""
        # Create not found error
        not_found = create_not_found_error("Actor", str(uuid.uuid4()))
        self.assertIsInstance(not_found, SFMNotFoundError)
        
        # Create validation error
        validation = create_validation_error("Invalid field", field="name", value="")
        self.assertIsInstance(validation, SFMValidationError)
        
        # Create node creation error
        node_creation = create_node_creation_error("Node exists", "Actor", uuid.uuid4())
        self.assertIsInstance(node_creation, NodeCreationError)
        
        # Create query error
        query = create_query_error("Query failed", "SELECT * FROM nodes")
        self.assertIsInstance(query, QueryExecutionError)
        
        # Create database error
        database = create_database_error("Connection failed", "networkx")
        self.assertIsInstance(database, DatabaseConnectionError)

    def test_repository_error_handling(self):
        """Test that repository operations raise appropriate errors."""
        # Test creating duplicate node
        self.repo.create_node(self.test_actor)
        with self.assertRaises(NodeCreationError) as context:
            self.repo.create_node(self.test_actor)
        
        self.assertEqual(context.exception.context.entity_type, "Actor")
        self.assertEqual(context.exception.context.entity_id, str(self.test_actor.id))
        self.assertEqual(context.exception.context.operation, "create_node")
        
        # Test updating non-existent node
        non_existent = Actor(label="Non-existent")
        with self.assertRaises(SFMNotFoundError) as context:
            self.repo.update_node(non_existent)
        
        self.assertEqual(context.exception.context.entity_type, "Actor")
        self.assertEqual(context.exception.context.entity_id, str(non_existent.id))

    def test_service_error_handling(self):
        """Test that service operations provide good error context."""
        # Test creating actor with invalid data
        from core.sfm_service import CreateActorRequest
        
        # This should work fine
        request = CreateActorRequest(name="Test Actor")
        result = self.service.create_actor(request)
        self.assertIsNotNone(result)
        
        # Test validation errors maintain context
        try:
            invalid_request = CreateActorRequest(name="")
            self.service.create_actor(invalid_request)
        except SFMValidationError as e:
            self.assertIn("label", e.message.lower())  # The error mentions "label" not "name"
            self.assertIsInstance(e.context, ErrorContext)

    def test_backward_compatibility(self):
        """Test that the new error system is backward compatible."""
        # Test that string error codes still work
        error = SFMError("Test error", "CUSTOM_ERROR")
        self.assertEqual(error.error_code, ErrorCode.SFM_ERROR)  # Falls back to default
        
        # Test that existing error structure is preserved
        validation_error = SFMValidationError("Invalid field", field="name", value="")
        self.assertEqual(validation_error.details["field"], "name")
        self.assertEqual(validation_error.details["value"], "")
        
        not_found_error = SFMNotFoundError("Actor", str(uuid.uuid4()))
        self.assertEqual(not_found_error.details["entity_type"], "Actor")


if __name__ == '__main__':
    unittest.main()