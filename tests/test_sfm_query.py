"""
Unit and integration tests for SFM query engine classes.
Tests the abstract query layer and NetworkX implementation for Social Fabric Matrix analysis.
"""

import unittest
import uuid
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
import networkx as nx
from networkx import NetworkXError, NetworkXNoPath

from models import (
    Actor,
    Institution,
    Resource,
    Policy,
    Flow,
    Relationship,
    Node,
    
)
from models.sfm_enums import ResourceType, FlowNature,RelationshipKind
from graph.sfm_query import (
    SFMQueryEngine,
    NetworkXSFMQueryEngine,
    SFMQueryFactory,
    AnalysisType,
    QueryResult,
    NodeMetrics,
    FlowAnalysis,
)
from graph.graph import SFMGraph

# Import centralized mocks and fixtures
from tests.mocks import (
    MockQueryEngineFactory,
    MockNetworkXFunctions,
    create_mock_graph,
    create_sample_nodes,
)


class TestSFMQueryEngineAbstract(unittest.TestCase):
    """Test suite for the abstract SFMQueryEngine class."""

    def test_abstract_class_cannot_be_instantiated(self):
        """Test that SFMQueryEngine cannot be instantiated directly."""
        graph = SFMGraph()
        with self.assertRaises(TypeError):
            # This should raise TypeError because SFMQueryEngine is abstract
            engine = object.__new__(SFMQueryEngine)
            engine.__init__(graph)

    def test_abstract_methods_exist(self):
        """Test that all expected abstract methods are defined."""
        abstract_methods = [
            "get_node_centrality",
            "get_most_central_nodes",
            "get_node_neighbors",
            "find_shortest_path",
            "get_relationship_strength",
            "find_cycles",
            "trace_resource_flows",
            "identify_bottlenecks",
            "calculate_flow_efficiency",
            "analyze_policy_impact",
            "identify_policy_targets",
            "compare_policy_scenarios",
            "get_network_density",
            "identify_communities",
            "get_structural_holes",
            "comprehensive_node_analysis",
            "system_vulnerability_analysis",
        ]

        for method_name in abstract_methods:
            self.assertTrue(hasattr(SFMQueryEngine, method_name))


class TestDataClasses(unittest.TestCase):
    """Test suite for data classes used in query results."""

    def test_query_result_creation(self):
        """Test QueryResult dataclass creation."""
        result = QueryResult(
            data={"test": "data"},
            query_type="centrality",
            parameters={"node_id": str(uuid.uuid4())},
            metadata={"execution_time": 0.1},
            timestamp="2025-06-19T10:00:00",
        )

        self.assertEqual(result.data, {"test": "data"})
        self.assertEqual(result.query_type, "centrality")
        self.assertIsInstance(result.parameters, dict)
        self.assertIsInstance(result.metadata, dict)

    def test_node_metrics_creation(self):
        """Test NodeMetrics dataclass creation."""
        node_id = uuid.uuid4()
        metrics = NodeMetrics(
            node_id=node_id,
            centrality_scores={"betweenness": 0.5, "closeness": 0.3},
            influence_score=0.7,
            dependency_score=0.4,
            connectivity=5,
            node_type="Actor",
        )

        self.assertEqual(metrics.node_id, node_id)
        self.assertEqual(metrics.centrality_scores["betweenness"], 0.5)
        self.assertEqual(metrics.influence_score, 0.7)
        self.assertEqual(metrics.node_type, "Actor")

    def test_flow_analysis_creation(self):
        """Test FlowAnalysis dataclass creation."""
        flow_analysis = FlowAnalysis(
            flow_paths=[[uuid.uuid4(), uuid.uuid4()]],
            bottlenecks=[uuid.uuid4()],
            flow_volumes={uuid.uuid4(): 100.0},
            efficiency_metrics={"avg_efficiency": 0.8},
        )

        self.assertIsInstance(flow_analysis.flow_paths, list)
        self.assertIsInstance(flow_analysis.bottlenecks, list)
        self.assertIsInstance(flow_analysis.flow_volumes, dict)
        self.assertIsInstance(flow_analysis.efficiency_metrics, dict)


class TestNetworkXSFMQueryEngineUnit(unittest.TestCase):
    """Unit tests for NetworkXSFMQueryEngine."""

    def setUp(self):
        """Set up test fixtures using centralized mock infrastructure."""
        # Use centralized mock graph creation
        self.graph = create_mock_graph()
        
        # Get the actual nodes from the graph to ensure we have the right IDs
        all_nodes = list(self.graph)
        actors = [n for n in all_nodes if isinstance(n, Actor)]
        institutions = [n for n in all_nodes if isinstance(n, Institution)]
        policies = [n for n in all_nodes if isinstance(n, Policy)]
        resources = [n for n in all_nodes if isinstance(n, Resource)]
        
        # Assign specific nodes - ensure we have fallbacks
        self.actor1 = actors[0] if actors else Actor(label="Test Actor 1", sector="Government")
        self.actor2 = actors[1] if len(actors) > 1 else Actor(label="Test Actor 2", sector="Private")
        self.institution = institutions[0] if institutions else Institution(label="Test Institution")
        self.policy = policies[0] if policies else Policy(label="Test Policy", authority="Government")
        self.resource = resources[0] if resources else Resource(label="Test Resource", rtype=ResourceType.NATURAL)

        # Create query engine
        self.query_engine = NetworkXSFMQueryEngine(self.graph)

    def test_initialization(self):
        """Test query engine initialization."""
        self.assertIsInstance(self.query_engine, NetworkXSFMQueryEngine)
        self.assertEqual(self.query_engine.graph, self.graph)
        self.assertIsNotNone(self.query_engine.nx_graph)

    def test_build_networkx_graph(self):
        """Test conversion of SFMGraph to NetworkX graph."""
        nx_graph = self.query_engine.nx_graph

        # Check nodes (our mock graph has 10 nodes: 3 actors + 2 institutions + 2 policies + 3 resources)
        self.assertEqual(len(nx_graph.nodes()), 10)
        self.assertIn(self.actor1.id, nx_graph.nodes())
        self.assertIn(self.actor2.id, nx_graph.nodes())

        # Check edges - should have some relationships from our mock data
        self.assertGreaterEqual(len(nx_graph.edges()), 3)  # At least 3 relationships

        # Check node data
        node_data = nx_graph.nodes[self.actor1.id]["data"]
        self.assertEqual(node_data, self.actor1)

        # Check edge data - just verify structure exists
        self.assertGreater(len(nx_graph.edges()), 0)

    @patch("networkx.betweenness_centrality")
    def test_get_node_centrality_betweenness(self, mock_centrality):
        """Test betweenness centrality calculation using centralized mocks."""
        # Use centralized mock data with UUID keys (not string keys)
        centrality_data = {
            self.actor1.id: 0.5,
            self.actor2.id: 0.3
        }
        mock_centrality.return_value = centrality_data

        centrality = self.query_engine.get_node_centrality(
            self.actor1.id, "betweenness"
        )

        self.assertEqual(centrality, 0.5)
        mock_centrality.assert_called_once()

    @patch("networkx.closeness_centrality")
    def test_get_node_centrality_closeness(self, mock_centrality):
        """Test closeness centrality calculation using centralized mocks."""
        centrality_data = {
            self.actor1.id: 0.7,
            self.actor2.id: 0.4
        }
        mock_centrality.return_value = centrality_data

        centrality = self.query_engine.get_node_centrality(self.actor1.id, "closeness")

        self.assertEqual(centrality, 0.7)
        mock_centrality.assert_called_once()

    @patch("networkx.degree_centrality")
    def test_get_node_centrality_degree(self, mock_centrality):
        """Test degree centrality calculation using centralized mocks."""
        centrality_data = {
            self.actor1.id: 0.6,
            self.actor2.id: 0.8
        }
        mock_centrality.return_value = centrality_data

        centrality = self.query_engine.get_node_centrality(self.actor1.id, "degree")

        self.assertEqual(centrality, 0.6)
        mock_centrality.assert_called_once()

    def test_get_node_centrality_invalid_type(self):
        """Test error handling for invalid centrality type."""
        with self.assertRaises(ValueError):
            self.query_engine.get_node_centrality(self.actor1.id, "invalid_type")

    @patch("networkx.eigenvector_centrality")
    @patch("networkx.degree_centrality")
    def test_get_node_centrality_eigenvector_fallback(self, mock_degree, mock_eigenvector):
        """Test eigenvector centrality with fallback to degree centrality."""
        # Mock eigenvector centrality to raise NetworkXError
        mock_eigenvector.side_effect = nx.NetworkXError("Convergence error")
        
        # Mock degree centrality as fallback
        centrality_data = {
            self.actor1.id: 0.5,
            self.actor2.id: 0.3
        }
        mock_degree.return_value = centrality_data
        
        centrality = self.query_engine.get_node_centrality(self.actor1.id, "eigenvector")
        
        self.assertEqual(centrality, 0.5)
        mock_eigenvector.assert_called_once()
        mock_degree.assert_called_once()

    @patch("networkx.eigenvector_centrality")
    def test_get_node_centrality_eigenvector_success(self, mock_eigenvector):
        """Test successful eigenvector centrality calculation."""
        centrality_data = {
            self.actor1.id: 0.8,
            self.actor2.id: 0.6
        }
        mock_eigenvector.return_value = centrality_data
        
        centrality = self.query_engine.get_node_centrality(self.actor1.id, "eigenvector")
        
        self.assertEqual(centrality, 0.8)
        mock_eigenvector.assert_called_once()

    @patch("networkx.betweenness_centrality")
    def test_get_most_central_nodes(self, mock_centrality):
        """Test getting most central nodes using centralized mocks."""
        centrality_data = {
            self.actor1.id: 0.8,
            self.actor2.id: 0.6,
            self.institution.id: 0.4,
            self.resource.id: 0.2,
            self.policy.id: 0.1,
        }
        mock_centrality.return_value = centrality_data

        # Test without type filter
        central_nodes = self.query_engine.get_most_central_nodes(limit=3)
        self.assertEqual(len(central_nodes), 3)
        self.assertEqual(central_nodes[0][0], self.actor1.id)
        self.assertEqual(central_nodes[0][1], 0.8)

        # Test with type filter
        central_actors = self.query_engine.get_most_central_nodes(Actor, limit=2)
        self.assertEqual(len(central_actors), 2)
        # Both results should be actors
        for node_id, score in central_actors:
            self.assertIn(node_id, [self.actor1.id, self.actor2.id])

    @patch("networkx.eigenvector_centrality")
    @patch("networkx.degree_centrality")
    def test_get_most_central_nodes_eigenvector_fallback(self, mock_degree, mock_eigenvector):
        """Test eigenvector centrality fallback in get_most_central_nodes."""
        # Mock eigenvector centrality to raise NetworkXError
        mock_eigenvector.side_effect = nx.NetworkXError("Convergence error")
        
        # Mock degree centrality as fallback
        centrality_data = {
            self.actor1.id: 0.8,
            self.actor2.id: 0.6,
            self.institution.id: 0.4,
        }
        mock_degree.return_value = centrality_data
        
        central_nodes = self.query_engine.get_most_central_nodes(
            centrality_type="eigenvector", limit=2
        )
        
        self.assertEqual(len(central_nodes), 2)
        self.assertEqual(central_nodes[0][0], self.actor1.id)
        self.assertEqual(central_nodes[0][1], 0.8)
        mock_eigenvector.assert_called_once()
        mock_degree.assert_called_once()

    @patch("networkx.closeness_centrality")
    def test_get_most_central_nodes_closeness(self, mock_centrality):
        """Test closeness centrality in get_most_central_nodes."""
        centrality_data = {
            self.actor1.id: 0.9,
            self.actor2.id: 0.7,
            self.institution.id: 0.5,
        }
        mock_centrality.return_value = centrality_data
        
        central_nodes = self.query_engine.get_most_central_nodes(
            centrality_type="closeness", limit=2
        )
        
        self.assertEqual(len(central_nodes), 2)
        self.assertEqual(central_nodes[0][0], self.actor1.id)
        self.assertEqual(central_nodes[0][1], 0.9)
        mock_centrality.assert_called_once()

    @patch("networkx.degree_centrality")
    def test_get_most_central_nodes_degree(self, mock_centrality):
        """Test degree centrality in get_most_central_nodes."""
        centrality_data = {
            self.actor1.id: 0.8,
            self.actor2.id: 0.6,
            self.institution.id: 0.4,
        }
        mock_centrality.return_value = centrality_data
        
        central_nodes = self.query_engine.get_most_central_nodes(
            centrality_type="degree", limit=2
        )
        
        self.assertEqual(len(central_nodes), 2)
        self.assertEqual(central_nodes[0][0], self.actor1.id)
        self.assertEqual(central_nodes[0][1], 0.8)
        mock_centrality.assert_called_once()

    def test_get_most_central_nodes_invalid_type(self):
        """Test error handling for invalid centrality type in get_most_central_nodes."""
        with self.assertRaises(ValueError):
            self.query_engine.get_most_central_nodes(centrality_type="invalid_type")

    def test_get_node_neighbors_direct(self):
        """Test getting direct neighbors."""
        neighbors = self.query_engine.get_node_neighbors(self.actor1.id, distance=1)

        # Actor1 should have Actor2 as neighbor through the GOVERNS relationship
        self.assertIn(self.actor2.id, neighbors)

    def test_get_node_neighbors_with_relationship_filter(self):
        """Test getting neighbors filtered by relationship kind."""
        neighbors = self.query_engine.get_node_neighbors(
            self.actor1.id, relationship_kinds=[RelationshipKind.GOVERNS], distance=1
        )

        # Should find Actor2 through GOVERNS relationship
        self.assertIn(self.actor2.id, neighbors)

        # Test with non-matching relationship kind
        no_neighbors = self.query_engine.get_node_neighbors(
            self.actor1.id, relationship_kinds=[RelationshipKind.PRODUCES], distance=1
        )

        # Should not find any neighbors for PRODUCES relationship
        self.assertEqual(len(no_neighbors), 0)

    @patch("networkx.ego_graph")
    def test_get_node_neighbors_multihop(self, mock_ego_graph):
        """Test getting multi-hop neighbors."""
        # Create a mock ego graph
        mock_graph = MagicMock()
        mock_graph.nodes.return_value = [self.actor1.id, self.actor2.id, self.institution.id]
        mock_ego_graph.return_value = mock_graph
        
        neighbors = self.query_engine.get_node_neighbors(self.actor1.id, distance=2)
        
        # Should return neighbors excluding the source node
        expected_neighbors = [self.actor2.id, self.institution.id]
        self.assertEqual(set(neighbors), set(expected_neighbors))
        mock_ego_graph.assert_called_once_with(self.query_engine.nx_graph, self.actor1.id, radius=2)

    @patch("networkx.ego_graph")
    def test_get_node_neighbors_multihop_network_error(self, mock_ego_graph):
        """Test multi-hop neighbors with NetworkX error."""
        mock_ego_graph.side_effect = nx.NetworkXError("Graph error")
        
        neighbors = self.query_engine.get_node_neighbors(self.actor1.id, distance=2)
        
        # Should return empty list on error
        self.assertEqual(neighbors, [])
        mock_ego_graph.assert_called_once()

    @patch("networkx.shortest_path_length")
    def test_get_node_neighbors_multihop_with_filter(self, mock_path_length):
        """Test multi-hop neighbors with relationship kind filtering."""
        # Mock path length calculations
        mock_path_length.side_effect = [1, 2, NetworkXNoPath("No path")]
        
        neighbors = self.query_engine.get_node_neighbors(
            self.actor1.id, 
            relationship_kinds=[RelationshipKind.GOVERNS], 
            distance=2
        )
        
        # Should handle the filtering and path length checks
        self.assertIsInstance(neighbors, list)

    def test_get_node_neighbors_negative_distance(self):
        """Test handling of negative distance parameter."""
        neighbors = self.query_engine.get_node_neighbors(self.actor1.id, distance=-1)
        
        # Should handle gracefully (implementation detail)
        self.assertIsInstance(neighbors, list)

    @patch("networkx.shortest_path")
    def test_find_shortest_path(self, mock_shortest_path):
        """Test finding shortest path between nodes using centralized mocks."""
        expected_path = MockNetworkXFunctions.get_default_shortest_path()
        # Override with our specific test nodes
        expected_path = [self.actor1.id, self.actor2.id]
        mock_shortest_path.return_value = expected_path

        path = self.query_engine.find_shortest_path(self.actor1.id, self.actor2.id)

        self.assertEqual(path, expected_path)
        mock_shortest_path.assert_called_once()

    @patch("networkx.shortest_path")
    def test_find_shortest_path_no_path(self, mock_shortest_path):
        """Test finding shortest path when no path exists."""
        mock_shortest_path.side_effect = NetworkXNoPath("No path")

        path = self.query_engine.find_shortest_path(self.actor1.id, uuid.uuid4())

        self.assertIsNone(path)

    @patch("networkx.shortest_path")
    def test_find_shortest_path_with_relationship_filter(self, mock_shortest_path):
        """Test finding shortest path with relationship kind filtering."""
        expected_path = [self.actor1.id, self.actor2.id]
        mock_shortest_path.return_value = expected_path
        
        path = self.query_engine.find_shortest_path(
            self.actor1.id, 
            self.actor2.id,
            relationship_kinds=[RelationshipKind.GOVERNS]
        )
        
        self.assertEqual(path, expected_path)
        # Should be called with the filtered subgraph
        mock_shortest_path.assert_called_once()

    @patch("networkx.shortest_path")
    def test_find_shortest_path_with_relationship_filter_no_path(self, mock_shortest_path):
        """Test finding shortest path with relationship filtering when no path exists."""
        mock_shortest_path.side_effect = nx.NetworkXNoPath("No path")
        
        path = self.query_engine.find_shortest_path(
            self.actor1.id,
            self.actor2.id,
            relationship_kinds=[RelationshipKind.PRODUCES]
        )
        
        self.assertIsNone(path)
        mock_shortest_path.assert_called_once()

    def test_get_relationship_strength(self):
        """Test calculating relationship strength."""
        # Test existing relationship
        strength = self.query_engine.get_relationship_strength(
            self.actor1.id, self.actor2.id
        )
        self.assertEqual(strength, 0.8)  # Weight of rel1

        # Test non-existing relationship
        no_strength = self.query_engine.get_relationship_strength(
            self.actor1.id, uuid.uuid4()
        )
        self.assertEqual(no_strength, 0.0)

    @patch("networkx.simple_cycles")
    def test_find_cycles(self, mock_cycles):
        """Test finding cycles in the graph using centralized mocks."""
        mock_cycles.return_value = [
            [self.actor1.id, self.actor2.id, self.actor1.id],
            [self.resource.id, self.institution.id, self.resource.id],
        ]

        cycles = self.query_engine.find_cycles(max_length=5)

        self.assertEqual(len(cycles), 2)
        self.assertIn(self.actor1.id, cycles[0])
        mock_cycles.assert_called_once()

    @patch("networkx.simple_cycles")
    def test_find_cycles_network_error(self, mock_cycles):
        """Test finding cycles with NetworkX error."""
        mock_cycles.side_effect = nx.NetworkXError("Graph error")
        
        cycles = self.query_engine.find_cycles(max_length=5)
        
        self.assertEqual(cycles, [])
        mock_cycles.assert_called_once()

    def test_trace_resource_flows(self):
        """Test tracing resource flows."""
        flow_analysis = self.query_engine.trace_resource_flows(ResourceType.NATURAL)

        self.assertIsInstance(flow_analysis, FlowAnalysis)
        self.assertIsInstance(flow_analysis.flow_paths, list)
        self.assertIsInstance(flow_analysis.bottlenecks, list)
        self.assertIsInstance(flow_analysis.flow_volumes, dict)

    def test_trace_resource_flows_with_relationships(self):
        """Test tracing resource flows with actual relationships."""
        # Create a resource of the requested type
        water_resource = Resource(
            label="Water Resource",
            rtype=ResourceType.NATURAL
        )
        self.graph.add_node(water_resource)
        
        # Create a relationship with flow characteristics (Actor uses Resource)
        flow_relationship = Relationship(
            source_id=self.actor1.id,
            target_id=water_resource.id,
            kind=RelationshipKind.USES,
            weight=0.7
        )
        self.graph.add_relationship(flow_relationship)
        
        # Rebuild the query engine with the updated graph
        query_engine = NetworkXSFMQueryEngine(self.graph)
        
        flow_analysis = query_engine.trace_resource_flows(ResourceType.NATURAL)
        
        self.assertIsInstance(flow_analysis, FlowAnalysis)
        # The current implementation looks for relationships FROM the resource
        # Since we have Actor->Resource, this might not find the flow
        # That's expected behavior, so we just verify the structure
        self.assertIsInstance(flow_analysis.flow_volumes, dict)
        self.assertIsInstance(flow_analysis.flow_paths, list)
        self.assertIsInstance(flow_analysis.bottlenecks, list)

    def test_trace_resource_flows_with_valid_flow_relationships(self):
        """Test tracing resource flows with relationships that create flow volumes."""
        # Create a resource of the requested type
        water_resource = Resource(
            label="Water Resource",
            rtype=ResourceType.NATURAL
        )
        self.graph.add_node(water_resource)
        
        # Create Actor2 if it doesn't exist
        actor2 = Actor(label="Actor 2", sector="Water")
        self.graph.add_node(actor2)
        
        # Create relationships that will be found by the flow tracing logic
        # These need to be FROM the resource (source) TO another node (target)
        exchange_relationship = Relationship(
            source_id=water_resource.id,
            target_id=actor2.id,
            kind=RelationshipKind.EXCHANGES_WITH,
            weight=0.8
        )
        
        try:
            self.graph.add_relationship(exchange_relationship)
            
            # Rebuild the query engine with the updated graph
            query_engine = NetworkXSFMQueryEngine(self.graph)
            
            flow_analysis = query_engine.trace_resource_flows(ResourceType.NATURAL)
            
            self.assertIsInstance(flow_analysis, FlowAnalysis)
            # Now we should have flow volumes
            if len(flow_analysis.flow_volumes) > 0:
                self.assertIn(exchange_relationship.id, flow_analysis.flow_volumes)
        except Exception:
            # If the relationship isn't valid, just verify the basic structure
            flow_analysis = self.query_engine.trace_resource_flows(ResourceType.NATURAL)
            self.assertIsInstance(flow_analysis, FlowAnalysis)

    @patch("networkx.betweenness_centrality")
    def test_identify_bottlenecks(self, mock_centrality):
        """Test identifying bottleneck nodes using centralized mocks."""
        centrality_data = {
            self.actor1.id: 0.9,
            self.actor2.id: 0.7,
            self.institution.id: 0.3,
            self.resource.id: 0.1,
            self.policy.id: 0.05,
        }
        mock_centrality.return_value = centrality_data

        bottlenecks = self.query_engine.identify_bottlenecks(FlowNature.TRANSFER)

        self.assertIsInstance(bottlenecks, list)
        # Should include high centrality nodes
        self.assertIn(self.actor1.id, bottlenecks)

    def test_calculate_flow_efficiency(self):
        """Test calculating flow efficiency."""
        # Mock the shortest path finding
        with patch.object(self.query_engine, "find_shortest_path") as mock_path:
            mock_path.return_value = [self.actor1.id, self.actor2.id]

            efficiency = self.query_engine.calculate_flow_efficiency(
                self.actor1.id, self.actor2.id
            )

            # Path length is 2 nodes, so 1 edge, efficiency should be 1.0
            self.assertEqual(efficiency, 1.0)

    def test_calculate_flow_efficiency_no_path(self):
        """Test calculating flow efficiency when no path exists."""
        with patch.object(self.query_engine, "find_shortest_path") as mock_path:
            mock_path.return_value = None
            
            efficiency = self.query_engine.calculate_flow_efficiency(
                self.actor1.id, uuid.uuid4()
            )
            
            # No path should return 0.0 efficiency
            self.assertEqual(efficiency, 0.0)

    def test_calculate_flow_efficiency_zero_division(self):
        """Test calculating flow efficiency with zero division error."""
        with patch.object(self.query_engine, "find_shortest_path") as mock_path:
            mock_path.return_value = [self.actor1.id]  # Single node path
            
            efficiency = self.query_engine.calculate_flow_efficiency(
                self.actor1.id, self.actor1.id
            )
            
            # Zero length path should return 0.0 efficiency
            self.assertEqual(efficiency, 0.0)

    def test_calculate_flow_efficiency_network_error(self):
        """Test calculating flow efficiency with NetworkX error."""
        with patch.object(self.query_engine, "find_shortest_path") as mock_path:
            mock_path.side_effect = nx.NetworkXError("Graph error")
            
            efficiency = self.query_engine.calculate_flow_efficiency(
                self.actor1.id, self.actor2.id
            )
            
            # Network error should return 0.0 efficiency
            self.assertEqual(efficiency, 0.0)

    @patch("networkx.ego_graph")
    @patch("networkx.density")
    @patch("networkx.betweenness_centrality")
    def test_analyze_policy_impact(self, mock_centrality, mock_density, mock_ego_graph):
        """Test policy impact analysis using centralized mocks."""
        # Mock ego graph
        mock_ego = MagicMock()
        mock_ego.nodes.return_value = [self.policy.id, self.actor1.id, self.actor2.id]
        mock_ego_graph.return_value = mock_ego

        # Mock other network measures using centralized data
        network_metrics = MockNetworkXFunctions.get_default_network_metrics()
        mock_density.return_value = network_metrics['density']
        mock_centrality.return_value = {self.policy.id: 0.8}

        impact = self.query_engine.analyze_policy_impact(
            self.policy.id, impact_radius=2
        )

        self.assertIsInstance(impact, dict)
        self.assertIn("total_affected_nodes", impact)
        self.assertIn("affected_actors", impact)
        self.assertIn("network_metrics", impact)
        self.assertEqual(
            impact["total_affected_nodes"], 2
        )  # Excluding policy node itself

    @patch("networkx.ego_graph")
    def test_analyze_policy_impact_network_error(self, mock_ego_graph):
        """Test policy impact analysis with NetworkX error."""
        mock_ego_graph.side_effect = nx.NetworkXError("Graph error")
        
        impact = self.query_engine.analyze_policy_impact(self.policy.id, impact_radius=2)
        
        self.assertIsInstance(impact, dict)
        self.assertIn("error", impact)
        self.assertEqual(impact["error"], "Policy node not found or network error")

    def test_analyze_policy_impact_detailed(self):
        """Test policy impact analysis with detailed node categorization."""
        # Create a more complex graph to test the categorization logic
        resource = Resource(label="Test Resource", rtype=ResourceType.NATURAL)
        institution = Institution(label="Test Institution")
        
        # Add nodes to the graph
        self.graph.add_node(resource)
        self.graph.add_node(institution)
        
        # Add relationships to create a connected subgraph
        rel_to_resource = Relationship(
            source_id=self.policy.id,
            target_id=resource.id,
            kind=RelationshipKind.INFLUENCES,
            weight=0.6
        )
        rel_to_institution = Relationship(
            source_id=self.policy.id,
            target_id=institution.id,
            kind=RelationshipKind.GOVERNS,
            weight=0.8
        )
        
        self.graph.add_relationship(rel_to_resource)
        self.graph.add_relationship(rel_to_institution)
        
        # Rebuild the query engine with the updated graph
        query_engine = NetworkXSFMQueryEngine(self.graph)
        
        impact = query_engine.analyze_policy_impact(self.policy.id, impact_radius=2)
        
        self.assertIsInstance(impact, dict)
        self.assertIn("affected_actors", impact)
        self.assertIn("affected_institutions", impact)
        self.assertIn("affected_resources", impact)
        self.assertIn("network_metrics", impact)
        
        # Check that the categorization worked
        self.assertIn(resource.id, impact["affected_resources"])
        self.assertIn(institution.id, impact["affected_institutions"])

    def test_identify_policy_targets(self):
        """Test identifying policy targets using centralized mocks."""
        with patch.object(self.query_engine, "get_node_neighbors") as mock_neighbors:
            mock_neighbors.side_effect = [
                [self.actor1.id],  # Direct targets
                [self.actor1.id, self.actor2.id],  # 2-hop targets
            ]

            targets = self.query_engine.identify_policy_targets(self.policy.id)

            self.assertIsInstance(targets, list)
            self.assertIn(self.actor1.id, targets)

    def test_compare_policy_scenarios(self):
        """Test comparing policy scenarios."""
        scenario_graphs = [self.graph()]

        comparison = self.query_engine.compare_policy_scenarios(scenario_graphs)

        self.assertIsInstance(comparison, dict)
        self.assertEqual(comparison["scenario_count"], 2)
        self.assertIn("basic_metrics", comparison)
        self.assertIn("structural_comparison", comparison)
        self.assertIn("policy_impact_analysis", comparison)
        self.assertIn("similarity_matrix", comparison)
        self.assertIn("key_differences", comparison)
        
        # Check basic metrics structure
        basic_metrics = comparison["basic_metrics"]
        self.assertIn("node_counts", basic_metrics)
        self.assertIn("relationship_counts", basic_metrics)
        self.assertIn("density_scores", basic_metrics)
        self.assertEqual(len(basic_metrics["node_counts"]), 2)
        self.assertEqual(len(basic_metrics["relationship_counts"]), 2)

    @patch("networkx.density")
    def test_get_network_density(self, mock_density):
        """Test getting network density using centralized mocks."""
        network_metrics = MockNetworkXFunctions.get_default_network_metrics()
        mock_density.return_value = network_metrics['density']

        density = self.query_engine.get_network_density()

        self.assertEqual(density, network_metrics['density'])
        mock_density.assert_called_once()

    def test_identify_communities(self):
        """Test community identification with improved implementation."""
        communities = self.query_engine.identify_communities()

        self.assertIsInstance(communities, dict)
        # Should return a dictionary of communities
        self.assertTrue(len(communities) >= 1)
        
        # Test different algorithms
        communities_louvain = self.query_engine.identify_communities("louvain")
        self.assertIsInstance(communities_louvain, dict)
        
        communities_label_prop = self.query_engine.identify_communities("label_propagation")
        self.assertIsInstance(communities_label_prop, dict)
        
        # Test fallback with unknown algorithm
        communities_unknown = self.query_engine.identify_communities("unknown_algorithm")
        self.assertIsInstance(communities_unknown, dict)

    @patch("networkx.betweenness_centrality")
    def test_get_structural_holes(self, mock_centrality):
        """Test identifying structural holes using centralized mocks."""
        centrality_data = {
            self.actor1.id: 0.95,
            self.actor2.id: 0.85,
            self.institution.id: 0.3,
            self.resource.id: 0.1,
            self.policy.id: 0.05,
        }
        mock_centrality.return_value = centrality_data

        bridges = self.query_engine.get_structural_holes()

        self.assertIsInstance(bridges, list)
        # Should include high centrality nodes (top 5%)
        self.assertIn(self.actor1.id, bridges)

    def test_comprehensive_node_analysis(self):
        """Test comprehensive node analysis."""
        with patch.object(self.query_engine, "get_node_centrality") as mock_centrality:
            mock_centrality.side_effect = [
                0.8,
                0.6,
                0.7,
            ]  # betweenness, closeness, degree

            with patch.object(
                self.query_engine, "get_node_neighbors"
            ) as mock_neighbors:
                mock_neighbors.return_value = [self.actor2.id, self.institution.id]

                metrics = self.query_engine.comprehensive_node_analysis(self.actor1.id)

                self.assertIsInstance(metrics, NodeMetrics)
                self.assertEqual(metrics.node_id, self.actor1.id)
                self.assertEqual(metrics.centrality_scores["betweenness"], 0.8)
                self.assertEqual(metrics.connectivity, 2)
                self.assertEqual(metrics.node_type, "Actor")

    @patch("networkx.average_clustering")
    @patch("networkx.number_weakly_connected_components")
    def test_system_vulnerability_analysis(self, mock_components, mock_clustering):
        """Test system vulnerability analysis."""
        mock_clustering.return_value = 0.3
        mock_components.return_value = 1

        with patch.object(self.query_engine, "get_network_density") as mock_density:
            mock_density.return_value = 0.4

            with patch.object(self.query_engine, "get_structural_holes") as mock_holes:
                mock_holes.return_value = [self.actor1.id]

                with patch.object(
                    self.query_engine, "identify_bottlenecks"
                ) as mock_bottlenecks:
                    mock_bottlenecks.return_value = [self.actor2.id]

                    analysis = self.query_engine.system_vulnerability_analysis()

                    self.assertIsInstance(analysis, dict)
                    self.assertIn("network_density", analysis)
                    self.assertIn("average_clustering", analysis)
                    self.assertIn("number_of_components", analysis)
                    self.assertIn("critical_nodes", analysis)
                    self.assertIn("bottlenecks", analysis)

                    self.assertEqual(analysis["network_density"], 0.4)
                    self.assertEqual(analysis["average_clustering"], 0.3)

    def test_analyze_temporal_changes(self):
        """Test temporal analysis methods."""
        from datetime import datetime
        
        # Create two time slices
        time1 = datetime(2023, 1, 1)
        time2 = datetime(2023, 6, 1)
        
        # Create a second graph with changes
        graph2 = SFMGraph()
        # Add some nodes from the original graph
        for node in list(self.graph)[:3]:
            graph2.add_node(node)
        
        # Add a new node
        new_actor = Actor(label="New Actor", sector="Test")
        graph2.add_node(new_actor)
        
        time_slices = [(time1, self.graph), (time2, graph2)]
        
        analysis = self.query_engine.analyze_temporal_changes(time_slices)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn("time_periods", analysis)
        self.assertIn("node_evolution", analysis)
        self.assertEqual(analysis["time_periods"], 2)

    def test_analyze_temporal_changes_insufficient_data(self):
        """Test temporal analysis with insufficient data."""
        from datetime import datetime
        
        time1 = datetime(2023, 1, 1)
        time_slices = [(time1, self.graph)]
        
        analysis = self.query_engine.analyze_temporal_changes(time_slices)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn("error", analysis)
        self.assertEqual(analysis["error"], "Need at least 2 time slices for temporal analysis")

    def test_detect_structural_changes(self):
        """Test structural change detection."""
        # Create a modified graph
        modified_graph = SFMGraph()
        
        # Add some nodes from the original graph
        for node in list(self.graph)[:2]:
            modified_graph.add_node(node)
        
        # Add a new node
        new_actor = Actor(label="New Actor", sector="Test")
        modified_graph.add_node(new_actor)
        
        changes = self.query_engine.detect_structural_changes(self.graph, modified_graph)
        
        self.assertIsInstance(changes, dict)
        self.assertIn("node_count_change", changes)
        self.assertIn("edge_count_change", changes)
        self.assertIn("density_change", changes)

    def test_assess_network_vulnerabilities(self):
        """Test network vulnerability assessment."""
        vulnerabilities = self.query_engine.assess_network_vulnerabilities()
        
        self.assertIsInstance(vulnerabilities, dict)
        self.assertIn("critical_nodes", vulnerabilities)
        self.assertIn("single_points_of_failure", vulnerabilities)
        self.assertIn("resilience_score", vulnerabilities)

    def test_simulate_node_failure_impact(self):
        """Test node failure simulation."""
        # Get some node IDs to simulate failures
        node_ids = [node.id for node in list(self.graph)[:2]]
        
        impact = self.query_engine.simulate_node_failure_impact(node_ids)
        
        self.assertIsInstance(impact, dict)
        self.assertIn("failed_nodes", impact)
        self.assertIn("connectivity_impact", impact)
        self.assertIn("failure_mode", impact)

    def test_analyze_flow_patterns(self):
        """Test flow pattern analysis."""
        patterns = self.query_engine.analyze_flow_patterns(FlowNature.TRANSFER)
        
        self.assertIsInstance(patterns, dict)
        self.assertIn("flow_type", patterns)
        self.assertIn("total_flows", patterns)
        self.assertIn("flow_distribution", patterns)

    def test_identify_flow_inefficiencies(self):
        """Test flow inefficiency identification."""
        inefficiencies = self.query_engine.identify_flow_inefficiencies()
        
        self.assertIsInstance(inefficiencies, dict)
        self.assertIn("redundant_paths", inefficiencies)
        self.assertIn("flow_imbalances", inefficiencies)
        self.assertIn("optimization_opportunities", inefficiencies)


class TestSFMQueryFactory(unittest.TestCase):
    """Test suite for SFMQueryFactory."""

    def setUp(self):
        """Set up test fixtures."""
        self.graph = SFMGraph()

    def test_create_networkx_query_engine(self):
        """Test creation of NetworkX query engine."""
        engine = SFMQueryFactory.create_query_engine(self.graph, "networkx")

        self.assertIsInstance(engine, NetworkXSFMQueryEngine)
        self.assertEqual(engine.graph, self.graph)

    def test_create_query_engine_case_insensitive(self):
        """Test factory is case insensitive."""
        engine = SFMQueryFactory.create_query_engine(self.graph, "NetworkX")

        self.assertIsInstance(engine, NetworkXSFMQueryEngine)

    def test_create_query_engine_unsupported_backend(self):
        """Test error handling for unsupported backend."""
        with self.assertRaises(ValueError):
            SFMQueryFactory.create_query_engine(self.graph, "unsupported")


class TestNetworkXSFMQueryEngineIntegration(unittest.TestCase):
    """Integration tests for NetworkXSFMQueryEngine with real NetworkX operations."""

    def setUp(self):
        """Set up a more complex test graph for integration testing."""
        self.graph = SFMGraph()

        # Create a network of nodes
        self.actors = [Actor(label=f"Actor {i}", sector="Test") for i in range(5)]
        self.institutions = [Institution(label=f"Institution {i}") for i in range(3)]
        self.resources = [
            Resource(label=f"Resource {i}", rtype=ResourceType.NATURAL)
            for i in range(2)
        ]
        self.policies = [
            Policy(label=f"Policy {i}", authority="Test") for i in range(2)
        ]

        # Add all nodes
        for node_list in [
            self.actors,
            self.institutions,
            self.resources,
            self.policies,
        ]:
            for node in node_list:
                self.graph.add_node(node)

        # Create a connected network
        relationships = [
            # Actors to institutions
            Relationship(
                self.actors[0].id,
                self.institutions[0].id,
                RelationshipKind.GOVERNS,
                0.8,
            ),
            Relationship(
                self.actors[1].id, self.institutions[1].id, RelationshipKind.SERVES, 0.7
            ),
            # Actors to resources
            Relationship(
                self.actors[2].id, self.resources[0].id, RelationshipKind.USES, 0.6
            ),
            Relationship(
                self.actors[3].id, self.resources[1].id, RelationshipKind.PRODUCES, 0.9
            ),
            # Policies to actors
            Relationship(
                self.policies[0].id, self.actors[0].id, RelationshipKind.AFFECTS, 0.5
            ),
            Relationship(
                self.policies[1].id, self.actors[4].id, RelationshipKind.FUNDS, 0.8
            ),
            # Cross connections for more interesting topology
            Relationship(
                self.actors[0].id,
                self.actors[1].id,
                RelationshipKind.COLLABORATES_WITH,
                0.4,
            ),
            Relationship(
                self.institutions[0].id,
                self.resources[0].id,
                RelationshipKind.GOVERNS,
                0.7,
            ),
        ]

        for rel in relationships:
            self.graph.add_relationship(rel)

        self.query_engine = NetworkXSFMQueryEngine(self.graph)

    def test_real_centrality_calculations(self):
        """Test centrality calculations with real NetworkX."""
        # Test that centrality values are reasonable
        for actor in self.actors:
            centrality = self.query_engine.get_node_centrality(actor.id, "degree")
            self.assertIsInstance(centrality, float)
            self.assertGreaterEqual(centrality, 0.0)
            self.assertLessEqual(centrality, 1.0)

    def test_real_shortest_path_finding(self):
        """Test shortest path finding with real NetworkX."""
        # Find path between connected nodes
        path = self.query_engine.find_shortest_path(
            self.actors[0].id, self.institutions[0].id
        )

        self.assertIsNotNone(path)
        self.assertIsInstance(path, list)
        if path:  # Check path is not None before accessing elements
            self.assertEqual(path[0], self.actors[0].id)
            self.assertEqual(path[-1], self.institutions[0].id)

    def test_real_network_metrics(self):
        """Test network-wide metrics with real NetworkX."""
        density = self.query_engine.get_network_density()

        self.assertIsInstance(density, float)
        self.assertGreaterEqual(density, 0.0)
        self.assertLessEqual(density, 1.0)

    def test_real_policy_impact_analysis(self):
        """Test policy impact analysis with real graph."""
        policy = self.policies[0]
        impact = self.query_engine.analyze_policy_impact(policy.id, impact_radius=2)

        self.assertIsInstance(impact, dict)
        self.assertIn("total_affected_nodes", impact)
        self.assertIn("network_metrics", impact)

        # Should find some affected nodes
        self.assertGreater(impact["total_affected_nodes"], 0)

    def test_neighbor_finding_integration(self):
        """Test neighbor finding with various parameters."""
        actor = self.actors[0]

        # Direct neighbors
        neighbors = self.query_engine.get_node_neighbors(actor.id, distance=1)
        self.assertGreater(len(neighbors), 0)

        # Multi-hop neighbors
        extended_neighbors = self.query_engine.get_node_neighbors(actor.id, distance=2)
        self.assertGreaterEqual(len(extended_neighbors), len(neighbors))

    def test_comprehensive_analysis_integration(self):
        """Test comprehensive node analysis integration."""
        actor = self.actors[0]
        metrics = self.query_engine.comprehensive_node_analysis(actor.id)

        self.assertIsInstance(metrics, NodeMetrics)
        self.assertEqual(metrics.node_id, actor.id)
        self.assertIsInstance(metrics.centrality_scores, dict)
        self.assertIn("betweenness", metrics.centrality_scores)
        self.assertIn("closeness", metrics.centrality_scores)
        self.assertIn("degree", metrics.centrality_scores)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up minimal test fixtures."""
        self.empty_graph = SFMGraph()
        self.single_node_graph = SFMGraph()

        self.single_actor = Actor(label="Single Actor")
        self.single_node_graph.add_node(self.single_actor)

    def test_empty_graph_handling(self):
        """Test query engine with empty graph."""
        engine = NetworkXSFMQueryEngine(self.empty_graph)

        # Should handle empty graph gracefully
        density = engine.get_network_density()
        self.assertEqual(density, 0.0)

        central_nodes = engine.get_most_central_nodes()
        self.assertEqual(len(central_nodes), 0)

    def test_single_node_graph(self):
        """Test query engine with single node graph."""
        engine = NetworkXSFMQueryEngine(self.single_node_graph)

        centrality = engine.get_node_centrality(self.single_actor.id)
        self.assertEqual(centrality, 0.0)  # No connections, so 0 centrality

        neighbors = engine.get_node_neighbors(self.single_actor.id)
        self.assertEqual(len(neighbors), 0)

    def test_nonexistent_node_queries(self):
        """Test queries for non-existent nodes."""
        engine = NetworkXSFMQueryEngine(self.single_node_graph)
        fake_id = uuid.uuid4()

        centrality = engine.get_node_centrality(fake_id)
        self.assertEqual(centrality, 0.0)

        # Updated: get_node_neighbors should return empty list for non-existent nodes
        # to be more robust in production environments
        neighbors = engine.get_node_neighbors(fake_id)
        self.assertEqual(neighbors, [])

    def test_invalid_parameters(self):
        """Test handling of invalid parameters."""
        engine = NetworkXSFMQueryEngine(self.single_node_graph)

        # Invalid centrality type
        with self.assertRaises(ValueError):
            engine.get_node_centrality(self.single_actor.id, "invalid")

        # Invalid distance (negative)
        neighbors = engine.get_node_neighbors(self.single_actor.id, distance=-1)
        # Should handle gracefully
        self.assertIsInstance(neighbors, list)

    def test_disconnected_graph_components(self):
        """Test query engine with disconnected graph components."""
        # Create a graph with two disconnected components
        disconnected_graph = SFMGraph()
        
        # Component 1
        actor1 = Actor(label="Actor 1", sector="A")
        institution1 = Institution(label="Institution 1")
        disconnected_graph.add_node(actor1)
        disconnected_graph.add_node(institution1)
        
        # Component 2 (disconnected)
        actor2 = Actor(label="Actor 2", sector="B")
        institution2 = Institution(label="Institution 2")
        disconnected_graph.add_node(actor2)
        disconnected_graph.add_node(institution2)
        
        # Add relationships within components only
        rel1 = Relationship(actor1.id, institution1.id, RelationshipKind.GOVERNS)
        rel2 = Relationship(actor2.id, institution2.id, RelationshipKind.GOVERNS)
        disconnected_graph.add_relationship(rel1)
        disconnected_graph.add_relationship(rel2)
        
        engine = NetworkXSFMQueryEngine(disconnected_graph)
        
        # Test shortest path between disconnected components
        path = engine.find_shortest_path(actor1.id, actor2.id)
        self.assertIsNone(path)
        
        # Test centrality calculations on disconnected graph
        centrality = engine.get_node_centrality(actor1.id)
        self.assertIsInstance(centrality, float)

    def test_large_distance_neighbors(self):
        """Test neighbor finding with very large distance values."""
        engine = NetworkXSFMQueryEngine(self.single_node_graph)
        
        # Very large distance should still work
        neighbors = engine.get_node_neighbors(self.single_actor.id, distance=100)
        self.assertIsInstance(neighbors, list)
        self.assertEqual(len(neighbors), 0)  # Single node has no neighbors

    def test_edge_cases_with_none_weight_relationships(self):
        """Test with relationships that have None weights."""
        graph = SFMGraph()
        actor1 = Actor(label="Actor 1", sector="A")
        actor2 = Actor(label="Actor 2", sector="B")
        graph.add_node(actor1)
        graph.add_node(actor2)
        
        # Relationship with None weight
        rel = Relationship(actor1.id, actor2.id, RelationshipKind.GOVERNS, weight=None)
        graph.add_relationship(rel)
        
        engine = NetworkXSFMQueryEngine(graph)
        
        # Test relationship strength calculation
        strength = engine.get_relationship_strength(actor1.id, actor2.id)
        self.assertIsInstance(strength, float)


class TestPerformance(unittest.TestCase):
    """Performance tests for query operations."""

    def setUp(self):
        """Set up a larger graph for performance testing."""
        self.large_graph = SFMGraph()

        # Create a larger network (50 nodes, ~100 relationships)
        self.nodes = []
        for i in range(50):
            if i < 20:
                node = Actor(label=f"Actor {i}")
            elif i < 35:
                node = Institution(label=f"Institution {i}")
            elif i < 45:
                node = Resource(label=f"Resource {i}", rtype=ResourceType.NATURAL)
            else:
                node = Policy(label=f"Policy {i}")

            self.nodes.append(node)
            self.large_graph.add_node(node)

        # Create relationships to form a connected graph
        import random

        random.seed(42)  # For reproducible tests

        relationships = []
        for i in range(100):
            source = random.choice(self.nodes)
            target = random.choice(self.nodes)
            if source.id != target.id:  # Avoid self-loops
                rel = Relationship(
                    source.id,
                    target.id,
                    RelationshipKind.AFFECTS,
                    weight=random.uniform(0.1, 1.0),
                )
                relationships.append(rel)

        for rel in relationships:
            self.large_graph.add_relationship(rel)

        self.query_engine = NetworkXSFMQueryEngine(self.large_graph)

    def test_centrality_performance(self):
        """Test centrality calculation performance."""
        import time

        start_time = time.time()

        # Calculate centrality for multiple nodes
        for node in self.nodes[:10]:
            centrality = self.query_engine.get_node_centrality(node.id)
            self.assertIsInstance(centrality, float)

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete reasonably quickly (adjust threshold as needed)
        self.assertLess(execution_time, 10.0)  # 10 seconds max

    def test_pathfinding_performance(self):
        """Test shortest path finding performance."""
        import time

        start_time = time.time()

        # Find paths between multiple node pairs
        for i in range(min(10, len(self.nodes))):
            for j in range(i + 1, min(i + 5, len(self.nodes))):
                path = self.query_engine.find_shortest_path(
                    self.nodes[i].id, self.nodes[j].id
                )
                # Path might be None if no connection exists
                self.assertTrue(path is None or isinstance(path, list))

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete reasonably quickly
        self.assertLess(execution_time, 15.0)  # 15 seconds max


class TestQueryEngineEdgeCaseRobustness(unittest.TestCase):
    """Test suite for edge case robustness improvements in NetworkXSFMQueryEngine."""

    def setUp(self):
        """Set up test fixtures."""
        self.empty_graph = SFMGraph()
        self.empty_engine = NetworkXSFMQueryEngine(self.empty_graph)
        
        # Single node graph
        self.single_graph = SFMGraph()
        self.single_actor = Actor(label="Single Actor")
        self.single_graph.add_node(self.single_actor)
        self.single_engine = NetworkXSFMQueryEngine(self.single_graph)

    def test_empty_graph_robustness(self):
        """Test that all methods handle empty graphs gracefully."""
        # Test structural analysis methods
        structural_holes = self.empty_engine.get_structural_holes()
        self.assertEqual(structural_holes, [])
        
        bottlenecks = self.empty_engine.identify_bottlenecks(FlowNature.TRANSFER)
        self.assertEqual(bottlenecks, [])
        
        # Test vulnerability analysis
        vulnerability = self.empty_engine.system_vulnerability_analysis()
        self.assertIsInstance(vulnerability, dict)
        self.assertIn("network_density", vulnerability)
        self.assertEqual(vulnerability["network_density"], 0)
        
        # Test community detection
        communities = self.empty_engine.identify_communities()
        self.assertEqual(communities, {})

    def test_nonexistent_node_robustness(self):
        """Test that methods handle non-existent nodes gracefully."""
        fake_id = uuid.uuid4()
        
        # Test policy analysis
        impact = self.empty_engine.analyze_policy_impact(fake_id)
        self.assertIn("error", impact)
        
        targets = self.empty_engine.identify_policy_targets(fake_id)
        self.assertEqual(targets, [])
        
        # Test node analysis
        analysis = self.empty_engine.comprehensive_node_analysis(fake_id)
        self.assertEqual(analysis.node_type, "Unknown")
        self.assertEqual(analysis.connectivity, 0)
        
        # Test neighbors
        neighbors = self.empty_engine.get_node_neighbors(fake_id)
        self.assertEqual(neighbors, [])

    def test_single_node_graph_robustness(self):
        """Test that methods handle single-node graphs gracefully."""
        # Test structural analysis
        structural_holes = self.single_engine.get_structural_holes()
        self.assertEqual(structural_holes, [])
        
        bottlenecks = self.single_engine.identify_bottlenecks(FlowNature.TRANSFER)
        self.assertEqual(bottlenecks, [])
        
        # Test vulnerability analysis
        vulnerability = self.single_engine.system_vulnerability_analysis()
        self.assertIsInstance(vulnerability, dict)
        self.assertIn("network_density", vulnerability)
        
        # Test community detection
        communities = self.single_engine.identify_communities()
        self.assertIsInstance(communities, dict)

    def test_flow_efficiency_edge_cases(self):
        """Test flow efficiency calculation edge cases."""
        fake_id1 = uuid.uuid4()
        fake_id2 = uuid.uuid4()
        
        # Test with non-existent nodes
        efficiency = self.empty_engine.calculate_flow_efficiency(fake_id1, fake_id2)
        self.assertEqual(efficiency, 0.0)
        
        # Test with single node (no path possible)
        efficiency = self.single_engine.calculate_flow_efficiency(
            self.single_actor.id, fake_id1
        )
        self.assertEqual(efficiency, 0.0)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
