"""
Base agent profile for the Agent Team module.

This module provides the base agent profile class that all agent profiles inherit from.
"""


import logging
import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert
from interfaces.agent_interfaces import IAgentProfile



(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# Set up logging
logger = logging.getLogger(__name__)


class AgentProfile(IAgentProfile):
    """
    Base agent profile class.

    This class provides the base functionality for all agent profiles.
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the agent profile.

        Args:
            name: Name of the agent profile
            description: Optional description of the agent profile
            capabilities: Optional list of capabilities
            parameters: Optional dictionary of parameters
        """
        self._name = name
        self._description = description or f"Agent profile for {name}"
        self._capabilities = capabilities or []
        self._parameters = parameters or {}

        logger.debug(f"Created agent profile: {name}")

    @property
    def name(self) -> str:
        """Get the profile name."""
        return self._name

    @property
    def description(self) -> str:
        """Get the profile description."""
        return self._description

    @property
    def capabilities(self) -> List[str]:
        """Get the profile capabilities."""
        return self._capabilities.copy()

    @property
    def parameters(self) -> Dict[str, Any]:
        """Get the profile parameters."""
        return self._parameters.copy()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the profile to a dictionary.

        Returns:
            Dictionary representation of the profile
        """
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "parameters": self.parameters,
        }

    def __str__(self) -> str:
        """Get a string representation of the profile."""
        return f"{self.name}: {self.description}"

    def __repr__(self) -> str:
        """Get a string representation of the profile for debugging."""
        return f"AgentProfile(name='{self.name}', capabilities={self.capabilities})"