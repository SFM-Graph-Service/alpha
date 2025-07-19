"""
Core SFM nodes representing primary entities.

This module defines the core Social Fabric Matrix entities including actors,
institutions, resources, processes, and flows.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from models.base_nodes import Node
from models.meta_entities import TimeSlice, SpatialUnit, Scenario
from models.metadata_models import TemporalDynamics
from models.sfm_enums import (
    InstitutionLayer,
    ResourceType,
    FlowNature,
    FlowType,
    EnumValidator,
)


@dataclass
class Actor(Node):
    """Individuals, firms, agencies, communities."""

    legal_form: Optional[str] = None  # e.g. "Corporation", "Household"
    sector: Optional[str] = None  # NAICS or custom taxonomy

    # Additional SFM-relevant fields
    power_resources: Dict[str, float] = field(default_factory=lambda: {})
    decision_making_capacity: Optional[float] = None
    institutional_affiliations: List[uuid.UUID] = field(default_factory=lambda: [])
    cognitive_frameworks: List[uuid.UUID] = field(default_factory=lambda: [])
    behavioral_patterns: List[uuid.UUID] = field(default_factory=lambda: [])


@dataclass
class Institution(Node):
    """Rules-in-use, organizations, or informal norms (Hayden's three layers)."""

    layer: Optional[InstitutionLayer] = None

    # Additional fields for Hayden's framework
    formal_rules: List[str] = field(default_factory=lambda: [])
    informal_norms: List[str] = field(default_factory=lambda: [])
    enforcement_mechanisms: List[str] = field(default_factory=lambda: [])
    legitimacy_basis: Optional[str] = None
    change_resistance: Optional[float] = None
    path_dependencies: List[uuid.UUID] = field(default_factory=lambda: [])


@dataclass
class Policy(Institution):
    """Specific policy intervention or regulatory framework."""

    authority: Optional[str] = None  # Implementing body
    enforcement: Optional[float] = 0.0  # Strength of enforcement (0-1)
    target_sectors: List[str] = field(default_factory=lambda: [])


@dataclass
class Resource(Node):
    """Stock or asset available for use or transformation."""

    rtype: ResourceType = ResourceType.NATURAL
    unit: Optional[str] = None  # e.g. "tonnes", "person-hours"


@dataclass
class Process(Node):
    """
    Transformation activity that converts inputs to outputs
    (production, consumption, disposal).
    """

    technology: Optional[str] = None  # e.g. "EAF-Steel-2024"
    responsible_actor_id: Optional[str] = None  # Actor that controls the process


@dataclass
class Flow(Node):  # pylint: disable=too-many-instance-attributes
    """Edge-like node representing an actual quantified transfer of resources or value."""

    nature: FlowNature = FlowNature.TRANSFER
    quantity: Optional[float] = None
    unit: Optional[str] = None
    time: Optional[TimeSlice] = None
    space: Optional[SpatialUnit] = None
    scenario: Optional[Scenario] = None

    # Additional SFM-specific fields
    flow_type: FlowType = FlowType.MATERIAL  # material, energy, information, financial, social
    source_process_id: Optional[uuid.UUID] = None
    target_process_id: Optional[uuid.UUID] = None
    transformation_coefficient: Optional[float] = None
    loss_factor: Optional[float] = None  # inefficiencies, waste

    # Hayden's value theory integration
    ceremonial_component: Optional[float] = None
    instrumental_component: Optional[float] = None
    temporal_dynamics: Optional[TemporalDynamics] = None  # Change over time

    def __post_init__(self) -> None:
        """Validate flow nature and type combination after initialization."""
        # Validate flow nature and type combination
        EnumValidator.validate_flow_combination(self.nature, self.flow_type)


@dataclass
class ValueFlow(Flow):
    """Tracks value creation, capture, and distribution."""

    value_created: Optional[float] = None
    value_captured: Optional[float] = None
    beneficiary_actors: List[uuid.UUID] = field(default_factory=lambda: [])
    distributional_impact: Dict[str, float] = field(default_factory=lambda: {})


@dataclass
class GovernanceStructure(Institution):
    """Formal and informal governance arrangements."""

    decision_making_process: Optional[str] = None
    power_distribution: Dict[str, float] = field(default_factory=lambda: {})
    accountability_mechanisms: List[str] = field(default_factory=lambda: [])
