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
    
    This function performs a comprehensive analysis to quantify how model pruning 
    affects key performance metrics. The analysis consists of several stages:
    
    1. Model loading: Both original and pruned models are loaded
    2. Size analysis: Compare file size and memory footprint
    3. Sparsity calculation: Measure the percentage of zero weights in each model
    4. Inference speed measurement: Time the generation of text for both models
    5. Output quality comparison: Calculate similarity between outputs of both models
    
    The comprehensive report enables data-driven decisions about pruning parameters
    by quantifying the tradeoffs between model size, inference speed, and output quality.
    
    Args:
        original_model_path: Path to the original model
        pruned_model_path: Path to the pruned model
        input_text: Input text for generation (None for random prompts)
        num_samples: Number of samples to generate
        max_tokens: Maximum number of tokens to generate
        **kwargs: Additional parameters for generation
        
    Returns:
        Dictionary with analysis results containing:
        - Original and pruned model statistics
        - Comparison metrics (size reduction, speed improvement, etc.)
        - Actual outputs for comparison
    """
    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
        raise ImportError("PyTorch and Transformers are required for pruning analysis")
    
    logger.info("Analyzing pruning effects")
    
    # Load original model and tokenizer
    logger.info(f"Loading original model from {original_model_path}")
    original_tokenizer = AutoTokenizer.from_pretrained(original_model_path)
    original_model = AutoModelForCausalLM.from_pretrained(
        original_model_path,
        device_map="auto"  # Automatically use best available device (CPU/GPU)
    )
    
    # Load pruned model and tokenizer
    logger.info(f"Loading pruned model from {pruned_model_path}")
    pruned_tokenizer = AutoTokenizer.from_pretrained(pruned_model_path)
    pruned_model = AutoModelForCausalLM.from_pretrained(
        pruned_model_path,
        device_map="auto"  # Automatically use best available device (CPU/GPU)
    )
    
    # Generate input prompts for testing model generation
    # Either use the provided input text or default test prompts
    if input_text:
        # Use the same input text for all samples to reduce variance
        prompts = [input_text] * num_samples
    else:
        # Use a diverse set of default prompts to test different aspects
        # of language generation (stories, facts, opinions, etc.)
        prompts = [
            "Once upon a time in a land far away,",
            "The quick brown fox jumps over the lazy dog.",
            "In a shocking turn of events, scientists discovered that",
            "The best way to learn a new programming language is to",
            "If I could travel anywhere in the world, I would go to"
        ]
        
        # Limit to num_samples
        prompts = prompts[:num_samples]
        
        # If we have fewer default prompts than requested samples,
        # duplicate prompts to reach the required number
        while len(prompts) < num_samples:
            prompts.append(prompts[len(prompts) % len(prompts)])
    
    # STAGE 1: Analyze model size and sparsity
    # This quantifies the memory/storage benefit of pruning
    original_size = _get_model_size(original_model)
    pruned_size = _get_model_size(pruned_model)
    original_sparsity = _calculate_model_sparsity(original_model)
    pruned_sparsity = _calculate_model_sparsity(pruned_model)
    
    # STAGE 2: Analyze generation speed and output quality
    # This measures the performance impact and output quality changes
    original_times = []
    pruned_times = []
    original_outputs = []
    pruned_outputs = []
    
    for prompt in prompts:
        # Generate text with original model and measure time
        start_time = time.time()
        original_output = _generate_text(original_model, original_tokenizer, prompt, max_tokens, **kwargs)
        original_time = time.time() - start_time
        
        original_times.append(original_time)
        original_outputs.append(original_output)
        
        # Generate text with pruned model and measure time
        start_time = time.time()
        pruned_output = _generate_text(pruned_model, pruned_tokenizer, prompt, max_tokens, **kwargs)
        pruned_time = time.time() - start_time
        
        pruned_times.append(pruned_time)
        pruned_outputs.append(pruned_output)
    
    # STAGE 3: Calculate comparison metrics
    # These derived metrics provide a clear picture of the pruning impact
    
    # Size reduction as a ratio and percentage
    size_reduction = 1.0 - (pruned_size / original_size)
    
    # Speed improvement as a ratio (>1.0 means faster)
    # Using mean times to get a stable measurement across samples
    speed_improvement = np.mean(original_times) / np.mean(pruned_times)
    
    # Sparsity increase (percentage points of additional zeros)
    sparsity_increase = pruned_sparsity - original_sparsity
    
    # STAGE 4: Calculate output similarity to measure quality degradation
    # Higher similarity indicates less quality degradation from pruning
    similarities = []
    for orig, pruned in zip(original_outputs, pruned_outputs):
        similarity = _calculate_text_similarity(orig, pruned)
        similarities.append(similarity)
    
    avg_similarity = np.mean(similarities)
    
    # STAGE 5: Compile comprehensive analysis results
    # Structure the data for easy interpretation and visualization
    results = {
        # Original model statistics
        "original_model": {
            "path": original_model_path,
            "size_mb": original_size,
            "sparsity": original_sparsity,
            "avg_generation_time": np.mean(original_times),
            "outputs": original_outputs
        },
        # Pruned model statistics
        "pruned_model": {
            "path": pruned_model_path,
            "size_mb": pruned_size,
            "sparsity": pruned_sparsity,
            "avg_generation_time": np.mean(pruned_times),
            "outputs": pruned_outputs
        },
        # Key comparison metrics
        "comparison": {
            "size_reduction": size_reduction,
            "size_reduction_percent": size_reduction * 100,  # More intuitive percentage
            "speed_improvement": speed_improvement,
            "speed_improvement_percent": (speed_improvement - 1) * 100,  # Percentage speedup
            "sparsity_increase": sparsity_increase,
            "sparsity_increase_percent": sparsity_increase * 100,  # Percentage point increase
            "output_similarity": avg_similarity,
            "individual_similarities": similarities  # For detailed analysis
        },
        # Preserve input data for reference
        "prompts": prompts
    }
    
    # Add pruning configuration if available
    # This helps track which pruning settings were used
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
    
    This function calculates the in-memory size of a PyTorch model by:
    1. Summing the size of all parameters (weights and biases)
    2. Summing the size of all buffers (e.g., running stats in batch norm)
    3. Converting the total size to megabytes
    
    The calculation accounts for both the number of elements and their data type sizes,
    providing an accurate measure of the model's memory footprint.
    
    Args:
        model: PyTorch model
        
    Returns:
        Size in megabytes
    """
    # Calculate size of all parameters (weights and biases)
    param_size = 0
    for param in model.parameters():
        # Number of elements * bytes per element
        param_size += param.nelement() * param.element_size()
    
    # Calculate size of all buffers (running stats, etc.)
    buffer_size = 0
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()
    
    # Convert to megabytes
    size_mb = (param_size + buffer_size) / (1024 * 1024)
    return size_mb


def _calculate_model_sparsity(model) -> float:
    """
    Calculate the sparsity of a model.
    
    Sparsity is the proportion of zero-valued parameters in a model's weight matrices.
    Higher sparsity generally means better compression potential and faster inference
    on hardware that supports sparse operations.
    
    This function:
    1. Counts the total number of parameters in weight matrices (excluding biases)
    2. Counts how many of those parameters are exactly zero
    3. Calculates the ratio of zero parameters to total parameters
    
    Only weight matrices (dim > 1) are considered because:
    - Biases are typically not pruned as they represent a small fraction of parameters
    - Pruning biases can disproportionately affect model quality
    
    Args:
        model: PyTorch model
        
    Returns:
        Sparsity as a float between 0.0 (dense) and 1.0 (completely sparse)
    """
    total_params = 0
    zero_params = 0
    
    for param in model.parameters():
        if param.dim() > 1:  # Only consider weight matrices, not biases
            total_params += param.numel()  # Total number of elements
            zero_params += (param == 0).sum().item()  # Count zeros
    
    if total_params == 0:
        return 0.0  # Avoid division by zero
    
    return zero_params / total_params  # Sparsity ratio


def _generate_text(model, tokenizer, prompt: str, max_tokens: int, **kwargs) -> str:
    """
    Generate text using a model.
    
    This function handles the text generation process with a given language model:
    1. Tokenize the input prompt and move to the appropriate device
    2. Set up generation parameters with smart defaults
    3. Generate text without computing gradients (for efficiency)
    4. Decode the generated token IDs back to text
    
    The generation is done with torch.no_grad() to:
    - Improve inference speed
    - Reduce memory usage
    - Prevent accidental gradient accumulation
    
    Args:
        model: PyTorch model
        tokenizer: Tokenizer
        prompt: Input prompt
        max_tokens: Maximum number of tokens to generate
        **kwargs: Additional parameters for generation
        
    Returns:
        Generated text as a string
    """
    # Tokenize input and move to model's device (CPU/GPU)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Set default generation parameters for reasonable output
    generation_kwargs = {
        "max_new_tokens": max_tokens,  # Control length of generated text
        "temperature": 0.7,            # Control randomness (higher = more random)
        "top_p": 0.9,                  # Nucleus sampling parameter
        "do_sample": True              # Use sampling instead of greedy decoding
    }
    
    # Override defaults with any user-provided parameters
    generation_kwargs.update(kwargs)
    
    # Generate text without computing gradients (for efficiency)
    with torch.no_grad():
        outputs = model.generate(**inputs, **generation_kwargs)
    
    # Decode the generated token IDs back to text and return
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def _calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts.
    
    This function implements a character-level Jaccard similarity metric:
    - Fast and language-agnostic
    - Works for comparing texts of different lengths
    - Provides a normalized score between 0 (completely different) and 1 (identical)
    
    The Jaccard similarity is defined as the size of the intersection 
    divided by the size of the union of the character sets. This method provides a
    reasonable approximation of text similarity for the purpose of comparing
    model outputs.
    
    For more sophisticated comparisons, consider using:
    - BLEU or ROUGE scores for specific NLP tasks
    - Embedding-based similarity for semantic comparison
    - Edit distance for character-level differences
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0.0 (completely different) and 1.0 (identical)
    """
    # Convert texts to sets of characters for Jaccard similarity
    set1 = set(text1)
    set2 = set(text2)
    
    # Calculate intersection (characters in both texts)
    intersection = len(set1.intersection(set2))
    
    # Calculate union (unique characters across both texts)
    union = len(set1.union(set2))
    
    # Handle edge case of empty texts
    if union == 0:
        return 0.0
    
    # Jaccard similarity = intersection size / union size
    return intersection / union
