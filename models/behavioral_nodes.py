"""
Behavioral and cognitive nodes for SFM modeling.

This module defines nodes related to behavioral patterns, cognitive frameworks,
value systems, and change processes in the Social Fabric Matrix.

Code Quality Status:
- Pylint: No warnings or errors
- Flake8: No warnings or errors
- Black: Properly formatted
- MyPy: No type errors
- Last scanned: 2025-07-16
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from models.base_nodes import Node
from models.meta_entities import TimeSlice
from models.metadata_models import TemporalDynamics
from models.sfm_enums import (
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
    legitimacy_source: Optional[LegitimacySource] = None  # Weber's authority types


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

    change_type: ChangeType = (
        ChangeType.EVOLUTIONARY
    )  # evolutionary, revolutionary, cyclical
    change_agents: List[uuid.UUID] = field(default_factory=lambda: [])
    resistance_factors: List[uuid.UUID] = field(default_factory=lambda: [])
    change_trajectory: List[TimeSlice] = field(default_factory=lambda: [])
    success_probability: Optional[float] = None
    temporal_dynamics: Optional[TemporalDynamics] = None  # Detailed change over time


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
