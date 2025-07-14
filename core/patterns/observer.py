"""
Observer Pattern Implementation for SFM Framework

This module implements the Observer pattern to provide notification mechanisms
for graph changes, allowing components to react to modifications in the graph.
"""

import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.base_nodes import Node
from core.relationships import Relationship


class GraphChangeObserver(ABC):
    """Abstract base class for graph change observers."""
    
    @abstractmethod
    def on_node_added(self, node: Node) -> None:
        """Called when a node is added to the graph."""
        pass
    
    @abstractmethod
    def on_node_removed(self, node_id: uuid.UUID) -> None:
        """Called when a node is removed from the graph."""
        pass
    
    @abstractmethod
    def on_node_updated(self, node: Node, previous_state: Dict[str, Any]) -> None:
        """Called when a node is updated."""
        pass
    
    @abstractmethod
    def on_relationship_added(self, relationship: Relationship) -> None:
        """Called when a relationship is added to the graph."""
        pass
    
    @abstractmethod
    def on_relationship_removed(self, relationship_id: uuid.UUID) -> None:
        """Called when a relationship is removed from the graph."""
        pass
    
    @abstractmethod
    def on_relationship_updated(self, relationship: Relationship, previous_state: Dict[str, Any]) -> None:
        """Called when a relationship is updated."""
        pass


class GraphObservable:
    """
    Mixin class that provides observable capabilities to graph components.
    
    This class implements the Subject part of the Observer pattern,
    allowing multiple observers to be notified of graph changes.
    """
    
    def __init__(self):
        self._observers: List[GraphChangeObserver] = []
        self._change_history: List[Dict[str, Any]] = []
        self._max_history_size = 1000
    
    def add_observer(self, observer: GraphChangeObserver) -> None:
        """Add an observer to be notified of graph changes."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: GraphChangeObserver) -> None:
        """Remove an observer from the notification list."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def clear_observers(self) -> None:
        """Remove all observers."""
        self._observers.clear()
    
    def get_observers(self) -> List[GraphChangeObserver]:
        """Get a copy of the current observers list."""
        return self._observers.copy()
    
    def _notify_node_added(self, node: Node) -> None:
        """Notify all observers that a node was added."""
        self._record_change("node_added", {"node_id": node.id, "node_type": type(node).__name__})
        for observer in self._observers:
            try:
                observer.on_node_added(node)
            except Exception as e:
                # Log error but don't stop other observers
                print(f"Error in observer {observer.__class__.__name__}: {e}")
    
    def _notify_node_removed(self, node_id: uuid.UUID) -> None:
        """Notify all observers that a node was removed."""
        self._record_change("node_removed", {"node_id": node_id})
        for observer in self._observers:
            try:
                observer.on_node_removed(node_id)
            except Exception as e:
                print(f"Error in observer {observer.__class__.__name__}: {e}")
    
    def _notify_node_updated(self, node: Node, previous_state: Dict[str, Any]) -> None:
        """Notify all observers that a node was updated."""
        self._record_change("node_updated", {
            "node_id": node.id,
            "node_type": type(node).__name__,
            "previous_state": previous_state
        })
        for observer in self._observers:
            try:
                observer.on_node_updated(node, previous_state)
            except Exception as e:
                print(f"Error in observer {observer.__class__.__name__}: {e}")
    
    def _notify_relationship_added(self, relationship: Relationship) -> None:
        """Notify all observers that a relationship was added."""
        self._record_change("relationship_added", {
            "relationship_id": relationship.id,
            "source_id": relationship.source_id,
            "target_id": relationship.target_id,
            "kind": relationship.kind.name if hasattr(relationship.kind, 'name') else str(relationship.kind)
        })
        for observer in self._observers:
            try:
                observer.on_relationship_added(relationship)
            except Exception as e:
                print(f"Error in observer {observer.__class__.__name__}: {e}")
    
    def _notify_relationship_removed(self, relationship_id: uuid.UUID) -> None:
        """Notify all observers that a relationship was removed."""
        self._record_change("relationship_removed", {"relationship_id": relationship_id})
        for observer in self._observers:
            try:
                observer.on_relationship_removed(relationship_id)
            except Exception as e:
                print(f"Error in observer {observer.__class__.__name__}: {e}")
    
    def _notify_relationship_updated(self, relationship: Relationship, previous_state: Dict[str, Any]) -> None:
        """Notify all observers that a relationship was updated."""
        self._record_change("relationship_updated", {
            "relationship_id": relationship.id,
            "source_id": relationship.source_id,
            "target_id": relationship.target_id,
            "kind": relationship.kind.name if hasattr(relationship.kind, 'name') else str(relationship.kind),
            "previous_state": previous_state
        })
        for observer in self._observers:
            try:
                observer.on_relationship_updated(relationship, previous_state)
            except Exception as e:
                print(f"Error in observer {observer.__class__.__name__}: {e}")
    
    def _record_change(self, change_type: str, details: Dict[str, Any]) -> None:
        """Record a change in the change history."""
        change_record = {
            "timestamp": datetime.now().isoformat(),
            "change_type": change_type,
            "details": details
        }
        
        self._change_history.append(change_record)
        
        # Limit history size
        if len(self._change_history) > self._max_history_size:
            self._change_history = self._change_history[-self._max_history_size:]
    
    def get_change_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get the change history, optionally limited to recent changes."""
        if limit is None:
            return self._change_history.copy()
        return self._change_history[-limit:]
    
    def clear_change_history(self) -> None:
        """Clear the change history."""
        self._change_history.clear()


class CachingObserver(GraphChangeObserver):
    """
    Example observer that invalidates caches when the graph changes.
    
    This demonstrates how observers can be used to implement cross-cutting
    concerns like cache invalidation.
    """
    
    def __init__(self):
        self.invalidated_caches: List[str] = []
    
    def on_node_added(self, node: Node) -> None:
        """Invalidate node-related caches when a node is added."""
        self._invalidate_cache(f"node_cache_{node.id}")
        self._invalidate_cache("node_list_cache")
        self._invalidate_cache("graph_statistics_cache")
    
    def on_node_removed(self, node_id: uuid.UUID) -> None:
        """Invalidate node-related caches when a node is removed."""
        self._invalidate_cache(f"node_cache_{node_id}")
        self._invalidate_cache("node_list_cache")
        self._invalidate_cache("graph_statistics_cache")
    
    def on_node_updated(self, node: Node, previous_state: Dict[str, Any]) -> None:
        """Invalidate node-related caches when a node is updated."""
        self._invalidate_cache(f"node_cache_{node.id}")
        self._invalidate_cache("node_list_cache")
    
    def on_relationship_added(self, relationship: Relationship) -> None:
        """Invalidate relationship-related caches when a relationship is added."""
        self._invalidate_cache(f"relationship_cache_{relationship.id}")
        self._invalidate_cache("relationship_list_cache")
        self._invalidate_cache("graph_statistics_cache")
        self._invalidate_cache("centrality_cache")
    
    def on_relationship_removed(self, relationship_id: uuid.UUID) -> None:
        """Invalidate relationship-related caches when a relationship is removed."""
        self._invalidate_cache(f"relationship_cache_{relationship_id}")
        self._invalidate_cache("relationship_list_cache")
        self._invalidate_cache("graph_statistics_cache")
        self._invalidate_cache("centrality_cache")
    
    def on_relationship_updated(self, relationship: Relationship, previous_state: Dict[str, Any]) -> None:
        """Invalidate relationship-related caches when a relationship is updated."""
        self._invalidate_cache(f"relationship_cache_{relationship.id}")
        self._invalidate_cache("relationship_list_cache")
        self._invalidate_cache("centrality_cache")
    
    def _invalidate_cache(self, cache_key: str) -> None:
        """Invalidate a specific cache."""
        if cache_key not in self.invalidated_caches:
            self.invalidated_caches.append(cache_key)
    
    def get_invalidated_caches(self) -> List[str]:
        """Get the list of invalidated caches."""
        return self.invalidated_caches.copy()
    
    def clear_invalidated_caches(self) -> None:
        """Clear the list of invalidated caches."""
        self.invalidated_caches.clear()


class MetricsObserver(GraphChangeObserver):
    """
    Example observer that tracks graph metrics and changes.
    
    This demonstrates how observers can be used to implement monitoring
    and analytics features.
    """
    
    def __init__(self):
        self.metrics = {
            "nodes_added": 0,
            "nodes_removed": 0,
            "nodes_updated": 0,
            "relationships_added": 0,
            "relationships_removed": 0,
            "relationships_updated": 0,
            "last_change_timestamp": None
        }
    
    def on_node_added(self, node: Node) -> None:
        """Track node addition metrics."""
        self.metrics["nodes_added"] += 1
        self.metrics["last_change_timestamp"] = datetime.now().isoformat()
    
    def on_node_removed(self, node_id: uuid.UUID) -> None:
        """Track node removal metrics."""
        self.metrics["nodes_removed"] += 1
        self.metrics["last_change_timestamp"] = datetime.now().isoformat()
    
    def on_node_updated(self, node: Node, previous_state: Dict[str, Any]) -> None:
        """Track node update metrics."""
        self.metrics["nodes_updated"] += 1
        self.metrics["last_change_timestamp"] = datetime.now().isoformat()
    
    def on_relationship_added(self, relationship: Relationship) -> None:
        """Track relationship addition metrics."""
        self.metrics["relationships_added"] += 1
        self.metrics["last_change_timestamp"] = datetime.now().isoformat()
    
    def on_relationship_removed(self, relationship_id: uuid.UUID) -> None:
        """Track relationship removal metrics."""
        self.metrics["relationships_removed"] += 1
        self.metrics["last_change_timestamp"] = datetime.now().isoformat()
    
    def on_relationship_updated(self, relationship: Relationship, previous_state: Dict[str, Any]) -> None:
        """Track relationship update metrics."""
        self.metrics["relationships_updated"] += 1
        self.metrics["last_change_timestamp"] = datetime.now().isoformat()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self) -> None:
        """Reset all metrics to zero."""
        self.metrics = {
            "nodes_added": 0,
            "nodes_removed": 0,
            "nodes_updated": 0,
            "relationships_added": 0,
            "relationships_removed": 0,
            "relationships_updated": 0,
            "last_change_timestamp": None
        }