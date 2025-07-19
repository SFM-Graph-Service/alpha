"""
Mock factories and utilities for query engine testing.

Provides centralized mock implementations for SFM query engines,
NetworkX functions, and analysis results.
"""

import uuid
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

from graph.sfm_query import (
    SFMQueryEngine, NetworkXSFMQueryEngine, QueryResult, 
    NodeMetrics, FlowAnalysis, AnalysisType
)
from models import Node, Actor, Institution, Policy, Resource


class MockNetworkXFunctions:
    """Centralized mock behaviors for NetworkX functions."""
    
    @staticmethod
    def get_default_centrality_data():
        """Return standard centrality data for testing."""
        return {
            str(uuid.uuid4()): 0.75,
            str(uuid.uuid4()): 0.60,
            str(uuid.uuid4()): 0.45,
            str(uuid.uuid4()): 0.30
        }
    
    @staticmethod
    def get_default_shortest_path():
        """Return standard shortest path data for testing."""
        return [uuid.uuid4() for _ in range(3)]
    
    @staticmethod
    def get_default_network_metrics():
        """Return standard network metrics for testing."""
        return {
            'density': 0.35,
            'clustering': 0.62,
            'diameter': 4,
            'average_path_length': 2.3
        }


class MockQueryEngineFactory:
    """Factory for creating consistently configured mock query engines."""
    
    @classmethod
    def create_mock_networkx_engine(cls, graph=None):
        """Create a fully mocked NetworkX query engine."""
        mock_engine = MagicMock(spec=NetworkXSFMQueryEngine)
        
        # Configure node analysis methods
        mock_engine.get_node_centrality.return_value = MockNetworkXFunctions.get_default_centrality_data()
        mock_engine.get_most_central_nodes.return_value = [
            (str(uuid.uuid4()), 0.85),
            (str(uuid.uuid4()), 0.72), 
            (str(uuid.uuid4()), 0.64)
        ]
        mock_engine.get_node_neighbors.return_value = [str(uuid.uuid4()) for _ in range(3)]
        
        # Configure relationship analysis methods
        mock_engine.get_shortest_path.return_value = MockNetworkXFunctions.get_default_shortest_path()
        mock_engine.get_relationship_strength.return_value = 0.68
        mock_engine.get_connected_components.return_value = [
            [str(uuid.uuid4()) for _ in range(2)],
            [str(uuid.uuid4()) for _ in range(3)]
        ]
        
        # Configure flow analysis methods
        mock_engine.trace_resource_flows.return_value = FlowAnalysis(
            flow_paths=[MockNetworkXFunctions.get_default_shortest_path()],
            bottlenecks=[uuid.uuid4()],
            flow_volumes={uuid.uuid4(): 150.0},
            efficiency_metrics={"efficiency": 0.78, "throughput": 120.0}
        )
        mock_engine.analyze_flow_bottlenecks.return_value = [uuid.uuid4() for _ in range(2)]
        mock_engine.get_flow_efficiency.return_value = 0.82
        
        # Configure policy analysis methods
        mock_engine.analyze_policy_impact.return_value = QueryResult(
            data={
                "affected_nodes": 8,
                "impact_strength": 0.65,
                "policy_reach": 3
            },
            query_type=AnalysisType.POLICY_IMPACT.value,
            parameters={"policy_id": str(uuid.uuid4())},
            metadata={"analysis_date": "2025-06-26"},
            timestamp="2025-06-26T10:00:00Z"
        )
        mock_engine.get_policy_influence_network.return_value = [str(uuid.uuid4()) for _ in range(4)]
        
        # Configure network analysis methods
        mock_engine.get_network_density.return_value = 0.35
        mock_engine.get_clustering_coefficient.return_value = 0.62
        mock_engine.detect_communities.return_value = [
            [str(uuid.uuid4()) for _ in range(3)],
            [str(uuid.uuid4()) for _ in range(2)]
        ]
        
        # Set graph reference
        if graph:
            mock_engine.graph = graph
            
        return mock_engine
    
    @classmethod
    def create_mock_abstract_engine(cls):
        """Create a mock of the abstract base query engine."""
        mock_engine = MagicMock(spec=SFMQueryEngine)
        
        # Abstract methods should raise NotImplementedError by default
        mock_engine.get_node_centrality.side_effect = NotImplementedError
        mock_engine.get_most_central_nodes.side_effect = NotImplementedError
        mock_engine.get_node_neighbors.side_effect = NotImplementedError
        
        return mock_engine


@contextmanager
def mock_all_networkx_functions():
    """Context manager that mocks all commonly used NetworkX functions."""
    with patch.multiple(
        'networkx',
        betweenness_centrality=MagicMock(return_value=MockNetworkXFunctions.get_default_centrality_data()),
        closeness_centrality=MagicMock(return_value=MockNetworkXFunctions.get_default_centrality_data()),
        degree_centrality=MagicMock(return_value=MockNetworkXFunctions.get_default_centrality_data()),
        eigenvector_centrality=MagicMock(return_value=MockNetworkXFunctions.get_default_centrality_data()),
        pagerank=MagicMock(return_value=MockNetworkXFunctions.get_default_centrality_data()),
        shortest_path=MagicMock(return_value=MockNetworkXFunctions.get_default_shortest_path()),
        shortest_path_length=MagicMock(return_value=2),
        density=MagicMock(return_value=0.35),
        clustering=MagicMock(return_value=0.62),
        average_clustering=MagicMock(return_value=0.62),
        connected_components=MagicMock(return_value=[[str(uuid.uuid4()) for _ in range(3)]]),
        is_connected=MagicMock(return_value=True),
        diameter=MagicMock(return_value=4),
        average_shortest_path_length=MagicMock(return_value=2.3)
    ) as mocks:
        yield mocks


class MockQueryResults:
    """Predefined query results for consistent testing."""
    
    @staticmethod
    def centrality_analysis_result():
        return QueryResult(
            data={
                "centrality_scores": MockNetworkXFunctions.get_default_centrality_data(),
                "most_central": [(str(uuid.uuid4()), 0.85)],
                "analysis_type": "betweenness"
            },
            query_type=AnalysisType.CENTRALITY.value,
            parameters={"algorithm": "betweenness", "normalized": True},
            metadata={"node_count": 10},
            timestamp="2025-06-26T10:00:00Z"
        )
    
    @staticmethod
    def network_structure_result():
        return QueryResult(
            data=MockNetworkXFunctions.get_default_network_metrics(),
            query_type=AnalysisType.NETWORK_STRUCTURE.value,
            parameters={"include_clustering": True},
            metadata={"node_count": 10, "edge_count": 15},
            timestamp="2025-06-26T10:00:00Z"
        )
    
    @staticmethod
    def flow_analysis_result():
        return FlowAnalysis(
            flow_paths=[MockNetworkXFunctions.get_default_shortest_path()],
            bottlenecks=[uuid.uuid4()],
            flow_volumes={uuid.uuid4(): 200.0},
            efficiency_metrics={"efficiency": 0.85, "throughput": 160.0}
        )
