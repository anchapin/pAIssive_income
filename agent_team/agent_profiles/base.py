"""
"""
Base agent profile for the Agent Team module.
Base agent profile for the Agent Team module.


This module provides the base agent profile class that all agent profiles inherit from.
This module provides the base agent profile class that all agent profiles inherit from.
"""
"""


import logging
import logging
import os
import os
import sys
import sys
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from interfaces.agent_interfaces import IAgentProfile
from interfaces.agent_interfaces import IAgentProfile


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class AgentProfile(IAgentProfile):
    class AgentProfile(IAgentProfile):
    """
    """
    Base agent profile class.
    Base agent profile class.


    This class provides the base functionality for all agent profiles.
    This class provides the base functionality for all agent profiles.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    name: str,
    name: str,
    description: Optional[str] = None,
    description: Optional[str] = None,
    capabilities: Optional[List[str]] = None,
    capabilities: Optional[List[str]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    ):
    ):
    """
    """
    Initialize the agent profile.
    Initialize the agent profile.


    Args:
    Args:
    name: Name of the agent profile
    name: Name of the agent profile
    description: Optional description of the agent profile
    description: Optional description of the agent profile
    capabilities: Optional list of capabilities
    capabilities: Optional list of capabilities
    parameters: Optional dictionary of parameters
    parameters: Optional dictionary of parameters
    """
    """
    self._name = name
    self._name = name
    self._description = description or f"Agent profile for {name}"
    self._description = description or f"Agent profile for {name}"
    self._capabilities = capabilities or []
    self._capabilities = capabilities or []
    self._parameters = parameters or {}
    self._parameters = parameters or {}


    logger.debug(f"Created agent profile: {name}")
    logger.debug(f"Created agent profile: {name}")


    @property
    @property
    def name(self) -> str:
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
    """
    Convert the profile to a dictionary.
    Convert the profile to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the profile
    Dictionary representation of the profile
    """
    """
    return {
    return {
    "name": self.name,
    "name": self.name,
    "description": self.description,
    "description": self.description,
    "capabilities": self.capabilities,
    "capabilities": self.capabilities,
    "parameters": self.parameters,
    "parameters": self.parameters,
    }
    }


    def __str__(self) -> str:
    def __str__(self) -> str:
    """Get a string representation of the profile."""
    return f"{self.name}: {self.description}"

    def __repr__(self) -> str:
    """Get a string representation of the profile for debugging."""
    return f"AgentProfile(name='{self.name}', capabilities={self.capabilities})"
