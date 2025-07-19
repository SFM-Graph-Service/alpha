"""
Audit Logging System for SFM Service

This module provides comprehensive audit logging for all SFM operations,
enabling security compliance, monitoring, and forensic analysis.

Features:
- Structured audit logging for all operations
- Security event logging with context
- Performance metrics integration
- Configurable log levels and destinations
- Integration with transaction management
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional, Callable, TypeVar
from enum import Enum

logger = logging.getLogger(__name__)


class AuditLevel(Enum):
    """Audit logging levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SECURITY = "security"
    PERFORMANCE = "performance"


class OperationType(Enum):
    """Types of operations for audit logging."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"
    ANALYSIS = "analysis"
    SYSTEM = "system"
    SECURITY = "security"


@dataclass
class AuditEvent:  # pylint: disable=too-many-instance-attributes
    """Audit event record."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    operation_type: OperationType = OperationType.SYSTEM
    operation_name: str = ""
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    user_context: Optional[str] = None
    session_id: Optional[str] = None
    transaction_id: Optional[str] = None
    level: AuditLevel = AuditLevel.INFO
    message: str = ""
    data: Dict[str, Any] = field(default_factory=lambda: {})
    performance_metrics: Dict[str, float] = field(default_factory=lambda: {})
    error_details: Optional[str] = None
    security_context: Dict[str, Any] = field(default_factory=lambda: {})

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary for logging."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "operation_type": self.operation_type.value,
            "operation_name": self.operation_name,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "user_context": self.user_context,
            "session_id": self.session_id,
            "transaction_id": self.transaction_id,
            "level": self.level.value,
            "message": self.message,
            "data": self.data,
            "performance_metrics": self.performance_metrics,
            "error_details": self.error_details,
            "security_context": self.security_context
        }


class AuditLogger:
    """Audit logging manager."""
    def __init__(self, logger_name: str = "sfm.audit"):
        self.audit_logger = logging.getLogger(logger_name)
        self._current_user_context: Optional[str] = None
        self._current_session_id: Optional[str] = None
        self._audit_history: List[AuditEvent] = []
        # Configure audit logger formatting
        if not self.audit_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - AUDIT - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.audit_logger.addHandler(handler)
            self.audit_logger.setLevel(logging.INFO)
    def set_user_context(self, user_id: str, session_id: Optional[str] = None):
        """Set current user context for audit logging."""
        self._current_user_context = user_id
        self._current_session_id = session_id or str(uuid.uuid4())
    def clear_user_context(self):
        """Clear current user context."""
        self._current_user_context = None
        self._current_session_id = None
    def log_event(self, event: AuditEvent):
        """Log an audit event."""
        # Add current context if not specified
        if not event.user_context:
            event.user_context = self._current_user_context
        if not event.session_id:
            event.session_id = self._current_session_id
        # Log the event
        log_data = event.to_dict()
        if event.level == AuditLevel.ERROR:
            self.audit_logger.error("AUDIT: %s", event.message, extra={"audit_data": log_data})
        elif event.level == AuditLevel.WARNING:
            self.audit_logger.warning("AUDIT: %s", event.message, extra={"audit_data": log_data})
        elif event.level == AuditLevel.SECURITY:
            self.audit_logger.warning("SECURITY: %s", event.message, extra={"audit_data": log_data})
        else:
            self.audit_logger.info("AUDIT: %s", event.message, extra={"audit_data": log_data})
        # Store in history (limited size)
        self._audit_history.append(event)
        if len(self._audit_history) > 1000:
            self._audit_history = self._audit_history[-500:]

    def log_operation(self, operation_type: OperationType, operation_name: str,  # pylint: disable=too-many-arguments,too-many-positional-arguments
                     entity_type: Optional[str] = None, entity_id: Optional[str] = None,
                     message: Optional[str] = None, data: Optional[Dict[str, Any]] = None,
                     level: AuditLevel = AuditLevel.INFO,
                     transaction_id: Optional[str] = None):
        """Log a standard operation."""
        event = AuditEvent(
            operation_type=operation_type,
            operation_name=operation_name,
            entity_type=entity_type,
            entity_id=entity_id,
            message=message or f"{operation_type.value.title()} {operation_name}",
            data=data or {},
            level=level,
            transaction_id=transaction_id
        )
        self.log_event(event)
    def log_security_event(self, message: str, security_context: Dict[str, Any],
                          operation_name: str = "security_validation",
                          data: Optional[Dict[str, Any]] = None):  # pylint: disable=too-many-arguments,too-many-positional-arguments
        """Log a security-related event."""
        event = AuditEvent(
            operation_type=OperationType.SECURITY,
            operation_name=operation_name,
            message=message,
            data=data or {},
            level=AuditLevel.SECURITY,
            security_context=security_context
        )
        self.log_event(event)

    def log_performance_event(self, operation_name: str, duration: float,  # pylint: disable=too-many-arguments,too-many-positional-arguments
                            additional_metrics: Optional[Dict[str, float]] = None,
                            entity_type: Optional[str] = None,
                            entity_id: Optional[str] = None):
        """Log a performance-related event."""
        metrics = {"duration_seconds": duration}
        if additional_metrics:
            metrics.update(additional_metrics)
        event = AuditEvent(
            operation_type=OperationType.SYSTEM,
            operation_name=operation_name,
            entity_type=entity_type,
            entity_id=entity_id,
            message=f"Performance: {operation_name} took {duration:.3f}s",
            level=AuditLevel.PERFORMANCE,
            performance_metrics=metrics
        )
        self.log_event(event)

    def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit logging statistics."""
        if not self._audit_history:
            return {
                "total_events": 0,
                "events_by_type": {},
                "events_by_level": {},
                "recent_events": 0
            }
        events_by_type: Dict[str, int] = {}
        events_by_level: Dict[str, int] = {}
        for event in self._audit_history:
            op_type = event.operation_type.value
            level = event.level.value
            events_by_type[op_type] = events_by_type.get(op_type, 0) + 1
            events_by_level[level] = events_by_level.get(level, 0) + 1
        # Count recent events (last hour)
        recent_threshold = datetime.now().timestamp() - 3600
        recent_events = sum(1 for event in self._audit_history
                          if datetime.fromisoformat(event.timestamp).timestamp() > recent_threshold)
        return {
            "total_events": len(self._audit_history),
            "events_by_type": events_by_type,
            "events_by_level": events_by_level,
            "recent_events": recent_events
        }


# Global audit logger instance
_global_audit_logger = AuditLogger()


F = TypeVar("F", bound=Callable[..., Any])

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
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            op_name = operation_name or func.__name__
            start_time = time.time()
            # Get transaction ID if available (from transaction manager)
            transaction_id = None
            try:
                # Try to get transaction ID from first argument if it's a service instance
                if args and hasattr(args[0], '_transaction_manager'):
                    transaction_id = args[0]._transaction_manager.get_current_transaction_id()  # pylint: disable=protected-access
            except (AttributeError, IndexError):
                pass
            try:
                # Execute the function
                result = func(*args, **kwargs)
                # Log successful operation
                duration = time.time() - start_time
                success_data: Dict[str, Any] = {"success": True}
                # Try to extract entity ID from result
                entity_id = None
                if hasattr(result, 'id') and not callable(getattr(result, 'id', None)):
                    entity_id = str(result.id)
                elif isinstance(result, dict) and 'id' in result and result['id'] is not None:
                    if isinstance(result['id'], (str, int, float, uuid.UUID)):
                        entity_id = str(result['id'])
                    else:
                        entity_id = None
                _global_audit_logger.log_operation(
                    operation_type=operation_type,
                    operation_name=op_name,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    message=f"Successfully completed {op_name}",
                    data=success_data,
                    level=level,
                    transaction_id=transaction_id
                )
                if include_performance:
                    _global_audit_logger.log_performance_event(
                        operation_name=op_name,
                        duration=duration,
                        entity_type=entity_type,
                        entity_id=entity_id
                    )

                return result  # type: ignore[return-value]
            except Exception as e:
                # Log failed operation
                duration = time.time() - start_time
                error_data: Dict[str, Any] = {"success": False, "error": str(e)}
                event = AuditEvent(
                    operation_type=operation_type,
                    operation_name=op_name,
                    entity_type=entity_type,
                    message=f"Failed to complete {op_name}: {str(e)}",
                    data=error_data,
                    level=AuditLevel.ERROR,
                    transaction_id=transaction_id,
                    error_details=str(e),
                    performance_metrics={"duration_seconds": duration}
                )
                _global_audit_logger.log_event(event)

                raise

        return wrapper  # type: ignore[return-value]
    return decorator


# Convenience functions for common operations
def log_operation(operation_type: OperationType, operation_name: str, **kwargs: Any) -> None:
    """Log an operation using the global audit logger."""
    _global_audit_logger.log_operation(operation_type, operation_name, **kwargs)


def log_security_event(message: str, security_context: Dict[str, Any], **kwargs: Any) -> None:
    """Log a security event using the global audit logger."""
    _global_audit_logger.log_security_event(message, security_context, **kwargs)


def log_performance_event(operation_name: str, duration: float, **kwargs: Any) -> None:
    """Log a performance event using the global audit logger."""
    _global_audit_logger.log_performance_event(operation_name, duration, **kwargs)


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger."""
    return _global_audit_logger


def set_user_context(user_id: str, session_id: Optional[str] = None):
    """Set user context for the global audit logger."""
    _global_audit_logger.set_user_context(user_id, session_id)


def clear_user_context():
    """Clear user context for the global audit logger."""
    _global_audit_logger.clear_user_context()
