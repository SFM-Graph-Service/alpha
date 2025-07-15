"""
Strategy Pattern Implementation for SFM Framework

This module implements the Strategy pattern to provide pluggable algorithms
for various graph analysis operations, allowing for easy extensibility and
algorithm swapping without modifying core code.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type, Callable
from dataclasses import dataclass

import networkx as nx

from core.base_nodes import Node


class Strategy(ABC):
    """Abstract base class for all strategies."""

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this strategy."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get a description of this strategy."""
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the strategy with the given arguments."""
        pass


class CentralityStrategy(Strategy):
    """Abstract base class for centrality calculation strategies."""

    @abstractmethod
    def calculate(self, graph: nx.Graph, node_id: uuid.UUID) -> float:
        """Calculate centrality for a specific node."""
        pass

    @abstractmethod
    def calculate_all(self, graph: nx.Graph) -> Dict[uuid.UUID, float]:
        """Calculate centrality for all nodes in the graph."""
        pass


class BetweennessCentralityStrategy(CentralityStrategy):
    """Strategy for calculating betweenness centrality."""

    def get_name(self) -> str:
        return "betweenness"

    def get_description(self) -> str:
        return "Betweenness centrality measures the extent to which a node lies on paths between other nodes"

    def calculate(self, graph: nx.Graph, node_id: uuid.UUID) -> float:
        """Calculate betweenness centrality for a specific node."""
        if node_id not in graph.nodes():
            return 0.0

        centrality_scores = nx.betweenness_centrality(graph)
        return centrality_scores.get(node_id, 0.0)

    def calculate_all(self, graph: nx.Graph) -> Dict[uuid.UUID, float]:
        """Calculate betweenness centrality for all nodes."""
        return nx.betweenness_centrality(graph)

    def execute(self,
                graph: nx.Graph,
                node_id: Optional[uuid.UUID] = None,
                **kwargs) -> Any:
        """Execute the strategy."""
        if node_id is not None:
            return self.calculate(graph, node_id)
        return self.calculate_all(graph)


class ClosenessCentralityStrategy(CentralityStrategy):
    """Strategy for calculating closeness centrality."""

    def get_name(self) -> str:
        return "closeness"

    def get_description(self) -> str:
        return "Closeness centrality measures how close a node is to all other nodes in the graph"

    def calculate(self, graph: nx.Graph, node_id: uuid.UUID) -> float:
        """Calculate closeness centrality for a specific node."""
        if node_id not in graph.nodes():
            return 0.0

        centrality_scores = nx.closeness_centrality(graph)
        return centrality_scores.get(node_id, 0.0)

    def calculate_all(self, graph: nx.Graph) -> Dict[uuid.UUID, float]:
        """Calculate closeness centrality for all nodes."""
        return nx.closeness_centrality(graph)

    def execute(self,
                graph: nx.Graph,
                node_id: Optional[uuid.UUID] = None,
                **kwargs) -> Any:
        """Execute the strategy."""
        if node_id is not None:
            return self.calculate(graph, node_id)
        return self.calculate_all(graph)


class EigenvectorCentralityStrategy(CentralityStrategy):
    """Strategy for calculating eigenvector centrality."""

    def get_name(self) -> str:
        return "eigenvector"

    def get_description(self) -> str:
        return "Eigenvector centrality measures the influence of a node based on the centrality of its neighbors"

    def calculate(self, graph: nx.Graph, node_id: uuid.UUID) -> float:
        """Calculate eigenvector centrality for a specific node."""
        if node_id not in graph.nodes():
            return 0.0

        try:
            centrality_scores = nx.eigenvector_centrality(graph, max_iter=1000)
            return centrality_scores.get(node_id, 0.0)
        except nx.NetworkXError:
            # Fallback to degree centrality if eigenvector fails to converge
            centrality_scores = nx.degree_centrality(graph)
            return centrality_scores.get(node_id, 0.0)

    def calculate_all(self, graph: nx.Graph) -> Dict[uuid.UUID, float]:
        """Calculate eigenvector centrality for all nodes."""
        try:
            return nx.eigenvector_centrality(graph, max_iter=1000)
        except nx.NetworkXError:
            # Fallback to degree centrality if eigenvector fails to converge
            return nx.degree_centrality(graph)

    def execute(self,
                graph: nx.Graph,
                node_id: Optional[uuid.UUID] = None,
                **kwargs) -> Any:
        """Execute the strategy."""
        if node_id is not None:
            return self.calculate(graph, node_id)
        return self.calculate_all(graph)


class DegreeCentralityStrategy(CentralityStrategy):
    """Strategy for calculating degree centrality."""

    def get_name(self) -> str:
        return "degree"

    def get_description(self) -> str:
        return "Degree centrality measures the number of connections a node has"

    def calculate(self, graph: nx.Graph, node_id: uuid.UUID) -> float:
        """Calculate degree centrality for a specific node."""
        if node_id not in graph.nodes():
            return 0.0

        centrality_scores = nx.degree_centrality(graph)
        return centrality_scores.get(node_id, 0.0)

    def calculate_all(self, graph: nx.Graph) -> Dict[uuid.UUID, float]:
        """Calculate degree centrality for all nodes."""
        return nx.degree_centrality(graph)

    def execute(self,
                graph: nx.Graph,
                node_id: Optional[uuid.UUID] = None,
                **kwargs) -> Any:
        """Execute the strategy."""
        if node_id is not None:
            return self.calculate(graph, node_id)
        return self.calculate_all(graph)


class CommunityDetectionStrategy(Strategy):
    """Abstract base class for community detection strategies."""

    @abstractmethod
    def detect_communities(
            self, graph: nx.Graph) -> Dict[int, List[uuid.UUID]]:
        """Detect communities in the graph."""
        pass


class LouvainCommunityStrategy(CommunityDetectionStrategy):
    """Strategy for Louvain community detection."""

    def get_name(self) -> str:
        return "louvain"

    def get_description(self) -> str:
        return "Louvain method for community detection based on modularity optimization"

    def detect_communities(
            self, graph: nx.Graph) -> Dict[int, List[uuid.UUID]]:
        """Detect communities using the Louvain algorithm."""
        if graph.number_of_nodes() == 0:
            return {}

        try:
            # Convert to undirected for community detection
            undirected_graph = graph.to_undirected() if graph.is_directed() else graph
            communities = nx.algorithms.community.louvain_communities(
                undirected_graph)

            # Convert to the expected format
            community_dict = {}
            for i, community in enumerate(communities):
                community_dict[i] = list(community)

            return community_dict
        except nx.NetworkXError:
            # Fallback: return all nodes as single community
            return {0: list(graph.nodes())}

    def execute(self, graph: nx.Graph, **kwargs) -> Dict[int, List[uuid.UUID]]:
        """Execute the strategy."""
        return self.detect_communities(graph)


class LabelPropagationCommunityStrategy(CommunityDetectionStrategy):
    """Strategy for label propagation community detection."""

    def get_name(self) -> str:
        return "label_propagation"

    def get_description(self) -> str:
        return "Label propagation algorithm for community detection"

    def detect_communities(
            self, graph: nx.Graph) -> Dict[int, List[uuid.UUID]]:
        """Detect communities using label propagation."""
        if graph.number_of_nodes() == 0:
            return {}

        try:
            # Convert to undirected for community detection
            undirected_graph = graph.to_undirected() if graph.is_directed() else graph
            communities = nx.algorithms.community.label_propagation_communities(
                undirected_graph)

            # Convert to the expected format
            community_dict = {}
            for i, community in enumerate(communities):
                community_dict[i] = list(community)

            return community_dict
        except nx.NetworkXError:
            # Fallback: return all nodes as single community
            return {0: list(graph.nodes())}

    def execute(self, graph: nx.Graph, **kwargs) -> Dict[int, List[uuid.UUID]]:
        """Execute the strategy."""
        return self.detect_communities(graph)


class GreedyModularityCommunityStrategy(CommunityDetectionStrategy):
    """Strategy for greedy modularity community detection."""

    def get_name(self) -> str:
        return "greedy_modularity"

    def get_description(self) -> str:
        return "Greedy modularity maximization algorithm for community detection"

    def detect_communities(
            self, graph: nx.Graph) -> Dict[int, List[uuid.UUID]]:
        """Detect communities using greedy modularity maximization."""
        if graph.number_of_nodes() == 0:
            return {}

        try:
            # Convert to undirected for community detection
            undirected_graph = graph.to_undirected() if graph.is_directed() else graph
            communities = nx.algorithms.community.greedy_modularity_communities(
                undirected_graph)

            # Convert to the expected format
            community_dict = {}
            for i, community in enumerate(communities):
                community_dict[i] = list(community)

            return community_dict
        except nx.NetworkXError:
            # Fallback: return all nodes as single community
            return {0: list(graph.nodes())}

    def execute(self, graph: nx.Graph, **kwargs) -> Dict[int, List[uuid.UUID]]:
        """Execute the strategy."""
        return self.detect_communities(graph)


class PathFindingStrategy(Strategy):
    """Abstract base class for path finding strategies."""

    @abstractmethod
    def find_path(self, graph: nx.Graph, source: uuid.UUID,
                  target: uuid.UUID) -> Optional[List[uuid.UUID]]:
        """Find a path between two nodes."""
        pass


class ShortestPathStrategy(PathFindingStrategy):
    """Strategy for finding shortest paths."""

    def get_name(self) -> str:
        return "shortest_path"

    def get_description(self) -> str:
        return "Dijkstra's algorithm for finding shortest paths"

    def find_path(self, graph: nx.Graph, source: uuid.UUID,
                  target: uuid.UUID) -> Optional[List[uuid.UUID]]:
        """Find the shortest path between two nodes."""
        try:
            path = nx.shortest_path(graph, source, target)
            return path if isinstance(path, list) else None
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def execute(self,
                graph: nx.Graph,
                source: uuid.UUID,
                target: uuid.UUID,
                **kwargs) -> Optional[List[uuid.UUID]]:
        """Execute the strategy."""
        return self.find_path(graph, source, target)


class AllShortestPathsStrategy(PathFindingStrategy):
    """Strategy for finding all shortest paths."""

    def get_name(self) -> str:
        return "all_shortest_paths"

    def get_description(self) -> str:
        return "Find all shortest paths between two nodes"

    def find_path(self, graph: nx.Graph, source: uuid.UUID,
                  target: uuid.UUID) -> Optional[List[uuid.UUID]]:
        """Find the first shortest path (for compatibility with interface)."""
        try:
            paths = list(nx.all_shortest_paths(graph, source, target))
            return paths[0] if paths else None
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def find_all_paths(self, graph: nx.Graph, source: uuid.UUID,
                       target: uuid.UUID) -> List[List[uuid.UUID]]:
        """Find all shortest paths between two nodes."""
        try:
            return list(nx.all_shortest_paths(graph, source, target))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def execute(self,
                graph: nx.Graph,
                source: uuid.UUID,
                target: uuid.UUID,
                **kwargs) -> List[List[uuid.UUID]]:
        """Execute the strategy."""
        return self.find_all_paths(graph, source, target)


@dataclass
class StrategyMetadata:
    """Metadata about a strategy."""
    name: str
    description: str
    strategy_type: str
    parameters: Dict[str, Any]
    performance_metrics: Dict[str, Any]


class StrategyManager:
    """
    Manager for strategies that allows registering and using different
    algorithm implementations.
    """

    def __init__(self):
        self._strategies: Dict[str, Dict[str, Strategy]] = {}
        self._default_strategies: Dict[str, str] = {}
        self._strategy_metadata: Dict[str, StrategyMetadata] = {}

        # Register default strategies
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        """Register default strategies for different categories."""
        # Centrality strategies
        self.register_strategy("centrality", BetweennessCentralityStrategy())
        self.register_strategy("centrality", ClosenessCentralityStrategy())
        self.register_strategy("centrality", EigenvectorCentralityStrategy())
        self.register_strategy("centrality", DegreeCentralityStrategy())
        self.set_default_strategy("centrality", "betweenness")

        # Community detection strategies
        self.register_strategy("community", LouvainCommunityStrategy())
        self.register_strategy(
            "community",
            LabelPropagationCommunityStrategy())
        self.register_strategy(
            "community",
            GreedyModularityCommunityStrategy())
        self.set_default_strategy("community", "louvain")

        # Path finding strategies
        self.register_strategy("pathfinding", ShortestPathStrategy())
        self.register_strategy("pathfinding", AllShortestPathsStrategy())
        self.set_default_strategy("pathfinding", "shortest_path")

    def register_strategy(self, category: str, strategy: Strategy) -> None:
        """Register a strategy for a specific category."""
        if category not in self._strategies:
            self._strategies[category] = {}

        strategy_name = strategy.get_name()
        self._strategies[category][strategy_name] = strategy

        # Create metadata
        self._strategy_metadata[f"{category}:{strategy_name}"] = StrategyMetadata(
            name=strategy_name,
            description=strategy.get_description(),
            strategy_type=category,
            parameters={},
            performance_metrics={}
        )

    def get_strategy(
            self,
            category: str,
            strategy_name: Optional[str] = None) -> Optional[Strategy]:
        """Get a strategy by category and name."""
        if category not in self._strategies:
            return None

        if strategy_name is None:
            strategy_name = self._default_strategies.get(category)

        if strategy_name is None:
            return None

        return self._strategies[category].get(strategy_name)

    def set_default_strategy(self, category: str, strategy_name: str) -> None:
        """Set the default strategy for a category."""
        if category in self._strategies and strategy_name in self._strategies[category]:
            self._default_strategies[category] = strategy_name

    def get_default_strategy(self, category: str) -> Optional[str]:
        """Get the default strategy name for a category."""
        return self._default_strategies.get(category)

    def list_strategies(
            self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """List all available strategies."""
        if category is not None:
            return {category: list(self._strategies.get(category, {}).keys())}

        return {cat: list(strategies.keys())
                for cat, strategies in self._strategies.items()}

    def get_strategy_metadata(
            self,
            category: str,
            strategy_name: str) -> Optional[StrategyMetadata]:
        """Get metadata for a specific strategy."""
        key = f"{category}:{strategy_name}"
        return self._strategy_metadata.get(key)

    def execute_strategy(
            self,
            category: str,
            strategy_name: Optional[str] = None,
            *args,
            **kwargs) -> Any:
        """Execute a strategy with the given arguments."""
        strategy = self.get_strategy(category, strategy_name)
        if strategy is None:
            raise ValueError(f"Strategy not found: {category}:{strategy_name}")

        return strategy.execute(*args, **kwargs)

    def remove_strategy(self, category: str, strategy_name: str) -> bool:
        """Remove a strategy from the manager."""
        if category not in self._strategies:
            return False

        if strategy_name not in self._strategies[category]:
            return False

        del self._strategies[category][strategy_name]

        # Remove metadata
        key = f"{category}:{strategy_name}"
        if key in self._strategy_metadata:
            del self._strategy_metadata[key]

        # Update default if necessary
        if self._default_strategies.get(category) == strategy_name:
            remaining_strategies = list(self._strategies[category].keys())
            if remaining_strategies:
                self._default_strategies[category] = remaining_strategies[0]
            else:
                del self._default_strategies[category]

        return True

    def clear_strategies(self, category: Optional[str] = None) -> None:
        """Clear all strategies, optionally filtered by category."""
        if category is not None:
            if category in self._strategies:
                # Remove metadata for this category
                for strategy_name in self._strategies[category]:
                    key = f"{category}:{strategy_name}"
                    if key in self._strategy_metadata:
                        del self._strategy_metadata[key]

                del self._strategies[category]
                if category in self._default_strategies:
                    del self._default_strategies[category]
        else:
            self._strategies.clear()
            self._default_strategies.clear()
            self._strategy_metadata.clear()

    def get_categories(self) -> List[str]:
        """Get all strategy categories."""
        return list(self._strategies.keys())

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about registered strategies."""
        total_strategies = sum(len(strategies)
                               for strategies in self._strategies.values())

        return {
            "total_strategies": total_strategies,
            "categories": len(
                self._strategies),
            "strategies_by_category": {
                cat: len(strategies) for cat,
                strategies in self._strategies.items()},
            "default_strategies": self._default_strategies.copy()}


class CentralityAnalyzer:
    """
    Analyzer that uses the Strategy pattern for centrality calculations.

    This class demonstrates how to use the StrategyManager for centrality analysis.
    """

    def __init__(self, strategy_manager: Optional[StrategyManager] = None):
        self.strategy_manager = strategy_manager or StrategyManager()

    def calculate_centrality(self, graph: nx.Graph, node_id: uuid.UUID,
                             strategy_name: str = "betweenness") -> float:
        """Calculate centrality for a node using the specified strategy."""
        strategy = self.strategy_manager.get_strategy(
            "centrality", strategy_name)
        if not strategy:
            raise ValueError(f"Unknown centrality strategy: {strategy_name}")

        return strategy.execute(graph, node_id)

    def calculate_all_centralities(
            self, graph: nx.Graph, strategy_name: str = "betweenness") -> Dict[uuid.UUID, float]:
        """Calculate centrality for all nodes using the specified strategy."""
        strategy = self.strategy_manager.get_strategy(
            "centrality", strategy_name)
        if not strategy:
            raise ValueError(f"Unknown centrality strategy: {strategy_name}")

        return strategy.execute(graph)

    def get_available_strategies(self) -> List[str]:
        """Get list of available centrality strategies."""
        return self.strategy_manager.list_strategies(
            "centrality").get("centrality", [])

    def compare_centralities(self,
                             graph: nx.Graph,
                             node_id: uuid.UUID,
                             strategies: Optional[List[str]] = None) -> Dict[str,
                                                                             Any]:
        """Compare centrality values using different strategies."""
        if strategies is None:
            strategies = self.get_available_strategies()

        results = {}
        for strategy_name in strategies:
            try:
                results[strategy_name] = self.calculate_centrality(
                    graph, node_id, strategy_name)
            except Exception as e:
                results[strategy_name] = f"Error: {str(e)}"  # type: ignore[assignment]

        return results
