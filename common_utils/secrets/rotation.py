"""
Secret Rotation Utilities

This module provides functionality for implementing secret rotation policies
and executing secret rotation operations.
"""

import os
import json
import time
import logging
import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from .secrets_manager import (
    get_secret,
    set_secret,
    delete_secret,
    list_secret_names,
    SecretsBackend
)

# Set up logging
logger = logging.getLogger(__name__)

# Default path for rotation metadata
DEFAULT_ROTATION_METADATA_FILE = os.path.expanduser('~/.paissive/rotation_metadata.json')


class RotationPolicy:
    """Defines a policy for secret rotation."""
    
    def __init__(self,
                interval_days: int = 90,
                warning_days: int = 7,
                description: str = "",
                rotation_func: Optional[Callable[[str, str, str], bool]] = None):
        """
        Initialize a rotation policy.
        
        Args:
            interval_days: Number of days between rotations
            warning_days: Days before expiry to generate warnings
            description: Description of this policy
            rotation_func: Custom function to perform rotation (if None, manual rotation is required)
        """
        self.interval_days = interval_days
        self.warning_days = warning_days
        self.description = description
        self.rotation_func = rotation_func


class SecretRotationManager:
    """
    Manager for secret rotation operations.
    
    This class manages the rotation policies and metadata for secrets, tracks
    rotation history, and facilitates the rotation process.
    """
    
    def __init__(self, 
                metadata_file: Optional[str] = None,
                backend: str = SecretsBackend.ENV_VAR):
        """
        Initialize the rotation manager.
        
        Args:
            metadata_file: Path to the rotation metadata file
            backend: The secret backend to use
        """
        self.metadata_file = metadata_file or DEFAULT_ROTATION_METADATA_FILE
        self.backend = backend
        self.metadata = {
            "secrets": {},
            "policies": {},
            "last_check": None
        }
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load rotation metadata from file if it exists."""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                logger.debug(f"Rotation metadata loaded from {self.metadata_file}")
        except Exception as e:
            logger.error(f"Error loading rotation metadata: {str(e)}")
    
    def _save_metadata(self) -> bool:
        """
        Save rotation metadata to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.metadata_file), mode=0o700, exist_ok=True)
            
            # Update last check timestamp
            self.metadata["last_check"] = datetime.datetime.now().isoformat()
            
            # Write to file
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
            
            # Set secure permissions
            os.chmod(self.metadata_file, 0o600)
            
            logger.debug(f"Rotation metadata saved to {self.metadata_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving rotation metadata: {str(e)}")
            return False
    
    def register_policy(self, name: str, policy: RotationPolicy) -> bool:
        """
        Register a named rotation policy.
        
        Args:
            name: Policy name
            policy: Rotation policy object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.metadata["policies"][name] = {
                "interval_days": policy.interval_days,
                "warning_days": policy.warning_days,
                "description": policy.description
            }
            return self._save_metadata()
        except Exception as e:
            logger.error(f"Error registering policy: {str(e)}")
            return False
    
    def set_secret_policy(self, secret_name: str, policy_name: str) -> bool:
        """
        Assign a rotation policy to a secret.
        
        Args:
            secret_name: The name of the secret
            policy_name: The name of the policy to apply
            
        Returns:
            True if successful, False otherwise
        """
        if policy_name not in self.metadata["policies"]:
            logger.error(f"Policy '{policy_name}' not found")
            return False
        
        # Get current timestamp
        now = datetime.datetime.now().isoformat()
        
        # Initialize or update secret metadata
        if secret_name not in self.metadata["secrets"]:
            self.metadata["secrets"][secret_name] = {
                "policy": policy_name,
                "created_at": now,
                "last_rotated": now,
                "rotation_history": []
            }
        else:
            self.metadata["secrets"][secret_name]["policy"] = policy_name
        
        return self._save_metadata()
    
    def get_secrets_requiring_rotation(self) -> List[Dict[str, Any]]:
        """
        Get a list of secrets that require rotation.
        
        Returns:
            List of dicts with secret details
        """
        result = []
        now = datetime.datetime.now()
        
        for secret_name, metadata in self.metadata["secrets"].items():
            policy_name = metadata.get("policy")
            if not policy_name or policy_name not in self.metadata["policies"]:
                continue
            
            policy = self.metadata["policies"][policy_name]
            
            # Calculate days since last rotation
            last_rotated = datetime.datetime.fromisoformat(metadata["last_rotated"])
            days_since_rotation = (now - last_rotated).days
            
            # Check if rotation is needed
            if days_since_rotation >= policy["interval_days"]:
                result.append({
                    "name": secret_name,
                    "policy": policy_name,
                    "last_rotated": metadata["last_rotated"],
                    "days_overdue": days_since_rotation - policy["interval_days"]
                })
            # Check if warning should be issued
            elif days_since_rotation >= (policy["interval_days"] - policy["warning_days"]):
                result.append({
                    "name": secret_name,
                    "policy": policy_name,
                    "last_rotated": metadata["last_rotated"],
                    "days_until_rotation": policy["interval_days"] - days_since_rotation,
                    "warning": True
                })
        
        return result
    
    def rotate_secret(self, 
                     secret_name: str, 
                     new_value: Optional[str] = None, 
                     rotation_reason: str = "scheduled") -> bool:
        """
        Rotate a secret.
        
        Args:
            secret_name: The name of the secret to rotate
            new_value: The new value for the secret (if None, will attempt to use policy's rotation function)
            rotation_reason: Reason for rotation
            
        Returns:
            True if successful, False otherwise
        """
        # Check if secret exists in our metadata
        if secret_name not in self.metadata["secrets"]:
            logger.error(f"Secret '{secret_name}' not registered for rotation management")
            return False
        
        metadata = self.metadata["secrets"][secret_name]
        policy_name = metadata.get("policy")
        
        # Get the current value
        current_value = get_secret(secret_name, backend=self.backend)
        if current_value is None:
            logger.error(f"Secret '{secret_name}' not found in backend")
            return False
        
        # Use policy's rotation function if available and no new value provided
        if new_value is None and policy_name in self.metadata["policies"]:
            policy = self.metadata["policies"][policy_name]
            # This would require custom rotation functions registered with the manager
            logger.info(f"No new value provided, manual rotation required for '{secret_name}'")
            return False
        
        if new_value is None:
            logger.error(f"New value required for secret '{secret_name}'")
            return False
        
        # Attempt to set the new value
        if not set_secret(secret_name, new_value, backend=self.backend):
            logger.error(f"Failed to set new value for secret '{secret_name}'")
            return False
        
        # Update rotation metadata
        now = datetime.datetime.now().isoformat()
        
        # Record rotation in history
        if "rotation_history" not in metadata:
            metadata["rotation_history"] = []
        
        metadata["rotation_history"].append({
            "timestamp": now,
            "reason": rotation_reason
        })
        
        # Update last_rotated
        metadata["last_rotated"] = now
        
        # Save metadata
        return self._save_metadata()
    
    def get_rotation_status(self, secret_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the rotation status of one or all secrets.
        
        Args:
            secret_name: Optional specific secret name
            
        Returns:
            Dict with rotation status information
        """
        now = datetime.datetime.now()
        
        if secret_name:
            if secret_name not in self.metadata["secrets"]:
                return {"error": f"Secret '{secret_name}' not found"}
            
            metadata = self.metadata["secrets"][secret_name]
            policy_name = metadata.get("policy")
            
            if not policy_name or policy_name not in self.metadata["policies"]:
                return {
                    "name": secret_name,
                    "error": "No valid policy assigned"
                }
            
            policy = self.metadata["policies"][policy_name]
            last_rotated = datetime.datetime.fromisoformat(metadata["last_rotated"])
            days_since_rotation = (now - last_rotated).days
            
            return {
                "name": secret_name,
                "policy": policy_name,
                "last_rotated": metadata["last_rotated"],
                "days_since_rotation": days_since_rotation,
                "interval_days": policy["interval_days"],
                "days_until_rotation": max(0, policy["interval_days"] - days_since_rotation),
                "needs_rotation": days_since_rotation >= policy["interval_days"],
                "warning": days_since_rotation >= (policy["interval_days"] - policy["warning_days"]),
                "rotation_history": metadata.get("rotation_history", [])
            }
        else:
            # Return status for all secrets
            result = {}
            for s_name in self.metadata["secrets"]:
                result[s_name] = self.get_rotation_status(s_name)
            return result


# Common policies
DEFAULT_POLICIES = {
    "high_security": RotationPolicy(
        interval_days=30,
        warning_days=7,
        description="High security policy for critical secrets (30 days)"
    ),
    "standard": RotationPolicy(
        interval_days=90,
        warning_days=14,
        description="Standard policy for most secrets (90 days)"
    ),
    "low_risk": RotationPolicy(
        interval_days=180,
        warning_days=30,
        description="Low risk policy for non-critical secrets (180 days)"
    )
}


def initialize_rotation_manager(backend: str = SecretsBackend.ENV_VAR) -> SecretRotationManager:
    """
    Initialize the rotation manager with default policies.
    
    Args:
        backend: The secret backend to use
        
    Returns:
        Configured SecretRotationManager
    """
    manager = SecretRotationManager(backend=backend)
    
    # Register default policies if they don't exist
    for name, policy in DEFAULT_POLICIES.items():
        if name not in manager.metadata.get("policies", {}):
            manager.register_policy(name, policy)
    
    return manager