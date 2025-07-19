"""
Advanced Caching module for SFM Graph Service.

This module provides core caching functionality for the SFM framework,
including cache warming for frequently accessed nodes.
"""

import logging
from typing import List, Optional, Any

logger = logging.getLogger(__name__)


class CacheWarmer:
    """Cache warming system for pre-populating frequently accessed data."""
    
    def __init__(self, graph_instance: Optional[Any] = None):
        """Initialize the cache warmer with optional graph instance."""
        self.graph = graph_instance
    
    def warm_frequently_accessed_nodes(self, node_ids: List[str]) -> None:
        """
        Warm cache for frequently accessed nodes.
        
        This method pre-loads frequently accessed node data into cache to improve
        performance for subsequent queries. It attempts to cache both node data
        and their relationships.
        
        Args:
            node_ids: List of node identifiers to warm in cache
        """
        if not self.graph:
            logger.warning("No graph instance available for cache warming")
            return
        
        if not node_ids:
            logger.debug("No node IDs provided for cache warming")
            return
        
        logger.info("Starting cache warming for %d nodes", len(node_ids))
        warmed_count = 0
        
        for node_id in node_ids:
            try:
                # Warm node data by attempting to retrieve the node
                if hasattr(self.graph, 'get_node_by_id'):
                    node_data = self.graph.get_node_by_id(node_id)
                    if node_data:
                        warmed_count += 1
                        logger.debug("Warmed cache for node: %s", node_id)
                    else:
                        logger.debug("Node not found: %s", node_id)
                elif hasattr(self.graph, 'get_node'):
                    # Try alternative method name
                    node_data = self.graph.get_node(node_id)
                    if node_data:
                        warmed_count += 1
                        logger.debug("Warmed cache for node: %s", node_id)
                
                # Warm node relationships if the method exists
                if hasattr(self.graph, 'get_node_relationships'):
                    relationships = self.graph.get_node_relationships(node_id)
                    if relationships:
                        logger.debug("Warmed relationships for node: %s", node_id)
                elif hasattr(self.graph, 'get_relationships'):
                    # Try alternative method name
                    relationships = self.graph.get_relationships(node_id)
                    if relationships:
                        logger.debug("Warmed relationships for node: %s", node_id)
                
                # Warm adjacent nodes if method exists
                if hasattr(self.graph, 'get_adjacent_nodes'):
                    adjacent = self.graph.get_adjacent_nodes(node_id)
                    if adjacent:
                        logger.debug("Warmed adjacent nodes for: %s", node_id)
                
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error warming cache for node %s: %s", node_id, e)
                continue
        
        logger.info("Cache warming completed. Successfully warmed %d out of %d nodes", 
                   warmed_count, len(node_ids))