# Core Module Analysis Report
==================================================

## Summary Statistics
- Total methods analyzed: 669
- Stub methods: 62
- Partially implemented methods: 0
- Unused methods: 246
- Potentially incomplete methods: 8

## Stub Methods
------------
### advanced_caching.get
- **File:** core/advanced_caching.py
- **Line:** 423
- **Parameters:** self, key
- **Return Type:** Optional[Any]
- **Docstring:** Get value with cache level promotion....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis

### advanced_caching.warm_common_queries
- **File:** core/advanced_caching.py
- **Line:** 615
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Warm cache for common query patterns....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### advanced_caching.warm_frequently_accessed_nodes
- **File:** core/advanced_caching.py
- **Line:** 596
- **Parameters:** self, node_ids
- **Return Type:** None
- **Docstring:** Warm cache for frequently accessed nodes....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### audit_logger.audit_operation
- **File:** core/audit_logger.py
- **Line:** 218
- **Parameters:** operation_type, operation_name, entity_type, include_performance, level
- **Return Type:** Callable[[F], F]
- **Docstring:** 
    Decorator for automatic audit logging of operations.

    Args:
        operation_type: Type of...
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$

### audit_logger.decorator
- **File:** core/audit_logger.py
- **Line:** 231
- **Parameters:** func
- **Return Type:** F
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$

### audit_logger.wrapper
- **File:** core/audit_logger.py
- **Line:** 233
- **Return Type:** Any
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase

### cache_monitoring._init_prometheus_metrics
- **File:** core/cache_monitoring.py
- **Line:** 62
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Initialize Prometheus metrics....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### memory_management.get_all_node_ids
- **File:** core/memory_management.py
- **Line:** 142
- **Parameters:** self
- **Return Type:** Set[uuid.UUID]
- **Docstring:** Get all node IDs in the graph....
- **Issues:**
  - Stub method - matches pattern: ^\s*\.\.\.\s*$
  - Minimal implementation - only pass/return/ellipsis

### memory_management.get_node_size_estimate
- **File:** core/memory_management.py
- **Line:** 150
- **Parameters:** self, node_id
- **Return Type:** int
- **Docstring:** Get estimated memory size of a node in bytes....
- **Issues:**
  - Stub method - matches pattern: ^\s*\.\.\.\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### memory_management.remove_node_from_memory
- **File:** core/memory_management.py
- **Line:** 146
- **Parameters:** self, node_id
- **Return Type:** bool
- **Docstring:** Remove a node from memory (but not from persistent storage)....
- **Issues:**
  - Stub method - matches pattern: ^\s*\.\.\.\s*$
  - Minimal implementation - only pass/return/ellipsis

### metrics.record_cache_hit
- **File:** core/metrics.py
- **Line:** 188
- **Parameters:** self, cache_type
- **Docstring:** Record cache hit....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### metrics.record_cache_miss
- **File:** core/metrics.py
- **Line:** 195
- **Parameters:** self, cache_type
- **Docstring:** Record cache miss....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### metrics.record_entity_creation
- **File:** core/metrics.py
- **Line:** 166
- **Parameters:** self, entity_type
- **Docstring:** Record entity creation....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### metrics.record_operation_duration
- **File:** core/metrics.py
- **Line:** 209
- **Parameters:** self, operation_type, operation_name, duration
- **Docstring:** Record operation duration....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### metrics.record_query_execution
- **File:** core/metrics.py
- **Line:** 180
- **Parameters:** self, query_type, duration
- **Docstring:** Record query execution....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### metrics.record_relationship_creation
- **File:** core/metrics.py
- **Line:** 173
- **Parameters:** self, relationship_type
- **Docstring:** Record relationship creation....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### metrics.record_system_error
- **File:** core/metrics.py
- **Line:** 202
- **Parameters:** self, error_type
- **Docstring:** Record system error....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### metrics.set_system_info
- **File:** core/metrics.py
- **Line:** 233
- **Parameters:** self, info
- **Docstring:** Set system information....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### metrics.update_active_connections
- **File:** core/metrics.py
- **Line:** 219
- **Parameters:** self, count
- **Docstring:** Update active connections gauge....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### metrics.update_memory_usage
- **File:** core/metrics.py
- **Line:** 226
- **Parameters:** self, usage_type, bytes_used
- **Docstring:** Update memory usage gauge....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.command.get_current_command
- **File:** core/patterns/command.py
- **Line:** 482
- **Parameters:** self
- **Return Type:** Optional[Command]
- **Docstring:** Get the current command in the history....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.decorator._remove_lru
- **File:** core/patterns/decorator.py
- **Line:** 109
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Remove the least recently used entry....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.decorator.get
- **File:** core/patterns/decorator.py
- **Line:** 60
- **Parameters:** self, key
- **Return Type:** Optional[Any]
- **Docstring:** Get a value from the cache....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.dependency_injection._check_circular_dependencies
- **File:** core/patterns/dependency_injection.py
- **Line:** 605
- **Parameters:** self, service_type, visited
- **Return Type:** None
- **Docstring:** Check for circular dependencies starting from a service type....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.dependency_injection._create_instance
- **File:** core/patterns/dependency_injection.py
- **Line:** 350
- **Parameters:** self, implementation_type, scope
- **Return Type:** T
- **Docstring:** Create an instance by invoking the constructor with dependencies....
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.dependency_injection._invoke_factory
- **File:** core/patterns/dependency_injection.py
- **Line:** 398
- **Parameters:** self, factory, scope
- **Return Type:** Any
- **Docstring:** Invoke a factory function with dependency injection....
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.dependency_injection.dispose
- **File:** core/patterns/dependency_injection.py
- **Line:** 75
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Dispose of all services in this scope....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.dependency_injection.try_get
- **File:** core/patterns/dependency_injection.py
- **Line:** 256
- **Parameters:** self, service_type
- **Return Type:** Optional[T]
- **Docstring:** Try to get a service instance, return None if not found....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus._apply_middleware
- **File:** core/patterns/event_bus.py
- **Line:** 402
- **Parameters:** self, event
- **Return Type:** Optional[Event]
- **Docstring:** Apply middleware to transform or filter events....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.event_bus.event_filtering_middleware
- **File:** core/patterns/event_bus.py
- **Line:** 566
- **Parameters:** event
- **Return Type:** Optional[Event]
- **Docstring:** Middleware that filters out certain events....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.publish
- **File:** core/patterns/event_bus.py
- **Line:** 240
- **Parameters:** self, event
- **Return Type:** None
- **Docstring:** 
        Publish an event to all registered handlers.
        
        Args:
            event: The ...
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$

### patterns.plugin._calculate_initialization_order
- **File:** core/patterns/plugin.py
- **Line:** 567
- **Parameters:** self
- **Return Type:** List[str]
- **Docstring:** Calculate plugin initialization order based on dependencies....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.plugin.cleanup
- **File:** core/patterns/plugin.py
- **Line:** 74
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Cleanup plugin resources....
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.plugin.configure
- **File:** core/patterns/plugin.py
- **Line:** 102
- **Parameters:** self, config
- **Return Type:** None
- **Docstring:** Configure the plugin with settings....
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.plugin.get_metadata
- **File:** core/patterns/plugin.py
- **Line:** 64
- **Parameters:** self
- **Return Type:** PluginMetadata
- **Docstring:** Get plugin metadata....
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.plugin.get_plugin_health
- **File:** core/patterns/plugin.py
- **Line:** 525
- **Parameters:** self, plugin_name
- **Return Type:** Optional[Dict[str, Any]]
- **Docstring:** Get health status of a plugin....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_plugin_metrics
- **File:** core/patterns/plugin.py
- **Line:** 540
- **Parameters:** self, plugin_name
- **Return Type:** Optional[Dict[str, Any]]
- **Docstring:** Get metrics from a plugin....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.initialize
- **File:** core/patterns/plugin.py
- **Line:** 69
- **Parameters:** self, framework_context
- **Return Type:** None
- **Docstring:** Initialize the plugin with framework context....
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.plugin.visit
- **File:** core/patterns/plugin.py
- **Line:** 574
- **Parameters:** plugin_name
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$

### patterns.strategy.find_path
- **File:** core/patterns/strategy.py
- **Line:** 324
- **Parameters:** self, graph, source, target
- **Return Type:** Optional[List[uuid.UUID]]
- **Docstring:** Find the first shortest path (for compatibility with interface)....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis

### patterns.strategy.get_strategy
- **File:** core/patterns/strategy.py
- **Line:** 405
- **Parameters:** self, category, strategy_name
- **Return Type:** Optional[Strategy]
- **Docstring:** Get a strategy by category and name....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis

### performance_metrics.decorator
- **File:** core/performance_metrics.py
- **Line:** 326
- **Parameters:** func
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$

### performance_metrics.increment_counter
- **File:** core/performance_metrics.py
- **Line:** 176
- **Parameters:** self, counter_name, value, metadata
- **Docstring:** Increment a counter metric....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$

### performance_metrics.record_histogram
- **File:** core/performance_metrics.py
- **Line:** 200
- **Parameters:** self, histogram_name, value, metadata
- **Docstring:** Record a value in a histogram metric....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Unused method - not called anywhere in codebase

### performance_metrics.record_operation
- **File:** core/performance_metrics.py
- **Line:** 162
- **Parameters:** self, operation_name, duration, success, metadata
- **Docstring:** Record an operation's performance metrics....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$

### performance_metrics.set_gauge
- **File:** core/performance_metrics.py
- **Line:** 189
- **Parameters:** self, gauge_name, value, metadata
- **Docstring:** Set a gauge metric value....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$

### performance_metrics.timed_operation
- **File:** core/performance_metrics.py
- **Line:** 318
- **Parameters:** operation_name, include_args
- **Docstring:** 
    Decorator to automatically time operations and record metrics.
    
    Args:
        operation...
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$

### performance_metrics.wrapper
- **File:** core/performance_metrics.py
- **Line:** 330
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase

### security_validators.validate_node_description
- **File:** core/security_validators.py
- **Line:** 461
- **Parameters:** description
- **Return Type:** Optional[str]
- **Docstring:** 
    Validate and sanitize a node description.

    Args:
        description: Description to valida...
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$

### sfm_enums.validate_cross_entity_consistency
- **File:** core/sfm_enums.py
- **Line:** 3044
- **Parameters:** entity_1_type, entity_2_type, relationship_kind, context
- **Return Type:** None
- **Docstring:** Validate consistency across multiple entities in SFM framework.
        
        This method impleme...
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase

### sfm_enums.validate_legitimacy_source_context
- **File:** core/sfm_enums.py
- **Line:** 2816
- **Parameters:** source, institutional_context
- **Return Type:** None
- **Docstring:** Validate LegitimacySource appropriateness for institutional context.

        Args:
            sour...
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase

### sfm_enums.validate_required_enum_context
- **File:** core/sfm_enums.py
- **Line:** 2732
- **Parameters:** enum_value, context, is_required
- **Return Type:** None
- **Docstring:** Validate whether an enum is required or optional in given context.

        Args:
            enum_v...
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase

### sfm_persistence._count_backups
- **File:** core/sfm_persistence.py
- **Line:** 908
- **Parameters:** self, stats
- **Return Type:** None
- **Docstring:** Count backup files with size calculation, validation, and age tracking....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis

### sfm_persistence._get_metadata
- **File:** core/sfm_persistence.py
- **Line:** 977
- **Parameters:** self, graph_id, version
- **Return Type:** Optional[GraphMetadata]
- **Docstring:** Load metadata for a graph with enhanced validation and error handling....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$

### sfm_persistence._load_metadata_data
- **File:** core/sfm_persistence.py
- **Line:** 1109
- **Parameters:** self, graph_id, version
- **Return Type:** Optional[Dict[str, Any]]
- **Docstring:** Load raw metadata data from file....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$

### sfm_persistence.load_graph
- **File:** core/sfm_persistence.py
- **Line:** 687
- **Parameters:** self, graph_id, version
- **Return Type:** Optional[SFMGraph]
- **Docstring:** 
        Load an SFM graph from persistent storage.

        Args:
            graph_id: Unique iden...
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$

### sfm_query.find_shortest_path
- **File:** core/sfm_query.py
- **Line:** 386
- **Parameters:** self, source_id, target_id, relationship_kinds
- **Return Type:** Optional[List[uuid.UUID]]
- **Docstring:** Find shortest path between two nodes....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$

### sfm_service._check_circular_dependencies
- **File:** core/sfm_service.py
- **Line:** 1796
- **Parameters:** self
- **Return Type:** List[Dict[str, Any]]
- **Docstring:** Check for circular dependencies that could cause issues....
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis

### sfm_service.find_shortest_path
- **File:** core/sfm_service.py
- **Line:** 1309
- **Parameters:** self, source_id, target_id, relationship_kinds
- **Return Type:** Optional[List[str]]
- **Docstring:** 
        Find the shortest path between two nodes.

        Args:
            source_id: ID of the s...
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$

### sfm_service.get_entity
- **File:** core/sfm_service.py
- **Line:** 934
- **Parameters:** self, entity_type, entity_id
- **Return Type:** Optional[T]
- **Docstring:** Generic method to retrieve any entity by type and ID....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis

### sfm_service.get_relationship
- **File:** core/sfm_service.py
- **Line:** 981
- **Parameters:** self, rel_id
- **Return Type:** Optional[RelationshipResponse]
- **Docstring:** Get a relationship by ID....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Unused method - not called anywhere in codebase

### transaction_manager.add_operation
- **File:** core/transaction_manager.py
- **Line:** 137
- **Parameters:** self, operation_type, data, rollback_data, rollback_function
- **Return Type:** Optional[str]
- **Docstring:** 
        Add an operation to the current transaction.
        
        Args:
            operation_t...
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$


## Partially Implemented Methods
-----------------------------
No methods found in this category.

## Unused Methods
--------------
### advanced_caching._warming_loop
- **File:** core/advanced_caching.py
- **Line:** 634
- **Issues:**
  - Unused method - not called anywhere in codebase

### advanced_caching.cached
- **File:** core/advanced_caching.py
- **Line:** 721
- **Parameters:** ttl, cache_key_func, invalidate_on, cache_instance
- **Return Type:** Callable[[F], F]
- **Docstring:** Enhanced cache decorator with configurable options.

    Args:
        ttl: Time to live for cached ...
- **Issues:**
  - Unused method - not called anywhere in codebase

### advanced_caching.cached_operation
- **File:** core/advanced_caching.py
- **Line:** 819
- **Parameters:** cache, operation_name, ttl
- **Return Type:** Callable[[F], F]
- **Docstring:** Decorator to automatically cache operation results....
- **Issues:**
  - Unused method - not called anywhere in codebase

### advanced_caching.create_cache_manager
- **File:** core/advanced_caching.py
- **Line:** 795
- **Parameters:** config
- **Return Type:** QueryCache
- **Docstring:** Factory function to create configured cache manager....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### advanced_caching.from_dict
- **File:** core/advanced_caching.py
- **Line:** 790
- **Parameters:** cls, config_dict
- **Return Type:** 'CacheConfig'
- **Docstring:** Create config from dictionary....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### advanced_caching.record_eviction
- **File:** core/advanced_caching.py
- **Line:** 685
- **Parameters:** self, cache_name, cache_type
- **Return Type:** None
- **Docstring:** Record a cache eviction....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### advanced_caching.register_key_generator
- **File:** core/advanced_caching.py
- **Line:** 496
- **Parameters:** self, operation, generator
- **Return Type:** None
- **Docstring:** Register a cache key generator for an operation....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### advanced_caching.register_warming_strategy
- **File:** core/advanced_caching.py
- **Line:** 570
- **Parameters:** self, name, strategy
- **Return Type:** None
- **Docstring:** Register a cache warming strategy....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### advanced_caching.schedule_warming
- **File:** core/advanced_caching.py
- **Line:** 632
- **Parameters:** self, interval_seconds
- **Return Type:** None
- **Docstring:** Schedule periodic cache warming....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### advanced_caching.update_hit_rate
- **File:** core/advanced_caching.py
- **Line:** 690
- **Parameters:** self, cache_name, cache_type, hit_rate
- **Return Type:** None
- **Docstring:** Update cache hit rate....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### advanced_caching.update_size
- **File:** core/advanced_caching.py
- **Line:** 695
- **Parameters:** self, cache_name, cache_type, size_bytes
- **Return Type:** None
- **Docstring:** Update cache size....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### advanced_caching.warm_common_queries
- **File:** core/advanced_caching.py
- **Line:** 615
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Warm cache for common query patterns....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### advanced_caching.warm_frequently_accessed_nodes
- **File:** core/advanced_caching.py
- **Line:** 596
- **Parameters:** self, node_ids
- **Return Type:** None
- **Docstring:** Warm cache for frequently accessed nodes....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### advanced_caching.wrapper
- **File:** core/advanced_caching.py
- **Line:** 824
- **Return Type:** Any
- **Issues:**
  - Unused method - not called anywhere in codebase

### audit_logger.wrapper
- **File:** core/audit_logger.py
- **Line:** 233
- **Return Type:** Any
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase

### cache_config.get_layer_config
- **File:** core/cache_config.py
- **Line:** 78
- **Parameters:** self, layer_name
- **Return Type:** CacheLayerConfig
- **Docstring:** Get configuration for a specific cache layer....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### cache_config.get_redis_config
- **File:** core/cache_config.py
- **Line:** 87
- **Parameters:** self
- **Return Type:** RedisConfig
- **Docstring:** Get Redis configuration....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### cache_config.update_config
- **File:** core/cache_config.py
- **Line:** 97
- **Parameters:** self, updates
- **Return Type:** None
- **Docstring:** Update configuration with new values....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### cache_monitoring.generate_cache_report
- **File:** core/cache_monitoring.py
- **Line:** 239
- **Parameters:** caches
- **Return Type:** Dict[str, Any]
- **Docstring:** Generate a comprehensive cache performance report....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### cache_monitoring.get_prometheus_metrics
- **File:** core/cache_monitoring.py
- **Line:** 193
- **Parameters:** self
- **Return Type:** Dict[str, Any]
- **Docstring:** Get Prometheus metrics (if available)....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### cache_monitoring.record_eviction
- **File:** core/cache_monitoring.py
- **Line:** 130
- **Parameters:** self, cache_type
- **Return Type:** None
- **Docstring:** Record a cache eviction....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### cache_monitoring.update_cache_size
- **File:** core/cache_monitoring.py
- **Line:** 154
- **Parameters:** self, size_bytes, cache_type
- **Return Type:** None
- **Docstring:** Update cache size....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### cache_monitoring.update_hit_rate
- **File:** core/cache_monitoring.py
- **Line:** 146
- **Parameters:** self, hit_rate, cache_type
- **Return Type:** None
- **Docstring:** Update cache hit rate....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### exceptions.create_database_error
- **File:** core/exceptions.py
- **Line:** 516
- **Parameters:** message, database_type
- **Return Type:** DatabaseConnectionError
- **Docstring:** Create a standardized database connection error....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### exceptions.create_node_creation_error
- **File:** core/exceptions.py
- **Line:** 502
- **Parameters:** message, node_type, node_id
- **Return Type:** NodeCreationError
- **Docstring:** Create a standardized node creation error....
- **Issues:**
  - Unused method - not called anywhere in codebase

### exceptions.create_not_found_error
- **File:** core/exceptions.py
- **Line:** 492
- **Parameters:** entity_type, entity_id
- **Return Type:** SFMNotFoundError
- **Docstring:** Create a standardized not found error....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### exceptions.create_query_error
- **File:** core/exceptions.py
- **Line:** 511
- **Parameters:** message, query
- **Return Type:** QueryExecutionError
- **Docstring:** Create a standardized query execution error....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### exceptions.create_validation_error
- **File:** core/exceptions.py
- **Line:** 497
- **Parameters:** message, field, value
- **Return Type:** SFMValidationError
- **Docstring:** Create a standardized validation error....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### graph.clear_all_caches
- **File:** core/graph.py
- **Line:** 529
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Clear all caches....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### graph.disable_lazy_loading
- **File:** core/graph.py
- **Line:** 401
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Disable lazy loading....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### graph.enable_advanced_caching
- **File:** core/graph.py
- **Line:** 523
- **Parameters:** self, enable
- **Return Type:** None
- **Docstring:** Enable or disable advanced caching....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### graph.enable_lazy_loading
- **File:** core/graph.py
- **Line:** 392
- **Parameters:** self, node_loader
- **Return Type:** None
- **Docstring:** Enable lazy loading with a custom node loader function.

        Args:
            node_loader: Func...
- **Issues:**
  - Unused method - not called anywhere in codebase

### graph.force_memory_cleanup
- **File:** core/graph.py
- **Line:** 493
- **Parameters:** self
- **Return Type:** int
- **Docstring:** Force memory cleanup by evicting nodes....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### graph.get_cache_stats
- **File:** core/graph.py
- **Line:** 536
- **Parameters:** self
- **Return Type:** Dict[str, Any]
- **Docstring:** Get comprehensive cache statistics....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### graph.get_memory_stats
- **File:** core/graph.py
- **Line:** 504
- **Parameters:** self
- **Return Type:** Dict[str, Any]
- **Docstring:** Get memory management statistics....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### graph.get_memory_usage
- **File:** core/graph.py
- **Line:** 487
- **Parameters:** self
- **Return Type:** MemoryUsageStats
- **Docstring:** Get current memory usage statistics....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### graph.get_node_size_estimate
- **File:** core/graph.py
- **Line:** 460
- **Parameters:** self, node_id
- **Return Type:** int
- **Docstring:** Get estimated memory size of a node in bytes....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### graph.set_eviction_strategy
- **File:** core/graph.py
- **Line:** 499
- **Parameters:** self, strategy
- **Return Type:** None
- **Docstring:** Set the node eviction strategy....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### graph.set_memory_limit
- **File:** core/graph.py
- **Line:** 481
- **Parameters:** self, limit_mb
- **Return Type:** None
- **Docstring:** Set the memory limit for the graph....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### health_checker.check_all
- **File:** core/health_checker.py
- **Line:** 350
- **Parameters:** self
- **Return Type:** HealthSummary
- **Docstring:** Run all health checks and return summary....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### health_checker.check_liveness
- **File:** core/health_checker.py
- **Line:** 358
- **Parameters:** self
- **Return Type:** HealthSummary
- **Docstring:** Run liveness health checks....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### health_checker.check_readiness
- **File:** core/health_checker.py
- **Line:** 362
- **Parameters:** self
- **Return Type:** HealthSummary
- **Docstring:** Run readiness health checks....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### health_checker.check_startup
- **File:** core/health_checker.py
- **Line:** 354
- **Parameters:** self
- **Return Type:** HealthSummary
- **Docstring:** Run startup health checks....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### health_checker.get_health_checker
- **File:** core/health_checker.py
- **Line:** 427
- **Return Type:** HealthChecker
- **Docstring:** Get the global health checker instance....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### health_checker.remove_check
- **File:** core/health_checker.py
- **Line:** 342
- **Parameters:** self, check_name
- **Docstring:** Remove a health check by name....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### lock_manager.force_release_all_locks
- **File:** core/lock_manager.py
- **Line:** 197
- **Parameters:** self, entity_id
- **Return Type:** None
- **Docstring:** 
        Force release all locks (emergency use only).
        
        Args:
            entity_id:...
- **Issues:**
  - Unused method - not called anywhere in codebase

### lock_manager.get_lock_info
- **File:** core/lock_manager.py
- **Line:** 159
- **Parameters:** self, entity_id
- **Return Type:** Dict[str, Any]
- **Docstring:** 
        Get information about locks for a specific entity.
        
        Args:
            entit...
- **Issues:**
  - Unused method - not called anywhere in codebase

### lock_manager.reset_lock_manager
- **File:** core/lock_manager.py
- **Line:** 234
- **Return Type:** None
- **Docstring:** Reset the global lock manager (for testing)....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### logging_config.configure_logging
- **File:** core/logging_config.py
- **Line:** 239
- **Parameters:** config
- **Docstring:** Configure the global logging system....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### logging_config.critical
- **File:** core/logging_config.py
- **Line:** 83
- **Parameters:** self, message
- **Docstring:** Log a critical message with structured format....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### logging_config.monitor_performance
- **File:** core/logging_config.py
- **Line:** 200
- **Parameters:** operation_name
- **Docstring:** 
    Decorator for automatic performance monitoring and logging.
    
    Args:
        operation_na...
- **Issues:**
  - Unused method - not called anywhere in codebase

### logging_config.wrapper
- **File:** core/logging_config.py
- **Line:** 209
- **Issues:**
  - Unused method - not called anywhere in codebase

### memory_management.current_strategy
- **File:** core/memory_management.py
- **Line:** 230
- **Parameters:** self, strategy
- **Docstring:** Set the eviction strategy....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### memory_management.get_access_count
- **File:** core/memory_management.py
- **Line:** 128
- **Parameters:** self, node_id
- **Return Type:** int
- **Docstring:** Get the access count for a node....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### memory_management.get_node_size_estimate
- **File:** core/memory_management.py
- **Line:** 150
- **Parameters:** self, node_id
- **Return Type:** int
- **Docstring:** Get estimated memory size of a node in bytes....
- **Issues:**
  - Stub method - matches pattern: ^\s*\.\.\.\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### metrics.add_custom_collector
- **File:** core/metrics.py
- **Line:** 356
- **Parameters:** self, name, collector
- **Docstring:** Add a custom metrics collector....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### metrics.collect_custom_metrics
- **File:** core/metrics.py
- **Line:** 361
- **Parameters:** self
- **Docstring:** Collect metrics from custom collectors....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### metrics.configure_metrics
- **File:** core/metrics.py
- **Line:** 446
- **Parameters:** config
- **Docstring:** Configure the global metrics system....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### metrics.get_performance_summary
- **File:** core/metrics.py
- **Line:** 377
- **Parameters:** self
- **Return Type:** Dict[str, Any]
- **Docstring:** Get performance metrics summary....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### metrics.get_prometheus_metrics
- **File:** core/metrics.py
- **Line:** 371
- **Parameters:** self
- **Return Type:** str
- **Docstring:** Get metrics in Prometheus format....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### metrics.monitor_performance
- **File:** core/metrics.py
- **Line:** 382
- **Parameters:** operation_type, entity_type
- **Docstring:** 
    Decorator for automatic performance monitoring.
    
    Args:
        operation_type: Type of ...
- **Issues:**
  - Unused method - not called anywhere in codebase

### metrics.record_cache_operation
- **File:** core/metrics.py
- **Line:** 323
- **Parameters:** self, operation, cache_type
- **Docstring:** Record cache operation metrics....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### metrics.set_system_info
- **File:** core/metrics.py
- **Line:** 233
- **Parameters:** self, info
- **Docstring:** Set system information....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### metrics.update_system_metrics
- **File:** core/metrics.py
- **Line:** 344
- **Parameters:** self, metrics
- **Docstring:** Update system-level metrics....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### metrics.wrapper
- **File:** core/metrics.py
- **Line:** 392
- **Issues:**
  - Unused method - not called anywhere in codebase

### monitoring_middleware.create_monitoring_middleware
- **File:** core/monitoring_middleware.py
- **Line:** 339
- **Parameters:** app, config
- **Return Type:** ASGIApp
- **Docstring:** 
    Create and configure monitoring middleware for the application.
    
    Args:
        app: ASG...
- **Issues:**
  - Unused method - not called anywhere in codebase

### patterns.command.clear_history
- **File:** core/patterns/command.py
- **Line:** 476
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Clear the command history....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.command.get_current_command
- **File:** core/patterns/command.py
- **Line:** 482
- **Parameters:** self
- **Return Type:** Optional[Command]
- **Docstring:** Get the current command in the history....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.command.get_redo_stack
- **File:** core/patterns/command.py
- **Line:** 471
- **Parameters:** self
- **Return Type:** List[CommandMetadata]
- **Docstring:** Get commands that can be redone....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.command.get_undo_stack
- **File:** core/patterns/command.py
- **Line:** 466
- **Parameters:** self
- **Return Type:** List[CommandMetadata]
- **Docstring:** Get commands that can be undone....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.decorator.clear_all_caches
- **File:** core/patterns/decorator.py
- **Line:** 479
- **Return Type:** None
- **Docstring:** Clear all caches from the default cache manager....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.decorator.clear_audit_log
- **File:** core/patterns/decorator.py
- **Line:** 484
- **Return Type:** None
- **Docstring:** Clear the default audit log....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.decorator.enhanced_operation
- **File:** core/patterns/decorator.py
- **Line:** 444
- **Parameters:** validator, cache_ttl, audit_level, max_retries
- **Return Type:** Callable[[F], F]
- **Docstring:** 
    Decorator that combines validation, caching, auditing, and retry logic.
    
    This demonstra...
- **Issues:**
  - Unused method - not called anywhere in codebase

### patterns.decorator.get_audit_entries
- **File:** core/patterns/decorator.py
- **Line:** 469
- **Parameters:** limit, level
- **Return Type:** List[AuditLogEntry]
- **Docstring:** Get entries from the default audit logger....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.decorator.get_cache_stats
- **File:** core/patterns/decorator.py
- **Line:** 464
- **Return Type:** Dict[str, Any]
- **Docstring:** Get statistics from the default cache manager....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.decorator.get_timing_stats
- **File:** core/patterns/decorator.py
- **Line:** 474
- **Parameters:** func_name
- **Return Type:** Dict[str, Any]
- **Docstring:** Get timing statistics from the default timing decorator....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.decorator.retry_on_failure
- **File:** core/patterns/decorator.py
- **Line:** 417
- **Parameters:** max_retries, delay, backoff_factor, exceptions
- **Return Type:** Callable[[F], F]
- **Docstring:** Decorator to retry failed operations....
- **Issues:**
  - Unused method - not called anywhere in codebase

### patterns.decorator.time_execution
- **File:** core/patterns/decorator.py
- **Line:** 412
- **Parameters:** log_results
- **Return Type:** Callable[[F], F]
- **Docstring:** Decorator to time function execution....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.decorator.validate_inputs
- **File:** core/patterns/decorator.py
- **Line:** 395
- **Parameters:** validator
- **Return Type:** Callable[[F], F]
- **Docstring:** Decorator to validate method inputs....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.decorator.validate_non_empty_string
- **File:** core/patterns/decorator.py
- **Line:** 490
- **Parameters:** obj, field_name, value
- **Return Type:** bool
- **Docstring:** Validate that a string field is not empty....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.decorator.validate_positive_number
- **File:** core/patterns/decorator.py
- **Line:** 495
- **Parameters:** obj, field_name, value
- **Return Type:** bool
- **Docstring:** Validate that a number is positive....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.decorator.validate_uuid_format
- **File:** core/patterns/decorator.py
- **Line:** 500
- **Parameters:** obj, field_name, value
- **Return Type:** bool
- **Docstring:** Validate that a string is a valid UUID format....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.decorator.wrapper
- **File:** core/patterns/decorator.py
- **Line:** 368
- **Issues:**
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.add_decorator
- **File:** core/patterns/dependency_injection.py
- **Line:** 507
- **Parameters:** self, decorator
- **Return Type:** 'DIContainer'
- **Docstring:** Add a decorator to modify service instances....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.add_event_handler
- **File:** core/patterns/dependency_injection.py
- **Line:** 517
- **Parameters:** self, event_name, handler
- **Return Type:** 'DIContainer'
- **Docstring:** Add an event handler....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.add_middleware
- **File:** core/patterns/dependency_injection.py
- **Line:** 512
- **Parameters:** self, middleware
- **Return Type:** 'DIContainer'
- **Docstring:** Add middleware to modify service creation context....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.configure_global_container
- **File:** core/patterns/dependency_injection.py
- **Line:** 656
- **Parameters:** configurator
- **Return Type:** None
- **Docstring:** Configure the global container....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.example_configuration
- **File:** core/patterns/dependency_injection.py
- **Line:** 689
- **Docstring:** Example of how to configure the DI container....
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.get_dependency_graph
- **File:** core/patterns/dependency_injection.py
- **Line:** 631
- **Parameters:** self
- **Return Type:** Dict[str, List[str]]
- **Docstring:** Get the dependency graph as a dictionary....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.get_global_container
- **File:** core/patterns/dependency_injection.py
- **Line:** 646
- **Return Type:** DIContainer
- **Docstring:** Get the global DI container instance....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.get_service
- **File:** core/patterns/dependency_injection.py
- **Line:** 62
- **Parameters:** self, service_type
- **Return Type:** T
- **Docstring:** Get a service within this scope....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.get_service_info
- **File:** core/patterns/dependency_injection.py
- **Line:** 541
- **Parameters:** self, service_type
- **Return Type:** Optional[ServiceDescriptor]
- **Docstring:** Get information about a registered service....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.inject
- **File:** core/patterns/dependency_injection.py
- **Line:** 651
- **Parameters:** service_type
- **Return Type:** T
- **Docstring:** Inject a service from the global container....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.is_registered
- **File:** core/patterns/dependency_injection.py
- **Line:** 537
- **Parameters:** self, service_type
- **Return Type:** bool
- **Docstring:** Check if a service type is registered....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.list_services
- **File:** core/patterns/dependency_injection.py
- **Line:** 545
- **Parameters:** self
- **Return Type:** List[ServiceDescriptor]
- **Docstring:** List all registered services....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.logging_interceptor
- **File:** core/patterns/dependency_injection.py
- **Line:** 706
- **Parameters:** service_type, instance
- **Return Type:** Any
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.register_instance
- **File:** core/patterns/dependency_injection.py
- **Line:** 226
- **Parameters:** self, service_type, instance, lifecycle
- **Return Type:** 'DIContainer'
- **Docstring:** Register a specific instance....
- **Issues:**
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.scope
- **File:** core/patterns/dependency_injection.py
- **Line:** 529
- **Parameters:** self
- **Docstring:** Context manager for service scopes....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.try_get
- **File:** core/patterns/dependency_injection.py
- **Line:** 256
- **Parameters:** self, service_type
- **Return Type:** Optional[T]
- **Docstring:** Try to get a service instance, return None if not found....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.unregister
- **File:** core/patterns/dependency_injection.py
- **Line:** 549
- **Parameters:** self, service_type
- **Return Type:** bool
- **Docstring:** Unregister a service type....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.validate_configuration
- **File:** core/patterns/dependency_injection.py
- **Line:** 584
- **Parameters:** self
- **Return Type:** List[str]
- **Docstring:** Validate the container configuration and return any issues....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.add_error_handler
- **File:** core/patterns/event_bus.py
- **Line:** 452
- **Parameters:** self, error_handler
- **Return Type:** None
- **Docstring:** Add error handler to process exceptions from event handlers....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.add_filter
- **File:** core/patterns/event_bus.py
- **Line:** 456
- **Parameters:** self, filter_func
- **Return Type:** None
- **Docstring:** Add filter to determine which events should be processed....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.add_middleware
- **File:** core/patterns/event_bus.py
- **Line:** 448
- **Parameters:** self, middleware
- **Return Type:** None
- **Docstring:** Add middleware to process events before they reach handlers....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.clear_handlers
- **File:** core/patterns/event_bus.py
- **Line:** 488
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Clear all handlers....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.clear_history
- **File:** core/patterns/event_bus.py
- **Line:** 484
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Clear event history....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.event_enrichment_middleware
- **File:** core/patterns/event_bus.py
- **Line:** 559
- **Parameters:** event
- **Return Type:** Event
- **Docstring:** Middleware that enriches events with additional metadata....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.event_filtering_middleware
- **File:** core/patterns/event_bus.py
- **Line:** 566
- **Parameters:** event
- **Return Type:** Optional[Event]
- **Docstring:** Middleware that filters out certain events....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.event_transformation_middleware
- **File:** core/patterns/event_bus.py
- **Line:** 574
- **Parameters:** event
- **Return Type:** Event
- **Docstring:** Middleware that transforms event data....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.get_event_history
- **File:** core/patterns/event_bus.py
- **Line:** 460
- **Parameters:** self, limit
- **Return Type:** List[Event]
- **Docstring:** Get event history....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.get_global_event_bus
- **File:** core/patterns/event_bus.py
- **Line:** 585
- **Return Type:** EventBus
- **Docstring:** Get the global event bus instance....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.get_handler_metadata
- **File:** core/patterns/event_bus.py
- **Line:** 466
- **Parameters:** self, handler_id
- **Return Type:** Union[EventHandlerMetadata, List[EventHandlerMetadata]]
- **Docstring:** Get metadata for handlers....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.get_supported_event_types
- **File:** core/patterns/event_bus.py
- **Line:** 553
- **Parameters:** self
- **Return Type:** List[str]
- **Docstring:** Supported event types for cache invalidation....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.publish_event
- **File:** core/patterns/event_bus.py
- **Line:** 590
- **Parameters:** event_type, data
- **Return Type:** None
- **Docstring:** Convenience function to publish an event to the global event bus....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.stop_async_processing
- **File:** core/patterns/event_bus.py
- **Line:** 305
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Stop asynchronous event processing....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.subscribe_to_all
- **File:** core/patterns/event_bus.py
- **Line:** 174
- **Parameters:** self, handler
- **Return Type:** str
- **Docstring:** 
        Subscribe a handler to all events (wildcard subscription).
        
        Args:
         ...
- **Issues:**
  - Unused method - not called anywhere in codebase

### patterns.event_bus.subscribe_to_event
- **File:** core/patterns/event_bus.py
- **Line:** 596
- **Parameters:** event_type, handler, priority
- **Return Type:** str
- **Docstring:** Convenience function to subscribe to an event on the global event bus....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.event_bus.unsubscribe
- **File:** core/patterns/event_bus.py
- **Line:** 204
- **Parameters:** self, event_type, handler_id
- **Return Type:** bool
- **Docstring:** 
        Unsubscribe a handler from an event type.
        
        Args:
            event_type: Th...
- **Issues:**
  - Unused method - not called anywhere in codebase

### patterns.observer._notify_node_removed
- **File:** core/patterns/observer.py
- **Line:** 92
- **Parameters:** self, node_id
- **Return Type:** None
- **Docstring:** Notify all observers that a node was removed....
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer._notify_node_updated
- **File:** core/patterns/observer.py
- **Line:** 101
- **Parameters:** self, node, previous_state
- **Return Type:** None
- **Docstring:** Notify all observers that a node was updated....
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer._notify_relationship_removed
- **File:** core/patterns/observer.py
- **Line:** 128
- **Parameters:** self, relationship_id
- **Return Type:** None
- **Docstring:** Notify all observers that a relationship was removed....
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer._notify_relationship_updated
- **File:** core/patterns/observer.py
- **Line:** 137
- **Parameters:** self, relationship, previous_state
- **Return Type:** None
- **Docstring:** Notify all observers that a relationship was updated....
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer.add_observer
- **File:** core/patterns/observer.py
- **Line:** 64
- **Parameters:** self, observer
- **Return Type:** None
- **Docstring:** Add an observer to be notified of graph changes....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer.clear_change_history
- **File:** core/patterns/observer.py
- **Line:** 172
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Clear the change history....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer.clear_invalidated_caches
- **File:** core/patterns/observer.py
- **Line:** 234
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Clear the list of invalidated caches....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer.clear_observers
- **File:** core/patterns/observer.py
- **Line:** 74
- **Parameters:** self
- **Return Type:** None
- **Docstring:** Remove all observers....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer.get_change_history
- **File:** core/patterns/observer.py
- **Line:** 166
- **Parameters:** self, limit
- **Return Type:** List[Dict[str, Any]]
- **Docstring:** Get the change history, optionally limited to recent changes....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer.get_invalidated_caches
- **File:** core/patterns/observer.py
- **Line:** 230
- **Parameters:** self
- **Return Type:** List[str]
- **Docstring:** Get the list of invalidated caches....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer.get_observers
- **File:** core/patterns/observer.py
- **Line:** 78
- **Parameters:** self
- **Return Type:** List[GraphChangeObserver]
- **Docstring:** Get a copy of the current observers list....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer.remove_observer
- **File:** core/patterns/observer.py
- **Line:** 69
- **Parameters:** self, observer
- **Return Type:** None
- **Docstring:** Remove an observer from the notification list....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.activate_all_plugins
- **File:** core/patterns/plugin.py
- **Line:** 598
- **Parameters:** self
- **Return Type:** Dict[str, bool]
- **Docstring:** Activate all loaded plugins in dependency order....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.add_plugin_directory
- **File:** core/patterns/plugin.py
- **Line:** 267
- **Parameters:** self, directory
- **Return Type:** None
- **Docstring:** Add a directory to search for plugins....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.configure_plugin
- **File:** core/patterns/plugin.py
- **Line:** 507
- **Parameters:** self, plugin_name, config
- **Return Type:** bool
- **Docstring:** Configure a plugin with settings....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.discover_plugins
- **File:** core/patterns/plugin.py
- **Line:** 276
- **Parameters:** self
- **Return Type:** List[str]
- **Docstring:** Discover plugins in the registered directories....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_analyzer
- **File:** core/patterns/plugin.py
- **Line:** 178
- **Parameters:** self, name
- **Return Type:** Optional[Callable]
- **Docstring:** Get an analyzer by name....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_configuration_schema
- **File:** core/patterns/plugin.py
- **Line:** 98
- **Parameters:** self
- **Return Type:** Dict[str, Any]
- **Docstring:** Get configuration schema for this plugin....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_entity_type
- **File:** core/patterns/plugin.py
- **Line:** 170
- **Parameters:** self, type_name
- **Return Type:** Optional[Type[Node]]
- **Docstring:** Get an entity type by name....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_event_handler
- **File:** core/patterns/plugin.py
- **Line:** 186
- **Parameters:** self, event_type
- **Return Type:** Optional[Callable]
- **Docstring:** Get an event handler by event type....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_global_plugin_manager
- **File:** core/patterns/plugin.py
- **Line:** 638
- **Return Type:** PluginManager
- **Docstring:** Get the global plugin manager instance....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_plugin_health
- **File:** core/patterns/plugin.py
- **Line:** 525
- **Parameters:** self, plugin_name
- **Return Type:** Optional[Dict[str, Any]]
- **Docstring:** Get health status of a plugin....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_plugin_info
- **File:** core/patterns/plugin.py
- **Line:** 490
- **Parameters:** self, plugin_name
- **Return Type:** Optional[PluginInfo]
- **Docstring:** Get information about a specific plugin....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_plugin_metrics
- **File:** core/patterns/plugin.py
- **Line:** 540
- **Parameters:** self, plugin_name
- **Return Type:** Optional[Dict[str, Any]]
- **Docstring:** Get metrics from a plugin....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_plugin_registry
- **File:** core/patterns/plugin.py
- **Line:** 503
- **Parameters:** self
- **Return Type:** PluginRegistry
- **Docstring:** Get the plugin registry....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_plugin_resources
- **File:** core/patterns/plugin.py
- **Line:** 224
- **Parameters:** self, plugin_name
- **Return Type:** Dict[str, List[str]]
- **Docstring:** Get all resources registered by a specific plugin....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_relationship_kind
- **File:** core/patterns/plugin.py
- **Line:** 174
- **Parameters:** self, kind_name
- **Return Type:** Optional[RelationshipKind]
- **Docstring:** Get a relationship kind by name....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.get_validator
- **File:** core/patterns/plugin.py
- **Line:** 182
- **Parameters:** self, name
- **Return Type:** Optional[Callable]
- **Docstring:** Get a validator by name....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.list_plugins
- **File:** core/patterns/plugin.py
- **Line:** 494
- **Parameters:** self, status
- **Return Type:** List[PluginInfo]
- **Docstring:** List all plugins, optionally filtered by status....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.load_plugin
- **File:** core/patterns/plugin.py
- **Line:** 287
- **Parameters:** self, plugin_name, plugin_path
- **Return Type:** bool
- **Docstring:** 
        Load a plugin from file or import path.
        
        Args:
            plugin_name: Nam...
- **Issues:**
  - Unused method - not called anywhere in codebase

### patterns.plugin.set_framework_context
- **File:** core/patterns/plugin.py
- **Line:** 272
- **Parameters:** self, context
- **Return Type:** None
- **Docstring:** Set the framework context passed to plugins....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.plugin.unload_plugin
- **File:** core/patterns/plugin.py
- **Line:** 455
- **Parameters:** self, plugin_name
- **Return Type:** bool
- **Docstring:** 
        Unload a plugin completely.
        
        Args:
            plugin_name: Name of the plu...
- **Issues:**
  - Unused method - not called anywhere in codebase

### patterns.strategy.clear_strategies
- **File:** core/patterns/strategy.py
- **Line:** 473
- **Parameters:** self, category
- **Return Type:** None
- **Docstring:** Clear all strategies, optionally filtered by category....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.strategy.compare_centralities
- **File:** core/patterns/strategy.py
- **Line:** 539
- **Parameters:** self, graph, node_id, strategies
- **Return Type:** Dict[str, float]
- **Docstring:** Compare centrality values using different strategies....
- **Issues:**
  - Unused method - not called anywhere in codebase

### patterns.strategy.execute_strategy
- **File:** core/patterns/strategy.py
- **Line:** 439
- **Parameters:** self, category, strategy_name
- **Return Type:** Any
- **Docstring:** Execute a strategy with the given arguments....
- **Issues:**
  - Unused method - not called anywhere in codebase

### patterns.strategy.get_categories
- **File:** core/patterns/strategy.py
- **Line:** 491
- **Parameters:** self
- **Return Type:** List[str]
- **Docstring:** Get all strategy categories....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.strategy.get_default_strategy
- **File:** core/patterns/strategy.py
- **Line:** 423
- **Parameters:** self, category
- **Return Type:** Optional[str]
- **Docstring:** Get the default strategy name for a category....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.strategy.get_strategy_metadata
- **File:** core/patterns/strategy.py
- **Line:** 434
- **Parameters:** self, category, strategy_name
- **Return Type:** Optional[StrategyMetadata]
- **Docstring:** Get metadata for a specific strategy....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.strategy.remove_strategy
- **File:** core/patterns/strategy.py
- **Line:** 448
- **Parameters:** self, category, strategy_name
- **Return Type:** bool
- **Docstring:** Remove a strategy from the manager....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### performance_metrics.collect_system_metrics
- **File:** core/performance_metrics.py
- **Line:** 264
- **Issues:**
  - Unused method - not called anywhere in codebase

### performance_metrics.get_custom_metric
- **File:** core/performance_metrics.py
- **Line:** 223
- **Parameters:** self, metric_name, limit
- **Return Type:** List[Dict[str, Any]]
- **Docstring:** Get custom metric values....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### performance_metrics.get_performance_summary
- **File:** core/performance_metrics.py
- **Line:** 313
- **Return Type:** Dict[str, Any]
- **Docstring:** Get a summary of all performance metrics....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### performance_metrics.record_histogram
- **File:** core/performance_metrics.py
- **Line:** 200
- **Parameters:** self, histogram_name, value, metadata
- **Docstring:** Record a value in a histogram metric....
- **Issues:**
  - Stub method - matches pattern: ^\s*return\s*$
  - Unused method - not called anywhere in codebase

### performance_metrics.set_enabled
- **File:** core/performance_metrics.py
- **Line:** 158
- **Parameters:** self, enabled
- **Docstring:** Enable or disable metrics collection....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### performance_metrics.wrapper
- **File:** core/performance_metrics.py
- **Line:** 330
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase

### security_validators.clear_validation_rate_limit_storage
- **File:** core/security_validators.py
- **Line:** 600
- **Return Type:** None
- **Docstring:** 
    Clear all rate limiting storage.
    Useful for testing environments.
    ...
- **Issues:**
  - Unused method - not called anywhere in codebase

### security_validators.disable_validation_rate_limiting
- **File:** core/security_validators.py
- **Line:** 583
- **Return Type:** None
- **Docstring:** 
    Disable rate limiting for validation operations.
    Useful for testing environments.
    ...
- **Issues:**
  - Unused method - not called anywhere in codebase

### security_validators.enable_validation_rate_limiting
- **File:** core/security_validators.py
- **Line:** 592
- **Return Type:** None
- **Docstring:** 
    Enable rate limiting for validation operations.
    ...
- **Issues:**
  - Unused method - not called anywhere in codebase

### security_validators.get_validation_rate_limit_status
- **File:** core/security_validators.py
- **Line:** 552
- **Parameters:** caller_id
- **Return Type:** Dict[str, Any]
- **Docstring:** 
    Get current rate limit status for a caller.
    
    Args:
        caller_id: Identifier for th...
- **Issues:**
  - Unused method - not called anywhere in codebase

### security_validators.rate_limit_validation
- **File:** core/security_validators.py
- **Line:** 84
- **Parameters:** func
- **Return Type:** Callable
- **Docstring:** 
    Decorator to apply rate limiting to validation functions.
    
    Args:
        func: Function...
- **Issues:**
  - Unused method - not called anywhere in codebase

### security_validators.set_validation_caller_context
- **File:** core/security_validators.py
- **Line:** 541
- **Parameters:** caller_id
- **Return Type:** None
- **Docstring:** 
    Set caller context for rate limiting validation operations.
    
    Args:
        caller_id: I...
- **Issues:**
  - Unused method - not called anywhere in codebase

### security_validators.validate_url
- **File:** core/security_validators.py
- **Line:** 368
- **Parameters:** url
- **Return Type:** bool
- **Docstring:** 
    Validate that a URL is safe and properly formatted.

    Args:
        url: URL to validate

  ...
- **Issues:**
  - Unused method - not called anywhere in codebase

### security_validators.wrapper
- **File:** core/security_validators.py
- **Line:** 95
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_enums.ceremonial_tendency
- **File:** core/sfm_enums.py
- **Line:** 2033
- **Parameters:** self
- **Return Type:** float
- **Docstring:** 
        Returns a value from 0.0-1.0 indicating ceremonial vs instrumental nature.

        Based o...
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_enums.get_extended_categories
- **File:** core/sfm_enums.py
- **Line:** 330
- **Parameters:** cls
- **Return Type:** Set['ValueCategory']
- **Docstring:** Return extended categories beyond core framework....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_enums.validate_business_rule_constraints
- **File:** core/sfm_enums.py
- **Line:** 3132
- **Parameters:** relationship_kind, source_type, target_type, domain_context
- **Return Type:** None
- **Docstring:** Validate SFM-specific business rules and domain constraints.
        
        This method implements...
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_enums.validate_cross_entity_consistency
- **File:** core/sfm_enums.py
- **Line:** 3044
- **Parameters:** entity_1_type, entity_2_type, relationship_kind, context
- **Return Type:** None
- **Docstring:** Validate consistency across multiple entities in SFM framework.
        
        This method impleme...
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase

### sfm_enums.validate_cross_enum_dependency
- **File:** core/sfm_enums.py
- **Line:** 2689
- **Parameters:** primary_enum, dependent_enum, relationship_type
- **Return Type:** None
- **Docstring:** Validate cross-enum dependencies and relationships.

        Args:
            primary_enum: The pri...
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_enums.validate_enum_operation
- **File:** core/sfm_enums.py
- **Line:** 3234
- **Parameters:** operation_name
- **Return Type:** Callable[[Callable[..., Any]], Callable[..., Any]]
- **Docstring:** Decorator to validate enum operations and provide better error messages.

    Args:
        operatio...
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_enums.validate_institution_layer_context
- **File:** core/sfm_enums.py
- **Line:** 2579
- **Parameters:** layer, institution_type
- **Return Type:** None
- **Docstring:** Validate that institution layer makes sense for the institution type.

        Args:
            lay...
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_enums.validate_legitimacy_source_context
- **File:** core/sfm_enums.py
- **Line:** 2816
- **Parameters:** source, institutional_context
- **Return Type:** None
- **Docstring:** Validate LegitimacySource appropriateness for institutional context.

        Args:
            sour...
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase

### sfm_enums.validate_required_enum_context
- **File:** core/sfm_enums.py
- **Line:** 2732
- **Parameters:** enum_value, context, is_required
- **Return Type:** None
- **Docstring:** Validate whether an enum is required or optional in given context.

        Args:
            enum_v...
- **Issues:**
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase

### sfm_enums.validate_technology_readiness_level
- **File:** core/sfm_enums.py
- **Line:** 2777
- **Parameters:** level, context
- **Return Type:** None
- **Docstring:** Validate TechnologyReadinessLevel usage in context.

        Args:
            level: The TRL level ...
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_enums.wrapper
- **File:** core/sfm_enums.py
- **Line:** 3244
- **Return Type:** Any
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_persistence._add_actor_kwargs
- **File:** core/sfm_persistence.py
- **Line:** 242
- **Parameters:** data, node_kwargs
- **Return Type:** None
- **Docstring:** Add Actor-specific constructor arguments....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence._add_flow_kwargs
- **File:** core/sfm_persistence.py
- **Line:** 273
- **Parameters:** data, node_kwargs
- **Return Type:** None
- **Docstring:** Add Flow-specific constructor arguments....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence._add_institution_kwargs
- **File:** core/sfm_persistence.py
- **Line:** 250
- **Parameters:** data, node_kwargs
- **Return Type:** None
- **Docstring:** Add Institution-specific constructor arguments....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence._add_policy_kwargs
- **File:** core/sfm_persistence.py
- **Line:** 265
- **Parameters:** data, node_kwargs
- **Return Type:** None
- **Docstring:** Add Policy-specific constructor arguments....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence._add_resource_kwargs
- **File:** core/sfm_persistence.py
- **Line:** 256
- **Parameters:** data, node_kwargs
- **Return Type:** None
- **Docstring:** Add Resource-specific constructor arguments....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence._handle_actor
- **File:** core/sfm_persistence.py
- **Line:** 157
- **Parameters:** actor, result
- **Return Type:** None
- **Docstring:** Handle Actor-specific fields....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence._handle_flow
- **File:** core/sfm_persistence.py
- **Line:** 193
- **Parameters:** flow, result
- **Return Type:** None
- **Docstring:** Handle Flow-specific fields....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence._handle_institution
- **File:** core/sfm_persistence.py
- **Line:** 167
- **Parameters:** institution, result
- **Return Type:** None
- **Docstring:** Handle Institution-specific fields....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence._handle_policy
- **File:** core/sfm_persistence.py
- **Line:** 184
- **Parameters:** policy, result
- **Return Type:** None
- **Docstring:** Handle Policy-specific fields....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence._handle_resource
- **File:** core/sfm_persistence.py
- **Line:** 176
- **Parameters:** resource, result
- **Return Type:** None
- **Docstring:** Handle Resource-specific fields....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence.check_version_consistency
- **File:** core/sfm_persistence.py
- **Line:** 1391
- **Parameters:** self, graph_id
- **Return Type:** Dict[str, Any]
- **Docstring:** Check version consistency for a graph across all storage locations....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence.cleanup_old_backups
- **File:** core/sfm_persistence.py
- **Line:** 1524
- **Parameters:** self, max_age_days
- **Return Type:** Dict[str, Any]
- **Docstring:** Clean up old backup files older than specified age....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence.cleanup_old_versions
- **File:** core/sfm_persistence.py
- **Line:** 1457
- **Parameters:** self, graph_id, keep_versions
- **Return Type:** Dict[str, Any]
- **Docstring:** Clean up old versions of a graph, keeping the specified number of recent versions....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence.create_backup
- **File:** core/sfm_persistence.py
- **Line:** 1307
- **Parameters:** self, graph_id, backup_name
- **Return Type:** str
- **Docstring:** Create a backup of a specific graph....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence.delete_graph
- **File:** core/sfm_persistence.py
- **Line:** 754
- **Parameters:** self, graph_id, include_versions
- **Return Type:** bool
- **Docstring:** 
        Delete a graph and optionally its versions.

        Args:
            graph_id: Unique ide...
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_persistence.get_graph_metadata
- **File:** core/sfm_persistence.py
- **Line:** 834
- **Parameters:** self, graph_id
- **Return Type:** Optional[GraphMetadata]
- **Docstring:** Get metadata for a specific graph....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence.get_storage_statistics
- **File:** core/sfm_persistence.py
- **Line:** 838
- **Parameters:** self
- **Return Type:** Dict[str, Any]
- **Docstring:** Get storage statistics....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence.json_serializer
- **File:** core/sfm_persistence.py
- **Line:** 451
- **Parameters:** obj
- **Return Type:** str
- **Docstring:** Custom JSON serializer for complex types....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence.list_sfm_graphs
- **File:** core/sfm_persistence.py
- **Line:** 1582
- **Parameters:** storage_path
- **Return Type:** List[str]
- **Docstring:** Quick list function for SFM graphs....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence.load_sfm_graph
- **File:** core/sfm_persistence.py
- **Line:** 1576
- **Parameters:** graph_id, storage_path
- **Return Type:** Optional[SFMGraph]
- **Docstring:** Quick load function for SFM graphs....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence.restore_from_backup
- **File:** core/sfm_persistence.py
- **Line:** 1339
- **Parameters:** self, backup_path, new_graph_id
- **Return Type:** str
- **Docstring:** Restore a graph from backup....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence.save_sfm_graph
- **File:** core/sfm_persistence.py
- **Line:** 1569
- **Parameters:** graph_id, graph, storage_path
- **Return Type:** GraphMetadata
- **Docstring:** Quick save function for SFM graphs....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_query.analyze_flow_patterns
- **File:** core/sfm_query.py
- **Line:** 1001
- **Parameters:** self, flow_type, time_window
- **Return Type:** Dict[str, Any]
- **Docstring:** Analyze patterns in resource or value flows....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_query.analyze_temporal_changes
- **File:** core/sfm_query.py
- **Line:** 774
- **Parameters:** self, time_slice_graphs
- **Return Type:** Dict[str, Any]
- **Docstring:** Analyze changes across multiple time slices of the graph....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_query.assess_network_vulnerabilities
- **File:** core/sfm_query.py
- **Line:** 839
- **Parameters:** self
- **Return Type:** Dict[str, Any]
- **Docstring:** Comprehensive vulnerability assessment of the network....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_query.calculate_flow_efficiency
- **File:** core/sfm_query.py
- **Line:** 506
- **Parameters:** self, source_id, target_id
- **Return Type:** float
- **Docstring:** Calculate efficiency of flows between nodes....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_query.compare_policy_scenarios
- **File:** core/sfm_query.py
- **Line:** 592
- **Parameters:** self, scenario_graphs
- **Return Type:** Dict[str, Any]
- **Docstring:** Compare multiple policy scenarios....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_query.comprehensive_node_analysis
- **File:** core/sfm_query.py
- **Line:** 718
- **Parameters:** self, node_id
- **Return Type:** NodeMetrics
- **Docstring:** Comprehensive analysis of a single node....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_query.create_query_engine
- **File:** core/sfm_query.py
- **Line:** 1226
- **Parameters:** graph, backend
- **Return Type:** SFMQueryEngine
- **Docstring:** Create a query engine for the specified backend....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_query.detect_structural_changes
- **File:** core/sfm_query.py
- **Line:** 809
- **Parameters:** self, reference_graph, comparison_graph
- **Return Type:** Dict[str, Any]
- **Docstring:** Detect structural changes between two graph states....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_query.find_cycles
- **File:** core/sfm_query.py
- **Line:** 431
- **Parameters:** self, max_length
- **Return Type:** List[List[uuid.UUID]]
- **Docstring:** Find cycles in the graph (feedback loops)....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_query.get_relationship_strength
- **File:** core/sfm_query.py
- **Line:** 414
- **Parameters:** self, source_id, target_id
- **Return Type:** float
- **Docstring:** Calculate aggregate relationship strength between nodes....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_query.identify_communities
- **File:** core/sfm_query.py
- **Line:** 652
- **Parameters:** self, algorithm
- **Return Type:** Dict[int, List[uuid.UUID]]
- **Docstring:** Identify communities/clusters in the network....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_query.identify_flow_inefficiencies
- **File:** core/sfm_query.py
- **Line:** 1026
- **Parameters:** self
- **Return Type:** Dict[str, Any]
- **Docstring:** Identify inefficiencies in flow patterns....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_query.identify_policy_targets
- **File:** core/sfm_query.py
- **Line:** 578
- **Parameters:** self, policy_id
- **Return Type:** List[uuid.UUID]
- **Docstring:** Identify nodes directly and indirectly affected by a policy....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_query.simulate_node_failure_impact
- **File:** core/sfm_query.py
- **Line:** 927
- **Parameters:** self, node_ids, failure_mode
- **Return Type:** Dict[str, Any]
- **Docstring:** Simulate the impact of node failures on network connectivity....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_query.system_vulnerability_analysis
- **File:** core/sfm_query.py
- **Line:** 755
- **Parameters:** self
- **Return Type:** Dict[str, Any]
- **Docstring:** Analyze system-wide vulnerabilities and resilience....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_query.trace_resource_flows
- **File:** core/sfm_query.py
- **Line:** 443
- **Parameters:** self, resource_type, source_actors
- **Return Type:** FlowAnalysis
- **Docstring:** Trace flows of specific resource types through the network....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_service.bulk_create_actors
- **File:** core/sfm_service.py
- **Line:** 1422
- **Parameters:** self, requests
- **Return Type:** List[NodeResponse]
- **Docstring:** Create multiple actors in batch with transaction support....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_service.clear_all_data
- **File:** core/sfm_service.py
- **Line:** 1396
- **Parameters:** self
- **Return Type:** Dict[str, Any]
- **Docstring:** Clear all data from the repository....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.connect
- **File:** core/sfm_service.py
- **Line:** 913
- **Parameters:** self, source_id, target_id, kind, weight
- **Return Type:** RelationshipResponse
- **Docstring:** Convenience method for creating relationships (backward compatibility)....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_service.create_institution
- **File:** core/sfm_service.py
- **Line:** 625
- **Parameters:** self, request
- **Return Type:** NodeResponse
- **Docstring:** Create a new Institution entity with security validation....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_service.create_policy
- **File:** core/sfm_service.py
- **Line:** 684
- **Parameters:** self, request
- **Return Type:** NodeResponse
- **Docstring:** Create a new Policy entity with security validation....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_service.create_resource
- **File:** core/sfm_service.py
- **Line:** 744
- **Parameters:** self, request
- **Return Type:** NodeResponse
- **Docstring:** Create a new Resource entity with security validation....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_service.find_shortest_path_legacy
- **File:** core/sfm_service.py
- **Line:** 1371
- **Parameters:** self, source_id, target_id
- **Return Type:** list
- **Docstring:** 
        Find the shortest path between two nodes by their IDs.
        Returns a list of node IDs r...
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_service.get_actor
- **File:** core/sfm_service.py
- **Line:** 957
- **Parameters:** self, actor_id
- **Return Type:** Optional[Actor]
- **Docstring:** Retrieve an actor by ID....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.get_command_history
- **File:** core/sfm_service.py
- **Line:** 1614
- **Parameters:** self
- **Return Type:** List[Dict[str, Any]]
- **Docstring:** Get the command history for undo/redo operations....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.get_command_statistics
- **File:** core/sfm_service.py
- **Line:** 1639
- **Parameters:** self
- **Return Type:** Dict[str, Any]
- **Docstring:** Get statistics about command execution....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.get_comprehensive_status
- **File:** core/sfm_service.py
- **Line:** 1580
- **Parameters:** self
- **Return Type:** Dict[str, Any]
- **Docstring:** Get comprehensive service status including all metrics....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.get_flow
- **File:** core/sfm_service.py
- **Line:** 977
- **Parameters:** self, flow_id
- **Return Type:** Optional[Flow]
- **Docstring:** Retrieve a flow by ID....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.get_institution
- **File:** core/sfm_service.py
- **Line:** 965
- **Parameters:** self, institution_id
- **Return Type:** Optional[Institution]
- **Docstring:** Retrieve an institution by ID....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.get_policy
- **File:** core/sfm_service.py
- **Line:** 961
- **Parameters:** self, policy_id
- **Return Type:** Optional[Policy]
- **Docstring:** Retrieve a policy by ID....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.get_process
- **File:** core/sfm_service.py
- **Line:** 973
- **Parameters:** self, process_id
- **Return Type:** Optional[Process]
- **Docstring:** Retrieve a process by ID....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.get_relationship
- **File:** core/sfm_service.py
- **Line:** 981
- **Parameters:** self, rel_id
- **Return Type:** Optional[RelationshipResponse]
- **Docstring:** Get a relationship by ID....
- **Issues:**
  - Stub method - matches pattern: return\s+None\s*$
  - Unused method - not called anywhere in codebase

### sfm_service.get_resource
- **File:** core/sfm_service.py
- **Line:** 969
- **Parameters:** self, resource_id
- **Return Type:** Optional[Resource]
- **Docstring:** Retrieve a resource by ID....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.get_sfm_service
- **File:** core/sfm_service.py
- **Line:** 1901
- **Return Type:** SFMService
- **Docstring:** Get singleton SFM service instance (for dependency injection)....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.list_relationships
- **File:** core/sfm_service.py
- **Line:** 1101
- **Parameters:** self, kind, limit, offset
- **Return Type:** List[RelationshipResponse]
- **Docstring:** List relationships with optional filtering and pagination....
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_service.query_engine
- **File:** core/sfm_service.py
- **Line:** 416
- **Parameters:** self
- **Return Type:** SFMQueryEngine
- **Docstring:** Get the query engine, creating it if necessary....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.quick_analysis
- **File:** core/sfm_service.py
- **Line:** 1918
- **Parameters:** service
- **Return Type:** Dict[str, Any]
- **Docstring:** 
    Perform a quick analysis of an SFM graph.

    Args:
        service: SFM service instance

   ...
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_service.redo_last_operation
- **File:** core/sfm_service.py
- **Line:** 1610
- **Parameters:** self
- **Return Type:** bool
- **Docstring:** Redo the last undone operation using the command pattern....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.repair_orphaned_relationships
- **File:** core/sfm_service.py
- **Line:** 1837
- **Parameters:** self, auto_repair
- **Return Type:** Dict[str, Any]
- **Docstring:** 
        Repair orphaned relationships by removing them.
        
        Args:
            auto_rep...
- **Issues:**
  - Unused method - not called anywhere in codebase

### sfm_service.reset_sfm_service
- **File:** core/sfm_service.py
- **Line:** 1909
- **Docstring:** Reset the singleton service instance (useful for testing)....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.undo_last_operation
- **File:** core/sfm_service.py
- **Line:** 1606
- **Parameters:** self
- **Return Type:** bool
- **Docstring:** Undo the last operation using the command pattern....
- **Issues:**
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service.validate_graph_integrity
- **File:** core/sfm_service.py
- **Line:** 1645
- **Parameters:** self
- **Return Type:** List[Dict[str, Any]]
- **Docstring:** 
        Validate the integrity of the entire graph and return violations.
        
        Returns:...
- **Issues:**
  - Unused method - not called anywhere in codebase


## Potentially Incomplete Methods
------------------------------
### patterns.dependency_injection.example_configuration
- **File:** core/patterns/dependency_injection.py
- **Line:** 689
- **Docstring:** Example of how to configure the DI container....
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.dependency_injection.logging_interceptor
- **File:** core/patterns/dependency_injection.py
- **Line:** 706
- **Parameters:** service_type, instance
- **Return Type:** Any
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Unused method - not called anywhere in codebase

### patterns.observer._notify_node_added
- **File:** core/patterns/observer.py
- **Line:** 82
- **Parameters:** self, node
- **Return Type:** None
- **Docstring:** Notify all observers that a node was added....
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis

### patterns.observer._notify_node_removed
- **File:** core/patterns/observer.py
- **Line:** 92
- **Parameters:** self, node_id
- **Return Type:** None
- **Docstring:** Notify all observers that a node was removed....
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer._notify_node_updated
- **File:** core/patterns/observer.py
- **Line:** 101
- **Parameters:** self, node, previous_state
- **Return Type:** None
- **Docstring:** Notify all observers that a node was updated....
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer._notify_relationship_added
- **File:** core/patterns/observer.py
- **Line:** 114
- **Parameters:** self, relationship
- **Return Type:** None
- **Docstring:** Notify all observers that a relationship was added....
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis

### patterns.observer._notify_relationship_removed
- **File:** core/patterns/observer.py
- **Line:** 128
- **Parameters:** self, relationship_id
- **Return Type:** None
- **Docstring:** Notify all observers that a relationship was removed....
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### patterns.observer._notify_relationship_updated
- **File:** core/patterns/observer.py
- **Line:** 137
- **Parameters:** self, relationship, previous_state
- **Return Type:** None
- **Docstring:** Notify all observers that a relationship was updated....
- **Issues:**
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase


## Module-by-Module Breakdown
------------------------------
### exceptions
- **create_database_error** [UNUSED] (Line 516)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **create_node_creation_error** [UNUSED] (Line 502)
  - Unused method - not called anywhere in codebase
- **create_not_found_error** [UNUSED] (Line 492)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **create_query_error** [UNUSED] (Line 511)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **create_validation_error** [UNUSED] (Line 497)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### monitoring_middleware
- **create_monitoring_middleware** [UNUSED] (Line 339)
  - Unused method - not called anywhere in codebase

### health_checker
- **check_all** [UNUSED] (Line 350)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **check_liveness** [UNUSED] (Line 358)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **check_readiness** [UNUSED] (Line 362)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **check_startup** [UNUSED] (Line 354)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_health_checker** [UNUSED] (Line 427)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **remove_check** [UNUSED] (Line 342)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_service
- **_check_circular_dependencies** [STUB] (Line 1796)
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis
- **bulk_create_actors** [UNUSED] (Line 1422)
  - Unused method - not called anywhere in codebase
- **clear_all_data** [UNUSED] (Line 1396)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **connect** [UNUSED] (Line 913)
  - Unused method - not called anywhere in codebase
- **create_institution** [UNUSED] (Line 625)
  - Unused method - not called anywhere in codebase
- **create_policy** [UNUSED] (Line 684)
  - Unused method - not called anywhere in codebase
- **create_resource** [UNUSED] (Line 744)
  - Unused method - not called anywhere in codebase
- **find_shortest_path** [STUB] (Line 1309)
  - Stub method - matches pattern: return\s+None\s*$
- **find_shortest_path_legacy** [UNUSED] (Line 1371)
  - Unused method - not called anywhere in codebase
- **get_actor** [UNUSED] (Line 957)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_command_history** [UNUSED] (Line 1614)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_command_statistics** [UNUSED] (Line 1639)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_comprehensive_status** [UNUSED] (Line 1580)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_entity** [STUB] (Line 934)
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
- **get_flow** [UNUSED] (Line 977)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_institution** [UNUSED] (Line 965)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_policy** [UNUSED] (Line 961)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_process** [UNUSED] (Line 973)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_relationship** [STUB, UNUSED] (Line 981)
  - Stub method - matches pattern: return\s+None\s*$
  - Unused method - not called anywhere in codebase
- **get_resource** [UNUSED] (Line 969)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_sfm_service** [UNUSED] (Line 1901)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **list_relationships** [UNUSED] (Line 1101)
  - Unused method - not called anywhere in codebase
- **query_engine** [UNUSED] (Line 416)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **quick_analysis** [UNUSED] (Line 1918)
  - Unused method - not called anywhere in codebase
- **redo_last_operation** [UNUSED] (Line 1610)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **repair_orphaned_relationships** [UNUSED] (Line 1837)
  - Unused method - not called anywhere in codebase
- **reset_sfm_service** [UNUSED] (Line 1909)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **undo_last_operation** [UNUSED] (Line 1606)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **validate_graph_integrity** [UNUSED] (Line 1645)
  - Unused method - not called anywhere in codebase

### cache_monitoring
- **_init_prometheus_metrics** [STUB] (Line 62)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **generate_cache_report** [UNUSED] (Line 239)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_prometheus_metrics** [UNUSED] (Line 193)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **record_eviction** [UNUSED] (Line 130)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **update_cache_size** [UNUSED] (Line 154)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **update_hit_rate** [UNUSED] (Line 146)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### logging_config
- **configure_logging** [UNUSED] (Line 239)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **critical** [UNUSED] (Line 83)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **monitor_performance** [UNUSED] (Line 200)
  - Unused method - not called anywhere in codebase
- **wrapper** [UNUSED] (Line 209)
  - Unused method - not called anywhere in codebase

### cache_config
- **get_layer_config** [UNUSED] (Line 78)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_redis_config** [UNUSED] (Line 87)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **update_config** [UNUSED] (Line 97)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### sfm_persistence
- **_add_actor_kwargs** [UNUSED] (Line 242)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_add_flow_kwargs** [UNUSED] (Line 273)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_add_institution_kwargs** [UNUSED] (Line 250)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_add_policy_kwargs** [UNUSED] (Line 265)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_add_resource_kwargs** [UNUSED] (Line 256)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_count_backups** [STUB] (Line 908)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **_get_metadata** [STUB] (Line 977)
  - Stub method - matches pattern: return\s+None\s*$
- **_handle_actor** [UNUSED] (Line 157)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_handle_flow** [UNUSED] (Line 193)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_handle_institution** [UNUSED] (Line 167)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_handle_policy** [UNUSED] (Line 184)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_handle_resource** [UNUSED] (Line 176)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_load_metadata_data** [STUB] (Line 1109)
  - Stub method - matches pattern: return\s+None\s*$
- **check_version_consistency** [UNUSED] (Line 1391)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **cleanup_old_backups** [UNUSED] (Line 1524)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **cleanup_old_versions** [UNUSED] (Line 1457)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **create_backup** [UNUSED] (Line 1307)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **delete_graph** [UNUSED] (Line 754)
  - Unused method - not called anywhere in codebase
- **get_graph_metadata** [UNUSED] (Line 834)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_storage_statistics** [UNUSED] (Line 838)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **json_serializer** [UNUSED] (Line 451)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **list_sfm_graphs** [UNUSED] (Line 1582)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **load_graph** [STUB] (Line 687)
  - Stub method - matches pattern: return\s+None\s*$
- **load_sfm_graph** [UNUSED] (Line 1576)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **restore_from_backup** [UNUSED] (Line 1339)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **save_sfm_graph** [UNUSED] (Line 1569)
  - Unused method - not called anywhere in codebase

### advanced_caching
- **_warming_loop** [UNUSED] (Line 634)
  - Unused method - not called anywhere in codebase
- **cached** [UNUSED] (Line 721)
  - Unused method - not called anywhere in codebase
- **cached_operation** [UNUSED] (Line 819)
  - Unused method - not called anywhere in codebase
- **create_cache_manager** [UNUSED] (Line 795)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **from_dict** [UNUSED] (Line 790)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get** [STUB] (Line 423)
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
- **record_eviction** [UNUSED] (Line 685)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **register_key_generator** [UNUSED] (Line 496)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **register_warming_strategy** [UNUSED] (Line 570)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **schedule_warming** [UNUSED] (Line 632)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **update_hit_rate** [UNUSED] (Line 690)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **update_size** [UNUSED] (Line 695)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **warm_common_queries** [STUB, UNUSED] (Line 615)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **warm_frequently_accessed_nodes** [STUB, UNUSED] (Line 596)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **wrapper** [UNUSED] (Line 824)
  - Unused method - not called anywhere in codebase

### performance_metrics
- **collect_system_metrics** [UNUSED] (Line 264)
  - Unused method - not called anywhere in codebase
- **decorator** [STUB] (Line 326)
  - Stub method - matches pattern: ^\s*pass\s*$
- **get_custom_metric** [UNUSED] (Line 223)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_performance_summary** [UNUSED] (Line 313)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **increment_counter** [STUB] (Line 176)
  - Stub method - matches pattern: ^\s*return\s*$
- **record_histogram** [STUB, UNUSED] (Line 200)
  - Stub method - matches pattern: ^\s*return\s*$
  - Unused method - not called anywhere in codebase
- **record_operation** [STUB] (Line 162)
  - Stub method - matches pattern: ^\s*return\s*$
- **set_enabled** [UNUSED] (Line 158)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **set_gauge** [STUB] (Line 189)
  - Stub method - matches pattern: ^\s*return\s*$
- **timed_operation** [STUB] (Line 318)
  - Stub method - matches pattern: ^\s*pass\s*$
- **wrapper** [STUB, UNUSED] (Line 330)
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase

### base_nodes
No problematic methods found.

### sfm_query
- **analyze_flow_patterns** [UNUSED] (Line 1001)
  - Unused method - not called anywhere in codebase
- **analyze_temporal_changes** [UNUSED] (Line 774)
  - Unused method - not called anywhere in codebase
- **assess_network_vulnerabilities** [UNUSED] (Line 839)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **calculate_flow_efficiency** [UNUSED] (Line 506)
  - Unused method - not called anywhere in codebase
- **compare_policy_scenarios** [UNUSED] (Line 592)
  - Unused method - not called anywhere in codebase
- **comprehensive_node_analysis** [UNUSED] (Line 718)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **create_query_engine** [UNUSED] (Line 1226)
  - Unused method - not called anywhere in codebase
- **detect_structural_changes** [UNUSED] (Line 809)
  - Unused method - not called anywhere in codebase
- **find_cycles** [UNUSED] (Line 431)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **find_shortest_path** [STUB] (Line 386)
  - Stub method - matches pattern: return\s+None\s*$
- **get_relationship_strength** [UNUSED] (Line 414)
  - Unused method - not called anywhere in codebase
- **identify_communities** [UNUSED] (Line 652)
  - Unused method - not called anywhere in codebase
- **identify_flow_inefficiencies** [UNUSED] (Line 1026)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **identify_policy_targets** [UNUSED] (Line 578)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **simulate_node_failure_impact** [UNUSED] (Line 927)
  - Unused method - not called anywhere in codebase
- **system_vulnerability_analysis** [UNUSED] (Line 755)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **trace_resource_flows** [UNUSED] (Line 443)
  - Unused method - not called anywhere in codebase

### audit_logger
- **audit_operation** [STUB] (Line 218)
  - Stub method - matches pattern: ^\s*pass\s*$
- **decorator** [STUB] (Line 231)
  - Stub method - matches pattern: ^\s*pass\s*$
- **wrapper** [STUB, UNUSED] (Line 233)
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase

### metrics
- **add_custom_collector** [UNUSED] (Line 356)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **collect_custom_metrics** [UNUSED] (Line 361)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **configure_metrics** [UNUSED] (Line 446)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_performance_summary** [UNUSED] (Line 377)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_prometheus_metrics** [UNUSED] (Line 371)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **monitor_performance** [UNUSED] (Line 382)
  - Unused method - not called anywhere in codebase
- **record_cache_hit** [STUB] (Line 188)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **record_cache_miss** [STUB] (Line 195)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **record_cache_operation** [UNUSED] (Line 323)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **record_entity_creation** [STUB] (Line 166)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **record_operation_duration** [STUB] (Line 209)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **record_query_execution** [STUB] (Line 180)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **record_relationship_creation** [STUB] (Line 173)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **record_system_error** [STUB] (Line 202)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **set_system_info** [STUB, UNUSED] (Line 233)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **update_active_connections** [STUB] (Line 219)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **update_memory_usage** [STUB] (Line 226)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **update_system_metrics** [UNUSED] (Line 344)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **wrapper** [UNUSED] (Line 392)
  - Unused method - not called anywhere in codebase

### graph
- **clear_all_caches** [UNUSED] (Line 529)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **disable_lazy_loading** [UNUSED] (Line 401)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **enable_advanced_caching** [UNUSED] (Line 523)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **enable_lazy_loading** [UNUSED] (Line 392)
  - Unused method - not called anywhere in codebase
- **force_memory_cleanup** [UNUSED] (Line 493)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_cache_stats** [UNUSED] (Line 536)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_memory_stats** [UNUSED] (Line 504)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_memory_usage** [UNUSED] (Line 487)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_node_size_estimate** [UNUSED] (Line 460)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **set_eviction_strategy** [UNUSED] (Line 499)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **set_memory_limit** [UNUSED] (Line 481)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### security_validators
- **clear_validation_rate_limit_storage** [UNUSED] (Line 600)
  - Unused method - not called anywhere in codebase
- **disable_validation_rate_limiting** [UNUSED] (Line 583)
  - Unused method - not called anywhere in codebase
- **enable_validation_rate_limiting** [UNUSED] (Line 592)
  - Unused method - not called anywhere in codebase
- **get_validation_rate_limit_status** [UNUSED] (Line 552)
  - Unused method - not called anywhere in codebase
- **rate_limit_validation** [UNUSED] (Line 84)
  - Unused method - not called anywhere in codebase
- **set_validation_caller_context** [UNUSED] (Line 541)
  - Unused method - not called anywhere in codebase
- **validate_node_description** [STUB] (Line 461)
  - Stub method - matches pattern: return\s+None\s*$
- **validate_url** [UNUSED] (Line 368)
  - Unused method - not called anywhere in codebase
- **wrapper** [UNUSED] (Line 95)
  - Unused method - not called anywhere in codebase

### specialized_nodes
No problematic methods found.

### memory_management
- **current_strategy** [UNUSED] (Line 230)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_access_count** [UNUSED] (Line 128)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_all_node_ids** [STUB] (Line 142)
  - Stub method - matches pattern: ^\s*\.\.\.\s*$
  - Minimal implementation - only pass/return/ellipsis
- **get_node_size_estimate** [STUB, UNUSED] (Line 150)
  - Stub method - matches pattern: ^\s*\.\.\.\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **remove_node_from_memory** [STUB] (Line 146)
  - Stub method - matches pattern: ^\s*\.\.\.\s*$
  - Minimal implementation - only pass/return/ellipsis

### sfm_enums
- **ceremonial_tendency** [UNUSED] (Line 2033)
  - Unused method - not called anywhere in codebase
- **get_extended_categories** [UNUSED] (Line 330)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **validate_business_rule_constraints** [UNUSED] (Line 3132)
  - Unused method - not called anywhere in codebase
- **validate_cross_entity_consistency** [STUB, UNUSED] (Line 3044)
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase
- **validate_cross_enum_dependency** [UNUSED] (Line 2689)
  - Unused method - not called anywhere in codebase
- **validate_enum_operation** [UNUSED] (Line 3234)
  - Unused method - not called anywhere in codebase
- **validate_institution_layer_context** [UNUSED] (Line 2579)
  - Unused method - not called anywhere in codebase
- **validate_legitimacy_source_context** [STUB, UNUSED] (Line 2816)
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase
- **validate_required_enum_context** [STUB, UNUSED] (Line 2732)
  - Stub method - matches pattern: ^\s*pass\s*$
  - Unused method - not called anywhere in codebase
- **validate_technology_readiness_level** [UNUSED] (Line 2777)
  - Unused method - not called anywhere in codebase
- **wrapper** [UNUSED] (Line 3244)
  - Unused method - not called anywhere in codebase

### lock_manager
- **force_release_all_locks** [UNUSED] (Line 197)
  - Unused method - not called anywhere in codebase
- **get_lock_info** [UNUSED] (Line 159)
  - Unused method - not called anywhere in codebase
- **reset_lock_manager** [UNUSED] (Line 234)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### core_nodes
No problematic methods found.

### transaction_manager
- **add_operation** [STUB] (Line 137)
  - Stub method - matches pattern: return\s+None\s*$

### observer
- **_notify_node_added** [INCOMPLETE] (Line 82)
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
- **_notify_node_removed** [UNUSED, INCOMPLETE] (Line 92)
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_notify_node_updated** [UNUSED, INCOMPLETE] (Line 101)
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_notify_relationship_added** [INCOMPLETE] (Line 114)
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
- **_notify_relationship_removed** [UNUSED, INCOMPLETE] (Line 128)
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **_notify_relationship_updated** [UNUSED, INCOMPLETE] (Line 137)
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **add_observer** [UNUSED] (Line 64)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **clear_change_history** [UNUSED] (Line 172)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **clear_invalidated_caches** [UNUSED] (Line 234)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **clear_observers** [UNUSED] (Line 74)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_change_history** [UNUSED] (Line 166)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_invalidated_caches** [UNUSED] (Line 230)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_observers** [UNUSED] (Line 78)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **remove_observer** [UNUSED] (Line 69)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### command
- **clear_history** [UNUSED] (Line 476)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_current_command** [STUB, UNUSED] (Line 482)
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_redo_stack** [UNUSED] (Line 471)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_undo_stack** [UNUSED] (Line 466)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### strategy
- **clear_strategies** [UNUSED] (Line 473)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **compare_centralities** [UNUSED] (Line 539)
  - Unused method - not called anywhere in codebase
- **execute_strategy** [UNUSED] (Line 439)
  - Unused method - not called anywhere in codebase
- **find_path** [STUB] (Line 324)
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
- **get_categories** [UNUSED] (Line 491)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_default_strategy** [UNUSED] (Line 423)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_strategy** [STUB] (Line 405)
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
- **get_strategy_metadata** [UNUSED] (Line 434)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **remove_strategy** [UNUSED] (Line 448)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### decorator
- **_remove_lru** [STUB] (Line 109)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **clear_all_caches** [UNUSED] (Line 479)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **clear_audit_log** [UNUSED] (Line 484)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **enhanced_operation** [UNUSED] (Line 444)
  - Unused method - not called anywhere in codebase
- **get** [STUB] (Line 60)
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
- **get_audit_entries** [UNUSED] (Line 469)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_cache_stats** [UNUSED] (Line 464)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_timing_stats** [UNUSED] (Line 474)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **retry_on_failure** [UNUSED] (Line 417)
  - Unused method - not called anywhere in codebase
- **time_execution** [UNUSED] (Line 412)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **validate_inputs** [UNUSED] (Line 395)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **validate_non_empty_string** [UNUSED] (Line 490)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **validate_positive_number** [UNUSED] (Line 495)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **validate_uuid_format** [UNUSED] (Line 500)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **wrapper** [UNUSED] (Line 368)
  - Unused method - not called anywhere in codebase

### plugin
- **_calculate_initialization_order** [STUB] (Line 567)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **activate_all_plugins** [UNUSED] (Line 598)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **add_plugin_directory** [UNUSED] (Line 267)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **cleanup** [STUB] (Line 74)
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis
- **configure** [STUB] (Line 102)
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis
- **configure_plugin** [UNUSED] (Line 507)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **discover_plugins** [UNUSED] (Line 276)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_analyzer** [UNUSED] (Line 178)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_configuration_schema** [UNUSED] (Line 98)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_entity_type** [UNUSED] (Line 170)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_event_handler** [UNUSED] (Line 186)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_global_plugin_manager** [UNUSED] (Line 638)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_metadata** [STUB] (Line 64)
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis
- **get_plugin_health** [STUB, UNUSED] (Line 525)
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_plugin_info** [UNUSED] (Line 490)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_plugin_metrics** [STUB, UNUSED] (Line 540)
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_plugin_registry** [UNUSED] (Line 503)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_plugin_resources** [UNUSED] (Line 224)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_relationship_kind** [UNUSED] (Line 174)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_validator** [UNUSED] (Line 182)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **initialize** [STUB] (Line 69)
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis
- **list_plugins** [UNUSED] (Line 494)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **load_plugin** [UNUSED] (Line 287)
  - Unused method - not called anywhere in codebase
- **set_framework_context** [UNUSED] (Line 272)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **unload_plugin** [UNUSED] (Line 455)
  - Unused method - not called anywhere in codebase
- **visit** [STUB] (Line 574)
  - Stub method - matches pattern: ^\s*return\s*$

### dependency_injection
- **_check_circular_dependencies** [STUB] (Line 605)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **_create_instance** [STUB] (Line 350)
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis
- **_invoke_factory** [STUB] (Line 398)
  - Stub method - matches pattern: ^\s*pass\s*$
  - Minimal implementation - only pass/return/ellipsis
- **add_decorator** [UNUSED] (Line 507)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **add_event_handler** [UNUSED] (Line 517)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **add_middleware** [UNUSED] (Line 512)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **configure_global_container** [UNUSED] (Line 656)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **dispose** [STUB] (Line 75)
  - Stub method - matches pattern: ^\s*return\s*$
  - Minimal implementation - only pass/return/ellipsis
- **example_configuration** [UNUSED, INCOMPLETE] (Line 689)
  - Potentially incomplete - contains: print\s*\(
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_dependency_graph** [UNUSED] (Line 631)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_global_container** [UNUSED] (Line 646)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_service** [UNUSED] (Line 62)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_service_info** [UNUSED] (Line 541)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **inject** [UNUSED] (Line 651)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **is_registered** [UNUSED] (Line 537)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **list_services** [UNUSED] (Line 545)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **logging_interceptor** [UNUSED, INCOMPLETE] (Line 706)
  - Potentially incomplete - contains: print\s*\(
  - Unused method - not called anywhere in codebase
- **register_instance** [UNUSED] (Line 226)
  - Unused method - not called anywhere in codebase
- **scope** [UNUSED] (Line 529)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **try_get** [STUB, UNUSED] (Line 256)
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **unregister** [UNUSED] (Line 549)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **validate_configuration** [UNUSED] (Line 584)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase

### event_bus
- **_apply_middleware** [STUB] (Line 402)
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
- **add_error_handler** [UNUSED] (Line 452)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **add_filter** [UNUSED] (Line 456)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **add_middleware** [UNUSED] (Line 448)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **clear_handlers** [UNUSED] (Line 488)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **clear_history** [UNUSED] (Line 484)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **event_enrichment_middleware** [UNUSED] (Line 559)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **event_filtering_middleware** [STUB, UNUSED] (Line 566)
  - Stub method - matches pattern: return\s+None\s*$
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **event_transformation_middleware** [UNUSED] (Line 574)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_event_history** [UNUSED] (Line 460)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_global_event_bus** [UNUSED] (Line 585)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_handler_metadata** [UNUSED] (Line 466)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **get_supported_event_types** [UNUSED] (Line 553)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **publish** [STUB] (Line 240)
  - Stub method - matches pattern: ^\s*return\s*$
- **publish_event** [UNUSED] (Line 590)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **stop_async_processing** [UNUSED] (Line 305)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **subscribe_to_all** [UNUSED] (Line 174)
  - Unused method - not called anywhere in codebase
- **subscribe_to_event** [UNUSED] (Line 596)
  - Minimal implementation - only pass/return/ellipsis
  - Unused method - not called anywhere in codebase
- **unsubscribe** [UNUSED] (Line 204)
  - Unused method - not called anywhere in codebase
