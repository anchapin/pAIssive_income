"""
AWQ (Activation-aware Weight Quantization) quantizer for AI models.

This module provides a quantizer that uses the AWQ method for
quantizing transformer models.
"""

try:
    import torch
except ImportError:
    pass


    import logging
    import os
    from typing import Any, Dict, List, Optional

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from .base import QuantizationConfig, QuantizationMethod, Quantizer

    TRANSFORMERS_AVAILABLE
    import awq
    from awq import AutoAWQForCausalLM

    AWQ_AVAILABLE
    from datasets import load_dataset

    calibration_dataset
    import json

    # Set up logging
    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Try to import optional dependencies
    try:


    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available. AWQ quantizer will not work.")
    TORCH_AVAILABLE = False

    try:
    = True
except ImportError:
    logger.warning(
    "Transformers not available. AWQ quantizer will have limited functionality."
    )
    TRANSFORMERS_AVAILABLE = False

    # Check if AWQ is available
    try:

    = True
except ImportError:
    logger.warning("AWQ not available. Please install it with: pip install autoawq")
    AWQ_AVAILABLE = False


    class AWQQuantizer(Quantizer):
    """
    Quantizer that uses the AWQ method.
    """

    def __init__(self, config: QuantizationConfig):
    """
    Initialize the AWQ quantizer.

    Args:
    config: Quantization configuration
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

    if not AWQ_AVAILABLE:
    raise ImportError(
    "AWQ not available. Please install it with: pip install autoawq"
    )

    # Validate configuration
    self._validate_config()

    def _validate_config(self) -> None:
    """
    Validate the quantization configuration.

    Raises:
    ValueError: If the configuration is invalid
    """
    supported_methods = self.get_supported_methods()
    if self.config.method not in supported_methods:
    raise ValueError(
    f"Unsupported quantization method: {self.config.method}. "
    f"Supported methods: {[m.value for m in supported_methods]}"
    )

    if self.config.bits not in [4, 8]:
    raise ValueError(
    f"Unsupported bits: {self.config.bits}. " "Supported bits: 4, 8"
    )

    def quantize(
    self, model_path: str, output_path: Optional[str] = None, **kwargs
    ) -> str:
    """
    Quantize a model using AWQ.

    Args:
    model_path: Path to the model
    output_path: Path to save the quantized model (None for in-place)
    **kwargs: Additional parameters for quantization

    Returns:
    Path to the quantized model
    """
    logger.info(f"Quantizing model {model_path} with AWQ")

    # Determine output path
    if output_path is None:
    output_path = model_path

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # Create AWQ model
    awq_model = AutoAWQForCausalLM.from_pretrained(model_path)

    # Get calibration dataset
    if self.config.calibration_dataset:
    # Use provided dataset
    calibration_dataset = self.config.calibration_dataset
    else:
    # Use default dataset (WikiText-2)
    = load_dataset(
    "wikitext", "wikitext-2-raw-v1", split="train"
    )

    # Process dataset
    def preprocess_function(examples):
    return tokenizer("\n\n".join(examples["text"]))

    calibration_dataset = calibration_dataset.map(
    preprocess_function, batched=True, remove_columns=["text"]
    )

    # Quantize model
    awq_model.quantize(
    tokenizer=tokenizer,
    quant_config={
    "zero_point": self.config.awq_zero_point,
    "q_group_size": self.config.awq_group_size,
    "w_bit": self.config.bits,
    "version": "GEMM",
    },
    calib_data=calibration_dataset,
    calib_n_samples=self.config.calibration_num_samples,
    calib_seqlen=self.config.calibration_seqlen,
    )

    # Save model and tokenizer
    logger.info(f"Saving quantized model to {output_path}")
    awq_model.save_quantized(output_path)
    tokenizer.save_pretrained(output_path)

    # Save quantization configuration
    self._save_quantization_config(output_path)

    # Export to ONNX if requested
    if self.config.awq_export_to_onnx:
    onnx_path = os.path.join(output_path, "model.onnx")
    logger.info(f"Exporting model to ONNX: {onnx_path}")

    try:
    awq_model.export_to_onnx(onnx_path)
except Exception as e:
    logger.error(f"Error exporting model to ONNX: {e}")

    return output_path

    def _save_quantization_config(self, output_path: str) -> None:
    """
    Save the quantization configuration.

    Args:
    output_path: Path to save the configuration
    """


    config_path = os.path.join(output_path, "quantization_config.json")

    with open(config_path, "w", encoding="utf-8") as f:
    json.dump(self.config.to_dict(), f, indent=2)

    def supports_model_type(self, model_type: str) -> bool:
    """
    Check if the quantizer supports a model type.

    Args:
    model_type: Type of the model

    Returns:
    True if the model type is supported, False otherwise
    """
    # AWQ primarily supports causal language models
    supported_types = ["text-generation", "causal-lm"]

    return model_type in supported_types

    def get_supported_methods(self) -> List[QuantizationMethod]:
    """
    Get the quantization methods supported by the quantizer.

    Returns:
    List of supported quantization methods
    """
    return [QuantizationMethod.AWQ]

    def get_quantization_info(self) -> Dict[str, Any]:
    """
    Get information about the quantization.

    Returns:
    Dictionary with quantization information
    """
    return {
    "quantizer": "AWQ",
    "method": self.config.method.value,
    "bits": self.config.bits,
    "zero_point": self.config.awq_zero_point,
    "group_size": self.config.awq_group_size,
    "export_to_onnx": self.config.awq_export_to_onnx,
    }