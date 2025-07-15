"""
Core data structures for modeling F. Gregory Hayden's Social Fabric Matrix (SFM).

This module serves as a unified import point for all SFM data structures.
The classes have been organized into smaller, focused modules:

- meta_entities: TimeSlice, SpatialUnit, Scenario
- base_nodes: Node (base class)
- core_nodes: Actor, Institution, Policy, Resource, Process, Flow, ValueFlow, GovernanceStructure
- specialized_nodes: BeliefSystem, TechnologySystem, Indicator, FeedbackLoop, SystemProperty, AnalyticalContext, PolicyInstrument
- behavioral_nodes: ValueSystem, CeremonialBehavior, InstrumentalBehavior, ChangeProcess, CognitiveFramework, BehavioralPattern
- metadata_models: TemporalDynamics, ValidationRule, ModelMetadata
- relationships: Relationship
- graph: SFMGraph, NetworkMetrics
"""

# Import all classes from the modularized structure
from core.meta_entities import TimeSlice, SpatialUnit, Scenario
from core.base_nodes import Node
from core.core_nodes import (
    Actor,
    Institution,
    Policy,
    Resource,
    Process,
    Flow,
    ValueFlow,
    GovernanceStructure)
from core.specialized_nodes import (
    BeliefSystem, TechnologySystem, Indicator, FeedbackLoop, SystemProperty,
    AnalyticalContext, PolicyInstrument
)
from core.behavioral_nodes import (
    ValueSystem, CeremonialBehavior, InstrumentalBehavior, ChangeProcess,
    CognitiveFramework, BehavioralPattern
)
from core.metadata_models import TemporalDynamics, ValidationRule, ModelMetadata
from core.relationships import Relationship
from core.graph import SFMGraph, NetworkMetrics

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
