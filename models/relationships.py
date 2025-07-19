"""
Relationship entities for SFM modeling.

This module defines the relationship class that connects nodes in the
Social Fabric Matrix graph.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime

from models.meta_entities import TimeSlice, SpatialUnit, Scenario
from models.metadata_models import TemporalDynamics
from models.sfm_enums import RelationshipKind


@dataclass
class Relationship:  # pylint: disable=too-many-instance-attributes
    """Typed edge connecting two nodes in the SFM graph."""

    source_id: uuid.UUID
    target_id: uuid.UUID
    kind: RelationshipKind
    weight: Optional[float] = 0.0  # e.g. $-value, mass, influence score
    time: Optional[TimeSlice] = None  # Temporal context of the relationship
    space: Optional[SpatialUnit] = None
    scenario: Optional[Scenario] = None
    meta: Dict[str, str] = field(default_factory=lambda: {})
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    certainty: Optional[float] = 1.0  # Confidence level (0-1)
    variability: Optional[float] = None  # Standard deviation or range
    # Versioning and data quality fields
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    data_quality: Optional[str] = None  # Description of data quality
    previous_version_id: Optional[uuid.UUID] = None
    temporal_dynamics: Optional[TemporalDynamics] = None  # Change over time
