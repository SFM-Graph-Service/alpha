"""
Specialized nodes for SFM modeling.

This module defines specialized nodes for belief systems, technology systems,
indicators, feedback loops, and other specialized SFM entities.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

from models.base_nodes import Node
from models.metadata_models import TemporalDynamics, ValidationRule
from models.sfm_enums import (
    FeedbackPolarity,
    FeedbackType,
    TechnologyReadinessLevel,
    ValueCategory,
    SystemPropertyType,
    PolicyInstrumentType,
    EnumValidator,
)


@dataclass
class BeliefSystem(Node):
    """Cultural myths, ideology or worldview that guides decision-making."""

    strength: Optional[float] = None  # Cultural embeddedness (0-1)
    domain: Optional[str] = None  # Area of society where belief operates


@dataclass
class FeedbackLoop(Node):
    """Represents a feedback loop in the Social Fabric Matrix."""

    relationships: List[uuid.UUID] = field(default_factory=lambda: [])
    description: Optional[str] = None
    polarity: Optional[FeedbackPolarity] = None  # "reinforcing" or "balancing"
    strength: Optional[float] = None  # Measure of loop strength/impact
    type: Optional[FeedbackType] = None  # e.g. "positive", "negative", "neutral"


@dataclass
class TechnologySystem(Node):
    """Coherent system of techniques, tools and knowledge."""

    maturity: Optional[TechnologyReadinessLevel] = None  # Technology readiness level
    compatibility: Dict[str, float] = field(default_factory=lambda: {})  # Fit with other systems


@dataclass
class Indicator(Node):
    """Measurable proxy for system performance."""

    value_category: Optional[ValueCategory] = (
        None  # Non-default field moved to the beginning
    )
    measurement_unit: Optional[str] = None  # Non-default field moved to the beginning
    current_value: Optional[float] = None
    target_value: Optional[float] = None
    threshold_values: Dict[str, float] = field(default_factory=lambda: {})
    temporal_dynamics: Optional[TemporalDynamics] = None  # Track changes over time

    def __post_init__(self) -> None:
        """Validate indicator configuration after initialization."""
        # Validate value category context if measurement unit suggests measurement type
        if self.value_category and self.measurement_unit:
            # Infer measurement context from measurement unit
            measurement_context = "quantitative"  # Default assumption
            if any(qual_indicator in self.measurement_unit.lower() for qual_indicator in
                   ['scale', 'rating', 'level', 'score', 'index']):
                measurement_context = "qualitative"

            EnumValidator.validate_value_category_context(
                self.value_category, measurement_context
            )


@dataclass
class AnalyticalContext(Node):  # pylint: disable=too-many-instance-attributes
    """Contains metadata about analysis parameters and configuration."""

    methods_used: List[str] = field(default_factory=lambda: [])
    assumptions: Dict[str, str] = field(default_factory=lambda: {})
    data_sources: Dict[str, str] = field(default_factory=lambda: {})
    validation_approach: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    parameters: Dict[str, Any] = field(default_factory=lambda: {})
    validation_rules: List[ValidationRule] = field(default_factory=lambda: [])


@dataclass
class SystemProperty(Node):
    """Represents a system-level property or metric of the SFM."""

    property_type: SystemPropertyType = SystemPropertyType.STRUCTURAL
    value: Any = None
    unit: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    affected_nodes: List[uuid.UUID] = field(default_factory=lambda: [])  # Nodes that this property applies to
    contributing_relationships: List[uuid.UUID] = field(default_factory=lambda: [])  # Relationships that contribute to this property
    # id, name, and description are inherited from Node


@dataclass
class PolicyInstrument(Node):
    """Specific tools used to implement policies."""

    # regulatory, economic, voluntary, information
    instrument_type: PolicyInstrumentType = PolicyInstrumentType.REGULATORY
    target_behavior: Optional[str] = None
    compliance_mechanism: Optional[str] = None
    effectiveness_measure: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate policy instrument configuration after initialization."""
        # Validate instrument type if target behavior is specified
        if self.target_behavior:
            EnumValidator.validate_policy_instrument_combination(
                self.instrument_type, self.target_behavior
            )
