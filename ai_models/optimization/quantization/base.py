"""
Base classes for model quantization.

This module provides the base classes and interfaces for model quantization.
"""

import abc
import enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


class QuantizationMethod(enum.Enum):
    """
    Enumeration of quantization methods.
    """

    NONE = "none"
    INT8 = "int8"
    INT4 = "int4"
    FLOAT16 = "float16"
    BFLOAT16 = "bfloat16"
    BITS_AND_BYTES_4BIT = "bitsandbytes-4bit"
    BITS_AND_BYTES_8BIT = "bitsandbytes-8bit"
    AWQ = "awq"
    GPTQ = "gptq"
    GGML = "ggml"
    GGUF = "gguf"


@dataclass
class QuantizationConfig:
    """
    Configuration for model quantization.
    """

    method: QuantizationMethod = QuantizationMethod.NONE
    bits: int = 8
    compute_dtype: Optional[str] = None

    # Method-specific parameters
    use_double_quant: bool = False  # For BitsAndBytes
    bnb_4bit_quant_type: str = "nf4"  # For BitsAndBytes 4-bit (nf4 or fp4)
    bnb_4bit_use_double_quant: bool = True  # For BitsAndBytes 4-bit
    bnb_4bit_compute_dtype: str = "float16"  # For BitsAndBytes 4-bit

    # AWQ parameters
    awq_zero_point: bool = True
    awq_group_size: int = 128
    awq_export_to_onnx: bool = False

    # GPTQ parameters
    gptq_bits: int = 4
    gptq_group_size: int = 128
    gptq_act_order: bool = False

    # GGML/GGUF parameters
    ggml_model_type: str = "llama"
    ggml_ftype: int = 1  # 0: float32, 1: float16, 2: int8, 3: int4

    # Calibration parameters
    calibration_dataset: Optional[str] = None
    calibration_num_samples: int = 128
    calibration_seqlen: int = 2048

    # Additional parameters
    additional_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "method": self.method.value,
            "bits": self.bits,
            "compute_dtype": self.compute_dtype,
            "use_double_quant": self.use_double_quant,
            "bnb_4bit_quant_type": self.bnb_4bit_quant_type,
            "bnb_4bit_use_double_quant": self.bnb_4bit_use_double_quant,
            "bnb_4bit_compute_dtype": self.bnb_4bit_compute_dtype,
            "awq_zero_point": self.awq_zero_point,
            "awq_group_size": self.awq_group_size,
            "awq_export_to_onnx": self.awq_export_to_onnx,
            "gptq_bits": self.gptq_bits,
            "gptq_group_size": self.gptq_group_size,
            "gptq_act_order": self.gptq_act_order,
            "ggml_model_type": self.ggml_model_type,
            "ggml_ftype": self.ggml_ftype,
            "calibration_dataset": self.calibration_dataset,
            "calibration_num_samples": self.calibration_num_samples,
            "calibration_seqlen": self.calibration_seqlen,
            **self.additional_params,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "QuantizationConfig":
        """
        Create a configuration from a dictionary.

        Args:
            config_dict: Dictionary with configuration parameters

        Returns:
            Quantization configuration
        """
        # Extract method
        method_str = config_dict.pop("method", "none")
        try:
            method = QuantizationMethod(method_str)
        except ValueError:
            method = QuantizationMethod.NONE

        # Extract additional parameters
        additional_params = {}
        for key, value in list(config_dict.items()):
            if key not in cls.__annotations__:
                additional_params[key] = config_dict.pop(key)

        # Create configuration
        config = cls(method=method, **config_dict)

        config.additional_params = additional_params
        return config


class Quantizer(abc.ABC):
    """
    Base class for model quantizers.
    """

    def __init__(self, config: QuantizationConfig):
        """
        Initialize the quantizer.

        Args:
            config: Quantization configuration
        """
        self.config = config

    @abc.abstractmethod
    def quantize(
        self, model_path: str, output_path: Optional[str] = None, **kwargs
    ) -> str:
        """
        Quantize a model.

        Args:
            model_path: Path to the model
            output_path: Path to save the quantized model (None for in-place)
            **kwargs: Additional parameters for quantization

        Returns:
            Path to the quantized model
        """
        pass

    @abc.abstractmethod
    def supports_model_type(self, model_type: str) -> bool:
        """
        Check if the quantizer supports a model type.

        Args:
            model_type: Type of the model

        Returns:
            True if the model type is supported, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_supported_methods(self) -> List[QuantizationMethod]:
        """
        Get the quantization methods supported by the quantizer.

        Returns:
            List of supported quantization methods
        """
        pass

    @abc.abstractmethod
    def get_quantization_info(self) -> Dict[str, Any]:
        """
        Get information about the quantization.

        Returns:
            Dictionary with quantization information
        """
        pass
