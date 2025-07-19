"""
Shafrom typing import Dict, List, Any, Optional
from datetime import datetime

from models import ( Actor, Institution, Policy, Resource, Process, Flow,
    Relationship, Node, RelationshipKind
)
from models.sfm_enums import ResourceType, InstitutionLayer, ValueCategory, FlowNatureures and utilities for SFM testing.

Provides common test data, mock graph creation, and utility functions
used across multiple test modules.
"""

import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from models import ( Actor, Institution, Policy, Resource, Process, Flow,
    Relationship, Node
)
from graph.graph import SFMGraph
from models.sfm_enums import ResourceType, InstitutionLayer, ValueCategory, RelationshipKind


def create_mock_graph() -> SFMGraph:
    """Create a mock SFM graph with sample data for testing."""
    graph = SFMGraph()
    
    # Add some sample nodes
    nodes = create_sample_nodes()
    for node in nodes:
        graph.add_node(node)
    
    # Add some sample relationships
    relationships = create_sample_relationships(nodes)
    for rel in relationships:
        graph.add_relationship(rel)
    
    return graph


def create_sample_nodes() -> List[Node]:
    """Create a set of sample nodes for testing."""
    nodes = []
    
    # Sample actors
    nodes.extend([
        Actor(
            label="Federal Government",
            sector="Government", 
            description="Primary government entity",
            meta={"level": "federal", "authority": "executive"}
        ),
        Actor(
            label="AgriCorp Inc",
            sector="Private",
            description="Large agricultural corporation",
            meta={"industry": "agriculture", "size": "large"}
        ),
        Actor(
            label="Environmental NGO",
            sector="Non-profit",
            description="Environmental advocacy organization",
            meta={"focus": "environment", "scope": "national"}
        )
    ])
    
    # Sample institutions
    nodes.extend([
        Institution(
            label="USDA",
            description="United States Department of Agriculture",
            layer=InstitutionLayer.FORMAL_RULE,
            meta={"type": "regulatory", "established": "1862"}
        ),
        Institution(
            label="Agricultural Trade Association",
            description="Industry trade association",
            layer=InstitutionLayer.ORGANIZATION,
            meta={"type": "industry_group", "membership": "private"}
        )
    ])
    
    # Sample policies
    nodes.extend([
        Policy(
            label="Farm Bill 2023",
            description="Agricultural policy legislation",
            authority="Federal Government",
            enforcement=0.8,
            target_sectors=["Agriculture", "Rural Development"],
            meta={"type": "legislation", "duration": "5_years"}
        ),
        Policy(
            label="Environmental Protection Standards",
            description="Environmental compliance requirements",
            authority="EPA",
            enforcement=0.9,
            target_sectors=["Agriculture", "Manufacturing"],
            meta={"type": "regulation", "scope": "national"}
        )
    ])
    
    # Sample resources
    nodes.extend([
        Resource(
            label="Agricultural Subsidies",
            description="Federal funding for farmers",
            rtype=ResourceType.FINANCIAL,
            meta={"amount": "billions", "annual": "true"}
        ),
        Resource(
            label="Farmland",
            description="Agricultural land resources",
            rtype=ResourceType.NATURAL,
            meta={"area": "millions_acres", "type": "cropland"}
        ),
        Resource(
            label="Agricultural Data",
            description="Crop and market information",
            rtype=ResourceType.INFORMATION,
            meta={"format": "digital", "frequency": "real_time"}
        )
    ])
    
    return nodes


def create_sample_relationships(nodes: Optional[List[Node]] = None) -> List[Relationship]:
    """Create sample relationships between nodes."""
    if nodes is None:
        nodes = create_sample_nodes()
    
    if len(nodes) < 3:
        return []
    
    relationships = []
    
    # Direct relationship: Government governs corporation
    relationships.append(Relationship(
        source_id=nodes[0].id,  # Federal Government
        target_id=nodes[1].id,  # AgriCorp Inc
        kind=RelationshipKind.GOVERNS,
        weight=0.8,
        meta={"type": "regulatory_oversight", "formal": "true"}
    ))
    
    # Government implements policy
    relationships.append(Relationship(
        source_id=nodes[0].id,  # Federal Government
        target_id=nodes[5].id if len(nodes) > 5 else nodes[0].id,  # Farm Bill 2023
        kind=RelationshipKind.IMPLEMENTS,
        weight=0.9,
        meta={"type": "policy_implementation", "formal": "true"}
    ))
    
    # Policy affects corporation
    relationships.append(Relationship(
        source_id=nodes[5].id if len(nodes) > 5 else nodes[0].id,  # Farm Bill 2023
        target_id=nodes[1].id,  # AgriCorp Inc
        kind=RelationshipKind.AFFECTS,
        weight=0.7,
        meta={"impact": "positive", "mechanism": "subsidies"}
    ))
    
    # Corporation uses resource
    relationships.append(Relationship(
        source_id=nodes[1].id,  # AgriCorp Inc
        target_id=nodes[7].id if len(nodes) > 7 else nodes[1].id,  # Agricultural Subsidies
        kind=RelationshipKind.USES,
        weight=0.8,
        meta={"dependency": "high", "frequency": "annual"}
    ))
    
    # NGO influences policy
    relationships.append(Relationship(
        source_id=nodes[2].id,  # Environmental NGO
        target_id=nodes[6].id if len(nodes) > 6 else nodes[2].id,  # Environmental Protection Standards
        kind=RelationshipKind.INFLUENCES,
        weight=0.6,
        meta={"method": "advocacy", "success_rate": "medium"}
    ))
    
    return relationships


def create_sample_flows(nodes: Optional[List[Node]] = None) -> List[Flow]:
    """Create sample flows between nodes."""
    if nodes is None:
        nodes = create_sample_nodes()
    
    if len(nodes) < 3:
        return []
    
    flows = []
    
    # Financial flow from government to corporation
    flows.append(Flow(
        label="Subsidy Flow",
        source_process_id=nodes[0].id,  # Federal Government
        target_process_id=nodes[1].id,  # AgriCorp Inc
        flow_type="subsidy",
        quantity=100000.0,
        meta={"currency": "USD", "frequency": "annual", "program": "crop_support"}
    ))
    
    # Information flow from corporation to government
    flows.append(Flow(
        label="Compliance Report Flow",
        source_process_id=nodes[1].id,  # AgriCorp Inc
        target_process_id=nodes[0].id,  # Federal Government
        flow_type="compliance_report",
        quantity=1.0,
        meta={"format": "digital", "frequency": "quarterly", "required": "true"}
    ))
    
    return flows


def get_sample_node_ids() -> Dict[str, uuid.UUID]:
    """Get a dictionary of sample node IDs for testing."""
    nodes = create_sample_nodes()
    return {
        "government": nodes[0].id,
        "corporation": nodes[1].id,
        "ngo": nodes[2].id,
        "institution": nodes[3].id if len(nodes) > 3 else nodes[0].id,
        "policy": nodes[5].id if len(nodes) > 5 else nodes[0].id,
        "resource": nodes[7].id if len(nodes) > 7 else nodes[0].id
    }


def get_sample_analysis_parameters() -> Dict[str, Any]:
    """Get sample parameters for analysis functions."""
    return {
        "centrality_type": "betweenness",
        "limit": 5,
        "normalized": True,
        "weight": "weight",
        "include_metadata": True,
        "time_period": "current",
        "analysis_depth": 3
    }


def create_mock_query_results() -> Dict[str, Any]:
    """Create mock query results for testing."""
    node_ids = get_sample_node_ids()
    
    return {
        "centrality_scores": {
            str(node_ids["government"]): 0.85,
            str(node_ids["corporation"]): 0.72,
            str(node_ids["ngo"]): 0.54
        },
        "shortest_paths": {
            f"{node_ids['government']}-{node_ids['corporation']}": [
                str(node_ids["government"]),
                str(node_ids["policy"]),
                str(node_ids["corporation"])
            ]
        },
        "network_metrics": {
            "density": 0.35,
            "clustering": 0.62,
            "diameter": 3,
            "average_path_length": 2.1,
            "connected_components": 1
        },
        "policy_impact": {
            "affected_nodes": 5,
            "impact_strength": 0.75,
            "policy_reach": 2,
            "secondary_effects": 3
        }
    }


class TestDataBuilder:
    """Builder class for creating consistent test data."""
    
    def __init__(self):
        self.nodes: List[Node] = []
        self.relationships: List[Relationship] = []
        self.flows: List[Flow] = []
    
    def add_actor(self, label: str, sector: str = "Test", **kwargs) -> 'TestDataBuilder':
        """Add an actor to the test data."""
        actor = Actor(label=label, sector=sector, **kwargs)
        self.nodes.append(actor)
        return self
    
    def add_institution(self, label: str, **kwargs) -> 'TestDataBuilder':
        """Add an institution to the test data."""
        institution = Institution(label=label, **kwargs)
        self.nodes.append(institution)
        return self
    
    def add_policy(self, label: str, authority: str = "Test Authority", **kwargs) -> 'TestDataBuilder':
        """Add a policy to the test data."""
        policy = Policy(label=label, authority=authority, **kwargs)
        self.nodes.append(policy)
        return self
    
    def add_resource(self, label: str, **kwargs) -> 'TestDataBuilder':
        """Add a resource to the test data."""
        resource = Resource(label=label, **kwargs)
        self.nodes.append(resource)
        return self
    
    def connect(self, source_idx: int, target_idx: int, 
                kind: RelationshipKind = RelationshipKind.AFFECTS, 
                weight: float = 0.5, **kwargs) -> 'TestDataBuilder':
        """Add a relationship between nodes by their indices."""
        if 0 <= source_idx < len(self.nodes) and 0 <= target_idx < len(self.nodes):
            rel = Relationship(
                source_id=self.nodes[source_idx].id,
                target_id=self.nodes[target_idx].id,
                kind=kind,
                weight=weight,
                **kwargs
            )
            self.relationships.append(rel)
        return self
    
    def build_graph(self) -> SFMGraph:
        """Build an SFM graph from the accumulated data."""
        graph = SFMGraph()
        
        for node in self.nodes:
            graph.add_node(node)
        
        for relationship in self.relationships:
            graph.add_relationship(relationship)
        
        return graph
    
    def get_nodes(self) -> List[Node]:
        """Get the list of nodes."""
        return self.nodes.copy()
    
    def get_relationships(self) -> List[Relationship]:
        """Get the list of relationships."""
        return self.relationships.copy()
