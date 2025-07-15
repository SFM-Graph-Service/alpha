"""
Configuration Management Module for SFM Service

This module provides comprehensive configuration management capabilities including:
- Environment-specific configurations
- Secrets management
- Configuration validation
- Configuration merging
- CLI tools for configuration management
"""

from .config_manager import (
    SFMConfig,
    DatabaseConfig,
    CacheConfig,
    LoggingConfig,
    SecurityConfig,
    ConfigLoader,
    ConfigurationError,
    Environment,
    get_config_loader,
    get_config,
    reload_config,
    set_config
)

from .secrets_manager import (
    SecretsManager,
    EnvironmentSecretsManager,
    AWSSecretsManager,
    AzureKeyVaultManager,
    VaultSecretsManager,
    SecretsManagerFactory,
    SecretType,
    SecretMetadata,
    SecretsError,
    SecretNotFoundError,
    SecretAccessError
)

from .validation import (
    SFMConfigModel,
    DatabaseConfigModel,
    CacheConfigModel,
    LoggingConfigModel,
    SecurityConfigModel,
    ValidationReport,
    ConfigValidator,
    validate_configuration,
    EnvironmentType,
    LogLevel,
    LogFormat,
    CacheBackend,
    SSLMode
)

from .monitoring import (
    MonitoringConfig,
    get_monitoring_config,
    load_monitoring_config_from_env,
    DEFAULT_MONITORING_CONFIG,
    DEVELOPMENT_CONFIG,
    PRODUCTION_CONFIG
)

# Export all public APIs
__all__ = [
    # Configuration Management
    'SFMConfig',
    'DatabaseConfig',
    'CacheConfig',
    'LoggingConfig',
    'SecurityConfig',
    'ConfigLoader',
    'ConfigurationError',
    'Environment',
    'get_config_loader',
    'get_config',
    'reload_config',
    'set_config',
    
    # Secrets Management
    'SecretsManager',
    'EnvironmentSecretsManager',
    'AWSSecretsManager',
    'AzureKeyVaultManager',
    'VaultSecretsManager',
    'SecretsManagerFactory',
    'SecretType',
    'SecretMetadata',
    'SecretsError',
    'SecretNotFoundError',
    'SecretAccessError',
    
    # Validation
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
    'SSLMode',
    
    # Monitoring
    'MonitoringConfig',
    'get_monitoring_config',
    'load_monitoring_config_from_env',
    'DEFAULT_MONITORING_CONFIG',
    'DEVELOPMENT_CONFIG',
    'PRODUCTION_CONFIG'
]
