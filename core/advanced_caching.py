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

from typing import TypeVar, Callable, cast
import time
import threading
import pickle
import hashlib
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from functools import wraps

import logging
logger = logging.getLogger(__name__)

# Optional Redis import - gracefully handle if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - RedisCache will be disabled")

# Optional Prometheus metrics import
try:
    from prometheus_client import Counter, Gauge, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.info("Prometheus client not available - metrics will be disabled")


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

    def __init__(
            self,
            name: str,
            max_size: int = 1000,
            default_ttl: float = 3600):
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


class RedisCache(CacheBackend):
    """Redis-based cache backend with persistence."""

    def __init__(
            self,
            name: str,
            redis_client: Optional[Any] = None,
            host: str = 'localhost',
            port: int = 6379,
            db: int = 0,
            password: Optional[str] = None,
            max_size: int = 10000,
            default_ttl: float = 3600):
        super().__init__(name, max_size)
        self.default_ttl = default_ttl

        if not REDIS_AVAILABLE:
            raise ImportError(
                "Redis is not available. Install redis-py to use RedisCache")

        if redis_client:
            self.redis = redis_client
        else:
            self.redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False)

        # Test connection
        try:
            self.redis.ping()
            logger.info(f"Redis cache '{name}' connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _make_key(self, key: str) -> str:
        """Create a namespaced key for this cache instance."""
        return f"{self.name}:{key}"

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            try:
                namespaced_key = self._make_key(key)
                data = self.redis.get(namespaced_key)
                if data:
                    value = pickle.loads(data)
                    self.stats.record_hit()
                    return value
                else:
                    self.stats.record_miss()
                    return None
            except Exception as e:
                logger.error(f"Redis get error for key {key}: {e}")
                self.stats.record_miss()
                return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        with self._lock:
            try:
                namespaced_key = self._make_key(key)
                data = pickle.dumps(value)
                effective_ttl = ttl or self.default_ttl
                self.redis.setex(namespaced_key, int(effective_ttl), data)
            except Exception as e:
                logger.error(f"Redis set error for key {key}: {e}")

    def delete(self, key: str) -> bool:
        with self._lock:
            try:
                namespaced_key = self._make_key(key)
                return bool(self.redis.delete(namespaced_key))
            except Exception as e:
                logger.error(f"Redis delete error for key {key}: {e}")
                return False

    def clear(self) -> None:
        with self._lock:
            try:
                # Delete all keys with this cache's namespace
                pattern = f"{self.name}:*"
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
            except Exception as e:
                logger.error(f"Redis clear error: {e}")

    def keys(self) -> List[str]:
        with self._lock:
            try:
                pattern = f"{self.name}:*"
                redis_keys = self.redis.keys(pattern)
                # Remove namespace prefix from keys
                return [key.decode('utf-8')[len(self.name) + 1:]
                        for key in redis_keys]
            except Exception as e:
                logger.error(f"Redis keys error: {e}")
                return []

    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching a pattern."""
        with self._lock:
            try:
                # Add namespace to pattern
                namespaced_pattern = f"{self.name}:{pattern}"
                keys = self.redis.keys(namespaced_pattern)
                if keys:
                    return self.redis.delete(*keys)
                return 0
            except Exception as e:
                logger.error(f"Redis delete_pattern error: {e}")
                return 0


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
            return {cache.name: cache.get_stats().to_dict()
                    for cache in self._levels}


class QueryCache:
    """Specialized cache for query results with intelligent invalidation."""

    def __init__(self, max_size: int = 10000, name: str = "query_cache"):
        # Multi-level cache setup
        self.name = name
        self._cache = MultiLevelCache(name)

        # Level 1: Fast memory cache for recent queries
        self._cache.add_level(MemoryCache("recent_queries", max_size=1000))

        # Level 2: TTL cache for general queries
        self._cache.add_level(
            TTLMemoryCache(
                "general_queries",
                max_size=max_size,
                default_ttl=1800))

        # Invalidation rules
        self._invalidation_rules: Dict[str, List[str]] = {}

        # Cache key generators
        self._key_generators: Dict[str, Callable[..., Any]] = {}

    def register_invalidation_rule(
            self,
            event: str,
            cache_patterns: List[str]) -> None:
        """Register cache invalidation rules for specific events."""
        self._invalidation_rules[event] = cache_patterns

    def register_key_generator(
            self, operation: str, generator: Callable[..., Any]) -> None:
        """Register a cache key generator for an operation."""
        self._key_generators[operation] = generator

    def get_cached_result(
            self,
            operation: str,
            *args: Any,
            **kwargs: Any) -> Optional[Any]:
        """Get cached result for an operation."""
        cache_key = self._generate_cache_key(operation, *args, **kwargs)
        return self._cache.get(cache_key)

    def cache_result(
            self,
            operation: str,
            result: Any,
            ttl: Optional[float] = None,
            *args: Any,
            **kwargs: Any) -> None:
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
                total_invalidated += self._cache.delete_pattern(
                    formatted_pattern)
            except KeyError as e:
                logger.warning(
                    f"Missing context key for invalidation pattern {pattern}: {e}")

        return total_invalidated

    def _generate_cache_key(self, operation: str, *
                            args: Any, **kwargs: Dict[str, Any]) -> str:
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
        stats["invalidation_rules_count"] = {
            "count": len(self._invalidation_rules)}
        stats["registered_generators"] = {"count": len(self._key_generators)}
        return stats

    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()


class CacheWarmer:
    """Cache warming system for pre-populating frequently accessed data."""

    def __init__(self, cache_manager: QueryCache,
                 graph_instance: Optional[Any] = None):
        self.cache = cache_manager
        self.graph = graph_instance
        self._warming_strategies: Dict[str, Callable[[], None]] = {}
        self._lock = threading.RLock()

    def register_warming_strategy(
            self, name: str, strategy: Callable[[], None]) -> None:
        """Register a cache warming strategy."""
        with self._lock:
            self._warming_strategies[name] = strategy

    def warm_cache(self, strategy_name: Optional[str] = None) -> None:
        """Warm cache using specified strategy or all strategies."""
        with self._lock:
            if strategy_name:
                if strategy_name in self._warming_strategies:
                    try:
                        self._warming_strategies[strategy_name]()
                        logger.info(
                            f"Cache warmed using strategy: {strategy_name}")
                    except Exception as e:
                        logger.error(
                            f"Error warming cache with strategy {strategy_name}: {e}")
                else:
                    logger.warning(
                        f"Warming strategy not found: {strategy_name}")
            else:
                # Warm using all strategies
                for name, strategy in self._warming_strategies.items():
                    try:
                        strategy()
                        logger.info(f"Cache warmed using strategy: {name}")
                    except Exception as e:
                        logger.error(
                            f"Error warming cache with strategy {name}: {e}")

    def warm_frequently_accessed_nodes(self, node_ids: List[str]) -> None:
        """Warm cache for frequently accessed nodes."""
        if not self.graph:
            logger.warning("No graph instance available for cache warming")
            return

        for node_id in node_ids:
            try:
                # Warm node relationships
                if hasattr(self.graph, 'get_node_relationships'):
                    self.graph.get_node_relationships(node_id)

                # Warm node data
                if hasattr(self.graph, 'get_node_by_id'):
                    self.graph.get_node_by_id(node_id)

            except Exception as e:
                logger.error(f"Error warming cache for node {node_id}: {e}")

    def warm_common_queries(self) -> None:
        """Warm cache for common query patterns."""
        if not self.graph:
            logger.warning("No graph instance available for cache warming")
            return

        try:
            # Warm common graph statistics
            if hasattr(self.graph, 'get_node_count'):
                self.graph.get_node_count()

            if hasattr(self.graph, 'get_relationship_count'):
                self.graph.get_relationship_count()

        except Exception as e:
            logger.error(f"Error warming common queries: {e}")

    def schedule_warming(self, interval_seconds: int = 3600) -> None:
        """Schedule periodic cache warming."""
        import threading
        import time

        def _warming_loop():
            while True:
                time.sleep(interval_seconds)
                self.warm_cache()

        warming_thread = threading.Thread(target=_warming_loop, daemon=True)
        warming_thread.start()
        logger.info(
            f"Cache warming scheduled every {interval_seconds} seconds")


class CacheMetrics:
    """Prometheus metrics for cache monitoring."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled and PROMETHEUS_AVAILABLE

        if self.enabled:
            self.cache_hits = Counter(
                'cache_hits_total', 'Total cache hits', [
                    'cache_name', 'cache_type'])
            self.cache_misses = Counter(
                'cache_misses_total', 'Total cache misses', [
                    'cache_name', 'cache_type'])
            self.cache_hit_rate = Gauge(
                'cache_hit_rate', 'Cache hit rate', [
                    'cache_name', 'cache_type'])
            self.cache_size = Gauge(
                'cache_size_bytes', 'Cache size in bytes', [
                    'cache_name', 'cache_type'])
            self.cache_operations = Counter(
                'cache_operations_total', 'Cache operations', [
                    'operation', 'cache_name'])
            self.cache_evictions = Counter(
                'cache_evictions_total', 'Cache evictions', [
                    'cache_name', 'cache_type'])
            self.cache_response_time = Histogram(
                'cache_response_time_seconds', 'Cache response time', [
                    'cache_name', 'operation'])
        else:
            logger.info("Prometheus metrics disabled or not available")

    def record_hit(self, cache_name: str, cache_type: str) -> None:
        """Record a cache hit."""
        if self.enabled:
            self.cache_hits.labels(
                cache_name=cache_name,
                cache_type=cache_type).inc()

    def record_miss(self, cache_name: str, cache_type: str) -> None:
        """Record a cache miss."""
        if self.enabled:
            self.cache_misses.labels(
                cache_name=cache_name,
                cache_type=cache_type).inc()

    def record_eviction(self, cache_name: str, cache_type: str) -> None:
        """Record a cache eviction."""
        if self.enabled:
            self.cache_evictions.labels(
                cache_name=cache_name,
                cache_type=cache_type).inc()

    def update_hit_rate(
            self,
            cache_name: str,
            cache_type: str,
            hit_rate: float) -> None:
        """Update cache hit rate."""
        if self.enabled:
            self.cache_hit_rate.labels(
                cache_name=cache_name,
                cache_type=cache_type).set(hit_rate)

    def update_size(
            self,
            cache_name: str,
            cache_type: str,
            size_bytes: int) -> None:
        """Update cache size."""
        if self.enabled:
            self.cache_size.labels(
                cache_name=cache_name,
                cache_type=cache_type).set(size_bytes)

    def record_operation(self, operation: str, cache_name: str) -> None:
        """Record a cache operation."""
        if self.enabled:
            self.cache_operations.labels(
                operation=operation, cache_name=cache_name).inc()

    def time_operation(self, cache_name: str, operation: str):
        """Context manager for timing cache operations."""
        if self.enabled:
            return self.cache_response_time.labels(
                cache_name=cache_name, operation=operation).time()
        else:
            from contextlib import nullcontext
            return nullcontext()


# Global cache metrics instance
cache_metrics = CacheMetrics()

# Type variable for function decorators
F = TypeVar("F", bound=Callable[..., Any])


def cached(ttl: int = 3600,
           cache_key_func: Optional[Callable[...,
                                             str]] = None,
           invalidate_on: Optional[List[str]] = None,
           cache_instance: Optional[QueryCache] = None) -> Callable[[F],
                                                                    F]:
    """Enhanced cache decorator with configurable options."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Use provided cache instance or create a default one
            cache = cache_instance or QueryCache()

            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                # Create a hash-based key for complex arguments
                key_data = f"{
                    func.__name__}:{
                    str(args)}:{
                    str(
                        sorted(
                            kwargs.items()))}"
                cache_key = f"{
                    func.__name__}:{
                    hashlib.md5(
                        key_data.encode()).hexdigest()}"

            # Try to get from cache
            with cache_metrics.time_operation(cache.name, "get"):
                cached_result = cache.get_cached_result(
                    func.__name__, cache_key)
                if cached_result is not None:
                    cache_metrics.record_hit(cache.name, "decorator")
                    return cached_result

            # Execute function and cache result
            with cache_metrics.time_operation(cache.name, "set"):
                result = func(*args, **kwargs)
                cache.cache_result(func.__name__, result, ttl, cache_key)
                cache_metrics.record_miss(cache.name, "decorator")
                return result

        # Add cache invalidation method to the wrapper
        def _invalidate_cache():
            cache = cache_instance or QueryCache()
            cache.delete_pattern(f"{func.__name__}:*")

        wrapper._cache_invalidate = _invalidate_cache
        return wrapper
    return decorator


# Global cache configuration
@dataclass
class CacheConfig:
    """Configuration for cache settings."""
    default_ttl: int = 3600
    memory_cache_size: int = 1000
    redis_cache_size: int = 10000
    enable_redis: bool = False
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    enable_metrics: bool = True
    warming_interval: int = 3600

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'CacheConfig':
        """Create config from dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})


def create_cache_manager(config: CacheConfig) -> QueryCache:
    """Factory function to create configured cache manager."""
    cache_manager = QueryCache(max_size=config.memory_cache_size)

    # Configure cache levels based on config
    if config.enable_redis and REDIS_AVAILABLE:
        try:
            redis_cache = RedisCache(
                name="redis_cache",
                host=config.redis_host,
                port=config.redis_port,
                db=config.redis_db,
                password=config.redis_password,
                max_size=config.redis_cache_size,
                default_ttl=config.default_ttl
            )
            cache_manager._cache.add_level(redis_cache)
            logger.info("Redis cache layer added to cache manager")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")

    return cache_manager


def cached_operation(cache: QueryCache, operation_name: str,
                     ttl: Optional[float] = None) -> Callable[[F], F]:
    """Decorator to automatically cache operation results."""
    def decorator(func: F) -> F:
        from functools import wraps

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Try to get cached result
            cached_result = cache.get_cached_result(
                operation_name, *args, **kwargs)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.cache_result(operation_name, result, ttl, *args, **kwargs)
            return result

        # Ensure the return type matches the decorated function
        return cast(F, wrapper)
    return decorator
