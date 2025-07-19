"""
Memory Management Infrastructure for SFM Graph Service

This module provides memory monitoring, limits enforcement, and node eviction
strategies to handle large graphs efficiently and prevent memory exhaustion.

Features:
- Real-time memory usage monitoring
- Configurable memory limits with enforcement
- Node eviction strategies (LRU, usage-based)
- Memory-aware caching with automatic cleanup
- Performance metrics integration
"""

import time
import uuid
import logging
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Protocol, Set
from enum import Enum

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class EvictionStrategy(Enum):
    """Available eviction strategies for memory management."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    OLDEST_FIRST = "oldest_first"  # Oldest nodes first
    LARGEST_FIRST = "largest_first"  # Largest nodes first (if size available)


@dataclass
class MemoryUsageStats:
    """Current memory usage statistics."""
    total_memory_mb: float = 0.0
    used_memory_mb: float = 0.0
    available_memory_mb: float = 0.0
    memory_percent: float = 0.0
    process_memory_mb: float = 0.0
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def capture_current(cls) -> 'MemoryUsageStats':
        """Capture current system memory usage."""
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available, returning empty memory stats")
            return cls()

        try:
            # System memory
            memory = psutil.virtual_memory()
            
            # Process memory
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return cls(
                total_memory_mb=memory.total / (1024 * 1024),
                used_memory_mb=memory.used / (1024 * 1024),
                available_memory_mb=memory.available / (1024 * 1024),
                memory_percent=memory.percent,
                process_memory_mb=process_memory.rss / (1024 * 1024)
            )
        except Exception as e:
            logger.error(f"Failed to capture memory stats: {e}")
            return cls()

    def is_over_limit(self, limit_mb: float) -> bool:
        """Check if process memory usage exceeds the specified limit."""
        return self.process_memory_mb > limit_mb


class NodeAccessTracker:
    """Tracks node access patterns for eviction decisions."""
    
    def __init__(self, max_tracking_size: int = 10000):
        self._access_times: Dict[uuid.UUID, float] = {}
        self._access_counts: Dict[uuid.UUID, int] = {}
        self._access_order: OrderedDict[uuid.UUID, None] = OrderedDict()
        self._max_tracking_size = max_tracking_size
    
    def record_access(self, node_id: uuid.UUID) -> None:
        """Record that a node was accessed."""
        current_time = time.time()
        
        # Update access time and count
        self._access_times[node_id] = current_time
        self._access_counts[node_id] = self._access_counts.get(node_id, 0) + 1
        
        # Update LRU order
        if node_id in self._access_order:
            del self._access_order[node_id]
        self._access_order[node_id] = None
        
        # Limit tracking size to prevent unbounded growth
        if len(self._access_order) > self._max_tracking_size:
            # Remove oldest tracked node
            oldest_id, _ = self._access_order.popitem(last=False)
            self._access_times.pop(oldest_id, None)
            self._access_counts.pop(oldest_id, None)
    
    def get_lru_nodes(self, count: int) -> List[uuid.UUID]:
        """Get the least recently used nodes."""
        return list(self._access_order.keys())[:count]
    
    def get_lfu_nodes(self, count: int) -> List[uuid.UUID]:
        """Get the least frequently used nodes."""
        sorted_nodes = sorted(
            self._access_counts.items(),
            key=lambda x: x[1]  # Sort by access count
        )
        return [node_id for node_id, _ in sorted_nodes[:count]]
    
    def get_access_time(self, node_id: uuid.UUID) -> Optional[float]:
        """Get the last access time for a node."""
        return self._access_times.get(node_id)
    
    def get_access_count(self, node_id: uuid.UUID) -> int:
        """Get the access count for a node."""
        return self._access_counts.get(node_id, 0)
    
    def remove_node(self, node_id: uuid.UUID) -> None:
        """Remove a node from tracking."""
        self._access_times.pop(node_id, None)
        self._access_counts.pop(node_id, None)
        self._access_order.pop(node_id, None)


class EvictableGraph(Protocol):
    """Protocol for graphs that support node eviction."""
    
    def get_all_node_ids(self) -> Set[uuid.UUID]:
        """Get all node IDs in the graph."""
        ...
    
    def remove_node_from_memory(self, node_id: uuid.UUID) -> bool:
        """Remove a node from memory (but not from persistent storage)."""
        ...
    
    def get_node_size_estimate(self, node_id: uuid.UUID) -> int:
        """Get estimated memory size of a node in bytes."""
        ...


class EvictionStrategyBase(ABC):
    """Base class for node eviction strategies."""
    
    def __init__(self, access_tracker: NodeAccessTracker):
        self.access_tracker = access_tracker
    
    @abstractmethod
    def select_nodes_for_eviction(self, graph: EvictableGraph, target_count: int) -> List[uuid.UUID]:
        """Select nodes for eviction based on the strategy."""
        pass


class LRUEvictionStrategy(EvictionStrategyBase):
    """Least Recently Used eviction strategy."""
    
    def select_nodes_for_eviction(self, graph: EvictableGraph, target_count: int) -> List[uuid.UUID]:
        """Select least recently used nodes for eviction."""
        candidates = self.access_tracker.get_lru_nodes(target_count * 2)  # Get more candidates
        available_nodes = [node_id for node_id in candidates if node_id in graph.get_all_node_ids()]
        return available_nodes[:target_count]


class LFUEvictionStrategy(EvictionStrategyBase):
    """Least Frequently Used eviction strategy."""
    
    def select_nodes_for_eviction(self, graph: EvictableGraph, target_count: int) -> List[uuid.UUID]:
        """Select least frequently used nodes for eviction."""
        candidates = self.access_tracker.get_lfu_nodes(target_count * 2)
        available_nodes = [node_id for node_id in candidates if node_id in graph.get_all_node_ids()]
        return available_nodes[:target_count]


class OldestFirstEvictionStrategy(EvictionStrategyBase):
    """Evict oldest nodes first based on creation time."""
    
    def select_nodes_for_eviction(self, graph: EvictableGraph, target_count: int) -> List[uuid.UUID]:
        """Select oldest nodes for eviction."""
        all_nodes = list(graph.get_all_node_ids())
        # Sort by UUID (which includes timestamp info in some cases) or access time
        sorted_nodes = sorted(all_nodes, key=lambda node_id: self.access_tracker.get_access_time(node_id) or 0)
        return sorted_nodes[:target_count]


class MemoryMonitor:
    """Monitors memory usage and triggers eviction when limits are exceeded."""
    
    def __init__(self, 
                 memory_limit_mb: float = 1000.0,
                 warning_threshold: float = 0.8,
                 critical_threshold: float = 0.95,
                 eviction_batch_size: int = 100):
        self.memory_limit_mb = memory_limit_mb
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.eviction_batch_size = eviction_batch_size
        
        self.access_tracker = NodeAccessTracker()
        self._eviction_strategies = {
            EvictionStrategy.LRU: LRUEvictionStrategy(self.access_tracker),
            EvictionStrategy.LFU: LFUEvictionStrategy(self.access_tracker),
            EvictionStrategy.OLDEST_FIRST: OldestFirstEvictionStrategy(self.access_tracker),
        }
        self._current_strategy = EvictionStrategy.LRU
        
        # Statistics
        self._eviction_count = 0
        self._last_eviction_time = 0.0
        self._total_nodes_evicted = 0
    
    @property
    def current_strategy(self) -> EvictionStrategy:
        """Get the current eviction strategy."""
        return self._current_strategy
    
    @current_strategy.setter
    def current_strategy(self, strategy: EvictionStrategy):
        """Set the eviction strategy."""
        if strategy in self._eviction_strategies:
            self._current_strategy = strategy
        else:
            raise ValueError(f"Unknown eviction strategy: {strategy}")
    
    def record_node_access(self, node_id: uuid.UUID) -> None:
        """Record that a node was accessed."""
        self.access_tracker.record_access(node_id)
    
    def check_memory_usage(self) -> MemoryUsageStats:
        """Check current memory usage and return stats."""
        return MemoryUsageStats.capture_current()
    
    def should_evict_nodes(self, memory_stats: Optional[MemoryUsageStats] = None) -> bool:
        """Check if node eviction should be triggered."""
        if memory_stats is None:
            memory_stats = self.check_memory_usage()
        
        return memory_stats.is_over_limit(self.memory_limit_mb * self.warning_threshold)
    
    def evict_nodes(self, graph: EvictableGraph, force: bool = False) -> int:
        """Evict nodes from the graph to free memory."""
        memory_stats = self.check_memory_usage()
        
        if not force and not self.should_evict_nodes(memory_stats):
            return 0
        
        # Determine how many nodes to evict
        if memory_stats.is_over_limit(self.memory_limit_mb * self.critical_threshold):
            # Critical: evict more aggressively
            target_count = self.eviction_batch_size * 2
        else:
            target_count = self.eviction_batch_size
        
        # Select nodes for eviction
        strategy = self._eviction_strategies[self._current_strategy]
        nodes_to_evict = strategy.select_nodes_for_eviction(graph, target_count)
        
        # Perform eviction
        evicted_count = 0
        for node_id in nodes_to_evict:
            try:
                if graph.remove_node_from_memory(node_id):
                    self.access_tracker.remove_node(node_id)
                    evicted_count += 1
            except Exception as e:
                logger.warning(f"Failed to evict node {node_id}: {e}")
        
        # Update statistics
        if evicted_count > 0:
            self._eviction_count += 1
            self._last_eviction_time = time.time()
            self._total_nodes_evicted += evicted_count
            
            logger.info(f"Evicted {evicted_count} nodes using {self._current_strategy.value} strategy")
        
        return evicted_count
    
    def get_eviction_stats(self) -> Dict[str, any]:
        """Get eviction statistics."""
        return {
            "eviction_count": self._eviction_count,
            "total_nodes_evicted": self._total_nodes_evicted,
            "last_eviction_time": self._last_eviction_time,
            "current_strategy": self._current_strategy.value,
            "memory_limit_mb": self.memory_limit_mb,
            "warning_threshold": self.warning_threshold,
            "critical_threshold": self.critical_threshold,
            "eviction_batch_size": self.eviction_batch_size
        }