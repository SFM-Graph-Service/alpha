"""
Cache monitoring and metrics for the SFM system.

This module provides monitoring capabilities for the advanced caching system
with support for Prometheus metrics and performance tracking.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import contextmanager
import time

logger = logging.getLogger(__name__)

# Optional Prometheus metrics import
try:
    from prometheus_client import Counter, Gauge, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.info("Prometheus client not available - metrics will be disabled")


@dataclass
class CachePerformanceMetrics:
    """Performance metrics for cache operations."""
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    eviction_rate: float = 0.0
    average_response_time: float = 0.0
    size_utilization: float = 0.0
    memory_usage_mb: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'hit_rate': self.hit_rate,
            'miss_rate': self.miss_rate,
            'eviction_rate': self.eviction_rate,
            'average_response_time': self.average_response_time,
            'size_utilization': self.size_utilization,
            'memory_usage_mb': self.memory_usage_mb
        }


class CacheMonitor:
    """Monitor cache performance and collect metrics."""
    
    def __init__(self, cache_name: str, enable_prometheus: bool = True):
        self.cache_name = cache_name
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        
        # Initialize Prometheus metrics if available
        if self.enable_prometheus:
            self._init_prometheus_metrics()
        
        # Internal metrics tracking
        self._operation_times: List[float] = []
        self._max_operation_history = 1000
    
    def _init_prometheus_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        if not self.enable_prometheus:
            return
            
        # Cache hit/miss counters
        self.hit_counter = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_name', 'cache_type']
        )
        
        self.miss_counter = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_name', 'cache_type']
        )
        
        # Cache performance gauges
        self.hit_rate_gauge = Gauge(
            'cache_hit_rate',
            'Cache hit rate',
            ['cache_name', 'cache_type']
        )
        
        self.cache_size_gauge = Gauge(
            'cache_size_bytes',
            'Cache size in bytes',
            ['cache_name', 'cache_type']
        )
        
        # Cache operations
        self.operations_counter = Counter(
            'cache_operations_total',
            'Cache operations',
            ['operation', 'cache_name']
        )
        
        # Cache evictions
        self.evictions_counter = Counter(
            'cache_evictions_total',
            'Cache evictions',
            ['cache_name', 'cache_type']
        )
        
        # Response time histogram
        self.response_time_histogram = Histogram(
            'cache_response_time_seconds',
            'Cache response time',
            ['cache_name', 'operation']
        )
    
    def record_hit(self, cache_type: str = 'default') -> None:
        """Record a cache hit."""
        if self.enable_prometheus:
            self.hit_counter.labels(
                cache_name=self.cache_name,
                cache_type=cache_type
            ).inc()
    
    def record_miss(self, cache_type: str = 'default') -> None:
        """Record a cache miss."""
        if self.enable_prometheus:
            self.miss_counter.labels(
                cache_name=self.cache_name,
                cache_type=cache_type
            ).inc()
    
    def record_eviction(self, cache_type: str = 'default') -> None:
        """Record a cache eviction."""
        if self.enable_prometheus:
            self.evictions_counter.labels(
                cache_name=self.cache_name,
                cache_type=cache_type
            ).inc()
    
    def record_operation(self, operation: str) -> None:
        """Record a cache operation."""
        if self.enable_prometheus:
            self.operations_counter.labels(
                operation=operation,
                cache_name=self.cache_name
            ).inc()
    
    def update_hit_rate(self, hit_rate: float, cache_type: str = 'default') -> None:
        """Update cache hit rate."""
        if self.enable_prometheus:
            self.hit_rate_gauge.labels(
                cache_name=self.cache_name,
                cache_type=cache_type
            ).set(hit_rate)
    
    def update_cache_size(self, size_bytes: int, cache_type: str = 'default') -> None:
        """Update cache size."""
        if self.enable_prometheus:
            self.cache_size_gauge.labels(
                cache_name=self.cache_name,
                cache_type=cache_type
            ).set(size_bytes)
    
    @contextmanager
    def time_operation(self, operation: str):
        """Context manager for timing cache operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self._operation_times.append(duration)
            
            # Keep only recent operations
            if len(self._operation_times) > self._max_operation_history:
                self._operation_times = self._operation_times[-self._max_operation_history:]
            
            # Record in Prometheus
            if self.enable_prometheus:
                self.response_time_histogram.labels(
                    cache_name=self.cache_name,
                    operation=operation
                ).observe(duration)
    
    def get_performance_metrics(self) -> CachePerformanceMetrics:
        """Get current performance metrics."""
        metrics = CachePerformanceMetrics()
        
        # Calculate average response time
        if self._operation_times:
            metrics.average_response_time = sum(self._operation_times) / len(self._operation_times)
        
        return metrics
    
    def get_prometheus_metrics(self) -> Dict[str, Any]:
        """Get Prometheus metrics (if available)."""
        if not self.enable_prometheus:
            return {}
        
        return {
            'hits': self.hit_counter._value.sum(),
            'misses': self.miss_counter._value.sum(),
            'evictions': self.evictions_counter._value.sum(),
            'operations': self.operations_counter._value.sum(),
        }


def monitor_cache_performance(caches: Dict[str, Any]) -> Dict[str, CachePerformanceMetrics]:
    """Monitor performance across multiple caches."""
    performance_metrics = {}
    
    for cache_name, cache in caches.items():
        try:
            stats = cache.get_stats() if hasattr(cache, 'get_stats') else {}
            
            metrics = CachePerformanceMetrics()
            
            # Calculate hit rate
            if hasattr(stats, 'hits') and hasattr(stats, 'total_operations'):
                if stats.total_operations > 0:
                    metrics.hit_rate = stats.hits / stats.total_operations
                    metrics.miss_rate = 1.0 - metrics.hit_rate
            
            # Calculate size utilization
            if hasattr(stats, 'size') and hasattr(stats, 'max_size'):
                if stats.max_size > 0:
                    metrics.size_utilization = stats.size / stats.max_size
            
            # Memory usage
            if hasattr(stats, 'memory_usage_bytes'):
                metrics.memory_usage_mb = stats.memory_usage_bytes / (1024 * 1024)
            
            performance_metrics[cache_name] = metrics
            
        except Exception as e:
            logger.error(f"Error monitoring cache {cache_name}: {e}")
    
    return performance_metrics


def generate_cache_report(caches: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a comprehensive cache performance report."""
    report = {
        'timestamp': time.time(),
        'cache_count': len(caches),
        'performance_metrics': {},
        'alerts': []
    }
    
    performance_metrics = monitor_cache_performance(caches)
    report['performance_metrics'] = {
        name: metrics.to_dict() for name, metrics in performance_metrics.items()
    }
    
    # Generate alerts for poor performance
    for cache_name, metrics in performance_metrics.items():
        if metrics.hit_rate < 0.5:  # Hit rate below 50%
            report['alerts'].append({
                'cache': cache_name,
                'type': 'low_hit_rate',
                'value': metrics.hit_rate,
                'threshold': 0.5
            })
        
        if metrics.size_utilization > 0.9:  # Size utilization above 90%
            report['alerts'].append({
                'cache': cache_name,
                'type': 'high_utilization',
                'value': metrics.size_utilization,
                'threshold': 0.9
            })
    
    return report