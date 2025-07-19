"""
Performance Metrics Collection for SFM Service

This module provides comprehensive performance monitoring and metrics
collection for SFM operations.

Features:
- Operation timing and performance tracking
- Resource usage monitoring
- System health metrics
- Trend analysis and reporting
- Integration with audit logging
"""

import time
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Deque
from enum import Enum

import logging
logger = logging.getLogger(__name__)

# Optional psutil import for system metrics
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False
    logger.info("psutil not available, system resource monitoring disabled")


class MetricType(Enum):
    """Types of metrics collected."""
    COUNTER = "counter"
    TIMER = "timer"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class MetricValue:
    """A single metric measurement."""
    value: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a specific operation or time period."""
    operation_count: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    avg_duration: float = 0.0
    success_count: int = 0
    error_count: int = 0
    last_execution: Optional[float] = None
    
    def update(self, duration: float, success: bool = True):
        """Update metrics with a new measurement."""
        self.operation_count += 1
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
        self.avg_duration = self.total_duration / self.operation_count
        self.last_execution = time.time()
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation_count": self.operation_count,
            "total_duration": self.total_duration,
            "min_duration": self.min_duration if self.min_duration != float('inf') else 0.0,
            "max_duration": self.max_duration,
            "avg_duration": self.avg_duration,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / self.operation_count if self.operation_count > 0 else 0.0,
            "last_execution": self.last_execution
        }


@dataclass
class SystemResourceMetrics:
    """System resource usage metrics."""
    cpu_percent: float = 0.0
    memory_usage_mb: float = 0.0
    memory_percent: float = 0.0
    disk_io_read_mb: float = 0.0
    disk_io_write_mb: float = 0.0
    network_bytes_sent: float = 0.0
    network_bytes_recv: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    @classmethod
    def capture_current(cls) -> 'SystemResourceMetrics':
        """Capture current system resource usage."""
        if not PSUTIL_AVAILABLE:
            return cls()  # Return empty metrics if psutil not available
            
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            net_io = psutil.net_io_counters()
            
            return cls(
                cpu_percent=cpu_percent,
                memory_usage_mb=memory.used / (1024 * 1024),
                memory_percent=memory.percent,
                disk_io_read_mb=(disk_io.read_bytes if disk_io else 0) / (1024 * 1024),
                disk_io_write_mb=(disk_io.write_bytes if disk_io else 0) / (1024 * 1024),
                network_bytes_sent=(net_io.bytes_sent if net_io else 0) / (1024 * 1024),
                network_bytes_recv=(net_io.bytes_recv if net_io else 0) / (1024 * 1024)
            )
        except Exception as e:
            logger.warning(f"Failed to capture system metrics: {e}")
            return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cpu_percent": self.cpu_percent,
            "memory_usage_mb": self.memory_usage_mb,
            "memory_percent": self.memory_percent,
            "disk_io_read_mb": self.disk_io_read_mb,
            "disk_io_write_mb": self.disk_io_write_mb,
            "network_bytes_sent_mb": self.network_bytes_sent,
            "network_bytes_recv_mb": self.network_bytes_recv,
            "timestamp": self.timestamp
        }


class MetricsCollector:
    """Centralized metrics collection and management."""
    
    def __init__(self, max_history_size: int = 1000):
        self._metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self._custom_metrics: Dict[str, Deque[MetricValue]] = defaultdict(lambda: deque(maxlen=max_history_size))
        self._system_metrics: Deque[SystemResourceMetrics] = deque(maxlen=max_history_size)
        self._lock = threading.Lock()
        self._start_time = time.time()
        self._enabled = True
        
        # Start background system monitoring
        self._start_system_monitoring()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable metrics collection."""
        self._enabled = enabled
    
    def record_operation(self, operation_name: str, duration: float, success: bool = True,
                        metadata: Optional[Dict[str, Any]] = None):
        """Record an operation's performance metrics."""
        if not self._enabled:
            return
            
        with self._lock:
            self._metrics[operation_name].update(duration, success)
            
            # Store detailed measurement
            self._custom_metrics[f"{operation_name}_duration"].append(
                MetricValue(duration, metadata=metadata or {})
            )
    
    def increment_counter(self, counter_name: str, value: float = 1.0,
                         metadata: Optional[Dict[str, Any]] = None):
        """Increment a counter metric."""
        if not self._enabled:
            return
            
        with self._lock:
            recent_values = self._custom_metrics[counter_name]
            current_value = recent_values[-1].value if recent_values else 0.0
            self._custom_metrics[counter_name].append(
                MetricValue(current_value + value, metadata=metadata or {})
            )
    
    def set_gauge(self, gauge_name: str, value: float,
                  metadata: Optional[Dict[str, Any]] = None):
        """Set a gauge metric value."""
        if not self._enabled:
            return
            
        with self._lock:
            self._custom_metrics[gauge_name].append(
                MetricValue(value, metadata=metadata or {})
            )
    
    def record_histogram(self, histogram_name: str, value: float,
                        metadata: Optional[Dict[str, Any]] = None):
        """Record a value in a histogram metric."""
        if not self._enabled:
            return
            
        with self._lock:
            self._custom_metrics[histogram_name].append(
                MetricValue(value, metadata=metadata or {})
            )
    
    def get_operation_metrics(self, operation_name: str) -> Dict[str, Any]:
        """Get performance metrics for a specific operation."""
        with self._lock:
            if operation_name in self._metrics:
                return self._metrics[operation_name].to_dict()
            return {}
    
    def get_all_operation_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics for all operations."""
        with self._lock:
            return {name: metrics.to_dict() for name, metrics in self._metrics.items()}
    
    def get_custom_metric(self, metric_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get custom metric values."""
        with self._lock:
            values = list(self._custom_metrics[metric_name])
            if limit:
                values = values[-limit:]
            return [{"value": v.value, "timestamp": v.timestamp, "metadata": v.metadata} for v in values]
    
    def get_system_metrics(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get system resource metrics."""
        with self._lock:
            metrics = list(self._system_metrics)
            if limit:
                metrics = metrics[-limit:]
            return [m.to_dict() for m in metrics]
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for all metrics."""
        with self._lock:
            uptime = time.time() - self._start_time
            
            # Operation summary
            total_operations = sum(m.operation_count for m in self._metrics.values())
            total_errors = sum(m.error_count for m in self._metrics.values())
            
            # Recent system metrics
            recent_system = self._system_metrics[-1] if self._system_metrics else None
            
            return {
                "uptime_seconds": uptime,
                "total_operations": total_operations,
                "total_errors": total_errors,
                "error_rate": total_errors / total_operations if total_operations > 0 else 0.0,
                "operations_per_second": total_operations / uptime if uptime > 0 else 0.0,
                "unique_operations": len(self._metrics),
                "system_metrics": recent_system.to_dict() if recent_system else None,
                "metrics_collection_enabled": self._enabled
            }
    
    def _start_system_monitoring(self):
        """Start background system metrics collection."""
        def collect_system_metrics():
            while self._enabled:
                try:
                    metrics = SystemResourceMetrics.capture_current()
                    with self._lock:
                        self._system_metrics.append(metrics)
                    time.sleep(30)  # Collect every 30 seconds
                except Exception as e:
                    logger.error(f"System metrics collection failed: {e}")
                    time.sleep(60)  # Wait longer on error
        
        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()
    
    def reset_metrics(self):
        """Reset all collected metrics."""
        with self._lock:
            self._metrics.clear()
            self._custom_metrics.clear()
            self._system_metrics.clear()
            self._start_time = time.time()


# Global metrics collector
_global_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    return _global_metrics_collector


def record_operation_time(operation_name: str, duration: float, success: bool = True,
                         metadata: Optional[Dict[str, Any]] = None):
    """Record operation timing using the global collector."""
    _global_metrics_collector.record_operation(operation_name, duration, success, metadata)


def increment_counter(counter_name: str, value: float = 1.0,
                     metadata: Optional[Dict[str, Any]] = None):
    """Increment a counter using the global collector."""
    _global_metrics_collector.increment_counter(counter_name, value, metadata)


def set_gauge(gauge_name: str, value: float, metadata: Optional[Dict[str, Any]] = None):
    """Set a gauge value using the global collector."""
    _global_metrics_collector.set_gauge(gauge_name, value, metadata)


def get_performance_summary() -> Dict[str, Any]:
    """Get a summary of all performance metrics."""
    return _global_metrics_collector.get_summary_stats()


def timed_operation(operation_name: Optional[str] = None, include_args: bool = False):
    """
    Decorator to automatically time operations and record metrics.
    
    Args:
        operation_name: Name for the operation (defaults to function name)
        include_args: Whether to include function arguments in metadata
    """
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            start_time = time.time()
            
            metadata = {}
            if include_args:
                # Safely include some argument info
                try:
                    metadata["arg_count"] = len(args)
                    metadata["kwarg_count"] = len(kwargs)
                    if args and hasattr(args[0], '__class__'):
                        metadata["instance_type"] = args[0].__class__.__name__
                except Exception:
                    pass
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                record_operation_time(op_name, duration, True, metadata)
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_metadata = metadata.copy()
                error_metadata["error_type"] = type(e).__name__
                record_operation_time(op_name, duration, False, error_metadata)
                raise
        
        return wrapper
    return decorator