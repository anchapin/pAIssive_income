"""
BitsAndBytes quantizer for AI models.

This module provides a quantizer that uses the BitsAndBytes library for
4 - bit and 8 - bit quantization of transformer models.
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
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available. BitsAndBytes quantizer will not work.")
    TORCH_AVAILABLE = False

try:
    pass

    BNB_AVAILABLE = True
except ImportError:
    logger.warning("BitsAndBytes not available. Please install it with: pip install bitsandbytes")
    BNB_AVAILABLE = False

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning(
        "Transformers not available. BitsAndBytes quantizer will have limited functionality."
    )
    TRANSFORMERS_AVAILABLE = False


class BitsAndBytesQuantizer(Quantizer):
    """
    Quantizer that uses the BitsAndBytes library.
    """

    def __init__(self, config: QuantizationConfig):
        """
        Initialize the BitsAndBytes quantizer.

        Args:
            config: Quantization configuration
        """
        super().__init__(config)

        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available. Please install it with: pip install torch")

        if not BNB_AVAILABLE:
            raise ImportError(
                "BitsAndBytes not available. Please install it with: pip install bitsandbytes"
            )

        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Transformers not available. Please install it with: pip install transformers"
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

        if self.config.method == QuantizationMethod.BITS_AND_BYTES_4BIT:
            if self.config.bnb_4bit_quant_type not in ["nf4", "fp4"]:
                raise ValueError(
                    f"Unsupported 4 - bit quantization type: {self.config.bnb_4bit_quant_type}. "
                    f"Supported types: nf4, fp4"
                )

    def quantize(self, model_path: str, output_path: Optional[str] = None, **kwargs) -> str:
        """
        Quantize a model using BitsAndBytes.

        Args:
            model_path: Path to the model
            output_path: Path to save the quantized model (None for in - place)
            **kwargs: Additional parameters for quantization

        Returns:
            Path to the quantized model
        """
        logger.info(f"Quantizing model {model_path} with BitsAndBytes")

        # Determine output path
        if output_path is None:
            output_path = model_path

        # Create BitsAndBytes configuration
        bnb_config = self._create_bnb_config()

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Load model with quantization
        model = AutoModelForCausalLM.from_pretrained(
            model_path, quantization_config=bnb_config, device_map="auto", **kwargs
        )

        # Save model and tokenizer
        logger.info(f"Saving quantized model to {output_path}")
        model.save_pretrained(output_path)
        tokenizer.save_pretrained(output_path)

        # Save quantization configuration
        self._save_quantization_config(output_path)

        return output_path

    def _create_bnb_config(self) -> BitsAndBytesConfig:
        """
        Create a BitsAndBytes configuration.

        Returns:
            BitsAndBytes configuration
        """
        if self.config.method == QuantizationMethod.BITS_AND_BYTES_4BIT:
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type=self.config.bnb_4bit_quant_type,
                bnb_4bit_use_double_quant=self.config.bnb_4bit_use_double_quant,
                bnb_4bit_compute_dtype=getattr(torch, self.config.bnb_4bit_compute_dtype),
            )
        elif self.config.method == QuantizationMethod.BITS_AND_BYTES_8BIT:
            return BitsAndBytesConfig(load_in_8bit=True, llm_int8_enable_fp32_cpu_offload=True)
        else:
            raise ValueError(f"Unsupported quantization method: {self.config.method}")

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
        # BitsAndBytes supports most transformer models
        supported_types = [
            "text - generation",
            "text - classification",
            "embedding",
            "causal - lm",
            "seq2seq - lm",
        ]

        return model_type in supported_types

    def get_supported_methods(self) -> List[QuantizationMethod]:
        """
        Get the quantization methods supported by the quantizer.

        Returns:
            List of supported quantization methods
        """
        return [
            QuantizationMethod.BITS_AND_BYTES_4BIT,
            QuantizationMethod.BITS_AND_BYTES_8BIT,
        ]

    def get_quantization_info(self) -> Dict[str, Any]:
        """
        Get information about the quantization.

        Returns:
            Dictionary with quantization information
        """
        info = {
            "quantizer": "BitsAndBytes",
            "method": self.config.method.value,
            "bits": (4 if self.config.method == QuantizationMethod.BITS_AND_BYTES_4BIT else 8),
        }

        if self.config.method == QuantizationMethod.BITS_AND_BYTES_4BIT:
            info.update(
                {
                    "quant_type": self.config.bnb_4bit_quant_type,
                    "use_double_quant": self.config.bnb_4bit_use_double_quant,
                    "compute_dtype": self.config.bnb_4bit_compute_dtype,
                }
            )

        return info
