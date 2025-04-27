"""
Base service for the pAIssive Income UI.

This module provides a base class for services that interact with the pAIssive Income framework.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional

from ..errors import (
    ServiceError, DataError, ValidationError, handle_exception
)

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

        Raises:
            DataError: If there's an issue loading the data
        """
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    try:
                        data = json.load(f)
                        logger.debug(f"Successfully loaded data from {filepath}")
                        return data
                    except json.JSONDecodeError as e:
                        raise DataError(
                            message=f"Invalid JSON format in file {filename}: {e}",
                            data_type="json",
                            operation="load",
                            original_exception=e
                        )
            except (IOError, OSError) as e:
                error = DataError(
                    message=f"Failed to read file {filename}: {e}",
                    data_type="file",
                    operation="read",
                    original_exception=e
                )
                error.log()
                raise error
        return None

    def _save_data(self, data: Any, filename: str) -> bool:
        """
        Save data to a JSON file.

        Args:
            data: Data to save
            filename: Name of the file to save to

        Returns:
            True if successful, False otherwise

        Raises:
            DataError: If there's an issue saving the data
        """
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w') as f:
                try:
                    json.dump(data, f, indent=2)
                    logger.debug(f"Successfully saved data to {filepath}")
                    return True
                except (TypeError, ValueError) as e:
                    raise DataError(
                        message=f"Failed to serialize data to JSON for file {filename}: {e}",
                        data_type="json",
                        operation="serialize",
                        original_exception=e
                    )
        except (IOError, OSError) as e:
            error = DataError(
                message=f"Failed to write to file {filename}: {e}",
                data_type="file",
                operation="write",
                original_exception=e
            )
            error.log()
            raise error
