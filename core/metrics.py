"""
Enhanced Metrics System for SFM Service

This module provides comprehensive metrics collection with Prometheus integration,
building on the existing performance_metrics.py system.

Features:
- Prometheus metrics export
- Request/response metrics
- Business logic metrics
- Performance counters
- Custom metric collectors
- Metric persistence
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager
import threading
from collections import defaultdict, deque

from core.logging_config import get_logger
from core.performance_metrics import MetricsCollector as CoreMetricsCollector, MetricType

# Optional Prometheus metrics import
try:
    from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


@dataclass
class MetricConfig:
    """Configuration for metrics collection."""
    enabled: bool = True
    export_port: int = 9090
    collection_interval: int = 15
    prometheus_enabled: bool = PROMETHEUS_AVAILABLE
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


class PrometheusMetrics:
    """Prometheus metrics for SFM Service."""

    def __init__(self, registry: CollectorRegistry = None):
        self.registry = registry or CollectorRegistry()
        self.logger = get_logger("metrics.prometheus")

        if not PROMETHEUS_AVAILABLE:
            self.logger.warning(
                "Prometheus client not available - metrics disabled")
            return

        # Application metrics
        self.requests_total = Counter(
            'sfm_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )

        self.request_duration = Histogram(
            'sfm_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )

        self.active_connections = Gauge(
            'sfm_active_connections',
            'Number of active database connections',
            registry=self.registry
        )

        # Business logic metrics
        self.entities_created = Counter(
            'sfm_entities_created_total',
            'Total entities created',
            ['entity_type'],
            registry=self.registry
        )

        self.relationships_created = Counter(
            'sfm_relationships_created_total',
            'Total relationships created',
            ['relationship_type'],
            registry=self.registry
        )

        self.queries_executed = Counter(
            'sfm_queries_executed_total',
            'Total queries executed',
            ['query_type'],
            registry=self.registry
        )

        self.query_duration = Histogram(
            'sfm_query_duration_seconds',
            'Query execution duration in seconds',
            ['query_type'],
            registry=self.registry
        )

        # Cache metrics
        self.cache_hits = Counter(
            'sfm_cache_hits_total',
            'Total cache hits',
            ['cache_type'],
            registry=self.registry
        )

        self.cache_misses = Counter(
            'sfm_cache_misses_total',
            'Total cache misses',
            ['cache_type'],
            registry=self.registry
        )

        # System metrics
        self.system_errors = Counter(
            'sfm_system_errors_total',
            'Total system errors',
            ['error_type'],
            registry=self.registry
        )

        self.system_info = Info(
            'sfm_system_info',
            'System information',
            registry=self.registry
        )

        # Performance metrics
        self.operation_duration = Histogram(
            'sfm_operation_duration_seconds',
            'Operation duration in seconds',
            ['operation_type', 'operation_name'],
            registry=self.registry
        )

        self.memory_usage = Gauge(
            'sfm_memory_usage_bytes',
            'Memory usage in bytes',
            ['type'],
            registry=self.registry
        )

        self.logger.info("Prometheus metrics initialized")

    def is_available(self) -> bool:
        """Check if Prometheus metrics are available."""
        return PROMETHEUS_AVAILABLE

    def record_request(
            self,
            method: str,
            endpoint: str,
            status: int,
            duration: float):
        """Record HTTP request metrics."""
        if not self.is_available():
            return

        self.requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status).inc()
        self.request_duration.labels(
            method=method, endpoint=endpoint).observe(duration)

    def record_entity_creation(self, entity_type: str):
        """Record entity creation."""
        if not self.is_available():
            return

        self.entities_created.labels(entity_type=entity_type).inc()

    def record_relationship_creation(self, relationship_type: str):
        """Record relationship creation."""
        if not self.is_available():
            return

        self.relationships_created.labels(
            relationship_type=relationship_type).inc()

    def record_query_execution(self, query_type: str, duration: float):
        """Record query execution."""
        if not self.is_available():
            return

        self.queries_executed.labels(query_type=query_type).inc()
        self.query_duration.labels(query_type=query_type).observe(duration)

    def record_cache_hit(self, cache_type: str):
        """Record cache hit."""
        if not self.is_available():
            return

        self.cache_hits.labels(cache_type=cache_type).inc()

    def record_cache_miss(self, cache_type: str):
        """Record cache miss."""
        if not self.is_available():
            return

        self.cache_misses.labels(cache_type=cache_type).inc()

    def record_system_error(self, error_type: str):
        """Record system error."""
        if not self.is_available():
            return

        self.system_errors.labels(error_type=error_type).inc()

    def record_operation_duration(
            self,
            operation_type: str,
            operation_name: str,
            duration: float):
        """Record operation duration."""
        if not self.is_available():
            return

        self.operation_duration.labels(
            operation_type=operation_type,
            operation_name=operation_name
        ).observe(duration)

    def update_active_connections(self, count: int):
        """Update active connections gauge."""
        if not self.is_available():
            return

        self.active_connections.set(count)

    def update_memory_usage(self, usage_type: str, bytes_used: int):
        """Update memory usage gauge."""
        if not self.is_available():
            return

        self.memory_usage.labels(type=usage_type).set(bytes_used)

    def set_system_info(self, info: Dict[str, str]):
        """Set system information."""
        if not self.is_available():
            return

        self.system_info.info(info)

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        if not self.is_available():
            return ""

        return generate_latest(self.registry).decode('utf-8')


class MetricsCollector:
    """
    Enhanced metrics collector that integrates with existing performance metrics
    and adds Prometheus support.
    """

    def __init__(self, config: MetricConfig = None):
        self.config = config or MetricConfig()
        self.logger = get_logger("metrics.collector")
        self.performance_metrics = CoreMetricsCollector()
        self.prometheus_metrics = PrometheusMetrics(
        ) if self.config.prometheus_enabled else None
        self._lock = threading.Lock()
        self._custom_collectors: Dict[str, Callable] = {}

        if self.prometheus_metrics:
            self.logger.info(
                "Metrics collector initialized with Prometheus support")
        else:
            self.logger.info(
                "Metrics collector initialized without Prometheus support")

    def record_request(
            self,
            method: str,
            endpoint: str,
            status: int,
            duration: float):
        """Record HTTP request metrics."""
        # Record in performance metrics
        self.performance_metrics.record_operation(
            f"http_{method}_{endpoint}",
            duration
        )

        # Record in Prometheus if available
        if self.prometheus_metrics:
            self.prometheus_metrics.record_request(
                method, endpoint, status, duration)

    def record_entity_operation(
            self,
            operation: str,
            entity_type: str,
            duration: float):
        """Record entity operation metrics."""
        # Record in performance metrics
        self.performance_metrics.record_operation(
            f"entity_{operation}_{entity_type}",
            duration
        )

        # Record in Prometheus if available
        if self.prometheus_metrics:
            if operation == "create":
                self.prometheus_metrics.record_entity_creation(entity_type)
            self.prometheus_metrics.record_operation_duration(
                "entity", f"{operation}_{entity_type}", duration
            )

    def record_relationship_operation(
            self,
            operation: str,
            relationship_type: str,
            duration: float):
        """Record relationship operation metrics."""
        # Record in performance metrics
        self.performance_metrics.record_operation(
            f"relationship_{operation}_{relationship_type}",
            duration
        )

        # Record in Prometheus if available
        if self.prometheus_metrics:
            if operation == "create":
                self.prometheus_metrics.record_relationship_creation(
                    relationship_type)
            self.prometheus_metrics.record_operation_duration(
                "relationship", f"{operation}_{relationship_type}", duration
            )

    def record_query(self, query_type: str, duration: float):
        """Record query execution metrics."""
        # Record in performance metrics
        self.performance_metrics.record_operation(
            f"query_{query_type}",
            duration
        )

        # Record in Prometheus if available
        if self.prometheus_metrics:
            self.prometheus_metrics.record_query_execution(
                query_type, duration)

    def record_cache_operation(self, operation: str, cache_type: str):
        """Record cache operation metrics."""
        # Record in performance metrics
        self.performance_metrics.increment_counter(
            f"cache_{operation}_{cache_type}")

        # Record in Prometheus if available
        if self.prometheus_metrics:
            if operation == "hit":
                self.prometheus_metrics.record_cache_hit(cache_type)
            elif operation == "miss":
                self.prometheus_metrics.record_cache_miss(cache_type)

    def record_error(self, error_type: str, error_message: str = None):
        """Record system error metrics."""
        # Record in performance metrics
        self.performance_metrics.increment_counter(f"error_{error_type}")

        # Record in Prometheus if available
        if self.prometheus_metrics:
            self.prometheus_metrics.record_system_error(error_type)

    def update_system_metrics(self, metrics: Dict[str, Any]):
        """Update system-level metrics."""
        if self.prometheus_metrics:
            # Update active connections if provided
            if 'active_connections' in metrics:
                self.prometheus_metrics.update_active_connections(
                    metrics['active_connections'])

            # Update memory usage if provided
            if 'memory_usage' in metrics:
                for usage_type, bytes_used in metrics['memory_usage'].items():
                    self.prometheus_metrics.update_memory_usage(
                        usage_type, bytes_used)

    def add_custom_collector(self, name: str, collector: Callable):
        """Add a custom metrics collector."""
        with self._lock:
            self._custom_collectors[name] = collector

    def collect_custom_metrics(self):
        """Collect metrics from custom collectors."""
        with self._lock:
            for name, collector in self._custom_collectors.items():
                try:
                    collector()
                except Exception as e:
                    self.logger.error(f"Error in custom collector '{name}'",
                                      error=str(e))

    def get_prometheus_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        if self.prometheus_metrics:
            return self.prometheus_metrics.get_metrics()
        return ""

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        return self.performance_metrics.get_summary_stats()


def monitor_performance(operation_type: str = None, entity_type: str = None):
    """
    Decorator for automatic performance monitoring.

    Args:
        operation_type: Type of operation (e.g., 'entity', 'relationship', 'query')
        entity_type: Type of entity being operated on
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_type or f"{func.__module__}.{func.__name__}"

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Get metrics collector
                metrics = get_metrics_collector()

                # Record operation metrics
                if operation_type == "entity" and entity_type:
                    metrics.record_entity_operation(
                        "execute", entity_type, duration)
                elif operation_type == "relationship" and entity_type:
                    metrics.record_relationship_operation(
                        "execute", entity_type, duration)
                elif operation_type == "query":
                    metrics.record_query(entity_type or "unknown", duration)
                else:
                    # Generic operation recording
                    if metrics.prometheus_metrics:
                        metrics.prometheus_metrics.record_operation_duration(
                            operation_type or "generic",
                            func.__name__,
                            duration
                        )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Record error metrics
                metrics = get_metrics_collector()
                metrics.record_error(type(e).__name__, str(e))

                raise

        return wrapper
    return decorator


# Global metrics collector instance
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def configure_metrics(config: MetricConfig):
    """Configure the global metrics system."""
    global _metrics_collector
    _metrics_collector = MetricsCollector(config)
