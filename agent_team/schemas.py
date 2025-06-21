"""
Central schemas for agent_team package.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class AgentProfileSchema(BaseModel):
    """Schema representing an agent's profile."""
    role: str = Field(..., description="The role name for this agent (e.g., 'developer').")
    goal: str = Field(..., description="The primary goal assigned to this agent.")
    backstory: str = Field(..., description="Background or context for the agent's persona.")

class TaskSchema(BaseModel):
    """Schema for a unit of work in the agent team."""
    description: str = Field(..., description="Description of the task.")
    agent_role: str = Field(..., description="Role of agent expected to handle this task.")

class TeamConfigSchema(BaseModel):
    """Configuration schema for an agent team."""
    model: Optional[Dict[str, Any]] = Field(default=None, description="Model config dictionary.")
    workflow: Optional[Dict[str, Any]] = Field(default=None, description="Workflow config dictionary.")