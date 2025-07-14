# Configuration Management System

The SFM service now includes a comprehensive configuration management system that provides centralized, environment-aware configuration with secure secrets management.

## Features

### 🔧 Core Configuration Management
- **Environment-specific configurations** - Support for development, staging, production, and testing environments
- **Configuration merging** - Hierarchical configuration loading with proper priority
- **Type-safe configuration** - Strongly typed configuration with validation
- **Hot reloading** - Runtime configuration updates without restart

### 🔐 Secrets Management
- **Multiple backends** - AWS Secrets Manager, Azure Key Vault, HashiCorp Vault, Environment variables
- **Secure handling** - Never log or expose secrets in plain text
- **Audit logging** - Track secret access and modifications
- **Rotation support** - Built-in secret rotation capabilities

### ✅ Configuration Validation
- **Pydantic validation** - Comprehensive type and business rule validation
- **Environment-specific rules** - Different validation rules for different environments
- **Detailed error reporting** - Clear error messages with remediation suggestions
- **Security validation** - Ensure secure configurations for production

### 🛠️ CLI Tools
- **Configuration validation** - `python config/cli.py validate`
- **Configuration inspection** - `python config/cli.py show`
- **Secrets management** - `python config/cli.py secrets`
- **Template generation** - `python config/cli.py generate-template`

## Configuration Structure

```yaml
# config/config.yml (base configuration)
environment: development
debug: false
version: "1.0.0"

database:
  host: localhost
  port: 5432
  name: sfm_db
  username: sfm_user
  password: ""  # Loaded from secrets manager
  pool_size: 10
  timeout: 30
  ssl_mode: disable
  max_connections: 100

cache:
  backend: memory
  host: localhost
  port: 6379
  ttl: 3600
  max_size: 10000

api:
  host: 0.0.0.0
  port: 8000
  debug: false
  cors_origins:
    - "http://localhost:3000"
  rate_limit: "100/hour"
  jwt_secret: ""  # Loaded from secrets manager

logging:
  level: INFO
  format: json
  file_enabled: false
  console_enabled: true

security:
  secret_key: ""  # Loaded from secrets manager
  encryption_enabled: false
  audit_enabled: true
  session_timeout: 3600
```

## Configuration Loading Priority

1. **Default values** - Defined in dataclasses
2. **Base configuration** - `config/config.yml`
3. **Environment-specific** - `config/config.{environment}.yml`
4. **Environment variables** - `SFM_*` prefixed variables
5. **Secrets manager** - For sensitive configuration

## Environment-Specific Configuration

The system supports different environments with specific configurations:

### Development (`config/config.development.yml`)
```yaml
environment: development
debug: true
database:
  name: sfm_dev_db
  pool_size: 5
cache:
  backend: memory
  max_size: 500
logging:
  level: DEBUG
  format: text
```

### Production (`config/config.production.yml`)
```yaml
environment: production
debug: false
database:
  host: prod-db-cluster.example.com
  ssl_mode: require
  pool_size: 50
cache:
  backend: redis
  host: prod-redis-cluster.example.com
  max_size: 100000
logging:
  level: WARNING
  format: json
  file_enabled: true
security:
  encryption_enabled: true
```

## Environment Variables

Override configuration using environment variables:

```bash
# Database configuration
export SFM_DATABASE_HOST=localhost
export SFM_DATABASE_PORT=5432
export SFM_DATABASE_NAME=sfm_db
export SFM_DATABASE_PASSWORD=secret

# API configuration
export SFM_API_HOST=0.0.0.0
export SFM_API_PORT=8000
export SFM_API_DEBUG=true

# General configuration
export SFM_ENVIRONMENT=development
export SFM_DEBUG=true
export SFM_LOG_LEVEL=DEBUG
```

## Secrets Management

### Environment Variables (Development)
```bash
export SFM_SECRET_DATABASE_PASSWORD=my_secret_password
export SFM_SECRET_JWT_SECRET=my_jwt_secret
export SFM_SECRET_SECRET_KEY=my_secret_key
```

### AWS Secrets Manager
```python
from config.secrets_manager import AWSSecretsManager

secrets_manager = AWSSecretsManager(region='us-east-1')
password = secrets_manager.get_secret('database_password')
```

### Azure Key Vault
```python
from config.secrets_manager import AzureKeyVaultManager

secrets_manager = AzureKeyVaultManager(
    vault_url='https://my-vault.vault.azure.net/'
)
password = secrets_manager.get_secret('database_password')
```

## CLI Usage

### Validate Configuration
```bash
# Validate current configuration
python config/cli.py validate

# Validate specific environment
python config/cli.py -e production validate
```

### Show Configuration
```bash
# Show current configuration
python config/cli.py show

# Show in JSON format
python config/cli.py show -f json
```

### Get Configuration Values
```bash
# Get specific configuration value
python config/cli.py get database.host
python config/cli.py get api.port
python config/cli.py get logging.level
```

### Secrets Management
```bash
# Set a secret
python config/cli.py secrets set-secret database_password "my_secret"

# Get a secret (shows length only for security)
python config/cli.py secrets get-secret database_password

# List all secrets
python config/cli.py secrets list-secrets
```

### Generate Configuration Templates
```bash
# Generate development template
python config/cli.py generate-template development

# Generate production template
python config/cli.py generate-template production -o config.prod.yml
```

## API Integration

The configuration system is integrated with the FastAPI application:

### Configuration Status Endpoint
```bash
curl http://localhost:8000/config/status
```

### Configuration Reload Endpoint
```bash
curl -X POST http://localhost:8000/config/reload
```

## Service Integration

The SFM service automatically uses the configuration system:

```python
from core.sfm_service import SFMService

# Service automatically loads configuration
service = SFMService()

# Configuration is available via service.config
print(f"Environment: {service.config.global_config.environment}")
print(f"Debug mode: {service.config.global_config.debug}")
```

## Configuration Validation

The system includes comprehensive validation:

```python
from config.validation import validate_configuration

config_dict = {...}  # Your configuration
report = validate_configuration(config_dict)

if report.is_valid:
    print("Configuration is valid")
else:
    print("Validation errors:")
    for error in report.errors:
        print(f"  - {error}")
```

## Security Best Practices

1. **Never commit secrets** - Use `.gitignore` to exclude secrets files
2. **Use environment-specific configs** - Different security levels per environment
3. **Enable encryption** - Turn on encryption for production environments
4. **Validate SSL settings** - Ensure SSL is enabled for production databases
5. **Use secrets managers** - Prefer cloud-based secrets management for production
6. **Audit configuration changes** - Track who changed what and when

## Testing

Run the configuration system tests:

```bash
# Run all configuration tests
python -m pytest tests/test_config_system.py -v

# Run specific test
python -m pytest tests/test_config_system.py::TestConfigLoader::test_load_environment_specific_config -v
```

## Demo

Run the configuration demo to see all features in action:

```bash
python demo_config.py
```

This will demonstrate:
- Basic configuration loading
- Environment-specific configurations
- Configuration validation
- Secrets management
- Service integration
- Environment variable overrides
- Configuration merging

## Implementation Details

### Configuration Schema
The configuration schema is defined using dataclasses with proper type hints:

```python
@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    name: str = "sfm_db"
    username: str = "sfm_user"
    password: str = ""
    pool_size: int = 10
    timeout: int = 30
    ssl_mode: str = "disable"
    max_connections: int = 100
```

### Configuration Merging
The system uses deep merging to combine configuration from multiple sources:

```python
def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = self._deep_merge(result[key], value)
        else:
            result[key] = value
    return result
```

### Secrets Manager Interface
All secrets managers implement a common interface:

```python
class SecretsManager(ABC):
    @abstractmethod
    def get_secret(self, key: str) -> str:
        pass
    
    @abstractmethod
    def set_secret(self, key: str, value: str, metadata: Optional[SecretMetadata] = None):
        pass
    
    @abstractmethod
    def delete_secret(self, key: str):
        pass
```

## Future Enhancements

- **Hot reloading** - Runtime configuration updates
- **Configuration versioning** - Track configuration changes over time
- **Remote configuration** - Load configuration from remote sources
- **Configuration UI** - Web interface for configuration management
- **Multi-tenant support** - Per-tenant configuration overrides
- **Configuration drift detection** - Detect configuration changes in deployed systems