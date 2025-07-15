"""
Decorator Pattern Implementation for SFM Framework

This module implements the Decorator pattern to provide cross-cutting concerns
like validation, logging, caching, and auditing in a reusable and composable way.
"""

import time
import functools
import hashlib
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, TypeVar, Generic, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Type variables for generic decorators
F = TypeVar('F', bound=Callable[..., Any])
T = TypeVar('T')


class ValidationError(Exception):
    """Exception raised when validation fails."""
    pass


class CacheEntry(Generic[T]):
    """Cache entry with TTL support."""

    def __init__(self, value: T, ttl: Optional[int] = None):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = self.created_at

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl is None:
            return False
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)

    def access(self) -> T:
        """Access the cached value and update access statistics."""
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.value


class CacheManager:
    """Manager for cache entries with TTL and size limits."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        if key not in self.cache:
            self.misses += 1
            return None

        entry = self.cache[key]
        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return None

        self.hits += 1
        return entry.access()

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache."""
        if ttl is None:
            ttl = self.default_ttl

        # Remove expired entries if cache is full
        if len(self.cache) >= self.max_size:
            self._cleanup_expired()

            # If still full, remove least recently used
            if len(self.cache) >= self.max_size:
                self._remove_lru()

        self.cache[key] = CacheEntry(value, ttl)

    def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def _cleanup_expired(self) -> None:
        """Remove expired entries from the cache."""
        expired_keys = [
            key for key,
            entry in self.cache.items() if entry.is_expired()]
        for key in expired_keys:
            del self.cache[key]

    def _remove_lru(self) -> None:
        """Remove the least recently used entry."""
        if not self.cache:
            return

        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed)
        del self.cache[lru_key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }


class AuditLevel(Enum):
    """Audit levels for different types of operations."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditLogEntry:
    """Entry in the audit log."""
    timestamp: datetime
    operation: str
    level: AuditLevel
    user_id: Optional[str]
    args: tuple
    kwargs: dict
    result: Optional[Any]
    error: Optional[str]
    execution_time_ms: float
    metadata: Dict[str, Any]


class AuditLogger:
    """Logger for audit trail of operations."""

    def __init__(self, max_entries: int = 10000):
        self.entries: List[AuditLogEntry] = []
        self.max_entries = max_entries

    def log(self,
            operation: str,
            level: AuditLevel,
            user_id: Optional[str],
            args: tuple,
            kwargs: dict,
            result: Optional[Any],
            error: Optional[str],
            execution_time_ms: float,
            metadata: Optional[Dict[str,
                                    Any]] = None) -> None:
        """Log an audit entry."""
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            operation=operation,
            level=level,
            user_id=user_id,
            args=args,
            kwargs=kwargs,
            result=result,
            error=error,
            execution_time_ms=execution_time_ms,
            metadata=metadata or {}
        )

        self.entries.append(entry)

        # Maintain size limit
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]

    def get_entries(
            self,
            limit: Optional[int] = None,
            level: Optional[AuditLevel] = None) -> List[AuditLogEntry]:
        """Get audit log entries."""
        entries = self.entries

        if level is not None:
            entries = [e for e in entries if e.level == level]

        if limit is not None:
            entries = entries[-limit:]

        return entries

    def clear(self) -> None:
        """Clear all audit log entries."""
        self.entries.clear()


class Decorator(ABC):
    """Abstract base class for all decorators."""

    @abstractmethod
    def __call__(self, func: F) -> F:
        """Apply the decorator to a function."""
        pass


class ValidationDecorator(Decorator):
    """Decorator for input validation."""

    def __init__(self, validator: Callable[..., bool]):
        self.validator = validator

    def __call__(self, func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.validator(*args, **kwargs):
                raise ValidationError(
                    f"Input validation failed for {
                        func.__name__}")
            return func(*args, **kwargs)
        return wrapper  # type: ignore[return-value]


class CacheDecorator(Decorator):
    """Decorator for caching function results."""

    def __init__(
            self,
            cache_manager: Optional[CacheManager] = None,
            ttl: int = 3600):
        self.cache_manager = cache_manager or CacheManager()
        self.ttl = ttl

    def __call__(self, func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = self._generate_cache_key(func.__name__, args, kwargs)

            # Try to get from cache
            cached_result = self.cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            self.cache_manager.set(cache_key, result, self.ttl)
            return result
        return wrapper  # type: ignore[return-value]

    def _generate_cache_key(
            self,
            func_name: str,
            args: tuple,
            kwargs: dict) -> str:
        """Generate a cache key from function name and arguments."""
        # Create a hashable representation of the arguments
        args_str = str(args)
        kwargs_str = str(sorted(kwargs.items()))
        combined = f"{func_name}:{args_str}:{kwargs_str}"
        return hashlib.md5(combined.encode()).hexdigest()


class AuditDecorator(Decorator):
    """Decorator for auditing function calls."""

    def __init__(self, audit_logger: Optional[AuditLogger] = None,
                 level: AuditLevel = AuditLevel.INFO,
                 user_id_provider: Optional[Callable[[], str]] = None):
        self.audit_logger = audit_logger or AuditLogger()
        self.level = level
        self.user_id_provider = user_id_provider

    def __call__(self, func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            user_id = self.user_id_provider() if self.user_id_provider else None
            result = None
            error = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                execution_time_ms = (time.time() - start_time) * 1000
                self.audit_logger.log(
                    operation=func.__name__,
                    level=self.level,
                    user_id=user_id,
                    args=args,
                    kwargs=kwargs,
                    result=result,
                    error=error,
                    execution_time_ms=execution_time_ms
                )

        return wrapper  # type: ignore[return-value]


class TimingDecorator(Decorator):
    """Decorator for timing function execution."""

    def __init__(self, log_results: bool = True):
        self.log_results = log_results
        self.timings: Dict[str, List[float]] = {}

    def __call__(self, func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time

                # Record timing
                if func.__name__ not in self.timings:
                    self.timings[func.__name__] = []
                self.timings[func.__name__].append(execution_time)

                if self.log_results:
                    print(f"{func.__name__} executed in {execution_time:.4f}s")

        return wrapper  # type: ignore[return-value]

    def get_timings(self, func_name: Optional[str] = None) -> Dict[str, Any]:
        """Get timing statistics."""
        if func_name is not None:
            if func_name not in self.timings:
                return {}

            timings = self.timings[func_name]
            return {
                "count": len(timings),
                "total_time": sum(timings),
                "average_time": sum(timings) / len(timings),
                "min_time": min(timings),
                "max_time": max(timings)
            }

        # Return all timings
        result = {}
        for name, timings in self.timings.items():
            result[name] = {
                "count": len(timings),
                "total_time": sum(timings),
                "average_time": sum(timings) / len(timings),
                "min_time": min(timings),
                "max_time": max(timings)
            }
        return result


class RetryDecorator(Decorator):
    """Decorator for retrying failed operations."""

    def __init__(self, max_retries: int = 3, delay: float = 1.0,
                 backoff_factor: float = 2.0,
                 exceptions: tuple = (Exception,)):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.exceptions = exceptions

    def __call__(self, func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = self.delay

            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except self.exceptions as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        time.sleep(current_delay)
                        current_delay *= self.backoff_factor
                    else:
                        raise last_exception

            # Should never reach here, but just in case
            raise last_exception

        return wrapper  # type: ignore[return-value]


# Global instances for convenience
_default_cache_manager = CacheManager()
_default_audit_logger = AuditLogger()
_default_timing_decorator = TimingDecorator()


def validate_inputs(validator: Callable[..., bool]) -> Callable[[F], F]:
    """Decorator to validate method inputs."""
    return ValidationDecorator(validator)


def cache_result(ttl: int = 3600,
                 cache_manager: Optional[CacheManager] = None) -> Callable[[F],
                                                                           F]:
    """Decorator to cache method results."""
    return CacheDecorator(cache_manager or _default_cache_manager, ttl)


def audit_operation(level: AuditLevel = AuditLevel.INFO,
                    audit_logger: Optional[AuditLogger] = None,
                    user_id_provider: Optional[Callable[[],
                                                        str]] = None) -> Callable[[F],
                                                                                  F]:
    """Decorator to audit operations."""
    return AuditDecorator(
        audit_logger or _default_audit_logger,
        level,
        user_id_provider)


def time_execution(log_results: bool = True) -> Callable[[F], F]:
    """Decorator to time function execution."""
    return TimingDecorator(log_results)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0,
                     backoff_factor: float = 2.0,
                     exceptions: tuple = (Exception,)) -> Callable[[F], F]:
    """Decorator to retry failed operations."""
    return RetryDecorator(max_retries, delay, backoff_factor, exceptions)


class DecoratorChain:
    """Chain multiple decorators together."""

    def __init__(self, decorators: List[Decorator]):
        self.decorators = decorators

    def __call__(self, func: F) -> F:
        """Apply all decorators in sequence."""
        result = func
        for decorator in self.decorators:
            result = decorator(result)
        return result


def create_decorator_chain(*decorators: Decorator) -> DecoratorChain:
    """Create a decorator chain from multiple decorators."""
    return DecoratorChain(list(decorators))


# Example usage combining multiple decorators
def enhanced_operation(validator: Callable[..., bool],
                       cache_ttl: int = 3600,
                       audit_level: AuditLevel = AuditLevel.INFO,
                       max_retries: int = 3) -> Callable[[F], F]:
    """
    Decorator that combines validation, caching, auditing, and retry logic.

    This demonstrates how multiple decorators can be composed together.
    """
    chain = create_decorator_chain(
        ValidationDecorator(validator),
        CacheDecorator(ttl=cache_ttl),
        AuditDecorator(level=audit_level),
        RetryDecorator(max_retries=max_retries),
        TimingDecorator()
    )
    return chain


# Utility functions for getting global statistics
def get_cache_stats() -> Dict[str, Any]:
    """Get statistics from the default cache manager."""
    return _default_cache_manager.get_stats()


def get_audit_entries(
        limit: Optional[int] = None,
        level: Optional[AuditLevel] = None) -> List[AuditLogEntry]:
    """Get entries from the default audit logger."""
    return _default_audit_logger.get_entries(limit, level)


def get_timing_stats(func_name: Optional[str] = None) -> Dict[str, Any]:
    """Get timing statistics from the default timing decorator."""
    return _default_timing_decorator.get_timings(func_name)


def clear_all_caches() -> None:
    """Clear all caches from the default cache manager."""
    _default_cache_manager.clear()


def clear_audit_log() -> None:
    """Clear the default audit log."""
    _default_audit_logger.clear()


# Example validator functions
def validate_non_empty_string(
        obj,
        field_name: str,
        value: str,
        **kwargs) -> bool:
    """Validate that a string field is not empty."""
    return isinstance(value, str) and len(value.strip()) > 0


def validate_positive_number(
        obj,
        field_name: str,
        value: float,
        **kwargs) -> bool:
    """Validate that a number is positive."""
    return isinstance(value, (int, float)) and value > 0


def validate_uuid_format(obj, field_name: str, value: str, **kwargs) -> bool:
    """Validate that a string is a valid UUID format."""
    import uuid
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False
