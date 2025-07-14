"""
Advanced Caching Demo - Comprehensive Example

This example demonstrates the advanced caching features implemented 
for the SFM Graph Service, including Redis backends, cache warming,
enhanced decorators, and monitoring.
"""

import time
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the caching components
from core.advanced_caching import (
    QueryCache, RedisCache, CacheWarmer, cached, cached_operation,
    CacheConfig, create_cache_manager, cache_metrics
)
from core.cache_config import CacheConfigManager, CACHE_CONFIG
from core.cache_monitoring import CacheMonitor, monitor_cache_performance


class GraphService:
    """Mock graph service to demonstrate caching features."""
    
    def __init__(self):
        # Initialize cache manager with configuration
        self.cache_config = CacheConfig(
            default_ttl=1800,
            memory_cache_size=1000,
            enable_redis=False,  # Set to True if Redis is available
            enable_metrics=True
        )
        self.cache_manager = create_cache_manager(self.cache_config)
        
        # Initialize cache warmer
        self.cache_warmer = CacheWarmer(self.cache_manager, self)
        
        # Initialize monitoring
        self.cache_monitor = CacheMonitor("graph_service", enable_prometheus=False)
        
        # Mock data
        self.nodes = {f"node_{i}": {"name": f"Node {i}", "type": "actor"} for i in range(1, 101)}
        self.relationships = [
            {"source": f"node_{i}", "target": f"node_{i+1}", "type": "connects_to"}
            for i in range(1, 100)
        ]
        
        # Register cache warming strategies
        self._register_warming_strategies()
    
    def _register_warming_strategies(self):
        """Register cache warming strategies."""
        
        def warm_popular_nodes():
            """Warm cache for popular nodes."""
            popular_nodes = ["node_1", "node_2", "node_3", "node_4", "node_5"]
            for node_id in popular_nodes:
                self.get_node_info(node_id)
                self.get_node_relationships(node_id)
        
        def warm_graph_metrics():
            """Warm cache for graph metrics."""
            self.get_node_count()
            self.get_relationship_count()
            self.calculate_graph_density()
        
        self.cache_warmer.register_warming_strategy("popular_nodes", warm_popular_nodes)
        self.cache_warmer.register_warming_strategy("graph_metrics", warm_graph_metrics)
    
    @cached(ttl=3600, cache_instance=self.cache_manager)
    def get_node_info(self, node_id: str) -> Dict[str, Any]:
        """Get node information - cached for 1 hour."""
        logger.info(f"Fetching node info for {node_id}")
        time.sleep(0.1)  # Simulate database query
        return self.nodes.get(node_id, {})
    
    @cached(ttl=1800, cache_instance=self.cache_manager)
    def get_node_relationships(self, node_id: str) -> List[Dict[str, Any]]:
        """Get relationships for a node - cached for 30 minutes."""
        logger.info(f"Fetching relationships for {node_id}")
        time.sleep(0.05)  # Simulate database query
        return [
            rel for rel in self.relationships
            if rel["source"] == node_id or rel["target"] == node_id
        ]
    
    @cached_operation(cache=self.cache_manager, operation_name="node_count", ttl=7200)
    def get_node_count(self) -> int:
        """Get total node count - cached for 2 hours."""
        logger.info("Calculating node count")
        time.sleep(0.2)  # Simulate expensive operation
        return len(self.nodes)
    
    @cached_operation(cache=self.cache_manager, operation_name="relationship_count", ttl=7200)
    def get_relationship_count(self) -> int:
        """Get total relationship count - cached for 2 hours."""
        logger.info("Calculating relationship count")
        time.sleep(0.2)  # Simulate expensive operation
        return len(self.relationships)
    
    @cached(ttl=3600, cache_instance=self.cache_manager)
    def calculate_graph_density(self) -> float:
        """Calculate graph density - cached for 1 hour."""
        logger.info("Calculating graph density")
        time.sleep(0.5)  # Simulate complex calculation
        
        node_count = self.get_node_count()
        relationship_count = self.get_relationship_count()
        
        if node_count <= 1:
            return 0.0
        
        max_possible_edges = node_count * (node_count - 1)
        return (2 * relationship_count) / max_possible_edges
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        return {
            "cache_manager_stats": self.cache_manager.get_stats(),
            "cache_monitor_metrics": self.cache_monitor.get_performance_metrics().to_dict(),
            "prometheus_metrics": self.cache_monitor.get_prometheus_metrics()
        }


def demonstrate_basic_caching():
    """Demonstrate basic caching functionality."""
    print("\n=== Basic Caching Demo ===")
    
    service = GraphService()
    
    # First call - should hit the database
    print("First call to get_node_info:")
    start_time = time.time()
    node_info = service.get_node_info("node_1")
    first_call_time = time.time() - start_time
    print(f"Result: {node_info}")
    print(f"Time taken: {first_call_time:.4f} seconds")
    
    # Second call - should hit cache
    print("\nSecond call to get_node_info:")
    start_time = time.time()
    node_info = service.get_node_info("node_1")
    second_call_time = time.time() - start_time
    print(f"Result: {node_info}")
    print(f"Time taken: {second_call_time:.4f} seconds")
    
    print(f"\nPerformance improvement: {first_call_time/second_call_time:.2f}x faster")


def demonstrate_cache_warming():
    """Demonstrate cache warming functionality."""
    print("\n=== Cache Warming Demo ===")
    
    service = GraphService()
    
    # Check cache stats before warming
    initial_stats = service.get_cache_stats()
    print("Cache stats before warming:")
    print(f"Cache levels: {list(initial_stats['cache_manager_stats'].keys())}")
    
    # Warm the cache
    print("\nWarming cache...")
    service.cache_warmer.warm_cache()
    
    # Check cache stats after warming
    warmed_stats = service.get_cache_stats()
    print("\nCache stats after warming:")
    print(f"Cache levels: {list(warmed_stats['cache_manager_stats'].keys())}")
    
    # Now access should be faster
    print("\nAccessing warmed data:")
    start_time = time.time()
    node_info = service.get_node_info("node_1")
    access_time = time.time() - start_time
    print(f"Access time for warmed data: {access_time:.4f} seconds")


def demonstrate_cache_invalidation():
    """Demonstrate cache invalidation functionality."""
    print("\n=== Cache Invalidation Demo ===")
    
    service = GraphService()
    
    # Cache some data
    print("Caching node info...")
    service.get_node_info("node_1")
    
    # Show cache stats
    stats = service.get_cache_stats()
    print(f"Cache stats: {stats['cache_manager_stats']}")
    
    # Clear cache
    print("\nClearing cache...")
    service.cache_manager.clear()
    
    # Show cache stats after clearing
    stats = service.get_cache_stats()
    print(f"Cache stats after clearing: {stats['cache_manager_stats']}")


def demonstrate_decorator_features():
    """Demonstrate advanced decorator features."""
    print("\n=== Advanced Decorator Features Demo ===")
    
    # Custom cache key function
    def node_key_func(node_id: str, include_metadata: bool = False) -> str:
        return f"node_data:{node_id}:metadata_{include_metadata}"
    
    @cached(ttl=600, cache_key_func=node_key_func)
    def get_node_with_metadata(node_id: str, include_metadata: bool = False) -> Dict[str, Any]:
        """Get node with optional metadata."""
        logger.info(f"Fetching node {node_id} with metadata={include_metadata}")
        time.sleep(0.1)
        
        base_data = {"id": node_id, "name": f"Node {node_id}"}
        if include_metadata:
            base_data["metadata"] = {"created": "2024-01-01", "updated": "2024-01-15"}
        
        return base_data
    
    # Test custom key function
    print("Testing custom cache key function:")
    result1 = get_node_with_metadata("node_1", include_metadata=True)
    print(f"Result with metadata: {result1}")
    
    result2 = get_node_with_metadata("node_1", include_metadata=False)
    print(f"Result without metadata: {result2}")
    
    # Both should be cached separately due to different keys
    print("Both results cached separately due to different cache keys")


def demonstrate_monitoring():
    """Demonstrate cache monitoring and metrics."""
    print("\n=== Cache Monitoring Demo ===")
    
    service = GraphService()
    
    # Generate some cache activity
    print("Generating cache activity...")
    for i in range(10):
        service.get_node_info(f"node_{i % 5}")  # Some cache hits, some misses
        service.get_node_relationships(f"node_{i % 3}")
    
    # Get comprehensive stats
    stats = service.get_cache_stats()
    
    print("\nCache Statistics:")
    print("=" * 50)
    
    for cache_name, cache_stats in stats['cache_manager_stats'].items():
        if isinstance(cache_stats, dict):
            print(f"\n{cache_name}:")
            for key, value in cache_stats.items():
                print(f"  {key}: {value}")
    
    print(f"\nMonitor Metrics:")
    monitor_metrics = stats['cache_monitor_metrics']
    for key, value in monitor_metrics.items():
        print(f"  {key}: {value}")


def demonstrate_configuration():
    """Demonstrate cache configuration management."""
    print("\n=== Cache Configuration Demo ===")
    
    # Show default configuration
    config_manager = CacheConfigManager()
    print("Default Cache Configuration:")
    print("=" * 40)
    
    for layer_name in ['default', 'query_cache', 'graph_cache']:
        config = config_manager.get_layer_config(layer_name)
        print(f"\n{layer_name}:")
        print(f"  Backend: {config.backend}")
        print(f"  TTL: {config.ttl} seconds")
        print(f"  Max Size: {config.max_size}")
    
    # Show Redis configuration
    redis_config = config_manager.get_redis_config()
    print(f"\nRedis Configuration:")
    print(f"  Host: {redis_config.host}")
    print(f"  Port: {redis_config.port}")
    print(f"  DB: {redis_config.db}")
    
    # Update configuration
    print("\nUpdating configuration...")
    config_manager.update_config({
        "custom_cache": {
            "backend": "memory",
            "ttl": 900,
            "max_size": 2000
        }
    })
    
    custom_config = config_manager.get_layer_config("custom_cache")
    print(f"\nCustom Cache Configuration:")
    print(f"  Backend: {custom_config.backend}")
    print(f"  TTL: {custom_config.ttl} seconds")
    print(f"  Max Size: {custom_config.max_size}")


def main():
    """Run all demonstrations."""
    print("Advanced Caching System Demonstration")
    print("=" * 60)
    
    try:
        demonstrate_basic_caching()
        demonstrate_cache_warming()
        demonstrate_cache_invalidation()
        demonstrate_decorator_features()
        demonstrate_monitoring()
        demonstrate_configuration()
        
        print("\n" + "=" * 60)
        print("All demonstrations completed successfully!")
        print("The advanced caching system is working correctly.")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        logger.exception("Demonstration failed")


if __name__ == "__main__":
    main()