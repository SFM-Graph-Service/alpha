"""
Advanced Caching Infrastructure for SFM Graph Service

This module provides comprehensive multi-level caching with TTL, LRU strategies,
cache invalidation patterns, and performance monitoring for improved scalability.

Features:
- Multi-level caching (Memory, TTL, LRU)
- Query result caching with intelligent invalidation
- Cache hit/miss metrics and monitoring
- Configurable cache policies and limits
- Graph-specific caching optimizations
"""

import time
import threading
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

import logging
logger = logging.getLogger(__name__)


class CacheType(Enum):
    """Types of cache backends available."""
    MEMORY = "memory"
    TTL = "ttl"
    LRU = "lru"
    FIFO = "fifo"


class CacheHitType(Enum):
    """Cache hit/miss types for metrics."""
    HIT = "hit"
    MISS = "miss"
    EXPIRED = "expired"
    EVICTED = "evicted"


@dataclass
class CacheStats:
    """Statistics for cache performance."""
    hits: int = 0
    misses: int = 0
    expired: int = 0
    evicted: int = 0
    total_operations: int = 0
    hit_rate: float = 0.0
    size: int = 0
    max_size: int = 0
    memory_usage_bytes: int = 0
    
    def record_hit(self):
        """Record a cache hit."""
        self.hits += 1
        self.total_operations += 1
        self._update_hit_rate()
    
    def record_miss(self):
        """Record a cache miss."""
        self.misses += 1
        self.total_operations += 1
        self._update_hit_rate()
    
    def record_expired(self):
        """Record a cache expiration."""
        self.expired += 1
    
    def record_evicted(self):
        """Record a cache eviction."""
        self.evicted += 1
    
    def _update_hit_rate(self):
        """Update the hit rate calculation."""
        if self.total_operations > 0:
            self.hit_rate = self.hits / self.total_operations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "expired": self.expired,
            "evicted": self.evicted,
            "total_operations": self.total_operations,
            "hit_rate": self.hit_rate,
            "size": self.size,
            "max_size": self.max_size,
            "memory_usage_bytes": self.memory_usage_bytes
        }


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    def __init__(self, name: str, max_size: int = 1000):
        self.name = name
        self.max_size = max_size
        self.stats = CacheStats(max_size=max_size)
        self._lock = threading.RLock()
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set a value in the cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def keys(self) -> List[str]:
        """Get all cache keys."""
        pass
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching a pattern (default implementation)."""
        deleted = 0
        keys_to_delete: List[str] = []
        
        # Simple pattern matching (can be enhanced with regex)
        for key in self.keys():
            if self._matches_pattern(key, pattern):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            if self.delete(key):
                deleted += 1
        
        return deleted
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching for cache keys."""
        # Support * as wildcard
        if '*' in pattern:
            parts = pattern.split('*')
            if len(parts) == 2:
                prefix, suffix = parts
                return key.startswith(prefix) and key.endswith(suffix)
        return key == pattern
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            self.stats.size = len(self.keys())
            return self.stats


class MemoryCache(CacheBackend):
    """Simple in-memory cache backend."""
    
    def __init__(self, name: str, max_size: int = 1000):
        super().__init__(name, max_size)
        self._cache: Dict[str, Any] = {}
        self._access_order: OrderedDict[str, None] = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                # Update access order (LRU)
                self._access_order.move_to_end(key)
                self.stats.record_hit()
                return self._cache[key]
            else:
                self.stats.record_miss()
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        with self._lock:
            # Handle size limit
            if key not in self._cache and len(self._cache) >= self.max_size:
                # Evict LRU item
                oldest_key, _ = self._access_order.popitem(last=False)
                del self._cache[oldest_key]
                self.stats.record_evicted()
            
            self._cache[key] = value
            self._access_order[key] = None
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._access_order.pop(key, None)
                return True
            return False
    
    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    def keys(self) -> List[str]:
        with self._lock:
            return list(self._cache.keys())


class TTLMemoryCache(CacheBackend):
    """TTL-aware memory cache backend."""
    
    @dataclass
    class CacheEntry:
        value: Any
        expiry_time: float
        
        def is_expired(self) -> bool:
            return time.time() > self.expiry_time
    
    def __init__(self, name: str, max_size: int = 1000, default_ttl: float = 3600):
        super().__init__(name, max_size)
        self.default_ttl = default_ttl
        self._cache: Dict[str, TTLMemoryCache.CacheEntry] = {}
        self._access_order: OrderedDict[str, None] = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry.is_expired():
                    # Clean up expired entry
                    del self._cache[key]
                    self._access_order.pop(key, None)
                    self.stats.record_expired()
                    self.stats.record_miss()
                    return None
                else:
                    # Update access order
                    self._access_order.move_to_end(key)
                    self.stats.record_hit()
                    return entry.value
            else:
                self.stats.record_miss()
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        with self._lock:
            expiry_time = time.time() + (ttl or self.default_ttl)
            
            # Handle size limit
            if key not in self._cache and len(self._cache) >= self.max_size:
                # Evict oldest item
                oldest_key, _ = self._access_order.popitem(last=False)
                del self._cache[oldest_key]
                self.stats.record_evicted()
            
            self._cache[key] = self.CacheEntry(value, expiry_time)
            self._access_order[key] = None
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._access_order.pop(key, None)
                return True
            return False
    
    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    def keys(self) -> List[str]:
        with self._lock:
            # Clean up expired entries while getting keys
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.expiry_time <= current_time
            ]
            for key in expired_keys:
                del self._cache[key]
                self._access_order.pop(key, None)
                self.stats.record_expired()
            
            return list(self._cache.keys())


class MultiLevelCache:
    """Multi-level cache with fallback and intelligent promotion."""
    
    def __init__(self, name: str):
        self.name = name
        self._levels: List[CacheBackend] = []
        self._lock = threading.RLock()
    
    def add_level(self, cache: CacheBackend) -> None:
        """Add a cache level (first added = highest priority)."""
        with self._lock:
            self._levels.append(cache)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value with cache level promotion."""
        with self._lock:
            for i, cache in enumerate(self._levels):
                value = cache.get(key)
                if value is not None:
                    # Promote to higher levels
                    for j in range(i):
                        self._levels[j].set(key, value)
                    return value
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in all cache levels."""
        with self._lock:
            for cache in self._levels:
                cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete from all cache levels."""
        deleted = False
        with self._lock:
            for cache in self._levels:
                if cache.delete(key):
                    deleted = True
        return deleted
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete pattern from all cache levels."""
        total_deleted = 0
        with self._lock:
            for cache in self._levels:
                total_deleted += cache.delete_pattern(pattern)
        return total_deleted
    
    def clear(self) -> None:
        """Clear all cache levels."""
        with self._lock:
            for cache in self._levels:
                cache.clear()
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all cache levels."""
        with self._lock:
            return {cache.name: cache.get_stats().to_dict() for cache in self._levels}


class QueryCache:
    """Specialized cache for query results with intelligent invalidation."""
    
    def __init__(self, max_size: int = 10000):
        # Multi-level cache setup
        self._cache = MultiLevelCache("query_cache")
        
        # Level 1: Fast memory cache for recent queries
        self._cache.add_level(MemoryCache("recent_queries", max_size=1000))
        
        # Level 2: TTL cache for general queries
        self._cache.add_level(TTLMemoryCache("general_queries", max_size=max_size, default_ttl=1800))
        
        # Invalidation rules
        self._invalidation_rules: Dict[str, List[str]] = {}
        
        # Cache key generators
        self._key_generators: Dict[str, Callable[..., Any]] = {}
    
    def register_invalidation_rule(self, event: str, cache_patterns: List[str]) -> None:
        """Register cache invalidation rules for specific events."""
        self._invalidation_rules[event] = cache_patterns
    
    def register_key_generator(self, operation: str, generator: Callable[..., Any]) -> None:
        """Register a cache key generator for an operation."""
        self._key_generators[operation] = generator
    
    def get_cached_result(self, operation: str, *args: Any, **kwargs: Any) -> Optional[Any]:
        """Get cached result for an operation."""
        cache_key = self._generate_cache_key(operation, *args, **kwargs)
        return self._cache.get(cache_key)
    
    def cache_result(self, operation: str, result: Any, ttl: Optional[float] = None, *args: Any, **kwargs: Any) -> None:
        """Cache a result for an operation."""
        cache_key = self._generate_cache_key(operation, *args, **kwargs)
        self._cache.set(cache_key, result, ttl)
    
    def invalidate_on_event(self, event: str, **context: Any) -> int:
        """Invalidate caches when specific events occur."""
        patterns = self._invalidation_rules.get(event, [])
        total_invalidated = 0
        
        for pattern in patterns:
            try:
                formatted_pattern = pattern.format(**context)
                total_invalidated += self._cache.delete_pattern(formatted_pattern)
            except KeyError as e:
                logger.warning(f"Missing context key for invalidation pattern {pattern}: {e}")
        
        return total_invalidated
    
    def _generate_cache_key(self, operation: str, *args: Any, **kwargs: Dict[str, Any]) -> str:
        """Generate a cache key for an operation."""
        if operation in self._key_generators:
            return self._key_generators[operation](*args, **kwargs)
        
        # Default key generation
        key_parts = [operation]
        
        # Add args
        for arg in args:
            if hasattr(arg, 'id'):
                key_parts.append(str(arg.id))
            else:
                key_parts.append(str(arg))
        
        # Add kwargs
        for k, v in sorted(kwargs.items()):
            if hasattr(v, 'id'):
                key_parts.append(f"{k}:{getattr(v, 'id', v)}")
            else:
                key_parts.append(f"{k}:{v}")
        
        return ":".join(key_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = self._cache.get_stats()
        stats["invalidation_rules_count"] = {"count": len(self._invalidation_rules)}
        stats["registered_generators"] = {"count": len(self._key_generators)}
        return stats
    
    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()


from typing import TypeVar, Callable, cast

F = TypeVar("F", bound=Callable[..., Any])

def cached_operation(cache: QueryCache, operation_name: str, ttl: Optional[float] = None) -> Callable[[F], F]:
    """Decorator to automatically cache operation results."""
    def decorator(func: F) -> F:
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Try to get cached result
            cached_result = cache.get_cached_result(operation_name, *args, **kwargs)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.cache_result(operation_name, result, ttl, *args, **kwargs)
            return result
        
        return cast(F, wrapper)  # Ensure the return type matches the decorated function
    return decorator