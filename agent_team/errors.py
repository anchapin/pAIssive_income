"""
Error handling for the Agent Team module.

This module provides custom exceptions and error handling utilities
specific to the Agent Team module.
"""

import logging
import os
import sys
from typing import Optional

from errors import (AgentError, AgentTeamError, ValidationError,
handle_exception)

# Add the project root to the Python path to import the errors module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Set up logging
logger = logging.getLogger(__name__)

# Re-export the error classes for convenience
__all__ = [
"AgentTeamError",
"AgentError",
"ValidationError",
"handle_exception",
"AgentInitializationError",
"AgentCommunicationError",
"WorkflowError",
"ResearchAgentError",
"DeveloperAgentError",
"MonetizationAgentError",
"MarketingAgentError",
"FeedbackAgentError",
]


class AgentInitializationError(AgentError):
    """Error raised when an agent fails to initialize."""


    def __init__(self, message: str, agent_name: Optional[str] = None, **kwargs):
    """
    Initialize the agent initialization error.

    Args:
    message: Human-readable error message
    agent_name: Name of the agent that failed to initialize
    **kwargs: Additional arguments to pass to the base class
    """
    super().__init__(
    message=message,
    agent_name=agent_name,
    code="agent_initialization_error",
    **kwargs
    )


    class AgentCommunicationError(AgentError):
    """Error raised when communication between agents fails."""


    def __init__(
    self,
    message: str,
    source_agent: Optional[str] = None,
    target_agent: Optional[str] = None,
    **kwargs
    ):
    """
    Initialize the agent communication error.

    Args:
    message: Human-readable error message
    source_agent: Name of the source agent
    target_agent: Name of the target agent
    **kwargs: Additional arguments to pass to the base class
    """
    details = kwargs.pop("details", {})
    if source_agent:
    details["source_agent"] = source_agent
    if target_agent:
    details["target_agent"] = target_agent


    super().__init__(
    message=message,
    agent_name=source_agent,
    code="agent_communication_error",
    details=details,
    **kwargs
    )


    class WorkflowError(AgentTeamError):
    """Error raised when a workflow operation fails."""


    def __init__(self, message: str, workflow_step: Optional[str] = None, **kwargs):
    """
    Initialize the workflow error.

    Args:
    message: Human-readable error message
    workflow_step: Name of the workflow step that failed
    **kwargs: Additional arguments to pass to the base class
    """
    details = kwargs.pop("details", {})
    if workflow_step:
    details["workflow_step"] = workflow_step


    super().__init__(message=message, code="workflow_error", details=details, **kwargs)


    class ResearchAgentError(AgentError):
    """Error raised when the Research Agent encounters an issue."""


    def __init__(self, message: str, **kwargs):
    """
    Initialize the Research Agent error.

    Args:
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    """
    super().__init__(
    message=message,
    agent_name="Research Agent",
    code="research_agent_error",
    **kwargs
    )


    class DeveloperAgentError(AgentError):
    """Error raised when the Developer Agent encounters an issue."""


    def __init__(self, message: str, **kwargs):
    """
    Initialize the Developer Agent error.

    Args:
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    """
    super().__init__(
    message=message,
    agent_name="Developer Agent",
    code="developer_agent_error",
    **kwargs
    )


    class MonetizationAgentError(AgentError):
    """Error raised when the Monetization Agent encounters an issue."""


    def __init__(self, message: str, **kwargs):
    """
    Initialize the Monetization Agent error.

    Args:
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    """
    super().__init__(
    message=message,
    agent_name="Monetization Agent",
    code="monetization_agent_error",
    **kwargs
    )


    class MarketingAgentError(AgentError):
    """Error raised when the Marketing Agent encounters an issue."""


    def __init__(self, message: str, **kwargs):
    """
    Initialize the Marketing Agent error.

    Args:
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    """
    super().__init__(
    message=message,
    agent_name="Marketing Agent",
    code="marketing_agent_error",
    **kwargs
    )


    class FeedbackAgentError(AgentError):
    """Error raised when the Feedback Agent encounters an issue."""


    def __init__(self, message: str, **kwargs):
    """
    Initialize the Feedback Agent error.

    Args:
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    """
    super().__init__(
    message=message,
    agent_name="Feedback Agent",
    code="feedback_agent_error",
    **kwargs
    )
