"""
Abstract query layer for Social Fabric Matrix (SFM) analysis.
Provides high-level analytical queries with support for different graph storage backends.
Default implementation uses NetworkX for graph analysis.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
import uuid
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

import networkx as nx

from core.sfm_models import (
    Actor,
    Institution,
    Resource,
    Relationship,
    SFMGraph,
)
from core.sfm_enums import ResourceType, FlowNature, RelationshipKind
from core.patterns.strategy import StrategyManager, CentralityAnalyzer

# Public API
__all__ = [
    'AnalysisType',
    'QueryResult',
    'NodeMetrics',
    'FlowAnalysis',
    'SFMQueryEngine',
    'NetworkXSFMQueryEngine',
    'SFMQueryFactory',
]


class AnalysisType(Enum):
    """Types of SFM analysis supported."""

    CENTRALITY = "centrality"
    INFLUENCE = "influence"
    DEPENDENCY = "dependency"
    FLOW_ANALYSIS = "flow_analysis"
    NETWORK_STRUCTURE = "network_structure"
    POLICY_IMPACT = "policy_impact"
    SCENARIO_COMPARISON = "scenario_comparison"


@dataclass
class QueryResult:
    """Container for query results with metadata."""

    data: Any
    query_type: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str


@dataclass
class NodeMetrics:
    """Metrics for individual nodes in the SFM."""

    node_id: uuid.UUID
    centrality_scores: Dict[str, float]
    influence_score: float
    dependency_score: float
    connectivity: int
    node_type: str


@dataclass
class FlowAnalysis:
    """Analysis results for resource/value flows."""

    flow_paths: List[List[uuid.UUID]]
    bottlenecks: List[uuid.UUID]
    flow_volumes: Dict[uuid.UUID, float]
    efficiency_metrics: Dict[str, float]


class SFMQueryEngine(ABC):  # pylint: disable=too-many-public-methods
    """Abstract base class for SFM analytical queries."""

    def __init__(self, graph: SFMGraph):
        self.graph = graph

    # ─── NODE ANALYSIS ───

    @abstractmethod
    def get_node_centrality(
        self, node_id: uuid.UUID, centrality_type: str = "betweenness"
    ) -> float:
        """Calculate centrality measures for a node."""

    @abstractmethod
    def get_most_central_nodes(
        self,
        node_type: Optional[type] = None,
        centrality_type: str = "betweenness",
        limit: int = 10,
    ) -> List[Tuple[uuid.UUID, float]]:
        """Get the most central nodes by type."""

    @abstractmethod
    def get_node_neighbors(
        self,
        node_id: uuid.UUID,
        relationship_kinds: Optional[List[RelationshipKind]] = None,
        distance: int = 1,
    ) -> List[uuid.UUID]:
        """Get neighboring nodes within specified distance."""

    # ─── RELATIONSHIP ANALYSIS ───

    @abstractmethod
    def find_shortest_path(
        self,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        relationship_kinds: Optional[List[RelationshipKind]] = None,
    ) -> Optional[List[uuid.UUID]]:
        """Find shortest path between two nodes."""

    @abstractmethod
    def get_relationship_strength(
        self, source_id: uuid.UUID, target_id: uuid.UUID
    ) -> float:
        """Calculate aggregate relationship strength between nodes."""

    @abstractmethod
    def find_cycles(self, max_length: int = 10) -> List[List[uuid.UUID]]:
        """Find cycles in the graph (feedback loops)."""

    # ─── FLOW ANALYSIS ───

    @abstractmethod
    def trace_resource_flows(
        self,
        resource_type: ResourceType,
        source_actors: Optional[List[uuid.UUID]] = None,
    ) -> FlowAnalysis:
        """Trace flows of specific resource types through the network."""

    @abstractmethod
    def identify_bottlenecks(self, flow_type: FlowNature) -> List[uuid.UUID]:
        """Identify bottleneck nodes in flow networks."""

    @abstractmethod
    def calculate_flow_efficiency(
        self, source_id: uuid.UUID, target_id: uuid.UUID
    ) -> float:
        """Calculate efficiency of flows between nodes."""

    # ─── POLICY ANALYSIS ───

    @abstractmethod
    def analyze_policy_impact(
        self, policy_id: uuid.UUID, impact_radius: int = 3
    ) -> Dict[str, Any]:
        """Analyze the network impact of a policy intervention."""

    @abstractmethod
    def identify_policy_targets(self, policy_id: uuid.UUID) -> List[uuid.UUID]:
        """Identify nodes directly and indirectly affected by a policy."""

    @abstractmethod
    def compare_policy_scenarios(
        self, scenario_graphs: List[SFMGraph]
    ) -> Dict[str, Any]:
        """Compare multiple policy scenarios."""

    # ─── STRUCTURAL ANALYSIS ───

    @abstractmethod
    def get_network_density(self) -> float:
        """Calculate overall network density."""

    @abstractmethod
    def identify_communities(
        self, algorithm: str = "louvain"
    ) -> Dict[int, List[uuid.UUID]]:
        """Identify communities/clusters in the network."""

    @abstractmethod
    def get_structural_holes(self) -> List[uuid.UUID]:
        """Identify nodes that bridge structural holes."""

    # ─── COMPOSITE QUERIES ───

    @abstractmethod
    def comprehensive_node_analysis(self, node_id: uuid.UUID) -> NodeMetrics:
        """Comprehensive analysis of a single node."""

    @abstractmethod
    def system_vulnerability_analysis(self) -> Dict[str, Any]:
        """Analyze system-wide vulnerabilities and resilience."""

    # ═══════════════════════════════════════════════════════════════════════════
    # ENHANCED TEMPORAL ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════

    @abstractmethod
    def analyze_temporal_changes(
        self, time_slice_graphs: List[Tuple[datetime, SFMGraph]]
    ) -> Dict[str, Any]:
        """Analyze changes across multiple time slices of the graph."""

    @abstractmethod
    def detect_structural_changes(
        self, reference_graph: SFMGraph, comparison_graph: SFMGraph
    ) -> Dict[str, Any]:
        """Detect structural changes between two graph states."""

    # ═══════════════════════════════════════════════════════════════════════════
    # RISK ASSESSMENT AND VULNERABILITY ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════

    @abstractmethod
    def assess_network_vulnerabilities(self) -> Dict[str, Any]:
        """Comprehensive vulnerability assessment of the network."""

    @abstractmethod
    def simulate_node_failure_impact(
        self, node_ids: List[uuid.UUID], failure_mode: str = "cascade"
    ) -> Dict[str, Any]:
        """Simulate the impact of node failures on network connectivity."""

    # ═══════════════════════════════════════════════════════════════════════════
    # ADVANCED FLOW ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════

    @abstractmethod
    def analyze_flow_patterns(self,
                              flow_type: FlowNature,
                              time_window: Optional[Tuple[datetime,
                                                          datetime]] = None) -> Dict[str,
                                                                                     Any]:
        """Analyze patterns in resource or value flows."""

    @abstractmethod
    def identify_flow_inefficiencies(self) -> Dict[str, Any]:
        """Identify inefficiencies in flow patterns."""


class NetworkXSFMQueryEngine(
        SFMQueryEngine):  # pylint: disable=too-many-public-methods
    """NetworkX-based implementation of SFM query engine."""

    def __init__(self, graph: SFMGraph):
        super().__init__(graph)
        self.nx_graph = self._build_networkx_graph()
        self.strategy_manager = StrategyManager()
        self.centrality_analyzer = CentralityAnalyzer(self.strategy_manager)

    def _build_networkx_graph(self) -> nx.MultiDiGraph:
        """Convert SFMGraph to NetworkX graph for analysis."""
        # Create directed multigraph to handle multiple relationships
        nx_graph = nx.MultiDiGraph()

        # Add all nodes
        for node in self.graph:
            nx_graph.add_node(node.id, data=node, type=type(node).__name__)

        # Add all relationships as edges
        for rel in self.graph.relationships.values():
            nx_graph.add_edge(
                rel.source_id,
                rel.target_id,
                key=rel.id,
                data=rel,
                kind=rel.kind,
                weight=rel.weight or 1.0,
            )

        return nx_graph

    def get_node_centrality(
        self, node_id: uuid.UUID, centrality_type: str = "betweenness"
    ) -> float:
        """Calculate centrality measures for a node using strategy pattern."""
        return self.centrality_analyzer.calculate_centrality(
            self.nx_graph, node_id, centrality_type
        )

    def get_most_central_nodes(
        self,
        node_type: Optional[type] = None,
        centrality_type: str = "betweenness",
        limit: int = 10,
    ) -> List[Tuple[uuid.UUID, float]]:
        """Get the most central nodes by type using strategy pattern."""
        # Calculate centrality for all nodes using strategy
        all_centralities = self.centrality_analyzer.calculate_all_centralities(
            self.nx_graph, centrality_type
        )

        # Filter by node type if specified
        if node_type:
            filtered_centrality = {
                node_id: score
                for node_id, score in all_centralities.items()
                if isinstance(self.nx_graph.nodes[node_id]["data"], node_type)
            }
        else:
            filtered_centrality = all_centralities

        # Sort and return top nodes
        sorted_nodes = sorted(
            filtered_centrality.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_nodes[:limit]

    def _get_direct_neighbors(
        self, node_id: uuid.UUID, relationship_kinds: Optional[List[RelationshipKind]] = None
    ) -> List[uuid.UUID]:
        """Get direct neighbors of a node."""
        # Check if node exists in graph
        if node_id not in self.nx_graph.nodes():
            return []

        if relationship_kinds:
            neighbors = []
            for neighbor in self.nx_graph.neighbors(node_id):
                for edge_data in self.nx_graph[node_id][neighbor].values():
                    if edge_data.get("kind") in relationship_kinds:
                        neighbors.append(neighbor)
                        break
            return list(set(neighbors))
        return list(self.nx_graph.neighbors(node_id))

    def _get_multihop_neighbors_with_filter(
        self, node_id: uuid.UUID, relationship_kinds: List[RelationshipKind], distance: int
    ) -> List[uuid.UUID]:
        """Get multi-hop neighbors with relationship kind filtering."""
        # Check if node exists in graph
        if node_id not in self.nx_graph.nodes():
            return []

        # Create subgraph with only desired relationship types
        edges_to_keep = []
        for u, v, key, data in self.nx_graph.edges(keys=True, data=True):
            if data.get("kind") in relationship_kinds:
                edges_to_keep.append((u, v, key))

        subgraph = self.nx_graph.edge_subgraph(edges_to_keep)
        try:
            neighbors = set()
            for target in subgraph.nodes():
                if target != node_id:
                    try:
                        path_length = nx.shortest_path_length(
                            subgraph, node_id, target)
                        if path_length <= distance:
                            neighbors.add(target)
                    except (nx.NetworkXNoPath, nx.NodeNotFound):
                        continue
            return list(neighbors)
        except (nx.NetworkXError, nx.NodeNotFound):
            return []

    def _get_multihop_neighbors_all(self,
                                    node_id: uuid.UUID,
                                    distance: int) -> List[uuid.UUID]:
        """Get multi-hop neighbors for all relationship types."""
        try:
            # Check if node exists in graph
            if node_id not in self.nx_graph.nodes():
                return []

            ego_graph = nx.ego_graph(self.nx_graph, node_id, radius=distance)
            return [n for n in ego_graph.nodes() if n != node_id]
        except (nx.NetworkXError, nx.NodeNotFound):
            return []

    def get_node_neighbors(
        self,
        node_id: uuid.UUID,
        relationship_kinds: Optional[List[RelationshipKind]] = None,
        distance: int = 1,
    ) -> List[uuid.UUID]:
        """Get neighboring nodes within specified distance."""
        if distance == 1:
            return self._get_direct_neighbors(node_id, relationship_kinds)

        # Multi-hop neighbors
        if relationship_kinds:
            return self._get_multihop_neighbors_with_filter(
                node_id, relationship_kinds, distance)
        return self._get_multihop_neighbors_all(node_id, distance)

    def find_shortest_path(
        self,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        relationship_kinds: Optional[List[RelationshipKind]] = None,
    ) -> Optional[List[uuid.UUID]]:
        """Find shortest path between two nodes."""
        try:
            # Check if both nodes exist in graph
            if source_id not in self.nx_graph.nodes() or target_id not in self.nx_graph.nodes():
                return None

            if relationship_kinds:
                # Create subgraph with only desired relationship types
                edges_to_keep = []
                for u, v, key, data in self.nx_graph.edges(
                        keys=True, data=True):
                    if data.get("kind") in relationship_kinds:
                        edges_to_keep.append((u, v, key))

                subgraph = self.nx_graph.edge_subgraph(edges_to_keep)
                path = nx.shortest_path(subgraph, source_id, target_id)
                return path if isinstance(path, list) else None

            path = nx.shortest_path(self.nx_graph, source_id, target_id)
            return path if isinstance(path, list) else None
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def get_relationship_strength(
        self, source_id: uuid.UUID, target_id: uuid.UUID
    ) -> float:
        """Calculate aggregate relationship strength between nodes."""
        if not self.nx_graph.has_edge(source_id, target_id):
            return 0.0

        total_weight = 0.0
        edge_count = 0

        for edge_data in self.nx_graph[source_id][target_id].values():
            weight = edge_data.get("weight", 1.0)
            total_weight += weight
            edge_count += 1

        return total_weight / edge_count if edge_count > 0 else 0.0

    def find_cycles(self, max_length: int = 10) -> List[List[uuid.UUID]]:
        """Find cycles in the graph (feedback loops)."""
        try:
            cycles = []
            # Find simple cycles up to max_length
            for cycle in nx.simple_cycles(self.nx_graph):
                if len(cycle) <= max_length:
                    cycles.append(cycle)
            return cycles
        except nx.NetworkXError:
            return []

    def trace_resource_flows(
        self,
        resource_type: ResourceType,
        source_actors: Optional[List[uuid.UUID]] = None,
    ) -> FlowAnalysis:
        """Trace flows of specific resource types through the network."""
        # This is a simplified implementation - would need more sophisticated
        # flow analysis
        flow_paths: List[List[uuid.UUID]] = []
        bottlenecks: List[uuid.UUID] = []
        flow_volumes: Dict[uuid.UUID, float] = {}

        # Find resource nodes of the specified type
        resource_nodes = [
            node_id
            for node_id, node_data in self.nx_graph.nodes(data=True)
            if (
                isinstance(node_data["data"], Resource)
                and node_data["data"].rtype == resource_type
            )
        ]

        # Trace flows from resource nodes
        for resource_id in resource_nodes:
            # Find flows connected to this resource
            for neighbor in self.nx_graph.neighbors(resource_id):
                for edge_data in self.nx_graph[resource_id][neighbor].values():
                    if isinstance(edge_data["data"], Relationship):
                        rel = edge_data["data"]
                        if rel.kind in [
                            RelationshipKind.PRODUCES,
                            RelationshipKind.USES,
                            RelationshipKind.EXCHANGES_WITH,
                        ]:
                            flow_volumes[rel.id] = rel.weight or 1.0

        return FlowAnalysis(
            flow_paths=flow_paths,
            bottlenecks=bottlenecks,
            flow_volumes=flow_volumes,
            efficiency_metrics={},
        )

    def identify_bottlenecks(self, flow_type: FlowNature) -> List[uuid.UUID]:
        """Identify bottleneck nodes in flow networks."""
        # Handle empty or single-node graphs
        if self.nx_graph.number_of_nodes() <= 1:
            return []

        # Use betweenness centrality as a proxy for bottlenecks
        centrality = nx.betweenness_centrality(self.nx_graph)

        # Handle case where no centrality values exist
        if not centrality:
            return []

        # Get top 10% of nodes by centrality
        threshold = sorted(centrality.values())[-max(1, len(centrality) // 10)]
        bottlenecks = [
            node_id for node_id,
            score in centrality.items() if score >= threshold]

        return bottlenecks

    def calculate_flow_efficiency(
        self, source_id: uuid.UUID, target_id: uuid.UUID
    ) -> float:
        """Calculate efficiency of flows between nodes."""
        try:
            path = self.find_shortest_path(source_id, target_id)

            # Handle cases where no path exists or path is too short
            if not path or len(path) <= 1:
                return 0.0

            shortest_path_length = len(path) - 1

            # Double-check for zero or negative path length
            if shortest_path_length <= 0:
                return 0.0

            # Simple efficiency metric: inverse of path length
            # Explicit ZeroDivisionError protection for Python 3.8
            # compatibility
            try:
                return 1.0 / shortest_path_length
            except ZeroDivisionError:
                return 0.0

        except (nx.NetworkXError, TypeError):
            return 0.0

    def analyze_policy_impact(
        self, policy_id: uuid.UUID, impact_radius: int = 3
    ) -> Dict[str, Any]:
        """Analyze the network impact of a policy intervention."""
        # Check if policy node exists in graph
        if policy_id not in self.nx_graph.nodes():
            return {"error": "Policy node not found in graph"}

        # Get nodes within impact radius
        try:
            ego_graph = nx.ego_graph(
                self.nx_graph, policy_id, radius=impact_radius)
            affected_nodes = list(ego_graph.nodes())

            # Categorize affected nodes by type
            impact_analysis: Dict[str, Any] = {
                "total_affected_nodes": len(affected_nodes)
                - 1,  # Exclude policy node itself
                "affected_actors": [],
                "affected_institutions": [],
                "affected_resources": [],
                "network_metrics": {
                    "density": nx.density(ego_graph),
                    "centrality": nx.betweenness_centrality(ego_graph).get(
                        policy_id, 0.0
                    ),
                },
            }

            for node_id in affected_nodes:
                if node_id == policy_id:
                    continue

                node_data = self.nx_graph.nodes[node_id]["data"]
                if isinstance(node_data, Actor):
                    impact_analysis["affected_actors"].append(node_id)
                elif isinstance(node_data, Institution):
                    impact_analysis["affected_institutions"].append(node_id)
                elif isinstance(node_data, Resource):
                    impact_analysis["affected_resources"].append(node_id)

            return impact_analysis

        except nx.NetworkXError:
            return {"error": "Policy node not found or network error"}

    def identify_policy_targets(self, policy_id: uuid.UUID) -> List[uuid.UUID]:
        """Identify nodes directly and indirectly affected by a policy."""
        targets = []

        # Direct targets (immediate neighbors)
        direct_targets = self.get_node_neighbors(policy_id, distance=1)
        targets.extend(direct_targets)

        # Indirect targets (2-hop neighbors)
        indirect_targets = self.get_node_neighbors(policy_id, distance=2)
        targets.extend(
            [t for t in indirect_targets if t not in direct_targets])

        return list(set(targets))

    def compare_policy_scenarios(
        self, scenario_graphs: List[SFMGraph]
    ) -> Dict[str, Any]:
        """Compare multiple policy scenarios."""
        if len(scenario_graphs) < 2:
            return {"error": "Need at least 2 scenarios for comparison"}

        comparison = {
            "scenario_count": len(scenario_graphs),
            "basic_metrics": {
                "node_counts": [],
                "relationship_counts": [],
                "density_scores": []
            },
            "structural_comparison": {},
            "policy_impact_analysis": {},
            "similarity_matrix": [],
            "key_differences": []
        }

        # Build NetworkX graphs for each scenario
        scenario_nx_graphs = []
        for graph in scenario_graphs:
            nx_graph = self._build_networkx_from_graph(graph)
            scenario_nx_graphs.append(nx_graph)

        # Basic metrics comparison
        for nx_graph in scenario_nx_graphs:
            comparison["basic_metrics"]["node_counts"].append(
                nx_graph.number_of_nodes())
            comparison["basic_metrics"]["relationship_counts"].append(
                nx_graph.number_of_edges())
            comparison["basic_metrics"]["density_scores"].append(
                nx.density(nx_graph) if nx_graph.number_of_nodes() > 0 else 0.0
            )

        # Structural comparison between scenarios
        comparison["structural_comparison"] = self._compare_scenario_structures(
            scenario_nx_graphs)

        # Policy impact analysis (if policy nodes exist)
        comparison["policy_impact_analysis"] = self._analyze_scenario_policy_impacts(
            scenario_graphs)

        # Calculate similarity matrix between scenarios
        comparison["similarity_matrix"] = self._calculate_scenario_similarity_matrix(
            scenario_nx_graphs)

        # Identify key differences
        comparison["key_differences"] = self._identify_key_scenario_differences(
            scenario_nx_graphs)

        return comparison

    def get_network_density(self) -> float:
        """Calculate overall network density."""
        return nx.density(self.nx_graph)

    def identify_communities(
        self, algorithm: str = "louvain"
    ) -> Dict[int, List[uuid.UUID]]:
        """Identify communities/clusters in the network."""
        if self.nx_graph.number_of_nodes() == 0:
            return {}

        try:
            # Convert to undirected graph for community detection
            undirected_graph = self.nx_graph.to_undirected()

            if algorithm.lower() == "louvain":
                # Use Louvain algorithm for community detection
                communities = nx.algorithms.community.louvain_communities(
                    undirected_graph
                )
            elif algorithm.lower() == "label_propagation":
                # Use label propagation algorithm
                communities = nx.algorithms.community.label_propagation_communities(
                    undirected_graph)
            elif algorithm.lower() == "greedy_modularity":
                # Use greedy modularity maximization
                communities = nx.algorithms.community.greedy_modularity_communities(
                    undirected_graph)
            else:
                # Default to Louvain if unknown algorithm specified
                communities = nx.algorithms.community.louvain_communities(
                    undirected_graph
                )

            # Convert to the expected format: Dict[int, List[uuid.UUID]]
            community_dict = {}
            for i, community in enumerate(communities):
                community_dict[i] = list(community)

            return community_dict

        except (nx.NetworkXError, AttributeError):
            # Fallback to single community containing all nodes
            return {0: list(self.nx_graph.nodes())}

    def get_structural_holes(self) -> List[uuid.UUID]:
        """Identify nodes that bridge structural holes."""
        # Handle empty or single-node graphs
        if self.nx_graph.number_of_nodes() <= 1:
            return []

        # Use betweenness centrality as a proxy for structural holes
        centrality = nx.betweenness_centrality(self.nx_graph)

        # Handle case where no centrality values exist
        if not centrality:
            return []

        # Nodes with high betweenness centrality often bridge structural holes
        threshold = sorted(centrality.values())[
            -max(1, len(centrality) // 20)
        ]  # Top 5%
        structural_bridges = [
            node_id for node_id,
            score in centrality.items() if score >= threshold]

        return structural_bridges

    def comprehensive_node_analysis(self, node_id: uuid.UUID) -> NodeMetrics:
        """Comprehensive analysis of a single node."""
        # Check if node exists in graph
        if node_id not in self.nx_graph.nodes():
            return NodeMetrics(
                node_id=node_id,
                centrality_scores={
                    "betweenness": 0.0,
                    "closeness": 0.0,
                    "degree": 0.0},
                influence_score=0.0,
                dependency_score=0.0,
                connectivity=0,
                node_type="Unknown")

        centrality_scores = {
            "betweenness": self.get_node_centrality(node_id, "betweenness"),
            "closeness": self.get_node_centrality(node_id, "closeness"),
            "degree": self.get_node_centrality(node_id, "degree"),
        }

        # Calculate influence and dependency scores
        neighbors = self.get_node_neighbors(node_id)
        influence_score = len(
            [n for n in neighbors if self.nx_graph.has_edge(node_id, n)]
        )
        dependency_score = len(
            [n for n in neighbors if self.nx_graph.has_edge(n, node_id)]
        )

        return NodeMetrics(
            node_id=node_id,
            centrality_scores=centrality_scores,
            influence_score=influence_score /
            len(neighbors) if neighbors else 0.0,
            dependency_score=dependency_score /
            len(neighbors) if neighbors else 0.0,
            connectivity=len(neighbors),
            node_type=type(
                self.nx_graph.nodes[node_id]["data"]).__name__,
        )

    def system_vulnerability_analysis(self) -> Dict[str, Any]:
        """Analyze system-wide vulnerabilities and resilience."""
        # Convert multigraph to simple graph for clustering analysis
        simple_graph = nx.Graph(self.nx_graph.to_undirected())

        # Calculate various network resilience metrics
        analysis = {
            "network_density": self.get_network_density(),
            "average_clustering": (nx.average_clustering(simple_graph)
                                   if simple_graph.number_of_nodes() > 0 else 0.0),
            "number_of_components": nx.number_weakly_connected_components(
                self.nx_graph
            ),
            "critical_nodes": self.get_structural_holes(),
            "bottlenecks": self.identify_bottlenecks(FlowNature.TRANSFER),
        }

        return analysis

    def analyze_temporal_changes(
        self, time_slice_graphs: List[Tuple[datetime, SFMGraph]]
    ) -> Dict[str, Any]:
        """Analyze changes across multiple time slices of the graph."""
        if len(time_slice_graphs) < 2:
            return {"error": "Need at least 2 time slices for temporal analysis"}

        analysis: Dict[str, Any] = {
            "time_periods": len(time_slice_graphs),
            "node_evolution": {},
            "relationship_evolution": {},
            "structural_changes": {},
            "growth_metrics": {}
        }

        # Track node changes
        for i in range(1, len(time_slice_graphs)):
            prev_time, prev_graph = time_slice_graphs[i - 1]
            curr_time, curr_graph = time_slice_graphs[i]

            prev_nodes = set(node.id for node in prev_graph)
            curr_nodes = set(node.id for node in curr_graph)

            added_nodes = curr_nodes - prev_nodes
            removed_nodes = prev_nodes - curr_nodes

            period_key = f"{prev_time.isoformat()}_{curr_time.isoformat()}"
            analysis["node_evolution"][period_key] = {
                "added": len(added_nodes),
                "removed": len(removed_nodes),
                "stable": len(prev_nodes & curr_nodes)
            }

        return analysis

    def detect_structural_changes(
        self, reference_graph: SFMGraph, comparison_graph: SFMGraph
    ) -> Dict[str, Any]:
        """Detect structural changes between two graph states."""
        # Build NetworkX graphs for comparison
        ref_nx = self._build_networkx_from_graph(reference_graph)
        comp_nx = self._build_networkx_from_graph(comparison_graph)

        changes = {
            "density_change": nx.density(comp_nx) -
            nx.density(ref_nx),
            "node_count_change": comp_nx.number_of_nodes() -
            ref_nx.number_of_nodes(),
            "edge_count_change": comp_nx.number_of_edges() -
            ref_nx.number_of_edges(),
            "centrality_shifts": {},
            "new_communities": [],
            "disbanded_communities": []}

        # Analyze centrality shifts for common nodes
        common_nodes = set(ref_nx.nodes()) & set(comp_nx.nodes())
        if common_nodes:
            ref_centrality = nx.betweenness_centrality(ref_nx)
            comp_centrality = nx.betweenness_centrality(comp_nx)

            for node in common_nodes:
                shift = comp_centrality.get(
                    node, 0) - ref_centrality.get(node, 0)
                if abs(shift) > 0.1:  # Significant shift threshold
                    changes["centrality_shifts"][str(node)] = shift

        return changes

    def assess_network_vulnerabilities(self) -> Dict[str, Any]:
        """Comprehensive vulnerability assessment of the network."""
        vulnerabilities: Dict[str, Any] = {
            "critical_nodes": [],
            "single_points_of_failure": [],
            "fragmentation_risk": 0.0,
            "cascade_failure_risk": 0.0,
            "resilience_score": 0.0,
            "mitigation_recommendations": []
        }

        # Identify critical nodes (high betweenness centrality)
        centrality = nx.betweenness_centrality(self.nx_graph)
        critical_threshold = sorted(
            centrality.values())[-max(1, len(centrality) // 20)]
        vulnerabilities["critical_nodes"] = [
            {"node_id": str(node_id), "centrality": score}
            for node_id, score in centrality.items()
            if score >= critical_threshold
        ]

        # Find single points of failure (articulation points)
        if not self.nx_graph.is_directed():
            simple_graph = self.nx_graph
        else:
            simple_graph = self.nx_graph.to_undirected()

        articulation_points = list(nx.articulation_points(simple_graph))
        vulnerabilities["single_points_of_failure"] = [
            str(node) for node in articulation_points
        ]

        # Calculate fragmentation risk
        if len(articulation_points) > 0:
            vulnerabilities["fragmentation_risk"] = (
                len(articulation_points) / len(self.nx_graph.nodes())
            )

        # Calculate resilience score
        connectivity = (nx.node_connectivity(simple_graph)
                        if simple_graph.number_of_nodes() > 1 else 0)
        density = nx.density(self.nx_graph)
        vulnerabilities["resilience_score"] = (connectivity + density) / 2

        # Generate mitigation recommendations
        if vulnerabilities["fragmentation_risk"] > 0.1:
            vulnerabilities["mitigation_recommendations"].append(
                "High fragmentation risk detected. Consider adding redundant connections."
            )
        if len(
                vulnerabilities["critical_nodes"]) > len(
                self.nx_graph.nodes()) * 0.2:
            vulnerabilities["mitigation_recommendations"].append(
                "Many critical nodes detected. Consider distributing centrality more evenly."
            )

        return vulnerabilities

    def _calculate_connectivity_impact(self,
                                       sim_graph: nx.Graph,
                                       original_components: int,
                                       original_largest: int) -> Dict[str,
                                                                      Any]:
        """Calculate connectivity impact metrics."""
        new_components = nx.number_weakly_connected_components(sim_graph)
        if sim_graph.number_of_nodes() > 0:
            new_largest = len(
                max(nx.weakly_connected_components(sim_graph), key=len))
        else:
            new_largest = 0

        return {
            "original_components": original_components,
            "new_components": new_components,
            "component_increase": new_components - original_components,
            "largest_component_size_change": new_largest - original_largest,
            "connectivity_loss_percentage": (
                (original_largest - new_largest) / original_largest * 100
                if original_largest > 0 else 0
            )
        }

    def _simulate_cascade_failures(self, sim_graph: nx.Graph) -> List[Any]:
        """Simulate cascading node failures."""
        cascade_nodes = []
        # Simple cascade model: remove nodes that lose significant connections
        for node in list(sim_graph.nodes()):
            sim_node_degree = len(list(sim_graph.neighbors(node)))
            orig_node_degree = len(list(self.nx_graph.neighbors(node)))
            if sim_node_degree < orig_node_degree * 0.3:  # Lost 70% of connections
                cascade_nodes.append(node)
                sim_graph.remove_node(node)
        return cascade_nodes

    def simulate_node_failure_impact(
        self, node_ids: List[uuid.UUID], failure_mode: str = "cascade"
    ) -> Dict[str, Any]:
        """Simulate the impact of node failures on network connectivity."""
        original_components = nx.number_weakly_connected_components(
            self.nx_graph)
        original_largest = len(
            max(nx.weakly_connected_components(self.nx_graph), key=len))

        # Create a copy of the graph for simulation
        sim_graph = self.nx_graph.copy()

        impact_results = {
            "failed_nodes": [str(nid) for nid in node_ids],
            "failure_mode": failure_mode,
            "connectivity_impact": {},
            "isolated_nodes": [],
            "affected_components": 0,
            "cascading_failures": []
        }

        # Remove the failed nodes
        sim_graph.remove_nodes_from(node_ids)

        # Analyze impact
        impact_results["connectivity_impact"] = self._calculate_connectivity_impact(
            sim_graph, original_components, original_largest)

        # Identify newly isolated nodes
        isolated = [node for node in sim_graph.nodes()
                    if len(list(sim_graph.neighbors(node))) == 0]
        impact_results["isolated_nodes"] = [str(node) for node in isolated]

        # Simulate cascading failures if requested
        if failure_mode == "cascade":
            cascade_nodes = self._simulate_cascade_failures(sim_graph)
            impact_results["cascading_failures"] = [
                str(node) for node in cascade_nodes]

        return impact_results

    def _get_relevant_flows(
            self, flow_type: FlowNature) -> List[Tuple[Any, Any, Dict[str, Any]]]:
        """Get flows of the specified type."""
        relevant_flows = []
        for rel in self.nx_graph.edges(data=True):
            edge_data = rel[2]
            if hasattr(edge_data.get("data"), "flow_nature"):
                if edge_data["data"].flow_nature == flow_type:
                    relevant_flows.append(rel)
        return relevant_flows

    def _analyze_flow_distribution(
            self, relevant_flows: List[Tuple[Any, Any, Dict[str, Any]]]) -> Dict[str, int]:
        """Analyze flow distribution by node type."""
        node_flow_counts: Dict[str, int] = {}
        for source, target, _ in relevant_flows:  # Use _ for unused variable
            source_type = type(self.nx_graph.nodes[source]["data"]).__name__
            target_type = type(self.nx_graph.nodes[target]["data"]).__name__

            flow_key = f"{source_type} -> {target_type}"
            node_flow_counts[flow_key] = node_flow_counts.get(flow_key, 0) + 1
        return node_flow_counts

    def _identify_major_pathways(self,
                                 relevant_flows: List[Tuple[Any,
                                                            Any,
                                                            Dict[str,
                                                                 Any]]]) -> List[Tuple[str,
                                                                                       float]]:
        """Identify major flow pathways (high-volume routes)."""
        pathway_volumes: Dict[str, float] = {}
        for source, target, data in relevant_flows:
            pathway_key = f"{source} -> {target}"
            volume = data.get("weight", 1.0)
            pathway_volumes[pathway_key] = pathway_volumes.get(
                pathway_key, 0) + volume

        # Sort and get top pathways
        sorted_pathways = sorted(
            pathway_volumes.items(),
            key=lambda x: x[1],
            reverse=True)
        return sorted_pathways[:10]  # Top 10 pathways

    def analyze_flow_patterns(self,
                              flow_type: FlowNature,
                              time_window: Optional[Tuple[datetime,
                                                          datetime]] = None) -> Dict[str,
                                                                                     Any]:
        """Analyze patterns in resource or value flows."""
        flow_analysis = {
            "flow_type": flow_type.value,
            "total_flows": 0,
            "flow_distribution": {},
            "major_pathways": [],
            "flow_concentrations": [],
            "temporal_patterns": {}
        }

        # Get flows of the specified type
        relevant_flows = self._get_relevant_flows(flow_type)
        flow_analysis["total_flows"] = len(relevant_flows)

        # Analyze flow distribution by node type
        flow_analysis["flow_distribution"] = self._analyze_flow_distribution(
            relevant_flows)

        # Identify major flow pathways
        flow_analysis["major_pathways"] = self._identify_major_pathways(
            relevant_flows)

        return flow_analysis

    def identify_flow_inefficiencies(self) -> Dict[str, Any]:
        """Identify inefficiencies in flow patterns."""
        inefficiencies: Dict[str, Any] = {
            "redundant_paths": [],
            "flow_imbalances": [],
            "underutilized_connections": [],
            "optimization_opportunities": []
        }

        # Find redundant paths (multiple paths with similar flows)
        node_pairs_with_multiple_paths = []
        for source in self.nx_graph.nodes():
            for target in self.nx_graph.nodes():
                if source != target:
                    try:
                        paths = list(nx.all_simple_paths(
                            self.nx_graph, source, target, cutoff=3
                        ))
                        if len(paths) > 1:
                            node_pairs_with_multiple_paths.append(
                                (source, target, len(paths))
                            )
                    except nx.NetworkXNoPath:
                        continue

        inefficiencies["redundant_paths"] = [
            {"source": str(s), "target": str(t), "path_count": count}
            for s, t, count in node_pairs_with_multiple_paths[:10]  # Top 10
        ]

        # Identify flow imbalances (nodes with very high in-degree vs
        # out-degree)
        for node in self.nx_graph.nodes():
            in_degree = len(list(self.nx_graph.predecessors(node)))
            out_degree = len(list(self.nx_graph.successors(node)))

            if in_degree > 0 and out_degree > 0:
                imbalance_ratio = abs(
                    in_degree - out_degree) / max(in_degree, out_degree)
                if imbalance_ratio > 0.7:  # High imbalance threshold
                    inefficiencies["flow_imbalances"].append({
                        "node": str(node),
                        "in_degree": in_degree,
                        "out_degree": out_degree,
                        "imbalance_ratio": imbalance_ratio
                    })

        return inefficiencies

    def _build_networkx_from_graph(
            self, sfm_graph: SFMGraph) -> nx.MultiDiGraph:
        """Helper method to build NetworkX graph from SFMGraph."""
        nx_graph = nx.MultiDiGraph()

        # Add nodes
        for node in sfm_graph:
            nx_graph.add_node(node.id, data=node, type=type(node).__name__)

        # Add relationships as edges
        for rel in sfm_graph.relationships.values():
            nx_graph.add_edge(
                rel.source_id,
                rel.target_id,
                key=rel.id,
                data=rel,
                kind=rel.kind,
                weight=rel.weight or 1.0,
            )

        return nx_graph

    def _compare_scenario_structures(
            self, scenario_graphs: List[nx.MultiDiGraph]) -> Dict[str, Any]:
        """Compare structural properties across scenarios."""
        structural_metrics = {
            "centrality_differences": [],
            "clustering_differences": [],
            "connectivity_differences": []
        }

        if len(scenario_graphs) < 2:
            return structural_metrics

        # Compare centrality measures
        base_centrality = nx.betweenness_centrality(scenario_graphs[0])
        for i, graph in enumerate(scenario_graphs[1:], 1):
            current_centrality = nx.betweenness_centrality(graph)

            # Find common nodes
            common_nodes = set(
                base_centrality.keys()) & set(
                current_centrality.keys())
            if common_nodes:
                centrality_diff = sum(
                    abs(current_centrality.get(node, 0) - base_centrality.get(node, 0))
                    for node in common_nodes
                ) / len(common_nodes)
                structural_metrics["centrality_differences"].append({
                    "scenario_pair": f"0_vs_{i}",
                    "avg_centrality_difference": centrality_diff
                })

        # Compare clustering coefficients
        for i, graph in enumerate(scenario_graphs):
            try:
                simple_graph = nx.Graph(graph.to_undirected())
                clustering = nx.average_clustering(
                    simple_graph) if simple_graph.number_of_nodes() > 0 else 0.0
                structural_metrics["clustering_differences"].append({
                    "scenario": i,
                    "clustering_coefficient": clustering
                })
            except nx.NetworkXError:
                structural_metrics["clustering_differences"].append({
                    "scenario": i,
                    "clustering_coefficient": 0.0
                })

        return structural_metrics

    def _analyze_scenario_policy_impacts(
            self, scenario_graphs: List[SFMGraph]) -> Dict[str, Any]:
        """Analyze policy impact differences across scenarios."""
        policy_analysis = {
            "policy_nodes_per_scenario": [],
            "impact_radius_comparison": [],
            "policy_target_overlap": []
        }

        # Import Policy here to avoid circular import
        from core.sfm_models import Policy

        for i, graph in enumerate(scenario_graphs):
            # Count policy nodes in each scenario
            policy_count = sum(1 for node in graph if isinstance(node, Policy))
            policy_analysis["policy_nodes_per_scenario"].append({
                "scenario": i,
                "policy_count": policy_count
            })

        return policy_analysis

    def _calculate_scenario_similarity_matrix(
            self, scenario_graphs: List[nx.MultiDiGraph]) -> List[List[float]]:
        """Calculate similarity matrix between all scenario pairs."""
        n_scenarios = len(scenario_graphs)
        similarity_matrix = [
            [0.0 for _ in range(n_scenarios)] for _ in range(n_scenarios)]

        for i in range(n_scenarios):
            for j in range(n_scenarios):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    # Calculate Jaccard similarity based on node overlap
                    nodes_i = set(scenario_graphs[i].nodes())
                    nodes_j = set(scenario_graphs[j].nodes())

                    if len(nodes_i) == 0 and len(nodes_j) == 0:
                        similarity_matrix[i][j] = 1.0
                    elif len(nodes_i) == 0 or len(nodes_j) == 0:
                        similarity_matrix[i][j] = 0.0
                    else:
                        intersection = len(nodes_i & nodes_j)
                        union = len(nodes_i | nodes_j)
                        similarity_matrix[i][j] = intersection / \
                            union if union > 0 else 0.0

        return similarity_matrix

    def _identify_key_scenario_differences(
            self, scenario_graphs: List[nx.MultiDiGraph]) -> List[Dict[str, Any]]:
        """Identify key structural differences between scenarios."""
        differences = []

        if len(scenario_graphs) < 2:
            return differences

        base_graph = scenario_graphs[0]
        base_nodes = set(base_graph.nodes())
        base_edges = set(base_graph.edges())

        for i, graph in enumerate(scenario_graphs[1:], 1):
            current_nodes = set(graph.nodes())
            current_edges = set(graph.edges())

            # Node differences
            added_nodes = current_nodes - base_nodes
            removed_nodes = base_nodes - current_nodes

            # Edge differences
            added_edges = current_edges - base_edges
            removed_edges = base_edges - current_edges

            differences.append({
                "comparison": f"scenario_0_vs_scenario_{i}",
                "nodes_added": len(added_nodes),
                "nodes_removed": len(removed_nodes),
                "edges_added": len(added_edges),
                "edges_removed": len(removed_edges),
                "structural_change_magnitude": (
                    len(added_nodes) + len(removed_nodes) + len(added_edges) + len(removed_edges)
                ) / max(1, len(base_nodes) + len(base_edges))
            })

        return differences


class SFMQueryFactory:
    """Factory for creating SFM query engines."""

    @staticmethod
    def create_query_engine(
        graph: SFMGraph, backend: str = "networkx"
    ) -> SFMQueryEngine:
        """Create a query engine for the specified backend."""
        if backend.lower() == "networkx":
            return NetworkXSFMQueryEngine(graph)

        raise ValueError(f"Unsupported backend: {backend}")
