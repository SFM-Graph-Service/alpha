#!/usr/bin/env python3
"""
Configuration System Demo

This script demonstrates the configuration management system features:
- Environment-specific configuration loading
- Configuration validation
- Secrets management
- Configuration merging
- CLI tools usage
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config_manager import get_config, reload_config, ConfigLoader
from config.secrets_manager import EnvironmentSecretsManager, SecretsManagerFactory
from config.validation import validate_configuration
from config.cli import config
from core.sfm_service import SFMService, SFMServiceConfig
from api.sfm_api import app, sfm_config

def demo_basic_configuration():
    """Demonstrate basic configuration loading."""
    print("🔧 Basic Configuration Loading Demo")
    print("=" * 50)
    
    # Load configuration
    config = get_config()
    
    print(f"Environment: {config.environment}")
    print(f"Debug mode: {config.debug}")
    print(f"API host: {config.api.host}:{config.api.port}")
    print(f"Database: {config.database.host}:{config.database.port}")
    print(f"Cache backend: {config.cache.backend}")
    print(f"Log level: {config.logging.level}")
    print()

def demo_environment_switching():
    """Demonstrate environment-specific configuration."""
    print("🌍 Environment-Specific Configuration Demo")
    print("=" * 50)
    
    environments = ['development', 'staging', 'production']
    
    for env in environments:
        print(f"\n--- {env.upper()} Configuration ---")
        
        # Set environment
        os.environ['SFM_ENV'] = env
        
        # Reload configuration
        config = reload_config()
        
        print(f"Debug mode: {config.debug}")
        print(f"Database host: {config.database.host}")
        print(f"Database pool size: {config.database.pool_size}")
        print(f"Cache backend: {config.cache.backend}")
        print(f"Log level: {config.logging.level}")
        print(f"Security encryption: {config.security.encryption_enabled}")
    
    # Reset to development
    os.environ['SFM_ENV'] = 'development'
    reload_config()
    print()

def demo_configuration_validation():
    """Demonstrate configuration validation."""
    print("✅ Configuration Validation Demo")
    print("=" * 50)
    
    # Load and validate current configuration
    config = get_config()
    report = validate_configuration(config.to_dict())
    
    print(f"Configuration is valid: {report.is_valid}")
    
    if report.errors:
        print("\nErrors:")
        for error in report.errors:
            print(f"  ❌ {error}")
    
    if report.warnings:
        print("\nWarnings:")
        for warning in report.warnings:
            print(f"  ⚠️  {warning}")
    
    print()

def demo_secrets_management():
    """Demonstrate secrets management."""
    print("🔐 Secrets Management Demo")
    print("=" * 50)
    
    # Create secrets manager
    secrets_manager = EnvironmentSecretsManager()
    
    # Set some test secrets
    secrets_manager.set_secret('database_password', 'super_secret_password')
    secrets_manager.set_secret('jwt_secret', 'jwt_signing_key')
    
    # Retrieve secrets
    print("Setting secrets...")
    try:
        db_password = secrets_manager.get_secret('database_password')
        print(f"Database password retrieved: {len(db_password)} characters")
        
        jwt_secret = secrets_manager.get_secret('jwt_secret')
        print(f"JWT secret retrieved: {len(jwt_secret)} characters")
    except Exception as e:
        print(f"Error retrieving secrets: {e}")
    
    # List secrets
    secrets = secrets_manager.list_secrets()
    print(f"Total secrets stored: {len(secrets)}")
    
    print()

def demo_service_integration():
    """Demonstrate service integration with configuration."""
    print("🔗 Service Integration Demo")
    print("=" * 50)
    
    # Create service with configuration
    service = SFMService()
    
    print(f"Service storage backend: {service.config.storage_backend}")
    print(f"Service validation enabled: {service.config.validation_enabled}")
    print(f"Service cache queries: {service.config.cache_queries}")
    print(f"Service logging enabled: {service.config.enable_logging}")
    print(f"Service log level: {service.config.log_level}")
    
    # Get service health
    health = service.get_health()
    print(f"Service status: {health.status.value}")
    print(f"Service backend: {health.backend}")
    
    print()

def demo_environment_variables():
    """Demonstrate environment variable overrides."""
    print("🌱 Environment Variable Overrides Demo")
    print("=" * 50)
    
    # Set environment variables
    os.environ['SFM_DATABASE_HOST'] = 'override-db'
    os.environ['SFM_API_PORT'] = '9000'
    os.environ['SFM_DEBUG'] = 'true'
    
    # Reload configuration
    config = reload_config()
    
    print(f"Database host (from env var): {config.database.host}")
    print(f"API port (from env var): {config.api.port}")
    print(f"Debug mode (from env var): {config.debug}")
    
    # Clean up
    del os.environ['SFM_DATABASE_HOST']
    del os.environ['SFM_API_PORT']
    del os.environ['SFM_DEBUG']
    
    print()

def demo_configuration_merging():
    """Demonstrate configuration merging priority."""
    print("🔄 Configuration Merging Priority Demo")
    print("=" * 50)
    
    print("Configuration loading priority:")
    print("1. Default values (in dataclasses)")
    print("2. Base configuration file (config.yml)")
    print("3. Environment-specific file (config.{env}.yml)")
    print("4. Environment variables (SFM_* prefixed)")
    print("5. Secrets manager")
    print()
    
    # Load configuration showing sources
    loader = ConfigLoader()
    
    # Load base config
    base_config = loader._load_from_file('config.yml')
    print(f"Base config loaded: {bool(base_config)}")
    
    # Load environment-specific config
    env_config = loader._load_from_file('config.development.yml')
    print(f"Environment config loaded: {bool(env_config)}")
    
    # Show merged result
    final_config = get_config()
    print(f"Final database host: {final_config.database.host}")
    print(f"Final API port: {final_config.api.port}")
    print(f"Final debug mode: {final_config.debug}")
    
    print()

def main():
    """Run all configuration demos."""
    print("🎯 SFM Configuration Management System Demo")
    print("=" * 60)
    print()
    
    try:
        demo_basic_configuration()
        demo_environment_switching()
        demo_configuration_validation()
        demo_secrets_management()
        demo_service_integration()
        demo_environment_variables()
        demo_configuration_merging()
        
        print("✅ All configuration demos completed successfully!")
        print()
        print("Next steps:")
        print("1. Try the CLI tools: python config/cli.py --help")
        print("2. Start the API server: python api/sfm_api.py")
        print("3. Check configuration status: curl http://localhost:8000/config/status")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()