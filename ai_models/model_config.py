"""
Model configuration for the AI Models module.

This module provides classes and functions for configuring AI models,
including settings for model paths, cache, and performance options.
"""

import json
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from interfaces.model_interfaces import IModelConfig


@dataclass
class ModelConfig(IModelConfig):
    """
    Configuration for AI models with secure defaults.
    """

    # Base directories - using restricted permissions by default
    _models_dir: str = field(
        default_factory=lambda: os.path.join(os.path.expanduser("~"), ".pAIssive_income", 
            "models")
    )
    _cache_dir: str = field(
        default_factory=lambda: os.path.join(os.path.expanduser("~"), ".pAIssive_income", 
            "cache")
    )

    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 86400  # 24 hours in seconds
    max_cache_size: int = 1000  # Maximum number of items in memory cache

    # Performance settings
    default_device: str = "auto"  # "auto", "cpu", "cuda", "mps", etc.
    _max_threads: Optional[int] = None  # None means use all available threads

    # Model discovery
    _auto_discover: bool = True
    model_sources: List[str] = field(default_factory=lambda: ["local", "huggingface"])

    # Default models
    default_text_model: str = "gpt2"
    default_embedding_model: str = "all - MiniLM - L6 - v2"

    def __post_init__(self):
        """Create necessary directories with secure permissions after initialization."""
        # Create directories with restricted permissions (0o750)
        os.makedirs(self.models_dir, mode=0o750, exist_ok=True)
        os.makedirs(self.cache_dir, mode=0o750, exist_ok=True)

    @property
    def models_dir(self) -> str:
        """Get the models directory path."""
        return self._models_dir

    @models_dir.setter
    def models_dir(self, value: str) -> None:
        """Set the models directory path with secure permissions."""
        if value:
            # Ensure absolute path
            value = os.path.abspath(value)
            # Create directory with secure permissions if it doesn't exist
            os.makedirs(value, mode=0o750, exist_ok=True)
            self._models_dir = value

    @property
    def cache_dir(self) -> str:
        """Get the cache directory path."""
        return self._cache_dir

    @cache_dir.setter
    def cache_dir(self, value: str) -> None:
        """Set the cache directory path with secure permissions."""
        if value:
            # Ensure absolute path
            value = os.path.abspath(value)
            # Create directory with secure permissions if it doesn't exist
            os.makedirs(value, mode=0o750, exist_ok=True)
            self._cache_dir = value

    @property
    def max_threads(self) -> Optional[int]:
        """Get the maximum number of threads to use."""
        return self._max_threads

    @max_threads.setter
    def max_threads(self, value: Optional[int]) -> None:
        """Set the maximum number of threads to use."""
        if value is not None and value <= 0:
            raise ValueError("max_threads must be positive or None")
        self._max_threads = value

    @property
    def auto_discover(self) -> bool:
        """Get whether to auto - discover models."""
        return self._auto_discover

    @auto_discover.setter
    def auto_discover(self, value: bool) -> None:
        """Set whether to auto - discover models."""
        self._auto_discover = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "models_dir": self.models_dir,
            "cache_dir": self.cache_dir,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "max_cache_size": self.max_cache_size,
            "default_device": self.default_device,
            "max_threads": self.max_threads,
            "auto_discover": self.auto_discover,
            "model_sources": self.model_sources,
            "default_text_model": self.default_text_model,
            "default_embedding_model": self.default_embedding_model,
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the configuration to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the configuration
        """
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, config_path: str) -> None:
        """
        Save the configuration to a JSON file securely.

        Args:
            config_path: Path to save the configuration
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config_path), mode=0o750, exist_ok=True)

            # Write config with secure permissions
            with open(config_path, "w", encoding="utf - 8") as f:
                os.chmod(config_path, 0o640)  # Secure file permissions
                json.dump(self.to_dict(), f, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save configuration to {config_path}: {e}")

    @classmethod
    def load(cls, config_path: str) -> "ModelConfig":
        """
        Load configuration from a JSON file with validation.

        Args:
            config_path: Path to the configuration file

        Returns:
            ModelConfig instance

        Raises:
            ValueError: If the configuration file is invalid or cannot be loaded
        """
        if not os.path.exists(config_path):
            return cls()

        try:
            # Load raw config from file
            with open(config_path, "r", encoding="utf - 8") as f:
                config_dict = json.load(f)

            # Validate using Pydantic if available
            try:
                from pydantic import ValidationError

                # Use the Pydantic schema to validate the config
                validated_config = ModelConfigSchema.model_validate(config_dict)

                # Convert back to dict for creating the ModelConfig instance
                validated_dict = validated_config.model_dump()

                # Convert public field names to private ones
                private_dict = {
                    (
                        f"_{key}"
                        if key in {"models_dir", "cache_dir", "max_threads", 
                            "auto_discover"}
                        else key
                    ): value
                    for key, value in validated_dict.items()
                }

                return cls(**private_dict)

            except ImportError:
                # Fallback to basic validation if Pydantic isn't available
                print("Warning: Pydantic validation not available - \
                    using basic validation")

                # Basic validation of required fields and types
                required_fields = {"models_dir", "cache_dir", "cache_enabled", 
                    "cache_ttl"}
                if not all(field in config_dict for field in required_fields):
                    raise ValueError(
                        f"Missing required fields: {required_fields - \
                            set(config_dict.keys())}"
                    )

                # Convert public field names to private ones
                private_dict = {
                    (
                        f"_{key}"
                        if key in {"models_dir", "cache_dir", "max_threads", 
                            "auto_discover"}
                        else key
                    ): value
                    for key, value in config_dict.items()
                }

                return cls(**private_dict)

        except Exception as e:
            raise ValueError(f"Failed to load configuration from {config_path}: {e}")

    @classmethod
    def get_default_config_path(cls) -> str:
        """
        Get the default path for the configuration file.

        Returns:
            Default configuration file path
        """
        config_dir = os.path.join(os.path.expanduser("~"), ".pAIssive_income")
        os.makedirs(config_dir, mode=0o750, exist_ok=True)
        return os.path.join(config_dir, "model_config.json")

    @classmethod
    def get_default(cls) -> "ModelConfig":
        """
        Get the default configuration.

        Returns:
            Default ModelConfig instance
        """
        config_path = cls.get_default_config_path()
        if os.path.exists(config_path):
            try:
                return cls.load(config_path)
            except Exception as e:
                print(f"Warning: Failed to load default config, creating new one: {e}")
                # Fall through to create new config

        # Create and save default config with secure permissions
        config = cls()
        try:
            config.save(config_path)
        except Exception as e:
            print(f"Warning: Failed to save default config: {e}")

        return config


# Optional Pydantic schema for validation
try:
    from pydantic import BaseModel, Field, model_validator

    class ModelConfigSchema(BaseModel):
        """Pydantic schema for model configuration validation."""

        models_dir: str
        cache_dir: str
        cache_enabled: bool = True
        cache_ttl: int = Field(ge=0)
        max_cache_size: int = Field(ge=0)
        default_device: str
        max_threads: Optional[int] = Field(gt=0, nullable=True)
        auto_discover: bool = True
        model_sources: List[str]
        default_text_model: str
        default_embedding_model: str

        @model_validator(mode="after")
        def validate_directories(cls, values):
            """Validate directory paths."""
            for dir_field in ["models_dir", "cache_dir"]:
                dir_path = values.get(dir_field)
                if dir_path:
                    values[dir_field] = os.path.abspath(dir_path)
            return values

except ImportError:
    # Pydantic is optional - if not available, validation will be basic
    pass
