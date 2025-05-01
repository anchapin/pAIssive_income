"""
Quantized model implementation for the AI Models module.

This module provides specialized classes for working with quantized models,
including 4-bit and 8-bit quantized models.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    logger.warning(
        "PyTorch not available. Some quantized model features will be limited."
    )
    TORCH_AVAILABLE = False

try:
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning(
        "Transformers not available. Text processing for quantized models will be limited."
    )
    TRANSFORMERS_AVAILABLE = False

try:
    import bitsandbytes as bnb

    BITSANDBYTES_AVAILABLE = True
except ImportError:
    logger.warning(
        "BitsAndBytes not available. 4-bit and 8-bit quantization will be limited."
    )
    BITSANDBYTES_AVAILABLE = False

try:
    from llama_cpp import Llama

    LLAMA_CPP_AVAILABLE = True
except ImportError:
    logger.warning(
        "llama-cpp-python not available. GGUF model support will be limited."
    )
    LLAMA_CPP_AVAILABLE = False


class QuantizedModel:
    """
    Base class for quantized models.
    """

    def __init__(
        self,
        model_path: str,
        model_type: str = "text-generation",
        quantization: str = "4bit",
        device: str = "auto",
        **kwargs,
    ):
        """
        Initialize a quantized model.

        Args:
            model_path: Path to the model file or directory
            model_type: Type of model (text-generation, embedding, etc.)
            quantization: Quantization level (4bit, 8bit, etc.)
            device: Device to run the model on (auto, cpu, cuda, etc.)
            **kwargs: Additional parameters for model initialization
        """
        self.model_path = model_path
        self.model_type = model_type
        self.quantization = quantization.lower()
        self.device = device
        self.kwargs = kwargs
        self.model = None
        self.tokenizer = None

        # Determine the model format
        self.model_format = self._detect_model_format()

        # Determine device
        if self.device == "auto":
            if TORCH_AVAILABLE and torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"

        logger.info(f"Initializing quantized model: {model_path}")
        logger.info(f"Model format: {self.model_format}")
        logger.info(f"Quantization: {self.quantization}")
        logger.info(f"Device: {self.device}")

    def _detect_model_format(self) -> str:
        """
        Detect the format of the model.

        Returns:
            Model format (huggingface, gguf, etc.)
        """
        if os.path.isdir(self.model_path):
            # Check if it's a Hugging Face model
            if os.path.exists(os.path.join(self.model_path, "config.json")):
                return "huggingface"
        else:
            # Check file extension
            file_ext = os.path.splitext(self.model_path)[1].lower()
            if file_ext == ".gguf":
                return "gguf"
            elif file_ext == ".bin" and os.path.exists(
                os.path.join(os.path.dirname(self.model_path), "config.json")
            ):
                return "huggingface"

        # Default to huggingface
        return "huggingface"

    def load(self) -> None:
        """
        Load the quantized model.
        """
        if self.model_format == "huggingface":
            self._load_huggingface_model()
        elif self.model_format == "gguf":
            self._load_gguf_model()
        else:
            raise ValueError(f"Unsupported model format: {self.model_format}")

    def _load_huggingface_model(self) -> None:
        """
        Load a quantized Hugging Face model.
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Transformers not available. Please install it with: pip install transformers"
            )

        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch not available. Please install it with: pip install torch"
            )

        logger.info(f"Loading quantized Hugging Face model: {self.model_path}")

        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)

            # Prepare quantization config
            if self.quantization == "4bit" or self.quantization == "4-bit":
                if not BITSANDBYTES_AVAILABLE:
                    raise ImportError(
                        "BitsAndBytes not available. Please install it with: pip install bitsandbytes"
                    )

                # 4-bit quantization
                quantization_config = transformers.BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )

            elif self.quantization == "8bit" or self.quantization == "8-bit":
                if not BITSANDBYTES_AVAILABLE:
                    raise ImportError(
                        "BitsAndBytes not available. Please install it with: pip install bitsandbytes"
                    )

                # 8-bit quantization
                quantization_config = transformers.BitsAndBytesConfig(
                    load_in_8bit=True, llm_int8_threshold=6.0
                )

            else:
                # No quantization or unsupported quantization
                quantization_config = None

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                quantization_config=quantization_config,
                device_map="auto" if self.device == "cuda" else None,
                **self.kwargs,
            )

            logger.info(
                f"Successfully loaded quantized Hugging Face model: {self.model_path}"
            )

        except Exception as e:
            logger.error(f"Error loading quantized Hugging Face model: {e}")
            raise

    def _load_gguf_model(self) -> None:
        """
        Load a quantized GGUF model.
        """
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError(
                "llama-cpp-python not available. Please install it with: pip install llama-cpp-python"
            )

        logger.info(f"Loading quantized GGUF model: {self.model_path}")

        try:
            # Determine number of threads
            n_threads = self.kwargs.get("n_threads", None) or os.cpu_count() // 2

            # Determine context size
            n_ctx = self.kwargs.get("n_ctx", 2048)

            # Load model
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                **self.kwargs,
            )

            logger.info(f"Successfully loaded quantized GGUF model: {self.model_path}")

        except Exception as e:
            logger.error(f"Error loading quantized GGUF model: {e}")
            raise

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        **kwargs,
    ) -> str:
        """
        Generate text using the quantized model.

        Args:
            prompt: Input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            **kwargs: Additional parameters for text generation

        Returns:
            Generated text
        """
        if not self.model:
            self.load()

        if self.model_format == "huggingface":
            return self._generate_text_huggingface(
                prompt, max_tokens, temperature, top_p, top_k, **kwargs
            )
        elif self.model_format == "gguf":
            return self._generate_text_gguf(
                prompt, max_tokens, temperature, top_p, top_k, **kwargs
            )
        else:
            raise ValueError(f"Unsupported model format: {self.model_format}")

    def _generate_text_huggingface(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        **kwargs,
    ) -> str:
        """
        Generate text using a quantized Hugging Face model.

        Args:
            prompt: Input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            **kwargs: Additional parameters for text generation

        Returns:
            Generated text
        """
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            input_ids = inputs["input_ids"].to(self.device)

            # Generate text
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    do_sample=temperature > 0,
                    pad_token_id=self.tokenizer.eos_token_id,
                    **kwargs,
                )

            # Decode output
            output_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Remove the prompt from the output if it's included
            if output_text.startswith(prompt):
                output_text = output_text[len(prompt) :]

            return output_text

        except Exception as e:
            logger.error(f"Error generating text with Hugging Face model: {e}")
            raise

    def _generate_text_gguf(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        **kwargs,
    ) -> str:
        """
        Generate text using a quantized GGUF model.

        Args:
            prompt: Input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            **kwargs: Additional parameters for text generation

        Returns:
            Generated text
        """
        try:
            # Generate text
            output = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                **kwargs,
            )

            # Extract text from output
            if isinstance(output, dict) and "choices" in output:
                return output["choices"][0]["text"]
            else:
                return str(output)

        except Exception as e:
            logger.error(f"Error generating text with GGUF model: {e}")
            raise

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the model.

        Returns:
            Dictionary with model metadata
        """
        metadata = {
            "model_path": self.model_path,
            "model_type": self.model_type,
            "model_format": self.model_format,
            "quantization": self.quantization,
            "device": self.device,
        }

        # Add model-specific metadata
        if self.model_format == "huggingface" and self.model:
            config = self.model.config
            metadata["model_config"] = {
                "model_type": getattr(config, "model_type", None),
                "vocab_size": getattr(config, "vocab_size", None),
                "hidden_size": getattr(config, "hidden_size", None),
                "num_hidden_layers": getattr(config, "num_hidden_layers", None),
                "num_attention_heads": getattr(config, "num_attention_heads", None),
            }

        return metadata


# Example usage
if __name__ == "__main__":
    # Example model path (replace with an actual model path)
    model_path = "path/to/model"

    if os.path.exists(model_path):
        # Create quantized model
        model = QuantizedModel(model_path=model_path, quantization="4bit")

        # Load the model
        model.load()

        # Get metadata
        metadata = model.get_metadata()
        print("Model Metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

        # Generate text
        prompt = "Hello, world!"
        print(f"\nGenerating text for prompt: {prompt}")
        output = model.generate_text(prompt)
        print(f"Output: {output}")
    else:
        print(f"Model file not found: {model_path}")
        print("Please specify a valid model path.")
