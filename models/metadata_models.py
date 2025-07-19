"""
Support classes and metadata models for SFM modeling.

This module defines support classes including temporal dynamics, validation rules,
and model metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

from models.meta_entities import TimeSlice
from models.sfm_enums import TemporalFunctionType, ValidationRuleType


@dataclass
class TemporalDynamics:
    """Models change over time for any value."""

    start_time: TimeSlice
    end_time: Optional[TimeSlice] = None
    # linear, exponential, logistic, etc.
    function_type: TemporalFunctionType = TemporalFunctionType.LINEAR
    parameters: Dict[str, float] = field(default_factory=lambda: {})


@dataclass
class ValidationRule:
    """Defines a validation rule for data integrity."""

    rule_type: ValidationRuleType  # e.g., "range", "sum", "required", "unique"
    target_field: str
    parameters: Dict[str, Any] = field(default_factory=lambda: {})
    error_message: str = ""


@dataclass
class ModelMetadata:  # pylint: disable=too-many-instance-attributes
    """Documentation about the model itself."""

    version: str
    authors: List[str] = field(default_factory=lambda: [])
    creation_date: datetime = field(default_factory=datetime.now)
    last_modified: Optional[datetime] = None
    citation: Optional[str] = None
    license: str = "MIT"
    description: str = ""
    change_log: List[str] = field(default_factory=lambda: [])
