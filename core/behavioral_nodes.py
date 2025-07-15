"""
Behavioral and cognitive nodes for SFM modeling.

This module defines nodes related to behavioral patterns, cognitive frameworks,
value systems, and change processes in the Social Fabric Matrix.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.base_nodes import Node
from core.meta_entities import TimeSlice
from core.metadata_models import TemporalDynamics
from core.sfm_enums import (
    LegitimacySource,
    ChangeType,
    BehaviorPatternType,
)


@dataclass
class ValueSystem(Node):
    """Hierarchical value structure that guides institutional behavior."""

    parent_values: List[uuid.UUID] = field(default_factory=lambda: [])
    priority_weight: Optional[float] = None
    cultural_domain: Optional[str] = None
    # Weber's authority types
    legitimacy_source: Optional[LegitimacySource] = None


@dataclass
class CeremonialBehavior(Node):
    """Hayden's ceremonial behaviors that resist change."""

    rigidity_level: Optional[float] = None
    tradition_strength: Optional[float] = None
    resistance_to_change: Optional[float] = None


@dataclass
class InstrumentalBehavior(Node):
    """Problem-solving, adaptive behaviors."""

    efficiency_measure: Optional[float] = None
    adaptability_score: Optional[float] = None
    innovation_potential: Optional[float] = None


@dataclass
class ChangeProcess(Node):
    """Models institutional and technological change over time."""

    # evolutionary, revolutionary, cyclical
    change_type: ChangeType = ChangeType.EVOLUTIONARY
    change_agents: List[uuid.UUID] = field(default_factory=lambda: [])
    resistance_factors: List[uuid.UUID] = field(default_factory=lambda: [])
    change_trajectory: List[TimeSlice] = field(default_factory=lambda: [])
    success_probability: Optional[float] = None
    # Detailed change over time
    temporal_dynamics: Optional[TemporalDynamics] = None


@dataclass
class CognitiveFramework(Node):
    """Mental models and worldviews that shape perception."""

    framing_effects: Dict[str, str] = field(default_factory=lambda: {})
    cognitive_biases: List[str] = field(default_factory=lambda: [])
    information_filters: List[str] = field(default_factory=lambda: [])
    learning_capacity: Optional[float] = None


@dataclass
class BehavioralPattern(Node):
    """Recurring patterns of behavior in the social fabric."""

    # habitual, strategic, adaptive, resistant
    pattern_type: BehaviorPatternType = BehaviorPatternType.HABITUAL
    frequency: Optional[float] = None
    predictability: Optional[float] = None
    context_dependency: List[str] = field(default_factory=lambda: [])
