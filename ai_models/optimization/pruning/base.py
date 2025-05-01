"""
Base classes for model pruning.

This module provides the base classes and interfaces for model pruning.
"""

import abc
import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Type, Union


class PruningMethod(enum.Enum):
    """
    Enumeration of pruning methods.
    """

    NONE = "none"
    MAGNITUDE = "magnitude"
    STRUCTURED = "structured"
    MOVEMENT = "movement"
    L0_REGULARIZATION = "l0_regularization"
    LOTTERY_TICKET = "lottery_ticket"


@dataclass
class PruningConfig:
    """
    Configuration for model pruning.
    """

    method: PruningMethod = PruningMethod.NONE
    sparsity: float = 0.5  # Target sparsity (0.0 to 1.0)

    # Method-specific parameters
    structured_block_size: int = 4  # For structured pruning
    structured_n_m_ratio: Tuple[int, int] = (2, 4)  # For N:M structured pruning

    # Layer-specific parameters
    excluded_layers: List[str] = field(default_factory=list)
    included_layers: Optional[List[str]] = None  # None means all layers except excluded

    # Pruning schedule
    gradual_pruning: bool = False
    pruning_steps: int = 10
    initial_sparsity: float = 0.0
    final_sparsity: float = 0.5

    # Calibration parameters
    calibration_dataset: Optional[str] = None
    calibration_num_samples: int = 128
    calibration_seqlen: int = 2048

    # Additional parameters
    additional_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "method": self.method.value,
            "sparsity": self.sparsity,
            "structured_block_size": self.structured_block_size,
            "structured_n_m_ratio": self.structured_n_m_ratio,
            "excluded_layers": self.excluded_layers,
            "included_layers": self.included_layers,
            "gradual_pruning": self.gradual_pruning,
            "pruning_steps": self.pruning_steps,
            "initial_sparsity": self.initial_sparsity,
            "final_sparsity": self.final_sparsity,
            "calibration_dataset": self.calibration_dataset,
            "calibration_num_samples": self.calibration_num_samples,
            "calibration_seqlen": self.calibration_seqlen,
            **self.additional_params,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "PruningConfig":
        """
        Create a configuration from a dictionary.

        Args:
            config_dict: Dictionary with configuration parameters

        Returns:
            Pruning configuration
        """
        # Extract method
        method_str = config_dict.pop("method", "none")
        try:
            method = PruningMethod(method_str)
        except ValueError:
            method = PruningMethod.NONE

        # Extract additional parameters
        additional_params = {}
        for key, value in list(config_dict.items()):
            if key not in cls.__annotations__:
                additional_params[key] = config_dict.pop(key)

        # Create configuration
        config = cls(method=method, **config_dict)

        config.additional_params = additional_params
        return config


class Pruner(abc.ABC):
    """
    Base class for model pruners.
    """

    def __init__(self, config: PruningConfig):
        """
        Initialize the pruner.

        Args:
            config: Pruning configuration
        """
        self.config = config

    @abc.abstractmethod
    def prune(
        self, model_path: str, output_path: Optional[str] = None, **kwargs
    ) -> str:
        """
        Prune a model.

        Args:
            model_path: Path to the model
            output_path: Path to save the pruned model (None for in-place)
            **kwargs: Additional parameters for pruning

        Returns:
            Path to the pruned model
        """
        pass

    @abc.abstractmethod
    def supports_model_type(self, model_type: str) -> bool:
        """
        Check if the pruner supports a model type.

        Args:
            model_type: Type of the model

        Returns:
            True if the model type is supported, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_supported_methods(self) -> List[PruningMethod]:
        """
        Get the pruning methods supported by the pruner.

        Returns:
            List of supported pruning methods
        """
        pass

    @abc.abstractmethod
    def get_pruning_info(self) -> Dict[str, Any]:
        """
        Get information about the pruning.

        Returns:
            Dictionary with pruning information
        """
        pass
