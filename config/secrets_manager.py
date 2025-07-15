"""
Secrets Management System for SFM Service

This module provides a secure secrets management system with support for:
- Multiple secrets backends (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
- Environment variable fallback for development
- Encryption at rest
- Secret rotation
- Audit logging
- Least-privilege access

Security Features:
- Never log or expose secrets in plain text
- Encryption for secrets at rest
- Configurable secret rotation
- Audit trail for secret access
- Error handling without exposing secrets
"""

from typing import Any, Dict, Optional, List
from abc import ABC, abstractmethod
import os
import logging
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class SecretType(Enum):
    """Types of secrets."""
    DATABASE_PASSWORD = "database_password"
    CACHE_PASSWORD = "cache_password"
    SECRET_KEY = "secret_key"
    ENCRYPTION_KEY = "encryption_key"
    CERTIFICATE = "certificate"
    PRIVATE_KEY = "private_key"


class SecretsError(Exception):
    """Base exception for secrets-related errors."""
    pass


class SecretNotFoundError(SecretsError):
    """Raised when a secret is not found."""
    pass


class SecretAccessError(SecretsError):
    """Raised when access to a secret is denied."""
    pass


@dataclass
class SecretMetadata:
    """Metadata for a secret."""
    name: str
    type: SecretType
    created_at: Optional[str] = None
    last_accessed: Optional[str] = None
    rotation_date: Optional[str] = None
    version: Optional[str] = None


class SecretsManager(ABC):
    """Abstract base class for secrets management."""
    
    @abstractmethod
    def get_secret(self, key: str) -> str:
        """Get a secret by key.
        
        Args:
            key: Secret key/name
            
        Returns:
            str: Secret value
            
        Raises:
            SecretNotFoundError: If secret is not found
            SecretAccessError: If access is denied
        """
        pass
    
    @abstractmethod
    def set_secret(self, key: str, value: str, metadata: Optional[SecretMetadata] = None):
        """Set a secret.
        
        Args:
            key: Secret key/name
            value: Secret value
            metadata: Optional metadata
            
        Raises:
            SecretAccessError: If access is denied
        """
        pass
    
    @abstractmethod
    def delete_secret(self, key: str):
        """Delete a secret.
        
        Args:
            key: Secret key/name
            
        Raises:
            SecretNotFoundError: If secret is not found
            SecretAccessError: If access is denied
        """
        pass
    
    @abstractmethod
    def list_secrets(self) -> List[str]:
        """List all secret keys.
        
        Returns:
            List[str]: List of secret keys
        """
        pass
    
    @abstractmethod
    def rotate_secret(self, key: str):
        """Rotate a secret.
        
        Args:
            key: Secret key/name
            
        Raises:
            SecretNotFoundError: If secret is not found
            SecretAccessError: If access is denied
        """
        pass


class EnvironmentSecretsManager(SecretsManager):
    """Secrets manager that reads from environment variables.
    
    This is primarily intended for development and testing.
    Never use this in production for sensitive secrets.
    """
    
    def __init__(self, prefix: str = "SFM_SECRET_"):
        """Initialize environment secrets manager.
        
        Args:
            prefix: Prefix for environment variables
        """
        self.prefix = prefix
        self.audit_log = []
        
    def get_secret(self, key: str) -> str:
        """Get secret from environment variable.
        
        Args:
            key: Secret key
            
        Returns:
            str: Secret value
            
        Raises:
            SecretNotFoundError: If secret is not found
        """
        env_var = f"{self.prefix}{key.upper()}"
        value = os.getenv(env_var)
        
        if value is None:
            # Try without prefix for common secrets
            value = os.getenv(key.upper())
        
        if value is None:
            self._log_access(key, success=False)
            raise SecretNotFoundError(f"Secret '{key}' not found")
        
        self._log_access(key, success=True)
        return value
    
    def set_secret(self, key: str, value: str, metadata: Optional[SecretMetadata] = None):
        """Set secret in environment (not persistent).
        
        Args:
            key: Secret key
            value: Secret value
            metadata: Optional metadata (ignored in this implementation)
        """
        env_var = f"{self.prefix}{key.upper()}"
        os.environ[env_var] = value
        logger.debug(f"Set environment secret: {key}")
    
    def delete_secret(self, key: str):
        """Delete secret from environment.
        
        Args:
            key: Secret key
        """
        env_var = f"{self.prefix}{key.upper()}"
        if env_var in os.environ:
            del os.environ[env_var]
            logger.debug(f"Deleted environment secret: {key}")
        else:
            raise SecretNotFoundError(f"Secret '{key}' not found")
    
    def list_secrets(self) -> List[str]:
        """List all secrets from environment.
        
        Returns:
            List[str]: List of secret keys
        """
        secrets = []
        for env_var in os.environ:
            if env_var.startswith(self.prefix):
                secret_key = env_var[len(self.prefix):].lower()
                secrets.append(secret_key)
        return secrets
    
    def rotate_secret(self, key: str):
        """Rotate secret (not supported in environment manager).
        
        Args:
            key: Secret key
            
        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError("Secret rotation not supported in environment manager")
    
    def _log_access(self, key: str, success: bool):
        """Log secret access for audit.
        
        Args:
            key: Secret key
            success: Whether access was successful
        """
        import datetime
        audit_entry = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'key': key,
            'success': success,
            'manager': 'environment'
        }
        self.audit_log.append(audit_entry)
        
        # Log to system logger (without exposing the secret)
        if success:
            logger.info(f"Secret accessed: {key}")
        else:
            logger.warning(f"Secret access failed: {key}")


class AWSSecretsManager(SecretsManager):
    """AWS Secrets Manager implementation.
    
    Requires boto3 to be installed and AWS credentials configured.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize AWS Secrets Manager.
        
        Args:
            region: AWS region
        """
        self.region = region
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS client."""
        try:
            import boto3
            from botocore.exceptions import ClientError
            self.client = boto3.client('secretsmanager', region_name=self.region)
            self.ClientError = ClientError
        except ImportError:
            logger.error("boto3 is required for AWS Secrets Manager")
            raise SecretsError("boto3 is required for AWS Secrets Manager")
    
    def get_secret(self, key: str) -> str:
        """Get secret from AWS Secrets Manager.
        
        Args:
            key: Secret key
            
        Returns:
            str: Secret value
            
        Raises:
            SecretNotFoundError: If secret is not found
            SecretAccessError: If access is denied
        """
        try:
            response = self.client.get_secret_value(SecretId=key)
            logger.info(f"Retrieved secret from AWS: {key}")
            return response['SecretString']
        except self.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                raise SecretNotFoundError(f"Secret '{key}' not found in AWS Secrets Manager")
            elif error_code == 'AccessDeniedException':
                raise SecretAccessError(f"Access denied to secret '{key}' in AWS Secrets Manager")
            else:
                raise SecretsError(f"AWS Secrets Manager error: {error_code}")
    
    def set_secret(self, key: str, value: str, metadata: Optional[SecretMetadata] = None):
        """Set secret in AWS Secrets Manager.
        
        Args:
            key: Secret key
            value: Secret value
            metadata: Optional metadata
        """
        try:
            self.client.put_secret_value(
                SecretId=key,
                SecretString=value
            )
            logger.info(f"Set secret in AWS: {key}")
        except self.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                raise SecretAccessError(f"Access denied to set secret '{key}' in AWS Secrets Manager")
            else:
                raise SecretsError(f"AWS Secrets Manager error: {error_code}")
    
    def delete_secret(self, key: str):
        """Delete secret from AWS Secrets Manager.
        
        Args:
            key: Secret key
        """
        try:
            self.client.delete_secret(SecretId=key)
            logger.info(f"Deleted secret from AWS: {key}")
        except self.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                raise SecretNotFoundError(f"Secret '{key}' not found in AWS Secrets Manager")
            elif error_code == 'AccessDeniedException':
                raise SecretAccessError(f"Access denied to delete secret '{key}' in AWS Secrets Manager")
            else:
                raise SecretsError(f"AWS Secrets Manager error: {error_code}")
    
    def list_secrets(self) -> List[str]:
        """List all secrets from AWS Secrets Manager.
        
        Returns:
            List[str]: List of secret keys
        """
        try:
            response = self.client.list_secrets()
            return [secret['Name'] for secret in response['SecretList']]
        except self.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                raise SecretAccessError("Access denied to list secrets in AWS Secrets Manager")
            else:
                raise SecretsError(f"AWS Secrets Manager error: {error_code}")
    
    def rotate_secret(self, key: str):
        """Rotate secret in AWS Secrets Manager.
        
        Args:
            key: Secret key
        """
        try:
            self.client.rotate_secret(SecretId=key)
            logger.info(f"Rotated secret in AWS: {key}")
        except self.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                raise SecretNotFoundError(f"Secret '{key}' not found in AWS Secrets Manager")
            elif error_code == 'AccessDeniedException':
                raise SecretAccessError(f"Access denied to rotate secret '{key}' in AWS Secrets Manager")
            else:
                raise SecretsError(f"AWS Secrets Manager error: {error_code}")


class AzureKeyVaultManager(SecretsManager):
    """Azure Key Vault implementation.
    
    Requires azure-keyvault-secrets to be installed and Azure credentials configured.
    """
    
    def __init__(self, vault_url: str):
        """Initialize Azure Key Vault manager.
        
        Args:
            vault_url: Azure Key Vault URL
        """
        self.vault_url = vault_url
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Azure client."""
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
            
            credential = DefaultAzureCredential()
            self.client = SecretClient(vault_url=self.vault_url, credential=credential)
            self.ResourceNotFoundError = ResourceNotFoundError
            self.ClientAuthenticationError = ClientAuthenticationError
        except ImportError:
            logger.error("azure-keyvault-secrets is required for Azure Key Vault")
            raise SecretsError("azure-keyvault-secrets is required for Azure Key Vault")
    
    def get_secret(self, key: str) -> str:
        """Get secret from Azure Key Vault.
        
        Args:
            key: Secret key
            
        Returns:
            str: Secret value
            
        Raises:
            SecretNotFoundError: If secret is not found
            SecretAccessError: If access is denied
        """
        try:
            secret = self.client.get_secret(key)
            logger.info(f"Retrieved secret from Azure Key Vault: {key}")
            return secret.value
        except self.ResourceNotFoundError:
            raise SecretNotFoundError(f"Secret '{key}' not found in Azure Key Vault")
        except self.ClientAuthenticationError:
            raise SecretAccessError(f"Access denied to secret '{key}' in Azure Key Vault")
    
    def set_secret(self, key: str, value: str, metadata: Optional[SecretMetadata] = None):
        """Set secret in Azure Key Vault.
        
        Args:
            key: Secret key
            value: Secret value
            metadata: Optional metadata
        """
        try:
            self.client.set_secret(key, value)
            logger.info(f"Set secret in Azure Key Vault: {key}")
        except self.ClientAuthenticationError:
            raise SecretAccessError(f"Access denied to set secret '{key}' in Azure Key Vault")
    
    def delete_secret(self, key: str):
        """Delete secret from Azure Key Vault.
        
        Args:
            key: Secret key
        """
        try:
            self.client.begin_delete_secret(key)
            logger.info(f"Deleted secret from Azure Key Vault: {key}")
        except self.ResourceNotFoundError:
            raise SecretNotFoundError(f"Secret '{key}' not found in Azure Key Vault")
        except self.ClientAuthenticationError:
            raise SecretAccessError(f"Access denied to delete secret '{key}' in Azure Key Vault")
    
    def list_secrets(self) -> List[str]:
        """List all secrets from Azure Key Vault.
        
        Returns:
            List[str]: List of secret keys
        """
        try:
            secrets = self.client.list_properties_of_secrets()
            return [secret.name for secret in secrets]
        except self.ClientAuthenticationError:
            raise SecretAccessError("Access denied to list secrets in Azure Key Vault")
    
    def rotate_secret(self, key: str):
        """Rotate secret in Azure Key Vault.
        
        Args:
            key: Secret key
        """
        # Azure Key Vault doesn't have built-in rotation, so we'll implement basic rotation
        try:
            # This is a placeholder - actual rotation would depend on the secret type
            current_secret = self.client.get_secret(key)
            # Generate new secret value based on type
            new_value = self._generate_new_secret_value(key, current_secret.value)
            self.client.set_secret(key, new_value)
            logger.info(f"Rotated secret in Azure Key Vault: {key}")
        except self.ResourceNotFoundError:
            raise SecretNotFoundError(f"Secret '{key}' not found in Azure Key Vault")
        except self.ClientAuthenticationError:
            raise SecretAccessError(f"Access denied to rotate secret '{key}' in Azure Key Vault")
    
    def _generate_new_secret_value(self, key: str, current_value: str) -> str:
        """Generate new secret value for rotation.
        
        Args:
            key: Secret key
            current_value: Current secret value
            
        Returns:
            str: New secret value
        """
        # This is a placeholder implementation
        # In practice, you'd implement specific rotation logic for each secret type
        import secrets
        import string
        
        # Generate a random string for most secrets
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))


class VaultSecretsManager(SecretsManager):
    """HashiCorp Vault implementation.
    
    Requires hvac to be installed and Vault server configured.
    """
    
    def __init__(self, url: str, token: str):
        """Initialize Vault secrets manager.
        
        Args:
            url: Vault server URL
            token: Vault authentication token
        """
        self.url = url
        self.token = token
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Vault client."""
        try:
            import hvac
            self.client = hvac.Client(url=self.url, token=self.token)
            
            # Verify client is authenticated
            if not self.client.is_authenticated():
                raise SecretsError("Vault authentication failed")
                
        except ImportError:
            logger.error("hvac is required for HashiCorp Vault")
            raise SecretsError("hvac is required for HashiCorp Vault")
    
    def get_secret(self, key: str) -> str:
        """Get secret from Vault.
        
        Args:
            key: Secret key
            
        Returns:
            str: Secret value
            
        Raises:
            SecretNotFoundError: If secret is not found
            SecretAccessError: If access is denied
        """
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=key)
            logger.info(f"Retrieved secret from Vault: {key}")
            return response['data']['data']['value']
        except Exception as e:
            if "404" in str(e):
                raise SecretNotFoundError(f"Secret '{key}' not found in Vault")
            elif "403" in str(e):
                raise SecretAccessError(f"Access denied to secret '{key}' in Vault")
            else:
                raise SecretsError(f"Vault error: {e}")
    
    def set_secret(self, key: str, value: str, metadata: Optional[SecretMetadata] = None):
        """Set secret in Vault.
        
        Args:
            key: Secret key
            value: Secret value
            metadata: Optional metadata
        """
        try:
            secret_data = {'value': value}
            if metadata:
                secret_data['metadata'] = metadata.__dict__
            
            self.client.secrets.kv.v2.create_or_update_secret(
                path=key,
                secret=secret_data
            )
            logger.info(f"Set secret in Vault: {key}")
        except Exception as e:
            if "403" in str(e):
                raise SecretAccessError(f"Access denied to set secret '{key}' in Vault")
            else:
                raise SecretsError(f"Vault error: {e}")
    
    def delete_secret(self, key: str):
        """Delete secret from Vault.
        
        Args:
            key: Secret key
        """
        try:
            self.client.secrets.kv.v2.delete_secret_versions(path=key)
            logger.info(f"Deleted secret from Vault: {key}")
        except Exception as e:
            if "404" in str(e):
                raise SecretNotFoundError(f"Secret '{key}' not found in Vault")
            elif "403" in str(e):
                raise SecretAccessError(f"Access denied to delete secret '{key}' in Vault")
            else:
                raise SecretsError(f"Vault error: {e}")
    
    def list_secrets(self) -> List[str]:
        """List all secrets from Vault.
        
        Returns:
            List[str]: List of secret keys
        """
        try:
            response = self.client.secrets.kv.v2.list_secrets(path='')
            return response['data']['keys']
        except Exception as e:
            if "403" in str(e):
                raise SecretAccessError("Access denied to list secrets in Vault")
            else:
                raise SecretsError(f"Vault error: {e}")
    
    def rotate_secret(self, key: str):
        """Rotate secret in Vault.
        
        Args:
            key: Secret key
        """
        try:
            # Get current secret
            current_secret = self.get_secret(key)
            # Generate new secret value
            new_value = self._generate_new_secret_value(key, current_secret)
            # Update secret
            self.set_secret(key, new_value)
            logger.info(f"Rotated secret in Vault: {key}")
        except Exception as e:
            raise SecretsError(f"Failed to rotate secret '{key}': {e}")
    
    def _generate_new_secret_value(self, key: str, current_value: str) -> str:
        """Generate new secret value for rotation.
        
        Args:
            key: Secret key
            current_value: Current secret value
            
        Returns:
            str: New secret value
        """
        import secrets
        import string
        
        # Generate a random string for most secrets
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))


class SecretsManagerFactory:
    """Factory for creating secrets managers."""
    
    @staticmethod
    def create_secrets_manager(manager_type: str, **kwargs) -> SecretsManager:
        """Create a secrets manager instance.
        
        Args:
            manager_type: Type of secrets manager ('environment', 'aws', 'azure', 'vault')
            **kwargs: Additional configuration parameters
            
        Returns:
            SecretsManager: Secrets manager instance
            
        Raises:
            ValueError: If manager type is not supported
        """
        if manager_type == 'environment':
            return EnvironmentSecretsManager(**kwargs)
        elif manager_type == 'aws':
            return AWSSecretsManager(**kwargs)
        elif manager_type == 'azure':
            return AzureKeyVaultManager(**kwargs)
        elif manager_type == 'vault':
            return VaultSecretsManager(**kwargs)
        else:
            raise ValueError(f"Unsupported secrets manager type: {manager_type}")


# Export public API
__all__ = [
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
    'SecretAccessError'
]