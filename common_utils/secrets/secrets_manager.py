"""
Core Secrets Manager Implementation

This module provides the core functionality for secrets management, with support for multiple
backend storage options like environment variables, encrypted files, and external secret services.
"""

import os
import json
import base64
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Set up logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_ENV_PREFIX = "PAISSIVE_"
DEFAULT_SECRETS_FILE = os.path.expanduser("~/.paissive/secrets.enc")
DEFAULT_SALT_FILE = os.path.expanduser("~/.paissive/salt")

# Initialize storage for in-memory secrets cache
_secrets_cache: Dict[str, str] = {}


class SecretsBackend:
    """Enumeration of available secrets backends."""
    ENV_VAR = "env"
    FILE = "file"
    MEMORY = "memory"
    VAULT = "vault"


def _derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive an encryption key from a password and salt.
    
    Args:
        password: The password to derive the key from
        salt: The salt for key derivation
        
    Returns:
        The derived encryption key
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def _ensure_secrets_dir() -> None:
    """Ensure the secrets directory exists."""
    secrets_dir = os.path.dirname(DEFAULT_SECRETS_FILE)
    os.makedirs(secrets_dir, mode=0o700, exist_ok=True)


def _generate_or_get_salt() -> bytes:
    """
    Generate a new salt or get the existing one.
    
    Returns:
        The salt as bytes
    """
    _ensure_secrets_dir()
    
    if os.path.exists(DEFAULT_SALT_FILE):
        with open(DEFAULT_SALT_FILE, 'rb') as f:
            return f.read()
    else:
        # Generate a new salt
        salt = os.urandom(16)
        # Save it securely
        with open(DEFAULT_SALT_FILE, 'wb') as f:
            f.write(salt)
        os.chmod(DEFAULT_SALT_FILE, 0o600)
        return salt


def _get_encryption_key() -> Fernet:
    """
    Get the encryption key for file-based secrets.
    
    Returns:
        Fernet encryption key
    
    Raises:
        ValueError: If no master password is set
    """
    master_password = os.environ.get(f"{DEFAULT_ENV_PREFIX}MASTER_PASSWORD")
    if not master_password:
        raise ValueError(
            f"Master password not set. Please set {DEFAULT_ENV_PREFIX}MASTER_PASSWORD environment variable."
        )
    
    salt = _generate_or_get_salt()
    key = _derive_key(master_password, salt)
    return Fernet(key)


def _save_secrets_to_file(secrets_data: Dict[str, str]) -> None:
    """
    Save secrets to an encrypted file.
    
    Args:
        secrets_data: Dictionary of secrets to save
    """
    _ensure_secrets_dir()
    
    try:
        # Encrypt the secrets
        fernet = _get_encryption_key()
        encrypted_data = fernet.encrypt(json.dumps(secrets_data).encode())
        
        # Write to file with secure permissions
        with open(DEFAULT_SECRETS_FILE, 'wb') as f:
            f.write(encrypted_data)
        
        # Set secure permissions
        os.chmod(DEFAULT_SECRETS_FILE, 0o600)
        
        logger.info("Secrets saved to encrypted file")
    except Exception as e:
        logger.error(f"Error saving secrets to file: {str(e)}")
        raise


def _load_secrets_from_file() -> Dict[str, str]:
    """
    Load secrets from an encrypted file.
    
    Returns:
        Dictionary of secrets loaded from file
    """
    if not os.path.exists(DEFAULT_SECRETS_FILE):
        return {}
    
    try:
        # Read and decrypt the secrets
        with open(DEFAULT_SECRETS_FILE, 'rb') as f:
            encrypted_data = f.read()
        
        if not encrypted_data:
            return {}
        
        fernet = _get_encryption_key()
        decrypted_data = fernet.decrypt(encrypted_data).decode()
        
        return json.loads(decrypted_data)
    except Exception as e:
        logger.error(f"Error loading secrets from file: {str(e)}")
        return {}


def get_secret(name: str, default: Optional[str] = None, backend: str = SecretsBackend.ENV_VAR) -> Optional[str]:
    """
    Get a secret from the specified backend.
    
    Args:
        name: The name of the secret
        default: Default value if the secret is not found
        backend: The backend to retrieve the secret from (env, file, memory, vault)
        
    Returns:
        The secret value or the default
    """
    # Try to get secret from environment variables
    if backend == SecretsBackend.ENV_VAR:
        # Try with prefix first
        env_var_name = f"{DEFAULT_ENV_PREFIX}{name.upper()}"
        value = os.environ.get(env_var_name)
        
        # If not found, try the name as-is
        if value is None:
            value = os.environ.get(name.upper())
        
        if value is not None:
            return value
    
    # Try to get secret from in-memory cache
    if backend == SecretsBackend.MEMORY:
        if name in _secrets_cache:
            return _secrets_cache[name]
    
    # Try to get secret from encrypted file
    if backend == SecretsBackend.FILE:
        try:
            secrets_data = _load_secrets_from_file()
            if name in secrets_data:
                return secrets_data[name]
        except Exception as e:
            logger.error(f"Error reading from secrets file: {str(e)}")
    
    # Try to get secret from vault (placeholder for future implementation)
    if backend == SecretsBackend.VAULT:
        # Placeholder for Vault implementation
        logger.warning("Vault backend not yet implemented")
    
    # Return default if secret not found
    return default


def set_secret(name: str, value: str, backend: str = SecretsBackend.ENV_VAR) -> bool:
    """
    Set a secret in the specified backend.
    
    Args:
        name: The name of the secret
        value: The value of the secret
        backend: The backend to store the secret in (env, file, memory, vault)
        
    Returns:
        True if successful, False otherwise
    """
    if not name or not isinstance(name, str):
        raise ValueError("Secret name must be a non-empty string")
    
    if value is None:
        raise ValueError("Secret value cannot be None")
    
    # Set in environment variable
    if backend == SecretsBackend.ENV_VAR:
        env_var_name = f"{DEFAULT_ENV_PREFIX}{name.upper()}"
        os.environ[env_var_name] = str(value)
        logger.debug(f"Secret '{name}' set in environment variable")
        return True
    
    # Set in memory
    if backend == SecretsBackend.MEMORY:
        _secrets_cache[name] = str(value)
        logger.debug(f"Secret '{name}' set in memory")
        return True
    
    # Set in encrypted file
    if backend == SecretsBackend.FILE:
        try:
            # Load existing secrets
            secrets_data = _load_secrets_from_file()
            
            # Update with new secret
            secrets_data[name] = str(value)
            
            # Save back to encrypted file
            _save_secrets_to_file(secrets_data)
            
            logger.debug(f"Secret '{name}' set in encrypted file")
            return True
        except Exception as e:
            logger.error(f"Error setting secret in file: {str(e)}")
            return False
    
    # Set in vault (placeholder for future implementation)
    if backend == SecretsBackend.VAULT:
        # Placeholder for Vault implementation
        logger.warning("Vault backend not yet implemented")
        return False
    
    logger.error(f"Unsupported backend: {backend}")
    return False


def delete_secret(name: str, backend: str = SecretsBackend.ENV_VAR) -> bool:
    """
    Delete a secret from the specified backend.
    
    Args:
        name: The name of the secret
        backend: The backend to delete the secret from (env, file, memory, vault)
        
    Returns:
        True if successful, False otherwise
    """
    # Delete from environment variable
    if backend == SecretsBackend.ENV_VAR:
        env_var_name = f"{DEFAULT_ENV_PREFIX}{name.upper()}"
        if env_var_name in os.environ:
            del os.environ[env_var_name]
            logger.debug(f"Secret '{name}' deleted from environment variable")
            return True
        return False
    
    # Delete from memory
    if backend == SecretsBackend.MEMORY:
        if name in _secrets_cache:
            del _secrets_cache[name]
            logger.debug(f"Secret '{name}' deleted from memory")
            return True
        return False
    
    # Delete from encrypted file
    if backend == SecretsBackend.FILE:
        try:
            # Load existing secrets
            secrets_data = _load_secrets_from_file()
            
            # Remove the secret if it exists
            if name in secrets_data:
                del secrets_data[name]
                
                # Save back to encrypted file
                _save_secrets_to_file(secrets_data)
                
                logger.debug(f"Secret '{name}' deleted from encrypted file")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting secret from file: {str(e)}")
            return False
    
    # Delete from vault (placeholder for future implementation)
    if backend == SecretsBackend.VAULT:
        # Placeholder for Vault implementation
        logger.warning("Vault backend not yet implemented")
        return False
    
    logger.error(f"Unsupported backend: {backend}")
    return False


def list_secret_names(backend: str = SecretsBackend.ENV_VAR) -> List[str]:
    """
    List all secret names from the specified backend.
    
    Args:
        backend: The backend to list secrets from (env, file, memory, vault)
        
    Returns:
        List of secret names
    """
    result = []
    
    # List from environment variables
    if backend == SecretsBackend.ENV_VAR:
        prefix = DEFAULT_ENV_PREFIX
        for key in os.environ:
            if key.startswith(prefix):
                result.append(key[len(prefix):].lower())
    
    # List from memory
    elif backend == SecretsBackend.MEMORY:
        result = list(_secrets_cache.keys())
    
    # List from encrypted file
    elif backend == SecretsBackend.FILE:
        try:
            secrets_data = _load_secrets_from_file()
            result = list(secrets_data.keys())
        except Exception as e:
            logger.error(f"Error listing secrets from file: {str(e)}")
    
    # List from vault (placeholder for future implementation)
    elif backend == SecretsBackend.VAULT:
        # Placeholder for Vault implementation
        logger.warning("Vault backend not yet implemented")
    
    return result