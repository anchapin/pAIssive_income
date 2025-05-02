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
import json
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Optional, Type

from common_utils import from_json, load_from_json_file, save_to_json_file, to_json
from interfaces.model_interfaces import IModelConfig

from .schemas import ModelConfigSchema


class IModelConfig(ABC):
    @property
    @abstractmethod
    def models_dir(self) -> str:
        pass

    @property
    @abstractmethod
    def cache_dir(self) -> str:
        pass

    @property
    @abstractmethod
    def max_threads(self) -> int:
        pass

    @property
    @abstractmethod
    def auto_discover(self) -> bool:
        pass

    @classmethod
    @abstractmethod
    def get_default(cls) -> "IModelConfig":
        pass


class ModelConfig(IModelConfig):
    def __init__(self, config_path: Optional[str] = None):
        self._config: Dict[str, Any] = {}
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                self._config = json.load(f)

    @property
    def models_dir(self) -> str:
        return self._config.get(
            "models_dir", os.path.join(os.path.dirname(__file__), "models")
        )

    @property
    def cache_dir(self) -> str:
        return self._config.get(
            "cache_dir", os.path.join(os.path.dirname(__file__), "cache")
        )

    @property
    def max_threads(self) -> int:
        return self._config.get("max_threads", 4)

    @property
    def auto_discover(self) -> bool:
        return self._config.get("auto_discover", True)

    @classmethod
    def get_default(cls) -> "IModelConfig":
        return cls()
