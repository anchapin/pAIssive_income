"""
"""
Magnitude pruner for AI models.
Magnitude pruner for AI models.


This module provides a pruner that uses magnitude-based pruning to reduce
This module provides a pruner that uses magnitude-based pruning to reduce
model size and improve inference speed.
model size and improve inference speed.
"""
"""


try:
    try:
    import torch
    import torch
except ImportError:
except ImportError:
    pass
    pass




    import json
    import json
    import logging
    import logging
    import os
    import os
    from typing import Any, Dict, List, Optional, Tuple
    from typing import Any, Dict, List, Optional, Tuple


    import torch
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from transformers import AutoModelForCausalLM, AutoTokenizer


    from .base import Pruner, PruningConfig, PruningMethod
    from .base import Pruner, PruningConfig, PruningMethod


    TRANSFORMERS_AVAILABLE
    TRANSFORMERS_AVAILABLE
    import torch.nn.utils.prune
    import torch.nn.utils.prune


    # Set up logging
    # Set up logging
    logging.basicConfig(
    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    )
    logger = logging.getLogger(__name__)
    logger = logging.getLogger(__name__)


    # Try to import optional dependencies
    # Try to import optional dependencies
    try:
    try:




    TORCH_AVAILABLE = True
    TORCH_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("PyTorch not available. Magnitude pruner will not work.")
    logger.warning("PyTorch not available. Magnitude pruner will not work.")
    TORCH_AVAILABLE = False
    TORCH_AVAILABLE = False


    try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning(
    logger.warning(
    "Transformers not available. Magnitude pruner will have limited functionality."
    "Transformers not available. Magnitude pruner will have limited functionality."
    )
    )
    TRANSFORMERS_AVAILABLE = False
    TRANSFORMERS_AVAILABLE = False


    try:
    try:
    as torch_prune
    as torch_prune


    TORCH_PRUNE_AVAILABLE = True
    TORCH_PRUNE_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("PyTorch pruning utilities not available.")
    logger.warning("PyTorch pruning utilities not available.")
    TORCH_PRUNE_AVAILABLE = False
    TORCH_PRUNE_AVAILABLE = False




    class MagnitudePruner(Pruner):
    class MagnitudePruner(Pruner):
    """
    """
    Pruner that uses magnitude-based pruning.
    Pruner that uses magnitude-based pruning.
    """
    """


    def __init__(self, config: PruningConfig):
    def __init__(self, config: PruningConfig):
    """
    """
    Initialize the magnitude pruner.
    Initialize the magnitude pruner.


    Args:
    Args:
    config: Pruning configuration
    config: Pruning configuration
    """
    """
    super().__init__(config)
    super().__init__(config)


    if not TORCH_AVAILABLE:
    if not TORCH_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "PyTorch not available. Please install it with: pip install torch"
    "PyTorch not available. Please install it with: pip install torch"
    )
    )


    if not TRANSFORMERS_AVAILABLE:
    if not TRANSFORMERS_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "Transformers not available. Please install it with: pip install transformers"
    "Transformers not available. Please install it with: pip install transformers"
    )
    )


    if not TORCH_PRUNE_AVAILABLE:
    if not TORCH_PRUNE_AVAILABLE:
    raise ImportError("PyTorch pruning utilities not available.")
    raise ImportError("PyTorch pruning utilities not available.")


    # Validate configuration
    # Validate configuration
    self._validate_config()
    self._validate_config()


    def _validate_config(self) -> None:
    def _validate_config(self) -> None:
    """
    """
    Validate the pruning configuration.
    Validate the pruning configuration.


    Raises:
    Raises:
    ValueError: If the configuration is invalid
    ValueError: If the configuration is invalid
    """
    """
    supported_methods = self.get_supported_methods()
    supported_methods = self.get_supported_methods()
    if self.config.method not in supported_methods:
    if self.config.method not in supported_methods:
    raise ValueError(
    raise ValueError(
    f"Unsupported pruning method: {self.config.method}. "
    f"Unsupported pruning method: {self.config.method}. "
    f"Supported methods: {[m.value for m in supported_methods]}"
    f"Supported methods: {[m.value for m in supported_methods]}"
    )
    )


    if not 0.0 <= self.config.sparsity <= 1.0:
    if not 0.0 <= self.config.sparsity <= 1.0:
    raise ValueError(
    raise ValueError(
    f"Sparsity must be between 0.0 and 1.0, got {self.config.sparsity}"
    f"Sparsity must be between 0.0 and 1.0, got {self.config.sparsity}"
    )
    )


    def prune(
    def prune(
    self, model_path: str, output_path: Optional[str] = None, **kwargs
    self, model_path: str, output_path: Optional[str] = None, **kwargs
    ) -> str:
    ) -> str:
    """
    """
    Prune a model using magnitude-based pruning.
    Prune a model using magnitude-based pruning.


    Args:
    Args:
    model_path: Path to the model
    model_path: Path to the model
    output_path: Path to save the pruned model (None for in-place)
    output_path: Path to save the pruned model (None for in-place)
    **kwargs: Additional parameters for pruning
    **kwargs: Additional parameters for pruning


    Returns:
    Returns:
    Path to the pruned model
    Path to the pruned model
    """
    """
    logger.info(f"Pruning model {model_path} with magnitude-based pruning")
    logger.info(f"Pruning model {model_path} with magnitude-based pruning")


    # Determine output path
    # Determine output path
    if output_path is None:
    if output_path is None:
    output_path = model_path
    output_path = model_path


    # Load tokenizer
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)


    # Load model
    # Load model
    model = AutoModelForCausalLM.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)


    # Get layers to prune
    # Get layers to prune
    layers_to_prune = self._get_layers_to_prune(model)
    layers_to_prune = self._get_layers_to_prune(model)


    # Apply pruning
    # Apply pruning
    if self.config.gradual_pruning:
    if self.config.gradual_pruning:
    self._apply_gradual_pruning(model, layers_to_prune)
    self._apply_gradual_pruning(model, layers_to_prune)
    else:
    else:
    self._apply_one_shot_pruning(model, layers_to_prune)
    self._apply_one_shot_pruning(model, layers_to_prune)


    # Remove pruning reparameterization
    # Remove pruning reparameterization
    for module, name in layers_to_prune:
    for module, name in layers_to_prune:
    torch_prune.remove(module, name)
    torch_prune.remove(module, name)


    # Save model and tokenizer
    # Save model and tokenizer
    logger.info(f"Saving pruned model to {output_path}")
    logger.info(f"Saving pruned model to {output_path}")
    model.save_pretrained(output_path)
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)


    # Save pruning configuration
    # Save pruning configuration
    self._save_pruning_config(output_path)
    self._save_pruning_config(output_path)


    return output_path
    return output_path


    def _get_layers_to_prune(self, model) -> List[Tuple[torch.nn.Module, str]]:
    def _get_layers_to_prune(self, model) -> List[Tuple[torch.nn.Module, str]]:
    """
    """
    Get the layers to prune.
    Get the layers to prune.


    Args:
    Args:
    model: PyTorch model
    model: PyTorch model


    Returns:
    Returns:
    List of (module, name) tuples to prune
    List of (module, name) tuples to prune
    """
    """
    layers_to_prune = []
    layers_to_prune = []


    # Iterate through named modules
    # Iterate through named modules
    for name, module in model.named_modules():
    for name, module in model.named_modules():
    # Skip if not a leaf module
    # Skip if not a leaf module
    if list(module.children()):
    if list(module.children()):
    continue
    continue


    # Check if the module has weight parameters
    # Check if the module has weight parameters
    if not hasattr(module, "weight") or module.weight is None:
    if not hasattr(module, "weight") or module.weight is None:
    continue
    continue


    # Check if the layer is excluded
    # Check if the layer is excluded
    if any(excluded in name for excluded in self.config.excluded_layers):
    if any(excluded in name for excluded in self.config.excluded_layers):
    continue
    continue


    # Check if the layer is included (if specified)
    # Check if the layer is included (if specified)
    if self.config.included_layers is not None:
    if self.config.included_layers is not None:
    if not any(
    if not any(
    included in name for included in self.config.included_layers
    included in name for included in self.config.included_layers
    ):
    ):
    continue
    continue


    # Add to layers to prune
    # Add to layers to prune
    layers_to_prune.append((module, "weight"))
    layers_to_prune.append((module, "weight"))


    return layers_to_prune
    return layers_to_prune


    def _apply_one_shot_pruning(
    def _apply_one_shot_pruning(
    self, model, layers_to_prune: List[Tuple[torch.nn.Module, str]]
    self, model, layers_to_prune: List[Tuple[torch.nn.Module, str]]
    ) -> None:
    ) -> None:
    """
    """
    Apply one-shot pruning to the model.
    Apply one-shot pruning to the model.


    Args:
    Args:
    model: PyTorch model
    model: PyTorch model
    layers_to_prune: List of (module, name) tuples to prune
    layers_to_prune: List of (module, name) tuples to prune
    """
    """
    logger.info(f"Applying one-shot pruning with sparsity {self.config.sparsity}")
    logger.info(f"Applying one-shot pruning with sparsity {self.config.sparsity}")


    for module, name in layers_to_prune:
    for module, name in layers_to_prune:
    torch_prune.l1_unstructured(module, name=name, amount=self.config.sparsity)
    torch_prune.l1_unstructured(module, name=name, amount=self.config.sparsity)


    def _apply_gradual_pruning(
    def _apply_gradual_pruning(
    self, model, layers_to_prune: List[Tuple[torch.nn.Module, str]]
    self, model, layers_to_prune: List[Tuple[torch.nn.Module, str]]
    ) -> None:
    ) -> None:
    """
    """
    Apply gradual pruning to the model.
    Apply gradual pruning to the model.


    Args:
    Args:
    model: PyTorch model
    model: PyTorch model
    layers_to_prune: List of (module, name) tuples to prune
    layers_to_prune: List of (module, name) tuples to prune
    """
    """
    logger.info(
    logger.info(
    f"Applying gradual pruning from {self.config.initial_sparsity} to {self.config.final_sparsity}"
    f"Applying gradual pruning from {self.config.initial_sparsity} to {self.config.final_sparsity}"
    )
    )


    # Calculate pruning schedule
    # Calculate pruning schedule
    initial_sparsity = self.config.initial_sparsity
    initial_sparsity = self.config.initial_sparsity
    final_sparsity = self.config.final_sparsity
    final_sparsity = self.config.final_sparsity
    steps = self.config.pruning_steps
    steps = self.config.pruning_steps


    for step in range(steps):
    for step in range(steps):
    # Calculate current sparsity
    # Calculate current sparsity
    current_sparsity = (
    current_sparsity = (
    initial_sparsity
    initial_sparsity
    + (final_sparsity - initial_sparsity) * (step + 1) / steps
    + (final_sparsity - initial_sparsity) * (step + 1) / steps
    )
    )
    logger.info(
    logger.info(
    f"Pruning step {step + 1}/{steps}, sparsity: {current_sparsity}"
    f"Pruning step {step + 1}/{steps}, sparsity: {current_sparsity}"
    )
    )


    for module, name in layers_to_prune:
    for module, name in layers_to_prune:
    # For the first step, apply pruning
    # For the first step, apply pruning
    if step == 0:
    if step == 0:
    torch_prune.l1_unstructured(
    torch_prune.l1_unstructured(
    module, name=name, amount=current_sparsity
    module, name=name, amount=current_sparsity
    )
    )
    # For subsequent steps, remove and reapply pruning
    # For subsequent steps, remove and reapply pruning
    else:
    else:
    torch_prune.remove(module, name)
    torch_prune.remove(module, name)
    torch_prune.l1_unstructured(
    torch_prune.l1_unstructured(
    module, name=name, amount=current_sparsity
    module, name=name, amount=current_sparsity
    )
    )


    def _save_pruning_config(self, output_path: str) -> None:
    def _save_pruning_config(self, output_path: str) -> None:
    """
    """
    Save the pruning configuration.
    Save the pruning configuration.


    Args:
    Args:
    output_path: Path to save the configuration
    output_path: Path to save the configuration
    """
    """
    config_path = os.path.join(output_path, "pruning_config.json")
    config_path = os.path.join(output_path, "pruning_config.json")


    with open(config_path, "w", encoding="utf-8") as f:
    with open(config_path, "w", encoding="utf-8") as f:
    json.dump(self.config.to_dict(), f, indent=2)
    json.dump(self.config.to_dict(), f, indent=2)


    def supports_model_type(self, model_type: str) -> bool:
    def supports_model_type(self, model_type: str) -> bool:
    """
    """
    Check if the pruner supports a model type.
    Check if the pruner supports a model type.


    Args:
    Args:
    model_type: Type of the model
    model_type: Type of the model


    Returns:
    Returns:
    True if the model type is supported, False otherwise
    True if the model type is supported, False otherwise
    """
    """
    # Magnitude pruning supports most model types
    # Magnitude pruning supports most model types
    supported_types = [
    supported_types = [
    "text-generation",
    "text-generation",
    "text-classification",
    "text-classification",
    "embedding",
    "embedding",
    "causal-lm",
    "causal-lm",
    "seq2seq-lm",
    "seq2seq-lm",
    "image-classification",
    "image-classification",
    "object-detection",
    "object-detection",
    ]
    ]


    return model_type in supported_types
    return model_type in supported_types


    def get_supported_methods(self) -> List[PruningMethod]:
    def get_supported_methods(self) -> List[PruningMethod]:
    """
    """
    Get the pruning methods supported by the pruner.
    Get the pruning methods supported by the pruner.


    Returns:
    Returns:
    List of supported pruning methods
    List of supported pruning methods
    """
    """
    return [PruningMethod.MAGNITUDE]
    return [PruningMethod.MAGNITUDE]


    def get_pruning_info(self) -> Dict[str, Any]:
    def get_pruning_info(self) -> Dict[str, Any]:
    """
    """
    Get information about the pruning.
    Get information about the pruning.


    Returns:
    Returns:
    Dictionary with pruning information
    Dictionary with pruning information
    """
    """
    return {
    return {
    "pruner": "MagnitudePruner",
    "pruner": "MagnitudePruner",
    "method": self.config.method.value,
    "method": self.config.method.value,
    "sparsity": self.config.sparsity,
    "sparsity": self.config.sparsity,
    "gradual_pruning": self.config.gradual_pruning,
    "gradual_pruning": self.config.gradual_pruning,
    "pruning_steps": (
    "pruning_steps": (
    self.config.pruning_steps if self.config.gradual_pruning else 1
    self.config.pruning_steps if self.config.gradual_pruning else 1
    ),
    ),
    "initial_sparsity": (
    "initial_sparsity": (
    self.config.initial_sparsity
    self.config.initial_sparsity
    if self.config.gradual_pruning
    if self.config.gradual_pruning
    else self.config.sparsity
    else self.config.sparsity
    ),
    ),
    "final_sparsity": (
    "final_sparsity": (
    self.config.final_sparsity
    self.config.final_sparsity
    if self.config.gradual_pruning
    if self.config.gradual_pruning
    else self.config.sparsity
    else self.config.sparsity
    ),
    ),
    }
    }