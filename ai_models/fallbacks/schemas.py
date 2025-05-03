"""
Schema definitions for model fallback configurations.

This module provides Pydantic models for validating and serializing / deserializing
fallback configurations with security features.
"""

import re
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
            "researcher": ["huggingface", "llama", "general - purpose"],
            "developer": ["huggingface", "llama", "general - purpose"],
            "monetization": ["huggingface", "general - purpose"],
            "marketing": ["huggingface", "general - purpose"],
            "default": ["huggingface", "general - purpose"],
        },
        description="Mapping of agent types to their preferred model types for fallbacks",
    )

    model_config = ConfigDict(
        str_max_length=1024,  # Security: limit string lengths
        str_strip_whitespace=True,  # Security: strip whitespace
    )

    @field_validator("preferred_model_types")
    @classmethod
    def validate_model_types(cls, v: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Validate model type preferences."""
        allowed_types = {"huggingface", "llama", "openai", "general - purpose"}
        agent_pattern = re.compile(r"^[a - zA - Z0 - 9_\-]+$")

        validated = {}
        for agent_type, model_types in v.items():
            # Validate agent type name
            if not agent_pattern.match(agent_type):
                raise ValueError(f"Invalid agent type format: {agent_type}")

            # Validate and filter model types
            safe_types = [
                mt for mt in model_types if isinstance(mt, str) and mt.lower() in allowed_types
            ]
            if safe_types:
                validated[agent_type] = safe_types

        return validated

    def get_preferences_for_agent(self, agent_type: str) -> List[str]:
        """Get fallback preferences for a specific agent type."""
        if not re.match(r"^[a - zA - Z0 - 9_\-]+$", agent_type):
            raise ValueError("Invalid agent type format")

        return self.preferred_model_types.get(
            agent_type, self.preferred_model_types.get("default", [])
        )


class FallbackConfig(BaseModel):
    """Configuration model for fallback behavior with security features."""

    enabled: bool = Field(default=True, description="Whether fallback mechanisms are enabled")

    default_strategy: FallbackStrategyEnum = Field(
        default=FallbackStrategyEnum.DEFAULT,
        description="Default fallback strategy to use",
    )

    max_attempts: int = Field(
        default=3,
        description="Maximum number of fallback attempts",
        ge=1,  # Must be positive
        le=10,  # Security: limit maximum attempts
    )

    default_model_id: Optional[str] = Field(
        default=None, description="ID of the default fallback model"
    )

    preferences: FallbackPreferences = Field(
        default_factory=FallbackPreferences,
        description="Fallback preferences configuration",
    )

    logging_level: str = Field(
        default="INFO",
        description="Logging level for fallback events",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",  # Security: validate log levels
    )

    use_general_purpose_fallback: bool = Field(
        default=True,
        description="Whether to use any general purpose model as a last resort",
    )

    secure_mode: bool = Field(
        default=True,
        description="Enable additional security checks",
    )

    allowed_model_types: List[str] = Field(
        default=["huggingface", "llama", "openai", "general - purpose"],
        description="List of allowed model types",
    )

    model_config = ConfigDict(
        str_max_length=1024,  # Security: limit string lengths
        str_strip_whitespace=True,  # Security: strip whitespace
        json_schema_extra={
            "example": {
                "enabled": True,
                "default_strategy": "default",
                "max_attempts": 3,
                "default_model_id": "a1b2c3d4e5f6",
                "preferences": {
                    "preferred_model_types": {
                        "researcher": ["huggingface", "llama", "general - purpose"],
                        "developer": ["huggingface", "llama", "general - purpose"],
                        "default": ["huggingface", "general - purpose"],
                    }
                },
                "logging_level": "INFO",
                "use_general_purpose_fallback": True,
                "secure_mode": True,
            }
        },
    )

    @field_validator("default_model_id")
    @classmethod
    def validate_model_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate model ID format."""
        if v is not None and not re.match(r"^[a - zA - Z0 - 9][a - zA - Z0 - 9_\-\.]+$", v):
            raise ValueError("Invalid model ID format")
        return v

    @field_validator("allowed_model_types")
    @classmethod
    def validate_allowed_types(cls, v: List[str]) -> List[str]:
        """Validate allowed model types."""
        allowed_types = {"huggingface", "llama", "openai", "general - purpose"}
        validated = [mt for mt in v if isinstance(mt, str) and mt.lower() in allowed_types]
        if not validated:
            raise ValueError("Must specify at least one valid model type")
        return validated


class FallbackEventSchema(BaseModel):
    """Schema for a model fallback event with security validations."""

    original_model_id: Optional[str] = Field(
        default=None,
        description="ID of the original model that failed",
        pattern=r"^[a - zA - Z0 - 9][a - zA - Z0 - 9_\-\.]+$",  # Security: validate model ID format
    )

    fallback_model_id: str = Field(
        description="ID of the fallback model that was selected",
        pattern=r"^[a - zA - Z0 - 9][a - zA - Z0 - 9_\-\.]+$",  # Security: validate model ID format
    )

    reason: str = Field(
        description="Reason for the fallback", max_length=1000  # Security: limit reason length
    )

    agent_type: Optional[str] = Field(
        default=None,
        description="Type of agent using the model",
        pattern=r"^[a - zA - Z0 - 9_\-]+$",  # Security: validate agent type format
    )

    task_type: Optional[str] = Field(
        default=None,
        description="Type of task being performed",
        pattern=r"^[a - zA - Z0 - 9_\-]+$",  # Security: validate task type format
    )

    strategy_used: FallbackStrategyEnum = Field(
        default=FallbackStrategyEnum.DEFAULT,
        description="The fallback strategy that was used",
    )

    timestamp: float = Field(
        description="Timestamp of the fallback event", ge=0  # Security: ensure positive timestamp
    )

    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional details about the fallback"
    )

    model_config = ConfigDict(
        str_max_length=1024,  # Security: limit string lengths
        str_strip_whitespace=True,  # Security: strip whitespace
    )

    @field_validator("details")
    @classmethod
    def validate_details(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize details dictionary."""
        sanitized = {}
        for key, value in v.items():
            # Only allow alphanumeric keys with underscores
            if not re.match(r"^[a - zA - Z0 - 9_]+$", key):
                continue
            # Convert values to strings and limit length
            sanitized[key] = str(value)[:500]
        return sanitized


class FallbackMetrics(BaseModel):
    """Schema for fallback metrics with validation."""

    success_count: int = Field(
        default=0,
        description="Number of successful fallbacks with this strategy",
        ge=0,  # Security: ensure non - negative count
    )

    total_count: int = Field(
        default=0,
        description="Total number of times this strategy was used",
        ge=0,  # Security: ensure non - negative count
    )

    success_rate: float = Field(
        default=0.0,
        description="Success rate of this strategy (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )

    model_config = ConfigDict(
        validate_assignment=True,  # Validate on assignment
        str_max_length=1024,  # Security: limit string lengths
        str_strip_whitespace=True,  # Security: strip whitespace
    )
