"""
Structured Logging Configuration for SFM Service

This module provides comprehensive structured logging with correlation IDs,
performance tracking, and integration with the existing audit logging system.

Features:
- Structured JSON logging format
- Correlation ID tracking across requests
- Performance metrics integration
- Log level configuration
- Request/response logging
- Error tracking with context
"""

import logging
import json
import time
import uuid
from typing import Dict, Any, Optional, Union
from datetime import datetime
from contextlib import contextmanager
from functools import wraps
from dataclasses import dataclass, field

# Import existing audit logging for integration
from core.audit_logger import AuditLogger, AuditLevel, OperationType


@dataclass
class LogContext:
    """Context information for structured logging."""
    correlation_id: str
    user_id: Optional[str] = None
    operation: Optional[str] = None
    component: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SFMLogger:
    """
    Structured logger for SFM Service with correlation ID tracking.

    This logger provides structured logging with JSON format and automatic
    correlation ID tracking for request tracing.
    """

    def __init__(self, name: str, correlation_id: str = None):
        self.logger = logging.getLogger(name)
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.context = LogContext(correlation_id=self.correlation_id)

    def with_context(self, **kwargs) -> 'SFMLogger':
        """Create a new logger instance with additional context."""
        new_logger = SFMLogger(self.logger.name, self.correlation_id)
        new_logger.context = LogContext(
            correlation_id=self.correlation_id,
            user_id=kwargs.get('user_id', self.context.user_id),
            operation=kwargs.get('operation', self.context.operation),
            component=kwargs.get('component', self.context.component),
            request_id=kwargs.get('request_id', self.context.request_id),
            metadata={**self.context.metadata, **kwargs.get('metadata', {})}
        )
        return new_logger

    def info(self, message: str, **kwargs):
        """Log an info message with structured format."""
        self._log('INFO', message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log a warning message with structured format."""
        self._log('WARNING', message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log an error message with structured format."""
        self._log('ERROR', message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log a debug message with structured format."""
        self._log('DEBUG', message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log a critical message with structured format."""
        self._log('CRITICAL', message, **kwargs)

    def _log(self, level: str, message: str, **kwargs):
        """Internal method to format and log messages."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'correlation_id': self.correlation_id,
            'module': self.logger.name,
            'context': {
                'user_id': self.context.user_id,
                'operation': self.context.operation,
                'component': self.context.component,
                'request_id': self.context.request_id,
                'metadata': self.context.metadata
            },
            **kwargs
        }

        # Remove None values from context
        log_data['context'] = {
            k: v for k,
            v in log_data['context'].items() if v is not None}

        self.logger.log(getattr(logging, level), json.dumps(log_data))


class LoggingManager:
    """
    Central logging manager for SFM Service.

    Manages logging configuration, correlation ID tracking, and integration
    with monitoring systems.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.audit_logger = AuditLogger()
        self._configure_logging()

    def _default_config(self) -> Dict[str, Any]:
        """Default logging configuration."""
        return {
            'level': 'INFO',
            'format': 'json',
            'correlation_tracking': True,
            'performance_logging': True,
            'audit_integration': True
        }

    def _configure_logging(self):
        """Configure the logging system."""
        # Set up root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config['level']))

        # Configure handlers if needed
        if not root_logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(getattr(logging, self.config['level']))
            root_logger.addHandler(handler)

    def get_logger(self, name: str, correlation_id: str = None) -> SFMLogger:
        """Get a structured logger instance."""
        return SFMLogger(name, correlation_id)

    @contextmanager
    def operation_context(
            self,
            operation: str,
            component: str = None,
            **kwargs):
        """Context manager for operation logging."""
        correlation_id = kwargs.get('correlation_id', str(uuid.uuid4()))
        logger = self.get_logger(
            f"sfm.{component}" if component else "sfm.operation",
            correlation_id)
        logger = logger.with_context(
            operation=operation, component=component, **kwargs)

        start_time = time.time()
        logger.info(f"Operation started: {operation}",
                    operation_type="start",
                    **kwargs)

        try:
            yield logger
            duration = time.time() - start_time
            logger.info(f"Operation completed: {operation}",
                        operation_type="complete",
                        duration=duration,
                        **kwargs)

            # Log to audit system if enabled
            if self.config.get('audit_integration', True):
                self.audit_logger.log_operation(
                    operation_type=OperationType.SYSTEM,
                    operation_name=operation,
                    data={
                        'user_id': kwargs.get('user_id'),
                        'duration': duration,
                        'status': 'success'
                    }
                )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Operation failed: {operation}",
                         operation_type="error",
                         duration=duration,
                         error=str(e),
                         **kwargs)

            # Log to audit system if enabled
            if self.config.get('audit_integration', True):
                self.audit_logger.log_operation(
                    operation_type=OperationType.SYSTEM,
                    operation_name=operation,
                    data={
                        'user_id': kwargs.get('user_id'),
                        'duration': duration,
                        'status': 'error',
                        'error': str(e)
                    }
                )
            raise


def monitor_performance(operation_name: str = None):
    """
    Decorator for automatic performance monitoring and logging.

    Args:
        operation_name: Name of the operation being monitored
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation = operation_name or f"{func.__module__}.{func.__name__}"

            # Get logging manager (should be configured globally)
            logging_manager = LoggingManager()

            with logging_manager.operation_context(operation, component=func.__module__):
                return func(*args, **kwargs)

        return wrapper
    return decorator


# Global logging manager instance
_logging_manager = None


def get_logging_manager() -> LoggingManager:
    """Get the global logging manager instance."""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()
    return _logging_manager


def get_logger(name: str, correlation_id: str = None) -> SFMLogger:
    """Get a structured logger instance."""
    return get_logging_manager().get_logger(name, correlation_id)


def configure_logging(config: Dict[str, Any]):
    """Configure the global logging system."""
    global _logging_manager
    _logging_manager = LoggingManager(config)
