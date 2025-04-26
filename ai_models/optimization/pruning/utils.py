"""
Utility functions for model pruning.

This module provides utility functions for pruning models and analyzing
the effects of pruning.
"""

import os
import logging
import time
import json
from typing import Dict, Any, Optional, List, Union, Type, Tuple

import numpy as np

from .base import Pruner, PruningConfig, PruningMethod
from .magnitude_pruner import MagnitudePruner
from .structured_pruner import StructuredPruner

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available. Some pruning utilities will not work.")
    TORCH_AVAILABLE = False

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Transformers not available. Some pruning utilities will have limited functionality.")
    TRANSFORMERS_AVAILABLE = False


def prune_model(
    model_path: str,
    output_path: Optional[str] = None,
    method: Union[str, PruningMethod] = PruningMethod.MAGNITUDE,
    sparsity: float = 0.5,
    model_type: str = "text-generation",
    **kwargs
) -> str:
    """
    Prune a model using the specified method.
    
    Args:
        model_path: Path to the model
        output_path: Path to save the pruned model (None for in-place)
        method: Pruning method
        sparsity: Target sparsity (0.0 to 1.0)
        model_type: Type of the model
        **kwargs: Additional parameters for pruning
        
    Returns:
        Path to the pruned model
    """
    # Convert method to PruningMethod if it's a string
    if isinstance(method, str):
        try:
            method = PruningMethod(method)
        except ValueError:
            raise ValueError(f"Unknown pruning method: {method}")
    
    # Create pruning configuration
    config = PruningConfig(
        method=method,
        sparsity=sparsity,
        **kwargs
    )
    
    # Create pruner based on method
    if method == PruningMethod.MAGNITUDE:
        pruner = MagnitudePruner(config)
    elif method == PruningMethod.STRUCTURED:
        pruner = StructuredPruner(config)
    else:
        raise ValueError(f"Unsupported pruning method: {method}")
    
    # Check if the pruner supports the model type
    if not pruner.supports_model_type(model_type):
        raise ValueError(f"Model type {model_type} is not supported by the {method.value} pruner")
    
    # Prune the model
    return pruner.prune(model_path, output_path)


def analyze_pruning(
    original_model_path: str,
    pruned_model_path: str,
    input_text: Optional[str] = None,
    num_samples: int = 5,
    max_tokens: int = 100,
    **kwargs
) -> Dict[str, Any]:
    """
    Analyze the effects of pruning on a model.
    
    Args:
        original_model_path: Path to the original model
        pruned_model_path: Path to the pruned model
        input_text: Input text for generation (None for random prompts)
        num_samples: Number of samples to generate
        max_tokens: Maximum number of tokens to generate
        **kwargs: Additional parameters for generation
        
    Returns:
        Dictionary with analysis results
    """
    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
        raise ImportError("PyTorch and Transformers are required for pruning analysis")
    
    logger.info("Analyzing pruning effects")
    
    # Load original model and tokenizer
    logger.info(f"Loading original model from {original_model_path}")
    original_tokenizer = AutoTokenizer.from_pretrained(original_model_path)
    original_model = AutoModelForCausalLM.from_pretrained(
        original_model_path,
        device_map="auto"
    )
    
    # Load pruned model and tokenizer
    logger.info(f"Loading pruned model from {pruned_model_path}")
    pruned_tokenizer = AutoTokenizer.from_pretrained(pruned_model_path)
    pruned_model = AutoModelForCausalLM.from_pretrained(
        pruned_model_path,
        device_map="auto"
    )
    
    # Generate input prompts
    if input_text:
        prompts = [input_text] * num_samples
    else:
        # Use default prompts
        prompts = [
            "Once upon a time in a land far away,",
            "The quick brown fox jumps over the lazy dog.",
            "In a shocking turn of events, scientists discovered that",
            "The best way to learn a new programming language is to",
            "If I could travel anywhere in the world, I would go to"
        ]
        
        # Limit to num_samples
        prompts = prompts[:num_samples]
        
        # Duplicate if needed
        while len(prompts) < num_samples:
            prompts.append(prompts[len(prompts) % len(prompts)])
    
    # Analyze model size and sparsity
    original_size = _get_model_size(original_model)
    pruned_size = _get_model_size(pruned_model)
    original_sparsity = _calculate_model_sparsity(original_model)
    pruned_sparsity = _calculate_model_sparsity(pruned_model)
    
    # Analyze generation speed and quality
    original_times = []
    pruned_times = []
    original_outputs = []
    pruned_outputs = []
    
    for prompt in prompts:
        # Generate with original model
        start_time = time.time()
        original_output = _generate_text(original_model, original_tokenizer, prompt, max_tokens, **kwargs)
        original_time = time.time() - start_time
        
        original_times.append(original_time)
        original_outputs.append(original_output)
        
        # Generate with pruned model
        start_time = time.time()
        pruned_output = _generate_text(pruned_model, pruned_tokenizer, prompt, max_tokens, **kwargs)
        pruned_time = time.time() - start_time
        
        pruned_times.append(pruned_time)
        pruned_outputs.append(pruned_output)
    
    # Calculate metrics
    size_reduction = 1.0 - (pruned_size / original_size)
    speed_improvement = np.mean(original_times) / np.mean(pruned_times)
    sparsity_increase = pruned_sparsity - original_sparsity
    
    # Calculate output similarity
    similarities = []
    for orig, pruned in zip(original_outputs, pruned_outputs):
        similarity = _calculate_text_similarity(orig, pruned)
        similarities.append(similarity)
    
    avg_similarity = np.mean(similarities)
    
    # Create analysis results
    results = {
        "original_model": {
            "path": original_model_path,
            "size_mb": original_size,
            "sparsity": original_sparsity,
            "avg_generation_time": np.mean(original_times),
            "outputs": original_outputs
        },
        "pruned_model": {
            "path": pruned_model_path,
            "size_mb": pruned_size,
            "sparsity": pruned_sparsity,
            "avg_generation_time": np.mean(pruned_times),
            "outputs": pruned_outputs
        },
        "comparison": {
            "size_reduction": size_reduction,
            "size_reduction_percent": size_reduction * 100,
            "speed_improvement": speed_improvement,
            "speed_improvement_percent": (speed_improvement - 1) * 100,
            "sparsity_increase": sparsity_increase,
            "sparsity_increase_percent": sparsity_increase * 100,
            "output_similarity": avg_similarity,
            "individual_similarities": similarities
        },
        "prompts": prompts
    }
    
    # Try to get pruning info
    try:
        pruning_config_path = os.path.join(pruned_model_path, "pruning_config.json")
        if os.path.exists(pruning_config_path):
            with open(pruning_config_path, "r", encoding="utf-8") as f:
                pruning_config = json.load(f)
            
            results["pruning_config"] = pruning_config
    except Exception as e:
        logger.warning(f"Error loading pruning config: {e}")
    
    return results


def _get_model_size(model) -> float:
    """
    Get the size of a model in megabytes.
    
    Args:
        model: PyTorch model
        
    Returns:
        Size in megabytes
    """
    param_size = 0
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    
    buffer_size = 0
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()
    
    size_mb = (param_size + buffer_size) / (1024 * 1024)
    return size_mb


def _calculate_model_sparsity(model) -> float:
    """
    Calculate the sparsity of a model.
    
    Args:
        model: PyTorch model
        
    Returns:
        Sparsity (0.0 to 1.0)
    """
    total_params = 0
    zero_params = 0
    
    for param in model.parameters():
        if param.dim() > 1:  # Only consider weight matrices, not biases
            total_params += param.numel()
            zero_params += (param == 0).sum().item()
    
    if total_params == 0:
        return 0.0
    
    return zero_params / total_params


def _generate_text(model, tokenizer, prompt: str, max_tokens: int, **kwargs) -> str:
    """
    Generate text using a model.
    
    Args:
        model: PyTorch model
        tokenizer: Tokenizer
        prompt: Input prompt
        max_tokens: Maximum number of tokens to generate
        **kwargs: Additional parameters for generation
        
    Returns:
        Generated text
    """
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Set default generation parameters
    generation_kwargs = {
        "max_new_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True
    }
    
    # Update with user-provided parameters
    generation_kwargs.update(kwargs)
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(**inputs, **generation_kwargs)
    
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def _calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-1)
    """
    # Simple character-level Jaccard similarity
    set1 = set(text1)
    set2 = set(text2)
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    if union == 0:
        return 0.0
    
    return intersection / union
