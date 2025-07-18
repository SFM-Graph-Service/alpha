"""
Configuration CLI Tools for SFM Service

This module provides command-line tools for configuration management:
- Configuration validation
- Environment-specific configuration generation
- Configuration value retrieval
- Secret management
- Configuration testing
"""

import click
import os
import sys
import json
import yaml
from typing import Dict, Any, Optional, Union, List
from pathlib import Path

# Add the project root to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_manager import (
    get_config_loader, 
    ConfigurationError
)
from config.secrets_manager import (
    SecretsManagerFactory,
    SecretsManager,
    SecretsError,
    SecretNotFoundError
)
from config.validation import validate_configuration


@click.group()
@click.option('--config-path', type=click.Path(exists=True), help='Configuration directory path')
@click.option('--environment', '-e', default='development', help='Environment name')
@click.pass_context
def config(ctx: click.Context, config_path: Optional[str], environment: str) -> None:
    """Configuration management commands for SFM Service."""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config_path
    ctx.obj['environment'] = environment
    
    # Set environment variable
    os.environ['SFM_ENV'] = environment


@config.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate current configuration."""
    click.echo("🔍 Validating configuration...")
    
    try:
        # Load configuration
        config_loader = get_config_loader()
        if ctx.obj and ctx.obj.get('config_path'):
            config_loader.config_path = Path(ctx.obj['config_path'])
        
        config_obj = config_loader.load_config()
        config_dict: Dict[str, Any] = config_obj.to_dict()
        
        # Validate configuration
        validation_report = validate_configuration(config_dict)
        
        if validation_report.is_valid:
            click.echo("✅ Configuration is valid!")
        else:
            click.echo("❌ Configuration validation failed!")
            
        # Display errors
        if validation_report.errors:
            click.echo("\n🚨 Errors:")
            for error in validation_report.errors:
                click.echo(f"  • {error}")
        
        # Display warnings
        if validation_report.warnings:
            click.echo("\n⚠️  Warnings:")
            for warning in validation_report.warnings:
                click.echo(f"  • {warning}")
        
        # Exit with appropriate code
        if not validation_report.is_valid:
            sys.exit(1)
            
    except ConfigurationError as e:
        click.echo(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        sys.exit(1)


@config.command()
@click.argument('key', required=True)
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'plain']), default='plain', help='Output format')
@click.pass_context
def get(ctx: click.Context, key: str, format: str) -> None:
    """Get configuration value by key (supports dot notation)."""
    try:
        # Load configuration
        config_loader = get_config_loader()
        if ctx.obj and ctx.obj.get('config_path'):
            config_loader.config_path = Path(ctx.obj['config_path'])
        
        config_obj = config_loader.load_config()
        config_dict: Dict[str, Any] = config_obj.to_dict()
        
        # Navigate to the key using dot notation
        value: Union[str, int, float, bool, List[Any], Dict[str, Any], None] = config_dict
        for key_part in key.split('.'):
            if isinstance(value, dict) and key_part in value:
                value = value[key_part]
            else:
                click.echo(f"❌ Key '{key}' not found in configuration")
                sys.exit(1)
        
        # Format output
        if format == 'json':
            click.echo(json.dumps(value, indent=2))
        elif format == 'yaml':
            click.echo(yaml.dump(value, default_flow_style=False))
        else:
            click.echo(str(value))
            
    except ConfigurationError as e:
        click.echo(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        sys.exit(1)


@config.command()
@click.option('--format', '-f', type=click.Choice(['json', 'yaml']), default='yaml', help='Output format')
@click.pass_context
def show(ctx: click.Context, format: str) -> None:
    """Show complete configuration."""
    try:
        # Load configuration
        config_loader = get_config_loader()
        if ctx.obj and ctx.obj.get('config_path'):
            config_loader.config_path = Path(ctx.obj['config_path'])
        
        config_obj = config_loader.load_config()
        config_dict: Dict[str, Any] = config_obj.to_dict()
        
        # Mask sensitive values
        masked_config: Dict[str, Any] = _mask_sensitive_values(config_dict)
        
        # Format output
        if format == 'json':
            click.echo(json.dumps(masked_config, indent=2))
        else:
            click.echo(yaml.dump(masked_config, default_flow_style=False))
            
    except ConfigurationError as e:
        click.echo(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        sys.exit(1)


@config.command()
@click.argument('environment', required=True)
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def generate_template(ctx: click.Context, environment: str, output: Optional[str]):
    """Generate configuration template for environment."""
    try:
        templates: Dict[str, Dict[str, Any]] = {
            'development': {
                'environment': 'development',
                'debug': True,
                'database': {
                    'host': 'localhost',
                    'port': 5432,
                    'name': 'sfm_dev_db',
                    'username': 'sfm_dev_user',
                    'pool_size': 5,
                    'ssl_mode': 'disable'
                },
                'cache': {
                    'backend': 'memory',
                    'max_size': 1000
                },
                'logging': {
                    'level': 'DEBUG',
                    'format': 'text',
                    'file_enabled': False
                }
            },
            'production': {
                'environment': 'production',
                'debug': False,
                'database': {
                    'host': 'prod-db.example.com',
                    'port': 5432,
                    'name': 'sfm_prod_db',
                    'username': 'sfm_prod_user',
                    'pool_size': 50,
                    'ssl_mode': 'require'
                },
                'cache': {
                    'backend': 'redis',
                    'host': 'prod-redis.example.com',
                    'max_size': 100000
                },
                'logging': {
                    'level': 'WARNING',
                    'format': 'json',
                    'file_enabled': True
                },
                'security': {
                    'encryption_enabled': True,
                    'audit_enabled': True
                }
            }
        }
        
        if environment not in templates:
            click.echo(f"❌ Unknown environment: {environment}")
            click.echo(f"Available environments: {', '.join(templates.keys())}")
            sys.exit(1)
        
        template: Dict[str, Any] = templates[environment]
        yaml_content: str = yaml.dump(template, default_flow_style=False)
        
        if output:
            with open(output, 'w') as f:
                f.write(yaml_content)
            click.echo(f"✅ Template saved to {output}")
        else:
            click.echo(yaml_content)
            
    except Exception as e:
        click.echo(f"❌ Error generating template: {e}")
        sys.exit(1)


@config.group()
def secrets():
    """Secrets management commands."""
    pass


@secrets.command()
@click.argument('key', required=True)
@click.option('--manager', '-m', type=click.Choice(['environment', 'aws', 'azure', 'vault']), 
              default='environment', help='Secrets manager type')
@click.option('--region', help='AWS region (for AWS secrets manager)')
@click.option('--vault-url', help='Vault URL (for HashiCorp Vault)')
@click.option('--vault-token', help='Vault token (for HashiCorp Vault)')
def get_secret(key: str, manager: str, region: Optional[str], vault_url: Optional[str], vault_token: Optional[str]) -> None:
    """Get a secret value."""
    try:
        # Create secrets manager
        kwargs: Dict[str, Union[str, int]] = {}
        if manager == 'aws' and region:
            kwargs['region'] = region
        elif manager == 'vault':
            if not vault_url or not vault_token:
                click.echo("❌ Vault URL and token are required for Vault secrets manager")
                sys.exit(1)
            kwargs['url'] = vault_url
            kwargs['token'] = vault_token
        secrets_manager: SecretsManager = SecretsManagerFactory.create_secrets_manager(manager, **kwargs) #type: ignore
        
        # Get secret
        secret_value: str = secrets_manager.get_secret(key)
        
        # Never display the actual secret value
        click.echo(f"✅ Secret '{key}' retrieved successfully")
        click.echo(f"📏 Length: {len(secret_value)} characters")
        
    except SecretNotFoundError:
        click.echo(f"❌ Secret '{key}' not found")
        sys.exit(1)
    except SecretsError as e:
        click.echo(f"❌ Secrets error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        sys.exit(1)


@secrets.command()
@click.argument('key', required=True)
@click.argument('value', required=True)
@click.option('--manager', '-m', type=click.Choice(['environment', 'aws', 'azure', 'vault']), 
              default='environment', help='Secrets manager type')
@click.option('--region', help='AWS region (for AWS secrets manager)')
@click.option('--vault-url', help='Vault URL (for HashiCorp Vault)')
@click.option('--vault-token', help='Vault token (for HashiCorp Vault)')
def set_secret(key: str, value: str, manager: str, region: Optional[str], vault_url: Optional[str], vault_token: Optional[str]) -> None:
    """Set a secret value."""
    try:
        # Create secrets manager
        kwargs: Dict[str, Union[str, int]] = {}
        if manager == 'aws' and region:
            kwargs['region'] = region
        elif manager == 'vault':
            if not vault_url or not vault_token:
                click.echo("❌ Vault URL and token are required for Vault secrets manager")
                sys.exit(1)
            kwargs['url'] = vault_url
            kwargs['token'] = vault_token
        secrets_manager: SecretsManager = SecretsManagerFactory.create_secrets_manager(manager, **kwargs) #type: ignore 
        
        # Set secret
        secrets_manager.set_secret(key, value)
        
        click.echo(f"✅ Secret '{key}' set successfully")
        
    except SecretsError as e:
        click.echo(f"❌ Secrets error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        sys.exit(1)


@secrets.command()
@click.option('--manager', '-m', type=click.Choice(['environment', 'aws', 'azure', 'vault']), 
              default='environment', help='Secrets manager type')
@click.option('--region', help='AWS region (for AWS secrets manager)')
@click.option('--vault-url', help='Vault URL (for HashiCorp Vault)')
@click.option('--vault-token', help='Vault token (for HashiCorp Vault)')
def list_secrets(manager: str, region: Optional[str], vault_url: Optional[str], vault_token: Optional[str]) -> None:
    """List all secrets."""
    try:
        # Create secrets manager
        kwargs: Dict[str, Union[str, int]] = {}
        if manager == 'aws' and region:
            kwargs['region'] = region
        elif manager == 'vault':
            if not vault_url or not vault_token:
                click.echo("❌ Vault URL and token are required for Vault secrets manager")
                sys.exit(1)
            kwargs['url'] = vault_url
            kwargs['token'] = vault_token
        secrets_manager: SecretsManager = SecretsManagerFactory.create_secrets_manager(manager, **kwargs) #type: ignore
        
        # List secrets
        secret_keys: List[str] = secrets_manager.list_secrets()
        
        if secret_keys:
            click.echo(f"📋 Found {len(secret_keys)} secrets:")
            for key in sorted(secret_keys):
                click.echo(f"  • {key}")
        else:
            click.echo("📋 No secrets found")
        
    except SecretsError as e:
        click.echo(f"❌ Secrets error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        sys.exit(1)


@config.command()
@click.pass_context
def test(ctx: click.Context) -> None:
    """Test configuration loading and validation."""
    click.echo("🧪 Testing configuration...")
    
    try:
        # Test configuration loading
        click.echo("  📥 Loading configuration...")
        config_loader = get_config_loader()
        if ctx.obj and ctx.obj.get('config_path'):
            config_loader.config_path = Path(ctx.obj['config_path'])
        
        config_obj = config_loader.load_config()
        click.echo("  ✅ Configuration loaded successfully")
        
        # Test validation
        click.echo("  🔍 Validating configuration...")
        config_dict: Dict[str, Any] = config_obj.to_dict()
        validation_report = validate_configuration(config_dict)
        
        if validation_report.is_valid:
            click.echo("  ✅ Configuration validation passed")
        else:
            click.echo("  ❌ Configuration validation failed")
            for error in validation_report.errors:
                click.echo(f"    • {error}")
        
        # Test database connection (mock)
        click.echo("  🔌 Testing database connection...")
        if config_obj.database.host and config_obj.database.port:
            click.echo("  ✅ Database configuration looks valid")
        else:
            click.echo("  ❌ Database configuration is incomplete")
        
        # Test cache configuration
        click.echo("  💾 Testing cache configuration...")
        if config_obj.cache.backend:
            click.echo(f"  ✅ Cache backend: {config_obj.cache.backend}")
        else:
            click.echo("  ❌ Cache backend not configured")
        
        click.echo("🎉 Configuration test completed!")
        
    except ConfigurationError as e:
        click.echo(f"❌ Configuration test failed: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error during test: {e}")
        sys.exit(1)


def _mask_sensitive_values(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive values in configuration dictionary."""
    sensitive_keys = {
        'password', 'secret', 'key', 'token', 'jwt_secret', 
        'secret_key', 'encryption_key'
    }
    
    def mask_dict(d: Any) -> Any:
        if isinstance(d, dict):
            masked_dict: Dict[str, Any] = {}
            for k, v in d.items(): #type: ignore
                # Type narrowing: ensure k is treated as a string when checking
                key_str = str(k) #type: ignore # Convert to string for safety
                if any(sens in key_str.lower() for sens in sensitive_keys):
                    if isinstance(v, (str, int, float, bool)):
                        masked_dict[k] = '***MASKED***'
                    else:
                        masked_dict[k] = mask_dict(v)
                else:
                    masked_dict[k] = mask_dict(v)
            return masked_dict
        elif isinstance(d, list):
            return [mask_dict(item) for item in d] #type: ignore
        else:
            return d
    
    return mask_dict(config_dict)


if __name__ == '__main__':
    config()