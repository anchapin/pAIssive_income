"""
Secret Configuration Management

This module provides a convenient configuration interface for application settings that may contain secrets.
"""

from typing import Any, Dict, Optional, Union, List
import os
import json
import logging
from pathlib import Path
from .secrets_manager import get_secret, set_secret, SecretsBackend

# Set up logging
logger = logging.getLogger(__name__)

# Default configuration file path
DEFAULT_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".paissive", "config.json")


class SecretConfig:
    """
    Configuration manager that handles secrets.
    
    This class provides a unified interface for accessing configuration values that may contain
    secrets, with support for hierarchical configuration and fallbacks.
    """
    
    def __init__(self, 
                 config_file: Optional[str] = None,
                 secrets_backend: str = SecretsBackend.ENV_VAR,
                 env_prefix: str = "PAISSIVE_"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file (optional)
            secrets_backend: Backend to use for secrets (env, file, memory, vault)
            env_prefix: Prefix for environment variables
        """
        self.config_file = config_file or DEFAULT_CONFIG_FILE
        self.secrets_backend = secrets_backend
        self.env_prefix = env_prefix
        self.config_data = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file if it exists."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config_data = json.load(f)
                logger.debug(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
                self.config_data = {}
    
    def _save_config(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Write the configuration
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            
            # Set secure permissions
            os.chmod(self.config_file, 0o600)
            
            logger.debug(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None, use_secret: bool = False) -> Any:
        """
        Get a configuration value, optionally treating it as a secret.
        
        Args:
            key: The configuration key (supports dot notation for nested config)
            default: Default value if not found
            use_secret: Whether to treat the value as a secret
            
        Returns:
            The configuration value or default
        """
        # If it's a secret, try to get it from the secrets backend
        if use_secret:
            secret_value = get_secret(key, default=None, backend=self.secrets_backend)
            if secret_value is not None:
                return secret_value
        
        # Check environment variables (with prefix)
        env_var_name = f"{self.env_prefix}{key.upper().replace('.', '_')}"
        env_value = os.environ.get(env_var_name)
        if env_value is not None:
            return env_value
        
        # Check configuration file
        if '.' in key:
            # Handle nested keys
            parts = key.split('.')
            current = self.config_data
            for part in parts[:-1]:
                if not isinstance(current, dict) or part not in current:
                    return default
                current = current[part]
            
            # Get the final value
            if not isinstance(current, dict) or parts[-1] not in current:
                return default
            return current[parts[-1]]
        else:
            # Simple key
            return self.config_data.get(key, default)
        
        return default
    
    def set(self, key: str, value: Any, use_secret: bool = False) -> bool:
        """
        Set a configuration value, optionally treating it as a secret.
        
        Args:
            key: The configuration key (supports dot notation for nested config)
            value: The value to set
            use_secret: Whether to treat the value as a secret
            
        Returns:
            True if successful, False otherwise
        """
        # If it's a secret, store it in the secrets backend
        if use_secret:
            return set_secret(key, str(value), backend=self.secrets_backend)
        
        # Store in configuration file
        if '.' in key:
            # Handle nested keys
            parts = key.split('.')
            current = self.config_data
            for part in parts[:-1]:
                if part not in current or not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]
            
            # Set the final value
            current[parts[-1]] = value
        else:
            # Simple key
            self.config_data[key] = value
        
        # Save the updated configuration
        return self._save_config()
    
    def delete(self, key: str, use_secret: bool = False) -> bool:
        """
        Delete a configuration value, optionally treating it as a secret.
        
        Args:
            key: The configuration key (supports dot notation for nested config)
            use_secret: Whether it's a secret
            
        Returns:
            True if successful, False otherwise
        """
        success = True
        
        # Delete from secrets backend if it's a secret
        if use_secret:
            from .secrets_manager import delete_secret
            success = delete_secret(key, backend=self.secrets_backend)
        
        # Delete from configuration file
        if '.' in key:
            # Handle nested keys
            parts = key.split('.')
            current = self.config_data
            for part in parts[:-1]:
                if not isinstance(current, dict) or part not in current:
                    return False
                current = current[part]
            
            # Delete the final value
            if parts[-1] in current:
                del current[parts[-1]]
                return self._save_config() and success
            return success
        else:
            # Simple key
            if key in self.config_data:
                del self.config_data[key]
                return self._save_config() and success
        
        return success
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """
        List all configuration keys, optionally filtered by prefix.
        
        Args:
            prefix: Optional prefix to filter keys
            
        Returns:
            List of configuration keys
        """
        keys = []
        
        def collect_keys(data, path=""):
            if isinstance(data, dict):
                for k, v in data.items():
                    current_path = f"{path}.{k}" if path else k
                    if isinstance(v, dict):
                        collect_keys(v, current_path)
                    else:
                        keys.append(current_path)
        
        collect_keys(self.config_data)
        
        if prefix:
            return [k for k in keys if k.startswith(prefix)]
        return keys