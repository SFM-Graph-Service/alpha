"""
Base node class and core infrastructure for SFM modeling.

This module defines the foundational Node class that serves as the base
for all SFM entities.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterator, Optional, Tuple


@dataclass
class Node:  # pylint: disable=too-many-instance-attributes
    """Generic graph node with a UUID primary key and free-form metadata."""

    label: str
    description: Optional[str] = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    meta: Dict[str, str] = field(default_factory=lambda: {})
    # Versioning and data quality fields
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    certainty: Optional[float] = 1.0  # Confidence level (0-1)
    data_quality: Optional[str] = None  # Description of data quality
    previous_version_id: Optional[uuid.UUID] = None

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """Iterator that yields (attribute_name, attribute_value) pairs."""
        for attr_name, attr_value in self.__dict__.items():
            yield attr_name, attr_value
