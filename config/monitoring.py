"""
Monitoring Configuration for SFM Service

This module provides configuration settings for the comprehensive
monitoring and logging system.

Features:
- Logging configuration
- Metrics collection settings
- Health check configuration
- Alert rules and thresholds
- Distributed tracing settings
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(Enum):
    """Log formats."""
    JSON = "json"
    TEXT = "text"


@dataclass
class LoggingConfig:
    """Configuration for logging system."""
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.JSON
    correlation_tracking: bool = True
    performance_logging: bool = True
    audit_integration: bool = True
    log_to_file: bool = False
    log_file_path: str = "/var/log/sfm/app.log"
    log_rotation_size: str = "100MB"
    log_rotation_count: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'level': self.level.value,
            'format': self.format.value,
            'correlation_tracking': self.correlation_tracking,
            'performance_logging': self.performance_logging,
            'audit_integration': self.audit_integration,
            'log_to_file': self.log_to_file,
            'log_file_path': self.log_file_path,
            'log_rotation_size': self.log_rotation_size,
            'log_rotation_count': self.log_rotation_count
        }


@dataclass
class MetricsConfig:
    """Configuration for metrics collection."""
    enabled: bool = True
    export_port: int = 9090
    collection_interval: int = 15
    prometheus_enabled: bool = True
    custom_metrics: Dict[str, Any] = field(default_factory=dict)  # type: ignore  # Dataclass field with default_factory
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'enabled': self.enabled,
            'export_port': self.export_port,
            'collection_interval': self.collection_interval,
            'prometheus_enabled': self.prometheus_enabled,
            'custom_metrics': self.custom_metrics
        }


@dataclass
class HealthCheckConfig:
    """Configuration for health checking."""
    enabled: bool = True
    check_interval: int = 30
    timeout: int = 5
    database_check: bool = True
    redis_check: bool = True
    system_resources_check: bool = True
    service_readiness_check: bool = True
    
    # Thresholds for system resource checks
    cpu_threshold: float = 90.0
    memory_threshold: float = 90.0
    disk_threshold: float = 90.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'enabled': self.enabled,
            'check_interval': self.check_interval,
            'timeout': self.timeout,
            'database_check': self.database_check,
            'redis_check': self.redis_check,
            'system_resources_check': self.system_resources_check,
            'service_readiness_check': self.service_readiness_check,
            'cpu_threshold': self.cpu_threshold,
            'memory_threshold': self.memory_threshold,
            'disk_threshold': self.disk_threshold
        }


@dataclass
class TracingConfig:
    """Configuration for distributed tracing."""
    enabled: bool = True
    sample_rate: float = 0.1
    jaeger_endpoint: str = "http://jaeger:14268"
    service_name: str = "sfm-service"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'enabled': self.enabled,
            'sample_rate': self.sample_rate,
            'jaeger_endpoint': self.jaeger_endpoint,
            'service_name': self.service_name
        }


@dataclass
class AlertConfig:
    """Configuration for alerting."""
    enabled: bool = True
    alert_rules: List[Dict[str, Any]] = field(default_factory=list)  # type: ignore  # Dataclass field with default_factory
    notification_channels: List[str] = field(default_factory=list)  # type: ignore  # Dataclass field with default_factory
    escalation_policies: Dict[str, Any] = field(default_factory=dict)  # type: ignore  # Dataclass field with default_factory
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'enabled': self.enabled,
            'alert_rules': self.alert_rules,
            'notification_channels': self.notification_channels,
            'escalation_policies': self.escalation_policies
        }


@dataclass
class MiddlewareConfig:
    """Configuration for monitoring middleware."""
    correlation_id_enabled: bool = True
    error_tracking_enabled: bool = True
    metrics_enabled: bool = True
    lightweight_metrics: bool = False
    
    # Request/response logging
    log_requests: bool = True
    log_responses: bool = True
    log_headers: bool = False
    log_body: bool = False
    
    # Excluded paths
    excluded_paths: List[str] = field(default_factory=lambda: ['/health', '/metrics'])
    
    # Error tracking
    capture_stack_traces: bool = True
    log_error_details: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'correlation_id_enabled': self.correlation_id_enabled,
            'error_tracking_enabled': self.error_tracking_enabled,
            'metrics_enabled': self.metrics_enabled,
            'lightweight_metrics': self.lightweight_metrics,
            'log_requests': self.log_requests,
            'log_responses': self.log_responses,
            'log_headers': self.log_headers,
            'log_body': self.log_body,
            'excluded_paths': self.excluded_paths,
            'capture_stack_traces': self.capture_stack_traces,
            'log_error_details': self.log_error_details
        }


@dataclass
class MonitoringConfig:
    """Complete monitoring configuration."""
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    health_check: HealthCheckConfig = field(default_factory=HealthCheckConfig)
    tracing: TracingConfig = field(default_factory=TracingConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    middleware: MiddlewareConfig = field(default_factory=MiddlewareConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'logging': self.logging.to_dict(),
            'metrics': self.metrics.to_dict(),
            'health_check': self.health_check.to_dict(),
            'tracing': self.tracing.to_dict(),
            'alerts': self.alerts.to_dict(),
            'middleware': self.middleware.to_dict()
        }


# Default configuration
DEFAULT_MONITORING_CONFIG = MonitoringConfig()

# Environment-specific configurations
DEVELOPMENT_CONFIG = MonitoringConfig(
    logging=LoggingConfig(
        level=LogLevel.DEBUG,
        format=LogFormat.TEXT,
        log_to_file=False
    ),
    metrics=MetricsConfig(
        collection_interval=10
    ),
    health_check=HealthCheckConfig(
        check_interval=15
    ),
    tracing=TracingConfig(
        sample_rate=1.0  # Sample all requests in development
    ),
    middleware=MiddlewareConfig(
        log_headers=True,
        log_body=True
    )
)

PRODUCTION_CONFIG = MonitoringConfig(
    logging=LoggingConfig(
        level=LogLevel.INFO,
        format=LogFormat.JSON,
        log_to_file=True
    ),
    metrics=MetricsConfig(
        collection_interval=15
    ),
    health_check=HealthCheckConfig(
        check_interval=30
    ),
    tracing=TracingConfig(
        sample_rate=0.1  # Sample 10% of requests in production
    ),
    middleware=MiddlewareConfig(
        log_headers=False,
        log_body=False
    )
)

# Alert rules for production
PRODUCTION_ALERT_RULES: List[Dict[str, Any]] = [
    {
        "name": "HighErrorRate",
        "expr": "rate(sfm_system_errors_total[5m]) > 0.1",
        "for": "5m",
        "labels": {
            "severity": "warning"
        },
        "annotations": {
            "summary": "High error rate detected",
            "description": "Error rate is above 10% for 5 minutes"
        }
    },
    {
        "name": "HighResponseTime",
        "expr": "histogram_quantile(0.95, sfm_request_duration_seconds_bucket) > 2.0",
        "for": "5m",
        "labels": {
            "severity": "warning"
        },
        "annotations": {
            "summary": "High response time detected",
            "description": "95th percentile response time is above 2 seconds"
        }
    },
    {
        "name": "ServiceDown",
        "expr": "up{job=\"sfm-service\"} == 0",
        "for": "1m",
        "labels": {
            "severity": "critical"
        },
        "annotations": {
            "summary": "SFM service is down",
            "description": "SFM service has been down for more than 1 minute"
        }
    },
    {
        "name": "HighMemoryUsage",
        "expr": "sfm_memory_usage_bytes{type=\"heap\"} / sfm_memory_usage_bytes{type=\"total\"} > 0.8",
        "for": "10m",
        "labels": {
            "severity": "warning"
        },
        "annotations": {
            "summary": "High memory usage detected",
            "description": "Memory usage is above 80% for 10 minutes"
        }
    }
]

# Update production config with alert rules
PRODUCTION_CONFIG.alerts.alert_rules = PRODUCTION_ALERT_RULES


def get_monitoring_config(environment: Optional[str] = None) -> MonitoringConfig:
    """
    Get monitoring configuration based on environment.
    
    Args:
        environment: Environment name (development, production, etc.)
    
    Returns:
        MonitoringConfig instance
    """
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return PRODUCTION_CONFIG
    elif environment == "development":
        return DEVELOPMENT_CONFIG
    else:
        return DEFAULT_MONITORING_CONFIG


def load_monitoring_config_from_env() -> MonitoringConfig:
    """
    Load monitoring configuration from environment variables.
    
    Returns:
        MonitoringConfig instance with values from environment
    """
    config = get_monitoring_config()
    
    # Override with environment variables if present
    log_level = os.getenv("LOG_LEVEL")
    if log_level:
        config.logging.level = LogLevel(log_level)
    
    log_format = os.getenv("LOG_FORMAT")
    if log_format:
        config.logging.format = LogFormat(log_format)
    
    metrics_enabled = os.getenv("METRICS_ENABLED")
    if metrics_enabled:
        config.metrics.enabled = metrics_enabled.lower() == "true"
    
    metrics_port = os.getenv("METRICS_PORT")
    if metrics_port:
        config.metrics.export_port = int(metrics_port)
    
    health_check_enabled = os.getenv("HEALTH_CHECK_ENABLED")
    if health_check_enabled:
        config.health_check.enabled = health_check_enabled.lower() == "true"
    
    tracing_enabled = os.getenv("TRACING_ENABLED")
    if tracing_enabled:
        config.tracing.enabled = tracing_enabled.lower() == "true"
    
    tracing_sample_rate = os.getenv("TRACING_SAMPLE_RATE")
    if tracing_sample_rate:
        config.tracing.sample_rate = float(tracing_sample_rate)
    
    jaeger_endpoint = os.getenv("JAEGER_ENDPOINT")
    if jaeger_endpoint:
        config.tracing.jaeger_endpoint = jaeger_endpoint
    
    return config


# Export commonly used configurations
__all__ = [
    'MonitoringConfig',
    'LoggingConfig',
    'MetricsConfig',
    'HealthCheckConfig',
    'TracingConfig',
    'AlertConfig',
    'MiddlewareConfig',
    'DEFAULT_MONITORING_CONFIG',
    'DEVELOPMENT_CONFIG',
    'PRODUCTION_CONFIG',
    'get_monitoring_config',
    'load_monitoring_config_from_env'
]