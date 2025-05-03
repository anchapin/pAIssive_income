"""
GPTQ (Generative Pre - trained Transformer Quantization) quantizer for AI models.

This module provides a quantizer that uses the GPTQ method for
quantizing transformer models.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from .base import QuantizationConfig, QuantizationMethod, Quantizer

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    pass

    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available. GPTQ quantizer will not work.")
    TORCH_AVAILABLE = False

try:
    from transformers import AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning(
        "Transformers not available. GPTQ quantizer will have limited functionality.")
    TRANSFORMERS_AVAILABLE = False

# Check if GPTQ is available
try:
    from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig

    GPTQ_AVAILABLE = True
except ImportError:
    logger.warning(
        "AutoGPTQ not available. Please install it with: pip install auto - gptq")
    GPTQ_AVAILABLE = False


class GPTQQuantizer(Quantizer):
    """
    Quantizer that uses the GPTQ method.
    """

    def __init__(self, config: QuantizationConfig):
        """
        Initialize the GPTQ quantizer.

        Args:
            config: Quantization configuration
        """
        super().__init__(config)

        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch not available. Please install it with: pip install torch")

        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Transformers not available. Please install it with: pip install transformers"
            )

        if not GPTQ_AVAILABLE:
            raise ImportError(
                "AutoGPTQ not available. Please install it with: pip install auto - \
                    gptq"
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

        if self.config.gptq_bits not in [2, 3, 4, 8]:
            raise ValueError(
                f"Unsupported bits: {self.config.gptq_bits}. " f"Supported bits: 2, 3, 4, 
                    8"
            )

    def quantize(self, model_path: str, output_path: Optional[str] = None, 
        **kwargs) -> str:
        """
        Quantize a model using GPTQ.

        Args:
            model_path: Path to the model
            output_path: Path to save the quantized model (None for in - place)
            **kwargs: Additional parameters for quantization

        Returns:
            Path to the quantized model
        """
        logger.info(f"Quantizing model {model_path} with GPTQ")

        # Determine output path
        if output_path is None:
            output_path = model_path

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Create GPTQ quantization configuration
        quantize_config = BaseQuantizeConfig(
            bits=self.config.gptq_bits,
            group_size=self.config.gptq_group_size,
            desc_act=self.config.gptq_act_order,
        )

        # Get calibration dataset
        if self.config.calibration_dataset:
            # Use provided dataset
            calibration_dataset = self.config.calibration_dataset
        else:
            # Use default dataset (WikiText - 2)
            from datasets import load_dataset

            calibration_dataset = load_dataset("wikitext", "wikitext - 2-raw - v1", 
                split="train")

            # Process dataset
            def preprocess_function(examples):
                return tokenizer("\n\n".join(examples["text"]))

            calibration_dataset = calibration_dataset.map(
                preprocess_function, batched=True, remove_columns=["text"]
            )

        # Create examples for calibration
        examples = []
        for i in range(min(self.config.calibration_num_samples, 
            len(calibration_dataset))):
            example = calibration_dataset[i]["input_ids"]
            if len(example) > self.config.calibration_seqlen:
                example = example[: self.config.calibration_seqlen]
            examples.append(example)

        # Create GPTQ model
        model = AutoGPTQForCausalLM.from_pretrained(model_path, 
            quantize_config=quantize_config)

        # Quantize model
        model.quantize(examples=examples, batch_size=1)

        # Save model and tokenizer
        logger.info(f"Saving quantized model to {output_path}")
        model.save_quantized(output_path)
        tokenizer.save_pretrained(output_path)

        # Save quantization configuration
        self._save_quantization_config(output_path)

        return output_path

    def _save_quantization_config(self, output_path: str) -> None:
        """
        Save the quantization configuration.

        Args:
            output_path: Path to save the configuration
        """
        import json

        config_path = os.path.join(output_path, "quantization_config.json")

        with open(config_path, "w", encoding="utf - 8") as f:
            json.dump(self.config.to_dict(), f, indent=2)

    def supports_model_type(self, model_type: str) -> bool:
        """
        Check if the quantizer supports a model type.

        Args:
            model_type: Type of the model

        Returns:
            True if the model type is supported, False otherwise
        """
        # GPTQ primarily supports causal language models
        supported_types = ["text - generation", "causal - lm"]

        return model_type in supported_types

    def get_supported_methods(self) -> List[QuantizationMethod]:
        """
        Get the quantization methods supported by the quantizer.

        Returns:
            List of supported quantization methods
        """
        return [QuantizationMethod.GPTQ]

    def get_quantization_info(self) -> Dict[str, Any]:
        """
        Get information about the quantization.

        Returns:
            Dictionary with quantization information
        """
        return {
            "quantizer": "GPTQ",
            "method": self.config.method.value,
            "bits": self.config.gptq_bits,
            "group_size": self.config.gptq_group_size,
            "act_order": self.config.gptq_act_order,
        }
