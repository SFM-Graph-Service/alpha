"""
Data package - Data access and persistence for SFM.

This package contains repositories, data access objects, and other
data persistence mechanisms for the SFM framework.
"""

from .repositories import (
    SFMRepository, SFMRepositoryFactory, NetworkXSFMRepository,
    T  # Type variable used in repositories
)

__all__ = ['SFMRepository', 'SFMRepositoryFactory', 'NetworkXSFMRepository', 'T']