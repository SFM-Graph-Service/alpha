"""
Dimensional meta entities for SFM modeling.

This module defines the foundational dimensional entities used to provide
context and scope for SFM analysis including time, space, and scenarios.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class TimeSlice:
    """Discrete period for snapshot-style SFM accounting (e.g., fiscal year, quarter)."""

    label: str  # e.g. "FY2025" or "Q1-2030"


@dataclass(frozen=True)
class SpatialUnit:
    """Hierarchical spatial identifier (nation, state, metro, census tract, etc.)."""

    code: str  # e.g. "US-WA-SEATTLE"
    name: str  # human-friendly display


@dataclass(frozen=True)
class Scenario:
    """Counterfactual or policy-design scenario name (baseline, carbon tax, UBI...)."""

    label: str
