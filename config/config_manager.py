"""
Configuration Management System for SFM Service

This module provides centralized configuration management with support for:
- Environment-specific configurations
- Configuration merging from multiple sources
- Secrets management integration
- Configuration validation
- Hot reloading capabilities

Configuration loading priority:
1. Default values (in dataclasses)
2. Base configuration file (config.yml)
3. Environment-specific file (config.{env}.yml)
4. Environment variables
5. Command-line arguments
6. Remote configuration (optional)
"""

from typing import Any, Dict, Optional, Type, Union, List
from dataclasses import dataclass, field
from pathlib import Path
import os
import yaml
import json
from abc import ABC, abstractmethod
import logging
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class Environment(Enum):
    """Supported environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 5432
    name: str = "sfm_db"
    username: str = "sfm_user"
    password: str = ""
    pool_size: int = 10
    timeout: int = 30
    ssl_mode: str = "disable"
    max_connections: int = 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'name': self.name,
            'username': self.username,
            'password': self.password,
            'pool_size': self.pool_size,
            'timeout': self.timeout,
            'ssl_mode': self.ssl_mode,
            'max_connections': self.max_connections
        }


@dataclass
class CacheConfig:
    """Cache configuration settings."""
    backend: str = "memory"
    host: str = "localhost"
    port: int = 6379
    ttl: int = 3600
    max_size: int = 10000
    password: str = ""
    db: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'backend': self.backend,
            'host': self.host,
            'port': self.port,
            'ttl': self.ttl,
            'max_size': self.max_size,
            'password': self.password,
            'db': self.db
        }


@dataclass
class APIConfig:
    """API configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit: str = "100/hour"
    jwt_secret: str = ""
    request_timeout: int = 30
    max_request_size: int = 10485760  # 10MB
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'debug': self.debug,
            'cors_origins': self.cors_origins,
            'rate_limit': self.rate_limit,
            'jwt_secret': self.jwt_secret,
            'request_timeout': self.request_timeout,
            'max_request_size': self.max_request_size
        }


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "json"
    file_path: str = "/var/log/sfm/app.log"
    file_enabled: bool = False
    console_enabled: bool = True
    rotation_size: str = "100MB"
    rotation_count: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'level': self.level,
            'format': self.format,
            'file_path': self.file_path,
            'file_enabled': self.file_enabled,
            'console_enabled': self.console_enabled,
            'rotation_size': self.rotation_size,
            'rotation_count': self.rotation_count
        }


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    secret_key: str = ""
    encryption_enabled: bool = False
    encryption_key: str = ""
    audit_enabled: bool = True
    session_timeout: int = 3600
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'secret_key': self.secret_key,
            'encryption_enabled': self.encryption_enabled,
            'encryption_key': self.encryption_key,
            'audit_enabled': self.audit_enabled,
            'session_timeout': self.session_timeout
        }


@dataclass
class SFMConfig:
    """Main SFM configuration container."""
    environment: str = "development"
    debug: bool = False
    version: str = "1.0.0"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    api: APIConfig = field(default_factory=APIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'environment': self.environment,
            'debug': self.debug,
            'version': self.version,
            'database': self.database.to_dict(),
            'cache': self.cache.to_dict(),
            'api': self.api.to_dict(),
            'logging': self.logging.to_dict(),
            'security': self.security.to_dict()
        }


class ConfigurationError(Exception):
    """Configuration-related error."""
    pass


class ConfigLoader:
    """Configuration loader with environment support and merging capabilities."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration loader.
        
        Args:
            config_path: Optional path to configuration directory
        """
        self.config_path = config_path or self._find_config_path()
        self.environment = os.getenv('SFM_ENV', 'development')
        self.secrets_manager = None
        
    def _find_config_path(self) -> Path:
        """Find configuration directory."""
        # Look for config directory in current working directory or package directory
        current_dir = Path.cwd()
        if (current_dir / "config").exists():
            return current_dir / "config"
        
        # Look in the package directory
        package_dir = Path(__file__).parent
        return package_dir
    
    def load_config(self) -> SFMConfig:
        """Load configuration from files and environment variables.
        
        Returns:
            SFMConfig: Complete configuration object
            
        Raises:
            ConfigurationError: If configuration loading fails
        """
        try:
            # Load base configuration
            base_config = self._load_from_file('config.yml')
            
            # Load environment-specific overrides
            env_config = self._load_from_file(f'config.{self.environment}.yml')
            
            # Apply environment variable overrides
            env_overrides = self._load_from_env()
            
            # Merge configurations
            merged_config = self._merge_configs(base_config, env_config, env_overrides)
            
            # Create and validate config object
            config = self._create_config_object(merged_config)
            
            # Load secrets if secrets manager is configured
            if self.secrets_manager:
                config = self._load_secrets(config)
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigurationError(f"Configuration loading failed: {e}")
    
    def _load_from_file(self, filename: str) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Args:
            filename: Name of the configuration file
            
        Returns:
            Dict: Configuration data
        """
        file_path = self.config_path / filename
        if not file_path.exists():
            logger.debug(f"Configuration file not found: {file_path}")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
            logger.debug(f"Loaded configuration from {file_path}")
            return config_data
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {e}")
            return {}
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration overrides from environment variables.
        
        Returns:
            Dict: Configuration overrides
        """
        env_mapping = {
            'SFM_DATABASE_HOST': 'database.host',
            'SFM_DATABASE_PORT': 'database.port',
            'SFM_DATABASE_NAME': 'database.name',
            'SFM_DATABASE_USERNAME': 'database.username',
            'SFM_DATABASE_PASSWORD': 'database.password',
            'SFM_CACHE_BACKEND': 'cache.backend',
            'SFM_CACHE_HOST': 'cache.host',
            'SFM_CACHE_PORT': 'cache.port',
            'SFM_API_HOST': 'api.host',
            'SFM_API_PORT': 'api.port',
            'SFM_API_DEBUG': 'api.debug',
            'SFM_API_JWT_SECRET': 'api.jwt_secret',
            'SFM_LOG_LEVEL': 'logging.level',
            'SFM_LOG_FORMAT': 'logging.format',
            'SFM_DEBUG': 'debug',
            'SFM_ENVIRONMENT': 'environment'
        }
        
        overrides = {}
        for env_var, config_path in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert types appropriately
                if env_var.endswith('_PORT'):
                    value = int(value)
                elif env_var.endswith('_DEBUG') or env_var == 'SFM_DEBUG':
                    value = value.lower() in ('true', '1', 'yes', 'on')
                
                self._set_nested_value(overrides, config_path, value)
        
        return overrides
    
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any):
        """Set nested dictionary value using dot notation.
        
        Args:
            data: Dictionary to modify
            path: Dot-separated path (e.g., 'database.host')
            value: Value to set
        """
        keys = path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _merge_configs(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries.
        
        Args:
            *configs: Configuration dictionaries to merge
            
        Returns:
            Dict: Merged configuration
        """
        result = {}
        
        for config in configs:
            if config:
                result = self._deep_merge(result, config)
        
        return result
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Override dictionary
            
        Returns:
            Dict: Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _create_config_object(self, config_data: Dict[str, Any]) -> SFMConfig:
        """Create SFMConfig object from configuration data.
        
        Args:
            config_data: Configuration data dictionary
            
        Returns:
            SFMConfig: Configuration object
        """
        # Extract nested configurations
        database_config = DatabaseConfig(**config_data.get('database', {}))
        cache_config = CacheConfig(**config_data.get('cache', {}))
        api_config = APIConfig(**config_data.get('api', {}))
        logging_config = LoggingConfig(**config_data.get('logging', {}))
        security_config = SecurityConfig(**config_data.get('security', {}))
        
        # Create main config object
        config = SFMConfig(
            environment=config_data.get('environment', 'development'),
            debug=config_data.get('debug', False),
            version=config_data.get('version', '1.0.0'),
            database=database_config,
            cache=cache_config,
            api=api_config,
            logging=logging_config,
            security=security_config
        )
        
        return config
    
    def _load_secrets(self, config: SFMConfig) -> SFMConfig:
        """Load secrets using configured secrets manager.
        
        Args:
            config: Configuration object to update
            
        Returns:
            SFMConfig: Updated configuration with secrets
        """
        if not self.secrets_manager:
            return config
        
        # Define secret mappings
        secret_mappings = {
            'database_password': 'database.password',
            'cache_password': 'cache.password',
            'jwt_secret': 'api.jwt_secret',
            'secret_key': 'security.secret_key',
            'encryption_key': 'security.encryption_key'
        }
        
        config_dict = config.to_dict()
        
        for secret_key, config_path in secret_mappings.items():
            try:
                secret_value = self.secrets_manager.get_secret(secret_key)
                if secret_value:
                    self._set_nested_value(config_dict, config_path, secret_value)
            except Exception as e:
                logger.warning(f"Failed to load secret '{secret_key}': {e}")
        
        return self._create_config_object(config_dict)
    
    def set_secrets_manager(self, secrets_manager):
        """Set secrets manager for loading sensitive configuration.
        
        Args:
            secrets_manager: Secrets manager instance
        """
        self.secrets_manager = secrets_manager
    
    def validate_config(self, config: SFMConfig) -> bool:
        """Validate configuration object.
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            ConfigurationError: If validation fails
        """
        # Validate environment
        valid_environments = [e.value for e in Environment]
        if config.environment not in valid_environments:
            raise ConfigurationError(f"Invalid environment: {config.environment}. Must be one of: {valid_environments}")
        
        # Validate database configuration
        if config.database.port < 1 or config.database.port > 65535:
            raise ConfigurationError(f"Invalid database port: {config.database.port}")
        
        if config.database.pool_size < 1:
            raise ConfigurationError(f"Invalid database pool size: {config.database.pool_size}")
        
        # Validate cache configuration
        if config.cache.port < 1 or config.cache.port > 65535:
            raise ConfigurationError(f"Invalid cache port: {config.cache.port}")
        
        if config.cache.ttl < 0:
            raise ConfigurationError(f"Invalid cache TTL: {config.cache.ttl}")
        
        # Validate API configuration
        if config.api.port < 1 or config.api.port > 65535:
            raise ConfigurationError(f"Invalid API port: {config.api.port}")
        
        # Validate logging configuration
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if config.logging.level not in valid_levels:
            raise ConfigurationError(f"Invalid log level: {config.logging.level}")
        
        return True


# Singleton instance
_config_loader = None
_current_config = None


def get_config_loader() -> ConfigLoader:
    """Get singleton configuration loader instance.
    
    Returns:
        ConfigLoader: Configuration loader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def get_config() -> SFMConfig:
    """Get current configuration.
    
    Returns:
        SFMConfig: Current configuration
    """
    global _current_config
    if _current_config is None:
        loader = get_config_loader()
        _current_config = loader.load_config()
    return _current_config


def reload_config() -> SFMConfig:
    """Reload configuration from sources.
    
    Returns:
        SFMConfig: Reloaded configuration
    """
    global _current_config
    loader = get_config_loader()
    _current_config = loader.load_config()
    return _current_config


def set_config(config: SFMConfig):
    """Set current configuration.
    
    Args:
        config: Configuration to set
    """
    global _current_config
    _current_config = config


# Export public API
__all__ = [
    'SFMConfig',
    'DatabaseConfig',
    'CacheConfig',
    'APIConfig',
    'LoggingConfig',
    'SecurityConfig',
    'ConfigLoader',
    'ConfigurationError',
    'Environment',
    'get_config_loader',
    'get_config',
    'reload_config',
    'set_config'
]