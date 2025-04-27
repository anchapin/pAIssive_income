"""
Model configuration for the AI Models module.

This module provides classes and functions for configuring AI models,
including settings for model paths, cache, and performance options.
"""

import os
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from interfaces.model_interfaces import IModelConfig
from common_utils import to_json, from_json, save_to_json_file, load_from_json_file
from .schemas import ModelConfigSchema


@dataclass
class ModelConfig(IModelConfig):
    """
    Configuration for AI models.
    """
    # Base directories
    _models_dir: str = field(default_factory=lambda: os.path.join(os.path.expanduser("~"), ".pAIssive_income", "models"))
    _cache_dir: str = field(default_factory=lambda: os.path.join(os.path.expanduser("~"), ".pAIssive_income", "cache"))

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
    default_embedding_model: str = "all-MiniLM-L6-v2"

    def __post_init__(self):
        """
        Create necessary directories after initialization.
        """
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

    @property
    def models_dir(self) -> str:
        """Get the models directory."""
        return self._models_dir
    
    @models_dir.setter
    def models_dir(self, value: str):
        """Set the models directory."""
        self._models_dir = value
        os.makedirs(self._models_dir, exist_ok=True)
    
    @property
    def cache_dir(self) -> str:
        """Get the cache directory."""
        return self._cache_dir
    
    @cache_dir.setter
    def cache_dir(self, value: str):
        """Set the cache directory."""
        self._cache_dir = value
        os.makedirs(self._cache_dir, exist_ok=True)
    
    @property
    def auto_discover(self) -> bool:
        """Get whether to auto-discover models."""
        return self._auto_discover
    
    @auto_discover.setter
    def auto_discover(self, value: bool):
        """Set whether to auto-discover models."""
        self._auto_discover = value
    
    @property
    def max_threads(self) -> Optional[int]:
        """Get the maximum number of threads to use."""
        return self._max_threads
    
    @max_threads.setter
    def max_threads(self, value: Optional[int]):
        """Set the maximum number of threads to use."""
        self._max_threads = value

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
            "default_embedding_model": self.default_embedding_model
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
