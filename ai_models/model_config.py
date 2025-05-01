"""
Model configuration for the AI Models module.

This module provides classes and functions for configuring AI models,
including settings for model paths, cache, and performance options.
"""

import enum
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common_utils import from_json, load_from_json_file, save_to_json_file, to_json
from interfaces.model_interfaces import IModelConfig

from .schemas import ModelConfigSchema


class ModelType(enum.Enum):
    """Enum for model types."""

    LLAMA_CPP = "llama_cpp"
    TRANSFORMERS = "transformers"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    ONNX = "onnx"
    TENSORRT = "tensorrt"
    LMSTUDIO = "lmstudio"
    OLLAMA = "ollama"
    OPENAI_COMPATIBLE = "openai_compatible"


class ModelConfig:
    """Configuration for model loading and management."""

    def __init__(
        self,
        models_dir: str,
        cache_dir: str,
        model_sources: Optional[List[str]] = None,
        auto_discover: bool = True,
        max_threads: Optional[int] = None,
    ) -> None:
        """Initialize model configuration.

        Args:
            models_dir: Directory containing model files
            cache_dir: Directory for caching model data
            model_sources: List of model sources (e.g. ['local', 'huggingface'])
            auto_discover: Whether to auto-discover models on init
            max_threads: Maximum number of threads for model loading
        """
        self.models_dir = models_dir
        self.cache_dir = cache_dir
        self.model_sources = model_sources or ["local"]
        self.auto_discover = auto_discover
        self._max_threads = max_threads or os.cpu_count() or 4

        # Create directories if they don't exist
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

    @property
    def max_threads(self) -> int:
        """Get maximum number of threads."""
        return self._max_threads

    @property
    def cache_enabled(self) -> bool:
        """Get whether caching is enabled."""
        return True

    @property
    def cache_ttl(self) -> int:
        """Get cache time-to-live in seconds."""
        return 3600  # 1 hour default

    @property
    def max_cache_size(self) -> int:
        """Get maximum cache size in bytes."""
        return 1024 * 1024 * 1024  # 1GB default

    @property
    def default_device(self) -> str:
        """Get default device for model inference."""
        return "cpu"

    @property
    def default_text_model(self) -> Optional[str]:
        """Get default text generation model ID."""
        return None

    @property
    def default_embedding_model(self) -> Optional[str]:
        """Get default text embedding model ID."""
        return None

    @classmethod
    def get_default(cls) -> "ModelConfig":
        """Get default configuration."""
        default_dir = os.path.expanduser("~/.paissive_income")
        return cls(
            models_dir=os.path.join(default_dir, "models"),
            cache_dir=os.path.join(default_dir, "cache"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        # Convert to dict but replace underscore-prefixed attributes with their property names
        result = {
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
        return result

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the configuration to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the configuration
        """
        return to_json(self.to_dict(), indent=indent)

    def save(self, config_path: str) -> None:
        """
        Save the configuration to a JSON file.

        Args:
            config_path: Path to save the configuration
        """
        save_to_json_file(self.to_dict(), config_path)

    @classmethod
    def load(cls, config_path: str) -> "ModelConfig":
        """
        Load configuration from a JSON file.

        Args:
            config_path: Path to the configuration file

        Returns:
            ModelConfig instance
        """
        if not os.path.exists(config_path):
            return cls()

        try:
            config_dict = load_from_json_file(config_path)
            return cls(**config_dict)
        except Exception as e:
            # If there's an error loading the config, return the default
            print(f"Error loading config from {config_path}: {e}")
            return cls()

    @classmethod
    def get_default_config_path(cls) -> str:
        """
        Get the default path for the configuration file.

        Returns:
            Default configuration file path
        """
        config_dir = os.path.join(os.path.expanduser("~"), ".pAIssive_income")
        os.makedirs(config_dir, exist_ok=True)
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
            return cls.load(config_path)

        # Create and save default config
        config = cls()
        config.save(config_path)
        return config
