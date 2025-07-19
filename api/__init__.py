"""
API package - Service layer and external interfaces for SFM.

This package contains high-level service facades and APIs that provide
simplified interfaces to the SFM framework functionality.
"""

from .sfm_service import SFMService, SFMServiceConfig

__all__ = ['SFMService', 'SFMServiceConfig']