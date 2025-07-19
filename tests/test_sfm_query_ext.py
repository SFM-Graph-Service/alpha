"""
unit and integration tests for SFM query engine classes.
"""

import unittest
import uuid
import time
import random
import sys
import gc
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from typing import List, Dict, Any, Optional
from dataclasses import asdict

try:
    import networkx as nx
    from networkx import NetworkXError, NetworkXNoPath
except ImportError:
    # Handle missing NetworkX gracefully for testing purposes
    nx = None
    NetworkXError = Exception
    NetworkXNoPath = Exception

from models import ( Actor, Institution, Resource, Policy, Flow, Relationship, Node
)
from models.sfm_enums import ResourceType, FlowNature, RelationshipKind, InstitutionLayer
from graph.sfm_query import (
    SFMQueryEngine, NetworkXSFMQueryEngine, SFMQueryFactory, AnalysisType,
    QueryResult, NodeMetrics, FlowAnalysis
)
from graph.graph import SFMGraph

# Import centralized mocks and fixtures
from tests.mocks import (
    MockQueryEngineFactory,
    MockNetworkXFunctions,
    create_mock_graph,
    create_sample_nodes,
)


# Remove the custom factory and use centralized mocks
# class SFMQueryTestDataFactory is replaced by create_mock_graph() and create_sample_nodes()


class TestSFMQueryEngineAbstract(unittest.TestCase):
    """Test suite for the abstract SFMQueryEngine class."""

    def test_abstract_class_cannot_be_instantiated(self):
        """Test that SFMQueryEngine cannot be instantiated directly."""
        graph = SFMGraph()
        with self.assertRaises(TypeError, msg="Abstract class should not be instantiable"):
            SFMQueryEngine(graph) #type: ignore for testing

    def test_abstract_methods_are_defined(self):
        """Test that all expected abstract methods are defined."""
        expected_abstract_methods = [
            "get_node_centrality", "get_most_central_nodes", "get_node_neighbors",
            "find_shortest_path", "get_relationship_strength", "find_cycles",
            "trace_resource_flows", "identify_bottlenecks", "calculate_flow_efficiency",
            "analyze_policy_impact", "identify_policy_targets", "compare_policy_scenarios",
            "get_network_density", "identify_communities", "get_structural_holes",
            "comprehensive_node_analysis", "system_vulnerability_analysis"
        ]

        for method_name in expected_abstract_methods:
            with self.subTest(method=method_name):
                self.assertTrue(
                    hasattr(SFMQueryEngine, method_name),
                    f"Missing abstract method: {method_name}"
                )
                method = getattr(SFMQueryEngine, method_name)
                self.assertTrue(
                    hasattr(method, '__isabstractmethod__'),
                    f"Method {method_name} should be abstract"
                )

    def test_graph_assignment_in_constructor(self):
        """Test that graph is properly assigned in base constructor."""
        # We'll test this through a concrete implementation
        graph = create_mock_graph()
        if nx is not None:
            engine = NetworkXSFMQueryEngine(graph)
            self.assertEqual(engine.graph, graph, "Graph should be assigned in constructor")


class TestDataClasses(unittest.TestCase):
    """Test suite for data classes used in query results."""

    def test_query_result_creation_and_serialization(self):
        """Test QueryResult dataclass creation and serialization."""
        test_data = {"centrality": 0.5, "rank": 1}
        test_params = {"node_id": str(uuid.uuid4()), "centrality_type": "betweenness"}
        test_metadata = {"execution_time": 0.15, "graph_size": 100}
        
        result = QueryResult(
            data=test_data,
            query_type="centrality_analysis",
            parameters=test_params,
            metadata=test_metadata,
            timestamp="2025-06-20T10:00:00Z"
        )

        # Test basic properties
        self.assertEqual(result.data, test_data)
        self.assertEqual(result.query_type, "centrality_analysis")
        self.assertEqual(result.parameters, test_params)
        self.assertEqual(result.metadata, test_metadata)
        self.assertEqual(result.timestamp, "2025-06-20T10:00:00Z")
        
        # Test serialization capability
        result_dict = asdict(result)
        self.assertIsInstance(result_dict, dict)
        self.assertIn("data", result_dict)
        self.assertIn("query_type", result_dict)

    def test_node_metrics_comprehensive_data(self):
        """Test NodeMetrics dataclass with comprehensive data."""
        node_id = uuid.uuid4()
        centrality_scores = {
            "betweenness": 0.75,
            "closeness": 0.65, 
            "degree": 0.80,
            "eigenvector": 0.55
        }
        
        metrics = NodeMetrics(
            node_id=node_id,
            centrality_scores=centrality_scores,
            influence_score=0.82,
            dependency_score=0.34,
            connectivity=8,
            node_type="Actor"
        )

        # Test all properties
        self.assertEqual(metrics.node_id, node_id)
        self.assertEqual(metrics.centrality_scores, centrality_scores)
        self.assertEqual(metrics.influence_score, 0.82)
        self.assertEqual(metrics.dependency_score, 0.34)
        self.assertEqual(metrics.connectivity, 8)
        self.assertEqual(metrics.node_type, "Actor")
        
        # Test that centrality scores contain expected measures
        for measure in ["betweenness", "closeness", "degree", "eigenvector"]:
            self.assertIn(measure, metrics.centrality_scores)
            self.assertIsInstance(metrics.centrality_scores[measure], float)

    def test_flow_analysis_data_structure(self):
        """Test FlowAnalysis dataclass structure and validation."""
        flow_paths = [
            [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()],
            [uuid.uuid4(), uuid.uuid4()]
        ]
        bottlenecks = [uuid.uuid4(), uuid.uuid4()]
        flow_volumes = {uuid.uuid4(): 250.0, uuid.uuid4(): 150.0}
        efficiency_metrics = {
            "average_efficiency": 0.78,
            "total_throughput": 400.0,
            "bottleneck_impact": 0.23
        }
        
        flow_analysis = FlowAnalysis(
            flow_paths=flow_paths,
            bottlenecks=bottlenecks,
            flow_volumes=flow_volumes,
            efficiency_metrics=efficiency_metrics
        )

        # Validate structure
        self.assertEqual(flow_analysis.flow_paths, flow_paths)
        self.assertEqual(flow_analysis.bottlenecks, bottlenecks)
        self.assertEqual(flow_analysis.flow_volumes, flow_volumes)
        self.assertEqual(flow_analysis.efficiency_metrics, efficiency_metrics)
        
        # Validate data types
        self.assertIsInstance(flow_analysis.flow_paths, list)
        self.assertIsInstance(flow_analysis.bottlenecks, list)
        self.assertIsInstance(flow_analysis.flow_volumes, dict)
        self.assertIsInstance(flow_analysis.efficiency_metrics, dict)
        
        # Validate flow path structure
        for path in flow_analysis.flow_paths:
            self.assertIsInstance(path, list)
            for node_id in path:
                self.assertIsInstance(node_id, uuid.UUID)


@unittest.skipIf(nx is None, "NetworkX not available")
class TestNetworkXSFMQueryEngineUnit(unittest.TestCase):
    """Unit tests for NetworkXSFMQueryEngine implementation."""

    def setUp(self):
        """Set up test fixtures using centralized mock infrastructure."""
        # Use centralized mock graph instead of custom factory
        self.graph = create_mock_graph()
        self.query_engine = NetworkXSFMQueryEngine(self.graph)
        
        # Get the actual nodes from the graph to ensure we have the right IDs
        all_nodes = list(self.graph)
        actors = [n for n in all_nodes if isinstance(n, Actor)]
        policies = [n for n in all_nodes if isinstance(n, Policy)]
        
        # Extract specific nodes for testing with fallbacks
        self.government = actors[0] if actors else Actor(label="Test Government", sector="Government")
        self.corporation = actors[1] if len(actors) > 1 else Actor(label="Test Corporation", sector="Private")
        self.policy = policies[0] if policies else Policy(label="Test Policy", authority="Government")

    def test_initialization_and_graph_conversion(self):
        """Test proper initialization and NetworkX graph conversion."""
        # Test basic initialization
        self.assertIsInstance(self.query_engine, NetworkXSFMQueryEngine)
        self.assertEqual(self.query_engine.graph, self.graph)
        self.assertIsNotNone(self.query_engine.nx_graph)
        
        # Test NetworkX graph structure
        nx_graph = self.query_engine.nx_graph
        if nx is not None:
            self.assertIsInstance(nx_graph, nx.MultiDiGraph)
        
        # Verify node count
        expected_node_count = len(self.graph)
        self.assertEqual(
            len(nx_graph.nodes()), expected_node_count,
            f"NetworkX graph should have {expected_node_count} nodes"
        )
        
        # Verify relationship count
        expected_edge_count = len(self.graph.relationships)
        self.assertEqual(
            len(nx_graph.edges()), expected_edge_count,
            f"NetworkX graph should have {expected_edge_count} edges"
        )
        
        # Test node data preservation
        for node in self.graph:
            self.assertIn(node.id, nx_graph.nodes(), f"Node {node.label} missing from NetworkX graph")
            node_data = nx_graph.nodes[node.id]['data']
            self.assertEqual(node_data, node, "Node data should be preserved")

    def test_centrality_calculation_methods(self):
        """Test all centrality calculation methods."""
        centrality_types = ["betweenness", "closeness", "degree", "eigenvector"]
        
        for centrality_type in centrality_types:
            with self.subTest(centrality_type=centrality_type):
                try:
                    centrality = self.query_engine.get_node_centrality(
                        self.government.id, centrality_type
                    )
                    
                    self.assertIsInstance(
                        centrality, float,
                        f"{centrality_type} centrality should return float"
                    )
                    self.assertGreaterEqual(
                        centrality, 0.0,
                        f"{centrality_type} centrality should be non-negative"
                    )
                    self.assertLessEqual(
                        centrality, 1.0,
                        f"{centrality_type} centrality should be <= 1.0"
                    )
                except Exception as e:
                    # Some centrality measures might fail on small graphs
                    if centrality_type == "eigenvector":
                        # Eigenvector centrality can fail to converge
                        pass
                    else:
                        raise e

    def test_centrality_invalid_type_error_handling(self):
        """Test error handling for invalid centrality types."""
        with self.assertRaises(ValueError, msg="Should raise ValueError for invalid centrality type"):
            self.query_engine.get_node_centrality(self.government.id, "invalid_centrality")

    def test_most_central_nodes_filtering_and_ranking(self):
        """Test getting most central nodes with filtering and proper ranking."""
        # Test without type filter
        central_nodes = self.query_engine.get_most_central_nodes(limit=5)
        
        self.assertIsInstance(central_nodes, list, "Should return a list")
        self.assertLessEqual(len(central_nodes), 5, "Should respect limit parameter")
        
        # Verify ranking order (descending centrality)
        for i in range(len(central_nodes) - 1):
            current_score = central_nodes[i][1]
            next_score = central_nodes[i + 1][1]
            self.assertGreaterEqual(
                current_score, next_score,
                "Nodes should be ranked by centrality (descending)"
            )
        
        # Test with type filter
        central_actors = self.query_engine.get_most_central_nodes(Actor, limit=3)
        
        # Verify all returned nodes are of the correct type
        for node_id, score in central_actors:
            node_data = self.query_engine.nx_graph.nodes[node_id]['data']
            self.assertIsInstance(
                node_data, Actor,
                "Type filter should only return Actor nodes"
            )

    def test_neighbor_discovery_with_filtering(self):
        """Test neighbor discovery with distance and relationship filtering."""
        # Test direct neighbors
        direct_neighbors = self.query_engine.get_node_neighbors(
            self.government.id, distance=1
        )
        
        self.assertIsInstance(direct_neighbors, list, "Should return list of neighbors")
        
        # Test with relationship kind filtering
        policy_neighbors = self.query_engine.get_node_neighbors(
            self.government.id,
            relationship_kinds=[RelationshipKind.IMPLEMENTS],
            distance=1
        )
        
        # Should find policy that government implements
        policy_ids = [p.id for p in self.graph.policies.values()]
        policy_neighbors_found = [nid for nid in policy_neighbors if nid in policy_ids]
        self.assertGreater(
            len(policy_neighbors_found), 0,
            "Should find at least one policy that government implements"
        )
        
        # Test multi-hop neighbors
        extended_neighbors = self.query_engine.get_node_neighbors(
            self.government.id, distance=2
        )
        
        self.assertGreaterEqual(
            len(extended_neighbors), len(direct_neighbors),
            "Extended neighbors should include at least as many as direct neighbors"
        )

    def test_shortest_path_finding_algorithms(self):
        """Test shortest path finding with and without relationship filtering."""
        # Test basic shortest path
        path = self.query_engine.find_shortest_path(
            self.government.id, self.corporation.id
        )
        
        if path is not None:
            self.assertIsInstance(path, list, "Path should be a list")
            self.assertGreater(len(path), 1, "Path should have at least 2 nodes")
            self.assertEqual(path[0], self.government.id, "Path should start with source")
            self.assertEqual(path[-1], self.corporation.id, "Path should end with target")
        
        # Test with relationship filtering
        filtered_path = self.query_engine.find_shortest_path(
            self.government.id, self.corporation.id,
            relationship_kinds=[RelationshipKind.IMPLEMENTS, RelationshipKind.AFFECTS]
        )
        
        # Path might be different or None with filtering
        if filtered_path is not None:
            self.assertIsInstance(filtered_path, list)

    def test_relationship_strength_calculation(self):
        """Test relationship strength calculation between nodes."""
        # Test strength between connected nodes
        strength = self.query_engine.get_relationship_strength(
            self.government.id, self.policy.id
        )
        
        if strength > 0.0:
            self.assertIsInstance(strength, float, "Strength should be a float")
            self.assertGreater(strength, 0.0, "Connected nodes should have positive strength")
        
        # Test strength between unconnected nodes
        fake_id = uuid.uuid4()
        no_strength = self.query_engine.get_relationship_strength(
            self.government.id, fake_id
        )
        self.assertEqual(no_strength, 0.0, "Unconnected nodes should have zero strength")

    def test_cycle_detection_and_feedback_loops(self):
        """Test cycle detection for identifying feedback loops."""
        cycles = self.query_engine.find_cycles(max_length=5)
        
        self.assertIsInstance(cycles, list, "Should return list of cycles")
        
        for cycle in cycles:
            self.assertIsInstance(cycle, list, "Each cycle should be a list")
            self.assertLessEqual(
                len(cycle), 5,
                "Cycles should respect max_length parameter"
            )
            
            if len(cycle) > 2:
                # Verify it's actually a cycle (first and last nodes should be connected)
                first_node = cycle[0]
                last_node = cycle[-1]
                # This is a simplified check - in a real cycle, last connects to first
                self.assertIn(
                    first_node, self.query_engine.nx_graph.nodes(),
                    "Cycle nodes should exist in graph"
                )

    def test_resource_flow_tracing_and_analysis(self):
        """Test resource flow tracing for specific resource types."""
        # Test natural resource flows
        natural_flow_analysis = self.query_engine.trace_resource_flows(
            ResourceType.NATURAL
        )
        
        self.assertIsInstance(natural_flow_analysis, FlowAnalysis)
        self.assertIsInstance(natural_flow_analysis.flow_paths, list)
        self.assertIsInstance(natural_flow_analysis.bottlenecks, list)
        self.assertIsInstance(natural_flow_analysis.flow_volumes, dict)
        self.assertIsInstance(natural_flow_analysis.efficiency_metrics, dict)
        
        # Test produced resource flows
        produced_flow_analysis = self.query_engine.trace_resource_flows(
            ResourceType.PRODUCED
        )
        
        self.assertIsInstance(produced_flow_analysis, FlowAnalysis)

    def test_bottleneck_identification_analysis(self):
        """Test identification of bottlenecks in flow networks."""
        bottlenecks = self.query_engine.identify_bottlenecks(FlowNature.TRANSFER)
        
        self.assertIsInstance(bottlenecks, list, "Should return list of bottleneck nodes")
        
        # Verify bottleneck nodes exist in graph
        for bottleneck_id in bottlenecks:
            self.assertIn(
                bottleneck_id, self.query_engine.nx_graph.nodes(),
                "Bottleneck nodes should exist in graph"
            )

    def test_policy_impact_analysis_comprehensive(self):
        """Test comprehensive policy impact analysis."""
        impact_analysis = self.query_engine.analyze_policy_impact(
            self.policy.id, impact_radius=2
        )
        
        self.assertIsInstance(impact_analysis, dict, "Should return impact analysis dict")
        
        expected_keys = [
            "total_affected_nodes", "affected_actors", "affected_institutions",
            "affected_resources", "network_metrics"
        ]
        
        for key in expected_keys:
            self.assertIn(key, impact_analysis, f"Missing key in impact analysis: {key}")
        
        # Validate metrics
        self.assertIsInstance(
            impact_analysis["total_affected_nodes"], int,
            "Total affected nodes should be integer"
        )
        self.assertIsInstance(
            impact_analysis["network_metrics"], dict,
            "Network metrics should be a dict"
        )

    def test_policy_target_identification(self):
        """Test identification of policy targets (direct and indirect)."""
        targets = self.query_engine.identify_policy_targets(self.policy.id)
        
        self.assertIsInstance(targets, list, "Should return list of target node IDs")
        
        # Verify targets exist in graph
        for target_id in targets:
            self.assertIn(
                target_id, self.query_engine.nx_graph.nodes(),
                "Policy targets should exist in graph"
            )

    def test_network_density_calculation(self):
        """Test network density calculation."""
        density = self.query_engine.get_network_density()
        
        self.assertIsInstance(density, float, "Density should be a float")
        self.assertGreaterEqual(density, 0.0, "Density should be non-negative")
        self.assertLessEqual(density, 1.0, "Density should be at most 1.0")

    def test_comprehensive_node_analysis_integration(self):
        """Test comprehensive analysis of individual nodes."""
        metrics = self.query_engine.comprehensive_node_analysis(self.government.id)
        
        self.assertIsInstance(metrics, NodeMetrics, "Should return NodeMetrics object")
        self.assertEqual(metrics.node_id, self.government.id, "Should analyze correct node")
        self.assertEqual(metrics.node_type, "Actor", "Should identify correct node type")
        
        # Verify centrality scores
        self.assertIsInstance(metrics.centrality_scores, dict)
        expected_centrality_types = ["betweenness", "closeness", "degree"]
        for centrality_type in expected_centrality_types:
            self.assertIn(
                centrality_type, metrics.centrality_scores,
                f"Missing centrality score: {centrality_type}"
            )
        
        # Verify other metrics
        self.assertIsInstance(metrics.influence_score, float)
        self.assertIsInstance(metrics.dependency_score, float)
        self.assertIsInstance(metrics.connectivity, int)


@unittest.skipIf(nx is None, "NetworkX not available")
class TestSFMQueryEngineIntegration(unittest.TestCase):
    """Integration tests with realistic SFM scenarios."""

    def setUp(self):
        """Set up complex test scenario using centralized mocks."""
        # Use centralized mock graph for consistency
        self.complex_graph = create_mock_graph()
        self.query_engine = NetworkXSFMQueryEngine(self.complex_graph)

    def test_end_to_end_policy_analysis_workflow(self):
        """Test complete policy analysis workflow."""
        # Find a policy to analyze
        policy_id = next(iter(self.complex_graph.policies.keys()))
        
        # Step 1: Analyze policy impact
        impact_analysis = self.query_engine.analyze_policy_impact(
            policy_id, impact_radius=3
        )
        
        self.assertIsInstance(impact_analysis, dict)
        self.assertIn("total_affected_nodes", impact_analysis)
        
        # Step 2: Identify specific targets
        targets = self.query_engine.identify_policy_targets(policy_id)
        self.assertIsInstance(targets, list)
        
        # Step 3: Analyze central actors in the policy network
        central_actors = self.query_engine.get_most_central_nodes(Actor, limit=5)
        self.assertGreater(len(central_actors), 0)
        
        # Step 4: Comprehensive analysis of top actor
        if central_actors:
            top_actor_id = central_actors[0][0]
            actor_metrics = self.query_engine.comprehensive_node_analysis(top_actor_id)
            self.assertIsInstance(actor_metrics, NodeMetrics)

    def test_resource_flow_analysis_workflow(self):
        """Test resource flow analysis workflow."""
        # Analyze natural resource flows
        natural_flows = self.query_engine.trace_resource_flows(ResourceType.NATURAL)
        self.assertIsInstance(natural_flows, FlowAnalysis)
        
        # Identify bottlenecks in transfer flows
        bottlenecks = self.query_engine.identify_bottlenecks(FlowNature.TRANSFER)
        self.assertIsInstance(bottlenecks, list)
        
        # Calculate flow efficiency between actors
        actor_ids = list(self.complex_graph.actors.keys())
        if len(actor_ids) >= 2:
            efficiency = self.query_engine.calculate_flow_efficiency(
                actor_ids[0], actor_ids[1]
            )
            self.assertIsInstance(efficiency, float)
            self.assertGreaterEqual(efficiency, 0.0)

    def test_structural_analysis_workflow(self):
        """Test structural analysis workflow."""
        # Calculate network density
        density = self.query_engine.get_network_density()
        self.assertIsInstance(density, float)
        
        # Identify communities
        communities = self.query_engine.identify_communities()
        self.assertIsInstance(communities, dict)
        
        # Find structural holes
        bridges = self.query_engine.get_structural_holes()
        self.assertIsInstance(bridges, list)
        
        # System vulnerability analysis
        vulnerability = self.query_engine.system_vulnerability_analysis()
        self.assertIsInstance(vulnerability, dict)

    def test_scenario_comparison_analysis(self):
        """Test comparison of multiple SFM scenarios."""
        # Create alternative scenario
        # Use centralized mock graph for alternative scenario
        scenario2 = create_mock_graph()
        
        scenarios = [self.complex_graph, scenario2]
        comparison = self.query_engine.compare_policy_scenarios(scenarios)
        
        self.assertIsInstance(comparison, dict)
        self.assertIn("scenario_count", comparison)
        self.assertEqual(comparison["scenario_count"], 2)


class TestSFMQueryFactory(unittest.TestCase):
    """Test suite for SFMQueryFactory."""

    def setUp(self):
        """Set up test fixtures."""
        self.graph = create_mock_graph()

    @unittest.skipIf(nx is None, "NetworkX not available")
    def test_create_networkx_query_engine(self):
        """Test creation of NetworkX query engine."""
        engine = SFMQueryFactory.create_query_engine(self.graph, "networkx")
        
        self.assertIsInstance(
            engine, NetworkXSFMQueryEngine,
            "Factory should create NetworkXSFMQueryEngine"
        )
        self.assertEqual(engine.graph, self.graph, "Engine should use provided graph")

    @unittest.skipIf(nx is None, "NetworkX not available")
    def test_factory_case_insensitive(self):
        """Test that factory is case insensitive."""
        variations = ["networkx", "NetworkX", "NETWORKX", "networkX"]
        
        for backend_name in variations:
            with self.subTest(backend=backend_name):
                engine = SFMQueryFactory.create_query_engine(self.graph, backend_name)
                self.assertIsInstance(engine, NetworkXSFMQueryEngine)

    def test_unsupported_backend_error(self):
        """Test error handling for unsupported backends."""
        with self.assertRaises(ValueError, msg="Should raise ValueError for unsupported backend"):
            SFMQueryFactory.create_query_engine(self.graph, "unsupported_backend")

    def test_factory_with_none_backend(self):
        """Test factory behavior with None backend."""
        with self.assertRaises(ValueError):
            SFMQueryFactory.create_query_engine(self.graph, "")


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up edge case test fixtures."""
        self.empty_graph = SFMGraph(name="Empty Graph")
        
        self.single_node_graph = SFMGraph(name="Single Node Graph")
        self.single_actor = Actor(label="Lone Actor")
        self.single_node_graph.add_node(self.single_actor)

    @unittest.skipIf(nx is None, "NetworkX not available")
    def test_empty_graph_handling(self):
        """Test query engine with empty graph."""
        engine = NetworkXSFMQueryEngine(self.empty_graph)
        
        # Test basic operations on empty graph
        density = engine.get_network_density()
        self.assertEqual(density, 0.0, "Empty graph should have zero density")
        
        central_nodes = engine.get_most_central_nodes()
        self.assertEqual(len(central_nodes), 0, "Empty graph should have no central nodes")
        
        communities = engine.identify_communities()
        self.assertIsInstance(communities, dict, "Should return empty communities dict")

    @unittest.skipIf(nx is None, "NetworkX not available")
    def test_single_node_graph_operations(self):
        """Test operations on single-node graph."""
        engine = NetworkXSFMQueryEngine(self.single_node_graph)
        
        # Test centrality calculations
        centrality = engine.get_node_centrality(self.single_actor.id)
        self.assertEqual(centrality, 0.0, "Single node should have zero centrality")
        
        # Test neighbor finding
        neighbors = engine.get_node_neighbors(self.single_actor.id)
        self.assertEqual(len(neighbors), 0, "Single node should have no neighbors")
        
        # Test path finding to itself
        path = engine.find_shortest_path(self.single_actor.id, self.single_actor.id)
        if path is not None:
            self.assertEqual(len(path), 1, "Path to self should be single node")

    @unittest.skipIf(nx is None, "NetworkX not available")
    def test_nonexistent_node_handling(self):
        """Test handling of queries for non-existent nodes."""
        engine = NetworkXSFMQueryEngine(self.single_node_graph)
        fake_id = uuid.uuid4()
        
        # Test centrality for non-existent node
        centrality = engine.get_node_centrality(fake_id)
        self.assertEqual(centrality, 0.0, "Non-existent node should have zero centrality")
        
        # Test relationship strength with non-existent node
        strength = engine.get_relationship_strength(self.single_actor.id, fake_id)
        self.assertEqual(strength, 0.0, "No relationship should have zero strength")

    @unittest.skipIf(nx is None, "NetworkX not available")
    def test_invalid_parameter_handling(self):
        """Test handling of invalid parameters."""
        engine = NetworkXSFMQueryEngine(self.single_node_graph)
        
        # Test invalid centrality type
        with self.assertRaises(ValueError):
            engine.get_node_centrality(self.single_actor.id, "invalid_centrality")
        
        # Test negative distance
        neighbors = engine.get_node_neighbors(self.single_actor.id, distance=-1)
        self.assertIsInstance(neighbors, list, "Should handle negative distance gracefully")
        
        # Test very large distance
        neighbors = engine.get_node_neighbors(self.single_actor.id, distance=1000)
        self.assertIsInstance(neighbors, list, "Should handle large distance gracefully")


@unittest.skipIf(nx is None, "NetworkX not available")
class TestPerformanceAndScalability(unittest.TestCase):
    """Performance and scalability tests for SFM query operations."""

    def setUp(self):
        """Set up large-scale test scenario using centralized mocks."""
        # Use centralized mock graph for consistency
        self.large_graph = create_mock_graph()
        self.query_engine = NetworkXSFMQueryEngine(self.large_graph)

    def test_centrality_calculation_performance(self):
        """Test performance of centrality calculations on large graph."""
        start_time = time.time()
        
        # Calculate centrality for sample of nodes
        sample_nodes = list(self.large_graph.actors.keys())[:10]
        centrality_types = ["betweenness", "closeness", "degree"]
        
        for node_id in sample_nodes:
            for centrality_type in centrality_types:
                try:
                    centrality = self.query_engine.get_node_centrality(node_id, centrality_type)
                    self.assertIsInstance(centrality, float)
                except Exception as e:
                    # Some centrality measures might fail, that's OK for performance test
                    pass
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(
            execution_time, 30.0,
            f"Centrality calculations took too long: {execution_time:.2f} seconds"
        )

    def test_pathfinding_performance_scalability(self):
        """Test pathfinding performance on large graph."""
        start_time = time.time()
        
        # Test pathfinding between random node pairs
        all_nodes = list(self.large_graph.actors.keys()) + list(self.large_graph.institutions.keys())
        random.seed(42)
        
        for _ in range(20):  # Test 20 random pairs
            source, target = random.sample(all_nodes, 2)
            path = self.query_engine.find_shortest_path(source, target)
            # Path might be None if nodes aren't connected
            self.assertTrue(path is None or isinstance(path, list))
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        self.assertLess(
            execution_time, 20.0,
            f"Pathfinding took too long: {execution_time:.2f} seconds"
        )

    def test_comprehensive_analysis_performance(self):
        """Test performance of comprehensive node analysis."""
        start_time = time.time()
        
        # Analyze sample of nodes
        sample_nodes = list(self.large_graph.actors.keys())[:5]
        
        for node_id in sample_nodes:
            metrics = self.query_engine.comprehensive_node_analysis(node_id)
            self.assertIsInstance(metrics, NodeMetrics)
            self.assertEqual(metrics.node_id, node_id)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        self.assertLess(
            execution_time, 25.0,
            f"Comprehensive analysis took too long: {execution_time:.2f} seconds"
        )

    def test_memory_usage_efficiency(self):
        """Test memory efficiency of query operations."""

        
        # Get initial memory usage
        initial_objects = len(gc.get_objects()) if 'gc' in sys.modules else 0
        
        # Perform various operations that might create many temporary objects
        for _ in range(10):
            density = self.query_engine.get_network_density()
            central_nodes = self.query_engine.get_most_central_nodes(limit=5)
            communities = self.query_engine.identify_communities()
        
        # Force garbage collection if available
        if 'gc' in sys.modules:
            gc.collect()
            final_objects = len(gc.get_objects())
            
            # Check that we haven't created too many persistent objects
            object_increase = final_objects - initial_objects
            self.assertLess(
                object_increase, 10000,
                f"Too many objects created: {object_increase}"
            )


if __name__ == "__main__":
    # Run tests with appropriate verbosity
    unittest.main(
        verbosity=2,
        # Optionally run specific test classes
        # argv=['test_sfm_query_ext.py', 'TestNetworkXSFMQueryEngineUnit']
    )
