"""
Base data types for the AI Models module.

This module provides shared data structures used across the AI Models module
to avoid circular imports between model_manager.py and model_versioning.py.
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from interfaces.model_interfaces import IModelInfo

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ModelInfo(IModelInfo):
    """
    Information about an AI model.
    """

    _id: str
    _name: str
    _type: str  # huggingface, llama, embedding, etc.
    _path: str
    _description: str = ""
    size_mb: float = 0.0
    format: str = ""  # gguf, onnx, pytorch, etc.
    quantization: str = ""  # 4-bit, 8-bit, etc.
    capabilities: List[str] = None
    _metadata: Dict[str, Any] = None
    performance: Dict[str, Any] = None
    last_updated: str = ""
    created_at: str = ""
    updated_at: str = ""
    # Added version field for model versioning
    version: str = "0.0.0"

    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        path: str,
        description: str = "",
        size_mb: float = 0.0,
        format: str = "",
        quantization: str = "",
        capabilities: List[str] = None,
        metadata: Dict[str, Any] = None,
        performance: Dict[str, Any] = None,
        last_updated: str = "",
        created_at: str = "",
        updated_at: str = "",
        version: str = "0.0.0",
    ):
        """Initialize a new ModelInfo object."""
        self._id = id
        self._name = name
        self._type = type
        self._path = path
        self._description = description
        self.size_mb = size_mb
        self.format = format
        self.quantization = quantization
        self.capabilities = capabilities if capabilities else []
        self._metadata = metadata if metadata else {}
        self.performance = performance if performance else {}
        self.last_updated = last_updated
        self.created_at = created_at
        self.updated_at = updated_at
        self.version = version

        # Run post-initialization logic
        self.__post_init__()

    @property
    def id(self) -> str:
        """Get the model ID."""
        return self._id

    @property
    def name(self) -> str:
        """Get the model name."""
        return self._name

    @property
    def description(self) -> str:
        """Get the model description."""
        return self._description

    @property
    def type(self) -> str:
        """Get the model type."""
        return self._type

    @property
    def path(self) -> str:
        """Get the model path."""
        return self._path

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the model metadata."""
        return self._metadata if self._metadata is not None else {}

    @property
    def model_version(self) -> str:
        """Get the model version."""
        return self.version

    def __post_init__(self):
        """
        Initialize default values after creation.
        """
        if self.capabilities is None:
            self.capabilities = []

        if self._metadata is None:
            self._metadata = {}

        if self.performance is None:
            self.performance = {}

        # Set timestamps if not provided
        current_time = time.strftime("%Y-%m-%dT%H:%M:%S")

        if not self.created_at:
            self.created_at = current_time

        if not self.updated_at:
            self.updated_at = current_time

        if not self.last_updated:
            self.last_updated = time.strftime("%Y-%m-%d %H:%M:%S")

        # Calculate size if path exists and size is not provided
        if self.size_mb == 0.0 and os.path.exists(self._path):
            try:
                self.size_mb = os.path.getsize(self._path) / (1024 * 1024)
            except (OSError, IOError):
                pass

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model info to a dictionary.

        Returns:
            Dictionary representation of the model info
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "path": self.path,
            "description": self.description,
            "size_mb": self.size_mb,
            "format": self.format,
            "quantization": self.quantization,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
            "performance": self.performance,
            "last_updated": self.last_updated,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the model info to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the model info
        """
        return json.dumps(self.to_dict(), indent=indent)

    def update_performance(self, metrics: Dict[str, Any]) -> None:
        """
        Update performance metrics for the model.

        Args:
            metrics: Dictionary of performance metrics
        """
        if self.performance is None:
            self.performance = {}

        self.performance.update(metrics)
        self.update_timestamp()

    def update_timestamp(self) -> None:
        """
        Update the last_updated and updated_at timestamps.
        """
        self.last_updated = time.strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = time.strftime("%Y-%m-%dT%H:%M:%S")

        # For compatibility with datetime.now().isoformat() in tests
        if hasattr(datetime, "now"):
            self.updated_at = datetime.now().isoformat()

    def has_capability(self, capability: str) -> bool:
        """
        Check if the model has a specific capability.

        Args:
            capability: Capability to check

        Returns:
            True if the model has the capability, False otherwise
        """
        return capability in self.capabilities

    def set_version(self, version: str) -> None:
        """
        Set the model version.

        Args:
            version: Version string in semver format (e.g., "1.0.0")
        """
        self.version = version
        self.update_timestamp()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelInfo":
        """
        Create a ModelInfo instance from a dictionary.

        Args:
            data: Dictionary containing model information

        Returns:
            ModelInfo instance
        """
        return cls(**data)
