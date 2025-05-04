"""
"""
Structured pruner for AI models.
Structured pruner for AI models.


This module provides a pruner that uses structured pruning techniques to reduce
This module provides a pruner that uses structured pruning techniques to reduce
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
    logger.warning("PyTorch not available. Structured pruner will not work.")
    logger.warning("PyTorch not available. Structured pruner will not work.")
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
    "Transformers not available. Structured pruner will have limited functionality."
    "Transformers not available. Structured pruner will have limited functionality."
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




    class StructuredPruner(Pruner):
    class StructuredPruner(Pruner):
    """
    """
    Pruner that uses structured pruning techniques.
    Pruner that uses structured pruning techniques.
    """
    """


    def __init__(self, config: PruningConfig):
    def __init__(self, config: PruningConfig):
    """
    """
    Initialize the structured pruner.
    Initialize the structured pruner.


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


    if self.config.structured_block_size <= 0:
    if self.config.structured_block_size <= 0:
    raise ValueError(
    raise ValueError(
    f"Block size must be positive, got {self.config.structured_block_size}"
    f"Block size must be positive, got {self.config.structured_block_size}"
    )
    )


    if (
    if (
    len(self.config.structured_n_m_ratio) != 2
    len(self.config.structured_n_m_ratio) != 2
    or self.config.structured_n_m_ratio[0] > self.config.structured_n_m_ratio[1]
    or self.config.structured_n_m_ratio[0] > self.config.structured_n_m_ratio[1]
    ):
    ):
    raise ValueError(
    raise ValueError(
    f"N:M ratio must be (N, M) where N <= M, got {self.config.structured_n_m_ratio}"
    f"N:M ratio must be (N, M) where N <= M, got {self.config.structured_n_m_ratio}"
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
    Prune a model using structured pruning.
    Prune a model using structured pruning.


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
    logger.info(f"Pruning model {model_path} with structured pruning")
    logger.info(f"Pruning model {model_path} with structured pruning")


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
    self._apply_structured_pruning(model, layers_to_prune)
    self._apply_structured_pruning(model, layers_to_prune)


    # Remove pruning reparameterization
    # Remove pruning reparameterization
    for module, name in layers_to_prune:
    for module, name in layers_to_prune:
    if hasattr(module, f"{name}_mask"):
    if hasattr(module, f"{name}_mask"):
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


    def _apply_structured_pruning(
    def _apply_structured_pruning(
    self, model, layers_to_prune: List[Tuple[torch.nn.Module, str]]
    self, model, layers_to_prune: List[Tuple[torch.nn.Module, str]]
    ) -> None:
    ) -> None:
    """
    """
    Apply structured pruning to the model.
    Apply structured pruning to the model.


    Args:
    Args:
    model: PyTorch model
    model: PyTorch model
    layers_to_prune: List of (module, name) tuples to prune
    layers_to_prune: List of (module, name) tuples to prune
    """
    """
    logger.info(f"Applying structured pruning with sparsity {self.config.sparsity}")
    logger.info(f"Applying structured pruning with sparsity {self.config.sparsity}")


    for module, name in layers_to_prune:
    for module, name in layers_to_prune:
    # Get the weight tensor
    # Get the weight tensor
    weight = getattr(module, name)
    weight = getattr(module, name)


    # Skip if the tensor is too small for structured pruning
    # Skip if the tensor is too small for structured pruning
    if any(dim < self.config.structured_block_size for dim in weight.shape):
    if any(dim < self.config.structured_block_size for dim in weight.shape):
    logger.warning(
    logger.warning(
    f"Skipping {name} with shape {weight.shape} (too small for block size {self.config.structured_block_size})"
    f"Skipping {name} with shape {weight.shape} (too small for block size {self.config.structured_block_size})"
    )
    )
    continue
    continue


    # Apply N:M structured sparsity
    # Apply N:M structured sparsity
    if hasattr(self, "_apply_n_m_sparsity"):
    if hasattr(self, "_apply_n_m_sparsity"):
    self._apply_n_m_sparsity(module, name)
    self._apply_n_m_sparsity(module, name)
    # Apply block pruning
    # Apply block pruning
    else:
    else:
    self._apply_block_pruning(module, name)
    self._apply_block_pruning(module, name)


    def _apply_block_pruning(self, module, name: str) -> None:
    def _apply_block_pruning(self, module, name: str) -> None:
    """
    """
    Apply block pruning to a module.
    Apply block pruning to a module.


    Args:
    Args:
    module: PyTorch module
    module: PyTorch module
    name: Name of the parameter to prune
    name: Name of the parameter to prune
    """
    """
    # Get the weight tensor
    # Get the weight tensor
    weight = getattr(module, name)
    weight = getattr(module, name)


    # Create a mask of the same shape as the weight
    # Create a mask of the same shape as the weight
    mask = torch.ones_like(weight)
    mask = torch.ones_like(weight)


    # Get the block size
    # Get the block size
    block_size = self.config.structured_block_size
    block_size = self.config.structured_block_size


    # Calculate the number of blocks
    # Calculate the number of blocks
    num_blocks_0 = weight.shape[0] // block_size
    num_blocks_0 = weight.shape[0] // block_size
    num_blocks_1 = weight.shape[1] // block_size
    num_blocks_1 = weight.shape[1] // block_size


    # Reshape the weight for block-wise operations
    # Reshape the weight for block-wise operations
    weight_reshaped = weight.reshape(
    weight_reshaped = weight.reshape(
    num_blocks_0, block_size, num_blocks_1, block_size
    num_blocks_0, block_size, num_blocks_1, block_size
    )
    )


    # Calculate the L2 norm of each block
    # Calculate the L2 norm of each block
    block_norms = torch.norm(weight_reshaped, p=2, dim=(1, 3))
    block_norms = torch.norm(weight_reshaped, p=2, dim=(1, 3))


    # Determine the number of blocks to prune
    # Determine the number of blocks to prune
    num_blocks = num_blocks_0 * num_blocks_1
    num_blocks = num_blocks_0 * num_blocks_1
    num_blocks_to_prune = int(num_blocks * self.config.sparsity)
    num_blocks_to_prune = int(num_blocks * self.config.sparsity)


    # Get the indices of the blocks to prune
    # Get the indices of the blocks to prune
    _, indices = torch.topk(
    _, indices = torch.topk(
    block_norms.flatten(), k=num_blocks_to_prune, largest=False
    block_norms.flatten(), k=num_blocks_to_prune, largest=False
    )
    )


    # Convert flat indices to 2D indices
    # Convert flat indices to 2D indices
    indices_0 = indices // num_blocks_1
    indices_0 = indices // num_blocks_1
    indices_1 = indices % num_blocks_1
    indices_1 = indices % num_blocks_1


    # Set the mask for the pruned blocks to zero
    # Set the mask for the pruned blocks to zero
    for i, j in zip(indices_0, indices_1):
    for i, j in zip(indices_0, indices_1):
    mask[
    mask[
    i * block_size : (i + 1) * block_size,
    i * block_size : (i + 1) * block_size,
    j * block_size : (j + 1) * block_size,
    j * block_size : (j + 1) * block_size,
    ] = 0
    ] = 0


    # Apply the mask
    # Apply the mask
    with torch.no_grad():
    with torch.no_grad():
    weight.mul_(mask)
    weight.mul_(mask)


    # Register the mask as a buffer
    # Register the mask as a buffer
    module.register_buffer(f"{name}_mask", mask)
    module.register_buffer(f"{name}_mask", mask)


    def _apply_n_m_sparsity(self, module, name: str) -> None:
    def _apply_n_m_sparsity(self, module, name: str) -> None:
    """
    """
    Apply N:M structured sparsity to a module.
    Apply N:M structured sparsity to a module.


    Args:
    Args:
    module: PyTorch module
    module: PyTorch module
    name: Name of the parameter to prune
    name: Name of the parameter to prune
    """
    """
    # Get the weight tensor
    # Get the weight tensor
    weight = getattr(module, name)
    weight = getattr(module, name)


    # Get the N:M ratio
    # Get the N:M ratio
    n, m = self.config.structured_n_m_ratio
    n, m = self.config.structured_n_m_ratio


    # Create a mask of the same shape as the weight
    # Create a mask of the same shape as the weight
    mask = torch.ones_like(weight)
    mask = torch.ones_like(weight)


    # Apply N:M sparsity along the output dimension
    # Apply N:M sparsity along the output dimension
    for i in range(0, weight.shape[0], m):
    for i in range(0, weight.shape[0], m):
    # Handle the case where the last group might be smaller than m
    # Handle the case where the last group might be smaller than m
    end_idx = min(i + m, weight.shape[0])
    end_idx = min(i + m, weight.shape[0])
    if end_idx - i < m:
    if end_idx - i < m:
    continue
    continue


    # Get the current group
    # Get the current group
    group = weight[i:end_idx, :]
    group = weight[i:end_idx, :]


    # Calculate the L1 norm of each weight
    # Calculate the L1 norm of each weight
    norms = torch.norm(group, p=1, dim=1)
    norms = torch.norm(group, p=1, dim=1)


    # Determine the number of weights to keep
    # Determine the number of weights to keep
    num_to_keep = min(n, end_idx - i)
    num_to_keep = min(n, end_idx - i)


    # Get the indices of the weights to keep
    # Get the indices of the weights to keep
    _, indices = torch.topk(norms, k=num_to_keep, largest=True)
    _, indices = torch.topk(norms, k=num_to_keep, largest=True)


    # Create a mask for this group
    # Create a mask for this group
    group_mask = torch.zeros(end_idx - i)
    group_mask = torch.zeros(end_idx - i)
    group_mask[indices] = 1
    group_mask[indices] = 1


    # Apply the mask to the original mask
    # Apply the mask to the original mask
    mask[i:end_idx, :] = group_mask.unsqueeze(1)
    mask[i:end_idx, :] = group_mask.unsqueeze(1)


    # Apply the mask
    # Apply the mask
    with torch.no_grad():
    with torch.no_grad():
    weight.mul_(mask)
    weight.mul_(mask)


    # Register the mask as a buffer
    # Register the mask as a buffer
    module.register_buffer(f"{name}_mask", mask)
    module.register_buffer(f"{name}_mask", mask)


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
    # Structured pruning supports most model types
    # Structured pruning supports most model types
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
    return [PruningMethod.STRUCTURED]
    return [PruningMethod.STRUCTURED]


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
    "pruner": "StructuredPruner",
    "pruner": "StructuredPruner",
    "method": self.config.method.value,
    "method": self.config.method.value,
    "sparsity": self.config.sparsity,
    "sparsity": self.config.sparsity,
    "block_size": self.config.structured_block_size,
    "block_size": self.config.structured_block_size,
    "n_m_ratio": self.config.structured_n_m_ratio,
    "n_m_ratio": self.config.structured_n_m_ratio,
    }
    }