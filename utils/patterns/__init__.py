"""
Design Patterns for SFM Framework

This module contains implementations of various design patterns to improve
the maintainability, extensibility, and robustness of the SFM framework.
"""

from .observer import GraphChangeObserver, GraphObservable
from .command import Command, CommandManager
from .strategy import Strategy, StrategyManager
from .decorator import (
    validate_inputs, audit_operation, cache_result,
    ValidationDecorator, AuditDecorator, CacheDecorator
)
from .event_bus import Event, EventHandler, EventBus
from .plugin import SFMPlugin, PluginManager
from .dependency_injection import DIContainer

__all__ = [
    # Observer Pattern
    'GraphChangeObserver',
    'GraphObservable',
    
    # Command Pattern
    'Command',
    'CommandManager',
    
    # Strategy Pattern
    'Strategy',
    'StrategyManager',
    
    # Decorator Pattern
    'validate_inputs',
    'audit_operation',
    'cache_result',
    'ValidationDecorator',
    'AuditDecorator',
    'CacheDecorator',
    
    # Event Bus
    'Event',
    'EventHandler',
    'EventBus',
    
    # Plugin Architecture
    'SFMPlugin',
    'PluginManager',
    
    # Dependency Injection
    'DIContainer',
]