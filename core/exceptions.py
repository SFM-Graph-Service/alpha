"""
SFM Exception Hierarchy - Centralized error handling for Social Fabric Matrix Framework

This module provides a comprehensive exception hierarchy for consistent error handling
across all SFM modules. It includes domain-specific exception types with rich context
information for better debugging and error handling.

Key Features:
- Domain-specific exception types for different operations
- Rich error context including entity IDs, operation details, timestamps
- Consistent error codes and messages
- Support for error remediation suggestions
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from enum import Enum


class ErrorCode(str, Enum):
    """Standardized error codes for SFM operations."""
    
    # Base error codes
    SFM_ERROR = "SFM_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND_ERROR = "NOT_FOUND_ERROR"
    INTEGRITY_ERROR = "INTEGRITY_ERROR"
    
    # Graph operation errors
    GRAPH_SIZE_EXCEEDED = "GRAPH_SIZE_EXCEEDED"
    GRAPH_OPERATION_ERROR = "GRAPH_OPERATION_ERROR"
    NODE_CREATION_ERROR = "NODE_CREATION_ERROR"
    NODE_UPDATE_ERROR = "NODE_UPDATE_ERROR"
    NODE_DELETE_ERROR = "NODE_DELETE_ERROR"
    RELATIONSHIP_ERROR = "RELATIONSHIP_ERROR"
    CREATE_ACTOR_FAILED = "CREATE_ACTOR_FAILED"
    CREATE_INSTITUTION_FAILED = "CREATE_INSTITUTION_FAILED"
    CREATE_POLICY_FAILED = "CREATE_POLICY_FAILED"
    CREATE_RESOURCE_FAILED = "CREATE_RESOURCE_FAILED"
    
    # Query errors
    QUERY_EXECUTION_ERROR = "QUERY_EXECUTION_ERROR"
    QUERY_TIMEOUT_ERROR = "QUERY_TIMEOUT_ERROR"
    QUERY_SYNTAX_ERROR = "QUERY_SYNTAX_ERROR"
    
    # Database errors
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_TRANSACTION_ERROR = "DATABASE_TRANSACTION_ERROR"
    DATABASE_PERSISTENCE_ERROR = "DATABASE_PERSISTENCE_ERROR"

    # Security errors
    SECURITY_VALIDATION_ERROR = "SECURITY_VALIDATION_ERROR"
    PERMISSION_DENIED_ERROR = "PERMISSION_DENIED_ERROR"


class ErrorContext:
    """Container for error context information."""
    
    def __init__(
        self,
        operation: Optional[str] = None,
        entity_id: Optional[Union[str, uuid.UUID]] = None,
        entity_type: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        self.operation = operation
        self.entity_id = str(entity_id) if entity_id else None
        self.entity_type = entity_type
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.user_id = user_id
        self.session_id = session_id
        self.request_id = request_id
        self.additional_data = additional_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary for serialization."""
        return {
            "operation": self.operation,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "additional_data": self.additional_data
        }


class SFMError(Exception):
    """Base exception for all SFM-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Union[ErrorCode, str] = ErrorCode.SFM_ERROR,
        context: Optional[ErrorContext] = None,
        remediation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        # Handle backward compatibility with string error codes
        if isinstance(error_code, str):
            # Try to map to existing ErrorCode, otherwise use default
            try:
                self.error_code = ErrorCode(error_code)
            except ValueError:
                self.error_code = ErrorCode.SFM_ERROR
        else:
            self.error_code = error_code
        self.context = context or ErrorContext()
        self.remediation = remediation
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": {
                "message": self.message,
                "error_code": self.error_code.value,
                "context": self.context.to_dict(),
                "remediation": self.remediation,
                "details": self.details
            }
        }


class SFMValidationError(SFMError):
    """Base class for validation-related errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        expected_type: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        remediation: Optional[str] = None
    ):
        details = {
            "field": field,
            "value": str(value) if value is not None else None,
            "expected_type": expected_type
        }
        # Also add to details dict for backward compatibility
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            context=context,
            remediation=remediation,
            details=details
        )


class SFMNotFoundError(SFMError):
    """Exception raised when a requested entity is not found."""
    
    def __init__(
        self,
        entity_type: str,
        entity_id: Union[str, uuid.UUID],
        context: Optional[ErrorContext] = None,
        remediation: Optional[str] = None
    ):
        message = f"{entity_type} with ID {entity_id} not found"
        if not context:
            context = ErrorContext(
                entity_id=entity_id,
                entity_type=entity_type,
                operation="read"
            )
        details = {
            "entity_type": entity_type,
            "entity_id": str(entity_id)
        }
        super().__init__(
            message=message,
            error_code=ErrorCode.NOT_FOUND_ERROR,
            context=context,
            remediation=remediation or f"Verify that the {entity_type} exists and you have access to it",
            details=details
        )


class SFMIntegrityError(SFMError):
    """Exception raised when data integrity constraints are violated."""
    
    def __init__(
        self,
        message: str,
        constraint_type: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        remediation: Optional[str] = None
    ):
        details = {"constraint_type": constraint_type}
        super().__init__(
            message=message,
            error_code=ErrorCode.INTEGRITY_ERROR,
            context=context,
            remediation=remediation,
            details=details
        )


# Graph-specific exceptions
class GraphOperationError(SFMError):
    """Exception for graph operation failures."""
    
    def __init__(
        self,
        message: str,
        operation: str,
        context: Optional[ErrorContext] = None,
        remediation: Optional[str] = None
    ):
        if not context:
            context = ErrorContext(operation=operation)
        super().__init__(
            message=message,
            error_code=ErrorCode.GRAPH_OPERATION_ERROR,
            context=context,
            remediation=remediation
        )


class NodeCreationError(GraphOperationError):
    """Exception for node creation failures."""
    
    def __init__(
        self,
        message: str,
        node_type: str,
        node_id: Optional[Union[str, uuid.UUID]] = None,
        context: Optional[ErrorContext] = None,
        remediation: Optional[str] = None
    ):
        if not context:
            context = ErrorContext(
                operation="create_node",
                entity_type=node_type,
                entity_id=node_id
            )
        super().__init__(
            message=message,
            operation="create_node",
            context=context,
            remediation=remediation
        )


class NodeUpdateError(GraphOperationError):
    """Exception for node update failures."""
    
    def __init__(
        self,
        message: str,
        node_id: Union[str, uuid.UUID],
        node_type: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        remediation: Optional[str] = None
    ):
        if not context:
            context = ErrorContext(
                operation="update_node",
                entity_id=node_id,
                entity_type=node_type
            )
        super().__init__(
            message=message,
            operation="update_node",
            context=context,
            remediation=remediation
        )


class NodeDeleteError(GraphOperationError):
    """Exception for node deletion failures."""
    
    def __init__(
        self,
        message: str,
        node_id: Union[str, uuid.UUID],
        node_type: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        remediation: Optional[str] = None
    ):
        if not context:
            context = ErrorContext(
                operation="delete_node",
                entity_id=node_id,
                entity_type=node_type
            )
        super().__init__(
            message=message,
            operation="delete_node",
            context=context,
            remediation=remediation
        )


class RelationshipValidationError(SFMValidationError):
    """Exception for relationship validation failures."""
    
    def __init__(
        self,
        message: str,
        source_id: Optional[Union[str, uuid.UUID]] = None,
        target_id: Optional[Union[str, uuid.UUID]] = None,
        relationship_kind: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        remediation: Optional[str] = None
    ):
        details = {
            "source_id": str(source_id) if source_id else None,
            "target_id": str(target_id) if target_id else None,
            "relationship_kind": relationship_kind
        }
        if not context:
            context = ErrorContext(
                operation="validate_relationship",
                additional_data=details
            )
        super().__init__(
            message=message,
            context=context,
            remediation=remediation
        )
        self.details.update(details)


# Query-specific exceptions
class QueryExecutionError(SFMError):
    """Exception for query execution failures."""
    
    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        remediation: Optional[str] = None
    ):
        details = {"query": query}
        if not context:
            context = ErrorContext(
                operation="execute_query",
                additional_data=details
            )
        super().__init__(
            message=message,
            error_code=ErrorCode.QUERY_EXECUTION_ERROR,
            context=context,
            remediation=remediation,
            details=details
        )


class QueryTimeoutError(QueryExecutionError):
    """Exception for query timeout failures."""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[int] = None,
        query: Optional[str] = None,
        context: Optional[ErrorContext] = None
    ):
        details = {"timeout_seconds": timeout_seconds}
        remediation = f"Try simplifying the query or increasing timeout limit" + \
                     (f" (current: {timeout_seconds}s)" if timeout_seconds else "")
        super().__init__(
            message=message,
            query=query,
            context=context,
            remediation=remediation
        )
        self.error_code = ErrorCode.QUERY_TIMEOUT_ERROR
        self.details.update(details)


# Database-specific exceptions
class DatabaseError(SFMError):
    """Base exception for database-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.DATABASE_CONNECTION_ERROR,
        context: Optional[ErrorContext] = None,
        remediation: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
            remediation=remediation
        )


class DatabaseConnectionError(DatabaseError):
    """Exception for database connection failures."""
    
    def __init__(
        self,
        message: str,
        database_type: Optional[str] = None,
        context: Optional[ErrorContext] = None
    ):
        details = {"database_type": database_type}
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_CONNECTION_ERROR,
            context=context,
            remediation="Check database connection settings and ensure the database is running"
        )
        self.details.update(details)


class DatabaseTransactionError(DatabaseError):
    """Exception for database transaction failures."""
    
    def __init__(
        self,
        message: str,
        transaction_id: Optional[str] = None,
        context: Optional[ErrorContext] = None
    ):
        details = {"transaction_id": transaction_id}
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_TRANSACTION_ERROR,
            context=context,
            remediation="Transaction may have been rolled back. Retry the operation."
        )
        self.details.update(details)


# Security-specific exceptions
class SecurityValidationError(SFMValidationError):
    """Exception for security validation failures."""
    
    def __init__(
        self,
        message: str,
        validation_type: Optional[str] = None,
        field: Optional[str] = None,
        context: Optional[ErrorContext] = None
    ):
        details = {"validation_type": validation_type}
        super().__init__(
            message=message,
            field=field,
            context=context,
            remediation="Ensure input data meets security requirements"
        )
        self.error_code = ErrorCode.SECURITY_VALIDATION_ERROR
        self.details.update(details)


class PermissionDeniedError(SFMError):
    """Exception for permission denied errors."""
    
    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        context: Optional[ErrorContext] = None
    ):
        details = {
            "resource": resource,
            "action": action
        }
        super().__init__(
            message=message,
            error_code=ErrorCode.PERMISSION_DENIED_ERROR,
            context=context,
            remediation="Contact an administrator to request access to this resource",
            details=details
        )


# Convenience functions for creating common errors
def create_not_found_error(entity_type: str, entity_id: Union[str, uuid.UUID]) -> SFMNotFoundError:
    """Create a standardized not found error."""
    return SFMNotFoundError(entity_type=entity_type, entity_id=entity_id)


def create_validation_error(message: str, field: Optional[str] = None, value: Any = None) -> SFMValidationError:
    """Create a standardized validation error."""
    return SFMValidationError(message=message, field=field, value=value)


def create_node_creation_error(
    message: str, 
    node_type: str, 
    node_id: Optional[Union[str, uuid.UUID]] = None
) -> NodeCreationError:
    """Create a standardized node creation error."""
    return NodeCreationError(message=message, node_type=node_type, node_id=node_id)


def create_query_error(message: str, query: Optional[str] = None) -> QueryExecutionError:
    """Create a standardized query execution error."""
    return QueryExecutionError(message=message, query=query)


def create_database_error(message: str, database_type: Optional[str] = None) -> DatabaseConnectionError:
    """Create a standardized database connection error."""
    return DatabaseConnectionError(message=message, database_type=database_type)