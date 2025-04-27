"""
Model configuration for the AI Models module.

This module provides classes and functions for configuring AI models,
including settings for model paths, cache, and performance options.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class ModelConfig:
    """
    Configuration for AI models.
    """
    # Base directories
    models_dir: str = field(default_factory=lambda: os.path.join(os.path.expanduser("~"), ".pAIssive_income", "models"))
    cache_dir: str = field(default_factory=lambda: os.path.join(os.path.expanduser("~"), ".pAIssive_income", "cache"))

    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 86400  # 24 hours in seconds
    max_cache_size: int = 1000  # Maximum number of items in memory cache

    # Performance settings
    default_device: str = "auto"  # "auto", "cpu", "cuda", "mps", etc.
    max_threads: Optional[int] = None  # None means use all available threads

    # Model discovery
    auto_discover: bool = True
    model_sources: List[str] = field(default_factory=lambda: ["local", "huggingface"])

    # Default models
    default_text_model: str = "gpt2"
    default_embedding_model: str = "all-MiniLM-L6-v2"

    def __post_init__(self):
        """
        Create necessary directories after initialization.
        """
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return asdict(self)

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
        Save the configuration to a JSON file.

        Args:
            config_path: Path to save the configuration
        """
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, config_path: str) -> 'ModelConfig':
        """
        Load configuration from a JSON file.

        Args:
            config_path: Path to the configuration file

        Returns:
            ModelConfig instance
        """
        if not os.path.exists(config_path):
            return cls()

        with open(config_path, 'r') as f:
            config_dict = json.load(f)

        return cls(**config_dict)

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
    def get_default(cls) -> 'ModelConfig':
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
