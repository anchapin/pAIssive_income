"""
HashiCorp Vault Backend for Secrets Management

This module provides integration with HashiCorp Vault for secrets storage and retrieval.
"""

import os
import logging
from typing import Dict, List, Optional, Any
import hvac

# Set up logging
logger = logging.getLogger(__name__)


class VaultBackend:
    """
    HashiCorp Vault backend for secrets management.
    """
    
    def __init__(self, 
                url: Optional[str] = None,
                token: Optional[str] = None,
                mount_point: str = 'secret',
                namespace: Optional[str] = None):
        """
        Initialize the Vault backend.
        
        Args:
            url: Vault server URL
            token: Vault authentication token
            mount_point: Mount point for the KV secrets engine
            namespace: Vault namespace (Enterprise only)
        """
        self.url = url or os.environ.get('VAULT_ADDR', 'http://127.0.0.1:8200')
        self.token = token or os.environ.get('VAULT_TOKEN')
        self.mount_point = mount_point
        self.namespace = namespace or os.environ.get('VAULT_NAMESPACE')
        self.client = None
        
        # Validate configuration
        if not self.token:
            logger.warning("Vault token not provided. Set VAULT_TOKEN environment variable.")
    
    def _connect(self) -> bool:
        """
        Connect to the Vault server.
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.client is not None and self.client.is_authenticated():
            return True
            
        try:
            client_kwargs = {
                'url': self.url,
                'token': self.token
            }
            
            if self.namespace:
                client_kwargs['namespace'] = self.namespace
                
            self.client = hvac.Client(**client_kwargs)
            
            # Check authentication
            if not self.client.is_authenticated():
                logger.error("Failed to authenticate with Vault")
                return False
                
            logger.debug("Successfully connected to Vault")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Vault: {str(e)}")
            return False
    
    def get_secret(self, name: str, default: Optional[str] = None, path: str = 'paissive') -> Optional[str]:
        """
        Get a secret from Vault.
        
        Args:
            name: Secret name
            default: Default value if secret not found
            path: Path in Vault where the secret is stored
            
        Returns:
            Secret value or default
        """
        if not self._connect():
            return default
            
        try:
            # Read from Vault
            secret_path = f"{path}/{name}"
            read_response = self.client.secrets.kv.v2.read_secret_version(
                path=secret_path,
                mount_point=self.mount_point
            )
            
            # Extract the value
            if read_response and 'data' in read_response and 'data' in read_response['data']:
                if 'value' in read_response['data']['data']:
                    return read_response['data']['data']['value']
                    
            logger.debug(f"Secret '{name}' not found in Vault")
            return default
        except Exception as e:
            logger.error(f"Error reading secret from Vault: {str(e)}")
            return default
    
    def set_secret(self, name: str, value: str, path: str = 'paissive') -> bool:
        """
        Store a secret in Vault.
        
        Args:
            name: Secret name
            value: Secret value
            path: Path in Vault where to store the secret
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connect():
            return False
            
        try:
            # Store in Vault
            secret_path = f"{path}/{name}"
            self.client.secrets.kv.v2.create_or_update_secret(
                path=secret_path,
                secret={"value": value},
                mount_point=self.mount_point
            )
            
            logger.debug(f"Secret '{name}' stored in Vault")
            return True
        except Exception as e:
            logger.error(f"Error storing secret in Vault: {str(e)}")
            return False
    
    def delete_secret(self, name: str, path: str = 'paissive') -> bool:
        """
        Delete a secret from Vault.
        
        Args:
            name: Secret name
            path: Path in Vault where the secret is stored
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connect():
            return False
            
        try:
            # Delete from Vault
            secret_path = f"{path}/{name}"
            self.client.secrets.kv.v2.delete_latest_version_of_secret(
                path=secret_path,
                mount_point=self.mount_point
            )
            
            logger.debug(f"Secret '{name}' deleted from Vault")
            return True
        except Exception as e:
            logger.error(f"Error deleting secret from Vault: {str(e)}")
            return False
    
    def list_secrets(self, path: str = 'paissive') -> List[str]:
        """
        List all secrets in a path.
        
        Args:
            path: Path in Vault to list secrets from
            
        Returns:
            List of secret names
        """
        if not self._connect():
            return []
            
        try:
            # List secrets in Vault
            list_response = self.client.secrets.kv.v2.list_secrets(
                path=path,
                mount_point=self.mount_point
            )
            
            if list_response and 'data' in list_response and 'keys' in list_response['data']:
                return list_response['data']['keys']
                
            return []
        except Exception as e:
            logger.error(f"Error listing secrets from Vault: {str(e)}")
            return []