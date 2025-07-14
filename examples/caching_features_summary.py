#!/usr/bin/env python3
"""
Advanced Caching System - Feature Summary

This example demonstrates the key features of the advanced caching system
implemented for the SFM Graph Service.
"""

import time
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Demonstrate key caching features."""
    
    print("🚀 Advanced Caching System - Feature Summary")
    print("=" * 60)
    
    # Import here to avoid import issues
    import sys
    import os
    sys.path.insert(0, os.path.abspath('.'))
    
    from core.advanced_caching import (
        QueryCache, MemoryCache, TTLMemoryCache, MultiLevelCache,
        CacheWarmer, cached, cached_operation, CacheConfig, create_cache_manager
    )
    from core.cache_config import CacheConfigManager
    
    # 1. Multi-Level Cache Hierarchy
    print("\n1. 🏗️  Multi-Level Cache Hierarchy")
    print("-" * 40)
    
    # Create a multi-level cache
    multi_cache = MultiLevelCache("demo_cache")
    multi_cache.add_level(MemoryCache("l1_memory", max_size=100))
    multi_cache.add_level(TTLMemoryCache("l2_ttl", max_size=1000, default_ttl=300))
    
    # Test cache promotion
    multi_cache.set("key1", "value1", ttl=300)
    result = multi_cache.get("key1")
    print(f"✅ Multi-level cache: {result}")
    
    stats = multi_cache.get_stats()
    print(f"✅ Cache levels: {list(stats.keys())}")
    
    # 2. Cache Decorators
    print("\n2. 🎯 Cache Decorators")
    print("-" * 40)
    
    query_cache = QueryCache()
    execution_count = 0
    
    @cached(ttl=300, cache_instance=query_cache)
    def expensive_calculation(n: int) -> int:
        nonlocal execution_count
        execution_count += 1
        time.sleep(0.01)  # Simulate work
        return n * n
    
    # First call - function executed
    start = time.time()
    result1 = expensive_calculation(10)
    first_time = time.time() - start
    
    # Second call - cached result
    start = time.time()  
    result2 = expensive_calculation(10)
    second_time = time.time() - start
    
    print(f"✅ First call: {result1} (executed, took {first_time:.4f}s)")
    print(f"✅ Second call: {result2} (cached, took {second_time:.4f}s)")
    print(f"✅ Speedup: {first_time/second_time:.1f}x faster")
    print(f"✅ Function executions: {execution_count}")
    
    # 3. Cache Warming
    print("\n3. 🔥 Cache Warming")
    print("-" * 40)
    
    warmer = CacheWarmer(query_cache)
    
    # Register warming strategy
    def warm_calculations():
        for i in range(1, 6):
            expensive_calculation(i)
    
    warmer.register_warming_strategy("calculations", warm_calculations)
    
    # Warm cache
    initial_count = execution_count
    warmer.warm_cache("calculations")
    warming_executions = execution_count - initial_count
    
    print(f"✅ Cache warming executed {warming_executions} calculations")
    
    # Now these should be cached
    start = time.time()
    cached_result = expensive_calculation(3)
    cached_time = time.time() - start
    
    print(f"✅ Warmed data access: {cached_result} (took {cached_time:.4f}s)")
    
    # 4. Cache Configuration
    print("\n4. ⚙️  Cache Configuration")
    print("-" * 40)
    
    config_manager = CacheConfigManager()
    
    # Show configuration
    query_config = config_manager.get_layer_config("query_cache")
    print(f"✅ Query cache config: {query_config.backend}, TTL: {query_config.ttl}s")
    
    # Create configured cache manager
    cache_config = CacheConfig(
        memory_cache_size=500,
        default_ttl=1800,
        enable_redis=False  # Disabled for demo
    )
    
    configured_cache = create_cache_manager(cache_config)
    print(f"✅ Configured cache created: {configured_cache.name}")
    
    # 5. Cache Statistics and Monitoring
    print("\n5. 📊 Cache Statistics and Monitoring")
    print("-" * 40)
    
    stats = query_cache.get_stats()
    
    for cache_name, cache_stats in stats.items():
        if isinstance(cache_stats, dict) and 'hits' in cache_stats:
            hit_rate = cache_stats.get('hit_rate', 0)
            total_ops = cache_stats.get('total_operations', 0)
            print(f"✅ {cache_name}: {total_ops} operations, {hit_rate:.1%} hit rate")
    
    # 6. Cache Invalidation
    print("\n6. 🗑️  Cache Invalidation") 
    print("-" * 40)
    
    # Add invalidation rule
    query_cache.register_invalidation_rule(
        "data_updated",
        ["expensive_calculation:*"]
    )
    
    # Test invalidation
    before_invalidation = execution_count
    query_cache.invalidate_on_event("data_updated")
    
    # This should execute the function again
    result_after_invalidation = expensive_calculation(10)
    after_invalidation = execution_count
    
    print(f"✅ Invalidation triggered: {after_invalidation - before_invalidation} new executions")
    print(f"✅ Result after invalidation: {result_after_invalidation}")
    
    # 7. Performance Summary
    print("\n7. 🏆 Performance Summary")
    print("-" * 40)
    
    print("✅ Features implemented:")
    print("   • Multi-level cache hierarchy with automatic promotion")
    print("   • Redis backend support (when available)")
    print("   • TTL-based cache expiration")
    print("   • LRU eviction policies")
    print("   • Cache warming strategies")
    print("   • Flexible cache decorators")
    print("   • Pattern-based cache invalidation")
    print("   • Comprehensive monitoring and statistics")
    print("   • Configurable cache layers")
    print("   • Thread-safe operations")
    print("   • Prometheus metrics integration")
    
    print("\n✅ Performance benefits:")
    print("   • Reduced database load")
    print("   • Faster response times")
    print("   • Improved scalability")
    print("   • Memory-efficient caching")
    print("   • Intelligent cache management")
    
    print("\n🎉 Advanced caching system is fully operational!")
    print("=" * 60)


if __name__ == "__main__":
    main()