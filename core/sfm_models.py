"""
Core data structures for modeling F. Gregory Hayden's Social Fabric Matrix (SFM).

This module serves as a backward compatibility layer, importing all SFM data structures
from their new organized locations:

- models/: Core data models and business entities
- graph/: Graph operations and network metrics
"""

# Import all classes from the reorganized structure for backward compatibility
from models.meta_entities import TimeSlice, SpatialUnit, Scenario
from models.base_nodes import Node
from models.core_nodes import (
    Actor, Institution, Policy, Resource, Process, Flow, ValueFlow, GovernanceStructure
)
from models.specialized_nodes import (
    BeliefSystem, TechnologySystem, Indicator, FeedbackLoop, SystemProperty,
    AnalyticalContext, PolicyInstrument
)
from models.behavioral_nodes import (
    ValueSystem, CeremonialBehavior, InstrumentalBehavior, ChangeProcess,
    CognitiveFramework, BehavioralPattern
)
from models.metadata_models import TemporalDynamics, ValidationRule, ModelMetadata
from models.relationships import Relationship
from graph.graph import SFMGraph, NetworkMetrics

# Public API
__all__ = [
    # Dimensional entities
    'TimeSlice',
    'SpatialUnit',
    'Scenario',
    # Base
    'Node',
    # Core nodes
    'Actor',
    'Institution',
    'Policy',
    'Resource',
    'Process',
    'Flow',
    'ValueFlow',
    'GovernanceStructure',
    # Specialized nodes
    'BeliefSystem',
    'TechnologySystem',
    'Indicator',
    'FeedbackLoop',
    'SystemProperty',
    'AnalyticalContext',
    'PolicyInstrument',
    # Behavioral nodes
    'ValueSystem',
    'CeremonialBehavior',
    'InstrumentalBehavior',
    'ChangeProcess',
    'CognitiveFramework',
    'BehavioralPattern',
    # Support classes
    'TemporalDynamics',
    'ValidationRule',
    'ModelMetadata',
    # Relationships and graph
    'Relationship',
    'SFMGraph',
    'NetworkMetrics',
]
