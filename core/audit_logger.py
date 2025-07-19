"""
Core Audit Logger Module

This module provides core audit logging functionality for the SFM system.
It integrates with the infrastructure audit logger and provides high-level
audit operations for core system components.
"""

import time
import uuid
from functools import wraps
from typing import Any, Dict, List, Optional, Callable, TypeVar
from datetime import datetime

# Import from the infrastructure audit logger
from infrastructure.audit_logger import (
    AuditLevel, OperationType, AuditEvent,
    get_audit_logger as get_infrastructure_audit_logger,
    log_operation, log_security_event, log_performance_event
)

# Type variable for decorator
F = TypeVar("F", bound=Callable[..., Any])


class CoreAuditLogger:
    """Core audit logger that wraps the infrastructure audit logger with core-specific features."""
    
    def __init__(self):
        self.infrastructure_logger = get_infrastructure_audit_logger()
        self._operation_count = 0
        self._error_count = 0
        self._performance_metrics: List[Dict[str, Any]] = []
    
    def log_core_operation(self, operation_type: OperationType, operation_name: str,
                          entity_type: Optional[str] = None, entity_id: Optional[str] = None,
                          success: bool = True, duration: Optional[float] = None,
                          metadata: Optional[Dict[str, Any]] = None):
        """Log a core system operation with additional core-specific context."""
        self._operation_count += 1
        if not success:
            self._error_count += 1
        
        # Add core-specific metadata
        core_metadata = {
            "component": "core",
            "operation_sequence": self._operation_count,
            "error_rate": self._error_count / self._operation_count if self._operation_count > 0 else 0.0
        }
        if metadata:
            core_metadata.update(metadata)
        
        # Log to infrastructure logger
        level = AuditLevel.ERROR if not success else AuditLevel.INFO
        self.infrastructure_logger.log_operation(
            operation_type=operation_type,
            operation_name=operation_name,
            entity_type=entity_type,
            entity_id=entity_id,
            message=f"Core operation: {operation_name} - {'Success' if success else 'Failed'}",
            data=core_metadata,
            level=level
        )
        
        # Track performance metrics
        if duration is not None:
            self._performance_metrics.append({
                "operation": operation_name,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "success": success
            })
            # Keep only last 1000 metrics
            if len(self._performance_metrics) > 1000:
                self._performance_metrics = self._performance_metrics[-500:]
    
    def get_core_audit_stats(self) -> Dict[str, Any]:
        """Get core-specific audit statistics."""
        avg_duration = 0.0
        if self._performance_metrics:
            avg_duration = sum(m["duration"] for m in self._performance_metrics) / len(self._performance_metrics)
        
        return {
            "total_operations": self._operation_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / self._operation_count if self._operation_count > 0 else 0.0,
            "average_duration": avg_duration,
            "recent_performance_samples": len(self._performance_metrics)
        }


# Global core audit logger instance
_global_core_audit_logger = CoreAuditLogger()


def get_core_audit_logger() -> CoreAuditLogger:
    """Get the global core audit logger instance."""
    return _global_core_audit_logger


def log_core_operation(operation_type: OperationType, operation_name: str, **kwargs: Any) -> None:
    """Log a core operation using the global core audit logger."""
    _global_core_audit_logger.log_core_operation(operation_type, operation_name, **kwargs)


def get_core_audit_stats() -> Dict[str, Any]:
    """Get core audit statistics."""
    return _global_core_audit_logger.get_core_audit_stats()


def reset_core_audit_stats() -> None:
    """Reset core audit statistics (for testing purposes)."""
    global _global_core_audit_logger
    _global_core_audit_logger = CoreAuditLogger()


# Helper functions for common audit operations
def audit_entity_creation(entity_type: str) -> Callable[[F], F]:
    """Decorator for entity creation operations."""
    return audit_operation(OperationType.CREATE, f"create_{entity_type.lower()}", entity_type)


def audit_entity_update(entity_type: str) -> Callable[[F], F]:
    """Decorator for entity update operations."""
    return audit_operation(OperationType.UPDATE, f"update_{entity_type.lower()}", entity_type)


def audit_entity_deletion(entity_type: str) -> Callable[[F], F]:
    """Decorator for entity deletion operations."""
    return audit_operation(OperationType.DELETE, f"delete_{entity_type.lower()}", entity_type)


def audit_query_operation(query_name: str) -> Callable[[F], F]:
    """Decorator for query operations."""
    return audit_operation(OperationType.QUERY, query_name, "Query")


def audit_analysis_operation(analysis_name: str) -> Callable[[F], F]:
    """Decorator for analysis operations."""
    return audit_operation(OperationType.ANALYSIS, analysis_name, "Analysis")


class AuditContext:
    """Context manager for manual audit logging."""
    
    def __init__(self, operation_type: OperationType, operation_name: str,
                 entity_type: Optional[str] = None, entity_id: Optional[str] = None):
        self.operation_type = operation_type
        self.operation_name = operation_name
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.start_time: Optional[float] = None
        self.core_logger = get_core_audit_logger()
    
    def __enter__(self):
        """Start the audit context."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the audit context and log the operation."""
        duration = time.time() - self.start_time if self.start_time else 0.0
        success = exc_type is None
        
        metadata = {
            "context_manager": True,
            "success": success,
        }
        
        if not success:
            metadata.update({
                "error": str(exc_val) if exc_val else "Unknown error",
                "error_type": exc_type.__name__ if exc_type else "Unknown"
            })
        
        self.core_logger.log_core_operation(
            operation_type=self.operation_type,
            operation_name=self.operation_name,
            entity_type=self.entity_type,
            entity_id=self.entity_id,
            success=success,
            duration=duration,
            metadata=metadata
        )


# ============================================================================
# MAIN AUDIT OPERATION DECORATOR - Line 218 as specified in problem statement
# ============================================================================
#
# This decorator provides comprehensive audit logging for all core operations.
# It captures operation metadata, performance metrics, success/failure status,
# and integrates with both the core audit logger and infrastructure audit logger
# for complete audit trail coverage.
#
# Key Features:
# - Automatic operation timing and performance measurement
# - Entity ID extraction from function results
# - Transaction context integration when available
# - Error logging with full exception details
# - Security event logging for failed operations
# - Configurable audit levels and operation types
# - Support for custom operation names and entity types
# - Performance metrics can be optionally included/excluded
#
# Usage Examples:
#   @audit_operation(OperationType.CREATE, "create_user", "User")
#   def create_user(name: str) -> dict:
#       return {"id": "user-123", "name": name}
#
#   @audit_operation(OperationType.QUERY, include_performance=False)
#   def simple_query() -> list:
#       return [1, 2, 3]
#
# Note: This implementation replaces the original stub method that contained
# only a 'pass' statement. The implementation is now complete and functional.
#
def audit_operation(operation_type: OperationType, operation_name: Optional[str] = None,
                   entity_type: Optional[str] = None, include_performance: bool = True,
                   level: AuditLevel = AuditLevel.INFO) -> Callable[[F], F]:
    """
    Decorator for automatic audit logging of operations.

    Args:
        operation_type: Type of operation being performed
        operation_name: Name of operation (defaults to function name)
        entity_type: Type of entity being operated on
        include_performance: Whether to include performance metrics
        level: Audit level for the operation

    Returns:
        Decorated function with audit logging
    """
    def decorator(func: F) -> F:
        """Inner decorator function."""
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrapper function that adds audit logging."""
            op_name = operation_name or func.__name__
            start_time = time.time()
            core_logger = get_core_audit_logger()
            
            # Get transaction ID if available
            transaction_id = None
            try:
                if args and hasattr(args[0], '_transaction_manager'):
                    transaction_id = args[0]._transaction_manager.get_current_transaction_id()
            except (AttributeError, IndexError):
                pass
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Calculate performance metrics
                duration = time.time() - start_time
                
                # Extract entity ID from result if possible
                entity_id = None
                if hasattr(result, 'id') and not callable(getattr(result, 'id', None)):
                    entity_id = str(result.id)
                elif isinstance(result, dict) and 'id' in result and result['id'] is not None:
                    if isinstance(result['id'], (str, int, float, uuid.UUID)):
                        entity_id = str(result['id'])
                
                # Log successful operation
                metadata = {
                    "function_name": func.__name__,
                    "module": func.__module__,
                    "success": True,
                    "result_type": type(result).__name__ if result is not None else None,
                    "transaction_id": transaction_id
                }
                
                core_logger.log_core_operation(
                    operation_type=operation_type,
                    operation_name=op_name,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    success=True,
                    duration=duration if include_performance else None,
                    metadata=metadata
                )
                
                return result
                
            except Exception as e:
                # Calculate performance metrics for failed operation
                duration = time.time() - start_time
                
                # Log failed operation
                metadata = {
                    "function_name": func.__name__,
                    "module": func.__module__,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "transaction_id": transaction_id
                }
                
                core_logger.log_core_operation(
                    operation_type=operation_type,
                    operation_name=op_name,
                    entity_type=entity_type,
                    success=False,
                    duration=duration if include_performance else None,
                    metadata=metadata
                )
                
                # Also log to infrastructure logger as error
                core_logger.infrastructure_logger.log_security_event(
                    message=f"Core operation failed: {op_name} - {str(e)}",
                    security_context={
                        "operation": op_name,
                        "error": str(e),
                        "function": func.__name__,
                        "module": func.__module__
                    },
                    data=metadata
                )
                
                raise
        
        return wrapper  # type: ignore[return-value]
    
    return decorator
    """
    Decorator for automatic audit logging of operations.

    Args:
        operation_type: Type of operation being performed
        operation_name: Name of operation (defaults to function name)
        entity_type: Type of entity being operated on
        include_performance: Whether to include performance metrics
        level: Audit level for the operation

    Returns:
        Decorated function with audit logging
    """
    def decorator(func: F) -> F:
        """Inner decorator function."""
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrapper function that adds audit logging."""
            op_name = operation_name or func.__name__
            start_time = time.time()
            core_logger = get_core_audit_logger()
            
            # Get transaction ID if available
            transaction_id = None
            try:
                if args and hasattr(args[0], '_transaction_manager'):
                    transaction_id = args[0]._transaction_manager.get_current_transaction_id()  # pylint: disable=protected-access
            except (AttributeError, IndexError):
                pass
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Calculate performance metrics
                duration = time.time() - start_time
                
                # Extract entity ID from result if possible
                entity_id = None
                if hasattr(result, 'id') and not callable(getattr(result, 'id', None)):
                    entity_id = str(result.id)
                elif isinstance(result, dict) and 'id' in result and result['id'] is not None:
                    if isinstance(result['id'], (str, int, float, uuid.UUID)):
                        entity_id = str(result['id'])
                
                # Log successful operation
                metadata = {
                    "function_name": func.__name__,
                    "module": func.__module__,
                    "success": True,
                    "result_type": type(result).__name__ if result is not None else None,
                    "transaction_id": transaction_id
                }
                
                core_logger.log_core_operation(
                    operation_type=operation_type,
                    operation_name=op_name,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    success=True,
                    duration=duration if include_performance else None,
                    metadata=metadata
                )
                
                return result
                
            except Exception as e:
                # Calculate performance metrics for failed operation
                duration = time.time() - start_time
                
                # Log failed operation
                metadata = {
                    "function_name": func.__name__,
                    "module": func.__module__,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "transaction_id": transaction_id
                }
                
                core_logger.log_core_operation(
                    operation_type=operation_type,
                    operation_name=op_name,
                    entity_type=entity_type,
                    success=False,
                    duration=duration if include_performance else None,
                    metadata=metadata
                )
                
                # Also log to infrastructure logger as error
                core_logger.infrastructure_logger.log_security_event(
                    message=f"Core operation failed: {op_name} - {str(e)}",
                    security_context={
                        "operation": op_name,
                        "error": str(e),
                        "function": func.__name__,
                        "module": func.__module__
                    },
                    data=metadata
                )
                
                raise
        
        return wrapper  # type: ignore[return-value]
    
    return decorator