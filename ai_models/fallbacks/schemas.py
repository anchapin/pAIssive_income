"""
Schema definitions for model fallback configurations.

This module provides Pydantic models for validating and serializing/deserializing
fallback configurations.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FallbackStrategyEnum(str, Enum):
    """Enumeration of fallback strategy types for Pydantic models."""

    NONE = "none"  # No fallback, just fail
    DEFAULT = "default"  # Use a default model
    SIMILAR_MODEL = "similar_model"  # Use a model with similar capabilities
    MODEL_TYPE = "model_type"  # Try other models of the same type
    ANY_AVAILABLE = "any_available"  # Use any available model
    SPECIFIED_LIST = "specified_list"  # Try models in a specified order
    SIZE_TIER = "size_tier"  # Try models of different size tiers
    CAPABILITY_BASED = "capability"  # Try models with required capabilities


class FallbackPreferences(BaseModel):
    """Model for fallback preferences configuration."""

    preferred_model_types: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "researcher": ["huggingface", "llama", "general-purpose"],
            "developer": ["huggingface", "llama", "general-purpose"],
            "monetization": ["huggingface", "general-purpose"],
            "marketing": ["huggingface", "general-purpose"],
            "default": ["huggingface", "general-purpose"],
        },
        description="Mapping of agent types to their preferred model types for fallbacks",
    )

    def get_preferences_for_agent(self, agent_type: str) -> List[str]:
        """Get fallback preferences for a specific agent type."""
        return self.preferred_model_types.get(
            agent_type, self.preferred_model_types.get("default", [])
        )


class FallbackConfig(BaseModel):
    """Configuration model for fallback behavior."""

    enabled: bool = Field(default=True, description="Whether fallback mechanisms are enabled")

    default_strategy: FallbackStrategyEnum = Field(
        default=FallbackStrategyEnum.DEFAULT,
        description="Default fallback strategy to use",
    )

    max_attempts: int = Field(
        default=3, description="Maximum number of fallback attempts", ge=1, le=10
    )

    default_model_id: Optional[str] = Field(
        default=None, description="ID of the default fallback model"
    )

    preferences: FallbackPreferences = Field(
        default_factory=FallbackPreferences,
        description="Fallback preferences configuration",
    )

    logging_level: str = Field(default="INFO", description="Logging level for fallback events")

    use_general_purpose_fallback: bool = Field(
        default=True,
        description="Whether to use any general purpose model as a last resort",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "enabled": True,
                "default_strategy": "default",
                "max_attempts": 3,
                "default_model_id": "a1b2c3d4e5f6",
                "preferences": {
                    "preferred_model_types": {
                        "researcher": ["huggingface", "llama", "general-purpose"],
                        "developer": ["huggingface", "llama", "general-purpose"],
                        "default": ["huggingface", "general-purpose"],
                    }
                },
                "logging_level": "INFO",
                "use_general_purpose_fallback": True,
            }
        }
    }


class FallbackEventSchema(BaseModel):
    """Schema for a model fallback event."""

    original_model_id: Optional[str] = Field(
        default=None, description="ID of the original model that failed"
    )

    fallback_model_id: str = Field(description="ID of the fallback model that was selected")

    reason: str = Field(description="Reason for the fallback")

    agent_type: Optional[str] = Field(default=None, description="Type of agent using the model")

    task_type: Optional[str] = Field(default=None, description="Type of task being performed")

    strategy_used: FallbackStrategyEnum = Field(
        default=FallbackStrategyEnum.DEFAULT,
        description="The fallback strategy that was used",
    )

    timestamp: float = Field(description="Timestamp of the fallback event")

    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional details about the fallback"
    )


class FallbackMetrics(BaseModel):
    """Schema for fallback metrics."""

    success_count: int = Field(
        default=0, description="Number of successful fallbacks with this strategy"
    )

    total_count: int = Field(default=0, description="Total number of times this strategy was used")

    success_rate: float = Field(
        default=0.0,
        description="Success rate of this strategy (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
