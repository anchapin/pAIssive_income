"""
Base service for the pAIssive Income UI.

This module provides a base class for services that interact with the pAIssive Income framework.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

class BaseService:
    """
    Base class for services that interact with the pAIssive Income framework.
    """
    
    def __init__(self):
        """Initialize the base service."""
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_data(self, filename: str) -> Any:
        """
        Load data from a JSON file.
        
        Args:
            filename: Name of the file to load
            
        Returns:
            Data from the file, or None if the file doesn't exist
        """
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading data from {filepath}: {e}")
                return None
        return None
    
    def _save_data(self, data: Any, filename: str) -> bool:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            filename: Name of the file to save to
            
        Returns:
            True if successful, False otherwise
        """
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving data to {filepath}: {e}")
            return False
