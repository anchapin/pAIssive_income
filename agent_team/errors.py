"""
"""
Error handling for the Agent Team module.
Error handling for the Agent Team module.


This module provides custom exceptions and error handling utilities
This module provides custom exceptions and error handling utilities
specific to the Agent Team module.
specific to the Agent Team module.
"""
"""


import logging
import logging
import os
import os
import sys
import sys
from typing import Optional
from typing import Optional


from errors import (AgentError, AgentTeamError, ValidationError,
from errors import (AgentError, AgentTeamError, ValidationError,
handle_exception)
handle_exception)


# Add the project root to the Python path to import the errors module
# Add the project root to the Python path to import the errors module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Re-export the error classes for convenience
# Re-export the error classes for convenience
__all__ = [
__all__ = [
"AgentTeamError",
"AgentTeamError",
"AgentError",
"AgentError",
"ValidationError",
"ValidationError",
"handle_exception",
"handle_exception",
"AgentInitializationError",
"AgentInitializationError",
"AgentCommunicationError",
"AgentCommunicationError",
"WorkflowError",
"WorkflowError",
"ResearchAgentError",
"ResearchAgentError",
"DeveloperAgentError",
"DeveloperAgentError",
"MonetizationAgentError",
"MonetizationAgentError",
"MarketingAgentError",
"MarketingAgentError",
"FeedbackAgentError",
"FeedbackAgentError",
]
]




class AgentInitializationError(AgentError):
    class AgentInitializationError(AgentError):
    """Error raised when an agent fails to initialize."""


    def __init__(self, message: str, agent_name: Optional[str] = None, **kwargs):
    """
    """
    Initialize the agent initialization error.
    Initialize the agent initialization error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    agent_name: Name of the agent that failed to initialize
    agent_name: Name of the agent that failed to initialize
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    super().__init__(
    super().__init__(
    message=message,
    message=message,
    agent_name=agent_name,
    agent_name=agent_name,
    code="agent_initialization_error",
    code="agent_initialization_error",
    **kwargs
    **kwargs
    )
    )




    class AgentCommunicationError(AgentError):
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
    """
    Initialize the agent communication error.
    Initialize the agent communication error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    source_agent: Name of the source agent
    source_agent: Name of the source agent
    target_agent: Name of the target agent
    target_agent: Name of the target agent
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if source_agent:
    if source_agent:
    details["source_agent"] = source_agent
    details["source_agent"] = source_agent
    if target_agent:
    if target_agent:
    details["target_agent"] = target_agent
    details["target_agent"] = target_agent




    super().__init__(
    super().__init__(
    message=message,
    message=message,
    agent_name=source_agent,
    agent_name=source_agent,
    code="agent_communication_error",
    code="agent_communication_error",
    details=details,
    details=details,
    **kwargs
    **kwargs
    )
    )




    class WorkflowError(AgentTeamError):
    class WorkflowError(AgentTeamError):
    """Error raised when a workflow operation fails."""


    def __init__(self, message: str, workflow_step: Optional[str] = None, **kwargs):
    """
    """
    Initialize the workflow error.
    Initialize the workflow error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    workflow_step: Name of the workflow step that failed
    workflow_step: Name of the workflow step that failed
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    details = kwargs.pop("details", {})
    details = kwargs.pop("details", {})
    if workflow_step:
    if workflow_step:
    details["workflow_step"] = workflow_step
    details["workflow_step"] = workflow_step




    super().__init__(message=message, code="workflow_error", details=details, **kwargs)
    super().__init__(message=message, code="workflow_error", details=details, **kwargs)




    class ResearchAgentError(AgentError):
    class ResearchAgentError(AgentError):
    """Error raised when the Research Agent encounters an issue."""


    def __init__(self, message: str, **kwargs):
    """
    """
    Initialize the Research Agent error.
    Initialize the Research Agent error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    super().__init__(
    super().__init__(
    message=message,
    message=message,
    agent_name="Research Agent",
    agent_name="Research Agent",
    code="research_agent_error",
    code="research_agent_error",
    **kwargs
    **kwargs
    )
    )




    class DeveloperAgentError(AgentError):
    class DeveloperAgentError(AgentError):
    """Error raised when the Developer Agent encounters an issue."""


    def __init__(self, message: str, **kwargs):
    """
    """
    Initialize the Developer Agent error.
    Initialize the Developer Agent error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    super().__init__(
    super().__init__(
    message=message,
    message=message,
    agent_name="Developer Agent",
    agent_name="Developer Agent",
    code="developer_agent_error",
    code="developer_agent_error",
    **kwargs
    **kwargs
    )
    )




    class MonetizationAgentError(AgentError):
    class MonetizationAgentError(AgentError):
    """Error raised when the Monetization Agent encounters an issue."""


    def __init__(self, message: str, **kwargs):
    """
    """
    Initialize the Monetization Agent error.
    Initialize the Monetization Agent error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    super().__init__(
    super().__init__(
    message=message,
    message=message,
    agent_name="Monetization Agent",
    agent_name="Monetization Agent",
    code="monetization_agent_error",
    code="monetization_agent_error",
    **kwargs
    **kwargs
    )
    )




    class MarketingAgentError(AgentError):
    class MarketingAgentError(AgentError):
    """Error raised when the Marketing Agent encounters an issue."""


    def __init__(self, message: str, **kwargs):
    """
    """
    Initialize the Marketing Agent error.
    Initialize the Marketing Agent error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    super().__init__(
    super().__init__(
    message=message,
    message=message,
    agent_name="Marketing Agent",
    agent_name="Marketing Agent",
    code="marketing_agent_error",
    code="marketing_agent_error",
    **kwargs
    **kwargs
    )
    )




    class FeedbackAgentError(AgentError):
    class FeedbackAgentError(AgentError):
    """Error raised when the Feedback Agent encounters an issue."""


    def __init__(self, message: str, **kwargs):
    """
    """
    Initialize the Feedback Agent error.
    Initialize the Feedback Agent error.


    Args:
    Args:
    message: Human-readable error message
    message: Human-readable error message
    **kwargs: Additional arguments to pass to the base class
    **kwargs: Additional arguments to pass to the base class
    """
    """
    super().__init__(
    super().__init__(
    message=message,
    message=message,
    agent_name="Feedback Agent",
    agent_name="Feedback Agent",
    code="feedback_agent_error",
    code="feedback_agent_error",
    **kwargs
    **kwargs
    )
    )

