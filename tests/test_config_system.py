"""
Tests for Configuration Management System

This module provides comprehensive tests for the configuration management system including:
- Configuration loading and merging
- Environment-specific configurations
- Secrets management
- Configuration validation
- CLI tools
"""

import unittest
import tempfile
import os
import yaml
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_manager import (
    SFMConfig, DatabaseConfig, CacheConfig, LoggingConfig, SecurityConfig,
    ConfigLoader, ConfigurationError, Environment, get_config_loader, get_config
)
from config.secrets_manager import (
    EnvironmentSecretsManager, SecretsManagerFactory, SecretNotFoundError, SecretsError
)
from config.validation import (
    validate_configuration, ValidationReport, ConfigValidator, 
    SFMConfigModel, DatabaseConfigModel
)


class TestConfigurationDataClasses(unittest.TestCase):
    """Test configuration data classes."""
    
    def test_database_config_creation(self):
        """Test DatabaseConfig creation and defaults."""
        db_config = DatabaseConfig()
        
        self.assertEqual(db_config.host, "localhost")
        self.assertEqual(db_config.port, 5432)
        self.assertEqual(db_config.name, "sfm_db")
        self.assertEqual(db_config.username, "sfm_user")
        self.assertEqual(db_config.password, "")
        self.assertEqual(db_config.pool_size, 10)
        self.assertEqual(db_config.timeout, 30)
        
    def test_database_config_custom_values(self):
        """Test DatabaseConfig with custom values."""
        db_config = DatabaseConfig(
            host="prod-db.example.com",
            port=5433,
            name="production_db",
            username="prod_user",
            password="secret123",
            pool_size=50,
            timeout=60
        )
        
        self.assertEqual(db_config.host, "prod-db.example.com")
        self.assertEqual(db_config.port, 5433)
        self.assertEqual(db_config.name, "production_db")
        self.assertEqual(db_config.username, "prod_user")
        self.assertEqual(db_config.password, "secret123")
        self.assertEqual(db_config.pool_size, 50)
        self.assertEqual(db_config.timeout, 60)
        
    def test_cache_config_creation(self):
        """Test CacheConfig creation and defaults."""
        cache_config = CacheConfig()
        
        self.assertEqual(cache_config.backend, "memory")
        self.assertEqual(cache_config.host, "localhost")
        self.assertEqual(cache_config.port, 6379)
        self.assertEqual(cache_config.ttl, 3600)
        self.assertEqual(cache_config.max_size, 10000)
        
    def test_sfm_config_creation(self):
        """Test SFMConfig creation and nested configs."""
        config = SFMConfig()
        
        self.assertEqual(config.environment, "development")
        self.assertEqual(config.debug, False)
        self.assertEqual(config.version, "1.0.0")
        self.assertIsInstance(config.database, DatabaseConfig)
        self.assertIsInstance(config.cache, CacheConfig)
        self.assertIsInstance(config.logging, LoggingConfig)
        self.assertIsInstance(config.security, SecurityConfig)
        
    def test_config_to_dict_conversion(self):
        """Test configuration to dictionary conversion."""
        config = SFMConfig()
        config_dict = config.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertIn('environment', config_dict)
        self.assertIn('debug', config_dict)
        self.assertIn('database', config_dict)
        self.assertIn('cache', config_dict)
        self.assertIn('logging', config_dict)
        self.assertIn('security', config_dict)
        
        # Check nested dictionary structure
        self.assertIsInstance(config_dict['database'], dict)
        self.assertIn('host', config_dict['database'])
        self.assertIn('port', config_dict['database'])


class TestConfigLoader(unittest.TestCase):
    """Test configuration loader."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_config_loader_initialization(self):
        """Test ConfigLoader initialization."""
        loader = ConfigLoader(self.config_path)
        
        self.assertEqual(loader.config_path, self.config_path)
        self.assertEqual(loader.environment, os.getenv('SFM_ENV', 'development'))
        
    def test_load_empty_config(self):
        """Test loading with no configuration files."""
        loader = ConfigLoader(self.config_path)
        config = loader.load_config()
        
        # Should return default configuration
        self.assertIsInstance(config, SFMConfig)
        self.assertEqual(config.environment, 'development')
        
    def test_load_base_config(self):
        """Test loading base configuration file."""
        # Create base config file
        base_config = {
            'environment': 'testing',
            'debug': True,
            'database': {
                'host': 'test-db',
                'port': 5433
            }
        }
        
        with open(self.config_path / 'config.yml', 'w') as f:
            yaml.dump(base_config, f)
        
        loader = ConfigLoader(self.config_path)
        config = loader.load_config()
        
        self.assertEqual(config.environment, 'testing')
        self.assertEqual(config.debug, True)
        self.assertEqual(config.database.host, 'test-db')
        self.assertEqual(config.database.port, 5433)
        
    def test_load_environment_specific_config(self):
        """Test loading environment-specific configuration."""
        # Create base config
        base_config = {
            'environment': 'development',
            'database': {
                'host': 'localhost',
                'port': 5432
            }
        }
        
        with open(self.config_path / 'config.yml', 'w') as f:
            yaml.dump(base_config, f)
        
        # Create development-specific config
        dev_config = {
            'debug': True,
            'database': {
                'host': 'dev-db',
                'pool_size': 5
            }
        }
        
        with open(self.config_path / 'config.development.yml', 'w') as f:
            yaml.dump(dev_config, f)
        
        loader = ConfigLoader(self.config_path)
        loader.environment = 'development'
        config = loader.load_config()
        
        # Should merge base and environment-specific configs
        self.assertEqual(config.environment, 'development')
        self.assertEqual(config.debug, True)
        self.assertEqual(config.database.host, 'dev-db')  # Override from dev config
        self.assertEqual(config.database.port, 5432)      # From base config
        self.assertEqual(config.database.pool_size, 5)    # From dev config
        
    def test_environment_variable_overrides(self):
        """Test environment variable overrides."""
        # Create base config
        base_config = {
            'database': {
                'host': 'localhost',
                'port': 5432
            }
        }
        
        with open(self.config_path / 'config.yml', 'w') as f:
            yaml.dump(base_config, f)
        
        # Set environment variables
        with patch.dict(os.environ, {
            'SFM_DATABASE_HOST': 'env-db',
            'SFM_DATABASE_PORT': '5433',
            'SFM_DEBUG': 'true'
        }):
            loader = ConfigLoader(self.config_path)
            config = loader.load_config()
            
            self.assertEqual(config.database.host, 'env-db')
            self.assertEqual(config.database.port, 5433)
            self.assertEqual(config.debug, True)
            
    def test_nested_value_setting(self):
        """Test setting nested dictionary values."""
        loader = ConfigLoader(self.config_path)
        data = {}
        
        loader._set_nested_value(data, 'database.host', 'test-host')
        loader._set_nested_value(data, 'database.port', 5432)
        
        expected = {
            'database': {
                'host': 'test-host',
                'port': 5432
            }
        }
        
        self.assertEqual(data, expected)
        
    def test_config_merging(self):
        """Test configuration merging."""
        loader = ConfigLoader(self.config_path)
        
        config1 = {
            'environment': 'development',
            'database': {
                'host': 'localhost',
                'port': 5432
            }
        }
        
        config2 = {
            'debug': True,
            'database': {
                'host': 'new-host',
                'pool_size': 10
            }
        }
        
        merged = loader._merge_configs(config1, config2)
        
        expected = {
            'environment': 'development',
            'debug': True,
            'database': {
                'host': 'new-host',
                'port': 5432,
                'pool_size': 10
            }
        }
        
        self.assertEqual(merged, expected)


class TestSecretsManager(unittest.TestCase):
    """Test secrets management."""
    
    def test_environment_secrets_manager(self):
        """Test EnvironmentSecretsManager."""
        manager = EnvironmentSecretsManager()
        
        # Test setting and getting secrets
        manager.set_secret('test_key', 'test_value')
        value = manager.get_secret('test_key')
        
        self.assertEqual(value, 'test_value')
        
        # Test secret not found
        with self.assertRaises(SecretNotFoundError):
            manager.get_secret('nonexistent_key')
        
        # Test listing secrets
        secrets = manager.list_secrets()
        self.assertIn('test_key', secrets)
        
        # Test deleting secrets
        manager.delete_secret('test_key')
        with self.assertRaises(SecretNotFoundError):
            manager.get_secret('test_key')
            
    def test_secrets_manager_factory(self):
        """Test SecretsManagerFactory."""
        # Test creating environment secrets manager
        manager = SecretsManagerFactory.create_secrets_manager('environment')
        self.assertIsInstance(manager, EnvironmentSecretsManager)
        
        # Test invalid manager type
        with self.assertRaises(ValueError):
            SecretsManagerFactory.create_secrets_manager('invalid_type')
            
    def test_environment_secrets_with_prefix(self):
        """Test EnvironmentSecretsManager with custom prefix."""
        manager = EnvironmentSecretsManager(prefix='TEST_')
        
        # Test with environment variable
        with patch.dict(os.environ, {'TEST_MY_SECRET': 'secret_value'}):
            value = manager.get_secret('my_secret')
            self.assertEqual(value, 'secret_value')


class TestConfigValidation(unittest.TestCase):
    """Test configuration validation."""
    
    def test_valid_configuration(self):
        """Test validation of valid configuration."""
        config_data = {
            'environment': 'development',
            'debug': False,
            'version': '1.0.0',
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'test_db',
                'username': 'test_user',
                'password': 'secret',
                'pool_size': 10,
                'timeout': 30,
                'ssl_mode': 'disable',
                'max_connections': 100
            },
            'cache': {
                'backend': 'memory',
                'host': 'localhost',
                'port': 6379,
                'ttl': 3600,
                'max_size': 10000,
                'password': '',
                'db': 0
            },
            'api': {
                'host': '0.0.0.0',
                'port': 8000,
                'debug': False,
                'cors_origins': ['http://localhost:3000'],
                'rate_limit': '100/hour',
                'jwt_secret': 'secret',
                'request_timeout': 30,
                'max_request_size': 10485760
            },
            'logging': {
                'level': 'INFO',
                'format': 'json',
                'file_path': '/var/log/app.log',
                'file_enabled': False,
                'console_enabled': True,
                'rotation_size': '100MB',
                'rotation_count': 10
            },
            'security': {
                'secret_key': 'secret',
                'encryption_enabled': False,
                'encryption_key': '',
                'audit_enabled': True,
                'session_timeout': 3600
            }
        }
        
        report = validate_configuration(config_data)
        self.assertTrue(report.is_valid)
        
    def test_invalid_database_port(self):
        """Test validation with invalid database port."""
        config_data = {
            'environment': 'development',
            'database': {
                'host': 'localhost',
                'port': 70000,  # Invalid port
                'name': 'test_db',
                'username': 'test_user',
                'pool_size': 10,
                'timeout': 30,
                'ssl_mode': 'disable',
                'max_connections': 100
            }
        }
        
        report = validate_configuration(config_data)
        self.assertFalse(report.is_valid)
        self.assertTrue(any('port' in error.lower() for error in report.errors))
        
    def test_invalid_environment(self):
        """Test validation with invalid environment."""
        config_data = {
            'environment': 'invalid_env',
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'test_db',
                'username': 'test_user',
                'pool_size': 10,
                'timeout': 30,
                'ssl_mode': 'disable',
                'max_connections': 100
            }
        }
        
        report = validate_configuration(config_data)
        self.assertFalse(report.is_valid)
        self.assertTrue(any('environment' in error.lower() for error in report.errors))
        
    def test_production_specific_validation(self):
        """Test production-specific validation rules."""
        config_data = {
            'environment': 'production',
            'debug': True,  # Should trigger error
            'database': {
                'host': 'prod-db',
                'port': 5432,
                'name': 'prod_db',
                'username': 'prod_user',
                'pool_size': 50,
                'timeout': 60,
                'ssl_mode': 'disable',  # Should trigger error
                'max_connections': 200
            }
        }
        
        report = validate_configuration(config_data)
        self.assertFalse(report.is_valid)
        self.assertTrue(any('debug' in error.lower() for error in report.errors))
        
    def test_validation_report(self):
        """Test ValidationReport functionality."""
        report = ValidationReport()
        
        self.assertTrue(report.is_valid)
        self.assertEqual(len(report.errors), 0)
        self.assertEqual(len(report.warnings), 0)
        
        report.add_error('Test error')
        self.assertFalse(report.is_valid)
        self.assertEqual(len(report.errors), 1)
        
        report.add_warning('Test warning')
        self.assertEqual(len(report.warnings), 1)
        
        report_dict = report.to_dict()
        self.assertIn('is_valid', report_dict)
        self.assertIn('errors', report_dict)
        self.assertIn('warnings', report_dict)


class TestConfigurationIntegration(unittest.TestCase):
    """Test configuration system integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_full_configuration_flow(self):
        """Test complete configuration loading and validation flow."""
        # Create configuration files
        base_config = {
            'environment': 'testing',
            'debug': False,
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'test_db',
                'username': 'test_user',
                'pool_size': 5,
                'timeout': 10,
                'ssl_mode': 'disable',
                'max_connections': 20
            },
            'cache': {
                'backend': 'memory',
                'ttl': 300,
                'max_size': 100
            },
            'api': {
                'host': '127.0.0.1',
                'port': 8001,
                'debug': False,
                'cors_origins': ['http://localhost:3000'],
                'rate_limit': '1000/hour',
                'request_timeout': 5,
                'max_request_size': 1048576
            },
            'logging': {
                'level': 'ERROR',
                'format': 'text',
                'file_enabled': False,
                'console_enabled': True
            },
            'security': {
                'encryption_enabled': False,
                'audit_enabled': False,
                'session_timeout': 600
            }
        }
        
        with open(self.config_path / 'config.yml', 'w') as f:
            yaml.dump(base_config, f)
        
        # Load configuration
        loader = ConfigLoader(self.config_path)
        config = loader.load_config()
        
        # Verify configuration values
        self.assertEqual(config.environment, 'testing')
        self.assertEqual(config.database.host, 'localhost')
        self.assertEqual(config.database.port, 5432)
        self.assertEqual(config.cache.backend, 'memory')
        
        # Validate configuration
        report = validate_configuration(config.to_dict())
        self.assertTrue(report.is_valid)
        
    def test_secrets_integration(self):
        """Test secrets manager integration with configuration."""
        # Create base config
        base_config = {
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'test_db',
                'username': 'test_user',
                'password': ''  # Should be loaded from secrets
            }
        }
        
        with open(self.config_path / 'config.yml', 'w') as f:
            yaml.dump(base_config, f)
        
        # Create secrets manager
        secrets_manager = EnvironmentSecretsManager()
        secrets_manager.set_secret('database_password', 'secret_password')
        
        # Load configuration with secrets
        loader = ConfigLoader(self.config_path)
        loader.set_secrets_manager(secrets_manager)
        config = loader.load_config()
        
        # Verify secret was loaded
        self.assertEqual(config.database.password, 'secret_password')


if __name__ == '__main__':
    unittest.main()