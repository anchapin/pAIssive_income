"""
Magnitude pruner for AI models.

This module provides a pruner that uses magnitude-based pruning to reduce
model size and improve inference speed.
"""

try:
    import torch
except ImportError:
    pass


import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from .base import Pruner, PruningConfig, PruningMethod


    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    TRANSFORMERS_AVAILABLE 
    import torch.nn.utils.prune

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:


    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available. Magnitude pruner will not work.")
    TORCH_AVAILABLE = False

try:
= True
except ImportError:
    logger.warning(
        "Transformers not available. Magnitude pruner will have limited functionality."
    )
    TRANSFORMERS_AVAILABLE = False

try:
 as torch_prune

    TORCH_PRUNE_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch pruning utilities not available.")
    TORCH_PRUNE_AVAILABLE = False


class MagnitudePruner(Pruner):
    """
    Pruner that uses magnitude-based pruning.
    """

    def __init__(self, config: PruningConfig):
        """
        Initialize the magnitude pruner.

        Args:
            config: Pruning configuration
        """
        super().__init__(config)

        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch not available. Please install it with: pip install torch"
            )

        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Transformers not available. Please install it with: pip install transformers"
            )

        if not TORCH_PRUNE_AVAILABLE:
            raise ImportError("PyTorch pruning utilities not available.")

        # Validate configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """
        Validate the pruning configuration.

        Raises:
            ValueError: If the configuration is invalid
        """
        supported_methods = self.get_supported_methods()
        if self.config.method not in supported_methods:
            raise ValueError(
                f"Unsupported pruning method: {self.config.method}. "
                f"Supported methods: {[m.value for m in supported_methods]}"
            )

        if not 0.0 <= self.config.sparsity <= 1.0:
            raise ValueError(
                f"Sparsity must be between 0.0 and 1.0, got {self.config.sparsity}"
            )

    def prune(
        self, model_path: str, output_path: Optional[str] = None, **kwargs
    ) -> str:
        """
        Prune a model using magnitude-based pruning.

        Args:
            model_path: Path to the model
            output_path: Path to save the pruned model (None for in-place)
            **kwargs: Additional parameters for pruning

        Returns:
            Path to the pruned model
        """
        logger.info(f"Pruning model {model_path} with magnitude-based pruning")

        # Determine output path
        if output_path is None:
            output_path = model_path

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Load model
        model = AutoModelForCausalLM.from_pretrained(model_path)

        # Get layers to prune
        layers_to_prune = self._get_layers_to_prune(model)

        # Apply pruning
        if self.config.gradual_pruning:
            self._apply_gradual_pruning(model, layers_to_prune)
        else:
            self._apply_one_shot_pruning(model, layers_to_prune)

        # Remove pruning reparameterization
        for module, name in layers_to_prune:
            torch_prune.remove(module, name)

        # Save model and tokenizer
        logger.info(f"Saving pruned model to {output_path}")
        model.save_pretrained(output_path)
        tokenizer.save_pretrained(output_path)

        # Save pruning configuration
        self._save_pruning_config(output_path)

        return output_path

    def _get_layers_to_prune(self, model) -> List[Tuple[torch.nn.Module, str]]:
        """
        Get the layers to prune.

        Args:
            model: PyTorch model

        Returns:
            List of (module, name) tuples to prune
        """
        layers_to_prune = []

        # Iterate through named modules
        for name, module in model.named_modules():
            # Skip if not a leaf module
            if list(module.children()):
                continue

            # Check if the module has weight parameters
            if not hasattr(module, "weight") or module.weight is None:
                continue

            # Check if the layer is excluded
            if any(excluded in name for excluded in self.config.excluded_layers):
                continue

            # Check if the layer is included (if specified)
            if self.config.included_layers is not None:
                if not any(
                    included in name for included in self.config.included_layers
                ):
                    continue

            # Add to layers to prune
            layers_to_prune.append((module, "weight"))

        return layers_to_prune

    def _apply_one_shot_pruning(
        self, model, layers_to_prune: List[Tuple[torch.nn.Module, str]]
    ) -> None:
        """
        Apply one-shot pruning to the model.

        Args:
            model: PyTorch model
            layers_to_prune: List of (module, name) tuples to prune
        """
        logger.info(f"Applying one-shot pruning with sparsity {self.config.sparsity}")

        for module, name in layers_to_prune:
            torch_prune.l1_unstructured(module, name=name, amount=self.config.sparsity)

    def _apply_gradual_pruning(
        self, model, layers_to_prune: List[Tuple[torch.nn.Module, str]]
    ) -> None:
        """
        Apply gradual pruning to the model.

        Args:
            model: PyTorch model
            layers_to_prune: List of (module, name) tuples to prune
        """
        logger.info(
            f"Applying gradual pruning from {self.config.initial_sparsity} to {self.config.final_sparsity}"
        )

        # Calculate pruning schedule
        initial_sparsity = self.config.initial_sparsity
        final_sparsity = self.config.final_sparsity
        steps = self.config.pruning_steps

        for step in range(steps):
            # Calculate current sparsity
            current_sparsity = (
                initial_sparsity
                + (final_sparsity - initial_sparsity) * (step + 1) / steps
            )
            logger.info(
                f"Pruning step {step + 1}/{steps}, sparsity: {current_sparsity}"
            )

            for module, name in layers_to_prune:
                # For the first step, apply pruning
                if step == 0:
                    torch_prune.l1_unstructured(
                        module, name=name, amount=current_sparsity
                    )
                # For subsequent steps, remove and reapply pruning
                else:
                    torch_prune.remove(module, name)
                    torch_prune.l1_unstructured(
                        module, name=name, amount=current_sparsity
                    )

    def _save_pruning_config(self, output_path: str) -> None:
        """
        Save the pruning configuration.

        Args:
            output_path: Path to save the configuration
        """
        config_path = os.path.join(output_path, "pruning_config.json")

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.config.to_dict(), f, indent=2)

    def supports_model_type(self, model_type: str) -> bool:
        """
        Check if the pruner supports a model type.

        Args:
            model_type: Type of the model

        Returns:
            True if the model type is supported, False otherwise
        """
        # Magnitude pruning supports most model types
        supported_types = [
            "text-generation",
            "text-classification",
            "embedding",
            "causal-lm",
            "seq2seq-lm",
            "image-classification",
            "object-detection",
        ]

        return model_type in supported_types

    def get_supported_methods(self) -> List[PruningMethod]:
        """
        Get the pruning methods supported by the pruner.

        Returns:
            List of supported pruning methods
        """
        return [PruningMethod.MAGNITUDE]

    def get_pruning_info(self) -> Dict[str, Any]:
        """
        Get information about the pruning.

        Returns:
            Dictionary with pruning information
        """
        return {
            "pruner": "MagnitudePruner",
            "method": self.config.method.value,
            "sparsity": self.config.sparsity,
            "gradual_pruning": self.config.gradual_pruning,
            "pruning_steps": (
                self.config.pruning_steps if self.config.gradual_pruning else 1
            ),
            "initial_sparsity": (
                self.config.initial_sparsity
                if self.config.gradual_pruning
                else self.config.sparsity
            ),
            "final_sparsity": (
                self.config.final_sparsity
                if self.config.gradual_pruning
                else self.config.sparsity
            ),
        }