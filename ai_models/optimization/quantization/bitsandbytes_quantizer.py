"""
"""
BitsAndBytes quantizer for AI models.
BitsAndBytes quantizer for AI models.


This module provides a quantizer that uses the BitsAndBytes library for
This module provides a quantizer that uses the BitsAndBytes library for
4-bit and 8-bit quantization of transformer models.
4-bit and 8-bit quantization of transformer models.
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




    import logging
    import logging
    import os
    import os
    from typing import Any, Dict, List, Optional
    from typing import Any, Dict, List, Optional


    import bitsandbytes
    import bitsandbytes
    import torch
    import torch
    from bitsandbytes.functional import dequantize_4bit, dequantize_8bit
    from bitsandbytes.functional import dequantize_4bit, dequantize_8bit


    from .base import QuantizationConfig, QuantizationMethod, Quantizer
    from .base import QuantizationConfig, QuantizationMethod, Quantizer


    BNB_AVAILABLE
    BNB_AVAILABLE
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
    BitsAndBytesConfig)
    BitsAndBytesConfig)


    TRANSFORMERS_AVAILABLE
    TRANSFORMERS_AVAILABLE
    import json
    import json


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
    logger.warning("PyTorch not available. BitsAndBytes quantizer will not work.")
    logger.warning("PyTorch not available. BitsAndBytes quantizer will not work.")
    TORCH_AVAILABLE = False
    TORCH_AVAILABLE = False


    try:
    try:
    as bnb
    as bnb
    = True
    = True
except ImportError:
except ImportError:
    logger.warning(
    logger.warning(
    "BitsAndBytes not available. Please install it with: pip install bitsandbytes"
    "BitsAndBytes not available. Please install it with: pip install bitsandbytes"
    )
    )
    BNB_AVAILABLE = False
    BNB_AVAILABLE = False


    try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning(
    logger.warning(
    "Transformers not available. BitsAndBytes quantizer will have limited functionality."
    "Transformers not available. BitsAndBytes quantizer will have limited functionality."
    )
    )
    TRANSFORMERS_AVAILABLE = False
    TRANSFORMERS_AVAILABLE = False




    class BitsAndBytesQuantizer(Quantizer):
    class BitsAndBytesQuantizer(Quantizer):
    """
    """
    Quantizer that uses the BitsAndBytes library.
    Quantizer that uses the BitsAndBytes library.
    """
    """


    def __init__(self, config: QuantizationConfig):
    def __init__(self, config: QuantizationConfig):
    """
    """
    Initialize the BitsAndBytes quantizer.
    Initialize the BitsAndBytes quantizer.


    Args:
    Args:
    config: Quantization configuration
    config: Quantization configuration
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


    if not BNB_AVAILABLE:
    if not BNB_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "BitsAndBytes not available. Please install it with: pip install bitsandbytes"
    "BitsAndBytes not available. Please install it with: pip install bitsandbytes"
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


    # Validate configuration
    # Validate configuration
    self._validate_config()
    self._validate_config()


    def _validate_config(self) -> None:
    def _validate_config(self) -> None:
    """
    """
    Validate the quantization configuration.
    Validate the quantization configuration.


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
    f"Unsupported quantization method: {self.config.method}. "
    f"Unsupported quantization method: {self.config.method}. "
    f"Supported methods: {[m.value for m in supported_methods]}"
    f"Supported methods: {[m.value for m in supported_methods]}"
    )
    )


    if self.config.method == QuantizationMethod.BITS_AND_BYTES_4BIT:
    if self.config.method == QuantizationMethod.BITS_AND_BYTES_4BIT:
    if self.config.bnb_4bit_quant_type not in ["nf4", "fp4"]:
    if self.config.bnb_4bit_quant_type not in ["nf4", "fp4"]:
    raise ValueError(
    raise ValueError(
    f"Unsupported 4-bit quantization type: {self.config.bnb_4bit_quant_type}. "
    f"Unsupported 4-bit quantization type: {self.config.bnb_4bit_quant_type}. "
    "Supported types: nf4, fp4"
    "Supported types: nf4, fp4"
    )
    )


    def quantize(
    def quantize(
    self, model_path: str, output_path: Optional[str] = None, **kwargs
    self, model_path: str, output_path: Optional[str] = None, **kwargs
    ) -> str:
    ) -> str:
    """
    """
    Quantize a model using BitsAndBytes.
    Quantize a model using BitsAndBytes.


    Args:
    Args:
    model_path: Path to the model
    model_path: Path to the model
    output_path: Path to save the quantized model (None for in-place)
    output_path: Path to save the quantized model (None for in-place)
    **kwargs: Additional parameters for quantization
    **kwargs: Additional parameters for quantization


    Returns:
    Returns:
    Path to the quantized model
    Path to the quantized model
    """
    """
    logger.info(f"Quantizing model {model_path} with BitsAndBytes")
    logger.info(f"Quantizing model {model_path} with BitsAndBytes")


    # Determine output path
    # Determine output path
    if output_path is None:
    if output_path is None:
    output_path = model_path
    output_path = model_path


    # Create BitsAndBytes configuration
    # Create BitsAndBytes configuration
    bnb_config = self._create_bnb_config()
    bnb_config = self._create_bnb_config()


    # Load tokenizer
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)


    # Load model with quantization
    # Load model with quantization
    model = AutoModelForCausalLM.from_pretrained(
    model = AutoModelForCausalLM.from_pretrained(
    model_path, quantization_config=bnb_config, device_map="auto", **kwargs
    model_path, quantization_config=bnb_config, device_map="auto", **kwargs
    )
    )


    # Save model and tokenizer
    # Save model and tokenizer
    logger.info(f"Saving quantized model to {output_path}")
    logger.info(f"Saving quantized model to {output_path}")
    model.save_pretrained(output_path)
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)


    # Save quantization configuration
    # Save quantization configuration
    self._save_quantization_config(output_path)
    self._save_quantization_config(output_path)


    return output_path
    return output_path


    def _create_bnb_config(self) -> BitsAndBytesConfig:
    def _create_bnb_config(self) -> BitsAndBytesConfig:
    """
    """
    Create a BitsAndBytes configuration.
    Create a BitsAndBytes configuration.


    Returns:
    Returns:
    BitsAndBytes configuration
    BitsAndBytes configuration
    """
    """
    if self.config.method == QuantizationMethod.BITS_AND_BYTES_4BIT:
    if self.config.method == QuantizationMethod.BITS_AND_BYTES_4BIT:
    return BitsAndBytesConfig(
    return BitsAndBytesConfig(
    load_in_4bit=True,
    load_in_4bit=True,
    bnb_4bit_quant_type=self.config.bnb_4bit_quant_type,
    bnb_4bit_quant_type=self.config.bnb_4bit_quant_type,
    bnb_4bit_use_double_quant=self.config.bnb_4bit_use_double_quant,
    bnb_4bit_use_double_quant=self.config.bnb_4bit_use_double_quant,
    bnb_4bit_compute_dtype=getattr(
    bnb_4bit_compute_dtype=getattr(
    torch, self.config.bnb_4bit_compute_dtype
    torch, self.config.bnb_4bit_compute_dtype
    ),
    ),
    )
    )
    elif self.config.method == QuantizationMethod.BITS_AND_BYTES_8BIT:
    elif self.config.method == QuantizationMethod.BITS_AND_BYTES_8BIT:
    return BitsAndBytesConfig(
    return BitsAndBytesConfig(
    load_in_8bit=True, llm_int8_enable_fp32_cpu_offload=True
    load_in_8bit=True, llm_int8_enable_fp32_cpu_offload=True
    )
    )
    else:
    else:
    raise ValueError(f"Unsupported quantization method: {self.config.method}")
    raise ValueError(f"Unsupported quantization method: {self.config.method}")


    def _save_quantization_config(self, output_path: str) -> None:
    def _save_quantization_config(self, output_path: str) -> None:
    """
    """
    Save the quantization configuration.
    Save the quantization configuration.


    Args:
    Args:
    output_path: Path to save the configuration
    output_path: Path to save the configuration
    """
    """




    config_path = os.path.join(output_path, "quantization_config.json")
    config_path = os.path.join(output_path, "quantization_config.json")


    with open(config_path, "w", encoding="utf-8") as f:
    with open(config_path, "w", encoding="utf-8") as f:
    json.dump(self.config.to_dict(), f, indent=2)
    json.dump(self.config.to_dict(), f, indent=2)


    def supports_model_type(self, model_type: str) -> bool:
    def supports_model_type(self, model_type: str) -> bool:
    """
    """
    Check if the quantizer supports a model type.
    Check if the quantizer supports a model type.


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
    # BitsAndBytes supports most transformer models
    # BitsAndBytes supports most transformer models
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
    ]
    ]


    return model_type in supported_types
    return model_type in supported_types


    def get_supported_methods(self) -> List[QuantizationMethod]:
    def get_supported_methods(self) -> List[QuantizationMethod]:
    """
    """
    Get the quantization methods supported by the quantizer.
    Get the quantization methods supported by the quantizer.


    Returns:
    Returns:
    List of supported quantization methods
    List of supported quantization methods
    """
    """
    return [
    return [
    QuantizationMethod.BITS_AND_BYTES_4BIT,
    QuantizationMethod.BITS_AND_BYTES_4BIT,
    QuantizationMethod.BITS_AND_BYTES_8BIT,
    QuantizationMethod.BITS_AND_BYTES_8BIT,
    ]
    ]


    def get_quantization_info(self) -> Dict[str, Any]:
    def get_quantization_info(self) -> Dict[str, Any]:
    """
    """
    Get information about the quantization.
    Get information about the quantization.


    Returns:
    Returns:
    Dictionary with quantization information
    Dictionary with quantization information
    """
    """
    info = {
    info = {
    "quantizer": "BitsAndBytes",
    "quantizer": "BitsAndBytes",
    "method": self.config.method.value,
    "method": self.config.method.value,
    "bits": (
    "bits": (
    4 if self.config.method == QuantizationMethod.BITS_AND_BYTES_4BIT else 8
    4 if self.config.method == QuantizationMethod.BITS_AND_BYTES_4BIT else 8
    ),
    ),
    }
    }


    if self.config.method == QuantizationMethod.BITS_AND_BYTES_4BIT:
    if self.config.method == QuantizationMethod.BITS_AND_BYTES_4BIT:
    info.update(
    info.update(
    {
    {
    "quant_type": self.config.bnb_4bit_quant_type,
    "quant_type": self.config.bnb_4bit_quant_type,
    "use_double_quant": self.config.bnb_4bit_use_double_quant,
    "use_double_quant": self.config.bnb_4bit_use_double_quant,
    "compute_dtype": self.config.bnb_4bit_compute_dtype,
    "compute_dtype": self.config.bnb_4bit_compute_dtype,
    }
    }
    )
    )


    return info
    return info