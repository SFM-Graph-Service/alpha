"""
Cache configuration for the SFM system.

This module provides configuration classes and default settings for the
advanced caching system.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CacheLayerConfig:
    """Configuration for individual cache layers."""
    backend: str = 'memory'
    ttl: int = 3600
    max_size: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'backend': self.backend,
            'ttl': self.ttl,
            'max_size': self.max_size
        }


@dataclass
class RedisConfig:
    """Redis-specific configuration."""
    host: str = 'localhost'
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'password': self.password
        }


# Default cache configuration as shown in the issue
CACHE_CONFIG = {
    'default': {
        'backend': 'redis',
        'ttl': 3600,
        'max_size': 10000
    },
    'query_cache': {
        'backend': 'memory',
        'ttl': 1800,
        'max_size': 5000
    },
    'graph_cache': {
        'backend': 'redis',
        'ttl': 7200,
        'max_size': 50000
    },
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': None
    }
}


class CacheConfigManager:
    """Manager for cache configuration settings."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or CACHE_CONFIG.copy()
    
    def get_layer_config(self, layer_name: str) -> CacheLayerConfig:
        """Get configuration for a specific cache layer."""
        layer_config = self.config.get(layer_name, self.config['default'])
        return CacheLayerConfig(
            backend=layer_config.get('backend', 'memory'),
            ttl=layer_config.get('ttl', 3600),
            max_size=layer_config.get('max_size', 1000)
        )
    
    def get_redis_config(self) -> RedisConfig:
        """Get Redis configuration."""
        redis_config = self.config.get('redis', {})
        return RedisConfig(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            db=redis_config.get('db', 0),
            password=redis_config.get('password')
        )
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        self.config.update(updates)
    
    def get_config(self) -> Dict[str, Any]:
        """Get the full configuration."""
        return self.config.copy()