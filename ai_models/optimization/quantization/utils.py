"""
Utility functions for model quantization.

This module provides utility functions for quantizing models and analyzing
the effects of quantization.
"""

import os
import logging
import time
import json
from typing import Dict, Any, Optional, List, Union, Type, Tuple

import numpy as np

from .base import Quantizer, QuantizationConfig, QuantizationMethod
from .bitsandbytes_quantizer import BitsAndBytesQuantizer
from .awq_quantizer import AWQQuantizer
from .gptq_quantizer import GPTQQuantizer

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
    logger.warning("PyTorch not available. Some quantization utilities will not work.")
    TORCH_AVAILABLE = False

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Transformers not available. Some quantization utilities will have limited functionality.")
    TRANSFORMERS_AVAILABLE = False


def quantize_model(
    model_path: str,
    output_path: Optional[str] = None,
    method: Union[str, QuantizationMethod] = QuantizationMethod.BITS_AND_BYTES_4BIT,
    bits: int = 4,
    model_type: str = "text-generation",
    **kwargs
) -> str:
    """
    Quantize a model using the specified method.
    
    Args:
        model_path: Path to the model
        output_path: Path to save the quantized model (None for in-place)
        method: Quantization method
        bits: Number of bits for quantization
        model_type: Type of the model
        **kwargs: Additional parameters for quantization
        
    Returns:
        Path to the quantized model
    """
    # Convert method to QuantizationMethod if it's a string
    if isinstance(method, str):
        try:
            method = QuantizationMethod(method)
        except ValueError:
            raise ValueError(f"Unknown quantization method: {method}")
    
    # Create quantization configuration
    config = QuantizationConfig(
        method=method,
        bits=bits,
        **kwargs
    )
    
    # Create quantizer based on method
    if method in [QuantizationMethod.BITS_AND_BYTES_4BIT, QuantizationMethod.BITS_AND_BYTES_8BIT]:
        quantizer = BitsAndBytesQuantizer(config)
    elif method == QuantizationMethod.AWQ:
        quantizer = AWQQuantizer(config)
    elif method == QuantizationMethod.GPTQ:
        quantizer = GPTQQuantizer(config)
    else:
        raise ValueError(f"Unsupported quantization method: {method}")
    
    # Check if the quantizer supports the model type
    if not quantizer.supports_model_type(model_type):
        raise ValueError(f"Model type {model_type} is not supported by the {method.value} quantizer")
    
    # Quantize the model
    return quantizer.quantize(model_path, output_path)


def analyze_quantization(
    original_model_path: str,
    quantized_model_path: str,
    input_text: Optional[str] = None,
    num_samples: int = 5,
    max_tokens: int = 100,
    **kwargs
) -> Dict[str, Any]:
    """
    Analyze the effects of quantization on a model.
    
    Args:
        original_model_path: Path to the original model
        quantized_model_path: Path to the quantized model
        input_text: Input text for generation (None for random prompts)
        num_samples: Number of samples to generate
        max_tokens: Maximum number of tokens to generate
        **kwargs: Additional parameters for generation
        
    Returns:
        Dictionary with analysis results
    """
    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
        raise ImportError("PyTorch and Transformers are required for quantization analysis")
    
    logger.info("Analyzing quantization effects")
    
    # Load original model and tokenizer
    logger.info(f"Loading original model from {original_model_path}")
    original_tokenizer = AutoTokenizer.from_pretrained(original_model_path)
    original_model = AutoModelForCausalLM.from_pretrained(
        original_model_path,
        device_map="auto"
    )
    
    # Load quantized model and tokenizer
    logger.info(f"Loading quantized model from {quantized_model_path}")
    quantized_tokenizer = AutoTokenizer.from_pretrained(quantized_model_path)
    
    # Check if quantization config exists
    quant_config_path = os.path.join(quantized_model_path, "quantization_config.json")
    if os.path.exists(quant_config_path):
        with open(quant_config_path, "r", encoding="utf-8") as f:
            quant_config_dict = json.load(f)
        
        quant_config = QuantizationConfig.from_dict(quant_config_dict)
        
        # Load model with appropriate configuration
        if quant_config.method == QuantizationMethod.BITS_AND_BYTES_4BIT:
            from transformers import BitsAndBytesConfig
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type=quant_config.bnb_4bit_quant_type,
                bnb_4bit_use_double_quant=quant_config.bnb_4bit_use_double_quant,
                bnb_4bit_compute_dtype=getattr(torch, quant_config.bnb_4bit_compute_dtype)
            )
            
            quantized_model = AutoModelForCausalLM.from_pretrained(
                quantized_model_path,
                quantization_config=quantization_config,
                device_map="auto"
            )
        
        elif quant_config.method == QuantizationMethod.BITS_AND_BYTES_8BIT:
            from transformers import BitsAndBytesConfig
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_enable_fp32_cpu_offload=True
            )
            
            quantized_model = AutoModelForCausalLM.from_pretrained(
                quantized_model_path,
                quantization_config=quantization_config,
                device_map="auto"
            )
        
        elif quant_config.method == QuantizationMethod.AWQ:
            from auto_awq import AutoAWQForCausalLM
            quantized_model = AutoAWQForCausalLM.from_quantized(
                quantized_model_path,
                device_map="auto"
            )
        
        elif quant_config.method == QuantizationMethod.GPTQ:
            from auto_gptq import AutoGPTQForCausalLM
            quantized_model = AutoGPTQForCausalLM.from_quantized(
                quantized_model_path,
                device_map="auto"
            )
        
        else:
            # Default loading
            quantized_model = AutoModelForCausalLM.from_pretrained(
                quantized_model_path,
                device_map="auto"
            )
    
    else:
        # Default loading
        quantized_model = AutoModelForCausalLM.from_pretrained(
            quantized_model_path,
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
    
    # Analyze model size
    original_size = _get_model_size(original_model)
    quantized_size = _get_model_size(quantized_model)
    
    # Analyze generation speed and quality
    original_times = []
    quantized_times = []
    original_outputs = []
    quantized_outputs = []
    
    for prompt in prompts:
        # Generate with original model
        start_time = time.time()
        original_output = _generate_text(original_model, original_tokenizer, prompt, max_tokens, **kwargs)
        original_time = time.time() - start_time
        
        original_times.append(original_time)
        original_outputs.append(original_output)
        
        # Generate with quantized model
        start_time = time.time()
        quantized_output = _generate_text(quantized_model, quantized_tokenizer, prompt, max_tokens, **kwargs)
        quantized_time = time.time() - start_time
        
        quantized_times.append(quantized_time)
        quantized_outputs.append(quantized_output)
    
    # Calculate metrics
    size_reduction = 1.0 - (quantized_size / original_size)
    speed_improvement = np.mean(original_times) / np.mean(quantized_times)
    
    # Calculate output similarity
    similarities = []
    for orig, quant in zip(original_outputs, quantized_outputs):
        similarity = _calculate_text_similarity(orig, quant)
        similarities.append(similarity)
    
    avg_similarity = np.mean(similarities)
    
    # Create analysis results
    results = {
        "original_model": {
            "path": original_model_path,
            "size_mb": original_size,
            "avg_generation_time": np.mean(original_times),
            "outputs": original_outputs
        },
        "quantized_model": {
            "path": quantized_model_path,
            "size_mb": quantized_size,
            "avg_generation_time": np.mean(quantized_times),
            "outputs": quantized_outputs
        },
        "comparison": {
            "size_reduction": size_reduction,
            "size_reduction_percent": size_reduction * 100,
            "speed_improvement": speed_improvement,
            "speed_improvement_percent": (speed_improvement - 1) * 100,
            "output_similarity": avg_similarity,
            "individual_similarities": similarities
        },
        "prompts": prompts
    }
    
    # Try to get quantization info
    try:
        quant_config_path = os.path.join(quantized_model_path, "quantization_config.json")
        if os.path.exists(quant_config_path):
            with open(quant_config_path, "r", encoding="utf-8") as f:
                quant_config = json.load(f)
            
            results["quantization_config"] = quant_config
    except Exception as e:
        logger.warning(f"Error loading quantization config: {e}")
    
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
