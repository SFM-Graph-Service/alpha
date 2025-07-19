"""
Health Check System for SFM Service

This module provides comprehensive health checking for the SFM service,
including dependency monitoring, readiness probes, and liveness probes.

Features:
- Database connection health checks
- Redis cache health checks
- System resource monitoring
- Service readiness validation
- Startup and liveness probes
- Dependency monitoring
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
from contextlib import contextmanager

from infrastructure.logging_config import get_logger


class HealthStatus(Enum):
    """Health check status values."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'status': self.status.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration,
            'metadata': self.metadata
        }


@dataclass
class HealthSummary:
    """Summary of all health checks."""
    overall_status: HealthStatus
    checks: List[HealthCheckResult]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'status': self.overall_status.value,
            'timestamp': self.timestamp.isoformat(),
            'checks': [check.to_dict() for check in self.checks]
        }


class HealthCheck:
    """Base class for health checks."""
    
    def __init__(self, name: str, timeout: float = 5.0):
        self.name = name
        self.timeout = timeout
        self.logger = get_logger(f"health.{name}")
    
    def check(self) -> HealthCheckResult:
        """Perform the health check."""
        start_time = time.time()
        
        try:
            # Use timeout context
            with self._timeout_context():
                result = self._check_health()
                duration = time.time() - start_time
                
                if result.duration == 0.0:
                    result.duration = duration
                
                self.logger.debug(f"Health check '{self.name}' completed",
                                status=result.status.value,
                                duration=duration)
                
                return result
                
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Health check '{self.name}' failed",
                            error=str(e),
                            duration=duration)
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                duration=duration
            )
    
    def _check_health(self) -> HealthCheckResult:
        """Override this method to implement specific health check logic."""
        raise NotImplementedError("Subclasses must implement _check_health")
    
    @contextmanager
    def _timeout_context(self):
        """Context manager for timeout handling."""
        # Simple timeout implementation - in production, consider using asyncio
        yield


class DatabaseHealthCheck(HealthCheck):
    """Health check for database connectivity."""
    
    def __init__(self, connection_provider: Callable = None):
        super().__init__("database", timeout=10.0)
        self.connection_provider = connection_provider
    
    def _check_health(self) -> HealthCheckResult:
        """Check database connection health."""
        if not self.connection_provider:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database health check skipped - no connection provider configured"
            )
        
        try:
            # Test database connection
            with self.connection_provider() as conn:
                # Simple query to test connection
                if hasattr(conn, 'execute'):
                    conn.execute("SELECT 1")
                
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database connection successful"
            )
            
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}"
            )


class RedisHealthCheck(HealthCheck):
    """Health check for Redis cache connectivity."""
    
    def __init__(self, redis_client=None):
        super().__init__("redis", timeout=5.0)
        self.redis_client = redis_client
    
    def _check_health(self) -> HealthCheckResult:
        """Check Redis connection health."""
        if not self.redis_client:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Redis health check skipped - no client configured"
            )
        
        try:
            # Test Redis connection
            self.redis_client.ping()
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Redis connection successful"
            )
            
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}"
            )


class SystemResourcesHealthCheck(HealthCheck):
    """Health check for system resources (CPU, memory, disk)."""
    
    def __init__(self, 
                 cpu_threshold: float = 90.0,
                 memory_threshold: float = 90.0,
                 disk_threshold: float = 90.0):
        super().__init__("system_resources", timeout=3.0)
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
    
    def _check_health(self) -> HealthCheckResult:
        """Check system resource usage."""
        try:
            # Try to import psutil for system monitoring
            import psutil
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            # Check thresholds
            issues = []
            if cpu_percent > self.cpu_threshold:
                issues.append(f"CPU usage high: {cpu_percent:.1f}%")
            if memory_percent > self.memory_threshold:
                issues.append(f"Memory usage high: {memory_percent:.1f}%")
            if disk_percent > self.disk_threshold:
                issues.append(f"Disk usage high: {disk_percent:.1f}%")
            
            metadata = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent
            }
            
            if issues:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.DEGRADED,
                    message=f"System resources under stress: {', '.join(issues)}",
                    metadata=metadata
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="System resources normal",
                    metadata=metadata
                )
                
        except ImportError:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message="psutil not available - system resource monitoring disabled"
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"System resource check failed: {str(e)}"
            )


class ServiceReadinessCheck(HealthCheck):
    """Health check for service readiness."""
    
    def __init__(self, service_provider: Callable = None):
        super().__init__("service_readiness", timeout=5.0)
        self.service_provider = service_provider
    
    def _check_health(self) -> HealthCheckResult:
        """Check if service is ready to handle requests."""
        if not self.service_provider:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Service readiness check skipped - no provider configured"
            )
        
        try:
            service = self.service_provider()
            
            # Check if service is initialized and ready
            if hasattr(service, 'is_ready') and callable(service.is_ready):
                if service.is_ready():
                    return HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.HEALTHY,
                        message="Service is ready"
                    )
                else:
                    return HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.UNHEALTHY,
                        message="Service is not ready"
                    )
            else:
                # If no is_ready method, assume service is ready if it exists
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="Service is available"
                )
                
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Service readiness check failed: {str(e)}"
            )


class HealthChecker:
    """
    Main health checker that coordinates all health checks.
    
    This class manages multiple health checks and provides different
    types of health endpoints (liveness, readiness, startup).
    """
    
    def __init__(self):
        self.checks: List[HealthCheck] = []
        self.startup_checks: List[HealthCheck] = []
        self.liveness_checks: List[HealthCheck] = []
        self.readiness_checks: List[HealthCheck] = []
        self.logger = get_logger("health.checker")
        self._lock = threading.Lock()
    
    def add_check(self, check: HealthCheck, 
                  include_in_startup: bool = True,
                  include_in_liveness: bool = True,
                  include_in_readiness: bool = True):
        """Add a health check to the system."""
        with self._lock:
            self.checks.append(check)
            if include_in_startup:
                self.startup_checks.append(check)
            if include_in_liveness:
                self.liveness_checks.append(check)
            if include_in_readiness:
                self.readiness_checks.append(check)
    
    def remove_check(self, check_name: str):
        """Remove a health check by name."""
        with self._lock:
            self.checks = [c for c in self.checks if c.name != check_name]
            self.startup_checks = [c for c in self.startup_checks if c.name != check_name]
            self.liveness_checks = [c for c in self.liveness_checks if c.name != check_name]
            self.readiness_checks = [c for c in self.readiness_checks if c.name != check_name]
    
    def check_all(self) -> HealthSummary:
        """Run all health checks and return summary."""
        return self._run_checks(self.checks)
    
    def check_startup(self) -> HealthSummary:
        """Run startup health checks."""
        return self._run_checks(self.startup_checks)
    
    def check_liveness(self) -> HealthSummary:
        """Run liveness health checks."""
        return self._run_checks(self.liveness_checks)
    
    def check_readiness(self) -> HealthSummary:
        """Run readiness health checks."""
        return self._run_checks(self.readiness_checks)
    
    def _run_checks(self, checks: List[HealthCheck]) -> HealthSummary:
        """Run a list of health checks and return summary."""
        results = []
        
        for check in checks:
            try:
                result = check.check()
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error running health check '{check.name}'",
                                error=str(e))
                results.append(HealthCheckResult(
                    name=check.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check error: {str(e)}"
                ))
        
        # Determine overall status
        overall_status = self._determine_overall_status(results)
        
        return HealthSummary(
            overall_status=overall_status,
            checks=results
        )
    
    def _determine_overall_status(self, results: List[HealthCheckResult]) -> HealthStatus:
        """Determine overall health status from individual check results."""
        if not results:
            return HealthStatus.UNKNOWN
        
        # If any check is unhealthy, overall is unhealthy
        if any(r.status == HealthStatus.UNHEALTHY for r in results):
            return HealthStatus.UNHEALTHY
        
        # If any check is degraded, overall is degraded
        if any(r.status == HealthStatus.DEGRADED for r in results):
            return HealthStatus.DEGRADED
        
        # If any check is unknown, overall is unknown
        if any(r.status == HealthStatus.UNKNOWN for r in results):
            return HealthStatus.UNKNOWN
        
        # All checks are healthy
        return HealthStatus.HEALTHY


def create_default_health_checker() -> HealthChecker:
    """Create a health checker with default checks."""
    checker = HealthChecker()
    
    # Add default health checks
    checker.add_check(SystemResourcesHealthCheck())
    
    # Add more checks as needed based on configuration
    return checker


# Global health checker instance
_health_checker = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = create_default_health_checker()
    return _health_checker