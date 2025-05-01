"""
Base service for the pAIssive Income UI.

This module provides a base class for services that interact with the pAIssive Income framework.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from common_utils import (
    create_directory,
    file_exists,
    get_file_path,
    load_from_json_file,
    save_to_json_file,
)
from interfaces.ui_interfaces import IBaseService

from ..errors import DataError, ServiceError, ValidationError, handle_exception

# Set up logging
logger = logging.getLogger(__name__)


class BaseService(IBaseService):
    """
    Base class for services that interact with the pAIssive Income framework.
    """

    def __init__(self):
        """Initialize the base service."""
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        create_directory(self.data_dir)

    def load_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load data from a JSON file.

        Args:
            filename: Name of the file to load

        Returns:
            Data from the file, or None if the file doesn't exist

        Raises:
            DataError: If there's an issue loading the data
        """
        filepath = get_file_path(self.data_dir, filename)
        if file_exists(filepath):
            try:
                data = load_from_json_file(filepath)
                logger.debug(f"Successfully loaded data from {filepath}")
                return data
            except Exception as e:
                error = DataError(
                    message=f"Failed to load data from file {filename}: {e}",
                    data_type="json",
                    operation="load",
                    original_exception=e,
                )
                error.log()
                raise error
        return None

    def save_data(self, filename: str, data: Dict[str, Any]) -> bool:
        """
        Save data to a JSON file.

        Args:
            filename: Name of the file to save
            data: Data to save

        Returns:
            True if successful, False otherwise

        Raises:
            DataError: If there's an issue saving the data
        """
        filepath = get_file_path(self.data_dir, filename)
        try:
            save_to_json_file(data, filepath)
            logger.debug(f"Successfully saved data to {filepath}")
            return True
        except Exception as e:
            error = DataError(
                message=f"Failed to save data to file {filename}: {e}",
                data_type="json",
                operation="save",
                original_exception=e,
            )
            error.log()
            raise error
