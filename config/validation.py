"""
Configuration Validation System for SFM Service

This module provides comprehensive validation for configuration data using
Pydantic models to ensure type safety and business rule compliance.

Features:
- Type validation for all configuration fields
- Business rule validation
- Environment-specific validation
- Detailed error messages
- Validation reporting
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError, field_validator
from pydantic.v1 import validator  # type: ignore  # Keep v1 validator for compatibility
from enum import Enum
import logging

# Configure logging
logger = logging.getLogger(__name__)


class EnvironmentType(str, Enum):
    """Valid environment types."""
    development = "development"
    staging = "staging"
    production = "production"
    testing = "testing"


class LogLevel(str, Enum):
    """Valid log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Valid log formats."""
    json = "json"
    text = "text"


class CacheBackend(str, Enum):
    """Valid cache backends."""
    memory = "memory"
    redis = "redis"


class SSLMode(str, Enum):
    """Valid SSL modes."""
    disable = "disable"
    require = "require"
    verify_ca = "verify-ca"
    verify_full = "verify-full"


class DatabaseConfigModel(BaseModel):
    """Pydantic model for database configuration validation."""
    
    host: str = Field(min_length=1, description="Database host")
    port: int = Field(ge=1, le=65535, description="Database port")
    name: str = Field(min_length=1, description="Database name")
    username: str = Field(min_length=1, description="Database username")
    password: str = Field(default="", description="Database password")
    pool_size: int = Field(ge=1, le=1000, description="Connection pool size")
    timeout: int = Field(ge=1, le=300, description="Connection timeout")
    ssl_mode: SSLMode = Field(default=SSLMode.disable, description="SSL mode")
    max_connections: int = Field(ge=1, le=10000, description="Maximum connections")
    
    @validator('pool_size')  # type: ignore  # Pydantic v1 validator for compatibility
    def validate_pool_size(cls, v: int, values: Dict[str, Any]) -> int:
        """Validate pool size doesn't exceed max connections."""
        if 'max_connections' in values and v > values['max_connections']:
            raise ValueError('Pool size cannot exceed max connections')
        return v
    
    @validator('ssl_mode')  # type: ignore  # Pydantic v1 validator for compatibility
    def validate_ssl_mode_for_production(cls, v: SSLMode, values: Dict[str, Any]) -> SSLMode:
        """Validate SSL mode for production environment."""
        # Note: This validator would need access to environment context
        # For now, we'll just ensure valid enum value
        return v


class CacheConfigModel(BaseModel):
    """Pydantic model for cache configuration validation."""
    
    backend: CacheBackend = Field(default=CacheBackend.memory, description="Cache backend")
    host: str = Field(default="localhost", description="Cache host")
    port: int = Field(default=6379, ge=1, le=65535, description="Cache port")
    ttl: int = Field(default=3600, ge=0, description="Time to live in seconds")
    max_size: int = Field(default=10000, ge=1, description="Maximum cache size")
    password: str = Field(default="", description="Cache password")
    db: int = Field(default=0, ge=0, le=15, description="Redis database number")
    
    @validator('host')  # type: ignore  # Pydantic v1 validator for compatibility
    def validate_host_for_redis(cls, v: str, values: Dict[str, Any]) -> str:
        """Validate host is provided for Redis backend."""
        if values.get('backend') == CacheBackend.redis and not v:
            raise ValueError('Host is required for Redis backend')
        return v


class LoggingConfigModel(BaseModel):
    """Pydantic model for logging configuration validation."""
    
    level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    format: LogFormat = Field(default=LogFormat.json, description="Log format")
    file_path: str = Field(default="/var/log/sfm/app.log", description="Log file path")
    file_enabled: bool = Field(default=False, description="Enable file logging")
    console_enabled: bool = Field(default=True, description="Enable console logging")
    rotation_size: str = Field(default="100MB", description="Log rotation size")
    rotation_count: int = Field(default=10, ge=1, le=100, description="Log rotation count")
    
    @validator('file_path')  # type: ignore  # Pydantic v1 validator for compatibility
    def validate_file_path(cls, v: str, values: Dict[str, Any]) -> str:
        """Validate file path when file logging is enabled."""
        if values.get('file_enabled', False) and not v:
            raise ValueError('File path is required when file logging is enabled')
        return v
    
    @validator('rotation_size')  # type: ignore  # Pydantic v1 validator for compatibility
    def validate_rotation_size(cls, v: str) -> str:
        """Validate rotation size format."""
        if not v:
            raise ValueError('Rotation size cannot be empty')
        
        if not v.endswith(('KB', 'MB', 'GB')):
            raise ValueError('Rotation size must end with KB, MB, or GB')
        
        try:
            size_part = v[:-2]
            int(size_part)
        except ValueError:
            raise ValueError('Rotation size must be a number followed by KB, MB, or GB')
        
        return v


class SecurityConfigModel(BaseModel):
    """Pydantic model for security configuration validation."""
    
    secret_key: str = Field(default="", description="Secret key")
    encryption_enabled: bool = Field(default=False, description="Enable encryption")
    encryption_key: str = Field(default="", description="Encryption key")
    audit_enabled: bool = Field(default=True, description="Enable audit logging")
    session_timeout: int = Field(default=3600, ge=60, le=86400, description="Session timeout")
    
    @validator('secret_key')  # type: ignore  # Pydantic v1 validator for compatibility
    def validate_secret_key(cls, v: str, values: Dict[str, Any]) -> str:
        """Validate secret key requirements."""
        if not v:
            logger.warning("Secret key is empty - should be loaded from secrets manager")
        return v
    
    @validator('encryption_key')  # type: ignore  # Pydantic v1 validator for compatibility
    def validate_encryption_key(cls, v: str, values: Dict[str, Any]) -> str:
        """Validate encryption key when encryption is enabled."""
        if values.get('encryption_enabled', False) and not v:
            raise ValueError('Encryption key is required when encryption is enabled')
        return v


class SFMConfigModel(BaseModel):
    """Pydantic model for main SFM configuration validation."""
    
    environment: EnvironmentType = Field(default=EnvironmentType.development, description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    version: str = Field(default="1.0.0", description="Application version")
    database: DatabaseConfigModel = Field(description="Database configuration")
    cache: CacheConfigModel = Field(description="Cache configuration")
    logging: LoggingConfigModel = Field(description="Logging configuration")
    security: SecurityConfigModel = Field(description="Security configuration")
    
    @field_validator('debug')
    @classmethod
    def validate_debug_for_production(cls, v: bool, info) -> bool:  # type: ignore  # Pydantic v2 validator info parameter
        """Validate debug mode for production environment."""
        if info.data.get('environment') == EnvironmentType.production and v:  # type: ignore  # Pydantic v2 validator info.data access
            raise ValueError('Debug mode should not be enabled in production')
        return v


class ValidationReport:
    """Report for configuration validation results."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.is_valid: bool = True
        
    def add_error(self, error: str):
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False
        
    def add_warning(self, warning: str):
        """Add validation warning."""
        self.warnings.append(warning)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings
        }


class ConfigValidator:
    """Configuration validator with comprehensive validation rules."""
    
    def __init__(self):
        self.report = ValidationReport()
        
    def validate_config(self, config_data: Dict[str, Any]) -> ValidationReport:
        """Validate configuration data.
        
        Args:
            config_data: Configuration data to validate
            
        Returns:
            ValidationReport: Validation results
        """
        try:
            # Validate using Pydantic model
            validated_config = SFMConfigModel(**config_data)
            
            # Additional business rule validation
            self._validate_business_rules(validated_config)
            
            # Environment-specific validation
            self._validate_environment_specific(validated_config)
            
            # Security validation
            self._validate_security_rules(validated_config)
            
        except ValidationError as e:
            for error in e.errors():
                field_path = ' -> '.join(str(loc) for loc in error['loc'])
                self.report.add_error(f"{field_path}: {error['msg']}")
        except Exception as e:
            self.report.add_error(f"Validation error: {str(e)}")
            
        return self.report
    
    def _validate_business_rules(self, config: SFMConfigModel):
        """Validate business rules."""
        # Database connection validation
        if config.database.pool_size > config.database.max_connections:
            self.report.add_error("Database pool size cannot exceed max connections")
            
        # Cache validation
        if config.cache.backend == CacheBackend.redis:
            if not config.cache.host or config.cache.host == "localhost":
                self.report.add_warning("Redis host is localhost - may not be suitable for production")
                
        # Logging validation
        if config.logging.level == LogLevel.DEBUG and config.environment == EnvironmentType.production:
            self.report.add_warning("Debug logging in production may impact performance")
    
    def _validate_environment_specific(self, config: SFMConfigModel):
        """Validate environment-specific rules."""
        if config.environment == EnvironmentType.production:
            # Production-specific validation
            if config.database.ssl_mode == SSLMode.disable:
                self.report.add_error("SSL must be enabled for production database")
                
            if not config.security.encryption_enabled:
                self.report.add_warning("Encryption should be enabled in production")
                
            if config.logging.level in [LogLevel.DEBUG, LogLevel.INFO]:
                self.report.add_warning("Consider using WARNING or ERROR log level in production")
                
        elif config.environment == EnvironmentType.development:
            # Development-specific validation
            if config.database.ssl_mode != SSLMode.disable:
                self.report.add_warning("SSL may not be necessary in development")
                
        elif config.environment == EnvironmentType.testing:
            # Testing-specific validation
            if config.database.pool_size > 5:
                self.report.add_warning("Large pool size may not be needed for testing")
    
    def _validate_security_rules(self, config: SFMConfigModel):
        """Validate security rules."""
        # Check for empty secrets (they should be loaded from secrets manager)
        if not config.security.secret_key:
            self.report.add_warning("Secret key is empty - ensure it's loaded from secrets manager")
            
        if not config.database.password:
            self.report.add_warning("Database password is empty - ensure it's loaded from secrets manager")
            
        # Session timeout validation
        if config.security.session_timeout < 300:  # 5 minutes
            self.report.add_warning("Session timeout is very short - may impact user experience")
            
        if config.security.session_timeout > 86400:  # 24 hours
            self.report.add_warning("Session timeout is very long - may be a security risk")


def validate_configuration(config_data: Dict[str, Any]) -> ValidationReport:
    """Validate configuration data.
    
    Args:
        config_data: Configuration data to validate
        
    Returns:
        ValidationReport: Validation results
    """
    validator = ConfigValidator()
    return validator.validate_config(config_data)


# Export public API
__all__ = [
    'SFMConfigModel',
    'DatabaseConfigModel',
    'CacheConfigModel',
    'LoggingConfigModel',
    'SecurityConfigModel',
    'ValidationReport',
    'ConfigValidator',
    'validate_configuration',
    'EnvironmentType',
    'LogLevel',
    'LogFormat',
    'CacheBackend',
    'SSLMode'
]